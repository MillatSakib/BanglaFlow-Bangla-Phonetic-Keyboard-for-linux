"""Comprehensive unit tests for the pure key-event state machine.

Covers all 15 rules defined in Section 4 of the BanglaFlow Specification.
"""

from banglaflow.candidates import CandidateGenerator
from banglaflow.config import BanglaFlowConfig
from banglaflow.dictionary import BengaliDictionary
from banglaflow.phonetic import PhoneticEngine
from banglaflow.state import (
    Commit,
    HideLookup,
    HidePreedit,
    InputStateMachine,
    KEY_BACKSPACE,
    KEY_DOWN,
    KEY_ESCAPE,
    KEY_RETURN,
    KEY_SPACE,
    KEY_TAB,
    KEY_UP,
    MOD_ALT,
    MOD_CONTROL,
    MOD_RELEASE,
    MOD_SUPER,
    UpdateLookup,
    UpdatePreedit,
)


def make_state_machine() -> InputStateMachine:
    engine = PhoneticEngine()
    dictionary = BengaliDictionary()
    candidates = CandidateGenerator(engine, dictionary)
    config = BanglaFlowConfig()
    return InputStateMachine(engine, candidates, config)


def type_string(sm: InputStateMachine, text: str):
    """Helper to simulate typing a string into the state machine."""
    last_handled = False
    all_actions = []
    for c in text:
        handled, actions = sm.process_key_event(ord(c), 0, 0, is_release=False)
        last_handled = handled
        all_actions.extend(actions)
    return last_handled, all_actions


def test_rule_1_release_events_ignored():
    sm = make_state_machine()
    handled, actions = sm.process_key_event(ord("a"), 0, 0, is_release=True)
    assert not handled
    assert actions == []

    handled, actions = sm.process_key_event(ord("a"), 0, MOD_RELEASE, is_release=False)
    assert not handled
    assert actions == []


def test_rule_2_shortcuts_commit_first_and_pass_through():
    sm = make_state_machine()
    type_string(sm, "ami")
    assert sm.composing

    # Press Ctrl+C
    handled, actions = sm.process_key_event(ord("c"), 0, MOD_CONTROL, is_release=False)
    assert not handled  # Shortcut must pass through to app
    assert any(isinstance(a, Commit) and "আমি" in a.text for a in actions)
    assert not sm.composing


def test_rule_3_typing_letters_updates_preedit():
    sm = make_state_machine()
    handled, actions = type_string(sm, "ami")
    assert handled
    assert sm.composing
    assert sm.bengali_preview == "আমি"
    assert any(isinstance(a, UpdatePreedit) and a.text == "আমি" for a in actions)


def test_rule_4_space_composing_commits_word_plus_single_space():
    sm = make_state_machine()
    type_string(sm, "ami")
    handled, actions = sm.process_key_event(KEY_SPACE, 0, 0, is_release=False)

    assert handled
    assert not sm.composing
    # Must commit "আমি " as ONE commit
    commits = [a.text for a in actions if isinstance(a, Commit)]
    assert commits == ["আমি "]


def test_rule_4_space_not_composing_not_handled():
    sm = make_state_machine()
    handled, actions = sm.process_key_event(KEY_SPACE, 0, 0, is_release=False)
    assert not handled
    assert actions == []


def test_rule_5_enter_composing_commits_and_returns_not_handled():
    sm = make_state_machine()
    type_string(sm, "ami")
    handled, actions = sm.process_key_event(KEY_RETURN, 0, 0, is_release=False)

    # Handled must be FALSE so app still receives Enter
    assert not handled
    assert not sm.composing
    commits = [a.text for a in actions if isinstance(a, Commit)]
    assert commits == ["আমি"]


def test_rule_6_tab_composing_commits_and_returns_not_handled():
    sm = make_state_machine()
    type_string(sm, "ami")
    handled, actions = sm.process_key_event(KEY_TAB, 0, 0, is_release=False)

    assert not handled
    assert not sm.composing
    commits = [a.text for a in actions if isinstance(a, Commit)]
    assert commits == ["আমি"]


