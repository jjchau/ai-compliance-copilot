"""
policy_signal_mapping.py

Purpose:
    Centralized mapping of policy IDs to their corresponding relevance check functions.

Usage:
    from src.policy.policy_signal_mapping import POLICY_RELEVANCE_CHECKS

Author: Jason Chau
Date: 2026-05-14
"""

from src.decisioning.violation_rules import (
    is_kyc_violation,
    is_suitability_violation,
    is_experience_violation
)
from src.decisioning.risk_signals import (
    is_kyc_uncertain,
    is_investment_too_aggressive_for_objective,
    is_investment_too_conservative_for_objective,
    is_investment_too_aggressive_for_horizon,
    is_overexposure,
    is_advisor_history_high_risk
)
from src.decisioning.documentation_signals import is_missing_rationale
from src.decisioning.conflict_detection import has_conflicting_signals

POLICY_RELEVANCE_CHECKS = {

    "POL-001-SUITABILITY":
        lambda t:
            is_suitability_violation(t)
            or is_experience_violation(t)
            or is_investment_too_aggressive_for_objective(t)
            or is_investment_too_aggressive_for_horizon(t)
            or is_overexposure(t),

    "POL-002-KYC":
        lambda t:
            is_kyc_violation(t)
            or is_kyc_uncertain(t)
            or has_conflicting_signals(t),

    "POL-003-SURVEILLANCE":
        lambda t:
            is_kyc_violation(t)
            or is_kyc_uncertain(t)
            or is_suitability_violation(t)
            or is_experience_violation(t)
            or is_missing_rationale(t)
            or is_advisor_history_high_risk(t),

    "POL-004-CONCENTRATION":
        lambda t:
            is_overexposure(t),

    "POL-005-SENIOR-VULNERABLE-CLIENTS":
        lambda t:
            t.client_age >= 65,

    "POL-006-HIGH-RISK-PRODUCTS":
        lambda t:
            t.investment_type == "Options",

    "POL-007-DOCUMENTATION-STANDARDS":
        lambda t:
            is_missing_rationale(t),

    "POL-008-EXCEPTIONS-AND-OVERRIDES":
        lambda t:
            False,

    "POL-009-CONFLICT-OF-INTEREST":
        lambda t:
            False,

    "POL-010-CLIENT-OBJECTIVE":
        lambda t:
            is_investment_too_aggressive_for_objective(t)
            or is_investment_too_conservative_for_objective(t)
}