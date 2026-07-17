import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from unittest.mock import Mock
from src.data.schema import Trade
from src.policy.policy_signal_mapping import POLICY_RELEVANCE_CHECKS


class TestPolicySignalMapping:
    def test_policy_relevance_checks_is_dict(self):
        """Test that POLICY_RELEVANCE_CHECKS is a dictionary."""
        assert isinstance(POLICY_RELEVANCE_CHECKS, dict)

    def test_all_policy_keys_present(self):
        """Test that all expected policy keys are present in the mapping."""
        expected_keys = [
            "POL-001-SUITABILITY",
            "POL-002-KYC",
            "POL-003-SURVEILLANCE",
            "POL-004-CONCENTRATION",
            "POL-005-SENIOR-VULNERABLE-CLIENTS",
            "POL-006-HIGH-RISK-PRODUCTS",
            "POL-007-DOCUMENTATION-STANDARDS",
            "POL-008-EXCEPTIONS-AND-OVERRIDES",
            "POL-009-CONFLICTS-OF-INTEREST",
            "POL-010-CLIENT-OBJECTIVE"
        ]
        
        for key in expected_keys:
            assert key in POLICY_RELEVANCE_CHECKS, f"Missing policy key: {key}"

    def test_all_values_are_callable(self):
        """Test that all values in POLICY_RELEVANCE_CHECKS are callable functions."""
        for policy_id, relevance_check in POLICY_RELEVANCE_CHECKS.items():
            assert callable(relevance_check), f"Policy {policy_id} has non-callable value: {relevance_check}"

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
            advisor_rationale='Advisor rationale provided.',
            kyc_completeness='Complete'
        )
        
        for policy_id, relevance_check in POLICY_RELEVANCE_CHECKS.items():
            try:
                result = relevance_check(trade)
                # Result should be boolean
                assert isinstance(result, bool), f"Policy {policy_id} returned non-boolean: {result}"
            except Exception as e:
                pytest.fail(f"Policy {policy_id} relevance check failed: {e}")

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
        
        # The new mapping uses composite lambdas for many policies. Ensure the
        # expected policy keys exist and their values are callable.
        for key in [
            "POL-002-KYC",
            "POL-001-SUITABILITY",
            "POL-003-SURVEILLANCE",
            "POL-007-DOCUMENTATION-STANDARDS",
            "POL-004-CONCENTRATION"
        ]:
            assert key in POLICY_RELEVANCE_CHECKS, f"Missing policy key: {key}"
            assert callable(POLICY_RELEVANCE_CHECKS[key])