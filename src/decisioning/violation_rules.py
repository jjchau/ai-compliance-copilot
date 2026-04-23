"""
violation_rules.py

Purpose:
    Wrapper functions for determining the ground truths of individual compliance conditions
    of trades based on heuristic rules.

Usage:
    from src.decisioning.violation_rules import is_kyc_violation, is_suitability_violation, etc.

Author: Jason Chau
Date: 2026-04-15
"""

from src.data.schema import Trade
from src.decisioning.risk_signals import (
    is_kyc_missing,
    is_risk_too_high_for_profile,
    is_too_complex_for_experience    
)

def is_kyc_violation(trade: Trade) -> bool:
    """
    A KYC violation occurs when the client's KYC completeness is 'Missing'.
    """
    return is_kyc_missing(trade)

def is_suitability_violation(trade: Trade) -> bool:
    """
    A suitability violation occurs when the investment type or amount is not suitable for the client's profile.
    For example:
    - A high-risk investment (e.g., Options) for a client with low risk tolerance.
    """
    return is_risk_too_high_for_profile(trade)

def is_experience_violation(trade: Trade) -> bool:
    """
    An experience violation occurs when the investment type is not suitable for the client's investment experience.
    For example:
    - A beginner client investing in complex products like Options or ETFs.
    """
    return is_too_complex_for_experience(trade)