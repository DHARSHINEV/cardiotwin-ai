# CardioTwin AI — Demonstration Script & Presentation Narrative

**Hackathon Challenge:** Digital Twin Challenge 2026 — Happiest Health  
**Showcase Patient:** Patient A-1042 (Male, Age 57, HTN, T2D, Dyslipidemia)  
**Presenter Roles:** AI/ML Lead, Clinical Informatics Specialist, Frontend Engineer

---

### Act 1: The Clinical Problem (0:00 - 2:00)
> *"Judges, modern cardiovascular care is reactive. A 57-year-old patient with hypertension and type-2 diabetes visits their cardiologist every six months. Their clinic blood pressure looks acceptable, their labs are reviewed, and they are sent home. But in between visits, continuous physiological changes occur silently. By the time the patient arrives at the emergency room with severe decompensation, irreversible damage has occurred. 
> 
> Current AI solutions simply run a static risk score on the EHR once every few months. But health is not static — it is a continuous physiological trajectory."*

---

### Act 2: The Solution & Digital Twin Core (2:00 - 4:00)
> *"We built **CardioTwin AI** — a living digital representation of the patient for earlier, personalized cardiovascular risk awareness.
> 
> Let us look at Patient A-1042. Notice what CardioTwin AI does differently:
> 1. It does NOT compare him to generic population averages.
> 2. It learns his **Personal Physiological Baseline**: his quiescent resting heart rate is **68 bpm**, his HRV is **52 ms**, his normal sleep is **7.1 hours**, and his daily activity is **6,200 steps**.
> 
> To a standard system, a heart rate of 82 bpm might look completely normal. But to CardioTwin AI, 82 bpm represents a significant **+20.6% (+2.8 SD) surge** above his own normal equilibrium."*

---

### Act 3: Live Deterioration Simulation (4:00 - 7:00)
> *"Watch our **Live Telemetry Simulator** in action:
> - We step forward through the 24-hour deterioration progression.
> - **At 08:00:** The patient is in stable baseline. Twin Drift Score is 12 (Normal).
> - **At 10:00 to 12:00:** Nocturnal resting HR rises to 75 bpm, while HRV drops to 43 ms. Vagal withdrawal is occurring.
> - **At 14:00:** A 1.7-hour sleep deficit compounds, and activity drops by 45%.
> - **At 16:00:** Twin Drift crosses the Elevated boundary.
> - **At 18:00:** Twin Drift hits 81 (High), and the forecasted 24-hour deterioration risk crosses 71%. 
> 
> Notice how the system automatically issues a non-alarmist, explainable clinical alert before any acute hospitalization event."*

---

### Act 4: Explainable AI & Telemetry Quality (7:00 - 9:00)
> *"Clinicians reject black-box scores. CardioTwin AI's **Explainable AI Attribution Layer** immediately reveals why risk escalated:
> - Resting HR deviation accounts for +25% weight (+20.6% elevation)
> - HRV vagal withdrawal accounts for +25% weight (-34.6% reduction)
> - Compounding sleep deficit accounts for +15% weight
> 
> Crucially, our **Data Quality Engine** verifies that the optical PPG sensor has 96% uptime and filters out motion spikes so clinicians never act on bad data."*

---

### Act 5: The What-If Scenario Simulator (9:00 - 11:30)
> *"Now for our core breakthrough: **The What-If Digital Twin Scenario Simulator**.
> 
> As clinicians, we don't just want to know that a patient is deteriorating — we want to know what happens if we intervene.
> 
> Using our interactive levers:
> - We simulate restoring nocturnal sleep from 5.4h back toward baseline (7.2h).
> - We simulate optimizing medication adherence from 70% to 95%.
> - We simulate gentle mobilization.
> 
> Instantly, the system projects dual trajectories:
> - The red line shows the unmitigated deterioration trajectory (rising to 78% risk).
> - The green dashed line shows the simulated intervention trajectory, where 24-hour risk drops to 28% and stabilizes!
> - The counterfactual engine explicitly tells the clinician: *'The largest modeled improvement stems from restoring sleep duration (+30.0% relative risk mitigation) and improving medication compliance.'*"*

---

### Act 6: Model Evaluation, Ablation & Safety (11:30 - 13:00)
> *"Finally, we evaluated our system across 1,000 synthetic patient cohorts using strict patient-stratified holdout test splits with zero data leakage:
> - **Model A (EHR-Only):** AUROC 0.579, Lead Time 2.1 hours.
> - **Model B (Wearable-Only):** AUROC 0.708, Lead Time 7.2 hours.
> - **Model C (Multimodal Fusion Digital Twin):** AUROC 0.744 (0.85+ on high-quality telemetry), Lead Time **14.5 hours**!
> 
> We also stress-tested the model under 25% sensor dropouts, proving that personal baseline imputation prevents catastrophic model collapse.
> 
> CardioTwin AI is open, transparent, fully synthetic, and architecturally aligned with India's Ayushman Bharat Digital Mission (ABDM) and HL7 FHIR R4."*
