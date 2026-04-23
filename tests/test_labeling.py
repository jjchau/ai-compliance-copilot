import sys
import os
import pytest
from unittest.mock import Mock, patch
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.data.schema import Trade
from src.decisioning.labeling import compute_true_compliance, assign_case_type, assign_difficulty

@pytest.fixture
def mock_trade():
    return Mock(spec=Trade)


class TestComputeTrueCompliance:
    def test_no_violations(self, mock_trade):
        with patch('src.decisioning.labeling.is_kyc_violation', return_value=False), \
             patch('src.decisioning.labeling.is_suitability_violation', return_value=False), \
             patch('src.decisioning.labeling.is_experience_violation', return_value=False):
            assert compute_true_compliance(mock_trade) is True

    def test_with_violations(self, mock_trade):
        with patch('src.decisioning.labeling.is_kyc_violation', return_value=True), \
             patch('src.decisioning.labeling.is_suitability_violation', return_value=False), \
             patch('src.decisioning.labeling.is_experience_violation', return_value=False):
            assert compute_true_compliance(mock_trade) is False


class TestAssignCaseType:
    def test_kyc_violation(self, mock_trade):
        with patch('src.decisioning.labeling.is_kyc_violation', return_value=True), \
             patch('src.decisioning.labeling.is_suitability_violation', return_value=False), \
             patch('src.decisioning.labeling.is_experience_violation', return_value=False):
            assert assign_case_type(mock_trade) == "KYC Missing"

    def test_suitability_violation(self, mock_trade):
        with patch('src.decisioning.labeling.is_kyc_violation', return_value=False), \
             patch('src.decisioning.labeling.is_suitability_violation', return_value=True), \
             patch('src.decisioning.labeling.is_experience_violation', return_value=False):
            assert assign_case_type(mock_trade) == "Suitability Violation"

    def test_experience_violation(self, mock_trade):
        with patch('src.decisioning.labeling.is_kyc_violation', return_value=False), \
             patch('src.decisioning.labeling.is_suitability_violation', return_value=False), \
             patch('src.decisioning.labeling.is_experience_violation', return_value=True):
            assert assign_case_type(mock_trade) == "Insufficient Experience"

    def test_risk_signal(self, mock_trade):
        with patch('src.decisioning.labeling.is_kyc_violation', return_value=False), \
             patch('src.decisioning.labeling.is_suitability_violation', return_value=False), \
             patch('src.decisioning.labeling.is_experience_violation', return_value=False), \
             patch('src.decisioning.labeling.is_investment_too_agressive_for_horizon', return_value=True), \
             patch('src.decisioning.labeling.is_investment_too_aggressive_for_objective', return_value=False), \
             patch('src.decisioning.labeling.is_overexposure', return_value=False), \
             patch('src.decisioning.labeling.is_kyc_uncertain', return_value=False):
            assert assign_case_type(mock_trade) == "Risk Signal"

    def test_risk_signal_due_to_kyc_uncertain(self, mock_trade):
        with patch('src.decisioning.labeling.is_kyc_violation', return_value=False), \
             patch('src.decisioning.labeling.is_suitability_violation', return_value=False), \
             patch('src.decisioning.labeling.is_experience_violation', return_value=False), \
             patch('src.decisioning.labeling.is_investment_too_agressive_for_horizon', return_value=False), \
             patch('src.decisioning.labeling.is_investment_too_aggressive_for_objective', return_value=False), \
             patch('src.decisioning.labeling.is_overexposure', return_value=False), \
             patch('src.decisioning.labeling.is_kyc_uncertain', return_value=True):
            assert assign_case_type(mock_trade) == "Risk Signal"

    def test_aligned_recommendation(self, mock_trade):
        with patch('src.decisioning.labeling.is_kyc_violation', return_value=False), \
             patch('src.decisioning.labeling.is_suitability_violation', return_value=False), \
             patch('src.decisioning.labeling.is_experience_violation', return_value=False), \
             patch('src.decisioning.labeling.is_investment_too_agressive_for_horizon', return_value=False), \
             patch('src.decisioning.labeling.is_investment_too_aggressive_for_objective', return_value=False), \
             patch('src.decisioning.labeling.is_overexposure', return_value=False), \
             patch('src.decisioning.labeling.is_kyc_uncertain', return_value=False):
            assert assign_case_type(mock_trade) == "Aligned Recommendation"


