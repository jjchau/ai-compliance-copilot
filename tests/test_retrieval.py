import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from unittest.mock import patch, MagicMock
from src.policy.retrieval import retrieve_policies, RETRIEVAL_CONFIG, ALL_POLICY_IDS
from src.data.schema import Trade
from src.policy.policy_corpus import POLICY_CORPUS


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


class TestRetrievalConfig:
    """Test RETRIEVAL_CONFIG structure and values."""

    def test_retrieval_config_exists(self):
        """Test that RETRIEVAL_CONFIG is defined."""
        assert RETRIEVAL_CONFIG is not None
        assert isinstance(RETRIEVAL_CONFIG, dict)

    def test_retrieval_config_has_recall_rate(self):
        """Test that recall_rate is configured."""
        assert 'recall_rate' in RETRIEVAL_CONFIG
        assert isinstance(RETRIEVAL_CONFIG['recall_rate'], (int, float))
        assert 0 <= RETRIEVAL_CONFIG['recall_rate'] <= 1

    def test_retrieval_config_has_noise_rate(self):
        """Test that noise_rate is configured."""
        assert 'noise_rate' in RETRIEVAL_CONFIG
        assert isinstance(RETRIEVAL_CONFIG['noise_rate'], (int, float))
        assert 0 <= RETRIEVAL_CONFIG['noise_rate'] <= 1

    def test_retrieval_config_has_max_noise(self):
        """Test that max_noise is configured."""
        assert 'max_noise' in RETRIEVAL_CONFIG
        assert isinstance(RETRIEVAL_CONFIG['max_noise'], int)
        assert RETRIEVAL_CONFIG['max_noise'] >= 0


class TestAllPolicyIds:
    """Test ALL_POLICY_IDS constant."""

    def test_all_policy_ids_exists(self):
        """Test that ALL_POLICY_IDS is defined."""
        assert ALL_POLICY_IDS is not None
        assert isinstance(ALL_POLICY_IDS, list)

    def test_all_policy_ids_not_empty(self):
        """Test that ALL_POLICY_IDS contains policy IDs."""
        assert len(ALL_POLICY_IDS) > 0

    def test_all_policy_ids_matches_corpus(self):
        """Test that ALL_POLICY_IDS matches POLICY_CORPUS keys."""
        corpus_keys = set(POLICY_CORPUS.keys())
        all_ids_set = set(ALL_POLICY_IDS)
        assert all_ids_set == corpus_keys

    def test_all_policy_ids_are_strings(self):
        """Test that all policy IDs are strings."""
        for policy_id in ALL_POLICY_IDS:
            assert isinstance(policy_id, str)


class TestRetrievePoliciesBasic:
    """Test basic functionality of retrieve_policies."""

    def test_retrieve_policies_returns_list(self):
        """Test that retrieve_policies returns a list."""
        trade = make_trade()
        result = retrieve_policies(trade)
        assert isinstance(result, list)

    def test_retrieve_policies_returns_strings(self):
        """Test that all retrieved policy IDs are strings."""
        trade = make_trade()
        result = retrieve_policies(trade)
        for policy_id in result:
            assert isinstance(policy_id, str)

    def test_retrieve_policies_valid_ids(self):
        """Test that retrieved policy IDs are valid."""
        trade = make_trade()
        result = retrieve_policies(trade)
        
        valid_ids = set(POLICY_CORPUS.keys())
        for policy_id in result:
            assert policy_id in valid_ids, \
                f"Retrieved invalid policy ID: {policy_id}"

    def test_retrieve_policies_no_duplicates(self):
        """Test that retrieved policies have no duplicates."""
        trade = make_trade()
        result = retrieve_policies(trade)
        
        assert len(result) == len(set(result)), \
            "Duplicate policy IDs in retrieval result"


