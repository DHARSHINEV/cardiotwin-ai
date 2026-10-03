# CardioTwin AI — System Architecture & Digital Twin Methodology

## 1. Executive Summary & Philosophy
**CardioTwin AI** is an end-to-end clinical decision support system designed for earlier, personalized cardiovascular risk awareness.
Traditional clinical predictive models evaluate a static slice of EHR variables to generate a single risk probability ($f(X) \to \hat{y}$). 
In contrast, CardioTwin AI maintains a continuous, personalized virtual representation (the **Digital Twin**) of the patient's individual cardiovascular state.

```
                    +------------------------------------+
                    |        Synthetic EHR Profile       |
                    | (Age, SBP, DBP, HbA1c, Meds, Med%) |
                    +-----------------+------------------+
                                      |
                                      v
+-----------------------------+       |
| Real-Time Wearable Stream   |       |
| (PPG HR, HRV, SpO2, Sleep)  |       |
+--------------+--------------+       |
               |                      |
               v                      v
+-----------------------------+  +-------------------------------+
|     Data Quality Engine     |  |   Personal Baseline Engine    |
| (PPG Artifacts, Sampling Gap|  | (Individual Mean, SD, 95% CI) |
+--------------+--------------+  +---------------+---------------+
               \                     /
                \                   /
                 v                 v
            +---------------------------+
            | Digital Twin State Engine |
            |  (Twin Drift Score 0-100) |
            +-------------+-------------+
                          |
                          v
            +---------------------------+
            |  Multi-Horizon Forecaster |
            |    (6h, 24h, 72h Risks)   |
            +-------------+-------------+
                          |
             +------------+------------+
             |                         |
             v                         v
+-------------------------+ +-------------------------+
|     Explainable AI      | | What-If Scenario Sim    |
|  (Exact SHAP / Weights) | | (Counterfactual Curves) |
+------------+------------+ +------------+------------+
             \                         /
              \                       /
               v                     v
          +-------------------------------+
          |   Clinician Decision Suite    |
          |  (React / TS / ABDM / FHIR)   |
          +-------------------------------+
```

---

## 2. Architectural Components

### A. Data Ingestion & Synthetic Correlation
- **Synthetic EHR:** Generates clinically correlated cardiovascular cohorts (hypertension $\to$ elevated SBP/DBP, diabetes $\to$ elevated HbA1c, dyslipidemia $\to$ elevated LDL, declining medication adherence $\to$ exacerbated hemodynamic instability).
- **Wearable Simulator:** Simulates real-time multi-sensor streams across 4 operational states:
  1. *Normal State* (tracking personal baseline)
  2. *Gradual Deterioration* (progressive drift over hours/days)
  3. *Acute Anomaly* (sudden hemodynamic perturbation / hypoxia)
  4. *Recovery* (therapeutic stabilization returning toward baseline)

### B. Personal Baseline Engine (The N=1 Concept)
- Calculates individual normal distributions ($\mu_i \pm 2\sigma_i$) over quiescent calibration intervals for each signal:
  - Resting Heart Rate (bpm)
  - HRV RMSSD (ms)
  - Nocturnal Sleep Duration (hours)
  - Daily Step Count (steps/day)
  - Nocturnal SpO2 (%)
  - Respiratory Rate (breaths/min)
  - Autonomic Stress Index (0-100)
- **Key Insight:** Avoids arbitrary population thresholds. Distinguishes between an athlete whose normal RHR is $50$ bpm vs. a patient whose normal RHR is $68$ bpm and for whom $82$ bpm is $+2.8\sigma$ elevated.

### C. Twin Drift Score & State Engine
- Calculates multivariate physiological distance from the patient's calibrated baseline:
$$\text{Twin Drift Score} = 100 \cdot \left(1 - e^{-0.45 \cdot \bar{Z}_{\text{weighted}}}\right)$$
- Categorizes drift into 4 clinical levels:
  - **Normal:** $[0.0 - 24.9]$
  - **Watch:** $[25.0 - 49.9]$
  - **Elevated:** $[50.0 - 74.9]$
  - **High:** $[75.0 - 100.0]$

### D. Data Quality Engine
- Validates physiological plausibility, flatlines, ectopic beat distortion in HRV, and optical sensor disconnections.
- Dynamically discounts corrupted signals and modulates model confidence intervals ($CI_{95\%} = \hat{p} \pm \Delta_{\text{quality}}$).

### E. Multi-Horizon Risk Forecasting
- Calibrated Gradient Boosting models compute discrete probabilities for 3 temporal windows:
  - **6-hour risk:** Acute immediate hemodynamic volatility
  - **24-hour risk:** Primary remote patient monitoring early-warning window
  - **72-hour risk:** Cumulative multi-day deterioration progression

### F. What-If Digital Twin Scenario Simulator
- Enables clinicians to explore virtual interventions (e.g. restoring nocturnal sleep from 5.4h to 7.2h, increasing medication adherence from 70% to 95%, light physical activity).
- Projects dual trajectories (**Unmitigated Current** vs. **Simulated Trajectory**) and synthesizes counterfactual explanations.
- Explicitly watermarked: `SIMULATED SCENARIO — NOT A CLINICAL PREDICTION`.

### G. Interoperability & India-Specific ABDM Layer
- Maps Digital Twin states and observations to **HL7 FHIR R4** (`Patient`, `Observation` with LOINC and custom Twin Drift codes).
- Integrates conceptual ABHA Health ID bindings and role-based clinician audit logging.

---

## 3. Technology Stack
- **Backend:** Python 3.14, FastAPI, SQLAlchemy, Pydantic v2, Scikit-Learn, Joblib
- **Database:** SQLite (local development zero-config) / PostgreSQL (production containerized)
- **Frontend:** React 19, TypeScript, Vite, Tailwind CSS, Recharts, Lucide Icons
- **ML & Analytics:** Scikit-learn Gradient Boosting, Pandas, NumPy, ReportLab
