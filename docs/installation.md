# BanglaFlow Installation & Setup Guide

## Requirements
- Operating System: Ubuntu 24.04 LTS / 26.04 LTS (or compatible Debian-based distribution).
- Desktop Environment: GNOME on Wayland or X11.
- Framework: IBus (`ibus`, `python3-gi`, `gir1.2-ibus-1.0`).

---

## 1. Installation via .deb Package

```bash
# Install the built package
sudo dpkg -i banglaflow_0.1.0-1_all.deb

# If any dependencies are missing, fix automatically:
sudo apt-get install -f
```

---

## 2. Enabling BanglaFlow in GNOME

1. Restart the user IBus daemon to register new components:
   ```bash
   ibus restart
   ```
2. Open **Settings** → **Keyboard**.
3. Under **Input Sources**, click **Add (+)**.
4. Click the three vertical dots (**...**) to expand all languages.
5. Search for **Bengali** (or **Bangla**).
6. Select **BanglaFlow** and click **Add**.

---

## 3. Switching and Typing

- Use **Super + Space** (or **Shift + Space**) to switch between English and BanglaFlow.
- When active, the system tray icon displays `বা`.
- Type phonetic Bengali (e.g. `ami bangla likhi` → `আমি বাংলা লিখি`).
- Press **Down Arrow** to navigate suggestions, or press **1–9** to select directly.
- Press **Space** or **Enter** to commit the active word.

---

## 4. Removal & Purge

To remove:
```bash
sudo dpkg -r banglaflow
```

To purge all configuration and shared files:
```bash
sudo dpkg -P banglaflow
```
User-learned dictionaries stored under `~/.local/share/banglaflow/` can be deleted manually if desired.

