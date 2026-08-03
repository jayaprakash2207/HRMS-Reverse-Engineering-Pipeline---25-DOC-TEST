import os
import re
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List

# ── SQL patterns ───────────────────────────────────────────────────────────────

_CREATE_TABLE = re.compile(
    r"CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?"
    r"(?:\[?(\w+)\]?\.)?"        # optional schema
    r"\[?(\w+)\]?\s*"            # table name
    r"\(([^;]{10,}?)\)"          # column block
    r"\s*(?:;|GO|ON\s+\[|\Z)",
    re.IGNORECASE | re.DOTALL,
)

_CREATE_PROC = re.compile(
    r"CREATE\s+(?:OR\s+(?:ALTER|REPLACE)\s+)?(?:PROCEDURE|PROC)\s+"
    r"(?:\[?(\w+)\]?\.)?"        # schema
    r"\[?(\w+)\]?",
    re.IGNORECASE,
)

_CREATE_TRIGGER = re.compile(
    r"CREATE\s+(?:OR\s+(?:ALTER|REPLACE)\s+)?TRIGGER\s+"
    r"(?:\[?(\w+)\]?\.)?"
    r"\[?(\w+)\]?\s+ON\s+\[?(\w+)\]?",
    re.IGNORECASE,
)

# Oracle trigger syntax — separate pattern from SQL Server shape above
_CREATE_TRIGGER_ORACLE = re.compile(
    r"CREATE\s+(?:OR\s+REPLACE\s+)?TRIGGER\s+"
    r"(?:(\w+)\.)?(\w+)\s+"
    r"(BEFORE|AFTER|INSTEAD\s+OF)\s+"
    r"([\w\s,]+?)\s+"
    r"ON\s+(?:(\w+)\.)?(\w+)"
    r"(?:\s+FOR\s+EACH\s+ROW)?"
    r"(?:\s+WHEN\s*\([^)]*\))?",
    re.IGNORECASE,
)

_CREATE_PACKAGE_BODY = re.compile(
    r"CREATE\s+(?:OR\s+REPLACE\s+)?PACKAGE\s+BODY\s+(?:(\w+)\.)?(\w+)",
    re.IGNORECASE,
)
_CREATE_PACKAGE_SPEC = re.compile(
    r"CREATE\s+(?:OR\s+REPLACE\s+)?PACKAGE\s+(?!BODY\b)(?:(\w+)\.)?(\w+)",
    re.IGNORECASE,
)

# Full view definition — capture everything after AS up to ; or end-of-statement
_CREATE_VIEW = re.compile(
    r"CREATE\s+(?:OR\s+(?:ALTER|REPLACE)\s+)?(?:FORCE\s+)?VIEW\s+"
    r"(?:\[?(\w+)\]?\.)?"
    r"\[?(\w+)\]?\s+AS\s+"
    r"([\s\S]+?)(?=;\s*(?:\/\s*)?(?:CREATE|$)|\Z)",
    re.IGNORECASE,
)

# Oracle materialized view
_CREATE_MATERIALIZED_VIEW = re.compile(
    r"CREATE\s+MATERIALIZED\s+VIEW\s+"
    r"(?:(\w+)\.)?(\w+)\s+"
    r"([\s\S]+?)(?=;\s*(?:\/\s*)?(?:CREATE|$)|\Z)",
    re.IGNORECASE,
)

# Oracle sequence
_CREATE_SEQUENCE = re.compile(
    r"CREATE\s+SEQUENCE\s+"
    r"(?:(\w+)\.)?(\w+)"
    r"(?:\s+START\s+WITH\s+(\d+))?"
    r"(?:\s+INCREMENT\s+BY\s+(\d+))?"
    r"(?:\s+(?:NO)?MAXVALUE(?:\s+(\d+))?)?"
    r"(?:\s+(?:NO)?MINVALUE(?:\s+(\d+))?)?"
    r"(?:\s+(?:NO)?CYCLE)?"
    r"(?:\s+(?:NO)?CACHE(?:\s+(\d+))?)?",
    re.IGNORECASE,
)

# Oracle synonym
_CREATE_SYNONYM = re.compile(
    r"CREATE\s+(?:OR\s+REPLACE\s+)?(?:PUBLIC\s+)?SYNONYM\s+"
    r"(?:(\w+)\.)?(\w+)\s+FOR\s+"
    r"(?:(\w+)\.)?(\w+)",
    re.IGNORECASE,
)

# Oracle VPD / Row Level Security
_DBMS_RLS = re.compile(
    r"DBMS_RLS\.(ADD_POLICY|DROP_POLICY|ENABLE_POLICY|DISABLE_POLICY)\s*\("
    r"[\s\S]*?object_name\s*=>\s*'(\w+)'[\s\S]*?\)",
    re.IGNORECASE,
)

