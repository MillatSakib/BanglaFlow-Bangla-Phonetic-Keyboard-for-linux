"""Unit tests for config loading, validation, and defaults."""

from banglaflow.config import BanglaFlowConfig, validate_config_dict, load_config, save_config


def test_default_config():
    config = BanglaFlowConfig()
    assert config.mode == "bengali"
    assert config.map_dari is True
    assert config.bengali_digits is True
    assert config.learn_words is False
    assert config.page_size == 5


def test_validate_config_dict_valid():
    custom = {
        "mode": "english",
        "map_dari": False,
        "bengali_digits": True,
        "max_buffer_len": 128,
        "learn_words": True,
        "show_candidate_lookup": False,
        "page_size": 7,
    }
    cfg = validate_config_dict(custom)
    assert cfg.mode == "english"
    assert cfg.map_dari is False
    assert cfg.bengali_digits is True
    assert cfg.max_buffer_len == 128
    assert cfg.learn_words is True
    assert cfg.show_candidate_lookup is False
    assert cfg.page_size == 7


def test_validate_config_dict_invalid_values_revert_to_default():
    bad = {
        "mode": "invalid_mode",
        "page_size": 999,  # out of bounds
        "max_buffer_len": -1,  # out of bounds
        "map_dari": "not_a_bool",
    }
    cfg = validate_config_dict(bad)
    assert cfg.mode == "bengali"
    assert cfg.page_size == 5
    assert cfg.max_buffer_len == 64
    assert cfg.map_dari is True


def test_save_and_load_config(tmp_path):
    cfg_file = tmp_path / "config.json"
    cfg = BanglaFlowConfig(page_size=8, bengali_digits=True)
    assert save_config(cfg, cfg_file)

    loaded = load_config(cfg_file)
    assert loaded.page_size == 8
    assert loaded.bengali_digits is True

