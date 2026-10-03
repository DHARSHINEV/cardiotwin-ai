import React, { useState } from 'react';
import { X, Sparkles, ChevronRight, ChevronLeft, CheckCircle2, Play, AlertTriangle } from 'lucide-react';
import { DemoStage, api } from '../services/api';

interface DemoModeModalProps {
  isOpen: boolean;
  onClose: () => void;
  stages: DemoStage[];
  currentStageNumber: number;
  onStageSelect: (stageNum: number) => void;
  onRefreshData: () => void;
}

export const DemoModeModal: React.FC<DemoModeModalProps> = ({
  isOpen,
  onClose,
  stages,
  currentStageNumber,
  onStageSelect,
  onRefreshData
}) => {
  if (!isOpen) return null;

  const currentStage = stages.find((s) => s.stage === currentStageNumber) || stages[0];

  const handleApplyStage = async (stageNum: number) => {
    try {
      await api.setDemoStage(stageNum);
      onStageSelect(stageNum);
      onRefreshData();
    } catch (err) {
      console.error('Failed to set demo stage', err);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-fade-in">
      <div className="bg-slate-900 border border-slate-700 rounded-2xl max-w-3xl w-full p-6 shadow-2xl space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between pb-4 border-b border-slate-800">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-amber-500 to-indigo-600 flex items-center justify-center shadow-lg">
              <Sparkles className="w-5 h-5 text-white" />
            </div>
            <div>
              <h2 className="text-lg font-bold text-white tracking-tight">
                CardioTwin AI — Guided Hackathon Demo Sequence
              </h2>
              <p className="text-xs text-slate-400">
                Deterministic 8-stage presentation journey for Patient A-1042.
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-400 hover:text-white transition-all"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Stage Progress Bar */}
        <div className="grid grid-cols-4 sm:grid-cols-8 gap-1.5">
          {stages.map((st) => {
            const isActive = st.stage === currentStageNumber;
            const isPassed = st.stage < currentStageNumber;
            return (
              <button
                key={st.stage}
                onClick={() => handleApplyStage(st.stage)}
                className={`p-2 rounded-lg text-center transition-all border ${
                  isActive
                    ? 'bg-sky-600 border-sky-400 text-white font-bold shadow-lg shadow-sky-600/30'
                    : isPassed
                    ? 'bg-slate-800 border-slate-700 text-slate-300'
                    : 'bg-slate-950 border-slate-800 text-slate-500 hover:border-slate-700'
                }`}
              >
                <div className="text-[10px] font-mono">Stage</div>
                <div className="text-sm font-bold">{st.stage}</div>
              </button>
            );
          })}
        </div>

        {/* Active Stage Card */}
        {currentStage && (
          <div className="bg-slate-950 p-5 rounded-xl border border-slate-800 space-y-4">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
              <div>
                <span className="text-xs font-mono font-bold text-sky-400 uppercase tracking-wider">
                  Stage {currentStage.stage} of 8
                </span>
                <h3 className="text-base font-bold text-white mt-0.5">{currentStage.title}</h3>
              </div>
              <div className="flex items-center gap-3 font-mono text-xs">
                <span className="text-slate-400">Twin Drift: <strong className="text-white">{currentStage.drift_score}</strong></span>
                <span className={`px-2 py-0.5 rounded border ${
                  currentStage.drift_level === "High" ? "bg-rose-950 text-rose-300 border-rose-800" :
                  currentStage.drift_level === "Elevated" ? "bg-amber-950 text-amber-300 border-amber-800" :
                  currentStage.drift_level === "Watch" ? "bg-amber-950 text-amber-300 border-amber-800" :
                  "bg-emerald-950 text-emerald-300 border-emerald-800"
                }`}>
                  {currentStage.drift_level}
                </span>
                <span className="text-slate-400">24h Risk: <strong className="text-rose-400">{Math.round(currentStage.risk_24h * 100)}%</strong></span>
              </div>
            </div>

            <p className="text-xs text-slate-300 leading-relaxed">
              {currentStage.description}
            </p>

            <div className="bg-slate-900/90 p-3 rounded-lg border border-slate-800 flex items-start gap-2 text-xs text-sky-200">
              <CheckCircle2 className="w-4 h-4 text-sky-400 shrink-0 mt-0.5" />
              <span><strong className="text-white">Milestone: </strong>{currentStage.key_event}</span>
            </div>
          </div>
        )}

        {/* Step Navigation Controls */}
        <div className="flex items-center justify-between pt-2">
          <button
            onClick={() => handleApplyStage(Math.max(1, currentStageNumber - 1))}
            disabled={currentStageNumber <= 1}
            className="px-4 py-2 rounded-lg text-xs font-semibold bg-slate-800 hover:bg-slate-700 text-slate-200 flex items-center gap-1.5 disabled:opacity-30 cursor-pointer"
          >
            <ChevronLeft className="w-4 h-4" /> Previous Stage
          </button>

          <span className="text-xs text-slate-400 font-mono">
            {currentStageNumber} / 8 Completed
          </span>

          <button
            onClick={() => handleApplyStage(Math.min(8, currentStageNumber + 1))}
            disabled={currentStageNumber >= 8}
            className="px-5 py-2 rounded-lg text-xs font-semibold bg-gradient-to-r from-sky-600 to-indigo-600 hover:from-sky-500 hover:to-indigo-500 text-white flex items-center gap-1.5 disabled:opacity-30 cursor-pointer shadow-md shadow-sky-600/20"
          >
            Next Stage <ChevronRight className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  );
};
