import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from unittest.mock import Mock, patch
from src.data.schema import Trade
from src.orchestration.explanation import generate_explanation, POLICY_EXPLANATIONS


class TestGenerateExplanation:
    def test_returns_no_concerns_when_no_policies_trigger(self):
        """Test that generate_explanation returns no concerns message when no policies trigger."""
        trade = Mock(spec=Trade)
        
        # Mock POLICY_SIGNAL_CHECKS to return a function that always returns False
        with patch('src.orchestration.explanation.POLICY_SIGNAL_CHECKS') as mock_checks:
            mock_checks.get.return_value = lambda t: False
            
            result = generate_explanation(trade, ["POLICY_KYC_001", "POLICY_SUIT_001"])
            assert result == "No significant compliance concerns detected."

    def test_returns_explanation_for_single_triggered_policy(self):
        """Test explanation generation for a single triggered policy."""
        trade = Mock(spec=Trade)
        
        def mock_signal_check(t):
            return True
        
        with patch('src.orchestration.explanation.POLICY_SIGNAL_CHECKS') as mock_checks:
            mock_checks.get.return_value = mock_signal_check
            
            result = generate_explanation(trade, ["POLICY_KYC_001"])
            assert result == "Missing KYC information."

    def test_returns_combined_explanations_for_multiple_policies(self):
        """Test explanation generation for multiple triggered policies."""
        trade = Mock(spec=Trade)
        
        def mock_signal_check(t):
            return True
        
        with patch('src.orchestration.explanation.POLICY_SIGNAL_CHECKS') as mock_checks:
            mock_checks.get.return_value = mock_signal_check
            
            result = generate_explanation(trade, ["POLICY_KYC_001", "POLICY_SUIT_001"])
            assert result == "Missing KYC information; Investment risk exceeds client risk tolerance."

    def test_ignores_policies_that_dont_trigger(self):
        """Test that only triggered policies are included in explanation."""
        trade = Mock(spec=Trade)
        
        call_count = 0
        def mock_signal_check(t):
            nonlocal call_count
            call_count += 1
            return call_count % 2 == 1  # Alternate True/False
        
        with patch('src.orchestration.explanation.POLICY_SIGNAL_CHECKS') as mock_checks:
            mock_checks.get.return_value = mock_signal_check
            
            result = generate_explanation(trade, ["POLICY_KYC_001", "POLICY_SUIT_001", "POLICY_EXP_001"])
            # Only odd-indexed policies should trigger
            assert "Missing KYC information" in result
            assert "Investment risk exceeds client risk tolerance" not in result
            assert "Complex investment exceeds client experience level" in result

    def test_handles_unknown_policy_ids(self):
        """Test handling of unknown policy IDs."""
        trade = Mock(spec=Trade)
        
        def mock_signal_check(t):
            return True
        
        with patch('src.orchestration.explanation.POLICY_SIGNAL_CHECKS') as mock_checks:
            mock_checks.get.return_value = mock_signal_check
            
            result = generate_explanation(trade, ["UNKNOWN_POLICY"])
            assert result == "Unknown issue."

    def test_empty_policies_list(self):
        """Test behavior with empty policies list."""
        trade = Mock(spec=Trade)
        
        result = generate_explanation(trade, [])
        assert result == "No significant compliance concerns detected."

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
            has_rationale=False,  # This should trigger POLICY_DOC_001
            kyc_completeness='Complete'
        )
        
        # Test with a policy that should trigger
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