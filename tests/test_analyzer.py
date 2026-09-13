"""Unit tests for the documentation analyzer and report generator (src/analyzer.py)."""

from src.analyzer import analyze_note
from src.sample_notes import get_note_by_id


def test_analyze_note_complete_sample_achieves_perfect_score() -> None:
    """Verifies that the comprehensive ACS note achieves 100.0% completeness with zero missing items."""
    complete_note = get_note_by_id("cp_complete")["note_text"]
    report = analyze_note(complete_note, "chest_pain")

    assert report.completeness_score == 100.0
    assert len(report.missing_high) == 0
    assert len(report.missing_medium) == 0
    assert len(report.present_fields) == 10
    assert len(report.negated_fields) == 0


def test_analyze_note_negated_sample_categorizes_negated_fields() -> None:
    """Verifies that explicitly negated symptoms are segregated into negated_fields and give 0% score."""
    negated_note = get_note_by_id("cp_negated")["note_text"]
    report = analyze_note(negated_note, "chest_pain")

    # Negated fields must not be empty
    assert len(report.negated_fields) > 0
    # No affirmative present fields should exist
    assert len(report.present_fields) == 0
    # Score should be 0.0 because no positive documentation exists
    assert report.completeness_score == 0.0
    # Negated items include radiation and associated anginal symptoms
    assert "Pain Radiation Pattern" in report.negated_fields
    assert "Associated Anginal Equivalents" in report.negated_fields


def test_weighted_scoring_logic() -> None:
    """Verifies the weighted scoring formula: HIGH=2 pts, MEDIUM=1 pt normalized against maximum points.

    For 'chest_pain': 7 HIGH (14 pts) + 3 MEDIUM (3 pts) = 17 total possible points.
    A note documenting only 1 HIGH ('vital_signs') and 1 MEDIUM ('cardiovascular_risk_factors')
    earns 3 points out of 17: (3 / 17) * 100 = 17.647... -> rounded to 17.6%.
    """
    synthetic_note = "Evaluation shows heart rate 75 bpm. Patient has diabetes mellitus."
    report = analyze_note(synthetic_note, "chest_pain")

    assert set(report.present_fields) == {
        "Hemodynamic Vital Signs",
        "Cardiovascular Risk Factors",
    }
    assert report.completeness_score == 17.6
    assert len(report.missing_high) == 6
    assert len(report.missing_medium) == 2
