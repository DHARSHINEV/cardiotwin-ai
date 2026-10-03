import React from 'react';
import { Play, Square, FastForward, RotateCcw, AlertTriangle, CheckCircle, TrendingUp, ShieldCheck } from 'lucide-react';

interface LiveSimulationControlProps {
  simulationState: string;
  onSelectState: (state: string) => void;
  onStepSimulation: () => void;
  isSimulating: boolean;
  onToggleSimulating: () => void;
  onResetPatient: () => void;
  lastUpdated: string;
}

export const LiveSimulationControl: React.FC<LiveSimulationControlProps> = ({
  simulationState,
  onSelectState,
  onStepSimulation,
  isSimulating,
  onToggleSimulating,
  onResetPatient,
  lastUpdated
}) => {
  const states = [
    {
      id: 'Normal',
      name: 'Normal State',
      desc: 'Quiescent telemetry tracking within personal baseline bounds.',
      icon: CheckCircle,
      activeColor: 'bg-emerald-600 text-white border-emerald-400 shadow-emerald-500/20'
    },
    {
      id: 'Gradual deterioration',
      name: 'Gradual Deterioration',
      desc: 'Progressive sympathovagal drift: HR climbs, HRV attenuates, sleep deficit.',
      icon: TrendingUp,
      activeColor: 'bg-amber-600 text-white border-amber-400 shadow-amber-500/20'
    },
    {
      id: 'Acute anomaly',
      name: 'Acute Anomaly',
      desc: 'Sudden tachycardia crisis, tachypnea, and nocturnal oxygen desaturation.',
      icon: AlertTriangle,
      activeColor: 'bg-rose-600 text-white border-rose-400 shadow-rose-500/20'
    },
    {
      id: 'Recovery',
      name: 'Recovery',
      desc: 'Gradual stabilization returning toward patient personal baseline.',
      icon: ShieldCheck,
      activeColor: 'bg-teal-600 text-white border-teal-400 shadow-teal-500/20'
    },
    {
      id: 'Sensor Failure / Artifact',
      name: 'Sensor Failure / Artifact',
      desc: 'Hardware artifact, missing telemetry & dropped packets. AI suppresses confidence.',
      icon: AlertTriangle,
      activeColor: 'bg-purple-600 text-white border-purple-400 shadow-purple-500/20'
    }
  ];

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-lg">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-slate-800">
        <div>
          <div className="flex items-center gap-2">
            <h3 className="text-sm font-bold text-white uppercase tracking-wider">Live Telemetry Simulator</h3>
            <span className={`inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full text-[10px] font-mono font-medium ${
              isSimulating ? 'bg-amber-950 text-amber-300 border border-amber-800 animate-pulse' : 'bg-slate-800 text-slate-400 border border-slate-700'
            }`}>
              <span className={`w-1.5 h-1.5 rounded-full ${isSimulating ? 'bg-amber-400' : 'bg-slate-500'}`}></span>
              {isSimulating ? 'STREAM ACTIVE (4s Loop)' : 'STREAM PAUSED'}
            </span>
          </div>
          <p className="text-xs text-slate-400 mt-0.5">
            Injects real-time synthetic wearable events to observe dynamic Twin Drift and risk recalculations.
          </p>
        </div>

        {/* Action Controls */}
        <div className="flex items-center gap-2">
          <button
            onClick={onToggleSimulating}
            className={`px-3 py-1.5 rounded-lg text-xs font-semibold flex items-center gap-1.5 transition-all shadow ${
              isSimulating
                ? 'bg-amber-600 hover:bg-amber-500 text-white animate-pulse'
                : 'bg-sky-600 hover:bg-sky-500 text-white'
            }`}
          >
            {isSimulating ? <Square className="w-3.5 h-3.5" /> : <Play className="w-3.5 h-3.5" />}
            {isSimulating ? 'Stop Timer' : 'Start Live Timer'}
          </button>

          <button
            onClick={onStepSimulation}
            className="px-3 py-1.5 rounded-lg text-xs font-semibold bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 flex items-center gap-1.5 transition-all"
            title="Advance telemetry by 1 simulated hour"
          >
            <FastForward className="w-3.5 h-3.5 text-sky-400" />
            Step +1h
          </button>

          <button
            onClick={onResetPatient}
            className="px-2.5 py-1.5 rounded-lg text-xs font-medium bg-slate-950 hover:bg-slate-800 text-slate-400 hover:text-slate-200 border border-slate-800 transition-all"
            title="Reset Patient to Healthy Baseline"
          >
            <RotateCcw className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {/* State Selector Buttons */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 mt-4">
        {states.map((st) => {
          const Icon = st.icon;
          const isSelected = simulationState === st.id;
          return (
            <button
              key={st.id}
              onClick={() => onSelectState(st.id)}
              className={`text-left p-3 rounded-lg border transition-all ${
                isSelected
                  ? `${st.activeColor} border shadow-md`
                  : 'bg-slate-950/70 border-slate-800 hover:border-slate-700 text-slate-300'
              }`}
            >
              <div className="flex items-center gap-2 mb-1">
                <Icon className={`w-4 h-4 ${isSelected ? 'text-white' : 'text-slate-400'}`} />
                <span className="text-xs font-bold">{st.name}</span>
              </div>
              <p className={`text-[11px] leading-relaxed ${isSelected ? 'text-white/90' : 'text-slate-400'}`}>
                {st.desc}
              </p>
            </button>
          );
        })}
      </div>

      {/* Telemetry Footer Info */}
      <div className="flex items-center justify-between text-[11px] text-slate-500 font-mono mt-3 pt-2 border-t border-slate-800/60">
        <span>Current Operational Mode: <strong className="text-slate-300">{simulationState}</strong></span>
        <span>Last Telemetry Sync: {new Date(lastUpdated).toLocaleTimeString()}</span>
      </div>
    </div>
  );
};
