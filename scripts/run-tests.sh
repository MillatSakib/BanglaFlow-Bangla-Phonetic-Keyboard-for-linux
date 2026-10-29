#!/usr/bin/env bash
set -euo pipefail

mkdir -p docs/evidence

echo "=== Running test suite (Unit, Golden, Property) ==="
PYTHONPATH=src:. pytest -v --tb=short tests/ | tee docs/evidence/pytest.log

echo "=== Test Suite PASSED ==="

