"""
FastAPI Route Handlers for CardioTwin AI.
Exposes endpoints for patients, EHR, wearables, twin state, risk forecasting,
what-if simulations, alerts, model metrics, and FHIR interoperability.
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone, timedelta
import uuid
import json

from backend.app.db.session import get_db
from backend.app.models.db_models import (
    Patient, EHRRecord, WearableReading, TwinState, RiskPrediction, Alert, SimulationRun, ModelPrediction
)
from backend.app.schemas.twin_schemas import (
    PatientSummary, PatientDetail, EHRResponse, WearableReadingResponse,
    TwinStateResponse, WhatIfRequest, WhatIfResponse, WearableSimulationStepRequest,
    WearableSimulationStepResponse, AlertResponse, DataQualityResponse,
    EvaluationMetricsResponse
)
from backend.app.services.baseline_engine import PersonalBaselineEngine
from backend.app.services.twin_engine import DigitalTwinEngine
from backend.app.services.risk_engine import RiskForecastingEngine
from backend.app.services.whatif_engine import WhatIfSimulationEngine
from backend.app.services.data_quality_engine import DataQualityEngine
from backend.app.services.wearable_simulator import WearableSimulator
from backend.app.services.alert_engine import AlertEngine

router = APIRouter()

# --- Health Check ---
@router.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "CardioTwin AI Core API",
        "version": "1.0.0",
        "disclaimer": "Research proof-of-concept using synthetic data. Not a medical device."
    }

# --- Patients ---
@router.get("/patients", response_model=List[PatientSummary])
def get_patients(
    skip: int = 0,
    limit: int = 50,
    risk_filter: Optional[str] = None, # Watch, Elevated, High, Normal
    db: Session = Depends(get_db)
):
    query = db.query(Patient)
    patients = query.offset(skip).limit(limit).all()

    summaries = []
    for p in patients:
        latest_twin = db.query(TwinState).filter(TwinState.patient_id == p.id).order_by(TwinState.timestamp.desc()).first()
        active_alerts = db.query(Alert).filter(Alert.patient_id == p.id, Alert.acknowledged == False).count()
        
        drift_score = latest_twin.twin_drift_score if latest_twin else 0.0
        drift_level = latest_twin.drift_level if latest_twin else "Normal"
        risk_24 = latest_twin.risk_24h if latest_twin else 0.05
        dq = latest_twin.data_quality if latest_twin else 95.0
        sim_state = latest_twin.simulation_state if latest_twin else "Normal"

        if risk_filter and risk_filter.lower() != drift_level.lower():
            continue

        summaries.append(PatientSummary(
            id=p.id,
            name=p.name,
            age=p.age,
            sex=p.sex,
            bmi=p.bmi,
            primary_condition=p.primary_condition,
            current_drift_score=drift_score,
            drift_level=drift_level,
            risk_24h=risk_24,
            data_quality=dq,
            active_alerts_count=active_alerts,
            simulation_state=sim_state
        ))
    return summaries


@router.get("/patients/{patient_id}", response_model=PatientDetail)
def get_patient(patient_id: str, db: Session = Depends(get_db)):
    p = db.query(Patient).filter(Patient.id == patient_id).first()
    if not p:
        raise HTTPException(status_code=404, detail=f"Patient {patient_id} not found")
    
    ehr = db.query(EHRRecord).filter(EHRRecord.patient_id == patient_id).first()
    latest_twin = db.query(TwinState).filter(TwinState.patient_id == patient_id).order_by(TwinState.timestamp.desc()).first()

    return PatientDetail(
        id=p.id,
        name=p.name,
        age=p.age,
        sex=p.sex,
        height_cm=p.height_cm,
        weight_kg=p.weight_kg,
        bmi=p.bmi,
        primary_condition=p.primary_condition,
        created_at=p.created_at,
        ehr=ehr,
        latest_twin_state=latest_twin
    )


# --- EHR ---
@router.get("/patients/{patient_id}/ehr", response_model=EHRResponse)
def get_patient_ehr(patient_id: str, db: Session = Depends(get_db)):
    ehr = db.query(EHRRecord).filter(EHRRecord.patient_id == patient_id).first()
    if not ehr:
        raise HTTPException(status_code=404, detail=f"EHR record for {patient_id} not found")
    return ehr


# --- Wearables ---
@router.get("/patients/{patient_id}/wearables", response_model=List[WearableReadingResponse])
def get_patient_wearables(
    patient_id: str,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    readings = db.query(WearableReading).filter(
        WearableReading.patient_id == patient_id
    ).order_by(WearableReading.timestamp.asc()).limit(limit).all()
    return readings


# --- Digital Twin State ---
@router.get("/patients/{patient_id}/twin", response_model=TwinStateResponse)
def get_patient_twin_state(patient_id: str, db: Session = Depends(get_db)):
    twin = db.query(TwinState).filter(
        TwinState.patient_id == patient_id
    ).order_by(TwinState.timestamp.desc()).first()
    
    if not twin:
        raise HTTPException(status_code=404, detail=f"Digital Twin state for {patient_id} not found")
    return twin


# --- Risk Forecast ---
@router.get("/patients/{patient_id}/risk")
def get_patient_risk(patient_id: str, db: Session = Depends(get_db)):
    twin = db.query(TwinState).filter(
        TwinState.patient_id == patient_id
    ).order_by(TwinState.timestamp.desc()).first()
    
    if not twin:
        raise HTTPException(status_code=404, detail=f"Risk state for {patient_id} not found")
    
    return {
        "patient_id": patient_id,
        "timestamp": twin.timestamp,
        "risk_6h": twin.risk_6h,
        "risk_24h": twin.risk_24h,
        "risk_72h": twin.risk_72h,
        "confidence": twin.confidence,
        "twin_drift_score": twin.twin_drift_score,
        "drift_level": twin.drift_level,
        "top_contributors": twin.top_contributors,
        "disclaimer": "Calculated by multimodal fusion model on synthetic telemetry. For clinical decision support only."
    }


# --- Patient Deterioration Timeline ---
@router.get("/patients/{patient_id}/timeline")
def get_patient_timeline(patient_id: str, db: Session = Depends(get_db)):
    readings = db.query(WearableReading).filter(
        WearableReading.patient_id == patient_id
    ).order_by(WearableReading.timestamp.asc()).all()

    if not readings:
        raise HTTPException(status_code=404, detail="No timeline readings available")

    twin = db.query(TwinState).filter(TwinState.patient_id == patient_id).order_by(TwinState.timestamp.desc()).first()
    base = twin.baseline if twin else PersonalBaselineEngine.get_default_baseline()

    timeline_points = []
    for r in readings[-24:]:
        devs = PersonalBaselineEngine.calculate_deviations({
            "resting_hr": r.resting_heart_rate,
            "hrv": r.hrv,
            "sleep_duration": r.sleep_duration,
            "steps": r.steps,
            "spo2": r.spo2,
            "respiratory_rate": r.respiratory_rate,
            "stress_index": r.stress_index
        }, base)
        drift, level, _ = DigitalTwinEngine.calculate_twin_drift_score(devs)
        
        timeline_points.append({
            "timestamp": r.timestamp.isoformat(),
            "time_str": r.timestamp.strftime("%H:%M"),
            "resting_hr": r.resting_heart_rate,
            "hrv": r.hrv,
            "spo2": r.spo2,
            "steps": r.steps,
            "sleep_duration": r.sleep_duration,
            "twin_drift_score": drift,
            "drift_level": level,
            "is_anomaly": r.is_anomaly
        })

    return {
        "patient_id": patient_id,
        "timeline": timeline_points,
        "baseline_summary": {
            "resting_hr": base.get("resting_hr", {}).get("mean"),
            "hrv": base.get("hrv", {}).get("mean"),
            "spo2": base.get("spo2", {}).get("mean")
        }
    }


# --- Alerts ---
@router.get("/patients/{patient_id}/alerts", response_model=List[AlertResponse])
def get_patient_alerts(patient_id: str, db: Session = Depends(get_db)):
    alerts = db.query(Alert).filter(
        Alert.patient_id == patient_id
    ).order_by(Alert.timestamp.desc()).all()
    return alerts


@router.post("/alerts/{alert_id}/acknowledge")
def acknowledge_alert(alert_id: str, acknowledged_by: str = "Dr. Clinician", db: Session = Depends(get_db)):
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    alert.acknowledged = True
    alert.acknowledged_by = acknowledged_by
    alert.acknowledged_at = datetime.now(timezone.utc)
    db.commit()
    return {"status": "success", "alert_id": alert_id, "acknowledged_by": acknowledged_by}


# --- Data Quality ---
@router.get("/data-quality/{patient_id}", response_model=DataQualityResponse)
def get_patient_data_quality(patient_id: str, db: Session = Depends(get_db)):
    latest_reading = db.query(WearableReading).filter(
        WearableReading.patient_id == patient_id
    ).order_by(WearableReading.timestamp.desc()).first()

    reading_dict = {
        "heart_rate": latest_reading.heart_rate if latest_reading else None,
        "resting_heart_rate": latest_reading.resting_heart_rate if latest_reading else None,
        "hrv": latest_reading.hrv if latest_reading else None,
        "spo2": latest_reading.spo2 if latest_reading else None,
        "steps": latest_reading.steps if latest_reading else None,
        "sleep_duration": latest_reading.sleep_duration if latest_reading else None,
        "respiratory_rate": latest_reading.respiratory_rate if latest_reading else None
    } if latest_reading else {}

    assessment = DataQualityEngine.assess_patient_data_quality(reading_dict)
    return DataQualityResponse(patient_id=patient_id, **assessment)


# --- What-If Digital Twin Scenario Simulator ---
@router.post("/simulation", response_model=WhatIfResponse)
@router.post("/simulation/run", response_model=WhatIfResponse)
def run_what_if_simulation(req: WhatIfRequest, db: Session = Depends(get_db)):
    p = db.query(Patient).filter(Patient.id == req.patient_id).first()
    if not p:
        raise HTTPException(status_code=404, detail=f"Patient {req.patient_id} not found")

    twin = db.query(TwinState).filter(TwinState.patient_id == req.patient_id).order_by(TwinState.timestamp.desc()).first()
    ehr = db.query(EHRRecord).filter(EHRRecord.patient_id == req.patient_id).first()
    
    if not twin or not ehr:
        raise HTTPException(status_code=400, detail="Twin baseline or EHR missing for patient")

    current_state = twin.current_state
    baseline = twin.baseline
    current_risks = {
        "risk_6h": twin.risk_6h,
        "risk_24h": twin.risk_24h,
        "risk_72h": twin.risk_72h
    }

    scenario_params = {
        "scenario_name": req.scenario_name,
        "simulated_sleep_hours": req.simulated_sleep_hours,
        "simulated_activity_level": req.simulated_activity_level,
        "simulated_medication_adherence": req.simulated_medication_adherence,
        "simulated_stress_reduction": req.simulated_stress_reduction,
        "simulated_dietary_adherence": req.simulated_dietary_adherence
    }

    result = WhatIfSimulationEngine.run_simulation(
        patient_id=req.patient_id,
        current_state=current_state,
        baseline=baseline,
        ehr={
            "age": p.age,
            "hypertension": ehr.hypertension,
            "diabetes": ehr.diabetes,
            "medication_adherence": ehr.medication_adherence
        },
        current_risks=current_risks,
        scenario_params=scenario_params
    )

    # Persist simulation run
    sim_run = SimulationRun(
        id=result["id"],
        patient_id=req.patient_id,
        scenario_name=result["scenario_name"],
        parameters_modified=result["parameters_modified"],
        baseline_trajectory=result["trajectories"],
        simulated_trajectory=result["trajectories"],
        counterfactual_insights="\n".join(result["counterfactual_insights"]),
        disclaimer=result["disclaimer"]
    )
    db.add(sim_run)
    db.commit()

    return result


# --- Live Wearable Step Simulation ---
@router.post("/wearable/simulate", response_model=WearableSimulationStepResponse)
def simulate_wearable_step(req: WearableSimulationStepRequest, db: Session = Depends(get_db)):
    p = db.query(Patient).filter(Patient.id == req.patient_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Patient not found")

    twin = db.query(TwinState).filter(TwinState.patient_id == req.patient_id).order_by(TwinState.timestamp.desc()).first()
    ehr = db.query(EHRRecord).filter(EHRRecord.patient_id == req.patient_id).first()
    
    baseline = twin.baseline if twin else PersonalBaselineEngine.get_default_baseline()
    now_t = datetime.now(timezone.utc)

    # Count recent steps to simulate realistic progression
    recent_readings_count = db.query(WearableReading).filter(WearableReading.patient_id == req.patient_id).count()

    new_reading_dict = WearableSimulator.generate_reading_for_state(
        patient_id=req.patient_id,
        baseline=baseline,
        simulation_state=req.simulation_state,
        step_index=recent_readings_count % 10,
        timestamp=now_t
    )

    new_reading = WearableReading(**new_reading_dict)
    db.add(new_reading)
    db.flush()

    # Recalculate twin state
    deviations = PersonalBaselineEngine.calculate_deviations(new_reading_dict, baseline)
    drift_score, drift_level, top_contributors = DigitalTwinEngine.calculate_twin_drift_score(deviations)

    ehr_dict = {
        "age": p.age,
        "hypertension": ehr.hypertension if ehr else True,
        "diabetes": ehr.diabetes if ehr else True,
        "dyslipidemia": ehr.dyslipidemia if ehr else True,
        "previous_cardiac_history": ehr.previous_cardiac_history if ehr else True,
        "medication_adherence": ehr.medication_adherence if ehr else 0.70
    }
    risks = RiskForecastingEngine.forecast_risks(ehr_dict, drift_score, deviations, data_quality=new_reading_dict["signal_quality"]*100)

    updated_twin = TwinState(
        patient_id=req.patient_id,
        timestamp=now_t,
        baseline=baseline,
        current_state=new_reading_dict,
        deviations=deviations,
        twin_drift_score=drift_score,
        drift_level=drift_level,
        risk_6h=risks["risk_6h"],
        risk_24h=risks["risk_24h"],
        risk_72h=risks["risk_72h"],
        confidence=risks["confidence"],
        data_quality=round(new_reading_dict["signal_quality"]*100, 1),
        top_contributors=top_contributors,
        simulation_state=req.simulation_state
    )
    db.add(updated_twin)

    # Check alert generation
    alerts = AlertEngine.evaluate_and_generate_alerts(
        req.patient_id, drift_score, drift_level, risks["risk_24h"], deviations, data_quality=updated_twin.data_quality
    )
    for a in alerts:
        db.add(Alert(**a))

    db.commit()

    return WearableSimulationStepResponse(
        patient_id=req.patient_id,
        new_reading=new_reading,
        updated_twin_state=updated_twin,
        alerts_generated=alerts
    )


# --- Model Evaluation & Ablation ---
@router.get("/model/metrics", response_model=EvaluationMetricsResponse)
def get_model_evaluation_metrics(db: Session = Depends(get_db)):
    from backend.app.core.config import settings
    eval_file = settings.DATA_DIR / "evaluation_results.json"
    
    if eval_file.exists():
        with open(eval_file, "r") as f:
            data = json.load(f)
            return EvaluationMetricsResponse(
                models=data.get("models", []),
                stress_test=data.get("stress_test", []),
                calibration_curve=data.get("calibration_curve", []),
                confusion_matrix=data.get("confusion_matrix", {}),
                disclaimer="Synthetic-data evaluation. Conducted via patient-stratified non-overlapping temporal test split."
            )

    preds = db.query(ModelPrediction).all()
    if not preds:
        # Trigger actual evaluation pipeline if not yet run
        import subprocess
        import sys
        subprocess.run([sys.executable, str(settings.BASE_DIR / "scripts" / "evaluate.py")], check=True)
        if eval_file.exists():
            with open(eval_file, "r") as f:
                data = json.load(f)
                return EvaluationMetricsResponse(
                    models=data.get("models", []),
                    stress_test=data.get("stress_test", []),
                    calibration_curve=data.get("calibration_curve", []),
                    confusion_matrix=data.get("confusion_matrix", {}),
                    disclaimer="Synthetic-data evaluation. Conducted via patient-stratified non-overlapping temporal test split."
                )

    models_list = []
    meta = preds[0].metadata_json or {} if preds else {}
    for p in preds:
        models_list.append({
            "model_name": p.model_name,
            "model_type": "Fusion Twin" if "Digital Twin" in p.model_name else ("Wearable-only" if "Wearable" in p.model_name else "EHR-only"),
            "auroc": p.auroc,
            "auprc": p.auprc,
            "precision": p.precision,
            "recall": p.recall,
            "f1": p.f1,
            "brier_score": p.brier_score,
            "false_alert_rate_per_patient_week": p.false_alert_rate_per_patient_week,
            "median_lead_time_hours": p.median_lead_time_hours
        })

    return EvaluationMetricsResponse(
        models=models_list,
        stress_test=meta.get("stress_test", []),
        calibration_curve=meta.get("calibration", []),
        confusion_matrix=meta.get("confusion_matrix", {}),
        disclaimer="Synthetic-data evaluation. Conducted via patient-stratified non-overlapping temporal test split."
    )


# --- India-Specific Interoperability (ABDM / FHIR R4 Conceptual Layer) ---
@router.get("/fhir/Patient/{patient_id}")
def get_fhir_patient(patient_id: str, db: Session = Depends(get_db)):
    """Returns HL7 FHIR R4 Patient representation."""
    p = db.query(Patient).filter(Patient.id == patient_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    return {
        "resourceType": "Patient",
        "id": p.id,
        "meta": {
            "versionId": "1",
            "lastUpdated": p.updated_at.isoformat(),
            "profile": ["https://nrces.in/ndhm/fhir/r4/StructureDefinition/Patient"]
        },
        "identifier": [
            {
                "type": {"coding": [{"system": "https://healthid.ndhm.gov.in", "code": "ABHA", "display": "Ayushman Bharat Health Account (Simulated)"}]},
                "system": "https://healthid.ndhm.gov.in",
                "value": f"91-{p.id.replace('PAT-', '')}-0024"
            }
        ],
        "active": True,
        "name": [{"use": "official", "text": p.name}],
        "gender": p.sex.lower(),
        "birthDate": str(datetime.now().year - p.age) + "-01-15",
        "_disclaimer": "ABDM / FHIR architectural compatibility demonstration. Not an official government certification."
    }


@router.get("/fhir/Observation")
def get_fhir_observations(patient: str, db: Session = Depends(get_db)):
    """Returns FHIR R4 Observations representing personal baseline deviations and twin drift."""
    twin = db.query(TwinState).filter(TwinState.patient_id == patient).order_by(TwinState.timestamp.desc()).first()
    if not twin:
        raise HTTPException(status_code=404, detail="Twin observations not found")
    
    entries = []
    # Twin Drift Score Observation
    entries.append({
        "resourceType": "Observation",
        "id": f"obs-drift-{patient}",
        "status": "final",
        "code": {
            "coding": [{"system": "http://cardiotwin.ai/fhir/codes", "code": "TWIN-DRIFT", "display": "CardioTwin Physiological Drift Score"}],
            "text": "Twin Drift Score"
        },
        "subject": {"reference": f"Patient/{patient}"},
        "effectiveDateTime": twin.timestamp.isoformat(),
        "valueQuantity": {"value": twin.twin_drift_score, "unit": "score", "system": "http://unitsofmeasure.org"},
        "interpretation": [{"coding": [{"system": "http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation", "code": twin.drift_level}]}]
    })

    # Resting HR observation
    cur_hr = twin.current_state.get("resting_heart_rate", 70.0)
    entries.append({
        "resourceType": "Observation",
        "id": f"obs-rhr-{patient}",
        "status": "final",
        "code": {
            "coding": [{"system": "http://loinc.org", "code": "8867-4", "display": "Heart rate"}],
            "text": "Resting Heart Rate"
        },
        "subject": {"reference": f"Patient/{patient}"},
        "effectiveDateTime": twin.timestamp.isoformat(),
        "valueQuantity": {"value": cur_hr, "unit": "beats/min", "system": "http://unitsofmeasure.org", "code": "/min"}
    })

    return {
        "resourceType": "Bundle",
        "type": "searchset",
        "total": len(entries),
        "entry": [{"resource": obs} for obs in entries],
        "_architecture_note": "ABDM/FHIR alignment architecture layer."
    }
