"""
compliance_prediction.py

Purpose:
    Predict compliance status based on trade characteristics and risk signals.

Usage:
    from src.decisioning.compliance_prediction import predict_compliance

Author: Jason Chau
Date: 2026-04-17
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
import random

# TODO: Refactor into a config file:
DETECTION_RATES = {
    "kyc": 0.6,
    "horizon_fp": 0.4,
    "objective_fp": 0.3,
    "noise": 0.05
}

def predict_compliance(trade: Trade) -> dict:
    """
    Heuristic-based compliance prediction that outputs probability + label.
    Designed to simulate imperfect model behavior (FN/FP/noise).
    In a real implementation, this could be replaced with a more sophisticated machine learning model trained on historical data.
    """

    score = 0.0  # higher = more likely NON-compliant

    # --- HARD VIOLATIONS (strong signals) ---
    if is_suitability_violation(trade):
        score += 0.6

    if is_experience_violation(trade):
        score += 0.5

    # KYC violation (imperfect detection → FN source)
    if is_kyc_violation(trade):
        if random.random() < DETECTION_RATES["kyc"]:
            score += 0.8

    # --- SOFT SIGNALS (FP source) ---
    if is_investment_too_aggressive_for_horizon(trade):
        if random.random() < DETECTION_RATES["horizon_fp"]:
            score += 0.2

    if is_investment_too_aggressive_for_objective(trade):
        if random.random() < DETECTION_RATES["objective_fp"]:
            score += 0.2

    # --- RANDOM NOISE ---
    if random.random() < DETECTION_RATES["noise"]:
        score += 0.3  # random false signal

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