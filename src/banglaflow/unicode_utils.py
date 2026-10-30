"""Unicode utilities and validation for Bengali text.

Enforces logical ordering and explicit sequence rules without applying
blanket normalization (NFC/NFKC/NFD), preserving precomposed characters
like ড় (U+09DC), ঢ় (U+09DD), য় (U+09DF) and vowel signs.
"""

from typing import Dict, Set, Tuple

# Independent Vowels
INDEPENDENT_VOWELS: Set[str] = {
    "\u0985",  # অ
    "\u0986",  # আ
    "\u0987",  # ই
    "\u0988",  # ঈ
    "\u0989",  # উ
    "\u098A",  # ঊ
    "\u098B",  # ঋ
    "\u098C",  # ঌ
    "\u098F",  # এ
    "\u0990",  # ঐ
    "\u0993",  # ও
    "\u0994",  # ঔ
}

# Consonants (including precomposed nukta forms and Khanda Ta)
BASE_CONSONANTS: Set[str] = {
    "\u0995",  # ক
    "\u0996",  # খ
    "\u0997",  # গ
    "\u0998",  # ঘ
    "\u0999",  # ঙ
    "\u099A",  # চ
    "\u099B",  # ছ
    "\u099C",  # জ
    "\u099D",  # ঝ
    "\u099E",  # ঞ
    "\u099F",  # ট
    "\u09A0",  # ঠ
    "\u09A1",  # ড
    "\u09A2",  # ঢ
    "\u09A3",  # ণ
    "\u09A4",  # ত
    "\u09A5",  # থ
    "\u09A6",  # দ
    "\u09A7",  # ধ
    "\u09A8",  # ন
    "\u09AA",  # প
    "\u09AB",  # ফ
    "\u09AC",  # ব
    "\u09AD",  # ভ
    "\u09AE",  # ম
    "\u09AF",  # য
    "\u09B0",  # র
    "\u09B2",  # ল
    "\u09B6",  # শ
    "\u09B7",  # ষ
    "\u09B8",  # স
    "\u09B9",  # হ
    "\u09DC",  # ড়
    "\u09DD",  # ঢ়
    "\u09DF",  # য়
    "\u09CE",  # ৎ (Khanda Ta)
    "\u09BD",  # ঽ (Avagraha)
}

# Dependent Vowel Signs (Kar)
DEPENDENT_VOWELS: Set[str] = {
    "\u09BE",  # া
    "\u09BF",  # ি
    "\u09C0",  # ী
    "\u09C1",  # ু
    "\u09C2",  # ূ
    "\u09C3",  # ৃ
    "\u09C4",  # ৄ
    "\u09C7",  # ে
    "\u09C8",  # ৈ
    "\u09CB",  # ো
    "\u09CC",  # ৌ
    "\u09E2",  # ৢ
    "\u09E3",  # ৣ
}

# Modifiers
HASANTA: str = "\u09CD"  # ্ (Virama)
NUKTA: str = "\u09BC"    # ়
ANUSVARA: str = "\u0982" # ং
VISARGA: str = "\u0983"  # ঃ
CANDRABINDU: str = "\u0981"  # ঁ

MODIFIERS: Set[str] = {ANUSVARA, VISARGA, CANDRABINDU}

# Digits
BENGALI_DIGITS: Set[str] = {chr(cp) for cp in range(0x09E6, 0x09F0)}

# Special Characters
BENGALI_PUNCTUATION: Set[str] = {
    "\u0964",  # । (Dari)
    "\u0965",  # ॥ (Double Dari)
    "\u09F3",  # ৳ (Bengali Taka Sign)
}

# Zero Width Controls
ZWJ: str = "\u200D"
ZWNJ: str = "\u200C"
ZERO_WIDTH_CHARS: Set[str] = {ZWJ, ZWNJ}

KAR_TO_INDEPENDENT: Dict[str, str] = {
    "\u09BE": "\u0986",  # া -> আ
    "\u09BF": "\u0987",  # ি -> ই
    "\u09C0": "\u0988",  # ী -> ঈ
    "\u09C1": "\u0989",  # ু -> উ
    "\u09C2": "\u098A",  # ূ -> ঊ
    "\u09C3": "\u098B",  # ৃ -> ঋ
    "\u09C7": "\u098F",  # ে -> এ
    "\u09C8": "\u0990",  # ৈ -> ঐ
    "\u09CB": "\u0993",  # ো -> ও
    "\u09CC": "\u0994",  # ৌ -> ঔ
}


def is_bengali_consonant(c: str) -> bool:
    """Check if character is a Bengali consonant."""
    return c in BASE_CONSONANTS


def is_bengali_independent_vowel(c: str) -> bool:
    """Check if character is an independent Bengali vowel."""
    return c in INDEPENDENT_VOWELS


def is_bengali_dependent_vowel(c: str) -> bool:
    """Check if character is a dependent Bengali vowel sign (Kar)."""
    return c in DEPENDENT_VOWELS


def is_bengali_modifier(c: str) -> bool:
    """Check if character is a Bengali modifier sign (Anusvara, Visarga, Candrabindu)."""
    return c in MODIFIERS


def is_bengali_digit(c: str) -> bool:
    """Check if character is a Bengali digit."""
    return c in BENGALI_DIGITS


