import pytest
from unittest.mock import Mock, patch
from src.data.schema import Trade
from src.decisioning.labeling import (
    assign_case_type,
    assign_difficulty,
    assign_expected_workflow_bucket,
    assign_primary_policy,
    assign_severity_tier,
    compute_true_compliance,
)

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
             patch('src.decisioning.labeling.is_investment_too_aggressive_for_horizon', return_value=True), \
             patch('src.decisioning.labeling.is_investment_too_aggressive_for_objective', return_value=False), \
             patch('src.decisioning.labeling.is_overexposure', return_value=False), \
             patch('src.decisioning.labeling.is_kyc_uncertain', return_value=False):
            assert assign_case_type(mock_trade) == "Risk Signal"

    def test_risk_signal_due_to_kyc_uncertain(self, mock_trade):
        with patch('src.decisioning.labeling.is_kyc_violation', return_value=False), \
             patch('src.decisioning.labeling.is_suitability_violation', return_value=False), \
             patch('src.decisioning.labeling.is_experience_violation', return_value=False), \
             patch('src.decisioning.labeling.is_investment_too_aggressive_for_horizon', return_value=False), \
             patch('src.decisioning.labeling.is_investment_too_aggressive_for_objective', return_value=False), \
             patch('src.decisioning.labeling.is_overexposure', return_value=False), \
             patch('src.decisioning.labeling.is_kyc_uncertain', return_value=True):
            assert assign_case_type(mock_trade) == "Risk Signal"

    def test_aligned_recommendation(self, mock_trade):
        with patch('src.decisioning.labeling.is_kyc_violation', return_value=False), \
             patch('src.decisioning.labeling.is_suitability_violation', return_value=False), \
             patch('src.decisioning.labeling.is_experience_violation', return_value=False), \
             patch('src.decisioning.labeling.is_investment_too_aggressive_for_horizon', return_value=False), \
             patch('src.decisioning.labeling.is_investment_too_aggressive_for_objective', return_value=False), \
             patch('src.decisioning.labeling.is_overexposure', return_value=False), \
             patch('src.decisioning.labeling.is_kyc_uncertain', return_value=False):
            assert assign_case_type(mock_trade) == "Aligned Recommendation"


