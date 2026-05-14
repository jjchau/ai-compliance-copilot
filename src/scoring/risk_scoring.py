"""
risk_scoring.py

Purpose:
    Heuristically calculate a risk score for a trade based on client profile, advisor, and trade
    characteristics.

Usage:
    from src.scoring.risk_scoring import compute_risk_score

Author: Jason Chau
Date: 2026-04-16
"""

from src.data.schema import Trade
from src.decisioning.violation_rules import *
from src.decisioning.risk_signals import *

WEIGHTS = {
    "kyc_violation": 40,
    "suitability": 40,
    "experience": 30,
    "aggressive_for_horizon": 15,
    "aggressive_for_objective": 10,
    "overexposure": 15,
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

    regulatory_risk = 0
    contextual_risk = 0

    # --- REGULATORY SEVERITY ---
    if is_kyc_violation(trade):
        regulatory_risk += WEIGHTS["kyc_violation"]

    if is_suitability_violation(trade):
        regulatory_risk += WEIGHTS["suitability"]

    if is_experience_violation(trade):
        regulatory_risk += WEIGHTS["experience"]

    # --- CONTEXTUAL / BUSINESS RISK ---
    if is_overexposure(trade):
        contextual_risk += WEIGHTS["overexposure"]

    if is_advisor_history_high_risk(trade):
        contextual_risk += WEIGHTS["advisor_history"]
    
    if is_kyc_uncertain(trade):
        contextual_risk += WEIGHTS["kyc_uncertain"]

    # --- SOFT MISALIGNMENTS ---
    if is_investment_too_aggressive_for_horizon(trade):
        contextual_risk += WEIGHTS["aggressive_for_horizon"]

    if is_investment_too_aggressive_for_objective(trade):
        contextual_risk += WEIGHTS["aggressive_for_objective"]

    # Low-impact signals
    if is_risk_too_low_for_profile(trade):
        contextual_risk += WEIGHTS["risk_too_low"]

    if is_investment_too_conservative_for_horizon(trade):
        contextual_risk += WEIGHTS["conservative_for_horizon"]

    if is_investment_too_conservative_for_objective(trade):
        contextual_risk += WEIGHTS["conservative_for_objective"]

    # Combine and return final score
    score = regulatory_risk + contextual_risk

    return min(score, 100)