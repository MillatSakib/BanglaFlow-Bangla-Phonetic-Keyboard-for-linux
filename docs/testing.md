# BanglaFlow Testing Guide

BanglaFlow utilizes a multi-tiered test suite ensuring 100% linguistic accuracy, deterministic behavior, and system reliability.

## 1. Test Levels

| Test Suite | Location | Purpose | Dependencies |
| :--- | :--- | :--- | :--- |
| **Unit Tests** | `tests/unit/` | Phonetic rules, Unicode validity, state machine, config | None (Pure Python) |
| **Golden Corpus** | `tests/golden/` | 700+ verified word pairs, sentences, and regressions | None (Pure Python) |
| **Property Tests** | `tests/property/` | Hypothesis-based fuzzing for invariants | `hypothesis` |
| **Adapter Tests** | `tests/fakes/` | Mocked IBus Engine verifying exact call sequences | None |
| **Security Tests** | `tests/unit/test_security.py` | Zero network code, no typed text in logs | None |
| **Integration** | `scripts/test-install-container.sh` | Clean container install/remove/purge/upgrade | Docker |

---

## 2. Running Tests Locally

Run all unit, golden, and property tests:
```bash
bash scripts/run-tests.sh
```

Or using pytest directly:
```bash
PYTHONPATH=src:. pytest -v tests/
```

---

## 3. Container Installation & Smoke Testing

To verify package installation in a fresh, isolated Ubuntu container:
```bash
bash scripts/test-install-container.sh
```
This tests:
1. `dpkg -i` on clean Ubuntu.
2. File layout verification in `/usr/lib`, `/usr/libexec`, `/usr/share`.
3. Headless Python smoke test importing engine and converting text.
4. Engine listing in `ibus`.
5. Upgrade test (`dpkg -i` reinstallation).
6. Clean removal (`dpkg -r`) and purge (`dpkg -P`).

