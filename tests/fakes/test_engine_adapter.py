"""Adapter tests using fake IBus API verifying call order and argument correctness."""

from banglaflow.engine import BanglaFlowEngine
from banglaflow.state import KEY_SPACE
from tests.fakes.fake_ibus import FakeIBusEngine


def test_adapter_typing_and_commit_sequence():
    fake = FakeIBusEngine()
    engine = BanglaFlowEngine()

    # Simulate typing 'a', 'm', 'i'
    for c in "ami":
        handled = engine.do_process_key_event(ord(c), 0, 0)
        assert handled

    # Replay actions onto fake to test exact call logging
    handled, actions = engine.state_machine.process_key_event(KEY_SPACE, 0, 0, is_release=False)
    assert handled
    engine.execute_actions(actions, ibus_impl=fake)

    # Assert exact call sequence:
    # 1. commit_text once
    # 2. hide_preedit_text
    # 3. hide_lookup_table
    calls = [call[0] for call in fake.call_log]
    assert "commit_text" in calls
    assert calls[0] == "commit_text"
    assert fake.call_log[0][1] == "আমি "
    assert "hide_preedit_text" in calls
    assert "hide_lookup_table" in calls


def test_adapter_focus_out():
    fake = FakeIBusEngine()
    engine = BanglaFlowEngine()

    # Type "ami"
    for c in "ami":
        engine.do_process_key_event(ord(c), 0, 0)

    # Focus out
    actions = engine.state_machine.handle_focus_out()
    engine.execute_actions(actions, ibus_impl=fake)

    calls = [call[0] for call in fake.call_log]
    assert "commit_text" in calls
    assert fake.call_log[0][1] == "আমি"


def test_adapter_handles_exceptions_gracefully():
    engine = BanglaFlowEngine()
    # Passing an invalid keyval that could cause chr() overflow or similar
    handled = engine.do_process_key_event(0xFFFFFFFFF, 0, 0)
    assert not handled
    assert not engine.state_machine.composing

