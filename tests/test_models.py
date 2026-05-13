import sys
import os

import pytest
from pydantic import ValidationError

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.api.models import ReviewSubmission


def test_review_submission_model_accepts_valid_data():
    review = ReviewSubmission(
        reviewer='Alice',
        decision='Approve',
        notes='This review looks complete.'
    )

    assert review.reviewer == 'Alice'
    assert review.decision == 'Approve'
    assert review.notes == 'This review looks complete.'


def test_review_submission_model_rejects_missing_reviewer():
    with pytest.raises(ValidationError):
        ReviewSubmission(
            decision='Reject',
            notes='Missing reviewer field.'
        )


def test_review_submission_model_rejects_missing_decision():
    with pytest.raises(ValidationError):
        ReviewSubmission(
            reviewer='Bob',
            notes='Missing decision field.'
        )


def test_review_submission_model_rejects_missing_notes():
    with pytest.raises(ValidationError):
        ReviewSubmission(
            reviewer='Bob',
            decision='Review'
        )
