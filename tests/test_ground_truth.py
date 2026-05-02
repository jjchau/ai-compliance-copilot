"""Unit tests for src/policy/ground_truth.py"""

import pytest
from unittest.mock import patch
from src.policy.ground_truth import get_relevant_policies
from src.data.schema import Trade


def make_trade(**kwargs):
    """Factory for creating test trades."""
    base = dict(
        client_age=40,
        client_income=100000,
        risk_tolerance='Medium',
        investment_experience='Intermediate',
        investment_objective='Growth',
        investment_time_horizon='Medium',
        investment_type='Stocks',
        investment_amount=10000.0,
        advisor_id='A1',
        advisor_experience='Mid',
        advisor_history_risk='Low',
        has_rationale=True,
        kyc_completeness='Complete',
    )
    base.update(kwargs)
    return Trade(**base)


class TestGetRelevantPoliciesKyc:
    """Test KYC-related policies."""

    def patch_all_rules(self, monkeypatch, **overrides):
        """Patch all rule functions to False by default, then apply overrides."""
        # Default all to False
        monkeypatch.setattr('src.policy.ground_truth.is_kyc_violation', lambda t: False)
        monkeypatch.setattr('src.policy.ground_truth.is_kyc_uncertain', lambda t: False)
        monkeypatch.setattr('src.policy.ground_truth.has_conflicting_signals', lambda t: False)
        monkeypatch.setattr('src.policy.ground_truth.is_suitability_violation', lambda t: False)
        monkeypatch.setattr('src.policy.ground_truth.is_investment_too_aggressive_for_objective', lambda t: False)
        monkeypatch.setattr('src.policy.ground_truth.is_investment_too_agressive_for_horizon', lambda t: False)
        monkeypatch.setattr('src.policy.ground_truth.is_experience_violation', lambda t: False)
        monkeypatch.setattr('src.policy.ground_truth.is_overexposure', lambda t: False)
        monkeypatch.setattr('src.policy.ground_truth.is_advisor_history_high_risk', lambda t: False)
        
        # Apply overrides
        for func_name, return_value in overrides.items():
            if return_value:
                monkeypatch.setattr(f'src.policy.ground_truth.{func_name}', lambda t: True)

    def test_kyc_violation_triggers_policy_kyc_001(self, monkeypatch):
        """Test that KYC violation triggers POLICY_KYC_001."""
        self.patch_all_rules(monkeypatch, is_kyc_violation=True)
        
        trade = make_trade()
        result = get_relevant_policies(trade)
        
        assert 'POLICY_KYC_001' in result

    def test_kyc_uncertain_triggers_policy_kyc_002(self, monkeypatch):
        """Test that KYC uncertainty triggers POLICY_KYC_002."""
        self.patch_all_rules(monkeypatch, is_kyc_uncertain=True)
        
        trade = make_trade()
        result = get_relevant_policies(trade)
        
        assert 'POLICY_KYC_002' in result

    def test_conflicting_signals_triggers_policy_kyc_003(self, monkeypatch):
        """Test that conflicting signals trigger POLICY_KYC_003."""
        self.patch_all_rules(monkeypatch, has_conflicting_signals=True)
        
        trade = make_trade()
        result = get_relevant_policies(trade)
        
        assert 'POLICY_KYC_003' in result

    def test_multiple_kyc_policies(self, monkeypatch):
        """Test that multiple KYC triggers produce multiple policies."""
        self.patch_all_rules(
            monkeypatch,
            is_kyc_violation=True,
            is_kyc_uncertain=True,
            has_conflicting_signals=True
        )
        
        trade = make_trade()
        result = get_relevant_policies(trade)
        
        assert 'POLICY_KYC_001' in result
        assert 'POLICY_KYC_002' in result
        assert 'POLICY_KYC_003' in result


