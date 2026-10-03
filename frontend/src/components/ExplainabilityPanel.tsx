import React from 'react';
import { Eye, TrendingUp, ShieldAlert, BarChart3, AlertCircle } from 'lucide-react';
import { TopContributor } from '../services/api';

interface ExplainabilityPanelProps {
  contributors: TopContributor[];
  driftScore: number;
  driftLevel: string;
}

export const ExplainabilityPanel: React.FC<ExplainabilityPanelProps> = ({
  contributors,
  driftScore,
  driftLevel
}) => {
  const safeContributors = contributors || [];

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-lg space-y-4">
      <div className="flex items-center justify-between pb-3 border-b border-slate-800">
        <div className="flex items-center gap-2">
          <Eye className="w-5 h-5 text-sky-400" />
          <h2 className="text-sm font-bold text-white uppercase tracking-wider">
            Explainable AI Attribution Layer
          </h2>
        </div>
        <span className="text-[11px] font-mono text-slate-400">
          SHAP-Aligned Sensitivity Decomposition
        </span>
      </div>

      <p className="text-xs text-slate-400 leading-relaxed">
        CardioTwin AI strictly decomposes risk forecasts into exact physiological drivers.
        Each attribution weight directly corresponds to the magnitude of the signal's personal baseline deviation.
      </p>

      {/* Feature Attribution List */}
      <div className="space-y-2.5 mt-2">
        {safeContributors.length === 0 ? (
          <div className="bg-slate-950 p-4 rounded-lg border border-slate-800/80 text-xs text-slate-400 text-center font-mono">
            All wearable telemetry is currently within personal baseline equilibrium. No acute adverse risk contributors detected.
          </div>
        ) : (
          safeContributors.map((contrib, idx) => {
            const isRisk = contrib.direction === "increased_risk";
            const maxImp = safeContributors[0]?.importance || 1.0;
            const widthPct = Math.min(100, Math.max(10, (contrib.importance / maxImp) * 100));

          return (
            <div key={idx} className="bg-slate-950 p-3 rounded-lg border border-slate-800/80">
              <div className="flex items-center justify-between mb-1.5">
                <div className="flex items-center gap-2">
                  <span className="w-5 h-5 rounded-full bg-slate-900 border border-slate-700 text-[10px] font-mono font-bold flex items-center justify-center text-slate-300">
                    {idx + 1}
                  </span>
                  <span className="text-xs font-bold text-slate-200">{contrib.name}</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className={`text-[10px] font-mono px-2 py-0.5 rounded border ${
                    isRisk ? 'bg-rose-950 text-rose-300 border-rose-800' : 'bg-emerald-950 text-emerald-300 border-emerald-800'
                  }`}>
                    {isRisk ? 'Increased Risk (+)' : 'Protective (-)'}
                  </span>
                  <span className="text-xs font-mono font-semibold text-slate-300">
                    Weight: {contrib.importance.toFixed(2)}
                  </span>
                </div>
              </div>

              {/* Attribution Impact Bar */}
              <div className="w-full bg-slate-900 rounded-full h-1.5 my-2 overflow-hidden border border-slate-800">
                <div
                  className={`h-full rounded-full transition-all duration-500 ${
                    isRisk ? 'bg-gradient-to-r from-amber-500 to-rose-500' : 'bg-emerald-500'
                  }`}
                  style={{ width: `${widthPct}%` }}
                ></div>
              </div>

              {/* Plain English Clinical Statement */}
              <p className="text-[11px] text-slate-300 leading-relaxed font-sans">
                • {contrib.explanation}
              </p>
            </div>
          );
        })
      )}
      </div>
    </div>
  );
};
