"""
Clarity - Clinical Negation Detection Module.

DESIGN RATIONALE & HEURISTIC ARCHITECTURE:
This module provides a lightweight, rule-based clinical negation detection algorithm.
It identifies whether a matched clinical keyword is preceded by a negation trigger
within a localized window in the same sentence/clause.

HOW IT WORKS:
1. Identifies the preceding clause/sentence boundary (e.g., '.', ';', '?', '!', newline)
   so negation in an earlier sentence does not inappropriately spill over.
2. Extracts up to `window` words (default: 6) immediately preceding the keyword start index.
3. Scans for standardized clinical negation trigger phrases (e.g., "denies", "no", "without").
4. If an adversative conjunction (e.g., "but", "however") occurs after a negation trigger,
   the negation scope is considered terminated.

KNOWN LIMITATIONS & ASSUMPTIONS:
- Heuristic-based word window: Does not perform full syntactic dependency parsing.
- Double negation or complex grammatical structures (e.g., "cannot rule out")
  may not be accurately resolved.
- Negation appearing AFTER the keyword (post-negation, e.g., "chest pain was denied")
  is outside this pre-negation window scope.
"""

import re

# Standard clinical negation triggers commonly observed in medical documentation
NEGATION_TRIGGERS: list[str] = [
    "denies",
    "denied",
    "denying",
    "no",
    "without",
    "negative for",
    "ruled out",
    "not",
    "absence of",
]

# Boundaries that terminate sentence/clause scope
SENTENCE_TERMINATORS = re.compile(r"[.!?;\n]")

# Adversative conjunctions that terminate negation scope within a sentence
ADVERSATIVE_CONJUNCTIONS = re.compile(r"\b(but|however|although|except)\b", re.IGNORECASE)


def is_negated(text: str, keyword_start_index: int, window: int = 6) -> bool:
    """Determines whether a clinical keyword occurrence is preceded by a negation trigger.

    Searches backward from keyword_start_index within the current sentence boundary
    up to `window` words for any clinical negation trigger.

    Args:
        text: The full clinical note text.
        keyword_start_index: The character index in text where the matched keyword begins.
        window: Maximum number of preceding words to inspect for negation triggers (default: 6).

    Returns:
        True if an active negation trigger is identified; False otherwise.
    """
    if keyword_start_index <= 0 or keyword_start_index > len(text):
        return False

    preceding_text = text[:keyword_start_index]

    # Find the most recent sentence boundary before the keyword
    matches = list(SENTENCE_TERMINATORS.finditer(preceding_text))
    if matches:
        last_boundary = matches[-1].end()
        clause = preceding_text[last_boundary:]
    else:
        clause = preceding_text

    # Extract words in the current clause
    words = clause.strip().split()
    if not words:
        return False

    # Inspect up to `window` words preceding the keyword
    window_words = words[-window:]
    window_text = " ".join(window_words).lower()

    # Clean punctuation except spaces and hyphens for regex matching
    cleaned_window = re.sub(r"[^\w\s-]", " ", window_text)

    # Check for presence of any negation trigger
    for trigger in NEGATION_TRIGGERS:
        trigger_pattern = rf"\b{re.escape(trigger.strip())}\b"
        match = re.search(trigger_pattern, cleaned_window)
        if match:
            # Check if an adversative conjunction (e.g. 'but', 'however') follows the trigger
            text_after_trigger = cleaned_window[match.end():]
            if ADVERSATIVE_CONJUNCTIONS.search(text_after_trigger):
                # Negation scope was broken by 'but' or similar conjunction
                continue
            return True

    return False


if __name__ == "__main__":
    print("=" * 70)
    print("TESTING NEGATION DETECTION MODULE (src/negation.py)")
    print("=" * 70)

    test_cases = [
        ("Patient denies chest pain radiation.", "chest pain radiation", True),
        ("Patient presents with acute chest pain radiation.", "chest pain radiation", False),
        ("Patient is without diaphoresis, dyspnea, or syncope.", "diaphoresis", True),
        ("Patient is without diaphoresis, dyspnea, or syncope.", "dyspnea", True),
        ("Denies fever. Patient has neck stiffness.", "neck stiffness", False),
        ("Denies fever but reports neck stiffness.", "neck stiffness", False),
        ("Fundoscopy confirms no papilledema.", "papilledema", True),
        ("No history of cancer.", "history of cancer", True),
    ]

    for sentence, target, expected in test_cases:
        idx = sentence.lower().find(target.lower())
        detected = is_negated(sentence, idx) if idx != -1 else False
        status = "PASS" if detected == expected else "FAIL"
        print(f"[{status}] Text: \"{sentence}\"")
        print(f"       Target: \"{target}\" | Negated: {detected} (Expected: {expected})\n")
