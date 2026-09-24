#!/usr/bin/env python3
"""Installs or updates Previo to a version equal to or newer than the one
currently installed, by detecting the OS and delegating to the matching
platform script at the repo root (install.ps1 on Windows via
`powershell.exe -File`, install.sh via `sh` everywhere else) -- the real
download logic (tarball, pv-*/ sync, pv.py, changelog) is never
reimplemented here, only in those two scripts.

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
here, same self-contained pattern). A hard rejection, with no escape flag,
applies to two distinct cases -- never delegated to install.sh/.ps1 for
GitHub to resolve or reject:

  - <tag> doesn't match the X.Y.Z[suffix] shape parse_version() expects
    (returns None) -- not a version at all (typo, branch name, ...).
  - <tag> parses but is older than the installed version -- a real
    downgrade.

This is deliberate friction against an ACCIDENTAL downgrade inside this
assisted flow (e.g. a mistyped --version), not a real prohibition on
downgrading at all: an intentional downgrade remains reachable by running
install.sh/install.ps1 directly, outside this flow, and that path already
ends at audit-context.py's existing version-check-downgrade mechanism
(confirmed via mark-verified.py --confirm-downgrade) -- unchanged by this
script.

On success, this script does NOT run mark-verified.py itself -- the normal
/pv-update audit flow does that. It only reminds the user to run it next.

Usage:
  python .claude/skills/pv-update/scripts/install-framework.py [--version <tag>]
"""

import argparse
import json
import platform
import re
import subprocess
import sys
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


def platform_script(root: Path) -> tuple[list[str], Path]:
    system = platform.system()
    if system == "Windows":
        script = root / "install.ps1"
        return (["powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass",
                  "-File", str(script)], script)
    script = root / "install.sh"
    return (["sh", str(script)], script)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--version", metavar="TAG", default=None,
                         help="Tag to install (must be >= the installed version). "
                              "Omit to install the latest official release.")
    args = parser.parse_args()

    root = repo_root()

    official_tag, prerelease_tag = report_releases()

    pv_init_md = root / ".claude/skills/pv-init/SKILL.md"
    installed_raw = read_skill_version(pv_init_md) if pv_init_md.is_file() else None
    installed_parsed = parse_version(installed_raw) if installed_raw else None

    requested_prerelease = False

    if args.version:
        requested_parsed = parse_version(args.version)
        if requested_parsed is None:
            print(f"Error: '{args.version}' doesn't have the X.Y.Z[suffix] shape "
                  f"of a framework version -- can't verify it's equal to or newer "
                  f"than the installed version. Not installing anything.",
                  file=sys.stderr)
            sys.exit(1)

        if installed_parsed is not None and requested_parsed[:3] < installed_parsed[:3]:
            print(f"Error: '{args.version}' is OLDER than the installed version "
                  f"'{installed_raw}'. 'pv-update install' never downgrades -- "
                  f"installing an older version by hand requires running "
                  f"install.sh/install.ps1 directly, outside this assisted flow. "
                  f"Not installing anything.", file=sys.stderr)
            sys.exit(1)

        requested_prerelease = args.version == prerelease_tag
        if requested_prerelease:
            print(f"'{args.version}' is a pre-release, requested explicitly -- "
                  f"proceeding, but it isn't recommended for normal use due to "
                  f"its stability.")

    target_desc = args.version or "the latest official release"
    print(f"Installing {target_desc}...")

    argv, script_path = platform_script(root)
    if args.version:
        argv = argv + [args.version]
    if not script_path.is_file():
        print(f"Error: platform install script not found at '{script_path}'.",
              file=sys.stderr)
        sys.exit(1)

    completed = subprocess.run(argv, cwd=root)
    if completed.returncode != 0:
        print(f"Error: '{script_path.name}' exited with code {completed.returncode}.",
              file=sys.stderr)
        sys.exit(completed.returncode)

    print("")
    print("Installation finished. Run /pv-update (audit mode) next to verify "
          "and repair the configuration.")


if __name__ == "__main__":
    main()
