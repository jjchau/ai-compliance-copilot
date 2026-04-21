from src.data.schema import Trade
from src.decisioning.violation_rules import  *
from src.decisioning.risk_signals import *
from typing import Literal

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
    elif any([is_investment_too_agressive_for_horizon(trade), is_investment_too_aggressive_for_objective(trade), is_overexposure(trade), is_kyc_uncertain(trade) ]):
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
        is_investment_too_agressive_for_horizon(trade),
        is_investment_too_aggressive_for_objective(trade),
        is_overexposure(trade),
        is_kyc_uncertain(trade)
    ])

    if hard_violations == 0 and soft_signals == 0:
        return "Easy"

    if hard_violations >= 2:
        return "Easy"

    if hard_violations == 1 and soft_signals == 0:
        return "Medium"

    return "Hard"  # ambiguous / conflicting