"""
Forward Engineering — Environment Preflight Check
Runs once, right after the target stack is confirmed, before any other Batch 1
step or any Batch 2 sprint LLM call happens.

Why this exists: test_executor_runner.py's _run_subproject() only discovers a
missing build tool (java, mvn, npm, python, dotnet, ...) when it actually
tries to run it — by which point Backend Dev, Security Review, Frontend Dev,
and Test-Writer have already run and spent real tokens generating that
sprint's code, for every sprint in the backlog, before anyone notices the
same tool is missing every time. Checking once, up front, catches it in
seconds instead.

Deliberately conservative about "fixing" things: only attempts an install via
the platform's OWN standard package manager (winget / apt-get / brew), only
if that manager is already present, with non-interactive flags and a hard
timeout so it can never hang on a permission prompt in an unattended run.
Because a newly-installed tool's PATH update is often invisible to the
*current* process (true on Windows in particular), any attempted install is
treated the same as "still missing" for THIS run — it reports what it did and
asks for a fresh re-run rather than gambling the new tool is usable yet.
"""

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from fwd_base import load_target_stack  # noqa: E402

# Reuse the exact same portable-install fallback paths test_executor_runner.py
# already checks, so "does the preflight see java" and "can the real test run
# find java later" never disagree.
from test_executor_runner import _JAVA_EXE, _MVN_BAT  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

_STACK_KEYWORDS = {
    "java":   ("java", "spring", "kotlin", "j2ee"),
    "node":   ("node", "react", "angular", "vue", "typescript", "javascript", "next.js", "express", "svelte"),
    "python": ("python", "django", "flask", "fastapi"),
    "dotnet": (".net", "c#", "csharp", "asp.net", "dotnet"),
}

# Each family maps to a list of REQUIREMENT GROUPS. A group is a list of
# (binary_name, portable_fallback_resolver_or_None) alternatives — the
# requirement is satisfied if ANY ONE of them is present (e.g. "mvn OR
# gradle" both count as "has a Java build tool"; only the first/preferred
# name in a group is ever the install target).
_FAMILY_REQUIREMENTS = {
    "java": [
        [("java", lambda: _JAVA_EXE)],
        [("mvn", lambda: _MVN_BAT), ("gradle", None)],
    ],
    "node": [
        [("node", None)],
        [("npm", None)],
    ],
    "python": [
        [("python", None), ("python3", None)],
        [("pip", None), ("pip3", None)],
    ],
    "dotnet": [
        [("dotnet", None)],
    ],
}

# Install target (always a group's preferred/first name) -> per-package-manager id.
_INSTALL_IDS = {
    "java":   {"winget": "Microsoft.OpenJDK.21",  "apt": "default-jdk",         "brew": "openjdk"},
    "mvn":    {"winget": "Apache.Maven",          "apt": "maven",               "brew": "maven"},
    "node":   {"winget": "OpenJS.NodeJS.LTS",     "apt": "nodejs npm",          "brew": "node"},
    "npm":    {"winget": "OpenJS.NodeJS.LTS",     "apt": "nodejs npm",          "brew": "node"},
    "python": {"winget": "Python.Python.3.12",    "apt": "python3 python3-pip", "brew": "python"},
    "pip":    {"winget": "Python.Python.3.12",    "apt": "python3-pip",         "brew": "python"},
    "dotnet": {"winget": "Microsoft.DotNet.SDK.8", "apt": "dotnet-sdk-8.0",     "brew": None},
}

_INSTALL_TIMEOUT = 300  # 5 min/tool — long enough for a real download, short enough to never look "hung"


# ── The claude CLI itself ──────────────────────────────────────────────────────
# Every agent step in both batches shells out to `claude`, so an unresolvable CLI
# is fatal to the entire run — yet this preflight used to ignore it completely and
# only look at the target stack's build tools. The failure then surfaced inside the
# sprint loop, where run_forward_batch2.py's broad `except Exception` read it as a
# failed attempt and retried it: one missing tool silently became "every sprint
# FAILED_BLOCKED" in under a second, with the real cause buried under N copies of
# itself. Checked here, unconditionally, before anything else.

def _npm_global_bin_candidates() -> list:
    """Directories an `npm install -g` shim can land in. Used to tell "not
    installed" apart from "installed but not on PATH" — by far the more confusing
    of the two, and the fix for it is completely different."""
    candidates = []
    appdata = os.environ.get("APPDATA")
    if appdata:
        candidates.append(Path(appdata) / "npm")
    prefix = os.environ.get("npm_config_prefix") or os.environ.get("NPM_CONFIG_PREFIX")
    if prefix:
        candidates.append(Path(prefix))
        candidates.append(Path(prefix) / "bin")
    home = Path.home()
    candidates += [home / ".npm-global" / "bin", home / ".local" / "bin", Path("/usr/local/bin")]
    return candidates


