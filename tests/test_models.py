import sys
import os

import pytest
from pydantic import ValidationError

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.api.models import ReviewSubmission


def test_review_submission_model_accepts_valid_data():
    review = ReviewSubmission(
        ai_recommendation='suggest_approve',
        review_action='approve',
        case_status='reviewed',
        review_outcome='compliant',
        reviewer='Alice',
        notes='This review looks complete.'
    )

    assert review.reviewer == 'Alice'
    assert review.review_action == 'approve'
    assert review.notes == 'This review looks complete.'


def test_review_submission_model_accepts_override_action():
    review = ReviewSubmission(
        ai_recommendation='suggest_escalate',
        review_action='escalate',
        case_status='awaiting_senior_review',
        review_outcome=None,
        reviewer='Bob',
        notes='Escalation requested.'
    )

    assert review.review_action == 'escalate'


def test_review_submission_model_rejects_invalid_action():
    with pytest.raises(ValidationError):
        ReviewSubmission(
            reviewer='Charlie',
            ai_recommendation='n/a',
            review_action='override',
            case_status='pending',
            review_outcome=None,
            notes='Invalid action value.'
        )


def test_review_submission_model_rejects_missing_reviewer():
    with pytest.raises(ValidationError):
        ReviewSubmission(
            ai_recommendation='n/a',
            review_action='approve',
            case_status='pending',
            review_outcome=None,
            notes='Missing reviewer field.'
        )


def test_review_submission_model_rejects_missing_action():
    with pytest.raises(ValidationError):
        ReviewSubmission(
            ai_recommendation='n/a',
            case_status='pending',
            review_outcome=None,
            reviewer='Bob',
            notes='Missing action field.'
        )


def test_review_submission_model_rejects_missing_notes():
    with pytest.raises(ValidationError):
        ReviewSubmission(
            ai_recommendation='n/a',
            review_action='approve',
            case_status='pending',
            review_outcome=None,
            reviewer='Bob'
        )
