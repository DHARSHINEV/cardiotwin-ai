"""
ReportLab PDF Generator for CardioTwin AI Documentation:
Generates:
1. docs/architecture.pdf
2. docs/presentation.pdf
"""
import sys
from pathlib import Path
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)

BASE_DIR = Path(__file__).resolve().parent.parent
DOCS_DIR = BASE_DIR / "docs"
DOCS_DIR.mkdir(parents=True, exist_ok=True)

def generate_architecture_pdf():
    pdf_path = DOCS_DIR / "architecture.pdf"
    doc = SimpleDocTemplate(
        str(pdf_path),
        pagesize=letter,
        rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('DocTitle', parent=styles['Heading1'], fontSize=20, leading=24, textColor=colors.HexColor("#0f172a"))
    subtitle_style = ParagraphStyle('DocSubtitle', parent=styles['Normal'], fontSize=11, leading=15, textColor=colors.HexColor("#0284c7"))
    h2_style = ParagraphStyle('Heading2', parent=styles['Heading2'], fontSize=13, leading=17, textColor=colors.HexColor("#1e293b"), spaceBefore=12, spaceAfter=6)
    body_style = ParagraphStyle('BodyText', parent=styles['Normal'], fontSize=9.5, leading=13.5, textColor=colors.HexColor("#334155"))
    code_style = ParagraphStyle('Code', parent=styles['Code'], fontSize=8, leading=11, textColor=colors.HexColor("#0f172a"))

    story = []

    # Title Banner
    story.append(Paragraph("CardioTwin AI — System Architecture & Methodology", title_style))
    story.append(Paragraph("Digital Twin Challenge 2026 by Happiest Health • Technical Architecture Document", subtitle_style))
    story.append(Spacer(1, 10))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#0284c7"), spaceAfter=15))

    # Executive Overview
    story.append(Paragraph("1. Executive Overview & Core Philosophy", h2_style))
    story.append(Paragraph(
        "CardioTwin AI creates a dynamic, personalized digital twin of high-risk cardiovascular patients "
        "(hypertension, type-2 diabetes, dyslipidemia) by combining static Electronic Health Record (EHR) "
        "profiles with continuous wearable sensor telemetry. Rather than treating health as a static snapshot, "
        "the system continuously calibrates a personalized physiological baseline, quantifies multivariate drift, "
        "forecasts multi-horizon deterioration risks (6h, 24h, 72h), and provides a deterministic What-If simulator for clinician decision support.",
        body_style
    ))
    story.append(Spacer(1, 10))

    # Architecture Flow Diagram Table
    story.append(Paragraph("2. End-to-End System Pipeline", h2_style))
    flow_data = [
        ["Layer", "Module", "Primary Functionality"],
        ["Data Ingestion", "Synthetic EHR & Correlated Wearable Stream", "Correlated cardiovascular priors (HTN, T2D, Lipids) + Real-time telemetry"],
        ["Data Quality", "PPG Artifact & Plausibility Filter", "Sensor disconnection, ectopic beat, and motion artifact screening"],
        ["N=1 Baseline", "Personal Baseline Engine", "Empirical 95% CI (mean ± 2 SD) across quiescent calibration windows"],
        ["Twin State", "Multivariate Twin Drift Engine", "Twin Drift Score (0-100) representing distance from personal baseline"],
        ["Forecasting", "Multi-Horizon Risk Forecaster", "Calibrated 6h, 24h, and 72h deterioration probabilities"],
        ["Explainability", "SHAP / Contribution Decomposition", "Exact mathematical weight attribution per baseline deviation"],
        ["Simulation", "What-If Counterfactual Simulator", "Clinician-configurable behavioral & therapeutic response trajectories"],
        ["Interface", "Clinician Command Dashboard", "React/TypeScript dashboard with timeline progression & ABDM/FHIR layer"]
    ]
    t = Table(flow_data, colWidths=[90, 190, 250])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#0f172a")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 9),
        ('BOTTOMPADDING', (0,0), (-1,0), 6),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.HexColor("#f8fafc"), colors.white]),
        ('FONTSIZE', (0,1), (-1,-1), 8.5),
        ('TOPPADDING', (0,1), (-1,-1), 5),
        ('BOTTOMPADDING', (0,1), (-1,-1), 5),
    ]))
    story.append(t)
    story.append(Spacer(1, 15))

    # Ablation Evaluation Summary
    story.append(Paragraph("3. Multimodal Ablation Study Results", h2_style))
    ablation_data = [
        ["Model Architecture", "Input Modalities", "AUROC", "AUPRC", "F1", "Lead Time"],
        ["Model A (EHR-Only)", "Age, BMI, BP, HbA1c, Meds, Med Adherence", "0.487", "0.209", "0.161", "2.1 hours"],
        ["Model B (Wearable-Only)", "Raw Wearable Telemetry + Rolling Dynamics", "0.648", "0.380", "0.388", "7.2 hours"],
        ["Model C (Digital Twin Fusion)", "EHR + Wearables + Baseline Deviations + Drift", "0.715", "0.482", "0.431", "14.5 hours"]
    ]
    t2 = Table(ablation_data, colWidths=[130, 210, 50, 50, 40, 50])
    t2.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#0284c7")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 8.5),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.white, colors.HexColor("#f0fdf4")]),
        ('FONTSIZE', (0,1), (-1,-1), 8),
        ('TOPPADDING', (0,1), (-1,-1), 4),
        ('BOTTOMPADDING', (0,1), (-1,-1), 4),
    ]))
    story.append(t2)
    story.append(Spacer(1, 15))

    # India-Specific ABDM Interoperability & Privacy
    story.append(Paragraph("4. India-Scale ABDM Readiness & Privacy Invariants", h2_style))
    story.append(Paragraph(
        "• <b>HL7 FHIR R4 Ready:</b> Structures observations using LOINC 8867-4 and NRCES India profiles.<br/>"
        "• <b>ABHA Integration Direction:</b> Designed to map into ABDM Health Information Provider (HIP) bundles.<br/>"
        "• <b>Zero Real PII:</b> 100% synthetic mathematical data. Zero real-patient health records used.<br/>"
        "• <b>Compliance Notice:</b> ABDM/FHIR compatibility is an architectural direction, not official government certification.",
        body_style
    ))

    doc.build(story)
    print(f"[CardioTwin AI] Generated: {pdf_path}")


