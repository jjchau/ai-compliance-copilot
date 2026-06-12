"""
scenario_builders.py

Purpose:
    Applies deterministic compliance scenarios to otherwise
    realistic investor profiles.

Each builder:

    Input:
        Realistic Trade profile

    Output:
        Modified Trade profile representing
        a specific compliance scenario.

Author: Jason Chau
Date: 2026-06-04
"""

from pathlib import Path
import sys

sys.path.append(
    str(Path(__file__).resolve().parents[2])
)

from copy import deepcopy

from src.data.schema import Trade

# ==========================================================
# Utility
# ==========================================================

def clone(trade: Trade) -> Trade:
    """
    Safe mutation helper.
    """
    return deepcopy(trade)


# ==========================================================
# 1. ALIGNED RECOMMENDATION
# ==========================================================

def build_aligned_recommendation(trade: Trade) -> Trade:
    """
    Clean compliant case.

    Should generate:

    - no hard violations
    - minimal soft signals
    - high confidence
    - escalation = none
    """

    t = clone(trade)

    t.kyc_completeness = "Complete"

    return t


# ==========================================================
# 2. KYC MISSING
# ==========================================================

def build_kyc_missing_case(trade: Trade) -> Trade:
    """
    Procedural violation.

    Should trigger:

    - KYC violation
    - elevated risk score
    """

    t = clone(trade)

    t.kyc_completeness = "Missing"

    return t


# ==========================================================
# 3. SUITABILITY VIOLATION
# ==========================================================

def build_suitability_violation_case(trade: Trade) -> Trade:
    """
    Low-risk client placed into high-risk product.

    Triggers:

    is_suitability_violation()
    """

    t = clone(trade)

    t.risk_tolerance = "Low"

    t.investment_objective = "Preservation"

    t.investment_type = "Stocks"

    return t


# ==========================================================
# 4. EXPERIENCE VIOLATION
# ==========================================================

def build_experience_violation_case(trade: Trade) -> Trade:
    """
    Beginner client purchasing options.
    """

    t = clone(trade)

    t.investment_experience = "Beginner"

    t.investment_type = "Options"

    return t


# ==========================================================
# 5. RISK SIGNAL
# ==========================================================

def build_risk_signal_case(trade: Trade) -> Trade:
    """
    Soft-signal case.

    No direct violation required.

    Produces:

    - overexposure
    - KYC uncertainty
    - aggressive horizon mismatch

    Useful for queue review testing.
    """

    t = clone(trade)

    t.kyc_completeness = "Uncertain"

    t.investment_amount = round(
        t.client_income * 0.50,
        2
    )

    if t.investment_time_horizon == "Short":
        t.investment_type = "Stocks"

    return t


# ==========================================================
# 6. LOW PRIORITY EXCEPTION
# ==========================================================

def build_low_priority_exception_case(trade: Trade) -> Trade:
    """
    Designed to simulate:

    AI thinks something looks suspicious,
    quantitative engine says risk is low.

    Goal:

    escalation = queue
    priority score suppressed

    Typical example:

    missing rationale
    uncertain documentation
    otherwise harmless trade
    """

    t = clone(trade)

    t.kyc_completeness = "Uncertain"

    t.investment_amount = min(
        t.client_income * 0.05,
        2500
    )

    return t


# ==========================================================
# 7. RETIREE SPECULATION
# ==========================================================

def build_retiree_speculation_case(trade: Trade) -> Trade:
    """
    POL-005-SENIOR-VULNERABLE-CLIENTS style scenario.

    Senior client
    Preservation objective
    Speculative product
    """

    t = clone(trade)

    t.client_age = 75

    t.risk_tolerance = "Low"

    t.investment_objective = "Preservation"

    t.investment_type = "Stocks"

    return t


# ==========================================================
# 8. RETIREE OPTIONS CASE
# ==========================================================

def build_retiree_options_case(trade: Trade) -> Trade:
    """
    Strong senior suitability failure.
    """

    t = clone(trade)

    t.client_age = 78

    t.risk_tolerance = "Low"

    t.investment_objective = "Preservation"

    t.investment_experience = "Beginner"

    t.investment_type = "Options"

    return t


# ==========================================================
# 9. OVEREXPOSURE CASE
# ==========================================================

def build_overexposure_case(trade: Trade) -> Trade:
    """
    Large allocation relative to income.

    Triggers:

    is_overexposure()
    """

    t = clone(trade)

    t.investment_amount = round(
        t.client_income * 0.60,
        2
    )

    return t


# ==========================================================
# 10. AGGRESSIVE HORIZON CASE
# ==========================================================

def build_aggressive_horizon_case(trade: Trade) -> Trade:
    """
    Short horizon client purchasing stocks.
    """

    t = clone(trade)

    t.investment_time_horizon = "Short"

    t.investment_type = "Stocks"

    return t


# ==========================================================
# 11. AGGRESSIVE OBJECTIVE CASE
# ==========================================================

def build_aggressive_objective_case(trade: Trade) -> Trade:
    """
    Preservation objective + Stocks.
    """

    t = clone(trade)

    t.investment_objective = "Preservation"

    t.investment_type = "Stocks"

    return t


# ==========================================================
# 12. CONFLICTING SIGNAL CASE
# ==========================================================

def build_conflicting_signal_case(trade: Trade) -> Trade:
    """
    Useful for confidence testing.

    Example:

    High risk tolerance
    but conservative investment.
    """

    t = clone(trade)

    t.risk_tolerance = "High"

    t.investment_objective = "Growth"

    t.investment_type = "T-Bills"

    t.investment_time_horizon = "Long"

    return t


# ==========================================================
# 13. HIGH-RISK ADVISOR CASE
# ==========================================================

def build_high_risk_advisor_case(trade: Trade) -> Trade:
    """
    Same trade,
    advisor history introduces concern.
    """

    t = clone(trade)

    t.advisor_history_risk = "High"

    return t


# ==========================================================
# 14. COMPOUND VIOLATION
# ==========================================================

def build_compound_violation_case(trade: Trade) -> Trade:
    """
    Designed to reach:

    risk_score >= 80

    and frequently trigger URGENT.
    """

    t = clone(trade)

    t.kyc_completeness = "Missing"

    t.risk_tolerance = "Low"

    t.investment_objective = "Preservation"

    t.investment_experience = "Beginner"

    t.investment_type = "Options"

    t.investment_amount = round(
        t.client_income * 0.70,
        2
    )

    t.advisor_history_risk = "High"

    return t


# ==========================================================
# Scenario Registry
# ==========================================================

SCENARIO_BUILDERS = {
    "Aligned Recommendation": build_aligned_recommendation,
    "KYC Missing": build_kyc_missing_case,
    "Suitability Violation": build_suitability_violation_case,
    "Insufficient Experience": build_experience_violation_case,
    "Risk Signal": build_risk_signal_case,
    "Low Priority Exception": build_low_priority_exception_case,
    "Retiree Speculation": build_retiree_speculation_case,
    "Retiree Options": build_retiree_options_case,
    "Overexposure": build_overexposure_case,
    "Aggressive Horizon": build_aggressive_horizon_case,
    "Aggressive Objective": build_aggressive_objective_case,
    "Conflicting Signals": build_conflicting_signal_case,
    "High Risk Advisor": build_high_risk_advisor_case,
    "Compound Violation": build_compound_violation_case
}