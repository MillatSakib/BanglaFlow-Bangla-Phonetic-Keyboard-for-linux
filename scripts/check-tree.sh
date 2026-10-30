#!/usr/bin/env bash
set -euo pipefail

echo "=== [1/3] Checking required files in tree ==="
required_files=(
    "README.md"
    "LICENSE"
    "pyproject.toml"
    ".gitignore"
    "CHANGELOG.md"
    "src/banglaflow/__init__.py"
    "src/banglaflow/unicode_utils.py"
    "src/banglaflow/rules.py"
    "src/banglaflow/phonetic.py"
    "src/banglaflow/dictionary.py"
    "src/banglaflow/candidates.py"
    "src/banglaflow/state.py"
    "src/banglaflow/config.py"
    "src/banglaflow/engine.py"
    "src/banglaflow/engine_main.py"
    "src/ibus-engine-banglaflow"
    "data/ibus/banglaflow.xml"
    "data/rules/phonetic_rules.json"
    "data/dictionaries/words.tsv"
    "data/icons/banglaflow.png"
    "tests/golden/words.tsv"
    "tests/golden/sentences.tsv"
    "tests/golden/regression.tsv"
    "debian/control"
    "debian/rules"
    "debian/changelog"
    "debian/copyright"
)

missing=0
for f in "${required_files[@]}"; do
    if [ ! -f "$f" ]; then
        echo "MISSING REQUIRED FILE: $f"
        missing=$((missing + 1))
    fi
done

if [ "$missing" -ne 0 ]; then
    echo "Tree check failed: $missing files missing."
    exit 1
fi
echo "All required files exist."

echo "=== [2/3] Validating XML files ==="
python3 -c "
import xml.etree.ElementTree as ET
ET.parse('data/ibus/banglaflow.xml')
print('data/ibus/banglaflow.xml is valid XML.')
"

echo "=== [3/3] Validating rules and dictionary ==="
PYTHONPATH=src python3 -c "
from banglaflow.rules import load_rules
from banglaflow.dictionary import BengaliDictionary

rules = load_rules()
print(f'Phonetic rules valid. Loaded {len(rules.patterns)} patterns.')

b_dict = BengaliDictionary()
print(f'Bengali dictionary valid. Contains words.')
"

echo "check-tree.sh PASSED."
