"""Pure phonetic conversion engine for Bengali.

Implements longest-match, context-aware tokenization over validated rule tables.
Completely pure: zero external dependencies, zero GI/IBus imports, deterministic.
"""

from typing import Optional, Set
from banglaflow.rules import RuleSet, load_rules
from banglaflow.unicode_utils import sanitize_bengali_sequence


class PhoneticEngine:
    """Pure Bengali phonetic conversion engine."""

    def __init__(self, ruleset: Optional[RuleSet] = None, map_dari: bool = True, bengali_digits: bool = False):
        self.ruleset = ruleset or load_rules()
        self.map_dari = map_dari
        self.bengali_digits = bengali_digits

    def is_vowel(self, c: str) -> bool:
        """Check if character is marked as vowel in phonetic alphabet."""
        return c.lower() in self.ruleset.vowels

    def is_consonant(self, c: str) -> bool:
        """Check if character is marked as consonant in phonetic alphabet."""
        return c.lower() in self.ruleset.consonants

    def is_punctuation(self, c: str) -> bool:
        """Check if character is punctuation (neither vowel nor consonant)."""
        return not (self.is_vowel(c) or self.is_consonant(c))

    def fix_string(self, text: str) -> str:
        """Normalize case of input according to case-sensitivity table."""
        res = []
        for c in text:
            if c.lower() in self.ruleset.casesensitive:
                res.append(c)
            else:
                res.append(c.lower())
        return "".join(res)

    def convert(self, text: str) -> str:
        """Convert Latin phonetic string into Bengali text.

        Pure and deterministic.
        """
        if not text:
            return ""

        fixed_str = self.fix_string(text)
        length = len(fixed_str)
        output = []
        cur = 0

        vowels = self.ruleset.vowels
        consonants = self.ruleset.consonants
        patterns = self.ruleset.patterns

        while cur < length:
            start = cur
            matched = False

            # Check digit mapping if enabled
            if self.bengali_digits and fixed_str[cur].isdigit():
                digit_cp = 0x09E6 + (ord(fixed_str[cur]) - ord("0"))
                output.append(chr(digit_cp))
                cur += 1
                continue

            # Check Dari mapping
            if self.map_dari and fixed_str[cur] == ".":
                # Check for double dot .. or single dot
                if cur + 1 < length and fixed_str[cur + 1] == ".":
                    output.append("\u0965")  # ॥
                    cur += 2
                    continue
                else:
                    output.append("\u0964")  # ।
                    cur += 1
                    continue

            for pattern in patterns:
                find_len = len(pattern.find)
                end = cur + find_len
                if end <= length and fixed_str[start:end] == pattern.find:
                    prev = start - 1
                    if pattern.rules:
                        for rule in pattern.rules:
                            replace_ok = True
                            for m in rule.matches:
                                chk = end if m.type == "suffix" else prev
                                scope = m.scope

                                if scope == "punctuation":
                                    cond = (
                                        (chk < 0 if m.type == "prefix" else chk >= length)
                                        or not (
                                            fixed_str[chk].lower() in vowels
                                            or fixed_str[chk].lower() in consonants
                                        )
                                    )
                                elif scope == "vowel":
                                    cond = (
                                        chk >= 0 if m.type == "prefix" else chk < length
                                    ) and (fixed_str[chk].lower() in vowels)
                                elif scope == "consonant":
                                    cond = (
                                        chk >= 0 if m.type == "prefix" else chk < length
                                    ) and (fixed_str[chk].lower() in consonants)
                                elif scope == "exact":
                                    val = m.value
                                    if m.type == "suffix":
                                        s = end
                                        e = end + len(val)
                                    else:
                                        s = start - len(val)
                                        e = start
                                    cond = (s >= 0 and e <= length and fixed_str[s:e] == val)
                                else:
                                    cond = False

                                if m.negative:
                                    cond = not cond

                                if not cond:
                                    replace_ok = False
                                    break

                            if replace_ok:
                                output.append(rule.replace)
                                cur = end
                                matched = True
                                break

                    if matched:
                        break

                    # Default pattern replacement
                    output.append(pattern.replace)
                    cur = end
                    matched = True
                    break

            if not matched:
                output.append(fixed_str[cur])
                cur += 1

        raw_result = "".join(output)
        return sanitize_bengali_sequence(raw_result)
