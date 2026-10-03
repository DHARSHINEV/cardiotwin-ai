import React, { useState, useEffect, useRef } from 'react';
import {
  Activity, Heart, AlertTriangle, ShieldCheck, CheckCircle2,
  Clock, Sliders, Layers, Bell, ArrowRight, UserCheck, Stethoscope
} from 'lucide-react';
import { Navbar } from './components/Navbar';
import { PersonalBaselineCard } from './components/PersonalBaselineCard';
import { LiveSimulationControl } from './components/LiveSimulationControl';
import { WhatIfSimulator } from './components/WhatIfSimulator';
import { DeteriorationTimelineView } from './components/DeteriorationTimelineView';
import { ExplainabilityPanel } from './components/ExplainabilityPanel';
import { DataQualityPanel } from './components/DataQualityPanel';
import { ModelEvaluationView } from './components/ModelEvaluationView';
import { ModelTransparencyView } from './components/ModelTransparencyView';
import { TwinJourneyView } from './components/TwinJourneyView';
import { MultimodalFusionDiagram } from './components/MultimodalFusionDiagram';
import { DemoModeModal } from './components/DemoModeModal';
import { InteroperabilityModal } from './components/InteroperabilityModal';
import {
  api, PatientSummary, PatientDetail, TwinState,
  TimelinePoint, AlertItem, EvaluationData, DataQualityData, DemoStage
} from './services/api';

