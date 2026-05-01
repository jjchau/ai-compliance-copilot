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
from src.scoring.risk_scoring import compute_risk_score
from src.scoring.confidence_scoring import compute_confidence_score
from src.decisioning.policy_rules import assess_escalation
from src.decisioning.conflict_detection import (
    has_conflicting_signals,
    get_signals
)

def evaluate_trade(trade: Trade) -> dict:
    compliance_probability = predict_compliance(trade)['compliance_probability']
    compliance_label = predict_compliance(trade)['compliance_label']
    risk_score = compute_risk_score(trade)
    confidence_score = compute_confidence_score(trade)['overall']
    escalation_level = assess_escalation(trade, compliance_probability, risk_score, confidence_score)
    has_conflict = has_conflicting_signals(trade)
    conflict_signals = get_signals(trade)

    return {
        'trade_id': trade.trade_id,
        'compliance_probability': compliance_probability,
        'compliance_label': compliance_label,
        'risk_score': risk_score,
        'confidence_score': confidence_score,
        'escalation_level': escalation_level,
        'has_conflicting_signals': has_conflict,
        'conflict_signals': conflict_signals
    }