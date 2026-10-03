# HL7® FHIR® R4 & ABDM Interoperability Specification

> **MANDATORY REGULATORY & CONFORMANCE NOTICE**
> - **FHIR-aligned prototype architecture**: This document and the CardioTwin AI software demonstrate an architectural prototype mapped to the HL7® FHIR® Release 4 (R4) standard.
> - **ABDM Integration Status**: ABDM integration is a future deployment direction; this prototype is **not ABDM-certified**.
> - **Non-Diagnostic Research Boundary**: This system is a clinician decision-support demonstration tool using synthetic mathematical physiological data. It does not possess CE mark, FDA 510(k), or CDSCO SaMD clearance.

---

## 1. Architectural Strategy

CardioTwin AI bridges two distinct data regimes:
1. **Static / Episodic Clinical Records**: Transmitted via standard FHIR R4 resources (Patient demographic records, chronic Conditions, prescribed Medications, laboratory Observations).
2. **High-Frequency Wearable Telemetry Streams**: Ingested via lightweight streaming pipelines (e.g., MQTT/WebSockets) and mapped to FHIR `Observation` bundles for longitudinal clinical audit trails.

The Digital Twin state engine synthesizes these inputs into an $N=1$ continuous personal baseline and multivariate drift score, creating derived FHIR `RiskAssessment` resources.

```
       [ Hospital EHR / Clinic ]                 [ Consumer Wearable / Sensor ]
                  │                                           │
         HL7 FHIR R4 JSON                           High-Freq Telemetry
                  ▼                                           ▼
       ┌─────────────────────────────────────────────────────────────┐
       │             CardioTwin AI Ingestion Layer                   │
       │       - Synthetic Patient Demographics (Patient)            │
       │       - Comorbidity Profiles (Condition)                    │
       │       - Pharmacotherapy Regimens (MedicationStatement)      │
       │       - Continuous Telemetry Points (Observation)           │
       └──────────────────────────────┬──────────────────────────────┘
                                      │
                                      ▼
                      ┌──────────────────────────────┐
                      │    CardioTwin State Engine   │
                      │  - N=1 Personalized Normal   │
                      │  - Multivariate Twin Drift   │
                      │  - Multi-Horizon Forecasting │
                      └──────────────┬───────────────┘
                                      │
                                      ▼
                      [ FHIR RiskAssessment Export ]
```

---

## 2. Standard HL7 FHIR R4 Mappings

### 2.1 Patient Resource (`Patient`)
Maps the synthetic patient cohort identifier, age, sex, and administrative status.

```json
{
  "resourceType": "Patient",
  "id": "PAT-A-1042",
  "meta": {
    "profile": ["http://hl7.org/fhir/StructureDefinition/Patient"]
  },
  "identifier": [
    {
      "use": "usual",
      "type": {
        "coding": [
          {
            "system": "http://terminology.hl7.org/CodeSystem/v2-0203",
            "code": "MR",
            "display": "Medical Record Number"
          }
        ]
      },
      "system": "urn:cardiotwin:synthetic:mrn",
      "value": "SYNTH-A1042-HTN"
    }
  ],
  "active": true,
  "name": [
    {
      "use": "official",
      "family": "Sharma",
      "given": ["Ramesh"]
    }
  ],
  "gender": "male",
  "birthDate": "1966-04-12"
}
```

---

### 2.2 Observation Resource (`Observation` — Telemetry & Baseline)
Maps wearable telemetry (Resting Heart Rate, HRV, SpO2) and personal baseline z-scores. Uses standard LOINC codes.

```json
{
  "resourceType": "Observation",
  "id": "OBS-A1042-RHR-LIVE",
  "status": "final",
  "category": [
    {
      "coding": [
        {
          "system": "http://terminology.hl7.org/CodeSystem/observation-category",
          "code": "vital-signs",
          "display": "Vital Signs"
        }
      ]
    }
  ],
  "code": {
    "coding": [
      {
        "system": "http://loinc.org",
        "code": "8867-4",
        "display": "Heart rate"
      }
    ],
    "text": "Resting Heart Rate"
  },
  "subject": {
    "reference": "Patient/PAT-A-1042"
  },
  "effectiveDateTime": "2026-10-03T14:30:00Z",
  "valueQuantity": {
    "value": 82.0,
    "unit": "beats/minute",
    "system": "http://unitsofmeasure.org",
    "code": "/min"
  },
  "referenceRange": [
    {
      "low": {
        "value": 58.4,
        "unit": "/min"
      },
      "high": {
        "value": 77.6,
        "unit": "/min"
      },
      "type": {
        "text": "Personalized N=1 Baseline Range (μ ± 2σ)"
      }
    }
  ],
  "component": [
    {
      "code": {
        "text": "Twin Drift Z-Score"
      },
      "valueQuantity": {
        "value": 2.83,
        "unit": "SD"
      }
    }
  ]
}
```

