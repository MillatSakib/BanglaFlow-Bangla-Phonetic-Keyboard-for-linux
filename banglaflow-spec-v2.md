# BanglaFlow — Agent Specification v2

Project: BanglaFlow, a native, system-wide Bengali phonetic input method for Linux
Language: Python 3 | Framework: IBus | Package: .deb | Distribution: GitHub Releases + Launchpad PPA
First target: Ubuntu LTS with GNOME (verify the exact release in Phase 0)

---

## 0. HOW YOU MUST WORK (read first, applies to everything)

You are a senior Linux input-method engineer, Python developer, Bengali text-processing engineer, Debian maintainer and test engineer. Build a real, end-user-ready input method, not a demo or a standalone editor.

### 0.1 Evidence rules (non-negotiable)
- Every claim of "works / passes / builds / installed" must be backed by a command you actually ran and its real output.
- Save raw outputs to `docs/evidence/` (e.g. `pytest.log`, `dpkg-deb-info.txt`, `lintian.log`, `install-test.log`, `env.txt`).
- If you could not run something (no root, no display, no network, no Docker), mark it `NOT RUN` with the reason. Never write "should work".
- Never invent package names, API names, file paths or versions. Verify with `apt-cache policy`, `dpkg -L`, `python3 -c "import gi; ..."`, `gi-docgen`/`gir` introspection, or the installed `.gir` file. If unverifiable, say so.
- "100% accurate" is not a claim you may make. Instead, meet the measurable gates in section 12 and report the real numbers.

### 0.2 Working method
1. Inspect the workspace and environment first. Preserve existing useful work; never overwrite blindly.
2. Record decisions in `docs/decisions.md` (what, why, alternatives, verified how).
3. Work in small increments: implement → test → fix root cause → rerun the full suite.
4. When a command fails, read the real error and find the cause before changing code. Do not guess-patch.
5. No unrelated refactors while fixing a bug. Every bug fix gets a regression test first (test fails, fix, test passes).
6. Do not stop after a plan. Do not ask unnecessary questions; choose reasonable defaults and document them. Ask only when a decision materially affects security, compatibility or publication, or when credentials/authorization are needed.
7. If the environment is missing something (root, Docker, Xvfb, GUI), finish all independent work and list the blocker precisely.

---

## 1. PHASE 0 — ENVIRONMENT AND FEASIBILITY (before writing code)

Capture into `docs/evidence/env.txt`:
- `lsb_release -a`, `uname -a`, `echo $XDG_SESSION_TYPE $XDG_CURRENT_DESKTOP`
- `python3 --version`, `ibus version`, `apt-cache policy ibus python3-gi gir1.2-ibus-1.0 debhelper dh-python lintian`
- Whether `dpkg-buildpackage`, `lintian`, `sbuild`/`pbuilder`/`docker`, `autopkgtest`, `xvfb-run`, `xdotool`, `dbus-run-session` are available.

Verify and document:
- How IBus engines register on this release: component XML in `/usr/share/ibus/component/*.xml`, `<exec>` launching an engine process, `--ibus` flag semantics, and the engine-name → factory mapping. Read an installed, maintained example (e.g. look at `ibus-typing-booster` if available via apt, or the IBus source/GIR docs) rather than relying on memory.
- The real GI namespace and version: `gi.require_version('IBus', '1.0')`, plus `GLib`, `GObject`.
- The real signatures of `IBus.Engine` virtual methods on the installed version (`do_process_key_event`, `do_focus_in`, `do_focus_out`, `do_reset`, `do_enable`, `do_disable`, `do_candidate_clicked`, `do_page_up/down`, `do_cursor_up/down`, `do_set_capabilities`, `do_property_activate`) and of `IBus.Text`, `IBus.LookupTable`, `update_preedit_text`, `commit_text`, `hide_preedit_text`, `update_lookup_table`, `register_properties`.
- Session reality: GNOME on Ubuntu defaults to Wayland. Document how IBus reaches apps there (GNOME Shell integration, text-input protocol, GTK/Qt IM modules, Electron/Chromium flags such as `--ozone-platform=wayland` / `--enable-wayland-ime`, XWayland apps via XIM/GTK module). Do not claim terminals, VS Code, Electron or Flatpak/Snap apps work until tested; document each as Tested / Untested / Known-limited.

