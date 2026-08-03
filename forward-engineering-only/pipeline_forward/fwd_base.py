"""
Forward Engineering — shared helpers.
Reuses call_claude / save_output / save_json / output_already_exists from the
existing reverse-engineering pipeline's base_runner.py — no duplication.
"""

import json
import re
import sys
from pathlib import Path

# Make the existing reverse-engineering pipeline's base_runner importable.
sys.path.insert(0, str(Path(__file__).parent.parent / "pipeline"))
from base_runner import (  # noqa: E402
    call_claude,
    save_output,
    save_json,
    load_prior_output,
    output_already_exists,
)

import os
import tempfile

__all__ = [
    "call_claude", "save_output", "save_json", "load_prior_output", "output_already_exists",
    "load_reverse_engineering_docs", "has_reverse_engineering_docs",
    "load_all_sprints", "scope_doc_to_sprint",
    "write_file_bundle", "read_files_bundle", "load_target_stack", "save_target_stack",
    "atomic_write_json", "load_ledger", "update_ledger_entry",
    "append_learning", "load_learnings_text",
    "sprint_slug", "load_sprint_manifest", "save_sprint_manifest", "sprint_output_missing",
    "load_sprint_progress", "save_sprint_progress", "clear_sprint_progress", "mark_step_done",
]


# ── Load the reverse-engineering pipeline's output (if present) ───────────────

def has_reverse_engineering_docs(input_dir: str) -> bool:
    """True if the reverse-engineering pipeline already produced usable docs."""
    base = Path(input_dir)
    fwd_docs = base / "ForwardEngineering_Docs"
    return fwd_docs.exists() and any(fwd_docs.glob("*.md"))


def load_reverse_engineering_docs(input_dir: str) -> dict:
    """
    Load whatever the reverse-engineering pipeline produced.
    Tolerant of gaps — e.g. Foundation_KnowledgeGraph may be incomplete;
    callers must handle missing keys rather than assume every doc exists.
    """
    base = Path(input_dir)
    fwd_dir = base / "ForwardEngineering_Docs"
    kg_dir = base / "Foundation_KnowledgeGraph"

    def read_text(path: Path) -> str:
        return path.read_text(encoding="utf-8") if path.exists() else ""

    docs = {}
    if fwd_dir.exists():
        for p in sorted(fwd_dir.glob("*.md")):
            docs[p.name] = read_text(p)
        for p in sorted(fwd_dir.glob("*.json")):
            docs[p.name] = read_text(p)

    kg = {}
    if kg_dir.exists():
        for p in sorted(kg_dir.glob("*")):
            kg[p.name] = read_text(p)

    return {"forward_docs": docs, "knowledge_graph": kg}


# ── Per-sprint document scoping ─────────────────────────────────────────────────
# Whole-system docs (BRD, Domain Model, API Contract, ...) were being sent in
# full to every sprint's every agent call — most of a doc's content is about
# OTHER bounded contexts, not the one currently being built. Trim it down using
# the doc's own markdown section headers, deterministically, with no LLM call.

_SECTION_HEADER_RE = re.compile(r"^(#{2,4})\s*(.+?)\s*$", re.MULTILINE)

# Sections carrying any of these words apply to every sprint regardless of
# bounded context — never drop them.
_CROSS_CUTTING_KEYWORDS = (
    "cross-cutting", "cross cutting", "convention", "authentication", "auth",
    "audit", "shared", "status and grounding", "purpose", "scope", "glossary",
    "not specified", "assumption", "open question", "traceability", "grounding",
)

_STOPWORDS = {"context", "management", "the", "and", "of", "for", "a", "an"}


def _doc_keywords(name: str) -> set:
    return {w for w in re.findall(r"[a-z0-9]+", name.lower())
            if w not in _STOPWORDS and len(w) > 2}


def load_all_sprints(output_dir: str) -> list:
    """Every sprint dict ({"name", "rationale", ...}) from SPRINT_BACKLOG.json,
    or [] if not produced yet."""
    path = Path(output_dir) / "SPRINT_BACKLOG.json"
    if not path.exists():
        return []
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _sprint_name(sprint) -> str:
    return sprint.get("name", "") if isinstance(sprint, dict) else str(sprint or "")


