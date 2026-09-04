#!/usr/bin/env python3
"""Mutates a change/fix's .metadata.json in the pv-* framework.

Single entry point for every write to
{workFolder}/changes/{state}/{xxxx}/.metadata.json -- the per-change file
of mutable state that sits next to description.md / plan.md / history.md.
Handles two independent pieces of state:
  - the 'flags' array (a set of extensible status labels: today 'priority'
    and 'workinprogress'), via --add-flag / --remove-flag / --toggle-flag.
  - the 'risk' integer 0-10 (the median of pv-internal-tech-risks' 9
    factors), via --set-risk. Written by pv-how in step 3.1, right after
    plan.md is drafted. Absent = not yet assessed.
A single invocation can touch flags, risk, or both; each is optional.

State resolution: given --xxxx, the script looks for the change folder
under every direct subfolder of {workFolder}/changes/ (inProgress,
implemented, closed, ...), skipping todo/. Pass --state to skip the search
and target one state directly. todo/ is rejected on purpose: a todo is a
loose idea outside the flow -- there's nothing "in progress" or
"prioritised within the flow" to mark. Any operation that resolves to a
folder under todo/ (or an explicit --state todo) is an error and writes
nothing.

Concurrency: the read-modify-write cycle is guarded by an exclusive file
lock on an adjacent {folder}/.metadata.json.lock, so a toggle from pv.py
and one from a Claude Code session in parallel can't clobber each other.
No last-write-wins.

The file is created on first write and NEVER deleted, even if 'flags'
ends up []. Unknown fields are preserved verbatim.

Every effective FLAG mutation refreshes 'flagsLastModified' to today's
date. 'risk' has no timestamp of its own and never touches
'flagsLastModified'. An operation that changes nothing (e.g. --remove-flag
on a flag that isn't set, --add-flag on one already set, or --set-risk to
the value already stored) leaves the file untouched and reports it as a
no-op.

Output: one plain-text confirmation line (no ANSI), like delete-todo.py.
With --print, the resulting .metadata.json is also emitted as JSON on
stdout (after the confirmation line) so callers don't have to re-read it.

workFolder is read from .claude/pv-context.json (framework section)
unless passed explicitly via --work-folder (same pattern as
move-change.py), so pv.py --testconfig can point it at fixtures.

Usage:
  python set-metadata.py --xxxx 00192 --toggle-flag priority
  python set-metadata.py --xxxx 00192 --add-flag workinprogress --print
  python set-metadata.py --xxxx 00192 --state inProgress --remove-flag priority
  python set-metadata.py --xxxx 00192 --set-risk 5
"""

import argparse
import json
import sys
from datetime import date
from pathlib import Path

# Canonical catalogue of valid flags -- mirrors metadata.schema.json's
# 'flags' enum. Kept as a literal here (rather than parsed from the schema)
# so the script has no JSON-Schema dependency; audit-context.py validates
# real files against the schema itself.
VALID_FLAGS = ("priority", "workinprogress")

METADATA_FILENAME = ".metadata.json"
LOCK_FILENAME = ".metadata.json.lock"


def repo_root() -> Path:
    # This script lives at {repo}/.claude/skills/pv-internal-workflow/scripts/
    return Path(__file__).resolve().parents[4]


def load_work_folder(root: Path) -> str:
    context_path = root / ".claude" / "pv-context.json"
    if not context_path.is_file():
        raise SystemExit(
            f"Cannot find {context_path}. Run the pv-init skill before "
            "setting metadata on a change/fix."
        )

    context = json.loads(context_path.read_text(encoding="utf-8"))
    framework = context.get("framework")
    if not framework:
        raise SystemExit(
            f"{context_path} has no 'framework' section. Run the pv-init "
            "skill to complete it."
        )
    return framework.get("workFolder", "/")


def resolve_changes_dir(root: Path, work_folder_rel: str) -> Path:
    # workFolder is always relative to the repo root, whether or not it
    # carries a leading "/" (that's only a convention to make it visually
    # explicit) -- Path("/a") / "/b" would otherwise discard "a" entirely,
    # since pathlib treats a leading-slash operand as its own absolute path.
    work_root = root / (work_folder_rel or "").lstrip("/")
    return work_root / "changes"


