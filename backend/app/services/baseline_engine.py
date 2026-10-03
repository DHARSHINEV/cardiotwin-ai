"""
Personal Baseline Engine for CardioTwin AI.
Computes patient-specific physiological baselines and individual deviation metrics (Percentage & Z-Score).
Ensures the system differentiates between population normalcy and individual deviation.
"""
from typing import Dict, List, Any
import numpy as np

SIGNALS_CONFIG = {
    "resting_hr": {"unit": "bpm", "name": "Resting Heart Rate", "higher_is_worse": True},
    "hrv": {"unit": "ms", "name": "Heart Rate Variability (RMSSD)", "higher_is_worse": False},
    "sleep_duration": {"unit": "hours", "name": "Sleep Duration", "higher_is_worse": False},
    "steps": {"unit": "steps/day", "name": "Daily Steps", "higher_is_worse": False},
    "spo2": {"unit": "%", "name": "Oxygen Saturation (SpO2)", "higher_is_worse": False},
    "respiratory_rate": {"unit": "breaths/min", "name": "Respiratory Rate", "higher_is_worse": True},
    "stress_index": {"unit": "index", "name": "Stress Index", "higher_is_worse": True}
}

class PersonalBaselineEngine:
    @staticmethod
    def compute_baseline_from_history(historical_readings: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        """
        Calculates personal baseline statistics (mean, std, median, 95% bounds)
        from a patient's historical stable period.
        """
        if not historical_readings:
            # Fallback default clinical reference baseline
            return PersonalBaselineEngine.get_default_baseline()

        baseline = {}
        for key, conf in SIGNALS_CONFIG.items():
            vals = [float(r[key]) for r in historical_readings if key in r and r[key] is not None]
            if len(vals) < 3:
                vals = [70.0 if key == "resting_hr" else 50.0]
            
            mean_val = float(np.mean(vals))
            std_val = float(np.std(vals)) if np.std(vals) > 0.01 else 1.0
            median_val = float(np.median(vals))
            
            # 2 standard deviations (~95% empirical normal range for THIS patient)
            lower_bound = round(max(0.0, mean_val - 2.0 * std_val), 1)
            upper_bound = round(mean_val + 2.0 * std_val, 1)

            baseline[key] = {
                "mean": round(mean_val, 1),
                "std": round(std_val, 2),
                "median": round(median_val, 1),
                "lower_bound": lower_bound,
                "upper_bound": upper_bound,
                "unit": conf["unit"],
                "name": conf["name"]
            }
        return baseline

    @staticmethod
    def get_default_baseline() -> Dict[str, Dict[str, Any]]:
        """Default baseline for demo patient PAT-A-1042"""
        return {
            "resting_hr": {"mean": 68.0, "std": 4.8, "median": 68.0, "lower_bound": 58.4, "upper_bound": 77.6, "unit": "bpm", "name": "Resting Heart Rate"},
            "hrv": {"mean": 52.0, "std": 6.2, "median": 52.0, "lower_bound": 39.6, "upper_bound": 64.4, "unit": "ms", "name": "Heart Rate Variability (RMSSD)"},
            "sleep_duration": {"mean": 7.1, "std": 0.6, "median": 7.1, "lower_bound": 5.9, "upper_bound": 8.3, "unit": "hours", "name": "Sleep Duration"},
            "steps": {"mean": 6200.0, "std": 850.0, "median": 6200.0, "lower_bound": 4500.0, "upper_bound": 7900.0, "unit": "steps/day", "name": "Daily Steps"},
            "spo2": {"mean": 97.0, "std": 0.8, "median": 97.0, "lower_bound": 95.4, "upper_bound": 98.6, "unit": "%", "name": "Oxygen Saturation (SpO2)"},
            "respiratory_rate": {"mean": 14.5, "std": 1.2, "median": 14.5, "lower_bound": 12.1, "upper_bound": 16.9, "unit": "breaths/min", "name": "Respiratory Rate"},
            "stress_index": {"mean": 28.0, "std": 5.5, "median": 28.0, "lower_bound": 17.0, "upper_bound": 39.0, "unit": "index", "name": "Stress Index"}
        }

    @staticmethod
    def calculate_deviations(
        current_state: Dict[str, float],
        baseline: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Dict[str, Any]]:
        """
        Calculates personal deviation metrics comparing current observed values
        against the patient's individual baseline.
        """
        deviations = {}
        for signal_key, current_val in current_state.items():
            if signal_key not in baseline:
                continue
            
            b_info = baseline[signal_key]
            mean_b = b_info["mean"]
            std_b = b_info["std"] if b_info["std"] > 0.001 else 1.0
            
            pct_change = round(((current_val - mean_b) / mean_b) * 100.0, 1)
            z_score = round((current_val - mean_b) / std_b, 2)
            
            # Clinical status determination
            abs_z = abs(z_score)
            if abs_z < 1.5:
                status = "normal"
            elif abs_z < 2.5:
                status = "elevated" if z_score > 0 else "depressed"
            else:
                status = "critical"

            deviations[signal_key] = {
                "current_value": round(current_val, 1),
                "baseline_mean": mean_b,
                "percentage_change": pct_change,
                "z_score": z_score,
                "unit": b_info.get("unit", ""),
                "status": status,
                "name": b_info.get("name", signal_key)
            }
        return deviations