def scope_doc_to_sprint(doc_text: str, sprint, all_sprints: list = None) -> str:
    """
    Trim a whole-system requirements doc down to the sections relevant to ONE
    sprint's bounded context, using the doc's own section headers.

    `sprint` may be the full sprint dict (preferred — its "rationale" text is
    used too, since a sprint's NAME doesn't always share vocabulary with its
    own domain section headers, e.g. sprint "Performance Context" vs. a doc
    header "Domain: Review Cycle / Individual Review"; the rationale usually
    does) or just a plain name string.

    Conservative by design — a header not mentioning THIS sprint is not enough
    reason to drop it (many docs, e.g. the BRD, are organized by topic rather
    than by bounded context, so an unmatched header is usually ambiguous, not
    irrelevant). A section is only omitted when its header clearly names a
    DIFFERENT sprint's bounded context — matched on that other sprint's NAME
    ONLY, deliberately not its rationale, to keep false-positive drops rare —
    and shows no sign of being cross-cutting or about this sprint. Everything
    ambiguous is kept. Fails open entirely (returns doc_text unchanged) if the
    doc has no real section structure, or if scoping would keep under ~15%.
    """
    if not doc_text or not doc_text.strip():
        return doc_text

    matches = list(_SECTION_HEADER_RE.finditer(doc_text))
    if len(matches) < 2:
        return doc_text

    sprint_name = _sprint_name(sprint)
    rationale = sprint.get("rationale", "") if isinstance(sprint, dict) else ""
    # NOTE: rationale is used to broaden what THIS sprint counts as relevant
    # (e.g. sprint "Performance Context" whose own rationale says "Review
    # Cycle/Individual Review" — the doc's actual header words — even though
    # the sprint NAME alone wouldn't match). Deliberately NOT used to narrow
    # anything: a rationale like Leave's "Consumes Employee master data" is a
    # real cross-sprint dependency, not noise, so a hub sprint's rationale
    # mentioning its downstream consumers by name may cause it to keep more
    # than strictly necessary — an efficiency cost, never a correctness one.
    this_kw = _doc_keywords(sprint_name) | _doc_keywords(rationale)
    other_kw_sets = [
        _doc_keywords(_sprint_name(s)) for s in (all_sprints or []) if _sprint_name(s) != sprint_name
    ]
    other_kw_sets = [kws for kws in other_kw_sets if kws]

    kept_parts = []
    omitted_titles = []
    for i, m in enumerate(matches):
        title = m.group(2)
        start = m.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(doc_text)
        title_l = title.lower()
        title_words = _doc_keywords(title)

        is_relevant = bool(title_words & this_kw) or any(kw in title_l for kw in this_kw)
        is_cross_cutting = any(kw in title_l for kw in _CROSS_CUTTING_KEYWORDS)
        belongs_to_other = any(title_words & kws for kws in other_kw_sets)

        if is_relevant or is_cross_cutting or not belongs_to_other:
            kept_parts.append(doc_text[start:end])
        else:
            omitted_titles.append(title)

    kept_text = "".join(kept_parts).strip()
    if not kept_text or len(kept_text) < 0.15 * len(doc_text):
        return doc_text  # scoping would remove too much — safer to send it all

    preamble = doc_text[:matches[0].start()].strip()
    parts = [p for p in (preamble, kept_text) if p]
    if omitted_titles:
        parts.append(
            f"[Sections omitted as out of scope for sprint '{sprint_name}': "
            + "; ".join(omitted_titles)
            + " — these belong to other bounded contexts, not this sprint.]"
        )
    return "\n\n".join(parts)


# ── Target stack state (produced by Stack Selection, read by everything after) ─

def load_target_stack(output_dir: str):
    """Return the confirmed target stack string, or None if not yet decided."""
    path = Path(output_dir) / "target_stack.json"
    if not path.exists():
        return None
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    return data.get("target_stack")


