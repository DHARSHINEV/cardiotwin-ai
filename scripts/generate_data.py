"""
Synthetic Data Generation Engine for CardioTwin AI.
Generates clinically correlated EHR records, personal baselines, and multi-day wearable time series.
Includes Patient PAT-A-1042 with a deterministic 24-hour deterioration sequence.
Ensures zero real-patient PII, 100% synthetic data compliance.
"""
import os
import sys
import json
import random
import argparse
from datetime import datetime, timezone, timedelta
from pathlib import Path
import numpy as np

# Adjust python path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

from backend.app.db.session import engine, SessionLocal, Base
from backend.app.models.db_models import (
    Patient, EHRRecord, WearableReading, TwinState, RiskPrediction, Alert, SimulationRun
)
from backend.app.services.baseline_engine import PersonalBaselineEngine
from backend.app.services.twin_engine import DigitalTwinEngine
from backend.app.services.risk_engine import RiskForecastingEngine
from backend.app.services.data_quality_engine import DataQualityEngine
from backend.app.services.alert_engine import AlertEngine

# First and last names for synthetic generation
FIRST_NAMES = ["Ramesh", "Priya", "Sunil", "Ananya", "Vijay", "Deepa", "Arun", "Kavita", "Sanjay", "Meera", "Rajesh", "Pooja", "Vikram", "Sneha", "Amit"]
LAST_NAMES = ["Sharma", "Patel", "Verma", "Iyer", "Rao", "Nair", "Reddy", "Gupta", "Deshmukh", "Menon", "Joshi", "Chopra", "Kulkarni", "Singh", "Bose"]

MEDICATION_OPTIONS = [
    "Amlodipine 5mg OD",
    "Atorvastatin 20mg OD",
    "Metformin 500mg BID",
    "Telmisartan 40mg OD",
    "Bisoprolol 2.5mg OD",
    "Aspirin 75mg OD",
    "Empagliflozin 10mg OD",
    "Rosuvastatin 10mg OD"
]

