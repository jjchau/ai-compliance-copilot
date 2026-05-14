from pydantic import BaseModel
from typing import Literal

class ReviewSubmission(BaseModel):
    reviewer: str
    action: Literal["approve", "override"]
    notes: str