#!/usr/bin/env python3
"""Interactive menu for the pv-* framework, for direct use from a terminal.

This file is generated/updated at the repo root by install.sh/install.ps1 on
every install or update, and also by the pv-init skill on every run — don't
edit it by hand, your changes would be lost the next time either happens
(master copy at .claude/skills/pv-init/assets/pv.py).

Meant for an advanced user who wants to check or close pv-* framework
changes without going through Claude Code or having to remember script
names, paths, or parameters: run this file and choose a menu option.

Most options are read-only and delegate to the pv-status skill's scripts.
Four options modify something:
- "Close an implemented entry": moves the folder from
  changes/implemented/{xxxx} to changes/closed/{xxxx} (delegating to
  pv-internal-workflow's move-change.py, which doesn't touch any file's
  content, only the folder), and always asks for explicit confirmation
  before moving anything.
- "Toggle a flag on a change" (inside "Changes info"): adds/removes a
  status flag (priority / workinprogress) on a change's .metadata.json,
  delegating every write to pv-internal-workflow's set-metadata.py (pv.py
  never writes .metadata.json itself). No confirm() -- a flag is
  trivially reversible (the same call flips it back); after each toggle
  the flag list is re-shown with the change reflected, and the change
  picker stays open too, so several flags/changes can be toggled without
  leaving. The flag icons shown in every change listing come from
  pv-status's read-flags.py (batch input: one subprocess per state);
  pv.py passes it --color/--no-color matching pv.py's own terminal,
  since it captures read-flags.py's stdout (a pipe, never a tty).
- "Ideas in todo/" (now a submenu): lists ideas and, once one is chosen,
  offers deleting its whole folder (delegating to pv-internal-workflow's
  delete-todo.py), always asking for explicit confirmation first. Every
  path that shows an idea's detail card ("Ideas in todo/", "Search by
  id", and "General project status"'s own id prompt) offers this same
  "delete this idea" follow-up, since it's the identical card everywhere
  (see show_id_detail_card()).
- "Sync skill models per pv-context.json" (inside the "Configuration"
  submenu): delegates to pv-init's sync-skill-models.py, which propagates
  pv-context.json's skillModels to each 'pv-*' SKILL.md's frontmatter
  (model/effort).
- "Change max character width" (inside the "Configuration" submenu): the
  only place pv.py *writes* pv-context.json -- it stores a single integer
  at framework.onescript.width (>= 40; empty input keeps the current
  value), read back on every launch to set this file's WIDTH. A minimal
  read-modify-write that preserves every other field and key order; still
  gated behind a confirm(). Under --testconfig the same value is read from
  / written to pv-config-test.json at the identical framework.onescript.width
  path, so the exact same code handles both.

"Changes info" opens a submenu with five options: "Search by id" (exact
id match, cheap -- doesn't read description.md except the match's),
"Search by content" (text match in description.md, reads every entry),
"Search by state" (the former top-level "Listing filtered by state"
option, now nested here), "Toggle a flag on a change" (the only
state-mutating option here -- see above), and "Show changes by flag"
(read-only: filter_status.py --flag, lists every change carrying the
chosen flag, across states). The searches scan every state; kept as
separate options rather than one combined search so each stays as fast as
the kind of lookup it's actually doing.

"Check Previo versions" opens a submenu that lists {workFolder}/versions/{XXXX}/
folders and prints the chosen one's changelog.md.

Design notes (screen types, colors, how to extend this menu) live in
.claude/pv-doc/pv-design-onescript/pv-design-onescript.es.md -- read it before adding a new menu,
submenu, or screen type.

--testconfig is a test-harness-only flag, not for normal end-user use: it
takes no argument -- it reads pv-config-test.json from this same script's
own folder, whose node tree mirrors pv-context.json's own
({"repoRoot": "..", "framework": {"workFolder": "...", "onescript": {...}}})
so the same code finds each value at the same path. repoRoot stays
top-level -- it has no pv-context.json equivalent (test-only: where the
real repo root is when pv.py runs as a copy outside it). Used instead of
the repo's real .claude/pv-context.json, letting pv.py be run against
throwaway fixture data (e.g. test/previo-sdd/) without touching the real
workFolder. The framework's real scripts are still invoked as-is (never
copied) -- only the --work-folder value forwarded to the ones that
support it changes. pv.py's own persisted settings (framework.onescript.*)
are also read from / written to this file instead of pv-context.json, at
the identical nested path. See test/pv-test.py and test/pv-config-test.json for
the intended setup (a plain copy of this same file, run with --testconfig
from inside test/, where its sibling pv-config-test.json lives).

Usage:
  python3 pv.py
  python3 pv.py --testconfig
"""

import argparse
import json
import os
import re
import subprocess
import sys
import textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parent
STATUS_SCRIPTS = ROOT / ".claude" / "skills" / "pv-status" / "scripts"
WORKFLOW_SCRIPTS = ROOT / ".claude" / "skills" / "pv-internal-workflow" / "scripts"
INIT_SCRIPTS = ROOT / ".claude" / "skills" / "pv-init" / "scripts"
INIT_SKILL_PATH = ROOT / ".claude" / "skills" / "pv-init" / "SKILL.md"
CONTEXT_PATH = ROOT / ".claude" / "pv-context.json"

# The config file pv.py reads its own settings from and writes them back to:
# CONTEXT_PATH normally, or the --testconfig file when that flag is passed
# (set in main()). Both carry pv.py's settings at the same nested path
# (framework.onescript.*), so load_onescript_width()/save_onescript_width()
# don't branch on which one it is.
ACTIVE_CONFIG_PATH = CONTEXT_PATH

# Set by main() when --testconfig is passed: the workFolder value to use
# instead of reading it from CONTEXT_PATH, and to forward as --work-folder
# to the external scripts that accept that override.
TEST_WORK_FOLDER: str | None = None