def _find_claude_shim():
    for directory in _npm_global_bin_candidates():
        for name in ("claude.cmd", "claude.exe", "claude"):
            try:
                candidate = directory / name
                if candidate.exists():
                    return candidate
            except OSError:
                continue  # unreadable/exotic path — just keep looking
    return None


def _check_claude_cli() -> dict:
    """{"ok": True} or {"ok": False, "reason": "not_on_path"|"not_installed", ...}.

    Resolution deliberately uses shutil.which — the exact same call
    pipeline/base_runner.claude_cmd() makes — so this check and the real
    invocation can never disagree about whether the CLI is usable.
    """
    if shutil.which("claude"):
        return {"ok": True}
    shim = _find_claude_shim()
    if shim:
        return {"ok": False, "reason": "not_on_path", "shim_dir": str(shim.parent)}
    return {"ok": False, "reason": "not_installed"}


def _report_missing_claude_cli(cli: dict) -> dict:
    print("\n[Environment Check] BLOCKED — the `claude` CLI is required for every agent step.")
    if cli["reason"] == "not_on_path":
        directory = cli["shim_dir"]
        print(f"  A claude shim EXISTS at {directory}, but that directory is not on PATH,")
        print("  so shutil.which('claude') cannot see it. This is a PATH problem, not a")
        print("  missing install — do NOT reinstall. Add it permanently:")
        if sys.platform == "win32":
            print(f"    [Environment]::SetEnvironmentVariable('PATH', '{directory};' + "
                  "[Environment]::GetEnvironmentVariable('PATH','User'), 'User')")
            print("  ...then open a NEW terminal (the current one keeps its old PATH).")
        else:
            print(f"    export PATH=\"{directory}:$PATH\"    # add to your shell profile")
        manual = [f"claude: add {directory} to PATH, then open a new terminal"]
    else:
        print("  Install with:      npm install -g @anthropic-ai/claude-code")
        print("  Then authenticate: claude login")
        manual = ["claude: npm install -g @anthropic-ai/claude-code && claude login"]
    print("  Verify with:       claude -p \"say hello\" --output-format text")
    return {"status": "blocked", "missing": ["claude"], "installed": [], "manual_steps": manual}


def _detect_families(target_stack: str) -> set:
    stack_l = target_stack.lower()
    return {family for family, kws in _STACK_KEYWORDS.items() if any(kw in stack_l for kw in kws)}


def _is_present(name: str, fallback_resolver=None) -> bool:
    if shutil.which(name):
        return True
    if fallback_resolver:
        path = fallback_resolver()
        if path and Path(path).exists():
            return True
    return False


def _group_satisfied(group) -> bool:
    return any(_is_present(name, resolver) for name, resolver in group)


def _package_manager() -> str:
    """Return 'winget' / 'apt' / 'brew' if usable on this machine, else None."""
    if sys.platform == "win32":
        return "winget" if shutil.which("winget") else None
    if sys.platform == "darwin":
        return "brew" if shutil.which("brew") else None
    # Only apt-based Linux is supported here — matches this pipeline's
    # existing Windows-first / apt-second tooling assumptions elsewhere
    # (test_executor_runner.py's portable-install fallback is Windows-only
    # too). Anything else falls through to manual instructions.
    return "apt" if shutil.which("apt-get") else None


def _install_command(tool: str, manager: str) -> list:
    ids = _INSTALL_IDS.get(tool, {})
    pkg = ids.get(manager)
    if not pkg:
        return None
    if manager == "winget":
        return ["winget", "install", "--id", pkg, "-e", "--source", "winget",
                "--silent", "--accept-package-agreements", "--accept-source-agreements"]
    if manager == "apt":
        base = ["apt-get", "install", "-y"] + pkg.split()
        # Running as root already (common in containers) doesn't need sudo,
        # and may not even have it installed. -n makes sudo fail immediately
        # instead of hanging on a password prompt it'll never get.
        if hasattr(os, "geteuid") and os.geteuid() == 0:
            return base
        return ["sudo", "-n"] + base
    if manager == "brew":
        return ["brew", "install", pkg]
    return None


