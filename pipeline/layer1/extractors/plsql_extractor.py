import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from .base_extractor import BaseExtractor

# ─────────────────────────────────────────────────────────────────────────────
# NOTE ON APPROACH
# ─────────────────────────────────────────────────────────────────────────────
# Pragmatic regex + hand-rolled block-balance scanner. Not a real PL/SQL parser
# but good enough to recover full trigger/procedure bodies for downstream LLM
# analysis. All content truncation limits have been removed — full bodies are
# captured so the LLM receives complete business logic.
# ─────────────────────────────────────────────────────────────────────────────

PLSQL_EXTENSIONS = {".sql", ".pks", ".pkb", ".pkg", ".trg", ".prc", ".fnc", ".vw"}

_PACKAGE_SPEC_RE = re.compile(
    r"CREATE\s+(?:OR\s+REPLACE\s+)?PACKAGE\s+(?!BODY\b)"
    r"(?:(\w+)\.)?(\w+)\s+(?:IS|AS)\b",
    re.IGNORECASE,
)

_PACKAGE_BODY_RE = re.compile(
    r"CREATE\s+(?:OR\s+REPLACE\s+)?PACKAGE\s+BODY\s+"
    r"(?:(\w+)\.)?(\w+)\s+(?:IS|AS)\b",
    re.IGNORECASE,
)

_PROCEDURE_RE = re.compile(
    r"(?:CREATE\s+(?:OR\s+REPLACE\s+)?)?PROCEDURE\s+"
    r"(?:(\w+)\.)?(\w+)\s*(\([^;]*?\))?\s*(?:IS|AS)\b",
    re.IGNORECASE | re.DOTALL,
)

_FUNCTION_RE = re.compile(
    r"(?:CREATE\s+(?:OR\s+REPLACE\s+)?)?FUNCTION\s+"
    r"(?:(\w+)\.)?(\w+)\s*(\([^;]*?\))?\s*RETURN\s+([\w%.]+)\s*(?:IS|AS)\b",
    re.IGNORECASE | re.DOTALL,
)

_TRIGGER_RE = re.compile(
    r"CREATE\s+(?:OR\s+REPLACE\s+)?TRIGGER\s+"
    r"(?:(\w+)\.)?(\w+)\s+"
    r"(BEFORE|AFTER|INSTEAD\s+OF)\s+"
    r"([\w\s,]+?)\s+"
    r"ON\s+(?:(\w+)\.)?(\w+)"
    r"(?P<for_each_row>\s+FOR\s+EACH\s+ROW)?"
    r"(?:\s+WHEN\s*\((?P<when_clause>[^)]*)\))?",
    re.IGNORECASE,
)

# DDL / system-level triggers (AFTER LOGON, AFTER CREATE, etc.)
_SYSTEM_TRIGGER_RE = re.compile(
    r"CREATE\s+(?:OR\s+REPLACE\s+)?TRIGGER\s+"
    r"(?:(\w+)\.)?(\w+)\s+"
    r"(AFTER|BEFORE)\s+"
    r"(CREATE|DROP|ALTER|TRUNCATE|LOGON|LOGOFF|STARTUP|SHUTDOWN|SERVERERROR)"
    r"(?:\s+OR\s+(?:CREATE|DROP|ALTER|TRUNCATE|LOGON|LOGOFF))*"
    r"\s+ON\s+(?:DATABASE|SCHEMA)",
    re.IGNORECASE,
)

# Package-level constants:  name  CONSTANT  type  [:= | DEFAULT]  value
_PACKAGE_CONSTANT_RE = re.compile(
    r"^\s+(\w+)\s+CONSTANT\s+([\w%.]+(?:\s*\(\s*\d+\s*(?:,\s*\d+\s*)?\))?)\s*"
    r"(?::=|DEFAULT)\s*(.+?)\s*;",
    re.IGNORECASE | re.MULTILINE,
)

# Package-level variables (non-constant package state, also useful for agents)
_PACKAGE_VARIABLE_RE = re.compile(
    r"^\s+(\w+)\s+([\w%.]+(?:\s*\(\s*\d+\s*(?:,\s*\d+\s*)?\))?)\s*"
    r"(?::=\s*(.+?))?\s*;",
    re.IGNORECASE | re.MULTILINE,
)

# Tokens that open/close a nested PL/SQL block
_BLOCK_TOKEN_RE = re.compile(
    r"\bBEGIN\b|\bCASE\b|\bIF\b|\bLOOP\b|\bEND\s+IF\b|\bEND\s+CASE\b|\bEND\s+LOOP\b|\bEND\b",
    re.IGNORECASE,
)