# The subset of scripts invoked via run_script() that accept --work-folder
# as an explicit override (filter_status.py, render_status.py,
# list_todo.py, read-flags.py, move-change.py, set-metadata.py,
# delete-todo.py). sync-skill-models.py doesn't touch changes/ or
# workFolder at all, so it has no such flag and is never forwarded one.
SCRIPTS_ACCEPTING_WORK_FOLDER = {
    "filter_status.py",
    "render_status.py",
    "list_todo.py",
    "read-flags.py",
    "move-change.py",
    "set-metadata.py",
    "delete-todo.py",
}

# The pv-status scripts whose --terminal output's column width is caller-
# supplied via --width (terminal_output.py has no fixed WIDTH of its own --
# see its module docstring). run_script() always forwards pv.py's own WIDTH
# here, so delegated screens (general status, searches, the detail card,
# the ideas listing) match this file's own menu/selection screens exactly.
# read-flags.py accepts --width for symmetry (it ignores it -- a flag
# prefix has no column to fit), so forwarding it is harmless.
SCRIPTS_ACCEPTING_WIDTH = {
    "filter_status.py",
    "render_status.py",
    "list_todo.py",
    "read-flags.py",
}

# Canonical flag catalogue -- kept in sync BY HAND with
# pv-status/scripts/terminal_output.py's FLAG_* maps and
# pv-internal-workflow/metadata.schema.json's enum. pv.py imports nothing,
# so it can't reuse those; it only needs the enum value <-> human label
# mapping for its own show_selection()s. The ICONS shown in listings come
# from read-flags.py (which DOES use terminal_output), never rendered here.
FLAG_VALUES = ["priority", "workinprogress"]  # canonical order
FLAG_LABELS = {"priority": "Priority", "workinprogress": "Work in progress"}
FLAG_ICONS = {"priority": "⭐", "workinprogress": "⚙️"}
FLAG_ICONS_ASCII = {"priority": "[P]", "workinprogress": "[W]"}


# =============================================================================
# Rendering primitives (color, width, low-level text helpers)
# =============================================================================
#
# Two-level color hierarchy, applied per whole screen block, never mixed
# within the same block:
#   - GOLD:      menu screens (print_header/run_menu) -- "you're navigating"
#   - DARK_GRAY: selection and info screens (show_selection/show_info) --
#                "you're viewing or picking data"
# See .claude/pv-doc/pv-design-onescript/pv-design-onescript.es.md > "Estilo por Tipo de Pantalla" for
# the full rationale and exact mockups.

WIDTH = 80  # default; overridden at startup by framework.onescript.width if set
MIN_WIDTH = 40  # below this, RING_ART and the delegated detail cards break
COLOR_RESET = "\033[0m"
GOLD = "\033[38;5;220m"
DARK_GRAY = "\033[38;5;238m"

# Per-state colors, used only to tint each option's text in "Available
# states:" (search_by_state()) -- an exception to the "one color per whole
# screen" rule (see "Estilo por Tipo de Pantalla" in the design doc),
# scoped to individual list items rather than the screen's own frame/rule,
# which stays DARK_GRAY like any other show_selection() call.
STATE_BLUE = "\033[38;5;75m"  # todo: not started yet
STATE_YELLOW = "\033[38;5;220m"  # inProgress: in progress
STATE_GREEN = "\033[38;5;114m"  # implemented: ready to close
STATE_WHITE = "\033[38;5;255m"  # closed: done
STATE_COLORS = {
    "todo": STATE_BLUE,
    "inProgress": STATE_YELLOW,
    "implemented": STATE_GREEN,
    "closed": STATE_WHITE,
}

# Gradient by character density, modeled on the actual One Ring: from the
# pale golden glow of the loose strokes (".", ":", "-") to the brown/maroon
# shadow of the metal in the densest areas ("#", "%").
RING_CHAR_COLORS = {
    ".": 223,
    ":": 220,
    "-": 214,
    "=": 208,
    "+": 166,
    "*": 130,
    "#": 94,
    "%": 52,
}

NAME_RE = re.compile(r"\*\*Name\*\*\s*[:—-]\s*(.+)")
VERSION_RE = re.compile(r"^\s*version:\s*(\S+)", re.MULTILINE)
VERSION_RE = re.compile(r"^\s*version:\s*(\S+)", re.MULTILINE)
IDEA_RE = re.compile(
    r"^##\s*Idea\s*\n+(.+?)(?=\n##\s|\Z)", re.IGNORECASE | re.MULTILINE | re.DOTALL
)


def supports_color() -> bool:
    if os.environ.get("NO_COLOR"):
        return False
    return sys.stdout.isatty()


def colorize(text: str, color: str) -> str:
    if not supports_color():
        return text
    return f"{color}{text}{COLOR_RESET}"


def colorize_ring_art(art: str) -> str:
    if not supports_color():
        return art

    out = []
    current_color = None
    for ch in art:
        color = RING_CHAR_COLORS.get(ch)
        if color != current_color:
            if current_color is not None:
                out.append(COLOR_RESET)
            if color is not None:
                out.append(f"\033[38;5;{color}m")
            current_color = color
        out.append(ch)
    if current_color is not None:
        out.append(COLOR_RESET)
    return "".join(out)


def enable_windows_ansi() -> None:
    if sys.platform != "win32":
        return
    import ctypes

    ENABLE_VIRTUAL_TERMINAL_PROCESSING = 0x0004
    handle = ctypes.windll.kernel32.GetStdHandle(-11)  # STD_OUTPUT_HANDLE
    mode = ctypes.c_uint32()
    if ctypes.windll.kernel32.GetConsoleMode(handle, ctypes.byref(mode)):
        ctypes.windll.kernel32.SetConsoleMode(
            handle, mode.value | ENABLE_VIRTUAL_TERMINAL_PROCESSING
        )


