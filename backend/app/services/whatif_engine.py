"""
What-If Digital Twin Scenario Simulator for CardioTwin AI.
Directly perturbs patient-specific physiological state variables,
recomputes baseline deviations and Twin Drift, and evaluates multi-horizon risk trajectories.
"""
from typing import Dict, Any, List, Optional
import uuid
import math
from backend.app.services.baseline_engine import PersonalBaselineEngine
from backend.app.services.twin_engine import DigitalTwinEngine
from backend.app.services.risk_engine import RiskForecastingEngine

class WhatIfSimulationEngine:
    @staticmethod
    def run_simulation(
        patient_id: str,
        current_state: Dict[str, Any],
        baseline: Dict[str, Any],
        ehr: Dict[str, Any],
        current_risks: Dict[str, float],
        scenario_params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Simulates future trajectory by modifying state variables and recalculating the Digital Twin.
        Deterministic, reproducible, and mathematically rigorous.
        """
        sim_id = f"SIM-{uuid.uuid4().hex[:8].upper()}"

        # 1. Unmitigated baseline trajectory
        base_6h = current_risks.get("risk_6h", 0.12)
        base_24h = current_risks.get("risk_24h", 0.35)
        base_72h = current_risks.get("risk_72h", 0.50)
        current_drift = current_state.get("twin_drift_score", 45.0)

        # 2. Extract clinician-configured simulation inputs
        sim_sleep = scenario_params.get("simulated_sleep_hours")
        sim_activity = scenario_params.get("simulated_activity_level") # sedentary, light, moderate, active
        sim_med_adh = scenario_params.get("simulated_medication_adherence") # 0.0 - 1.0
        sim_stress_red = scenario_params.get("simulated_stress_reduction", 0.0) # 0 - 100%
        sim_rhr_input = scenario_params.get("simulated_resting_hr")

        # 3. Create simulated physiological state dictionary
        sim_state = dict(current_state)
        sim_ehr = dict(ehr)

        base_rhr = baseline.get("resting_hr", {}).get("mean", 68.0)
        base_hrv = baseline.get("hrv", {}).get("mean", 52.0)
        base_sleep = baseline.get("sleep_duration", {}).get("mean", 7.1)
        base_steps = baseline.get("steps", {}).get("mean", 6200.0)

        cur_rhr = current_state.get("resting_heart_rate", current_state.get("resting_hr", base_rhr))
        cur_hrv = current_state.get("hrv", base_hrv)
        cur_sleep = current_state.get("sleep_duration", base_sleep)
        cur_stress = current_state.get("stress_index", 28.0)

        intervention_yields = {}

        # Apply Sleep intervention
        if sim_sleep is not None:
            sim_state["sleep_duration"] = float(sim_sleep)
            sleep_delta = float(sim_sleep) - cur_sleep
            if sleep_delta > 0:
                intervention_yields["Sleep Restoration (+{:.1f}h)".format(sleep_delta)] = (sleep_delta / base_sleep) * 0.30

        # Apply Medication Adherence intervention
        if sim_med_adh is not None:
            sim_ehr["medication_adherence"] = float(sim_med_adh)
            cur_adh = ehr.get("medication_adherence", 0.70)
            adh_delta = float(sim_med_adh) - cur_adh
            if adh_delta > 0:
                intervention_yields["Medication Adherence (+{:.0f}%)".format(adh_delta * 100)] = adh_delta * 0.40

        # Apply Physical Mobilization intervention
        if sim_activity is not None:
            activity_steps = {
                "sedentary": min(cur_steps := current_state.get("steps", 2800), 2500),
                "light": max(cur_steps, 4000),
                "moderate": max(cur_steps, int(base_steps)),
                "active": max(cur_steps, int(base_steps * 1.25))
            }
            sim_steps = activity_steps.get(sim_activity, int(base_steps))
            sim_state["steps"] = sim_steps
            sim_state["activity_level"] = sim_activity
            if sim_steps > current_state.get("steps", 2800):
                intervention_yields["Physical Mobilization ({})".format(sim_activity)] = 0.15

        # Apply Stress reduction
        if sim_stress_red is not None and sim_stress_red > 0:
            sim_state["stress_index"] = max(15.0, cur_stress * (1.0 - (sim_stress_red / 100.0)))
            intervention_yields["Autonomic Stress Reduction (-{:.0f}%)".format(sim_stress_red)] = (sim_stress_red / 100.0) * 0.18

        # Hemodynamic physiological coupling:
        # Improved sleep and stress reduction restore RHR and HRV toward patient's baseline
        recovery_fraction = 0.0
        if sim_sleep and sim_sleep > cur_sleep:
            recovery_fraction += min(0.40, (sim_sleep - cur_sleep) / 3.0)
        if sim_stress_red:
            recovery_fraction += min(0.30, sim_stress_red / 150.0)

        if sim_rhr_input is not None:
            sim_state["resting_heart_rate"] = float(sim_rhr_input)
            sim_state["heart_rate"] = float(sim_rhr_input) + 4.0
        else:
            sim_rhr = cur_rhr - (recovery_fraction * max(0.0, cur_rhr - base_rhr))
            sim_state["resting_heart_rate"] = round(sim_rhr, 1)
            sim_state["heart_rate"] = round(sim_rhr + 4.0, 1)

        sim_hrv = cur_hrv + (recovery_fraction * max(0.0, base_hrv - cur_hrv))
        sim_state["hrv"] = round(sim_hrv, 1)

        # 4. RECALCULATE derived deviations from baseline
        sim_deviations = PersonalBaselineEngine.calculate_deviations(sim_state, baseline)

        # 5. RECALCULATE Twin Drift Score
        sim_drift_score, sim_drift_level, _ = DigitalTwinEngine.calculate_twin_drift_score(sim_deviations)

        # 6. RECALCULATE Risk Forecast using updated state
        sim_risks = RiskForecastingEngine.forecast_risks(
            sim_ehr, sim_drift_score, sim_deviations, data_quality=sim_state.get("signal_quality", 1.0) * 100
        )

        # 7. Formulate dual trajectories
        # Immediate 6h has physiological response latency
        trajectories = [
            {
                "horizon": "Now",
                "hours_from_now": 0,
                "baseline_risk": round(base_6h * 0.85, 3),
                "simulated_risk": round(base_6h * 0.85, 3),
                "projected_drift": round(current_drift, 1)
            },
            {
                "horizon": "6h",
                "hours_from_now": 6,
                "baseline_risk": base_6h,
                "simulated_risk": round(max(0.04, base_6h * 0.70 + sim_risks["risk_6h"] * 0.30), 3),
                "projected_drift": round(current_drift * 0.90 + sim_drift_score * 0.10, 1)
            },
            {
                "horizon": "24h",
                "hours_from_now": 24,
                "baseline_risk": base_24h,
                "simulated_risk": round(sim_risks["risk_24h"], 3),
                "projected_drift": round(sim_drift_score, 1)
            },
            {
                "horizon": "72h",
                "hours_from_now": 72,
                "baseline_risk": base_72h,
                "simulated_risk": round(sim_risks["risk_72h"], 3),
                "projected_drift": round(max(10.0, sim_drift_score * 0.85), 1)
            }
        ]

        # 8. Counterfactual Explanations
        insights = []
        if intervention_yields:
            sorted_yields = sorted(intervention_yields.items(), key=lambda x: x[1], reverse=True)
            largest_yield_name = sorted_yields[0][0]
            insights.append(
                f"Under this simulated scenario, the largest modeled risk mitigation stems from {largest_yield_name}."
            )
            for y_name, _ in sorted_yields[1:]:
                insights.append(f"Additional physiological stabilization provided by {y_name}.")
            
            risk_drop = max(0, int((base_24h - sim_risks["risk_24h"]) * 100))
            insights.append(
                f"Projected 24h deterioration risk decreases from {int(base_24h*100)}% to {int(sim_risks['risk_24h']*100)}% "
                f"(-{risk_drop}% absolute reduction), shifting Twin Drift to {sim_drift_level} ({sim_drift_score:.1f})."
            )
        else:
            largest_yield_name = "No active interventions"
            insights.append("No active scenario adjustments made. Trajectory matches current unmitigated progression.")

        return {
            "id": sim_id,
            "patient_id": patient_id,
            "scenario_name": scenario_params.get("scenario_name", "Clinician Intervention Scenario"),
            "parameters_modified": scenario_params,
            "trajectories": trajectories,
            "counterfactual_insights": insights,
            "largest_contributor_to_improvement": largest_yield_name,
            "disclaimer": "SIMULATED SCENARIO — NOT A CLINICAL PREDICTION. FOR CLINICIAN DECISION SUPPORT ONLY."
        }
