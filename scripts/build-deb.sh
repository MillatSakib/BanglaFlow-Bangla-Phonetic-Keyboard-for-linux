#!/usr/bin/env bash
set -euo pipefail

# build-deb.sh - Complete build and verification pipeline for BanglaFlow
# Halts immediately on any failure.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$ROOT_DIR"
mkdir -p docs/evidence

echo "=========================================="
echo " BanglaFlow Debian Build & Verification   "
echo "=========================================="

echo "[1/3] Running test suite..."
bash scripts/run-tests.sh

echo "[2/3] Building Debian package with dpkg-buildpackage..."
dpkg-buildpackage -us -uc -b

echo "[3/3] Verifying and copying built .deb package..."
DEB_FILE=$(ls -t ../banglaflow_*.deb 2>/dev/null | head -n 1 || true)
if [ -z "$DEB_FILE" ] || [ ! -f "$DEB_FILE" ]; then
    echo "ERROR: .deb file was not generated!"
    exit 1
fi
echo "Found generated package: $DEB_FILE"
cp "$DEB_FILE" "$ROOT_DIR/"
cp "$DEB_FILE" "$ROOT_DIR/banglaflow.deb"
PKG_BASENAME="$(basename "$DEB_FILE")"

echo "=========================================="
echo " BUILD SUCCESSFUL!                        "
echo " Package: $PKG_BASENAME                   "
echo " Convenient copy: banglaflow.deb          "
echo "=========================================="

