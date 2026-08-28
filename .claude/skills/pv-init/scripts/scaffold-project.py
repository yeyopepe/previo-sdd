#!/usr/bin/env python3
"""Creates the pv-* framework's base folder structure and doc placeholders.

Invoked by pv-init right after writing .claude/pv-context.json, so it reads
the final resolved paths (workFolder, docs.tech.architectureDocDir,
docs.tech.styleBibleDocDir, docs.functional.featuresDocPathDir) directly
from that file instead of receiving them as arguments.

What it creates, only if nothing already exists at that path (never
overwrites or touches existing content):
- workFolder's fixed subfolders: changes/{inProgress,implemented,todo,closed},
  versions/, stuff/ -- empty, with a .gitkeep so git tracks them.
- docs.tech.architectureDocDir / styleBibleDocDir / docs.functional.featuresDocPathDir
  (each if configured): all three follow the same pv-internal-doc-files
  convention -- one {NNN}-{slug}.md file per topic plus a generated
  INDEX.md, never hand-written. architectureDocDir/styleBibleDocDir get a
  single "001-overview.md" placeholder (filled in later by pv-init, or
  pv-do over time); featuresDocPathDir gets no placeholder file, just the
  empty folder with its INDEX.md regenerated (pv-internal-doc-files's
  rebuild-index.py already handles the zero-file case).
  architectureDocDir additionally gets a "00-namespace.md" seed (the single
  per-project namespace tree) -- created only if absent, never overwritten,
  even when the folder itself already exists (status "namespace_seeded" in
  that case). styleBibleDocDir gets no namespace file: its concepts hang off
  the `ui.*` branch of architectureDocDir's tree.

Always overwrites (it's a generated file, not user content):
- assets/pv.py -> {repo root}/pv.py

Before creating anything, verifies every resolved path stays inside the
repo root -- pv-context.json is local configuration that could in principle
be hand-edited with a path like "../.." for workFolder or a docs.* dir.

This script resolves the docs.* dirs itself (it's owned by pv-init, the
schema's owner, same as resolve-path.py) rather than shelling out to
resolve-path.py: it runs before the folders exist (resolve-path.py would
exit 4), it needs the extra resolve_inside_repo containment check, and it's
fully deterministic. The docs.* -> workFolder resolution rule here must stay
in sync with pv-init/scripts/resolve-path.py and
pv-update/scripts/audit-context.py's check_docs_dir.

Prints ONLY a JSON summary on stdout, e.g.:

  {
    "workFolderSubfolders": {"created": ["previo-sdd/changes/inProgress", ...], "skipped": []},
    "docs": {
      "architecture": {"path": "previo-sdd/docs/architecture", "status": "created"},
      "style": {"path": "previo-sdd/docs/style", "status": "skipped"},
      "features": {"path": null, "status": "not_configured"}
    },
    "pvPy": {"path": "pv.py", "status": "overwritten"}
  }

'status' is one of "created", "skipped" (something already existed at that
path -- folder or, for docs, even a legacy single file -- left untouched),
"namespace_seeded" (architecture folder already existed but was missing
00-namespace.md, now added) or "not_configured" (the field isn't set in
pv-context.json).

Usage:
  python .claude/skills/pv-init/scripts/scaffold-project.py
"""

import json
import shutil
import subprocess
import sys
from pathlib import Path

WORKFOLDER_SUBFOLDERS = (
    "changes/inProgress",
    "changes/implemented",
    "changes/todo",
    "changes/closed",
    "versions",
    "stuff",
)

OVERVIEW_TEMPLATE = """# 001 — {title}

**Area**: {title}

<Placeholder, generated empty by scaffold-project.py. Filled in afterwards \
with what's known about the project (type, stack, conventions) -- by \
pv-init on first setup, or expanded by pv-do over time.>
"""

# Seed for {architectureDocDir}/00-namespace.md -- the single per-project
# namespace tree (see pv-internal-doc-technical's "## Namespace"). The `00-`
# prefix is reserved: rebuild-index.py / next-feature-number.py skip it, so it
# never lands in INDEX.md or the {NNN} numbering. Only architectureDocDir gets
# one -- styleBibleDocDir concepts hang off the `ui.*` branch of this same tree.
# The literal headings `## Notation` and `## Tree` are normative: pv-update
# checks for them and pv-do locates them to insert nodes.
NAMESPACE_SEED = """# 00 — Namespace

Single canonical name tree for this project. Every concept and every assertion \
(architecture and style alike) has exactly one path here. Style concepts live \
on the `ui.*` branch -- there is no separate namespace file for the style bible.

## Notation

Compact notation for structured data:

```
field: type                  required field
field?: type                 optional field
field: type = value          default value
field: type ∈ {a, b, c}      enum / allowed set
field: type [min..max]       range
```

Invariants -- executable vs declarative:

- `assert <expr>` when there is a program point where the condition can be \
checked with the values at hand.
- declarative `inv: …` / `pre:` / `post:` (propositional logic, `∧ ∨ ¬ → ⟹ \
∀`) when it quantifies over an abstract set, talks about an FSM state, \
or a non-observable global property.
- If both forms fit, the `assert` governs and the declarative one is a \
restatement.

Boundary between a leaf's two forms:

- `path = <scalar>` -- a simple value (number, enum, boolean).
- `path:` then a notation block -- an assertion with logical structure (a \
contract, a logic expression).

## Tree

Segment order: aggregate to part, module to detail. \
`<area>.<aggregate>.<entity>.<field-or-assertion>`.

- `auth.token.session.exp` -- OK (area auth -> aggregate token -> entity \
session -> field exp)
- `auth.session.token.exp` -- wrong (inverts aggregate and entity)

Domain terms with no standard English translation: if the concept has a code \
symbol, the path uses the symbol name; if it has none, the slug may stay in the \
project's language for that one node (e.g. `billing.recargo-equivalencia`), \
noted here as an explicit exception with a one-line approximate-English gloss.

Commented example (delete once real nodes exist):

```
# auth.token.session                       concept.   anchor: src/auth/token.ts#SessionToken
# auth.token.session.ttl.value = 3600      assertion (scalar)
# auth.token.session.refresh.rule:         assertion (non-scalar -> notation block)
#     pre:  state ∈ {AUTHENTICATED, EXPIRED} ∧ now - token.exp < 7d
#     post: token'.exp = now + auth.token.session.ttl.value
# auth.decision.circuit-breaker-over-retry decision.  no code anchor
#     [motivación] downstream SLA is 99.5%; retry storms already caused 2 incidents.
# ui.grid.columns = 16                     style assertion (same tree)
```

A `path.decision.<slug>` node records its rationale as a `[motivación]` line \
(or a comparison table), never as bare prose alongside the `decision.` marker.

<Empty. pv-do populates this over time.>
"""


