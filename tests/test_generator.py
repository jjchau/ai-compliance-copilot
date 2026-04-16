import pytest
from unittest.mock import patch, MagicMock

from src.data.generator import (
    generate_base_case,
    generate_labeled_case,
    RISK_TOLERANCES,
    INVESTMENT_EXPERIENCE,
    INVESTMENT_OBJECTIVES,
    INVESTMENT_TIME_HORIZONS,
    INVESTMENT_TYPES,
    ADVISOR_EXPERIENCE,
    KYC_COMPLETENESS,
    advisor_profiles
)


class TestGenerateBaseCase:
    def test_generate_base_case_returns_trade(self):
        trade = generate_base_case()
        assert trade is not None
        assert hasattr(trade, 'client_age')
        assert hasattr(trade, 'advisor_id')

    def test_client_age_in_valid_range(self):
        for _ in range(10):
            trade = generate_base_case()
            assert 18 <= trade.client_age <= 80

    def test_client_income_in_valid_range(self):
        for _ in range(10):
            trade = generate_base_case()
            assert 30000 <= trade.client_income <= 200000

    def test_investment_amount_in_valid_range(self):
        for _ in range(10):
            trade = generate_base_case()
            assert 100 <= trade.investment_amount <= 100000

    def test_risk_tolerance_valid_choice(self):
        for _ in range(10):
            trade = generate_base_case()
            assert trade.risk_tolerance in RISK_TOLERANCES

    def test_investment_experience_valid_choice(self):
        for _ in range(10):
            trade = generate_base_case()
            assert trade.investment_experience in INVESTMENT_EXPERIENCE

    def test_investment_objective_valid_choice(self):
        for _ in range(10):
            trade = generate_base_case()
            assert trade.investment_objective in INVESTMENT_OBJECTIVES

    def test_investment_time_horizon_valid_choice(self):
        for _ in range(10):
            trade = generate_base_case()
            assert trade.investment_time_horizon in INVESTMENT_TIME_HORIZONS

    def test_investment_type_valid_choice(self):
        for _ in range(10):
            trade = generate_base_case()
            assert trade.investment_type in INVESTMENT_TYPES

    def test_advisor_id_valid(self):
        for _ in range(10):
            trade = generate_base_case()
            assert trade.advisor_id in advisor_profiles

    def test_advisor_history_risk_matches_profile(self):
        for _ in range(10):
            trade = generate_base_case()
            assert trade.advisor_history_risk == advisor_profiles[trade.advisor_id]

    def test_has_rationale_is_boolean(self):
        for _ in range(10):
            trade = generate_base_case()
            assert isinstance(trade.has_rationale, bool)

    def test_advisor_notes_valid(self):
        for _ in range(10):
            trade = generate_base_case()
            assert trade.advisor_notes is None or isinstance(trade.advisor_notes, str)

    def test_kyc_completeness_valid_choice(self):
        for _ in range(10):
            trade = generate_base_case()
            assert trade.kyc_completeness in KYC_COMPLETENESS


class TestGenerateLabeledCase:
    @patch('src.data.generator.compute_true_compliance')
    @patch('src.data.generator.assign_case_type')
    def test_generate_labeled_case_returns_labeled_trade(self, mock_assign, mock_compute):
        mock_compute.return_value = True
        mock_assign.return_value = "Aligned Recommendation"
        
        labeled_trade = generate_labeled_case()
        assert labeled_trade is not None
        assert hasattr(labeled_trade, 'true_compliance')
        assert labeled_trade.true_compliance is True
        assert hasattr(labeled_trade, 'case_type')
        assert labeled_trade.case_type == "Aligned Recommendation"
        assert hasattr(labeled_trade, 'difficulty')
        assert labeled_trade.difficulty in ['Easy', 'Medium', 'Hard']
        assert hasattr(labeled_trade, 'case_type')
        assert hasattr(labeled_trade, 'difficulty')

    @patch('src.data.generator.compute_true_compliance')
    @patch('src.data.generator.assign_case_type')
    def test_true_compliance_is_set(self, mock_assign, mock_compute):
        mock_compute.return_value = True
        mock_assign.return_value = "Aligned Recommendation"
        
        labeled_trade = generate_labeled_case()
        assert labeled_trade.true_compliance is True

    @patch('src.data.generator.compute_true_compliance')
    @patch('src.data.generator.assign_case_type')
    def test_case_type_is_set(self, mock_assign, mock_compute):
        mock_compute.return_value = False
        mock_assign.return_value = "Suitability Violation"
        
        labeled_trade = generate_labeled_case()
        assert labeled_trade.case_type == "Suitability Violation"

    @patch('src.data.generator.compute_true_compliance')
    @patch('src.data.generator.assign_case_type')
    def test_difficulty_is_valid(self, mock_assign, mock_compute):
        mock_compute.return_value = True
        mock_assign.return_value = "Aligned Recommendation"
        
        for _ in range(10):
            labeled_trade = generate_labeled_case()
            assert labeled_trade.difficulty in ['Easy', 'Medium', 'Hard']

    @patch('src.data.generator.compute_true_compliance')
    @patch('src.data.generator.assign_case_type')
    def test_labeled_case_inherits_base_trade_fields(self, mock_assign, mock_compute):
        mock_compute.return_value = False
        mock_assign.return_value = "KYC Missing"
        
        labeled_trade = generate_labeled_case()
        assert 18 <= labeled_trade.client_age <= 80
        assert labeled_trade.advisor_id in advisor_profiles