class TestAssignDifficulty:
    def test_easy_no_violations(self, mock_trade):
        with patch('src.decisioning.labeling.is_kyc_violation', return_value=False), \
             patch('src.decisioning.labeling.is_suitability_violation', return_value=False), \
             patch('src.decisioning.labeling.is_experience_violation', return_value=False), \
             patch('src.decisioning.labeling.is_investment_too_agressive_for_horizon', return_value=False), \
             patch('src.decisioning.labeling.is_investment_too_aggressive_for_objective', return_value=False), \
             patch('src.decisioning.labeling.is_overexposure', return_value=False), \
             patch('src.decisioning.labeling.is_kyc_uncertain', return_value=False):
            assert assign_difficulty(mock_trade) == "Easy"

    def test_easy_multiple_hard_violations(self, mock_trade):
        with patch('src.decisioning.labeling.is_kyc_violation', return_value=True), \
             patch('src.decisioning.labeling.is_suitability_violation', return_value=True), \
             patch('src.decisioning.labeling.is_experience_violation', return_value=False), \
             patch('src.decisioning.labeling.is_investment_too_agressive_for_horizon', return_value=False), \
             patch('src.decisioning.labeling.is_investment_too_aggressive_for_objective', return_value=False), \
             patch('src.decisioning.labeling.is_overexposure', return_value=False), \
             patch('src.decisioning.labeling.is_kyc_uncertain', return_value=False):
            assert assign_difficulty(mock_trade) == "Easy"

    def test_easy_one_violation_no_signals(self, mock_trade):
        with patch('src.decisioning.labeling.is_kyc_violation', return_value=True), \
             patch('src.decisioning.labeling.is_suitability_violation', return_value=False), \
             patch('src.decisioning.labeling.is_experience_violation', return_value=False), \
             patch('src.decisioning.labeling.is_investment_too_agressive_for_horizon', return_value=False), \
             patch('src.decisioning.labeling.is_investment_too_aggressive_for_objective', return_value=False), \
             patch('src.decisioning.labeling.is_overexposure', return_value=False), \
             patch('src.decisioning.labeling.is_kyc_uncertain', return_value=False):
            assert assign_difficulty(mock_trade) == "Easy"

    def test_hard_soft_signals_only(self, mock_trade):
        with patch('src.decisioning.labeling.is_kyc_violation', return_value=False), \
             patch('src.decisioning.labeling.is_suitability_violation', return_value=False), \
             patch('src.decisioning.labeling.is_experience_violation', return_value=False), \
             patch('src.decisioning.labeling.is_investment_too_agressive_for_horizon', return_value=True), \
             patch('src.decisioning.labeling.is_investment_too_aggressive_for_objective', return_value=False), \
             patch('src.decisioning.labeling.is_overexposure', return_value=False), \
             patch('src.decisioning.labeling.is_kyc_uncertain', return_value=False):
            assert assign_difficulty(mock_trade) == "Hard"

    def test_hard_kyc_uncertain_only(self, mock_trade):
        with patch('src.decisioning.labeling.is_kyc_violation', return_value=False), \
             patch('src.decisioning.labeling.is_suitability_violation', return_value=False), \
             patch('src.decisioning.labeling.is_experience_violation', return_value=False), \
             patch('src.decisioning.labeling.is_investment_too_agressive_for_horizon', return_value=False), \
             patch('src.decisioning.labeling.is_investment_too_aggressive_for_objective', return_value=False), \
             patch('src.decisioning.labeling.is_overexposure', return_value=False), \
             patch('src.decisioning.labeling.is_kyc_uncertain', return_value=True):
            assert assign_difficulty(mock_trade) == "Hard"

    def test_easy_mixed_violations_and_signals(self, mock_trade):
        with patch('src.decisioning.labeling.is_kyc_violation', return_value=True), \
             patch('src.decisioning.labeling.is_suitability_violation', return_value=False), \
             patch('src.decisioning.labeling.is_experience_violation', return_value=False), \
             patch('src.decisioning.labeling.is_investment_too_agressive_for_horizon', return_value=True), \
             patch('src.decisioning.labeling.is_investment_too_aggressive_for_objective', return_value=False), \
             patch('src.decisioning.labeling.is_overexposure', return_value=False), \
             patch('src.decisioning.labeling.is_kyc_uncertain', return_value=False):
            assert assign_difficulty(mock_trade) == "Easy"