Choose one of two designs and justify with evidence:
- A. Pure-Python engine launched by IBus via component XML (preferred first target).
- B. Python core + thin shim, only if A hits a verified limitation.

---

## 2. REPOSITORY LAYOUT

```
banglaflow/
  README.md  LICENSE  pyproject.toml  .gitignore  CHANGELOG.md
  src/banglaflow/
    __init__.py
    unicode_utils.py     # validation, ordering checks, no blind normalization
    rules.py             # data-driven phonetic rules (loaded from data, validated)
    phonetic.py          # pure conversion engine, zero IBus/GI imports
    dictionary.py        # offline dictionary + user dictionary
    candidates.py        # candidate generation/ranking
    state.py             # pure key-event state machine, zero GI imports
    config.py            # XDG config load/validate
    engine.py            # thin IBus adapter ONLY
    __main__.py / engine_main.py   # process entry point used by <exec>
  data/
    ibus/banglaflow.xml.in   # component metadata
    icons/  dictionaries/  rules/
  tests/
    unit/ (test_phonetic, test_unicode, test_candidates, test_state, test_config)
    golden/ (words.tsv, sentences.tsv, regression.tsv)
    property/ (hypothesis-based)
    integration/ (needs ibus/dbus/xvfb; clearly separated and skippable)
    fakes/ (fake IBus engine API for adapter tests)
  debian/ (control changelog rules copyright compat-or-debhelper-compat source/format
           install, postinst/postrm only if needed, tests/ for autopkgtest, lintian-overrides if justified)
  docs/ (installation, architecture, testing, contributing, decisions, evidence/)
  scripts/ (check-tree.sh, run-tests.sh, build-deb.sh, test-install-container.sh)
```
Hard architecture rule: `phonetic.py` and `state.py` must never import `gi`. All logic is testable without IBus. `engine.py` only translates IBus callbacks to state-machine inputs and state-machine outputs to IBus calls.

---

## 3. PHONETIC ENGINE

### 3.1 Design
- Longest-match, context-aware tokenizer over a validated rule table (data files, not hard-coded if-chains), producing a sequence of units: consonant, vowel (independent or dependent depending on context), hasanta/conjunct joiner, modifiers, digits, punctuation, pass-through Latin.
- Deterministic: same input → same output. Pure functions. No hidden global state.
- Rule file schema is documented and validated at load time (duplicates, shadowed patterns, invalid code points rejected with clear errors).
- Reference for behavior: study Avro Phonetic's publicly documented rules for familiarity, but implement your own rule set. Before copying any rule data, check its license compatibility; otherwise derive rules independently and document the sources in `docs/decisions.md`.
- Documented escape for literal text: e.g. a configurable pass-through (Avro-style backtick) and an English/Bengali mode toggle.

### 3.2 Linguistic coverage (each item needs its own tests)
- Independent vowels: অ আ ই ঈ উ ঊ ঋ এ ঐ ও ঔ.
- Dependent signs: া ি ী ু ূ ৃ ে ৈ ো ৌ — dependent form only after a consonant, independent form at word start or after another vowel. Define and test ambiguous cases (`i`, `ii`, `u`, `uu`, `rri`, `e`, `oi`, `o`, `ou`, `oo`, `a` vs `o` inherent vowel).
- Consonants incl. aspirated, retroflex, nasals, ড় ঢ় য় (precomposed U+09DC/U+09DD/U+09DF policy documented), ৎ (khanda ta U+09CE), ং ঃ ঁ.
- Conjuncts via hasanta (U+09CD): common clusters (ক্ষ জ্ঞ ন্ত ন্দ ম্প স্ত ঙ্গ ঞ্চ শ্চ ষ্ট স্ক ত্র দ্র ক্র প্র ব্র গ্র ...), explicit hasanta input rule (e.g. `,,` or documented key), and rules for when no conjunct is formed.
- Reph (র + ্ + consonant), র-ফলা, য-ফলা, ব-ফলা, and the ZWJ/ZWNJ policy (e.g. র‍্য) — document exact code point sequences and test them.
- Final য় vs য (`banglay` → বাংলায়), `ng` → ং in context (`bangla` → বাংলা) vs ঙ্গ/ঙ, `ng`/`ngg`/`Ng` disambiguation table.
- Bengali digits (optional mode), Bengali punctuation: `.` → । (configurable), `?` `,` `!` `$` → ৳ (documented).