def generate_correlated_patient(idx: int) -> dict:
    """Generates an individual patient with physiologically correlated covariates."""
    patient_id = f"PAT-SYN-{1000 + idx}"
    name = f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"
    age = int(random.gauss(58, 9))
    age = max(35, min(84, age))
    sex = random.choice(["Male", "Female"])
    
    height_cm = round(random.gauss(170 if sex == "Male" else 158, 7), 1)
    weight_kg = round(random.gauss(76 if sex == "Male" else 65, 11), 1)
    bmi = round(weight_kg / ((height_cm / 100.0) ** 2), 1)

    # Correlated clinical history
    prob_htn = 0.50 + (0.015 * (age - 50)) + (0.02 * max(0, bmi - 25))
    has_htn = random.random() < min(0.85, prob_htn)

    prob_dm = 0.30 + (0.03 * max(0, bmi - 26)) + (0.10 if has_htn else 0.0)
    has_dm = random.random() < min(0.75, prob_dm)

    prob_dys = 0.40 + (0.15 if has_dm else 0.0) + (0.10 if has_htn else 0.0)
    has_dys = random.random() < min(0.80, prob_dys)

    has_family_hist = random.random() < 0.42
    has_prev_cardiac = random.random() < (0.28 if (has_htn and has_dm) else 0.12)

    # Biomarkers correlated with diagnoses
    if has_htn:
        systolic_bp = round(random.gauss(144, 12), 1)
        diastolic_bp = round(random.gauss(90, 8), 1)
    else:
        systolic_bp = round(random.gauss(118, 8), 1)
        diastolic_bp = round(random.gauss(76, 6), 1)

    if has_dm:
        hba1c = round(random.gauss(7.8, 1.1), 1)
    else:
        hba1c = round(random.gauss(5.4, 0.3), 1)

    if has_dys:
        ldl = round(random.gauss(146, 22), 1)
        chol_total = round(ldl + random.gauss(75, 15), 1)
        hdl = round(random.gauss(38, 6), 1)
    else:
        ldl = round(random.gauss(92, 14), 1)
        chol_total = round(ldl + random.gauss(80, 12), 1)
        hdl = round(random.gauss(49, 7), 1)

    creatinine = round(random.gauss(1.05 + (0.15 if has_dm else 0.0), 0.2), 2)
    smoking = random.choice(["Never", "Former", "Current"] if sex == "Male" else ["Never", "Never", "Former"])
    med_adh = round(random.betavariate(6, 2), 2) # Mostly 0.70 - 0.95

    # Assigned medications
    meds = []
    if has_htn:
        meds.append("Amlodipine 5mg OD")
        if systolic_bp > 145:
            meds.append("Telmisartan 40mg OD")
    if has_dm:
        meds.append("Metformin 500mg BID")
    if has_dys:
        meds.append("Atorvastatin 20mg OD")

    # Personal baseline parameters
    base_rhr = round(random.gauss(68 + (4 if smoking == "Current" else 0) + (3 if bmi > 30 else 0), 5), 1)
    base_hrv = round(random.gauss(52 - (0.4 * (age - 50)) - (4 if has_dm else 0), 6), 1)
    base_hrv = max(25.0, base_hrv)
    base_sleep = round(random.gauss(7.0, 0.6), 1)
    base_steps = int(random.gauss(6500 - (50 * max(0, bmi - 24)), 1000))
    base_steps = max(2500, base_steps)
    base_spo2 = round(min(99.0, max(95.0, random.gauss(97.2, 0.7))), 1)

    return {
        "patient": {
            "id": patient_id,
            "name": name,
            "age": age,
            "sex": sex,
            "height_cm": height_cm,
            "weight_kg": weight_kg,
            "bmi": bmi,
            "primary_condition": "Cardiovascular Risk Profile"
        },
        "ehr": {
            "patient_id": patient_id,
            "smoking_status": smoking,
            "diabetes": has_dm,
            "hypertension": has_htn,
            "dyslipidemia": has_dys,
            "family_history": has_family_hist,
            "previous_cardiac_history": has_prev_cardiac,
            "medications": meds,
            "medication_adherence": med_adh,
            "systolic_bp": systolic_bp,
            "diastolic_bp": diastolic_bp,
            "resting_hr": base_rhr,
            "cholesterol_total": chol_total,
            "ldl": ldl,
            "hdl": hdl,
            "hba1c": hba1c,
            "creatinine": creatinine,
            "risk_factors": [k for k, v in [("Hypertension", has_htn), ("Diabetes", has_dm), ("Dyslipidemia", has_dys), ("Previous Cardiac", has_prev_cardiac)] if v]
        },
        "baseline": {
            "resting_hr": {"mean": base_rhr, "std": 4.5, "median": base_rhr, "lower_bound": round(base_rhr - 9.0, 1), "upper_bound": round(base_rhr + 9.0, 1), "unit": "bpm", "name": "Resting Heart Rate"},
            "hrv": {"mean": base_hrv, "std": 5.5, "median": base_hrv, "lower_bound": round(base_hrv - 11.0, 1), "upper_bound": round(base_hrv + 11.0, 1), "unit": "ms", "name": "HRV (RMSSD)"},
            "sleep_duration": {"mean": base_sleep, "std": 0.6, "median": base_sleep, "lower_bound": round(base_sleep - 1.2, 1), "upper_bound": round(base_sleep + 1.2, 1), "unit": "hours", "name": "Sleep Duration"},
            "steps": {"mean": float(base_steps), "std": 800.0, "median": float(base_steps), "lower_bound": float(base_steps - 1600), "upper_bound": float(base_steps + 1600), "unit": "steps/day", "name": "Daily Steps"},
            "spo2": {"mean": base_spo2, "std": 0.8, "median": base_spo2, "lower_bound": round(base_spo2 - 1.6, 1), "upper_bound": 99.0, "unit": "%", "name": "SpO2"},
            "respiratory_rate": {"mean": 14.5, "std": 1.1, "median": 14.5, "lower_bound": 12.3, "upper_bound": 16.7, "unit": "breaths/min", "name": "Respiratory Rate"},
            "stress_index": {"mean": 28.0, "std": 5.0, "median": 28.0, "lower_bound": 18.0, "upper_bound": 38.0, "unit": "index", "name": "Stress Index"}
        }
    }


