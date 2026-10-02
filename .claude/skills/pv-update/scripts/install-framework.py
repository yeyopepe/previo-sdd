#!/usr/bin/env python3
"""Installs or updates Previo to a version equal to or newer than the one
currently installed, by detecting the OS and delegating to the matching
platform script (install.ps1 on Windows via `powershell.exe -File`,
install.sh via `sh` everywhere else) -- the real download logic (tarball,
pv-*/ sync, pv.py, changelog) is never reimplemented here, only in those
two scripts.

Those scripts only live at the previo-sdd repo root -- a project that
installed the framework via the documented `irm|iex` / `curl|sh` one-liner
never has them locally, since that one-liner never copies itself into the
target project. So this script NEVER trusts a local install.ps1/install.sh,
even if one happens to sit at the repo root (leftover from a manual copy,
a previous bug, or previo-sdd's own repo): any local copy found there is
deleted first, then a fresh copy is always fetched from previo-sdd's own
`main` branch on GitHub (the same raw URL the install one-liners
themselves point at) into a temp file, run from there, and deleted again
in a `finally` -- it's never kept: not on success, not on failure, not on
an unexpected exception, and never left at the repo root either before or
after running it.

REPO = "yeyopepe/previo-sdd" is this script's own copy of the constant
already hardcoded, by duplication, as install.sh/.ps1's REPO= -- same
self-contained-script pattern as check-framework-status.py's
EXPECTED_SKILL_COUNT. Never a shared source of truth.

Before deciding anything, queries GitHub Releases to always inform the user
of the latest OFFICIAL release (GET /repos/{REPO}/releases/latest -- GitHub
excludes pre-releases from this endpoint by design) and the most recently
PUBLISHED release of any kind (GET /repos/{REPO}/releases?per_page=1 --
GitHub always orders releases newest-first regardless of type, so this
endpoint never filters by prerelease). If that second result's tag_name
differs from the first's and its prerelease field is true, a newer
pre-release exists and is reported -- neutrally, never recommended, never
installed by default.

Version comparison against the installed version reuses the same
read_skill_version()/parse_version() logic as audit-context.py (duplicated
here, same self-contained pattern). The target version is always resolved
to a single concrete tag FIRST -- <tag> if --version was given, otherwise
the latest official release -- and the same hard rejection, with no escape
flag, applies to that one resolved tag regardless of which path it came
from (never delegated to install.sh/.ps1 for GitHub to resolve or reject):

  - <tag> doesn't match the X.Y.Z[suffix] shape parse_version() expects
    (returns None) -- not a version at all (typo, branch name, ...).
  - <tag> parses but is older than the installed version -- a real
    downgrade. This check used to run only when --version was passed
    explicitly, which meant an unattended "install latest" could silently
    downgrade an installed pre-release (0.9.8b6 -> 0.9.7 official, since
    0.9.7 sorts older by (major, minor, patch) alone) with no rejection and
    no confirmation. Now it always runs against whatever tag was resolved.

This is deliberate friction against an ACCIDENTAL downgrade inside this
assisted flow (e.g. a mistyped --version, or a "latest" that resolves
older than an installed pre-release), not a real prohibition on
downgrading at all: an intentional downgrade remains reachable by running
install.sh/install.ps1 directly, outside this flow, and that path already
ends at audit-context.py's existing version-check-downgrade mechanism
(confirmed via mark-verified.py --confirm-downgrade) -- unchanged by this
script.

**Two-step confirmation, enforced by --yes.** Without --yes, the script
resolves the target tag, runs every safety check against it, prints it,
and STOPS -- nothing is installed. The caller (the /pv-update install
skill, or pv.py's "Install new Previo version") is required to show that
exact resolved tag to the user and get their explicit confirmation before
re-running with --version <the same resolved tag> --yes. This script never
decides "latest" and installs it in one unattended step -- the version
actually being installed must always be named out loud and confirmed,
never assumed.

On success, this script does NOT run mark-verified.py itself -- the normal
/pv-update audit flow does that. It only reminds the user to run it next.

--list-only queries and prints the same release info as a normal run
(report_releases()) but exits before installing anything, additionally
printing two machine-parseable "KEY=value" lines (OFFICIAL_TAG=.../
PRERELEASE_TAG=..., empty value if unknown/absent) after the human-readable
lines. Used by pv.py's "Install new Previo version" menu option (capturing
this script's stdout via run_script_capture()) to learn which tags exist
before asking the user which one to install, without duplicating the
GitHub Releases query logic.

Usage:
  python .claude/skills/pv-update/scripts/install-framework.py [--version <tag>]
      Resolves the target tag and runs every safety check, but does NOT
      install -- prints the resolved tag for the caller to confirm with
      the user.
  python .claude/skills/pv-update/scripts/install-framework.py --version <tag> --yes
      Actually installs <tag>, after the caller has confirmed it with the
      user. <tag> must be the exact tag a prior no-flag run resolved.
  python .claude/skills/pv-update/scripts/install-framework.py --list-only
"""

