"""Regenerates INDEX.md from all the feature files in the folder.

Never edit INDEX.md by hand -- this script is the only source of truth for
its content, so it never drifts out of sync with the real files. Usage:

    python rebuild-index.py --folder docs/features
    python rebuild-index.py --folder docs/architecture --title Architecture

The INDEX.md H1 defaults to the folder name (title-cased, dashes/underscores
to spaces): docs/architecture -> "# Architecture", docs/style -> "# Style",
docs/features -> "# Features". Pass --title to override.
"""
import argparse
import re
from pathlib import Path


def parse_feature(path):
    title = None
    area = "No area"
    for line in path.read_text(encoding="utf-8").splitlines():
        if title is None:
            m = re.match(r"#\s+(.+)", line)
            if m:
                title = m.group(1).strip()
                continue
        m = re.match(r"\*\*Area\*\*:\s*(.+)", line)
        if m:
            area = m.group(1).strip()
            break
    return title or path.stem, area


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--folder", required=True)
    parser.add_argument(
        "--title", default=None,
        help="INDEX.md H1; defaults to the folder name, title-cased",
    )
    args = parser.parse_args()

    folder = Path(args.folder)
    folder.mkdir(parents=True, exist_ok=True)
    index_title = args.title or folder.name.replace("-", " ").replace("_", " ").title()

    by_area = {}
    for path in sorted(folder.glob("*.md")):
        if path.name == "INDEX.md" or path.name.startswith("00-"):
            continue
        title, area = parse_feature(path)
        by_area.setdefault(area, []).append((title, path.name))

    lines = [f"# {index_title}", ""]
    for area in sorted(by_area, key=str.casefold):
        lines.append(f"## {area}")
        lines.append("")
        for title, filename in sorted(by_area[area], key=lambda t: t[0].casefold()):
            lines.append(f"- [{title}]({filename})")
        lines.append("")

    (folder / "INDEX.md").write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    total = sum(len(v) for v in by_area.values())
    print(f"INDEX.md regenerated: {total} features across {len(by_area)} areas.")


if __name__ == "__main__":
    main()
