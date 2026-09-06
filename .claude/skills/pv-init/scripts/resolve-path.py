#!/usr/bin/env python3
"""Resolves an absolute path from .claude/pv-context.json by LOGICAL KEY, so no
flow skill (pv-new, pv-fix, pv-how, pv-do, pv-internal-*) has to know the JSON's
internal shape or the per-field resolution rules. Only pv-init (this script's
owner, and the schema's owner) and pv-update know the schema; everyone else asks
here.

Usage:
  python .claude/skills/pv-init/scripts/resolve-path.py --what <key>

Supported logical keys (field -> resolution base, embedded below):

  workFolder          framework.workFolder (default '/previo-sdd')      repo root
  sourcecodeDir       framework.sourcecodeDir (default '/src')          repo root
  changesDir          {workFolder}/changes  (derived)                  repo root
  versionsDir         {workFolder}/versions (derived)                  repo root
  stuffDir            {workFolder}/stuff    (derived)                  repo root
  architectureDocDir  framework.docs.tech.architectureDocDir           workFolder
  styleBibleDocDir    framework.docs.tech.styleBibleDocDir             workFolder
  featuresDocPathDir  framework.docs.functional.featuresDocPathDir     workFolder

On success: exit 0, prints ONLY the resolved absolute path on stdout (POSIX
slashes, no trailing slash, nothing else) so a skill can capture it directly.

On failure: exit != 0, a fixed-format diagnostic on stderr:

  resolve-path: <category> -- <detail>
    what: architectureDocDir
    field: framework.docs.tech.architectureDocDir
    fix: run /pv-update

  Exit  Cause                                                     Caller must
  2     pv-context.json missing / invalid JSON / no 'framework'   stop -> /pv-init
  3     configurable key absent in pv-context.json                stop -> /pv-update
  4     key configured but the folder doesn't exist on disk       stop -> /pv-update
  5     unknown logical key (bug in the calling skill)             stop, report bug

  workFolder / sourcecodeDir / changesDir / versionsDir / stuffDir always have a
  value (schema default or derived), so they never give exit 3; they can still
  give exit 4 if the resulting folder doesn't exist.
  architectureDocDir / styleBibleDocDir / featuresDocPathDir give exit 3 if the
  field is missing, exit 4 if it's set but the folder isn't there.

Flags:
  --json           print {"what":..., "field":..., "path":..., "exists":...}
                   instead of the bare path. For debugging / other scripts.
  --allow-missing  turn exit 4 into exit 0 and print the path anyway. Used by
                   pv-init (scaffolding, folder not created yet) and potentially
                   audit-context.py. Flow skills must NOT pass it.

Implementation notes:
  - repo_root() uses parents[4]: this script lives at
    {repo}/.claude/skills/pv-init/scripts/ -- same depth as
    pv-update/scripts/audit-context.py, which also uses parents[4].
  - strip_leading_slash / resolve_under are copied (not imported) from
    audit-context.py -- the framework has no shared module and scripts are
    self-contained. Resolution logic kept in sync with
    pv-update/scripts/audit-context.py's check_docs_dir -- change both together.
  - Only stdlib: json, sys, argparse, pathlib.
  - Never accepts --context-path: always {repo_root}/.claude/pv-context.json.
"""

import argparse
import json
import sys
from pathlib import Path


def repo_root() -> Path:
    # This script lives at {repo}/.claude/skills/pv-init/scripts/
    return Path(__file__).resolve().parents[4]


def strip_leading_slash(value: str) -> str:
    return value.lstrip("/")


def resolve_under(root: Path, base: str) -> Path:
    return root / strip_leading_slash(base)


# Logical keys whose base is the repo root. workFolder / sourcecodeDir read a
# framework field (with a schema default); the *Dir ones are derived from
# workFolder. None of these can be "unconfigured" -> they never raise exit 3.
ROOT_RELATIVE = {
    "workFolder": ("framework.workFolder", ("workFolder",), "/previo-sdd"),
    "sourcecodeDir": ("framework.sourcecodeDir", ("sourcecodeDir",), "/src"),
}
WORKFOLDER_DERIVED = {
    "changesDir": "changes",
    "versionsDir": "versions",
    "stuffDir": "stuff",
}
# Logical keys resolved UNDER workFolder, reading a configurable field that has
# no default -> exit 3 if absent, exit 4 if set but the folder isn't there.
DOCS_KEYS = {
    "architectureDocDir": ("framework.docs.tech.architectureDocDir",
                           ("docs", "tech", "architectureDocDir")),
    "styleBibleDocDir": ("framework.docs.tech.styleBibleDocDir",
                         ("docs", "tech", "styleBibleDocDir")),
    "featuresDocPathDir": ("framework.docs.functional.featuresDocPathDir",
                           ("docs", "functional", "featuresDocPathDir")),
}

ALL_KEYS = list(ROOT_RELATIVE) + list(WORKFOLDER_DERIVED) + list(DOCS_KEYS)