### 3.3 Unicode correctness
- Logical order only. Never reorder code points to match visual appearance (e.g. কি = U+0995 U+09BF). Pre-base vowel signs are the renderer's job.
- DO NOT apply blanket NFC/NFKC/NFD to output. Bengali has composition-excluded and decomposable characters (e.g. ড় U+09DC decomposes to ড + ় under normalization; ো/ৌ decompose to two code points), so normalization silently changes results. State an explicit output policy, implement a validator, and test it.
- Implement `validate_bengali(text)` that flags: dependent vowel with no base, double dependent vowels, consecutive hasanta, hasanta at invalid positions, stray ZWJ/ZWNJ, nukta misuse, characters outside the allowed set.
- Every converted output in the test corpus must pass the validator.

### 3.4 Required examples (initial, not complete)
`ami`→আমি, `bangla`→বাংলা, `banglay`→বাংলায়, `likhi`→লিখি, `bhasha`→ভাষা, `amar`→আমার.
Provide a code-point-level assertion for each, e.g. `আমি == "\u0986\u09AE\u09BF"`.

---

## 4. KEY-EVENT STATE MACHINE (pure Python, fully unit-tested)

State: `phonetic_buffer`, `bengali_preview`, `candidates`, `selected_index`, `composing: bool`, `mode` (bengali/english-passthrough), `caps` (preedit supported?).

Input: `(keyval, keycode, modifiers, is_release)`. Output: `(handled: bool, actions: list)` where actions are `Commit(text)`, `UpdatePreedit(text, cursor)`, `HidePreedit`, `UpdateLookup(...)`, `HideLookup`. The IBus adapter performs actions in order and returns `handled`.

Rules (each needs a test):
1. Key RELEASE events: ignore, return not-handled (never double-process).
2. Any key with Ctrl, Alt or Super held: if composing, commit current word first, then return not-handled so the shortcut works.
3. Letters/digits allowed by rules: append to buffer, recompute preview, update preedit. Handled.
4. SPACE, composing: commit `selected_candidate + " "` as ONE commit, clear state, hide preedit/lookup, handled. SPACE, not composing: not-handled (normal behavior). Never emit two spaces.
5. ENTER, composing: commit word, clear state, return NOT-handled so the app still receives Enter (decide and document; test no duplicate/lost Enter). ENTER, not composing: not-handled.
6. TAB: commit word, not-handled.
7. BACKSPACE, composing: remove last phonetic unit (define unit; re-derive preview from the buffer, never edit the preview text); if buffer becomes empty, end composition. BACKSPACE, not composing: not-handled — must never delete committed text through the engine.
8. ESCAPE, composing: discard composition (no commit), handled. Not composing: not-handled.
9. Punctuation (`, . ? ! ; : ' " ( )`): commit word first, then emit the mapped Bengali punctuation or pass through per the documented table; no duplicate characters.
10. Arrow/Home/End/PageUp/PageDown: commit current word, not-handled (when candidate lookup is visible, Up/Down/PageUp/PageDown navigate candidates and are handled).
11. Candidate selection: documented keys (e.g. Down/Up, Tab-cycle option, digits 1–9 when the lookup is open, mouse click via `do_candidate_clicked`).
12. `do_focus_out`, `do_reset`, `do_disable`: commit or discard per documented policy (default: commit pending word on focus-out only if the context is still valid; otherwise discard), clear state, never leak to another context. One engine instance per input context must not share mutable state.
13. Apps without preedit capability: define fallback (e.g. show candidates in lookup table only and commit on delimiter) and test it with `caps` without `CAP_PREEDIT_TEXT`.
14. Never simulate keystrokes, never synthesize Backspace to replace text. Use only `update_preedit_text` / `commit_text` / lookup table APIs.
15. Long input safety: cap buffer length; handle rapid repeated keys; idempotent clear.

---

## 5. SUGGESTIONS AND DICTIONARY

