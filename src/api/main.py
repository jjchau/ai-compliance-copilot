from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from src.services.review_case_service import get_all_enriched_cases, get_single_case_from_db
from src.api.models import ReviewSubmission
from src.logging.review_logger import log_reviewer_action

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
    """
    Returns the complete list of cases instantly. 
    Fully populated with escalation_levels ready for dynamic frontend layout sorting.
    """
    return get_all_enriched_cases(escalation_filter=escalation)
    
@app.get("/cases/{trade_id}")
def get_case(trade_id: str):
    """
    Returns individual case records instantly with stable, cached data structures.
    """
    case_data = get_single_case_from_db(trade_id)
    if case_data is None:
        raise HTTPException(status_code=404, detail="Case not found")
    return {"case": case_data}

@app.post("/cases/{trade_id}/review")
def submit_review(trade_id: str, review: ReviewSubmission):
    # Query the service layer instead of the deleted in-memory case_lookup dictionary
    case = get_single_case_from_db(trade_id)
    if case is None:
        raise HTTPException(status_code=404, detail="Case not found")

    reviewer_disagreement = False

    if review.review_outcome is not None:
        reviewer_disagreement = (
            review.ai_recommendation != review.review_outcome
        )

    log_reviewer_action(
        trade_id=trade_id,
        review=review,
        reviewer_disagreement=reviewer_disagreement
    )

    review_payload = {
        "trade_id": trade_id,
        "ai_recommendation": review.ai_recommendation,
        "review_action": review.review_action,
        "reviewer_action": review.review_action,
        "case_status": review.case_status,
        "review_outcome": review.review_outcome,
        "reviewer": review.reviewer,
        "notes": review.notes,
        "reviewer_disagreement": reviewer_disagreement,
        "timestamp": datetime.now().isoformat()
    }

    return {"status": "review posted successfully", "review": review_payload}