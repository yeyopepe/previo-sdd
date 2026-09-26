#!/bin/sh
# Installs or updates Previo in the current project.
# Usage: curl -fsSL https://raw.githubusercontent.com/yeyopepe/previo-sdd/main/install.sh | sh
# Usage (specific version): curl -fsSL https://raw.githubusercontent.com/yeyopepe/previo-sdd/main/install.sh | sh -s -- v1.2.3
set -e

REPO="yeyopepe/previo-sdd"
REQUESTED_TAG="$1"

# Detect, before overwriting anything, whether this project already had the
# framework installed -- used at the end to show the right next-step message.
WAS_ALREADY_INSTALLED=0
[ -d ".claude/skills/pv-init" ] && WAS_ALREADY_INSTALLED=1

INSTALLED_FROM_RAW_TAG=0
if [ -n "$REQUESTED_TAG" ]; then
  RELEASE_JSON=$(curl -fsSL "https://api.github.com/repos/${REPO}/releases/tags/${REQUESTED_TAG}") || RELEASE_JSON=""
  if [ -n "$RELEASE_JSON" ]; then
    TAG=$(echo "$RELEASE_JSON" | grep -m1 '"tag_name"' | sed -E 's/.*"tag_name": *"([^"]+)".*/\1/')
  else
    if curl -fsSL -o /dev/null "https://api.github.com/repos/${REPO}/git/refs/tags/${REQUESTED_TAG}"; then
      TAG="$REQUESTED_TAG"
      INSTALLED_FROM_RAW_TAG=1
    else
      echo "Version '${REQUESTED_TAG}' doesn't exist in Previo's releases." >&2
      exit 1
    fi
  fi
else
  TAG=$(curl -fsSL "https://api.github.com/repos/${REPO}/releases/latest" | grep -m1 '"tag_name"' | sed -E 's/.*"tag_name": *"([^"]+)".*/\1/')
fi
if [ -z "$TAG" ]; then
  echo "Couldn't determine which version of Previo to install." >&2
  exit 1
fi
TARBALL="https://github.com/${REPO}/archive/refs/tags/${TAG}.tar.gz"

TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT

TAR_PATH="$TMP/previo.tar.gz"
echo "Downloading Previo (${TAG})..."

# GitHub's codeload tarball endpoint never sends Content-Length, so there's no
# real total to compute a bar/percentage against. Assume 3 MB (typical size of
# this repo's tarball) so the bar still moves instead of sitting empty at 0%:
# capped at 99% while still downloading (in case the real file is bigger),
# then forced to a full 100% bar once the download actually ends.
ASSUMED_TOTAL_BYTES=3145728
WIDTH=40

draw_progress_bar() {
  read_total=$1
  elapsed=$2
  done=$3
  if [ "$done" = "1" ]; then
    pct=100
    filled=$WIDTH
  else
    pct=$((read_total * 100 / ASSUMED_TOTAL_BYTES))
    [ "$pct" -gt 99 ] && pct=99
    filled=$((WIDTH * read_total / ASSUMED_TOTAL_BYTES))
    [ "$filled" -gt "$WIDTH" ] && filled=$WIDTH
  fi
  bar=$(printf '%*s' "$filled" '' | tr ' ' '=')
  if [ "$filled" -lt "$WIDTH" ] && [ "$filled" -gt 0 ]; then
    bar="${bar%=}>"
  fi
  pad=$((WIDTH - filled))
  spaces=$(printf '%*s' "$pad" '')
  size_mb=$(awk -v b="$read_total" 'BEGIN { printf "%.1f", b / 1048576 }')
  if [ "$elapsed" -gt 0 ]; then
    speed_mb=$(awk -v b="$read_total" -v s="$elapsed" 'BEGIN { printf "%.1f", (b / 1048576) / s }')
  else
    speed_mb="0.0"
  fi
  printf '\r[\033[34m%s%s\033[0m] %3d%% (%s MB, \033[90m%s MB/s\033[0m)  ' "$bar" "$spaces" "$pct" "$size_mb" "$speed_mb"
}

