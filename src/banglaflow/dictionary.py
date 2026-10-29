"""Offline Bengali dictionary and user dictionary manager.

Supports frequency-ranked dictionary lookups and user dictionary persistence.
Offline only: no network connections, strict local file permissions (0600).
"""

import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from banglaflow.unicode_utils import validate_bengali


class BengaliDictionary:
    """Manages bundled and user dictionaries for Bengali words."""

    MAX_WORD_LENGTH: int = 64
    MAX_DICT_ENTRIES: int = 200_000

    def __init__(self, bundled_path: Optional[Path] = None, user_path: Optional[Path] = None):
        self._entries: Dict[str, int] = {}
        self._user_entries: Dict[str, int] = {}

        # Default bundled dictionary location
        if bundled_path is None:
            candidates = [
                Path(__file__).resolve().parent.parent.parent / "data" / "dictionaries" / "words.tsv",
                Path("/usr/share/banglaflow/dictionaries/words.tsv"),
            ]
            for c in candidates:
                if c.exists():
                    bundled_path = c
                    break

        if bundled_path and bundled_path.exists():
            self.load_tsv(bundled_path, is_user=False)

        # User dictionary path
        if user_path is None:
            xdg_data = os.environ.get("XDG_DATA_HOME")
            if xdg_data:
                base_dir = Path(xdg_data) / "banglaflow"
            else:
                base_dir = Path.home() / ".local" / "share" / "banglaflow"
            user_path = base_dir / "user.tsv"

        self.user_path = user_path
        if self.user_path.exists():
            self.load_tsv(self.user_path, is_user=True)

    def load_tsv(self, file_path: Path, is_user: bool = False) -> int:
        """Load and validate words from a TSV file.

        Returns the number of loaded valid words.
        """
        count = 0
        target_dict = self._user_entries if is_user else self._entries

        with open(file_path, "r", encoding="utf-8") as f:
            for line_no, line in enumerate(f, start=1):
                line = line.strip()
                if not line or line.startswith("#"):
                    continue

                if len(target_dict) >= self.MAX_DICT_ENTRIES:
                    break

                parts = line.split("\t")
                word = parts[0].strip()
                freq = 1
                if len(parts) > 1:
                    try:
                        freq = int(parts[1].strip())
                    except ValueError:
                        freq = 1

                if len(word) > self.MAX_WORD_LENGTH:
                    continue

                # Control character check
                if any(ord(c) < 32 and c not in "\t\n\r" for c in word):
                    continue

                valid, _ = validate_bengali(word)
                if not valid:
                    continue

                target_dict[word] = freq
                count += 1

        return count

    def get_frequency(self, word: str) -> int:
        """Get frequency score for a word.

        User entries have priority over bundled entries.
        """
        if word in self._user_entries:
            return self._user_entries[word] + 10_000
        return self._entries.get(word, 0)

    def contains(self, word: str) -> bool:
        """Check if word exists in either dictionary."""
        return word in self._user_entries or word in self._entries

    def add_user_word(self, word: str, frequency: int = 100) -> bool:
        """Add a word to user dictionary with secure file permissions (0600)."""
        valid, _ = validate_bengali(word)
        if not valid or len(word) > self.MAX_WORD_LENGTH:
            return False

        self._user_entries[word] = frequency

        # Ensure directory exists with 0700
        self.user_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            os.chmod(self.user_path.parent, 0o700)
        except OSError:
            pass

        # Write or append securely with 0600
        fd = os.open(
            str(self.user_path),
            os.O_WRONLY | os.O_CREAT | os.O_TRUNC,
            0o600,
        )
        with open(fd, "w", encoding="utf-8") as f:
            f.write("# BanglaFlow User Learned Dictionary\n")
            for w, freq in sorted(self._user_entries.items(), key=lambda x: -x[1]):
                f.write(f"{w}\t{freq}\n")

        return True