def fail(code: int, category: str, detail: str, what: str, field: str) -> "NoReturn":
    print(f"resolve-path: {category} -- {detail}", file=sys.stderr)
    print(f"  what: {what}", file=sys.stderr)
    print(f"  field: {field}", file=sys.stderr)
    if code == 2:
        print("  fix: run /pv-init", file=sys.stderr)
    elif code in (3, 4):
        print("  fix: run /pv-update", file=sys.stderr)
    else:
        print("  fix: bug in the calling skill -- report it; run /pv-update", file=sys.stderr)
    sys.exit(code)


def dig(obj: dict, path: tuple) -> object:
    cur = obj
    for key in path:
        if not isinstance(cur, dict) or key not in cur:
            return None
        cur = cur[key]
    return cur


def emit(args, what: str, field: str, resolved: Path, exists: bool) -> "NoReturn":
    path_str = resolved.as_posix().rstrip("/")
    if args.json:
        json.dump({"what": what, "field": field, "path": path_str, "exists": exists},
                  sys.stdout, ensure_ascii=False)
        print()
    else:
        print(path_str)
    sys.exit(0)


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(
        prog="resolve-path.py",
        description="Resolve an absolute path from .claude/pv-context.json by logical key.")
    parser.add_argument("--what", required=True, metavar="KEY",
                        help="logical key: " + ", ".join(ALL_KEYS))
    parser.add_argument("--json", action="store_true",
                        help='print {"what",...,"path","exists"} instead of the bare path')
    parser.add_argument("--allow-missing", action="store_true",
                        help="turn exit 4 into exit 0 and print the path anyway (pv-init only)")
    args = parser.parse_args()

    what = args.what

    if what not in ALL_KEYS:
        fail(5, "unknown key",
             f"'{what}' is not a supported logical key. Supported: {', '.join(ALL_KEYS)}.",
             what, "(none)")

    root = repo_root()
    context_path = root / ".claude/pv-context.json"

    if not context_path.is_file():
        fail(2, "no context",
             "'.claude/pv-context.json' doesn't exist -- the framework isn't initialized.",
             what, "(file)")
    try:
        context = json.loads(context_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        fail(2, "no context",
             f"'.claude/pv-context.json' can't be read as JSON: {exc}", what, "(file)")

    framework = context.get("framework")
    if not isinstance(framework, dict) or not framework:
        fail(2, "no context",
             "'.claude/pv-context.json' has no 'framework' section -- the framework isn't initialized.",
             what, "framework")

    work_folder = framework.get("workFolder", "/previo-sdd")
    if not isinstance(work_folder, str) or not work_folder.strip():
        fail(2, "no context",
             "'framework.workFolder' is set but isn't a non-empty string.",
             what, "framework.workFolder")

    # --- root-relative keys: workFolder / sourcecodeDir ---
    if what in ROOT_RELATIVE:
        field, _, default = ROOT_RELATIVE[what]
        value = framework.get(what, default)
        if not isinstance(value, str) or not value.strip():
            value = default
        resolved = resolve_under(root, value)
        exists = resolved.is_dir()
        if not exists and not args.allow_missing:
            fail(4, "folder missing",
                 f"'{field}' resolves to '{resolved.as_posix()}' but that folder doesn't exist.",
                 what, field)
        emit(args, what, field, resolved, exists)

    # --- derived-from-workFolder keys: changesDir / versionsDir / stuffDir ---
    if what in WORKFOLDER_DERIVED:
        sub = WORKFOLDER_DERIVED[what]
        field = f"{'framework.workFolder'} ({sub})"
        resolved = resolve_under(root, f"{work_folder.rstrip('/')}/{sub}")
        exists = resolved.is_dir()
        if not exists and not args.allow_missing:
            fail(4, "folder missing",
                 f"'{resolved.as_posix()}' (derived from workFolder) doesn't exist.",
                 what, field)
        emit(args, what, field, resolved, exists)

    # --- docs.* keys: resolved under workFolder, configurable, no default ---
    field, json_path = DOCS_KEYS[what]
    configured = dig(framework, json_path)
    if not isinstance(configured, str) or not configured.strip():
        fail(3, "not configured",
             f"'{field}' isn't set in pv-context.json. pv-init always configures "
             f"all three doc dirs; every pv-* skill requires them.",
             what, field)
    resolved = resolve_under(root, f"{work_folder.rstrip('/')}/{configured}")
    # featuresDocPathDir is a folder in the recommended convention but may still
    # be a single .md file in unmigrated projects (see schema.json) -- accept
    # either. The two tech dirs are always folders.
    if what == "featuresDocPathDir":
        exists = resolved.is_dir() or resolved.is_file()
    else:
        exists = resolved.is_dir()
    if not exists and not args.allow_missing:
        fail(4, "folder missing",
             f"'{field}' is configured as '{configured}' but '{resolved.as_posix()}' "
             f"doesn't exist on disk.",
             what, field)
    emit(args, what, field, resolved, exists)


if __name__ == "__main__":
    main()
