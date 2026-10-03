"""
Wearable Data Simulator for CardioTwin AI.
Simulates real-time physiological telemetry across 4 operational states:
1. Normal state (stable around personal baseline)
2. Gradual deterioration (progressive drift over hours/days)
3. Acute anomaly (sudden hemodynamic perturbation)
4. Recovery (therapeutic stabilization returning toward baseline)
"""
from typing import Dict, Any
from datetime import datetime, timezone, timedelta
import random

class WearableSimulator:
    @staticmethod
    def generate_reading_for_state(
        patient_id: str,
        baseline: Dict[str, Dict[str, Any]],
        simulation_state: str = "Normal",
        step_index: int = 0,
        timestamp: datetime = None
    ) -> Dict[str, Any]:
        """
        Generates a physiologically correlated wearable reading conditioned on the patient's baseline
        and the current simulation state.
        """
        if timestamp is None:
            timestamp = datetime.now(timezone.utc)

        # Baseline means
        base_hr = baseline.get("resting_hr", {}).get("mean", 68.0)
        base_hrv = baseline.get("hrv", {}).get("mean", 52.0)
        base_sleep = baseline.get("sleep_duration", {}).get("mean", 7.1)
        base_steps = baseline.get("steps", {}).get("mean", 6200.0)
        base_spo2 = baseline.get("spo2", {}).get("mean", 97.0)
        base_rr = baseline.get("respiratory_rate", {}).get("mean", 14.5)
        base_stress = baseline.get("stress_index", {}).get("mean", 28.0)

        # Add minor natural circadian / white noise
        noise_hr = random.uniform(-1.5, 1.5)
        noise_hrv = random.uniform(-2.0, 2.0)

        is_anomaly = False
        signal_quality = 1.0

        if simulation_state == "Normal":
            # Physiological stability around baseline
            rhr = base_hr + noise_hr
            hr = rhr + random.uniform(2.0, 8.0)
            hrv = max(30.0, base_hrv + noise_hrv)
            sleep_dur = base_sleep + random.uniform(-0.3, 0.4)
            sleep_qual = random.uniform(82.0, 92.0)
            steps = int(base_steps + random.uniform(-400, 600))
            spo2 = min(99.0, max(95.5, base_spo2 + random.uniform(-0.4, 0.6)))
            rr = base_rr + random.uniform(-0.5, 0.8)
            stress = max(10.0, base_stress + random.uniform(-4.0, 5.0))
            activity = "moderate" if steps > 5000 else "light"

        elif simulation_state == "Gradual deterioration":
            # Progressively higher drift factor as step_index increases
            drift_progress = min(1.0, 0.35 + (step_index * 0.12))
            
            # HR rises progressively (+15 to +26%)
            hr_delta = 16.0 * drift_progress
            rhr = base_hr + hr_delta + noise_hr
            hr = rhr + random.uniform(4.0, 10.0)
            
            # HRV declines significantly (-25 to -40%)
            hrv = max(22.0, base_hrv * (1.0 - (0.35 * drift_progress)) + noise_hrv)
            
            # Sleep deficit compounding
            sleep_dur = max(4.2, base_sleep - (1.9 * drift_progress))
            sleep_qual = max(45.0, 80.0 - (30.0 * drift_progress))
            
            # Activity slumps
            steps = int(max(1800, base_steps * (1.0 - (0.55 * drift_progress))))
            
            # SpO2 mild degradation
            spo2 = round(max(92.0, base_spo2 - (1.8 * drift_progress)), 1)
            
            # Compensatory tachypnea
            rr = base_rr + (3.2 * drift_progress)
            
            # Sympathetic stress elevation
            stress = min(90.0, base_stress + (42.0 * drift_progress))
            activity = "sedentary"

        elif simulation_state == "Acute anomaly":
            # Sudden acute tachycardic or hypotensive crisis
            is_anomaly = True
            rhr = base_hr + 28.0 + random.uniform(0.0, 6.0) # > 96 bpm
            hr = rhr + random.uniform(10.0, 20.0)
            hrv = max(18.0, base_hrv * 0.45) # Severe vagal withdrawal
            sleep_dur = max(3.5, base_sleep - 2.8)
            sleep_qual = 38.0
            steps = 1400
            spo2 = round(max(91.0, base_spo2 - 4.5), 1) # Hypoxia alert
            rr = base_rr + 6.5 # Tachypnea > 20
            stress = 88.0
            activity = "sedentary"

        elif simulation_state == "Recovery":
            # Gradually stabilizing back toward baseline
            recovery_factor = min(1.0, 0.5 + (step_index * 0.15))
            rhr = base_hr + (14.0 * (1.0 - recovery_factor)) + noise_hr
            hr = rhr + random.uniform(3.0, 7.0)
            hrv = max(32.0, base_hrv - (15.0 * (1.0 - recovery_factor)))
            sleep_dur = base_sleep - (0.8 * (1.0 - recovery_factor))
            sleep_qual = 78.0
            steps = int(base_steps * (0.8 + 0.2 * recovery_factor))
            spo2 = round(base_spo2 - (0.8 * (1.0 - recovery_factor)), 1)
            rr = base_rr + (1.2 * (1.0 - recovery_factor))
            stress = base_stress + (15.0 * (1.0 - recovery_factor))
            activity = "light" if steps < 5000 else "moderate"

        elif simulation_state in ["Sensor Failure / Artifact", "Unreliable Sensor"]:
            # Failure Case Demo: Sensor detachment / high motion artifact
            is_anomaly = True
            signal_quality = 0.42 # Severely degraded
            rhr = 210.0 # Biologically suspect optical spike
            hr = 215.0
            hrv = 4.0 # Ectopic distortion
            sleep_dur = base_sleep
            sleep_qual = 60.0
            steps = 0 # Suspicious disconnect
            spo2 = 82.0 # Low perfusion / air gap artifact
            rr = base_rr
            stress = 80.0
            activity = "sedentary"

        else:
            # Default normal fallback
            rhr = base_hr
            hr = rhr + 4.0
            hrv = base_hrv
            sleep_dur = base_sleep
            sleep_qual = 85.0
            steps = int(base_steps)
            spo2 = base_spo2
            rr = base_rr
            stress = base_stress
            activity = "moderate"

        return {
            "patient_id": patient_id,
            "timestamp": timestamp,
            "heart_rate": round(float(hr), 1),
            "resting_heart_rate": round(float(rhr), 1),
            "hrv": round(float(hrv), 1),
            "spo2": round(float(spo2), 1),
            "steps": int(steps),
            "activity_level": activity,
            "sleep_duration": round(float(sleep_dur), 1),
            "sleep_quality": round(float(sleep_qual), 1),
            "respiratory_rate": round(float(rr), 1),
            "body_temperature": round(36.8 + random.uniform(-0.2, 0.4), 1),
            "stress_index": round(float(stress), 1),
            "is_anomaly": is_anomaly,
            "signal_quality": signal_quality
        }
