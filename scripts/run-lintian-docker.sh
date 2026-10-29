#!/usr/bin/env bash
set -euo pipefail

DEB_PATH="$(realpath banglaflow_0.1.0-1_all.deb)"
mkdir -p docs/evidence

echo "=== Running Lintian check in Ubuntu 24.04 container ==="
docker run --rm -v "${DEB_PATH}:/tmp/banglaflow.deb:ro" ubuntu:24.04 bash -c 'apt-get update -qq && apt-get install -y --no-install-recommends lintian && echo "=== Lintian Output Start ===" && lintian --display-info /tmp/banglaflow.deb && echo "=== Lintian Output End ==="' 2>&1 | tee docs/evidence/lintian.log

echo "Lintian check completed. Saved to docs/evidence/lintian.log"
