"""
Pydantic Schemas for CardioTwin AI API validation and serialization.
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Dict, Any, Optional
from datetime import datetime

# --- EHR Schemas ---
class EHRBase(BaseModel):
    smoking_status: str = "Never"
    diabetes: bool = False
    hypertension: bool = True
    dyslipidemia: bool = True
    family_history: bool = False
    previous_cardiac_history: bool = False
    medications: List[str] = []
    medication_adherence: float = 0.85
    systolic_bp: float = 138.0
    diastolic_bp: float = 88.0
    resting_hr: float = 68.0
    cholesterol_total: float = 210.0
    ldl: float = 135.0
    hdl: float = 42.0
    hba1c: float = 6.8
    creatinine: float = 1.05
    previous_events: List[str] = []
    risk_factors: List[str] = []

class EHRResponse(EHRBase):
    id: int
    patient_id: str
    recorded_at: datetime
    model_config = ConfigDict(from_attributes=True)


# --- Wearable Schemas ---
class WearableReadingBase(BaseModel):
    timestamp: datetime
    heart_rate: float
    resting_heart_rate: float
    hrv: float
    spo2: float
    steps: int
    activity_level: str = "moderate"
    sleep_duration: float
    sleep_quality: float
    respiratory_rate: float
    body_temperature: float
    stress_index: float
    is_anomaly: bool = False
    signal_quality: float = 1.0

class WearableReadingResponse(WearableReadingBase):
    id: int
    patient_id: str
    model_config = ConfigDict(from_attributes=True)


# --- Baseline & Deviations ---
class SignalBaseline(BaseModel):
    mean: float
    std: float
    median: float
    lower_bound: float
    upper_bound: float
    unit: str

class SignalDeviation(BaseModel):
    current_value: float
    baseline_mean: float
    percentage_change: float
    z_score: float
    unit: str
    status: str # normal, elevated, depressed, critical


# --- Twin State Schemas ---
class TopContributor(BaseModel):
    signal: str
    importance: float # SHAP or feature weight contribution (0.0 to 1.0)
    direction: str # "increased_risk", "protective"
    explanation: str

class TwinStateResponse(BaseModel):
    patient_id: str
    timestamp: datetime
    baseline: Dict[str, Any]
    current_state: Dict[str, Any]
    deviations: Dict[str, Any]
    twin_drift_score: float
    drift_level: str # Normal, Watch, Elevated, High
    risk_6h: float
    risk_24h: float
    risk_72h: float
    confidence: float
    data_quality: float
    top_contributors: List[TopContributor]
    simulation_state: str
    model_config = ConfigDict(from_attributes=True)


# --- Patient Overview Schemas ---
class PatientSummary(BaseModel):
    id: str
    name: str
    age: int
    sex: str
    bmi: float
    primary_condition: str
    current_drift_score: float
    drift_level: str
    risk_24h: float
    data_quality: float
    active_alerts_count: int
    simulation_state: str
    model_config = ConfigDict(from_attributes=True)

class PatientDetail(BaseModel):
    id: str
    name: str
    age: int
    sex: str
    height_cm: float
    weight_kg: float
    bmi: float
    primary_condition: str
    created_at: datetime
    ehr: Optional[EHRResponse] = None
    latest_twin_state: Optional[TwinStateResponse] = None
    model_config = ConfigDict(from_attributes=True)


# --- Simulation Schemas ---
class WhatIfRequest(BaseModel):
    patient_id: str
    scenario_name: Optional[str] = "Clinician Intervention Scenario"
    simulated_sleep_hours: Optional[float] = None
    simulated_activity_level: Optional[str] = None # sedentary, light, moderate, active
    simulated_medication_adherence: Optional[float] = None # 0.0 - 1.0
    simulated_stress_reduction: Optional[float] = None # 0 - 100
    simulated_dietary_adherence: Optional[float] = None # 0.0 - 1.0

class TrajectoryPoint(BaseModel):
    horizon: str # "Now", "6h", "24h", "72h"
    hours_from_now: int
    baseline_risk: float
    simulated_risk: float
    projected_drift: float

class WhatIfResponse(BaseModel):
    id: str
    patient_id: str
    scenario_name: str
    parameters_modified: Dict[str, Any]
    trajectories: List[TrajectoryPoint]
    counterfactual_insights: List[str]
    largest_contributor_to_improvement: str
    disclaimer: str = "SIMULATED SCENARIO — NOT A CLINICAL PREDICTION. FOR CLINICIAN DECISION SUPPORT ONLY."


class WearableSimulationStepRequest(BaseModel):
    patient_id: str
    simulation_state: str = "Gradual deterioration" # Normal, Gradual deterioration, Acute anomaly, Recovery
    step_minutes: int = 60

class WearableSimulationStepResponse(BaseModel):
    patient_id: str
    new_reading: WearableReadingResponse
    updated_twin_state: TwinStateResponse
    alerts_generated: List[Dict[str, Any]]


# --- Alert Schemas ---
class AlertResponse(BaseModel):
    id: str
    patient_id: str
    timestamp: datetime
    severity: str
    title: str
    reason: str
    affected_signals: List[str]
    trend: str
    model_risk: float
    data_quality: float
    acknowledged: bool
    acknowledged_by: Optional[str] = None
    acknowledged_at: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)


# --- Data Quality Schemas ---
class SensorQualityItem(BaseModel):
    sensor_name: str
    status: str # "OK", "Missing", "Degraded", "Spike/Artifact"
    uptime_percentage: float
    last_sample_minutes_ago: int
    warning_message: Optional[str] = None

class DataQualityResponse(BaseModel):
    patient_id: str
    overall_quality_score: float # 0 - 100
    quality_level: str # Excellent, Good, Degraded, Critical
    wearable_completeness: float = 97.0
    signal_consistency: float = 92.0
    freshness: float = 95.0
    sensors: List[SensorQualityItem]
    warnings: List[str]


# --- Model Evaluation Schemas ---
class MetricModelComparison(BaseModel):
    model_name: str
    model_type: str # EHR-only, Wearable-only, Fusion Twin
    auroc: float
    auprc: float
    precision: float
    recall: float
    f1: float
    brier_score: float
    false_alert_rate_per_patient_week: float
    median_lead_time_hours: float

class StressTestResult(BaseModel):
    missing_data_rate: float # 0.0, 0.10, 0.25, 0.50
    auroc: float
    f1: float
    performance_drop_percentage: float

class EvaluationMetricsResponse(BaseModel):
    models: List[MetricModelComparison]
    stress_test: List[StressTestResult]
    calibration_curve: List[Dict[str, float]]
    confusion_matrix: Dict[str, int]
    disclaimer: str = "Synthetic-data evaluation. Conducted via patient-stratified non-overlapping temporal test split."
