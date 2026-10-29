# Architecture & Design Decisions — BanglaFlow

## 1. Engine Architecture
- **Decision**: Design A (Pure-Python engine launched by IBus via component XML).
- **Why**: Ubuntu 26.04 provides official `python3-gi` and `gir1.2-ibus-1.0` with Python overrides for `IBus.Engine`, `IBus.LookupTable`, `IBus.Text`, `IBus.Component`, `IBus.Factory`. Pure Python eliminates native C compilation dependencies, produces an `Architecture: all` Debian package, and allows rapid execution of property and golden tests.
- **Alternatives Considered**: C shim + Python core. Rejected as unnecessary overhead since PyGObject introspects IBus 1.0 directly and cleanly with sub-millisecond dispatch times.
- **Verification**: Verified via `/usr/bin/python3 -c "import gi; gi.require_version('IBus', '1.0'); from gi.repository import IBus"`.

## 2. Decoupling and Pure Logic Separation
- **Decision**: Zero `gi` or `IBus` imports in `phonetic.py`, `rules.py`, `unicode_utils.py`, `candidates.py`, `dictionary.py`, and `state.py`.
- **Why**: Guarantees that all phonetic rules, Bengali Unicode validation, candidate ranking, and the key-event state machine can be tested headlessly on any machine, CI runner, or platform without an X11/Wayland display, D-Bus session, or root privileges.
- **Verification**: Unit tests and hypothesis property tests run against `banglaflow.phonetic` and `banglaflow.state` without any GUI dependencies. A dedicated static test asserts no prohibited imports (`socket`, `urllib`, `requests`, `gi`) in core modules.

## 3. Component Registration & Execution Paths
- **Decision**:
  - Component XML: `/usr/share/ibus/component/banglaflow.xml`
  - Engine executable: `/usr/libexec/ibus-engine-banglaflow`
  - Launcher accepts `--ibus` argument passed by IBus daemon.
  - Python package installed to `/usr/lib/python3/dist-packages/banglaflow/`
  - Data directory: `/usr/share/banglaflow/`
- **Why**: Follows Ubuntu 26.04 standards (as observed in `m17n.xml` and `table.xml` using `/usr/libexec/ibus-engine-*`).

## 4. Unicode Policy & Normalization
- **Decision**: Explicit rejection of blanket Unicode normalization (NFC/NFKC/NFD) on Bengali output.
- **Why**: Bengali includes precomposed characters (e.g. ড় U+09DC, ঢ় U+09DD, য় U+09DF) that decompose under NFD/NFKD, and vowel signs (ো U+09CB, ৌ U+09CC) that can decompose into two code points. Blanket normalization silently mutates intended code point sequences.
- **Verification**: `validate_bengali(text)` strictly checks valid Bengali Unicode sequence rules (logical order, valid dependent vowels following consonant/nukta/hasanta, no consecutive hasantas, no double vowel signs, valid ZWJ/ZWNJ usage).

## 5. Phonetic Rule Definition & Longest-Match Tokenizer
- **Decision**: Context-aware, longest-match tokenization over structured rule tables loaded from validated data.
- **Why**: Hardcoded `if/else` chains are error-prone and unmaintainable. Data-driven rules with longest-match prefix matching allow clean handling of multi-character phonemes (`kkh` -> ক্ষ, `sh` -> শ, `ng` -> ং, `rri` -> ঋ/ৃ) and contextual transformations.
- **Licensing**: Rules are designed clean-room based on the standard phonetic mapping conventions used by the Bengali language community.