def _attempt_install(tool: str, manager: str) -> dict:
    cmd = _install_command(tool, manager)
    if not cmd:
        return {"tool": tool, "succeeded": False, "output": f"no known {manager} package for '{tool}'"}
    print(f"    [{tool}] installing via {manager}: {' '.join(cmd)}")
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8",
                               errors="replace", timeout=_INSTALL_TIMEOUT)
        return {"tool": tool, "succeeded": proc.returncode == 0,
                "output": ((proc.stdout or "") + (proc.stderr or ""))[-500:].strip()}
    except subprocess.TimeoutExpired:
        return {"tool": tool, "succeeded": False,
                "output": f"timed out after {_INSTALL_TIMEOUT}s (likely stuck waiting on a permission prompt)"}
    except FileNotFoundError as exc:
        return {"tool": tool, "succeeded": False, "output": str(exc)}


def _manual_hint(tool: str) -> str:
    ids = _INSTALL_IDS.get(tool, {})
    parts = []
    if ids.get("winget"):
        parts.append(f"Windows: winget install --id {ids['winget']} -e")
    if ids.get("apt"):
        parts.append(f"Linux (apt): sudo apt-get install -y {ids['apt']}")
    if ids.get("brew"):
        parts.append(f"macOS: brew install {ids['brew']}")
    if tool == "dotnet":
        parts.append("macOS: brew install --cask dotnet-sdk")
    return " | ".join(parts) if parts else f"(no known install command for '{tool}' — install it manually)"


def run(output_dir: str) -> dict:
    # Checked FIRST, and independently of the target stack: the CLI is required no
    # matter what gets built, and the early "nothing to check" returns below would
    # otherwise let a run start with no way to call an agent at all.
    cli = _check_claude_cli()
    if not cli["ok"]:
        return _report_missing_claude_cli(cli)

    target_stack = load_target_stack(output_dir)
    if not target_stack:
        print("\n[Environment Check] No target stack confirmed yet — nothing to check.")
        return {"status": "ok"}

    families = _detect_families(target_stack)
    if not families:
        print(f"\n[Environment Check] Could not map target stack {target_stack!r} to a known "
              "tool family (java/node/python/dotnet) — skipping, nothing to check against.")
        return {"status": "ok"}

    print(f"\n[Environment Check] Target stack {target_stack!r} needs: {', '.join(sorted(families))}")

    unmet_groups, seen_keys = [], set()
    for family in sorted(families):
        for group in _FAMILY_REQUIREMENTS[family]:
            key = tuple(name for name, _ in group)
            if key in seen_keys:
                continue
            seen_keys.add(key)
            if not _group_satisfied(group):
                unmet_groups.append(group)

    if not unmet_groups:
        print("  All required tools already present (claude CLI included).")
        return {"status": "ok"}

    to_install = [group[0][0] for group in unmet_groups]  # preferred name per unmet group
    print(f"  Missing: {', '.join(to_install)}")

    manager = _package_manager()
    installed, still_missing, manual_steps = [], [], []

    if manager:
        print(f"  Package manager available: {manager} — attempting install...")
        for tool in to_install:
            result = _attempt_install(tool, manager)
            if result["succeeded"]:
                installed.append(tool)
                print(f"    [{tool}] install command completed.")
            else:
                still_missing.append(tool)
                print(f"    [{tool}] could not auto-install: {result['output']}")
                manual_steps.append(f"{tool}: {_manual_hint(tool)}")
    else:
        print("  No supported package manager found on this machine (winget/apt-get/brew) — "
              "cannot attempt auto-install.")
        still_missing = to_install
        manual_steps = [f"{tool}: {_manual_hint(tool)}" for tool in to_install]

    # Even a "successful" install command doesn't guarantee THIS process can
    # see the new PATH entry yet — never claim "ok" in the same run an
    # install was attempted; ask for a fresh re-run instead of gambling.
    print("\n[Environment Check] BLOCKED.")
    if installed:
        print(f"  Installed this run (needs a FRESH terminal/process to be picked up on PATH): "
              f"{', '.join(installed)}")
    if still_missing:
        print("  Still missing — install manually, then re-run:")
        for step in manual_steps:
            print(f"    - {step}")
    print("\n  Re-run this exact command again once the tools above are confirmed available "
          "(open a new terminal first if anything was just installed).")
    return {"status": "blocked", "missing": still_missing, "installed": installed, "manual_steps": manual_steps}


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--output", required=True)
    args = p.parse_args()
    result = run(args.output)
    sys.exit(0 if result["status"] == "ok" else 3)
