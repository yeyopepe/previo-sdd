# Maintaining the mnoteqz7k-framework sandbox

Dev-only tooling for manually testing `mockup-annotations.html` (the real asset the skill
copies into mockups). None of the files described here ship to consuming projects — see
"Never distributed" below.

## Files

- **`mockup-annotations.html`** — the master. The only file `pv-internal-mockups-html` reads
  and copies from. Has no demo body on purpose (just the marker comment, `#mnoteqz7k-styles`,
  an empty `#mnoteqz7k-data`, and `#mnoteqz7k-runtime`).
- **`_build_sandbox.py`** — the builder. Extracts the `#mnoteqz7k-styles`/`#mnoteqz7k-runtime` blocks
  from the master and writes them, verbatim, into a demo body full of interactive widgets and
  complex nested markup. Run it with `python3 _build_sandbox.py` from this directory.
- **`mockup-annotations.sandbox.golden.html`** — a clean copy of the builder's output. Never
  hand-edited, never opened in a browser for testing. Exists only to restore the working copy
  instantly without re-running the builder.
- **`mockup-annotations.sandbox.html`** — the working copy. Open **this** file in a browser to
  test. It accumulates notes, `localStorage` state, and whatever the framework writes back to
  it when you hit Save — that's expected, and exactly why it's a separate file from the golden
  copy.

## Workflow

**Changed something in the framework** (`#mnoteqz7k-styles`/`#mnoteqz7k-runtime` in the master)?
Re-run the builder — it regenerates both the working copy and the golden copy from the
master's current blocks, so they start identical again:

```
cd .claude/skills/pv-internal-mockups-html/assets
python3 _build_sandbox.py
```

**Want to test again from a clean slate** without any framework change (e.g. after a save
round-trip left notes/state in the working copy, or you want to re-run the same manual
checklist)? Don't re-run the builder — just restore the working copy from the golden copy:

```
cd .claude/skills/pv-internal-mockups-html/assets
cp mockup-annotations.sandbox.golden.html mockup-annotations.sandbox.html
```

(On Windows PowerShell: `Copy-Item mockup-annotations.sandbox.golden.html mockup-annotations.sandbox.html -Force`.)

**Adding more demo widgets/structures to test against?** Edit `_build_sandbox.py`'s
`demo_body` string, then re-run the builder (regenerates both copies). Never hand-edit
`mockup-annotations.sandbox.html` or `.golden.html` directly — the next builder run or golden
restore would silently discard the change.

## Never distributed

`install.sh`/`install.ps1` copy each `pv-*` skill folder wholesale, then explicitly strip
`*.sandbox.*` files and `_build_sandbox.py` from the copy before it lands in a consuming
project — this `SANDBOX.md` file itself is not stripped (harmless if it ships, but there's
nothing to run against it without the sandbox files). `pv-update` never copies skills itself;
it always delegates to a freshly downloaded `install.sh`/`install.ps1`, so it's covered by the
same exclusion automatically. If you rename any of the sandbox/builder files, update the
exclusion patterns in both install scripts to match.
