"""
SQLAlchemy ORM models for CardioTwin AI.
Represents patients, EHR clinical records, high-frequency wearable readings,
Digital Twin personalized states, risk predictions, clinician alerts, and what-if simulation runs.
"""
from sqlalchemy import (
    Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text, JSON, func
)
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.app.db.session import Base

class Patient(Base):
    __tablename__ = "patients"

    id = Column(String(64), primary_key=True, index=True)
    name = Column(String(128), nullable=False)
    age = Column(Integer, nullable=False)
    sex = Column(String(16), nullable=False)
    height_cm = Column(Float, nullable=False)
    weight_kg = Column(Float, nullable=False)
    bmi = Column(Float, nullable=False)
    primary_condition = Column(String(128), default="Hypertension & Dyslipidemia")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    ehr = relationship("EHRRecord", back_populates="patient", uselist=False, cascade="all, delete-orphan")
    wearables = relationship("WearableReading", back_populates="patient", cascade="all, delete-orphan", order_by="WearableReading.timestamp")
    twin_states = relationship("TwinState", back_populates="patient", cascade="all, delete-orphan", order_by="TwinState.timestamp.desc()")
    risk_predictions = relationship("RiskPrediction", back_populates="patient", cascade="all, delete-orphan")
    alerts = relationship("Alert", back_populates="patient", cascade="all, delete-orphan", order_by="Alert.timestamp.desc()")
    simulations = relationship("SimulationRun", back_populates="patient", cascade="all, delete-orphan")


class EHRRecord(Base):
    __tablename__ = "ehr_records"

    id = Column(Integer, primary_key=True, autoincrement=True)
    patient_id = Column(String(64), ForeignKey("patients.id"), nullable=False, unique=True, index=True)
    
    smoking_status = Column(String(32), default="Never")
    diabetes = Column(Boolean, default=False)
    hypertension = Column(Boolean, default=False)
    dyslipidemia = Column(Boolean, default=False)
    family_history = Column(Boolean, default=False)
    previous_cardiac_history = Column(Boolean, default=False)
    
    medications = Column(JSON, default=list) # e.g. ["Amlodipine 5mg", "Atorvastatin 20mg", "Metformin 500mg"]
    medication_adherence = Column(Float, default=0.85) # 0.0 to 1.0
    
    systolic_bp = Column(Float, nullable=False)
    diastolic_bp = Column(Float, nullable=False)
    resting_hr = Column(Float, nullable=False)
    cholesterol_total = Column(Float, nullable=False)
    ldl = Column(Float, nullable=False)
    hdl = Column(Float, nullable=False)
    hba1c = Column(Float, nullable=False)
    creatinine = Column(Float, nullable=False)
    
    previous_events = Column(JSON, default=list)
    risk_factors = Column(JSON, default=list)
    recorded_at = Column(DateTime, default=datetime.utcnow)

    patient = relationship("Patient", back_populates="ehr")


class WearableReading(Base):
    __tablename__ = "wearable_readings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    patient_id = Column(String(64), ForeignKey("patients.id"), nullable=False, index=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    
    heart_rate = Column(Float, nullable=False)
    resting_heart_rate = Column(Float, nullable=False)
    hrv = Column(Float, nullable=False) # RMSSD in ms
    spo2 = Column(Float, nullable=False) # %
    steps = Column(Integer, nullable=False)
    activity_level = Column(String(32), default="sedentary") # sedentary, light, moderate, active
    sleep_duration = Column(Float, nullable=False) # hours
    sleep_quality = Column(Float, nullable=False) # 0-100 score
    respiratory_rate = Column(Float, nullable=False) # breaths/min
    body_temperature = Column(Float, nullable=False) # Celsius
    stress_index = Column(Float, nullable=False) # 0-100
    
    is_anomaly = Column(Boolean, default=False)
    signal_quality = Column(Float, default=1.0) # 0.0 - 1.0 quality flag

    patient = relationship("Patient", back_populates="wearables")