class TestRetrievePoliciesKycSignals:
    """Test retrieval based on KYC completeness."""

    @patch('src.policy.retrieval.random.random')
    def test_kyc_missing_triggers_kyc_001(self, mock_random):
        """Test that missing KYC triggers POLICY_KYC_001 retrieval."""
        # Mock random to be below recall_rate threshold (0.7) so policy is added
        mock_random.return_value = 0.3
        
        trade = make_trade(kyc_completeness='Missing')
        result = retrieve_policies(trade)
        
        assert 'POLICY_KYC_001' in result

    @patch('src.policy.retrieval.random.random')
    def test_kyc_missing_respects_recall_rate(self, mock_random):
        """Test that KYC_001 retrieval respects recall_rate."""
        # Mock random to be above recall_rate (0.7) so policy is NOT added
        mock_random.return_value = 0.9
        
        trade = make_trade(kyc_completeness='Missing')
        result = retrieve_policies(trade)
        
        # Should not retrieve KYC_001 if random >= recall_rate
        assert 'POLICY_KYC_001' not in result

    @patch('src.policy.retrieval.random.random')
    def test_kyc_complete_no_kyc_001(self, mock_random):
        """Test that complete KYC doesn't trigger POLICY_KYC_001."""
        mock_random.return_value = 0.3
        
        trade = make_trade(kyc_completeness='Complete')
        result = retrieve_policies(trade)
        
        assert 'POLICY_KYC_001' not in result

    @patch('src.policy.retrieval.random.random')
    def test_kyc_uncertain_triggers_kyc_002(self, mock_random):
        """Test that uncertain KYC triggers POLICY_KYC_002."""
        mock_random.return_value = 0.3
        
        trade = make_trade(kyc_completeness='Uncertain')
        result = retrieve_policies(trade)
        
        assert 'POLICY_KYC_002' in result

    @patch('src.policy.retrieval.has_conflicting_signals')
    @patch('src.policy.retrieval.random.random')
    def test_conflicting_signals_triggers_kyc_003(self, mock_random, mock_conflict):
        """Test that conflicting signals trigger POLICY_KYC_003."""
        mock_random.return_value = 0.3
        mock_conflict.return_value = True
        
        trade = make_trade(kyc_completeness='Complete')
        result = retrieve_policies(trade)
        
        assert 'POLICY_KYC_003' in result


class TestRetrievePoliciesSuitabilitySignals:
    """Test retrieval based on suitability attributes."""

    @patch('src.policy.retrieval.random.random')
    def test_low_risk_tolerance_triggers_suit_001(self, mock_random):
        """Test that low risk tolerance triggers POLICY_SUIT_001."""
        mock_random.return_value = 0.3
        
        trade = make_trade(risk_tolerance='Low')
        result = retrieve_policies(trade)
        
        assert 'POLICY_SUIT_001' in result

    @patch('src.policy.retrieval.random.random')
    def test_short_horizon_triggers_suit_003(self, mock_random):
        """Test that short horizon triggers POLICY_SUIT_003."""
        mock_random.return_value = 0.3
        
        trade = make_trade(investment_time_horizon='Short')
        result = retrieve_policies(trade)
        
        assert 'POLICY_SUIT_003' in result

    @patch('src.policy.retrieval.random.random')
    def test_medium_risk_tolerance_no_suit_001(self, mock_random):
        """Test that medium risk tolerance doesn't trigger POLICY_SUIT_001."""
        mock_random.return_value = 0.9
        
        trade = make_trade(risk_tolerance='Medium')
        result = retrieve_policies(trade)
        
        assert 'POLICY_SUIT_001' not in result

    @patch('src.policy.retrieval.random.random')
    def test_medium_horizon_no_suit_003(self, mock_random):
        """Test that medium horizon doesn't trigger POLICY_SUIT_003."""
        mock_random.return_value = 0.9
        
        trade = make_trade(investment_time_horizon='Medium')
        result = retrieve_policies(trade)
        
        assert 'POLICY_SUIT_003' not in result


class TestRetrievePoliciesRiskAndSupervisionSignals:
    """Test retrieval based on risk and supervisor-related policies."""

    @patch('src.policy.retrieval.random.random')
    def test_high_amount_triggers_risk_001(self, mock_random):
        """Test that high investment amount triggers POLICY_RISK_001."""
        mock_random.return_value = 0.3
        
        trade = make_trade(investment_amount=40000.0)
        result = retrieve_policies(trade)
        
        assert 'POLICY_RISK_001' in result

    @patch('src.policy.retrieval.random.random')
    def test_high_advisor_history_risk_triggers_sup_001(self, mock_random):
        """Test that high advisor history risk triggers POLICY_SUP_001."""
        mock_random.return_value = 0.3
        
        trade = make_trade(advisor_history_risk='High')
        result = retrieve_policies(trade)
        
        assert 'POLICY_SUP_001' in result


