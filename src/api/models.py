from pydantic import BaseModel
from typing import List, Literal, Optional
from src.decisioning.policy_rules import ESCALATION_LEVEL

class aiAssessment(BaseModel):
    retrieved_policies: List[str]
    compliance_probability: float
    compliance_label: bool
    risk_score: int
    confidence_score: float
    escalation_level: ESCALATION_LEVEL
    priority_score: Optional[float]
    flag_reasons: str

class ReviewSubmission(BaseModel):
    ai_recommendation: str
    review_action: Literal["reject", "approve", "escalate"]
    case_status: Literal["pending", "reviewed", "awaiting_senior_review"]
    review_outcome: Literal["compliant", "non-compliant", None]
    reviewer: str
    notes: str