class TwinState(Base):
    """
    Patient-specific Digital Twin state snapshot.
    Maintains baseline statistics, current observed values, deviations,
    Twin Drift Score, multi-horizon risks, and confidence intervals.
    """
    __tablename__ = "twin_states"

    id = Column(Integer, primary_key=True, autoincrement=True)
    patient_id = Column(String(64), ForeignKey("patients.id"), nullable=False, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    # JSON blobs for rich personalized profile
    baseline = Column(JSON, nullable=False)
    # {
    #   "resting_hr": {"mean": 68.0, "std": 4.5, "median": 68.0, "lower": 59.0, "upper": 77.0},
    #   "hrv": {"mean": 52.0, "std": 6.0, "median": 52.0, "lower": 40.0, "upper": 64.0},
    #   "sleep": {"mean": 7.1, "std": 0.6, "median": 7.1, "lower": 5.9, "upper": 8.3},
    #   "steps": {"mean": 6200, "std": 800, "median": 6200, "lower": 4600, "upper": 7800},
    #   "spo2": {"mean": 97.0, "std": 0.8, "median": 97.0, "lower": 95.4, "upper": 98.6}
    # }
    
    current_state = Column(JSON, nullable=False)
    deviations = Column(JSON, nullable=False) # Percentage & Z-score deviations
    
    twin_drift_score = Column(Float, nullable=False) # 0 - 100 scale
    drift_level = Column(String(32), nullable=False) # Normal, Watch, Elevated, High
    
    risk_6h = Column(Float, nullable=False) # 0.0 - 1.0
    risk_24h = Column(Float, nullable=False) # 0.0 - 1.0
    risk_72h = Column(Float, nullable=False) # 0.0 - 1.0
    
    top_contributors = Column(JSON, default=list)
    confidence = Column(Float, default=0.92)
    data_quality = Column(Float, default=0.95)
    simulation_state = Column(String(32), default="Normal") # Normal, Gradual deterioration, Acute anomaly, Recovery

    patient = relationship("Patient", back_populates="twin_states")


class RiskPrediction(Base):
    __tablename__ = "risk_predictions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    patient_id = Column(String(64), ForeignKey("patients.id"), nullable=False, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    horizon = Column(String(16), nullable=False) # 6h, 24h, 72h
    probability = Column(Float, nullable=False)
    risk_category = Column(String(32), nullable=False) # Low, Moderate, Elevated, Critical
    confidence_lower = Column(Float, nullable=False)
    confidence_upper = Column(Float, nullable=False)
    model_version = Column(String(32), default="v1.0-fusion")

    patient = relationship("Patient", back_populates="risk_predictions")


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(String(64), primary_key=True)
    patient_id = Column(String(64), ForeignKey("patients.id"), nullable=False, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    severity = Column(String(32), nullable=False) # Watch, Elevated, High
    title = Column(String(256), nullable=False)
    reason = Column(Text, nullable=False)
    affected_signals = Column(JSON, default=list)
    trend = Column(String(64), default="Worsening")
    model_risk = Column(Float, nullable=False)
    data_quality = Column(Float, nullable=False)
    acknowledged = Column(Boolean, default=False)
    acknowledged_by = Column(String(128), nullable=True)
    acknowledged_at = Column(DateTime, nullable=True)

    patient = relationship("Patient", back_populates="alerts")


class SimulationRun(Base):
    __tablename__ = "simulation_runs"

    id = Column(String(64), primary_key=True)
    patient_id = Column(String(64), ForeignKey("patients.id"), nullable=False, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    scenario_name = Column(String(128), default="Custom Scenario")
    parameters_modified = Column(JSON, nullable=False) # e.g. {"sleep": 7.0, "medication_adherence": 0.95}
    baseline_trajectory = Column(JSON, nullable=False) # [{time: "6h", risk: 0.12}, ...]
    simulated_trajectory = Column(JSON, nullable=False)
    counterfactual_insights = Column(Text, nullable=False)
    disclaimer = Column(String(256), default="SIMULATED SCENARIO — NOT A CLINICAL PREDICTION")

    patient = relationship("Patient", back_populates="simulations")


class ModelPrediction(Base):
    __tablename__ = "model_predictions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    model_name = Column(String(64), nullable=False) # Model A (EHR-only), Model B (Wearable-only), Model C (Fusion Twin)
    dataset_split = Column(String(32), default="test")
    auroc = Column(Float, nullable=False)
    auprc = Column(Float, nullable=False)
    precision = Column(Float, nullable=False)
    recall = Column(Float, nullable=False)
    f1 = Column(Float, nullable=False)
    brier_score = Column(Float, nullable=False)
    false_alert_rate_per_patient_week = Column(Float, nullable=False)
    median_lead_time_hours = Column(Float, nullable=False)
    metadata_json = Column(JSON, default=dict)
    evaluated_at = Column(DateTime, default=datetime.utcnow)
