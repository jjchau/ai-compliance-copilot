import pytest
from unittest.mock import Mock, patch
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
             patch('src.decisioning.labeling.is_horizon_mismatch', return_value=True), \
             patch('src.decisioning.labeling.is_objective_mismatch', return_value=False), \
             patch('src.decisioning.labeling.is_overexposure', return_value=False):
            assert assign_case_type(mock_trade) == "Risk Signal"

    def test_aligned_recommendation(self, mock_trade):
        with patch('src.decisioning.labeling.is_kyc_violation', return_value=False), \
             patch('src.decisioning.labeling.is_suitability_violation', return_value=False), \
             patch('src.decisioning.labeling.is_experience_violation', return_value=False), \
             patch('src.decisioning.labeling.is_horizon_mismatch', return_value=False), \
             patch('src.decisioning.labeling.is_objective_mismatch', return_value=False), \
             patch('src.decisioning.labeling.is_overexposure', return_value=False):
            assert assign_case_type(mock_trade) == "Aligned Recommendation"


class TestAssignDifficulty:
    def test_easy_no_violations(self, mock_trade):
        with patch('src.decisioning.labeling.is_kyc_violation', return_value=False), \
             patch('src.decisioning.labeling.is_suitability_violation', return_value=False), \
             patch('src.decisioning.labeling.is_experience_violation', return_value=False), \
             patch('src.decisioning.labeling.is_horizon_mismatch', return_value=False), \
             patch('src.decisioning.labeling.is_objective_mismatch', return_value=False), \
             patch('src.decisioning.labeling.is_overexposure', return_value=False):
            assert assign_difficulty(mock_trade) == "Easy"

    def test_easy_multiple_hard_violations(self, mock_trade):
        with patch('src.decisioning.labeling.is_kyc_violation', return_value=True), \
             patch('src.decisioning.labeling.is_suitability_violation', return_value=True), \
             patch('src.decisioning.labeling.is_experience_violation', return_value=False), \
             patch('src.decisioning.labeling.is_horizon_mismatch', return_value=False), \
             patch('src.decisioning.labeling.is_objective_mismatch', return_value=False), \
             patch('src.decisioning.labeling.is_overexposure', return_value=False):
            assert assign_difficulty(mock_trade) == "Easy"

    def test_medium_one_violation_no_signals(self, mock_trade):
        with patch('src.decisioning.labeling.is_kyc_violation', return_value=True), \
             patch('src.decisioning.labeling.is_suitability_violation', return_value=False), \
             patch('src.decisioning.labeling.is_experience_violation', return_value=False), \
             patch('src.decisioning.labeling.is_horizon_mismatch', return_value=False), \
             patch('src.decisioning.labeling.is_objective_mismatch', return_value=False), \
             patch('src.decisioning.labeling.is_overexposure', return_value=False):
            assert assign_difficulty(mock_trade) == "Medium"

    def test_hard_soft_signals_only(self, mock_trade):
        with patch('src.decisioning.labeling.is_kyc_violation', return_value=False), \
             patch('src.decisioning.labeling.is_suitability_violation', return_value=False), \
             patch('src.decisioning.labeling.is_experience_violation', return_value=False), \
             patch('src.decisioning.labeling.is_horizon_mismatch', return_value=True), \
             patch('src.decisioning.labeling.is_objective_mismatch', return_value=False), \
             patch('src.decisioning.labeling.is_overexposure', return_value=False):
            assert assign_difficulty(mock_trade) == "Hard"

    def test_hard_mixed_violations_and_signals(self, mock_trade):
        with patch('src.decisioning.labeling.is_kyc_violation', return_value=True), \
             patch('src.decisioning.labeling.is_suitability_violation', return_value=False), \
             patch('src.decisioning.labeling.is_experience_violation', return_value=False), \
             patch('src.decisioning.labeling.is_horizon_mismatch', return_value=True), \
             patch('src.decisioning.labeling.is_objective_mismatch', return_value=False), \
             patch('src.decisioning.labeling.is_overexposure', return_value=False):
            assert assign_difficulty(mock_trade) == "Hard"