"""
Clarity — Clinical Note Missing Information Detector.
Next.js / shadcn-inspired Healthtech Interface.

PURPOSE:
Provides an ultra-clean, minimal clinical documentation audit dashboard
benchmarking free-text notes against AHA/ACC and SNNOOP10 guidelines.
"""

import sys
from pathlib import Path

# Ensure local package resolution
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st
from src.checklist import list_conditions
from src.analyzer import analyze_note, AnalysisReport
from src.sample_notes import SAMPLE_NOTES


FAVICON_PATH = Path(__file__).resolve().parent / "favicon.svg"

# Configure Streamlit page layout
st.set_page_config(
    page_title="Clarity | Clinical Audit",
    page_icon=str(FAVICON_PATH),
    layout="wide",
    initial_sidebar_state="collapsed",
)

# React / Next.js / shadcn-like Minimalist Dark Theme
SHADCN_DARK_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:ital,wght@0,300;0,400;0,500;0,600;0,700;0,800;1,400&display=swap');

    /* Global Application Shell - JetBrains Mono Everywhere */
    .stApp, .stApp * {
        font-family: "JetBrains Mono", ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace !important;
    }

    .stApp {
        background-color: #060911 !important;
        color: #f8fafc !important;
        letter-spacing: -0.02em !important;
    }

    /* Hide Streamlit dev header and status bar during presentations */
    header[data-testid="stHeader"], header {
        visibility: hidden !important;
        height: 0 !important;
    }

    /* Container Spacing */
    .block-container {
        padding-top: 1.6rem !important;
        padding-bottom: 4rem !important;
        max-width: 1320px !important;
    }

    /* Single Unified Glass Card for Left Control Panel */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        background-color: #0e131f !important;
        border-radius: 12px !important;
        padding: 1.25rem !important;
        box-shadow: 0 4px 20px -2px rgba(0, 0, 0, 0.5) !important;
    }

    /* Micro Typography Labels */
    label[data-testid="stWidgetLabel"] p {
        font-size: 0.72rem !important;
        font-weight: 600 !important;
        color: #64748b !important;
        text-transform: uppercase !important;
        letter-spacing: 0.06em !important;
        margin-bottom: 6px !important;
    }

    /* Form Inputs - Selectbox */
    div[data-baseweb="select"] > div {
        background-color: #090d16 !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 8px !important;
        color: #f8fafc !important;
        font-size: 0.88rem !important;
        transition: all 0.15s ease !important;
    }
    div[data-baseweb="select"] > div:hover {
        border-color: rgba(255, 255, 255, 0.18) !important;
    }
    div[data-baseweb="select"] * {
        color: #f8fafc !important;
    }
    div[data-baseweb="popover"], div[data-baseweb="menu"] {
        background-color: #0d121f !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 8px !important;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.6) !important;
    }

    /* Form Inputs - Textarea */
    .stTextArea textarea {
        background-color: #090d16 !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 10px !important;
        color: #e2e8f0 !important;
        font-family: "JetBrains Mono", ui-monospace, Menlo, Consolas, monospace !important;
        font-size: 0.85rem !important;
        line-height: 1.65 !important;
        padding: 14px 16px !important;
        transition: border-color 0.15s ease, box-shadow 0.15s ease !important;
    }
    .stTextArea textarea:focus {
        border-color: rgba(96, 165, 250, 0.4) !important;
        box-shadow: 0 0 0 1px rgba(96, 165, 250, 0.25) !important;
    }

    /* Primary Action CTA Button (Refined low-contrast slate-blue gradient) */
    div[data-testid="stButton"] > button[kind="primary"] {
        background: linear-gradient(180deg, #1e3a5f 0%, #172554 100%) !important;
        color: #f1f5f9 !important;
        border: 1px solid rgba(59, 130, 246, 0.28) !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        font-size: 0.88rem !important;
        padding: 0.6rem 1.25rem !important;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.4) !important;
        transition: all 0.15s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }
    div[data-testid="stButton"] > button[kind="primary"]:hover {
        background: linear-gradient(180deg, #234775 0%, #1e3a5f 100%) !important;
        border-color: rgba(59, 130, 246, 0.45) !important;
        color: #ffffff !important;
        box-shadow: 0 4px 12px rgba(15, 23, 42, 0.6) !important;
        transform: translateY(-1px) !important;
    }

    /* Secondary Action Buttons (Outline Pills / Ghost buttons) */
    div[data-testid="stButton"] > button:not([kind="primary"]) {
        background-color: rgba(255, 255, 255, 0.02) !important;
        color: #cbd5e1 !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 8px !important;
        font-weight: 500 !important;
        font-size: 0.82rem !important;
        padding: 0.48rem 0.75rem !important;
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }
    div[data-testid="stButton"] > button:not([kind="primary"]):hover {
        background-color: rgba(255, 255, 255, 0.06) !important;
        border-color: rgba(255, 255, 255, 0.2) !important;
        color: #ffffff !important;
        transform: translateY(-1px) !important;
    }

    /* KPI Metric Cards (shadcn stat card) */
    div[data-testid="stMetric"] {
        background: #0d121f !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 10px !important;
        padding: 14px 18px !important;
        box-shadow: 0 2px 8px -2px rgba(0, 0, 0, 0.4) !important;
    }
    div[data-testid="stMetric"] label p {
        font-size: 0.7rem !important;
        font-weight: 600 !important;
        color: #64748b !important;
        text-transform: uppercase !important;
        letter-spacing: 0.06em !important;
    }
    div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
        font-size: 1.55rem !important;
        font-weight: 700 !important;
        color: #f8fafc !important;
        letter-spacing: -0.03em !important;
    }

    /* Clean Scrollbar */
    ::-webkit-scrollbar {
        width: 6px;
        height: 6px;
    }
    ::-webkit-scrollbar-track {
        background: #060911;
    }
    ::-webkit-scrollbar-thumb {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 3px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: rgba(255, 255, 255, 0.2);
    }
