#!/usr/bin/env python3
"""Renders the flag-icon prefix for one or more change/fix codes, for pv.py.

pv.py is a single self-contained file that imports nothing, so it can't
reuse pv-status's canonical flag map (terminal_output.FLAG_*) directly. It
calls this script via run_script() the same way it already calls
render_status.py / filter_status.py, and gets back the ready-rendered
prefix string per code.

Batch input from day 1 (decision 6.13): pass several --xxxx in one
invocation, get one line of output per code, in the same order. pv.py's
list_implemented_entries() calls this ONCE with every code in its list --
1 subprocess, not N (Python startup on Windows is slow).

Color: pass --color / --no-color to force the icon style. pv.py always
does (based on its own terminal), because it captures our stdout, so our
own isatty() check would always report "no tty" and fall back to ASCII.
Without either flag, we decide from our own stdout -- correct only when a
human runs this script directly.

For each --xxxx, one line on stdout:
  - the flags_prefix (e.g. "⭐ ⚙️  ", or "[P] [W]  " when NO_COLOR / no
    tty), already rendered per terminal_output.flags_prefix()
  - an empty line if that change has no flags, is a todo/ entry (todos
    never carry flags), or the code doesn't resolve to any folder

State resolution mirrors set-metadata.py: every state under changes/ is
searched (skipping todo/); pass --state to pin one. The output is
position-based, so an unresolved --xxxx still consumes its line (emitted
empty) -- pv.py can zip output lines to its input list without
realignment.

Usage:
  python read-flags.py --xxxx 00192 --xxxx 00184 --terminal
  python read-flags.py --xxxx 1001 --state implemented --terminal --width 80
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from collect_status import load_changes_dir, read_flags, repo_root  # noqa: E402
import terminal_output as term  # noqa: E402


def resolve_entry_dir(changes_dir: Path, xxxx: str, state: str | None) -> Path | None:
    """Finds {changes_dir}/{state}/{xxxx}/. Searches every state except
    todo/ if --state wasn't given. Returns None (never raises) if not
    found, ambiguous, or under todo/ -- the caller wants an empty line for
    any of those, not an error."""
    if state is not None:
        if state == "todo":
            return None
        candidate = changes_dir / state / xxxx
        return candidate if candidate.is_dir() else None

    if not changes_dir.is_dir():
        return None
    matches = []
    for state_dir in sorted(p for p in changes_dir.iterdir() if p.is_dir()):
        if state_dir.name == "todo":
            continue
        candidate = state_dir / xxxx
        if candidate.is_dir():
            matches.append(candidate)
    return matches[0] if len(matches) == 1 else None


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--xxxx",
        action="append",
        default=[],
        required=True,
        metavar="CODE",
        help="Code of a change/fix (repeatable). One output line per code, in order.",
    )
    parser.add_argument(
        "--state",
        help="State folder under changes/ to look in. If omitted, every state "
        "except todo/ is searched for each --xxxx.",
    )
    parser.add_argument(
        "--work-folder",
        help="Path to workFolder relative to the repo root. If not given, "
        "read from .claude/pv-context.json (default '/').",
    )
    parser.add_argument(
        "--terminal",
        action="store_true",
        help="Plain-text output (the only mode). Present for symmetry with the "
        "other pv-status scripts pv.py invokes.",
    )
    parser.add_argument(
        "--width",
        type=int,
        default=term.DEFAULT_WIDTH,
        help="Accepted for symmetry with the other pv-status scripts; unused "
        "(a flag prefix has no column width to fit).",
    )
    color_group = parser.add_mutually_exclusive_group()
    color_group.add_argument(
        "--color",
        dest="color",
        action="store_true",
        default=None,
        help="Force emoji icons regardless of this process's stdout. pv.py "
        "passes this (based on ITS OWN terminal) because it captures our "
        "stdout, so our own isatty() check would always say 'no tty'.",
    )
    color_group.add_argument(
        "--no-color",
        dest="color",
        action="store_false",
        help="Force ASCII icons ([P]/[W]).",
    )
    args = parser.parse_args()

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    # --color / --no-color win; otherwise fall back to our own stdout check
    # (right when a human runs this script directly, wrong when pv.py pipes
    # us -- hence pv.py always passes an explicit flag).
    color = args.color if args.color is not None else term.supports_color()
    root = repo_root()
    changes_dir = load_changes_dir(root, args.work_folder)

    out_lines = []
    for xxxx in args.xxxx:
        entry_dir = resolve_entry_dir(changes_dir, xxxx, args.state)
        if entry_dir is None:
            out_lines.append("")
            continue
        out_lines.append(term.flags_prefix(read_flags(entry_dir), color=color))

    # Exactly len(args.xxxx) lines, no trailing blank beyond them.
    print("\n".join(out_lines))


if __name__ == "__main__":
    main()