def save_target_stack(output_dir: str, target_stack: str) -> None:
    save_json(output_dir, "target_stack.json", {"target_stack": target_stack})


# ── File-bundle writer (Scaffolder writes many real files from one response) ──

_FILE_BLOCK_RE = re.compile(
    r"===\s*FILE:\s*(.+?)\s*===\s*\n(.*?)(?=\n===\s*FILE:|\Z)",
    re.DOTALL,
)


def _winlong(path: Path) -> str:
    """
    On Windows, prefix an absolute path with \\\\?\\ to opt out of the 260-char
    MAX_PATH limit for this call — harmless no-op on other platforms. Needed
    because generated Java/Maven package trees (src/main/java/com/.../SomeClass.java)
    and per-sprint state paths (forward_results/sprints/<slug>/manifest.json, plus
    tempfile.mkstemp()'s own generated name on top of that) routinely push an
    absolute path past 260 chars once the project sits inside any reasonably long
    parent folder — which raises WinError 206/ENOENT from plain mkdir()/
    write_text()/tempfile.mkstemp() with no such workaround applied. Resolves the
    path itself, so it's safe to call on a path the caller hasn't resolved yet.
    """
    if sys.platform != "win32":
        return str(path)
    s = str(Path(path).resolve())
    if s.startswith("\\\\?\\"):
        return s
    if s.startswith("\\\\"):  # UNC path
        return "\\\\?\\UNC\\" + s.lstrip("\\")
    return "\\\\?\\" + s


def write_file_bundle(raw_text: str, target_root: str) -> list:
    """
    Parse '=== FILE: path ===\\n<content>' blocks out of raw_text and write
    each as a real file under target_root. Returns the list of paths written.
    Skips any path that tries to escape target_root (defense in depth).
    """
    root = Path(target_root).resolve()
    Path(_winlong(root)).mkdir(parents=True, exist_ok=True)
    written = []

    for m in _FILE_BLOCK_RE.finditer(raw_text):
        rel_path = m.group(1).strip().strip("`").replace("\\", "/")
        content = m.group(2).strip("\n")

        candidate = (root / rel_path).resolve()
        if root not in candidate.parents and candidate != root:
            print(f"  [write_file_bundle] Skipped suspicious path outside target: {rel_path}")
            continue

        try:
            Path(_winlong(candidate.parent)).mkdir(parents=True, exist_ok=True)
            Path(_winlong(candidate)).write_text(content + "\n", encoding="utf-8")
        except OSError as exc:
            print(f"  [write_file_bundle] Failed to write {rel_path!r} ({len(str(candidate))} char "
                  f"full path): {exc}")
            continue
        written.append(str(candidate.relative_to(root)))

    return written


def read_files_bundle(target_root: str, relative_paths: list) -> str:
    """
    Inverse of write_file_bundle: read the CURRENT content of real files on disk
    and format them the same '=== FILE: path ===' way, so a later agent can be
    shown "here is what exists right now" and asked to modify it.
    Missing files are noted, not fatal.
    """
    root = Path(target_root).resolve()
    parts = []
    for rel_path in relative_paths:
        p = (root / rel_path).resolve()
        if root not in p.parents and p != root:
            continue
        if p.exists():
            parts.append(f"=== FILE: {rel_path} ===\n{p.read_text(encoding='utf-8')}")
        else:
            parts.append(f"=== FILE: {rel_path} ===\n[File does not exist yet]")
    return "\n\n".join(parts)


# ── Atomic JSON state (ledger) ─────────────────────────────────────────────────
# Same discipline as the note in orchestrator.json elsewhere in this project:
# JSON writes MUST overwrite the whole file via a temp-file + rename, never be
# partially written — a crash mid-write must never leave a corrupt/half file
# that a resume step could mistake for valid state.

