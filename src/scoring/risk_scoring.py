"""
risk_scoring.py

Purpose:
    Heuristically calculate a risk score for a trade based on client profile, advisor, and trade
    characteristics.

Usage:
    from src.scoring.risk_scoring import compute_risk_score

Author: Jason Chau
Date: 2026-04-16
"""

from src.data.schema import Trade
from src.decisioning.schema import *

WEIGHTS = {
    "kyc_violation": 40,
    "suitability": 40,
    "experience": 30,
    "aggressive_for_horizon": 15,
    "aggressive_for_objective": 10,
    "overexposure": 15,
    "advisor_history": 10,
    "senior_client": 10,
    "kyc_uncertain": 10,
    "risk_too_low": 5,
    "conservative_for_horizon": 5,
    "conservative_for_objective": 5
}

def compute_risk_score(trade: Trade, evidence: ComplianceEvidenceSchema) -> int:
    """
    Computes a heuristic risk score (0–100+) based on:
    - Hard violations (strong signals)
    - Soft signals (contextual / ambiguous risk factors)

    Priority:
    1. LLM evidence
    2. heuristic fallback

    This is a SYSTEM PREDICTION, not ground truth.
    """

    if evidence is None:
        evidence = ComplianceEvidenceSchema(
            violations=[],
            concern_signals=[],
            mitigating_factors=[],
            evidence_quality=[],
            audit_reasoning=""
        )
        
    regulatory_risk = 0
    contextual_risk = 0

    violations = set(evidence.violations)
    concern_signals = set(evidence.concern_signals)
    evidence_quality = set(evidence.evidence_quality)

    # --------------------------------------------------
    # HARD REGULATORY VIOLATIONS
    # --------------------------------------------------

    if ViolationType.KYC_MISSING in violations:
        regulatory_risk += WEIGHTS["kyc_violation"]

    if ViolationType.RISK_TOLERANCE_VIOLATION in violations:
        regulatory_risk += WEIGHTS["suitability"]

    if ViolationType.EXPERIENCE_COMPLEXITY_MISMATCH in violations:
        regulatory_risk += WEIGHTS["experience"]

    # --------------------------------------------------
    # CONTEXTUAL SIGNALS
    # --------------------------------------------------

    if ConcernSignalType.OVEREXPOSURE in concern_signals:
        contextual_risk += WEIGHTS["overexposure"]
    
    if ConcernSignalType.HIGH_RISK_ADVISOR in concern_signals:
        contextual_risk += WEIGHTS["advisor_history"]

    if ConcernSignalType.SENIOR_CLIENT_RISK in concern_signals:
        contextual_risk += WEIGHTS["senior_client"]

    if EvidenceQualityType.KYC_UNCERTAIN in evidence_quality:
        contextual_risk += WEIGHTS["kyc_uncertain"]

    if ConcernSignalType.AGGRESSIVE_FOR_SHORT_HORIZON in concern_signals:
        contextual_risk += WEIGHTS["aggressive_for_horizon"]

    if ConcernSignalType.AGGRESSIVE_FOR_OBJECTIVE in concern_signals:
        contextual_risk += WEIGHTS["aggressive_for_objective"]

    # --------------------------------------------------
    # LOW IMPACT SIGNALS
    # --------------------------------------------------

    if ConcernSignalType.TOO_CONSERVATIVE_FOR_RISK_PROFILE in concern_signals:
        contextual_risk += WEIGHTS["risk_too_low"]

    if ConcernSignalType.TOO_CONSERVATIVE_FOR_HORIZON in concern_signals:
        contextual_risk += WEIGHTS["conservative_for_horizon"]

    if ConcernSignalType.TOO_CONSERVATIVE_FOR_OBJECTIVE in concern_signals:
        contextual_risk += WEIGHTS["conservative_for_objective"]

    score = regulatory_risk + contextual_risk

    return min(score, 100)