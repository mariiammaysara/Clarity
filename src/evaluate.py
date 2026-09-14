"""
Clarity - Benchmark Evaluation & Error Analysis Engine.

PURPOSE:
This module benchmarks the actual extraction outcomes of `extractor.py` against
the curated clinical ground truth defined in `data/ground_truth.json`.
It computes classification metrics (Accuracy, Precision, Recall, F1) and
generates a detailed confusion matrix and error audit without third-party ML dependencies.
"""

import json
from pathlib import Path
from typing import Any

# Flexible package and direct execution imports
try:
    from src.checklist import ChecklistField, load_checklist
    from src.extractor import ExtractionResult, extract_fields
    from src.sample_notes import SAMPLE_NOTES
except ImportError:
    from checklist import ChecklistField, load_checklist
    from extractor import ExtractionResult, extract_fields
    from sample_notes import SAMPLE_NOTES

CLASSES: list[str] = ["found", "negated", "missing"]


def get_ground_truth_path() -> Path:
    """Resolves the path to data/ground_truth.json reliably."""
    base_dir = Path(__file__).resolve().parent.parent
    gt_path = base_dir / "data" / "ground_truth.json"
    if not gt_path.exists():
        # Fallback for relative current working directory
        gt_path = Path("data/ground_truth.json").resolve()
    return gt_path


def run_evaluation() -> dict[str, Any]:
    """Executes evaluation across all sample notes against ground truth annotations.

    Runs extraction pipeline on each note in SAMPLE_NOTES, compares actual
    vs. expected status for each checklist field, and calculates:
    - Overall accuracy
    - Per-class Precision, Recall, F1, and Support
    - Macro and Weighted average metrics
    - 3x3 Confusion Matrix
    - Comprehensive mismatch diagnostic list

    Returns:
        Dictionary containing raw predictions, matrix, summary metrics, and mismatches.
    """
    gt_path = get_ground_truth_path()
    with open(gt_path, "r", encoding="utf-8") as f:
        ground_truth: dict[str, dict[str, str]] = json.load(f)

    y_true: list[str] = []
    y_pred: list[str] = []
    records: list[dict[str, Any]] = []
    mismatches: list[dict[str, Any]] = []

    for note_entry in SAMPLE_NOTES:
        note_id = note_entry["id"]
        condition = note_entry["condition"]
        note_text = note_entry["note_text"]

        expected_fields = ground_truth.get(note_id, {})
        fields: list[ChecklistField] = load_checklist(condition)
        extractions: list[ExtractionResult] = extract_fields(note_text, fields)

        for res in extractions:
            actual_status = expected_fields.get(res.field_name)
            predicted_status = res.status

            if actual_status is None:
                continue

            y_true.append(actual_status)
            y_pred.append(predicted_status)

            record = {
                "note_id": note_id,
                "condition": condition,
                "field_name": res.field_name,
                "ground_truth": actual_status,
                "predicted": predicted_status,
                "matched_keyword": res.matched_keyword,
                "matched_context": res.matched_context,
            }
            records.append(record)

            if actual_status != predicted_status:
                mismatches.append(record)

    total_samples = len(y_true)
    correct_samples = sum(1 for yt, yp in zip(y_true, y_pred) if yt == yp)
    accuracy = (correct_samples / total_samples) if total_samples > 0 else 0.0

    # Build 3x3 Confusion Matrix: rows = Ground Truth, columns = Predicted
    confusion_matrix: dict[str, dict[str, int]] = {
        actual: {pred: 0 for pred in CLASSES} for actual in CLASSES
    }
    for yt, yp in zip(y_true, y_pred):
        if yt in confusion_matrix and yp in confusion_matrix[yt]:
            confusion_matrix[yt][yp] += 1

    # Calculate per-class metrics
    class_metrics: dict[str, dict[str, float]] = {}
    for cls in CLASSES:
        tp = confusion_matrix[cls][cls]
        fp = sum(confusion_matrix[other][cls] for other in CLASSES if other != cls)
        fn = sum(confusion_matrix[cls][other] for other in CLASSES if other != cls)
        support = sum(confusion_matrix[cls][other] for other in CLASSES)

        precision = (tp / (tp + fp)) if (tp + fp) > 0 else 0.0
        recall = (tp / (tp + fn)) if (tp + fn) > 0 else 0.0
        f1 = (
            (2 * precision * recall / (precision + recall))
            if (precision + recall) > 0
            else 0.0
        )

        class_metrics[cls] = {
            "precision": precision,
            "recall": recall,
            "f1": f1,
            "support": support,
            "tp": tp,
            "fp": fp,
            "fn": fn,
        }

    # Macro & Weighted Averages
    macro_precision = sum(m["precision"] for m in class_metrics.values()) / len(CLASSES)
    macro_recall = sum(m["recall"] for m in class_metrics.values()) / len(CLASSES)
    macro_f1 = sum(m["f1"] for m in class_metrics.values()) / len(CLASSES)

    weighted_precision = (
        sum(m["precision"] * m["support"] for m in class_metrics.values()) / total_samples
        if total_samples > 0
        else 0.0
    )
    weighted_recall = (
        sum(m["recall"] * m["support"] for m in class_metrics.values()) / total_samples
        if total_samples > 0
        else 0.0
    )
    weighted_f1 = (
        sum(m["f1"] * m["support"] for m in class_metrics.values()) / total_samples
        if total_samples > 0
        else 0.0
    )

    return {
        "total_samples": total_samples,
        "correct_samples": correct_samples,
        "accuracy": accuracy,
        "confusion_matrix": confusion_matrix,
        "class_metrics": class_metrics,
        "averages": {
            "macro": {
                "precision": macro_precision,
                "recall": macro_recall,
                "f1": macro_f1,
            },
            "weighted": {
                "precision": weighted_precision,
                "recall": weighted_recall,
                "f1": weighted_f1,
            },
        },
        "records": records,
        "mismatches": mismatches,
    }


