# Contributing to BanglaFlow

Contributions to BanglaFlow are welcome! Please follow these engineering guidelines:

## Code & Design Standards
- **Pure Python Core**: Never import `gi` or `IBus` into modules under `src/banglaflow/` except `engine.py` and `engine_main.py`.
- **Unicode Integrity**: Never use `unicodedata.normalize('NFC', ...)` on Bengali text. Always validate new output patterns with `validate_bengali()`.
- **Zero Network Code**: BanglaFlow is strictly offline. No network libraries or telemetry are permitted.
- **Privacy by Design**: Never log typed characters or converted text. Debug logs may only record lengths and state types.

## Adding Phonetic Rules or Vocabulary
1. Add new rule patterns to `data/rules/phonetic_rules.json`.
2. Add new dictionary words to `data/dictionaries/words.tsv` with appropriate frequency ranks.
3. Add regression tests to `tests/golden/words.tsv` or `tests/golden/regression.tsv`.
4. Run `bash scripts/run-tests.sh` to ensure all tests pass 100%.

## Submitting Pull Requests
- Ensure `bash scripts/check-tree.sh` passes.
- Ensure `bash scripts/build-deb.sh` produces a clean Debian package.
- Document design decisions in `docs/decisions.md`.

