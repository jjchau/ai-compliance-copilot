import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from unittest.mock import Mock
from src.data.schema import Trade
from src.policy.policy_signal_mapping import POLICY_SIGNAL_CHECKS


class TestPolicySignalMapping:
    def test_policy_signal_checks_is_dict(self):
        """Test that POLICY_SIGNAL_CHECKS is a dictionary."""
        assert isinstance(POLICY_SIGNAL_CHECKS, dict)

    def test_all_policy_keys_present(self):
        """Test that all expected policy keys are present in the mapping."""
        expected_keys = [
            "POLICY_KYC_001",
            "POLICY_KYC_002", 
            "POLICY_KYC_003",
            "POLICY_SUIT_001",
            "POLICY_SUIT_002",
            "POLICY_SUIT_003",
            "POLICY_EXP_001",
            "POLICY_RISK_001",
            "POLICY_DOC_001",
            "POLICY_SUP_001"
        ]
        
        for key in expected_keys:
            assert key in POLICY_SIGNAL_CHECKS, f"Missing policy key: {key}"

    def test_all_values_are_callable(self):
        """Test that all values in POLICY_SIGNAL_CHECKS are callable functions."""
        for policy_id, signal_check in POLICY_SIGNAL_CHECKS.items():
            assert callable(signal_check), f"Policy {policy_id} has non-callable value: {signal_check}"

    def test_functions_accept_trade_parameter(self):
        """Test that all signal check functions can be called with a Trade object."""
        # Use a real Trade object instead of mock to ensure all attributes are available
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
        
        for policy_id, signal_check in POLICY_SIGNAL_CHECKS.items():
            try:
                result = signal_check(trade)
                # Result should be boolean
                assert isinstance(result, bool), f"Policy {policy_id} returned non-boolean: {result}"
            except Exception as e:
                pytest.fail(f"Policy {policy_id} signal check failed: {e}")

    def test_specific_policy_mappings(self):
        """Test specific policy to function mappings."""
        from src.decisioning.violation_rules import (
            is_kyc_violation,
            is_suitability_violation,
            is_experience_violation
        )
        from src.decisioning.risk_signals import (
            is_kyc_uncertain,
            is_investment_too_aggressive_for_objective,
            is_investment_too_aggressive_for_horizon,
            is_overexposure,
            is_advisor_history_high_risk
        )
        from src.decisioning.documentation_signals import is_missing_rationale
        from src.decisioning.conflict_detection import has_conflicting_signals
        
        expected_mappings = {
            "POLICY_KYC_001": is_kyc_violation,
            "POLICY_KYC_002": is_kyc_uncertain,
            "POLICY_KYC_003": has_conflicting_signals,
            "POLICY_SUIT_001": is_suitability_violation,
            "POLICY_SUIT_002": is_investment_too_aggressive_for_objective,
            "POLICY_SUIT_003": is_investment_too_aggressive_for_horizon,
            "POLICY_EXP_001": is_experience_violation,
            "POLICY_RISK_001": is_overexposure,
            "POLICY_DOC_001": is_missing_rationale,
            "POLICY_SUP_001": is_advisor_history_high_risk,
        }
        
        for policy_id, expected_function in expected_mappings.items():
            assert POLICY_SIGNAL_CHECKS[policy_id] == expected_function, \
                f"Policy {policy_id} not mapped to expected function"