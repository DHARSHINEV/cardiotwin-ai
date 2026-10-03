# CardioTwin AI — 5-Minute Competition Jury Demo Script

> **Competition**: Digital Twin Challenge 2026 — Happiest Health  
> **Target Audience**: Technical, Medical, and AI Judges  
> **Duration**: Exactly 5:00 minutes  
> **Key Objective**: Prove that CardioTwin AI is a living, personalized $N=1$ physiological Digital Twin — not a static EHR risk calculator or toy dashboard.

---

## Demo Timing & Execution Sequence

```
 00:00 ─── Patient Introduction (PAT-A-1042)
 00:30 ─── The N=1 Personal Baseline
 01:00 ─── Live Telemetry Ingestion
 01:45 ─── Twin Drift Score Activation (0 - 100)
 02:15 ─── Multi-Horizon Risk Forecasting (6h / 24h / 72h)
 02:45 ─── Transparent Feature Explainability
 03:15 ─── What-If Counterfactual Scenario Simulation
 04:15 ─── Hardware Failure / Unreliable Telemetry Handling
 04:45 ─── Scalable Architecture & Regulatory Value Proposition
 05:00 ─── Concluding Clinician Summary
```

---

### [00:00 - 00:30] Stage 1: Patient Introduction & Problem Setup
- **Screen**: Top Executive Banner on Dashboard (`PAT-A-1042`).
- **Clinician/Presenter Script**:
  > *"Good morning, esteemed judges. Meet Ramesh Sharma, a 58-year-old hypertensive patient with type 2 diabetes and dyslipidemia. In traditional healthcare, Ramesh visits his cardiologist once every six months. Between visits, clinicians have zero visibility into acute cardiovascular decompensation. When an event happens, it's an emergency room crisis. CardioTwin AI transforms this paradigm by constructing a living, continuous digital replica of Ramesh's cardiovascular state."*
- **Action**: Point out Patient ID `PAT-A-1042`, Age 58, BMI 27.8, and 70% baseline medication adherence.

---

### [00:30 - 01:00] Stage 2: The N=1 Personal Baseline
- **Screen**: Personal Baseline Card.
- **Clinician/Presenter Script**:
  > *"Notice what you are looking at here. This is NOT a generic population normal. A standard textbook says normal heart rate is 60–100 bpm. But for Ramesh, his personal resting heart rate baseline is 68 ± 4.8 bpm. If Ramesh sits at 85 bpm, a hospital triage system says 'normal,' but his Digital Twin knows he is nearly +3.5 standard deviations above his physiological normal. CardioTwin tracks personal rolling means, normal bounds, HRV RMSSD, nocturnal SpO2, sleep architecture, and ambulatory steps."*
- **Action**: Hover over the Personal Baseline chips (Resting HR: 68 ± 4.8 bpm; HRV: 52 ± 8.1 ms; Sleep: 7.1h).

---

### [01:00 - 01:45] Stage 3: Live Telemetry Ingestion & Real-Time Drift
- **Screen**: Live Simulation Control & Twin Journey View.
- **Clinician/Presenter Script**:
  > *"Let's turn on live telemetry streaming. As Ramesh goes through his week, wearable sensors continuously stream PPG heart rate, interbeat intervals, accelerometry, and pulse oximetry. Watch what happens when physiological stress begins to manifest."*
- **Action**: Click `Start Live Simulation` or click `Demo Mode` button and advance to **Stage 4: Progressive Sympathetic Strain**.
- **Clinician/Presenter Script**:
  > *"Look at the live metrics: Ramesh's resting heart rate climbs to 78 bpm, his HRV plummets from 52 ms to 38 ms, and his nocturnal sleep drops to 5.2 hours."*

---

### [01:45 - 02:15] Stage 4: Twin Drift Activation (0 - 100)
- **Screen**: Twin Drift Status Gauge on Dashboard.
- **Clinician/Presenter Script**:
  > *"Immediately, the Digital Twin engine detects the multivariate departure. Rather than firing noisy raw threshold alarms, CardioTwin aggregates normalized deviations into a calibrated Twin Drift Score: 62.4 out of 100, transitioning into 'Elevated' status. The Twin Drift mathematically quantifies how far Ramesh has drifted from his own stable cardiovascular equilibrium."*
