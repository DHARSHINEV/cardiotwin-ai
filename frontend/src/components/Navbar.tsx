import React from 'react';
import { Activity, ShieldAlert, Play, Square, Sparkles, FileText, Share2, AlertCircle } from 'lucide-react';
import { PatientSummary } from '../services/api';

interface NavbarProps {
  patients: PatientSummary[];
  selectedPatientId: string;
  onSelectPatient: (id: string) => void;
  isSimulating: boolean;
  onToggleSimulation: () => void;
  onOpenDemo: () => void;
  onOpenInterop: () => void;
  activeTab: string;
  onTabChange: (tab: string) => void;
  alertsCount: number;
}

export const Navbar: React.FC<NavbarProps> = ({
  patients,
  selectedPatientId,
  onSelectPatient,
  isSimulating,
  onToggleSimulation,
  onOpenDemo,
  onOpenInterop,
  activeTab,
  onTabChange,
  alertsCount
}) => {
  return (
    <header className="bg-slate-900 border-b border-slate-800 sticky top-0 z-40 backdrop-blur-md bg-opacity-95">
      {/* Safety Disclaimer Banner */}
      <div className="bg-sky-950/80 border-b border-sky-800/40 px-4 py-1.5 text-xs text-sky-200 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className="inline-block w-2 h-2 rounded-full bg-sky-400 animate-pulse"></span>
          <span className="font-semibold tracking-wide uppercase text-[10px] bg-sky-900/90 px-1.5 py-0.5 rounded text-sky-300 border border-sky-700">
            RESEARCH PROTOTYPE
          </span>
          <span className="text-slate-300">
            CardioTwin AI is a clinician decision support research system using synthetic physiological data. Not an autonomous diagnostic device.
          </span>
        </div>
        <div className="flex items-center gap-3 text-slate-400">
          <span>Digital Twin Challenge 2026 — Happiest Health</span>
          <button 
            onClick={onOpenInterop}
            className="hover:text-sky-300 flex items-center gap-1 font-mono text-[11px] underline underline-offset-2"
          >
            <Share2 className="w-3 h-3" /> FHIR / ABDM Interop
          </button>
        </div>
      </div>

      {/* Main Navigation Bar */}
      <div className="max-w-7xl mx-auto px-4 py-3 flex flex-wrap items-center justify-between gap-4">
        {/* Brand & Tagline */}
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-sky-600 to-indigo-600 flex items-center justify-center shadow-lg shadow-sky-500/20 border border-sky-400/30">
            <Activity className="w-6 h-6 text-white" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-lg font-bold text-white tracking-tight">CardioTwin AI</h1>
              <span className="text-[10px] uppercase font-mono tracking-wider px-2 py-0.5 rounded-full bg-emerald-950/80 text-emerald-400 border border-emerald-800">
                PoC v1.0
              </span>
            </div>
            <p className="text-xs text-slate-400 hidden sm:block">
              A living digital representation of the patient for earlier, personalized cardiovascular risk awareness.
            </p>
          </div>
        </div>

        {/* Navigation Tabs */}
        <div className="flex items-center bg-slate-950/80 rounded-lg p-1 border border-slate-800 text-xs font-medium">
          <button
            onClick={() => onTabChange('twin')}
            className={`px-3 py-1.5 rounded-md transition-all ${
              activeTab === 'twin'
                ? 'bg-sky-600 text-white shadow'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            Digital Twin
          </button>
          <button
            onClick={() => onTabChange('timeline')}
            className={`px-3 py-1.5 rounded-md transition-all ${
              activeTab === 'timeline'
                ? 'bg-sky-600 text-white shadow'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            Deterioration Timeline
          </button>
          <button
            onClick={() => onTabChange('whatif')}
            className={`px-3 py-1.5 rounded-md transition-all ${
              activeTab === 'whatif'
                ? 'bg-sky-600 text-white shadow'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            What-If Simulator
          </button>
          <button
            onClick={() => onTabChange('eval')}
            className={`px-3 py-1.5 rounded-md transition-all ${
              activeTab === 'eval'
                ? 'bg-sky-600 text-white shadow'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            Model Ablation & Eval
          </button>
          <button
            onClick={() => onTabChange('transparency')}
            className={`px-3 py-1.5 rounded-md transition-all ${
              activeTab === 'transparency'
                ? 'bg-sky-600 text-white shadow'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            Model Transparency
          </button>
          <button
            onClick={() => onTabChange('alerts')}
            className={`px-3 py-1.5 rounded-md transition-all flex items-center gap-1.5 ${
              activeTab === 'alerts'
                ? 'bg-sky-600 text-white shadow'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <span>Alerts</span>
            {alertsCount > 0 && (
              <span className="w-4 h-4 rounded-full bg-rose-500 text-white text-[10px] flex items-center justify-center font-bold">
                {alertsCount}
              </span>
            )}
          </button>
        </div>

        {/* Action Controls & Patient Switcher */}
        <div className="flex items-center gap-2.5">
          {/* Patient Selector */}
          <div className="flex items-center gap-1.5 bg-slate-950 px-2 py-1.5 rounded-lg border border-slate-800 text-xs">
            <span className="text-slate-500 text-[11px]">Patient:</span>
            <select
              value={selectedPatientId}
              onChange={(e) => onSelectPatient(e.target.value)}
              className="bg-transparent text-white font-medium focus:outline-none cursor-pointer"
            >
              {patients.map((p) => (
                <option key={p.id} value={p.id} className="bg-slate-900 text-white">
                  {p.name} ({p.id}) {p.id === 'PAT-A-1042' ? '★ Demo' : ''}
                </option>
              ))}
            </select>
          </div>

          {/* Live Simulation Button */}
          <button
            onClick={onToggleSimulation}
            className={`px-3 py-1.5 rounded-lg text-xs font-semibold flex items-center gap-1.5 transition-all shadow-sm ${
              isSimulating
                ? 'bg-amber-600 text-white hover:bg-amber-500 animate-pulse'
                : 'bg-slate-800 text-slate-200 hover:bg-slate-700 border border-slate-700'
            }`}
          >
            {isSimulating ? (
              <>
                <Square className="w-3.5 h-3.5" /> Stop Simulation
              </>
            ) : (
              <>
                <Play className="w-3.5 h-3.5 text-emerald-400" /> Start Live Simulation
              </>
            )}
          </button>

          {/* Guided Demo Mode Launcher */}
          <button
            onClick={onOpenDemo}
            className="px-3 py-1.5 rounded-lg text-xs font-semibold bg-gradient-to-r from-indigo-600 to-sky-600 hover:from-indigo-500 hover:to-sky-500 text-white flex items-center gap-1.5 shadow-md shadow-indigo-600/20 border border-indigo-400/30"
          >
            <Sparkles className="w-3.5 h-3.5 text-amber-300" /> Demo Mode
          </button>
        </div>
      </div>
    </header>
  );
};
