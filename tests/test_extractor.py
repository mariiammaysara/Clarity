"""Unit tests for the keyword and negation extractor module (src/extractor.py)."""

from src.checklist import load_checklist
from src.extractor import extract_fields
from src.sample_notes import get_note_by_id


def test_extract_fields_detects_found_status_on_affirmative_text() -> None:
    """Verifies that affirmative documentation yields 'found' status with matched snippet."""
    fields = load_checklist("chest_pain")
    complete_note = get_note_by_id("cp_complete")["note_text"]

    results = extract_fields(complete_note, fields)
    results_by_name = {r.field_name: r for r in results}

    # Verify pain_radiation is found affirmatively
    radiation_res = results_by_name["pain_radiation"]
    assert radiation_res.status == "found"
    assert radiation_res.matched_keyword is not None
    assert "radiation to left arm" in radiation_res.matched_keyword.lower()
    assert radiation_res.matched_context is not None


def test_extract_fields_detects_negated_status_on_negated_text() -> None:
    """Verifies that clinical negation (e.g., 'denies radiation to left arm') yields 'negated' status."""
    fields = load_checklist("chest_pain")
    negated_note = get_note_by_id("cp_negated")["note_text"]

    results = extract_fields(negated_note, fields)
    results_by_name = {r.field_name: r for r in results}

    # Verify pain_radiation was correctly categorized as negated
    radiation_res = results_by_name["pain_radiation"]
    assert radiation_res.status == "negated"
    assert radiation_res.matched_keyword is not None

    # Verify associated anginal symptoms was also categorized as negated
    symptoms_res = results_by_name["associated_anginal_symptoms"]
    assert symptoms_res.status == "negated"


def test_extract_fields_detects_missing_status_on_absent_text() -> None:
    """Verifies that completely unmentioned checklist fields receive 'missing' status."""
    fields = load_checklist("chest_pain")
    incomplete_note = get_note_by_id("cp_incomplete")["note_text"]

    results = extract_fields(incomplete_note, fields)
    results_by_name = {r.field_name: r for r in results}

    # Troponin and ECG are completely absent in the incomplete walk-in clinic note
    ecg_res = results_by_name["ecg_findings"]
    assert ecg_res.status == "missing"
    assert ecg_res.matched_keyword is None
    assert ecg_res.matched_context is None

    troponin_res = results_by_name["cardiac_biomarkers"]
    assert troponin_res.status == "missing"
    assert troponin_res.matched_keyword is None


def test_extract_fields_matches_onset_time_phrases() -> None:
    """Verifies that phrases describing onset time fulfill the 'Onset and Duration of Pain' criterion."""
    fields = load_checklist("chest_pain")
    onset_field = [f for f in fields if f.field_name == "onset_and_duration"]

    test_notes = [
        ("Discomfort started 3 hours ago after lunch.", "started ... ago"),
        ("Chest pressure began 45 minutes prior to presentation.", "began ... prior to"),
        ("Patient reports acute onset substernal heaviness.", "acute onset"),
        ("Symptom onset was 2 hours ago.", "hours ago"),
    ]

    for note, description in test_notes:
        results = extract_fields(note, onset_field)
        assert len(results) == 1
        res = results[0]
        assert res.field_name == "onset_and_duration"
        assert res.status == "found", f"Failed for phrasing '{description}' in note: {note}"
        assert res.matched_keyword is not None


def test_extract_fields_matches_relieving_and_provoking_factors() -> None:
    """Verifies that medication responses and exertion triggers fulfill Provoking and Relieving Factors."""
    fields = load_checklist("chest_pain")
    factor_field = [f for f in fields if f.field_name == "provocative_and_palliative_factors"]

    test_notes = [
        ("Patient had partial relief with nitroglycerin sublingually.", "relief with nitroglycerin"),
        ("Took two aspirins with minimal relief.", "minimal relief"),
        ("Pain occurs when walking up stairs.", "walking up stairs"),
        ("Patient notes symptoms are worse with exertion.", "worse with exertion"),
    ]

    for note, description in test_notes:
        results = extract_fields(note, factor_field)
        assert len(results) == 1
        res = results[0]
        assert res.field_name == "provocative_and_palliative_factors"
        assert res.status == "found", f"Failed for phrasing '{description}' in note: {note}"
        assert res.matched_keyword is not None

