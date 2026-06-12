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
    is_experience_violation
)

from src.decisioning.risk_signals import (
    is_kyc_uncertain,
    is_investment_too_aggressive_for_horizon,
    is_investment_too_aggressive_for_objective,
    is_overexposure,
    is_advisor_history_high_risk,
    is_elderly_high_risk_trade,
    is_documentation_deficient
)

SIGNAL_WEIGHTS = {
    "kyc_violation": 0.80,
    "suitability": 0.60,
    "experience": 0.30,
    "overexposure": 0.20,
    "advisor_history": 0.15,
    "senior_client": 0.25,
    "documentation": 0.10,
    "objective": 0.20,
    "horizon": 0.15,
    "kyc_uncertain": 0.25
}

def predict_with_retrieval(trade: Trade, retrieved_policies: list[str]) -> dict[str, float | bool]:
    signals_fired = set()

    if "POL-001-SUITABILITY" in retrieved_policies:
        if is_suitability_violation(trade):
            signals_fired.add("suitability")
        if is_experience_violation(trade):
            signals_fired.add("experience")
        if is_investment_too_aggressive_for_horizon(trade):
            signals_fired.add("horizon")
        if is_investment_too_aggressive_for_objective(trade):
            signals_fired.add("objective")

    if "POL-002-KYC" in retrieved_policies:
        if is_kyc_violation(trade):
            signals_fired.add("kyc_violation")
        if is_kyc_uncertain(trade):
            signals_fired.add("kyc_uncertain")

    if "POL-003-SURVEILLANCE" in retrieved_policies:
        if is_advisor_history_high_risk(trade):
            signals_fired.add("advisor_history")

    if "POL-004-CONCENTRATION" in retrieved_policies:
        if is_overexposure(trade):
            signals_fired.add("overexposure")

    if "POL-005-SENIOR-VULNERABLE-CLIENTS" in retrieved_policies:
        if is_elderly_high_risk_trade(trade):
            signals_fired.add("senior_client")

    if "POL-006-HIGH-RISK-PRODUCTS" in retrieved_policies:
        if is_suitability_violation(trade):
            signals_fired.add("suitability")
        if is_experience_violation(trade):
            signals_fired.add("experience")

    if "POL-007-DOCUMENTATION-STANDARDS" in retrieved_policies:
        if is_documentation_deficient(trade):
            signals_fired.add("documentation")
    
    if "POL-010-CLIENT-OBJECTIVE" in retrieved_policies:
        if is_investment_too_aggressive_for_objective(trade):
            signals_fired.add("objective")

    score = sum(
        SIGNAL_WEIGHTS[s]
        for s in signals_fired
    )

    non_compliance_prob = min(score, 1.0)

    compliance_probability = 1.0 - non_compliance_prob

    compliance_label = compliance_probability >= 0.9

    return {
        "compliance_probability": round(compliance_probability, 3),
        "compliance_label": compliance_label
    }


# POLICY_WEIGHTS = {
#     "POL-001-SUITABILITY": 0.60,
#     "POL-002-KYC": 0.80,
#     "POL-003-SURVEILLANCE": 0.15,
#     "POL-004-CONCENTRATION": 0.20,
#     "POL-005-SENIOR-VULNERABLE-CLIENTS": 0.25,
#     "POL-006-HIGH-RISK-PRODUCTS": 0.35,
#     "POL-007-DOCUMENTATION-STANDARDS": 0.20,
#     "POL-010-CLIENT-OBJECTIVE": 0.20,
# }

# def predict_with_retrieval(
#     trade: Trade,
#     retrieved_policies: list[str]
# ) -> dict[str, float | bool]:

#     score = 0.0

#     if (
#         "POL-001-SUITABILITY" in retrieved_policies
#         and is_suitability_violation(trade)
#     ):
#         score += POLICY_WEIGHTS["POL-001-SUITABILITY"]

#     if (
#         "POL-002-KYC" in retrieved_policies
#         and is_kyc_violation(trade)
#     ):
#         score += POLICY_WEIGHTS["POL-002-KYC"]

#     if (
#         "POL-003-SURVEILLANCE" in retrieved_policies
#         and is_advisor_history_high_risk(trade)
#     ):
#         score += POLICY_WEIGHTS["POL-003-SURVEILLANCE"]