START_TIME=$(date +%s)
curl -fL "$TARBALL" -o "$TAR_PATH" &
CURL_PID=$!
while kill -0 "$CURL_PID" 2>/dev/null; do
  READ_TOTAL=$(wc -c < "$TAR_PATH" 2>/dev/null || echo 0)
  ELAPSED=$(($(date +%s) - START_TIME))
  draw_progress_bar "$READ_TOTAL" "$ELAPSED" 0
  sleep 0.2
done
wait "$CURL_PID"
FINAL_TOTAL=$(wc -c < "$TAR_PATH" 2>/dev/null || echo 0)
FINAL_ELAPSED=$(($(date +%s) - START_TIME))
draw_progress_bar "$FINAL_TOTAL" "$FINAL_ELAPSED" 1
echo ""

tar -xzf "$TAR_PATH" -C "$TMP" --strip-components=1

SRC_SKILLS="$TMP/.claude/skills"
DEST_SKILLS=".claude/skills"
mkdir -p "$DEST_SKILLS"

echo "[ ] Previo skills"
echo "[ ] Other stuff"

REMOVED_SKILLS=""
# Syncs only the framework's own skills (pv- prefix), without touching the user's own skills.
for dir in "$SRC_SKILLS"/pv-*; do
  name=$(basename "$dir")
  rm -rf "$DEST_SKILLS/$name"
  cp -r "$dir" "$DEST_SKILLS/$name"
  # Dev-only tooling (sandbox test files, their builder script) never ships to consuming projects.
  find "$DEST_SKILLS/$name" -type f \( -name "*.sandbox.*" -o -name "_build_sandbox.py" \) -delete
done

for dir in "$DEST_SKILLS"/pv-*; do
  [ -d "$dir" ] || continue
  name=$(basename "$dir")
  if [ ! -d "$SRC_SKILLS/$name" ]; then
    REMOVED_SKILLS="${REMOVED_SKILLS:+$REMOVED_SKILLS, }$name"
    rm -rf "$dir"
  fi
done

printf '\033[2A\r[x] Previo skills\033[1B\r' 2>/dev/null || true

# Syncs the framework's documentation.
mkdir -p ".claude/pv-doc"
for doc in pv-guide.en.md pv-guide.es.md; do
  if [ -f "$TMP/.claude/pv-doc/$doc" ]; then
    cp "$TMP/.claude/pv-doc/$doc" ".claude/pv-doc/$doc"
  fi
done

# Syncs the framework's changelog.
CHANGELOG_MISSING=0
for doc in pv-changelog.en.md pv-changelog.es.md; do
  if [ -f "$TMP/.claude/$doc" ]; then
    cp "$TMP/.claude/$doc" ".claude/$doc"
  else
    CHANGELOG_MISSING=1
  fi
done

# Syncs the pv.py launcher at the repo root (generated file, always overwritten).
if [ -f "$SRC_SKILLS/pv-init/assets/pv.py" ]; then
  cp "$SRC_SKILLS/pv-init/assets/pv.py" "pv.py"
fi

printf '\r[x] Other stuff\033[1B\r' 2>/dev/null || true

if [ -n "$REMOVED_SKILLS" ]; then
  echo "Removed obsolete skills: $REMOVED_SKILLS"
fi

echo ""
echo "Previo installed/updated successfully. Ready to go!"
echo ""
if [ "$CHANGELOG_MISSING" = "1" ]; then
  printf '\033[33m'
  echo "=========================================================="
  echo " Warning: the new version was installed, but something"
  echo " went wrong and the changelog for this release is missing."
  echo " You won't have information about what changed."
  echo "=========================================================="
  printf '\033[0m'
  echo ""
fi
if [ "$INSTALLED_FROM_RAW_TAG" = "1" ]; then
  printf '\033[33m'
  echo "=========================================================="
  echo " Warning: '${TAG}' is not a published release, it was"
  echo " installed as a raw git tag. It may be untested/unstable."
  echo "=========================================================="
  printf '\033[0m'
  echo ""
fi
if [ "$WAS_ALREADY_INSTALLED" = "1" ]; then
  echo "=========================================================="
  echo " You're updating from a previous version: run /pv-update"
  echo " in your agent to check and repair the configuration."
  echo "=========================================================="
else
  echo "=========================================================="
  echo " First install: run /pv-init in your agent to set it up."
  echo "=========================================================="
fi