def atomic_write_json(path: str, data) -> None:
    path = Path(path)
    Path(_winlong(path.parent)).mkdir(parents=True, exist_ok=True)
    # dir= must also be long-path-safe: tempfile.mkstemp() appends its own
    # random name + suffix on top of it, which is exactly what pushed this
    # over 260 chars in the first place.
    fd, tmp_path = tempfile.mkstemp(dir=_winlong(path.parent), prefix=".tmp_", suffix=".json")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        os.replace(tmp_path, _winlong(path))  # atomic on POSIX and Windows
    except Exception:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
        raise


LEDGER_FILE = "sprint_ledger.json"


def load_ledger(output_dir: str) -> dict:
    """{ sprint_name: {status, attempts, last_updated, notes} }"""
    path = Path(output_dir) / LEDGER_FILE
    if not path.exists():
        return {}
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def update_ledger_entry(output_dir: str, sprint_name: str, **fields) -> dict:
    """Read-modify-write the WHOLE ledger atomically. Never append-only."""
    import datetime
    ledger = load_ledger(output_dir)
    entry = ledger.get(sprint_name, {"status": "NOT_STARTED", "attempts": 0, "notes": []})
    entry.update(fields)
    entry["last_updated"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    ledger[sprint_name] = entry
    atomic_write_json(str(Path(output_dir) / LEDGER_FILE), ledger)
    return entry


# ── Per-attempt step progress (interruption resume) ────────────────────────────
# Without this, killing the batch mid-sprint (out of budget, network drop,
# Ctrl+C) and re-running from the same command re-does every step of that
# sprint's current attempt from "backend" again — even the ones that already
# succeeded and already wrote their files last time. This tracks which of the
# attempt's checkpoints ("backend", "security", "frontend", "migration",
# "test_writer", "test_executor", "review") have actually completed, so a
# restart can skip straight to the first one that hasn't.

PROGRESS_FILE = "progress.json"
SPRINT_STEPS = ("backend", "security", "frontend", "migration", "test_writer",
                "test_executor", "review")


def _progress_path(output_dir: str, sprint_name: str) -> Path:
    return Path(output_dir) / "sprints" / sprint_slug(sprint_name) / PROGRESS_FILE


def load_sprint_progress(output_dir: str, sprint_name: str, attempt: int) -> dict:
    """
    Returns {"attempt": N, "completed_steps": [...], "test_result": {...}|None,
    "review": {...}|None} for the CURRENT attempt. If the saved state belongs
    to a different attempt (a fresh attempt/retry, not a resume), returns a
    clean slate for `attempt` instead — completed_steps from a superseded
    attempt must never be reused, only completed_steps from a crash *within*
    the same attempt.
    """
    path = _progress_path(output_dir, sprint_name)
    if path.exists():
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        if data.get("attempt") == attempt:
            return data
    return {"attempt": attempt, "completed_steps": [], "test_result": None, "review": None}


def save_sprint_progress(output_dir: str, sprint_name: str, progress: dict) -> None:
    atomic_write_json(str(_progress_path(output_dir, sprint_name)), progress)


def mark_step_done(output_dir: str, sprint_name: str, progress: dict, step: str, **extra) -> dict:
    """Record `step` as completed for the current attempt and persist immediately —
    so a kill at any later point only ever loses the one step still in flight."""
    if step not in progress["completed_steps"]:
        progress["completed_steps"].append(step)
    progress.update(extra)
    save_sprint_progress(output_dir, sprint_name, progress)
    return progress


def clear_sprint_progress(output_dir: str, sprint_name: str) -> None:
    """Attempt reached a terminal state (PASSED/FAILED_BLOCKED) — progress.json
    is only meaningful mid-attempt, so drop it."""
    path = _progress_path(output_dir, sprint_name)
    if path.exists():
        path.unlink()


# ── Learnings memory ───────────────────────────────────────────────────────────
# Accumulates root causes across sprints so a later sprint's agents can avoid
# repeating a mistake an earlier sprint already paid to fix.

LEARNINGS_JSON = "LEARNINGS.json"
LEARNINGS_MD = "LEARNINGS.md"


def append_learning(output_dir: str, sprint_name: str, issue: str, root_cause: str,
                     fix_applied: str, outcome: str) -> None:
    import datetime
    path = Path(output_dir) / LEARNINGS_JSON
    learnings = []
    if path.exists():
        with open(path, encoding="utf-8") as f:
            learnings = json.load(f)

    learnings.append({
        "sprint": sprint_name,
        "issue": issue,
        "root_cause": root_cause,
        "fix_applied": fix_applied,
        "outcome": outcome,
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    })
    atomic_write_json(str(path), learnings)

    # Human-readable mirror — full rewrite each time, not appended, so it can
    # never be left half-written either.
    md_lines = ["# Learnings Log", ""]
    for entry in learnings:
        md_lines += [
            f"## {entry['sprint']} — {entry['outcome']}",
            f"- **Issue:** {entry['issue']}",
            f"- **Root cause:** {entry['root_cause']}",
            f"- **Fix applied:** {entry['fix_applied']}",
            "",
        ]
    (Path(output_dir) / LEARNINGS_MD).write_text("\n".join(md_lines), encoding="utf-8")


def load_learnings_text(output_dir: str, limit: int = 15) -> str:
    """Formatted for inclusion in a later agent's prompt. Empty string if none yet.

    Only entries fire (append_learning is called on FAILED_BLOCKED, not on
    every sprint), so this stays small on a smooth run — but on a long run
    where several sprints struggle, the list only ever grows, and a sprint
    late in the backlog would otherwise resend every earlier sprint's
    learnings even when most are irrelevant to it. Capped to the most recent
    `limit` entries rather than filtered by relevance — this only fires on
    failures, so it's not worth the complexity of dependency-graph filtering
    for that path.
    """
    path = Path(output_dir) / LEARNINGS_JSON
    if not path.exists():
        return ""
    with open(path, encoding="utf-8") as f:
        learnings = json.load(f)
    if not learnings:
        return ""
    recent = learnings[-limit:]
    lines = ["Known issues from earlier sprints — do not repeat these mistakes:"]
    if len(learnings) > limit:
        lines.append(f"(showing the {limit} most recent of {len(learnings)} total)")
    for entry in recent:
        lines.append(f"- [{entry['sprint']}] {entry['root_cause']} → fix: {entry['fix_applied']}")
    return "\n".join(lines)


# ── Per-sprint file manifest ────────────────────────────────────────────────────
# Tracks which files (relative to new_app/) belong to each sprint, so later
# steps (Test-Writer, Reviewers, Fix loop) know exactly what's in scope.

def sprint_slug(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")


def load_sprint_manifest(output_dir: str, sprint_name: str) -> dict:
    path = Path(output_dir) / "sprints" / sprint_slug(sprint_name) / "manifest.json"
    if not path.exists():
        return {"backend_files": [], "security_files": [], "frontend_files": [],
                "migration_files": [], "test_files": []}
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save_sprint_manifest(output_dir: str, sprint_name: str, manifest: dict) -> None:
    path = Path(output_dir) / "sprints" / sprint_slug(sprint_name) / "manifest.json"
    atomic_write_json(str(path), manifest)


def sprint_output_missing(output_dir: str, sprint_name: str) -> bool:
    """True if this sprint's manifest lists files but NONE of them exist on
    disk anymore. Signals a stale ledger entry — e.g. new_app/ was deleted or
    reset (to start over) after a sprint was already marked PASSED/
    FAILED_BLOCKED — so the caller shouldn't just silently skip it forever;
    it needs to run again. False (not missing) when nothing was ever tracked
    for this sprint — that's simply not this check's concern."""
    manifest = load_sprint_manifest(output_dir, sprint_name)
    all_files = (
        manifest.get("backend_files", []) + manifest.get("security_files", [])
        + manifest.get("frontend_files", []) + manifest.get("test_files", [])
        + manifest.get("migration_files", [])
    )
    if not all_files:
        return False
    new_app_dir = Path(output_dir) / "new_app"
    return not any((new_app_dir / f).exists() for f in all_files)
