import React from 'react';
import { Heart, Activity, Moon, Footprints, Droplets, Wind, Zap, Info } from 'lucide-react';
import { TwinState } from '../services/api';

interface PersonalBaselineCardProps {
  twinState: TwinState;
  patientName: string;
}

export const PersonalBaselineCard: React.FC<PersonalBaselineCardProps> = ({ twinState, patientName }) => {
  const { baseline, deviations, current_state } = twinState;

  const signals = [
    {
      key: 'resting_hr',
      label: 'Resting Heart Rate',
      icon: Heart,
      color: 'text-rose-400',
      bgColor: 'bg-rose-950/40 border-rose-800/40',
      unit: 'bpm'
    },
    {
      key: 'hrv',
      label: 'HRV (RMSSD)',
      icon: Activity,
      color: 'text-indigo-400',
      bgColor: 'bg-indigo-950/40 border-indigo-800/40',
      unit: 'ms'
    },
    {
      key: 'sleep_duration',
      label: 'Sleep Duration',
      icon: Moon,
      color: 'text-purple-400',
      bgColor: 'bg-purple-950/40 border-purple-800/40',
      unit: 'hrs'
    },
    {
      key: 'steps',
      label: 'Daily Steps',
      icon: Footprints,
      color: 'text-emerald-400',
      bgColor: 'bg-emerald-950/40 border-emerald-800/40',
      unit: 'steps'
    },
    {
      key: 'spo2',
      label: 'Oxygen Saturation',
      icon: Droplets,
      color: 'text-sky-400',
      bgColor: 'bg-sky-950/40 border-sky-800/40',
      unit: '%'
    },
    {
      key: 'respiratory_rate',
      label: 'Respiratory Rate',
      icon: Wind,
      color: 'text-teal-400',
      bgColor: 'bg-teal-950/40 border-teal-800/40',
      unit: 'br/min'
    },
    {
      key: 'stress_index',
      label: 'Autonomic Stress',
      icon: Zap,
      color: 'text-amber-400',
      bgColor: 'bg-amber-950/40 border-amber-800/40',
      unit: 'idx'
    }
  ];

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-lg">
      {/* Header and Clinical Concept Callout */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-4 border-b border-slate-800">
        <div>
          <div className="flex items-center gap-2">
            <h2 className="text-base font-bold text-white tracking-tight">Personal Baseline & Physiological Deviations</h2>
            <span className="text-[11px] font-mono px-2 py-0.5 rounded bg-sky-950 text-sky-300 border border-sky-800">
              N=1 Individualized Model
            </span>
          </div>
          <p className="text-xs text-slate-400 mt-0.5">
            Calibrated over quiescent nocturnal intervals. Compares observed readings to {patientName}'s established normal distribution ($\mu \pm 2\sigma$).
          </p>
        </div>

        {/* The Core Differentiator Callout Box */}
        <div className="bg-slate-950/90 border border-sky-800/50 rounded-lg p-2.5 max-w-md text-xs text-sky-200 flex items-start gap-2">
          <Info className="w-4 h-4 text-sky-400 shrink-0 mt-0.5" />
          <div>
            <span className="font-semibold text-white">Digital Twin Principle: </span>
            <span>
              "82 bpm may be acceptable for an arbitrary person, but for {patientName}, 82 bpm represents a significant <strong className="text-amber-300">+20.6% (+2.8 SD)</strong> deviation from their personal 68 bpm baseline."
            </span>
          </div>
        </div>
      </div>

      {/* Grid of Signals */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3.5 mt-4">
        {signals.map((sig) => {
          const bInfo = baseline[sig.key];
          const devInfo = deviations[sig.key];
          if (!bInfo || !devInfo) return null;

          const IconComponent = sig.icon;
          const currentVal = devInfo.current_value;
          const meanVal = bInfo.mean;
          const zScore = devInfo.z_score;
          const pct = devInfo.percentage_change;

          // Status Badge styling
          let statusBadge = "bg-emerald-950 text-emerald-300 border-emerald-800";
          if (devInfo.status === "critical") {
            statusBadge = "bg-rose-950 text-rose-300 border-rose-800 animate-pulse";
          } else if (devInfo.status === "elevated" || devInfo.status === "depressed") {
            statusBadge = "bg-amber-950 text-amber-300 border-amber-800";
          }

          // Calculate visual needle position inside 4 SD range
          const lower = bInfo.lower_bound;
          const upper = bInfo.upper_bound;
          const span = upper - lower || 1;
          const normalizedPos = Math.max(0, Math.min(100, ((currentVal - lower) / span) * 100));

          return (
            <div
              key={sig.key}
              className={`rounded-lg p-3.5 border transition-all ${sig.bgColor} hover:border-slate-600`}
            >
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2">
                  <IconComponent className={`w-4 h-4 ${sig.color}`} />
                  <span className="text-xs font-semibold text-slate-200">{sig.label}</span>
                </div>
                <span className={`text-[10px] font-mono px-1.5 py-0.5 rounded border ${statusBadge}`}>
                  {zScore > 0 ? `+${zScore} SD` : `${zScore} SD`}
                </span>
              </div>

              {/* Observed Value vs Baseline */}
              <div className="flex items-baseline justify-between mt-1">
                <div>
                  <span className="text-xl font-bold text-white tracking-tight">
                    {sig.key === 'steps' ? Math.round(currentVal).toLocaleString() : currentVal}
                  </span>
                  <span className="text-xs text-slate-400 ml-1">{sig.unit}</span>
                </div>
                <div className="text-right">
                  <span className={`text-xs font-semibold ${pct > 0 ? (['resting_hr', 'respiratory_rate', 'stress_index'].includes(sig.key) ? 'text-rose-400' : 'text-emerald-400') : (['hrv', 'sleep_duration', 'steps', 'spo2'].includes(sig.key) ? 'text-rose-400' : 'text-emerald-400')}`}>
                    {pct > 0 ? `+${pct}%` : `${pct}%`}
                  </span>
                  <div className="text-[10px] text-slate-400 font-mono">
                    Base: {sig.key === 'steps' ? Math.round(meanVal).toLocaleString() : meanVal}
                  </div>
                </div>
              </div>

              {/* Visual Range Indicator Bar */}
              <div className="mt-3">
                <div className="flex justify-between text-[10px] text-slate-500 font-mono mb-1">
                  <span>95% Min: {sig.key === 'steps' ? Math.round(lower) : lower}</span>
                  <span>95% Max: {sig.key === 'steps' ? Math.round(upper) : upper}</span>
                </div>
                <div className="h-2 w-full bg-slate-800 rounded-full relative overflow-hidden border border-slate-700">
                  {/* Personal Normal Zone */}
                  <div className="absolute top-0 bottom-0 left-[20%] right-[20%] bg-sky-500/20 rounded"></div>
                  {/* Current Reading Marker Needle */}
                  <div
                    className="absolute top-0 bottom-0 w-1.5 bg-white shadow-md shadow-white/50 rounded-full transition-all duration-500"
                    style={{ left: `calc(${normalizedPos}% - 3px)` }}
                  ></div>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
