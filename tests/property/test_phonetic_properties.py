"""Hypothesis-based property testing for BanglaFlow phonetic engine and state machine."""

from hypothesis import given, settings, strategies as st
from banglaflow.phonetic import PhoneticEngine
from banglaflow.unicode_utils import validate_bengali
from banglaflow.state import InputStateMachine, KEY_BACKSPACE
from banglaflow.candidates import CandidateGenerator
from banglaflow.dictionary import BengaliDictionary
from banglaflow.config import BanglaFlowConfig


# Allowed alphabet letters used in phonetic input
allowed_letters = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"

engine = PhoneticEngine()
dictionary = BengaliDictionary()
candidate_gen = CandidateGenerator(engine, dictionary)


@given(st.text(alphabet=allowed_letters, min_size=1, max_size=30))
@settings(max_examples=100)
def test_phonetic_engine_properties(text: str):
    # 1. No exceptions
    res1 = engine.convert(text)
    res2 = engine.convert(text)

    # 2. Determinism
    assert res1 == res2

    # 3. Non-empty output for non-empty valid letter input
    assert len(res1) > 0

    # 4. Bengali Unicode validity
    valid, reason = validate_bengali(res1)
    assert valid, f"Output '{res1}' for input '{text}' failed validation: {reason}"


@given(
    st.text(alphabet="abcdefghijklmnopqrstuvwxyz", min_size=1, max_size=15),
    st.characters(whitelist_categories=("Ll", "Lu")),
)
@settings(max_examples=50, deadline=None)
def test_state_machine_backspace_reverts_preview(initial_text: str, extra_char: str):
    sm = InputStateMachine(engine, candidate_gen, BanglaFlowConfig())

    # Type initial string
    for c in initial_text:
        sm.process_key_event(ord(c), 0, 0, is_release=False)
    preview_before = sm.bengali_preview

    # Type extra character
    sm.process_key_event(ord(extra_char), 0, 0, is_release=False)

    # Press Backspace
    sm.process_key_event(KEY_BACKSPACE, 0, 0, is_release=False)
    preview_after = sm.bengali_preview

    # Preview after backspace must match preview before
    assert preview_after == preview_before
