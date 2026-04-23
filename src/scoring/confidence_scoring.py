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

from src.decisioning.violation_rules import (
    is_kyc_violation,
    is_suitability_violation,
    is_experience_violation
)

from src.decisioning.risk_signals import (
    is_kyc_uncertain,
    is_overexposure,
    is_advisor_history_high_risk
)

from src.decisioning.conflict_detection import has_conflicting_signals


def compute_confidence_score(trade: Trade) -> float:
    """
    Computes a confidence score (0.0–1.0) representing how confident
    the system is in its compliance prediction.

    Higher = more confident
    Lower = more uncertain / ambiguous
    """

    # Start from a high baseline
    confidence = 0.9

    # Critical uncertainty: missing KYC
    if is_kyc_violation(trade):
        return 0.3  # immediate low confidence

    # Data quality issues
    if is_kyc_uncertain(trade):
        confidence -= 0.2

    if not trade.has_rationale:
        confidence -= 0.1

    # Ambiguity: conflicting signals
    if has_conflicting_signals(trade):
        confidence -= 0.25

    # Contextual risk factors (not violations, but add uncertainty)
    if is_overexposure(trade):
        confidence -= 0.1

    if is_advisor_history_high_risk(trade):
        confidence -= 0.05

    # Strong, clear cases increase confidence
    violations = sum([
        is_suitability_violation(trade),
        is_experience_violation(trade),
    ])

    if violations >= 2:
        confidence += 0.1  # clearly non-compliant

    if (
    violations == 0
    and not is_kyc_uncertain(trade)
    and not has_conflicting_signals(trade)
    ):
        confidence += 0.1  # clearly clean


    # Clamp to valid range
    return max(0.0, min(confidence, 1.0))