import argparse
import json
import os
import platform
import re
import stat
import subprocess
import sys
import tempfile
import urllib.error
import urllib.request
from pathlib import Path

REPO = "yeyopepe/previo-sdd"

VERSION_RE = re.compile(r"^(\d+)\.(\d+)\.(\d+)([a-zA-Z][\w.-]*)?$")


def repo_root() -> Path:
    # This script lives at {repo}/.claude/skills/pv-update/scripts/
    return Path(__file__).resolve().parents[4]


def parse_version(version: str) -> tuple[int, int, int, str] | None:
    match = VERSION_RE.match(version.strip())
    if not match:
        return None
    major, minor, patch, suffix = match.groups()
    return int(major), int(minor), int(patch), suffix or ""


def read_skill_version(path: Path) -> str | None:
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


def fetch_json(url: str) -> dict | None:
    request = urllib.request.Request(url, headers={"Accept": "application/vnd.github+json"})
    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            return json.loads(response.read().decode("utf-8"))
    except (urllib.error.URLError, urllib.error.HTTPError, json.JSONDecodeError, TimeoutError):
        return None


def report_releases() -> tuple[str | None, str | None]:
    """Prints the latest official release and, if newer, the latest
    pre-release. Returns (latest_official_tag, newer_prerelease_tag)."""
    latest_official = fetch_json(f"https://api.github.com/repos/{REPO}/releases/latest")
    most_recent_any = fetch_json(f"https://api.github.com/repos/{REPO}/releases?per_page=1")

    official_tag = latest_official.get("tag_name") if latest_official else None
    if official_tag:
        print(f"Latest official release: {official_tag}")
    else:
        print("Couldn't determine the latest official release from GitHub.")

    prerelease_tag = None
    if most_recent_any and isinstance(most_recent_any, list) and most_recent_any:
        candidate = most_recent_any[0]
        candidate_tag = candidate.get("tag_name")
        if candidate_tag and candidate_tag != official_tag and candidate.get("prerelease") is True:
            prerelease_tag = candidate_tag
            print(f"A pre-release '{prerelease_tag}' is available, but it isn't "
                  f"recommended for normal use due to its stability.")

    return official_tag, prerelease_tag


def platform_script_name() -> str:
    return "install.ps1" if platform.system() == "Windows" else "install.sh"


def platform_script_argv(script: Path) -> list[str]:
    if platform.system() == "Windows":
        return ["powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass",
                 "-File", str(script)]
    return ["sh", str(script)]


