"""
Clarity - Clinical Note Keyword & Negation Extractor.

ARCHITECTURE & DESIGN RATIONALE:
This module implements rule-based keyword matching combined with localized
pre-negation detection (via negation.py) to assess whether clinical documentation
elements are documented as present (found), explicitly denied (negated),
or absent (missing).

STATUS CATEGORIES:
- "found": Target keyword detected without an active preceding negation trigger.
- "negated": Target keyword detected, but preceded by a clinical negation trigger
  (e.g., "denies", "no", "without") within the same sentence/clause.
- "missing": No matching keyword for this field was identified in the text.

HEURISTIC EXTENSION:
Unlike simple substring search, this module differentiates between affirmative
documentation and explicit negation, preventing false positives when clinicians
document that a red flag or symptom was absent.
"""

import re
from dataclasses import dataclass
from pathlib import Path

# Support running directly or as part of a package
try:
    from src.checklist import ChecklistField, load_checklist
    from src.negation import is_negated
except ImportError:
    from checklist import ChecklistField, load_checklist
    from negation import is_negated


# Domain-specific regex patterns for clinical parameters with variable linguistic structure
FIELD_REGEX_PATTERNS: dict[str, list[re.Pattern[str]]] = {
    "onset_and_duration": [
        # "started ... ago" (e.g., started 2 hours ago, started yesterday morning ago)
        re.compile(r"\bstarted\b.{1,60}?\bago\b", re.IGNORECASE),
        # "began ... prior to" (e.g., began 3 hours prior to arrival)
        re.compile(r"\bbegan\b.{1,60}?\bprior to\b", re.IGNORECASE),
        # "hours ago", "minutes ago", "days ago"
        re.compile(r"\b(?:\w+\s+)?(?:hours?|hrs?|minutes?|mins?|days?)\s+ago\b", re.IGNORECASE),
        # "acute onset", "gradual onset", "sudden onset"
        re.compile(r"\b(?:acute|gradual|sudden)\s+onset\b", re.IGNORECASE),
        # "time of onset", "onset prior to"
        re.compile(r"\b(?:time of onset|onset prior to)\b", re.IGNORECASE),
        # duration phrases: "2 hours duration", "duration of 3 hours"
        re.compile(r"\b(?:\w+\s+)?(?:hours?|hrs?|minutes?|mins?|days?)\s+duration\b", re.IGNORECASE),
        re.compile(r"\bduration of\b", re.IGNORECASE),
        # temporal onset anchors: "since yesterday", "since this morning"
        re.compile(r"\b(?:onset|started|began|since)\s+(?:yesterday|this morning|last night)\b", re.IGNORECASE),
    ],
    "provocative_and_palliative_factors": [
        # medication response: "relief with nitroglycerin", "nitroglycerin relief", "relief with aspirin"
        re.compile(r"\brelief with (?:nitroglycerin|ntg|aspirin|medications?|meds)\b", re.IGNORECASE),
        re.compile(r"\b(?:nitroglycerin|ntg|aspirin)\s+relief\b", re.IGNORECASE),
        # "minimal relief", "partial relief", "no relief", "complete relief"
        re.compile(r"\b(?:minimal|partial|no|mild|moderate|complete|temporary)\s+relief\b", re.IGNORECASE),
        # "relieved by ...", "relieved with ..."
        re.compile(r"\brelieved\s+(?:by|with|after)\b", re.IGNORECASE),
        # exertion triggers: "walking up stairs", "climbing stairs", "worse with exertion"
        re.compile(r"\bwalking\s+(?:up\s+)?stairs\b", re.IGNORECASE),
        re.compile(r"\bclimbing\s+stairs\b", re.IGNORECASE),
        re.compile(r"\bworse\s+with\s+(?:exertion|activity|walking|exercise|movement|stairs)\b", re.IGNORECASE),
        re.compile(r"\b(?:exertional|exertion)\s*(?:pain|chest pain|angina|discomfort)?\b", re.IGNORECASE),
        re.compile(r"\bpain\s+(?:on|with)\s+(?:exertion|exercise|walking)\b", re.IGNORECASE),
        re.compile(r"\bpleuritic\s+variation\b", re.IGNORECASE),
    ],
}


@dataclass
class ExtractionResult:
    """Represents the extraction outcome for a single checklist field.

    Attributes:
        field_name: The unique snake_case name of the checklist field.
        status: Detection status: 'found', 'negated', or 'missing'.
        matched_keyword: The checklist keyword string that triggered the match, or None.
        matched_context: A short text snippet (~40 characters before and after the keyword)
            serving as clinical documentation evidence, or None.
    """

    field_name: str
    status: str
    matched_keyword: str | None
    matched_context: str | None


