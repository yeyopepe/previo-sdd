#!/usr/bin/env python3
"""Validates .claude/pv-context.json against schema.json's required fields.

'framework' carries required: ["docs"] (see schema.json), and 'docs' in turn
requires functional.featuresDocPathDir, tech.architectureDocDir and
tech.styleBibleDocDir -- pv-init always writes and scaffolds all three, and
every other pv-* skill requires them. 'workFolder'/'sourcecodeDir' still have
defaults and are never "required" here. So a project is initialized when the
'framework' section exists AND none of those four required paths is missing.

Doesn't decide anything on its own (doesn't create or complete the file) --
only determines which required fields are missing, so pv-init knows whether
to ask the full questionnaire, treat it as a broken state (delegate to
pv-update), or do nothing. On a first-ever init (file doesn't exist), a
non-empty missingRequired is expected; on an already-initialized project it
means a required field was lost and pv-init routes to its S1Broken branch.

Also reports 'hasLanguage': true if framework.interaction.language exists in
the file (regardless of its content) -- it's the only field whose absence
triggers the unconditional language question in pv-init; the other language
fields (changes/versions/docs.*) are optional refinements on top of that
default and don't gate this flag.

Prints ONLY a JSON on stdout:

  {"exists": true, "hasFramework": true, "missingRequired": [], "complete": true, "hasLanguage": true}
  {"exists": false, "hasFramework": false, "missingRequired": [], "complete": false, "hasLanguage": false}

Usage:
  python check-context.py
"""

import argparse
import json
import sys
from pathlib import Path

# Dotted paths under 'framework' that schema.json marks required. Checked
# against the real file so pv-init can tell "needs first-time setup" (file
# absent) from "a required field was lost" (file present, path missing ->
# S1Broken -> pv-update).
REQUIRED_PATHS = (
    "docs.functional.featuresDocPathDir",
    "docs.tech.architectureDocDir",
    "docs.tech.styleBibleDocDir",
)


def _get_path(obj: dict, dotted: str):
    cur = obj
    for part in dotted.split("."):
        if not isinstance(cur, dict) or part not in cur:
            return None
        cur = cur[part]
    return cur


def repo_root() -> Path:
    # This script lives at {repo}/.claude/skills/pv-init/scripts/
    return Path(__file__).resolve().parents[4]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--context-path",
        help="Path to pv-context.json relative to the repo root. Defaults to "
        ".claude/pv-context.json.",
    )
    args = parser.parse_args()

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    root = repo_root()
    context_path = root / (args.context_path or ".claude/pv-context.json")

    if not context_path.is_file():
        result = {
            "exists": False,
            "hasFramework": False,
            # First-ever init: everything required is "missing" by definition;
            # pv-init's step 3 writes it. Not a broken state.
            "missingRequired": list(REQUIRED_PATHS),
            "complete": False,
            "hasLanguage": False,
        }
        json.dump(result, sys.stdout, ensure_ascii=False)
        print()
        return

    context = json.loads(context_path.read_text(encoding="utf-8"))
    framework = context.get("framework") or {}
    has_framework = bool(context.get("framework"))

    missing = [p for p in REQUIRED_PATHS if _get_path(framework, p) in (None, "")]
    has_language = "language" in (framework.get("interaction") or {})

    result = {
        "exists": True,
        "hasFramework": has_framework,
        "missingRequired": missing,
        # "complete" means the 'framework' section exists AND every required
        # path (schema.json's framework.required -> docs -> the three doc
        # dirs) is present. A non-empty missingRequired on an existing file is
        # a broken state -> pv-init's S1Broken branch, not S1AskComplete.
        "complete": has_framework and not missing,
        "hasLanguage": has_language,
    }
    json.dump(result, sys.stdout, ensure_ascii=False)
    print()


if __name__ == "__main__":
    main()
