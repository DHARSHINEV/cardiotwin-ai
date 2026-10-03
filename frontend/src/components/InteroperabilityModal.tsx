import React, { useState, useEffect } from 'react';
import { X, Share2, Shield, Lock, FileCode, CheckCircle, ExternalLink } from 'lucide-react';
import { api } from '../services/api';

interface InteroperabilityModalProps {
  isOpen: boolean;
  onClose: () => void;
  patientId: string;
}

export const InteroperabilityModal: React.FC<InteroperabilityModalProps> = ({
  isOpen,
  onClose,
  patientId
}) => {
  const [fhirData, setFhirData] = useState<any>(null);
  const [activeTab, setActiveTab] = useState<'fhir' | 'abdm' | 'privacy'>('fhir');

  useEffect(() => {
    if (isOpen) {
      api.getFhirPatient(patientId)
        .then(setFhirData)
        .catch(console.error);
    }
  }, [isOpen, patientId]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-fade-in">
      <div className="bg-slate-900 border border-slate-700 rounded-2xl max-w-3xl w-full p-6 shadow-2xl space-y-5">
        {/* Header */}
        <div className="flex items-center justify-between pb-3 border-b border-slate-800">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-teal-600 to-sky-600 flex items-center justify-center shadow-lg">
              <Share2 className="w-5 h-5 text-white" />
            </div>
            <div>
              <h2 className="text-base font-bold text-white tracking-tight">
                India-Specific Interoperability & Privacy Architecture
              </h2>
              <p className="text-xs text-slate-400">
                Ayushman Bharat Digital Mission (ABDM) / HL7 FHIR R4 Architectural Readiness.
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-400 hover:text-white"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Tab Switcher */}
        <div className="flex border-b border-slate-800 gap-4 text-xs font-semibold">
          <button
            onClick={() => setActiveTab('fhir')}
            className={`pb-2 transition-all ${
              activeTab === 'fhir' ? 'text-sky-400 border-b-2 border-sky-400' : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            HL7 FHIR R4 Resource JSON
          </button>
          <button
            onClick={() => setActiveTab('abdm')}
            className={`pb-2 transition-all ${
              activeTab === 'abdm' ? 'text-sky-400 border-b-2 border-sky-400' : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            ABDM Integration Concept
          </button>
          <button
            onClick={() => setActiveTab('privacy')}
            className={`pb-2 transition-all ${
              activeTab === 'privacy' ? 'text-sky-400 border-b-2 border-sky-400' : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            Privacy, RBAC & Audit Logs
          </button>
        </div>

        {/* Content Area */}
        {activeTab === 'fhir' && (
          <div className="space-y-3">
            <div className="bg-slate-950 p-4 rounded-xl border border-slate-800 font-mono text-[11px] text-slate-300 max-h-72 overflow-y-auto">
              <pre>{JSON.stringify(fhirData, null, 2)}</pre>
            </div>
            <p className="text-[11px] text-slate-400 italic">
              • Demonstrates interoperability mapping to HL7 FHIR R4 Patient and Observation resources (NRCES India StructureDefinition).
            </p>
          </div>
        )}

        {activeTab === 'abdm' && (
          <div className="space-y-3 text-xs text-slate-300 leading-relaxed bg-slate-950 p-4 rounded-xl border border-slate-800">
            <div className="flex items-center gap-2 text-teal-400 font-bold uppercase text-[11px]">
              <CheckCircle className="w-4 h-4" /> ABDM Architectural Direction
            </div>
            <p>
              CardioTwin AI structures telemetry to easily serialize into ABDM-compliant Health Information User (HIU) and Health Information Provider (HIP) bundles.
            </p>
            <div className="p-3 bg-slate-900 rounded-lg border border-slate-800 font-mono text-[11px] space-y-1 text-slate-400">
              <p>• ABHA Address: <span className="text-white">patient.a1042@abdm (Simulated)</span></p>
              <p>• Consent Manager: <span className="text-white">HIP/HIU Gateway Sandbox Ready</span></p>
              <p>• Data Types: <span className="text-white">OPConsultation, DiagnosticReport, VitalTelemetry</span></p>
            </div>
            <div className="bg-amber-950/40 border border-amber-800/40 p-2.5 rounded text-[11px] text-amber-300">
              <strong>Mandatory Compliance Disclosure: </strong>
              ABDM/FHIR compatibility is an architectural direction in this prototype and does not represent official government certification or empanelment.
            </div>
          </div>
        )}

        {activeTab === 'privacy' && (
          <div className="space-y-3 text-xs text-slate-300 leading-relaxed bg-slate-950 p-4 rounded-xl border border-slate-800">
            <div className="flex items-center gap-2 text-sky-400 font-bold uppercase text-[11px]">
              <Lock className="w-4 h-4" /> Healthcare Privacy & Security Framework
            </div>
            <ul className="list-disc pl-5 space-y-1.5 text-slate-300 text-[11px]">
              <li><strong>Zero Real PII:</strong> 100% synthetic cohorts. No human identifiers used in prototype.</li>
              <li><strong>Role-Based Access Control (RBAC):</strong> Telemetry charts restricted by clinical role (Cardiologist, Primary Nurse, Telemetry Tech).</li>
              <li><strong>Tamper-Evident Audit Logging:</strong> Every alert review, simulation run, and threshold change logged with timestamps and clinician ID.</li>
              <li><strong>Differential Privacy Concept:</strong> Baseline telemetry perturbations prevent inversion attacks on physiological time-series.</li>
            </ul>
          </div>
        )}

        <div className="flex justify-end pt-2">
          <button
            onClick={onClose}
            className="px-4 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold cursor-pointer"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
};
