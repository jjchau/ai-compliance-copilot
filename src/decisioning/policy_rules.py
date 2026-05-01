"""
policy_rules.py

Purpose:
    Generate a policy-based flagging decision for a trade based on heuristic rules.

Usage:
    from src.decisioning.policy_rules import should_flag

Author: Jason Chau
Date: 2026-04-21
"""

from typing import Literal
from src.data.schema import Trade
from src.decisioning.conflict_detection import has_conflicting_signals
from src.decisioning.violation_rules import (
    is_kyc_violation,
    is_suitability_violation
)
from src.decisioning.risk_signals import is_too_complex_for_experience

ESCALATION_LEVEL = Literal['none', 'queue', 'priority', 'urgent']

def assess_escalation(trade: Trade, compliance_probability: float, risk_score: int, confidence_score: float) -> ESCALATION_LEVEL:
    """
    Determines the escalation level for a trade based on a combination of:
        - Compliance prediction probability
        - Risk score
        - Confidence score
        - Presence of hard violations
        - Presence of conflicting signals
    """
    
    # --- URGENT ---
    if is_kyc_violation(trade):
        return "urgent"

    if compliance_probability < 0.3 and risk_score >= 70:
        return "urgent"

    # --- PRIORITY ---
    if risk_score >= 75:
        return "priority"

    if compliance_probability < 0.5:
        return "priority"

    # --- QUEUE ---
    if confidence_score < 0.6:
        return "queue"

    if has_conflicting_signals(trade):
        return "queue"

    # --- NONE ---
    return "none"