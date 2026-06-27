"""
compliance_scoring.py

Purpose:
    Deterministically convert LLM evidence findings into a
    compliance probability.

Author: Jason Chau
Date: 2026-06-15
"""

from src.decisioning.schema import *


PROBLEM_WEIGHTS = {
    ViolationType.KYC_MISSING: 0.80,
    ViolationType.RISK_TOLERANCE_VIOLATION: 0.60,
    ViolationType.EXPERIENCE_COMPLEXITY_MISMATCH: 0.30,
    # ConcernSignalType.OVEREXPOSURE: 0.20,
    # ConcernSignalType.AGGRESSIVE_FOR_SHORT_HORIZON: 0.15,
    # ConcernSignalType.AGGRESSIVE_FOR_OBJECTIVE: 0.20,
    # # ConcernSignalType.HIGH_RISK_ADVISOR: 0.15,
    # ConcernSignalType.SENIOR_CLIENT_RISK: 0.25,
    # EvidenceQualityType.KYC_UNCERTAIN: 0.25,
    # EvidenceQualityType.MISSING_RATIONALE: 0.02,
    # EvidenceQualityType.WEAK_RATIONALE: 0.01,
    # EvidenceQualityType.MINIMAL_ADVISOR_NOTES: 0.01,
    # # ConcernSignalType.TOO_CONSERVATIVE_FOR_RISK_PROFILE: 0.05,
    # # ConcernSignalType.TOO_CONSERVATIVE_FOR_HORIZON: 0.05,
    # # ConcernSignalType.TOO_CONSERVATIVE_FOR_OBJECTIVE: 0.05,
}


def compute_compliance_probability(evidence: ComplianceEvidenceSchema) -> dict[str, float | bool]:

    score = 0.0

    for violation in evidence.violations:
        score += PROBLEM_WEIGHTS.get(violation, 0.0)

    # for risk in evidence.concern_signals:
    #     score += PROBLEM_WEIGHTS.get(risk, 0.0)

    # for missing_evidence in evidence.evidence_quality:
    #     score += PROBLEM_WEIGHTS.get(missing_evidence, 0.0)

    non_compliance_probability = min(score, 1.0)

    compliance_probability = round(1.0 - non_compliance_probability, 3)

    compliance_label = compliance_probability >= 0.80

    return {
        "compliance_probability": compliance_probability,
        "compliance_label": compliance_label
    }