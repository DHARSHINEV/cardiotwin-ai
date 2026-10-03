# CardioTwin AI — Limitations & Responsible AI Controls

## 1. Prototype & Synthetic Data Boundaries
- **Research Proof-of-Concept:** CardioTwin AI is developed solely for the **Digital Twin Challenge 2026 by Happiest Health**. It is an exploratory prototype designed to demonstrate software architecture, multimodal fusion, and personal baseline modeling.
- **Zero Real-Patient Validation:** The system is trained and validated on purely synthetic data generated via mathematical distributions and correlated medical rules. It has **NOT** undergone clinical trials, prospective human testing, or institutional review board (IRB) evaluation.
- **No Diagnostic Claims:** CardioTwin AI does not diagnose myocardial infarction, congestive heart failure, arrhythmias, or any other medical condition.

---

## 2. Sensor & Physiological Telemetry Caveats
- **Consumer Wearable Noise:** Consumer smartwatches (optical photoplethysmography / PPG) are prone to motion artifacts, loose wrist fit, and peripheral vasoconstriction during cold weather or shock.
- **Melanin & Skin Tone Attenuation:** Green-light PPG sensors have documented inaccuracies across dark skin pigmentation (Fitzpatrick skin types V and VI). Multi-wavelength infrared validation is required before real-world clinical use.
- **Sampling Gaps:** Battery depletion, charging periods, and patient non-adherence inevitably cause missing readings. While our Personal Baseline Imputation retains model stability up to 25% missingness, prolonged telemetry absence degrades predictive reliability.

---

## 3. Human-in-the-Loop & Decision Support Invariants
- **Non-Autonomous Operations:** The AI never alters drug prescriptions, medical therapies, or hospital admission decisions autonomously. All recommendations and counterfactual projections exist strictly for clinician evaluation.
- **Automation Bias Prevention:** Alerts explicitly list the underlying raw physiological deviations (e.g. $+20.6\%$ Resting HR, $-34.6\%$ HRV) so physicians can independently verify the primary clinical evidence rather than blindly trusting a single composite probability.
- **False Positive vs. False Negative Trade-Offs:** The 24-hour decision threshold ($0.35$) is optimized for high sensitivity ($85.0\%$) and warning lead time ($14.5$ hours) while keeping false alerts under $0.85$ per patient-week. In clinical deployment, alert thresholds must be customizable per clinical department.

---

## 4. India-Specific Health Interoperability Notice
- **ABDM Architectural Direction:** References to the Ayushman Bharat Digital Mission (ABDM), Ayushman Bharat Health Account (ABHA), and HL7 FHIR R4 reflect architectural alignment and API structural readiness. They do **NOT** imply official certification, accreditation, or government empanelment.
