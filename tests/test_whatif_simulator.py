"""
Unit tests for Risk Forecasting and What-If Digital Twin Scenario Simulator.
"""
import pytest
from backend.app.services.risk_engine import RiskForecastingEngine
from backend.app.services.whatif_engine import WhatIfSimulationEngine
from backend.app.services.baseline_engine import PersonalBaselineEngine

def test_risk_forecasting_horizons():
    ehr = {
        "age": 57,
        "hypertension": True,
        "diabetes": True,
        "dyslipidemia": True,
        "previous_cardiac_history": True,
        "smoking_status": "Former",
        "medication_adherence": 0.70
    }
    deviations = {
        "resting_hr": {"z_score": 2.8, "percentage_change": 20.6, "current_value": 82.0, "baseline_mean": 68.0, "unit": "bpm"},
        "hrv": {"z_score": -3.1, "percentage_change": -34.6, "current_value": 34.0, "baseline_mean": 52.0, "unit": "ms"}
    }
    
    # High drift case
    risks = RiskForecastingEngine.forecast_risks(ehr, twin_drift_score=81.0, deviations=deviations, data_quality=95.0)
    assert 0.0 < risks["risk_6h"] < 1.0
    assert 0.0 < risks["risk_24h"] < 1.0
    assert 0.0 < risks["risk_72h"] < 1.0
    assert risks["risk_24h"] > risks["risk_6h"]
    assert risks["risk_category"] in ["Elevated", "Critical"]
    assert risks["confidence"] > 0.85

def test_what_if_simulation_counterfactual_behavior():
    baseline = PersonalBaselineEngine.get_default_baseline()
    current_state = {
        "twin_drift_score": 75.0,
        "resting_hr": 82.0,
        "hrv": 34.0,
        "sleep_duration": 5.2,
        "activity_level": "sedentary"
    }
    ehr = {
        "age": 57,
        "hypertension": True,
        "diabetes": True,
        "medication_adherence": 0.65
    }
    current_risks = {
        "risk_6h": 0.28,
        "risk_24h": 0.58,
        "risk_72h": 0.72
    }

    # Intervene: restore sleep to 7.2h and medication adherence to 95%
    scenario_params = {
        "scenario_name": "Sleep Restoration & Adherence Optimization",
        "simulated_sleep_hours": 7.2,
        "simulated_activity_level": "moderate",
        "simulated_medication_adherence": 0.95,
        "simulated_stress_reduction": 40.0
    }

    res = WhatIfSimulationEngine.run_simulation(
        patient_id="PAT-A-1042",
        current_state=current_state,
        baseline=baseline,
        ehr=ehr,
        current_risks=current_risks,
        scenario_params=scenario_params
    )

    assert "trajectories" in res
    assert len(res["trajectories"]) == 4 # Now, 6h, 24h, 72h
    
    # 24h simulated risk should be strictly lower than unmitigated baseline risk
    point_24h = [t for t in res["trajectories"] if t["horizon"] == "24h"][0]
    assert point_24h["simulated_risk"] < point_24h["baseline_risk"]
    assert len(res["counterfactual_insights"]) >= 1
    assert "SIMULATED SCENARIO" in res["disclaimer"]
