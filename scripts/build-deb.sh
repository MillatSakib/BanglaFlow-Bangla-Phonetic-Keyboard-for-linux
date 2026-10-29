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

echo "[1/6] Validating file tree & schemas..."
bash scripts/check-tree.sh

echo "[2/6] Running unit, golden & property tests..."
bash scripts/run-tests.sh

echo "[3/6] Building Debian package with dpkg-buildpackage..."
dpkg-buildpackage -us -uc -b

echo "[4/6] Verifying built .deb package..."
DEB_FILE=$(ls -t ../banglaflow_*.deb 2>/dev/null | head -n 1 || true)
if [ -z "$DEB_FILE" ] || [ ! -f "$DEB_FILE" ]; then
    echo "ERROR: .deb file was not generated!"
    exit 1
fi
echo "Found generated package: $DEB_FILE"

# Save package inspection info
{
    echo "=== dpkg-deb -I ==="
    dpkg-deb -I "$DEB_FILE"
    echo ""
    echo "=== dpkg-deb -c ==="
    dpkg-deb -c "$DEB_FILE"
} > docs/evidence/dpkg-deb-info.txt
echo "Saved package info to docs/evidence/dpkg-deb-info.txt"

# Copy package and generate checksums
cp "$DEB_FILE" "$ROOT_DIR/"
PKG_BASENAME="$(basename "$DEB_FILE")"
sha256sum "$PKG_BASENAME" > "$ROOT_DIR/SHA256SUMS"
cat "$ROOT_DIR/SHA256SUMS" >> docs/evidence/dpkg-deb-info.txt

echo "[5/6] Testing container installation, upgrade, remove, purge..."
bash scripts/test-install-container.sh "$ROOT_DIR/$PKG_BASENAME"

echo "=========================================="
echo " BUILD AND VERIFICATION SUCCESSFUL!       "
echo " Package: $PKG_BASENAME"
echo " Checksum: $(cat "$ROOT_DIR/SHA256SUMS")"
echo "=========================================="

