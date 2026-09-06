#!/usr/bin/env python3
"""Mutates a change/fix's .metadata.json in the pv-* framework.

Single entry point for every write to
{workFolder}/changes/{state}/{xxxx}/.metadata.json -- the per-change file
of mutable state that sits next to description.md / plan.md / history.md.
Handles three independent pieces of state:
  - the 'flags' array (a set of extensible status labels: today 'priority'
    and 'workinprogress'), via --add-flag / --remove-flag / --toggle-flag.
  - the 'risk' integer 0-10 (the median of pv-internal-tech-risks' 9
    factors), via --set-risk. Written by pv-how in step 3.1, right after
    plan.md is drafted. Absent = not yet assessed.
  - the 'relatedIds' array (codes of other changes/fixes related to this
    one), via --add-related / --remove-related. Written by pv-new/pv-fix
    when the user points out a relation or the skill detects one during
    analysis. Each id passed to --add-related must exist under some
    non-todo state of changes/, and can't be the entry's own --xxxx.
    relatedIds is RECIPROCAL: --add-related B on --xxxx A also adds A to
    B's own relatedIds (and --remove-related the same, in reverse) in the
    same invocation, so a relation never ends up known to only one side.
A single invocation can touch flags, risk, relatedIds, or any combination;
each is optional.

State resolution: given --xxxx, the script looks for the change folder
under every direct subfolder of {workFolder}/changes/ (inProgress,
implemented, closed, ...), skipping todo/. Pass --state to skip the search
and target one state directly. todo/ is rejected on purpose: a todo is a
loose idea outside the flow -- there's nothing "in progress" or
"prioritised within the flow" to mark. Any operation that resolves to a
folder under todo/ (or an explicit --state todo) is an error and writes
nothing. The same non-todo search is used to validate each --add-related
id.

Concurrency: the read-modify-write cycle is guarded by an exclusive file
lock on an adjacent {folder}/.metadata.json.lock, so a toggle from pv.py
and one from a Claude Code session in parallel can't clobber each other.
No last-write-wins. When relatedIds' reciprocal side also needs writing,
every affected folder (--xxxx plus each touched related id) is locked and
written one at a time, always in a fixed order (sorted by code) across the
whole invocation -- so two concurrent set-metadata.py runs touching an
overlapping pair of entries always acquire locks in the same order and
can't deadlock each other.

The file is created on first write and NEVER deleted, even if 'flags'
ends up []. Unknown fields are preserved verbatim.

Every effective FLAG mutation refreshes 'flagsLastModified' to today's
date. 'risk' and 'relatedIds' have no timestamp of their own and never
touch 'flagsLastModified'. An operation that changes nothing (e.g.
--remove-flag on a flag that isn't set, --add-flag on one already set,
--set-risk to the value already stored, or --add-related on an id already
present) leaves the file untouched and reports it as a no-op.

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
  python set-metadata.py --xxxx 00192 --add-related 00212 --add-related 00214
  python set-metadata.py --xxxx 00192 --remove-related 00212
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


def find_entry_dirs(changes_dir: Path, xxxx: str) -> list[Path]:
    """Every non-todo {changes_dir}/{state}/{xxxx}/ that exists, across all
    states. Used both to resolve --xxxx itself and to validate a
    --add-related id (which must exist somewhere, but ambiguity across
    states isn't an error for a *related* id the way it is for --xxxx)."""
    if not changes_dir.is_dir():
        return []
    matches: list[Path] = []
    for state_dir in sorted(p for p in changes_dir.iterdir() if p.is_dir()):
        if state_dir.name == "todo":
            continue
        candidate = state_dir / xxxx
        if candidate.is_dir():
            matches.append(candidate)
    return matches


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

    matches = find_entry_dirs(changes_dir, xxxx)
    todo_match = (changes_dir / "todo" / xxxx).is_dir()

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


def apply_related_ops(
    current: list[str], adds: list[str], removes: list[str]
) -> list[str]:
    """Returns the new relatedIds list. No fixed enum here (unlike flags),
    so the result is sorted numerically for a deterministic on-disk
    array."""
    result = set(current)
    result.update(adds)
    result.difference_update(removes)
    return sorted(result, key=lambda code: (len(code), code))


def mutate_related_only(entry_dir: Path, adds: list[str], removes: list[str]) -> bool:
    """Applies --add-related/--remove-related to a single entry_dir's
    relatedIds, under its own file lock. Used for the *reciprocal* side of
    a relation (the id(s) named by --add-related/--remove-related, not the
    --xxxx entry itself) -- doesn't touch flags/risk, doesn't print
    anything, doesn't re-validate existence (the caller already resolved
    entry_dir). Returns whether anything actually changed."""
    with _FileLock(entry_dir / LOCK_FILENAME):
        data = read_metadata(entry_dir)
        raw_related = data.get("relatedIds", [])
        if not isinstance(raw_related, list):
            raise SystemExit(
                f"{entry_dir / METADATA_FILENAME}: 'relatedIds' must be an "
                f"array, got {type(raw_related).__name__}."
            )
        current_related = sorted(
            {rid for rid in raw_related if isinstance(rid, str)},
            key=lambda code: (len(code), code),
        )
        new_related = apply_related_ops(current_related, adds, removes)
        changed = new_related != current_related
        if changed:
            data["relatedIds"] = new_related
            write_metadata(entry_dir, data)
        return changed


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
        "--add-related",
        action="append",
        default=[],
        metavar="XXXX",
        help="Add a related change/fix id (repeatable). Must exist under "
        "some non-todo state of changes/, and can't be --xxxx itself.",
    )
    parser.add_argument(
        "--remove-related",
        action="append",
        default=[],
        metavar="XXXX",
        help="Remove a related change/fix id (repeatable).",
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
    related_requested = args.add_related + args.remove_related
    if not requested and args.set_risk is None and not related_requested:
        parser.error(
            "nothing to do: pass at least one of --add-flag / --remove-flag / "
            "--toggle-flag / --set-risk / --add-related / --remove-related."
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
    bad_format = sorted({rid for rid in related_requested if not rid.isdigit()})
    if bad_format:
        parser.error(
            f"invalid related id(s): {', '.join(bad_format)}. "
            "A related id must be a change/fix's numeric code."
        )
    self_referencing = sorted(set(args.add_related) & {args.xxxx})
    if self_referencing:
        parser.error(f"'{args.xxxx}' can't be listed as related to itself.")

    root = repo_root()
    work_folder_rel = args.work_folder or load_work_folder(root)
    changes_dir = resolve_changes_dir(root, work_folder_rel)
    entry_dir = resolve_entry_dir(changes_dir, args.xxxx, args.state)

    missing_related = sorted(
        rid for rid in set(args.add_related) if not find_entry_dirs(changes_dir, rid)
    )
    if missing_related:
        raise SystemExit(
            "no change/fix folder found (in any non-todo state) for related "
            f"id(s): {', '.join(missing_related)}."
        )

    # relatedIds is reciprocal: resolve every id named by --add-related /
    # --remove-related to its own folder now, so the other side of the
    # relation gets updated too (mutate_related_only below). A
    # --remove-related id that no longer exists (or never did) is not an
    # error -- there's nothing to clean up on that side.
    reciprocal_dirs: dict[str, Path] = {}
    for rid in set(args.add_related) | set(args.remove_related):
        matches = find_entry_dirs(changes_dir, rid)
        if matches:
            reciprocal_dirs[rid] = matches[0]

    # Fixed lock order (by code, entry_dir's own folder included) across the
    # whole invocation, so two concurrent runs touching an overlapping pair
    # never acquire locks in opposite order.
    own_code = entry_dir.name
    ordered_reciprocal = sorted(
        (rid for rid in reciprocal_dirs if rid != own_code),
        key=lambda code: (len(code), code),
    )

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

        raw_related = data.get("relatedIds", [])
        if not isinstance(raw_related, list):
            raise SystemExit(
                f"{entry_dir / METADATA_FILENAME}: 'relatedIds' must be an "
                f"array, got {type(raw_related).__name__}."
            )
        current_related = sorted(
            {rid for rid in raw_related if isinstance(rid, str)},
            key=lambda code: (len(code), code),
        )
        new_related = apply_related_ops(
            current_related, args.add_related, args.remove_related
        )
        related_changed = new_related != current_related

        if flags_changed:
            data["flags"] = new_flags
            data["flagsLastModified"] = date.today().isoformat()
        if risk_changed:
            data["risk"] = args.set_risk
        if related_changed:
            data["relatedIds"] = new_related

        if flags_changed or risk_changed or related_changed:
            write_metadata(entry_dir, data)
        elif not (entry_dir / METADATA_FILENAME).is_file():
            # Still materialise the file if it was absent and the caller
            # asked for a concrete (even if unchanged) state -- keeps
            # "--add-flag X" / "--set-risk N" / "--add-related X" idempotent
            # from the caller's point of view.
            data.setdefault("flags", new_flags)
            data.setdefault("flagsLastModified", date.today().isoformat())
            if args.set_risk is not None:
                data.setdefault("risk", args.set_risk)
            if related_requested:
                data.setdefault("relatedIds", new_related)
            write_metadata(entry_dir, data)

    # Reciprocal side: an effective add/remove of a related id also
    # touches that id's own relatedIds, so the relation is never known to
    # only one side. Locked and written one entry at a time, in the fixed
    # order resolved above -- never re-locks entry_dir itself.
    added_related_ids = sorted(set(new_related) - set(current_related))
    removed_related_ids = sorted(set(current_related) - set(new_related))
    reciprocal_changed: list[str] = []
    for rid in ordered_reciprocal:
        rid_adds = [own_code] if rid in added_related_ids else []
        rid_removes = [own_code] if rid in removed_related_ids else []
        if not rid_adds and not rid_removes:
            continue
        if mutate_related_only(reciprocal_dirs[rid], rid_adds, rid_removes):
            reciprocal_changed.append(rid)

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
    if related_changed:
        if added_related_ids:
            parts.append("added related " + ", ".join(added_related_ids))
        if removed_related_ids:
            parts.append("removed related " + ", ".join(removed_related_ids))
        parts.append(f"related now [{', '.join(new_related)}]")
    elif related_requested:
        parts.append(f"related unchanged [{', '.join(new_related)}]")
    if reciprocal_changed:
        parts.append(
            "reciprocated on " + ", ".join(sorted(reciprocal_changed, key=lambda c: (len(c), c)))
        )

    if flags_changed or risk_changed or related_changed or reciprocal_changed:
        print(f"{rel}: {'; '.join(parts)}")
    else:
        print(f"{rel}: no change -> {'; '.join(parts)}")

    if args.print_json:
        print(json.dumps(read_metadata(entry_dir), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
