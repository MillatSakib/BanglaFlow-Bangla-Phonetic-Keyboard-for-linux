"""Tests against the golden and regression corpora."""

from pathlib import Path
from banglaflow.phonetic import PhoneticEngine
from banglaflow.unicode_utils import validate_bengali

GOLDEN_DIR = Path(__file__).resolve().parent.parent / "golden"


def load_tsv_corpus(file_name: str):
    file_path = GOLDEN_DIR / file_name
    assert file_path.exists(), f"Corpus file not found: {file_path}"
    pairs = []
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split("\t")
            if len(parts) >= 2:
                pairs.append((parts[0], parts[1]))
    return pairs


def test_golden_words_pass_rate():
    engine = PhoneticEngine(map_dari=True)
    pairs = load_tsv_corpus("words.tsv")
    assert len(pairs) >= 500, f"Expected at least 500 word pairs, got {len(pairs)}"

    passed = 0
    failures = []

    for lat, expected in pairs:
        actual = engine.convert(lat)
        valid, reason = validate_bengali(actual)
        assert valid, f"Output '{actual}' for input '{lat}' failed Bengali validation: {reason}"

        if actual == expected:
            passed += 1
        else:
            failures.append((lat, expected, actual))

    pass_rate = (passed / len(pairs)) * 100.0
    if failures:
        sample_fail = failures[:5]
        assert False, f"Golden words pass rate {pass_rate:.2f}% ({passed}/{len(pairs)}). Failures: {sample_fail}"

    assert pass_rate == 100.0


def test_golden_sentences_pass_rate():
    engine = PhoneticEngine(map_dari=True)
    pairs = load_tsv_corpus("sentences.tsv")
    assert len(pairs) >= 5

    for lat, expected in pairs:
        actual = engine.convert(lat)
        valid, reason = validate_bengali(actual)
        assert valid, f"Output '{actual}' for sentence '{lat}' failed validation: {reason}"
        assert actual == expected, f"Sentence mismatch: input='{lat}', expected='{expected}', got='{actual}'"


def test_regression_corpus():
    engine = PhoneticEngine(map_dari=True)
    pairs = load_tsv_corpus("regression.tsv")
    assert len(pairs) >= 10

    for lat, expected in pairs:
        actual = engine.convert(lat)
        valid, reason = validate_bengali(actual)
        assert valid, f"Output '{actual}' for regression '{lat}' failed validation: {reason}"
        assert actual == expected, f"Regression mismatch: input='{lat}', expected='{expected}', got='{actual}'"

