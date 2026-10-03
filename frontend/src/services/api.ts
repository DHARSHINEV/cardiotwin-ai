/**
 * API Client for CardioTwin AI Backend.
 */

const API_BASE = "http://localhost:8000/api";

export interface PatientSummary {
  id: string;
  name: string;
  age: number;
  sex: string;
  bmi: number;
  primary_condition: string;
  current_drift_score: number;
  drift_level: "Normal" | "Watch" | "Elevated" | "High";
  risk_24h: number;
  data_quality: number;
  active_alerts_count: number;
  simulation_state: string;
}

export interface PatientDetail {
  id: string;
  name: string;
  age: number;
  sex: string;
  height_cm: number;
  weight_kg: number;
  bmi: number;
  primary_condition: string;
  created_at: string;
  ehr?: {
    smoking_status: string;
    diabetes: boolean;
    hypertension: boolean;
    dyslipidemia: boolean;
    family_history: boolean;
    previous_cardiac_history: boolean;
    medications: string[];
    medication_adherence: number;
    systolic_bp: number;
    diastolic_bp: number;
    resting_hr: number;
    cholesterol_total: number;
    ldl: number;
    hdl: number;
    hba1c: number;
    creatinine: number;
    previous_events: string[];
    risk_factors: string[];
  };
}

export interface SignalBaseline {
  mean: number;
  std: number;
  median: number;
  lower_bound: number;
  upper_bound: number;
  unit: string;
  name: string;
}

export interface SignalDeviation {
  current_value: number;
  baseline_mean: number;
  percentage_change: number;
  z_score: number;
  unit: string;
  status: string;
  name: string;
}

export interface TopContributor {
  signal: string;
  name: string;
  importance: number;
  z_score: number;
  percentage_change: number;
  direction: string;
  explanation: string;
}

export interface TwinState {
  patient_id: string;
  timestamp: string;
  baseline: Record<string, SignalBaseline>;
  current_state: Record<string, any>;
  deviations: Record<string, SignalDeviation>;
  twin_drift_score: number;
  drift_level: "Normal" | "Watch" | "Elevated" | "High";
  risk_6h: number;
  risk_24h: number;
  risk_72h: number;
  confidence: number;
  data_quality: number;
  top_contributors: TopContributor[];
  simulation_state: string;
}

export interface TimelinePoint {
  timestamp: string;
  time_str: string;
  resting_hr: number;
  hrv: number;
  spo2: number;
  steps: number;
  sleep_duration: number;
  twin_drift_score: number;
  drift_level: string;
  is_anomaly: boolean;
}

export interface AlertItem {
  id: string;
  patient_id: string;
  timestamp: string;
  severity: "Watch" | "Elevated" | "High";
  title: string;
  reason: string;
  affected_signals: string[];
  trend: string;
  model_risk: number;
  data_quality: number;
  acknowledged: boolean;
  acknowledged_by?: string;
}

export interface TrajectoryPoint {
  horizon: string;
  hours_from_now: number;
  baseline_risk: number;
  simulated_risk: number;
  projected_drift: number;
}

export interface WhatIfResult {
  id: string;
  patient_id: string;
  scenario_name: string;
  parameters_modified: Record<string, any>;
  trajectories: TrajectoryPoint[];
  counterfactual_insights: string[];
  largest_contributor_to_improvement: string;
  disclaimer: string;
}

export interface ModelMetric {
  model_name: string;
  model_type: string;
  auroc: number;
  auprc: number;
  precision: number;
  recall: number;
  f1: number;
  brier_score: number;
  false_alert_rate_per_patient_week: number;
  median_lead_time_hours: number;
}

export interface EvaluationData {
  models: ModelMetric[];
  stress_test: Array<{
    missing_data_rate: number;
    auroc: number;
    f1: number;
    performance_drop_percentage: number;
  }>;
  calibration_curve: Array<{
    mean_predicted_value: number;
    fraction_of_positives: number;
  }>;
  confusion_matrix: {
    true_negative: number;
    false_positive: number;
    false_negative: number;
    true_positive: number;
  };
  disclaimer: string;
}

export interface DataQualityData {
  patient_id: string;
  overall_quality_score: number;
  quality_level: string;
  wearable_completeness?: number;
  signal_consistency?: number;
  freshness?: number;
  sensors: Array<{
    sensor_name: string;
    status: string;
    uptime_percentage: number;
    last_sample_minutes_ago: number;
    warning_message?: string;
  }>;
  warnings: string[];
}

export interface DemoStage {
  stage: number;
  title: string;
  description: string;
  drift_score: number;
  drift_level: string;
  risk_24h: number;
  key_event: string;
}

export const api = {
  async getPatients(limit = 20, riskFilter?: string): Promise<PatientSummary[]> {
    const url = new URL(`${API_BASE}/patients`);
    url.searchParams.append("limit", limit.toString());
    if (riskFilter) url.searchParams.append("risk_filter", riskFilter);
    const res = await fetch(url.toString());
    return res.json();
  },

  async getPatient(id: string): Promise<PatientDetail> {
    const res = await fetch(`${API_BASE}/patients/${id}`);
    return res.json();
  },

  async getTwinState(id: string): Promise<TwinState> {
    const res = await fetch(`${API_BASE}/patients/${id}/twin`);
    return res.json();
  },

  async getTimeline(id: string): Promise<{ patient_id: string; timeline: TimelinePoint[]; baseline_summary: any }> {
    const res = await fetch(`${API_BASE}/patients/${id}/timeline`);
    return res.json();
  },

  async getAlerts(id: string): Promise<AlertItem[]> {
    const res = await fetch(`${API_BASE}/patients/${id}/alerts`);
    return res.json();
  },

  async acknowledgeAlert(alertId: string, clinicianName = "Dr. Clinician"): Promise<any> {
    const res = await fetch(`${API_BASE}/alerts/${alertId}/acknowledge?acknowledged_by=${encodeURIComponent(clinicianName)}`, {
      method: "POST"
    });
    return res.json();
  },

  async runWhatIf(params: {
    patient_id: string;
    scenario_name?: string;
    simulated_sleep_hours?: number;
    simulated_activity_level?: string;
    simulated_medication_adherence?: number;
    simulated_stress_reduction?: number;
  }): Promise<WhatIfResult> {
    const res = await fetch(`${API_BASE}/simulation`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(params)
    });
    return res.json();
  },

  async simulateWearableStep(patient_id: string, simulation_state: string): Promise<any> {
    const res = await fetch(`${API_BASE}/wearable/simulate`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ patient_id, simulation_state, step_minutes: 60 })
    });
    return res.json();
  },

  async getEvaluationMetrics(): Promise<EvaluationData> {
    const res = await fetch(`${API_BASE}/model/metrics`);
    return res.json();
  },

  async getDataQuality(patient_id: string): Promise<DataQualityData> {
    const res = await fetch(`${API_BASE}/data-quality/${patient_id}`);
    return res.json();
  },

  async getDemoStages(): Promise<{ stages: DemoStage[]; total_stages: number }> {
    const res = await fetch(`${API_BASE}/demo/stages`);
    return res.json();
  },

  async setDemoStage(stageNum: number): Promise<any> {
    const res = await fetch(`${API_BASE}/demo/set-stage/${stageNum}`, { method: "POST" });
    return res.json();
  },

  async getFhirPatient(id: string): Promise<any> {
    const res = await fetch(`${API_BASE}/fhir/Patient/${id}`);
    return res.json();
  }
};