def resolve_entry_dir(changes_dir: Path, xxxx: str, state: str | None) -> Path:
    """Finds {changes_dir}/{state}/{xxxx}/, searching every non-todo state
    if --state wasn't given. Raises SystemExit (writing nothing) if it's
    not found, is ambiguous, or resolves under todo/."""
    if state is not None:
        if state == "todo":
            raise SystemExit(
                "flags don't apply to todo/ entries: a todo is a loose idea "
                "outside the change/fix flow, with nothing to mark as "
                "prioritised or in progress."
            )
        entry_dir = changes_dir / state / xxxx
        if not entry_dir.is_dir():
            raise SystemExit(f"Change folder doesn't exist: {entry_dir}")
        return entry_dir

    if not changes_dir.is_dir():
        raise SystemExit(f"No changes/ folder at: {changes_dir}")

    matches: list[Path] = []
    todo_match = False
    for state_dir in sorted(p for p in changes_dir.iterdir() if p.is_dir()):
        candidate = state_dir / xxxx
        if not candidate.is_dir():
            continue
        if state_dir.name == "todo":
            todo_match = True
            continue
        matches.append(candidate)

    if not matches:
        if todo_match:
            raise SystemExit(
                f"'{xxxx}' is a todo/ idea, and flags don't apply to todo/ "
                "entries (a todo is a loose idea outside the change/fix flow)."
            )
        raise SystemExit(
            f"No change/fix folder named '{xxxx}' under {changes_dir} "
            "(searched every state except todo/)."
        )
    if len(matches) > 1:
        states = ", ".join(sorted(p.parent.name for p in matches))
        raise SystemExit(
            f"'{xxxx}' exists in more than one state ({states}). "
            "Pass --state to disambiguate."
        )
    return matches[0]


def read_metadata(entry_dir: Path) -> dict:
    """Reads {entry_dir}/.metadata.json. Returns {} for a missing file;
    raises SystemExit for one that exists but isn't a JSON object."""
    path = entry_dir / METADATA_FILENAME
    if not path.is_file():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"{path} isn't valid JSON: {exc}")
    if not isinstance(data, dict):
        raise SystemExit(f"{path} must contain a JSON object, got {type(data).__name__}.")
    return data


def write_metadata(entry_dir: Path, data: dict) -> None:
    path = entry_dir / METADATA_FILENAME
    path.write_text(
        json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )


class _FileLock:
    """Cross-platform advisory exclusive lock around a lock file adjacent to
    .metadata.json. msvcrt on Windows, fcntl elsewhere. Best-effort: if the
    platform module is unavailable the lock degrades to a no-op (the
    create/mutate window is tiny), but on the two platforms pv.py runs on
    it's a real lock."""

    def __init__(self, lock_path: Path) -> None:
        self._lock_path = lock_path
        self._handle = None

    def __enter__(self) -> "_FileLock":
        self._handle = open(self._lock_path, "a+")
        try:
            import msvcrt

            self._handle.seek(0)
            msvcrt.locking(self._handle.fileno(), msvcrt.LK_LOCK, 1)
        except ImportError:
            try:
                import fcntl

                fcntl.flock(self._handle.fileno(), fcntl.LOCK_EX)
            except ImportError:
                pass
        return self

    def __exit__(self, *exc_info) -> None:
        if self._handle is None:
            return
        try:
            import msvcrt

            self._handle.seek(0)
            msvcrt.locking(self._handle.fileno(), msvcrt.LK_UNLCK, 1)
        except (ImportError, OSError):
            try:
                import fcntl

                fcntl.flock(self._handle.fileno(), fcntl.LOCK_UN)
            except (ImportError, OSError):
                pass
        self._handle.close()
        self._handle = None


