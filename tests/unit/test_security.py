"""Security and privacy compliance tests."""

import ast
import logging
from pathlib import Path

SRC_DIR = Path(__file__).resolve().parent.parent.parent / "src" / "banglaflow"


def test_no_network_imports():
    """Verify that no network modules are imported anywhere in src/banglaflow."""
    forbidden_modules = {
        "socket",
        "urllib",
        "urllib.request",
        "http",
        "http.client",
        "requests",
        "aiohttp",
        "httpx",
        "ftplib",
        "telnetlib",
    }

    for py_file in SRC_DIR.glob("*.py"):
        with open(py_file, "r", encoding="utf-8") as f:
            tree = ast.parse(f.read(), filename=str(py_file))

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    assert alias.name not in forbidden_modules, (
                        f"Forbidden network module '{alias.name}' imported in {py_file.name}"
                    )
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    assert node.module not in forbidden_modules, (
                        f"Forbidden network module '{node.module}' imported in {py_file.name}"
                    )
                    top_mod = node.module.split(".")[0]
                    assert top_mod not in forbidden_modules, (
                        f"Forbidden network module '{top_mod}' imported in {py_file.name}"
                    )


def test_strict_gi_isolation():
    """Verify that pure logic modules never import gi or IBus."""
    pure_modules = [
        "phonetic.py",
        "state.py",
        "rules.py",
        "unicode_utils.py",
        "candidates.py",
        "dictionary.py",
        "config.py",
    ]

    for mod_name in pure_modules:
        file_path = SRC_DIR / mod_name
        assert file_path.exists(), f"File {file_path} must exist"
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        tree = ast.parse(content, filename=str(file_path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    assert alias.name != "gi", f"{mod_name} must never import 'gi'"
            elif isinstance(node, ast.ImportFrom):
                assert node.module != "gi", f"{mod_name} must never import from 'gi'"


def test_no_typed_text_in_logs(caplog):
    """Verify that debug logs never leak typed keys or Bengali output text."""
    from banglaflow.engine import BanglaFlowEngine

    engine = BanglaFlowEngine()
    sensitive_word = "SuperSecretPassword123"

    with caplog.at_level(logging.DEBUG, logger="banglaflow.engine"):
        for c in sensitive_word:
            engine.do_process_key_event(ord(c), 0, 0)
        engine.do_process_key_event(32, 0, 0)  # SPACE

    for record in caplog.records:
        msg = record.getMessage()
        # Verify typed text is absent
        assert sensitive_word not in msg
        assert "SuperSecret" not in msg
        assert "Password" not in msg

