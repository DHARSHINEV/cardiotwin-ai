# Model Card: CardioTwin AI Multimodal Deterioration Risk Forecaster

## 1. Model Details
- **Model Name:** CardioTwin AI Fusion Forecaster (`v1.0-fusion`)
- **Model Developers:** CardioTwin AI Engineering Team (Digital Twin Challenge 2026 by Happiest Health)
- **Model Architecture:** Multimodal Ensemble Gradient Boosting Classifier (`HistGradientBoosting` / `XGBoost` compatible)
- **Input Modalities:** 
  1. Static EHR Clinical Profile (Age, BMI, SBP, DBP, HbA1c, LDL, Comorbidities, Medication Adherence)
  2. Longitudinal Wearable Telemetry (Resting Heart Rate, HRV RMSSD, Nocturnal SpO2, Daily Step Count, Sleep Duration, Respiratory Rate, Stress Index)
  3. Patient-Specific Personal Baseline Deviations ($\Delta\%$ and Z-score distances relative to individual normal distribution)
  4. Unified Twin Drift Score ($[0, 100]$ multivariate Mahalanobis-inspired drift distance)
- **Output:** Multi-horizon Calibrated Probabilities ($P_{6h}$, $P_{24h}$, $P_{72h}$) for acute adverse cardiovascular deterioration, coupled with empirical 95% uncertainty intervals and mathematical feature attribution contributions.
- **License:** Apache 2.0 (Open Prototype)

---

## 2. Intended Use
- **Primary Purpose:** Clinician decision support for early detection of hemodynamic and autonomic physiological deterioration in high-risk cardiovascular patients (hypertension, type-2 diabetes, dyslipidemia).
- **Intended Users:** Cardiologists, internal medicine physicians, telemetry care nurses, and remote patient monitoring (RPM) clinical teams.
- **Out-of-Scope & Prohibited Use:** 
  - **NOT** an autonomous diagnostic system.
  - **NOT** a standalone medical device (SaMD).
  - Must not be used for emergency triaging without direct physician oversight.
  - Must not be used on pediatric cohorts or acute surgical trauma without model retraining.

---

## 3. Training & Validation Data
- **Dataset:** Synthetic Multi-Modal Cardiovascular Cohort (1,000 synthetic patient cohorts; 100% synthetic mathematical simulation).
- **Zero Real PII Compliance:** All records generated using correlated physiological priors and Monte Carlo simulation. Zero real-patient health records or identifiers were utilized.
- **Validation Scheme:** Patient-stratified holdout split:
  - 70% Training Cohort (700 patients, zero leakage to test)
  - 15% Validation Cohort (150 patients)
  - 15% Test Cohort (150 patients, completely unseen patient identifiers)
- **Temporal Integrity:** Time-series validation strictly maintains temporal order. No future time points were used to predict past states.

---

## 4. Evaluation & Ablation Results

The following table summarizes the test performance on the patient-stratified holdout set:

| Model Architecture | AUROC | AUPRC | Precision | Recall | F1-Score | Brier Score | False Alerts / Pt-Wk | Median Warning Lead Time |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Model A: EHR-Only** | 0.579 | 0.324 | 0.284 | 0.210 | 0.225 | 0.178 | 3.82 | 2.1 hours |
| **Model B: Wearable-Only** | 0.708 | 0.521 | 0.512 | 0.465 | 0.487 | 0.134 | 2.38 | 7.2 hours |
| **Model C: Digital Twin Fusion** | **0.744** | **0.580** | **0.612** | **0.558** | **0.583** | **0.091** | **0.85** | **14.5 hours** |

*Note: All figures derived from rigorous evaluation on synthetic test benchmarks. Clinical superiority on human populations is explicitly NOT claimed.*

---

## 5. Stress Testing & Robustness Under Missing Telemetry

Model C was subjected to severe sensor dropouts and noise degradation to simulate real-world wearable adherence challenges:

| Wearable Dropout Rate | Retention Strategy | AUROC | F1-Score | Performance Degradation |
| :---: | :---: | :---: | :---: | :---: |
| **0% (Full Telemetry)** | Real-time Stream | 0.744 | 0.583 | 0.0% (Baseline) |
| **10% Random Dropout** | Personal Baseline Imputation | 0.728 | 0.562 | -2.1% |
| **25% Random Dropout** | Personal Baseline Imputation | 0.694 | 0.519 | -6.7% |
| **50% Severe Dropout** | Personal Baseline Imputation | 0.642 | 0.461 | -13.7% |

*Key Takeaway:* The inclusion of personal physiological baselines prevents catastrophic model collapse during sensor dropouts compared to population median imputation.

---

## 6. Explainability & Interpretability
- **Attribution Method:** Transparent additive feature contribution layer ($z$-score distance weighted by physiological sensitivity matrix).
- **Biological Plausibility:** Alerts explicitly trace back to individual sensor deviations (e.g. $+20.6\%$ Resting HR surge, $-34.6\%$ HRV vagal drop).
- **Counterfactual Reasoning:** The What-If Engine allows clinicians to simulate therapeutic modifications (e.g., restoring nocturnal sleep, improving medication adherence) to observe predicted risk trajectory changes.

---

## 7. Limitations & Ethical Considerations
1. **Synthetic Nature:** All evaluations reflect synthetic distributions. Real biological phenomena possess non-linear chaotic dynamics, sub-clinical infections, and behavioral confounders not captured in synthetic models.
2. **Sensor Quality Sensitivity:** Optical PPG sensors are vulnerable to motion artifacts, skin pigmentation variability, and peripheral vasoconstriction. The system incorporates a Data Quality Layer to discount degraded signals.
3. **Alert Fatigue:** Even at 0.85 false alerts per patient-week, long-term RPM monitoring requires clinical prioritization filters.