class TestGetRelevantPoliciesSuitability:
    """Test suitability-related policies."""

    def patch_all_rules(self, monkeypatch, **overrides):
        """Patch all rule functions to False by default."""
        monkeypatch.setattr('src.policy.ground_truth.is_kyc_violation', lambda t: False)
        monkeypatch.setattr('src.policy.ground_truth.is_kyc_uncertain', lambda t: False)
        monkeypatch.setattr('src.policy.ground_truth.has_conflicting_signals', lambda t: False)
        monkeypatch.setattr('src.policy.ground_truth.is_suitability_violation', lambda t: False)
        monkeypatch.setattr('src.policy.ground_truth.is_investment_too_aggressive_for_objective', lambda t: False)
        monkeypatch.setattr('src.policy.ground_truth.is_investment_too_agressive_for_horizon', lambda t: False)
        monkeypatch.setattr('src.policy.ground_truth.is_experience_violation', lambda t: False)
        monkeypatch.setattr('src.policy.ground_truth.is_overexposure', lambda t: False)
        monkeypatch.setattr('src.policy.ground_truth.is_advisor_history_high_risk', lambda t: False)
        
        for func_name, return_value in overrides.items():
            if return_value:
                monkeypatch.setattr(f'src.policy.ground_truth.{func_name}', lambda t: True)

    def test_suitability_violation_triggers_policy_suit_001(self, monkeypatch):
        """Test that suitability violation triggers POLICY_SUIT_001."""
        self.patch_all_rules(monkeypatch, is_suitability_violation=True)
        
        trade = make_trade()
        result = get_relevant_policies(trade)
        
        assert 'POLICY_SUIT_001' in result

    def test_aggressive_for_objective_triggers_policy_suit_002(self, monkeypatch):
        """Test that aggressive investment for objective triggers POLICY_SUIT_002."""
        self.patch_all_rules(monkeypatch, is_investment_too_aggressive_for_objective=True)
        
        trade = make_trade()
        result = get_relevant_policies(trade)
        
        assert 'POLICY_SUIT_002' in result

    def test_aggressive_for_horizon_triggers_policy_suit_003(self, monkeypatch):
        """Test that aggressive investment for horizon triggers POLICY_SUIT_003."""
        self.patch_all_rules(monkeypatch, is_investment_too_agressive_for_horizon=True)
        
        trade = make_trade()
        result = get_relevant_policies(trade)
        
        assert 'POLICY_SUIT_003' in result

    def test_multiple_suitability_policies(self, monkeypatch):
        """Test that multiple suitability triggers produce multiple policies."""
        self.patch_all_rules(
            monkeypatch,
            is_suitability_violation=True,
            is_investment_too_aggressive_for_objective=True,
            is_investment_too_agressive_for_horizon=True
        )
        
        trade = make_trade()
        result = get_relevant_policies(trade)
        
        assert 'POLICY_SUIT_001' in result
        assert 'POLICY_SUIT_002' in result
        assert 'POLICY_SUIT_003' in result


class TestGetRelevantPoliciesExperience:
    """Test experience-related policies."""

    def patch_all_rules(self, monkeypatch, **overrides):
        """Patch all rule functions to False by default."""
        monkeypatch.setattr('src.policy.ground_truth.is_kyc_violation', lambda t: False)
        monkeypatch.setattr('src.policy.ground_truth.is_kyc_uncertain', lambda t: False)
        monkeypatch.setattr('src.policy.ground_truth.has_conflicting_signals', lambda t: False)
        monkeypatch.setattr('src.policy.ground_truth.is_suitability_violation', lambda t: False)
        monkeypatch.setattr('src.policy.ground_truth.is_investment_too_aggressive_for_objective', lambda t: False)
        monkeypatch.setattr('src.policy.ground_truth.is_investment_too_agressive_for_horizon', lambda t: False)
        monkeypatch.setattr('src.policy.ground_truth.is_experience_violation', lambda t: False)
        monkeypatch.setattr('src.policy.ground_truth.is_overexposure', lambda t: False)
        monkeypatch.setattr('src.policy.ground_truth.is_advisor_history_high_risk', lambda t: False)
        
        for func_name, return_value in overrides.items():
            if return_value:
                monkeypatch.setattr(f'src.policy.ground_truth.{func_name}', lambda t: True)

    def test_experience_violation_triggers_policy_exp_001(self, monkeypatch):
        """Test that experience violation triggers POLICY_EXP_001."""
        self.patch_all_rules(monkeypatch, is_experience_violation=True)
        
        trade = make_trade()
        result = get_relevant_policies(trade)
        
        assert 'POLICY_EXP_001' in result

    def test_no_experience_violation_no_policy(self, monkeypatch):
        """Test that lack of experience violation means no policy."""
        self.patch_all_rules(monkeypatch)
        
        trade = make_trade()
        result = get_relevant_policies(trade)
        
        assert 'POLICY_EXP_001' not in result


