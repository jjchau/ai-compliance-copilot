from src.data.schema import Trade
from src.decisioning.risk_signals import (
    is_risk_too_high_for_profile,
    is_too_complex_for_experience,
    is_investment_too_aggressive_for_objective,
    is_investment_too_agressive_for_horizon,
    is_risk_too_low_for_profile,
    is_investment_too_conservative_for_objective,
    is_investment_too_conservative_for_horizon
)

def get_signals(trade: Trade) -> dict:
    """
    Returns a dictionary signals for a given trade.
    This can be used for debugging and explainability of conflict detection.
    """
    return {
        "risk_too_high_for_profile": is_risk_too_high_for_profile(trade),
        "too_complex_for_experience": is_too_complex_for_experience(trade),
        "investment_too_aggressive_for_objective": is_investment_too_aggressive_for_objective(trade),
        "investment_too_agressive_for_horizon": is_investment_too_agressive_for_horizon(trade),
        "risk_too_low_for_profile": is_risk_too_low_for_profile(trade),
        "investment_too_conservative_for_objective": is_investment_too_conservative_for_objective(trade),
        "investment_too_conservative_for_horizon": is_investment_too_conservative_for_horizon(trade)
    }

def has_conflicting_signals(trade: Trade) -> bool:
    """
    Returns True if there are conflicting risk signals for a given trade, indicating mixed signals about appropriate risk direction.
    For example, if a trade has signals indicating both "too aggressive for profile" and "too conservative for profile", that would be a conflict.
    This can be used to identify cases where the system is uncertain about the risk level, which may warrant human review or more cautious handling.
    """

    signals = get_signals(trade)
    
    aggressive_signals = [
        signals["risk_too_high_for_profile"],      # pushing toward risk
        signals["too_complex_for_experience"],
        signals["investment_too_aggressive_for_objective"],
        signals["investment_too_agressive_for_horizon"]
    ]

    conservative_signals = [
        signals["risk_too_low_for_profile"],       # pushing toward safety
        signals["investment_too_conservative_for_objective"],
        signals["investment_too_conservative_for_horizon"]
    ]

    return any(aggressive_signals) and any(conservative_signals)