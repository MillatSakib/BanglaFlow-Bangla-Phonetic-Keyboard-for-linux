#!/usr/bin/env bash
# ==============================================================================
# BanglaFlow — Launchpad PPA Uploader
# Builds signed source package and uploads to ppa:kovenceit/banglaflow
# ==============================================================================

set -euo pipefail

PPA="ppa:kovenceit/banglaflow"
KEY_EMAIL="contact@kovence.com"
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "==> Preparing BanglaFlow for Launchpad PPA (${PPA})..."
cd "${ROOT_DIR}"

# 1. Detect package version from debian/changelog
VERSION=$(dpkg-parsechangelog -S Version)
PKG=$(dpkg-parsechangelog -S Source)
BASE_VER=$(echo "${VERSION}" | cut -d'-' -f1)

echo "==> Package: ${PKG}, Version: ${VERSION}"

# 2. Always recreate pristine orig.tar.gz to match current tree
echo "==> Creating fresh ../${PKG}_${BASE_VER}.orig.tar.gz..."
rm -f "../${PKG}_${BASE_VER}.orig.tar.gz"
tar --exclude-vcs \
    --exclude='./debian' \
    --exclude='./website' \
    --exclude='./.github' \
    --exclude='*.deb' \
    --exclude='*.snap' \
    --exclude='__pycache__' \
    -czf "../${PKG}_${BASE_VER}.orig.tar.gz" .

# 3. Clean old debhelper artifacts
dh clean || true

# 4. Build signed source package
echo "==> Building and signing source package with ${KEY_EMAIL}..."
dpkg-buildpackage -S -k"${KEY_EMAIL}"

# 5. Upload via dput
CHANGES_FILE="../${PKG}_${VERSION}_source.changes"
echo "==> Uploading ${CHANGES_FILE} to ${PPA}..."
dput "${PPA}" "${CHANGES_FILE}"

echo ""
echo "================================================================="
echo " Successfully uploaded BanglaFlow to Launchpad PPA!"
echo " Check build status at: https://launchpad.net/~kovenceit/+archive/ubuntu/banglaflow"
echo "================================================================="

