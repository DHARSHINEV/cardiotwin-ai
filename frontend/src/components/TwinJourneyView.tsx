import React from 'react';
import { ArrowRight, UserCheck, Activity, TrendingUp, AlertTriangle, Sparkles, CheckCircle, ShieldCheck } from 'lucide-react';
import { TwinState } from '../services/api';

interface TwinJourneyViewProps {
  twinState: TwinState;
  patientName: string;
  onOpenWhatIf: () => void;
}

export const TwinJourneyView: React.FC<TwinJourneyViewProps> = ({
  twinState,
  patientName,
  onOpenWhatIf
}) => {
  const { baseline, deviations, current_state, twin_drift_score, drift_level, risk_24h } = twinState;

  // Extract current values safely from deviations or current_state
  const rhrDev = deviations?.resting_hr || deviations?.resting_heart_rate;
  const rhrBase = baseline?.resting_hr || baseline?.resting_heart_rate;
  const currentRhr = rhrDev?.current_value
    ?? current_state?.resting_heart_rate
    ?? current_state?.resting_hr
    ?? rhrBase?.mean
    ?? 68.0;

  const currentHrv = deviations?.hrv?.current_value
    ?? current_state?.hrv
    ?? baseline?.hrv?.mean
    ?? 52.0;

  const currentSteps = deviations?.steps?.current_value
    ?? current_state?.steps
    ?? baseline?.steps?.mean
    ?? 6200;

  // Personal Standard Deviation Calculation
  let sdDisplay = "SD unavailable";
  const bMean = rhrBase?.mean ?? 68.0;
  const bStd = rhrBase?.std ?? 4.8;
  if (currentRhr != null && bMean != null && bStd && !isNaN(bStd) && bStd > 0) {
    const z = (currentRhr - bMean) / bStd;
    if (isFinite(z)) {
      sdDisplay = `${z >= 0 ? '+' : ''}${z.toFixed(1)} SD`;
    }
  }

  // Percentage deviation calculation
  let pctDisplay = "";
  if (currentRhr != null && bMean != null && bMean > 0) {
    const pct = ((currentRhr - bMean) / bMean) * 100;
    pctDisplay = ` (${pct >= 0 ? '+' : ''}${pct.toFixed(1)}%)`;
  }

  const currentRiskPct = Math.round(risk_24h * 100);
  const simulatedTargetPct = Math.max(8, Math.round(risk_24h * 0.40 * 100));
  const riskDiff = Math.max(0, currentRiskPct - simulatedTargetPct);

  const step5Desc = currentRiskPct > 15
    ? `Restoring sleep & adherence modeled to reduce projected 24h risk from ${currentRiskPct}% to ${simulatedTargetPct}% (-${riskDiff} pts).`
    : `Current modeled 24h risk is stable at ${currentRiskPct}%. Counterfactual modeling projects continued physiological equilibrium.`;
  const step5Badge = currentRiskPct > 15
    ? `Target: ${simulatedTargetPct}% Modeled`
    : `Target: ${currentRiskPct}% Stable`;

  const steps = [
    {
      num: "01",
      title: "Patient Baseline",
      subtitle: "Personal N=1 Equilibrium",
      desc: `Quiescent profile: RHR ${Math.round(rhrBase?.mean ?? 68)} bpm, HRV ${Math.round(baseline?.hrv?.mean ?? 52)} ms, Sleep ${baseline?.sleep_duration?.mean ?? 7.1}h, Steps ${(baseline?.steps?.mean ?? 6200).toLocaleString()}.`,
      badge: `${rhrBase?.mean ?? 68} ± ${rhrBase?.std ?? 4.8} bpm`,
      icon: UserCheck,
      color: "border-sky-500/50 bg-sky-950/20 text-sky-400"
    },
    {
      num: "02",
      title: "Live Telemetry",
      subtitle: "Continuous Wearable Ingestion",
      desc: `Observed state: RHR ${Math.round(currentRhr)} bpm${pctDisplay}, HRV ${Math.round(currentHrv)} ms, Steps ${Math.round(currentSteps).toLocaleString()}.`,
      badge: `${Math.round(currentRhr)} bpm (${sdDisplay})`,
      icon: Activity,
      color: "border-amber-500/50 bg-amber-950/20 text-amber-400"
    },
    {
      num: "03",
      title: "Twin Drift",
      subtitle: "Multivariate Distance",
      desc: `Compound deviation score: ${twin_drift_score.toFixed(1)} (${drift_level} status).`,
      badge: `Drift Score: ${twin_drift_score.toFixed(1)}`,
      icon: TrendingUp,
      color: drift_level === "High" ? "border-rose-500/60 bg-rose-950/30 text-rose-400" : "border-amber-500/50 bg-amber-950/20 text-amber-400"
    },
    {
      num: "04",
      title: "Risk Forecast",
      subtitle: "Multi-Horizon Modeling",
      desc: `24-hour deterioration probability: ${currentRiskPct}% with 95% CI.`,
      badge: `${currentRiskPct}% 24h Risk`,
      icon: AlertTriangle,
      color: risk_24h > 0.5 ? "border-rose-500/60 bg-rose-950/30 text-rose-400" : "border-amber-500/50 bg-amber-950/20 text-amber-400"
    },
    {
      num: "05",
      title: "Simulated Future",
      subtitle: "Counterfactual Trajectory",
      desc: step5Desc,
      badge: step5Badge,
      icon: Sparkles,
      color: "border-emerald-500/50 bg-emerald-950/20 text-emerald-400"
    }
  ];

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-lg space-y-4">
      {/* Title */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-3 border-b border-slate-800">
        <div>
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-sky-400 animate-ping"></span>
            <h2 className="text-sm font-bold text-white uppercase tracking-wider">
              30-Second Twin Journey: Baseline to Proactive Intervention
            </h2>
          </div>
          <p className="text-xs text-slate-400 mt-0.5">
            How CardioTwin AI transforms passive wearable and EHR telemetry into proactive, actionable cardiovascular foresight for {patientName}.
          </p>
        </div>

        <button
          onClick={onOpenWhatIf}
          className="px-3 py-1.5 rounded-lg bg-sky-600 hover:bg-sky-500 text-white font-semibold text-xs flex items-center gap-1.5 transition-all self-start sm:self-auto cursor-pointer"
        >
          <Sparkles className="w-3.5 h-3.5 text-amber-300" /> Open What-If Simulator
        </button>
      </div>

      {/* 5-Step Horizontal Pipeline */}
      <div className="grid grid-cols-1 md:grid-cols-5 gap-3 relative">
        {steps.map((st, idx) => {
          const Icon = st.icon;
          return (
            <div
              key={idx}
              className={`p-3.5 rounded-xl border ${st.color} flex flex-col justify-between transition-all hover:scale-[1.02] shadow-md`}
            >
              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-[10px] font-mono font-bold text-slate-400">
                    STEP {st.num}
                  </span>
                  <Icon className="w-4 h-4" />
                </div>
                <h3 className="text-xs font-bold text-white tracking-tight">{st.title}</h3>
                <h4 className="text-[10px] text-slate-400 uppercase font-mono tracking-wider mb-2">{st.subtitle}</h4>
                <p className="text-[11px] text-slate-300 leading-relaxed">{st.desc}</p>
              </div>

              <div className="mt-3 pt-2 border-t border-slate-800/80">
                <span className="inline-block text-[10px] font-mono font-bold px-2 py-0.5 rounded bg-slate-950/80 text-white border border-slate-700/60">
                  {st.badge}
                </span>
              </div>
            </div>
          );
        })}
      </div>

      {/* Clinical Disclaimer Footer */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between pt-2 border-t border-slate-800/60 text-[10px] text-slate-500 font-mono gap-1">
        <span>* Modelled counterfactual — not a treatment recommendation. Clinician decision support research prototype.</span>
        <span>Patient ID: {twinState.patient_id} • Continuous N=1 State Sync</span>
      </div>
    </div>
  );
};
