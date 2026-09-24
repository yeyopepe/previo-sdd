#!/usr/bin/env python3
"""Cheap gate run by every public pv-* skill's step 0, on every invocation --
deliberately a subset of audit-context.py's full auditor (markers,
.metadata.json, namespace, hooks...), which only runs on demand via
/pv-update. This script must stay fast and never duplicate the auditor's
expensive checks.

Checks, in this order, stopping at the first failure (a binary gate, not a
report -- never accumulates multiple problems like audit-context.py does):

  1. context-missing        .claude/pv-context.json doesn't exist.
  2. context-invalid-json   it exists but doesn't parse.
  3. blocked                framework.frameworkStatus.blocked is true.
  4. version-mismatch       pv-init/SKILL.md's metadata.version doesn't match
                             framework.frameworkStatus.lastVerifiedVersion
                             (missing frameworkStatus counts as a mismatch).
  5. skill-count-mismatch   number of installed pv-* skill folders doesn't
                             match EXPECTED_SKILL_COUNT.

'blocked' is checked before 'version-mismatch' on purpose: mark-verified.py
--block leaves lastVerifiedVersion untouched while setting blocked=true, so
whenever blocked is true the real version is already different from
lastVerifiedVersion too -- checking version-mismatch first would mean
'blocked' is never reached, and the user would get the generic mismatch
message instead of the specific one (with blockedReason).

Never raises an uncaught exception -- expected failures (broken JSON, an
uninitialized framework) are reported as data, not a traceback.

Prints ONLY a JSON on stdout:

  {"ok": true, "problem": null, "message": null}

or, on failure:

  {
    "ok": false,
    "problem": "context-missing | context-invalid-json | blocked | version-mismatch | skill-count-mismatch",
    "message": "text ready to show the user",
    "expected": "...",
    "actual": "..."
  }

Usage:
  python .claude/skills/pv-update/scripts/check-framework-status.py
"""

import json
import re
import sys
from pathlib import Path

# Number of pv-* skill folders the current framework version installs.
# Kept in sync by tools/set-skill-versions.py on every release cut -- never
# edit this by hand.
EXPECTED_SKILL_COUNT = 23


def repo_root() -> Path:
    # This script lives at {repo}/.claude/skills/pv-update/scripts/
    return Path(__file__).resolve().parents[4]


def read_skill_version(path: Path) -> str | None:
    """Reads metadata.version from a SKILL.md's YAML frontmatter, manually
    (no PyYAML) -- same logic as audit-context.py/mark-verified.py,
    duplicated here on purpose (each pv-* script is self-contained)."""
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None
    try:
        close_idx = next(i for i in range(1, len(lines)) if lines[i].strip() == "---")
    except StopIteration:
        return None
    in_metadata = False
    for line in lines[1:close_idx]:
        if re.match(r"^metadata:\s*$", line):
            in_metadata = True
            continue
        if not in_metadata:
            continue
        version_match = re.match(r"^\s+version:\s*(.+?)\s*$", line)
        if version_match:
            return version_match.group(1).strip().strip('"').strip("'")
        if not line.startswith((" ", "\t")):
            in_metadata = False
    return None


def result(ok: bool, problem: str | None = None, message: str | None = None,
           expected=None, actual=None) -> dict:
    out = {"ok": ok, "problem": problem, "message": message}
    if expected is not None:
        out["expected"] = expected
    if actual is not None:
        out["actual"] = actual
    return out


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    root = repo_root()
    context_path = root / ".claude/pv-context.json"

    if not context_path.is_file():
        json.dump(result(
            False, "context-missing",
            "The framework isn't initialized in this project "
            "('.claude/pv-context.json' doesn't exist). Run pv-init first."
        ), sys.stdout, ensure_ascii=False, indent=2)
        print()
        return

    try:
        context = json.loads(context_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        json.dump(result(
            False, "context-invalid-json",
            f"'.claude/pv-context.json' isn't valid JSON ({exc}). "
            "Run /pv-update to check and repair the configuration."
        ), sys.stdout, ensure_ascii=False, indent=2)
        print()
        return

    framework = context.get("framework") if isinstance(context, dict) else None
    if not isinstance(framework, dict):
        framework = {}

    framework_status = framework.get("frameworkStatus") or {}

    if framework_status.get("blocked") is True:
        reason = framework_status.get("blockedReason")
        message = "The framework is blocked."
        if reason:
            message += f" Reason: {reason}"
        message += " Run /pv-update to check and repair the configuration."
        json.dump(result(False, "blocked", message), sys.stdout, ensure_ascii=False, indent=2)
        print()
        return

    last_verified = framework_status.get("lastVerifiedVersion")
    pv_init_md = root / ".claude/skills/pv-init/SKILL.md"
    real_version = read_skill_version(pv_init_md) if pv_init_md.is_file() else None

    if not last_verified or not real_version or last_verified != real_version:
        json.dump(result(
            False, "version-mismatch",
            "The installed framework version doesn't match the last verified "
            "version. Run /pv-update to check and repair the configuration.",
            expected=real_version, actual=last_verified
        ), sys.stdout, ensure_ascii=False, indent=2)
        print()
        return

    skills_dir = root / ".claude/skills"
    actual_count = len(list(skills_dir.glob("pv-*"))) if skills_dir.is_dir() else 0
    if actual_count != EXPECTED_SKILL_COUNT:
        json.dump(result(
            False, "skill-count-mismatch",
            f"Found {actual_count} pv-* skill folders, expected "
            f"{EXPECTED_SKILL_COUNT}. Previo doesn't look correctly installed "
            "-- either an incomplete/corrupt installation, or loose pv-* "
            "skills copied outside the framework's intended use. Run "
            "/pv-update install to install the latest version.",
            expected=EXPECTED_SKILL_COUNT, actual=actual_count
        ), sys.stdout, ensure_ascii=False, indent=2)
        print()
        return

    json.dump(result(True), sys.stdout, ensure_ascii=False, indent=2)
    print()


if __name__ == "__main__":
    main()
