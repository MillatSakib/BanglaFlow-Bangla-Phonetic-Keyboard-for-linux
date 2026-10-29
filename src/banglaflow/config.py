"""XDG configuration loader and validator for BanglaFlow.

Strict validation of types and values, fallback to safe defaults,
and persistence to $XDG_CONFIG_HOME/banglaflow/config.json.
"""

import json
import os
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict


@dataclass
class BanglaFlowConfig:
    mode: str = "bengali"  # "bengali" or "english"
    map_dari: bool = True  # '.' -> '।'
    bengali_digits: bool = False  # 0-9 -> ০-৯
    max_buffer_len: int = 64
    learn_words: bool = False  # Explicit opt-in only
    show_candidate_lookup: bool = True
    page_size: int = 5


def get_config_path() -> Path:
    """Return standard XDG config file path."""
    xdg_config = os.environ.get("XDG_CONFIG_HOME")
    if xdg_config:
        base_dir = Path(xdg_config) / "banglaflow"
    else:
        base_dir = Path.home() / ".config" / "banglaflow"
    return base_dir / "config.json"


def validate_config_dict(data: Dict[str, Any]) -> BanglaFlowConfig:
    """Validate dictionary against schema and return a BanglaFlowConfig instance."""
    config = BanglaFlowConfig()

    if not isinstance(data, dict):
        return config

    if "mode" in data and data["mode"] in ("bengali", "english"):
        config.mode = data["mode"]

    if "map_dari" in data and isinstance(data["map_dari"], bool):
        config.map_dari = data["map_dari"]

    if "bengali_digits" in data and isinstance(data["bengali_digits"], bool):
        config.bengali_digits = data["bengali_digits"]

    if "max_buffer_len" in data and isinstance(data["max_buffer_len"], int):
        if 8 <= data["max_buffer_len"] <= 256:
            config.max_buffer_len = data["max_buffer_len"]

    if "learn_words" in data and isinstance(data["learn_words"], bool):
        config.learn_words = data["learn_words"]

    if "show_candidate_lookup" in data and isinstance(data["show_candidate_lookup"], bool):
        config.show_candidate_lookup = data["show_candidate_lookup"]

    if "page_size" in data and isinstance(data["page_size"], int):
        if 1 <= data["page_size"] <= 10:
            config.page_size = data["page_size"]

    return config


def load_config(path: Path | None = None) -> BanglaFlowConfig:
    """Load configuration from path or default XDG location."""
    if path is None:
        path = get_config_path()

    if not path.exists():
        return BanglaFlowConfig()

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return validate_config_dict(data)
    except Exception:
        # Fall back safely to default config on corrupted file
        return BanglaFlowConfig()


def save_config(config: BanglaFlowConfig, path: Path | None = None) -> bool:
    """Save configuration to path or default XDG location with secure permissions."""
    if path is None:
        path = get_config_path()

    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        data = asdict(config)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        return True
    except OSError:
        return False

