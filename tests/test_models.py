import sys
import os

import pytest
from pydantic import ValidationError

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.api.models import ReviewSubmission


def test_review_submission_model_accepts_valid_data():
    review = ReviewSubmission(
        reviewer='Alice',
        action='approve',
        notes='This review looks complete.'
    )

    assert review.reviewer == 'Alice'
    assert review.action == 'approve'
    assert review.notes == 'This review looks complete.'


def test_review_submission_model_accepts_override_action():
    review = ReviewSubmission(
        reviewer='Bob',
        action='override',
        notes='Override is allowed.'
    )

    assert review.action == 'override'


def test_review_submission_model_rejects_invalid_action():
    with pytest.raises(ValidationError):
        ReviewSubmission(
            reviewer='Charlie',
            action='reject',
            notes='Invalid action value.'
        )


def test_review_submission_model_rejects_missing_reviewer():
    with pytest.raises(ValidationError):
        ReviewSubmission(
            action='approve',
            notes='Missing reviewer field.'
        )


def test_review_submission_model_rejects_missing_action():
    with pytest.raises(ValidationError):
        ReviewSubmission(
            reviewer='Bob',
            notes='Missing action field.'
        )


def test_review_submission_model_rejects_missing_notes():
    with pytest.raises(ValidationError):
        ReviewSubmission(
            reviewer='Bob',
            action='approve'
        )
