"""
Integration and End-to-End API tests for CardioTwin AI FastAPI endpoints.
Tests all endpoints including health, patients, twin, risk, what-if simulation,
wearable simulator, data quality, demo stages, reset, and 404 error handling.
"""
from fastapi.testclient import TestClient
from backend.main import app
from backend.app.services.data_quality_engine import DataQualityEngine
from backend.app.services.baseline_engine import PersonalBaselineEngine
from backend.app.services.risk_engine import RiskForecastingEngine
from pathlib import Path
import json

client = TestClient(app)

def test_health_endpoint():
    res = client.get("/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert "disclaimer" in data

def test_get_patients_list():
    res = client.get("/patients?limit=5")
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, list)
    assert len(data) > 0
    pids = [p["id"] for p in data]
    assert "PAT-A-1042" in pids or len(pids) > 0

def test_get_demo_patient_profile():
    res = client.get("/patients/PAT-A-1042")
    assert res.status_code == 200
    data = res.json()
    assert data["id"] == "PAT-A-1042"
    assert data["age"] == 57
    assert data["ehr"] is not None

def test_invalid_patient_returns_404():
    res = client.get("/patients/NON_EXISTENT_PATIENT_9999")
    assert res.status_code == 404
    assert "not found" in res.json()["detail"].lower()

def test_get_patient_twin_state():
    res = client.get("/patients/PAT-A-1042/twin")
    assert res.status_code == 200
    data = res.json()
    assert "twin_drift_score" in data
    assert "baseline" in data
    assert "deviations" in data
    assert "top_contributors" in data

def test_get_patient_risk():
    res = client.get("/patients/PAT-A-1042/risk")
    assert res.status_code == 200
    data = res.json()
    assert "risk_6h" in data
    assert "risk_24h" in data
    assert "risk_72h" in data
    assert 0.0 <= data["risk_6h"] <= 1.0
    assert 0.0 <= data["risk_24h"] <= 1.0
    assert 0.0 <= data["risk_72h"] <= 1.0

def test_get_patient_timeline():
    res = client.get("/patients/PAT-A-1042/timeline")
    assert res.status_code == 200
    data = res.json()
    assert "timeline" in data
    assert len(data["timeline"]) > 0

def test_get_patient_alerts():
    res = client.get("/patients/PAT-A-1042/alerts")
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, list)

def test_what_if_simulation_endpoint():
    payload = {
        "patient_id": "PAT-A-1042",
        "scenario_name": "Test Adherence Optimization",
        "simulated_sleep_hours": 7.5,
        "simulated_medication_adherence": 0.95
    }
    res = client.post("/simulation", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "trajectories" in data
    assert len(data["trajectories"]) == 4
    assert "counterfactual_insights" in data
    assert "SIMULATED SCENARIO" in data["disclaimer"]

def test_wearable_step_simulation():
    payload = {
        "patient_id": "PAT-A-1042",
        "simulation_state": "Gradual deterioration",
        "step_minutes": 60
    }
    res = client.post("/wearable/simulate", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "new_reading" in data
    assert "updated_twin_state" in data

def test_data_quality_endpoint():
    res = client.get("/data-quality/PAT-A-1042")
    assert res.status_code == 200
    data = res.json()
    assert "overall_quality_score" in data
    assert "sensors" in data
    assert "wearable_completeness" in data
    assert "signal_consistency" in data
    assert "freshness" in data

def test_data_quality_missing_telemetry():
    # Unit test data quality engine when readings are missing
    dq = DataQualityEngine.assess_patient_data_quality({})
    assert dq["overall_quality_score"] == 0.0
    assert dq["quality_level"] == "Critical"
    assert len(dq["warnings"]) > 0

def test_model_metrics_endpoint():
    res = client.get("/model/metrics")
    assert res.status_code == 200
    data = res.json()
    assert "models" in data
    assert len(data["models"]) >= 3 # EHR-Only, Wearable-Only, Digital Twin Fusion
    twin_model = next((m for m in data["models"] if "Digital Twin" in m["model_name"]), None)
    assert twin_model is not None
    assert twin_model["auroc"] >= 0.70

def test_demo_stages_and_reset():
    # Check 10 stages
    res = client.get("/demo/stages")
    assert res.status_code == 200
    data = res.json()
    assert data["total_stages"] == 10
    assert len(data["stages"]) == 10

    # Test setting stage
    res_set = client.post("/demo/set-stage/3")
    assert res_set.status_code == 200
    assert res_set.json()["current_stage"]["stage"] == 3

    # Test demo reset
    res_reset = client.post("/demo/reset")
    assert res_reset.status_code == 200
    assert res_reset.json()["current_stage"]["stage"] == 1

def test_model_artifacts_and_loading():
    # Verify trained model artifacts or evaluation results exist
    eval_file = Path("data/evaluation_results.json")
    assert eval_file.exists(), "evaluation_results.json must exist"
    with open(eval_file, "r") as f:
        results = json.load(f)
    assert "models" in results
    assert len(results["models"]) == 3
    assert "Digital Twin" in results["models"][2]["model_name"]