def test_rule_7_backspace_composing():
    sm = make_state_machine()
    type_string(sm, "ami")
    assert sm.phonetic_buffer == "ami"

    # Backspace once -> "am"
    handled, actions = sm.process_key_event(KEY_BACKSPACE, 0, 0, is_release=False)
    assert handled
    assert sm.composing
    assert sm.phonetic_buffer == "am"

    # Backspace twice more -> empty
    sm.process_key_event(KEY_BACKSPACE, 0, 0, is_release=False)
    handled, actions = sm.process_key_event(KEY_BACKSPACE, 0, 0, is_release=False)
    assert handled
    assert not sm.composing
    assert sm.phonetic_buffer == ""
    assert any(isinstance(a, HidePreedit) for a in actions)


def test_rule_7_backspace_not_composing_not_handled():
    sm = make_state_machine()
    handled, actions = sm.process_key_event(KEY_BACKSPACE, 0, 0, is_release=False)
    assert not handled
    assert actions == []


def test_rule_8_escape_composing_discards_without_commit():
    sm = make_state_machine()
    type_string(sm, "ami")
    handled, actions = sm.process_key_event(KEY_ESCAPE, 0, 0, is_release=False)

    assert handled
    assert not sm.composing
    assert not any(isinstance(a, Commit) for a in actions)
    assert any(isinstance(a, HidePreedit) for a in actions)


def test_rule_9_punctuation_commits_word_and_mapped_dari():
    sm = make_state_machine()
    type_string(sm, "ami")
    # Type '.'
    handled, actions = sm.process_key_event(ord("."), 0, 0, is_release=False)
    assert handled
    commits = [a.text for a in actions if isinstance(a, Commit)]
    # Must commit "আমি।" as a single atomic commit so word is never erased
    assert commits == ["আমি\u0964"]
    assert not sm.composing


def test_rule_9_unmapped_punctuation_passes_through_cleanly():
    sm = make_state_machine()
    type_string(sm, "ami")
    # Type '?'
    handled, actions = sm.process_key_event(ord("?"), 0, 0, is_release=False)
    # Unmapped punctuation: handled is False so app inserts '?' without double emission
    assert not handled
    commits = [a.text for a in actions if isinstance(a, Commit)]
    assert commits == ["আমি"]


def test_rule_10_and_11_candidate_navigation_and_selection():
    sm = make_state_machine()
    type_string(sm, "bhasha")
    assert sm.lookup_visible
    assert len(sm.candidates) >= 2
    initial_idx = sm.selected_index
    assert initial_idx == 0

    # Down arrow navigates
    handled, actions = sm.process_key_event(KEY_DOWN, 0, 0, is_release=False)
    assert handled
    assert sm.selected_index == 1
    assert any(isinstance(a, UpdateLookup) and a.selected_index == 1 for a in actions)

    # Up arrow navigates back
    handled, actions = sm.process_key_event(KEY_UP, 0, 0, is_release=False)
    assert handled
    assert sm.selected_index == 0

    # Number key '1' selects first candidate (primary phonetic transliteration)
    handled, actions = sm.process_key_event(ord("1"), 0, 0, is_release=False)
    assert handled
    assert not sm.composing
    commits = [a.text for a in actions if isinstance(a, Commit)]
    assert commits == ["ভাশা"]


def test_rule_12_focus_out_commits_pending():
    sm = make_state_machine()
    type_string(sm, "ami")
    actions = sm.handle_focus_out()
    assert not sm.composing
    commits = [a.text for a in actions if isinstance(a, Commit)]
    assert commits == ["আমি"]


def test_rule_12_reset_discards():
    sm = make_state_machine()
    type_string(sm, "ami")
    actions = sm.handle_reset()
    assert not sm.composing
    assert not any(isinstance(a, Commit) for a in actions)


def test_rule_13_no_preedit_client_fallback():
    sm = make_state_machine()
    # Disable PREEDIT_TEXT capability (caps = 0)
    sm.set_capabilities(0)
    handled, actions = type_string(sm, "ami")
    assert handled
    # Must NOT emit UpdatePreedit when preedit capability is missing
    assert not any(isinstance(a, UpdatePreedit) for a in actions)


def test_rule_15_buffer_cap_safety():
    sm = make_state_machine()
    sm.config.max_buffer_len = 10
    long_string = "a" * 15
    type_string(sm, long_string)
    # Must not crash and buffer should stay capped
    assert len(sm.phonetic_buffer) <= 10


def test_isolation_between_instances():
    sm1 = make_state_machine()
    sm2 = make_state_machine()

    type_string(sm1, "ami")
    assert sm1.composing
    assert not sm2.composing
    assert sm2.phonetic_buffer == ""

