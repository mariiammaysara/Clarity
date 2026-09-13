"""
Clarity - Clinical Note Keyword Extractor.

ARCHITECTURE & DESIGN RATIONALE:
This module implements a deterministic, rule-based keyword matching algorithm
to identify whether clinical documentation elements from a ChecklistField
are mentioned within a raw clinical note.

CRITICAL KNOWN LIMITATION - NEGATION UNAWARENESS:
- This is NOT an LLM, transformer, or clinical Named Entity Recognition (NER) model.
- It performs direct case-insensitive substring searching without syntactic parsing.
- Consequently, negated statements (e.g., "denies chest pain", "no radiation",
  "patient is without SOB or diaphoresis") will be flagged as FOUND (True)
  because the target keywords exist in the text.
- In clinical documentation integrity (CDI), recording the absence of a symptom
  is often valid documentation that the physician inquired about the symptom.
  However, this simple matcher cannot differentiate between affirmation,
  negation, or family history.

FUTURE WORK / EXTENSION POINTS:
- Integration of a clinical negation detection algorithm (such as NegEx or ConText).
- Upgrading to biomedical transformer-based NER (e.g., BioClinicalBERT).
"""

from dataclasses import dataclass
import sys
from pathlib import Path

# Support running directly (python src/extractor.py) or as part of a package
try:
    from src.checklist import ChecklistField, load_checklist
except ImportError:
    from checklist import ChecklistField, load_checklist


@dataclass
class ExtractionResult:
    """Represents the extraction outcome for a single checklist field.

    Attributes:
        field_name: The unique snake_case name of the checklist field.
        found: True if any keyword for the field was detected in the text; False otherwise.
        matched_keyword: The checklist keyword string that triggered the match, or None.
        matched_context: A short text snippet (~40 characters before and after the keyword)
            serving as clinical documentation evidence, or None.
    """

    field_name: str
    found: bool
    matched_keyword: str | None
    matched_context: str | None


def extract_fields(
    note_text: str, fields: list[ChecklistField], context_window: int = 40
) -> list[ExtractionResult]:
    """Extracts presence of checklist fields from clinical note text using keyword matching.

    Performs case-insensitive search for keywords defined in each ChecklistField.
    Matching halts upon the first matched keyword per field.

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

                results.append(
                    ExtractionResult(
                        field_name=field.field_name,
                        found=True,
                        matched_keyword=kw,
                        matched_context=snippet,
                    )
                )
                break

        if not match_found:
            results.append(
                ExtractionResult(
                    field_name=field.field_name,
                    found=False,
                    matched_keyword=None,
                    matched_context=None,
                )
            )

    return results


if __name__ == "__main__":
    print("=" * 80)
    print("CLARITY - EXTRACTOR DEMONSTRATION & LIMITATION ANALYSIS")
    print("=" * 80)

    checklist = load_checklist("chest_pain")

    # Focus on radiation and associated symptoms for clean comparison
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
        status = "[FOUND]" if res.found else "[MISSING]"
        print(f"{status:10} Field: {res.field_name}")
        print(f"           Matched Keyword : {res.matched_keyword}")
        print(f"           Context Snippet : {res.matched_context}")

    print("\n" + "-" * 80)
    print("--- TEST NOTE 2: NEGATED DOCUMENTATION (KNOWN LIMITATION DEMO) ---")
    print(f"Note: \"{note_negated}\"\n")
    results_negated = extract_fields(note_negated, target_fields)
    for res in results_negated:
        status = "[FOUND]" if res.found else "[MISSING]"
        print(f"{status:10} Field: {res.field_name}")
        print(f"           Matched Keyword : {res.matched_keyword}")
        print(f"           Context Snippet : {res.matched_context}")

    print("\n" + "=" * 80)
    print("CRITICAL OBSERVATION ON NEGATION:")
    print("Notice how in Note 2, the note states 'Patient denies radiation to left arm'")
    print("and 'without diaphoresis'. However, because this rule-based extractor")
    print("performs simple keyword matching without negation parsing, it flags both")
    print("as FOUND (False Positives for presence of the symptom).")
    print("This confirms the design specification and documents the exact limitation.")
    print("=" * 80)
