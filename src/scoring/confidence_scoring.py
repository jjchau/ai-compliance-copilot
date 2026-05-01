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

from src.decisioning.violation_rules import (
    is_kyc_violation,
    is_suitability_violation,
    is_experience_violation
)

from src.decisioning.risk_signals import (
    is_kyc_uncertain,
    is_overexposure,
    is_investment_too_agressive_for_horizon,
    is_investment_too_aggressive_for_objective,
    is_risk_too_low_for_profile,
    is_investment_too_conservative_for_horizon,
    is_investment_too_conservative_for_objective
)

from src.decisioning.conflict_detection import has_conflicting_signals


from typing import Dict

def compute_confidence_score(trade: Trade) -> Dict[str, float]:
    """
    Returns structured confidence:
    {
        "overall": float,
        "data_completeness": float,
        "signal_consistency": float,
        "rule_coverage": float
    }
    """

    # -----------------------------
    # 1. DATA COMPLETENESS
    # -----------------------------
    data_completeness = 1.0

    if is_kyc_violation(trade):
        data_completeness -= 0.3  # critical missing info

    if is_kyc_uncertain(trade):
        data_completeness -= 0.2

    if not trade.has_rationale:
        data_completeness -= 0.1

    data_completeness = max(0.0, min(data_completeness, 1.0))


    # -----------------------------
    # 2. SIGNAL CONSISTENCY (directional)
    # -----------------------------
    positive_signals = []
    negative_signals = []

    if is_suitability_violation(trade):
        negative_signals.append("suitability")

    if is_experience_violation(trade):
        negative_signals.append("experience")

    if is_investment_too_agressive_for_horizon(trade):
        negative_signals.append("horizon")

    if is_investment_too_aggressive_for_objective(trade):
        negative_signals.append("objective")

    if is_overexposure(trade):
        negative_signals.append("overexposure")

    if is_risk_too_low_for_profile(trade):
        positive_signals.append("too_conservative")
    
    if is_investment_too_conservative_for_objective(trade):
        positive_signals.append("too_conservative_objective")

    if is_investment_too_conservative_for_horizon(trade):
        positive_signals.append("too_conservative_horizon")

    total_signals = len(positive_signals) + len(negative_signals)

    if total_signals == 0:
        signal_consistency = 0.7  # neutral baseline
    elif total_signals == 1:
        signal_consistency = 0.6  # weak evidence, even if "consistent"
    else:
        dominant = max(len(positive_signals), len(negative_signals))
        signal_consistency = dominant / total_signals

    signal_consistency = max(0.0, min(signal_consistency, 1.0))


    # -----------------------------
    # 3. RULE COVERAGE (evidence strength)
    # -----------------------------
    rule_coverage = 0.5  # neutral baseline

    strong_violations = sum([
        is_suitability_violation(trade),
        is_experience_violation(trade),
    ])

    soft_signals = sum([
        is_investment_too_agressive_for_horizon(trade),
        is_investment_too_aggressive_for_objective(trade),
        is_overexposure(trade),
    ])

    # Strong violations → high certainty
    if strong_violations >= 2:
        rule_coverage += 0.3
    elif strong_violations == 1:
        rule_coverage += 0.15

    # Procedural certainty (KYC)
    if is_kyc_violation(trade):
        rule_coverage += 0.25

    # Soft signals handling (aligned vs conflicting)
    if strong_violations == 0 and soft_signals >= 2:
        if signal_consistency > 0.7:
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

    rule_coverage = max(0.0, min(rule_coverage, 1.0))


    # -----------------------------
    # 4. OVERALL CONFIDENCE
    # -----------------------------
    overall = (
        0.4 * data_completeness +
        0.3 * signal_consistency +
        0.3 * rule_coverage
    )

    overall = max(0.0, min(overall, 1.0))


    return {
        "overall": round(overall, 3),
        "data_completeness": round(data_completeness, 3),
        "signal_consistency": round(signal_consistency, 3),
        "rule_coverage": round(rule_coverage, 3)
    }