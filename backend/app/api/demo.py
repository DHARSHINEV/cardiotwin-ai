"""
Demo Mode Engine for CardioTwin AI.
Provides deterministic 10-stage interactive demonstration flow for jury presentations:
Stage 1: Stable baseline
Stage 2: Early deviation
Stage 3: HR increase
Stage 4: HRV decline
Stage 5: Sleep/activity deterioration
Stage 6: Twin Drift increase
Stage 7: Risk alert generated
Stage 8: Explainability & What-If simulation
Stage 9: Failure Case Demo (Sensor artifact / degraded telemetry -> confidence reduced)
Stage 10: Recovery & stabilization
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from typing import Dict, Any

from backend.app.db.session import get_db
from backend.app.models.db_models import Patient, EHRRecord, WearableReading, TwinState, Alert
from backend.app.services.baseline_engine import PersonalBaselineEngine
from backend.app.services.twin_engine import DigitalTwinEngine
from backend.app.services.risk_engine import RiskForecastingEngine

router = APIRouter(prefix="/demo", tags=["Demo Mode"])

DEMO_STAGES = [
    {
        "stage": 1,
        "title": "Stable Baseline",
        "description": "Patient A-1042 in stable quiescent state. Wearables closely track personal baseline values.",
        "telemetry": {"resting_hr": 68.0, "hrv": 52.0, "sleep_duration": 7.1, "steps": 6200, "spo2": 97.0, "respiratory_rate": 14.5, "stress_index": 28.0},
        "drift_score": 12.4,
        "drift_level": "Normal",
        "risk_24h": 0.08,
        "data_quality": 98.0,
        "key_event": "Personal baseline established: RHR 68 bpm, HRV 52 ms."
    },
    {
        "stage": 2,
        "title": "Early Autonomic Deviation",
        "description": "Subtle nocturnal elevation in resting HR (+4 bpm) and modest HRV attenuation (-4 ms).",
        "telemetry": {"resting_hr": 72.0, "hrv": 48.0, "sleep_duration": 6.8, "steps": 5100, "spo2": 97.0, "respiratory_rate": 15.0, "stress_index": 35.0},
        "drift_score": 26.8,
        "drift_level": "Watch",
        "risk_24h": 0.14,
        "data_quality": 97.0,
        "key_event": "Early autonomic drift detected: Watch status initiated."
    },
    {
        "stage": 3,
        "title": "Resting HR Elevation",
        "description": "Resting HR increases to 75 bpm (+10.3%), sympathetic activation detected.",
        "telemetry": {"resting_hr": 75.0, "hrv": 45.0, "sleep_duration": 6.5, "steps": 4600, "spo2": 96.8, "respiratory_rate": 15.4, "stress_index": 42.0},
        "drift_score": 38.2,
        "drift_level": "Watch",
        "risk_24h": 0.19,
        "data_quality": 96.0,
        "key_event": "Resting HR exceeds +1.5 personal standard deviations."
    },
    {
        "stage": 4,
        "title": "Vagal HRV Decline",
        "description": "HRV drops to 39 ms (-25.0%), indicating progressive parasympathetic withdrawal.",
        "telemetry": {"resting_hr": 78.0, "hrv": 39.0, "sleep_duration": 6.0, "steps": 3900, "spo2": 96.5, "respiratory_rate": 16.0, "stress_index": 52.0},
        "drift_score": 48.9,
        "drift_level": "Watch",
        "risk_24h": 0.26,
        "data_quality": 96.0,
        "key_event": "Sympathovagal balance shifts toward sustained distress."
    },
    {
        "stage": 5,
        "title": "Sleep & Activity Deterioration",
        "description": "Sleep duration drops to 5.4h (1.7h deficit), daily steps slump by 55% to 2,800 steps.",
        "telemetry": {"resting_hr": 80.0, "hrv": 36.0, "sleep_duration": 5.4, "steps": 2800, "spo2": 96.0, "respiratory_rate": 16.5, "stress_index": 64.0},
        "drift_score": 62.4,
        "drift_level": "Elevated",
        "risk_24h": 0.38,
        "data_quality": 95.0,
        "key_event": "Twin Drift crosses Elevated threshold (62.4)."
    },
    {
        "stage": 6,
        "title": "Twin Drift Surge",
        "description": "Resting HR reaches 82 bpm (+20.6%), HRV at 34 ms (-34.6%), SpO2 drifts to 95%.",
        "telemetry": {"resting_hr": 82.0, "hrv": 34.0, "sleep_duration": 5.4, "steps": 2800, "spo2": 95.0, "respiratory_rate": 17.5, "stress_index": 72.0},
        "drift_score": 79.6,
        "drift_level": "High",
        "risk_24h": 0.68,
        "data_quality": 95.0,
        "key_event": "Twin Drift Score reaches High status (79.6)."
    },
    {
        "stage": 7,
        "title": "Risk Alert Dispatched",
        "description": "Automated clinical alert triggered: High physiological deterioration drift with 24h risk crossing 70%.",
        "telemetry": {"resting_hr": 82.0, "hrv": 34.0, "sleep_duration": 5.4, "steps": 2800, "spo2": 95.0, "respiratory_rate": 18.0, "stress_index": 74.0},
        "drift_score": 81.1,
        "drift_level": "High",
        "risk_24h": 0.71,
        "data_quality": 95.0,
        "key_event": "Explainable alert dispatched with exact feature weights."
    },
    {
        "stage": 8,
        "title": "Explainability & What-If Simulation",
        "description": "Clinician reviews SHAP-style weights and runs counterfactual simulation (sleep to 7.2h, med adherence to 95%).",
        "telemetry": {"resting_hr": 82.0, "hrv": 34.0, "sleep_duration": 5.4, "steps": 2800, "spo2": 95.0, "respiratory_rate": 18.0, "stress_index": 74.0},
        "drift_score": 81.1,
        "drift_level": "High",
        "risk_24h": 0.71,
        "data_quality": 95.0,
        "key_event": "What-If engine projects risk decreasing from 71% to 28%."
    },
    {
        "stage": 9,
        "title": "Failure Case Demo: Sensor Artifact",
        "description": "PPG sensor experiences motion artifact / loose wrist fit. Data Quality drops to 45%. System refuses to issue false alarm and widens uncertainty bounds.",
        "telemetry": {"resting_hr": 210.0, "hrv": 4.0, "sleep_duration": 7.1, "steps": 0, "spo2": 82.0, "respiratory_rate": 14.5, "stress_index": 80.0},
        "drift_score": 45.0,
        "drift_level": "Watch",
        "risk_24h": 0.25,
        "data_quality": 45.0,
        "key_event": "Data Quality Engine flags sensor artifact. AI warns clinician: 'Prediction confidence reduced because telemetry quality is insufficient.'"
    },
    {
        "stage": 10,
        "title": "Recovery & Stabilization",
        "description": "Patient adheres to clinician guidance: sleep restored, medications taken, physiology stabilizes back toward baseline.",
        "telemetry": {"resting_hr": 70.0, "hrv": 50.0, "sleep_duration": 7.2, "steps": 5800, "spo2": 97.0, "respiratory_rate": 14.8, "stress_index": 32.0},
        "drift_score": 18.5,
        "drift_level": "Normal",
        "risk_24h": 0.11,
        "data_quality": 97.0,
        "key_event": "Twin Drift returns to Normal equilibrium (18.5). Successful proactive prevention."
    }
]

@router.get("/stages")
def get_demo_stages():
    """Returns the list of 10 demonstration stages for presentation flow."""
    return {"stages": DEMO_STAGES, "total_stages": len(DEMO_STAGES)}

@router.post("/set-stage/{stage_num}")
def set_demo_stage(stage_num: int, db: Session = Depends(get_db)):
    """Sets Patient A-1042 to the exact specified stage in the presentation sequence."""
    if stage_num < 1 or stage_num > len(DEMO_STAGES):
        raise HTTPException(status_code=400, detail="Invalid stage number (1-10)")

    stage_data = DEMO_STAGES[stage_num - 1]
    p_id = "PAT-A-1042"
    patient = db.query(Patient).filter(Patient.id == p_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Demo patient not found")

    ehr = db.query(EHRRecord).filter(EHRRecord.patient_id == p_id).first()
    now_t = datetime.now(timezone.utc)

    # Base profile
    base = PersonalBaselineEngine.get_default_baseline()
    telem = stage_data["telemetry"]
    dq_val = stage_data.get("data_quality", 96.0)

    # Generate or update latest reading
    reading = {
        "patient_id": p_id,
        "timestamp": now_t,
        "heart_rate": telem["resting_hr"] + 4.0,
        "resting_heart_rate": telem["resting_hr"],
        "hrv": telem["hrv"],
        "spo2": telem["spo2"],
        "steps": telem["steps"],
        "activity_level": "moderate" if telem["steps"] > 5000 else "sedentary",
        "sleep_duration": telem["sleep_duration"],
        "sleep_quality": max(45.0, 90.0 - telem["stress_index"] * 0.6),
        "respiratory_rate": telem["respiratory_rate"],
        "body_temperature": 36.8,
        "stress_index": telem["stress_index"],
        "is_anomaly": stage_num in [6, 7, 9],
        "signal_quality": dq_val / 100.0
    }
    db.add(WearableReading(**reading))

    # Recalculate twin state
    devs = PersonalBaselineEngine.calculate_deviations(reading, base)
    d_score = stage_data["drift_score"]
    d_level = stage_data["drift_level"]
    _, _, top_c = DigitalTwinEngine.calculate_twin_drift_score(devs)

    r_24 = stage_data["risk_24h"]
    r_6 = round(r_24 * 0.65, 3)
    r_72 = round(min(0.95, r_24 * 1.3), 3)

    twin_state = TwinState(
        patient_id=p_id,
        timestamp=now_t,
        baseline=base,
        current_state=reading,
        deviations=devs,
        twin_drift_score=d_score,
        drift_level=d_level,
        risk_6h=r_6,
        risk_24h=r_24,
        risk_72h=r_72,
        confidence=round(0.94 * (dq_val / 100.0), 2),
        data_quality=dq_val,
        top_contributors=top_c,
        simulation_state=stage_data["title"]
    )
    db.add(twin_state)

    # Stage 7 generates alert
    if stage_num in [6, 7]:
        existing_alert = db.query(Alert).filter(Alert.patient_id == p_id, Alert.severity == "High").first()
        if not existing_alert:
            db.add(Alert(
                id="ALT-DEMO-001",
                patient_id=p_id,
                timestamp=now_t,
                severity="High",
                title="High Physiological Deterioration Drift Detected",
                reason="Twin Drift Score reached 81.1 (High). 24h deterioration risk is 71.2%. Primary contributors: Resting HR (+20.6%), HRV decline (-34.6%), Activity reduction (-54.8%).",
                affected_signals=["resting_hr", "hrv", "steps", "sleep_duration"],
                trend="Acute Progression",
                model_risk=0.712,
                data_quality=dq_val,
                acknowledged=False
            ))

    db.commit()

    return {
        "status": "success",
        "current_stage": stage_data,
        "patient_id": p_id,
        "message": f"Demo set to Stage {stage_num}: {stage_data['title']}"
    }

@router.post("/reset")
def reset_demo(db: Session = Depends(get_db)):
    """Resets Patient A-1042 back to Stage 1 (Stable Baseline)."""
    return set_demo_stage(1, db=db)
