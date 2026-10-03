import React from 'react';
import { Clock, TrendingUp, AlertTriangle, CheckCircle, ShieldAlert, Heart, Activity } from 'lucide-react';
import { TimelinePoint } from '../services/api';
import { ResponsiveContainer, AreaChart, Area, XAxis, YAxis, Tooltip, CartesianGrid } from 'recharts';

interface DeteriorationTimelineViewProps {
  timeline: TimelinePoint[];
  patientId: string;
}

export const DeteriorationTimelineView: React.FC<DeteriorationTimelineViewProps> = ({ timeline, patientId }) => {
  // Pre-configured narrative milestone steps matching Section 19
  const milestones = [
    {
      time: "08:00",
      title: "Normal Baseline",
      status: "Normal",
      hr: "68 bpm",
      hrv: "52 ms",
      desc: "Quiescent baseline state. Telemetry aligns tightly within 95% confidence intervals.",
      badgeColor: "bg-emerald-950 text-emerald-300 border-emerald-800"
    },
    {
      time: "10:00",
      title: "Resting HR Elevation",
      status: "Watch",
      hr: "72 bpm",
      hrv: "48 ms",
      desc: "Subtle upward drift in nocturnal resting HR (+4 bpm). Sympathetic tone beginning to elevate.",
      badgeColor: "bg-amber-950 text-amber-300 border-amber-800"
    },
    {
      time: "12:00",
      title: "Autonomic HRV Decline",
      status: "Watch",
      hr: "75 bpm",
      hrv: "43 ms",
      desc: "Vagal withdrawal detected. HRV RMSSD drops below 45 ms, indicating diminished heart rate variability.",
      badgeColor: "bg-amber-950 text-amber-300 border-amber-800"
    },
    {
      time: "14:00",
      title: "Compounding Sleep Deficit",
      status: "Elevated",
      hr: "77 bpm",
      hrv: "39 ms",
      desc: "Patient logs 5.4h sleep (1.7h deficit from baseline). Ambulatory step count drops by 45%.",
      badgeColor: "bg-orange-950 text-orange-300 border-orange-800"
    },
    {
      time: "16:00",
      title: "Twin Drift Acceleration",
      status: "Elevated",
      hr: "80 bpm",
      hrv: "36 ms",
      desc: "Twin Drift Score reaches 62.1. System detects multivariate departure from individual homeostatic equilibrium.",
      badgeColor: "bg-orange-950 text-orange-300 border-orange-800"
    },
    {
      time: "18:00",
      title: "Risk Threshold Crossed",
      status: "High",
      hr: "82 bpm",
      hrv: "34 ms",
      desc: "Resting HR reaches 82 bpm (+20.6%), HRV at 34 ms (-34.6%). Forecasted 24h risk crosses 70% threshold. Automated alert dispatched.",
      badgeColor: "bg-rose-950 text-rose-300 border-rose-800 animate-pulse"
    }
  ];

  const chartData = timeline.map((pt) => ({
    time: pt.time_str,
    hr: pt.resting_hr,
    hrv: pt.hrv,
    drift: pt.twin_drift_score
  }));

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-lg space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-slate-800">
        <div>
          <div className="flex items-center gap-2">
            <Clock className="w-5 h-5 text-sky-400" />
            <h2 className="text-base font-bold text-white tracking-tight">
              Chronological Physiological Deterioration Sequence
            </h2>
            <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-sky-950 text-sky-300 border border-sky-800">
              24-Hour Longitudinal Tracker
            </span>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Visualizing how subtle autonomic deviations compound over hours into an elevated cardiovascular deterioration state.
          </p>
        </div>
      </div>

      {/* Visual Chart: Drift Score & Heart Rate progression */}
      <div className="bg-slate-950/70 p-4 rounded-xl border border-slate-800">
        <div className="flex items-center justify-between mb-2">
          <span className="text-xs font-bold text-slate-300 uppercase tracking-wider">
            Twin Drift Score & Resting HR Progression
          </span>
          <div className="flex items-center gap-4 text-xs font-mono">
            <span className="flex items-center gap-1.5 text-amber-400">
              <span className="w-2.5 h-2.5 rounded-full bg-amber-500"></span> Twin Drift Score (0-100)
            </span>
            <span className="flex items-center gap-1.5 text-rose-400">
              <span className="w-2.5 h-2.5 rounded-full bg-rose-500"></span> Resting HR (bpm)
            </span>
          </div>
        </div>

        <div className="h-56 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={chartData} margin={{ top: 10, right: 10, left: -10, bottom: 0 }}>
              <defs>
                <linearGradient id="driftGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#f59e0b" stopOpacity={0.4} />
                  <stop offset="95%" stopColor="#f59e0b" stopOpacity={0.0} />
                </linearGradient>
                <linearGradient id="hrGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#ef4444" stopOpacity={0.3} />
                  <stop offset="95%" stopColor="#ef4444" stopOpacity={0.0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
              <XAxis dataKey="time" stroke="#64748b" />
              <YAxis stroke="#64748b" domain={[20, 100]} />
              <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px' }} />
              <Area type="monotone" dataKey="drift" stroke="#f59e0b" strokeWidth={2} fillOpacity={1} fill="url(#driftGradient)" name="Twin Drift" />
              <Area type="monotone" dataKey="hr" stroke="#ef4444" strokeWidth={2} fillOpacity={1} fill="url(#hrGradient)" name="Resting HR" />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Narrative Milestone Progression Cards */}
      <div className="relative pl-6 border-l-2 border-slate-800 space-y-6">
        {milestones.map((m, idx) => (
          <div key={idx} className="relative group">
            {/* Timeline bullet icon */}
            <div className="absolute -left-[31px] top-1.5 w-4 h-4 rounded-full bg-slate-900 border-2 border-sky-400 group-hover:scale-125 transition-all"></div>

            <div className="bg-slate-950 p-4 rounded-xl border border-slate-800/80 hover:border-slate-700 transition-all">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-2">
                <div className="flex items-center gap-2">
                  <span className="font-mono text-xs font-bold text-sky-400 bg-sky-950/80 px-2 py-0.5 rounded border border-sky-800">
                    {m.time}
                  </span>
                  <h3 className="text-sm font-bold text-white">{m.title}</h3>
                </div>
                <div className="flex items-center gap-3">
                  <div className="flex items-center gap-2 text-xs font-mono text-slate-300">
                    <span className="text-rose-400 font-semibold">{m.hr}</span>
                    <span className="text-slate-600">|</span>
                    <span className="text-indigo-400 font-semibold">{m.hrv}</span>
                  </div>
                  <span className={`text-[10px] font-mono px-2 py-0.5 rounded border ${m.badgeColor}`}>
                    {m.status}
                  </span>
                </div>
              </div>
              <p className="text-xs text-slate-300 leading-relaxed">{m.desc}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
