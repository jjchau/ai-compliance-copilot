"""
explanation.py

Purpose:
    Generate human-readable explanations for why a trade was flagged based on the retrieved policies and their associated signals.

Usage:
    from src.orchestration.explanation import generate_explanation

Author: Jason Chau
Date: 2026-05-14
"""

from typing import List
from src.data.schema import Trade

def generate_explanation(trade: Trade, retrieved_policies: List[str]) -> str:
    explanations = []

    for policy_id in retrieved_policies:
        explanations.append(POLICY_EXPLANATIONS.get(policy_id, "Unknown issue"))

    if not explanations:
        return "Retrieved policies did not produce significant concerns."

    return "; ".join(explanations) + "."
    
POLICY_EXPLANATIONS = {
    "POL-001-SUITABILITY": "Potential suitability concern identified",

    "POL-002-KYC": "Client profile information may be incomplete or inconsistent",

    "POL-003-SURVEILLANCE": "Supervisory review indicators detected",

    "POL-004-CONCENTRATION": "Elevated portfolio concentration exposure detected",

    "POL-005-SENIOR-VULNERABLE-CLIENTS": "Senior or vulnerable client review considerations apply",

    "POL-006-HIGH-RISK-PRODUCTS": "High-risk or complex product requires enhanced review",

    "POL-007-DOCUMENTATION-STANDARDS": "Advisor rationale or documentation may be insufficient",

    "POL-008-EXCEPTIONS-AND-OVERRIDES": "Policy exception review may be required",

    "POL-009-CONFLICT-OF-INTEREST": "Potential conflict-of-interest review may be required",

    "POL-010-CLIENT-OBJECTIVE": "Recommendation may not align with stated investment objectives",
}