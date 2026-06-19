#!/usr/bin/env bash
# Bump the bundled modelship version and the add-on's own version in lockstep.
#
#   ./bump.sh <modelship-version>      e.g. ./bump.sh 0.5.0
#
# - build.yaml: repoint both build_from lines at modelship:<version>-cpu
# - config.yaml: bump the add-on's own version (patch) so HA offers the update
# - CHANGELOG.md: prepend an entry
set -euo pipefail

MSHIP_VERSION="${1:?usage: bump.sh <modelship-version> (e.g. 0.5.0)}"
MSHIP_VERSION="${MSHIP_VERSION#v}"   # tolerate a leading "v"

ROOT="$(cd "$(dirname "$0")" && pwd)"
BUILD="$ROOT/modelship-voice/build.yaml"
CONFIG="$ROOT/modelship-voice/config.yaml"
CHANGELOG="$ROOT/modelship-voice/CHANGELOG.md"

current="$(sed -nE 's#.*modelship:([0-9.]+)-cpu.*#\1#p' "$BUILD" | head -1)"
if [ "$current" = "$MSHIP_VERSION" ]; then
    echo "already pinned to modelship ${MSHIP_VERSION}; nothing to do"
    exit 0
fi

# 1. Repoint both arch build_from lines at the new -cpu image.
sed -i -E "s#(ghcr\.io/alez007/modelship:)[0-9.]+(-cpu)#\1${MSHIP_VERSION}\2#g" "$BUILD"

# 2. Bump the add-on's own version (patch).
old_addon="$(sed -nE 's/^version:[[:space:]]*"?([0-9]+\.[0-9]+\.[0-9]+)"?.*/\1/p' "$CONFIG")"
new_addon="$(python3 - "$old_addon" <<'PY'
import sys
maj, mino, pat = (int(x) for x in sys.argv[1].split("."))
print(f"{maj}.{mino}.{pat + 1}")
PY
)"
sed -i -E "s/^version:.*/version: \"${new_addon}\"/" "$CONFIG"

# 3. Prepend a changelog entry.
tmp="$(mktemp)"
{
    printf '# Changelog\n\n## %s\n\n- Bump bundled modelship to %s.\n\n' "$new_addon" "$MSHIP_VERSION"
    tail -n +2 "$CHANGELOG"
} >"$tmp"
mv "$tmp" "$CHANGELOG"

echo "modelship ${current:-?} -> ${MSHIP_VERSION}; add-on ${old_addon} -> ${new_addon}"
