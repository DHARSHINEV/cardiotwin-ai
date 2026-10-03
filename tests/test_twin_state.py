"""
Unit tests for Personal Baseline Engine and Digital Twin State Calculation.
"""
import pytest
from backend.app.services.baseline_engine import PersonalBaselineEngine
from backend.app.services.twin_engine import DigitalTwinEngine

def test_personal_baseline_calculation():
    # Synthetic 5-day stable telemetry
    history = [
        {"resting_hr": 68.0, "hrv": 52.0, "sleep_duration": 7.1, "steps": 6200, "spo2": 97.0, "respiratory_rate": 14.5, "stress_index": 28.0},
        {"resting_hr": 67.0, "hrv": 54.0, "sleep_duration": 7.3, "steps": 6400, "spo2": 97.0, "respiratory_rate": 14.2, "stress_index": 26.0},
        {"resting_hr": 69.0, "hrv": 50.0, "sleep_duration": 6.9, "steps": 6000, "spo2": 97.0, "respiratory_rate": 14.8, "stress_index": 30.0},
        {"resting_hr": 68.0, "hrv": 51.0, "sleep_duration": 7.0, "steps": 6100, "spo2": 97.0, "respiratory_rate": 14.5, "stress_index": 29.0},
    ]
    baseline = PersonalBaselineEngine.compute_baseline_from_history(history)
    
    assert "resting_hr" in baseline
    assert baseline["resting_hr"]["mean"] == 68.0
    assert baseline["resting_hr"]["lower_bound"] < 68.0
    assert baseline["resting_hr"]["upper_bound"] > 68.0
    assert baseline["hrv"]["mean"] == pytest.approx(51.8, 0.5)

def test_deviation_and_drift_score_calculation():
    baseline = PersonalBaselineEngine.get_default_baseline()
    
    # 1. Normal state should have low drift score (< 25)
    normal_reading = {
        "resting_hr": 68.0,
        "hrv": 52.0,
        "sleep_duration": 7.1,
        "steps": 6200,
        "spo2": 97.0,
        "respiratory_rate": 14.5,
        "stress_index": 28.0
    }
    devs_normal = PersonalBaselineEngine.calculate_deviations(normal_reading, baseline)
    drift_norm, level_norm, _ = DigitalTwinEngine.calculate_twin_drift_score(devs_normal)
    assert drift_norm < 25.0
    assert level_norm == "Normal"

    # 2. Deteriorated state (Patient A-1042 current snapshot from Prompt Section 5)
    # Resting HR: 82 bpm (+20.6%)
    # HRV: 34 ms (-34.6%)
    # Sleep: 5.4 hours (-23.9%)
    # Daily steps: 2800 (-54.8%)
    # SpO2: 95%
    deteriorated_reading = {
        "resting_hr": 82.0,
        "hrv": 34.0,
        "sleep_duration": 5.4,
        "steps": 2800,
        "spo2": 95.0,
        "respiratory_rate": 18.0,
        "stress_index": 74.0
    }
    devs_det = PersonalBaselineEngine.calculate_deviations(deteriorated_reading, baseline)
    drift_det, level_det, top_c = DigitalTwinEngine.calculate_twin_drift_score(devs_det)
    
    assert drift_det >= 50.0 # Should be Elevated or High
    assert level_det in ["Elevated", "High"]
    assert len(top_c) >= 3
    # Verify resting HR and HRV are ranked at the top of contributors
    top_signals = [c["signal"] for c in top_c[:3]]
    assert "resting_hr" in top_signals or "hrv" in top_signals