def download_platform_script(name: str) -> Path | None:
    """Fetches install.ps1/install.sh fresh from previo-sdd's main branch
    into a temp file (never the repo root) -- always, regardless of
    whether a local copy exists, since a local copy can never be trusted
    (see module docstring). Caller is responsible for deleting the
    returned path."""
    url = f"https://raw.githubusercontent.com/{REPO}/main/{name}"
    request = urllib.request.Request(url)
    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            content = response.read()
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError):
        return None

    fd, tmp_path = tempfile.mkstemp(prefix="previo-", suffix=f"-{name}")
    tmp = Path(tmp_path)
    with os.fdopen(fd, "wb") as f:
        f.write(content)
    if name == "install.sh":
        tmp.chmod(tmp.stat().st_mode | stat.S_IEXEC)
    return tmp


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--version", metavar="TAG", default=None,
                         help="Tag to install (must be >= the installed version). "
                              "Omit to resolve the latest official release.")
    parser.add_argument("--list-only", action="store_true",
                         help="Query and print the available release info, then "
                              "exit without installing anything.")
    parser.add_argument("--yes", action="store_true",
                         help="Actually perform the install. Without it, the "
                              "script only resolves and prints the exact target "
                              "version (and runs every safety check against it) "
                              "then stops -- the caller must show that resolved "
                              "version to the user, get their explicit "
                              "confirmation, and only then re-run with --yes.")
    args = parser.parse_args()

    root = repo_root()

    official_tag, prerelease_tag = report_releases()

    if args.list_only:
        print(f"OFFICIAL_TAG={official_tag or ''}")
        print(f"PRERELEASE_TAG={prerelease_tag or ''}")
        return

    pv_init_md = root / ".claude/skills/pv-init/SKILL.md"
    installed_raw = read_skill_version(pv_init_md) if pv_init_md.is_file() else None
    installed_parsed = parse_version(installed_raw) if installed_raw else None

    # Resolve a single target tag up front, whatever its origin (explicit
    # --version, or the latest official release), and run the SAME
    # format/downgrade checks against it either way. Only comparing when
    # --version was passed (the previous behavior) let an unattended
    # "install latest" silently downgrade an installed pre-release (e.g.
    # 0.9.8b6 -> 0.9.7, since 0.9.7 sorts older by (major, minor, patch))
    # -- exactly the accidental-downgrade case this check exists to catch.
    if args.version:
        target_tag = args.version
    elif official_tag:
        target_tag = official_tag
    else:
        print("Error: couldn't determine the latest official release from "
              "GitHub, and no --version was given. Not installing anything.",
              file=sys.stderr)
        sys.exit(1)

    target_parsed = parse_version(target_tag)
    if target_parsed is None:
        print(f"Error: '{target_tag}' doesn't have the X.Y.Z[suffix] shape "
              f"of a framework version -- can't verify it's equal to or newer "
              f"than the installed version. Not installing anything.",
              file=sys.stderr)
        sys.exit(1)

    if installed_parsed is not None and target_parsed[:3] < installed_parsed[:3]:
        print(f"Error: '{target_tag}' is OLDER than the installed version "
              f"'{installed_raw}'. 'pv-update install' never downgrades -- "
              f"installing an older version by hand requires running "
              f"install.sh/install.ps1 directly, outside this assisted flow. "
              f"Not installing anything.", file=sys.stderr)
        sys.exit(1)

    if target_tag == prerelease_tag:
        print(f"'{target_tag}' is a pre-release -- proceeding, but it isn't "
              f"recommended for normal use due to its stability.")

    print(f"Resolved target version: {target_tag}"
          + (f" (currently installed: {installed_raw})" if installed_raw else ""))

    if not args.yes:
        print("")
        print(f"Not installing -- re-run with --version {target_tag} --yes "
              f"once the user has explicitly confirmed THIS EXACT VERSION.")
        return

    script_name = platform_script_name()
    local_script = root / script_name
    if local_script.is_file():
        print(f"Found a local '{script_name}' at the repo root -- deleting it "
              f"and fetching a fresh copy instead (a local copy is never "
              f"trusted, see module docstring).")
        local_script.unlink()

    print(f"Fetching '{script_name}' from {REPO}'s main branch...")
    downloaded_script = download_platform_script(script_name)
    if downloaded_script is None:
        print(f"Error: couldn't download '{script_name}' from GitHub. "
              f"Not installing anything.", file=sys.stderr)
        sys.exit(1)

    print(f"Installing {target_tag}...")
    argv = platform_script_argv(downloaded_script) + [target_tag]

    try:
        completed = subprocess.run(argv, cwd=root)
    finally:
        downloaded_script.unlink(missing_ok=True)

    if completed.returncode != 0:
        print(f"Error: '{script_name}' exited with code {completed.returncode}.",
              file=sys.stderr)
        sys.exit(completed.returncode)

    print("")
    print("Installation finished. Run /pv-update (audit mode) next to verify "
          "and repair the configuration.")


if __name__ == "__main__":
    main()
