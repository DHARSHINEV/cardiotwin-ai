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
  const { baseline, deviations, twin_drift_score, drift_level, risk_24h } = twinState;

  const steps = [
    {
      num: "01",
      title: "Patient Baseline",
      subtitle: "Personal N=1 Equilibrium",
      desc: "Quiescent profile: RHR 68 bpm, HRV 52 ms, Sleep 7.1h, Steps 6200.",
      badge: "68 ± 4.8 bpm",
      icon: UserCheck,
      color: "border-sky-500/50 bg-sky-950/20 text-sky-400"
    },
    {
      num: "02",
      title: "Live Telemetry",
      subtitle: "Continuous Wearable Ingestion",
      desc: "Observed state: RHR 82 bpm (+20.6%), HRV 34 ms (-34.6%), Steps 2800.",
      badge: `${deviations?.resting_hr?.current_value || 82} bpm (${deviations?.resting_hr?.z_score > 0 ? '+' : ''}${deviations?.resting_hr?.z_score} SD)`,
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
      desc: `24-hour deterioration probability: ${Math.round(risk_24h * 100)}% with 95% CI.`,
      badge: `${Math.round(risk_24h * 100)}% 24h Risk`,
      icon: AlertTriangle,
      color: risk_24h > 0.5 ? "border-rose-500/60 bg-rose-950/30 text-rose-400" : "border-amber-500/50 bg-amber-950/20 text-amber-400"
    },
    {
      num: "05",
      title: "Simulated Future",
      subtitle: "Counterfactual Trajectory",
      desc: "Restoring sleep & adherence reduces projected 24h risk from 71% to 28%.",
      badge: "Target: 28% Stabilized",
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
    </div>
  );
};
