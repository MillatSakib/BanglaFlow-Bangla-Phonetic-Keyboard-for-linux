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


def test_candidates_bhasha_ranks_dictionary_match():
    engine = PhoneticEngine()
    dict_mgr = BengaliDictionary()
    generator = CandidateGenerator(engine, dict_mgr)

    cands = generator.generate_candidates("bhasha")
    assert len(cands) >= 2
    # Primary conversion is in edit panel at index 0, followed by dictionary matches
    assert cands[0] == "ভাশা"
    assert "ভাষা" in cands


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


def test_candidates_s_and_S():
    """User requirement: typing 's' must give 'স', typing 'S' must give 'শ', typing 'Sh' must give 'ষ'."""
    engine = PhoneticEngine()
    dict_mgr = BengaliDictionary()
    generator = CandidateGenerator(engine, dict_mgr)

    cands_s = generator.generate_candidates("s")
    assert cands_s[0] == "স"
    assert "শ" in cands_s
    assert "ষ" in cands_s

    cands_S = generator.generate_candidates("S")
    assert cands_S[0] == "শ"
    assert "স" in cands_S
    assert "ষ" in cands_S

    cands_Sh = generator.generate_candidates("Sh")
    assert cands_Sh[0] == "ষ"
    assert "শ" in cands_Sh
    assert "স" in cands_Sh


def test_candidates_chad_chondrobindhu():
    engine = PhoneticEngine()
    dict_mgr = BengaliDictionary()
    generator = CandidateGenerator(engine, dict_mgr)

    cands = generator.generate_candidates("chad")
    assert len(cands) >= 2
    # Direct conversion in edit panel, followed by chandrabindu suggestion
    assert cands[0] == "ছাদ"
    assert "চাঁদ" in cands


def test_candidates_chadmukh_and_prefix():
    engine = PhoneticEngine()
    dict_mgr = BengaliDictionary()
    generator = CandidateGenerator(engine, dict_mgr)

    cands_full = generator.generate_candidates("chadmukh")
    assert cands_full[0] == "ছাদ্মুখ"
    assert "চাঁদমুখ" in cands_full

    # User requirement: typing prefix of longer word must suggest word
    cands_prefix = generator.generate_candidates("chadm")
    assert "চাঁদমুখ" in cands_prefix


def test_candidates_prefix_completion():
    engine = PhoneticEngine()
    dict_mgr = BengaliDictionary()
    generator = CandidateGenerator(engine, dict_mgr)

    cands = generator.generate_candidates("bangl")
    assert "বাংলা" in cands
    assert "বাংলাদেশ" in cands


