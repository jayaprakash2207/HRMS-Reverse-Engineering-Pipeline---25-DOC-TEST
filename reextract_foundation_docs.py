"""
Re-extracts all 25 Foundation documents from Foundation_Raw_Output_Part1.md
and Foundation_Raw_Output_Part2.md without any Claude calls.

The raw files contain all content — some docs have === DOCUMENT: filename === markers,
others are embedded without markers. This script handles both cases.
"""
from pathlib import Path

RESULTS = Path("c:/rev-eng1 test oracle new/automated-reverse-engineering-pipeline-main/automated-reverse-engineering-pipeline-main/results")
FWDENG  = RESULTS / "ForwardEngineering_Docs"
KG_DIR  = RESULTS / "Foundation_KnowledgeGraph"
FWDENG.mkdir(exist_ok=True)
KG_DIR.mkdir(exist_ok=True)

part1 = (RESULTS / "Foundation_Raw_Output_Part1.md").read_text(encoding="utf-8")
part2 = (RESULTS / "Foundation_Raw_Output_Part2.md").read_text(encoding="utf-8")

lines1 = part1.splitlines()
lines2 = part2.splitlines()

def find_line(lines, pattern, start=0):
    for i in range(start, len(lines)):
        if pattern in lines[i]:
            return i
    return -1

def extract_between(lines, start_line, end_patterns, include_start=True):
    """Extract lines from start_line until any end_pattern is found."""
    result = []
    begin = start_line if include_start else start_line + 1
    for i in range(begin, len(lines)):
        line = lines[i]
        if any(p in line for p in end_patterns):
            break
        result.append(line)
    return "\n".join(result).strip()

def extract_by_marker(lines, filename):
    """Extract doc that has === DOCUMENT: filename === marker."""
    start = find_line(lines, f"=== DOCUMENT: {filename} ===")
    if start == -1:
        return None
    # skip the marker line itself
    content_lines = []
    for i in range(start + 1, len(lines)):
        l = lines[i]
        if l.startswith("=== DOCUMENT:") or l.startswith("END OF DOCUMENT"):
            break
        content_lines.append(l)
    return "\n".join(content_lines).strip()

saved = []

# ─── Part1: docs 01-04 are at the beginning without markers ───────────────────
# Doc 01-04 start from line 0 and end at "END OF DOCUMENT 04_BUSINESS_PROCESS_MODEL.md"
# We need to look for structural sections

# Find the BRD section — it's the very start of Part1 (payroll process tree starts it)
# The content before === DOCUMENT: 05_DOMAIN_MODEL.md === is docs 01-04 combined
end_of_04 = find_line(lines1, "END OF DOCUMENT 04_BUSINESS_PROCESS_MODEL.md")
doc_05_start = find_line(lines1, "=== DOCUMENT: 05_DOMAIN_MODEL.md ===")

# Part1 begins mid-content — get full Part1 content before doc 05
pre_05 = "\n".join(lines1[:end_of_04 if end_of_04 > 0 else doc_05_start]).strip()

# Look for section markers within pre_05 to split 01-04
pre_lines = pre_05.splitlines()

# BRD (01): everything from start until we see BUSINESS_CAPABILITY or doc 02 heading
# These docs are flowing content — identify by looking for === headings
section_starts = []
for i, l in enumerate(pre_lines):
    if l.startswith("=== ") and not l.startswith("=== DOCUMENT:") and not l.startswith("=== PROCESS"):
        section_starts.append((i, l))

# Find PROCESS sections for 04_BUSINESS_PROCESS_MODEL
process_starts = []
for i, l in enumerate(pre_lines):
    if l.startswith("=== PROCESS"):
        process_starts.append(i)

# Doc 04: PROCESS 1 through PROCESS 7 (everything from first === PROCESS to end)
if process_starts:
    doc04_start = process_starts[0]
    doc04_content = "\n".join(pre_lines[doc04_start:]).strip()
    doc04_full = "# 04 — Business Process Model\n\n" + doc04_content
    (FWDENG / "04_BUSINESS_PROCESS_MODEL.md").write_text(doc04_full, encoding="utf-8")
    saved.append("04_BUSINESS_PROCESS_MODEL.md")
    print(f"  Saved 04_BUSINESS_PROCESS_MODEL.md ({len(doc04_full)} chars)")

    # Docs 01-03: everything before first PROCESS section
    pre_process = "\n".join(pre_lines[:doc04_start]).strip()
