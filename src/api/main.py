from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import json
from src.services.review_case_service import cases, case_lookup
from src.api.models import ReviewSubmission

app = FastAPI(title="AI Compliance Copilot API")

# Define the origins that are allowed to talk to your backend
origins = [
    "http://localhost:5173",  # Vite dev server
    "http://127.0.0.1:5173",
]

# Add the CORS middleware to app instance
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,            # Allows Vite frontend through
    allow_credentials=True,
    allow_methods=["*"],              # Allows GET, POST, PUT, DELETE, etc.
    allow_headers=["*"],              # Allows all custom/standard headers
)

@app.get("/")
def root():
    return {"message": "Compliance Copilot API is running!"}

@app.get("/cases")
def get_cases(escalation: str | None = None):
    # If a specific escalation filter is passed, filter and return the flat list directly
    if escalation in ["urgent", "priority", "queue", "none"]:
        return [case for case in cases if case["escalation_level"] == escalation]

    # Default: Return the entire flat list of cases directly
    return cases
    
@app.get("/cases/{trade_id}")
def get_case(trade_id: str):
    case = case_lookup.get(trade_id)
    if case is None:
        raise HTTPException(status_code=404, detail="Case not found")
    return {"case": case}

@app.post("/cases/{trade_id}/review")
def submit_review(trade_id: str, review: ReviewSubmission):
    if trade_id not in case_lookup:
        raise HTTPException(status_code=404, detail="Case not found")

    reviewer_disagreement = False

    if review.review_outcome is not None:
        reviewer_disagreement = (
            review.ai_recommendation != review.review_outcome
        )

    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "trade_id": trade_id,
        "ai_recommendation": review.ai_recommendation,  # Consider removing in future since this is not a reviewer action, and we can look it up on the backend case object if needed
        "reviewer_action": review.review_action,
        "case_status": review.case_status,
        "review_outcome": review.review_outcome,
        "reviewer": review.reviewer,
        "notes": review.notes,
        "reviewer_disagreement": reviewer_disagreement
    }

    with open("logs/reviewer_actions.jsonl", "a") as f:
        f.write(json.dumps(log_entry) + "\n")

    return {"status": "review posted successfully", "review": log_entry}