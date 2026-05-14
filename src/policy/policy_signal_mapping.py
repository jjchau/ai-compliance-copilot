from src.decisioning.violation_rules import (
    is_kyc_violation,
    is_suitability_violation,
    is_experience_violation
)
from src.decisioning.risk_signals import (
    is_kyc_uncertain,
    is_investment_too_aggressive_for_objective,
    is_investment_too_aggressive_for_horizon,
    is_overexposure,
    is_advisor_history_high_risk
)
from src. decisioning.documentation_signals import is_missing_rationale
from src.decisioning.conflict_detection import has_conflicting_signals

POLICY_SIGNAL_CHECKS = {
    "POLICY_KYC_001": is_kyc_violation,
    "POLICY_KYC_002": is_kyc_uncertain,
    "POLICY_KYC_003": has_conflicting_signals,
    "POLICY_SUIT_001": is_suitability_violation,
    "POLICY_SUIT_002": is_investment_too_aggressive_for_objective,
    "POLICY_SUIT_003": is_investment_too_aggressive_for_horizon,
    "POLICY_EXP_001": is_experience_violation,
    "POLICY_RISK_001": is_overexposure,
#    "POLICY_RISK_002": is_leverage_violation,
    "POLICY_DOC_001": is_missing_rationale,
    "POLICY_SUP_001": is_advisor_history_high_risk,
#    "POLICY_CLIENT_001": is_client_violation,
}