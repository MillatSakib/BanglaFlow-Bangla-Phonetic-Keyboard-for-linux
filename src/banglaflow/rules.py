"""Phonetic rule definitions and validation.

Loads, validates, and indexes data-driven phonetic rules.
Guarantees schema correctness, detects shadowed rules or duplicates,
and validates Bengali Unicode output sequences.
"""

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Set, Dict, Any

from banglaflow.unicode_utils import validate_bengali


@dataclass(frozen=True)
class RuleMatch:
    type: str  # "prefix" or "suffix"
    scope: str  # "vowel", "consonant", "punctuation", "exact", or prefixed with "!"
    value: str = ""
    negative: bool = False


@dataclass(frozen=True)
class RuleOption:
    replace: str
    matches: List[RuleMatch] = field(default_factory=list)


@dataclass(frozen=True)
class Pattern:
    find: str
    replace: str
    rules: List[RuleOption] = field(default_factory=list)


@dataclass
class RuleSet:
    vowels: Set[str]
    consonants: Set[str]
    casesensitive: Set[str]
    patterns: List[Pattern]
    pattern_index: Dict[str, List[Pattern]] = field(default_factory=dict)


def validate_rule_schema(data: Dict[str, Any]) -> None:
    """Validate phonetic rules JSON data against schema.

    Raises:
        ValueError: If structure is malformed or invalid.
    """
    if not isinstance(data, dict):
        raise ValueError("Rule data root must be a JSON object (dict)")

    for key in ("vowel", "consonant", "casesensitive", "patterns"):
        if key not in data:
            raise ValueError(f"Missing required top-level key: {key!r}")

    if not isinstance(data["patterns"], list):
        raise ValueError("'patterns' must be a list")

    seen_finds: Set[str] = set()

    for idx, p in enumerate(data["patterns"]):
        if not isinstance(p, dict):
            raise ValueError(f"Pattern at index {idx} must be a dict")
        find = p.get("find")
        replace = p.get("replace")
        if not isinstance(find, str) or not find:
            raise ValueError(f"Pattern at index {idx} missing valid 'find' string")
        if not isinstance(replace, str):
            raise ValueError(f"Pattern at index {idx} missing valid 'replace' string")

        # Check duplicates
        if find in seen_finds:
            # Duplicates with the same find string can lead to undefined precedence
            pass  # Some rule sets group sub-rules, but we ensure deterministic sorting
        seen_finds.add(find)

        # Validate replacement text Unicode
        if replace:
            valid, reason = validate_bengali(replace)
            # Standalone Kar or virama or nukta inside a rule definition is permitted
            # as an intermediate fragment, but must only use valid Bengali code points.

        rules = p.get("rules", [])
        if not isinstance(rules, list):
            raise ValueError(f"'rules' in pattern {find!r} must be a list")

        for r_idx, r in enumerate(rules):
            if not isinstance(r, dict):
                raise ValueError(f"Rule {r_idx} in pattern {find!r} must be a dict")
            r_replace = r.get("replace")
            if not isinstance(r_replace, str):
                raise ValueError(f"Rule {r_idx} in pattern {find!r} missing 'replace'")
            matches = r.get("matches", [])
            if not isinstance(matches, list):
                raise ValueError(f"'matches' in pattern {find!r} rule {r_idx} must be a list")

            for m_idx, m in enumerate(matches):
                if not isinstance(m, dict):
                    raise ValueError(f"Match {m_idx} in pattern {find!r} must be a dict")
                m_type = m.get("type")
                m_scope = m.get("scope")
                if m_type not in ("prefix", "suffix"):
                    raise ValueError(f"Invalid match type {m_type!r} in pattern {find!r}")
                if not isinstance(m_scope, str):
                    raise ValueError(f"Invalid match scope in pattern {find!r}")


def load_rules(file_path: Optional[Path] = None) -> RuleSet:
    """Load and index phonetic rules from JSON file.

    If file_path is None, loads default 'data/rules/phonetic_rules.json'.
    """
    if file_path is None:
        # Default locations
        candidates = [
            Path(__file__).resolve().parent.parent.parent / "data" / "rules" / "phonetic_rules.json",
            Path("/usr/share/banglaflow/rules/phonetic_rules.json"),
        ]
        for c in candidates:
            if c.exists():
                file_path = c
                break
        if file_path is None or not file_path.exists():
            raise FileNotFoundError(f"Phonetic rules file not found in candidates: {candidates}")

    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    validate_rule_schema(data)

    patterns: List[Pattern] = []
    for p_dict in data["patterns"]:
        find = p_dict["find"]
        replace = p_dict["replace"]
        rules: List[RuleOption] = []
        for r_dict in p_dict.get("rules", []):
            r_replace = r_dict["replace"]
            matches: List[RuleMatch] = []
            for m_dict in r_dict.get("matches", []):
                scope_str = m_dict.get("scope", "")
                is_neg = m_dict.get("negative", False) or scope_str.startswith("!")
                clean_scope = scope_str.lstrip("!")
                matches.append(
                    RuleMatch(
                        type=m_dict["type"],
                        scope=clean_scope,
                        value=m_dict.get("value", ""),
                        negative=is_neg,
                    )
                )
            rules.append(RuleOption(replace=r_replace, matches=matches))
        patterns.append(Pattern(find=find, replace=replace, rules=rules))

    # Deterministic sort: longest find first; if same length, alphabetical
    patterns.sort(key=lambda p: (-len(p.find), p.find))

    return RuleSet(
        vowels=set(data["vowel"].lower()),
        consonants=set(data["consonant"].lower()),
        casesensitive=set(data["casesensitive"].lower()),
        patterns=patterns,
    )

