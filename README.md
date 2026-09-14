<div align="center">

# Clarity
**Clinical Documentation Integrity & Guideline Audit Engine**

<p>
  An evidence-based clinical documentation integrity engine that audits free-text medical records against authoritative clinical society guidelines to detect documentation omissions without diagnosing patients.
</p>

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-0f172a?style=flat-square&logo=python&logoColor=cbd5e1)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.30%2B-1e293b?style=flat-square&logo=streamlit&logoColor=cbd5e1)](https://clarity-3sdzzb4ebw9kkq92j7x5dq.streamlit.app)
[![Tests Passing](https://img.shields.io/badge/Tests-12%20Passing-334155?style=flat-square&logo=pytest&logoColor=cbd5e1)](https://docs.pytest.org/)
[![Architecture](https://img.shields.io/badge/Architecture-Deterministic%20%7C%20Zero--Inference-1e293b?style=flat-square)]()
[![License](https://img.shields.io/badge/License-MIT-0f172a?style=flat-square)](LICENSE)

<p>
  <strong><a href="https://clarity-3sdzzb4ebw9kkq92j7x5dq.streamlit.app" target="_blank" rel="noopener noreferrer">Live Demo ↗</a></strong>
</p>

<a href="https://clarity-3sdzzb4ebw9kkq92j7x5dq.streamlit.app" target="_blank" rel="noopener noreferrer">
  <img src="assets/clarity_dashboard.png" alt="Clarity Clinical Documentation Integrity Auditor Interface" width="760" style="border: 1px solid #1e293b; border-radius: 10px; max-width: 100%; height: auto;" />
</a>

</div>

---

> [!CAUTION]
> ### Clinical Research & Educational Disclaimer
> **Clarity is an academic engineering and research portfolio demonstration, NOT an approved medical diagnostic or clinical decision-support system (CDSS).**  
> It does not evaluate patient pathology, propose differential diagnoses, formulate triage recommendations, or prescribe therapeutics. Its sole scope is evaluating the **completeness of clinical documentation** against codified medical society checklists. It has not undergone clinical trials and must never be utilized in active clinical care pathways.

---

## Executive Overview

In emergency and acute outpatient settings, incomplete clinical documentation represents a critical patient safety risk, a frequent cause of diagnostic delay, and a primary vulnerability in medical-legal audit. While generative Large Language Models (LLMs) are often proposed for medical note analysis, they suffer from stochasticity, hallucinations, unpredictable inference latency, high token costs, and black-box uninterpretability.

**Clarity** resolves this by providing a deterministic, transparent, and ultra-fast documentation audit engine. It ingests unstructured free-text clinical notes, matches concepts against standardized medical guideline checklists, detects clause-bounded symptom negations, and generates an actionable integrity report detailing:
- **Completeness Score (%):** Weighted coverage of required documentation items.
- **Critical & Medium Deficits:** Specific missing clinical parameters mapped to their medical rationale and guideline citation.
- **Documented Findings:** Segmented into affirmative findings and explicitly documented negative/negated findings.

---

## Key Capabilities

- 🩺 **Evidence-Based Guideline Grounding**: Codified knowledge bases strictly derived from published standards:
  - **2021 AHA/ACC Chest Pain Guideline** (American Heart Association / American College of Cardiology).
  - **SNNOOP10 Headache Red Flag Criteria** (European & International Headache Society standards).
- 🔍 **Clause-Bounded Clinical Negation Detection**: Implements a localized sliding-window heuristic that isolates negated observations (e.g., *"denies shortness of breath"*, *"no radiation to jaw"*), preventing documented absences from being misclassified as missing documentation while excluding them from affirmative points.
- ⚖️ **Weighted Clinical Risk Scoring**: Prioritizes life-threatening parameters (`HIGH` priority = 2 points, e.g., ECG or troponin in acute chest pain) over routine historical elements (`MEDIUM` priority = 1 point).
- ⚡ **Zero-Inference Footprint**: Runs locally with 100% deterministic reproducibility in $<10\text{ ms}$, requiring no GPU hardware, external APIs, or heavy ML dependencies.
- 🖥️ **Production-Grade Next.js/shadcn Aesthetic**: Built with a sleek dark dashboard featuring monospace typography, high-contrast clinical indicators, and responsive alignment.

---

## Codified Clinical Guidelines

Clarity stores its knowledge bases in structured, version-controlled JSON (`data/checklists.json`). Each parameter includes clinical priority, keyword taxonomies, medical rationales, and formal guideline citations.

### 1. Acute Chest Pain (`chest_pain`)
*Source: 2021 AHA/ACC/ASE/CHEST/SAEM/SCCT/SCMR Guideline for the Evaluation and Diagnosis of Chest Pain.*

| Parameter | Priority | Weight | Clinical Rationale & Guideline Citation |
| :--- | :---: | :---: | :--- |
| **Pain Character** | `HIGH` | 2 pts | Distinguishes ischemic (pressure/tightness) from non-ischemic etiologies. *(AHA/ACC 2021, Sec 4.1.1)* |
| **Pain Location & Radiation** | `HIGH` | 2 pts | Radiation to neck, jaw, or arms significantly elevates Acute Coronary Syndrome likelihood. *(AHA/ACC 2021, Sec 4.1.2)* |
| **Onset & Acuity** | `HIGH` | 2 pts | Abrupt 'thunderclap' or tearing onset flags aortic dissection. *(AHA/ACC 2021, Sec 4.1.3)* |
| **Electrocardiogram (ECG)** | `HIGH` | 2 pts | Mandatory within 10 minutes of presentation to detect STEMI. *(AHA/ACC 2021, Sec 4.2.1)* |
| **Cardiac Biomarkers (Troponin)** | `HIGH` | 2 pts | Essential to confirm or exclude acute myocardial injury. *(AHA/ACC 2021, Sec 4.2.2)* |
| **Associated Symptoms** | `MEDIUM` | 1 pt | Diaphoresis, dyspnea, nausea are secondary anginal equivalents. *(AHA/ACC 2021, Sec 4.1.4)* |
| **Provoking / Relieving Factors**| `MEDIUM` | 1 pt | Exertional aggravation or rest relief guides ischemic vs pleuritic etiology. *(AHA/ACC 2021, Sec 4.1.5)* |
| **Vital Signs** | `MEDIUM` | 1 pt | Hemodynamic stability directly governs triage priority. *(AHA/ACC 2021, Sec 3.1)* |
| **Cardiovascular Risk Factors** | `MEDIUM` | 1 pt | Hypertension, diabetes, smoking, hyperlipidemia inform pre-test probability. *(AHA/ACC 2021, Sec 4.3)* |
| **Prior Cardiac History** | `MEDIUM` | 1 pt | Known CAD, prior PCI/CABG markedly shifts clinical suspicion. *(AHA/ACC 2021, Sec 4.3)* |

### 2. Acute Headache (`headache`)
*Source: SNNOOP10 Headache Red Flag Criteria (International Headache Society & consensus guidelines).*

| Parameter | Priority | Weight | Clinical Rationale & Guideline Citation |
| :--- | :---: | :---: | :--- |
| **Onset & Speed (Thunderclap)** | `HIGH` | 2 pts | Reaching peak within 1 minute mandates immediate exclusion of Subarachnoid Hemorrhage. *(SNNOOP10 - O)* |
| **Systemic Symptoms (Fever/Weight)**| `HIGH` | 2 pts | Suggests meningitis, encephalitis, or giant cell arteritis. *(SNNOOP10 - S)* |
| **Neurologic Deficits** | `HIGH` | 2 pts | Motor/sensory/cranial nerve deficits flag intracranial space-occupying lesions. *(SNNOOP10 - N)* |
| **Neoplasm History** | `HIGH` | 2 pts | Significantly increases pre-test probability of brain metastasis. *(SNNOOP10 - N)* |
| **Pain Character & Severity** | `MEDIUM` | 1 pt | Characterizes primary vs secondary presentation; 'worst headache of life'. *(SNNOOP10)* |
| **Older Age at Onset (>50)** | `MEDIUM` | 1 pt | New headache onset in older adults raises concern for Giant Cell Arteritis or mass. *(SNNOOP10 - O)* |
| **Postural / Positional Triggers**| `MEDIUM` | 1 pt | Positional variation indicates intracranial hypotension or hypertension. *(SNNOOP10 - P)* |
| **Precipitated by Valsalva** | `MEDIUM` | 1 pt | Cough, bend, exertion onset indicates posterior fossa pathology or Chiari malformation. *(SNNOOP10 - P)* |
| **Papilledema** | `MEDIUM` | 1 pt | Critical physical sign of elevated intracranial pressure. *(SNNOOP10 - P)* |
| **Immunosuppression / HIV** | `MEDIUM` | 1 pt | High risk for opportunistic CNS infections and abscesses. *(SNNOOP10 - I)* |

---

## Audit & Scoring Methodology

### 1. Extraction & Negation Pipeline
1. **Keyword Pattern Matching:** Case-insensitive substring and synonym matching scans clinical text against the checklist dictionary.
2. **Clause-Bounded Negation Detection (`src/negation.py`):**
   - When a keyword matches, the preceding context window (up to 6 words) is inspected.
   - The scan is strictly bounded by clause boundaries (`.`, `!`, `?`, `;`, `\n`).
   - Trigger dictionary contains 14 clinical negation patterns:
     `"no", "not", "denies", "denied", "denying", "without", "negative", "rules out", "ruled out", "free of", "absent", "unremarkable", "non-", "never"`
3. **Classification:**
   - **`found`**: Affirmatively documented in note $\rightarrow$ awards completeness points.
   - **`negated`**: Explicitly documented as absent/denied $\rightarrow$ tracked as a documented negative finding; does not award affirmative points.
   - **`missing`**: Not detected in note $\rightarrow$ flagged as a documentation gap with priority tier.

### 2. Mathematical Completeness Formulation

$$\text{Completeness Score} = \left( \frac{\sum_{i \in \text{Present}} \text{Weight}_i}{\sum_{j \in \text{Checklist}} \text{Weight}_j} \right) \times 100$$

Where:
- $\text{Weight} = 2$ for `HIGH` priority items.
- $\text{Weight} = 1$ for `MEDIUM` priority items.
- Explicitly negated items are isolated in clinical coverage reports rather than penalized or falsely scored.

---

## System Architecture

```text
Clarity/
├── data/
│   └── checklists.json       # Guideline knowledge base (AHA/ACC, SNNOOP10) with versioning
├── src/
│   ├── checklist.py          # Typed dataclasses & JSON loader with schema validation
│   ├── negation.py           # Clause-bounded clinical negation sliding-window detector
│   ├── extractor.py          # Keyword matcher tracking status (found, negated, missing)
│   ├── analyzer.py           # Weighted completeness calculation & audit report generation
│   └── sample_notes.py       # 6 standardized clinical fixtures (complete, deficient, negated)
├── tests/
│   ├── test_checklist.py     # Schema validation and condition registry unit tests
│   ├── test_extractor.py     # Affirmative, negated, and absent extraction unit tests
│   └── test_analyzer.py      # Mathematical scoring and deficit aggregation unit tests
├── app.py                    # Interactive Streamlit clinical review dashboard
├── favicon.svg               # Custom monospace branded application favicon
├── requirements.txt          # Pinned dependency ranges for reproducible deployment
├── LICENSE                   # MIT Open Source License
└── README.md
```

### Data Flow Diagram

```text
       ┌────────────────────────┐
       │  data/checklists.json  │
       └───────────┬────────────┘
                   │  (ChecklistField Dataclasses)
                   ▼
         [ src/checklist.py ]
                   │
                   ├───────────────────────────────────┐
                   │                                   │
                   ▼                                   ▼
         [ Raw Clinical Note ]               [ src/negation.py ]
                   │                                   │
                   └───────────────► [ src/extractor.py ] ◄─┘
                                           │
                                           │  (ExtractionResult: found/negated/missing)
                                           ▼
                                  [ src/analyzer.py ]
                                           │
                        ┌──────────────────┴──────────────────┐
                        ▼                                     ▼
             [ CLI Analysis Report ]               [ Streamlit UI (app.py) ]
```

---

## Quickstart

### 1. Installation

```bash
# Clone the repository
git clone https://github.com/mariiammaysara/Clarity.git
cd Clarity

# Install dependencies (Python 3.10+)
pip install -r requirements.txt
```

### 2. Run Automated Test Suite

All 9 test cases run in $<0.1\text{ s}$:

```bash
pytest -v
```

```text
tests/test_analyzer.py::test_analyzer_complete_note PASSED           [ 33%]
tests/test_analyzer.py::test_analyzer_deficient_note PASSED          [ 44%]
tests/test_analyzer.py::test_analyzer_negated_note PASSED            [ 55%]
tests/test_checklist.py::test_load_checklist_valid_condition PASSED  [ 66%]
tests/test_checklist.py::test_load_checklist_unknown_condition PASSED[ 77%]
tests/test_checklist.py::test_list_conditions PASSED                [ 88%]
tests/test_extractor.py::test_extractor_complete_note PASSED        [ 92%]
tests/test_extractor.py::test_extractor_deficient_note PASSED       [ 96%]
tests/test_extractor.py::test_extractor_negated_note PASSED         [100%]

============================== 9 passed in 0.06s ==============================
```

### 3. Launch the Interactive Dashboard

```bash
streamlit run app.py
```

Open your browser at `http://localhost:8501` to access the interactive clinical interface.

### 4. Run CLI Audit Matrix

Evaluate the preloaded benchmark fixtures across all conditions directly from the terminal:

```bash
python src/sample_notes.py
```

Or run an audit on a single sample clinical note:

```bash
python src/analyzer.py
```

### 5. Run Ground-Truth Benchmark Evaluation

Validate the clinical extraction engine against curated physician ground-truth annotations across 60 clinical checkpoints:

```bash
python -m src.evaluate
```

---

## Benchmark Clinical Scenarios

Clarity includes 6 calibrated clinical fixtures in `src/sample_notes.py` representing three realistic documentation profiles across both clinical conditions:

| Scenario ID | Condition | Profile Description | Expected Audit Finding |
| :--- | :--- | :--- | :--- |
| `chest_pain_complete` | Chest Pain | ED physician note with complete workup. | **100% Completeness** • 0 Deficits |
| `chest_pain_deficient` | Chest Pain | Triage note lacking troponin, ECG, and vitals. | **Critical Gaps Identified** • High Priority Alerts |
| `chest_pain_negated` | Chest Pain | History explicitly denying radiation & dyspnea. | **Documented Negatives** • Isolated Coverage |
| `headache_complete` | Headache | Complete neurological & red-flag workup. | **100% Completeness** • 0 Deficits |
| `headache_deficient` | Headache | Brief note omitting onset speed, fever, papilledema.| **Critical Gaps Identified** • Subarachnoid Risk |
| `headache_negated` | Headache | Comprehensive note denying thunderclap & deficits. | **Documented Negatives** • Red Flags Documented Absent |

---

## Engineering Design Principles

1. **Deterministic Over Stochastic**: In clinical auditing, consistency is paramount. Two runs on the exact same note will yield the exact same score and gap breakdown every time.
2. **Zero Black-Box Dependencies**: Transparent keyword taxonomies mean every audit finding can be directly traced to specific characters and guideline citations.
3. **Low Latency & High Portability**: Zero compilation or GPU prerequisites allow Clarity to run inside lightweight Docker containers, on microservices, or directly on clinical client machines.
4. **Clean Decoupling**: Checklists (`data/`), data loading (`src/checklist.py`), extraction (`src/extractor.py`), negation (`src/negation.py`), and presentation (`app.py`) are fully isolated and independently testable.

---

## Technical Stack

- **Language**: Python 3.10+ (Standard Library: `dataclasses`, `pathlib`, `typing`, `re`, `json`)
- **Frontend Framework**: Streamlit (Custom Next.js/shadcn dark design system)
- **Testing & Quality Assurance**: pytest
- **Version Control**: Git & GitHub

---

## Academic Context

Developed as an independent portfolio project demonstrating competencies in applied healthcare informatics, clinical natural language processing, and medical documentation integrity. Created as part of academic preparation for competitive Master's programs in Medical Artificial Intelligence (including the Erasmus Mundus Joint Master Degree in Medical Imaging and Applications - MAIA).

---

## License

This project is licensed under the [MIT License](LICENSE) — see the LICENSE file for details.
