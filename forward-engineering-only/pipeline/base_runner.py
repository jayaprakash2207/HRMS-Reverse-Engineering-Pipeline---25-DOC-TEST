"""
Base runner — shared Claude CLI invocation, Layer 1 loading, and output helpers.
All agent runners import from here.
"""

import datetime
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

# The CLI's account-level default model (Fable 5) requires separate usage
# credits this account doesn't have, which makes every call exit 1 with no
# useful stderr. Pin an explicit model that works; override via env var if
# a different model is available on the account.
CLAUDE_MODEL = os.environ.get("PIPELINE_CLAUDE_MODEL", "claude-sonnet-5")

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# ── Claude CLI ─────────────────────────────────────────────────────────────────

def claude_cmd(allow_tools: bool = True, system_prompt_file: str = None) -> list:
    """Return base claude CLI command. Headless, no session persistence.

    --output-format json (rather than text) is required to read back per-call
    token/cost usage — see call_claude()'s usage-logging block below.

    system_prompt_file, when given, goes out via --append-system-prompt-file
    (a path) rather than --append-system-prompt (inline text) or being folded
    into the piped stdin prompt. This isn't cosmetic, and it isn't just a
    style choice either: a real, full-size system prompt (contract + scoped
    docs, tens of thousands of characters) passed inline blows straight
    through Windows' command-line length limit — cmd.exe caps out around
    8,000 characters — so Windows refuses to even start the process,
    producing "The command line is too long" with returncode 1 (a lesson
    learned the hard way — this shipped once as --append-system-prompt with
    inline text, verified only against a small test string, and broke every
    single call in a real run). Only a short file path goes on the command
    line this way, which sidesteps the limit entirely.

    Prompt caching itself is unaffected by this — confirmed empirically (a
    second call with identical --append-system-prompt-file content dropped
    from $0.17 to $0.017, a ~90% reduction, with zero session persistence
    involved) keyed on byte-identical prefix content, not on local session
    state — so separate "claude -p --no-session-persistence" processes DO
    share a cache as long as they carry the same system-prompt text within
    the (1h ephemeral, per observed usage.cache_creation.ephemeral_1h_input_tokens)
    cache window. --exclude-dynamic-system-prompt-sections moves per-run bits
    (cwd, git status, memory paths) out of the cached prefix so they can't
    invalidate it call to call.
    """
    # Checked on every platform now — the previous win32 branch skipped this
    # check entirely and just assumed "claude" existed, so a missing CLI
    # only surfaced after 3 retries x 30s waits inside call_claude(), with a
    # cryptic cmd.exe error at the end instead of an immediate clear one.
    found = shutil.which("claude")
    if not found:
        raise FileNotFoundError(
            "claude CLI not found on PATH.\n"
            "Install with:  npm install -g @anthropic-ai/claude-code\n"
            "Then authenticate with:  claude login\n"
            "Verify with:  claude -p \"say hello\" --output-format text"
        )
    if sys.platform == "win32":
        base = ["cmd", "/c", "claude", "-p", "--output-format", "json", "--no-session-persistence", "--model", CLAUDE_MODEL]
    else:
        base = [found, "-p", "--output-format", "json", "--no-session-persistence", "--model", CLAUDE_MODEL]
    if allow_tools:
        base += ["--permission-mode", "acceptEdits"]
    if system_prompt_file:
        base += ["--append-system-prompt-file", system_prompt_file, "--exclude-dynamic-system-prompt-sections"]
    return base


def _log_usage(output_dir: str, label: str, data: dict) -> None:
    """Append one usage record to <output_dir>/token_usage_log.jsonl and print
    a one-line summary. Logging must never be able to break the pipeline —
    any failure here is swallowed."""
    usage = data.get("usage") or {}
    entry = {
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "label": label,
        "input_tokens": usage.get("input_tokens", 0),
        "cache_creation_input_tokens": usage.get("cache_creation_input_tokens", 0),
        "cache_read_input_tokens": usage.get("cache_read_input_tokens", 0),
        "output_tokens": usage.get("output_tokens", 0),
        "total_cost_usd": data.get("total_cost_usd", 0.0),
    }
    total_in = entry["input_tokens"] + entry["cache_creation_input_tokens"] + entry["cache_read_input_tokens"]
    cache_pct = (100 * entry["cache_read_input_tokens"] / total_in) if total_in else 0
    print(f"  [{label}] tokens: in={entry['input_tokens']} "
          f"cache_write={entry['cache_creation_input_tokens']} "
          f"cache_read={entry['cache_read_input_tokens']} out={entry['output_tokens']} "
          f"cost=${entry['total_cost_usd']:.4f}"
          + (f"  ({cache_pct:.0f}% cached)" if cache_pct else ""))

    if not output_dir:
        return
    try:
        path = Path(output_dir) / "token_usage_log.jsonl"
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except OSError as exc:
        print(f"  [{label}] (could not write token_usage_log.jsonl: {exc})")