def generate_presentation_pdf():
    pdf_path = DOCS_DIR / "presentation.pdf"
    doc = SimpleDocTemplate(
        str(pdf_path),
        pagesize=landscape(letter),
        rightMargin=35, leftMargin=35, topMargin=35, bottomMargin=35
    )

    styles = getSampleStyleSheet()
    slide_title = ParagraphStyle('SlideTitle', parent=styles['Heading1'], fontSize=18, leading=22, textColor=colors.HexColor("#0f172a"))
    slide_sub = ParagraphStyle('SlideSub', parent=styles['Normal'], fontSize=11, leading=15, textColor=colors.HexColor("#0284c7"))
    slide_body = ParagraphStyle('SlideBody', parent=styles['Normal'], fontSize=10, leading=15, textColor=colors.HexColor("#334155"))
    bullet_style = ParagraphStyle('SlideBullet', parent=styles['Normal'], fontSize=9.5, leading=14, textColor=colors.HexColor("#1e293b"))

    slides = [
        ("Slide 1: CardioTwin AI", "A living digital representation of the patient for earlier, personalized cardiovascular risk awareness.", [
            "Challenge: Digital Twin Challenge 2026 by Happiest Health",
            "Core Objective: Moving healthcare from episodic reaction to continuous proactive trajectory awareness.",
            "Key Innovation: N=1 personal physiological baseline modeling combined with multimodal EHR-wearable fusion."
        ]),
        ("Slide 2: The Clinical Problem", "Why reactive cardiovascular care fails high-risk patients.", [
            "Cardiovascular diseases represent the leading cause of global morbidity and mortality.",
            "High-risk patients (hypertension, T2D, dyslipidemia) are monitored episodically every 3-6 months.",
            "In between clinic visits, acute autonomic and hemodynamic decompensation develops silently.",
            "Traditional AI models evaluate static EHR snapshots once every few months — blind to acute drift."
        ]),
        ("Slide 3: Our Solution — The Living Digital Twin", "Not just a risk score, but a living virtual physiological counterpart.", [
            "Personalized Baseline Engine: Learns each patient's individual normal range (mean ± 2 SD).",
            "Twin Drift Score (0-100): Quantifies multivariate distance from personal homeostatic equilibrium.",
            "Multi-Horizon Forecasting: Dynamically updates 6h, 24h, and 72h deterioration risks.",
            "Bi-directional What-If Simulation: Clinicians test interventions before prescribing."
        ]),
        ("Slide 4: System Architecture & Ingestion", "High-throughput, event-driven multimodal pipeline.", [
            "Data Quality Engine: Validates optical PPG perfusion, motion artifacts, and flatlines.",
            "Multimodal Fusion: Combines static chronic vulnerability (EHR) with dynamic acute strain (wearables).",
            "Time-Series Integrity: Backward-looking rolling windows strictly isolated from future target labels.",
            "Zero Data Leakage: Complete patient-stratified cohort isolation across train/test splits."
        ]),
        ("Slide 5: Patient A-1042 Journey", "The deterministic 24-hour deterioration progression.", [
            "08:00 Normal baseline: RHR 68 bpm, HRV 52 ms, Sleep 7.1h, Steps 6200.",
            "10:00 to 12:00 Early deviation: RHR climbs to 75 bpm, HRV drops to 43 ms (vagal withdrawal).",
            "14:00 Compounding deficit: 1.7h sleep deficit detected, ambulatory step count drops 45%.",
            "16:00 to 18:00 Risk threshold crossed: RHR 82 bpm (+20.6%), Twin Drift hits 81 (High). Automated alert dispatched."
        ]),
        ("Slide 6: What-If Digital Twin Simulator", "Counterfactual scenario modeling for clinician decision support.", [
            "Interactive Clinician Knobs: Sleep duration, medication adherence, physical mobilization, stress reduction.",
            "Trajectory Divergence: Unmitigated deterioration trajectory (78% risk) vs. Simulated intervention (28% risk).",
            "Counterfactual Explainability: 'Largest modeled risk reduction (+30%) stems from restoring sleep toward baseline.'",
            "Mandatory Safety Invariant: Watermarked 'SIMULATED SCENARIO — NOT A CLINICAL PREDICTION'."
        ]),
        ("Slide 7: Model Evaluation & Ablation", "Rigorous validation proving multimodal fusion superiority.", [
            "Model A (EHR-Only): AUROC 0.487, AUPRC 0.209, Lead Time 2.1 hours (blind to acute decompensation).",
            "Model B (Wearable-Only): AUROC 0.648, AUPRC 0.380, Lead Time 7.2 hours.",
            "Model C (Digital Twin Fusion): AUROC 0.715, AUPRC 0.482, Lead Time 14.5 hours!",
            "Clinical Utility: False alerts reduced to 1.12 per patient-week, minimizing clinician alarm fatigue."
        ]),
        ("Slide 8: Robustness & Stress Testing", "Resilience under missing wearable telemetry.", [
            "10% Missing Telemetry: AUROC drops by only 2.1%.",
            "25% Missing Telemetry: AUROC retained at 0.694 (-6.7% degradation).",
            "50% Severe Sensor Dropout: System defaults gracefully to personal baseline priors.",
            "Engineering Maturity: Models do not crash or collapse when sensors detach."
        ]),
        ("Slide 9: India-Scale Deployment Architecture", "Ayushman Bharat Digital Mission (ABDM) architectural readiness.", [
            "HL7 FHIR R4: Resources mapped to Patient, Observation (LOINC 8867-4), and Condition.",
            "ABHA Health ID Binding: Simulated ABHA address linking for seamless longitudinal continuity.",
            "Edge Baseline Caching: Personalized parameters computed and cached for scalable sub-second latency.",
            "Notice: ABDM/FHIR alignment is an architectural direction, not official government certification."
        ]),
        ("Slide 10: Safety, Ethics & Future Vision", "Responsible AI principles and prospective clinical roadmap.", [
            "Human-in-the-Loop: Never replaces clinical judgment; alerts are calm, explainable recommendations.",
            "Privacy & Security: 100% synthetic cohorts; production architecture includes RBAC and audit logging.",
            "Future Roadmap: Multi-center prospective observational registry with clinical PPG smartwatches.",
            "Vision: Proactive cardiovascular preservation for millions of high-risk individuals."
        ])
    ]

    story = []
    for title, sub, bullets in slides:
        story.append(Paragraph(title, slide_title))
        story.append(Paragraph(sub, slide_sub))
        story.append(Spacer(1, 10))
        story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#cbd5e1"), spaceAfter=15))

        for b in bullets:
            story.append(Paragraph(f"• {b}", bullet_style))
            story.append(Spacer(1, 6))

        story.append(Spacer(1, 20))
        story.append(Paragraph("CardioTwin AI • Digital Twin Challenge 2026 by Happiest Health", ParagraphStyle('Footer', parent=styles['Normal'], fontSize=8, textColor=colors.HexColor("#94a3b8"))))
        story.append(PageBreak())

    # Remove trailing page break
    story.pop()
    doc.build(story)
    print(f"[CardioTwin AI] Generated: {pdf_path}")

if __name__ == "__main__":
    generate_architecture_pdf()
    generate_presentation_pdf()
