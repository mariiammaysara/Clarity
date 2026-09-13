# Clarity — Clinical Note Missing Information Detector

> An evidence-based clinical documentation integrity auditor that reviews clinical notes against medical guidelines to flag missing critical information without diagnosing patients.

---

> [!CAUTION]
> ### Clinical & Educational Disclaimer
> **Clarity is an educational and portfolio engineering project, NOT an approved medical diagnostic or clinical decision-support system.**  
> It does not evaluate patient health, suggest treatments, or formulate clinical diagnoses. Its sole function is to assess the **completeness of medical documentation** against standardized clinical checklists. It is not validated by a licensed physician and must never be used in active clinical workflows.

---

## What It Does

Clarity audits free-text clinical documentation against authoritative, evidence-based medical society guidelines. When a clinician drafts a note for an acute clinical scenario—such as acute chest pain or severe headache—Clarity benchmarks the text against codified clinical checklists derived from standards like the **2021 AHA/ACC Chest Pain Guideline** and the **SNNOOP10 Headache Red Flags** framework. It identifies omitted documentation items, categorizes their clinical urgency (HIGH vs. MEDIUM priority), isolates explicitly negated symptoms, and generates an audit report complete with clinical rationales and formal guideline references.

## Why This Project

This project was developed as an applied Medical AI portfolio demonstration to explore the intersection of clinical guidelines, natural language processing, and medical documentation integrity. It represents practical preparation for competitive European joint Master’s degree programs in medical technology and computer vision, such as Erasmus Mundus MAIA (Medical Imaging and Applications).

---

## Architecture

### Repository Structure

```text
Clarity/
├── data/
│   └── checklists.json     # Curated clinical guideline knowledge base (Chest Pain, Headache)
├── src/
│   ├── checklist.py        # Typed dataclasses and JSON checklist loader with validation
│   ├── negation.py         # Clause-bounded clinical negation detection heuristic
│   ├── extractor.py        # Case-insensitive keyword extractor tracking status (found/negated/missing)
│   ├── analyzer.py         # Documentation integrity auditor computing weighted completeness scores
│   └── sample_notes.py     # 6 standardized clinical note fixtures (complete, deficient, negated)
├── tests/
│   ├── test_checklist.py   # Unit tests for schema validation and condition loading
│   ├── test_extractor.py   # Unit tests for affirmative, negated, and absent keyword matching
│   └── test_analyzer.py    # Unit tests for weighted scoring mathematics and reporting
├── app.py                  # Interactive Streamlit clinical review dashboard
├── requirements.txt        # Lightweight dependencies (Streamlit, Pytest)
└── README.md
```

### Module Responsibilities (`src/`)

- **`checklist.py`**: Loads and validates clinical checklist items into immutable typed `ChecklistField` dataclasses with strict priority enforcement (`HIGH` or `MEDIUM`).
- **`negation.py`**: Lightweight clinical negation detector that analyzes preceding word windows within sentence boundaries to identify negated findings (e.g., *"denies"*, *"no"*, *"without"*).
- **`extractor.py`**: Case-insensitive keyword matching engine that scans clinical notes, extracts documentation context snippets (~40 characters), and tags status as `found`, `negated`, or `missing`.
- **`analyzer.py`**: Orchestrates extraction results to compute a weighted completeness score and format structured terminal/visual audit reports.
- **`sample_notes.py`**: Fixed test harness containing realistic clinical fixtures used for automated evaluation and live demonstrations.

### Data Flow Diagram

```text
  [ data/checklists.json ]
             │
             ▼
     [ src/checklist.py ] ──(List of ChecklistField objects)──┐
                                                              │
  [ Raw Clinical Note ]                                       ▼
             │                                        [ src/extractor.py ]
             └───────────────────────────────────────►        ▲
                                                              │
                                                     [ src/negation.py ]
                                                              │
                                                     (ExtractionResult)
                                                              │
                                                              ▼
                                                     [ src/analyzer.py ]
                                                              │
                                     ┌────────────────────────┴────────────────────────┐
                                     ▼                                                 ▼
                          [ Console Audit Report ]                         [ Streamlit UI (app.py) ]
```

---

## Quickstart

### 1. Clone and Install Dependencies

```bash
git clone https://github.com/mariiammaysara/Clarity.git
cd Clarity
pip install -r requirements.txt
```

### 2. Run the Command-Line Matrix Demo

Evaluate the 6 standardized clinical fixtures directly in your terminal:

```bash
python src/sample_notes.py
```

To run a single formatted audit report on a clinical note:

```bash
python src/analyzer.py
```

### 3. Launch the Interactive Web Dashboard

Launch the browser-based Streamlit interface:

```bash
streamlit run app.py
```

### 4. Run the Pytest Test Suite

Execute all 9 automated unit tests verifying loading, negation, extraction, and scoring logic:

```bash
pytest -v
```

---

## Design Decisions

- **Rule-Based Engine Over Generative LLMs**: Prioritized deterministic, inspectable keyword extraction over black-box LLMs to ensure reproducible audits, instant execution speed, and zero external API dependencies or inference costs.
- **Weighted Clinical Scoring (HIGH = 2 pts, MEDIUM = 1 pt)**: Designed to reflect medical reality, where omitting acute life-threat workups (e.g., troponin or ECG in acute coronary syndrome) carries far greater clinical risk than omitting background historical details.
- **Dedicated Clause-Bounded Negation (`negation.py`)**: Decoupled negation logic from keyword searching so that negated observations (e.g., *"denies radiation to left arm"*) are excluded from completeness points while remaining tracked as documented negative findings.
- **Zero Heavy NLP Frameworks**: Built using standard Python data structures and minimal UI tooling (`streamlit`) to maintain a lean, dependency-light footprint that can run on any environment without PyTorch or spaCy overhead.

---

## Known Limitations

- **Heuristic Negation Scope**: Negation detection relies on a localized pre-negation word window (default: 6 words) bounded by sentence terminators. It does not perform full syntactic dependency parsing and cannot resolve post-negation (e.g., *"chest pain was denied"*) or complex double negations.
- **Keyword Substring Collisions**: Naive substring searching can cause collisions when a short term is embedded within another compound phrase (for instance, the keyword `"pressure"` matching inside `"blood pressure"`).
- **Documentation Completeness vs. Clinical Truth**: Clarity verifies whether concepts were *written* in the note. It cannot judge clinical accuracy, verify whether diagnostic tests were performed correctly, or evaluate patient risk.

---

## Tech Stack

- **Python 3.10+** (Core logic, dataclasses, regex parsing)
- **Streamlit** (Interactive clinical demonstration dashboard)
- **pytest** (Automated unit testing suite)

---

## License

Distributed under the [MIT License](https://opensource.org/licenses/MIT).
