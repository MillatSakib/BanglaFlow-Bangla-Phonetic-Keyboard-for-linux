# Supported Environment Matrix

| Environment / Application | Status | Notes / Limitations |
| :--- | :--- | :--- |
| **Ubuntu 26.04 LTS (resolute)** | **Tested** | Native host test environment; GNOME Wayland; Python 3.14 + IBus 1.5.34. |
| **Ubuntu 24.04 LTS (noble)** | **Tested** | Clean Docker container verified; package installs, upgrades, and purges cleanly. |
| **GNOME Shell Integration** | **Tested** | Component XML registered; engine recognised in IBus engine registry. |
| **GTK 3 / GTK 4 Applications** | **Tested** | Native IBus text-input protocol supported. |
| **Terminal (GNOME Terminal)** | **Tested** | Supported via standard IBus terminal preedit. |
| **Chromium / Google Chrome** | **Tested** | Requires standard Wayland IME flag (`--enable-wayland-ime` or `--ozone-platform=wayland`). |
| **VS Code / Electron** | **Tested** | Standard Electron Wayland flags (`--enable-wayland-ime`) recommended on Wayland. |
| **KDE Plasma / Qt Applications** | **Untested** | Expected to work via `ibus-qt` / Qt IM module; not verified on host. |
| **XWayland Legacy Apps** | **Tested** | Uses standard XIM / GTK IM module bridging. |
| **Flatpak / Snap Sandboxes** | **Untested** | Requires standard IBus socket portal permissions in sandbox profiles. |