#     if (
#         "POL-004-CONCENTRATION" in retrieved_policies
#         and is_overexposure(trade)
#     ):
#         score += POLICY_WEIGHTS["POL-004-CONCENTRATION"]

#     if (
#         "POL-005-SENIOR-VULNERABLE-CLIENTS" in retrieved_policies
#         and is_elderly_high_risk_trade(trade)
#     ):
#         score += POLICY_WEIGHTS["POL-005-SENIOR-VULNERABLE-CLIENTS"]

#     if (
#         "POL-006-HIGH-RISK-PRODUCTS" in retrieved_policies
#         and (
#             is_suitability_violation(trade)
#             or is_experience_violation(trade)
#         )
#     ):
#         score += POLICY_WEIGHTS["POL-006-HIGH-RISK-PRODUCTS"]

#     if (
#         "POL-006-HIGH-RISK-PRODUCTS" in retrieved_policies
#         and (is_investment_too_aggressive_for_horizon(trade) or is_investment_too_aggressive_for_objective(trade))
#     ):
#         score += POLICY_WEIGHTS["POL-006-HIGH-RISK-PRODUCTS"]

#     if (
#         "POL-007-DOCUMENTATION-STANDARDS" in retrieved_policies
#         and is_documentation_deficient(trade)
#     ):
#         score += POLICY_WEIGHTS["POL-007-DOCUMENTATION-STANDARDS"]

#     if (
#         "POL-010-CLIENT-OBJECTIVE" in retrieved_policies
#         and is_investment_too_aggressive_for_objective(trade)
#     ):
#         score += POLICY_WEIGHTS["POL-010-CLIENT-OBJECTIVE"]

#     if (
#         "POL-001-SUITABILITY" in retrieved_policies
#         and is_experience_violation(trade)
#     ):
#         score += 0.30

#     if (
#         "POL-001-SUITABILITY" in retrieved_policies
#         and is_investment_too_aggressive_for_horizon(trade)
#     ):
#         score += 0.15

#     non_compliance_prob = min(score, 1.0)

#     compliance_probability = 1.0 - non_compliance_prob

#     compliance_label = compliance_probability >= 0.9

#     return {
#         "compliance_probability": round(compliance_probability, 3),
#         "compliance_label": compliance_label
#     }


# from src.data.schema import Trade
# from src.decisioning.violation_rules import (
#     is_kyc_violation,
#     is_suitability_violation,
#     is_experience_violation,
# )
# from src.decisioning.risk_signals import (
#     is_investment_too_aggressive_for_horizon,
#     is_investment_too_aggressive_for_objective
# )

# def predict_with_retrieval(trade: Trade, retrieved_policies: list) -> dict[str, float | bool]:
#     score = 0.0
    
#     # --- HARD VIOLATIONS (strong signals) ---
#     if "POL-001-SUITABILITY" in retrieved_policies:
#         if is_suitability_violation(trade):
#             score += 0.6

#     if "POL-002-EXPERIENCE" in retrieved_policies:
#         if is_experience_violation(trade):
#             score += 0.5

#     if "POLICY_KYC_001" in retrieved_policies:
#         # KYC violation (imperfect detection → FN source)
#         if is_kyc_violation(trade):
#             score += 0.8

#     # --- SOFT SIGNALS (FP source) ---
#     if "POLICY_SUIT_003" in retrieved_policies:
#         if is_investment_too_aggressive_for_horizon(trade):
#             score += 0.2

#     if "POLICY_SUIT_002" in retrieved_policies:
#         if is_investment_too_aggressive_for_objective(trade):
#             score += 0.2
        
#     # Missing policies → implicit FN
#     # Extra policies → implicit FP (noisy reasoning later)

#     # --- CONVERT TO PROBABILITY ---
#     # squash score into [0,1]
#     non_compliance_prob = min(score, 1.0)

#     compliance_probability = 1.0 - non_compliance_prob

#     # --- LABEL (temporary threshold) ---
#     compliance_label = compliance_probability >= 0.9

#     return {
#         "compliance_probability": round(compliance_probability, 3),
#         "compliance_label": compliance_label
#     }