def create_demo_patient_a1042() -> dict:
    """
    Creates Patient A-1042 strictly according to prompt specifications:
    Age: 57, HTN: Yes, Diabetes: Yes, Dyslipidemia: Yes
    Personal baseline:
    Resting HR: 68 bpm, HRV: 52 ms, Sleep: 7.1 hours, Daily steps: 6200, SpO2: 97%
    """
    p_id = "PAT-A-1042"
    patient_data = {
        "id": p_id,
        "name": "Patient A-1042",
        "age": 57,
        "sex": "Male",
        "height_cm": 174.0,
        "weight_kg": 85.8,
        "bmi": 28.3,
        "primary_condition": "Hypertension, T2D & Dyslipidemia"
    }

    ehr_data = {
        "patient_id": p_id,
        "smoking_status": "Former",
        "diabetes": True,
        "hypertension": True,
        "dyslipidemia": True,
        "family_history": True,
        "previous_cardiac_history": True,
        "medications": ["Amlodipine 5mg OD", "Metformin 500mg BID", "Atorvastatin 20mg OD"],
        "medication_adherence": 0.70, # Declining adherence
        "systolic_bp": 142.0,
        "diastolic_bp": 90.0,
        "resting_hr": 68.0,
        "cholesterol_total": 218.0,
        "ldl": 138.0,
        "hdl": 41.0,
        "hba1c": 7.4,
        "creatinine": 1.1,
        "previous_events": ["Mild Angina 2024", "Exertional dyspnea"],
        "risk_factors": ["Hypertension Stage 2", "Type 2 Diabetes Mellitus", "Dyslipidemia", "Sedentary lifestyle"]
    }

    baseline_data = {
        "resting_hr": {"mean": 68.0, "std": 4.8, "median": 68.0, "lower_bound": 58.4, "upper_bound": 77.6, "unit": "bpm", "name": "Resting Heart Rate"},
        "hrv": {"mean": 52.0, "std": 5.8, "median": 52.0, "lower_bound": 40.4, "upper_bound": 63.6, "unit": "ms", "name": "HRV (RMSSD)"},
        "sleep_duration": {"mean": 7.1, "std": 0.6, "median": 7.1, "lower_bound": 5.9, "upper_bound": 8.3, "unit": "hours", "name": "Sleep Duration"},
        "steps": {"mean": 6200.0, "std": 750.0, "median": 6200.0, "lower_bound": 4700.0, "upper_bound": 7700.0, "unit": "steps/day", "name": "Daily Steps"},
        "spo2": {"mean": 97.0, "std": 0.7, "median": 97.0, "lower_bound": 95.6, "upper_bound": 98.4, "unit": "%", "name": "SpO2"},
        "respiratory_rate": {"mean": 14.5, "std": 1.2, "median": 14.5, "lower_bound": 12.1, "upper_bound": 16.9, "unit": "breaths/min", "name": "Respiratory Rate"},
        "stress_index": {"mean": 28.0, "std": 5.0, "median": 28.0, "lower_bound": 18.0, "upper_bound": 38.0, "unit": "index", "name": "Stress Index"}
    }

    # Generate 24-hour chronological deterioration sequence
    # 08:00 Normal baseline
    # 10:00 HR begins increasing
    # 12:00 HRV decreases
    # 14:00 Sleep deficit detected
    # 16:00 Twin Drift increases
    # 18:00 Risk threshold crossed
    now = datetime.now(timezone.utc)
    base_time = now - timedelta(hours=24)
    wearable_readings = []

    # Historical 7 days stable baseline readings
    for d in range(7, 1, -1):
        for h in [8, 14, 20]:
            t = base_time - timedelta(days=d, hours=-h)
            wearable_readings.append({
                "patient_id": p_id,
                "timestamp": t,
                "heart_rate": 70.0 + random.uniform(-2, 3),
                "resting_heart_rate": 68.0 + random.uniform(-2, 2),
                "hrv": 52.0 + random.uniform(-3, 3),
                "spo2": 97.0,
                "steps": 6200 + int(random.uniform(-400, 400)),
                "activity_level": "moderate",
                "sleep_duration": 7.1 + random.uniform(-0.2, 0.3),
                "sleep_quality": 88.0,
                "respiratory_rate": 14.5,
                "body_temperature": 36.7,
                "stress_index": 28.0,
                "is_anomaly": False,
                "signal_quality": 1.0
            })

    # The 24-hour deterioration progression
    timeline_steps = [
        {"hours_ago": 16, "rhr": 68.0, "hr": 70.0, "hrv": 52.0, "sleep": 7.0, "steps": 5800, "spo2": 97.0, "rr": 14.5, "stress": 29.0, "state": "Normal baseline"},
        {"hours_ago": 14, "rhr": 72.0, "hr": 75.0, "hrv": 48.0, "sleep": 6.8, "steps": 4800, "spo2": 97.0, "rr": 15.0, "stress": 36.0, "state": "HR begins increasing"},
        {"hours_ago": 12, "rhr": 75.0, "hr": 78.0, "hrv": 43.0, "sleep": 6.2, "steps": 4100, "spo2": 96.8, "rr": 15.5, "stress": 44.0, "state": "HRV decreases"},
        {"hours_ago": 10, "rhr": 77.0, "hr": 81.0, "hrv": 39.0, "sleep": 5.4, "steps": 3500, "spo2": 96.5, "rr": 16.0, "stress": 55.0, "state": "Sleep deficit detected"},
        {"hours_ago": 6,  "rhr": 80.0, "hr": 84.0, "hrv": 36.0, "sleep": 5.4, "steps": 3100, "spo2": 96.0, "rr": 16.5, "stress": 64.0, "state": "Twin Drift increases"},
        {"hours_ago": 2,  "rhr": 82.0, "hr": 87.0, "hrv": 34.0, "sleep": 5.4, "steps": 2800, "spo2": 95.0, "rr": 17.5, "stress": 72.0, "state": "Risk threshold crossed"}
    ]

    for item in timeline_steps:
        t = now - timedelta(hours=item["hours_ago"])
        wearable_readings.append({
            "patient_id": p_id,
            "timestamp": t,
            "heart_rate": item["hr"],
            "resting_heart_rate": item["rhr"],
            "hrv": item["hrv"],
            "spo2": item["spo2"],
            "steps": item["steps"],
            "activity_level": "sedentary" if item["steps"] < 3500 else "light",
            "sleep_duration": item["sleep"],
            "sleep_quality": max(45.0, 85.0 - (item["stress"] * 0.5)),
            "respiratory_rate": item["rr"],
            "body_temperature": 36.9,
            "stress_index": item["stress"],
            "is_anomaly": False,
            "signal_quality": 0.96
        })

    # Latest reading state (matches Section 5 of prompt exactly!)
    # Resting HR: 82 bpm (+20.6%)
    # HRV: 34 ms (-34.6%)
    # Sleep: 5.4 hours (-23.9%)
    # Daily steps: 2800 (-54.8%)
    # SpO2: 95%
    latest_reading = {
        "patient_id": p_id,
        "timestamp": now,
        "heart_rate": 88.0,
        "resting_heart_rate": 82.0,
        "hrv": 34.0,
        "spo2": 95.0,
        "steps": 2800,
        "activity_level": "sedentary",
        "sleep_duration": 5.4,
        "sleep_quality": 52.0,
        "respiratory_rate": 18.0,
        "body_temperature": 37.1,
        "stress_index": 74.0,
        "is_anomaly": False,
        "signal_quality": 0.95
    }
    wearable_readings.append(latest_reading)

    return {
        "patient": patient_data,
        "ehr": ehr_data,
        "baseline": baseline_data,
        "wearables": wearable_readings,
        "latest_reading": latest_reading
    }


