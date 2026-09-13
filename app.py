"""
Clarity — Clinical Note Missing Information Detector.
Interactive Streamlit Application.

PURPOSE:
Provides a clinician-facing demonstration UI to analyze free-text clinical notes
against evidence-based medical checklists, flag omitted high/medium priority items,
identify explicitly negated symptoms, and compute a weighted completeness score.

DISCLAIMER:
This is an educational and portfolio tool. It is not an approved clinical decision-support
system, does not provide medical diagnosis, and reviews documentation integrity only.
"""

import sys
from pathlib import Path

# Adjust sys.path so that imports from the `src` package resolve seamlessly
# regardless of whether the app is launched via `streamlit run app.py` from the root
# or executed from different working directories.
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st
from src.checklist import list_conditions
from src.analyzer import analyze_note, AnalysisReport
from src.sample_notes import SAMPLE_NOTES


# Configure Streamlit page layout and title
st.set_page_config(
    page_title="Clarity — Clinical Note Missing Information Detector",
    page_icon="🩺",
    layout="wide",
)


def find_sample_note(condition: str, scenario_keyword: str) -> dict | None:
    """Finds the first sample note matching the condition and scenario keyword."""
    for note in SAMPLE_NOTES:
        if note["condition"] == condition and scenario_keyword.lower() in note["id"].lower():
            return note
    return None


def main() -> None:
    # Header & Educational Subtitle
    st.title("Clarity — Clinical Note Missing Information Detector")
    st.markdown(
        """
        > **Educational & Portfolio Tool**: This system reviews clinical documentation completeness 
        > against evidence-based medical checklists. It **does not** provide medical diagnosis or 
        > clinical decision-support. Built on published guidelines rather than direct specialist validation.
        """
    )
    st.write("")

    # Condition Selector
    conditions = list_conditions()
    selected_condition = st.selectbox(
        "Select Clinical Presentation / Condition:",
        options=conditions,
        format_func=lambda c: c.replace("_", " ").title(),
        help="Select the clinical guideline checklist to validate documentation against.",
    )

    # Sample Note Loader Buttons
    st.markdown("**Quick Load Sample Clinical Notes:**")
    col_btn1, col_btn2, col_btn3 = st.columns(3)

    if col_btn1.button("📄 Load Sample: Complete", use_container_width=True):
        sample = find_sample_note(selected_condition, "complete")
        if sample:
            st.session_state["note_input"] = sample["note_text"]
            st.session_state["active_sample_label"] = sample["label"]
            st.rerun()

    if col_btn2.button("⚠️ Load Sample: Incomplete", use_container_width=True):
        sample = find_sample_note(selected_condition, "incomplete")
        if sample:
            st.session_state["note_input"] = sample["note_text"]
            st.session_state["active_sample_label"] = sample["label"]
            st.rerun()

    if col_btn3.button("🚫 Load Sample: Negated", use_container_width=True):
        sample = find_sample_note(selected_condition, "negated")
        if sample:
            st.session_state["note_input"] = sample["note_text"]
            st.session_state["active_sample_label"] = sample["label"]
            st.rerun()

    if "active_sample_label" in st.session_state:
        st.caption(f"📌 Active fixture: *{st.session_state['active_sample_label']}*")

    # Text Area for Clinical Note
    note_text = st.text_area(
        "Enter or Edit Clinical Note:",
        value=st.session_state.get("note_input", ""),
        height=200,
        placeholder="Paste clinical note text here, or click one of the sample buttons above...",
    )

    # Analyze Button
    analyze_clicked = st.button("🔍 Analyze Note", type="primary", use_container_width=True)

    if analyze_clicked:
        if not note_text.strip():
            st.warning("Please provide clinical note text before analyzing.")
            return

        # Perform Documentation Integrity Audit
        report: AnalysisReport = analyze_note(note_text, selected_condition)
        st.session_state["last_report"] = report

    # Display Report if available
    if "last_report" in st.session_state:
        report: AnalysisReport = st.session_state["last_report"]

        st.write("---")
        st.subheader("Audit Results & Completeness Summary")

        # Critical Missing Warning Banner
        if report.missing_high:
            st.error(
                f"🚨 **CRITICAL DOCUMENTATION GAP**: {len(report.missing_high)} High-Priority "
                f"clinical documentation items are missing from this note!"
            )
        else:
            st.success("✅ **CRITICAL FIELDS DOCUMENTED**: All high-priority checklist items are covered.")

        # Metric Cards Row
        total_fields = (
            len(report.missing_high)
            + len(report.missing_medium)
            + len(report.negated_fields)
            + len(report.present_fields)
        )

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Completeness Score", f"{report.completeness_score}%")
        m2.metric("High Priority Missing", f"{len(report.missing_high)} / {total_fields}")
        m3.metric("Medium Priority Missing", f"{len(report.missing_medium)} / {total_fields}")
        m4.metric("Documented (Present / Negated)", f"{len(report.present_fields)} / {len(report.negated_fields)}")

        st.write("")

        # Visual Detail Sections in 2 Columns
        col_missing, col_found = st.columns(2)

        with col_missing:
            # High Priority Missing Section
            st.markdown("### 🚨 High Priority — Missing")
            if report.missing_high:
                for item in report.missing_high:
                    with st.expander(f"❌ {item.display_name}", expanded=True):
                        st.markdown(f"**Clinical Rationale:** {item.rationale}")
                        st.markdown(f"**Guideline Reference:** 📖 `{item.guideline_ref}`")
            else:
                st.success("None — all high-priority items documented!")

            # Medium Priority Missing Section
            st.markdown("### ⚠️ Medium Priority — Missing")
            if report.missing_medium:
                for item in report.missing_medium:
                    with st.expander(f"⚠️ {item.display_name}", expanded=False):
                        st.markdown(f"**Clinical Rationale:** {item.rationale}")
                        st.markdown(f"**Guideline Reference:** 📖 `{item.guideline_ref}`")
            else:
                st.info("None — all medium-priority items documented!")

        with col_found:
            # Negated Elements Section
            st.markdown("### 🚫 Negated (Documented as Absent)")
            if report.negated_fields:
                st.info(
                    "The following findings were evaluated and **explicitly documented as absent** "
                    "(e.g., patient denies symptom). These are tracked separately from positive findings:\n\n"
                    + "\n".join(f"- **{field}**" for field in report.negated_fields)
                )
            else:
                st.caption("No negated clinical elements identified.")

            # Documented Elements Section
            st.markdown("### ✅ Documented (Present)")
            if report.present_fields:
                st.success(
                    "The following clinical elements were affirmatively documented in the note:\n\n"
                    + "\n".join(f"- **{field}**" for field in report.present_fields)
                )
            else:
                st.caption("No affirmative checklist elements identified.")

    # Footer Disclaimer & Limitation Caption
    st.write("---")
    st.caption(
        "ℹ️ **Negation Detection Limitation**: Clarity utilizes a localized pre-negation heuristic "
        "window (inspecting trigger words such as 'denies', 'no', 'without' within the active sentence). "
        "It does not perform full grammatical dependency parsing; complex syntactic phrasing may "
        "warrant manual clinician review."
    )


if __name__ == "__main__":
    main()
