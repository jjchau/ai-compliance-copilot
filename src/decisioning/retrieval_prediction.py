"""
retrieval_prediction.py

Purpose:
    Predict compliance status based on retrieved policies and trade characteristics.

Usage:
    from src.decisioning.retrieval_prediction import predict_with_retrieval

Author: Jason Chau
Date: 2026-05-05
"""

from src.data.schema import Trade
from src.decisioning.violation_rules import (
    is_kyc_violation,
    is_suitability_violation,
    is_experience_violation,
)
from src.decisioning.risk_signals import (
    is_investment_too_aggressive_for_horizon,
    is_investment_too_aggressive_for_objective
)

def predict_with_retrieval(trade: Trade, retrieved_policies: list) -> dict[str, float | bool]:
    score = 0.0
    
    # --- HARD VIOLATIONS (strong signals) ---
    if "POLICY_SUIT_001" in retrieved_policies:
        if is_suitability_violation(trade):
            score += 0.6

    if "POLICY_EXP_001" in retrieved_policies:
        if is_experience_violation(trade):
            score += 0.5

    if "POLICY_KYC_001" in retrieved_policies:
        # KYC violation (imperfect detection → FN source)
        if is_kyc_violation(trade):
            score += 0.8

    # --- SOFT SIGNALS (FP source) ---
    if "POLICY_SUIT_003" in retrieved_policies:
        if is_investment_too_aggressive_for_horizon(trade):
            score += 0.2

    if "POLICY_SUIT_002" in retrieved_policies:
        if is_investment_too_aggressive_for_objective(trade):
            score += 0.2
        
    # Missing policies → implicit FN
    # Extra policies → implicit FP (noisy reasoning later)

    # --- CONVERT TO PROBABILITY ---
    # squash score into [0,1]
    non_compliance_prob = min(score, 1.0)

    compliance_probability = 1.0 - non_compliance_prob

    # --- LABEL (temporary threshold) ---
    compliance_label = compliance_probability >= 0.9

    return {
        "compliance_probability": round(compliance_probability, 3),
        "compliance_label": compliance_label
    }