def main():
    parser = argparse.ArgumentParser(description="CardioTwin AI Synthetic Data Generator")
    parser.add_argument("--patients", type=int, default=1000, help="Number of synthetic patients to generate")
    parser.add_argument("--quick", action="store_true", help="Quick mode for rapid seeding (50 patients)")
    args = parser.parse_args()

    count = 50 if args.quick else args.patients
    print(f"[CardioTwin AI] Generating {count} synthetic patient cohorts with correlated EHR and wearable time series...")

    # Ensure tables exist
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    # Clear old records
    db.query(Alert).delete()
    db.query(SimulationRun).delete()
    db.query(RiskPrediction).delete()
    db.query(TwinState).delete()
    db.query(WearableReading).delete()
    db.query(EHRRecord).delete()
    db.query(Patient).delete()
    db.commit()

    # 1. Create Patient A-1042 (The Showcase Demo Patient)
    demo_dict = create_demo_patient_a1042()
    p_demo = Patient(**demo_dict["patient"])
    db.add(p_demo)
    db.flush()

    ehr_demo = EHRRecord(**demo_dict["ehr"])
    db.add(ehr_demo)

    for w_dict in demo_dict["wearables"]:
        db.add(WearableReading(**w_dict))

    # Calculate Twin State for Demo Patient
    deviations = PersonalBaselineEngine.calculate_deviations(demo_dict["latest_reading"], demo_dict["baseline"])
    drift_score, drift_level, top_contributors = DigitalTwinEngine.calculate_twin_drift_score(deviations)
    risks = RiskForecastingEngine.forecast_risks(demo_dict["ehr"], drift_score, deviations, data_quality=95.0)

    twin_state_demo = TwinState(
        patient_id=p_demo.id,
        timestamp=demo_dict["latest_reading"]["timestamp"],
        baseline=demo_dict["baseline"],
        current_state=demo_dict["latest_reading"],
        deviations=deviations,
        twin_drift_score=drift_score,
        drift_level=drift_level,
        risk_6h=risks["risk_6h"],
        risk_24h=risks["risk_24h"],
        risk_72h=risks["risk_72h"],
        confidence=risks["confidence"],
        data_quality=95.0,
        top_contributors=top_contributors,
        simulation_state="Gradual deterioration"
    )
    db.add(twin_state_demo)

    # Initial Alerts for Demo Patient
    demo_alerts = AlertEngine.evaluate_and_generate_alerts(
        p_demo.id, drift_score, drift_level, risks["risk_24h"], deviations, data_quality=95.0
    )
    for a in demo_alerts:
        db.add(Alert(**a))

    print(f" -> Demo Patient {p_demo.id} initialized: Drift Score={drift_score} ({drift_level}), 24h Risk={risks['risk_24h']*100:.1f}%")

    # 2. Generate remaining cohort
    all_patients_json = [demo_dict["patient"]]
    all_ehr_json = [demo_dict["ehr"]]

    for i in range(1, count):
        data = generate_correlated_patient(i)
        p = Patient(**data["patient"])
        db.add(p)
        db.flush()

        ehr = EHRRecord(**data["ehr"])
        db.add(ehr)

        all_patients_json.append(data["patient"])
        all_ehr_json.append(data["ehr"])

        # Generate latest wearable reading with some variance in drift state
        # 70% normal, 18% watch, 8% elevated, 4% high
        rand_val = random.random()
        if rand_val < 0.70:
            sim_state = "Normal"
            hr_drift = random.uniform(-2, 3)
            hrv_drift = random.uniform(-3, 3)
            sleep_drift = random.uniform(-0.3, 0.3)
            step_drift = random.uniform(-400, 500)
            spo2_drift = 0.0
            rr_drift = 0.0
            stress_drift = 0.0
        elif rand_val < 0.88:
            sim_state = "Watch"
            hr_drift = random.uniform(5, 9)
            hrv_drift = random.uniform(-10, -5)
            sleep_drift = random.uniform(-0.8, -0.4)
            step_drift = random.uniform(-1200, -800)
            spo2_drift = -0.5
            rr_drift = 1.0
            stress_drift = 15.0
        elif rand_val < 0.96:
            sim_state = "Elevated"
            hr_drift = random.uniform(11, 16)
            hrv_drift = random.uniform(-18, -12)
            sleep_drift = random.uniform(-1.5, -1.0)
            step_drift = random.uniform(-2500, -1800)
            spo2_drift = -1.2
            rr_drift = 2.5
            stress_drift = 35.0
        else:
            sim_state = "High"
            hr_drift = random.uniform(18, 26)
            hrv_drift = random.uniform(-28, -20)
            sleep_drift = random.uniform(-2.5, -1.8)
            step_drift = random.uniform(-4000, -3000)
            spo2_drift = -2.5
            rr_drift = 4.5
            stress_drift = 55.0

        base = data["baseline"]
        now_t = datetime.now(timezone.utc)
        reading = {
            "patient_id": p.id,
            "timestamp": now_t,
            "heart_rate": round(base["resting_hr"]["mean"] + hr_drift + 4.0, 1),
            "resting_heart_rate": round(base["resting_hr"]["mean"] + hr_drift, 1),
            "hrv": round(max(15.0, base["hrv"]["mean"] + hrv_drift), 1),
            "spo2": round(max(91.0, min(99.0, base["spo2"]["mean"] + spo2_drift)), 1),
            "steps": int(max(800, base["steps"]["mean"] + step_drift)),
            "activity_level": "sedentary" if step_drift < -1500 else "moderate",
            "sleep_duration": round(max(3.5, base["sleep_duration"]["mean"] + sleep_drift), 1),
            "sleep_quality": round(max(40.0, 85.0 + (sleep_drift * 15.0)), 1),
            "respiratory_rate": round(base["respiratory_rate"]["mean"] + rr_drift, 1),
            "body_temperature": 36.8,
            "stress_index": round(min(95.0, max(15.0, base["stress_index"]["mean"] + stress_drift)), 1),
            "is_anomaly": sim_state == "High",
            "signal_quality": round(random.uniform(0.90, 0.99), 2)
        }
        db.add(WearableReading(**reading))

        # Twin state
        devs = PersonalBaselineEngine.calculate_deviations(reading, base)
        d_score, d_level, top_c = DigitalTwinEngine.calculate_twin_drift_score(devs)
        p_risks = RiskForecastingEngine.forecast_risks(data["ehr"], d_score, devs, data_quality=reading["signal_quality"]*100)

        ts = TwinState(
            patient_id=p.id,
            timestamp=now_t,
            baseline=base,
            current_state=reading,
            deviations=devs,
            twin_drift_score=d_score,
            drift_level=d_level,
            risk_6h=p_risks["risk_6h"],
            risk_24h=p_risks["risk_24h"],
            risk_72h=p_risks["risk_72h"],
            confidence=p_risks["confidence"],
            data_quality=round(reading["signal_quality"]*100, 1),
            top_contributors=top_c,
            simulation_state=sim_state
        )
        db.add(ts)

        # Generate alerts if elevated/high
        al = AlertEngine.evaluate_and_generate_alerts(p.id, d_score, d_level, p_risks["risk_24h"], devs, data_quality=reading["signal_quality"]*100)
        for a in al:
            db.add(Alert(**a))

        if i % 100 == 0 or i == count - 1:
            db.commit()
            print(f" -> Processed {i+1}/{count} patients...")

    db.commit()
    db.close()

    # Save JSON files
    data_dir = BASE_DIR / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    with open(data_dir / "synthetic_ehr.json", "w") as f:
        json.dump(all_ehr_json, f, indent=2, default=str)

    # Data dictionary
    data_dictionary = {
        "dataset_name": "CardioTwin AI Synthetic Cardiovascular Cohort",
        "version": "1.0.0",
        "description": "Synthetic multi-modal cohort combining clinical EHR and longitudinal wearable telemetry.",
        "compliance": "Zero Real-Patient Data. Purely synthetic mathematical simulation.",
        "variables": {
            "patient_id": {"type": "string", "description": "Unique synthetic patient identifier"},
            "age": {"type": "integer", "unit": "years", "range": "35-85"},
            "sex": {"type": "categorical", "values": ["Male", "Female"]},
            "bmi": {"type": "float", "unit": "kg/m^2", "range": "18.5-42.0"},
            "systolic_bp": {"type": "float", "unit": "mmHg", "description": "Resting seated blood pressure"},
            "diastolic_bp": {"type": "float", "unit": "mmHg", "description": "Resting diastolic blood pressure"},
            "hba1c": {"type": "float", "unit": "%", "description": "Glycated hemoglobin"},
            "ldl": {"type": "float", "unit": "mg/dL", "description": "Low-density lipoprotein cholesterol"},
            "resting_heart_rate": {"type": "float", "unit": "bpm", "description": "Wearable nocturnal/quiescent resting HR"},
            "hrv": {"type": "float", "unit": "ms", "description": "Root Mean Square of Successive Differences (RMSSD)"},
            "sleep_duration": {"type": "float", "unit": "hours", "description": "Total nocturnal sleep duration"},
            "steps": {"type": "integer", "unit": "steps/day", "description": "Daily ambulatory step count"},
            "spo2": {"type": "float", "unit": "%", "description": "Peripheral capillary oxygen saturation"},
            "twin_drift_score": {"type": "float", "range": "0-100", "description": "Multivariate distance from personal baseline"}
        }
    }
    with open(data_dir / "data_dictionary.json", "w") as f:
        json.dump(data_dictionary, f, indent=2)

    print("[CardioTwin AI] Data generation complete! Seeded database & generated JSON artifacts.")

if __name__ == "__main__":
    main()