def sanitize_bengali_sequence(text: str) -> str:
    """Ensure logical correctness of Bengali Unicode output sequences.

    Transforms invalid dependent vowels without consonant into independent vowels,
    removes illegal consecutive or stray hasantas, and replaces stray ya-phala with য.
    Does NOT decompose precomposed characters (ড়, ঢ়, য়).
    """
    if not text:
        return ""

    res = []
    for c in text:
        # Check hasanta
        if c == HASANTA:
            if not res:
                continue
            prev = res[-1]
            if prev not in BASE_CONSONANTS and prev != NUKTA:
                continue
            res.append(c)
        # Check dependent vowel
        elif c in DEPENDENT_VOWELS:
            if not res:
                res.append(KAR_TO_INDEPENDENT.get(c, c))
                continue
            prev = res[-1]
            if prev in BASE_CONSONANTS or prev == NUKTA:
                res.append(c)
            elif prev == HASANTA:
                # E.g. hasanta followed by kar
                res.pop()
                if res and (res[-1] in BASE_CONSONANTS or res[-1] == NUKTA):
                    res.append(c)
                else:
                    res.append(KAR_TO_INDEPENDENT.get(c, c))
            else:
                res.append(KAR_TO_INDEPENDENT.get(c, c))
        # Check modifiers
        elif c in MODIFIERS:
            if not res:
                res.append(c)
                continue
            prev = res[-1]
            if prev.isspace() or (prev.isascii() and not prev.isalnum()):
                continue
            res.append(c)
        else:
            res.append(c)

    return "".join(res)


def validate_bengali(text: str) -> Tuple[bool, str]:
    """Validate logical Bengali Unicode string structure.

    Checks:
      1. Characters outside allowed set.
      2. Dependent vowel with no base.
      3. Double dependent vowels.
      4. Consecutive hasanta.
      5. Hasanta at invalid positions.
      6. Stray ZWJ/ZWNJ.
      7. Nukta misuse.

    Returns:
      (True, "") if valid, (False, "reason") if invalid.
    """
    if not text:
        return True, ""

    length = len(text)
    for i, c in enumerate(text):
        # 1. Allowed set check
        is_bengali = (
            c in BASE_CONSONANTS
            or c in INDEPENDENT_VOWELS
            or c in DEPENDENT_VOWELS
            or c in MODIFIERS
            or c == HASANTA
            or c == NUKTA
            or c in BENGALI_DIGITS
            or c in BENGALI_PUNCTUATION
            or c in ZERO_WIDTH_CHARS
        )
        is_allowed_ascii = (
            c.isascii() and (c.isalnum() or c.isspace() or (c in r"""`~!@#$%^&*()-_=+[{]}\|;:'",<.>/? """))
        )
        is_allowed_extra = c in "“”‘’—–•…₹"

        if not (is_bengali or is_allowed_ascii or is_allowed_extra):
            return False, f"Character outside allowed set at index {i}: U+{ord(c):04X}"

        # 2 & 3. Dependent Vowel Checks
        if c in DEPENDENT_VOWELS:
            if i == 0:
                return False, f"Dependent vowel at string start (index {i}): U+{ord(c):04X}"
            prev = text[i - 1]
            if prev in DEPENDENT_VOWELS:
                return False, f"Double dependent vowels at index {i-1}-{i}: U+{ord(prev):04X} U+{ord(c):04X}"
            if prev == HASANTA:
                return False, f"Dependent vowel immediately following hasanta at index {i}: U+{ord(c):04X}"
            if prev in INDEPENDENT_VOWELS:
                return False, f"Dependent vowel following independent vowel at index {i}: U+{ord(c):04X}"
            if prev.isspace() or prev in BENGALI_PUNCTUATION or (prev.isascii() and not prev.isalnum()):
                return False, f"Dependent vowel without consonant base at index {i}: U+{ord(c):04X}"

        # 4 & 5. Hasanta Checks
        if c == HASANTA:
            if i == 0:
                return False, f"Hasanta at string start (index {i})"
            prev = text[i - 1]
            if prev == HASANTA:
                return False, f"Consecutive hasanta at index {i-1}-{i}"
            if prev in INDEPENDENT_VOWELS:
                return False, f"Hasanta following independent vowel at index {i}"
            if prev in DEPENDENT_VOWELS:
                return False, f"Hasanta following dependent vowel at index {i}"
            if prev.isspace() or prev in BENGALI_PUNCTUATION or (prev.isascii() and not prev.isalnum()):
                return False, f"Hasanta at invalid position (after punctuation/space) at index {i}"

        # 6. Stray ZWJ / ZWNJ Checks
        if c in ZERO_WIDTH_CHARS:
            if i == 0:
                return False, f"Stray zero-width character at string start (index {i})"
            prev = text[i - 1]
            if not (prev == HASANTA or prev in BASE_CONSONANTS or prev == NUKTA):
                return False, f"Stray zero-width character following U+{ord(prev):04X} at index {i}"

        # 7. Nukta Misuse Checks
        if c == NUKTA:
            if i == 0:
                return False, f"Nukta at string start (index {i})"
            prev = text[i - 1]
            if prev not in BASE_CONSONANTS:
                return False, f"Nukta misuse: must immediately follow a base consonant, got U+{ord(prev):04X}"

        # 8. Modifiers (Anusvara, Visarga, Candrabindu) position check
        if c in MODIFIERS:
            if i == 0:
                if length == 1:
                    continue
                return False, f"Modifier at string start (index {i}): U+{ord(c):04X}"
            prev = text[i - 1]
            if prev.isspace() or (prev.isascii() and not prev.isalnum()):
                return False, f"Modifier following space or punctuation at index {i}"

    return True, ""


def assert_valid_bengali(text: str) -> None:
    """Raise ValueError if Bengali text is invalid."""
    valid, reason = validate_bengali(text)
    if not valid:
        raise ValueError(f"Bengali Unicode Validation Error: {reason} in {text!r}")