# Oracle DDL/Logon system triggers
_CREATE_SYSTEM_TRIGGER = re.compile(
    r"CREATE\s+(?:OR\s+REPLACE\s+)?TRIGGER\s+"
    r"(?:(\w+)\.)?(\w+)\s+"
    r"(AFTER|BEFORE)\s+"
    r"(CREATE|DROP|ALTER|TRUNCATE|LOGON|LOGOFF|STARTUP|SHUTDOWN|SERVERERROR)"
    r"(?:\s+OR\s+(?:CREATE|DROP|ALTER|TRUNCATE|LOGON|LOGOFF))*"
    r"\s+ON\s+(?:DATABASE|SCHEMA)",
    re.IGNORECASE,
)

_FK = re.compile(
    r"FOREIGN\s+KEY[^R]*REFERENCES\s+\[?(\w+)\]?",
    re.IGNORECASE,
)

# CHECK constraint — capture the expression
_CHECK_CONSTRAINT = re.compile(
    r"(?:CONSTRAINT\s+\w+\s+)?CHECK\s*\(([^)]+)\)",
    re.IGNORECASE,
)

# UNIQUE constraint
_UNIQUE_CONSTRAINT = re.compile(
    r"(?:CONSTRAINT\s+(\w+)\s+)?UNIQUE\s*\(([^)]+)\)",
    re.IGNORECASE,
)

# ── C# EF Core patterns ────────────────────────────────────────────────────────

_DBSET = re.compile(r"DbSet<(\w+)>", re.MULTILINE)
_EF_ENTITY = re.compile(r"modelBuilder\.Entity<(\w+)>", re.MULTILINE)
_TABLE_ATTR = re.compile(r'\[Table\(["\'](\w+)["\']\)\]')
_COLUMN_LINE = re.compile(
    r"\[?(\w+)\]?\s+([\w]+(?:\(\d+(?:,\s*\d+)?\))?)"
    r"(?:\s+(NOT\s+NULL|NULL))?"
    r"(?:\s+(PRIMARY\s+KEY|IDENTITY|UNIQUE))?",
    re.IGNORECASE,
)

# File extensions considered SQL scripts
_SQL_EXTS = {".sql", ".ddl", ".dml", ".prc", ".trg", ".vw", ".fnc", ".pkb", ".pks"}