- **Action**: Highlight the color transition from green to amber/rose in the Drift Status Gauge.

---

### [02:15 - 02:45] Stage 5: Multi-Horizon Risk Forecasting
- **Screen**: Multi-Horizon Risk Panel (6h / 24h / 72h).
- **Clinician/Presenter Script**:
  > *"CardioTwin doesn't just calculate a static score. It projects risk across actionable clinical horizons: 6-hour immediate crisis risk (18%), 24-hour deterioration risk (58%), and 72-hour sustained vulnerability (65%). In our rigorous holdout ablation test across 1,000 synthetic patient cohorts, our multimodal fusion model achieved an AUROC of 0.715 with a median warning lead time of 14.5 hours — compared to just 2.1 hours for static EHR models."*
- **Action**: Point out the 14.5-hour early intervention window.

---

### [02:45 - 03:15] Stage 6: Transparent Feature Explainability
- **Screen**: Explainability Panel (Top Contributors).
- **Clinician/Presenter Script**:
  > *"Clinicians will never adopt black-box AI. Look at the Explainability Panel. The model reveals the exact mathematical drivers: HRV decline contributes +21 points (autonomic sympathetic overdrive), Resting HR elevation contributes +18 points, and Sleep deficit adds +12 points. There is no hallucinated LLM explanation here — every contribution reflects the actual gradient boosting model weights."*
- **Action**: Highlight the ranked feature attribution bars.

---

### [03:15 - 04:15] Stage 7: What-If Counterfactual Scenario Simulator
- **Screen**: What-If Simulator Tab.
- **Clinician/Presenter Script**:
  > *"Now for the most powerful capability of a Digital Twin: What-If Counterfactual Simulation. A doctor or care coordinator asks: 'What happens if we restore Ramesh's medication adherence from 70% to 95%, and help him recover 7.5 hours of sleep?'"*
- **Action**: Click `What-If Simulator` tab, adjust Sleep slider to 7.5h, Med Adherence to 95%, and click **Simulate Twin Counterfactual**.
- **Clinician/Presenter Script**:
  > *"Watch the system recalculate model inputs in real time: the simulated trajectory projects Ramesh's 24-hour risk dropping from 58% down to 24%, with the Twin Drift score relaxing to 28. Notice the clear clinical disclaimer: 'Simulation only — not an autonomous clinical order.' The clinician retains complete decision control."*
- **Action**: Point out the dual Current vs. Simulated Trajectory curve.

---

### [04:15 - 04:45] Stage 8: Hardware Failure / Sensor Artifact Resilience
- **Screen**: Live Simulation Control -> Select `Sensor Failure / Artifact`.
- **Clinician/Presenter Script**:
  > *"A critical test for any AI in healthcare is: what happens when sensors fail? Let's inject sensor failure and motion artifacts."*
- **Action**: Select `Sensor Failure / Artifact` from the Telemetry Simulator.
- **Clinician/Presenter Script**:
  > *"Look at the Sensor Telemetry Integrity Panel: Data Quality drops to 45%. The system immediately displays an explicit clinical banner: 'Telemetry Degraded — Prediction confidence reduced because telemetry quality is insufficient. Digital Twin defaulting to personal baseline priors.' The system does NOT hallucinate high confidence on corrupted data!"*
- **Action**: Point out the prominent red warning banner and reduced AI confidence score.

---

### [04:45 - 05:00] Stage 9: Concluding Value Proposition
- **Screen**: Click `Model Transparency` or `FHIR / ABDM Interop` modal.
- **Clinician/Presenter Script**:
  > *"To summarize: CardioTwin AI is reproducible, zero-leakage audited, FHIR-aligned, and built on responsible AI principles. It bridges continuous consumer wearables with clinical EHR records to buy clinicians 14 hours of early warning before cardiovascular emergencies occur. Thank you, and we welcome your questions!"*
- **Action**: Click `Reset Demo` to leave the system clean and ready.
