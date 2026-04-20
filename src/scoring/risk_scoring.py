from src.data.schema import Trade
from src.decisioning.violation_rules import  *
from src.decisioning.risk_signals import *

WEIGHTS = {
    "suitability": 40,
    "experience": 35,
    "kyc_violation": 30,
    "horizon": 15,
    "objective": 10,
    "overexposure": 10,
    "kyc_uncertain": 10,
    "advisor_history": 10
}

def compute_risk_score(trade: Trade) -> int:
    """
    Computes a heuristic risk score (0–100+) based on:
    - Hard violations (strong signals)
    - Soft signals (contextual / ambiguous risk factors)

    This is a SYSTEM PREDICTION, not ground truth.
    """
    
    score = 0

    # HARD VIOLATIONS (high weight, but not sole decision drivers)
    if is_suitability_violation(trade):
        score += WEIGHTS["suitability"]

    if is_experience_violation(trade):
        score += WEIGHTS["experience"]

    if is_kyc_violation(trade):
        score += WEIGHTS["kyc_violation"]

    # SOFT SIGNALS (moderate weight)
    if is_horizon_mismatch(trade):
        score += WEIGHTS["horizon"]

    if is_objective_mismatch(trade):
        score += WEIGHTS["objective"]

    if is_overexposure(trade):
        score += WEIGHTS["overexposure"]

    if is_kyc_uncertain(trade):
        score += WEIGHTS["kyc_uncertain"]

    # CONTEXTUAL RISK FACTORS
    if trade.advisor_history_risk == "High":
        score += WEIGHTS["advisor_history"]

    return min(score, 100)  # optional cap for normalization

def assign_risk_tier(score: int) -> str:
    if score < 5:
        return 'Low'
    elif score < 10:
        return 'Medium'
    else:
        return 'High'
    
def detect_conflicts(trade: Trade) -> bool:
    if trade.risk_tolerance == 'Low' and trade.investment_type in ['Stocks', 'Options']:
        return True
    if trade.risk_tolerance == 'High' and trade.investment_type in ['Bonds']:
        return True
    if trade.investment_experience == 'Beginner' and trade.investment_type in ['Options']:
        return True
    return False