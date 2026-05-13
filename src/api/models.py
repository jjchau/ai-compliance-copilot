from pydantic import BaseModel

class ReviewSubmission(BaseModel):
    reviewer: str
    decision: str
    notes: str