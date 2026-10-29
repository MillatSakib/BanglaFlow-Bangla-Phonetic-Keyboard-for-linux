#!/usr/bin/env bash
set -euo pipefail

# test-install-container.sh
# Tests package installation, verification, upgrade, removal, and purge in an isolated container.

DEB_FILE="${1:-}"
if [ -z "$DEB_FILE" ] || [ ! -f "$DEB_FILE" ]; then
    DEB_FILE=$(ls -t ../banglaflow_*.deb 2>/dev/null | head -n 1 || true)
    if [ -z "$DEB_FILE" ]; then
        DEB_FILE=$(ls -t banglaflow_*.deb 2>/dev/null | head -n 1 || true)
    fi
fi

if [ -z "$DEB_FILE" ] || [ ! -f "$DEB_FILE" ]; then
    echo "ERROR: .deb file not found to test in container."
    exit 1
fi

mkdir -p docs/evidence
LOG_FILE="$(pwd)/docs/evidence/install-test.log"
exec > >(tee "$LOG_FILE") 2>&1

echo "=== Testing package installation in container ==="
echo "Package: $DEB_FILE"

docker run --rm \
    -v "$(realpath "$DEB_FILE"):/tmp/banglaflow.deb:ro" \
    ubuntu:24.04 bash -c '
set -euo pipefail
echo "--- [1] Updating apt and installing dependencies ---"
apt-get update -qq
apt-get install -y --no-install-recommends \
    ibus \
    python3 \
    python3-gi \
    gir1.2-ibus-1.0 \
    gir1.2-glib-2.0

echo "--- [2] Installing banglaflow.deb ---"
dpkg -i /tmp/banglaflow.deb

echo "--- [3] Verifying files installed ---"
test -f /usr/share/ibus/component/banglaflow.xml
test -x /usr/libexec/ibus-engine-banglaflow
test -f /usr/lib/python3/dist-packages/banglaflow/__init__.py
test -f /usr/share/banglaflow/rules/phonetic_rules.json
test -f /usr/share/banglaflow/dictionaries/words.tsv
test -f /usr/share/banglaflow/icons/banglaflow.png

echo "--- [4] Smoke testing python module in container ---"
python3 -c "
import banglaflow
from banglaflow.phonetic import PhoneticEngine
from banglaflow.rules import load_rules
from banglaflow.dictionary import BengaliDictionary
from banglaflow.unicode_utils import validate_bengali

eng = PhoneticEngine()
out = eng.convert(\"ami bangla likhi\")
valid, reason = validate_bengali(out)
assert valid, f\"Invalid Bengali: {reason}\"
print(\"Smoke test inside container OK:\", out)
"

echo "--- [5] Testing upgrade (reinstall) ---"
dpkg -i /tmp/banglaflow.deb

echo "--- [6] Testing remove ---"
dpkg --remove banglaflow
test ! -f /usr/share/ibus/component/banglaflow.xml
test ! -x /usr/libexec/ibus-engine-banglaflow

echo "--- [7] Testing purge ---"
dpkg --purge banglaflow
test ! -d /usr/share/banglaflow
test ! -d /usr/lib/python3/dist-packages/banglaflow

echo "--- Container test sequence completed successfully! ---"
'

echo "=== test-install-container.sh PASSED ==="
