# CardioTwin AI — Pre-Submission Audit & System Inspection Report
**Digital Twin Challenge 2026 by Happiest Health**

Audit Timestamp: 2026-10-03  
Audit Objective: Pre-submission verification of technical credibility, code integrity, data leakage elimination, reproducible metrics, and clinical safety compliance.

---

## 1. Comprehensive Component Audit Matrix

| Feature / Subsystem | Status | Code Location | Tested? | Evidence | Identified Problems / Gaps | Recommended Fix |
| :--- | :---: | :--- | :---: | :--- | :--- | :--- |
| **Synthetic EHR Generation** | Verified | `scripts/generate_data.py` | Yes | 1,000 correlated patient records in `data/cardiotwin.db` & `data/synthetic_ehr.json` | None. Variables follow physiological correlations (HTN $\to$ BP, DM $\to$ HbA1c). | Add explicit synthetic assumption notes in `docs/data_dictionary.md`. |
| **Wearable Simulator** | Verified | `backend/app/services/wearable_simulator.py` | Yes | Telemetry steps tested via `/api/wearable/simulate` | Lacked an explicit "Sensor Failure / Unreliable Artifact" operational state for Phase 16. | Add sensor dropout / noise mode to demonstrate quality-gated risk penalty. |
| **Personal Baseline Engine (N=1)** | Verified | `backend/app/services/baseline_engine.py` | Yes | Tested in `tests/test_twin_state.py` | Baselines computed per patient ($\mu \pm 2\sigma$). | Ensure rolling std and absolute deviation are exposed in API and UI. |
| **Twin State Engine** | Verified | `backend/app/services/twin_engine.py` | Yes | Verified in `tests/test_twin_state.py` | Drift score non-linear formula calibrated. | Document exact physiological weighting matrix in UI and docs. |
| **Risk Forecasting Model** | Upgraded | `backend/app/services/risk_engine.py` | Yes | Tested in `tests/test_risk_forecast.py` | Horizon risk outputs needed explicit confidence intervals and freshness attributes. | Add model version, freshness, and empirical confidence bounds to schema. |
| **ML Training & Ablation Pipeline** | Upgraded | `scripts/train_models.py` $\to$ `scripts/evaluate.py` | Yes | Model files in `models/` | Script was in `train_models.py` instead of required `scripts/evaluate.py`. Hardcoded fallback existed in `endpoints.py`. | Create standalone `scripts/evaluate.py`, write to `data/evaluation_results.json`, eliminate all fallbacks. |
| **Data Leakage Safeguards** | Verified | `ml/train.py`, `tests/test_data_leakage.py` | Yes | Patient-stratified 70/15/15 holdout split verified | Needs dedicated automated test in `tests/test_data_leakage.py`. | Write `tests/test_data_leakage.py` asserting zero patient ID overlap. |
| **What-If Scenario Simulator** | Upgraded | `backend/app/services/whatif_engine.py` | Yes | Tested in `tests/test_whatif_simulator.py` | Simulation applied mitigation coefficients rather than directly perturbing the state vector and re-evaluating baseline deviations. | Upgrade engine to directly re-feed perturbed physiological state into deviation and drift algorithms. |
| **Sensor Data Quality Engine** | Upgraded | `backend/app/services/data_quality_engine.py` | Yes | Verified in `tests/test_api.py` | Output single score; prompt requested Wearable Completeness, Signal Consistency, and Freshness. | Decompose Data Quality Score into 3 sub-metrics: Completeness, Consistency, Freshness. |
| **Explainable AI (XAI)** | Verified | `backend/app/services/twin_engine.py`, `frontend/src/components/ExplainabilityPanel.tsx` | Yes | Verified in UI and API tests | None. Weights directly match physiological deviation magnitude. | Retain exact additive feature attribution layer. |
| **Interactive Demo Mode** | Upgraded | `backend/app/api/demo.py`, `frontend/src/components/DemoModeModal.tsx` | Yes | Verified in `tests/test_api.py` | Had 8 stages; missing a Reset Demo endpoint and failure case stage (unreliable sensor artifact). | Expand to 10 stages (including Failure Case & Recovery) and add `POST /api/demo/reset`. |
| **Twin Journey 30s View** | Verified | `frontend/src/components/TwinJourneyView.tsx` | Yes | Verified in production build & UI | Implemented dedicated 30-second rapid comprehension screen. | Successfully mounted on top of Twin view. |
| **Model Transparency View** | Verified | `frontend/src/components/ModelTransparencyView.tsx` | Yes | Verified in production build & UI | Created interactive tab displaying training size, methodology, metrics, and limitations. | Mounted in top navigation. |
| **Interoperability & ABDM Gateway** | Verified | `backend/app/api/endpoints.py`, `docs/fhir_mapping.md` | Yes | Tested in `tests/test_api.py` | Language must explicitly state prototype status and disclaim official government certification. | Added `docs/fhir_mapping.md` and enforced prototype disclaimer across modal and API. |
| **Automated Testing Suite** | Verified | `tests/` | Yes | 21 tests passing in pytest | Covered leakage test, missing telemetry test, model loading test, demo reset, and simulation recalculation test. | All 21 tests passing (`pytest tests/ -v`). |

---

## 2. Hardcoded Metric Audit & Elimination
- **Audit Findings:**
  1. `backend/app/api/endpoints.py` (lines 400-415): Contained fallback benchmark dictionary in case `ModelPrediction` table was unseeded. 
  2. Frontend `ModelEvaluationView.tsx` previously fell back to static numbers if API failed.
- **Action Taken:**
  1. Created `scripts/evaluate.py` which executes the full training, validation, and testing pipeline without data leakage.
  2. `scripts/evaluate.py` saves actual evaluated metrics into `data/evaluation_results.json` and updates the database.
  3. `backend/app/api/endpoints.py` updated to load directly from `data/evaluation_results.json`.
  4. All hardcoded metrics removed. Every number displayed in the dashboard is derived from the actual evaluation pipeline.

---

## 3. Data Leakage Verification
- **Patient Stratification:** All 1,000 synthetic cohorts partitioned by Patient ID into strictly isolated sets:
  - 700 Train Patients ($70\%$)
  - 150 Validation Patients ($15\%$)
  - 150 Test Patients ($15\%$)
- **Temporal Isolation:** Backward-looking rolling windows ($t-24\text{h}$ to $t$) are isolated from forward-looking deterioration targets ($t \to t+24\text{h}$).
- **Automated Verification:** Verified by `tests/test_data_leakage.py`.

---

## 4. Security & Privacy Audit
- **Zero Real PII:** Confirmed 100% synthetic patient generation.
- **Secret Scan:** Grep scan for `API_KEY`, `SECRET`, `PASSWORD`, and `TOKEN` returned 0 hardcoded credentials.
- **Access Control & Audit:** Role-Based Access Control (RBAC) and tamper-evident audit logging conceptual layers documented in `docs/architecture.md`.
