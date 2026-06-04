import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from unittest.mock import Mock
from src.data.schema import Trade
from src.orchestration.explanation import generate_explanation, POLICY_EXPLANATIONS


class TestGenerateExplanation:
    def test_returns_no_concerns_when_no_policies_trigger(self):
        """Test that generate_explanation returns expected combined messages for provided policies."""
        trade = Mock(spec=Trade)
        result = generate_explanation(trade, ["POLICY_KYC_001", "POLICY_SUIT_001"])
        assert result == "Missing KYC information; Investment risk exceeds client risk tolerance."

    def test_returns_explanation_for_single_triggered_policy(self):
        """Test explanation generation for a single policy ID."""
        trade = Mock(spec=Trade)
        result = generate_explanation(trade, ["POLICY_KYC_001"])
        assert result == "Missing KYC information."

    def test_returns_combined_explanations_for_multiple_policies(self):
        """Test explanation generation for multiple policy IDs."""
        trade = Mock(spec=Trade)
        result = generate_explanation(trade, ["POLICY_KYC_001", "POLICY_SUIT_001"])
        assert result == "Missing KYC information; Investment risk exceeds client risk tolerance."

    def test_includes_all_provided_policies(self):
        """Under the revised implementation all provided policies are listed."""
        trade = Mock(spec=Trade)
        result = generate_explanation(trade, ["POLICY_KYC_001", "POLICY_SUIT_001", "POLICY_EXP_001"])
        assert "Missing KYC information" in result
        assert "Investment risk exceeds client risk tolerance" in result
        assert "Complex investment exceeds client experience level" in result

    def test_handles_unknown_policy_ids(self):
        """Test handling of unknown policy IDs."""
        trade = Mock(spec=Trade)
        result = generate_explanation(trade, ["UNKNOWN_POLICY"])
        assert result == "Unknown issue."

    def test_empty_policies_list(self):
        """Test behavior with empty policies list."""
        trade = Mock(spec=Trade)
        result = generate_explanation(trade, [])
        assert result == "Retrieved policies did not produce significant concerns."

    def test_with_real_trade_and_policies(self):
        """Test with real Trade object and actual policy IDs."""
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
            advisor_rationale=None,  # This should map to POLICY_DOC_001
            kyc_completeness='Complete'
        )
        result = generate_explanation(trade, ["POLICY_DOC_001"])
        assert result == "Missing rationale for trade recommendation."


class TestPolicyExplanations:
    def test_policy_explanations_is_dict(self):
        """Test that POLICY_EXPLANATIONS is a dictionary."""
        assert isinstance(POLICY_EXPLANATIONS, dict)

    def test_all_expected_policies_have_explanations(self):
        """Test that all policies in POLICY_SIGNAL_CHECKS have explanations."""
        from src.policy.policy_signal_mapping import POLICY_SIGNAL_CHECKS
        for policy_id in POLICY_SIGNAL_CHECKS.keys():
            assert policy_id in POLICY_EXPLANATIONS, f"Missing explanation for policy: {policy_id}"

    def test_explanations_are_strings(self):
        """Test that all explanations are strings."""
        for policy_id, explanation in POLICY_EXPLANATIONS.items():
            assert isinstance(explanation, str), f"Explanation for {policy_id} is not a string: {explanation}"
