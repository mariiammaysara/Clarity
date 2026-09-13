# Clarity Benchmark — Clinical Ground Truth Notes for Review

This document highlights clinical interpretation nuances and borderline documentation cases identified during the human clinical review of the 6 test fixtures in [`src/sample_notes.py`](file:///c:/Users/ahmed/Desktop/CLARITY/src/sample_notes.py) for [`data/ground_truth.json`](file:///c:/Users/ahmed/Desktop/CLARITY/data/ground_truth.json).

---

## 1. `cp_incomplete` (Deficient / Hurried Walk-in Clinic Note)

### Field: `pain_character`
- **Note Text Snippet**: `"felt achy chest discomfort"`
- **Current Assignment**: `"found"`
- **Clinical Nuance / Ambiguity**:
  - The patient describes the sensation as `"achy"`. Clinically, "achy" describes pain quality/character (differentiating from burning, sharp, or stabbing).
  - *Alternative view*: ACC/AHA guidelines focus primarily on classic ischemic descriptors (pressure, squeezing, heaviness, crushing, or pleuritic). If the benchmark strictly requires documenting ischemic-specific character rather than generic non-anginal character, this could be debated as `"missing"`.
  - *Recommendation*: Keep as `"found"` because the clinician did document what the pain felt like.

### Field: `onset_and_duration`
- **Note Text Snippet**: `"off and on since yesterday morning"`
- **Current Assignment**: `"found"`
- **Clinical Nuance / Ambiguity**:
  - Timing is specified as `"since yesterday morning"`, which establishes the onset window.
  - *Alternative view*: The duration is somewhat imprecise ("off and on since yesterday morning") compared to an exact hour/minute duration.
  - *Recommendation*: `"found"`, as onset timing is documented.

---

## 2. `cp_negated` (Explicit Negation Demonstration)

### Field: `pain_character`
- **Note Text Snippet**: `"reports mild atypical epigastric discomfort"`
- **Current Assignment**: `"missing"`
- **Clinical Nuance / Ambiguity**:
  - The note uses `"atypical epigastric discomfort"`. "Epigastric" describes anatomical location, "mild" is severity, and "atypical" is an assessment/classification, but no qualitative descriptor (e.g., pressure, sharpness, tightness, ache) is documented.
  - *Alternative view*: Some might argue `"atypical discomfort"` serves as a shorthand documentation of non-ischemic character.
  - *Recommendation*: Keep as `"missing"` because pain quality itself is omitted.

### Field: `cardiovascular_risk_factors`
- **Note Text Snippet**: `"62-year-old female presents for routine follow-up."`
- **Current Assignment**: `"missing"`
- **Clinical Nuance / Ambiguity**:
  - Age (female > 55 or > 65) is epidemiologically a cardiovascular risk factor.
  - However, in clinical documentation integrity auditing, the parameter evaluates documentation of the patient's modifiable/family risk factor profile (hypertension, diabetes, smoking status, hyperlipidemia, family history). None of these were addressed or denied.
  - *Recommendation*: Keep as `"missing"`.

---

## 3. `ha_complete` (Comprehensive Secondary Headache Workup Note)

### Field: `positional_or_valsalva_features`
- **Note Text Snippet**: `"thunderclap headache that peaked in seconds while exercising"`
- **Current Assignment**: `"found"`
- **Clinical Nuance / Ambiguity**:
  - SNNOOP10 defines criterion **P3** as: *"Precipitated by coughing, sneezing, exercise, or Valsalva maneuver."* Peak onset during strenuous physical exercise represents an exertional/Valsalva precipitation trigger.
  - *Alternative view*: If interpreted strictly as *postural/orthostatic change* (standing vs. lying down), exercise might be considered distinct. However, in SNNOOP10 and international headache taxonomy, exertional and Valsalva triggers are unified in the red-flag framework.
  - *Recommendation*: `"found"`.

### Field: `age_of_onset`
- **Note Text Snippet**: `"A 34-year-old female presents..."`
- **Current Assignment**: `"missing"`
- **Clinical Nuance / Ambiguity**:
  - The red flag in SNNOOP10 is: *"Older age of onset (new onset or progressive headache after age 50)"*.
  - Because the patient is 34, this red flag is clinically irrelevant/not present.
  - *Question*: Is this field `"missing"` because the clinician did not discuss headache onset history relative to age, or is it `"negated"` because documenting age 34 objectively rules out onset > 50?
  - *Recommendation*: `"missing"` in documentation audit, because the specific red-flag assessment for late-onset headache wasn't a documented clinical review item (the patient simply is young).

---

## 4. `ha_incomplete` (Deficient Primary Headache Note Missing Red Flags)

### Field: `focal_neurological_deficits`
- **Note Text Snippet**: `"Cranial nerves grossly intact per brief exam"`
- **Current Assignment**: `"negated"`
- **Clinical Nuance / Ambiguity**:
  - In neurological documentation, `"grossly intact"` indicates that cranial nerve assessment was performed and **no focal cranial deficit** was identified (i.e. normal/negative finding).
  - *Question*: Should normal physical exam findings that rule out deficits be labeled `"negated"` (explicitly documented as absent/normal) or `"found"`?
  - *Recommendation*: `"negated"`. In Clarity's architecture, red flags that are documented as absent/normal are treated as negated findings rather than affirmative presence of pathology.

---

## 5. `ha_negated` (Secondary Headache Rule-Out Note with Negated Red Flags)

### Field: `sudden_thunderclap_onset`
- **Note Text Snippet**: `"Patient presents with persistent bilateral tension-type headache."`
- **Current Assignment**: `"missing"`
- **Clinical Nuance / Ambiguity**:
  - The note characterizes the presentation as "persistent bilateral tension-type". While this description implies a gradual or non-thunderclap nature, the physician never explicitly asked about or documented the exclusion of sudden/thunderclap onset.
  - *Recommendation*: `"missing"`.
