import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from unittest.mock import Mock
from src.data.schema import Trade
from src.decisioning.documentation_signals import is_missing_rationale


class TestIsMissingRationale:
    def test_returns_true_when_has_rationale_is_false(self):
        """Test that is_missing_rationale returns True when trade has no rationale."""
        trade = Mock(spec=Trade)
        trade.has_rationale = False
        
        result = is_missing_rationale(trade)
        assert result is True

    def test_returns_false_when_has_rationale_is_true(self):
        """Test that is_missing_rationale returns False when trade has rationale."""
        trade = Mock(spec=Trade)
        trade.has_rationale = True
        
        result = is_missing_rationale(trade)
        assert result is False

    def test_with_real_trade_object_missing_rationale(self):
        """Test with actual Trade object that has no rationale."""
        trade = Trade(
            client_age=35,
            client_income=75000,
            risk_tolerance='Medium',
            investment_experience='Intermediate',
            investment_objective='Growth',
            investment_time_horizon='Medium',
            investment_type='Stocks',
            investment_amount=10000.0,
            advisor_id='A123',
            advisor_experience='Mid',
            advisor_history_risk='Low',
            has_rationale=False,
            kyc_completeness='Complete'
        )
        
        result = is_missing_rationale(trade)
        assert result is True

    def test_with_real_trade_object_with_rationale(self):
        """Test with actual Trade object that has rationale."""
        trade = Trade(
            client_age=35,
            client_income=75000,
            risk_tolerance='Medium',
            investment_experience='Intermediate',
            investment_objective='Growth',
            investment_time_horizon='Medium',
            investment_type='Stocks',
            investment_amount=10000.0,
            advisor_id='A123',
            advisor_experience='Mid',
            advisor_history_risk='Low',
            has_rationale=True,
            kyc_completeness='Complete'
        )
        
        result = is_missing_rationale(trade)
        assert result is False