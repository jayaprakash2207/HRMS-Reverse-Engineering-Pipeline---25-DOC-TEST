import re
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Optional

from .base_extractor import BaseExtractor
from .plsql_extractor import PlsqlExtractor, scan_to_unit_end

# ─────────────────────────────────────────────────────────────────────────────
# NOTE ON APPROACH
# ─────────────────────────────────────────────────────────────────────────────
# Oracle Forms (.fmb/.mmb/.pll) is a proprietary binary format. This extractor
# reads Oracle's own text/XML exports:
#   - JDAPI or frmf2xml/frmcmp → XML export (.frmxml / .mmxml / .pllxml)
#   - Forms Builder "Save Module As Text" → .fmt / .mmt / .pld
#
# Enhancements over original:
#   - Trigger event type captured (WHEN-VALIDATE-ITEM, PRE-INSERT, ON-ERROR, etc.)
#   - Block → DB table link captured (DML_DATA_TARGET_NAME attribute)
#   - Item UI type captured (TEXT_ITEM, CHECK_BOX, LIST_ITEM, RADIO_GROUP, etc.)
#   - Parameter data type and default value captured
#   - Block DML permissions captured (INSERT/UPDATE/DELETE allowed flags)
#   - Full trigger body — no 4000-char truncation
#   - Full program unit body — no 4000-char truncation
# ─────────────────────────────────────────────────────────────────────────────

FORMS_XML_EXTENSIONS = {".frmxml", ".mmxml", ".pllxml"}
FORMS_TEXT_EXTENSIONS = {".fmt", ".mmt", ".pld"}

_FORMS_XML_ROOT_RE = re.compile(
    r"<\s*(FormModule|MenuModule|LibraryModule|PLLModule|MMBModule)\b",
    re.IGNORECASE,
)


def looks_like_oracle_forms_xml(file_path: str) -> bool:
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as fh:
            head = fh.read(2048)
    except OSError:
        return False
    return bool(_FORMS_XML_ROOT_RE.search(head))


# Ordered (first match wins) substring classifiers for XML tag names.
_TAG_CLASSIFIERS = [
    ("MENUITEM", "menu_item"),
    ("TRIGGER", "trigger"),
    ("PROGRAMUNIT", "program_unit"),
    ("PROGRAM_UNIT", "program_unit"),
    ("LIBRARYUNIT", "program_unit"),
    ("RECORDGROUP", "record_group"),
    ("BLOCK", "block"),
    ("CANVAS", "canvas"),
    ("WINDOW", "window"),
    ("LOV", "lov"),
    ("ALERT", "alert"),
    ("PARAMETER", "parameter"),
    ("MENU", "menu"),
    ("ITEM", "item"),
]

_NAME_ATTR_CANDIDATES = ("Name", "NAME", "name", "id", "ID")
_TEXT_TAG_HINTS = ("TRIGGERTEXT", "PLSQLTEXT", "TEXT", "SOURCE", "BODY")

# Forms trigger names always start with one of these prefixes
_TRIGGER_NAME_RE = re.compile(
    r"^(WHEN|PRE|POST|KEY|ON)-[A-Z0-9\-]+$"
)

_STRUCTURAL_MARKER_RE = re.compile(
    r"^\s*(MODULE|FORM|BLOCK|ITEM|CANVAS|WINDOW|ALERT|LOV|RECORD\s*GROUP|"
    r"PARAMETER|MENU\s*ITEM|MENU)\s*[:=]?\s*([\w\-\.]+)\s*$",
    re.IGNORECASE,
)

# Attribute names used in Oracle Forms XML for block DB source
_BLOCK_DB_ATTRS = ("DmlDataTargetName", "DML_DATA_TARGET_NAME", "QueryDataSourceName",
                   "QUERY_DATA_SOURCE_NAME", "DataSourceName", "DATA_SOURCE_NAME")

# Attribute names for item type
_ITEM_TYPE_ATTRS = ("ItemType", "ITEM_TYPE", "Type", "TYPE")