# allow_tools=False steps (Stack Selection, Stack Mapping, Scaffolder) ask Claude
# to return a document as plain response text — Python does the actual file
# writing. Without --permission-mode acceptEdits, Claude occasionally still
# attempts a Write/Edit tool call anyway (e.g. reading "produce a document
# named X.md" as an instruction to save X.md itself), which headless -p mode
# can never approve — Claude then returns an explanation of being blocked as
# its final text instead of the document, and that explanation gets silently
# saved and treated as valid content by every step downstream. Catch that
# shape of response here and retry instead of returning it as success.
_BLOCKED_RESPONSE_MARKERS = (
    "waiting on write permission",
    "waiting for write permission",
    "please approve the write",
    "blocked waiting",
    "which would you like",
    "let me know which",
    "i did not treat this as",
    "i did not act on",
)


def _looks_blocked_or_unresolved(text: str) -> bool:
    lowered = text.lower()
    return any(marker in lowered for marker in _BLOCKED_RESPONSE_MARKERS)


def call_claude(prompt: str, label: str, timeout: int = 1800, allow_tools: bool = True,
                max_retries: int = 3, retry_wait: int = 30, system_prompt: str = None,
                output_dir: str = None) -> str:
    """
    Call claude -p with prompt on stdin. Returns the output text.
    Retries up to max_retries times on failure, waiting retry_wait seconds between attempts.
    Raises RuntimeError if all attempts fail.

    system_prompt: large, stable, repeated-across-calls content (contract,
    scoped requirement docs) — written to a temp file and sent via
    --append-system-prompt-file (not inline) so it's eligible for Claude
    Code's own prompt caching WITHOUT hitting Windows' command-line length
    limit. See claude_cmd() docstring — a real system_prompt runs tens of
    thousands of characters, which cmd.exe rejects outright if passed inline.
    A fresh temp file per call (not a shared/reused path) matters because
    review_runner.py fires 3 concurrent calls with 3 different system
    prompts — a shared path would race.
    output_dir: when given, per-call token/cost usage is appended to
    <output_dir>/token_usage_log.jsonl. Purely observational — never affects
    control flow.
    """
    system_prompt_file = None
    if system_prompt:
        fd, system_prompt_file = tempfile.mkstemp(suffix=".txt", prefix="claude_sysprompt_")
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(system_prompt)

    try:
        return _call_claude_inner(prompt, label, timeout, allow_tools, max_retries, retry_wait,
                                   system_prompt_file, output_dir)
    finally:
        if system_prompt_file:
            try:
                os.remove(system_prompt_file)
            except OSError:
                pass


def _call_claude_inner(prompt: str, label: str, timeout: int, allow_tools: bool,
                        max_retries: int, retry_wait: int, system_prompt_file: str,
                        output_dir: str) -> str:
    cmd = claude_cmd(allow_tools=allow_tools, system_prompt_file=system_prompt_file)
    last_error = None

    for attempt in range(1, max_retries + 1):
        if attempt > 1:
            print(f"  [{label}] retry {attempt}/{max_retries} (waiting {retry_wait}s)...")
            time.sleep(retry_wait)
        else:
            print(f"  [{label}] calling Claude CLI...")

        try:
            proc = subprocess.run(
                cmd,
                input=prompt,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=timeout,
            )
        except subprocess.TimeoutExpired:
            last_error = f"[{label}] Claude call timed out after {timeout}s"
            print(f"  [{label}] attempt {attempt} timed out — {'retrying' if attempt < max_retries else 'giving up'}.")
            continue
        except Exception as exc:
            last_error = f"[{label}] Claude call failed: {exc}"
            print(f"  [{label}] attempt {attempt} error: {exc} — {'retrying' if attempt < max_retries else 'giving up'}.")
            continue

        if proc.returncode != 0:
            # stderr is usually where a real error lands, but not always — a
            # rate-limit/overload response or a CLI-level failure can print
            # to stdout instead, and --output-format json means stdout isn't
            # always just the result payload on a failure path. Show both
            # immediately, right here, rather than only stashing stderr into
            # last_error for a final message that's only ever seen if every
            # retry fails too — a transient blip that succeeds on retry 2
            # should still tell you what it was, not just "non-zero exit".
            stderr = (proc.stderr or "").strip()
            stdout = (proc.stdout or "").strip()
            detail = stderr or stdout or "(no output on either stdout or stderr)"
            last_error = f"[{label}] Claude exited {proc.returncode}: {detail[:600]}"
            print(f"  [{label}] attempt {attempt} non-zero exit ({proc.returncode}): "
                  f"{detail[:300]!r} — {'retrying' if attempt < max_retries else 'giving up'}.")
            continue

        raw = proc.stdout or ""
        try:
            data = json.loads(raw)
        except ValueError:
            last_error = f"[{label}] Claude returned non-JSON output: {raw[:300]!r}"
            print(f"  [{label}] attempt {attempt} could not parse --output-format json output — "
                  f"{'retrying' if attempt < max_retries else 'giving up'}.")
            continue

        if data.get("is_error"):
            last_error = f"[{label}] Claude reported an error: {str(data.get('result', ''))[:300]}"
            print(f"  [{label}] attempt {attempt} returned is_error=true — "
                  f"{'retrying' if attempt < max_retries else 'giving up'}.")
            continue

        output = data.get("result") or ""
        _log_usage(output_dir, label, data)

        if not allow_tools and _looks_blocked_or_unresolved(output):
            last_error = (
                f"[{label}] Claude returned a blocked/clarifying response instead of the "
                f"expected document: {output[:300]!r}"
            )
            print(f"  [{label}] attempt {attempt} got a blocked/incomplete response instead of "
                  f"real content — {'retrying' if attempt < max_retries else 'giving up'}.")
            continue

        return output

    raise RuntimeError(last_error or f"[{label}] all {max_retries} attempts failed.")


