#!/usr/bin/env bash
# Builds Beedo-Trade.app and a .dmg on macOS. Run from the app folder:  bash packaging/build_mac.sh
# Needs uv (https://docs.astral.sh/uv/). The app is ad-hoc signed, not notarised (see README: first launch).
set -euo pipefail
cd "$(dirname "$0")/.."
APP="$PWD"
VERSION="$(sed -n 's/__version__ = "\(.*\)"/\1/p' beedo_app/__init__.py)"
ARCH="$(uname -m)"   # arm64 (Apple Silicon) or x86_64 (Intel)
echo "Building Beedo-Trade $VERSION for macOS $ARCH"

uv sync --quiet
uv run pytest -q

rm -rf build dist/mac
uv run pyinstaller --noconfirm --clean --windowed --name "Beedo-Trade" \
  --icon "$APP/packaging/beedo.icns" --osx-bundle-identifier com.beedo.trade \
  --add-data "$APP/beedo_app/web:web" \
  --add-data "$APP/packaging/guide/Beedo-Trade User Guide.pdf:docs" \
  --paths "$APP/../skills/beedo-trade/scripts" --paths "$APP" --hidden-import analyze --hidden-import fundamentals --hidden-import metals \
  --exclude-module setuptools --exclude-module pkg_resources \
  --workpath build --distpath dist/mac --specpath build \
  "$APP/beedo_app/main.py"

BUNDLE="dist/mac/Beedo-Trade.app"
/usr/libexec/PlistBuddy -c "Add :CFBundleShortVersionString string $VERSION" "$BUNDLE/Contents/Info.plist" 2>/dev/null \
  || /usr/libexec/PlistBuddy -c "Set :CFBundleShortVersionString $VERSION" "$BUNDLE/Contents/Info.plist"
codesign --force --deep --sign - "$BUNDLE"   # re-sign: editing Info.plist invalidates PyInstaller's ad-hoc signature

# Smoke test without a window: the bundled engine must answer and return the right version
"$BUNDLE/Contents/MacOS/Beedo-Trade" --serve &
PID=$!
trap 'kill $PID 2>/dev/null || true' EXIT
for _ in $(seq 1 30); do
  OUT="$(curl -s -X POST -d '[]' http://127.0.0.1:8765/api/info || true)"
  [ -n "$OUT" ] && break
  sleep 1
done
echo "smoke test: $OUT"
echo "$OUT" | grep -q "\"version\": \"$VERSION\"" || { echo "Smoke test failed"; exit 1; }
curl -s -o /dev/null -w "ui files: %{http_code}\n" http://127.0.0.1:8765/vendor/lightweight-charts.standalone.production.js | grep -q 200
kill $PID; trap - EXIT

DMG="dist/Beedo-Trade-$VERSION-mac-$ARCH.dmg"
STAGE="$(mktemp -d)"
cp -R "$BUNDLE" "$STAGE/"
ln -s /Applications "$STAGE/Applications"
rm -f "$DMG"
hdiutil create -volname "Beedo-Trade $VERSION" -srcfolder "$STAGE" -ov -format UDZO "$DMG" >/dev/null
ls -lh "$DMG"
