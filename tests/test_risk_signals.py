import pytest
from unittest.mock import Mock
from src.data.schema import Trade
from src.decisioning.risk_signals import is_horizon_mismatch, is_objective_mismatch, is_overexposure, is_kyc_uncertain


@pytest.fixture
def mock_trade():
    return Mock(spec=Trade)


class TestIsHorizonMismatch:
    def test_short_horizon_stocks(self, mock_trade):
        mock_trade.investment_time_horizon = 'Short'
        mock_trade.investment_type = 'Stocks'
        assert is_horizon_mismatch(mock_trade) is True

    def test_short_horizon_options(self, mock_trade):
        mock_trade.investment_time_horizon = 'Short'
        mock_trade.investment_type = 'Options'
        assert is_horizon_mismatch(mock_trade) is True

    def test_short_horizon_bonds(self, mock_trade):
        mock_trade.investment_time_horizon = 'Short'
        mock_trade.investment_type = 'Bonds'
        assert is_horizon_mismatch(mock_trade) is False

    def test_medium_horizon_stocks(self, mock_trade):
        mock_trade.investment_time_horizon = 'Medium'
        mock_trade.investment_type = 'Stocks'
        assert is_horizon_mismatch(mock_trade) is False

    def test_long_horizon_options(self, mock_trade):
        mock_trade.investment_time_horizon = 'Long'
        mock_trade.investment_type = 'Options'
        assert is_horizon_mismatch(mock_trade) is False


class TestIsObjectiveMismatch:
    def test_preservation_stocks(self, mock_trade):
        mock_trade.investment_objective = 'Preservation'
        mock_trade.investment_type = 'Stocks'
        assert is_objective_mismatch(mock_trade) is True

    def test_preservation_options(self, mock_trade):
        mock_trade.investment_objective = 'Preservation'
        mock_trade.investment_type = 'Options'
        assert is_objective_mismatch(mock_trade) is True

    def test_preservation_bonds(self, mock_trade):
        mock_trade.investment_objective = 'Preservation'
        mock_trade.investment_type = 'Bonds'
        assert is_objective_mismatch(mock_trade) is False

    def test_growth_stocks(self, mock_trade):
        mock_trade.investment_objective = 'Growth'
        mock_trade.investment_type = 'Stocks'
        assert is_objective_mismatch(mock_trade) is False

    def test_income_options(self, mock_trade):
        mock_trade.investment_objective = 'Income'
        mock_trade.investment_type = 'Options'
        assert is_objective_mismatch(mock_trade) is False


class TestIsOverexposure:
    def test_overexposure_high_amount(self, mock_trade):
        mock_trade.investment_amount = 40000
        mock_trade.client_income = 100000
        assert is_overexposure(mock_trade) is True

    def test_overexposure_exact_threshold(self, mock_trade):
        mock_trade.investment_amount = 30000
        mock_trade.client_income = 100000
        assert is_overexposure(mock_trade) is False

    def test_no_overexposure_low_amount(self, mock_trade):
        mock_trade.investment_amount = 20000
        mock_trade.client_income = 100000
        assert is_overexposure(mock_trade) is False

    def test_overexposure_zero_income(self, mock_trade):
        mock_trade.investment_amount = 1
        mock_trade.client_income = 0
        assert is_overexposure(mock_trade) is True

    def test_no_overexposure_zero_amount(self, mock_trade):
        mock_trade.investment_amount = 0
        mock_trade.client_income = 100000
        assert is_overexposure(mock_trade) is False


class TestIsKycUncertain:
    def test_kyc_uncertain(self, mock_trade):
        mock_trade.kyc_completeness = 'Uncertain'
        assert is_kyc_uncertain(mock_trade) is True

    def test_kyc_complete(self, mock_trade):
        mock_trade.kyc_completeness = 'Complete'
        assert is_kyc_uncertain(mock_trade) is False