# Attribute names for item data type / max length
_ITEM_DATATYPE_ATTRS = ("DataType", "DATA_TYPE", "MaximumLength", "MAXIMUM_LENGTH")

# Attribute names for DML permissions on block
_BLOCK_INSERT_ATTR = ("InsertAllowed", "INSERT_ALLOWED")
_BLOCK_UPDATE_ATTR = ("UpdateAllowed", "UPDATE_ALLOWED")
_BLOCK_DELETE_ATTR = ("DeleteAllowed", "DELETE_ALLOWED")

# Attribute names for parameter
_PARAM_TYPE_ATTRS = ("ParamDataType", "PARAM_DATA_TYPE", "DataType", "DATA_TYPE")
_PARAM_DEFAULT_ATTRS = ("ParamInitialValue", "PARAM_INITIAL_VALUE", "InitialValue", "INITIAL_VALUE")


class OracleFormsExtractor(BaseExtractor):
    """
    Extracts business artefacts from exported Oracle Forms/Menu/Library text or XML.
    Captures: triggers (with event type), blocks (with DB table link + DML permissions),
    items (with UI type + data type), parameters (with type + default), program units.
    """

    def __init__(self):
        self._plsql = PlsqlExtractor()

    def extract(self, file_path: str) -> List[Dict]:
        ext = Path(file_path).suffix.lower()

        if ext in FORMS_XML_EXTENSIONS:
            return self._extract_from_xml(file_path)
        if ext in FORMS_TEXT_EXTENSIONS:
            return self._extract_from_text(file_path)
        if ext == ".xml" and looks_like_oracle_forms_xml(file_path):
            return self._extract_from_xml(file_path)
        return []

    # ── XML export ────────────────────────────────────────────────────────────

    def _extract_from_xml(self, file_path: str) -> List[Dict]:
        try:
            tree = ET.parse(file_path)
        except (ET.ParseError, OSError):
            return []

        artifacts: List[Dict] = []
        self._walk_xml(tree.getroot(), file_path,
                       context={"block": "", "item": "", "block_table": ""}, out=artifacts)
        return artifacts

    def _walk_xml(self, elem: ET.Element, file_path: str, context: Dict, out: List[Dict]):
        tag = self._classify_tag(elem.tag)
        name = self._get_name(elem)
        child_context = dict(context)

        if tag == "block":
            db_table = self._get_attr(elem, _BLOCK_DB_ATTRS)
            insert_ok = self._get_attr(elem, _BLOCK_INSERT_ATTR) or ""
            update_ok = self._get_attr(elem, _BLOCK_UPDATE_ATTR) or ""
            delete_ok = self._get_attr(elem, _BLOCK_DELETE_ATTR) or ""
            child_context["block"] = name or context.get("block", "")
            child_context["block_table"] = db_table or context.get("block_table", "")
            child_context["item"] = ""
            out.append(self._structural_artifact(file_path, "block", name, child_context, extra={
                "db_table": db_table,
                "insert_allowed": insert_ok.upper() not in ("FALSE", "NO", "0"),
                "update_allowed": update_ok.upper() not in ("FALSE", "NO", "0"),
                "delete_allowed": delete_ok.upper() not in ("FALSE", "NO", "0"),
            }))

        elif tag == "item" and name:
            item_type = self._get_attr(elem, _ITEM_TYPE_ATTRS) or ""
            data_type = self._get_attr(elem, _ITEM_DATATYPE_ATTRS) or ""
            child_context["item"] = name
            out.append(self._structural_artifact(file_path, "item", name, child_context, extra={
                "item_type": item_type,
                "data_type": data_type,
            }))

        elif tag == "parameter":
            param_type = self._get_attr(elem, _PARAM_TYPE_ATTRS) or ""
            param_default = self._get_attr(elem, _PARAM_DEFAULT_ATTRS) or ""
            out.append(self._structural_artifact(file_path, "parameter", name, child_context, extra={
                "param_type": param_type,
                "param_default": param_default,
            }))

        elif tag in ("canvas", "window", "lov", "record_group", "alert", "menu", "menu_item"):
            out.append(self._structural_artifact(file_path, tag, name, child_context))

        elif tag == "trigger" and name:
            body = self._get_body_text(elem)
            # Determine event category from trigger name
            event_category = self._classify_trigger_event(name)
            out.append(self._trigger_artifact(file_path, name, body, child_context, event_category))

        elif tag == "program_unit" and name:
            body = self._get_body_text(elem)
            out.append(self._program_unit_artifact(file_path, name, body, child_context))

        for child in elem:
            self._walk_xml(child, file_path, child_context, out)

    @staticmethod
    def _classify_tag(tag: str) -> Optional[str]:
        local = tag.split("}")[-1].upper()
        for needle, label in _TAG_CLASSIFIERS:
            if needle in local:
                return label
        return None

    @staticmethod
    def _get_name(elem: ET.Element) -> str:
        for attr in _NAME_ATTR_CANDIDATES:
            if attr in elem.attrib and elem.attrib[attr]:
                return elem.attrib[attr]
        for child in elem:
            local = child.tag.split("}")[-1].upper()
            if "NAME" in local and child.text:
                return child.text.strip()
        return ""

    @staticmethod
    def _get_attr(elem: ET.Element, attr_candidates) -> Optional[str]:
        """Try multiple attribute name variants (Oracle Forms version differences)."""
        # Direct attributes
        for attr in attr_candidates:
            if attr in elem.attrib and elem.attrib[attr]:
                return elem.attrib[attr]
        # Child element tags
        for child in elem:
            local = child.tag.split("}")[-1].upper()
            for attr in attr_candidates:
                if attr.upper() in local and child.text:
                    return child.text.strip()
        return None

    @staticmethod
    def _get_body_text(elem: ET.Element) -> str:
        for child in elem.iter():
            local = child.tag.split("}")[-1].upper()
            if any(hint in local for hint in _TEXT_TAG_HINTS) and child.text and child.text.strip():
                return child.text
        return "".join(elem.itertext())

    @staticmethod
    def _classify_trigger_event(trigger_name: str) -> str:
        """Classify trigger event category from its name prefix."""
        name_upper = trigger_name.upper()
        if name_upper.startswith("WHEN-VALIDATE"):
            return "validation"
        elif name_upper.startswith("WHEN-NEW"):
            return "navigation"
        elif name_upper.startswith("WHEN-BUTTON"):
            return "user_action"
        elif name_upper.startswith("WHEN-LIST") or name_upper.startswith("WHEN-CHECKBOX"):
            return "user_action"
        elif name_upper.startswith("PRE-INSERT") or name_upper.startswith("POST-INSERT"):
            return "dml_insert"
        elif name_upper.startswith("PRE-UPDATE") or name_upper.startswith("POST-UPDATE"):
            return "dml_update"
        elif name_upper.startswith("PRE-DELETE") or name_upper.startswith("POST-DELETE"):
            return "dml_delete"
        elif name_upper.startswith("PRE-QUERY") or name_upper.startswith("POST-QUERY"):
            return "query"
        elif name_upper.startswith("ON-"):
            return "override"
        elif name_upper.startswith("KEY-"):
            return "keyboard"
        elif name_upper.startswith("PRE-FORM") or name_upper.startswith("POST-FORM"):
            return "form_lifecycle"
        elif name_upper.startswith("PRE-BLOCK") or name_upper.startswith("POST-BLOCK"):
            return "block_lifecycle"
        else:
            return "other"

    # ── plain text export ────────────────────────────────────────────────────

    def _extract_from_text(self, file_path: str) -> List[Dict]:
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as fh:
                content = fh.read()
        except OSError:
            return []

        artifacts: List[Dict] = []
        artifacts.extend(self._plsql._extract_standalone_procs_and_funcs(content, file_path))

        lines = content.split("\n")
        current_block, current_item, current_block_table = "", "", ""
        i = 0
        while i < len(lines):
            line = lines[i]
            stripped = line.strip()

            marker = _STRUCTURAL_MARKER_RE.match(line)
            if marker:
                kind_raw = marker.group(1).upper().replace(" ", "")
                name = marker.group(2)
                kind_map = {
                    "MODULE": "module", "FORM": "module", "BLOCK": "block",
                    "ITEM": "item", "CANVAS": "canvas", "WINDOW": "window",
                    "ALERT": "alert", "LOV": "lov", "RECORDGROUP": "record_group",
                    "PARAMETER": "parameter", "MENUITEM": "menu_item", "MENU": "menu",
                }
                kind = kind_map.get(kind_raw, "structural")
                if kind == "block":
                    current_block, current_item, current_block_table = name, "", ""
                    # Try to find TABLE= or QUERY DATA SOURCE on next few lines
                    for j in range(i + 1, min(i + 10, len(lines))):
                        tbl_match = re.match(
                            r"\s*(?:TABLE|DML_DATA_TARGET_NAME|QUERY_DATA_SOURCE_NAME)\s*=\s*(\w+)",
                            lines[j], re.IGNORECASE
                        )
                        if tbl_match:
                            current_block_table = tbl_match.group(1)
                            break
                elif kind == "item":
                    current_item = name
                context = {"block": current_block, "item": current_item, "block_table": current_block_table}
                artifacts.append(self._structural_artifact(file_path, kind, name, context))
                i += 1
                continue

            if _TRIGGER_NAME_RE.match(stripped):
                trigger_name = stripped
                body_start_pos = sum(len(l) + 1 for l in lines[:i + 1])
                end_pos = scan_to_unit_end(content, body_start_pos)
                body = content[body_start_pos:end_pos]
                event_category = self._classify_trigger_event(trigger_name)
                context = {"block": current_block, "item": current_item, "block_table": current_block_table}
                artifacts.append(self._trigger_artifact(file_path, trigger_name, body, context, event_category))
                consumed_lines = content.count("\n", 0, end_pos) - i
                i += max(consumed_lines, 1)
                continue

            i += 1

        return artifacts

    # ── artifact builders ────────────────────────────────────────────────────

    def _structural_artifact(self, file_path: str, kind: str, name: str,
                              context: Dict, extra: Optional[Dict] = None) -> Dict:
        meta = {
            "block": context.get("block", ""),
            "item": context.get("item", ""),
            "block_table": context.get("block_table", ""),
        }
        if extra:
            meta.update(extra)
        return self.make_artifact(
            language="oracle_forms",
            source_file=file_path,
            type=kind,
            name=name or f"unnamed_{kind}",
            content=f"{kind}: {name}",
            metadata=meta,
            is_business_artifact=False,
            business_category="ui_structure",
        )

    def _trigger_artifact(self, file_path: str, name: str, body: str,
                           context: Dict, event_category: str = "") -> Dict:
        return self.make_artifact(
            language="oracle_forms",
            source_file=file_path,
            type="forms_trigger",
            name=name,
            content=body,   # no truncation
            metadata={
                "block": context.get("block", ""),
                "item": context.get("item", ""),
                "block_table": context.get("block_table", ""),
                "trigger_event": name,
                "event_category": event_category,
            },
            is_business_artifact=True,
            business_category="trigger_logic",
        )

    def _program_unit_artifact(self, file_path: str, name: str, body: str, context: Dict) -> Dict:
        is_business = self.is_business_method(name)
        return self.make_artifact(
            language="oracle_forms",
            source_file=file_path,
            type="program_unit",
            name=name,
            content=body,   # no truncation
            metadata={
                "block": context.get("block", ""),
                "item": context.get("item", ""),
            },
            is_business_artifact=is_business,
            business_category=self.get_business_category(name),
        )
