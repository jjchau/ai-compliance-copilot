import pytest
from unittest.mock import Mock
from src.data.schema import Trade
from src.decisioning.risk_signals import (
    is_investment_too_agressive_for_horizon, 
    is_investment_too_aggressive_for_objective, 
    is_overexposure, 
    is_kyc_uncertain,
    is_kyc_missing,
    is_risk_too_high_for_profile,
    is_too_complex_for_experience,
    is_risk_too_low_for_profile,
    is_investment_too_conservative_for_horizon,
    is_investment_too_conservative_for_objective,
    is_advisor_history_high_risk
)


@pytest.fixture
def mock_trade():
    return Mock(spec=Trade)


class TestIsHorizonMismatch:
    def test_short_horizon_stocks(self, mock_trade):
        mock_trade.investment_time_horizon = 'Short'
        mock_trade.investment_type = 'Stocks'
        assert is_investment_too_agressive_for_horizon(mock_trade) is True

    def test_short_horizon_options(self, mock_trade):
        mock_trade.investment_time_horizon = 'Short'
        mock_trade.investment_type = 'Options'
        assert is_investment_too_agressive_for_horizon(mock_trade) is True

    def test_short_horizon_bonds(self, mock_trade):
        mock_trade.investment_time_horizon = 'Short'
        mock_trade.investment_type = 'Bonds'
        assert is_investment_too_agressive_for_horizon(mock_trade) is False

    def test_medium_horizon_stocks(self, mock_trade):
        mock_trade.investment_time_horizon = 'Medium'
        mock_trade.investment_type = 'Stocks'
        assert is_investment_too_agressive_for_horizon(mock_trade) is False

    def test_long_horizon_options(self, mock_trade):
        mock_trade.investment_time_horizon = 'Long'
        mock_trade.investment_type = 'Options'
        assert is_investment_too_agressive_for_horizon(mock_trade) is False


class TestIsInvestmentTooAggressiveForObjective:
    def test_preservation_stocks(self, mock_trade):
        mock_trade.investment_objective = 'Preservation'
        mock_trade.investment_type = 'Stocks'
        assert is_investment_too_aggressive_for_objective(mock_trade) is True

    def test_preservation_options(self, mock_trade):
        mock_trade.investment_objective = 'Preservation'
        mock_trade.investment_type = 'Options'
        assert is_investment_too_aggressive_for_objective(mock_trade) is True

    def test_preservation_bonds(self, mock_trade):
        mock_trade.investment_objective = 'Preservation'
        mock_trade.investment_type = 'Bonds'
        assert is_investment_too_aggressive_for_objective(mock_trade) is False

    def test_growth_stocks(self, mock_trade):
        mock_trade.investment_objective = 'Growth'
        mock_trade.investment_type = 'Stocks'
        assert is_investment_too_aggressive_for_objective(mock_trade) is False

    def test_income_options(self, mock_trade):
        mock_trade.investment_objective = 'Income'
        mock_trade.investment_type = 'Options'
        assert is_investment_too_aggressive_for_objective(mock_trade) is False


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


class TestIsKycMissing:
    def test_kyc_missing(self, mock_trade):
        mock_trade.kyc_completeness = 'Missing'
        assert is_kyc_missing(mock_trade) is True

    def test_kyc_not_missing(self, mock_trade):
        mock_trade.kyc_completeness = 'Complete'
        assert is_kyc_missing(mock_trade) is False


class TestIsRiskTooHighForProfile:
    def test_low_risk_tolerance_stocks(self, mock_trade):
        mock_trade.risk_tolerance = 'Low'
        mock_trade.investment_type = 'Stocks'
        assert is_risk_too_high_for_profile(mock_trade) is True

    def test_low_risk_tolerance_options(self, mock_trade):
        mock_trade.risk_tolerance = 'Low'
        mock_trade.investment_type = 'Options'
        assert is_risk_too_high_for_profile(mock_trade) is True

    def test_low_risk_tolerance_bonds(self, mock_trade):
        mock_trade.risk_tolerance = 'Low'
        mock_trade.investment_type = 'Bonds'
        assert is_risk_too_high_for_profile(mock_trade) is False

    def test_medium_risk_tolerance_stocks(self, mock_trade):
        mock_trade.risk_tolerance = 'Medium'
        mock_trade.investment_type = 'Stocks'
        assert is_risk_too_high_for_profile(mock_trade) is False


