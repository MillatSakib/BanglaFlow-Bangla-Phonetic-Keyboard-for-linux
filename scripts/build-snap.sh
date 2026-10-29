#!/usr/bin/env bash
set -euo pipefail

# build-snap.sh - Fast native Snap package builder for BanglaFlow
# Builds directly using 'snap pack' without requiring LXD or network builders.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$ROOT_DIR"
BUILD_DIR="/tmp/banglaflow_snap_build"

echo "=========================================="
echo " BanglaFlow Snap Package Builder          "
echo "=========================================="

rm -rf "$BUILD_DIR"
mkdir -p "$BUILD_DIR/meta/gui"
mkdir -p "$BUILD_DIR/snap/hooks"
mkdir -p "$BUILD_DIR/usr/lib/python3/dist-packages/banglaflow"
mkdir -p "$BUILD_DIR/usr/libexec"
mkdir -p "$BUILD_DIR/usr/share/ibus/component"
mkdir -p "$BUILD_DIR/usr/share/banglaflow/rules"
mkdir -p "$BUILD_DIR/usr/share/banglaflow/dictionaries"
mkdir -p "$BUILD_DIR/usr/share/banglaflow/icons"

echo "[1/4] Copying engine and assets..."
cp -r src/banglaflow/* "$BUILD_DIR/usr/lib/python3/dist-packages/banglaflow/"
cp src/ibus-engine-banglaflow "$BUILD_DIR/usr/libexec/ibus-engine-banglaflow"
chmod 755 "$BUILD_DIR/usr/libexec/ibus-engine-banglaflow"

cp data/ibus/banglaflow.xml "$BUILD_DIR/usr/share/ibus/component/banglaflow.xml"
cp -r data/rules/* "$BUILD_DIR/usr/share/banglaflow/rules/"
cp -r data/dictionaries/* "$BUILD_DIR/usr/share/banglaflow/dictionaries/"
cp -r data/icons/* "$BUILD_DIR/usr/share/banglaflow/icons/"

cp data/icons/banglaflow-512.png "$BUILD_DIR/meta/gui/icon.png"
cp snap/hooks/install "$BUILD_DIR/snap/hooks/install"
cp snap/hooks/remove "$BUILD_DIR/snap/hooks/remove"
chmod 755 "$BUILD_DIR/snap/hooks/install" "$BUILD_DIR/snap/hooks/remove"

echo "[2/4] Generating snap metadata..."
cat << 'EOF' > "$BUILD_DIR/meta/snap.yaml"
name: banglaflow
version: '1.0.1'
summary: Native Bengali Phonetic Keyboard for Linux (IBus)
description: |
  BanglaFlow is a fast, lightweight, and offline Bengali phonetic input method
  for Linux desktops (Ubuntu GNOME Wayland & X11). Features full Avro phonetic
  layout compatibility with a 177k+ pre-warmed dictionary cache.
  Developed by Kovence (https://kovence.com).
architectures:
  - amd64
base: core24
confinement: classic
grade: stable
apps:
  banglaflow:
    command: usr/libexec/ibus-engine-banglaflow --ibus
EOF

echo "[3/4] Packing snap package..."
snap pack "$BUILD_DIR" "$ROOT_DIR"

SNAP_FILE=$(ls -t "$ROOT_DIR"/banglaflow_*_amd64.snap 2>/dev/null | head -n 1 || true)
rm -rf "$BUILD_DIR"

echo "=========================================="
echo " SNAP BUILD SUCCESSFUL!                   "
echo " Package: $(basename "$SNAP_FILE")        "
echo " Size: $(ls -lh "$SNAP_FILE" | awk '{print $5}') "
echo "=========================================="