def extract_fields(
    note_text: str, fields: list[ChecklistField], context_window: int = 40
) -> list[ExtractionResult]:
    """Extracts presence or negation of checklist fields from clinical note text.

    Combines domain-specific regex pattern evaluation with case-insensitive
    keyword search for clinical elements. Evaluates matched occurrences using
    clinical negation detection.

    Args:
        note_text: Raw clinical note text string.
        fields: List of ChecklistField objects to search for.
        context_window: Number of characters before and after the match to extract
            as evidence context (default: 40).

    Returns:
        A list of ExtractionResult objects preserving the input fields order.
    """
    results: list[ExtractionResult] = []
    lower_note = note_text.lower()

    for field in fields:
        match_found = False

        # 1. Specialized regex pattern evaluation for complex clinical phrasing
        patterns = FIELD_REGEX_PATTERNS.get(field.field_name, [])
        for pattern in patterns:
            match = pattern.search(note_text)
            if match:
                start_idx = match.start()
                end_idx = match.end()
                matched_str = match.group(0)

                # Extract surrounding snippet for auditability / report evidence
                ctx_start = max(0, start_idx - context_window)
                ctx_end = min(len(note_text), end_idx + context_window)

                snippet = note_text[ctx_start:ctx_end].replace("\n", " ").strip()
                if ctx_start > 0:
                    snippet = f"...{snippet}"
                if ctx_end < len(note_text):
                    snippet = f"{snippet}..."

                negated = is_negated(note_text, start_idx)
                status = "negated" if negated else "found"

                results.append(
                    ExtractionResult(
                        field_name=field.field_name,
                        status=status,
                        matched_keyword=matched_str,
                        matched_context=snippet,
                    )
                )
                match_found = True
                break

        if match_found:
            continue

        # 2. Checklist keyword search (supports 'word ... word' ellipsis patterns & exact substring)
        for kw in field.keywords:
            start_idx = -1
            end_idx = -1
            matched_str = kw

            if "..." in kw:
                parts = [re.escape(p.strip()) for p in kw.split("...") if p.strip()]
                if len(parts) == 2:
                    ellipsis_pattern = re.compile(
                        rf"\b{parts[0]}\b.{{1,60}}?\b{parts[1]}\b", re.IGNORECASE
                    )
                    m = ellipsis_pattern.search(note_text)
                    if m:
                        start_idx = m.start()
                        end_idx = m.end()
                        matched_str = m.group(0)
            else:
                kw_lower = kw.lower()
                start_idx = lower_note.find(kw_lower)
                if start_idx != -1:
                    end_idx = start_idx + len(kw_lower)

            if start_idx != -1:
                match_found = True

                # Extract surrounding snippet for auditability / report evidence
                ctx_start = max(0, start_idx - context_window)
                ctx_end = min(len(note_text), end_idx + context_window)

                snippet = note_text[ctx_start:ctx_end].replace("\n", " ").strip()
                if ctx_start > 0:
                    snippet = f"...{snippet}"
                if ctx_end < len(note_text):
                    snippet = f"{snippet}..."

                # Determine if the finding is negated or affirmed
                negated = is_negated(note_text, start_idx)
                status = "negated" if negated else "found"

                results.append(
                    ExtractionResult(
                        field_name=field.field_name,
                        status=status,
                        matched_keyword=matched_str,
                        matched_context=snippet,
                    )
                )
                break

        if not match_found:
            results.append(
                ExtractionResult(
                    field_name=field.field_name,
                    status="missing",
                    matched_keyword=None,
                    matched_context=None,
                )
            )

    return results


if __name__ == "__main__":
    print("=" * 80)
    print("CLARITY - EXTRACTOR WITH NEGATION DETECTION DEMONSTRATION")
    print("=" * 80)

    checklist = load_checklist("chest_pain")

    # Focus on radiation, character, and associated symptoms for clean comparison
    target_fields = [
        f for f in checklist if f.field_name in ("pain_radiation", "pain_character", "associated_anginal_symptoms")
    ]

    # Example 1: Affirmative clinical documentation
    note_affirmative = (
        "Patient presents with acute pressure sensation. "
        "Reports crushing chest pain with radiation to left arm since 2 hours ago. "
        "Complains of diaphoresis and nausea."
    )

    # Example 2: Explicitly negated clinical documentation
    note_negated = (
        "Patient denies chest pain radiation. "
        "Denies radiation to left arm or jaw. "
        "Patient is without diaphoresis, shortness of breath, or palpitations."
    )

    print("\n--- TEST NOTE 1: AFFIRMATIVE DOCUMENTATION ---")
    print(f"Note: \"{note_affirmative}\"\n")
    results_affirmative = extract_fields(note_affirmative, target_fields)
    for res in results_affirmative:
        print(f"[{res.status.upper():7}] Field: {res.field_name}")
        print(f"          Matched Keyword : {res.matched_keyword}")
        print(f"          Context Snippet : {res.matched_context}")

    print("\n" + "-" * 80)
    print("--- TEST NOTE 2: NEGATED DOCUMENTATION (NEGATION HANDLING DEMO) ---")
    print(f"Note: \"{note_negated}\"\n")
    results_negated = extract_fields(note_negated, target_fields)
    for res in results_negated:
        print(f"[{res.status.upper():7}] Field: {res.field_name}")
        print(f"          Matched Keyword : {res.matched_keyword}")
        print(f"          Context Snippet : {res.matched_context}")

    print("\n" + "=" * 80)
    print("OBSERVATION:")
    print("With negation detection enabled, symptoms like 'radiation to left arm'")
    print("and 'diaphoresis' in Note 2 are now accurately classified as [NEGATED]")
    print("instead of false-positive [FOUND]!")
    print("=" * 80)
