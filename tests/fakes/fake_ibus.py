"""Fake IBus engine API for unit testing the adapter in complete isolation."""

from typing import List, Tuple, Any


class FakeIBusText:
    def __init__(self, text: str):
        self.text = text

    @classmethod
    def new_from_string(cls, text: str):
        return cls(text)


class FakeIBusLookupTable:
    def __init__(self, page_size: int = 5, cursor_pos: int = 0, cursor_visible: bool = True, round: bool = True):
        self.page_size = page_size
        self.cursor_pos = cursor_pos
        self.cursor_visible = cursor_visible
        self.round = round
        self.candidates: List[FakeIBusText] = []

    @classmethod
    def new(cls, page_size: int, cursor_pos: int, cursor_visible: bool, round: bool):
        return cls(page_size, cursor_pos, cursor_visible, round)

    def append_candidate(self, cand_text: FakeIBusText):
        self.candidates.append(cand_text)

    def clear(self):
        self.candidates.clear()

    def set_cursor_pos(self, pos: int):
        self.cursor_pos = pos


class FakeIBusEngine:
    def __init__(self):
        self.call_log: List[Tuple[str, Any]] = []

    def commit_text(self, ibus_text):
        self.call_log.append(("commit_text", getattr(ibus_text, "text", str(ibus_text))))

    def update_preedit_text(self, ibus_text, cursor_pos: int, visible: bool):
        self.call_log.append(
            ("update_preedit_text", (getattr(ibus_text, "text", str(ibus_text)), cursor_pos, visible))
        )

    def hide_preedit_text(self):
        self.call_log.append(("hide_preedit_text", None))

    def update_lookup_table(self, lookup_table, visible: bool):
        cands = [c.text for c in getattr(lookup_table, "candidates", [])]
        self.call_log.append(("update_lookup_table", (cands, getattr(lookup_table, "cursor_pos", 0), visible)))

    def hide_lookup_table(self):
        self.call_log.append(("hide_lookup_table", None))