- Primary conversion + alternatives from rule ambiguity + dictionary matches, ranked deterministically (dictionary frequency, then rule priority).
- Offline only. No network code in the package. Add a test that fails if `socket`, `urllib`, `http`, `requests` are imported anywhere in `src/`.
- Dictionary: plain-text/TSV, with a documented license for every word source. Validate on load (valid Bengali, no control characters, size limit). Bundled word list must be license-clean; if no clean list is available, ship a small hand-made seed list and document how to expand.
- User dictionary: `$XDG_DATA_HOME/banglaflow/user.tsv`, created with mode 0600, learned words only after explicit opt-in, nothing logged.
- Never modify already-committed text. Candidate choice affects only the current composition.
- Do not market it as spelling correction.

---

## 6. IBUS ADAPTER

- Subclass `IBus.Engine`; register via `IBus.Factory` and the component XML as verified in Phase 0.
- Engine metadata: name `banglaflow`, longname `BanglaFlow`, description, language `bn`, layout `default`, icon, rank, symbol `বা` (or verified suitable), author, license, version from a single source of truth.
- Entry point handles: `--ibus` launch, exit when the IBus connection disconnects, clean `GLib.MainLoop` shutdown, missing-dependency error message to stderr with a non-zero exit code.
- Logging: use `logging`, default WARNING, to `$XDG_STATE_HOME`/journal; debug logs must NEVER contain typed text (log lengths, event types, state names only, test this).
- No runtime root, no network, no shell invocation, no `eval/exec` of any input.

---

## 7. PACKAGING (Debian)

- `debhelper-compat (= 13)` (or the version verified on the target release), `dh-python`, `pybuild`, `Build-Depends` verified with `apt-cache`. `Architecture: all`.
- `Depends`: `ibus`, `python3`, `python3-gi`, `gir1.2-ibus-1.0`, `gir1.2-glib-2.0` (or the verified equivalents), plus `${python3:Depends}`, `${misc:Depends}`. Fonts: recommend a Bengali font package (`fonts-noto-core` / verified name) via `Recommends`.
- Install: Python package to the dist-packages path, engine launcher to the verified libexec path, component XML to `/usr/share/ibus/component/`, icon(s), docs, dictionaries under `/usr/share/banglaflow/`.
- The component XML `<exec>` path must exactly match the installed launcher (add a test that parses the XML and asserts the path exists in the built package).
- Maintainer scripts: avoid unless necessary. No pip, no network, no per-user file edits, no forced `ibus restart` as root for all users. Document: log out/in or `ibus restart` as the user; adding the input source via Settings → Keyboard → Input Sources → Bengali → BanglaFlow.
- Clean removal and purge leave no files; upgrade tested (old → new version).
- Lintian: zero errors; warnings either fixed or justified in `lintian-overrides` with comments.
- Versioning: Debian format, e.g. `0.1.0-1`; PPA uploads use series-suffixed versions, e.g. `0.1.0-1~ppa1~noble1`, one upload per Ubuntu series.

---

## 8. BUILD AND VALIDATION SCRIPTS

`scripts/build-deb.sh` must, stopping on first failure (`set -euo pipefail`):
1. Validate tree (`check-tree.sh`: required files exist, XML well-formed, rule/dictionary validators pass).
2. Run unit + golden + property tests.
3. `dpkg-buildpackage -us -uc -b` (or `sbuild`/`pbuilder`/Docker `ubuntu:<release>` for a clean chroot).
4. Verify the `.deb` file exists. If not, the script fails.
5. `dpkg-deb -I`, `dpkg-deb -c`, `lintian`, dependency check, parse of the component XML from inside the package.
6. `scripts/test-install-container.sh`: in a disposable container/VM: install, verify `ibus` lists the engine, smoke-run the engine module, remove, purge, verify no leftover files, upgrade test.
7. Write all outputs to `docs/evidence/`.

Never mark success unless the `.deb` was produced and the checks above ran.

---

## 9. TEST SUITE

