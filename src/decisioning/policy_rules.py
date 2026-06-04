"""
src/decisioning/policy_rules.py

Purpose:
    Deterministic governance and routing rules engine. Evaluates qualitative 
    AI inputs alongside quantitative risk scores to assign formal workspace 
    escalation pathways.

Author: Jason Chau
Date: 2026-06-03
"""

from typing import Literal
from src.data.schema import Trade
from src.decisioning.conflict_detection import has_conflicting_signals

ESCALATION_LEVEL = Literal['none', 'queue', 'priority', 'urgent']

def assess_escalation(
    trade: Trade, 
    compliance_probability: float, 
    risk_score: int, 
    confidence_score: float
) -> ESCALATION_LEVEL:
    """
    Determines the escalation level for a trade based on a combination of
    compliance prediction probability, quantitative risk scores, and data confidence.
    """
    
    # 1. CRITICAL RISK (Spaced at >= 80 to catch severe compounding violations)
    if risk_score >= 80:
        return "urgent"
        
    # 2. HIGH RISK WITH POOR COMPLIANCE CONFIDENCE
    if risk_score >= 65 and compliance_probability < 0.3:
        return "urgent"

    # 3. HIGH RISK ELEVATED BACKLOG
    if risk_score >= 65:
        return "priority"

    # 4. TECHNICAL EXCEPTION
    # The AI flags a compliance problem, but the quantitative engine confirms low risk.
    # Route to standard queue so it pools at the bottom of the active backlog.
    if compliance_probability < 0.5 and risk_score < 35:
        return "queue"

    # 5. STANDARD WORKSPACE VERIFICATION
    if risk_score >= 35 or confidence_score < 0.6 or has_conflicting_signals(trade):
        return "queue"

    # 6. STRAIGHT-THROUGH PROCESSING
    return "none"

# """
# policy_rules.py

# Purpose:
#     Generate a policy-based flagging decision for a trade based on heuristic rules.

# Usage:
#     from src.decisioning.policy_rules import should_flag

# Author: Jason Chau
# Date: 2026-04-21
# """

# from typing import Literal
# from src.data.schema import Trade
# from src.decisioning.conflict_detection import has_conflicting_signals
# # from src.decisioning.violation_rules import (
# #     is_kyc_violation,
# #     is_suitability_violation
# # )
# # from src.decisioning.risk_signals import is_too_complex_for_experience

# ESCALATION_LEVEL = Literal['none', 'queue', 'priority', 'urgent']

# def assess_escalation(trade: Trade, compliance_probability: float, risk_score: int, confidence_score: float) -> ESCALATION_LEVEL:
#     """
#     Determines the escalation level for a trade based on a combination of:
#         - Compliance prediction probability
#         - Risk score
#         - Confidence score
#         - Presence of hard violations
#         - Presence of conflicting signals
#     """
    
#     # # --- URGENT ---
#     # if is_kyc_violation(trade):
#     #     return "urgent"

#     if compliance_probability < 0.3 and risk_score >= 70:
#         return "urgent"

#     # --- PRIORITY ---
#     if risk_score >= 75:
#         return "priority"

#     if compliance_probability < 0.5:
#         return "priority"

#     # --- QUEUE ---
#     if confidence_score < 0.6:
#         return "queue"

#     if has_conflicting_signals(trade):
#         return "queue"

#     # --- NONE ---
#     return "none"