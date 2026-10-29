"""Unit tests for Bengali Unicode validation."""

import pytest
from banglaflow.unicode_utils import validate_bengali, assert_valid_bengali


def test_valid_bengali_words():
    valid_samples = [
        "আমি",
        "বাংলা",
        "বাংলায়",
        "লিখি",
        "ভাষা",
        "আমার",
        "ক্ষমা",
        "বিজ্ঞান",
        "শান্তি",
        "সুন্দর",
        "সম্পর্ক",
        "র‍্যাপ",  # with ZWJ
        "বাংলাদেশ ১ ২ ৩ । ৳১০০",
    ]
    for sample in valid_samples:
        valid, reason = validate_bengali(sample)
        assert valid, f"Expected '{sample}' to be valid, but failed: {reason}"
        assert_valid_bengali(sample)


def test_dependent_vowel_at_start():
    # া (U+09BE) at start
    valid, reason = validate_bengali("\u09BE\u09AE\u09BF")
    assert not valid
    assert "start" in reason.lower()


def test_double_dependent_vowels():
    # ক + া + ি
    invalid_word = "\u0995\u09BE\u09BF"
    valid, reason = validate_bengali(invalid_word)
    assert not valid
    assert "double dependent vowels" in reason.lower()


def test_hasanta_at_start():
    invalid_word = "\u09CD\u0995"
    valid, reason = validate_bengali(invalid_word)
    assert not valid
    assert "start" in reason.lower()


def test_consecutive_hasanta():
    # ক + ্ + ্ + ত
    invalid_word = "\u0995\u09CD\u09CD\u09A4"
    valid, reason = validate_bengali(invalid_word)
    assert not valid
    assert "consecutive hasanta" in reason.lower()


def test_hasanta_after_independent_vowel():
    invalid_word = "\u0985\u09CD\u0995"
    valid, reason = validate_bengali(invalid_word)
    assert not valid
    assert "hasanta following independent vowel" in reason.lower()


def test_hasanta_after_dependent_vowel():
    # ক + া + ্
    invalid_word = "\u0995\u09BE\u09CD"
    valid, reason = validate_bengali(invalid_word)
    assert not valid
    assert "hasanta following dependent vowel" in reason.lower()


def test_stray_zwj():
    invalid_word = "\u200D\u0995"
    valid, reason = validate_bengali(invalid_word)
    assert not valid
    assert "stray" in reason.lower()


def test_nukta_misuse():
    # Nukta at start
    valid, reason = validate_bengali("\u09BC\u0995")
    assert not valid
    assert "nukta" in reason.lower()

    # Nukta after vowel
    valid, reason = validate_bengali("\u0986\u09BC")
    assert not valid
    assert "nukta" in reason.lower()


def test_modifier_at_start():
    # Anusvara (ং) at start
    valid, reason = validate_bengali("\u0982\u0995")
    assert not valid
    assert "modifier at string start" in reason.lower()


def test_assert_valid_bengali_raises():
    with pytest.raises(ValueError):
        assert_valid_bengali("\u09BE\u0995")