</style>
"""

st.markdown(SHADCN_DARK_CSS, unsafe_allow_html=True)


def find_sample_note(condition: str, scenario_keyword: str) -> dict | None:
    """Finds the first sample note matching the condition and scenario keyword."""
    for note in SAMPLE_NOTES:
        if note["condition"] == condition and scenario_keyword.lower() in note["id"].lower():
            return note
    return None


def main() -> None:
    # Centered Minimalist Clinical Header (Directly starting with title)
    st.markdown(
        """
        <div style="text-align: center; max-width: 680px; margin: 0 auto 1.6rem auto;">
            <h1 style="font-size: 2.75rem; font-weight: 800; letter-spacing: -0.04em; margin: 0 0 8px 0; color: #f8fafc;">Clarity</h1>
            <p style="color: #94a3b8; font-size: 0.94rem; line-height: 1.55; margin: 0; font-weight: 400;">
                Clinical documentation integrity auditor benchmarking free-text notes against AHA/ACC and SNNOOP10 guidelines.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Two-Column Workspace Layout (Left: Protocol & Benchmark Scenarios, Right: Clinical Note & Findings)
    col_ctrl, col_workspace = st.columns([1, 2], gap="large")

    # ================= LEFT COLUMN: SINGLE COHESIVE CARD CONTAINER =================
    with col_ctrl:
        with st.container(border=True):
            st.markdown(
                '<div style="font-size: 0.72rem; font-weight: 600; color: #64748b; text-transform: uppercase; letter-spacing: 0.06em; margin-bottom: 8px;">Clinical Protocol</div>',
                unsafe_allow_html=True,
            )

            conditions = list_conditions()
            selected_condition = st.selectbox(
                "Condition",
                options=conditions,
                format_func=lambda c: c.replace("_", " ").title(),
                label_visibility="collapsed",
            )

            st.markdown(
                '<div style="font-size: 0.72rem; font-weight: 600; color: #64748b; text-transform: uppercase; letter-spacing: 0.06em; margin-top: 16px; margin-bottom: 8px;">Benchmark Scenarios</div>',
                unsafe_allow_html=True,
            )

            if st.button("Comprehensive Note", use_container_width=True):
                sample = find_sample_note(selected_condition, "complete")
                if sample:
                    st.session_state["note_input"] = sample["note_text"]
                    st.session_state["active_sample_label"] = sample["label"]
                    st.rerun()

            if st.button("Deficient Note", use_container_width=True):
                sample = find_sample_note(selected_condition, "incomplete")
                if sample:
                    st.session_state["note_input"] = sample["note_text"]
                    st.session_state["active_sample_label"] = sample["label"]
                    st.rerun()

            if st.button("Negated Findings", use_container_width=True):
                sample = find_sample_note(selected_condition, "negated")
                if sample:
                    st.session_state["note_input"] = sample["note_text"]
                    st.session_state["active_sample_label"] = sample["label"]
                    st.rerun()

            if "active_sample_label" in st.session_state:
                st.markdown(
                    f"""
                    <div style="margin-top: 10px; margin-bottom: 4px; padding: 6px 10px; background: rgba(255, 255, 255, 0.02); border: 1px solid rgba(255, 255, 255, 0.06); border-radius: 6px; font-size: 0.72rem; color: #94a3b8;">
                        Active: <span style="color: #f1f5f9; font-weight: 500;">{st.session_state['active_sample_label']}</span>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            st.markdown('<div style="margin-top: 16px;"></div>', unsafe_allow_html=True)
            analyze_clicked = st.button(
                "Evaluate Documentation",
                type="primary",
                use_container_width=True,
            )

    # ================= RIGHT COLUMN: CLINICAL NOTE & AUDIT STREAM =================
    with col_workspace:
        st.markdown(
            """
            <div style="font-size: 0.72rem; font-weight: 600; color: #64748b; text-transform: uppercase; letter-spacing: 0.06em; margin-bottom: 6px;">
                Clinical Note Input
            </div>
            """,
            unsafe_allow_html=True,
        )

        note_text = st.text_area(
            "Clinical Note Input",
            value=st.session_state.get("note_input", ""),
            height=265,
            label_visibility="collapsed",
            placeholder="Type or paste free-text clinical note here, or choose a benchmark fixture from the left panel...",
        )

        # Trigger Audit
        if analyze_clicked:
            if not note_text.strip():
                st.markdown(
                    """
                    <div style="background: rgba(245, 158, 11, 0.08); border: 1px solid rgba(245, 158, 11, 0.25); border-radius: 8px; padding: 12px 16px; color: #fcd34d; font-size: 0.84rem; margin-top: 14px;">
                        Please provide clinical note text before initiating audit.
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                st.session_state.pop("last_report", None)
            else:
                report: AnalysisReport = analyze_note(note_text, selected_condition)
                st.session_state["last_report"] = report

        # Render Audit Results Stream
        if "last_report" in st.session_state:
            report: AnalysisReport = st.session_state["last_report"]

            st.markdown(
                "<div style='margin-top: 24px; margin-bottom: 18px; border-top: 1px solid rgba(255, 255, 255, 0.06);'></div>",
                unsafe_allow_html=True,
            )

            # Severity Banner (Minimal, Clean)
            if report.missing_high:
                st.markdown(
                    f"""
                    <div style="background: rgba(239, 68, 68, 0.08); border: 1px solid rgba(239, 68, 68, 0.2); border-left: 3px solid #ef4444; border-radius: 8px; padding: 12px 16px; margin-bottom: 16px;">
                        <div style="font-weight: 600; color: #f87171; font-size: 0.88rem;">Documentation Deficit Identified</div>
                        <div style="color: #fca5a5; font-size: 0.81rem; margin-top: 2px;">{len(report.missing_high)} high-priority clinical documentation elements are missing from this record.</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    """
                    <div style="background: rgba(16, 185, 129, 0.08); border: 1px solid rgba(16, 185, 129, 0.2); border-left: 3px solid #10b981; border-radius: 8px; padding: 12px 16px; margin-bottom: 16px;">
                        <div style="font-weight: 600; color: #34d399; font-size: 0.88rem;">Complete High-Priority Coverage</div>
                        <div style="color: #a7f3d0; font-size: 0.81rem; margin-top: 2px;">All essential guideline criteria are documented.</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            # KPI Metric Cards
            total_fields = (
                len(report.missing_high)
                + len(report.missing_medium)
                + len(report.negated_fields)
                + len(report.present_fields)
            )

            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Completeness", f"{report.completeness_score}%")
            m2.metric("Critical Gaps", f"{len(report.missing_high)} / {total_fields}")
            m3.metric("Medium Gaps", f"{len(report.missing_medium)} / {total_fields}")
            m4.metric("Documented / Negated", f"{len(report.present_fields)} / {len(report.negated_fields)}")

            st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)

            # Detailed Findings Columns
            col_gaps, col_coverage = st.columns(2, gap="medium")

            # DEFICITS COLUMN
            with col_gaps:
                st.markdown(
                    f"""
                    <div style="font-size: 0.72rem; font-weight: 600; color: #ef4444; text-transform: uppercase; letter-spacing: 0.06em; margin-bottom: 10px;">
                        High Priority Deficits ({len(report.missing_high)})
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                if report.missing_high:
                    for item in report.missing_high:
                        st.markdown(
                            f"""
                            <div style="background: #0d121f; border: 1px solid rgba(255, 255, 255, 0.08); border-left: 3px solid #ef4444; border-radius: 8px; padding: 12px 14px; margin-bottom: 10px;">
                                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 5px;">
                                    <span style="font-weight: 600; font-size: 0.86rem; color: #f8fafc;">{item.display_name}</span>
                                    <span style="font-size: 0.65rem; font-weight: 600; color: #fca5a5; background: rgba(239, 68, 68, 0.15); border: 1px solid rgba(239, 68, 68, 0.25); padding: 1px 6px; border-radius: 4px;">HIGH</span>
                                </div>
                                <div style="font-size: 0.79rem; color: #94a3b8; line-height: 1.45; margin-bottom: 6px;">{item.rationale}</div>
                                <div style="font-size: 0.71rem; color: #7dd3fc; font-family: 'JetBrains Mono', monospace;">Ref: {item.guideline_ref}</div>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )
                else:
                    st.markdown(
                        """
                        <div style="background: rgba(16, 185, 129, 0.04); border: 1px solid rgba(16, 185, 129, 0.15); border-radius: 8px; padding: 12px; font-size: 0.81rem; color: #34d399;">
                            Zero critical gaps — all high-priority parameters are present.
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                # Medium Priority Deficits
                st.markdown(
                    f"""
                    <div style="font-size: 0.72rem; font-weight: 600; color: #f59e0b; text-transform: uppercase; letter-spacing: 0.06em; margin-top: 18px; margin-bottom: 10px;">
                        Medium Priority Deficits ({len(report.missing_medium)})
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                if report.missing_medium:
                    for item in report.missing_medium:
                        st.markdown(
                            f"""
                            <div style="background: #0d121f; border: 1px solid rgba(255, 255, 255, 0.08); border-left: 3px solid #f59e0b; border-radius: 8px; padding: 12px 14px; margin-bottom: 10px;">
                                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 5px;">
                                    <span style="font-weight: 600; font-size: 0.86rem; color: #f8fafc;">{item.display_name}</span>
                                    <span style="font-size: 0.65rem; font-weight: 600; color: #fcd34d; background: rgba(245, 158, 11, 0.15); border: 1px solid rgba(245, 158, 11, 0.25); padding: 1px 6px; border-radius: 4px;">MED</span>
                                </div>
                                <div style="font-size: 0.79rem; color: #94a3b8; line-height: 1.45; margin-bottom: 6px;">{item.rationale}</div>
                                <div style="font-size: 0.71rem; color: #7dd3fc; font-family: 'JetBrains Mono', monospace;">Ref: {item.guideline_ref}</div>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )
                else:
                    st.markdown(
                        """
                        <div style="background: rgba(16, 185, 129, 0.04); border: 1px solid rgba(16, 185, 129, 0.15); border-radius: 8px; padding: 12px; font-size: 0.81rem; color: #34d399;">
                            All medium-priority checklist items are documented.
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

            # COVERAGE COLUMN (Negated & Affirmed)
            with col_coverage:
                st.markdown(
                    f"""
                    <div style="font-size: 0.72rem; font-weight: 600; color: #64748b; text-transform: uppercase; letter-spacing: 0.06em; margin-bottom: 10px;">
                        Documented as Absent / Negated ({len(report.negated_fields)})
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                if report.negated_fields:
                    chips_html = "".join(
                        f"<span style='display: inline-block; background: rgba(255, 255, 255, 0.04); color: #cbd5e1; border: 1px solid rgba(255, 255, 255, 0.08); font-size: 0.76rem; padding: 3px 9px; border-radius: 6px; margin: 3px 4px 3px 0; font-weight: 500;'>{field}</span>"
                        for field in report.negated_fields
                    )
                    st.markdown(
                        f"""
                        <div style="background: #0d121f; border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 8px; padding: 12px; margin-bottom: 18px;">
                            <div style="font-size: 0.74rem; color: #64748b; margin-bottom: 8px;">Explicitly documented as absent or denied:</div>
                            <div>{chips_html}</div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                else:
                    st.markdown(
                        """
                        <div style="background: #0d121f; border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 8px; padding: 12px; font-size: 0.78rem; color: #64748b; margin-bottom: 18px;">
                            No negated findings identified in this note.
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                # Affirmatively Documented
                st.markdown(
                    f"""
                    <div style="font-size: 0.72rem; font-weight: 600; color: #10b981; text-transform: uppercase; letter-spacing: 0.06em; margin-bottom: 10px;">
                        Affirmatively Documented ({len(report.present_fields)})
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                if report.present_fields:
                    chips_html = "".join(
                        f"<span style='display: inline-block; background: rgba(16, 185, 129, 0.1); color: #6ee7b7; border: 1px solid rgba(16, 185, 129, 0.22); font-size: 0.76rem; padding: 3px 9px; border-radius: 6px; margin: 3px 4px 3px 0; font-weight: 500;'>{field}</span>"
                        for field in report.present_fields
                    )
                    st.markdown(
                        f"""
                        <div style="background: #0d121f; border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 8px; padding: 12px;">
                            <div style="font-size: 0.74rem; color: #64748b; margin-bottom: 8px;">Positively documented in clinical record:</div>
                            <div>{chips_html}</div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                else:
                    st.markdown(
                        """
                        <div style="background: #0d121f; border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 8px; padding: 12px; font-size: 0.78rem; color: #64748b;">
                            No affirmative checklist elements detected.
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

    # Research-Grade Clinical & Architecture Footer
    st.markdown(
        """
        <style>
            .clarity-footer a {
                color: #94a3b8 !important;
                text-decoration: none !important;
                transition: color 0.15s ease !important;
            }
            .clarity-footer a:hover {
                color: #f8fafc !important;
            }
        </style>
        <footer class="clarity-footer" style="border-top: 1px solid rgba(255, 255, 255, 0.08); margin-top: 3.5rem; padding-top: 1.25rem;">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px; margin-bottom: 8px;">
                <div style="font-size: 0.78rem; color: #94a3b8;">
                    Benchmark Standards: AHA/ACC Chest Pain Guidelines &bull; SNNOOP10 Headache Criteria
                </div>
                <div style="display: inline-flex; align-items: center; font-size: 0.78rem; color: #64748b;">
                    <span>Clarity Engine v1.0 &bull; Research Build</span>
                    <a href="https://github.com/mariiammaysara/Clarity" target="_blank" rel="noopener noreferrer" style="color: #94a3b8; text-decoration: none; margin-left: 12px; font-weight: 500;">GitHub ↗</a>
                </div>
            </div>
            <div style="font-size: 0.75rem; color: #64748b; line-height: 1.5;">
                For research and clinical documentation integrity audit only. Evaluates documentation completeness and does not formulate diagnostic or triage decisions.
            </div>
        </footer>
        """,
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()

