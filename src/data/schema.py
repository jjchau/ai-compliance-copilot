"""
schema.py

Purpose:
    Define the data structures for trades and labeled trades.

Usage:
    from src.data.schema import Trade, LabeledTrade

Author: Jason Chau
Date: 2026-04-14
"""

from pydantic import BaseModel, Field
from typing import Optional, Literal
from uuid import uuid4
from datetime import datetime, timedelta
import random

RiskTolerance = Literal["Low", "Medium", "High"]
InvestmentExperience = Literal["Beginner", "Intermediate", "Advanced"]
AdvisorExperience = Literal["Junior", "Mid", "Senior"]
AdvisorHistoryRisk = Literal["Low", "Medium", "High"]

SeverityTier = Literal["Low", "Medium", "High"]
WorkflowBucket = Literal["Auto_pass", "Queue", "Priority", "Urgent"]



def random_timestamp():
    now = datetime.now()
    start = now - timedelta(days=30)

    delta = now - start
    random_microseconds = random.randint(0, int(delta.total_seconds() * 1_000_000))

    return start + timedelta(microseconds=random_microseconds)

class Trade(BaseModel):
    trade_id: str = Field(default_factory=lambda: f'TRADE-{uuid4().hex[:8]}')
    trade_timestamp: datetime = Field(default_factory=lambda: random_timestamp())

    # Client
    client_age: int
    client_income: int
    risk_tolerance: RiskTolerance
    investment_experience: InvestmentExperience
    investment_objective: Literal['Growth', 'Income', 'Preservation', 'Balanced']
    investment_time_horizon: Literal['Short', 'Medium', 'Long']

    # Trade
    investment_type: Literal['Stocks', 'Bonds', 'GICs', 'T-Bills', 'Mutual Funds', 'ETFs', 'Options']
    investment_amount: float

    # Advisor
    advisor_id: str
    advisor_experience: AdvisorExperience
    advisor_history_risk: AdvisorHistoryRisk
    advisor_rationale: Optional[str] = None
    advisor_notes: Optional[str] = None

    # Data quality
    kyc_completeness: Literal['Complete', 'Uncertain', 'Missing']

class LabeledTrade(Trade):
    # Ground truth
    true_compliance: bool

    # Metadata
    case_type: Literal[
        "Suitability Violation",
        "KYC Missing",
        "Insufficient Experience",
        "Risk Signal",
        "Aligned Recommendation"
    ]

    scenario_name: str
    difficulty: Literal['Easy', 'Medium', 'Hard'] # Rough mappings: Easy->Clean, Medium->Ambiguous, Hard->Edge
    severity_tier: SeverityTier
    expected_workflow_bucket: WorkflowBucket
    relevant_policies: Optional[list[str]] = None
    primary_policy: Optional[str] = None