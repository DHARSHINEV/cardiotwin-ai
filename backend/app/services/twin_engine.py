"""
Digital Twin State Engine for CardioTwin AI.
Calculates the unified Twin Drift Score (0 - 100), drift level (Normal, Watch, Elevated, High),
and ranks top physiological contributors with explainability weights.
"""
from typing import Dict, List, Any, Tuple
import math

# Clinical weights for multivariate physiological drift calculation
SIGNAL_WEIGHTS = {
    "resting_hr": 0.25,        # Sympathetic surge / hemodynamic load
    "hrv": 0.25,               # Autonomic imbalance / vagal withdrawal
    "spo2": 0.15,              # Pulmonary / systemic oxygenation
    "sleep_duration": 0.15,    # Recovery deficit / circadian stress
    "steps": 0.10,             # Functional capacity / activity slump
    "respiratory_rate": 0.08,  # Cardiopulmonary compensatory effort
    "stress_index": 0.07       # Neurohumoral activation
}

class DigitalTwinEngine:
    @staticmethod
    def calculate_twin_drift_score(deviations: Dict[str, Dict[str, Any]]) -> Tuple[float, str, List[Dict[str, Any]]]:
        """
        Calculates multivariate physiological distance from the patient's personal baseline.
        Returns:
            - twin_drift_score: float in [0.0, 100.0]
            - drift_level: "Normal" | "Watch" | "Elevated" | "High"
            - top_contributors: List of structured explanations
        """
        weighted_z_sum = 0.0
        total_weight = 0.0
        contributions = []

        for signal, weight in SIGNAL_WEIGHTS.items():
            if signal not in deviations:
                continue

            dev = deviations[signal]
            z = dev.get("z_score", 0.0)
            pct = dev.get("percentage_change", 0.0)
            val = dev.get("current_value", 0.0)
            baseline = dev.get("baseline_mean", 0.0)
            unit = dev.get("unit", "")
            name = dev.get("name", signal)

            # Determine if this deviation is deleterious (harmful direction)
            # For HR, RR, Stress: positive Z is deleterious.
            # For HRV, SpO2, Sleep, Steps: negative Z is deleterious.
            is_worse = False
            if signal in ["resting_hr", "respiratory_rate", "stress_index"]:
                impact_factor = max(0.0, z) + 0.3 * max(0.0, -z) # Mostly penalized when elevated
                is_worse = z > 0
            else:
                impact_factor = max(0.0, -z) + 0.2 * max(0.0, z) # Mostly penalized when depressed
                is_worse = z < 0

            # Scale contribution
            raw_contrib = impact_factor * weight
            weighted_z_sum += raw_contrib
            total_weight += weight

            # Explainable contribution text
            if abs(z) >= 0.8:
                direction = "increased_risk" if is_worse else "protective"
                if signal == "resting_hr":
                    expl = f"Resting HR is {abs(pct):.1f}% {'above' if pct > 0 else 'below'} personal baseline ({val:.0f} vs {baseline:.0f} {unit})"
                elif signal == "hrv":
                    expl = f"HRV (RMSSD) is {abs(pct):.1f}% {'below' if pct < 0 else 'above'} personal baseline ({val:.0f} vs {baseline:.0f} {unit})"
                elif signal == "sleep_duration":
                    expl = f"Sleep duration decreased by {abs(baseline - val):.1f} hours relative to baseline"
                elif signal == "steps":
                    expl = f"Daily activity dropped by {abs(pct):.1f}% ({val:.0f} vs {baseline:.0f} {unit})"
                elif signal == "spo2":
                    expl = f"SpO2 drifted to {val:.1f}% ({abs(pct):.1f}% deviation from personal normal)"
                else:
                    expl = f"{name} deviated by {z:+.1f} standard deviations from baseline"

                contributions.append({
                    "signal": signal,
                    "name": name,
                    "importance": round(raw_contrib, 3),
                    "z_score": z,
                    "percentage_change": pct,
                    "direction": direction,
                    "explanation": expl
                })

        # Normalize score into a sigmoid-like 0-100 scale
        # 1.0 aggregate Z-impact ~ 25 (Watch)
        # 2.0 aggregate Z-impact ~ 50 (Elevated)
        # 3.0+ aggregate Z-impact ~ 75-100 (High)
        if total_weight > 0:
            normalized_impact = weighted_z_sum / total_weight
        else:
            normalized_impact = 0.0

        # Nonlinear scaling to 0 - 100
        # 25.0 * impact gives intuitive scaling: 1 SD -> 25, 2 SD -> 50, 3 SD -> 75
        raw_score = 100.0 * (1.0 - math.exp(-0.45 * max(0.0, normalized_impact)))
        twin_drift_score = round(min(100.0, max(0.0, raw_score)), 1)

        # Categorize
        if twin_drift_score < 25.0:
            drift_level = "Normal"
        elif twin_drift_score < 50.0:
            drift_level = "Watch"
        elif twin_drift_score < 75.0:
            drift_level = "Elevated"
        else:
            drift_level = "High"

        # Sort contributions by importance descending
        contributions.sort(key=lambda x: x["importance"], reverse=True)

        return twin_drift_score, drift_level, contributions
