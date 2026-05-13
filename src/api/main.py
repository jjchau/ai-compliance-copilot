from fastapi import FastAPI, HTTPException
from datetime import datetime
import json
from src.api.data_loader import cases, case_lookup
from src.api.models import ReviewSubmission

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Compliance Copilot API is running!"}

@app.get("/cases")
def get_cases(escalation: str | None = None):
    if escalation == "urgent":
        return {"cases": [case for case in cases if case["escalation_level"] == "urgent"]}
    elif escalation == "priority":
        return {"cases": [case for case in cases if case["escalation_level"] == "priority"]}
    elif escalation == "queue":
        return {"cases": [case for case in cases if case["escalation_level"] == "queue"]}
    return {"cases": cases}

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

    log_entry = {
        "trade_id": trade_id,
        "reviewer": review.reviewer,
        "decision": review.decision,
        "notes": review.notes,
        "timestamp": datetime.now().isoformat()
    }

    with open("logs/reviewer_actions.jsonl", "a") as f:
        f.write(json.dumps(log_entry) + "\n")

    return {"status": "review posted successfully", "review": log_entry}