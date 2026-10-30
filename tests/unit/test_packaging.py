"""Tests validating packaging metadata, XML validity, and file layout consistency."""

import os
import xml.etree.ElementTree as ET
from pathlib import Path
from banglaflow import __version__

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


def test_component_xml_validity():
    xml_path = PROJECT_ROOT / "data" / "ibus" / "banglaflow.xml"
    assert xml_path.exists(), f"Component XML missing at {xml_path}"

    tree = ET.parse(xml_path)
    root = tree.getroot()
    assert root.tag == "component"

    name = root.findtext("name")
    assert name == "org.freedesktop.IBus.BanglaFlow"

    exec_cmd = root.findtext("exec")
    assert exec_cmd == "/usr/libexec/ibus-engine-banglaflow --ibus"

    version = root.findtext("version")
    assert version == __version__

    engines = root.find("engines")
    assert engines is not None
    engine = engines.find("engine")
    assert engine is not None
    assert engine.findtext("name") == "banglaflow"
    assert engine.findtext("language") == "bn"
    assert engine.findtext("symbol") == "bn"


def test_launcher_executable():
    launcher_path = PROJECT_ROOT / "src" / "ibus-engine-banglaflow"
    assert launcher_path.exists()
    assert os.access(launcher_path, os.X_OK), "Launcher script must be executable"

