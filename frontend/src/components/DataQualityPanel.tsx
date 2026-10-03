import React from 'react';
import { ShieldCheck, AlertTriangle, CheckCircle2, Wifi, Activity, Cpu } from 'lucide-react';
import { DataQualityData } from '../services/api';

interface DataQualityPanelProps {
  dataQuality: DataQualityData | null;
}

export const DataQualityPanel: React.FC<DataQualityPanelProps> = ({ dataQuality }) => {
  if (!dataQuality) return null;

  const { overall_quality_score, quality_level, sensors, warnings } = dataQuality;

  let scoreColor = "text-emerald-400";
  let badgeColor = "bg-emerald-950 text-emerald-300 border-emerald-800";
  if (overall_quality_score < 75) {
    scoreColor = "text-amber-400";
    badgeColor = "bg-amber-950 text-amber-300 border-amber-800";
  }
  if (overall_quality_score < 50) {
    scoreColor = "text-rose-400";
    badgeColor = "bg-rose-950 text-rose-300 border-rose-800";
  }

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-lg space-y-4">
      <div className="flex items-center justify-between pb-3 border-b border-slate-800">
        <div className="flex items-center gap-2">
          <ShieldCheck className="w-5 h-5 text-sky-400" />
          <h2 className="text-sm font-bold text-white uppercase tracking-wider">
            Sensor Telemetry Integrity
          </h2>
        </div>
        <span className={`text-xs font-mono font-semibold px-2 py-0.5 rounded border ${badgeColor}`}>
          {quality_level} ({overall_quality_score}%)
        </span>
      </div>

      <p className="text-xs text-slate-400 leading-relaxed">
        The Digital Twin modulates prediction confidence based on real-time hardware telemetry uptime,
        physiological plausibility bounds, and motion artifact filters.
      </p>

      {/* Subscore Breakdown: Completeness, Consistency, Freshness */}
      <div className="grid grid-cols-3 gap-2 py-2 border-y border-slate-800/80 text-center font-mono">
        <div className="bg-slate-950/80 p-2 rounded border border-slate-800/60">
          <span className="text-[10px] text-slate-400 block uppercase">Completeness</span>
          <span className="text-sm font-bold text-white">
            {dataQuality.wearable_completeness ?? 97}%
          </span>
        </div>
        <div className="bg-slate-950/80 p-2 rounded border border-slate-800/60">
          <span className="text-[10px] text-slate-400 block uppercase">Consistency</span>
          <span className="text-sm font-bold text-white">
            {dataQuality.signal_consistency ?? 91}%
          </span>
        </div>
        <div className="bg-slate-950/80 p-2 rounded border border-slate-800/60">
          <span className="text-[10px] text-slate-400 block uppercase">Freshness</span>
          <span className="text-sm font-bold text-white">
            {dataQuality.freshness ?? 95}%
          </span>
        </div>
      </div>

      {/* Sensor Stream Integrity Matrix */}
      <div className="space-y-2 mt-2">
        {(sensors || []).map((s, idx) => (
          <div key={idx} className="bg-slate-950 p-2.5 rounded-lg border border-slate-800/80 flex items-center justify-between">
            <div className="flex items-center gap-2.5">
              <Cpu className="w-3.5 h-3.5 text-slate-500" />
              <div>
                <span className="text-xs font-semibold text-slate-200">{s.sensor_name}</span>
                {s.warning_message && (
                  <p className="text-[10px] text-amber-400 font-mono mt-0.5">⚠ {s.warning_message}</p>
                )}
              </div>
            </div>
            <div className="flex items-center gap-3 text-xs font-mono">
              <span className="text-slate-400 text-[11px]">{s.uptime_percentage}% uptime</span>
              <span className={`px-1.5 py-0.5 rounded text-[10px] ${
                s.status === "OK" ? "bg-emerald-950 text-emerald-400 border border-emerald-800" : "bg-amber-950 text-amber-400 border border-amber-800"
              }`}>
                {s.status}
              </span>
            </div>
          </div>
        ))}
      </div>

      {/* Sensor Warnings */}
      {(warnings || []).length > 0 && (
        <div className={`border rounded-lg p-3 text-xs space-y-1 ${
          overall_quality_score < 70
            ? 'bg-rose-950/60 border-rose-800/80 text-rose-200 shadow-md shadow-rose-950/40'
            : 'bg-amber-950/40 border-amber-800/60 text-amber-200'
        }`}>
          <div className="flex items-center gap-1.5 font-bold text-[11px] uppercase tracking-wide">
            <AlertTriangle className={`w-3.5 h-3.5 ${overall_quality_score < 70 ? 'text-rose-400' : 'text-amber-300'}`} />
            <span>{overall_quality_score < 70 ? 'Telemetry Degraded — AI Confidence Suppressed' : 'Telemetry Warnings'}</span>
          </div>
          {(warnings || []).map((w, idx) => (
            <p key={idx} className="text-[11px] pl-5 leading-relaxed">• {w}</p>
          ))}
        </div>
      )}
    </div>
  );
};
