"""Offline Bengali dictionary and user dictionary manager.

Supports frequency-ranked dictionary lookups and user dictionary persistence.
Offline only: no network connections, strict local file permissions (0600).
"""

import bisect
import os
import pickle
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

from banglaflow.unicode_utils import validate_bengali


class BengaliDictionary:
    """Manages bundled and user dictionaries for Bengali words."""

    MAX_WORD_LENGTH: int = 64
    MAX_DICT_ENTRIES: int = 250_000

    _shared_instance: Optional["BengaliDictionary"] = None

    @classmethod
    def get_shared_instance(cls) -> "BengaliDictionary":
        """Get or initialize singleton shared dictionary instance."""
        if cls._shared_instance is None:
            cls._shared_instance = cls()
        return cls._shared_instance

    def __init__(self, bundled_path: Optional[Path] = None, user_path: Optional[Path] = None):
        self._entries: Dict[str, int] = {}
        self._user_entries: Dict[str, int] = {}
        self._exact_norm_map: Dict[str, List[str]] = {}
        self._prefix_norm_keys: List[str] = []
        self._prefix_words: List[str] = []

        # Default bundled dictionary location
        if bundled_path is None:
            candidates = [
                Path.home() / ".local" / "share" / "banglaflow" / "dictionaries" / "words.tsv",
                Path(__file__).resolve().parent.parent.parent / "data" / "dictionaries" / "words.tsv",
                Path("/usr/share/banglaflow/dictionaries/words.tsv"),
            ]
            for c in candidates:
                if c.exists():
                    bundled_path = c
                    break

        loaded_from_cache = False
        if bundled_path and bundled_path.exists():
            bin_path = bundled_path.with_name(bundled_path.name + ".bin")
            if bin_path.exists():
                try:
                    if bin_path.stat().st_mtime >= bundled_path.stat().st_mtime:
                        with open(bin_path, "rb") as f:
                            cached = pickle.load(f)
                        self._entries = cached["entries"]
                        self._exact_norm_map = cached["exact_norm_map"]
                        self._prefix_norm_keys = cached["prefix_norm_keys"]
                        self._prefix_words = cached["prefix_words"]
                        loaded_from_cache = True
                except Exception:
                    loaded_from_cache = False

            if not loaded_from_cache:
                self.load_tsv(bundled_path, is_user=False)
                self._rebuild_search_index()
                try:
                    # Write cache for instant next startups
                    cache_data = {
                        "entries": self._entries,
                        "exact_norm_map": self._exact_norm_map,
                        "prefix_norm_keys": self._prefix_norm_keys,
                        "prefix_words": self._prefix_words,
                    }
                    with open(bin_path, "wb") as f:
                        pickle.dump(cache_data, f, protocol=pickle.HIGHEST_PROTOCOL)
                except Exception:
                    pass

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
            self._rebuild_search_index()
        elif not loaded_from_cache:
            self._rebuild_search_index()

    @staticmethod
    def normalize_bn(text: str) -> str:
        """Phonetic normalization for Bengali text (chandrabindu, vowels, sibilants, halant)."""
        res = text.replace("\u0981", "")  # Remove chandrabindu
        res = res.replace("\u09cd", "")   # Remove halant for prefix matching
        res = res.replace("\u09c0", "\u09bf").replace("\u09c2", "\u09c1")
        res = res.replace("\u0988", "\u0987").replace("\u098a", "\u0989")
        res = res.replace("\u09b6", "\u09b8").replace("\u09b7", "\u09b8")
        res = res.replace("\u09a3", "\u09a8")
        res = res.replace("\u099b", "\u099a")
        res = res.replace("\u09dc", "\u09b0").replace("\u09dd", "\u09b0")
        res = res.replace("\u09a1", "\u09a6").replace("\u09a2", "\u09a7")
        res = res.replace("\u099f", "\u09a4").replace("\u09a0", "\u09a5")
        res = res.replace("\u099d", "\u099c").replace("\u09af", "\u09af\u09bc")
        res = res.replace("\u09ce", "\u09a4")
        return res

    def _rebuild_search_index(self) -> None:
        """Rebuild exact normalized lookup and prefix search structures."""
        self._exact_norm_map = {}
        all_words = set(self._entries.keys()) | set(self._user_entries.keys())

        for w in all_words:
            k = self.normalize_bn(w)
            if k not in self._exact_norm_map:
                self._exact_norm_map[k] = []
            self._exact_norm_map[k].append(w)

        for k in self._exact_norm_map:
            self._exact_norm_map[k].sort(key=lambda w: (-self.get_frequency(w), len(w), w))

        norm_pairs = sorted(
            [(self.normalize_bn(w), w) for w in all_words],
            key=lambda x: x[0],
        )
        self._prefix_norm_keys = [p[0] for p in norm_pairs]
        self._prefix_words = [p[1] for p in norm_pairs]

    def find_exact_matches(self, bengali_text: str) -> List[str]:
        """Find all dictionary words matching the normalized phonetic form."""
        k = self.normalize_bn(bengali_text)
        return self._exact_norm_map.get(k, [])

    def find_prefix_matches(self, bengali_prefix: str, max_matches: int = 20) -> List[str]:
        """Find dictionary words starting with the normalized phonetic prefix."""
        k = self.normalize_bn(bengali_prefix)
        if not k:
            return []

        idx = bisect.bisect_left(self._prefix_norm_keys, k)
        matches: List[str] = []
        seen: Set[str] = set()

        while idx < len(self._prefix_norm_keys) and self._prefix_norm_keys[idx].startswith(k):
            w = self._prefix_words[idx]
            if w not in seen:
                seen.add(w)
                matches.append(w)
                if len(matches) >= 100:
                    break
            idx += 1

        matches.sort(key=lambda w: (-self.get_frequency(w), len(w), w))
        return matches[:max_matches]

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
        self._rebuild_search_index()

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