class TestGetRelevantPoliciesRisk:
    """Test risk-related policies."""

    def patch_all_rules(self, monkeypatch, **overrides):
        """Patch all rule functions to False by default."""
        monkeypatch.setattr('src.policy.ground_truth.is_kyc_violation', lambda t: False)
        monkeypatch.setattr('src.policy.ground_truth.is_kyc_uncertain', lambda t: False)
        monkeypatch.setattr('src.policy.ground_truth.has_conflicting_signals', lambda t: False)
        monkeypatch.setattr('src.policy.ground_truth.is_suitability_violation', lambda t: False)
        monkeypatch.setattr('src.policy.ground_truth.is_investment_too_aggressive_for_objective', lambda t: False)
        monkeypatch.setattr('src.policy.ground_truth.is_investment_too_agressive_for_horizon', lambda t: False)
        monkeypatch.setattr('src.policy.ground_truth.is_experience_violation', lambda t: False)
        monkeypatch.setattr('src.policy.ground_truth.is_overexposure', lambda t: False)
        monkeypatch.setattr('src.policy.ground_truth.is_advisor_history_high_risk', lambda t: False)
        
        for func_name, return_value in overrides.items():
            if return_value:
                monkeypatch.setattr(f'src.policy.ground_truth.{func_name}', lambda t: True)

    def test_overexposure_triggers_policy_risk_001(self, monkeypatch):
        """Test that portfolio overexposure triggers POLICY_RISK_001."""
        self.patch_all_rules(monkeypatch, is_overexposure=True)
        
        trade = make_trade()
        result = get_relevant_policies(trade)
        
        assert 'POLICY_RISK_001' in result

    def test_no_overexposure_no_risk_policy(self, monkeypatch):
        """Test that lack of overexposure means no risk policy."""
        self.patch_all_rules(monkeypatch)
        
        trade = make_trade()
        result = get_relevant_policies(trade)
        
        assert 'POLICY_RISK_001' not in result


class TestGetRelevantPoliciesDocumentation:
    """Test documentation-related policies."""

    def patch_all_rules(self, monkeypatch, **overrides):
        """Patch all rule functions to False by default."""
        monkeypatch.setattr('src.policy.ground_truth.is_kyc_violation', lambda t: False)
        monkeypatch.setattr('src.policy.ground_truth.is_kyc_uncertain', lambda t: False)
        monkeypatch.setattr('src.policy.ground_truth.has_conflicting_signals', lambda t: False)
        monkeypatch.setattr('src.policy.ground_truth.is_suitability_violation', lambda t: False)
        monkeypatch.setattr('src.policy.ground_truth.is_investment_too_aggressive_for_objective', lambda t: False)
        monkeypatch.setattr('src.policy.ground_truth.is_investment_too_agressive_for_horizon', lambda t: False)
        monkeypatch.setattr('src.policy.ground_truth.is_experience_violation', lambda t: False)
        monkeypatch.setattr('src.policy.ground_truth.is_overexposure', lambda t: False)
        monkeypatch.setattr('src.policy.ground_truth.is_advisor_history_high_risk', lambda t: False)
        
        for func_name, return_value in overrides.items():
            if return_value:
                monkeypatch.setattr(f'src.policy.ground_truth.{func_name}', lambda t: True)

    def test_missing_rationale_triggers_policy_doc_001(self, monkeypatch):
        """Test that missing rationale triggers POLICY_DOC_001."""
        self.patch_all_rules(monkeypatch)
        
        trade = make_trade(has_rationale=False)
        result = get_relevant_policies(trade)
        
        assert 'POLICY_DOC_001' in result

    def test_with_rationale_no_doc_policy(self, monkeypatch):
        """Test that present rationale means no documentation policy."""
        self.patch_all_rules(monkeypatch)
        
        trade = make_trade(has_rationale=True)
        result = get_relevant_policies(trade)
        
        assert 'POLICY_DOC_001' not in result


