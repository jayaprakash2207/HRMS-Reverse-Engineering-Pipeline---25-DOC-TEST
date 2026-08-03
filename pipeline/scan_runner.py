"""
Scan Once Runner — Step 2
Reads every file in the repo once, stores full content (no truncation) into file_cache.json.
Disk is never read again after this step — all agents load from the cache.
"""

import json
import os
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

SKIP_DIRS = {
    "bin", "obj", "node_modules", ".git", ".svn", "wwwroot",
    "TestResults", ".vs", ".idea", "__pycache__",
    "dist", "build", "vendor",
}

# Skipped ONLY as a direct child of the repo root, never at arbitrary depth.
# "packages" used to sit in SKIP_DIRS above, which matched on ANY path segment —
# so an Oracle codebase's "plsql/packages/" directory (the PL/SQL package bodies
# and specs, i.e. essentially all of its business logic) was discarded as if it
# were a NuGet/npm dependency cache. NuGet's really is "<root>/packages", so
# anchoring the rule to the root keeps that exclusion working without eating
# source directories that merely share the name.
ROOT_ONLY_SKIP_DIRS = {"packages"}

# MUST stay in sync with the two other extension lists in this pipeline —
# layer1/file_filter.py (filter_by_language) and layer1/language_detector.py.
# Those two already listed the Oracle/PL-SQL and COBOL suffixes below; this one
# did not, and because THIS is the list that builds file_cache.json — the single
# cache every downstream agent reads, since "disk is never read again after this
# step" — anything missing here is invisible to the entire pipeline. An Oracle
# Forms/PL-SQL codebase was scanned with only .sql matching, so every package
# body and spec (.pkb/.pks) was silently skipped: the schema was analysed while
# 100% of the business logic in the packages was never read by anything.
INCLUDE_EXTENSIONS = {
    # .NET / JVM / scripting
    ".cs", ".vb", ".java", ".py", ".js", ".ts", ".jsx", ".tsx",
    ".json", ".yml", ".yaml", ".xml", ".csproj", ".vbproj",
    ".sln", ".props", ".targets", ".bicep", ".tf",
    ".dockerfile", ".sh", ".bat", ".ps1", ".sql",
    ".md", ".txt", ".env", ".config",
    # Oracle PL/SQL — package specs/bodies hold the business logic; .sql alone
    # only ever catches DDL, triggers and seed scripts.
    ".pks", ".pkb", ".pkg", ".trg", ".prc", ".fnc",
    ".tps", ".tpb", ".spc", ".bdy", ".vw",
    # Oracle Forms/Reports TEXT exports only. The binary .fmb/.mmb/.pll are
    # deliberately excluded: read_text() would yield replacement-char garbage
    # that costs tokens and teaches the agents nothing.
    ".fmt", ".mmt", ".pld", ".frmxml", ".mmxml", ".pllxml", ".rdf",
    # COBOL — listed as supported in file_filter.py but never scannable before.
    ".cbl", ".cob", ".cpy",
}


def _long_path_safe(root: Path) -> Path:
    """Return `root` in a form Windows can walk past the 260-char MAX_PATH limit.

    Beyond that limit Windows does not raise — it reports the file as simply not
    existing, so Path.is_file() returns False and rglob() omits it. A deeply
    nested checkout therefore scans to a fraction of its real size and reports
    success, which is exactly how an Oracle codebase was analysed with its
    package bodies missing: the paths were 260-265 chars, so the longest-named
    (and largest) packages vanished while the short-named ones came through.
    The \\\\?\\ prefix opts into extended-length paths and makes them visible.
    """
    if os.name != "nt":
        return root
    resolved = root.resolve()
    text = str(resolved)
    if text.startswith("\\\\?\\"):
        return resolved
    if text.startswith("\\\\"):  # UNC share: \\server\share -> \\?\UNC\server\share
        return Path("\\\\?\\UNC\\" + text.lstrip("\\"))
    return Path("\\\\?\\" + text)


def run(repo_root: str, output_dir: str) -> dict:
    display_root = Path(repo_root)
    root = _long_path_safe(display_root)
    cache = {}
    skipped = 0

    print(f"\n[Scan Once] Walking {display_root} ...")

    for p in sorted(root.rglob("*")):
        if not p.is_file():
            continue

        # Match exclusions against the path RELATIVE to the repo root, not the
        # absolute path: p.parts includes every parent directory of the checkout
        # too, so a repo living under any folder named e.g. "build" or "dist"
        # (a temp dir, a CI workspace) silently scanned to zero files.
        rel_parts = p.relative_to(root).parts
        dir_parts = rel_parts[:-1]

        if any(part in SKIP_DIRS for part in dir_parts):
            continue
        if dir_parts and dir_parts[0] in ROOT_ONLY_SKIP_DIRS:
            continue

        if p.suffix.lower() not in INCLUDE_EXTENSIONS:
            skipped += 1
            continue
        try:
            content = p.read_text(encoding="utf-8", errors="replace")
            rel = "/".join(rel_parts)
            cache[rel] = content
        except Exception:
            continue

    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    cache_file = out_path / "file_cache.json"
    with open(cache_file, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False)

    print(f"  [Scan Once] {len(cache)} files cached → {cache_file}")
    print(f"  [Scan Once] {skipped} files skipped (excluded extensions)")

    # ── Validation: re-walk source and compare against cache ─────────────────
    print(f"\n  [Scan Once] Validating cache completeness...")
    actual_files = set()
    for p in sorted(root.rglob("*")):
        if not p.is_file():
            continue
        rel_parts = p.relative_to(root).parts
        dir_parts = rel_parts[:-1]
        if any(part in SKIP_DIRS for part in dir_parts):
            continue
        if dir_parts and dir_parts[0] in ROOT_ONLY_SKIP_DIRS:
            continue
        if p.suffix.lower() not in INCLUDE_EXTENSIONS:
            continue
        actual_files.add("/".join(rel_parts))

    missing = actual_files - set(cache.keys())
    if missing:
        print(f"\n  [Scan Once] WARNING: {len(missing)} file(s) found on disk but NOT in cache:")
        for f in sorted(missing):
            print(f"    MISSING: {f}")
        print(f"\n  [Scan Once] These files will be INVISIBLE to all downstream agents.")
        print(f"  [Scan Once] Possible causes: new file extension not in INCLUDE_EXTENSIONS,")
        print(f"              Windows path length limit, or read permission error.")
        raise RuntimeError(
            f"[Scan Once] Cache is incomplete — {len(missing)} file(s) missing. "
            f"Fix INCLUDE_EXTENSIONS or path issues above, then re-run Step 2."
        )
    else:
        print(f"  [Scan Once] Validation PASSED — all {len(actual_files)} source files are in cache.")

    return {"file_count": len(cache), "cache_path": str(cache_file)}


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--repo-root", required=True)
    p.add_argument("--output",    required=True)
    args = p.parse_args()
    run(args.repo_root, args.output)