else:
    pre_process = pre_05

# Try to find 01, 02, 03 within pre_process
pp_lines = pre_process.splitlines()

# Look for major heading patterns that indicate doc boundaries
# 01_BRD typically starts with "# 01" or "# Business Requirements"
# 02_BUSINESS_CAPABILITY with "# 02" or capability headings
# 03_USE_CASE with "# 03" or use case headings

boundaries = []
for i, l in enumerate(pp_lines):
    stripped = l.strip()
    if stripped.startswith("# 01") or "Business Requirements Document" in stripped:
        boundaries.append((i, "01"))
    elif stripped.startswith("# 02") or ("Business Capability" in stripped and stripped.startswith("#")):
        boundaries.append((i, "02"))
    elif stripped.startswith("# 03") or ("Use Case" in stripped and stripped.startswith("#")):
        boundaries.append((i, "03"))

# Deduplicate keeping first occurrence of each
seen_nums = {}
clean_boundaries = []
for (idx, num) in boundaries:
    if num not in seen_nums:
        seen_nums[num] = idx
        clean_boundaries.append((idx, num))
clean_boundaries.sort()

doc_names = {
    "01": ("01_BRD.md", "# 01 — Business Requirements Document"),
    "02": ("02_BUSINESS_CAPABILITY_MODEL.md", "# 02 — Business Capability Model"),
    "03": ("03_USE_CASE_SPECIFICATION.md", "# 03 — Use Case Specification"),
}

for i, (start_idx, num) in enumerate(clean_boundaries):
    end_idx = clean_boundaries[i+1][0] if i+1 < len(clean_boundaries) else len(pp_lines)
    content = "\n".join(pp_lines[start_idx:end_idx]).strip()
    fname, default_heading = doc_names[num]
    if not content:
        content = default_heading + "\n\n(Content embedded in business process section — see 04_BUSINESS_PROCESS_MODEL.md for process flows)"
    (FWDENG / fname).write_text(content, encoding="utf-8")
    saved.append(fname)
    print(f"  Saved {fname} ({len(content)} chars)")

# If boundaries weren't found, write what we have as BRD
if not clean_boundaries and pre_process.strip():
    content = pre_process.strip()
    (FWDENG / "01_BRD.md").write_text(content, encoding="utf-8")
    saved.append("01_BRD.md")
    print(f"  Saved 01_BRD.md ({len(content)} chars) [full pre-process content]")

# ─── Part1: docs 05 and 06 have proper markers ────────────────────────────────
for fname in ["05_DOMAIN_MODEL.md", "06_DATA_DICTIONARY.md"]:
    content = extract_by_marker(lines1, fname)
    if content:
        (FWDENG / fname).write_text(content, encoding="utf-8")
        saved.append(fname)
        print(f"  Saved {fname} ({len(content)} chars)")

# ─── Part2: docs 07-16 are at beginning without markers, 17-20 have markers ──
# Find where doc 17 marker starts
doc17_start = find_line(lines2, "=== DOCUMENT: 17_FORWARD_ENGINEERING_READINESS_REPORT.md ===")

# Everything before doc 17 is docs 07-16 + Knowledge Graph JSON
pre_17 = "\n".join(lines2[:doc17_start]).strip() if doc17_start > 0 else ""
pre17_lines = pre_17.splitlines() if pre_17 else []

# Find the Knowledge Graph JSON block
kg_json_start = find_line(pre17_lines, '"enterprise_knowledge_graph"')
if kg_json_start == -1:
    kg_json_start = find_line(pre17_lines, "ENTERPRISE_KNOWLEDGE_GRAPH")
if kg_json_start == -1:
    kg_json_start = find_line(pre17_lines, '"entities"')

# Find ```json block start before the KG
json_block_start = -1
for i in range(max(0, kg_json_start - 5), min(len(pre17_lines), kg_json_start + 2)):
    if "```json" in pre17_lines[i] or pre17_lines[i].strip() == "{":
        json_block_start = i
        break

# Find the closing ``` or } of the JSON
json_block_end = -1
if json_block_start > -1:
    brace_depth = 0
    for i in range(json_block_start, len(pre17_lines)):
        l = pre17_lines[i]
        if "```" in l and i > json_block_start:
            json_block_end = i
            break
        brace_depth += l.count("{") - l.count("}")
        if brace_depth <= 0 and i > json_block_start + 5:
            json_block_end = i
            break

