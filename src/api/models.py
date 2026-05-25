from pydantic import BaseModel
from typing import Literal

class ReviewSubmission(BaseModel):
    ai_recommendation: str
    review_action: Literal["reject", "approve", "escalate"]
    case_status: Literal["pending", "reviewed", "awaiting_senior_review"]
    review_outcome: Literal["compliant", "non-compliant", None]
    reviewer: str
    notes: str