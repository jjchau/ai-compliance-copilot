"""
decision_engine.py

Purpose:
    Main decision engine for evaluating trades and determining compliance status.

Usage:
    from src.decisioning.decision_engine import evaluate_trade

Author: Jason Chau
Date: 2026-04-21
"""

from src.data.schema import Trade
from src.decisioning.compliance_prediction import predict_compliance
#from src.decisioning.violation_rules import is_kyc_violation
from src.scoring.risk_scoring import compute_risk_score
from src.scoring.confidence_scoring import compute_confidence_score
from src.decisioning.policy_rules import assess_escalation
from typing import Optional

# For legacy rule-based compliance prediction, called from sprint 1 notebook. See build_review_case() for retrieval-based compliance prediction.
def evaluate_trade(trade):
    compliance_prediction = predict_compliance(trade)

    return evaluate_prediction(
        trade,
        compliance_prediction
    )

def evaluate_prediction(trade: Trade, compliance_result: dict) -> dict:
    compliance_probability = compliance_result["compliance_probability"]
    compliance_label = compliance_result["compliance_label"]
    risk_score = compute_risk_score(trade)
    confidence_score = compute_confidence_score(trade)["overall"]
    escalation_level = assess_escalation(trade, compliance_probability, risk_score, confidence_score)
    priority_score = compute_priority_score(trade, risk_score, confidence_score, escalation_level)

    return {
        "compliance_probability": compliance_probability,
        "compliance_label": compliance_label,
        "risk_score": risk_score,
        "confidence_score": confidence_score,
        "escalation_level": escalation_level,
        "priority_score": priority_score
    }

def compute_priority_score(trade: Trade, risk_score: float, confidence_score: float, escalation_level: str) -> Optional[float]:
    """
    Computes a relative priority sorting score for backlog optimization.
    """
    base_score = (
        0.7 * risk_score +
        0.3 * (1 - confidence_score) * 100
    )

    if escalation_level == "urgent":
        return base_score + 100.0
    elif escalation_level == "priority":
        return base_score + 50.0
    elif escalation_level == "queue":
        # SPECIAL OVERRIDE: If this is a low-risk Technical Exception,
        # forcefully suppress its priority score so it sinks to the bottom.
        if risk_score < 35:
            return float(max(5.0, risk_score - 20.0))
        return base_score
        
    return 0.0

# def compute_priority_score(trade: Trade, risk_score: float, confidence_score: float, escalation_level: str) -> Optional[float]:
#     base_score = (
#         0.7 * risk_score +
#         0.3 * (1 - confidence_score) * 100
#     )

#     if escalation_level == "priority":
#         return base_score + 100  # ensure priority > queue

#     if escalation_level == "queue":
#         return base_score

#     return None