class PlsqlExtractor(BaseExtractor):
    """
    Extracts Oracle PL/SQL business artefacts: packages (specs + bodies),
    standalone procedures/functions, triggers, package constants, and system
    triggers. Full source bodies captured with NO truncation.
    """

    def extract(self, file_path: str) -> List[Dict]:
        ext = Path(file_path).suffix.lower()
        if ext not in PLSQL_EXTENSIONS:
            return []

        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as fh:
                content = fh.read()
        except OSError:
            return []

        artifacts: List[Dict] = []
        artifacts.extend(self._extract_package_specs(content, file_path))

        body_artifacts, body_spans = self._extract_package_bodies(content, file_path)
        artifacts.extend(body_artifacts)

        artifacts.extend(
            self._extract_standalone_procs_and_funcs(
                content, file_path, exclude_spans=body_spans
            )
        )
        artifacts.extend(self._extract_triggers(content, file_path))
        artifacts.extend(self._extract_system_triggers(content, file_path))
        return artifacts

    # ── packages ──────────────────────────────────────────────────────────────

    def _extract_package_specs(self, content: str, file_path: str) -> List[Dict]:
        artifacts = []
        for m in _PACKAGE_SPEC_RE.finditer(content):
            name = m.group(2)
            end = _scan_to_unit_end(content, m.end())
            body = content[m.start():end]

            # Extract procedure/function signatures from spec (no body needed — just signatures)
            proc_sigs = re.findall(
                r"(?:PROCEDURE|FUNCTION)\s+(\w+)\s*(\([^;]*?\))?(?:\s*RETURN\s+[\w%.]+)?",
                body, re.IGNORECASE | re.DOTALL
            )
            signatures = [{"name": s[0], "params_raw": (s[1] or "").strip()} for s in proc_sigs]

            # Extract package-level constants from spec
            constants = self._extract_constants(body)

            artifacts.append(self.make_artifact(
                language="plsql",
                source_file=file_path,
                type="package_spec",
                name=name,
                content=body,   # no truncation
                metadata={
                    "schema": m.group(1) or "",
                    "line_number": _line_of(content, m.start()),
                    "procedure_signatures": signatures,
                    "constants": constants,
                },
                is_business_artifact=True,
                business_category="contract_definition",
            ))
        return artifacts

    def _extract_package_bodies(
        self, content: str, file_path: str
    ) -> Tuple[List[Dict], List[Tuple[int, int]]]:
        artifacts = []
        spans: List[Tuple[int, int]] = []
        for m in _PACKAGE_BODY_RE.finditer(content):
            pkg_name = m.group(2)
            body_start = m.end()
            body_end = _scan_to_unit_end(content, body_start)
            package_body_text = content[m.start():body_end]
            spans.append((m.start(), body_end))

            constants = self._extract_constants(package_body_text)

            # Whole-package artifact
            artifacts.append(self.make_artifact(
                language="plsql",
                source_file=file_path,
                type="package_body",
                name=pkg_name,
                content=package_body_text,   # no truncation — full body
                metadata={
                    "schema": m.group(1) or "",
                    "line_number": _line_of(content, m.start()),
                    "constants": constants,
                },
                is_business_artifact=True,
                business_category="process",
            ))

            # Individual procedures/functions inside the body
            artifacts.extend(
                self._extract_standalone_procs_and_funcs(
                    package_body_text, file_path, parent_package=pkg_name
                )
            )
        return artifacts, spans

    # ── constants extractor ───────────────────────────────────────────────────

    @staticmethod
    def _extract_constants(body: str) -> List[Dict]:
        constants = []
        for m in _PACKAGE_CONSTANT_RE.finditer(body):
            constants.append({
                "name": m.group(1),
                "type": m.group(2),
                "value": m.group(3).strip(),
            })
        return constants

    # ── standalone / nested procedures & functions ───────────────────────────

    def _extract_standalone_procs_and_funcs(
        self,
        content: str,
        file_path: str,
        parent_package: Optional[str] = None,
        exclude_spans: Optional[List[Tuple[int, int]]] = None,
    ) -> List[Dict]:
        artifacts = []
        exclude_spans = exclude_spans or []

        def _excluded(pos: int) -> bool:
            return any(start <= pos < end for start, end in exclude_spans)

        for m in _PROCEDURE_RE.finditer(content):
            if _excluded(m.start()):
                continue
            name = m.group(2)
            end = _scan_to_unit_end(content, m.end())
            body = content[m.start():end]
            is_business = self.is_business_method(name)
            artifacts.append(self.make_artifact(
                language="plsql",
                source_file=file_path,
                type="procedure",
                name=name,
                content=body,   # no truncation
                metadata={
                    "schema": m.group(1) or "",
                    "parent_package": parent_package or "",
                    "params_raw": (m.group(3) or "").strip(),
                    "line_number": _line_of(content, m.start()),
                },
                is_business_artifact=is_business or bool(parent_package),
                business_category=self.get_business_category(name),
            ))

        for m in _FUNCTION_RE.finditer(content):
            if _excluded(m.start()):
                continue
            name = m.group(2)
            end = _scan_to_unit_end(content, m.end())
            body = content[m.start():end]
            is_business = self.is_business_method(name)
            artifacts.append(self.make_artifact(
                language="plsql",
                source_file=file_path,
                type="function",
                name=name,
                content=body,   # no truncation
                metadata={
                    "schema": m.group(1) or "",
                    "parent_package": parent_package or "",
                    "params_raw": (m.group(3) or "").strip(),
                    "return_type": m.group(4),
                    "line_number": _line_of(content, m.start()),
                },
                is_business_artifact=is_business or bool(parent_package),
                business_category=self.get_business_category(name),
            ))

        return artifacts

    # ── triggers ──────────────────────────────────────────────────────────────

    def _extract_triggers(self, content: str, file_path: str) -> List[Dict]:
        artifacts = []
        for m in _TRIGGER_RE.finditer(content):
            name = m.group(2)
            table = m.group(6)
            end = _scan_to_unit_end(content, m.end())
            body = content[m.start():end]

            events = [e.strip().upper() for e in m.group(4).split(",") if e.strip()]
            timing = m.group(3).upper().replace("  ", " ")
            for_each_row = bool(m.group("for_each_row"))
            when_clause = (m.group("when_clause") or "").strip()
            new_old_refs = len(re.findall(r":(?:NEW|OLD)\.\w+", body, re.IGNORECASE))

            artifacts.append(self.make_artifact(
                language="plsql",
                source_file=file_path,
                type="trigger",
                name=name,
                content=body,   # no truncation
                metadata={
                    "schema": m.group(5) or "",
                    "table": table,
                    "timing": timing,
                    "events": events,
                    "for_each_row": for_each_row,
                    "when_clause": when_clause,
                    "new_old_reference_count": new_old_refs,
                    "line_number": _line_of(content, m.start()),
                },
                is_business_artifact=True,
                business_category="trigger_logic",
            ))
        return artifacts

    # ── system / DDL triggers ─────────────────────────────────────────────────

    def _extract_system_triggers(self, content: str, file_path: str) -> List[Dict]:
        artifacts = []
        for m in _SYSTEM_TRIGGER_RE.finditer(content):
            name = m.group(2)
            end = _scan_to_unit_end(content, m.end())
            body = content[m.start():end]
            artifacts.append(self.make_artifact(
                language="plsql",
                source_file=file_path,
                type="system_trigger",
                name=name,
                content=body,
                metadata={
                    "schema": m.group(1) or "",
                    "timing": m.group(3).upper(),
                    "event": m.group(4).upper(),
                    "line_number": _line_of(content, m.start()),
                },
                is_business_artifact=True,
                business_category="system_trigger",
            ))
        return artifacts


# ── shared helpers (also used by OracleFormsExtractor) ────────────────────────

def _line_of(content: str, pos: int) -> int:
    return content.count("\n", 0, pos) + 1


def scan_to_unit_end(content: str, start_pos: int) -> int:
    """Public entry point."""
    return _scan_to_unit_end(content, start_pos)


def _scan_to_unit_end(content: str, start_pos: int) -> int:
    """
    Scan forward from start_pos tracking BEGIN/CASE/IF/LOOP nesting depth.
    Returns the index just past the bare END/END-name/; that closes the unit.
    No artificial cap — returns true end of unit or end of file.
    """
    depth = 0
    length = len(content)

    for tok in _BLOCK_TOKEN_RE.finditer(content, start_pos):
        word = tok.group(0).upper().strip()
        word = re.sub(r"\s+", " ", word)

        if word in ("BEGIN", "CASE", "IF", "LOOP"):
            depth += 1
        elif word in ("END IF", "END CASE", "END LOOP"):
            depth = max(0, depth - 1)
        elif word == "END":
            if depth > 0:
                depth -= 1
            else:
                semi = content.find(";", tok.end())
                return (semi + 1) if semi != -1 else min(tok.end() + 200, length)

    return length
