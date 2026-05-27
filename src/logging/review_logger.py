"""
review_logger.py

Human reviewer audit logging.

Purpose:
    Logs reviewer decisions and manual interventions
    for compliance audit traceability.

Author: Jason Chau
Date: 2026-05-27
"""

from src.api.models import ReviewSubmission
from src.logging.logger import append_jsonl
from src.config.paths import LOG_DIR

def log_reviewer_action(
    trade_id: str,
    review: ReviewSubmission,
    reviewer_disagreement: bool
) -> None:
    """
    Logs a human reviewer action.
    """

    log_entry = {
        "trade_id": trade_id,
        "ai_recommendation": review.ai_recommendation,  # Consider removing in future since this is not a reviewer action, and we can look it up on the backend case object if needed
        "reviewer_action": review.review_action,
        "case_status": review.case_status,
        "review_outcome": review.review_outcome,
        "reviewer": review.reviewer,
        "notes": review.notes,
        "reviewer_disagreement": reviewer_disagreement
    }

    append_jsonl(
        LOG_DIR / "reviewer_actions.jsonl",
        log_entry
    )