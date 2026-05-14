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
"""from src.decisioning.conflict_detection import (
    has_conflicting_signals,
    get_signals
)
"""
from typing import Optional

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

"""def evaluate_trade(trade: Trade) -> dict:
    compliance_result = predict_compliance(trade)
    compliance_probability = compliance_result['compliance_probability']
    compliance_label = compliance_result['compliance_label']
    risk_score = compute_risk_score(trade)
    confidence_score = compute_confidence_score(trade)['overall']
    escalation_level = assess_escalation(trade, compliance_probability, risk_score, confidence_score)
    priority_score = compute_priority_score(trade, risk_score, confidence_score, escalation_level)
    has_conflict = has_conflicting_signals(trade)
    conflict_signals = get_signals(trade)

    return {
        'trade_id': trade.trade_id,
        'compliance_probability': compliance_probability,
        'compliance_label': compliance_label,
        'risk_score': risk_score,
        'confidence_score': confidence_score,
        'escalation_level': escalation_level,
        'priority_score': priority_score,
        'has_conflicting_signals': has_conflict,
        'conflict_signals': conflict_signals
    }"""

def compute_priority_score(trade: Trade, risk_score: float, confidence_score: float, escalation_level: str) -> Optional[float]:
    base_score = (
        0.7 * risk_score +
        0.3 * (1 - confidence_score) * 100
    )

    if escalation_level == "priority":
        return base_score + 100  # ensure priority > queue

    if escalation_level == "queue":
        return base_score

    return None