# ── Layer 1 output loader ──────────────────────────────────────────────────────

def load_layer1(input_dir: str) -> dict:
    """Load all Layer 1 JSON artifacts from input_dir."""
    base = Path(input_dir)

    # Source_Code.json is always written by Step 1 (Layer 1) once it
    # completes, even if the list inside is empty — so its absence means
    # Step 1 never finished against this --input/--output folder, not that
    # the project simply has no source code. Failing loud here beats every
    # downstream agent silently running on empty data with no warning at all.
    primary = base / "Source_Code.json"
    if not primary.exists():
        raise RuntimeError(
            f"Layer 1 output not found: '{primary}'.\n"
            f"This is produced by Step 1 (Layer 1 — Deterministic Source Extraction) "
            f"and every agent step needs it.\n"
            f"Likely cause: Step 1 hasn't completed successfully for this --output folder, "
            f"or --input/--output points somewhere different than where Step 1 actually wrote "
            f"its results (check for a mismatched or renamed --output path).\n"
            f"Fix: run Step 1 again, e.g.\n"
            f"  python run.py --source <your-source> --output <this-output-folder> --track setup"
        )

    def read(filename):
        path = base / filename
        if path.exists():
            with open(path, encoding="utf-8") as f:
                return json.load(f)
        return {}

    return {
        "source_code": read("Source_Code.json"),
        "database":    read("Database.json"),
        "config":      read("Config.json"),
        "logs":        read("Logs.json"),
        "summary":     read("Extraction_Summary.json"),
    }


# ── file_cache.json loader ─────────────────────────────────────────────────────

def load_file_cache(output_dir: str) -> dict:
    """Load the full file cache produced by Scan Once (Step 2)."""
    cache_path = Path(output_dir) / "file_cache.json"
    if not cache_path.exists():
        raise RuntimeError(
            f"file_cache.json not found: '{cache_path}'.\n"
            f"This is produced by Step 2 (Scan Once) and every agent step needs it.\n"
            f"Likely cause: Step 2 hasn't completed successfully for this --output folder, "
            f"or --output points somewhere different than where Step 2 actually wrote its results.\n"
            f"Fix: run Step 2 again, e.g.\n"
            f"  python run.py --source <your-source> --output \"{output_dir}\" --track setup"
        )
    with open(cache_path, encoding="utf-8") as f:
        return json.load(f)


# ── FILE MAP builder ───────────────────────────────────────────────────────────

def build_file_map(layer1_source: list, file_cache: dict) -> str:
    """
    Build a one-line-per-file FILE MAP sent to Claude in Turn 1.
    Every file in file_cache appears — even those Layer 1 missed.
    Format:  <path>   <one-line summary>
    """
    l1_lookup = {}
    for a in layer1_source:
        f = (a.get("source_file") or a.get("file", "")).replace("\\", "/")
        if not f:
            continue
        name  = a.get("name", "")
        atype = a.get("type", "")
        methods = a.get("methods", [])
        fields  = a.get("fields",  [])
        parts = []
        if atype:
            parts.append(atype)
        if name:
            parts.append(name)
        if isinstance(methods, list) and methods:
            parts.append(f"{len(methods)} methods")
        if isinstance(fields, list) and fields:
            parts.append(f"{len(fields)} fields")
        l1_lookup[f] = ", ".join(parts) if parts else "source file"

    lines = []
    for path in sorted(file_cache.keys()):
        summary = l1_lookup.get(path, "")
        if not summary:
            ext = Path(path).suffix.lower()
            if ext == ".csproj":
                summary = "project file"
            elif ext in (".yml", ".yaml"):
                summary = "YAML config / pipeline"
            elif ext == ".json":
                summary = "JSON config"
            elif ext == ".sln":
                summary = "solution file"
            elif ext in (".bicep", ".tf"):
                summary = "infrastructure as code"
            elif ext == ".sql":
                summary = "SQL script"
            elif ext == ".dockerfile":
                summary = "Dockerfile"
            else:
                summary = ext.lstrip(".") or "file"
        lines.append(f"{path:<70} {summary}")

    return "\n".join(lines)