# Find major headings for docs 07-16
doc_heading_patterns = [
    ("07", "07_DATA_MODEL_SPECIFICATION.md", ["# 07", "Data Model Specification", "## Data Model"]),
    ("08", "08_ERD.md", ["# 08", "Entity Relationship Diagram", "## ERD", "## Entity"]),
    ("09", "09_DATA_FLOW_DIAGRAM.md", ["# 09", "Data Flow Diagram"]),
    ("10", "10_SERVICE_CATALOG.md", ["# 10", "Service Catalog"]),
    ("11", "11_API_CONTRACT_SPECIFICATION.md", ["# 11", "API Contract"]),
    ("12", "12_TECHNOLOGY_BLUEPRINT.md", ["# 12", "Technology Blueprint"]),
    ("13", "13_SECURITY_ARCHITECTURE.md", ["# 13", "Security Architecture"]),
    ("14", "14_NFR_SPECIFICATION.md", ["# 14", "NFR Specification", "Non-Functional"]),
    ("15", "15_FORWARD_ENGINEERING_SPECIFICATION.md", ["# 15", "Forward Engineering Specification"]),
    ("16", "16_GENERATION_MANIFEST.md", ["# 16", "Generation Manifest", "generation_manifest"]),
]

# Find heading positions in pre17_lines
found_docs = []
for num, fname, patterns in doc_heading_patterns:
    for i, l in enumerate(pre17_lines):
        stripped = l.strip()
        if any(p in stripped for p in patterns) and stripped.startswith("#"):
            found_docs.append((i, num, fname))
            break

found_docs.sort()

# Also check if the KG JSON exists as its own section
kg_section_start = -1
for i, l in enumerate(pre17_lines):
    if '"enterprise_knowledge_graph"' in l or (l.strip() == "{" and i < 10):
        kg_section_start = i
        break

# Extract each doc between heading boundaries
for i, (start_idx, num, fname) in enumerate(found_docs):
    end_idx = found_docs[i+1][0] if i+1 < len(found_docs) else (doc17_start if doc17_start > 0 else len(pre17_lines))
    content = "\n".join(pre17_lines[start_idx:end_idx]).strip()
    if content:
        target_dir = FWDENG
        if not (FWDENG / fname).exists() or len((FWDENG / fname).read_text(encoding="utf-8")) < len(content):
            (target_dir / fname).write_text(content, encoding="utf-8")
            saved.append(fname)
            print(f"  Saved {fname} ({len(content)} chars)")

# Extract KG JSON from Part2 beginning (it's before doc 07 headings)
if found_docs:
    first_doc_line = found_docs[0][0]
    kg_content = "\n".join(pre17_lines[:first_doc_line]).strip()
else:
    kg_content = pre_17

if kg_content:
    # Save the full KG JSON
    (KG_DIR / "ENTERPRISE_KNOWLEDGE_GRAPH.json").write_text(kg_content, encoding="utf-8")
    saved.append("ENTERPRISE_KNOWLEDGE_GRAPH.json")
    print(f"  Saved ENTERPRISE_KNOWLEDGE_GRAPH.json ({len(kg_content)} chars)")

# ─── Part2: docs 17-20 have proper markers ────────────────────────────────────
for fname in [
    "17_FORWARD_ENGINEERING_READINESS_REPORT.md",
    "18_DEPLOYMENT_ARCHITECTURE.md",
    "19_FRONTEND_ARCHITECTURE.md",
    "20_UI_UX_SPECIFICATION.md",
]:
    content = extract_by_marker(lines2, fname)
    if content:
        (FWDENG / fname).write_text(content, encoding="utf-8")
        saved.append(fname)
        print(f"  Saved {fname} ({len(content)} chars)")

# ─── Summary ──────────────────────────────────────────────────────────────────
print(f"\n{'='*60}")
print(f"Extraction complete — {len(saved)} files saved")
print(f"\nForwardEngineering_Docs/:")
for f in sorted(FWDENG.iterdir()):
    size = f.stat().st_size
    print(f"  {f.name:50s} {size:>8,} bytes")
print(f"\nFoundation_KnowledgeGraph/:")
for f in sorted(KG_DIR.iterdir()):
    size = f.stat().st_size
    print(f"  {f.name:50s} {size:>8,} bytes")
