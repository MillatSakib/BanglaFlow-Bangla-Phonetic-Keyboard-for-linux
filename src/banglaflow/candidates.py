"""Candidate generation and ranking for BanglaFlow.

Produces primary phonetic conversion, rule ambiguity alternatives,
and frequency-ranked suggestions deterministically.
"""

from typing import Dict, List, Set, Tuple
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

        # Candidate pool: word -> score
        pool: Dict[str, int] = {}

        # 1. Phonetic variants of Latin input
        variants_input: Set[str] = {latin_input}
        lower_input = latin_input.lower()

        # sh <-> Sh (শ vs ষ)
        if "sh" in lower_input:
            variants_input.add(latin_input.replace("sh", "Sh"))
            variants_input.add(latin_input.replace("Sh", "sh"))
            variants_input.add(latin_input.replace("sh", "s"))
            variants_input.add(latin_input.replace("Sh", "s"))

        # s <-> sh / Sh
        if "s" in lower_input and "sh" not in lower_input:
            variants_input.add(latin_input.replace("s", "sh"))
            variants_input.add(latin_input.replace("s", "Sh"))

        # c <-> ch / chh
        if "c" in lower_input and "ch" not in lower_input:
            variants_input.add(latin_input.replace("c", "ch"))
        if "ch" in lower_input:
            variants_input.add(latin_input.replace("ch", "c"))
            variants_input.add(latin_input.replace("ch", "chh"))

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

        # o <-> O (অ vs ও-কার)
        if "o" in latin_input:
            variants_input.add(latin_input.replace("o", "O"))
        if "O" in latin_input:
            variants_input.add(latin_input.replace("O", "o"))

        # v <-> bh
        if "v" in lower_input:
            variants_input.add(latin_input.replace("v", "bh"))
            variants_input.add(latin_input.replace("V", "bh"))
        if "bh" in lower_input:
            variants_input.add(latin_input.replace("bh", "v"))

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

        # Double consonant <-> Z-fola / common spelling variants (e.g. somossa -> সমস্যা)
        if "ss" in lower_input:
            variants_input.add(latin_input.replace("ss", "sy"))
        if "nn" in lower_input:
            variants_input.add(latin_input.replace("nn", "ny"))
        if "kk" in lower_input:
            variants_input.add(latin_input.replace("kk", "ky"))
        if "tt" in lower_input:
            variants_input.add(latin_input.replace("tt", "ty"))
        if "mm" in lower_input:
            variants_input.add(latin_input.replace("mm", "my"))
        if "cc" in lower_input:
            variants_input.add(latin_input.replace("cc", "cy"))

        # Convert each variant to Bengali root
        bengali_roots: Set[str] = {primary}
        for v in variants_input:
            conv = self.engine.convert(v)
            if conv and validate_bengali(conv)[0]:
                bengali_roots.add(conv)

        # 2. Exact matches from dictionary for all roots
        # The primary conversion is ALWAYS candidate #0 (shown in edit panel),
        # so suggestions_pool only collects alternative relevant candidates.
        suggestions_pool: Dict[str, int] = {}

        all_roots = [primary] + list(bengali_roots)
        for root in all_roots:
            exact_matches = self.dictionary.find_exact_matches(root)
            for w in exact_matches:
                if w != primary:
                    suggestions_pool[w] = max(
                        suggestions_pool.get(w, 0), self.dictionary.get_frequency(w) + 2000
                    )

        # 3. Add phonetic roots to suggestions
        for root in bengali_roots:
            if root != primary:
                base_score = self.dictionary.get_frequency(root)
                suggestions_pool[root] = max(suggestions_pool.get(root, 0), base_score + 500)

        # 4. Prefix autocomplete matches if length >= 2
        if len(latin_input) >= 2:
            prefix_matches = self.dictionary.find_prefix_matches(primary, max_matches=25)
            for w in prefix_matches:
                if w != primary and w not in suggestions_pool:
                    suggestions_pool[w] = self.dictionary.get_frequency(w)

            # Also check prefix matches for variants if pool is small
            if len(suggestions_pool) < max_candidates:
                for root in bengali_roots:
                    if root != primary:
                        for w in self.dictionary.find_prefix_matches(root, max_matches=10):
                            if w != primary and w not in suggestions_pool:
                                suggestions_pool[w] = self.dictionary.get_frequency(w)

        # Filter valid Bengali
        scored: List[Tuple[int, int, str]] = []
        for cand, score in suggestions_pool.items():
            valid, _ = validate_bengali(cand)
            if valid:
                scored.append((score, len(cand), cand))

        # Sort suggestions: score DESC, length ASC, alphabetical ASC
        scored.sort(key=lambda item: (-item[0], item[1], item[2]))

        # Primary conversion is ALWAYS #0 (shown in edit panel),
        # followed by the most relevant suggestions in order.
        result = [primary] + [cand for _, _, cand in scored]
        return result[:max_candidates]