def hr(char: str = "=", color: str = DARK_GRAY) -> None:
    print(colorize(char * WIDTH, color))


def read_input(prompt: str) -> str:
    """input() wrapper that lets "exit" quit the whole program from any
    screen that asks for a real answer (menu choice, selection, y/N
    confirmation, free-text search) -- case-insensitive, surrounding
    whitespace ignored. Not used by the "Press Enter to return..." pause,
    which treats any input (including "exit") as just continuing."""
    answer = input(prompt)
    if answer.strip().lower() == "exit":
        sys.exit(0)
    return answer


def wrap(text: str, indent: str = "") -> str:
    return textwrap.fill(
        text,
        width=WIDTH,
        initial_indent=indent,
        subsequent_indent=" " * len(indent),
    )


RING_ART = r"""
     ........
  :=. . ..:::::----:
 -*:.:..:---=---:-====-.
:*#-.       .:=*+==--==+=:
++#*:            :-+*+==**+.
++*##=              :+**==**: 	Previo: the AI-driven, visual,
*+=*##*:              :**=+#*.	rapid-development framework.
 *++***#*-.             +*=**:
  +*+******+-.           ***= 	One script, growing
   -**+++*####*+-:.      --:. 	to manage more.
     -++++**#*##***++===---:
       .=*###+#****+**+--:
           :=+*###%#*=:.
"""


# =============================================================================
# Screen-type helpers
# =============================================================================
#
# Every interactive screen in this file is one of these building blocks.
# Adding a new menu, submenu, or list should mean calling one of these --
# not hand-rolling hr()/print() calls. See .claude/pv-doc/pv-design-onescript/pv-design-onescript.es.md
# for the full catalogue of screen types and their exact appearance.


def print_header(title: str) -> None:
    """Menu-screen header: GOLD rule + centered GOLD title + GOLD rule."""
    hr("=", GOLD)
    print(colorize(title.center(WIDTH), GOLD))
    hr("=", GOLD)


def show_selection(
    title: str,
    options: list[str],
    prompt: str,
    extra_option: tuple[str, str] | None = None,
    options_shown: bool = False,
) -> int | str | None:
    """Selection screen: numbered list framed by DARK_GRAY '-' rules.

    Returns the chosen option's 0-based index into `options`, the
    extra_option's key (lowercased) if picked, or None if the user
    cancelled (empty input) or entered something invalid. Returning an
    index rather than the option's text avoids ambiguity when two options
    render the same label. `extra_option` is a (key, label) pair for a
    non-numeric choice, e.g. ("a", "Close all") -- see close_entry() for a
    real usage.

    `title=""` omits the title line and the leading blank line -- used for
    an inline selection directly under a listing it acts on (see "Inline
    Selection" in the design doc's glossary), so the '-' rule sits right
    below that listing's own closing rule instead of floating apart from
    it.

    `options_shown=True` means the caller has ALREADY printed the numbered
    options itself (e.g. a grouped listing with headings show_selection()
    can't render) -- so only the opening '-' rule and the prompt are
    emitted, not the flat list again. The caller's numbering must match
    `options`' order 1:1. Implies `title=""`.
    """
    if not options_shown:
        if title:
            print()
        hr("-")
        if title:
            print(title)
        for i, option in enumerate(options, start=1):
            print(wrap(f"{i}. {option}", indent="  "))
        if extra_option:
            key, label = extra_option
            print(wrap(f"{key}. {label}", indent="  "))
        hr("-")

    choice = read_input(prompt).strip()
    if not choice:
        return None

    if extra_option and choice.lower() == extra_option[0].lower():
        return choice.lower()

    index = int(choice) - 1 if choice.lstrip("-").isdigit() else -1
    if 0 <= index < len(options):
        return index

    print("Invalid option.")
    return None


def show_info(lines: list[str], framed: bool = True) -> None:
    """Info screen: plain content, optionally framed by DARK_GRAY '-' rules.

    Use framed=True for content worth setting apart (e.g. a changelog's raw
    text); framed=False for a short paragraph that doesn't need a frame
    (e.g. a one-off status message).
    """
    print()
    if framed:
        hr("-")
    for line in lines:
        print(line)
    if framed:
        hr("-")


def confirm(question: str) -> bool:
    """Yes/no confirmation, no frame of its own -- nests inside whatever
    screen (usually a Selection) triggered it."""
    print(wrap(question))
    answer = read_input("(y/N): ").strip().lower()
    return answer in ("y", "yes")


# =============================================================================
# Framework paths and shared lookups
# =============================================================================


def _script_args(script: Path, args: tuple[str, ...]) -> list[str]:
    full_args = list(args)
    if TEST_WORK_FOLDER is not None and script.name in SCRIPTS_ACCEPTING_WORK_FOLDER:
        full_args += ["--work-folder", TEST_WORK_FOLDER]
    if script.name in SCRIPTS_ACCEPTING_WIDTH:
        full_args += ["--width", str(WIDTH)]
    return full_args


def run_script(script: Path, *args: str) -> None:
    subprocess.run(
        [sys.executable, str(script), *_script_args(script, args)], cwd=ROOT
    )


