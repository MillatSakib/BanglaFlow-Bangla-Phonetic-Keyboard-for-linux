#!/usr/bin/env bash
# ==============================================================================
# BanglaFlow — Debian Upstream Source Package Builder
# Generates pristine .orig.tar.gz and Debian 3.0 (quilt) source package for
# mentors.debian.net and Debian/Ubuntu Upstream archive submission.
# ==============================================================================

set -euo pipefail

VERSION="1.0.1"
PKG="banglaflow"
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "==> Building Debian Upstream Source Package for ${PKG} v${VERSION}..."

cd "${ROOT_DIR}"

# 1. Clean previous build artifacts
rm -f "../${PKG}_${VERSION}.orig.tar.gz"
rm -f "../${PKG}_${VERSION}-1.debian.tar.xz"
rm -f "../${PKG}_${VERSION}-1.dsc"
rm -f "../${PKG}_${VERSION}-1_source."*

# 2. Create pristine upstream tarball (.orig.tar.gz)
echo "==> Packaging upstream source archive..."
tar --exclude-vcs \
    --exclude='./debian' \
    --exclude='./website' \
    --exclude='./.github' \
    --exclude='*.deb' \
    --exclude='*.snap' \
    --exclude='__pycache__' \
    -czf "../${PKG}_${VERSION}.orig.tar.gz" .

# 3. Build source package
echo "==> Running dpkg-buildpackage (source only)..."
dpkg-buildpackage -S -us -uc

echo ""
echo "================================================================="
echo " Debian Source Package generated successfully in parent directory:"
echo "  - ../${PKG}_${VERSION}.orig.tar.gz"
echo "  - ../${PKG}_${VERSION}-1.debian.tar.xz"
echo "  - ../${PKG}_${VERSION}-1.dsc"
echo "  - ../${PKG}_${VERSION}-1_source.changes"
echo "================================================================="
echo "Ready for upload to mentors.debian.net via dput!"