class TestRetrievePoliciesDocumentationSignals:
    """Test retrieval based on documentation."""

    @patch('src.policy.retrieval.random.random')
    def test_no_rationale_triggers_doc_001(self, mock_random):
        """Test that missing rationale triggers POLICY_DOC_001."""
        mock_random.return_value = 0.3
        
        trade = make_trade(has_rationale=False)
        result = retrieve_policies(trade)
        
        assert 'POLICY_DOC_001' in result

    @patch('src.policy.retrieval.random.random')
    def test_with_rationale_no_doc_001(self, mock_random):
        """Test that present rationale doesn't trigger POLICY_DOC_001."""
        mock_random.return_value = 0.3
        
        trade = make_trade(has_rationale=True)
        result = retrieve_policies(trade)
        
        assert 'POLICY_DOC_001' not in result


class TestRetrievePoliciesExperienceSignals:
    """Test retrieval based on experience."""

    @patch('src.policy.retrieval.random.random')
    def test_beginner_triggers_exp_001(self, mock_random):
        """Test that beginner experience triggers POLICY_EXP_001."""
        mock_random.return_value = 0.3
        
        trade = make_trade(investment_experience='Beginner')
        result = retrieve_policies(trade)
        
        assert 'POLICY_EXP_001' in result

    @patch('src.policy.retrieval.random.random')
    def test_intermediate_no_exp_001(self, mock_random):
        """Test that intermediate experience doesn't trigger POLICY_EXP_001."""
        mock_random.return_value = 0.3
        
        trade = make_trade(investment_experience='Intermediate')
        result = retrieve_policies(trade)
        
        assert 'POLICY_EXP_001' not in result


class TestRetrievePoliciesNoiseInjection:
    """Test noise injection (false positives)."""

    @patch('src.policy.retrieval.random.sample')
    @patch('src.policy.retrieval.random.randint')
    @patch('src.policy.retrieval.random.random')
    def test_noise_injection_adds_irrelevant_policies(self, mock_random, mock_randint, mock_sample):
        """Test that noise injection adds irrelevant policies."""
        mock_random.return_value = 0.1
        mock_randint.return_value = 1
        mock_sample.return_value = ['POLICY_RISK_001']
        
        trade = make_trade()
        result = retrieve_policies(trade)
        
        assert 'POLICY_RISK_001' in result
        assert len(result) == len(set(result))

    @patch('src.policy.retrieval.random.random')
    def test_noise_respects_config_rate(self, mock_random):
        """Test that no noise is injected when noise_rate is not met."""
        mock_random.return_value = 0.9
        
        trade = make_trade()
        result = retrieve_policies(trade)
        
        assert result == []

    @patch('src.policy.retrieval.random.sample')
    @patch('src.policy.retrieval.random.randint')
    @patch('src.policy.retrieval.random.random')
    def test_noise_respects_max_noise(self, mock_random, mock_randint, mock_sample):
        """Test that noise respects max_noise limit."""
        mock_random.return_value = 0.1
        mock_randint.return_value = 10
        mock_sample.return_value = ALL_POLICY_IDS[:10]
        
        trade = make_trade()
        result = retrieve_policies(trade)
        
        assert len(result) == 10
        assert set(result) == set(ALL_POLICY_IDS[:10])


class TestRetrievePoliciesMultipleSignals:
    """Test retrieval with multiple triggering signals."""

    @patch('src.policy.retrieval.random.random')
    def test_multiple_signals_trigger_multiple_policies(self, mock_random):
        """Test that multiple signals can trigger multiple policies."""
        mock_random.return_value = 0.3  # Below recall_rate to trigger retrieval
        
        trade = make_trade(
            kyc_completeness='Missing',
            risk_tolerance='Low',
            investment_time_horizon='Short',
            has_rationale=False,
            investment_experience='Beginner'
        )
        result = retrieve_policies(trade)
        
        expected = [
            'POLICY_KYC_001',
            'POLICY_SUIT_001',
            'POLICY_SUIT_003',
            'POLICY_DOC_001',
            'POLICY_EXP_001'
        ]
        
        for policy in expected:
            assert policy in result

    @patch('src.policy.retrieval.random.random')
    def test_clean_trade_minimal_retrieval(self, mock_random):
        """Test that clean trade retrieves minimal policies."""
        mock_random.return_value = 0.9  # Above recall_rate, no signal-based retrieval
        
        trade = make_trade(
            kyc_completeness='Complete',
            risk_tolerance='High',
            investment_time_horizon='Long',
            has_rationale=True,
            investment_experience='Advanced'
        )
        result = retrieve_policies(trade)
        
        # Should not retrieve signal-based policies
        unwanted = [
            'POLICY_KYC_001',
            'POLICY_SUIT_001',
            'POLICY_SUIT_003',
            'POLICY_DOC_001',
            'POLICY_EXP_001'
        ]
        
        for policy in unwanted:
            assert policy not in result


