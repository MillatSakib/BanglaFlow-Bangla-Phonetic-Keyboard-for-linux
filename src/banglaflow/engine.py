"""IBus Engine Adapter for BanglaFlow.

Subclasses IBus.Engine and dispatches key events to the pure state machine.
Enforces privacy (zero typed text in logs) and fault tolerance (session resilience).
"""

import logging
import os
from typing import Any, List, Optional

from banglaflow.candidates import CandidateGenerator
from banglaflow.config import BanglaFlowConfig, load_config
from banglaflow.dictionary import BengaliDictionary
from banglaflow.phonetic import PhoneticEngine
from banglaflow.state import (
    Action,
    Commit,
    HideLookup,
    HidePreedit,
    InputStateMachine,
    UpdateLookup,
    UpdatePreedit,
)

# Logger setup: default WARNING, never log typed text
logger = logging.getLogger("banglaflow.engine")

try:
    import gi

    gi.require_version("IBus", "1.0")
    from gi.repository import GObject, IBus

    HAS_GI = True
    BaseEngine = IBus.Engine
except (ImportError, ValueError):
    HAS_GI = False

    class BaseEngine:  # type: ignore
        pass


class BanglaFlowEngine(BaseEngine):
    """IBus Engine implementation for BanglaFlow."""

    def __init__(self, *args, **kwargs):
        if HAS_GI and isinstance(self, IBus.Engine):
            super().__init__(*args, **kwargs)

        self.config: BanglaFlowConfig = load_config()
        self.phonetic_engine = PhoneticEngine(
            map_dari=self.config.map_dari, bengali_digits=self.config.bengali_digits
        )
        self.dictionary = BengaliDictionary()
        self.candidate_gen = CandidateGenerator(self.phonetic_engine, self.dictionary)
        self.state_machine = InputStateMachine(
            self.phonetic_engine, self.candidate_gen, self.config
        )

        if HAS_GI:
            self._lookup_table = IBus.LookupTable.new(
                self.config.page_size, 0, True, True
            )
        else:
            self._lookup_table = None

    def execute_actions(self, actions: List[Action], ibus_impl: Any = None) -> None:
        """Translate state machine actions to IBus API calls."""
        engine = ibus_impl or self

        for action in actions:
            if isinstance(action, Commit):
                logger.debug("Action: Commit (len=%d)", len(action.text))
                if HAS_GI and hasattr(engine, "commit_text"):
                    engine.commit_text(IBus.Text.new_from_string(action.text))
                elif hasattr(engine, "commit_text"):
                    engine.commit_text(action.text)

            elif isinstance(action, UpdatePreedit):
                logger.debug("Action: UpdatePreedit (len=%d, cursor=%d)", len(action.text), action.cursor)
                if HAS_GI and hasattr(engine, "update_preedit_text"):
                    engine.update_preedit_text(
                        IBus.Text.new_from_string(action.text),
                        action.cursor,
                        True,
                    )
                elif hasattr(engine, "update_preedit_text"):
                    engine.update_preedit_text(action.text, action.cursor, True)

            elif isinstance(action, HidePreedit):
                logger.debug("Action: HidePreedit")
                if hasattr(engine, "hide_preedit_text"):
                    engine.hide_preedit_text()

            elif isinstance(action, UpdateLookup):
                logger.debug("Action: UpdateLookup (candidates_count=%d)", len(action.candidates))
                if HAS_GI and hasattr(engine, "update_lookup_table"):
                    table = self._lookup_table or IBus.LookupTable.new(
                        self.config.page_size, 0, True, True
                    )
                    table.clear()
                    for cand in action.candidates:
                        table.append_candidate(IBus.Text.new_from_string(cand))
                    table.set_cursor_pos(action.selected_index)
                    engine.update_lookup_table(table, action.visible)
                elif hasattr(engine, "update_lookup_table"):
                    engine.update_lookup_table(action.candidates, action.visible)

            elif isinstance(action, HideLookup):
                logger.debug("Action: HideLookup")
                if hasattr(engine, "hide_lookup_table"):
                    engine.hide_lookup_table()

    # --- IBus Engine Virtual Methods ---

    def do_process_key_event(self, keyval: int, keycode: int, state: int) -> bool:
        """Handle incoming key event from IBus daemon."""
        logger.debug("Event: keycode=%d, modifiers_mask=0x%x", keycode, state)
        try:
            is_release = bool(state & (1 << 30))
            handled, actions = self.state_machine.process_key_event(
                keyval, keycode, state, is_release=is_release
            )
            self.execute_actions(actions)
            return handled
        except Exception as exc:
            # Session safety: never crash user desktop on internal exception
            logger.error("Error processing key event: %s", type(exc).__name__)
            self.state_machine.clear()
            return False

    def do_focus_in(self) -> None:
        logger.debug("Event: focus_in")

    def do_focus_out(self) -> None:
        logger.debug("Event: focus_out")
        try:
            actions = self.state_machine.handle_focus_out()
            self.execute_actions(actions)
        except Exception as exc:
            logger.error("Error on focus_out: %s", type(exc).__name__)

    def do_reset(self) -> None:
        logger.debug("Event: reset")
        try:
            actions = self.state_machine.handle_reset()
            self.execute_actions(actions)
        except Exception as exc:
            logger.error("Error on reset: %s", type(exc).__name__)

    def do_disable(self) -> None:
        logger.debug("Event: disable")
        try:
            actions = self.state_machine.handle_disable()
            self.execute_actions(actions)
        except Exception as exc:
            logger.error("Error on disable: %s", type(exc).__name__)

    def do_set_capabilities(self, caps: int) -> None:
        logger.debug("Event: set_capabilities (caps=0x%x)", caps)
        self.state_machine.set_capabilities(caps)

    def do_candidate_clicked(self, index: int, button: int, state: int) -> None:
        logger.debug("Event: candidate_clicked (index=%d)", index)
        try:
            actions = self.state_machine.handle_candidate_clicked(index)
            self.execute_actions(actions)
        except Exception as exc:
            logger.error("Error on candidate_clicked: %s", type(exc).__name__)

