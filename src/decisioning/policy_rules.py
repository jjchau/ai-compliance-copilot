from src.data.schema import Trade
from src.decisioning.violation_rules import (
    is_kyc_violation,
    is_suitability_violation
)
from src.decisioning.risk_signals import is_too_complex_for_experience

def should_flag(trade: Trade, risk_score: int, confidence_score: float) -> bool:
    if is_kyc_violation(trade):
        return True

    if is_suitability_violation(trade):
        return True

    if is_too_complex_for_experience(trade):
        return True
    
    if risk_score > 70:
        return True

    if confidence_score < 0.6:
        return True
    
    return False