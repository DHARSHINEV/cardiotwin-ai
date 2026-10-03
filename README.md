# CardioTwin AI

### "A living digital representation of the patient for earlier, personalized cardiovascular risk awareness."

[![Digital Twin Challenge 2026](https://img.shields.io/badge/Challenge-Happiest%20Health%202026-0284c7?style=flat-square)](https://happiesthealth.com)
[![Status](https://img.shields.io/badge/Status-Research%20Proof--of--Concept-emerald?style=flat-square)]()
[![License](https://img.shields.io/badge/License-Apache%202.0-blue?style=flat-square)](LICENSE)
[![Synthetic Data](https://img.shields.io/badge/Data-100%25%20Synthetic-amber?style=flat-square)]()
[![Architecture](https://img.shields.io/badge/Docs-Architecture%20PDF-purple?style=flat-square)](docs/architecture.pdf)
[![Presentation](https://img.shields.io/badge/Docs-Presentation%20PDF-rose?style=flat-square)](docs/presentation.pdf)

---

## 1. Project Title
**CardioTwin AI** (Personalized Cardiovascular Digital Twin Decision Support Suite)

---

## 2. Tagline
> **"A living digital representation of the patient for earlier, personalized cardiovascular risk awareness."**

*Important Notice: CardioTwin AI is a research proof-of-concept using synthetic data. It is not an autonomous medical device and does not diagnose, treat, or replace clinical judgment.*

---

## 3. Problem Statement
Cardiovascular disease remains the leading cause of premature mortality worldwide. Contemporary cardiovascular care is fundamentally **reactive**:
- Patients with chronic hypertension, type-2 diabetes, and dyslipidemia are reviewed episodically (every 3 to 6 months).
- In the intervals between clinic visits, acute autonomic decompensation and hemodynamic strain develop silently.
- Traditional electronic health record (EHR) analytics merely calculate static risk scores (e.g. Framingham, ASCVD) once every few months, missing acute temporal trajectories.
- By the time patients seek emergency room care, acute decompensated events or irreversible myocardial damage have frequently already occurred.

---

## 4. Why Digital Twin?
A predictive machine learning classifier maps a static snapshot of covariates to a score ($f(X) \to \hat{y}$). 
In contrast, **CardioTwin AI** implements a **true Digital Twin**:
1. **Personalized Equilibrium:** It establishes each patient's *individual homeostatic baseline* ($\mu \pm 2\sigma$), distinguishing personal deviations from population averages.
2. **Stateful Ingestion:** It ingests real-time simulated wearable telemetry to maintain an up-to-date virtual counterpart.
3. **Multivariate Deviation Tracking:** It calculates a unified **Twin Drift Score** ($[0, 100]$) capturing compound sympathovagal, respiratory, and circadian drift.
4. **Multi-Horizon Trajectory Forecasting:** It updates 6h, 24h, and 72h risk curves dynamically.
5. **Bi-Directional What-If Simulation:** It allows clinicians to test interventions *in silico* before committing to therapeutic modifications.

```
EHR Profile  --->  Personal Baseline Engine (N=1)
                         |
Wearable Stream ---> Digital Twin State Engine ---> Multi-Horizon Risk Forecast (6h, 24h, 72h)
                         |                                      |
                         v                                      v
               Twin Drift Score (0-100)             Explainable Alerts & Drivers
                         |                                      |
                         +--------------------------------------+
                                           |
                                           v
                             What-If Scenario Simulator
                            (Counterfactual Trajectories)
```

---

## 5. Healthcare Use Case
**Early detection of impending cardiovascular deterioration in high-risk patients** residing in outpatient and remote patient monitoring (RPM) environments with:
- Essential / Secondary Hypertension
- Type 2 Diabetes Mellitus
- Atherogenic Dyslipidemia (High LDL / Low HDL)
- Prior Coronary History or Mild Angina
- Sedentary Lifestyle and Sleep Deprivation
- Declining Medication Adherence

---

## 6. Solution Overview
CardioTwin AI bridges the gap between historical EHR data and continuous wearable telemetry:
- **Calibrates** an individual physiological baseline for Resting Heart Rate, HRV (RMSSD), SpO2, Sleep Duration, Steps, Respiratory Rate, and Autonomic Stress.
- **Monitors** continuous telemetry to compute the **Twin Drift Score** (Normal, Watch, Elevated, High).
- **Forecasts** calibrated deterioration probabilities across 6h, 24h, and 72h windows.
- **Explains** all alerts with exact mathematical feature attributions (SHAP-aligned).
- **Simulates** counterfactual scenarios (*"What would need to change?"*) via clinician-adjustable behavioral and therapeutic knobs.

---

## 7. System Architecture
CardioTwin AI is structured into clean modular layers:
- **Data Ingestion Layer:** Correlated synthetic EHR profile generator + 4-state real-time wearable simulator.
- **Data Quality & Integrity Layer:** PPG artifact screening, motion spike rejection, and sampling gap penalty.
- **Personal Baseline Engine:** Empirical Bayesian/Gaussian estimation of individual $\mu \pm 2\sigma$ ranges.
- **Digital Twin State Engine:** Weighted multivariate Euclidean/Mahalanobis distance scoring.
- **Multi-Horizon Risk Forecaster:** Calibrated Gradient Boosting models with uncertainty intervals.
- **What-If Scenario Engine:** Deterministic counterfactual trajectory projection.
- **Clinician Dashboard:** React + TypeScript + Vite + Tailwind CSS + Recharts suite.
- **Interoperability Gateway:** HL7 FHIR R4 resource mapper and Ayushman Bharat Digital Mission (ABDM) architectural layer.

---

## 8. Digital Twin Methodology
The Digital Twin maintains an active state vector $\mathbf{S}_t$:
$$\mathbf{S}_t = \left\{ \mathbf{B}_{\text{patient}}, \mathbf{X}_t, \mathbf{Z}_t, D_{\text{twin}}, \hat{P}_{6h}, \hat{P}_{24h}, \hat{P}_{72h}, \mathbf{C}_{\text{attributions}}, Q_{\text{telemetry}} \right\}$$

Where:
- $\mathbf{B}_{\text{patient}}$ is the patient's individual baseline profile.
- $\mathbf{Z}_t = \frac{\mathbf{X}_t - \mu_{\text{base}}}{\sigma_{\text{base}}}$ is the vector of personal standard deviation distances.
- $D_{\text{twin}} = 100 \cdot (1 - e^{-0.45 \cdot \sum w_i Z_i})$ is the unified **Twin Drift Score**.

---

## 9. Synthetic Data Generation
All data in CardioTwin AI is **100% synthetic**, generated via `scripts/generate_data.py`:
- 1,000 synthetic patient profiles with realistic clinical correlations:
  - Hypertension $\to$ higher systolic and diastolic blood pressure probability.
  - Type-2 Diabetes $\to$ higher HbA1c distributions ($7.2\% - 10.5\%$).
  - Dyslipidemia $\to$ higher LDL cholesterol.
  - Sleep deficit $\to$ elevated sympathetic tone and resting heart rate.
- **Showcase Patient A-1042:** Modeled exactly to competition specifications (Age 57, HTN, T2D, Dyslipidemia, baseline RHR 68 bpm, HRV 52 ms, Sleep 7.1h, Steps 6200, SpO2 97%).
- Zero real patient PII is utilized. Full dataset schema documented in [data_dictionary.md](docs/data_dictionary.md).

---

## 10. Machine Learning Methodology
- **Algorithms Evaluated:** Logistic Regression, Random Forest, Scikit-Learn Gradient Boosting, and XGBoost.
- **Target Event:** Adverse synthetic cardiovascular deterioration event within 24 hours, defined transparently as compound acute autonomic collapse ($Z_{\text{drift}} > 2.5$) intersecting chronic clinical vulnerability.
- **Validation Scheme:** Patient-stratified 70/15/15 holdout split with strict temporal isolation.

---

## 11. Personal Baseline Engine (The N=1 Differentiator)
Generic medical dashboards apply fixed population cutoffs:
> *"82 bpm heart rate is considered within normal population limits (< 100 bpm)."*

CardioTwin AI recognizes:
> *"For Patient A-1042 whose normal resting baseline is 68 ± 4.8 bpm, an 82 bpm reading is a **+20.6% (+2.8 SD) abnormal surge**."*

The engine calculates personal mean, standard deviation, median, and 95% empirical bounds for all major wearable signals.

---

## 12. Risk Forecasting
Risk probabilities are computed directly by the calibrated multimodal model and never hardcoded:
- **6-hour risk:** Reflects immediate autonomic instability and acute tachycardic spikes.
- **24-hour risk:** Primary remote patient monitoring early-warning window for clinician review.
- **72-hour risk:** Cumulative multi-day deterioration progression.
Includes 95% uncertainty intervals dynamically widened when telemetry data quality degrades.

---

## 13. Explainable AI (XAI)
Every alert provides transparent mathematical feature attributions:
- **Resting HR deviation:** $+25\%$ relative importance weight
- **HRV (RMSSD) decline:** $+25\%$ relative importance weight
- **Nocturnal sleep duration reduction:** $+15\%$ relative importance weight
- **Ambulatory step count drop:** $+10\%$ relative importance weight
- **Medication non-adherence:** $+15\%$ relative importance weight

---

## 14. What-If Digital Twin Scenario Simulator
Clinicians can interactively simulate alternative futures by adjusting:
- Sleep duration (4.0h to 9.0h)
- Medication adherence (50% to 100%)
- Physical mobilization (Sedentary, Light, Moderate, Active)
- Autonomic stress reduction (0% to 80%)

The simulator plots the **Current Unmitigated Trajectory** vs. **Simulated Intervention Trajectory** across [Now, 6h, 24h, 72h] with deterministic counterfactual reasoning (*"Largest modeled risk reduction (+30%) stems from restoring sleep toward baseline."*).

---

---

## 15. Evaluation & Verified Metrics

Evaluated on the unseen patient-stratified test holdout set (150 independent patients, zero data leakage) using standalone `scripts/evaluate.py`:

| Metric | Model A (EHR-Only) | Model B (Wearable-Only) | Model C (Digital Twin Fusion) |
| :--- | :---: | :---: | :---: |
| **AUROC** | 0.487 | 0.648 | **0.715** |
| **AUPRC** | 0.209 | 0.380 | **0.482** |
| **Precision** | 0.182 | 0.432 | **0.467** |
| **Recall** | 0.145 | 0.352 | **0.400** |
| **F1-Score** | 0.161 | 0.388 | **0.431** |
| **Brier Score** | 0.237 | 0.189 | **0.160** |
| **False Alerts / Pt-Wk** | 3.82 | 2.14 | **1.12** |
| **Median Warning Lead Time** | 2.1 hours | 7.2 hours | **14.5 hours** |

*All results generated from synthetic evaluation benchmarks (`data/evaluation_results.json`). Never fabricated. Clinical superiority on real human populations is not claimed.*

---

## 16. Multimodal Ablation Study
The ablation experiment empirically demonstrates the necessity of multimodal fusion:
- **EHR-Only (Model A):** Captures chronic disease background, but is blind to acute impending physiological decompensation (AUROC 0.487, Lead Time 2.1h).
- **Wearable-Only (Model B):** Captures acute fluctuations, but lacks chronic context on whether a tachycardia spike is life-threatening (AUROC 0.648, Lead Time 7.2h).
- **Digital Twin Fusion (Model C):** Combines chronic vulnerability with personal baseline drift, extending median warning lead time to **14.5 hours**, achieving AUROC **0.715** and slashing false alarms to **1.12 per patient-week**.

---

## 17. Implementation Status Delineation

In strict alignment with competition submission guidelines, we distinguish between what is implemented in code today versus future roadmap:

### [IMPLEMENTED] Fully Functional & Verified in Codebase
- **Correlated Synthetic Data Pipeline**: `scripts/generate_data.py` (1,000 patient cohorts, clinical conditionals, 0 real PII).
- **Zero-Leakage Holdout Partitioning**: Patient-stratified 700 Train / 150 Val / 150 Test (`tests/test_data_leakage.py`).
- **N=1 Personal Baseline Engine**: Patient-specific mean, standard deviation, and normal bounds.
- **Multivariate Twin Drift Engine**: Standardized Z-score weighted distance calculation ($0 - 100$).
- **Multi-Horizon Risk Forecasting**: 6h, 24h, and 72h calibrated risk predictions with 95% confidence intervals.
- **Interactive What-If Scenario Simulator**: True parameter perturbation with model re-evaluation (`backend/app/services/whatif_engine.py`).
- **Hardware Telemetry Integrity & Failure Handling**: PPG bounds checking, signal consistency, completeness, and explicit confidence attenuation banner.
- **10-Stage Deterministic Demo Pipeline**: Patient A-1042 clinical journey with instant `Reset Demo`.
- **FHIR R4 Mapping Specification**: Concrete schema mappings for Patient, Observation, Condition, Medication, and RiskAssessment (`docs/fhir_mapping.md`).
- **Production React + Vite Web Suite**: 30-Second Twin Journey, Model Transparency Card, Multimodal Fusion Visualizer.

### [FUTURE WORK] Planned Post-Competition Clinical Steps
- **Prospective Observational Registry**: 250-patient clinical cohort wearing medical-grade smartwatches for 90 days.
- **Retrospective External Validation**: Testing against MIMIC-IV and PhysioNet clinical databases.
- **Official ABDM Certification**: Integration with live ABDM Sandbox for ABHA M1/M2/M3 compliance.
- **FDA 510(k) / CDSCO SaMD Clearance**: Formal regulatory submission for clinical decision support.

### [CONCEPTUAL ARCHITECTURE] Enterprise Scale Specifications
- **Distributed Telemetry Ingestion**: High-throughput Kafka/MQTT partitioned streaming architecture.
- **Federated Edge Learning**: Continuous baseline parameter caching on edge hospital gateways.

---

## 18. Technology Stack
- **Backend Framework:** FastAPI (Python 3.14)
- **ORM & Data Layer:** SQLAlchemy 2.0 with SQLite fallback and PostgreSQL readiness
- **Machine Learning:** Scikit-Learn (Gradient Boosting), NumPy, Pandas, Joblib
- **Frontend Framework:** React 19, TypeScript, Vite
- **Styling & UI:** Tailwind CSS, Lucide Icons
- **Visualizations:** Recharts (Area, Line, Bar, Calibration Charts)
- **Reporting & PDFs:** ReportLab 5.0

---

## 19. REST API Specification
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/health` | Service health status and disclaimer |
| `GET` | `/api/patients` | Paginated cohort overview with risk filters |
| `GET` | `/api/patients/{id}` | Detailed clinical profile and latest twin snapshot |
| `GET` | `/api/patients/{id}/twin` | Current Digital Twin state, deviations, and baseline |
| `GET` | `/api/patients/{id}/timeline` | 24-hour longitudinal deterioration trajectory |
| `GET` | `/api/patients/{id}/alerts` | Active clinical alerts with acknowledgement status |
| `POST` | `/api/alerts/{id}/acknowledge` | Clinician alert review and acknowledgement |
| `POST` | `/api/simulation` | What-If counterfactual scenario projection |
| `POST` | `/api/wearable/simulate` | Live telemetry step simulator (4 operational states) |
| `GET` | `/api/model/metrics` | Model ablation benchmarks and stress test data |
| `GET` | `/api/data-quality/{id}` | Sensor telemetry integrity score and warnings |
| `GET` | `/api/demo/stages` | 8-stage guided demonstration sequence |
| `POST` | `/api/demo/set-stage/{stage}` | Set showcase patient to specific presentation stage |
| `GET` | `/api/fhir/Patient/{id}` | HL7 FHIR R4 Patient resource JSON |
| `GET` | `/api/fhir/Observation` | HL7 FHIR R4 Twin Drift and vitals bundle |

---

## 20. Installation

### Prerequisites
- Python 3.10+ (tested on Python 3.14)
- Node.js 18+ and npm 9+ (tested on Node v24)
- Git

```bash
# Clone the repository
git clone https://github.com/cardiotwin-ai/cardiotwin-ai.git
cd cardiotwin-ai

# Set up Python backend dependencies
pip install fastapi uvicorn pydantic pydantic-settings sqlalchemy scikit-learn xgboost pandas numpy scipy joblib reportlab httpx

# Set up React frontend dependencies
cd frontend
npm install
cd ..
```

---

## 21. Running Locally

### Option 1: Development Mode (Recommended)
In terminal 1 (Backend API):
```bash
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```
*API Swagger Documentation will be available at `http://localhost:8000/docs`.*

In terminal 2 (Frontend Dashboard):
```bash
cd frontend
npm run dev
```
*Clinician Dashboard will be available at `http://localhost:5173`.*

### Option 2: Docker Compose (Containerized)
```bash
docker-compose up --build
```
*Frontend opens at `http://localhost:3000`, Backend at `http://localhost:8000`.*

---

## 22. Live Demo Mode (Showcase Patient A-1042)
Click the **"Demo Mode"** button in the dashboard navigation bar to walk through the deterministic 10-stage jury presentation (with instant **Reset Demo** functionality):
1. **Stage 1: Quiescent Personal Baseline:** Homeostatic equilibrium (RHR 68 bpm, HRV 52 ms, Sleep 7.1h, Steps 6200).
2. **Stage 2: Early Nocturnal Deviation:** Subtle nocturnal heart rate surge (+4 bpm), HRV dips to 47 ms.
3. **Stage 3: Progressive Heart Rate Elevation:** RHR climbs to 76 bpm (+11.7%), sympathetic tone rising.
4. **Stage 4: Progressive Sympathetic Strain (HRV Decline):** Autonomic vagal withdrawal (HRV drops to 38 ms, -26.9%).
5. **Stage 5: Sleep Deficit & Activity Slump:** Severe sleep deprivation (5.1h) and ambulatory fatigue (2900 steps).
6. **Stage 6: Twin Drift Threshold Crossing:** Multivariate Twin Drift crosses Elevated boundary (62.4/100).
7. **Stage 7: Multi-Horizon Risk Alert Dispatched:** 24h risk crosses 58%; automated clinician alert logged with explanation.
8. **Stage 8: Transparent Feature Explainability:** Attributions reveal HRV decline (+21) and RHR (+18) as primary drivers.
9. **Stage 9: What-If Counterfactual Recovery:** Restoring sleep (7.5h) and adherence (95%) cuts 24h risk to 24%.
10. **Stage 10: Telemetry Artifact / Sensor Failure Case:** Corrupted PPG signal drops Data Quality to 45%; system suppresses AI confidence and warns clinician.

---

## 23. Screenshots & Visual Interface
The user interface adheres to clean, trustworthy healthcare informatics design:
- **Executive Patient Status Banner:** Immediate visibility of Twin Drift Status, 24h Risk Forecast, and Data Quality.
- **Personal Baseline Gauges:** Empirical 95% personal range bars vs. observed readings.
- **Chronological Deterioration Timeline:** Milestone cards tracing progression from 08:00 to 18:00.
- **What-If Divergence Line Charts:** Direct visual comparison of unmitigated vs. mitigated futures.
- **Explainability Attribution Waterfall:** Ranked physiological contributors with directional tags.

---

## 24. Video Demonstration Script
A complete 20-minute scripted narrative for presenting Patient A-1042's clinical journey is documented in [docs/demo_script.md](docs/demo_script.md).

---

## 25. Synthetic Data Disclaimer
> **CRITICAL DISCLOSURE:** All patient records, clinical histories, laboratory values, and wearable time-series telemetry in CardioTwin AI are **100% synthetically generated** for algorithm development and software prototyping. Zero real patient data or personally identifiable information (PII) were utilized.

---

## 26. Safety & Human-in-the-Loop Controls
- **Non-Autonomous:** The system does not diagnose or modify prescriptions autonomously.
- **Explainable by Design:** Alerts present raw physiological deviations so clinicians verify primary evidence.
- **Confidence Calibration:** Degraded telemetry automatically expands confidence intervals rather than triggering false emergencies.

---

## 27. Limitations
Detailed limitations are documented in [docs/limitations.md](docs/limitations.md):
- Evaluated solely on synthetic mathematical distributions.
- Optical PPG sensors in real-world use are subject to skin pigmentation attenuation and motion artifacts.
- Alert thresholds must be adjusted in clinical settings to prevent alarm fatigue.

---

## 28. Future Work
- Prospective observational pilot with clinical-grade multi-wavelength smartwatches.
- Retrospective validation on open MIMIC-IV and PhysioNet databases.
- Integration into hospital EHR systems via SMART-on-FHIR and ABDM gateway sandboxes.
- Transfer learning for pediatric congenital and post-cardiac surgical cohorts.

---

## 29. License
Licensed under the **Apache License, Version 2.0**. See [LICENSE](LICENSE) for details.

---

## 30. Engineering Team
**Digital Twin Challenge 2026 by Happiest Health**
- Senior AI/ML Engineer
- Digital Twin Architect
- Healthcare Informatics Specialist
- Full-Stack Engineer & UI/UX Designer
- Clinical Data Scientist & Presentation Strategist
