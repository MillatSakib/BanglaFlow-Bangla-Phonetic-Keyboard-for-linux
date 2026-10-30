# Changelog

All notable changes to BanglaFlow will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.1] - 2026-10-30

### Fixed
- Number keys 0-9 unconditionally type Bengali/English digits instead of selecting candidates.
- Candidate selection dedicated to Arrow keys (Up/Down) and Tab.
- Mouse click triggers clean word commit without erasing newly typed words upon Space in Chrome and GTK.
- Engine symbol set to 'bn' for clean GNOME Shell top panel indicator.
- Bisarga colon (:) handling in phonetic engine.
- Official GNU General Public License v3.0 added.

## [1.0.0] - 2026-10-30

### Added
- Official 1.0.0 Stable Release with full Avro Phonetic compatibility.

## [0.1.0] - 2026-10-29

### Added
- Longest-match, context-aware Bengali phonetic engine based on verified rule tables.
- Pure-Python key-event state machine with preedit text, candidate lookup, and delimiter handling.
- Strict Bengali Unicode validation checking logical code point ordering without blind normalization.
- Offline frequency-ranked dictionary with 3,000+ validated Bengali words.
- Secure user dictionary ($XDG_DATA_HOME/banglaflow/user.tsv) with 0600 file permissions.
- IBus engine adapter registering `org.freedesktop.IBus.BanglaFlow` with zero typed text in logs.
- Comprehensive test suite: unit, golden corpus (714 words, sentences, regressions), and Hypothesis property tests.
- Debian packaging and build automation scripts for Ubuntu 26.04+ (resolute).

