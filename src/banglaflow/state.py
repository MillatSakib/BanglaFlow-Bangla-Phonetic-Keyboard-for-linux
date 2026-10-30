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

# Navigation Keys
KEY_UP = 65362
KEY_DOWN = 65364
KEY_PAGE_UP = 65365
KEY_PAGE_DOWN = 65366
KEY_LEFT = 65361
KEY_RIGHT = 65363
KEY_HOME = 65360
KEY_END = 65367

# Keypad Navigation Keys (when NumLock is OFF)
KEY_KP_HOME = 65429       # 0xFF95
KEY_KP_LEFT = 65430       # 0xFF96
KEY_KP_UP = 65431         # 0xFF97
KEY_KP_RIGHT = 65432      # 0xFF98
KEY_KP_DOWN = 65433       # 0xFF99
KEY_KP_PAGE_UP = 65434    # 0xFF9A
KEY_KP_PAGE_DOWN = 65435  # 0xFF9B
KEY_KP_END = 65436        # 0xFF9C
KEY_KP_BEGIN = 65437      # 0xFF9D

# Function Keys (F1 - F35: 0xFFBE - 0xFFE0)
KEY_F1 = 65470
KEY_F2 = 65471
KEY_F3 = 65472
KEY_F4 = 65473
KEY_F5 = 65474
KEY_F6 = 65475
KEY_F7 = 65476
KEY_F8 = 65477
KEY_F9 = 65478
KEY_F10 = 65479
KEY_F11 = 65480
KEY_F12 = 65481
KEY_F35 = 65504

# Keypad Numbers (0-9: 0xFFB0 - 0xFFB9)
KEY_KP_0 = 65456
KEY_KP_1 = 65457
KEY_KP_2 = 65458
KEY_KP_3 = 65459
KEY_KP_4 = 65460
KEY_KP_5 = 65461
KEY_KP_6 = 65462
KEY_KP_7 = 65463
KEY_KP_8 = 65464
KEY_KP_9 = 65465

# Keypad Arithmetic & Operators
KEY_KP_ADD = 65451        # 0xFFAB (+)
KEY_KP_SUBTRACT = 65453   # 0xFFAD (-)
KEY_KP_MULTIPLY = 65450   # 0xFFAA (*)
KEY_KP_DIVIDE = 65455     # 0xFFAF (/)
KEY_KP_DECIMAL = 65454    # 0xFFAE (.)
KEY_KP_SEPARATOR = 65452  # 0xFFAC (,)
KEY_KP_EQUAL = 65469      # 0xFFBD (=)
KEY_KP_SPACE = 65408      # 0xFF80 (space)
KEY_KP_TAB = 65417        # 0xFF89 (tab)

# System / Control Pass-through Keys
KEY_SYSTEM_PASS_THROUGH = {
    65535,  # KEY_DELETE (0xFFFF)
    65439,  # KEY_KP_DELETE (0xFF9F)
    65379,  # KEY_INSERT (0xFF63)
    65438,  # KEY_KP_INSERT (0xFF9E)
    65377,  # KEY_PRINT (0xFF61)
    65301,  # KEY_SYS_REQ (0xFF15)
    65299,  # KEY_PAUSE (0xFF13)
    65387,  # KEY_BREAK (0xFF6B)
    65383,  # KEY_MENU (0xFF67)
    65386,  # KEY_HELP (0xFF6A)
}

# Bare Modifiers & Lock Keys (never intercept, always pass through)
KEY_MODIFIERS_AND_LOCKS = {
    65505,  # Shift_L (0xFFE1)
    65506,  # Shift_R (0xFFE2)
    65507,  # Control_L (0xFFE3)
    65508,  # Control_R (0xFFE4)
    65509,  # Caps_Lock (0xFFE5)
    65407,  # Num_Lock (0xFF7F)
    65300,  # Scroll_Lock (0xFF14)
    65513,  # Alt_L (0xFFE9)
    65514,  # Alt_R (0xFFEA)
    65515,  # Super_L (0xFFEB)
    65516,  # Super_R (0xFFEC)
    65027,  # ISO_Level3_Shift (0xFE03)
    65406,  # Mode_switch (0xFF7E)
}

