"""
confidence_scoring.py

Purpose:
    Heuristically calculate a confidence score for a trade based on various risk
    and data quality factors.

Usage:
    from src.scoring.confidence_scoring import compute_confidence_score

Author: Jason Chau
Date: 2026-04-16
"""

from src.data.schema import Trade
from typing import Dict

from src.decisioning.schema import *

def compute_confidence_score(trade: Trade, evidence: ComplianceEvidenceSchema | None = None) -> Dict[str, float]:
    """
    Returns structured confidence:
    {
        "overall": float,
        "data_completeness": float,
        "directional_consistency": float,
        "rule_coverage": float
    }
    """

    if evidence is None:
        evidence = ComplianceEvidenceSchema(
            violations=[],
            concern_signals=[],
            mitigating_factors=[],
            evidence_quality=[],
            audit_reasoning=""
        )

    violations = set(evidence.violations)
    concern_signals = set(evidence.concern_signals)
    evidence_quality = set(evidence.evidence_quality)
    mitigation_count = len(evidence.mitigating_factors)


    # -----------------------------
    # 1. DATA COMPLETENESS
    # -----------------------------
    data_completeness = 1.0

    if ViolationType.KYC_MISSING in violations:
        data_completeness -= 0.3  # critical missing info

    if EvidenceQualityType.KYC_UNCERTAIN in evidence_quality:
        data_completeness -= 0.2

    if EvidenceQualityType.MISSING_RATIONALE in evidence_quality or EvidenceQualityType.WEAK_RATIONALE in evidence_quality:
        data_completeness -= 0.1
    
    if EvidenceQualityType.MINIMAL_ADVISOR_NOTES in evidence_quality:
        data_completeness -= 0.1

    data_completeness = max(0.0, min(data_completeness, 1.0))


    # -----------------------------
    # 2. DIRECTIONAL CONSISTENCY
    # -----------------------------
    underaggressive_signals = []
    overaggressive_signals = []

    if ViolationType.RISK_TOLERANCE_VIOLATION in violations:
        overaggressive_signals.append("suitability")

    if ViolationType.EXPERIENCE_COMPLEXITY_MISMATCH in violations:
        overaggressive_signals.append("experience")

    if ConcernSignalType.AGGRESSIVE_FOR_SHORT_HORIZON in concern_signals:
        overaggressive_signals.append("horizon")

    if ConcernSignalType.AGGRESSIVE_FOR_OBJECTIVE in concern_signals:
        overaggressive_signals.append("objective")

    if ConcernSignalType.OVEREXPOSURE in concern_signals:
        overaggressive_signals.append("overexposure")

    if ConcernSignalType.TOO_CONSERVATIVE_FOR_RISK_PROFILE in concern_signals:
        underaggressive_signals.append("too_conservative")
    
    if ConcernSignalType.TOO_CONSERVATIVE_FOR_OBJECTIVE in concern_signals:
        underaggressive_signals.append("too_conservative_objective")

    if ConcernSignalType.TOO_CONSERVATIVE_FOR_HORIZON in concern_signals:
        underaggressive_signals.append("too_conservative_horizon")
    
    total_signals = len(underaggressive_signals) + len(overaggressive_signals)

    if total_signals == 0:
        directional_consistency = 0.7  # neutral baseline
    elif total_signals == 1:
        directional_consistency = 0.6  # weak evidence, even if "consistent"
    else:
        dominant = max(len(underaggressive_signals), len(overaggressive_signals))
        directional_consistency = dominant / total_signals

    # if evidence.mitigating_factors:
    #     directional_consistency *= (1 - min(mitigation_count * 0.05, 0.15))

    directional_consistency = max(0.0, min(directional_consistency, 1.0))


    # -----------------------------
    # 3. RULE COVERAGE (evidence strength)
    # -----------------------------
    rule_coverage = 0.5  # neutral baseline

    strong_violations = sum([
        ViolationType.RISK_TOLERANCE_VIOLATION in violations,
        ViolationType.EXPERIENCE_COMPLEXITY_MISMATCH in violations,
        ConcernSignalType.SENIOR_CLIENT_RISK in concern_signals,
    ])

    soft_signals = sum([
        ConcernSignalType.AGGRESSIVE_FOR_SHORT_HORIZON in concern_signals,
        ConcernSignalType.AGGRESSIVE_FOR_OBJECTIVE in concern_signals,
        ConcernSignalType.OVEREXPOSURE in concern_signals,
        EvidenceQualityType.KYC_UNCERTAIN in evidence_quality,
        EvidenceQualityType.MISSING_RATIONALE in evidence_quality or EvidenceQualityType.WEAK_RATIONALE in evidence_quality,
        EvidenceQualityType.MINIMAL_ADVISOR_NOTES in evidence_quality, # don't have deterministic helper function here
    ])

    # Strong violations → high certainty
    if strong_violations >= 2:
        rule_coverage += 0.3
    elif strong_violations == 1:
        rule_coverage += 0.15

    # Procedural certainty (KYC)
    if ViolationType.KYC_MISSING in violations:
        rule_coverage += 0.25

    # Soft signals handling (aligned vs conflicting)
    if strong_violations == 0 and soft_signals >= 2:
        if directional_consistency > 0.7:
            rule_coverage += 0.15
        else:
            rule_coverage -= 0.2

    # Clean cases → also high confidence
    if (
        strong_violations == 0
        and soft_signals == 0
        and data_completeness > 0.8
    ):
        rule_coverage += 0.2

    rule_coverage -= mitigation_count * 0.05

    rule_coverage = max(0.0, min(rule_coverage, 1.0))


    # -----------------------------
    # 4. OVERALL CONFIDENCE
    # -----------------------------
    overall = (
        0.4 * data_completeness +
        0.3 * directional_consistency +
        0.3 * rule_coverage
    )

    overall = max(0.0, min(overall, 1.0))


    return {
        "overall": round(overall, 3),
        "data_completeness": round(data_completeness, 3),
        "directional_consistency": round(directional_consistency, 3),
        "rule_coverage": round(rule_coverage, 3)
    }