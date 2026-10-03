import React from 'react';
import { Database, Activity, UserCheck, Clock, ArrowDown, Cpu, ShieldCheck, HeartPulse } from 'lucide-react';

export const MultimodalFusionDiagram: React.FC = () => {
  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-lg space-y-4">
      <div>
        <div className="flex items-center gap-2">
          <HeartPulse className="w-5 h-5 text-sky-400" />
          <h2 className="text-sm font-bold text-white uppercase tracking-wider">
            Why Multimodal Fusion? The Clinical Triad
          </h2>
        </div>
        <p className="text-xs text-slate-400 mt-1">
          EHR, continuous wearables, and personal baselines provide fundamentally non-redundant clinical dimensions.
        </p>
      </div>

      {/* 3 Pillar Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-3.5">
        <div className="bg-slate-950 p-4 rounded-xl border border-indigo-900/40 space-y-2">
          <div className="flex items-center gap-2 text-indigo-400 font-bold text-xs">
            <Database className="w-4 h-4" /> 1. Chronic Vulnerability (EHR)
          </div>
          <p className="text-[11px] text-slate-300 leading-relaxed">
            <strong>What it provides:</strong> Long-term clinical substrate (age, microvascular damage from diabetes, established hypertension, coronary plaque burden, and baseline lab biomarkers).
          </p>
          <div className="text-[10px] text-slate-500 font-mono bg-slate-900/80 p-2 rounded border border-slate-800">
            Without wearables: Blind to acute decompensation occurring between 6-month visits (AUROC: 0.487).
          </div>
        </div>

        <div className="bg-slate-950 p-4 rounded-xl border border-sky-900/40 space-y-2">
          <div className="flex items-center gap-2 text-sky-400 font-bold text-xs">
            <Activity className="w-4 h-4" /> 2. Acute Dynamic Strain (Wearables)
          </div>
          <p className="text-[11px] text-slate-300 leading-relaxed">
            <strong>What it provides:</strong> Continuous hemodynamic fluctuations, immediate nocturnal sympathovagal activation, sleep deficits, and real-time oxygenation changes.
          </p>
          <div className="text-[10px] text-slate-500 font-mono bg-slate-900/80 p-2 rounded border border-slate-800">
            Without EHR: Cannot contextualize whether a tachycardia surge is dangerous or benign exercise (AUROC: 0.648).
          </div>
        </div>

        <div className="bg-slate-950 p-4 rounded-xl border border-emerald-900/40 space-y-2">
          <div className="flex items-center gap-2 text-emerald-400 font-bold text-xs">
            <UserCheck className="w-4 h-4" /> 3. Personalized Normal (N=1 Baseline)
          </div>
          <p className="text-[11px] text-slate-300 leading-relaxed">
            <strong>What it provides:</strong> The patient's individual homeostatic bounds ($\mu \pm 2\sigma$), distinguishing personal anomalies from arbitrary population rules.
          </p>
          <div className="text-[10px] text-slate-500 font-mono bg-slate-900/80 p-2 rounded border border-slate-800">
            Combined Fusion: Extends early detection lead time from 2.1h to 14.5 hours with AUROC 0.715!
          </div>
        </div>
      </div>
    </div>
  );
};