class TestGetRelevantPoliciesSupervision:
    """Test supervision-related policies."""

    def patch_all_rules(self, monkeypatch, **overrides):
        """Patch all rule functions to False by default."""
        monkeypatch.setattr('src.policy.ground_truth.is_kyc_violation', lambda t: False)
        monkeypatch.setattr('src.policy.ground_truth.is_kyc_uncertain', lambda t: False)
        monkeypatch.setattr('src.policy.ground_truth.has_conflicting_signals', lambda t: False)
        monkeypatch.setattr('src.policy.ground_truth.is_suitability_violation', lambda t: False)
        monkeypatch.setattr('src.policy.ground_truth.is_investment_too_aggressive_for_objective', lambda t: False)
        monkeypatch.setattr('src.policy.ground_truth.is_investment_too_agressive_for_horizon', lambda t: False)
        monkeypatch.setattr('src.policy.ground_truth.is_experience_violation', lambda t: False)
        monkeypatch.setattr('src.policy.ground_truth.is_overexposure', lambda t: False)
        monkeypatch.setattr('src.policy.ground_truth.is_advisor_history_high_risk', lambda t: False)
        
        for func_name, return_value in overrides.items():
            if return_value:
                monkeypatch.setattr(f'src.policy.ground_truth.{func_name}', lambda t: True)

    def test_advisor_high_risk_history_triggers_policy_sup_001(self, monkeypatch):
        """Test that advisor high-risk history triggers POLICY_SUP_001."""
        self.patch_all_rules(monkeypatch, is_advisor_history_high_risk=True)
        
        trade = make_trade()
        result = get_relevant_policies(trade)
        
        assert 'POLICY_SUP_001' in result

    def test_advisor_low_risk_history_no_sup_policy(self, monkeypatch):
        """Test that advisor low-risk history means no supervision policy."""
        self.patch_all_rules(monkeypatch)
        
        trade = make_trade()
        result = get_relevant_policies(trade)
        
        assert 'POLICY_SUP_001' not in result


class TestGetRelevantPoliciesCombinations:
    """Test combinations of policies triggering together."""

    def patch_all_rules(self, monkeypatch, **overrides):
        """Patch all rule functions to False by default."""
        monkeypatch.setattr('src.policy.ground_truth.is_kyc_violation', lambda t: False)
        monkeypatch.setattr('src.policy.ground_truth.is_kyc_uncertain', lambda t: False)
        monkeypatch.setattr('src.policy.ground_truth.has_conflicting_signals', lambda t: False)
        monkeypatch.setattr('src.policy.ground_truth.is_suitability_violation', lambda t: False)
        monkeypatch.setattr('src.policy.ground_truth.is_investment_too_aggressive_for_objective', lambda t: False)
        monkeypatch.setattr('src.policy.ground_truth.is_investment_too_agressive_for_horizon', lambda t: False)
        monkeypatch.setattr('src.policy.ground_truth.is_experience_violation', lambda t: False)
        monkeypatch.setattr('src.policy.ground_truth.is_overexposure', lambda t: False)
        monkeypatch.setattr('src.policy.ground_truth.is_advisor_history_high_risk', lambda t: False)
        
        for func_name, return_value in overrides.items():
            if return_value:
                monkeypatch.setattr(f'src.policy.ground_truth.{func_name}', lambda t: True)

    def test_clean_trade_returns_empty_list(self, monkeypatch):
        """Test that a clean trade returns no policies."""
        self.patch_all_rules(monkeypatch)
        
        trade = make_trade(has_rationale=True)
        result = get_relevant_policies(trade)
        
        assert result == []

    def test_multiple_categories_trigger_multiple_policies(self, monkeypatch):
        """Test that violations in multiple categories trigger multiple policies."""
        self.patch_all_rules(
            monkeypatch,
            is_kyc_violation=True,
            is_suitability_violation=True,
            is_experience_violation=True,
            is_overexposure=True,
            is_advisor_history_high_risk=True
        )
        
        trade = make_trade(has_rationale=False)
        result = get_relevant_policies(trade)
        
        # Should have policies from KYC, Suitability, Experience, Risk, Documentation, Supervision
        assert 'POLICY_KYC_001' in result
        assert 'POLICY_SUIT_001' in result
        assert 'POLICY_EXP_001' in result
        assert 'POLICY_RISK_001' in result
        assert 'POLICY_DOC_001' in result
        assert 'POLICY_SUP_001' in result

    def test_worst_case_scenario(self, monkeypatch):
        """Test worst-case scenario with all violations."""
        self.patch_all_rules(
            monkeypatch,
            is_kyc_violation=True,
            is_kyc_uncertain=True,
            has_conflicting_signals=True,
            is_suitability_violation=True,
            is_investment_too_aggressive_for_objective=True,
            is_investment_too_agressive_for_horizon=True,
            is_experience_violation=True,
            is_overexposure=True,
            is_advisor_history_high_risk=True
        )
        
        trade = make_trade(has_rationale=False)
        result = get_relevant_policies(trade)
        
        # Should retrieve all possible policies except POLICY_RISK_002 (future)
        expected_policies = [
            'POLICY_KYC_001',
            'POLICY_KYC_002',
            'POLICY_KYC_003',
            'POLICY_SUIT_001',
            'POLICY_SUIT_002',
            'POLICY_SUIT_003',
            'POLICY_EXP_001',
            'POLICY_RISK_001',
            'POLICY_DOC_001',
            'POLICY_SUP_001'
        ]
        
        assert len(result) == len(expected_policies)
        for policy in expected_policies:
            assert policy in result

    def test_only_kyc_and_doc_violations(self, monkeypatch):
        """Test trade with only KYC and documentation issues."""
        self.patch_all_rules(monkeypatch, is_kyc_violation=True)
        
        trade = make_trade(has_rationale=False)
        result = get_relevant_policies(trade)
        
        assert 'POLICY_KYC_001' in result
        assert 'POLICY_DOC_001' in result
        assert len(result) == 2

    def test_suitability_and_risk_violations(self, monkeypatch):
        """Test trade with suitability and risk violations."""
        self.patch_all_rules(
            monkeypatch,
            is_suitability_violation=True,
            is_overexposure=True
        )
        
        trade = make_trade(has_rationale=True)
        result = get_relevant_policies(trade)
        
        assert 'POLICY_SUIT_001' in result
        assert 'POLICY_RISK_001' in result
        assert len(result) == 2


