"""Unit tests for the benchmark evaluation module (src/evaluate.py)."""

from src.evaluate import run_evaluation


def test_run_evaluation_computes_expected_samples_and_metrics() -> None:
    """Verifies that run_evaluation evaluates all 60 fields across the 6 sample notes."""
    results = run_evaluation()

    assert results["total_samples"] == 60
    assert results["correct_samples"] >= 50
    assert results["accuracy"] >= 0.90

    # Ensure confusion matrix has 3x3 dimensions
    cm = results["confusion_matrix"]
    assert set(cm.keys()) == {"found", "negated", "missing"}
    for actual in cm:
        assert set(cm[actual].keys()) == {"found", "negated", "missing"}

    # Ensure class metrics are present and bounded between 0.0 and 1.0
    metrics = results["class_metrics"]
    for cls in ["found", "negated", "missing"]:
        assert cls in metrics
        assert 0.0 <= metrics[cls]["precision"] <= 1.0
        assert 0.0 <= metrics[cls]["recall"] <= 1.0
        assert 0.0 <= metrics[cls]["f1"] <= 1.0

    # Ensure mismatch list matches actual discrepancy count
    expected_mismatch_count = results["total_samples"] - results["correct_samples"]
    assert len(results["mismatches"]) == expected_mismatch_count
