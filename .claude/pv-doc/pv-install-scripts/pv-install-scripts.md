# `install.sh` / `install.ps1`

Two standalone entry points (POSIX shell / PowerShell) that install or update
Previo in a consuming project. Distributed as raw files at the repo root
(`install.sh`, `install.ps1`), fetched by URL — never invoked from inside
Previo itself. `scripts/install-framework.py` (used by `pv-update`'s install
mode) never trusts a copy that may already exist at the target repo's root:
it deletes any `install.ps1`/`install.sh` found there and re-downloads a
fresh one from previo-sdd's `main` branch before running it.

Both scripts implement the same sequence; the sections below describe it
once, flagging shell-specific mechanics where they differ.

## 1. Version resolution

```
input: $1 / $env:PREVIO_VERSION (optional, a tag, e.g. "v1.2.3")
  ├─ empty → GET /repos/{REPO}/releases/latest → tag_name
  └─ given → GET /repos/{REPO}/releases/tags/{tag}
       ├─ 200 → tag_name (published release)
       └─ 404 → GET /repos/{REPO}/git/refs/tags/{tag}
            ├─ 200 → tag used as-is, INSTALLED_FROM_RAW_TAG=1
            └─ 404 → abort: "Version '{tag}' doesn't exist in Previo's releases."
```

`releases/tags/{tag}` only resolves **published releases**: a tag that
exists in the repo but has no release attached also 404s there, identically
to a tag that doesn't exist at all. The `git/refs/tags/{tag}` fallback
disambiguates the two cases — if the ref exists, the tag is real and its
source tarball (`archive/refs/tags/{tag}.tar.gz`) is downloadable regardless
of whether a release was ever published for it. This path is only reachable
for an explicitly requested version; resolving "latest" never falls back to
a raw tag.

`INSTALLED_FROM_RAW_TAG` (`install.sh`) / `$InstalledFromRawTag`
(`install.ps1`) drives a warning block printed near the end of the run (see
"Final messages" below).

## 2. Download

```
TARBALL = https://github.com/{REPO}/archive/refs/tags/{TAG}.tar.gz
```

This URL 302-redirects to `codeload.github.com`, which serves the tarball
**without ever sending a `Content-Length` header** — confirmed against both
a published release and a raw tag. This is permanent behavior of that
endpoint, not an edge case, and it shapes both download implementations
below: neither can compute a real percentage, so both fake one against an
assumed 3 MB total (`ASSUMED_TOTAL_BYTES` / `$AssumedTotalBytes`, chosen as
this repo's typical tarball size), clamped to 99% while still downloading —
in case the real file is bigger — and forced to a full 100% bar only once
the download has actually finished, regardless of how many bytes that took.

**`install.sh`**: runs `curl -fL "$TARBALL" -o "$TAR_PATH"` in the
background (`&`), then polls the growing output file's size with `wc -c` in
a `while kill -0 "$CURL_PID"` loop (every 0.2s) to drive `draw_progress_bar`.
`curl --progress-bar` was tried first and discarded: without
`Content-Length` it falls back to a bare, unparseable spinner
(`#=#=#`, `##O#-#`, ...) with no percentage, and curl exposes no flag to
customize that output — hence the manual poll-and-redraw loop instead. The
bar is repainted on a single line with `\r`; the fill segment is wrapped in
`\033[34m`/`\033[0m` (blue), the rest of the line in default text color.

**`install.ps1`**: downloads via `System.Net.Http.HttpClient` streamed to
disk (`GetAsync` with `ResponseHeadersRead`, then `Read`/`Write` in an
81920-byte-buffer loop), calling `Write-ProgressBar` after every chunk.
`Invoke-WebRequest` was discarded even though it draws a native bar: it
enables `WebClient`'s internal progress reporting, which can slow a large
download 10-100x. `Write-Progress` was also discarded — it occupies a
separate 2-3 line region inconsistent with `install.sh`'s single-line bar,
can't draw a bar at all without `Content-Length` (only a generic spinner),
and renders inconsistently across hosts (Windows Terminal vs. classic
console vs. VS Code's integrated terminal). The bar is repainted in place
with `` `r ``; only the fill segment (`=`/`>`) is drawn with
`-ForegroundColor Blue`, the rest of the line in default text color
(`%`, download speed in `MB/s`, computed from a `Stopwatch` over the total
bytes read so far).

Both bars use a 40-character-wide ASCII fill (`=` with a `>` tip marking the
advancing edge) — no Unicode glyphs, since some consoles and remote
terminals render them inconsistently. `install.ps1`'s bar is wrapped in
`[`/`]` brackets (drawn manually, one `Write-Host` call per segment);
`install.sh`'s is too, drawn the same way inside `draw_progress_bar`. If
GitHub ever starts sending a real `Content-Length` for this endpoint, the
percentage would still be computed the same way — the "assumed 3 MB" total
only matters because that header is absent today.

## 3. Selective sync

The tarball is extracted whole (`tar -xzf ... --strip-components=1`) into a
temp dir, but only a subset of it is copied into the consuming project —
the rest of previo-sdd's own source is discarded:

```
$TMP/.claude/skills/pv-*        → .claude/skills/pv-*   (synced, obsolete pv-* dirs removed)
$TMP/.claude/pv-doc/pv-guide.*  → .claude/pv-doc/       (copied if present)
$TMP/.claude/pv-changelog.*     → .claude/               (copied if present; missing → CHANGELOG_MISSING)
$TMP/.claude/skills/pv-init/assets/pv.py → ./pv.py       (always overwritten)
```

The skills sync is two passes: copy every `pv-*` folder found in the
tarball (deleting sandbox-only tooling — `*.sandbox.*`,
`_build_sandbox.py` — from each copy, since dev fixtures never ship to
consuming projects), then remove any `pv-*` folder already on disk that no
longer exists in the tarball (a skill dropped from the framework). Only
`pv-*`-prefixed folders are touched; a project's own custom skills are
never touched by either pass.

## 4. Final messages

Printed in this fixed order, each as a `====`-bordered block except the
first line:

1. `Previo installed/updated in .claude/skills.`
2. **Changelog missing** (yellow) — if `CHANGELOG_MISSING`/`$ChangelogMissing`.
3. **Raw tag warning** (yellow) — if `INSTALLED_FROM_RAW_TAG`/`$InstalledFromRawTag`: `'{tag}' is not a published release, it was installed as a raw git tag. It may be untested/unstable.`
4. **Next step** (default color, informational — not a warning) — `You're updating...` if the project already had `.claude/skills/pv-init` before this run, else `First install...`.

`WAS_ALREADY_INSTALLED`/`$WasAlreadyInstalled` is captured at the very
start of the script, before anything is overwritten, specifically so this
last message can tell the two cases apart.