---

### 2.3 Condition Resource (`Condition` — Clinical History)
Maps chronic comorbidities (Essential Hypertension, Type 2 Diabetes, Dyslipidemia) using SNOMED CT and ICD-10.

```json
{
  "resourceType": "Condition",
  "id": "COND-A1042-HTN",
  "clinicalStatus": {
    "coding": [
      {
        "system": "http://terminology.hl7.org/CodeSystem/condition-clinical",
        "code": "active"
      }
    ]
  },
  "verificationStatus": {
    "coding": [
      {
        "system": "http://terminology.hl7.org/CodeSystem/condition-ver-status",
        "code": "confirmed"
      }
    ]
  },
  "category": [
    {
      "coding": [
        {
          "system": "http://terminology.hl7.org/CodeSystem/condition-category",
          "code": "problem-list-item"
        }
      ]
    }
  ],
  "code": {
    "coding": [
      {
        "system": "http://snomed.info/sct",
        "code": "38341003",
        "display": "Hypertensive disorder, systemic arterial (disorder)"
      },
      {
        "system": "http://hl7.org/fhir/sid/icd-10",
        "code": "I10",
        "display": "Essential (primary) hypertension"
      }
    ],
    "text": "Essential Hypertension"
  },
  "subject": {
    "reference": "Patient/PAT-A-1042"
  }
}
```

---

### 2.4 Medication Resource (`MedicationStatement` — Adherence Tracking)
Tracks active antihypertensive and statin therapy alongside measured patient adherence.

```json
{
  "resourceType": "MedicationStatement",
  "id": "MED-A1042-AMLODIPINE",
  "status": "active",
  "medicationCodeableConcept": {
    "coding": [
      {
        "system": "http://www.nlm.nih.gov/research/umls/rxnorm",
        "code": "197361",
        "display": "Amlodipine 5 MG Oral Tablet"
      }
    ],
    "text": "Amlodipine 5mg Daily"
  },
  "subject": {
    "reference": "Patient/PAT-A-1042"
  },
  "effectivePeriod": {
    "start": "2024-01-15"
  },
  "note": [
    {
      "text": "Simulated wearable/refill adherence: 70% (Non-adherence flagged as deterioration accelerant)"
    }
  ]
}
```

---

### 2.5 Derived Risk Resource (`RiskAssessment`)
Exports the Digital Twin deterioration forecast and major explainability contributors.

```json
{
  "resourceType": "RiskAssessment",
  "id": "RISK-A1042-24H",
  "status": "final",
  "subject": {
    "reference": "Patient/PAT-A-1042"
  },
  "occurrenceDateTime": "2026-10-03T14:30:00Z",
  "basis": [
    { "reference": "Observation/OBS-A1042-RHR-LIVE" },
    { "reference": "Condition/COND-A1042-HTN" }
  ],
  "prediction": [
    {
      "outcome": {
        "coding": [
          {
            "system": "http://snomed.info/sct",
            "code": "410429000",
            "display": "Cardiac arrest or decompensated heart failure (event)"
          }
        ],
        "text": "24-Hour Acute Hemodynamic Decompensation"
      },
      "probabilityDecimal": 0.27,
      "whenPeriod": {
        "start": "2026-10-03T14:30:00Z",
        "end": "2026-10-04T14:30:00Z"
      }
    }
  ],
  "note": [
    {
      "text": "Twin Drift Score: 71.2/100 (High). Top contributors: Resting HR (+18), HRV Decline (+21), Sleep Deficit (+12)."
    }
  ]
}
```

---

## 3. Ayushman Bharat Digital Mission (ABDM) Direction

### 3.1 Future Integration Roadmap
While this competition submission is an uncertified research prototype, its architectural interfaces are structured to align with future ABDM milestone specifications:

1. **M1 (ABHA Creation & Verification)**:
   - Ingestion of 14-digit Ayushman Bharat Health Account (ABHA) IDs for patient matching.
2. **M2 (Health Information Provider - HIP)**:
   - Publishing Digital Twin deterioration summaries as FHIR DiagnosticReport / RiskAssessment bundles to ABDM Health Information Exchanges upon clinician approval.
3. **M3 (Health Information User - HIU)**:
   - Querying historical longitudinal EHR, lab records, and discharge summaries across India's federated health data network using patient consent tokens.

### 3.2 Consent Artifact Handling
Under ABDM guidelines, patient sensor streaming requires explicit electronic consent:
- Consent artifact specifies granularity: `Continuous Telemetry + Digital Twin Processing`.
- Purpose code: `CAREPROV` (Care Management).
- Revocation capability: Instant purge of active in-memory twin states upon patient request.
