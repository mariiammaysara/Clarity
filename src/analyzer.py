"""
Clarity - Clinical Documentation Analyzer & Report Generator.

ARCHITECTURE & INTEGRATION:
This module integrates the checklist knowledge base (checklist.py) with the
extraction engine (extractor.py) and negation detection (negation.py) to assess
clinical note completeness.

STATUS CLASSIFICATION:
- Documented (Found): Clinical element is documented and present (adds to completeness score).
- Negated: Clinical element is explicitly documented as absent or denied (does NOT add to
  completeness score, but is tracked separately from omitted items).
- Missing: Clinical element is not documented at all (categorized as HIGH or MEDIUM priority).

NOTE:
This tool evaluates DOCUMENTATION COMPLETENESS ONLY; it does not diagnose or
provide clinical recommendations.
"""

from dataclasses import dataclass
from typing import Sequence

try:
    from src.checklist import ChecklistField, load_checklist
    from src.extractor import ExtractionResult, extract_fields
except ImportError:
    from checklist import ChecklistField, load_checklist
    from extractor import ExtractionResult, extract_fields


@dataclass
class MissingItem:
    """Represents an omitted clinical documentation field requiring attention.

    Attributes:
        field_name: Unique snake_case identifier of the field.
        display_name: Human-readable clinical label.
        priority: Priority tier ('HIGH' or 'MEDIUM').
        rationale: Clinical significance explaining why omission poses clinical risk.
        guideline_ref: Authoritative clinical guideline reference citation.
    """

    field_name: str
    display_name: str
    priority: str
    rationale: str
    guideline_ref: str


@dataclass
class AnalysisReport:
    """Complete clinical documentation integrity audit report.

    Attributes:
        condition: Clinical presentation evaluated (e.g., 'chest_pain').
        missing_high: List of missing critical/high-priority documentation elements.
        missing_medium: List of missing medium-priority documentation elements.
        negated_fields: Display names of fields explicitly documented as denied/absent.
        present_fields: Display names of affirmatively documented clinical fields.
        completeness_score: Weighted completeness percentage (0.0 to 100.0).
    """

    condition: str
    missing_high: list[MissingItem]
    missing_medium: list[MissingItem]
    negated_fields: list[str]
    present_fields: list[str]
    completeness_score: float


def analyze_note(note_text: str, condition: str) -> AnalysisReport:
    """Analyzes a clinical note against the specified condition's medical checklist.

    Calculates a weighted completeness score where:
    - HIGH priority fields documented as present ('found') = 2 points each
    - MEDIUM priority fields documented as present ('found') = 1 point each
    - Fields documented as absent ('negated') = 0 points (tracked separately in report)
    - Missing fields = 0 points
    Score is normalized as a percentage of total possible points (0.0 to 100.0).

    Args:
        note_text: The free-text clinical note to inspect.
        condition: The condition key to validate against (e.g., 'chest_pain', 'headache').

    Returns:
        An AnalysisReport detailing missing items, negated items, present items, and score.

    Raises:
        ValueError: If condition is unknown or checklist loading fails.
    """
    fields: list[ChecklistField] = load_checklist(condition)
    extractions: list[ExtractionResult] = extract_fields(note_text, fields)

    extraction_map: dict[str, ExtractionResult] = {
        res.field_name: res for res in extractions
    }

    missing_high: list[MissingItem] = []
    missing_medium: list[MissingItem] = []
    negated_fields: list[str] = []
    present_fields: list[str] = []

    earned_points = 0.0
    total_possible_points = 0.0

    for field in fields:
        weight = 2.0 if field.priority == "HIGH" else 1.0
        total_possible_points += weight

        result = extraction_map.get(field.field_name)
        if result and result.status == "found":
            earned_points += weight
            present_fields.append(field.display_name)
        elif result and result.status == "negated":
            # Explicitly documented as absent: separated from missing and present
            negated_fields.append(field.display_name)
        else:
            missing_item = MissingItem(
                field_name=field.field_name,
                display_name=field.display_name,
                priority=field.priority,
                rationale=field.rationale,
                guideline_ref=field.guideline_ref,
            )
            if field.priority == "HIGH":
                missing_high.append(missing_item)
            else:
                missing_medium.append(missing_item)

    if total_possible_points > 0:
        score = round((earned_points / total_possible_points) * 100.0, 1)
    else:
        score = 0.0

    return AnalysisReport(
        condition=condition,
        missing_high=missing_high,
        missing_medium=missing_medium,
        negated_fields=negated_fields,
        present_fields=present_fields,
        completeness_score=score,
    )


def format_report(report: AnalysisReport) -> str:
    """Formats an AnalysisReport into a clean, human-readable terminal display string.

    Args:
        report: The AnalysisReport instance to format.

    Returns:
        A multiline formatted string suitable for console display.
    """
    condition_title = report.condition.replace("_", " ").title()
    total_fields = (
        len(report.missing_high)
        + len(report.missing_medium)
        + len(report.negated_fields)
        + len(report.present_fields)
    )

    lines: list[str] = [
        "=" * 80,
        f"CLARITY CLINICAL DOCUMENTATION INTEGRITY REPORT",
        f"Condition: {condition_title} | Completeness Score: {report.completeness_score}%",
        "=" * 80,
        "",
        f"[!] HIGH PRIORITY - MISSING ({len(report.missing_high)} items):",
    ]

    if report.missing_high:
        for item in report.missing_high:
            lines.append(f"  * {item.display_name}")
            lines.append(f"    Rationale: {item.rationale}")
            lines.append(f"    Guideline: {item.guideline_ref}")
            lines.append("")
    else:
        lines.append("  None -- fully documented\n")

    lines.append(f"[-] MEDIUM PRIORITY - MISSING ({len(report.missing_medium)} items):")
    if report.missing_medium:
        for item in report.missing_medium:
            lines.append(f"  * {item.display_name}")
            lines.append(f"    Rationale: {item.rationale}")
            lines.append(f"    Guideline: {item.guideline_ref}")
            lines.append("")
    else:
        lines.append("  None -- fully documented\n")

    lines.append(f"[~] NEGATED (explicitly documented as absent) ({len(report.negated_fields)} items):")
    if report.negated_fields:
        lines.append(f"  {', '.join(report.negated_fields)}")
    else:
        lines.append("  None")
    lines.append("")

    lines.append(f"[+] DOCUMENTED ({len(report.present_fields)}/{total_fields} fields):")
    if report.present_fields:
        lines.append(f"  {', '.join(report.present_fields)}")
    else:
        lines.append("  None")

    lines.append("")
    lines.append("=" * 80)
    lines.append(
        "NOTE: Evaluation is limited to documentation completeness. "
        "Negated findings indicate documented absence."
    )
    lines.append("=" * 80)

    return "\n".join(lines)


if __name__ == "__main__":
    # Test Note 1: Affirmative clinical documentation
    note_text = (
        "Patient presents with acute pressure sensation. "
        "Reports crushing chest pain with radiation to left arm since 2 hours ago. "
        "Complains of diaphoresis and nausea."
    )

    print("--- ANALYSIS FOR AFFIRMATIVE NOTE ---")
    report = analyze_note(note_text, condition="chest_pain")
    print(format_report(report))

    # Test Note 2: Negated clinical documentation
    note_negated = (
        "Patient denies chest pain radiation. "
        "Denies radiation to left arm or jaw. "
        "Patient is without diaphoresis, shortness of breath, or palpitations."
    )

    print("\n--- ANALYSIS FOR NEGATED NOTE ---")
    report_negated = analyze_note(note_negated, condition="chest_pain")
    print(format_report(report_negated))