export function App() {
  const [patients, setPatients] = useState<PatientSummary[]>([]);
  const [selectedPatientId, setSelectedPatientId] = useState<string>('PAT-A-1042');
  const [patientDetail, setPatientDetail] = useState<PatientDetail | null>(null);
  const [twinState, setTwinState] = useState<TwinState | null>(null);
  const [timeline, setTimeline] = useState<TimelinePoint[]>([]);
  const [alerts, setAlerts] = useState<AlertItem[]>([]);
  const [evalData, setEvalData] = useState<EvaluationData | null>(null);
  const [dataQuality, setDataQuality] = useState<DataQualityData | null>(null);
  const [demoStages, setDemoStages] = useState<DemoStage[]>([]);
  const [currentDemoStage, setCurrentDemoStage] = useState<number>(5);

  const [activeTab, setActiveTab] = useState<string>('twin');
  const [isSimulating, setIsSimulating] = useState<boolean>(false);
  const [isDemoOpen, setIsDemoOpen] = useState<boolean>(false);
  const [isInteropOpen, setIsInteropOpen] = useState<boolean>(false);
  const [simulationState, setSimulationState] = useState<string>('Gradual deterioration');
  const [showJourney, setShowJourney] = useState<boolean>(true);

  const simulationTimerRef = useRef<any>(null);

  // Load Initial Cohort & Benchmarks
  useEffect(() => {
    loadPatients();
    loadEvaluationData();
    loadDemoStages();
  }, []);

  // Reload patient-specific data when patient changes
  useEffect(() => {
    if (selectedPatientId) {
      loadPatientData(selectedPatientId);
    }
  }, [selectedPatientId]);

  // Live Timer Simulation Loop
  useEffect(() => {
    if (isSimulating) {
      simulationTimerRef.current = setInterval(() => {
        handleStepSimulation();
      }, 4000);
    } else {
      if (simulationTimerRef.current) clearInterval(simulationTimerRef.current);
    }
    return () => {
      if (simulationTimerRef.current) clearInterval(simulationTimerRef.current);
    };
  }, [isSimulating, selectedPatientId, simulationState]);

  const loadPatients = async () => {
    try {
      const data = await api.getPatients(20);
      setPatients(data);
    } catch (err) {
      console.error('Failed to load patients', err);
    }
  };

  const loadEvaluationData = async () => {
    try {
      const data = await api.getEvaluationMetrics();
      setEvalData(data);
    } catch (err) {
      console.error('Failed to load evaluation data', err);
    }
  };

  const loadDemoStages = async () => {
    try {
      const data = await api.getDemoStages();
      setDemoStages(data.stages);
    } catch (err) {
      console.error('Failed to load demo stages', err);
    }
  };

  const loadPatientData = async (id: string) => {
    try {
      const [detail, twin, tl, al, dq] = await Promise.all([
        api.getPatient(id),
        api.getTwinState(id),
        api.getTimeline(id),
        api.getAlerts(id),
        api.getDataQuality(id)
      ]);
      setPatientDetail(detail);
      setTwinState(twin);
      setTimeline(tl.timeline || []);
      setAlerts(al);
      setDataQuality(dq);
      if (twin.simulation_state) {
        setSimulationState(twin.simulation_state);
      }
    } catch (err) {
      console.error(`Failed to load data for patient ${id}`, err);
    }
  };

  const handleStepSimulation = async () => {
    try {
      const res = await api.simulateWearableStep(selectedPatientId, simulationState);
      if (res.updated_twin_state) {
        setTwinState(res.updated_twin_state);
      }
      // Refresh alerts & timeline
      const [newAlerts, tl, dq] = await Promise.all([
        api.getAlerts(selectedPatientId),
        api.getTimeline(selectedPatientId),
        api.getDataQuality(selectedPatientId)
      ]);
      setAlerts(newAlerts);
      setTimeline(tl.timeline || []);
      setDataQuality(dq);
    } catch (err) {
      console.error('Failed to step simulation', err);
    }
  };

  const handleAcknowledgeAlert = async (alertId: string) => {
    try {
      await api.acknowledgeAlert(alertId, 'Dr. Clinician');
      const updated = await api.getAlerts(selectedPatientId);
      setAlerts(updated);
    } catch (err) {
      console.error('Failed to acknowledge alert', err);
    }
  };

  const handleResetPatient = async () => {
    try {
      await api.resetDemo();
      setCurrentDemoStage(1);
      loadPatientData(selectedPatientId);
    } catch (err) {
      console.error('Failed to reset patient', err);
    }
  };

  const unacknowledgedAlerts = alerts.filter((a) => !a.acknowledged);

  return (
    <div className="min-h-screen bg-[#090d16] text-slate-100 flex flex-col font-sans">
      {/* Top Navigation */}
      <Navbar
        patients={patients}
        selectedPatientId={selectedPatientId}
        onSelectPatient={setSelectedPatientId}
        isSimulating={isSimulating}
        onToggleSimulation={() => setIsSimulating(!isSimulating)}
        onOpenDemo={() => setIsDemoOpen(true)}
        onOpenInterop={() => setIsInteropOpen(true)}
        activeTab={activeTab}
        onTabChange={setActiveTab}
        alertsCount={unacknowledgedAlerts.length}
      />

      {/* Main Content Dashboard */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 py-6 space-y-6">
        {/* Executive Patient Status Banner (Section 40 Visual Quality) */}
        {patientDetail && twinState && (
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 shadow-xl">
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 items-center">
              {/* Patient Identity */}
              <div className="flex items-center gap-3 border-b md:border-b-0 md:border-r border-slate-800 pb-3 md:pb-0 md:pr-4">
                <div className="w-12 h-12 rounded-xl bg-slate-800 border border-slate-700 flex items-center justify-center text-sky-400 font-bold font-mono text-base">
                  {patientDetail.sex === 'Male' ? 'M' : 'F'}{patientDetail.age}
                </div>
                <div>
                  <div className="flex items-center gap-2">
                    <h2 className="text-base font-bold text-white tracking-tight">{patientDetail.name}</h2>
                    <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-slate-800 text-slate-300">
                      {patientDetail.id}
                    </span>
                  </div>
                  <p className="text-xs text-slate-400 font-medium">{patientDetail.primary_condition}</p>
                  <p className="text-[11px] text-slate-500 font-mono mt-0.5">
                    BMI: {patientDetail.bmi} • Med Adherence: {Math.round((patientDetail.ehr?.medication_adherence || 0.70) * 100)}%
                  </p>
                </div>
              </div>

              {/* Digital Twin Drift Status Gauge */}
              <div className="border-b md:border-b-0 md:border-r border-slate-800 pb-3 md:pb-0 md:pr-4">
                <span className="text-[10px] uppercase font-mono tracking-wider text-slate-400 block mb-1">
                  Twin Drift Status
                </span>
                <div className="flex items-center justify-between">
                  <div className="flex items-baseline gap-2">
                    <span className="text-2xl font-black tracking-tight text-white">
                      {twinState.twin_drift_score.toFixed(1)}
                    </span>
                    <span className="text-xs text-slate-500 font-mono">/ 100</span>
                  </div>
                  <span className={`px-2.5 py-1 rounded-full text-xs font-bold font-mono border ${
                    twinState.drift_level === 'High' ? 'bg-rose-950 text-rose-300 border-rose-800 animate-pulse' :
                    twinState.drift_level === 'Elevated' ? 'bg-amber-950 text-amber-300 border-amber-800' :
                    twinState.drift_level === 'Watch' ? 'bg-amber-950/80 text-amber-300 border-amber-800' :
                    'bg-emerald-950 text-emerald-300 border-emerald-800'
                  }`}>
                    {twinState.drift_level}
                  </span>
                </div>
                {/* Visual Progress Bar */}
                <div className="w-full bg-slate-800 h-1.5 rounded-full mt-2 overflow-hidden">
                  <div
                    className={`h-full rounded-full transition-all duration-500 ${
                      twinState.twin_drift_score > 75 ? 'bg-rose-500' :
                      twinState.twin_drift_score > 50 ? 'bg-orange-500' :
                      twinState.twin_drift_score > 25 ? 'bg-amber-500' : 'bg-emerald-500'
                    }`}
                    style={{ width: `${Math.min(100, twinState.twin_drift_score)}%` }}
                  ></div>
                </div>
              </div>

              {/* Multi-Horizon Risk Forecast */}
              <div className="border-b md:border-b-0 md:border-r border-slate-800 pb-3 md:pb-0 md:pr-4">
                <span className="text-[10px] uppercase font-mono tracking-wider text-slate-400 block mb-1">
                  Multi-Horizon Risk
                </span>
                <div className="grid grid-cols-3 gap-2 text-center font-mono">
                  <div className="bg-slate-950/60 p-1.5 rounded border border-slate-800/80">
                    <span className="text-[10px] text-slate-500 block">6h Risk</span>
                    <span className="text-xs font-bold text-slate-200">
                      {Math.round(twinState.risk_6h * 100)}%
                    </span>
                  </div>
                  <div className="bg-slate-950/60 p-1.5 rounded border border-slate-800/80">
                    <span className="text-[10px] text-slate-500 block">24h Risk</span>
                    <span className={`text-xs font-bold ${twinState.risk_24h > 0.5 ? 'text-rose-400' : 'text-amber-400'}`}>
                      {Math.round(twinState.risk_24h * 100)}%
                    </span>
                  </div>
                  <div className="bg-slate-950/60 p-1.5 rounded border border-slate-800/80">
                    <span className="text-[10px] text-slate-500 block">72h Risk</span>
                    <span className="text-xs font-bold text-slate-200">
                      {Math.round(twinState.risk_72h * 100)}%
                    </span>
                  </div>
                </div>
              </div>

              {/* Data Quality & Alert Summary */}
              <div className="flex items-center justify-between">
                <div>
                  <span className="text-[10px] uppercase font-mono tracking-wider text-slate-400 block mb-0.5">
                    Data Quality
                  </span>
                  <div className="flex items-center gap-1.5">
                    <ShieldCheck className="w-4 h-4 text-emerald-400" />
                    <span className="text-sm font-bold text-white font-mono">
                      {twinState.data_quality}%
                    </span>
                  </div>
                  <span className="text-[10px] text-slate-500 font-mono">Telemetry Calibrated</span>
                </div>

                <div className="text-right">
                  <span className="text-[10px] uppercase font-mono tracking-wider text-slate-400 block mb-0.5">
                    Alert Status
                  </span>
                  <div className="flex items-center justify-end gap-1.5">
                    <Bell className={`w-4 h-4 ${unacknowledgedAlerts.length > 0 ? 'text-rose-400 animate-bounce' : 'text-slate-500'}`} />
                    <span className={`text-sm font-bold font-mono ${unacknowledgedAlerts.length > 0 ? 'text-rose-400' : 'text-slate-300'}`}>
                      {unacknowledgedAlerts.length > 0
                        ? `${unacknowledgedAlerts.length} Pending Review`
                        : alerts.length > 0
                        ? `0 Active (${alerts.length} Historical)`
                        : '0 Active'}
                    </span>
                  </div>
                  <button
                    onClick={() => setActiveTab('alerts')}
                    className="text-[10px] text-sky-400 hover:text-sky-300 font-medium underline cursor-pointer"
                  >
                    View Alert Center
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Tab 1: Digital Twin Main Overview */}
        {activeTab === 'twin' && twinState && patientDetail && (
          <div className="space-y-6">
            {/* 30-Second Twin Journey Overview (Phase 13) */}
            <div className="space-y-2">
              <div className="flex items-center justify-between px-1">
                <span className="text-xs uppercase font-mono tracking-wider text-slate-400 font-semibold">
                  30-Second Digital Twin Journey Architecture
                </span>
                <button
                  onClick={() => setShowJourney(!showJourney)}
                  className="text-xs font-mono text-sky-400 hover:text-sky-300 underline cursor-pointer"
                >
                  {showJourney ? 'Hide Architecture Journey' : 'Show Architecture Journey'}
                </button>
              </div>
              {showJourney && (
                <TwinJourneyView
                  twinState={twinState}
                  patientName={patientDetail.name}
                  onOpenWhatIf={() => setActiveTab('whatif')}
                />
              )}
            </div>

            {/* Live Telemetry Simulator Bar */}
            <LiveSimulationControl
              simulationState={simulationState}
              onSelectState={setSimulationState}
              onStepSimulation={handleStepSimulation}
              isSimulating={isSimulating}
              onToggleSimulating={() => setIsSimulating(!isSimulating)}
              onResetPatient={handleResetPatient}
              lastUpdated={twinState.timestamp}
            />

            {/* Personal Baseline and Deviations */}
            <PersonalBaselineCard
              twinState={twinState}
              patientName={patientDetail.name}
            />

            {/* Dual Panel: Explainability & Data Quality */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <ExplainabilityPanel
                contributors={twinState.top_contributors}
                driftScore={twinState.twin_drift_score}
                driftLevel={twinState.drift_level}
              />
              <DataQualityPanel dataQuality={dataQuality} />
            </div>
          </div>
        )}

        {/* Tab 2: Deterioration Timeline */}
        {activeTab === 'timeline' && (
          <DeteriorationTimelineView
            timeline={timeline}
            patientId={selectedPatientId}
          />
        )}

        {/* Tab 3: What-If Digital Twin Scenario Simulator */}
        {activeTab === 'whatif' && (
          <WhatIfSimulator
            patientId={selectedPatientId}
            twinState={twinState}
          />
        )}

        {/* Tab 4: Model Evaluation & Ablation */}
        {activeTab === 'eval' && (
          <div className="space-y-6">
            <MultimodalFusionDiagram />
            <ModelEvaluationView
              evalData={evalData}
            />
          </div>
        )}

        {/* Tab 5: Model Transparency & Responsible AI (Phase 15) */}
        {activeTab === 'transparency' && (
          <ModelTransparencyView
            evalData={evalData}
          />
        )}

        {/* Tab 6: Clinician Alerts Center */}
        {activeTab === 'alerts' && (
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-lg space-y-4">
            <div className="flex items-center justify-between pb-3 border-b border-slate-800">
              <div className="flex items-center gap-2">
                <Bell className="w-5 h-5 text-rose-400" />
                <h2 className="text-base font-bold text-white tracking-tight">Clinician Alert Center</h2>
              </div>
              <span className="text-xs font-mono text-slate-400">
                {unacknowledgedAlerts.length} Pending Review • {alerts.length - unacknowledgedAlerts.length} Historical Records
              </span>
            </div>

            <div className="space-y-3">
              {alerts.length === 0 ? (
                <div className="p-8 text-center text-slate-400 text-xs">
                  No active deterioration alerts logged for this patient.
                </div>
              ) : (
                alerts.map((al) => (
                  <div
                    key={al.id}
                    className={`p-4 rounded-xl border transition-all ${
                      al.acknowledged
                        ? 'bg-slate-950/40 border-slate-800/60 opacity-60'
                        : al.severity === 'High'
                        ? 'bg-rose-950/20 border-rose-800/80 shadow-md shadow-rose-900/10'
                        : 'bg-amber-950/20 border-amber-800/80'
                    }`}
                  >
                    <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-2">
                      <div className="flex items-center gap-2">
                        <span className={`text-[10px] font-mono px-2 py-0.5 rounded font-bold border ${
                          al.severity === 'High' ? 'bg-rose-950 text-rose-300 border-rose-800' : 'bg-amber-950 text-amber-300 border-amber-800'
                        }`}>
                          {al.severity} Severity
                        </span>
                        <span className={`text-[10px] font-mono px-2 py-0.5 rounded font-bold border ${
                          al.acknowledged ? 'bg-slate-800 text-slate-400 border-slate-700' : 'bg-rose-950 text-rose-300 border-rose-700 animate-pulse'
                        }`}>
                          {al.acknowledged ? 'Historical Archive' : 'Pending Review'}
                        </span>
                        <h3 className="text-sm font-bold text-white">{al.title}</h3>
                      </div>
                      <span className="text-[11px] font-mono text-slate-400">
                        {new Date(al.timestamp).toLocaleString()}
                      </span>
                    </div>

                    <p className="text-xs text-slate-300 leading-relaxed mb-3">
                      {al.reason}
                    </p>

                    <div className="flex items-center justify-between pt-2 border-t border-slate-800/80 text-xs">
                      <div className="flex items-center gap-2 text-[11px] text-slate-400 font-mono">
                        <span>Model Forecast Risk: <strong className="text-white">{Math.round(al.model_risk * 100)}%</strong></span>
                        <span>•</span>
                        <span>Telemetry Quality: <strong className="text-white">{al.data_quality}%</strong></span>
                      </div>

                      {al.acknowledged ? (
                        <span className="text-[11px] text-emerald-400 font-mono flex items-center gap-1">
                          <CheckCircle2 className="w-3.5 h-3.5" /> Acknowledged by {al.acknowledged_by || 'Dr. Clinician'}
                        </span>
                      ) : (
                        <button
                          onClick={() => handleAcknowledgeAlert(al.id)}
                          className="px-3 py-1 rounded bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold border border-slate-700 transition-all cursor-pointer"
                        >
                          Acknowledge & Dismiss
                        </button>
                      )}
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        )}
      </main>

      {/* Presentation Demo Mode Guided Modal */}
      <DemoModeModal
        isOpen={isDemoOpen}
        onClose={() => setIsDemoOpen(false)}
        stages={demoStages}
        currentStageNumber={currentDemoStage}
        onStageSelect={setCurrentDemoStage}
        onRefreshData={() => loadPatientData(selectedPatientId)}
      />

      {/* ABDM / FHIR Interoperability Modal */}
      <InteroperabilityModal
        isOpen={isInteropOpen}
        onClose={() => setIsInteropOpen(false)}
        patientId={selectedPatientId}
      />

      {/* Footer */}
      <footer className="border-t border-slate-800/80 bg-slate-950 py-4 px-4 text-center text-xs text-slate-500">
        <p>
          CardioTwin AI • Digital Twin Challenge 2026 by Happiest Health • Built with Python, FastAPI, React & TypeScript
        </p>
        <p className="text-[11px] text-slate-600 mt-1">
          Research proof-of-concept using 100% synthetic mathematical data. Zero real patient identifiers.
        </p>
      </footer>
    </div>
  );
}
export default App;
