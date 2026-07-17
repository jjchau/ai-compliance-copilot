"""
labeling.py

Purpose:
    Logic for aggregating and assigning ground truth labels for evaluation and analysis.

Usage:
    from src.decisioning.labeling import compute_true_compliance, assign_case_type, etc.

Author: Jason Chau
Date: 2026-04-16
"""

from src.data.schema import (
    Trade,
    SeverityTier,
    WorkflowBucket
)
from src.decisioning.violation_rules import  *
from src.decisioning.risk_signals import *
from src.decisioning.documentation_signals import is_missing_rationale
from src.decisioning.conflict_detection import has_conflicting_signals
from typing import Literal

from src.policy.ground_truth import get_relevant_policies

POLICY_PRECEDENCE = [
    "POL-002-KYC",
    "POL-001-SUITABILITY",
    "POL-006-HIGH-RISK-PRODUCTS",
    "POL-005-SENIOR-VULNERABLE-CLIENTS",
    "POL-004-CONCENTRATION",
    "POL-007-DOCUMENTATION-STANDARDS",
    "POL-010-CLIENT-OBJECTIVE",
    "POL-003-SURVEILLANCE"
]

def compute_true_compliance(trade: Trade) -> bool:
    violations = [
        is_kyc_violation(trade),
		is_suitability_violation(trade),
        is_experience_violation(trade)
	]
    return not any(violations)

def assign_case_type(trade: Trade) -> Literal["Suitability Violation", "KYC Missing", "Insufficient Experience", "Risk Signal", "Aligned Recommendation"]:
    if is_kyc_violation(trade):
        return "KYC Missing"
    elif is_suitability_violation(trade):
        return "Suitability Violation"
    elif is_experience_violation(trade):
        return "Insufficient Experience"
    elif any([is_investment_too_aggressive_for_horizon(trade), is_investment_too_aggressive_for_objective(trade), is_overexposure(trade), is_kyc_uncertain(trade) ]):
        return "Risk Signal"
    else:
        return "Aligned Recommendation"

def assign_difficulty(trade: Trade) -> Literal['Easy', 'Medium', 'Hard']:
    hard_violations = sum([
        is_kyc_violation(trade),
        is_suitability_violation(trade),
        is_experience_violation(trade)
    ])

    soft_signals = sum([
        is_investment_too_aggressive_for_horizon(trade),
        is_investment_too_aggressive_for_objective(trade),
        is_overexposure(trade),
        is_kyc_uncertain(trade)
    ])

    if hard_violations == 0 and soft_signals == 0:
        return "Easy"

    if hard_violations >= 1 and soft_signals <= 1:
        return "Easy"

    if hard_violations == 1:
        return "Medium"

    return "Hard"

def assign_severity_tier(trade: Trade) -> SeverityTier:
    """
    Ground-truth compliance impact severity.

    Low:
        Minor procedural concerns.

    Medium:
        Meaningful suitability concerns requiring review.

    High:
        Clear regulatory violations.
    """

    hard_violations = sum([
        is_kyc_violation(trade),
        is_suitability_violation(trade),
        is_experience_violation(trade)
    ])

    medium_signals = sum([
        is_kyc_uncertain(trade),
        is_overexposure(trade),
        is_investment_too_aggressive_for_horizon(trade),
        is_investment_too_aggressive_for_objective(trade),
        has_conflicting_signals(trade)
    ])

    low_signals = sum([
        is_missing_rationale(trade),
        is_advisor_history_high_risk(trade)
    ])

    # High-impact compliance failures
    if hard_violations >= 1:
        return "High"

    # Material suitability concerns
    if medium_signals >= 2:
        return "Medium"

    if medium_signals == 1:
        return "Medium"

    # Procedural/documentation concerns only
    if low_signals >= 1:
        return "Low"

    return "Low"

def assign_expected_workflow_bucket(
    trade: Trade
) -> WorkflowBucket:

    hard_violations = sum([
        is_kyc_violation(trade),
        is_suitability_violation(trade),
        is_experience_violation(trade)
    ])

    medium_signals = sum([
        is_kyc_uncertain(trade),
        is_overexposure(trade),
        is_investment_too_aggressive_for_horizon(trade),
        is_investment_too_aggressive_for_objective(trade),
        has_conflicting_signals(trade)
    ])

    low_signals = sum([
        is_missing_rationale(trade),
        is_advisor_history_high_risk(trade)
    ])

    # Compound severe failures
    if hard_violations >= 2:
        return "Urgent"

    # Single severe failure
    if hard_violations == 1:
        return "Priority"

    # Multiple meaningful concerns
    if medium_signals >= 3:
        return "Priority"

    # Any meaningful concern
    if medium_signals >= 1:
        return "Queue"

    # Documentation / procedural concerns
    if low_signals >= 2:
        return "Queue"

    return "Auto_pass"

def assign_primary_policy(trade: Trade) -> str:

    relevant = get_relevant_policies(trade)

    for policy in POLICY_PRECEDENCE:
        if policy in relevant:
            return policy

    return ""