def print_evaluation_report(results: dict[str, Any]) -> None:
    """Formats and prints the evaluation report clearly in the terminal."""
    total = results["total_samples"]
    correct = results["correct_samples"]
    acc = results["accuracy"] * 100.0
    cm = results["confusion_matrix"]
    metrics = results["class_metrics"]
    avg = results["averages"]
    mismatches = results["mismatches"]

    print("=" * 80)
    print("           CLARITY CLINICAL EXTRACTOR BENCHMARK EVALUATION REPORT")
    print("=" * 80)
    print(f"Total Evaluated Fields : {total}")
    print(f"Correct Classifications: {correct} / {total}")
    print(f"Overall Accuracy       : {acc:.2f}% ({correct}/{total})\n")

    # 1. Confusion Matrix
    print("-" * 80)
    print("CONFUSION MATRIX (Rows: Ground Truth Actual, Columns: Extractor Predicted)")
    print("-" * 80)
    col_label = "Actual / Predicted"
    header = f"{col_label:<20} | {'found':>10} | {'negated':>10} | {'missing':>10} | {'Total':>8}"
    print(header)
    print("-" * len(header))
    for actual in CLASSES:
        row_total = sum(cm[actual][p] for p in CLASSES)
        print(
            f"{actual:<20} | {cm[actual]['found']:>10} | {cm[actual]['negated']:>10} | {cm[actual]['missing']:>10} | {row_total:>8}"
        )
    print("-" * len(header))
    pred_totals = [sum(cm[a][p] for a in CLASSES) for p in CLASSES]
    print(
        f"{'Pred Total':<20} | {pred_totals[0]:>10} | {pred_totals[1]:>10} | {pred_totals[2]:>10} | {total:>8}\n"
    )

    # 2. Classification Metrics Table
    print("-" * 80)
    print("PER-CLASS CLASSIFICATION METRICS")
    print("-" * 80)
    m_header = f"{'Class':<12} | {'Precision':>10} | {'Recall':>10} | {'F1-Score':>10} | {'Support':>8}"
    print(m_header)
    print("-" * len(m_header))
    for cls in CLASSES:
        m = metrics[cls]
        print(
            f"{cls:<12} | {m['precision'] * 100:>9.1f}% | {m['recall'] * 100:>9.1f}% | {m['f1'] * 100:>9.1f}% | {int(m['support']):>8}"
        )
    print("-" * len(m_header))
    mac = avg["macro"]
    print(
        f"{'Macro Avg':<12} | {mac['precision'] * 100:>9.1f}% | {mac['recall'] * 100:>9.1f}% | {mac['f1'] * 100:>9.1f}% | {total:>8}"
    )
    wt = avg["weighted"]
    print(
        f"{'Weighted Avg':<12} | {wt['precision'] * 100:>9.1f}% | {wt['recall'] * 100:>9.1f}% | {wt['f1'] * 100:>9.1f}% | {total:>8}"
    )
    print("-" * len(m_header))
    print()

    # 3. Mismatches Diagnostic Analysis
    print("-" * 80)
    print(f"ERROR ANALYSIS & MISMATCH DIAGNOSTICS ({len(mismatches)} Discrepancies Identified)")
    print("-" * 80)

    if not mismatches:
        print("  [✓] Perfect 100% agreement between extractor and ground truth!\n")
    else:
        # Display top mismatches (up to 5 as requested for focused error analysis)
        display_count = min(5, len(mismatches))
        print(f"Displaying top {display_count} discrepancies for error analysis:\n")

        for idx, m in enumerate(mismatches[:display_count], 1):
            print(f"[{idx}] Note ID     : {m['note_id']} ({m['condition']})")
            print(f"    Field       : {m['field_name']}")
            print(f"    Ground Truth: [{m['ground_truth'].upper()}]")
            print(f"    Predicted   : [{m['predicted'].upper()}]")
            if m["matched_keyword"]:
                print(f"    Trigger     : '{m['matched_keyword']}'")
            else:
                print(f"    Trigger     : None (No keyword/regex matched)")
            if m["matched_context"]:
                print(f"    Evidence    : \"{m['matched_context']}\"")
            print()

    print("=" * 80)


if __name__ == "__main__":
    results = run_evaluation()
    print_evaluation_report(results)
