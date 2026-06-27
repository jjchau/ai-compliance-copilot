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
from src.decisioning.schema import *

ESCALATION_LEVEL = Literal['none', 'queue', 'priority', 'urgent']

def assess_escalation(
    trade: Trade,
    compliance_probability: float,
    evidence: ComplianceEvidenceSchema,
    risk_score: int,
    confidence_score: float
) -> ESCALATION_LEVEL:
    """
    Determines the escalation level for a trade based on:
    - deterministic compliance probability
    - LLM-extracted evidence
    - deterministic risk score
    - deterministic confidence score

    Compliance violations drive priority/urgent routing.
    Material concern signals and meaningful evidence-quality issues drive queue routing.
    Weak documentation alone does not route an otherwise clean trade.
    """

    violations = set(evidence.violations)
    concern_signals = set(evidence.concern_signals)
    evidence_quality = set(evidence.evidence_quality)

    hard_violation_count = sum([
        ViolationType.KYC_MISSING in violations,
        ViolationType.RISK_TOLERANCE_VIOLATION in violations,
        ViolationType.EXPERIENCE_COMPLEXITY_MISMATCH in violations,
    ])

    severe_context_present = any([
        ConcernSignalType.SENIOR_CLIENT_RISK in concern_signals,
        ConcernSignalType.OVEREXPOSURE in concern_signals,
        ConcernSignalType.AGGRESSIVE_FOR_SHORT_HORIZON in concern_signals,
        ConcernSignalType.AGGRESSIVE_FOR_OBJECTIVE in concern_signals,
    ])

    # -----------------------------
    # 1. URGENT
    # -----------------------------

    if risk_score >= 80:
        return "urgent"

    if risk_score >= 65 and compliance_probability < 0.3:
        return "urgent"

    # Compound urgent rule:
    # Multiple hard violations become urgent when paired with either
    # materially elevated risk or a serious contextual risk signal.
    if hard_violation_count >= 2 and (
        risk_score >= 60
        or severe_context_present
    ):
        return "urgent"

    # -----------------------------
    # 2. PRIORITY
    # -----------------------------
    # True compliance violations are high-priority review items even when
    # the numeric risk score is not extreme.

    if ViolationType.KYC_MISSING in violations:
        return "priority"

    if ViolationType.RISK_TOLERANCE_VIOLATION in violations:
        return "priority"

    if ViolationType.EXPERIENCE_COMPLEXITY_MISMATCH in violations:
        return "priority"

    # Senior risk should only become priority when paired with material
    # risk indicators. Age / senior status alone should not force priority.
    if (
        ConcernSignalType.SENIOR_CLIENT_RISK in concern_signals
        and (
            risk_score >= 40
            or ConcernSignalType.OVEREXPOSURE in concern_signals
            or ConcernSignalType.AGGRESSIVE_FOR_SHORT_HORIZON in concern_signals
            or ConcernSignalType.AGGRESSIVE_FOR_OBJECTIVE in concern_signals
            or ViolationType.RISK_TOLERANCE_VIOLATION in violations
            or ViolationType.EXPERIENCE_COMPLEXITY_MISMATCH in violations
        )
    ):
        return "priority"

    # Numeric high-risk cases go to priority even without a hard violation.
    if risk_score >= 40:
        return "priority"

    # -----------------------------
    # 3. QUEUE
    # -----------------------------
    # Queue is for review-worthy cases that are not priority/urgent:
    # uncertain KYC, material concern signals, or low-confidence cases
    # where evidence is insufficient to auto-pass.

    if compliance_probability < 0.5 and risk_score < 35:
        return "queue"

    material_concern_present = any([
        ConcernSignalType.OVEREXPOSURE in concern_signals,
        ConcernSignalType.AGGRESSIVE_FOR_SHORT_HORIZON in concern_signals,
        ConcernSignalType.AGGRESSIVE_FOR_OBJECTIVE in concern_signals,
    ])

    meaningful_evidence_quality_issue = any([
        EvidenceQualityType.KYC_UNCERTAIN in evidence_quality,
    ])

    weak_documentation_present = any([
        EvidenceQualityType.MISSING_RATIONALE in evidence_quality,
        EvidenceQualityType.WEAK_RATIONALE in evidence_quality,
        EvidenceQualityType.MINIMAL_ADVISOR_NOTES in evidence_quality,
    ])

    soft_context_only = any([
        ConcernSignalType.HIGH_RISK_ADVISOR in concern_signals,
        ConcernSignalType.SENIOR_CLIENT_RISK in concern_signals,
        ConcernSignalType.TOO_CONSERVATIVE_FOR_RISK_PROFILE in concern_signals,
        ConcernSignalType.TOO_CONSERVATIVE_FOR_HORIZON in concern_signals,
        ConcernSignalType.TOO_CONSERVATIVE_FOR_OBJECTIVE in concern_signals,
    ])

    if material_concern_present:
        return "queue"

    if meaningful_evidence_quality_issue:
        return "queue"

    # Weak documentation should not queue a clean trade by itself.
    # It can queue only when paired with some other soft/contextual risk.
    if (
        weak_documentation_present
        and (
            risk_score > 0
            or soft_context_only
            or confidence_score < 0.6
        )
    ):
        return "queue"

    # Soft contextual signals alone should not route unless confidence is low.
    if soft_context_only and confidence_score < 0.6:
        return "queue"

    # -----------------------------
    # 4. STRAIGHT-THROUGH PROCESSING
    # -----------------------------

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