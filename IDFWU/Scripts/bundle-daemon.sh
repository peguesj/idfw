#!/usr/bin/env bash
# Bundle the /idea AG-UI FastAPI daemon into IDFWU.app.
#
# DRTW: only `uv` is available on the host (no pyinstaller/pipx/py2app).
# Lowest-risk path = a `uv`-built relocatable venv with a bundled CPython,
# plus the vendored `idea` skill package. No new build tooling, reproducible,
# Gatekeeper-friendly (plain directory tree, ad-hoc signed).
#
# Usage:  IDFWU/Scripts/bundle-daemon.sh <path-to-IDFWU.app>
set -euo pipefail

APP="${1:?usage: bundle-daemon.sh <IDFWU.app>}"
UV="${UV:-$HOME/.local/bin/uv}"
SKILL="$HOME/.claude/skills/idea"
DST="$APP/Contents/Resources/idfw-daemon"

[ -x "$UV" ] || { echo "uv not found at $UV" >&2; exit 1; }
[ -d "$SKILL" ] || { echo "/idea skill not found at $SKILL" >&2; exit 1; }

echo "→ building relocatable venv (CPython 3.12) at $DST/venv"
rm -rf "$DST"; mkdir -p "$DST"
"$UV" venv --python 3.12 --relocatable "$DST/venv"

echo "→ installing daemon deps"
"$UV" pip install --python "$DST/venv/bin/python" \
    "fastapi>=0.110" "uvicorn>=0.29" "pyyaml>=6.0"

# unified_framework.discovery provides the /api/v3/projects router the daemon mounts
if [ -d "/Users/jeremiah/Developer/idfw/unified_framework" ]; then
  "$UV" pip install --python "$DST/venv/bin/python" --no-deps \
      /Users/jeremiah/Developer/idfw 2>/dev/null || \
      echo "  (skipped unified_framework install — discovery router optional)"
fi

echo "→ vendoring /idea skill package"
mkdir -p "$DST/idea"
for item in server cli.py __init__.py __main__.py ui requirements.txt; do
  [ -e "$SKILL/$item" ] && cp -R "$SKILL/$item" "$DST/idea/"
done

echo "→ ad-hoc signing bundled Mach-Os (Gatekeeper)"
find "$DST/venv" \( -name "python*" -o -name "*.so" -o -name "*.dylib" \) -type f \
  -exec codesign --force --sign - {} \; 2>/dev/null || true
xattr -dr com.apple.quarantine "$DST" 2>/dev/null || true

echo "✓ daemon bundled: $DST"
echo "  spawn: \$RES/idfw-daemon/venv/bin/python3.12 -m idea.cli start default"
echo "         (PYTHONPATH=\$RES/idfw-daemon, HOME=\$HOME)"
