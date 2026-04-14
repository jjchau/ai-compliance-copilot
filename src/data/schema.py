from pydantic import BaseModel, Field
from typing import Optional, Literal
from uuid import uuid4
from datetime import datetime

class Trade(BaseModel):
    trade_id: str = Field(default_factory=lambda: f'TRADE-{uuid4().hex[:8]}')
    trade_timestamp: datetime = Field(default_factory=datetime.now)

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
    kyc_completeness: Literal['Complete', 'Partial', 'Missing']

class LabeledTrade(Trade):
    # Ground truth
    true_compliance: bool
    true_risk_tier: Literal['Low', 'Medium', 'High']
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
        "Overtrading",
        "Aligned Recommendation"
    ]
    difficulty: Literal['Easy', 'Medium', 'Hard'] # Rough mappings: Easy->Clean, Medium->Ambiguous, Hard->Edge