# ── DEEP_SCAN_OUTPUT.md section extractor ─────────────────────────────────────

def extract_deep_scan_sections(output_dir: str, file_paths: list) -> str:
    """
    Extract sections for the given file paths from DEEP_SCAN_OUTPUT.md.
    Returns them concatenated, ready to include in Turn 2 prompt.
    """
    deep_scan_path = Path(output_dir) / "DEEP_SCAN_OUTPUT.md"
    if not deep_scan_path.exists():
        # This file is Step 3's output — if it's missing, every requested
        # file below would silently resolve to "[Not found in deep scan]"
        # and the agent would produce a document from no real content at
        # all, with nothing in the logs to explain why. Fail loud instead.
        raise RuntimeError(
            f"DEEP_SCAN_OUTPUT.md not found: '{deep_scan_path}'.\n"
            f"This is produced by Step 3 (Scan Agent) and every agent step needs it.\n"
            f"Fix: run Step 3 again, e.g.\n"
            f"  python run.py --source <your-source> --output \"{output_dir}\" --track setup"
        )

    text = deep_scan_path.read_text(encoding="utf-8")
    parts = []
    for fp in file_paths:
        fp_norm = fp.replace("\\", "/")
        pattern = re.compile(
            r"=== FILE:\s*" + re.escape(fp_norm) + r"\s*===(.*?)(?====\s*FILE:|\Z)",
            re.DOTALL | re.IGNORECASE,
        )
        m = pattern.search(text)
        if m:
            parts.append(f"=== FILE: {fp_norm} ===\n{m.group(1).strip()}")
        else:
            parts.append(f"=== FILE: {fp_norm} ===\n[Not found in deep scan]")
    return "\n\n".join(parts)


# ── Output helpers ─────────────────────────────────────────────────────────────

def _winlong(path: Path) -> str:
    """
    On Windows, prefix an absolute path with \\\\?\\ to opt out of the 260-char
    MAX_PATH limit for this call — harmless no-op on other platforms. Sprint
    names get slugified into directory segments (e.g.
    "forward_results/sprints/Action_Audit_Logging_(cross-cutting)"), which
    combined with any reasonably long parent folder pushes plain mkdir()/
    write_text() past 260 chars and raises WinError 206. Resolves the path
    itself, so it's safe to call on a path the caller hasn't resolved yet.
    """
    if sys.platform != "win32":
        return str(path)
    s = str(Path(path).resolve())
    if s.startswith("\\\\?\\"):
        return s
    if s.startswith("\\\\"):  # UNC path
        return "\\\\?\\UNC\\" + s.lstrip("\\")
    return "\\\\?\\" + s


def save_output(output_dir: str, filename: str, content: str) -> Path:
    """Save text content to output_dir/filename. Creates dirs if needed."""
    out = Path(output_dir)
    path = out / filename
    # filename can itself contain subdirectories (e.g. "sprints/<slug>/test_log.txt")
    # — mkdir on out alone doesn't create those, only on output_dir itself.
    Path(_winlong(path.parent)).mkdir(parents=True, exist_ok=True)
    Path(_winlong(path)).write_text(content, encoding="utf-8")
    print(f"  Saved → {path}")
    return path


def save_json(output_dir: str, filename: str, data: dict) -> Path:
    """Save dict as JSON to output_dir/filename."""
    out = Path(output_dir)
    path = out / filename
    Path(_winlong(path.parent)).mkdir(parents=True, exist_ok=True)
    with open(_winlong(path), "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"  Saved → {path}")
    return path


def load_prior_output(output_dir: str, filename: str) -> str:
    """Load a prior agent's output file as text. Returns empty string if missing."""
    path = Path(output_dir) / filename
    if path.exists():
        return path.read_text(encoding="utf-8")
    return ""


def output_already_exists(output_dir: str, filename: str) -> bool:
    """Return True if the output file already exists and is non-empty.
    Used to skip steps that completed in a previous run (resume logic)."""
    path = Path(output_dir) / filename
    return path.exists() and path.stat().st_size > 0
