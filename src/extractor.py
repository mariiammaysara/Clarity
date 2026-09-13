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

from dataclasses import dataclass
from pathlib import Path

# Support running directly or as part of a package
try:
    from src.checklist import ChecklistField, load_checklist
    from src.negation import is_negated
except ImportError:
    from checklist import ChecklistField, load_checklist
    from negation import is_negated


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

    Performs case-insensitive search for keywords defined in each ChecklistField.
    Matching halts upon the first matched keyword per field, which is then evaluated
    by the negation detection heuristic.

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

        for kw in field.keywords:
            kw_lower = kw.lower()
            start_idx = lower_note.find(kw_lower)

            if start_idx != -1:
                match_found = True
                end_idx = start_idx + len(kw_lower)

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
                        matched_keyword=kw,
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