class TestGetRelevantPoliciesEdgeCases:
    """Test edge cases."""

    def patch_all_rules(self, monkeypatch, **overrides):
        """Patch all rule functions to False by default."""
        monkeypatch.setattr('src.policy.ground_truth.is_kyc_violation', lambda t: False)
        monkeypatch.setattr('src.policy.ground_truth.is_kyc_uncertain', lambda t: False)
        monkeypatch.setattr('src.policy.ground_truth.has_conflicting_signals', lambda t: False)
        monkeypatch.setattr('src.policy.ground_truth.is_suitability_violation', lambda t: False)
        monkeypatch.setattr('src.policy.ground_truth.is_investment_too_aggressive_for_objective', lambda t: False)
        monkeypatch.setattr('src.policy.ground_truth.is_investment_too_agressive_for_horizon', lambda t: False)
        monkeypatch.setattr('src.policy.ground_truth.is_experience_violation', lambda t: False)
        monkeypatch.setattr('src.policy.ground_truth.is_overexposure', lambda t: False)
        monkeypatch.setattr('src.policy.ground_truth.is_advisor_history_high_risk', lambda t: False)
        
        for func_name, return_value in overrides.items():
            if return_value:
                monkeypatch.setattr(f'src.policy.ground_truth.{func_name}', lambda t: True)

    def test_returns_list_type(self, monkeypatch):
        """Test that function returns a list."""
        self.patch_all_rules(monkeypatch)
        
        trade = make_trade()
        result = get_relevant_policies(trade)
        
        assert isinstance(result, list)

    def test_no_duplicate_policies(self, monkeypatch):
        """Test that returned policies have no duplicates."""
        self.patch_all_rules(
            monkeypatch,
            is_kyc_violation=True,
            is_kyc_uncertain=True,
            has_conflicting_signals=True,
            is_suitability_violation=True,
            is_experience_violation=True,
            is_overexposure=True,
            is_advisor_history_high_risk=True
        )
        
        trade = make_trade(has_rationale=False)
        result = get_relevant_policies(trade)
        
        # All items should be unique (no duplicates)
        assert len(result) == len(set(result))

    def test_policies_are_strings(self, monkeypatch):
        """Test that all returned policies are strings."""
        self.patch_all_rules(
            monkeypatch,
            is_kyc_violation=True,
            is_suitability_violation=True,
            is_experience_violation=True
        )
        
        trade = make_trade()
        result = get_relevant_policies(trade)
        
        for policy in result:
            assert isinstance(policy, str)
            assert policy.startswith('POLICY_')

    def test_with_extreme_trade_values(self, monkeypatch):
        """Test with extreme trade values."""
        self.patch_all_rules(monkeypatch)
        
        trade = make_trade(
            client_age=18,
            client_income=1000000,
            investment_amount=100000000.0
        )
        result = get_relevant_policies(trade)
        
        # Should still return a list without errors
        assert isinstance(result, list)
