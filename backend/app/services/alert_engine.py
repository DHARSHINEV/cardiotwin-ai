"""
Alert Engine for CardioTwin AI.
Generates non-alarmist, explainable clinical alerts based on physiological baseline deviations,
Twin Drift Score thresholds, and multi-horizon risk forecasts.
"""
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
import uuid

class AlertEngine:
    @staticmethod
    def evaluate_and_generate_alerts(
        patient_id: str,
        twin_drift_score: float,
        drift_level: str,
        risk_24h: float,
        deviations: Dict[str, Dict[str, Any]],
        data_quality: float = 95.0
    ) -> List[Dict[str, Any]]:
        """
        Evaluates current Twin State against clinical thresholds and generates explainable alerts.
        """
        alerts = []
        now = datetime.now(timezone.utc)

        # High Severity Alert
        if drift_level == "High" or risk_24h >= 0.55:
            affected = []
            reasons = []
            for sig, dev in deviations.items():
                if abs(dev.get("z_score", 0.0)) >= 2.0:
                    affected.append(sig)
                    reasons.append(f"{dev.get('name', sig)} ({dev.get('percentage_change', 0):+.1f}%)")

            alert_id = f"ALT-{uuid.uuid4().hex[:6].upper()}"
            alerts.append({
                "id": alert_id,
                "patient_id": patient_id,
                "timestamp": now,
                "severity": "High",
                "title": "High Physiological Deterioration Drift Detected",
                "reason": (
                    f"Twin Drift Score has reached {twin_drift_score:.1f} (High). "
                    f"Forecasted 24-hour deterioration risk is {risk_24h*100:.1f}%. "
                    f"Primary contributors: {', '.join(reasons) if reasons else 'Multivariate systemic deviation'}."
                ),
                "affected_signals": affected,
                "trend": "Acute Worsening",
                "model_risk": round(risk_24h, 3),
                "data_quality": data_quality,
                "acknowledged": False
            })

        # Elevated Severity Alert
        elif drift_level == "Elevated" or risk_24h >= 0.35:
            affected = []
            reasons = []
            for sig, dev in deviations.items():
                if abs(dev.get("z_score", 0.0)) >= 1.5:
                    affected.append(sig)
                    reasons.append(f"{dev.get('name', sig)} ({dev.get('percentage_change', 0):+.1f}%)")

            alert_id = f"ALT-{uuid.uuid4().hex[:6].upper()}"
            alerts.append({
                "id": alert_id,
                "patient_id": patient_id,
                "timestamp": now,
                "severity": "Elevated",
                "title": "Elevated Deterioration Risk Detected",
                "reason": (
                    f"Patient's physiological state has drifted into Elevated status (Score: {twin_drift_score:.1f}). "
                    f"Significant deviations observed in: {', '.join(reasons) if reasons else 'Resting HR & HRV'}."
                ),
                "affected_signals": affected,
                "trend": "Progressive Drift",
                "model_risk": round(risk_24h, 3),
                "data_quality": data_quality,
                "acknowledged": False
            })

        # Watch Alert
        elif drift_level == "Watch" or risk_24h >= 0.20:
            affected = [sig for sig, dev in deviations.items() if abs(dev.get("z_score", 0.0)) >= 1.2]
            alert_id = f"ALT-{uuid.uuid4().hex[:6].upper()}"
            alerts.append({
                "id": alert_id,
                "patient_id": patient_id,
                "timestamp": now,
                "severity": "Watch",
                "title": "Subtle Baseline Drift Detected (Early Watch)",
                "reason": (
                    f"Mild physiological drift (Score: {twin_drift_score:.1f}). "
                    f"Early autonomic or activity changes noted compared to personal normal baseline."
                ),
                "affected_signals": affected,
                "trend": "Early Deviation",
                "model_risk": round(risk_24h, 3),
                "data_quality": data_quality,
                "acknowledged": False
            })

        return alerts
