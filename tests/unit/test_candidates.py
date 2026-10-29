"""Unit tests for candidate generation and deterministic ranking."""

from banglaflow.phonetic import PhoneticEngine
from banglaflow.dictionary import BengaliDictionary
from banglaflow.candidates import CandidateGenerator


def test_candidates_ami():
    engine = PhoneticEngine()
    dict_mgr = BengaliDictionary()
    generator = CandidateGenerator(engine, dict_mgr)

    cands = generator.generate_candidates("ami")
    assert len(cands) >= 1
    assert cands[0] == "আমি"


def test_candidates_bhasha_ranks_dictionary_match_first():
    engine = PhoneticEngine()
    dict_mgr = BengaliDictionary()
    generator = CandidateGenerator(engine, dict_mgr)

    cands = generator.generate_candidates("bhasha")
    assert len(cands) >= 2
    # Even though pure rule produces ভাশা, dictionary has ভাষা which must rank #1
    assert cands[0] == "ভাষা"
    assert "ভাশা" in cands


def test_candidates_bangla():
    engine = PhoneticEngine()
    dict_mgr = BengaliDictionary()
    generator = CandidateGenerator(engine, dict_mgr)

    cands = generator.generate_candidates("bangla")
    assert cands[0] == "বাংলা"


def test_deterministic_order():
    engine = PhoneticEngine()
    dict_mgr = BengaliDictionary()
    generator = CandidateGenerator(engine, dict_mgr)

    cands1 = generator.generate_candidates("shonar")
    cands2 = generator.generate_candidates("shonar")
    assert cands1 == cands2

