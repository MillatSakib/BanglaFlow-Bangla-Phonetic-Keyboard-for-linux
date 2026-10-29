"""Process entry point for BanglaFlow IBus engine."""

import argparse
import logging
import os
import sys
from pathlib import Path

# Verify dependencies before importing GI
try:
    import gi

    gi.require_version("IBus", "1.0")
    from gi.repository import GLib, GObject, IBus
except Exception as exc:
    sys.stderr.write(
        f"BanglaFlow Error: Missing required system dependencies (python3-gi, gir1.2-ibus-1.0): {exc}\n"
    )
    sys.exit(1)

from banglaflow import __version__
from banglaflow.engine import BanglaFlowEngine

# Configure logging: default WARNING to XDG_STATE_HOME or journal
xdg_state = os.environ.get("XDG_STATE_HOME")
if xdg_state:
    log_dir = Path(xdg_state) / "banglaflow"
else:
    log_dir = Path.home() / ".local" / "state" / "banglaflow"

log_dir.mkdir(parents=True, exist_ok=True)
log_file = log_dir / "engine.log"

logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.FileHandler(str(log_file), encoding="utf-8")],
)
logger = logging.getLogger("banglaflow.main")


def main():
    parser = argparse.ArgumentParser(description="BanglaFlow IBus Engine")
    parser.add_argument("--ibus", action="store_true", help="Executed by IBus daemon")
    parser.add_argument("--version", action="version", version=f"BanglaFlow {__version__}")
    args = parser.parse_args()

    IBus.init()
    bus = IBus.Bus()

    if not bus.is_connected():
        sys.stderr.write("BanglaFlow Error: Cannot connect to IBus daemon.\n")
        sys.exit(1)

    loop = GLib.MainLoop()

    # Disconnect handler
    def on_disconnected(bus_obj):
        logger.warning("IBus daemon disconnected. Terminating.")
        loop.quit()

    bus.connect("disconnected", on_disconnected)

    # Register Factory and Engine
    engine_type = GObject.type_from_name("BanglaFlowEngine")
    if not engine_type:
        # Register type explicitly if needed
        engine_type = BanglaFlowEngine.__gtype__

    factory = IBus.Factory.new(bus.get_connection())
    factory.add_engine("banglaflow", engine_type)

    if args.ibus:
        bus.request_name("org.freedesktop.IBus.BanglaFlow", 0)

    try:
        loop.run()
    except (KeyboardInterrupt, SystemExit):
        pass
    finally:
        loop.quit()


if __name__ == "__main__":
    main()

