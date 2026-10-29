"""Candidate generation and ranking for BanglaFlow.

Produces primary phonetic conversion, rule ambiguity alternatives,
and frequency-ranked suggestions deterministically.
"""

from typing import List, Set, Tuple
from banglaflow.phonetic import PhoneticEngine
from banglaflow.dictionary import BengaliDictionary
from banglaflow.unicode_utils import validate_bengali


class CandidateGenerator:
    """Generates and ranks candidate Bengali words for phonetic inputs."""

    def __init__(self, engine: PhoneticEngine, dictionary: BengaliDictionary):
        self.engine = engine
        self.dictionary = dictionary

    def generate_candidates(self, latin_input: str, max_candidates: int = 9) -> List[str]:
        """Generate deterministically ranked candidates for a phonetic Latin input."""
        if not latin_input:
            return []

        primary = self.engine.convert(latin_input)
        candidates_set: Set[str] = {primary}

        # Generate phonetic variants for common Banglish transliteration ambiguities
        variants_input: Set[str] = set()

        # sh <-> Sh (শ vs ষ)
        if "sh" in latin_input.lower():
            variants_input.add(latin_input.replace("sh", "Sh"))
            variants_input.add(latin_input.replace("Sh", "sh"))
            variants_input.add(latin_input.replace("sh", "s"))

        # s <-> sh / Sh
        if "s" in latin_input.lower() and "sh" not in latin_input.lower():
            variants_input.add(latin_input.replace("s", "sh"))
            variants_input.add(latin_input.replace("s", "Sh"))

        # i <-> I (হ্রস্ব-ই vs দীর্ঘ-ঈ)
        if "i" in latin_input:
            variants_input.add(latin_input.replace("i", "I"))
        if "ee" in latin_input:
            variants_input.add(latin_input.replace("ee", "I"))

        # u <-> U (হ্রস্ব-উ vs দীর্ঘ-ঊ)
        if "u" in latin_input:
            variants_input.add(latin_input.replace("u", "U"))
        if "oo" in latin_input:
            variants_input.add(latin_input.replace("oo", "U"))

        # t <-> T, d <-> D, r <-> R, z <-> j
        if "t" in latin_input:
            variants_input.add(latin_input.replace("t", "T"))
        if "d" in latin_input:
            variants_input.add(latin_input.replace("d", "D"))
        if "r" in latin_input:
            variants_input.add(latin_input.replace("r", "R"))
            variants_input.add(latin_input.replace("r", "rr"))
        if "z" in latin_input:
            variants_input.add(latin_input.replace("z", "j"))
        if "j" in latin_input:
            variants_input.add(latin_input.replace("j", "z"))

        for v in variants_input:
            conv = self.engine.convert(v)
            if conv and validate_bengali(conv)[0]:
                candidates_set.add(conv)

        # Deterministic scoring:
        # Score = dictionary frequency + (500 bonus for primary rule result)
        scored_candidates: List[Tuple[int, str]] = []
        for cand in candidates_set:
            if not validate_bengali(cand)[0]:
                continue
            freq = self.dictionary.get_frequency(cand)
            bonus = 500 if cand == primary else 0
            total_score = freq + bonus
            scored_candidates.append((total_score, cand))

        # Sort by score descending, then alphabetically for stability
        scored_candidates.sort(key=lambda item: (-item[0], item[1]))

        result = [cand for _, cand in scored_candidates]
        return result[:max_candidates]