class DatabaseExtractor:
    """Extracts database objects from SQL scripts and EF Core C# files."""

    def extract(self, files: List[str], root_path: str) -> Dict:
        results: Dict = {
            "tables": [],
            "stored_procedures": [],
            "packages": [],
            "triggers": [],
            "system_triggers": [],
            "views": [],
            "materialized_views": [],
            "sequences": [],
            "synonyms": [],
            "vpd_policies": [],
            "relationships": [],
            "check_constraints": [],
            "unique_constraints": [],
            "ef_entities": [],
            "db_contexts": [],
        }

        for file_path in files:
            ext = Path(file_path).suffix.lower()
            if ext in _SQL_EXTS:
                self._from_sql(file_path, results)
            elif ext == ".cs":
                self._from_csharp(file_path, results)

        return results

    # ── SQL ────────────────────────────────────────────────────────────────────

    def _from_sql(self, file_path: str, results: Dict):
        try:
            content = Path(file_path).read_text(encoding="utf-8", errors="ignore")
        except OSError:
            return

        for m in _CREATE_TABLE.finditer(content):
            schema = m.group(1) or "dbo"
            name = m.group(2)
            col_block = m.group(3)
            table_entry = {
                "name": name,
                "schema": schema,
                "columns": self._parse_columns(col_block),
                "check_constraints": self._parse_check_constraints(col_block),
                "unique_constraints": self._parse_unique_constraints(col_block),
                "source_file": file_path,
                "ddl": m.group(0),   # full DDL, no truncation
            }
            results["tables"].append(table_entry)

        for m in _CREATE_PROC.finditer(content):
            results["stored_procedures"].append({
                "name": m.group(2),
                "schema": m.group(1) or "dbo",
                "source_file": file_path,
            })

        for m in _CREATE_TRIGGER.finditer(content):
            results["triggers"].append({
                "name": m.group(2),
                "on_table": m.group(3),
                "source_file": file_path,
            })

        for m in _CREATE_TRIGGER_ORACLE.finditer(content):
            events = [e.strip().upper() for e in m.group(4).split(",") if e.strip()]
            results["triggers"].append({
                "name": m.group(2),
                "schema": m.group(1) or "",
                "timing": m.group(3).upper(),
                "events": events,
                "on_table": m.group(6),
                "table_schema": m.group(5) or "",
                "source_file": file_path,
            })

        for m in _CREATE_SYSTEM_TRIGGER.finditer(content):
            results["system_triggers"].append({
                "name": m.group(2),
                "schema": m.group(1) or "",
                "timing": m.group(3).upper(),
                "event": m.group(4).upper(),
                "source_file": file_path,
            })

        for m in _CREATE_PACKAGE_BODY.finditer(content):
            results["packages"].append({
                "name": m.group(2),
                "schema": m.group(1) or "",
                "kind": "body",
                "source_file": file_path,
            })

        for m in _CREATE_PACKAGE_SPEC.finditer(content):
            results["packages"].append({
                "name": m.group(2),
                "schema": m.group(1) or "",
                "kind": "spec",
                "source_file": file_path,
            })

        for m in _CREATE_VIEW.finditer(content):
            results["views"].append({
                "name": m.group(2),
                "schema": m.group(1) or "dbo",
                "definition": m.group(3).strip(),   # full SELECT definition
                "source_file": file_path,
            })

        for m in _CREATE_MATERIALIZED_VIEW.finditer(content):
            results["materialized_views"].append({
                "name": m.group(2),
                "schema": m.group(1) or "",
                "definition": m.group(3).strip(),
                "source_file": file_path,
            })

        for m in _CREATE_SEQUENCE.finditer(content):
            results["sequences"].append({
                "name": m.group(2),
                "schema": m.group(1) or "",
                "start_with": m.group(3) or "1",
                "increment_by": m.group(4) or "1",
                "max_value": m.group(5) or "",
                "min_value": m.group(6) or "",
                "cache": m.group(7) or "",
                "source_file": file_path,
            })

        for m in _CREATE_SYNONYM.finditer(content):
            results["synonyms"].append({
                "name": m.group(2),
                "schema": m.group(1) or "",
                "for_object": m.group(4),
                "for_schema": m.group(3) or "",
                "source_file": file_path,
            })

        for m in _DBMS_RLS.finditer(content):
            results["vpd_policies"].append({
                "action": m.group(1).upper(),
                "table": m.group(2),
                "source_file": file_path,
                "raw": m.group(0)[:500],
            })

        for m in _FK.finditer(content):
            results["relationships"].append({
                "references_table": m.group(1),
                "source_file": file_path,
            })

    # ── C# EF Core ─────────────────────────────────────────────────────────────

    def _from_csharp(self, file_path: str, results: Dict):
        try:
            content = Path(file_path).read_text(encoding="utf-8", errors="ignore")
        except OSError:
            return

        if "DbContext" in content:
            entities = list({m.group(1) for m in _DBSET.finditer(content)})
            entities += [
                m.group(1) for m in _EF_ENTITY.finditer(content)
                if m.group(1) not in entities
            ]
            if entities:
                results["db_contexts"].append({
                    "file": file_path,
                    "entities": entities,
                })
                for entity in entities:
                    results["ef_entities"].append({
                        "entity_name": entity,
                        "source_file": file_path,
                        "type": "ef_entity",
                    })

        for m in _TABLE_ATTR.finditer(content):
            results["tables"].append({
                "name": m.group(1),
                "source_file": file_path,
                "source": "data_annotation",
                "columns": [],
            })

    # ── helpers ────────────────────────────────────────────────────────────────

    @staticmethod
    def _parse_columns(col_block: str) -> List[Dict]:
        columns = []
        skip_starts = ("CONSTRAINT", "PRIMARY", "FOREIGN", "UNIQUE", "CHECK", "INDEX", "KEY")

        for raw_line in col_block.split("\n"):
            line = raw_line.strip().rstrip(",")
            if not line or line.upper().startswith(skip_starts):
                continue

            m = _COLUMN_LINE.match(line)
            if m:
                col_name = m.group(1)
                if col_name.upper() in ("GO", "END", "BEGIN"):
                    continue
                # Capture DEFAULT value if present
                default_match = re.search(r"DEFAULT\s+(\S+)", line, re.IGNORECASE)
                columns.append({
                    "name": col_name,
                    "type": m.group(2),
                    "nullable": "NOT NULL" not in (m.group(3) or "").upper(),
                    "is_primary_key": bool(
                        re.search(r"PRIMARY\s+KEY|IDENTITY", m.group(4) or "", re.IGNORECASE)
                    ),
                    "default": default_match.group(1) if default_match else None,
                })

        return columns

    @staticmethod
    def _parse_check_constraints(col_block: str) -> List[Dict]:
        constraints = []
        for m in _CHECK_CONSTRAINT.finditer(col_block):
            constraints.append({"expression": m.group(1).strip()})
        return constraints

    @staticmethod
    def _parse_unique_constraints(col_block: str) -> List[Dict]:
        constraints = []
        for m in _UNIQUE_CONSTRAINT.finditer(col_block):
            constraints.append({
                "name": m.group(1) or "",
                "columns": [c.strip() for c in m.group(2).split(",")],
            })
        return constraints
