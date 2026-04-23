import sys
import os
from datetime import datetime

import pytest
from pydantic import ValidationError

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.data.schema import Trade, LabeledTrade


def test_trade_model_defaults_and_fields():
    trade = Trade(
        client_age=35,
        client_income=90000,
        risk_tolerance='Medium',
        investment_experience='Intermediate',
        investment_objective='Growth',
        investment_time_horizon='Medium',
        investment_type='Stocks',
        investment_amount=15000.0,
        advisor_id='A123',
        advisor_experience='Mid',
        advisor_history_risk='Low',
        has_rationale=True,
        kyc_completeness='Complete',
    )

    assert isinstance(trade.trade_id, str)
    assert isinstance(trade.trade_timestamp, datetime)
    assert trade.advisor_notes is None
    assert trade.investment_amount == 15000.0
    assert trade.kyc_completeness == 'Complete'


def test_labeled_trade_inherits_trade_fields():
    labeled_trade = LabeledTrade(
        client_age=45,
        client_income=120000,
        risk_tolerance='High',
        investment_experience='Advanced',
        investment_objective='Balanced',
        investment_time_horizon='Long',
        investment_type='Mutual Funds',
        investment_amount=20000.0,
        advisor_id='A456',
        advisor_experience='Senior',
        advisor_history_risk='Medium',
        has_rationale=False,
        kyc_completeness='Complete',
        true_compliance=True,
        case_type='Aligned Recommendation',
        difficulty='Easy',
    )

    assert labeled_trade.true_compliance is True
    assert labeled_trade.case_type == 'Aligned Recommendation'
    assert labeled_trade.difficulty == 'Easy'
    assert labeled_trade.investment_type == 'Mutual Funds'


def test_trade_model_invalid_literal_value():
    with pytest.raises(ValidationError):
        Trade(
            client_age=28,
            client_income=50000,
            risk_tolerance='Very High',
            investment_experience='Beginner',
            investment_objective='Income',
            investment_time_horizon='Short',
            investment_type='Bonds',
            investment_amount=5000.0,
            advisor_id='A789',
            advisor_experience='Junior',
            advisor_history_risk='Low',
            has_rationale=True,
            kyc_completeness='Complete',
        )
