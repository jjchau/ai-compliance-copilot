"""
profile_factories.py

Purpose:
    Generate realistic investor profiles that represent coherent
    client archetypes before compliance scenarios are applied.

Author: Jason Chau
Date: 2026-06-04
"""

from pathlib import Path
import sys

sys.path.append(
    str(Path(__file__).resolve().parents[2])
)

import random
from typing import cast
from src.data.schema import (
    Trade,
    AdvisorExperience,
    AdvisorHistoryRisk
)


# ==========================================================
# Advisor Registry
# ==========================================================

ADVISOR_PROFILES = {
    'ADV-001': 'Low',
    'ADV-002': 'Low',
    'ADV-003': 'Low',
    'ADV-004': 'Low',
    'ADV-005': 'Medium',
    'ADV-006': 'Low',
    'ADV-007': 'Medium',
    'ADV-008': 'Low',
    'ADV-009': 'High',
    'ADV-010': 'Low',
    'ADV-011': 'Medium',
    'ADV-012': 'Low',
    'ADV-013': 'Low',
    'ADV-014': 'Medium',
    'ADV-015': 'Medium',
    'ADV-016': 'Medium',
    'ADV-017': 'High',
    'ADV-018': 'Medium',
    'ADV-019': 'High',
    'ADV-020': 'Low',
    'ADV-021': 'Low',
    'ADV-022': 'Medium',
    'ADV-023': 'Low',
    'ADV-024': 'Low',
    'ADV-025': 'Low',
    'ADV-026': 'High',
    'ADV-027': 'Medium',
    'ADV-028': 'Low',
    'ADV-029': 'Low',
    'ADV-030': 'Low',
    'ADV-031': 'Medium',
    'ADV-032': 'Low',
    'ADV-033': 'Medium',
    'ADV-034': 'Low',
    'ADV-035': 'Low',
    'ADV-036': 'Medium',
    'ADV-037': 'Low',
    'ADV-038': 'Low',
    'ADV-039': 'Medium',
    'ADV-040': 'Low',
    'ADV-041': 'Low',
    'ADV-042': 'High',
    'ADV-043': 'Medium',
    'ADV-044': 'Medium',
    'ADV-045': 'Medium',
    'ADV-046': 'Medium',
    'ADV-047': 'Low',
    'ADV-048': 'Medium',
    'ADV-049': 'Low',
    'ADV-050': 'Medium'
}


# ==========================================================
# Helpers
# ==========================================================

def pick_advisor():

    advisor_id = random.choice(list(ADVISOR_PROFILES.keys()))

    return (
        advisor_id,
        ADVISOR_PROFILES[advisor_id]
    )


def pick_advisor_experience() -> AdvisorExperience:
    return cast(
        AdvisorExperience,
        random.choices(
            population=["Junior", "Mid", "Senior"],
            weights=[0.25, 0.45, 0.30],
            k=1
        )[0]
    )


def base_trade(**kwargs):

    advisor_id, advisor_history = pick_advisor()

    return Trade(
        advisor_id=advisor_id,
        advisor_history_risk=cast(AdvisorHistoryRisk, advisor_history),
        advisor_experience=pick_advisor_experience(),
        advisor_rationale=None,
        advisor_notes=None,
        **kwargs
    )


# ==========================================================
# Profile Archetype #1
# Young Growth Investor
# ==========================================================

def create_young_growth_investor() -> Trade:

    income = random.randint(45000, 120000)

    return base_trade(
        client_age=random.randint(22, 35),
        client_income=income,

        risk_tolerance=random.choice(
            ["Medium", "High"]
        ),

        investment_experience=random.choice(
            ["Beginner", "Intermediate"]
        ),

        investment_objective="Growth",

        investment_time_horizon=random.choice(
            ["Long", "Medium"]
        ),

        investment_type=random.choice(
            ["ETFs", "Mutual Funds"]
        ),

        investment_amount=round(
            random.uniform(5000, income * 0.20),
            2
        ),

        kyc_completeness=random.choices(
            ["Complete", "Uncertain"],
            weights=[0.85, 0.15],
            k=1
        )[0]
    )


# ==========================================================
# Profile Archetype #2
# Mid-Career Balanced Investor
# ==========================================================

def create_midcareer_balanced_investor() -> Trade:

    income = random.randint(80000, 180000)

    return base_trade(
        client_age=random.randint(36, 60),
        client_income=income,

        risk_tolerance=random.choice(
            ["Low", "Medium"]
        ),

        investment_experience=random.choice(
            ["Intermediate", "Advanced"]
        ),

        investment_objective=random.choice(
            ["Balanced", "Income"]
        ),

        investment_time_horizon=random.choice(
            ["Medium", "Long"]
        ),

        investment_type=random.choice(
            ["Mutual Funds", "ETFs", "Bonds"]
        ),

        investment_amount=round(
            random.uniform(10000, income * 0.25),
            2
        ),

        kyc_completeness=random.choices(
            ["Complete", "Uncertain"],
            weights=[0.90, 0.10],
            k=1
        )[0]
    )


# ==========================================================
# Profile Archetype #3
# Retiree Preservation Investor
# ==========================================================

def create_retiree_preservation_investor() -> Trade:

    income = random.randint(40000, 120000)

    return base_trade(
        client_age=random.randint(65, 85),
        client_income=income,

        risk_tolerance="Low",

        investment_experience=random.choice(
            ["Beginner", "Intermediate"]
        ),

        investment_objective="Preservation",

        investment_time_horizon=random.choice(
            ["Short", "Medium"]
        ),

        investment_type=random.choice(
            ["Bonds", "GICs", "T-Bills"]
        ),

        investment_amount=round(
            random.uniform(5000, income * 0.30),
            2
        ),

        kyc_completeness=random.choices(
            ["Complete", "Uncertain"],
            weights=[0.90, 0.10],
            k=1
        )[0]
    )


# ==========================================================
# Profile Archetype #4
# Active Trader
# ==========================================================

def create_active_trader() -> Trade:

    income = random.randint(70000, 250000)

    return base_trade(
        client_age=random.randint(25, 60),
        client_income=income,

        risk_tolerance="High",

        investment_experience="Advanced",

        investment_objective="Growth",

        investment_time_horizon=random.choice(
            ["Short", "Medium"]
        ),

        investment_type=random.choice(
            ["Stocks", "ETFs"]
        ),

        investment_amount=round(
            random.uniform(10000, income * 0.35),
            2
        ),

        kyc_completeness=random.choices(
            ["Complete", "Uncertain"],
            weights=[0.80, 0.20],
            k=1
        )[0]
    )


# ==========================================================
# Registry
# ==========================================================

PROFILE_FACTORIES = [
    create_young_growth_investor,
    create_midcareer_balanced_investor,
    create_retiree_preservation_investor,
    create_active_trader
]