def apply_flag_ops(
    current: list[str], adds: list[str], removes: list[str], toggles: list[str]
) -> list[str]:
    """Returns the new flag list. Order follows VALID_FLAGS (canonical),
    not insertion order, so the on-disk array is deterministic."""
    result = set(current)
    for name in toggles:
        if name in result:
            result.discard(name)
        else:
            result.add(name)
    for name in adds:
        result.add(name)
    for name in removes:
        result.discard(name)
    return [f for f in VALID_FLAGS if f in result]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--xxxx", required=True, help="Code of the change/fix.")
    parser.add_argument(
        "--state",
        help="State folder under changes/ (e.g. inProgress, implemented). "
        "If omitted, every state except todo/ is searched for --xxxx.",
    )
    parser.add_argument(
        "--add-flag",
        action="append",
        default=[],
        metavar="NAME",
        help=f"Add a flag (repeatable). Valid: {', '.join(VALID_FLAGS)}.",
    )
    parser.add_argument(
        "--remove-flag",
        action="append",
        default=[],
        metavar="NAME",
        help="Remove a flag (repeatable).",
    )
    parser.add_argument(
        "--toggle-flag",
        action="append",
        default=[],
        metavar="NAME",
        help="Toggle a flag (repeatable): add it if absent, remove it if present.",
    )
    parser.add_argument(
        "--set-risk",
        type=int,
        default=None,
        metavar="N",
        help="Set the change's risk median (integer 0-10), from "
        "pv-internal-tech-risks. Independent of flags; doesn't touch "
        "flagsLastModified.",
    )
    parser.add_argument(
        "--work-folder",
        help="Path to workFolder, relative to the repo root. If not given, "
        "read from .claude/pv-context.json (default '/').",
    )
    parser.add_argument(
        "--print",
        dest="print_json",
        action="store_true",
        help="Also emit the resulting .metadata.json as JSON on stdout.",
    )
    args = parser.parse_args()

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    requested = args.add_flag + args.remove_flag + args.toggle_flag
    if not requested and args.set_risk is None:
        parser.error(
            "nothing to do: pass at least one of --add-flag / --remove-flag / "
            "--toggle-flag / --set-risk."
        )
    unknown = sorted({f for f in requested if f not in VALID_FLAGS})
    if unknown:
        parser.error(
            f"unknown flag(s): {', '.join(unknown)}. "
            f"Valid flags: {', '.join(VALID_FLAGS)}."
        )
    if args.set_risk is not None and not (0 <= args.set_risk <= 10):
        parser.error(
            f"--set-risk must be an integer 0-10, got {args.set_risk}."
        )

    root = repo_root()
    work_folder_rel = args.work_folder or load_work_folder(root)
    changes_dir = resolve_changes_dir(root, work_folder_rel)
    entry_dir = resolve_entry_dir(changes_dir, args.xxxx, args.state)

    with _FileLock(entry_dir / LOCK_FILENAME):
        data = read_metadata(entry_dir)

        raw_flags = data.get("flags", [])
        if not isinstance(raw_flags, list):
            raise SystemExit(
                f"{entry_dir / METADATA_FILENAME}: 'flags' must be an array, "
                f"got {type(raw_flags).__name__}."
            )
        current = [f for f in VALID_FLAGS if f in raw_flags]

        new_flags = apply_flag_ops(
            current, args.add_flag, args.remove_flag, args.toggle_flag
        )

        flags_changed = new_flags != current

        old_risk = data.get("risk")
        risk_changed = args.set_risk is not None and old_risk != args.set_risk

        if flags_changed:
            data["flags"] = new_flags
            data["flagsLastModified"] = date.today().isoformat()
        if risk_changed:
            data["risk"] = args.set_risk

        if flags_changed or risk_changed:
            write_metadata(entry_dir, data)
        elif not (entry_dir / METADATA_FILENAME).is_file():
            # Still materialise the file if it was absent and the caller
            # asked for a concrete (even if unchanged) state -- keeps
            # "--add-flag X" / "--set-risk N" idempotent from the caller's
            # point of view.
            data.setdefault("flags", new_flags)
            data.setdefault("flagsLastModified", date.today().isoformat())
            if args.set_risk is not None:
                data.setdefault("risk", args.set_risk)
            write_metadata(entry_dir, data)

    rel = entry_dir.relative_to(root).as_posix()
    parts: list[str] = []
    if flags_changed:
        added = sorted(set(new_flags) - set(current))
        removed = sorted(set(current) - set(new_flags))
        if added:
            parts.append("added " + ", ".join(added))
        if removed:
            parts.append("removed " + ", ".join(removed))
        parts.append(f"flags now [{', '.join(new_flags)}]")
    elif requested:
        parts.append(f"flags unchanged [{', '.join(new_flags)}]")
    if risk_changed:
        if old_risk is None:
            parts.append(f"risk set to {args.set_risk}")
        else:
            parts.append(f"risk {old_risk} -> {args.set_risk}")
    elif args.set_risk is not None:
        parts.append(f"risk unchanged ({args.set_risk})")

    if flags_changed or risk_changed:
        print(f"{rel}: {'; '.join(parts)}")
    else:
        print(f"{rel}: no change -> {'; '.join(parts)}")

    if args.print_json:
        print(json.dumps(read_metadata(entry_dir), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
