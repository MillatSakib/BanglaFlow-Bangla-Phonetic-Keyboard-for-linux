# BanglaFlow Architecture Documentation

## Overview
BanglaFlow is a native Bengali phonetic input method for Linux based on the IBus framework. It enables system-wide Bengali typing across GNOME, GTK, Qt, and browser applications without requiring third-party background daemons or simulated keystroke injection.

```
                    ┌────────────────────────────┐
                    │      Desktop Client        │
                    │ (GNOME / GTK / Chromium)   │
                    └─────────────┬──────────────┘
                                  │ IBus DBus Protocol
                    ┌─────────────▼──────────────┐
                    │        IBus Daemon         │
                    └─────────────┬──────────────┘
                                  │
    ┌─────────────────────────────┼─────────────────────────────┐
    │ BanglaFlow Engine Process   │                             │
    │                             ▼                             │
    │                   ┌───────────────────┐                   │
    │                   │   IBus Adapter    │ (engine.py)       │
    │                   │ (BanglaFlowEngine)│                   │
    │                   └─────────┬─────────┘                   │
    │                             │ Pure Python Events / Actions│
    │                             ▼                             │
    │                   ┌───────────────────┐                   │
    │                   │   State Machine   │ (state.py)        │
    │                   │(InputStateMachine)│                   │
    │                   └────┬──────────▲───┘                   │
    │                        │          │                       │
    │         Generate Cands │          │ Pure Function Calls   │
    │                        ▼          │                       │
    │      ┌────────────────────────────┴─────────────┐         │
    │      │ Candidate Generator (candidates.py)      │         │
    │      └─────────┬──────────────────────┬─────────┘         │
    │                ▼                      ▼                   │
    │      ┌──────────────────┐   ┌──────────────────┐          │
    │      │  Phonetic Engine │   │Bengali Dictionary│          │
    │      │  (phonetic.py)   │   │ (dictionary.py)  │          │
    │      └─────────┬────────┘   └──────────────────┘          │
    │                │                                          │
    │                ▼                                          │
    │      ┌──────────────────┐                                 │
    │      │  Unicode Utils   │                                 │
    │      │(unicode_utils.py)│                                 │
    │      └──────────────────┘                                 │
    └───────────────────────────────────────────────────────────┘
```

## Key Architectural Principles

### 1. Pure Python Logic Decoupling
The core text processing layer (`phonetic.py`, `state.py`, `rules.py`, `unicode_utils.py`, `candidates.py`, `dictionary.py`, `config.py`) has strictly **zero** `gi` or `IBus` dependencies.
- Can be tested headlessly on any platform or CI runner in fractions of a second.
- Guarantees zero GUI side effects during unit and property testing.

### 2. Context-Aware Longest-Match Tokenizer
The phonetic engine parses Latin input by scanning the rule set sorted by pattern length descending (`longest match first`).
- Disambiguates phonemes such as `kkh` -> ক্ষ, `sh` -> শ, `Sh` -> ষ, `rri` -> ঋ/ৃ, `ng` -> ং, `ngg` -> ঙ্গ.
- Context conditions inspect prefix and suffix characters (vowel, consonant, punctuation, exact string) to choose the correct variant.

### 3. Unicode Policy: No Blind Normalization
- Bengali contains composition-excluded precomposed characters:
  - ড় (`U+09DC`)
  - ঢ় (`U+09DD`)
  - য় (`U+09DF`)
- Standard Unicode normalization algorithms (`NFC`, `NFD`, `NFKC`, `NFKD`) decompose these into base consonants + Nukta (`U+09BC`), which silently corrupts Bengali text representations.
- BanglaFlow enforces logical code point ordering without blind normalization and validates all outputs with `validate_bengali()`.

### 4. Deterministic State Machine
The state machine converts incoming `(keyval, keycode, modifiers)` into discrete actions:
- `Commit(text)`: emits committed text to the active application.
- `UpdatePreedit(text, cursor)`: displays interactive underline preview.
- `HidePreedit()`: hides preview when composition completes or resets.
- `UpdateLookup(candidates, index, visible)`: shows alternative suggestions.
- `HideLookup()`: dismisses the lookup popup.
- Key release events are strictly ignored to prevent duplicate processing.
- Modifier shortcuts (Ctrl, Alt, Super) commit any pending preview and pass through immediately.
- SPACE commits `selected_candidate + " "` in a single atomic commit.

