from pydantic import BaseModel, Field
from typing import Optional, Literal
from uuid import uuid4
from datetime import datetime, timedelta
import random

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
    risk_tolerance: Literal['Low', 'Medium', 'High']
    investment_experience: Literal['Beginner', 'Intermediate', 'Advanced']
    investment_objective: Literal['Growth', 'Income', 'Preservation', 'Balanced']
    investment_time_horizon: Literal['Short', 'Medium', 'Long']

    # Trade
    investment_type: Literal['Stocks', 'Bonds', 'GICs', 'T-Bills', 'Mutual Funds', 'ETFs', 'Options']
    investment_amount: float

    # Advisor
    advisor_id: str
    advisor_experience: Literal['Junior', 'Mid', 'Senior']
    advisor_history_risk: Literal['Low', 'Medium', 'High']
    has_rationale: bool
    advisor_notes: Optional[str] = None

    # Data quality
    kyc_completeness: Literal['Complete', 'Uncertain', 'Missing']

class LabeledTrade(Trade):
    # Ground truth
    true_compliance: bool
    """
    # COMPUTE THESE IN RUN-TIME SCORING LOGIC:
    risk_score: float
    #e.g. risk_score = compute_risk_score(trade) 
    #
    # def compute_risk_score(case: Case) -> float:
    #...

    # def assign_risk_tier(score: float) -> str
    
    Conflicting_signals: bool
    #e.g.
    # conflict_flag = detect_conflict(trade)
    #
    # def detect_conflict(trade: Trade) -> bool:
    #...
    """
    # Metadata
    case_type: Literal[
        "Suitability Violation",
        "KYC Missing",
        "Insufficient Experience",
        "Risk Signal",
        "Aligned Recommendation"
    ]
    difficulty: Literal['Easy', 'Medium', 'Hard'] # Rough mappings: Easy->Clean, Medium->Ambiguous, Hard->Edge