class TestAssignDifficulty:
    def test_easy_no_violations(self, mock_trade):
        with patch('src.decisioning.labeling.is_kyc_violation', return_value=False), \
             patch('src.decisioning.labeling.is_suitability_violation', return_value=False), \
             patch('src.decisioning.labeling.is_experience_violation', return_value=False), \
             patch('src.decisioning.labeling.is_investment_too_aggressive_for_horizon', return_value=False), \
             patch('src.decisioning.labeling.is_investment_too_aggressive_for_objective', return_value=False), \
             patch('src.decisioning.labeling.is_overexposure', return_value=False), \
             patch('src.decisioning.labeling.is_kyc_uncertain', return_value=False):
            assert assign_difficulty(mock_trade) == "Easy"

    def test_easy_multiple_hard_violations(self, mock_trade):
        with patch('src.decisioning.labeling.is_kyc_violation', return_value=True), \
             patch('src.decisioning.labeling.is_suitability_violation', return_value=True), \
             patch('src.decisioning.labeling.is_experience_violation', return_value=False), \
             patch('src.decisioning.labeling.is_investment_too_aggressive_for_horizon', return_value=False), \
             patch('src.decisioning.labeling.is_investment_too_aggressive_for_objective', return_value=False), \
             patch('src.decisioning.labeling.is_overexposure', return_value=False), \
             patch('src.decisioning.labeling.is_kyc_uncertain', return_value=False):
            assert assign_difficulty(mock_trade) == "Easy"

    def test_easy_one_violation_no_signals(self, mock_trade):
        with patch('src.decisioning.labeling.is_kyc_violation', return_value=True), \
             patch('src.decisioning.labeling.is_suitability_violation', return_value=False), \
             patch('src.decisioning.labeling.is_experience_violation', return_value=False), \
             patch('src.decisioning.labeling.is_investment_too_aggressive_for_horizon', return_value=False), \
             patch('src.decisioning.labeling.is_investment_too_aggressive_for_objective', return_value=False), \
             patch('src.decisioning.labeling.is_overexposure', return_value=False), \
             patch('src.decisioning.labeling.is_kyc_uncertain', return_value=False):
            assert assign_difficulty(mock_trade) == "Easy"

    def test_hard_soft_signals_only(self, mock_trade):
        with patch('src.decisioning.labeling.is_kyc_violation', return_value=False), \
             patch('src.decisioning.labeling.is_suitability_violation', return_value=False), \
             patch('src.decisioning.labeling.is_experience_violation', return_value=False), \
             patch('src.decisioning.labeling.is_investment_too_aggressive_for_horizon', return_value=True), \
             patch('src.decisioning.labeling.is_investment_too_aggressive_for_objective', return_value=False), \
             patch('src.decisioning.labeling.is_overexposure', return_value=False), \
             patch('src.decisioning.labeling.is_kyc_uncertain', return_value=False):
            assert assign_difficulty(mock_trade) == "Hard"

    def test_hard_kyc_uncertain_only(self, mock_trade):
        with patch('src.decisioning.labeling.is_kyc_violation', return_value=False), \
             patch('src.decisioning.labeling.is_suitability_violation', return_value=False), \
             patch('src.decisioning.labeling.is_experience_violation', return_value=False), \
             patch('src.decisioning.labeling.is_investment_too_aggressive_for_horizon', return_value=False), \
             patch('src.decisioning.labeling.is_investment_too_aggressive_for_objective', return_value=False), \
             patch('src.decisioning.labeling.is_overexposure', return_value=False), \
             patch('src.decisioning.labeling.is_kyc_uncertain', return_value=True):
            assert assign_difficulty(mock_trade) == "Hard"

    def test_easy_mixed_violations_and_signals(self, mock_trade):
        with patch('src.decisioning.labeling.is_kyc_violation', return_value=True), \
             patch('src.decisioning.labeling.is_suitability_violation', return_value=False), \
             patch('src.decisioning.labeling.is_experience_violation', return_value=False), \
             patch('src.decisioning.labeling.is_investment_too_aggressive_for_horizon', return_value=True), \
             patch('src.decisioning.labeling.is_investment_too_aggressive_for_objective', return_value=False), \
             patch('src.decisioning.labeling.is_overexposure', return_value=False), \
             patch('src.decisioning.labeling.is_kyc_uncertain', return_value=False):
            assert assign_difficulty(mock_trade) == "Easy"


def test_assign_difficulty_medium_for_one_hard_violation_with_multiple_soft_signals(mock_trade):
    with patch('src.decisioning.labeling.is_kyc_violation', return_value=True), \
         patch('src.decisioning.labeling.is_suitability_violation', return_value=False), \
         patch('src.decisioning.labeling.is_experience_violation', return_value=False), \
         patch('src.decisioning.labeling.is_investment_too_aggressive_for_horizon', return_value=True), \
         patch('src.decisioning.labeling.is_investment_too_aggressive_for_objective', return_value=True), \
         patch('src.decisioning.labeling.is_overexposure', return_value=False), \
         patch('src.decisioning.labeling.is_kyc_uncertain', return_value=False):
        assert assign_difficulty(mock_trade) == "Medium"


