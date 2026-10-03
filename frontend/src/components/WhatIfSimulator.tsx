import React, { useState } from 'react';
import { Sliders, Play, RefreshCw, AlertCircle, TrendingDown, Sparkles, CheckCircle2 } from 'lucide-react';
import { ResponsiveContainer, LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid, Legend } from 'recharts';
import { WhatIfResult, TwinState, api } from '../services/api';

interface WhatIfSimulatorProps {
  patientId: string;
  twinState?: TwinState | null;
  initialResult?: WhatIfResult | null;
}

export const WhatIfSimulator: React.FC<WhatIfSimulatorProps> = ({ patientId, twinState, initialResult }) => {
  const [sleepHours, setSleepHours] = useState<number>(7.2);
  const [activityLevel, setActivityLevel] = useState<string>('moderate');
  const [medAdherence, setMedAdherence] = useState<number>(95);
  const [stressReduction, setStressReduction] = useState<number>(40);
  const [loading, setLoading] = useState<boolean>(false);
  const [result, setResult] = useState<WhatIfResult | null>(initialResult || null);

  const currentRisk24h = twinState?.risk_24h ?? 0.08;
  const currentRisk6h = twinState?.risk_6h ?? 0.05;
  const currentRisk72h = twinState?.risk_72h ?? 0.12;
  const currentDrift = twinState?.twin_drift_score ?? 12.4;

  const handleSimulate = async () => {
    setLoading(true);
    try {
      const data = await api.runWhatIf({
        patient_id: patientId,
        scenario_name: 'Clinician Tailored Optimization',
        simulated_sleep_hours: sleepHours,
        simulated_activity_level: activityLevel,
        simulated_medication_adherence: medAdherence / 100.0,
        simulated_stress_reduction: stressReduction
      });
      setResult(data);
    } catch (err) {
      console.error('Failed to run simulation', err);
    } finally {
      setLoading(false);
    }
  };

  const defaultChartData = [
    { name: 'Now', hours: '0h', baselineRisk: Math.round(currentRisk6h * 0.85 * 100), simulatedRisk: Math.round(currentRisk6h * 0.85 * 100), projectedDrift: Math.round(currentDrift) },
    { name: '6h', hours: '6h', baselineRisk: Math.round(currentRisk6h * 100), simulatedRisk: Math.round(currentRisk6h * 100), projectedDrift: Math.round(currentDrift) },
    { name: '24h', hours: '24h', baselineRisk: Math.round(currentRisk24h * 100), simulatedRisk: Math.round(currentRisk24h * 100), projectedDrift: Math.round(currentDrift) },
    { name: '72h', hours: '72h', baselineRisk: Math.round(currentRisk72h * 100), simulatedRisk: Math.round(currentRisk72h * 100), projectedDrift: Math.round(currentDrift) }
  ];

  const chartData = result?.trajectories.map((t) => ({
    name: t.horizon,
    hours: `${t.hours_from_now}h`,
    baselineRisk: Math.round(t.baseline_risk * 100),
    simulatedRisk: Math.round(t.simulated_risk * 100),
    projectedDrift: Math.round(t.projected_drift)
  })) || defaultChartData;

  const current24hPct = result
    ? Math.round((result.trajectories.find(t => t.horizon === '24h')?.baseline_risk ?? currentRisk24h) * 100)
    : Math.round(currentRisk24h * 100);

  const counterfactual24hPct = result
    ? Math.round((result.trajectories.find(t => t.horizon === '24h')?.simulated_risk ?? currentRisk24h) * 100)
    : current24hPct;

  const changePts = current24hPct - counterfactual24hPct;

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-lg space-y-5">
      {/* Header with Mandatory Clinical Disclaimer */}
      <div>
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-slate-800">
          <div>
            <div className="flex items-center gap-2">
              <Sliders className="w-5 h-5 text-indigo-400" />
              <h2 className="text-base font-bold text-white tracking-tight">What-If Digital Twin Scenario Simulator</h2>
              <span className="text-[10px] font-mono uppercase px-2 py-0.5 rounded bg-indigo-950 text-indigo-300 border border-indigo-800">
                Bi-Directional Trajectory Modeling
              </span>
            </div>
            <p className="text-xs text-slate-400 mt-1">
              Adjust behavioral and therapeutic levers to project counterfactual risk trajectories over 6h, 24h, and 72h.
            </p>
          </div>

          <div className="bg-amber-950/80 border border-amber-700/60 rounded-lg px-3 py-1.5 text-xs text-amber-200 flex items-center gap-2">
            <AlertCircle className="w-4 h-4 text-amber-400 shrink-0" />
            <span className="font-semibold tracking-wide uppercase text-[10px]">
              Modelled counterfactual — not a treatment recommendation.
            </span>
          </div>
        </div>
      </div>

      {/* 24-Hour Counterfactual Impact Summary (Phase 11 & Consistency Requirements) */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 p-3.5 bg-slate-950/80 rounded-xl border border-slate-800 font-mono text-center">
        <div className="bg-slate-900/80 p-2.5 rounded-lg border border-slate-800/80">
          <span className="text-[10px] text-slate-400 block uppercase">Current Modeled 24h Risk</span>
          <span className="text-xl font-bold text-slate-200">{current24hPct}%</span>
        </div>
        <div className="bg-slate-900/80 p-2.5 rounded-lg border border-slate-800/80">
          <span className="text-[10px] text-slate-400 block uppercase">Counterfactual Modeled 24h Risk</span>
          <span className={`text-xl font-bold ${counterfactual24hPct < current24hPct ? 'text-emerald-400' : 'text-slate-200'}`}>
            {counterfactual24hPct}%
          </span>
        </div>
        <div className="bg-slate-900/80 p-2.5 rounded-lg border border-slate-800/80">
          <span className="text-[10px] text-slate-400 block uppercase">Modeled Change</span>
          <span className={`text-xl font-bold ${changePts > 0 ? 'text-emerald-400' : changePts < 0 ? 'text-rose-400' : 'text-slate-400'}`}>
            {changePts > 0 ? `-${changePts} percentage points` : changePts < 0 ? `+${Math.abs(changePts)} percentage points` : '0 percentage points'}
          </span>
        </div>
      </div>

      {/* Simulator Knobs and Interactive Sliders */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 p-4 rounded-xl bg-slate-950 border border-slate-800">
        {/* Knob 1: Sleep Hours */}
        <div className="space-y-1.5">
          <div className="flex justify-between text-xs font-semibold">
            <span className="text-slate-300">Simulated Sleep Duration</span>
            <span className="text-sky-400 font-mono">{sleepHours} hrs</span>
          </div>
          <input
            type="range"
            min="4.0"
            max="9.0"
            step="0.2"
            value={sleepHours}
            onChange={(e) => setSleepHours(parseFloat(e.target.value))}
            className="w-full accent-sky-500 cursor-pointer h-1.5 bg-slate-800 rounded-lg"
          />
          <div className="flex justify-between text-[10px] text-slate-500 font-mono">
            <span>4.0h (Deficit)</span>
            <span>7.1h (Baseline)</span>
            <span>9.0h</span>
          </div>
        </div>

        {/* Knob 2: Medication Adherence */}
        <div className="space-y-1.5">
          <div className="flex justify-between text-xs font-semibold">
            <span className="text-slate-300">Medication Adherence</span>
            <span className="text-emerald-400 font-mono">{medAdherence}%</span>
          </div>
          <input
            type="range"
            min="50"
            max="100"
            step="5"
            value={medAdherence}
            onChange={(e) => setMedAdherence(parseInt(e.target.value))}
            className="w-full accent-emerald-500 cursor-pointer h-1.5 bg-slate-800 rounded-lg"
          />
          <div className="flex justify-between text-[10px] text-slate-500 font-mono">
            <span>50% (Poor)</span>
            <span>70% (Current)</span>
            <span>100% (Strict)</span>
          </div>
        </div>

        {/* Knob 3: Physical Activity */}
        <div className="space-y-1.5">
          <div className="flex justify-between text-xs font-semibold">
            <span className="text-slate-300">Physical Mobilization</span>
            <span className="text-indigo-400 uppercase text-[11px] font-mono">{activityLevel}</span>
          </div>
          <select
            value={activityLevel}
            onChange={(e) => setActivityLevel(e.target.value)}
            className="w-full bg-slate-900 border border-slate-700 text-slate-200 text-xs rounded-lg p-1.5 focus:outline-none focus:border-indigo-500"
          >
            <option value="sedentary">Sedentary (&lt; 2,500 steps)</option>
            <option value="light">Light Activity (3,500 steps)</option>
            <option value="moderate">Moderate Exercise (6,200 steps)</option>
            <option value="active">Active Recovery (&gt; 8,000 steps)</option>
          </select>
        </div>

        {/* Knob 4: Autonomic Stress Reduction */}
        <div className="space-y-1.5">
          <div className="flex justify-between text-xs font-semibold">
            <span className="text-slate-300">Stress Reduction Effort</span>
            <span className="text-purple-400 font-mono">-{stressReduction}%</span>
          </div>
          <input
            type="range"
            min="0"
            max="80"
            step="10"
            value={stressReduction}
            onChange={(e) => setStressReduction(parseInt(e.target.value))}
            className="w-full accent-purple-500 cursor-pointer h-1.5 bg-slate-800 rounded-lg"
          />
          <div className="flex justify-between text-[10px] text-slate-500 font-mono">
            <span>0% (None)</span>
            <span>40% (Target)</span>
            <span>80% (Max)</span>
          </div>
        </div>
      </div>

      {/* Execute Simulation CTA */}
      <div className="flex justify-end">
        <button
          onClick={handleSimulate}
          disabled={loading}
          className="px-5 py-2 rounded-lg bg-gradient-to-r from-sky-600 to-indigo-600 hover:from-sky-500 hover:to-indigo-500 text-white font-semibold text-xs flex items-center gap-2 shadow-lg shadow-sky-600/20 disabled:opacity-50 transition-all cursor-pointer"
        >
          {loading ? (
            <>
              <RefreshCw className="w-4 h-4 animate-spin" /> Simulating Trajectories...
            </>
          ) : (
            <>
              <Play className="w-4 h-4" /> Run What-If Projection
            </>
          )}
        </button>
      </div>

      {/* Trajectory Comparison Chart */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-5 pt-2">
        <div className="lg:col-span-2 bg-slate-950/70 p-4 rounded-xl border border-slate-800">
          <div className="flex items-center justify-between mb-3">
            <div>
              <h3 className="text-xs font-bold text-slate-200 uppercase tracking-wider">
                Multi-Horizon Risk Divergence
              </h3>
              <p className="text-[11px] text-slate-400">
                Current Unmitigated Trajectory vs. Simulated Intervention Trajectory
              </p>
            </div>
            <div className="flex items-center gap-4 text-xs font-mono">
              <span className="flex items-center gap-1.5 text-rose-400">
                <span className="w-2.5 h-2.5 rounded-full bg-rose-500"></span> Unmitigated Trajectory
              </span>
              <span className="flex items-center gap-1.5 text-emerald-400">
                <span className="w-2.5 h-2.5 rounded-full bg-emerald-500"></span> Simulated Intervention
              </span>
            </div>
          </div>

          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={chartData} margin={{ top: 10, right: 20, left: 0, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis dataKey="name" stroke="#64748b" textAnchor="middle" />
                <YAxis unit="%" stroke="#64748b" domain={[0, 100]} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px' }}
                  formatter={(val: any) => [`${val}%`, '']}
                />
                <Line
                  type="monotone"
                  dataKey="baselineRisk"
                  name="Current Risk"
                  stroke="#ef4444"
                  strokeWidth={3}
                  dot={{ r: 5, fill: '#ef4444' }}
                />
                <Line
                  type="monotone"
                  dataKey="simulatedRisk"
                  name="Simulated Risk"
                  stroke="#10b981"
                  strokeWidth={3}
                  strokeDasharray="4 4"
                  dot={{ r: 5, fill: '#10b981' }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Counterfactual Insights Box */}
        <div className="bg-slate-950/70 p-4 rounded-xl border border-slate-800 flex flex-col justify-between">
          <div>
            <div className="flex items-center gap-2 mb-2">
              <Sparkles className="w-4 h-4 text-amber-300" />
              <h3 className="text-xs font-bold text-white uppercase tracking-wider">
                Counterfactual AI Explanation
              </h3>
            </div>
            <p className="text-[11px] text-slate-400 mb-3">
              "What would need to change for {patientId} to shift into a stable cardiovascular zone?"
            </p>

            <div className="space-y-2.5">
              {result?.counterfactual_insights.map((insight, idx) => (
                <div key={idx} className="flex items-start gap-2 bg-slate-900/90 p-2.5 rounded-lg border border-slate-800 text-xs text-slate-200">
                  <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
                  <span className="leading-relaxed">{insight}</span>
                </div>
              )) || (
                <div className="text-xs text-slate-400 italic">
                  Run simulation to generate patient-specific counterfactual interventions.
                </div>
              )}
            </div>
          </div>

          <div className="mt-4 pt-3 border-t border-slate-800/80 text-[11px] text-slate-500">
            <span className="text-slate-400 font-semibold">Clinician note: </span>
            This tool explores theoretical physiological response curves. Never substitute for patient-guided clinical management.
          </div>
        </div>
      </div>
    </div>
  );
};