KEYPAD_OPERATORS_MAP = {
    KEY_KP_ADD: "+",
    KEY_KP_SUBTRACT: "-",
    KEY_KP_MULTIPLY: "*",
    KEY_KP_DIVIDE: "/",
    KEY_KP_DECIMAL: ".",
    KEY_KP_SEPARATOR: ",",
    KEY_KP_EQUAL: "=",
}

BN_DIGITS_MAP = {
    0: "\u09E6",
    1: "\u09E7",
    2: "\u09E8",
    3: "\u09E9",
    4: "\u09EA",
    5: "\u09EB",
    6: "\u09EC",
    7: "\u09ED",
    8: "\u09EE",
    9: "\u09EF",
}

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

        # 2. Bare Modifiers and Lock keys (Shift, Ctrl, Alt, CapsLock, NumLock, ScrollLock):
        # Never intercept, never consume, pass through cleanly to system.
        if keyval in KEY_MODIFIERS_AND_LOCKS:
            return False, []

        has_ctrl = bool(modifiers & MOD_CONTROL)
        has_alt = bool(modifiers & MOD_ALT)
        has_super = bool(modifiers & MOD_SUPER)

        # 3. Key combination with Ctrl, Alt, or Super: if composing, commit first, then return not-handled
        if has_ctrl or has_alt or has_super:
            if self.composing:
                cand = self._get_selected_candidate()
                actions.append(Commit(cand))
                actions.append(HidePreedit())
                actions.append(HideLookup())
                self.clear()
            return False, actions

        # 4. Function keys (F1 - F35): never intercept or alter system function key behavior
        if KEY_F1 <= keyval <= KEY_F35:
            if self.composing:
                cand = self._get_selected_candidate()
                actions.append(Commit(cand))
                actions.append(HidePreedit())
                actions.append(HideLookup())
                self.clear()
            return False, actions

        # 5. System / Control / Editing keys (Delete, Insert, PrintScreen, Pause, Break, Menu)
        if keyval in KEY_SYSTEM_PASS_THROUGH:
            if self.composing:
                cand = self._get_selected_candidate()
                actions.append(Commit(cand))
                actions.append(HidePreedit())
                actions.append(HideLookup())
                self.clear()
            return False, actions

        # 6. ESCAPE: discard composition, handled
        if keyval == KEY_ESCAPE:
            if self.composing:
                self.clear()
                actions.append(HidePreedit())
                actions.append(HideLookup())
                return True, actions
            return False, []

        # 7. SPACE
        if keyval in (KEY_SPACE, KEY_KP_SPACE):
            if self.composing:
                cand = self._get_selected_candidate()
                # Commit selected candidate + " " as ONE commit
                actions.append(Commit(cand + " "))
                actions.append(HidePreedit())
                actions.append(HideLookup())
                self.clear()
                return True, actions
            return False, []

        # 8. ENTER / KP_ENTER
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

        # 9. TAB
        if keyval in (KEY_TAB, KEY_ISO_LEFT_TAB, KEY_KP_TAB):
            if self.composing:
                cand = self._get_selected_candidate()
                actions.append(Commit(cand))
                actions.append(HidePreedit())
                actions.append(HideLookup())
                self.clear()
                return False, actions
            return False, []

        # 10. BACKSPACE
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

        # 11. Navigation / Candidate Selection with Arrow / Page keys
        if self.composing and self.lookup_visible and len(self.candidates) > 1:
            if keyval in (KEY_DOWN, KEY_KP_DOWN, KEY_PAGE_DOWN, KEY_KP_PAGE_DOWN):
                self.selected_index = (self.selected_index + 1) % len(self.candidates)
                self.bengali_preview = self.candidates[self.selected_index]
                if self.caps & CAP_PREEDIT_TEXT:
                    actions.append(UpdatePreedit(self.bengali_preview, len(self.bengali_preview)))
                actions.append(UpdateLookup(self.candidates, self.selected_index, True))
                return True, actions

            if keyval in (KEY_UP, KEY_KP_UP, KEY_PAGE_UP, KEY_KP_PAGE_UP):
                self.selected_index = (self.selected_index - 1) % len(self.candidates)
                self.bengali_preview = self.candidates[self.selected_index]
                if self.caps & CAP_PREEDIT_TEXT:
                    actions.append(UpdatePreedit(self.bengali_preview, len(self.bengali_preview)))
                actions.append(UpdateLookup(self.candidates, self.selected_index, True))
                return True, actions

        # Arrow keys / Home / End / PageUp / PageDown without active lookup navigation:
        # Commit pending composition and let app navigate cleanly
        nav_keys = {
            KEY_UP, KEY_DOWN, KEY_LEFT, KEY_RIGHT, KEY_HOME, KEY_END, KEY_PAGE_UP, KEY_PAGE_DOWN,
            KEY_KP_HOME, KEY_KP_LEFT, KEY_KP_UP, KEY_KP_RIGHT, KEY_KP_DOWN,
            KEY_KP_PAGE_UP, KEY_KP_PAGE_DOWN, KEY_KP_END, KEY_KP_BEGIN,
        }
        if keyval in nav_keys:
            if self.composing:
                cand = self._get_selected_candidate()
                actions.append(Commit(cand))
                actions.append(HidePreedit())
                actions.append(HideLookup())
                self.clear()
            return False, actions

        # 12. Keypad Numbers (0-9: KEY_KP_0 - KEY_KP_9)
        if KEY_KP_0 <= keyval <= KEY_KP_9:
            digit = keyval - KEY_KP_0
            out_digit = BN_DIGITS_MAP[digit] if self.config.bengali_digits else str(digit)
            if self.composing:
                cand = self._get_selected_candidate()
                actions.append(Commit(cand + out_digit))
                actions.append(HidePreedit())
                actions.append(HideLookup())
                self.clear()
                return True, actions
            else:
                actions.append(Commit(out_digit))
                return True, actions

        # 13. Keypad Operators (+, -, *, /, ., ,, =)
        if keyval in KEYPAD_OPERATORS_MAP:
            op_char = KEYPAD_OPERATORS_MAP[keyval]
            if self.composing:
                cand = self._get_selected_candidate()
                actions.append(Commit(cand + op_char))
                actions.append(HidePreedit())
                actions.append(HideLookup())
                self.clear()
                return True, actions
            else:
                actions.append(Commit(op_char))
                return True, actions

        # 14. Top-row Number keys (0-9)
        if ord("0") <= keyval <= ord("9"):
            digit = keyval - ord("0")
            out_digit = BN_DIGITS_MAP[digit] if self.config.bengali_digits else str(digit)
            if self.composing:
                cand = self._get_selected_candidate()
                actions.append(Commit(cand + out_digit))
                actions.append(HidePreedit())
                actions.append(HideLookup())
                self.clear()
                return True, actions
            else:
                actions.append(Commit(out_digit))
                return True, actions

        # 15. Backtick (`): if not composing, directly output `
        if keyval == ord("`"):
            if not self.composing:
                actions.append(Commit("`"))
                return True, actions

        # 16. Special Keysym & Control Code Guard:
        # Special X11 keysyms (0xFF00 - 0xFFFF) and ASCII control characters (< 0x20)
        # that were not explicitly handled above must NEVER be passed to chr().
        # In Unicode, 0xFF00 - 0xFFEF is the Halfwidth and Fullwidth Forms block,
        # which would otherwise turn X11 keysyms into halfwidth Hangul/forms (e.g. ﾭ, ﾫ, ﾰ).
        if keyval < 0x20 or (0xFF00 <= keyval <= 0xFFFF):
            if self.composing:
                cand = self._get_selected_candidate()
                actions.append(Commit(cand))
                actions.append(HidePreedit())
                actions.append(HideLookup())
                self.clear()
            return False, actions

        char = chr(keyval)

        # 17. Phonetic Composition handling
        # Alphabetic characters, backtick, caret (^), colon (:) for bisarga, and while composing: comma (,) for hasanta
        is_composing_char = (
            char.isalpha()
            or char in ("`", "^", ":")
            or (self.composing and char == ",")
        )

        if is_composing_char:
            if len(self.phonetic_buffer) >= self.config.max_buffer_len:
                # Buffer overflow safety: commit current and start fresh
                cand = self._get_selected_candidate()
                actions.append(Commit(cand))
                self.clear()

            self.phonetic_buffer += char
            self.composing = True
            self._update_composition(actions)
            return True, actions

        # 18. Punctuation handling
        punctuation_marks = {",", ".", "?", "!", ";", "'", '"', "(", ")", "[", "]", "{", "}"}
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
        """Commit pending word on reset and clear state."""
        actions: List[Action] = []
        if self.composing and self.bengali_preview:
            cand = self._get_selected_candidate()
            actions.append(Commit(cand))
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