class TestIsTooComplexForExperience:
    def test_beginner_options(self, mock_trade):
        mock_trade.investment_experience = 'Beginner'
        mock_trade.investment_type = 'Options'
        assert is_too_complex_for_experience(mock_trade) is True

    def test_beginner_stocks(self, mock_trade):
        mock_trade.investment_experience = 'Beginner'
        mock_trade.investment_type = 'Stocks'
        assert is_too_complex_for_experience(mock_trade) is False

    def test_intermediate_options(self, mock_trade):
        mock_trade.investment_experience = 'Intermediate'
        mock_trade.investment_type = 'Options'
        assert is_too_complex_for_experience(mock_trade) is False

    def test_advanced_options(self, mock_trade):
        mock_trade.investment_experience = 'Advanced'
        mock_trade.investment_type = 'Options'
        assert is_too_complex_for_experience(mock_trade) is False


class TestIsRiskTooLowForProfile:
    def test_high_risk_tolerance_bonds(self, mock_trade):
        mock_trade.risk_tolerance = 'High'
        mock_trade.investment_type = 'Bonds'
        assert is_risk_too_low_for_profile(mock_trade) is True

    def test_high_risk_tolerance_gics(self, mock_trade):
        mock_trade.risk_tolerance = 'High'
        mock_trade.investment_type = 'GICs'
        assert is_risk_too_low_for_profile(mock_trade) is True

    def test_high_risk_tolerance_stocks(self, mock_trade):
        mock_trade.risk_tolerance = 'High'
        mock_trade.investment_type = 'Stocks'
        assert is_risk_too_low_for_profile(mock_trade) is False

    def test_medium_risk_tolerance_bonds(self, mock_trade):
        mock_trade.risk_tolerance = 'Medium'
        mock_trade.investment_type = 'Bonds'
        assert is_risk_too_low_for_profile(mock_trade) is False


class TestIsInvestmentTooConservativeForHorizon:
    def test_long_horizon_bonds(self, mock_trade):
        mock_trade.investment_time_horizon = 'Long'
        mock_trade.investment_type = 'Bonds'
        assert is_investment_too_conservative_for_horizon(mock_trade) is True

    def test_long_horizon_stocks(self, mock_trade):
        mock_trade.investment_time_horizon = 'Long'
        mock_trade.investment_type = 'Stocks'
        assert is_investment_too_conservative_for_horizon(mock_trade) is False

    def test_short_horizon_bonds(self, mock_trade):
        mock_trade.investment_time_horizon = 'Short'
        mock_trade.investment_type = 'Bonds'
        assert is_investment_too_conservative_for_horizon(mock_trade) is False


class TestIsInvestmentTooConservativeForObjective:
    def test_growth_objective_bonds(self, mock_trade):
        mock_trade.investment_objective = 'Growth'
        mock_trade.investment_type = 'Bonds'
        assert is_investment_too_conservative_for_objective(mock_trade) is True

    def test_growth_objective_stocks(self, mock_trade):
        mock_trade.investment_objective = 'Growth'
        mock_trade.investment_type = 'Stocks'
        assert is_investment_too_conservative_for_objective(mock_trade) is False

    def test_preservation_objective_bonds(self, mock_trade):
        mock_trade.investment_objective = 'Preservation'
        mock_trade.investment_type = 'Bonds'
        assert is_investment_too_conservative_for_objective(mock_trade) is False


class TestIsAdvisorHistoryHighRisk:
    def test_advisor_high_risk(self, mock_trade):
        mock_trade.advisor_history_risk = 'High'
        assert is_advisor_history_high_risk(mock_trade) is True

    def test_advisor_low_risk(self, mock_trade):
        mock_trade.advisor_history_risk = 'Low'
        assert is_advisor_history_high_risk(mock_trade) is False

    def test_advisor_medium_risk(self, mock_trade):
        mock_trade.advisor_history_risk = 'Medium'
        assert is_advisor_history_high_risk(mock_trade) is False
