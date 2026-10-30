# BanglaFlow (বাংলাফ্লো)

Native Bengali phonetic input method for Linux (IBus).

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](LICENSE)
[![Platform: Linux / Ubuntu](https://img.shields.io/badge/Platform-Ubuntu%2024.04%20%7C%2026.04-orange.svg)]()
[![IBus: 1.5+](https://img.shields.io/badge/IBus-1.5%2B-green.svg)]()

BanglaFlow is a native, lightweight, and system-wide Bengali phonetic input method designed specifically for Linux desktop environments (GNOME Wayland/X11). It provides accurate Banglish-to-Bengali conversion directly within any application without background key-sniffing daemons or simulated backspace hacks.

---

## Features

- **Longest-Match Phonetic Tokenizer**: High-precision context-aware parsing of phonetic rules (e.g. `ami` → `আমি`, `bangla` → `বাংলা`, `banglay` → `বাংলায়`, `bhaSha` → `ভাষা`).
- **Pure-Python Architecture**: Completely decoupled text-processing engine, state machine, and dictionary with zero GUI dependencies in the core.
- **Strict Bengali Unicode Compliance**: Enforces logical code point order without blind normalization (preserves precomposed `ড়`, `ঢ়`, `য়`).
- **Interactive Preedit & Suggestions**: Native underline preedit with frequency-ranked candidate lookup table.
- **Offline & Privacy-First**: Zero network calls, zero telemetry, zero typed keystrokes in logs.
- **Atomic Commits**: Single-press Space and Enter commit candidate words cleanly without duplicate spaces or characters.

---

## Supported Environments

| Environment | Release | Status |
| :--- | :--- | :--- |
| **Ubuntu Desktop** | 26.04 LTS (resolute) | **TESTED** |
| **Ubuntu Desktop** | 24.04 LTS (noble) | **TESTED** |
| **GNOME Shell (Wayland)** | Default Ubuntu session | **TESTED** |
| **GNOME Shell (X11)** | X11 fallback session | **TESTED** |
| **GTK 3 / GTK 4 Apps** | Native Linux apps | **TESTED** |
| **Web Browsers** | Chrome / Chromium / Firefox | **TESTED** |

---

## Installation

### 1. Via Ubuntu PPA (Recommended for Ubuntu & Debian)

The easiest and official way to install and receive automatic updates on Ubuntu:

```bash
# Add official BanglaFlow PPA
sudo add-apt-repository ppa:kovenceit/banglaflow
sudo apt update

# Install BanglaFlow and restart IBus
sudo apt install banglaflow
ibus restart
```

---

### 2. Via Canonical Snap Store (Universal Linux)

Available across all Snap-supported distributions (Ubuntu, Debian, Fedora, Arch, Manjaro):

```bash
sudo snap install --classic banglaflow
ibus restart
```

---

### 3. From Debian Package (.deb)

Download the latest `.deb` release directly from [GitHub Releases](https://github.com/MillatSakib/BanglaFlow-Bangla-Phonetic-Keyboard-for-linux/releases/latest) or install locally:

```bash
sudo dpkg -i banglaflow_1.0.1.deb
sudo apt-get install -f
ibus restart
```

---

### 4. Build from Source

Compile and install directly from the git repository:

```bash
git clone https://github.com/MillatSakib/BanglaFlow-Bangla-Phonetic-Keyboard-for-linux.git
cd BanglaFlow-Bangla-Phonetic-Keyboard-for-linux
bash scripts/build-deb.sh
sudo dpkg -i banglaflow.deb
ibus restart
```

---

### Enable in GNOME Desktop

After installing via any of the methods above:

1. Open **Settings** → **Keyboard** → **Input Sources**.
2. Click **Add (+)** → Select **Bengali**.
3. Choose **BanglaFlow** (marked with the `bn` indicator).
4. Switch to Bengali typing using <kbd>Super</kbd> + <kbd>Space</kbd> or <kbd>Ctrl</kbd> + <kbd>Space</kbd>.

---

## Phonetic Typing Reference Guide

Complete reference map for all Bengali vowels (স্বরবর্ণ), consonants (ব্যঞ্জনবর্ণ), vowel signs/kar (কার), conjuncts (যুক্তাক্ষর), digits (সংখ্যা), and punctuation:

![BanglaFlow Character & Keyboard Mapping Guide](docs/images/banglaflow-keyboard-layout.png)

### Quick Reference & Examples

| English Input | Bengali Output | Notes |
| :--- | :--- | :--- |
| `ami` | `আমি` | Basic vowel + consonant |
| `bangla` | `বাংলা` | Anusvara (`ng` → `ং`) |
| `banglay` | `বাংলায়` | Precomposed `য়` (`U+09DF`) |
| `likhi` | `লিখি` | Dependent vowel signs |
| `bhaSha` | `ভাষা` | Retroflex `ষ` |
| `amar` | `আমার` | Independent `আ` |
| `torrko` | `তর্ক` | Reph (`rr` before consonant) |
| `brriShTi` | `বৃষ্টি` | Ri-kar (`rri`) + conjunct |
| `Taka $500.` | `টাকা ৳৫০০।` | Auto currency (`৳`) and Dari (`।`) |

---

## Uninstallation

To remove:
```bash
sudo dpkg -r banglaflow
```

To purge all files:
```bash
sudo dpkg -P banglaflow
```

---

## Bug Reporting Template

When reporting an issue, please include the following environment details:

```text
=== System Info ===
OS: $(lsb_release -d)
Desktop: $XDG_CURRENT_DESKTOP ($XDG_SESSION_TYPE)
IBus Version: $(ibus version)
Python: $(python3 --version)
BanglaFlow Version: 1.0.1

=== Issue Description ===
Input string: [e.g. "somporrko"]
Expected output: [e.g. "সম্পর্ক"]
Actual output: [e.g. "সম্পরক"]
Application: [e.g. GNOME Text Editor / Chrome / Terminal]
```

---

## License

BanglaFlow is licensed under the [GNU General Public License v3.0](LICENSE).
Phonetic rule tables derived from OmicronLab under MPL-2.0.
Dictionary wordlists derived from LibreOffice under MPL-2.0 / LGPL-3.0.

