"""
Clarity - Clinical Note Test Fixtures & Sample Dataset.

PURPOSE:
This module provides standardized, realistic clinical note fixtures across
various clinical documentation scenarios (comprehensive, deficient/incomplete,
and negated). It serves as a fixed test harness for automated evaluation,
interactive CLI demonstrations, and validation of the documentation integrity
analyzer.
"""

from typing import Any

# Standardized sample clinical notes covering chest_pain and headache
SAMPLE_NOTES: list[dict[str, Any]] = [
    {
        "id": "cp_complete",
        "condition": "chest_pain",
        "label": "Comprehensive Emergency Department ACS Documentation",
        "note_text": (
            "A 58-year-old male with a history of HTN, DM, and CAD with prior stent "
            "presents with acute onset retrosternal squeezing chest pain of 2 hours duration, "
            "worse with exertion and partially relieved by rest. Pain features radiation to left arm "
            "accompanied by diaphoresis and dyspnea. Initial hemodynamic evaluation reveals "
            "blood pressure 148/92 and heart rate 86 bpm. 12-lead ECG demonstrates normal sinus "
            "rhythm with no ST elevation or T-wave inversion; initial high-sensitivity troponin "
            "is within normal limits."
        ),
        "expected_note": "Should achieve 100% completeness score with all HIGH and MEDIUM priority elements documented.",
    },
    {
        "id": "cp_incomplete",
        "condition": "chest_pain",
        "label": "Deficient / Hurried Walk-in Clinic Note",
        "note_text": (
            "Patient walked into urgent care stating he has felt achy chest discomfort "
            "off and on since yesterday morning. He took two aspirins at home with minimal relief. "
            "Lungs clear to auscultation bilaterally. Patient advised to go to emergency department "
            "if pain persists."
        ),
        "expected_note": "Should show a very low completeness score (missing ECG, troponin, vitals, radiation, character).",
    },
    {
        "id": "cp_negated",
        "condition": "chest_pain",
        "label": "Explicit Negation Demonstration (False-Positive Baseline)",
        "note_text": (
            "62-year-old female presents for routine follow-up. Patient reports mild atypical "
            "epigastric discomfort but specifically denies radiation to left arm or jaw. "
            "Patient is without diaphoresis, dyspnea, or exertional pain. No prior MI or known CAD."
        ),
        "expected_note": "With negation detection, denied items (radiation, diaphoresis, CAD) are recognized as negated, preserving a realistic low score.",
    },
    {
        "id": "ha_complete",
        "condition": "headache",
        "label": "Comprehensive Secondary Headache Workup Note",
        "note_text": (
            "A 34-year-old female presents with sudden onset thunderclap headache that peaked "
            "in seconds while exercising. Physical exam is notable for fever with marked "
            "neck stiffness and meningismus; neurological exam reveals subtle cranial nerve palsy "
            "and altered mental status. Urgent fundoscopy is negative for papilledema; "
            "patient denies history of cancer or immunocompromised state."
        ),
        "expected_note": "Should show high completeness score capturing the core red flags from the SNOOP10 framework.",
    },
    {
        "id": "ha_incomplete",
        "condition": "headache",
        "label": "Deficient Primary Headache Note Missing Red Flags",
        "note_text": (
            "Patient comes in complaining of a dull throbbing headache on the right temple "
            "that started this morning. States work has been stressful this week. "
            "Cranial nerves grossly intact per brief exam; prescribed ibuprofen and recommended rest."
        ),
        "expected_note": "Should show near-zero completeness score due to complete lack of red-flag documentation.",
    },
    {
        "id": "ha_negated",
        "condition": "headache",
        "label": "Secondary Headache Rule-Out Note with Negated Red Flags",
        "note_text": (
            "Patient presents with persistent bilateral tension-type headache. Exam confirms "
            "no neck stiffness or meningismus, and patient denies focal deficit or confusion. "
            "Fundoscopy confirms no papilledema or optic disc swelling. No history of cancer, "
            "and patient denies daily NSAID use."
        ),
        "expected_note": "With negation detection, explicitly denied red flags are correctly flagged as negated instead of present.",
    },
]


def get_note_by_id(note_id: str) -> dict[str, Any]:
    """Retrieves a sample note fixture by its unique identifier.

    Args:
        note_id: Unique string identifier (e.g., 'cp_complete', 'ha_incomplete').

    Returns:
        The matching sample note dictionary.

    Raises:
        ValueError: If note_id does not exist in SAMPLE_NOTES.
    """
    for note in SAMPLE_NOTES:
        if note["id"] == note_id:
            return note

    available_ids = [n["id"] for n in SAMPLE_NOTES]
    raise ValueError(
        f"Unknown note id '{note_id}'. Available note IDs are: {available_ids}"
    )


if __name__ == "__main__":
    try:
        from src.analyzer import analyze_note
    except ImportError:
        from analyzer import analyze_note

    print("=" * 95)
    print("CLARITY - SAMPLE CLINICAL NOTES EVALUATION MATRIX (WITH NEGATION DETECTION)")
    print("=" * 95)
    print(f"{'ID':<15} | {'Condition':<11} | {'Score':<7} | {'Doc':<4} | {'Neg':<4} | {'Miss(H/M)':<9} | Label")
    print("-" * 95)

    for note in SAMPLE_NOTES:
        report = analyze_note(note["note_text"], condition=note["condition"])
        doc = len(report.present_fields)
        neg = len(report.negated_fields)
        miss = f"{len(report.missing_high)}H/{len(report.missing_medium)}M"
        print(
            f"{note['id']:<15} | {note['condition']:<11} | {report.completeness_score:>5.1f}% | {doc:>4} | {neg:>4} | {miss:<9} | {note['label']}"
        )

    print("=" * 95)