def repo_root() -> Path:
    # This script lives at {repo}/.claude/skills/pv-init/scripts/
    return Path(__file__).resolve().parents[4]


def resolve_inside_repo(root: Path, relative: str) -> Path:
    resolved = (root / relative.lstrip("/")).resolve()
    if resolved != root and root not in resolved.parents:
        raise ValueError(
            f"Path '{relative}' resolves outside the repo root: {resolved}"
        )
    return resolved


def ensure_workfolder_subfolders(root: Path, work_folder: str) -> dict:
    created, skipped = [], []
    for sub in WORKFOLDER_SUBFOLDERS:
        folder = resolve_inside_repo(root, f"{work_folder.rstrip('/')}/{sub}")
        rel = folder.relative_to(root).as_posix()
        if folder.exists():
            skipped.append(rel)
            continue
        folder.mkdir(parents=True, exist_ok=True)
        (folder / ".gitkeep").touch()
        created.append(rel)
    return {"created": created, "skipped": skipped}


def rebuild_index(root: Path, folder: Path) -> None:
    script = root / ".claude/skills/pv-internal-doc-files/scripts/rebuild-index.py"
    subprocess.run(
        [sys.executable, str(script), "--folder", str(folder)],
        cwd=root,
        check=True,
        capture_output=True,
    )


def ensure_overview_doc(
    root: Path, work_folder: str, relative_dir: str | None, title: str,
    seed_namespace: bool = False,
) -> dict:
    if not relative_dir:
        return {"path": None, "status": "not_configured"}
    folder = resolve_inside_repo(root, f"{work_folder.rstrip('/')}/{relative_dir}")
    rel = folder.relative_to(root).as_posix()
    if folder.exists():
        # Folder already there: still seed 00-namespace.md if it's the
        # architecture dir and the file is missing (idempotent -- never
        # overwrite an existing one).
        if seed_namespace:
            ns_file = folder / "00-namespace.md"
            if not ns_file.exists():
                ns_file.write_text(NAMESPACE_SEED, encoding="utf-8")
                return {"path": rel, "status": "namespace_seeded"}
        return {"path": rel, "status": "skipped"}
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "001-overview.md").write_text(OVERVIEW_TEMPLATE.format(title=title), encoding="utf-8")
    if seed_namespace:
        (folder / "00-namespace.md").write_text(NAMESPACE_SEED, encoding="utf-8")
    rebuild_index(root, folder)
    return {"path": rel, "status": "created"}


def ensure_features_doc(root: Path, work_folder: str, relative_dir: str | None) -> dict:
    if not relative_dir:
        return {"path": None, "status": "not_configured"}
    folder = resolve_inside_repo(root, f"{work_folder.rstrip('/')}/{relative_dir}")
    rel = folder.relative_to(root).as_posix()
    if folder.exists():
        return {"path": rel, "status": "skipped"}
    folder.mkdir(parents=True, exist_ok=True)
    rebuild_index(root, folder)
    return {"path": rel, "status": "created"}


def copy_pv_py(root: Path) -> dict:
    src = root / ".claude/skills/pv-init/assets/pv.py"
    dst = resolve_inside_repo(root, "pv.py")
    shutil.copyfile(src, dst)
    return {"path": "pv.py", "status": "overwritten"}


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    root = repo_root()
    context_path = root / ".claude/pv-context.json"
    context = json.loads(context_path.read_text(encoding="utf-8"))
    framework = context.get("framework") or {}

    work_folder = framework.get("workFolder", "/previo-sdd")
    docs = framework.get("docs") or {}
    tech = docs.get("tech") or {}
    functional = docs.get("functional") or {}

    result = {
        "workFolderSubfolders": ensure_workfolder_subfolders(root, work_folder),
        "docs": {
            "architecture": ensure_overview_doc(
                root, work_folder, tech.get("architectureDocDir"), "Architecture",
                seed_namespace=True,
            ),
            "style": ensure_overview_doc(
                root, work_folder, tech.get("styleBibleDocDir"), "Style bible"
            ),
            "features": ensure_features_doc(
                root, work_folder, functional.get("featuresDocPathDir")
            ),
        },
        "pvPy": copy_pv_py(root),
    }

    json.dump(result, sys.stdout, ensure_ascii=False, indent=2)
    print()


if __name__ == "__main__":
    main()
