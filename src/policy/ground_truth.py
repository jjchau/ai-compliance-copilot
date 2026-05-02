from typing import List
from src.data.schema import Trade
from src.decisioning.violation_rules import (
    is_kyc_violation,
    is_suitability_violation,
    is_experience_violation
)
from src.decisioning.risk_signals import (
    is_kyc_uncertain,
    is_investment_too_aggressive_for_objective,
    is_investment_too_agressive_for_horizon,
    is_overexposure,
    is_advisor_history_high_risk
)
from src.decisioning.conflict_detection import has_conflicting_signals

def get_relevant_policies(trade: Trade) -> List[str]:
    """
    Ground truth mapping:
    Returns all policies that SHOULD apply to this trade.
    Deterministic and aligned with rule logic.
    """

    policies = []

    # --- KYC ---
    if is_kyc_violation(trade):
        policies.append("POLICY_KYC_001")

    if is_kyc_uncertain(trade):
        policies.append("POLICY_KYC_002")

    if has_conflicting_signals(trade):
        policies.append("POLICY_KYC_003")

    # --- Suitability ---
    if is_suitability_violation(trade):
        policies.append("POLICY_SUIT_001")

    if is_investment_too_aggressive_for_objective(trade):
        policies.append("POLICY_SUIT_002")

    if is_investment_too_agressive_for_horizon(trade):
        policies.append("POLICY_SUIT_003")

    # --- Experience ---
    if is_experience_violation(trade):
        policies.append("POLICY_EXP_001")

    # --- Portfolio risk ---
    if is_overexposure(trade):
        policies.append("POLICY_RISK_001")

    # (future) leverage
    # if is_leverage_violation(trade):
    #     policies.append("POLICY_RISK_002")

    # --- Documentation ---
    if not trade.has_rationale:
        policies.append("POLICY_DOC_001")

    # --- Supervision ---
    if is_advisor_history_high_risk(trade):
        policies.append("POLICY_SUP_001")

    return policies