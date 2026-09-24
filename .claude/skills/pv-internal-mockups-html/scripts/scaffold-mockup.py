#!/usr/bin/env python3
"""Copies assets/mockup-annotations.html verbatim to a new design_<description>.html,
renaming the title and dropping the master's own dev-only comment. The two framework
blocks (`#mnoteqz7k-styles`, `#mnoteqz7k-runtime`) and the empty `#mnoteqz7k-data` land
byte-identical -- the caller (the model acting as pv-internal-mockups-html) never
retypes them, it only fills in the mockup's own markup between the placeholder comment
this script leaves and the `#mnoteqz7k-data` script tag.

Usage:
    python scaffold-mockup.py --dest <folder> --description <element-description>

Exits non-zero (without writing anything) if the destination file already exists --
this script is only for `action: create`'s first write; `action: edit` never calls it.
"""
import argparse
import pathlib
import re
import sys

ASSET_PATH = pathlib.Path(__file__).resolve().parent.parent / "assets" / "mockup-annotations.html"

DEV_COMMENT_RE = re.compile(
    r"<!--\s*\n\s*This is the real asset\..*?-->\n?",
    re.S,
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dest", required=True, help="Destination folder (usually mockups/)")
    parser.add_argument("--description", required=True, help="Element description, e.g. 'progress-bar'")
    args = parser.parse_args()

    dest_dir = pathlib.Path(args.dest)
    dest_dir.mkdir(parents=True, exist_ok=True)
    target = dest_dir / f"design_{args.description}.html"

    if target.exists():
        print(f"ERROR: {target} already exists -- this script is only for a first create, not an edit.", file=sys.stderr)
        return 1

    if not ASSET_PATH.exists():
        print(f"ERROR: asset not found at {ASSET_PATH}", file=sys.stderr)
        return 1

    html = ASSET_PATH.read_text(encoding="utf-8")

    html = html.replace(
        "<title>mnoteqz7k-framework</title>",
        f"<title>Mockup — {args.description}</title>",
        1,
    )

    html, n = DEV_COMMENT_RE.subn(
        "<!-- Fill in the mockup's own markup below this comment, then leave #mnoteqz7k-data as-is. -->\n",
        html,
        count=1,
    )
    if n == 0:
        print("ERROR: master asset's dev-only comment not found -- asset may have changed shape; update this script's DEV_COMMENT_RE.", file=sys.stderr)
        return 1

    target.write_text(html, encoding="utf-8")
    print(str(target))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
