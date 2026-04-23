from src.data.schema import Trade
from src.decisioning.violation_rules import *
from src.decisioning.risk_signals import *

WEIGHTS = {
    "kyc_violation": 30,
    "suitability": 40,
    "experience": 35,
    "aggressive_for_horizon": 15,
    "aggressive_for_objective": 10,
    "overexposure": 10,
    "advisor_history": 10,
    "kyc_uncertain": 10,
    "risk_too_low": 5,
    "conservative_for_horizon": 5,
    "conservative_for_objective": 5
}

def compute_risk_score(trade: Trade) -> int:
    """
    Computes a heuristic risk score (0–100+) based on:
    - Hard violations (strong signals)
    - Soft signals (contextual / ambiguous risk factors)

    This is a SYSTEM PREDICTION, not ground truth.
    """
    
    score = 0

    if is_kyc_violation(trade):
        score += WEIGHTS["kyc_violation"]

    if is_suitability_violation(trade):
        score += WEIGHTS["suitability"]

    if is_experience_violation(trade):
        score += WEIGHTS["experience"]

    if is_investment_too_agressive_for_horizon(trade):
        score += WEIGHTS["aggressive_for_horizon"]

    if is_investment_too_aggressive_for_objective(trade):
        score += WEIGHTS["aggressive_for_objective"]

    if is_overexposure(trade):
        score += WEIGHTS["overexposure"]

    if is_advisor_history_high_risk(trade):
        score += WEIGHTS["advisor_history"]
    
    if is_kyc_uncertain(trade):
        score += WEIGHTS["kyc_uncertain"]

    if is_risk_too_low_for_profile(trade):
        score += WEIGHTS["risk_too_low"]

    if is_investment_too_conservative_for_horizon(trade):
        score += WEIGHTS["conservative_for_horizon"]

    if is_investment_too_conservative_for_objective(trade):
        score += WEIGHTS["conservative_for_objective"]

    return min(score, 100)  # optional cap for normalization