def run_script_capture(script: Path, *args: str) -> str:
    """Like run_script() but returns the script's stdout instead of letting
    it print through. Used when pv.py needs the output as data (e.g.
    read-flags.py's per-code flag prefixes) rather than as a screen. Same
    --work-folder / --width forwarding. Returns "" on a non-zero exit or
    any failure to launch -- a missing flag prefix must never break a
    listing."""
    try:
        result = subprocess.run(
            [sys.executable, str(script), *_script_args(script, args)],
            cwd=ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
    except OSError:
        return ""
    return result.stdout if result.returncode == 0 else ""


def work_root() -> Path:
    # workFolder is always relative to the repo root, whether or not it
    # carries a leading "/" (that's only a convention to make it visually
    # explicit) -- Path("/a") / "/b" would otherwise discard "a" entirely,
    # since pathlib treats a leading-slash operand as its own absolute path.
    if TEST_WORK_FOLDER is not None:
        work_folder_rel = TEST_WORK_FOLDER
    else:
        context = json.loads(CONTEXT_PATH.read_text(encoding="utf-8"))
        work_folder_rel = context.get("framework", {}).get("workFolder", "/")
    return ROOT / (work_folder_rel or "").lstrip("/")


def load_onescript_width() -> int:
    """Reads framework.onescript.width from the active config file
    (ACTIVE_CONFIG_PATH -- pv-context.json, or the --testconfig file, both
    using the same nested path). Returns the module default WIDTH if the
    file, the section, or the field is absent, or if the value isn't an int
    >= MIN_WIDTH -- a malformed setting falls back silently rather than
    failing a launch, matching how the rest of this file treats config."""
    try:
        config = json.loads(ACTIVE_CONFIG_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return WIDTH
    value = config.get("framework", {}).get("onescript", {}).get("width")
    if isinstance(value, int) and not isinstance(value, bool) and value >= MIN_WIDTH:
        return value
    return WIDTH


def save_onescript_width(width: int) -> None:
    """Writes framework.onescript.width into the active config file,
    preserving every other field and the existing key order (read-modify-
    write with json.load + json.dump, indent=2). Creates the
    framework/onescript objects if missing. This is the only place pv.py
    writes its config file -- a single validated integer, always confirmed
    by the caller first."""
    config = json.loads(ACTIVE_CONFIG_PATH.read_text(encoding="utf-8"))
    config.setdefault("framework", {}).setdefault("onescript", {})["width"] = width
    ACTIVE_CONFIG_PATH.write_text(
        json.dumps(config, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )


def changes_dir() -> Path:
    return work_root() / "changes"


def versions_dir() -> Path:
    return work_root() / "versions"


def framework_version() -> str:
    """Reads the pv-* framework's own version from pv-init/SKILL.md's YAML
    frontmatter (metadata.version) -- not the project's own version under
    versions/{XXXX}/, which is a separate, project-specific number."""
    text = INIT_SKILL_PATH.read_text(encoding="utf-8")
    match = VERSION_RE.search(text)
    return match.group(1) if match else "?"


def load_test_config(path: Path) -> dict[str, str]:
    """Reads pv-config-test.json, expected next to this script (--testconfig
    takes no argument). Shape mirrors pv-context.json's own node tree so the
    same code finds each value at the same path:

      {"repoRoot": "..", "framework": {"workFolder": "...", "onescript": {...}}}

    - "repoRoot" stays top-level: it has no equivalent in pv-context.json
      (it's test-harness-only -- it tells pv.py where the real repo root is
      when it runs as a copy outside it). Resolved by the caller relative to
      this file's own location, not the process cwd.
    - "workFolder" lives at framework.workFolder, the same path pv-context.json
      uses. framework.onescript.* (pv.py's persisted settings) is read/written
      in place by load_onescript_width()/save_onescript_width(), which point
      at this file via ACTIVE_CONFIG_PATH -- load_test_config() doesn't touch
      it.

    Exits with a clear message (no raw traceback) if the file doesn't
    exist, isn't valid JSON, or is missing repoRoot / framework.workFolder --
    this flag is test-harness-only, so a broken/misconfigured pointer should
    fail loudly rather than silently fall back to the real repo state.
    """
    if not path.is_file():
        sys.exit(f"--testconfig: file not found: {path}")

    try:
        config = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        sys.exit(f"--testconfig: {path} isn't valid JSON: {exc}")

    repo_root = config.get("repoRoot")
    work_folder = (config.get("framework") or {}).get("workFolder")
    missing = []
    if not repo_root:
        missing.append("repoRoot")
    if not work_folder:
        missing.append("framework.workFolder")
    if missing:
        sys.exit(f"--testconfig: {path} is missing required field(s): {', '.join(missing)}")

    return {"repoRoot": repo_root, "workFolder": work_folder}


# =============================================================================
# Actions -- root menu
# =============================================================================


# render_status.py/list_todo.py/filter_status.py (below) draw their own
# "--terminal" output via the sibling module pv-status/scripts/terminal_output.py
# -- a separate color/hr()/title() implementation, not this file's. If a
# screen delegated to one of these three scripts looks wrong, the fix is
# there, not here. See .claude/pv-doc/pv-design-onescript/pv-design-onescript.es.md > "Diagrama de
# Componentes" / "Info delegada".


def show_general_status() -> None:
    run_script(STATUS_SCRIPTS / "render_status.py", "--terminal")

    # render_status.py only prints its three pages -- the id prompt below
    # is pv.py's own, so it can reuse show_id_detail_card() and offer
    # "delete this idea" here too, exactly like "Search by id" does (see
    # "The Detail Card" in the design doc: all paths that reach it must
    # produce the identical screen).
    while True:
        query = read_input("Enter an id for its detail card, or press Enter to go back: ").strip()
        if not query:
            return
        show_id_detail_card(query)


def flag_prefixes_for(codes: list[str], state: str | None = None) -> list[str]:
    """One flag-icon prefix per code, in order, via a single read-flags.py
    subprocess (batch input -- decision 6.13: 1 subprocess, not N). Each
    line is either the rendered prefix ("⭐ ⚙️  ", or "[P] [W]  " under
    NO_COLOR) or empty for a change with no flags / an unresolved code.
    Returns a list the same length as `codes` (padded with "" if the
    script misbehaved), so callers can zip it straight onto their list.

    Pass `state` when every code is known to live in the same state --
    read-flags.py resolves an ambiguous bare code (one that exists in two
    states) to an empty prefix otherwise. For a mixed-state list, call
    once per state (see toggle_flag_on_change()).

    Color is forced to match pv.py's OWN terminal via --color/--no-color:
    read-flags.py's stdout is a pipe here, so its own isatty() check would
    always fall back to ASCII."""
    if not codes:
        return []
    args: list[str] = []
    for code in codes:
        args += ["--xxxx", code]
    if state:
        args += ["--state", state]
    args += ["--terminal", "--color" if supports_color() else "--no-color"]
    out = run_script_capture(STATUS_SCRIPTS / "read-flags.py", *args)
    # splitlines() handles \n and \r\n alike (Windows Python prints \r\n),
    # so each prefix comes back clean with no trailing carriage return.
    lines = out.splitlines() if out else []
    # read-flags.py prints exactly len(codes) lines; tolerate a stray
    # trailing "" from a newline-terminated capture.
    if len(lines) > len(codes) and lines[-1] == "":
        lines = lines[:-1]
    lines += [""] * (len(codes) - len(lines))
    return lines[: len(codes)]


def flag_prefixes_by_state(pairs: list[tuple[str, str]]) -> list[str]:
    """flag_prefixes_for() for a list of (code, state) pairs that may span
    several states. Groups by state so each read-flags.py call can pass
    --state and resolve codes that exist in more than one state (e.g. a
    fast change in both implemented/ and closed/). Returns prefixes in the
    original order of `pairs`."""
    if not pairs:
        return []
    by_state: dict[str, list[int]] = {}
    for i, (_code, state) in enumerate(pairs):
        by_state.setdefault(state, []).append(i)
    result = [""] * len(pairs)
    for state, indices in by_state.items():
        prefixes = flag_prefixes_for([pairs[i][0] for i in indices], state=state)
        for i, prefix in zip(indices, prefixes):
            result[i] = prefix
    return result


def list_implemented_entries() -> list[tuple[str, str]]:
    implemented_dir = changes_dir() / "implemented"
    if not implemented_dir.is_dir():
        return []

    entries = []
    for entry_dir in sorted(p for p in implemented_dir.iterdir() if p.is_dir()):
        name = "(no name)"
        description_path = entry_dir / "description.md"
        if description_path.is_file():
            match = NAME_RE.search(description_path.read_text(encoding="utf-8"))
            if match:
                name = match.group(1).splitlines()[0].strip().strip("` ")
        entries.append((entry_dir.name, name))
    return entries


def close_entry() -> None:
    first_pass = True
    while True:
        entries = list_implemented_entries()
        if not entries:
            if first_pass:
                show_info(
                    [wrap("There's no entry in changes/implemented/ pending closure.")],
                    framed=False,
                )
            return
        first_pass = False

        prefixes = flag_prefixes_for([code for code, _ in entries], state="implemented")
        labels = [
            f"{prefix}{code} — {name}"
            for (code, name), prefix in zip(entries, prefixes)
        ]
        choice = show_selection(
            "Implemented entries, pending closure:",
            labels,
            "Choose an entry to close (number, 'a' to close all, or empty to cancel): ",
            extra_option=("a", "Close all"),
        )
        if choice is None:
            return

        if choice == "a":
            if confirm(
                f"Confirm moving the {len(entries)} listed entries to changes/closed/?"
            ):
                for code, _ in entries:
                    close_change(code)
            else:
                print("Cancelled.")
            return

        code, _ = entries[choice]
        if confirm(f"Confirm moving '{labels[choice]}' to changes/closed/?"):
            close_change(code)
        else:
            print("Cancelled.")
        # Loop back: re-list remaining entries; if none, return to previous menu.


def close_change(code: str) -> None:
    run_script(
        WORKFLOW_SCRIPTS / "move-change.py",
        "--xxxx", code,
        "--from", "implemented",
        "--to", "closed",
    )


# =============================================================================
# Actions -- Configuration submenu
# =============================================================================


def sync_skill_models() -> None:
    run_script(INIT_SCRIPTS / "sync-skill-models.py")


def change_width() -> None:
    """Persists framework.onescript.width. Empty input keeps the current
    value; anything under MIN_WIDTH is rejected without writing. Follows
    the state-mutating pattern (show + confirm before writing) even though
    the "mutation" is a single integer."""
    global WIDTH

    show_info(
        [wrap(f"Current max character width: {WIDTH} (minimum {MIN_WIDTH}).")],
        framed=False,
    )
    answer = read_input(
        f"New width (Enter to keep {WIDTH}): "
    ).strip()
    if not answer:
        print("Unchanged.")
        return

    if not answer.isdigit() or int(answer) < MIN_WIDTH:
        print(f"Width must be a whole number >= {MIN_WIDTH}. Unchanged.")
        return

    new_width = int(answer)
    if new_width == WIDTH:
        print("Unchanged.")
        return

    if not confirm(
        f"Set max character width to {new_width} in {ACTIVE_CONFIG_PATH.name}?"
    ):
        print("Cancelled.")
        return

    save_onescript_width(new_width)
    WIDTH = new_width
    show_info(
        [wrap(f"Saved. Width is now {new_width}.")],
        framed=False,
    )


def show_settings_menu() -> None:
    run_menu(
        "Previo: settings",
        [
            ("Sync skill models per pv-context.json", sync_skill_models),
            ("Change max character width", change_width),
        ],
        "Back",
    )


show_settings_menu.is_submenu = True


# =============================================================================
# Actions -- Versions submenu
# =============================================================================


def list_versions() -> list[str]:
    versions = versions_dir()
    if not versions.is_dir():
        return []
    return sorted(p.name for p in versions.iterdir() if p.is_dir())


def show_version_changelog() -> None:
    versions = list_versions()
    if not versions:
        show_info([wrap("There are no versions yet in this project.")], framed=False)
        return

    index = show_selection(
        "Available versions:", versions, "Choose a version (number, or empty to cancel): "
    )
    if index is None:
        return

    version = versions[index]
    changelog_path = versions_dir() / version / "changelog.md"
    if not changelog_path.is_file():
        show_info([wrap(f"'{version}' has no changelog.md.")], framed=False)
        return

    show_info([changelog_path.read_text(encoding="utf-8")])


def check_closed_temp() -> None:
    temp_dir = changes_dir() / "closed" / "temp"
    if not temp_dir.is_dir():
        show_info([wrap("changes/closed/temp/ doesn't exist. Nothing pending.")], framed=False)
        return

    entries = sorted(p.name for p in temp_dir.iterdir())
    if not entries:
        show_info(
            [wrap("changes/closed/temp/ exists but is empty. Nothing pending.")], framed=False
        )
        return

    lines = [
        wrap(
            "changes/closed/temp/ isn't empty — the versioning process (pv-version) "
            "has either failed or is currently in progress:"
        )
    ]
    lines += [wrap(f"- {entry}", indent="  ") for entry in entries]
    show_info(lines, framed=False)


def show_versions_menu() -> None:
    run_menu(
        "Previo: versions",
        [
            ("List versions and read their changelog", show_version_changelog),
            ("Check changes/closed/temp/ is clear", check_closed_temp),
        ],
        "Back",
    )


show_versions_menu.is_submenu = True


# =============================================================================
# Actions -- Changes info submenu
# =============================================================================


def list_states() -> list[str]:
    changes = changes_dir()
    if not changes.is_dir():
        return []
    return sorted(p.name for p in changes.iterdir() if p.is_dir())


def search_by_id() -> None:
    query = read_input("Search by id (empty to cancel): ").strip()
    if not query:
        return

    show_id_detail_card(query)


def search_by_content() -> None:
    query = read_input("Search by description content (empty to cancel): ").strip()
    if not query:
        return

    run_script(STATUS_SCRIPTS / "filter_status.py", "--search-content", query, "--terminal")


def search_by_state() -> None:
    states = list_states()
    if not states:
        show_info([wrap("There are no changes yet in this project.")], framed=False)
        return

    labels = [colorize(state, STATE_COLORS.get(state, DARK_GRAY)) for state in states]
    index = show_selection(
        "Available states:", labels, "Choose a state (number, or empty to cancel): "
    )
    if index is None:
        return

    run_script(STATUS_SCRIPTS / "filter_status.py", states[index], "--terminal")


# Groups for the "Pick a change:" listing in "Toggle a flag on a change",
# mirroring "General project status"'s IN PROGRESS breakdown (render_status.py:
# render_terminal_page_in_progress()) so the two screens read the same way:
#   🟢 implemented/*                       -> ready to review and close
#   🟠 inProgress/* with plan.md           -> planned, pending implementation
#   🟡 inProgress/* with only description  -> pending technical analysis
# closed/* is intentionally excluded: a closed change is frozen (it's been
# folded into a release), so there's nothing left to re-prioritise or mark
# as in progress -- listing it would only offer a no-op toggle.
# Each tuple is (heading, ordering key among groups).
FLAG_GROUPS = [
    ("🟢 Ready to review and close", "ready"),
    ("🟠 Planned, pending implementation", "planned"),
    ("🟡 Pending technical analysis", "pending"),
]


def _flaggable_group_of(state: str, entry_dir: Path) -> str:
    if state == "implemented":
        return "ready"
    if state == "inProgress":
        return "planned" if (entry_dir / "plan.md").is_file() else "pending"
    # Any other state folder (unusual) -- lump it with "pending" so it's
    # still reachable rather than silently dropped.
    return "pending"


def list_flaggable_changes() -> list[tuple[str, str, str, str]]:
    """Every change/fix under changes/ that can still carry a meaningful
    flag -- i.e. NOT todo/ (ideas can't) and NOT closed/ (frozen), as
    (code, state, name, group) tuples. `group` is one of FLAG_GROUPS'
    keys. Ordered by FLAG_GROUPS, then by code within each group -- the
    same reading order as "General project status". Used by "Toggle a flag
    on a change"."""
    changes = changes_dir()
    if not changes.is_dir():
        return []

    collected: list[tuple[str, str, str, str]] = []
    for state_dir in sorted(p for p in changes.iterdir() if p.is_dir()):
        if state_dir.name in ("todo", "closed"):
            continue
        for entry_dir in sorted(p for p in state_dir.iterdir() if p.is_dir()):
            name = "(no name)"
            description_path = entry_dir / "description.md"
            if description_path.is_file():
                match = NAME_RE.search(description_path.read_text(encoding="utf-8"))
                if match:
                    name = match.group(1).splitlines()[0].strip().strip("` ")
            group = _flaggable_group_of(state_dir.name, entry_dir)
            collected.append((entry_dir.name, state_dir.name, name, group))

    group_order = {key: i for i, (_label, key) in enumerate(FLAG_GROUPS)}
    collected.sort(key=lambda t: (group_order.get(t[3], len(FLAG_GROUPS)), t[0]))
    return collected


def read_change_flags(code: str, state: str) -> list[str]:
    """The change's current flags, read straight from its .metadata.json
    (cheap, no subprocess) so "Toggle a flag" can show [x]/[ ] per flag.
    [] if there's no file / no flags / it's malformed."""
    meta_path = changes_dir() / state / code / ".metadata.json"
    if not meta_path.is_file():
        return []
    try:
        data = json.loads(meta_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []
    raw = data.get("flags") if isinstance(data, dict) else None
    if not isinstance(raw, list):
        return []
    present = {f for f in raw if isinstance(f, str)}
    return [f for f in FLAG_VALUES if f in present]


def _flag_label_with_icon(value: str) -> str:
    table = FLAG_ICONS if supports_color() else FLAG_ICONS_ASCII
    return f"{table[value]} {FLAG_LABELS[value]}"


def _toggle_flags_on(code: str, state: str, name: str) -> None:
    """Inner loop of "Toggle a flag on a change": show this change's flags
    as [x]/[ ], toggle the picked one immediately (no confirm -- a flag is
    trivially reversible, same call flips it back), then re-show the
    refreshed list. Empty input returns to the change picker."""
    while True:
        current = read_change_flags(code, state)
        flag_labels = [
            f"[{'x' if value in current else ' '}] {_flag_label_with_icon(value)}"
            for value in FLAG_VALUES
        ]
        show_info([wrap(f"Flags on {code} — {name}:")], framed=False)
        flag_index = show_selection(
            "", flag_labels, "Choose a flag to toggle (number, or empty to go back): "
        )
        if flag_index is None:
            return

        value = FLAG_VALUES[flag_index]
        # set-metadata.py prints its own one-line confirmation of what it did.
        run_script(
            WORKFLOW_SCRIPTS / "set-metadata.py",
            "--xxxx", code,
            "--state", state,
            "--toggle-flag", value,
        )
        # Loop: re-read and re-show the list with the change reflected.


def _print_flaggable_listing(
    entries: list[tuple[str, str, str, str]], prefixes: list[str]
) -> None:
    """The "Pick a change:" listing, grouped by FLAG_GROUPS the same way
    "General project status"'s IN PROGRESS page groups entries (headings
    🟢/🟠/🟡/📦). Numbering runs continuously across groups so it lines up
    with the Inline Selection printed right below it (same order). Empty
    groups are skipped. Framed by DARK_GRAY '-' rules like a listing, so
    the Inline Selection's own rule sits flush under it."""
    print()
    hr("-")
    print("Pick a change:")
    n = 0
    for label, key in FLAG_GROUPS:
        group_items = [
            (i, e) for i, e in enumerate(entries) if e[3] == key
        ]
        if not group_items:
            continue
        # Group headings tinted GOLD -- a scoped exception to "one color per
        # screen" (same as search_by_state()'s per-state option colors), so
        # the 🟢/🟠/🟡/📦 dividers stand out from the DARK_GRAY entry rows.
        print(wrap(colorize(label, GOLD)))
        for i, (code, _state, name, _group) in group_items:
            n += 1
            print(wrap(f"{n}. {prefixes[i]}{code} — {name}", indent="  "))
    hr("-")


def toggle_flag_on_change() -> None:
    while True:
        entries = list_flaggable_changes()
        if not entries:
            show_info([wrap("There's no change/fix to flag (todo/ ideas can't carry flags).")], framed=False)
            return

        # Batch by state so a code that exists in two states (e.g. a fast
        # change in both implemented/ and closed/) still resolves.
        prefixes = flag_prefixes_by_state([(code, state) for code, state, _, _ in entries])

        _print_flaggable_listing(entries, prefixes)
        # The grouped listing above IS the numbered option list (its
        # numbering matches `entries` order 1:1, since list_flaggable_
        # changes() pre-sorts by group then code). options_shown=True so
        # show_selection() doesn't reprint it flat -- it just reads the
        # choice. show_selection() can't render the group headings itself,
        # hence the separate listing.
        labels = [f"{code} — {name}" for code, _state, name, _group in entries]
        index = show_selection(
            "", labels, "Choose a change (number, or empty to go back): ",
            options_shown=True,
        )
        if index is None:
            return

        code, state, name, _group = entries[index]
        _toggle_flags_on(code, state, name)
        # Loop: re-show the change picker with updated prefixes.


def show_changes_by_flag() -> None:
    labels = [_flag_label_with_icon(value) for value in FLAG_VALUES]
    index = show_selection(
        "", labels, "Choose a flag (number, or empty to cancel): "
    )
    if index is None:
        return

    run_script(
        STATUS_SCRIPTS / "filter_status.py",
        "--flag", FLAG_VALUES[index],
        "--terminal",
    )


def show_changes_info_menu() -> None:
    run_menu(
        "Previo: Changes info",
        [
            ("Search by id", search_by_id),
            ("Search by content", search_by_content),
            ("Search by state", search_by_state),
            ("Toggle a flag on a change", toggle_flag_on_change),
            ("Show changes by flag", show_changes_by_flag),
        ],
        "Back",
    )


show_changes_info_menu.is_submenu = True


# =============================================================================
# Actions -- Ideas (root menu)
# =============================================================================


def show_todo_ideas() -> None:
    run_script(STATUS_SCRIPTS / "list_todo.py", "--terminal")


def list_todo_entries() -> list[tuple[str, str]]:
    todo_dir = changes_dir() / "todo"
    if not todo_dir.is_dir():
        return []

    entries = []
    for entry_dir in sorted(p for p in todo_dir.iterdir() if p.is_dir()):
        idea = "(no '## Idea' section in description.md)"
        description_path = entry_dir / "description.md"
        if description_path.is_file():
            match = IDEA_RE.search(description_path.read_text(encoding="utf-8"))
            if match:
                idea = match.group(1).strip().splitlines()[0].strip()
        entries.append((entry_dir.name, idea))
    return entries


def find_todo_code(query: str) -> str | None:
    """Case-insensitive lookup of `query` as a changes/todo/ folder name --
    same matching rule as filter_status.py's ids_match() for non-numeric
    (todo/) ids. Returns the folder's actual on-disk name (not `query`
    verbatim), or None if there's no such idea."""
    todo_dir = changes_dir() / "todo"
    if not todo_dir.is_dir():
        return None
    for entry_dir in todo_dir.iterdir():
        if entry_dir.is_dir() and entry_dir.name.lower() == query.lower():
            return entry_dir.name
    return None


def delete_idea_by_code(code: str) -> None:
    if confirm(f"Confirm deleting '{code}' from changes/todo/? This can't be undone."):
        run_script(WORKFLOW_SCRIPTS / "delete-todo.py", "--xxxx", code)
    else:
        print("Cancelled.")


def show_id_detail_card(query: str) -> None:
    """Shows one id's detail card (filter_status.py --search-id --terminal,
    Delegated Info) and, only if that id resolves to a changes/todo/ idea,
    an Inline Selection offering to delete it right below -- same card,
    same follow-up, from every path that reaches it: "Search by id" here
    and the id prompt at the end of "General project status"
    (show_general_status()) both call this, so the screen is identical
    regardless of how you got to it (see "The Detail Card" in the design
    doc)."""
    run_script(STATUS_SCRIPTS / "filter_status.py", "--search-id", query, "--terminal")

    # The detail card above is delegated info (filter_status.py's own
    # render) -- pv.py can't see what it printed, only that it ran. To
    # offer "delete this idea" right under it, pv.py separately checks
    # whether `query` resolves to a changes/todo/ folder (cheap, no
    # description.md read) using the same case-insensitive match
    # filter_status.py's ids_match() uses for non-numeric ids.
    code = find_todo_code(query)
    if code is None:
        return

    index = show_selection("", ["Delete this idea"], "Choose an option (or empty to go back): ")
    if index == 0:
        delete_idea_by_code(code)


def delete_idea() -> None:
    entries = list_todo_entries()
    if not entries:
        show_info([wrap("There's no idea in changes/todo/ to delete.")], framed=False)
        return

    labels = [f"{code} — {idea}" for code, idea in entries]
    index = show_selection(
        "Ideas in todo/:", labels, "Choose an idea to delete (number, or empty to cancel): "
    )
    if index is None:
        return

    code, _ = entries[index]
    show_info([wrap(labels[index])], framed=False)
    delete_idea_by_code(code)


def show_ideas_menu() -> None:
    show_todo_ideas()
    choice = show_selection(
        "", ["Delete an idea by code"], "Choose an option (or empty to go back): "
    )
    if choice == 0:
        delete_idea()


# =============================================================================
# Root menu definition
# =============================================================================
#
# To add a new top-level option: write an action function above (or a new
# `show_*_menu()` + mark it `.is_submenu = True` for a submenu), then append
# a (label, action) tuple here. To add a new submenu, follow the pattern of
# show_settings_menu()/show_versions_menu() above.

MENU: list[tuple[str, "callable"]] = [
    ("General project status", show_general_status),
    ("Changes info", show_changes_info_menu),
    ("Ideas in todo/", show_ideas_menu),
    ("Close an implemented entry (move to changes/closed/)", close_entry),
    ("Configuration", show_settings_menu),
    ("Check Previo versions", show_versions_menu),
]


# =============================================================================
# Menu engine
# =============================================================================


def run_menu(
    title: str, items: list[tuple[str, "callable"]], last_label: str
) -> None:
    last_index = len(items) + 1

    while True:
        print()
        print_header(title)
        for i, (label, _) in enumerate(items, start=1):
            print(wrap(f"{i}. {label}", indent="  "))
        print(wrap(f"{last_index}. {last_label}", indent="  "))
        hr("=", GOLD)

        choice = read_input("Choose an option: ").strip()
        if choice == "":
            continue

        try:
            index = int(choice)
        except ValueError:
            print("Invalid option.")
            continue

        if index == last_index:
            return

        try:
            _, action = items[index - 1]
        except IndexError:
            print("Invalid option.")
            continue

        print()
        action()
        if not getattr(action, "is_submenu", False):
            input("\nPress Enter to return to the menu...")


def main() -> None:
    global ROOT, STATUS_SCRIPTS, WORKFLOW_SCRIPTS, INIT_SCRIPTS, INIT_SKILL_PATH, CONTEXT_PATH, TEST_WORK_FOLDER
    global ACTIVE_CONFIG_PATH, WIDTH

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--testconfig",
        action="store_true",
        help="Test-harness-only: reads pv-config-test.json from this script's "
        "own folder ({\"repoRoot\", \"workFolder\"}), used instead of the real "
        ".claude/pv-context.json so pv.py can run against throwaway fixture "
        "data. Not for normal end-user use.",
    )
    args = parser.parse_args()

    if args.testconfig:
        testconfig_path = Path(__file__).resolve().parent / "pv-config-test.json"
        config = load_test_config(testconfig_path)
        # repoRoot is resolved relative to the config file's own location,
        # not the process cwd -- so --testconfig works the same regardless
        # of which directory it's invoked from.
        ROOT = (testconfig_path.parent / config["repoRoot"]).resolve()
        STATUS_SCRIPTS = ROOT / ".claude" / "skills" / "pv-status" / "scripts"
        WORKFLOW_SCRIPTS = ROOT / ".claude" / "skills" / "pv-internal-workflow" / "scripts"
        INIT_SCRIPTS = ROOT / ".claude" / "skills" / "pv-init" / "scripts"
        INIT_SKILL_PATH = ROOT / ".claude" / "skills" / "pv-init" / "SKILL.md"
        CONTEXT_PATH = ROOT / ".claude" / "pv-context.json"
        TEST_WORK_FOLDER = config["workFolder"]
        # pv.py's own settings still come from (and are written back to) the
        # --testconfig file, at the same framework.onescript.* path they'd
        # use in pv-context.json -- so load/save_onescript_width() need no
        # special case for test mode.
        ACTIVE_CONFIG_PATH = testconfig_path

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    enable_windows_ansi()

    if not CONTEXT_PATH.is_file():
        print(wrap("This project doesn't have the pv-* framework initialized."))
        print(wrap("Run /pv-init first from Claude Code."))
        return

    WIDTH = load_onescript_width()

    print(colorize_ring_art(RING_ART))

    run_menu(f"Previo v{framework_version()}: MAIN MENU", MENU, "Exit")


if __name__ == "__main__":
    main()