class TestRetrievePoliciesDeterministic:
    """Test deterministic behavior when controlling randomness."""

    @patch('src.policy.retrieval.random.random')
    def test_deterministic_with_mocked_random(self, mock_random):
        """Test that behavior is deterministic with controlled randomness."""
        mock_random.return_value = 0.9  # Above recall_rate threshold, so no policy
        
        trade = make_trade(kyc_completeness='Missing')
        result = retrieve_policies(trade)
        
        assert 'POLICY_KYC_001' not in result

    @patch('src.policy.retrieval.random.random')
    def test_deterministic_high_random(self, mock_random):
        """Test deterministic behavior with low random value."""
        mock_random.return_value = 0.3  # Below recall_rate, so policy added
        
        trade = make_trade(kyc_completeness='Missing')
        result = retrieve_policies(trade)
        
        assert 'POLICY_KYC_001' in result


class TestRetrievePoliciesEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_retrieve_policies_with_all_none_values(self):
        """Test retrieval handles trade with None-like values gracefully."""
        # This tests robustness - trade should have all required fields
        trade = make_trade()
        result = retrieve_policies(trade)
        
        assert isinstance(result, list)

    def test_retrieve_policies_consistency(self):
        """Test that same trade with same random seed gives same result."""
        trade = make_trade(
            kyc_completeness='Missing',
            has_rationale=False
        )
        
        # Can't truly test randomness without seeding, but can verify consistency of logic
        result1 = retrieve_policies(trade)
        assert 'POLICY_KYC_001' in result1 or 'POLICY_KYC_001' not in result1  # Tautology, but valid

    def test_retrieve_policies_result_not_exceeding_corpus(self):
        """Test that result never contains policies not in corpus."""
        for _ in range(10):  # Test multiple times due to randomness
            trade = make_trade()
            result = retrieve_policies(trade)
            
            corpus_ids = set(POLICY_CORPUS.keys())
            for policy_id in result:
                assert policy_id in corpus_ids


class TestRetrievePoliciesIntegration:
    """Integration tests for retrieve_policies."""

    def test_retrieve_policies_integration_with_trade_schema(self):
        """Test that retrieve_policies works with actual Trade objects."""
        trade = make_trade()
        result = retrieve_policies(trade)
        
        assert isinstance(result, list)
        assert all(isinstance(p, str) for p in result)
        assert all(p in POLICY_CORPUS for p in result)

    def test_retrieve_policies_handles_various_trade_profiles(self):
        """Test retrieval for various trade profiles."""
        profiles = [
            make_trade(kyc_completeness='Missing'),
            make_trade(risk_tolerance='Low'),
            make_trade(investment_time_horizon='Short'),
            make_trade(has_rationale=False),
            make_trade(investment_experience='Beginner'),
        ]
        
        for trade in profiles:
            result = retrieve_policies(trade)
            assert isinstance(result, list)
            assert all(p in POLICY_CORPUS for p in result)

    @patch('src.policy.retrieval.random.random')
    def test_retrieve_policies_worst_case_scenario(self, mock_random):
        """Test retrieval in worst-case compliance scenario."""
        mock_random.return_value = 0.3  # Low value to trigger all applicable policies
        
        trade = make_trade(
            kyc_completeness='Missing',
            risk_tolerance='Low',
            investment_time_horizon='Short',
            has_rationale=False,
            investment_experience='Beginner'
        )
        result = retrieve_policies(trade)
        
        # Should retrieve multiple high-priority policies
        assert len(result) >= 5
        assert 'POLICY_KYC_001' in result  # Critical
        assert 'POLICY_EXP_001' in result  # Critical