Unit (no IBus): phonetic rules, unicode validator, candidates, dictionary loader, config validation, state machine.
Golden corpus: `tests/golden/words.tsv` (minimum 500 word pairs at first release, growing), `sentences.tsv`, covering every rule category. Include code-point-level expectations. Include known-tricky words. Each regression bug adds a row.
Property-based (hypothesis): for any input made of allowed letters: no exception, output passes `validate_bengali`, deterministic, `convert(x)` never empty for non-empty valid input, appending then backspacing returns the earlier preview.
State-machine scenarios (table-driven): typing "ami␣" → exactly one commit `আমি `; "ami banglay likhi" → `আমি বাংলায় লিখি`; space with no composition → not-handled; double space; repeated release events; Enter/Escape/Backspace/punctuation sequences; focus-out/reset; mode toggle; candidate selection; no-preedit client; modifier shortcuts; rapid key bursts; isolation between two engine instances.
Adapter tests: `tests/fakes/` fake IBus API verifying exact call order and arguments (`commit_text` once, `hide_preedit_text` after commit, etc.).
Integration (separate, skippable markers `@integration`): real `ibus-daemon` in `dbus-run-session` + `Xvfb`, drive a GTK entry (and optionally a browser) with `xdotool`/IBus test client, assert the final text. Wayland-specific behavior: mark NOT RUN unless a real Wayland session was available.
Packaging tests: component XML validity, install-path consistency, lintian, autopkgtest (`debian/tests/`) for import + smoke.
Report separately: unit pass/fail counts, golden pass rate, property-test seeds, integration run/not-run.

---

## 10. SECURITY AND PRIVACY

No network, no telemetry, no typing history by default. Optional history/learning is off by default and explicit. Config and dictionary inputs are validated (type, size, encoding). Files created with minimal permissions. No `shell=True`. No dynamic code execution. Logs never contain typed content (tested). Engine failures must not crash the user's session: catch exceptions in key handlers, log a redacted message, reset state, and return not-handled so typing continues.

---

## 11. DISTRIBUTION

GitHub: README (features, supported releases as TESTED, install, remove, bug reporting template with env info), `CHANGELOG.md`, license, release notes, attach the `.deb` and its `SHA256SUMS` only after section 8 passed. Add a CI workflow (GitHub Actions on `ubuntu-*` runners) running tests and the build.
Launchpad PPA: valid `debian/changelog`, `debian/copyright` (DEP-5), source format `3.0 (quilt)` or `native` (decide and justify), signed source upload (`debuild -S -sa`, `dput ppa:<user>/<ppa> *_source.changes`), instructions to add the PPA (`add-apt-repository`, `apt update`, `apt install banglaflow`). Launchpad builds have no network access and build per series; confirm Build-Depends exist in that series. Do NOT upload, sign, or publish anything; stop and ask the user for their GPG key and Launchpad account. Explain the difference between a GitHub release, a PPA, and the official Ubuntu archive (including Debian→Ubuntu sync/sponsorship).

---

## 12. DEFINITION OF DONE (measurable gates)

All of these must be true and evidenced in `docs/evidence/`:
- [ ] All unit, golden, property and state-machine tests pass; golden pass rate 100% on the shipped corpus; zero known-failing tests hidden with skips (skips only for integration tests, each with a reason).
- [ ] `validate_bengali` passes on 100% of corpus outputs.
- [ ] SPACE commits one word plus one space exactly once; the next word starts fresh; committed text never touched (state-machine and adapter tests).
- [ ] `.deb` built, `lintian` has no errors, dependencies verified, install/remove/purge/upgrade tested in a clean environment, or explicitly NOT RUN with reason.
- [ ] Engine appears in `ibus` engine list in the test environment; typing in at least one real GTK app verified, or NOT RUN with reason.
- [ ] Network-free and no-typed-text-in-logs tests pass.
- [ ] Docs complete: installation, removal, architecture, testing, contributing, supported-environment table (Tested / Untested / Known-limited).

---

## 13. FINAL REPORT FORMAT

1. Environment (from `env.txt`).
2. Implemented features.
3. Tested features (with commands and counts).
4. Untested features (and why).
5. Known bugs and limitations (prioritized).
6. Artifacts: file tree, `.deb` path, checksums.
7. Actions requiring the user (GPG key, Launchpad account, GitHub credentials, real-desktop checks).
8. Next steps.

Never fabricate results, package contents, compatibility or publication status.