def test_assign_severity_tier_high_medium_and_low(mock_trade):
    common_false = [
        patch('src.decisioning.labeling.is_suitability_violation', return_value=False),
        patch('src.decisioning.labeling.is_experience_violation', return_value=False),
        patch('src.decisioning.labeling.is_missing_rationale', return_value=False),
        patch('src.decisioning.labeling.is_advisor_history_high_risk', return_value=False),
    ]

    with patch('src.decisioning.labeling.is_kyc_violation', return_value=True), \
         patch('src.decisioning.labeling.is_kyc_uncertain', return_value=False), \
         patch('src.decisioning.labeling.is_overexposure', return_value=False), \
         patch('src.decisioning.labeling.is_investment_too_aggressive_for_horizon', return_value=False), \
         patch('src.decisioning.labeling.is_investment_too_aggressive_for_objective', return_value=False), \
         patch('src.decisioning.labeling.has_conflicting_signals', return_value=False), \
         common_false[0], common_false[1], common_false[2], common_false[3]:
        assert assign_severity_tier(mock_trade) == "High"

    with patch('src.decisioning.labeling.is_kyc_violation', return_value=False), \
         patch('src.decisioning.labeling.is_suitability_violation', return_value=False), \
         patch('src.decisioning.labeling.is_experience_violation', return_value=False), \
         patch('src.decisioning.labeling.is_kyc_uncertain', return_value=True), \
         patch('src.decisioning.labeling.is_overexposure', return_value=False), \
         patch('src.decisioning.labeling.is_investment_too_aggressive_for_horizon', return_value=False), \
         patch('src.decisioning.labeling.is_investment_too_aggressive_for_objective', return_value=False), \
         patch('src.decisioning.labeling.has_conflicting_signals', return_value=False), \
         patch('src.decisioning.labeling.is_missing_rationale', return_value=False), \
         patch('src.decisioning.labeling.is_advisor_history_high_risk', return_value=False):
        assert assign_severity_tier(mock_trade) == "Medium"

    with patch('src.decisioning.labeling.is_kyc_violation', return_value=False), \
         patch('src.decisioning.labeling.is_suitability_violation', return_value=False), \
         patch('src.decisioning.labeling.is_experience_violation', return_value=False), \
         patch('src.decisioning.labeling.is_kyc_uncertain', return_value=False), \
         patch('src.decisioning.labeling.is_overexposure', return_value=False), \
         patch('src.decisioning.labeling.is_investment_too_aggressive_for_horizon', return_value=False), \
         patch('src.decisioning.labeling.is_investment_too_aggressive_for_objective', return_value=False), \
         patch('src.decisioning.labeling.has_conflicting_signals', return_value=False), \
         patch('src.decisioning.labeling.is_missing_rationale', return_value=True), \
         patch('src.decisioning.labeling.is_advisor_history_high_risk', return_value=False):
        assert assign_severity_tier(mock_trade) == "Low"


def test_assign_expected_workflow_bucket_branches(mock_trade):
    def patch_all(*, hard=0, medium=0, low=0):
        hard_values = [hard >= 1, hard >= 2, False]
        medium_values = [medium >= 1, medium >= 2, medium >= 3, False, False]
        low_values = [low >= 1, low >= 2]
        return (
            patch('src.decisioning.labeling.is_kyc_violation', return_value=hard_values[0]),
            patch('src.decisioning.labeling.is_suitability_violation', return_value=hard_values[1]),
            patch('src.decisioning.labeling.is_experience_violation', return_value=hard_values[2]),
            patch('src.decisioning.labeling.is_kyc_uncertain', return_value=medium_values[0]),
            patch('src.decisioning.labeling.is_overexposure', return_value=medium_values[1]),
            patch('src.decisioning.labeling.is_investment_too_aggressive_for_horizon', return_value=medium_values[2]),
            patch('src.decisioning.labeling.is_investment_too_aggressive_for_objective', return_value=medium_values[3]),
            patch('src.decisioning.labeling.has_conflicting_signals', return_value=medium_values[4]),
            patch('src.decisioning.labeling.is_missing_rationale', return_value=low_values[0]),
            patch('src.decisioning.labeling.is_advisor_history_high_risk', return_value=low_values[1]),
        )

    for expected, kwargs in [
        ("Urgent", {"hard": 2}),
        ("Priority", {"hard": 1}),
        ("Priority", {"medium": 3}),
        ("Queue", {"medium": 2}),
        ("Queue", {"medium": 1}),
        ("Queue", {"low": 2}),
        ("Auto_pass", {}),
    ]:
        patches = patch_all(**kwargs)
        with patches[0], patches[1], patches[2], patches[3], patches[4], \
             patches[5], patches[6], patches[7], patches[8], patches[9]:
            assert assign_expected_workflow_bucket(mock_trade) == expected


def test_assign_primary_policy_uses_precedence_and_empty_fallback(mock_trade):
    with patch(
        'src.decisioning.labeling.get_relevant_policies',
        return_value=["POL-003-SURVEILLANCE", "POL-001-SUITABILITY"],
    ):
        assert assign_primary_policy(mock_trade) == "POL-001-SUITABILITY"

    with patch('src.decisioning.labeling.get_relevant_policies', return_value=[]):
        assert assign_primary_policy(mock_trade) == ""
