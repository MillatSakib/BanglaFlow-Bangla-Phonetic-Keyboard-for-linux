"""Pure key-event state machine for BanglaFlow.

Processes key events (keyval, keycode, modifiers, is_release) into
deterministic actions (Commit, UpdatePreedit, HidePreedit, UpdateLookup, HideLookup).
Completely pure: zero external dependencies, zero GI/IBus imports.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Tuple, Union

from banglaflow.candidates import CandidateGenerator
from banglaflow.config import BanglaFlowConfig
from banglaflow.phonetic import PhoneticEngine

# Key Constants (X11 / IBus keyval standards)
KEY_SPACE = 32
KEY_RETURN = 65293
KEY_KP_ENTER = 65421
KEY_BACKSPACE = 65288
KEY_ESCAPE = 65307
KEY_TAB = 65289
KEY_ISO_LEFT_TAB = 65056
KEY_UP = 65362
KEY_DOWN = 65364
KEY_PAGE_UP = 65365
KEY_PAGE_DOWN = 65366
KEY_LEFT = 65361
KEY_RIGHT = 65363
KEY_HOME = 65360
KEY_END = 65367

# Modifier bitmasks
MOD_SHIFT = 1 << 0
MOD_LOCK = 1 << 1
MOD_CONTROL = 1 << 2
MOD_ALT = 1 << 3
MOD_SUPER = 1 << 26
MOD_RELEASE = 1 << 30

# Capability bits
CAP_PREEDIT_TEXT = 1
CAP_LOOKUP_TABLE = 4


@dataclass(frozen=True)
class Commit:
    text: str


@dataclass(frozen=True)
class UpdatePreedit:
    text: str
    cursor: int


@dataclass(frozen=True)
class HidePreedit:
    pass


@dataclass(frozen=True)
class UpdateLookup:
    candidates: List[str]
    selected_index: int
    visible: bool


@dataclass(frozen=True)
class HideLookup:
    pass


Action = Union[Commit, UpdatePreedit, HidePreedit, UpdateLookup, HideLookup]


class InputStateMachine:
    """Pure key-event state machine."""

    def __init__(
        self,
        phonetic_engine: PhoneticEngine,
        candidate_generator: CandidateGenerator,
        config: Optional[BanglaFlowConfig] = None,
    ):
        self.engine = phonetic_engine
        self.candidate_gen = candidate_generator
        self.config = config or BanglaFlowConfig()

        self.phonetic_buffer: str = ""
        self.bengali_preview: str = ""
        self.candidates: List[str] = []
        self.selected_index: int = 0
        self.composing: bool = False
        self.mode: str = self.config.mode  # "bengali" or "english"
        self.caps: int = CAP_PREEDIT_TEXT | CAP_LOOKUP_TABLE
        self.lookup_visible: bool = False

    def clear(self) -> None:
        """Clear composition state."""
        self.phonetic_buffer = ""
        self.bengali_preview = ""
        self.candidates = []
        self.selected_index = 0
        self.composing = False
        self.lookup_visible = False

    def set_capabilities(self, caps: int) -> None:
        """Update client capability flags."""
        self.caps = caps

    def set_mode(self, mode: str) -> List[Action]:
        """Switch between 'bengali' and 'english' mode."""
        actions: List[Action] = []
        if self.composing and self.bengali_preview:
            actions.append(Commit(self.bengali_preview))
            actions.append(HidePreedit())
            actions.append(HideLookup())
            self.clear()
        if mode in ("bengali", "english"):
            self.mode = mode
        return actions

    def process_key_event(
        self, keyval: int, keycode: int, modifiers: int, is_release: bool = False
    ) -> Tuple[bool, List[Action]]:
        """Process a single key event and return (handled, actions)."""
        actions: List[Action] = []

        # 1. Key release events: ignore, never double-process
        if is_release or (modifiers & MOD_RELEASE):
            return False, []

        # English pass-through mode
        if self.mode == "english":
            return False, []

        has_ctrl = bool(modifiers & MOD_CONTROL)
        has_alt = bool(modifiers & MOD_ALT)
        has_super = bool(modifiers & MOD_SUPER)

        # 2. Key with Ctrl, Alt, or Super: if composing, commit first, then return not-handled
        if has_ctrl or has_alt or has_super:
            if self.composing:
                cand = self._get_selected_candidate()
                actions.append(Commit(cand))
                actions.append(HidePreedit())
                actions.append(HideLookup())
                self.clear()
            return False, actions

        # 8. ESCAPE: discard composition, handled
        if keyval == KEY_ESCAPE:
            if self.composing:
                self.clear()
                actions.append(HidePreedit())
                actions.append(HideLookup())
                return True, actions
            return False, []

        # 4. SPACE
        if keyval == KEY_SPACE:
            if self.composing:
                cand = self._get_selected_candidate()
                # Commit selected candidate + " " as ONE commit
                actions.append(Commit(cand + " "))
                actions.append(HidePreedit())
                actions.append(HideLookup())
                self.clear()
                return True, actions
            return False, []

        # 5. ENTER / KP_ENTER
        if keyval in (KEY_RETURN, KEY_KP_ENTER):
            if self.composing:
                cand = self._get_selected_candidate()
                actions.append(Commit(cand))
                actions.append(HidePreedit())
                actions.append(HideLookup())
                self.clear()
                # Return not-handled so the app still receives Enter
                return False, actions
            return False, []

        # 6. TAB
        if keyval in (KEY_TAB, KEY_ISO_LEFT_TAB):
            if self.composing:
                cand = self._get_selected_candidate()
                actions.append(Commit(cand))
                actions.append(HidePreedit())
                actions.append(HideLookup())
                self.clear()
                return False, actions
            return False, []

        # 7. BACKSPACE
        if keyval == KEY_BACKSPACE:
            if self.composing:
                self.phonetic_buffer = self.phonetic_buffer[:-1]
                if not self.phonetic_buffer:
                    self.clear()
                    actions.append(HidePreedit())
                    actions.append(HideLookup())
                    return True, actions
                else:
                    self._update_composition(actions)
                    return True, actions
            return False, []

        # 10 & 11. Navigation / Candidate Selection with Arrow / Page keys
        if self.composing and self.lookup_visible and len(self.candidates) > 1:
            if keyval in (KEY_DOWN, KEY_PAGE_DOWN):
                self.selected_index = (self.selected_index + 1) % len(self.candidates)
                self.bengali_preview = self.candidates[self.selected_index]
                if self.caps & CAP_PREEDIT_TEXT:
                    actions.append(UpdatePreedit(self.bengali_preview, len(self.bengali_preview)))
                actions.append(UpdateLookup(self.candidates, self.selected_index, True))
                return True, actions

            if keyval in (KEY_UP, KEY_PAGE_UP):
                self.selected_index = (self.selected_index - 1) % len(self.candidates)
                self.bengali_preview = self.candidates[self.selected_index]
                if self.caps & CAP_PREEDIT_TEXT:
                    actions.append(UpdatePreedit(self.bengali_preview, len(self.bengali_preview)))
                actions.append(UpdateLookup(self.candidates, self.selected_index, True))
                return True, actions

        # Arrow keys / Home / End without lookup: commit word and let app navigate
        if keyval in (KEY_UP, KEY_DOWN, KEY_LEFT, KEY_RIGHT, KEY_HOME, KEY_END, KEY_PAGE_UP, KEY_PAGE_DOWN):
            if self.composing:
                cand = self._get_selected_candidate()
                actions.append(Commit(cand))
                actions.append(HidePreedit())
                actions.append(HideLookup())
                self.clear()
            return False, actions

        # Number keys 1-9 for candidate selection when lookup is active
        if self.composing and self.lookup_visible and ord("1") <= keyval <= ord("9"):
            digit = int(chr(keyval))
            cand_idx = digit - 1
            if 0 <= cand_idx < len(self.candidates):
                chosen = self.candidates[cand_idx]
                actions.append(Commit(chosen))
                actions.append(HidePreedit())
                actions.append(HideLookup())
                self.clear()
                return True, actions

        # Convert keyval to character if printable ASCII
        try:
            char = chr(keyval)
        except (ValueError, OverflowError):
            return False, []

        # 9. Punctuation handling
        punctuation_marks = {",", ".", "?", "!", ";", ":", "'", '"', "(", ")", "[", "]", "{", "}"}
        if char in punctuation_marks or char == "$":
            # Bengali Dari । mapped from .
            if char == "." and self.config.map_dari:
                if self.composing:
                    cand = self._get_selected_candidate()
                    # Commit word + dari as ONE atomic commit so word is never erased
                    actions.append(Commit(cand + "\u0964"))
                    actions.append(HidePreedit())
                    actions.append(HideLookup())
                    self.clear()
                    return True, actions
                else:
                    actions.append(Commit("\u0964"))
                    return True, actions

            # Bengali Taka ৳ mapped from $
            if char == "$":
                if self.composing:
                    cand = self._get_selected_candidate()
                    actions.append(Commit(cand + "\u09F3"))
                    actions.append(HidePreedit())
                    actions.append(HideLookup())
                    self.clear()
                    return True, actions
                else:
                    actions.append(Commit("\u09F3"))
                    return True, actions

            # Other punctuation (commit current composing word first)
            if self.composing:
                cand = self._get_selected_candidate()
                actions.append(Commit(cand))
                actions.append(HidePreedit())
                actions.append(HideLookup())
                self.clear()

            # Return not-handled so app inserts punctuation cleanly without duplicate
            return False, actions

        # 3. Regular letters and digits (composition)
        if char.isalnum() or char in ("`", "^"):
            if len(self.phonetic_buffer) >= self.config.max_buffer_len:
                # Buffer overflow safety: commit current and start fresh
                cand = self._get_selected_candidate()
                actions.append(Commit(cand))
                self.clear()

            self.phonetic_buffer += char
            self.composing = True
            self._update_composition(actions)
            return True, actions

        return False, []

    def _get_selected_candidate(self) -> str:
        if self.candidates and 0 <= self.selected_index < len(self.candidates):
            return self.candidates[self.selected_index]
        return self.bengali_preview or self.engine.convert(self.phonetic_buffer)

    def _update_composition(self, actions: List[Action]) -> None:
        self.candidates = self.candidate_gen.generate_candidates(
            self.phonetic_buffer, max_candidates=self.config.page_size
        )
        self.selected_index = 0
        if self.candidates:
            self.bengali_preview = self.candidates[0]
        else:
            self.bengali_preview = self.engine.convert(self.phonetic_buffer)

        # Preedit update
        if self.caps & CAP_PREEDIT_TEXT:
            actions.append(UpdatePreedit(self.bengali_preview, len(self.bengali_preview)))

        # Lookup table update
        if self.config.show_candidate_lookup and len(self.candidates) > 1:
            self.lookup_visible = True
            actions.append(UpdateLookup(self.candidates, self.selected_index, True))
        else:
            self.lookup_visible = False
            actions.append(HideLookup())

    def handle_focus_out(self) -> List[Action]:
        """Commit pending word on focus-out and clear state."""
        actions: List[Action] = []
        if self.composing and self.bengali_preview:
            cand = self._get_selected_candidate()
            actions.append(Commit(cand))
            actions.append(HidePreedit())
            actions.append(HideLookup())
        self.clear()
        return actions

    def handle_reset(self) -> List[Action]:
        """Discard state on reset."""
        actions: List[Action] = []
        if self.composing:
            actions.append(HidePreedit())
            actions.append(HideLookup())
        self.clear()
        return actions

    def handle_disable(self) -> List[Action]:
        """Commit pending word on disable and clear state."""
        actions: List[Action] = []
        if self.composing and self.bengali_preview:
            cand = self._get_selected_candidate()
            actions.append(Commit(cand))
            actions.append(HidePreedit())
            actions.append(HideLookup())
        self.clear()
        return actions

    def handle_candidate_clicked(self, index: int) -> List[Action]:
        """Handle candidate selection via mouse click."""
        actions: List[Action] = []
        if 0 <= index < len(self.candidates):
            chosen = self.candidates[index]
            actions.append(Commit(chosen))
            actions.append(HidePreedit())
            actions.append(HideLookup())
            self.clear()
        return actions

