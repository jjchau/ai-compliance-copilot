import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from unittest.mock import Mock
from src.data.schema import Trade
from src.decisioning.retrieval_prediction import predict_with_retrieval


@pytest.fixture
def mock_trade():
    return Mock(spec=Trade)


class TestPredictWithRetrieval:
    def test_no_policies_no_violations(self, monkeypatch):
        """Test with no retrieved policies and no violations"""
        trade = Mock(spec=Trade)
        
        # Mock all violation functions to return False
        import src.decisioning.retrieval_prediction as rp_mod
        monkeypatch.setattr(rp_mod, 'is_suitability_violation', lambda t: False)
        monkeypatch.setattr(rp_mod, 'is_experience_violation', lambda t: False)
        monkeypatch.setattr(rp_mod, 'is_kyc_violation', lambda t: False)
        monkeypatch.setattr(rp_mod, 'is_investment_too_agressive_for_horizon', lambda t: False)
        monkeypatch.setattr(rp_mod, 'is_investment_too_aggressive_for_objective', lambda t: False)
        
        result = predict_with_retrieval(trade, [])
        
        assert result["compliance_probability"] == 1.0
        assert result["compliance_label"] is True

    def test_kyc_violation_with_policy(self, monkeypatch):
        """Test KYC violation when POLICY_KYC_001 is retrieved and KYC violation exists"""
        trade = Mock(spec=Trade)
        
        import src.decisioning.retrieval_prediction as rp_mod
        monkeypatch.setattr(rp_mod, 'is_suitability_violation', lambda t: False)
        monkeypatch.setattr(rp_mod, 'is_experience_violation', lambda t: False)
        monkeypatch.setattr(rp_mod, 'is_kyc_violation', lambda t: True)
        monkeypatch.setattr(rp_mod, 'is_investment_too_agressive_for_horizon', lambda t: False)
        monkeypatch.setattr(rp_mod, 'is_investment_too_aggressive_for_objective', lambda t: False)
        
        result = predict_with_retrieval(trade, ["POLICY_KYC_001"])
        
        assert result["compliance_probability"] == 0.2  # 1.0 - 0.8
        assert result["compliance_label"] is False

    def test_suitability_violation_with_policy(self, monkeypatch):
        """Test suitability violation when POLICY_SUIT_001 is retrieved and suitability violation exists"""
        trade = Mock(spec=Trade)
        
        import src.decisioning.retrieval_prediction as rp_mod
        monkeypatch.setattr(rp_mod, 'is_suitability_violation', lambda t: True)
        monkeypatch.setattr(rp_mod, 'is_experience_violation', lambda t: False)
        monkeypatch.setattr(rp_mod, 'is_kyc_violation', lambda t: False)
        monkeypatch.setattr(rp_mod, 'is_investment_too_agressive_for_horizon', lambda t: False)
        monkeypatch.setattr(rp_mod, 'is_investment_too_aggressive_for_objective', lambda t: False)
        
        result = predict_with_retrieval(trade, ["POLICY_SUIT_001"])
        
        assert result["compliance_probability"] == 0.4  # 1.0 - 0.6
        assert result["compliance_label"] is False

    def test_experience_violation_with_policy(self, monkeypatch):
        """Test experience violation when POLICY_EXP_001 is retrieved and experience violation exists"""
        trade = Mock(spec=Trade)
        
        import src.decisioning.retrieval_prediction as rp_mod
        monkeypatch.setattr(rp_mod, 'is_suitability_violation', lambda t: False)
        monkeypatch.setattr(rp_mod, 'is_experience_violation', lambda t: True)
        monkeypatch.setattr(rp_mod, 'is_kyc_violation', lambda t: False)
        monkeypatch.setattr(rp_mod, 'is_investment_too_agressive_for_horizon', lambda t: False)
        monkeypatch.setattr(rp_mod, 'is_investment_too_aggressive_for_objective', lambda t: False)
        
        result = predict_with_retrieval(trade, ["POLICY_EXP_001"])
        
        assert result["compliance_probability"] == 0.5  # 1.0 - 0.5
        assert result["compliance_label"] is False

    def test_soft_signals_with_policies(self, monkeypatch):
        """Test soft signals when POLICY_SUIT_002 and POLICY_SUIT_003 are retrieved"""
        trade = Mock(spec=Trade)
        
        import src.decisioning.retrieval_prediction as rp_mod
        monkeypatch.setattr(rp_mod, 'is_suitability_violation', lambda t: False)
        monkeypatch.setattr(rp_mod, 'is_experience_violation', lambda t: False)
        monkeypatch.setattr(rp_mod, 'is_kyc_violation', lambda t: False)
        monkeypatch.setattr(rp_mod, 'is_investment_too_agressive_for_horizon', lambda t: True)
        monkeypatch.setattr(rp_mod, 'is_investment_too_aggressive_for_objective', lambda t: True)
        
        result = predict_with_retrieval(trade, ["POLICY_SUIT_002", "POLICY_SUIT_003"])
        
        assert result["compliance_probability"] == 0.6  # 1.0 - (0.2 + 0.2)
        assert result["compliance_label"] is False

    def test_multiple_violations_score_capped(self, monkeypatch):
        """Test that score is capped at 1.0 (probability can't go below 0.0)"""
        trade = Mock(spec=Trade)
        
        import src.decisioning.retrieval_prediction as rp_mod
        monkeypatch.setattr(rp_mod, 'is_suitability_violation', lambda t: True)
        monkeypatch.setattr(rp_mod, 'is_experience_violation', lambda t: True)
        monkeypatch.setattr(rp_mod, 'is_kyc_violation', lambda t: True)
        monkeypatch.setattr(rp_mod, 'is_investment_too_agressive_for_horizon', lambda t: True)
        monkeypatch.setattr(rp_mod, 'is_investment_too_aggressive_for_objective', lambda t: True)
        
        result = predict_with_retrieval(trade, [
            "POLICY_SUIT_001", "POLICY_EXP_001", "POLICY_KYC_001",
            "POLICY_SUIT_002", "POLICY_SUIT_003"
        ])
        
        # Score = 0.6 + 0.5 + 0.8 + 0.2 + 0.2 = 2.3, but capped at 1.0
        assert result["compliance_probability"] == 0.0  # 1.0 - 1.0
        assert result["compliance_label"] is False

    def test_violations_without_relevant_policies(self, monkeypatch):
        """Test that violations don't affect score if relevant policies aren't retrieved"""
        trade = Mock(spec=Trade)
        
        import src.decisioning.retrieval_prediction as rp_mod
        monkeypatch.setattr(rp_mod, 'is_suitability_violation', lambda t: True)
        monkeypatch.setattr(rp_mod, 'is_experience_violation', lambda t: True)
        monkeypatch.setattr(rp_mod, 'is_kyc_violation', lambda t: True)
        monkeypatch.setattr(rp_mod, 'is_investment_too_agressive_for_horizon', lambda t: True)
        monkeypatch.setattr(rp_mod, 'is_investment_too_aggressive_for_objective', lambda t: True)
        
        # No relevant policies retrieved
        result = predict_with_retrieval(trade, ["POLICY_UNRELATED_001"])
        
        assert result["compliance_probability"] == 1.0
        assert result["compliance_label"] is True

    def test_threshold_boundary_cases(self, monkeypatch):
        """Test compliance label threshold at 0.9"""
        trade = Mock(spec=Trade)
        
        import src.decisioning.retrieval_prediction as rp_mod
        
        # Test exactly at threshold (0.9)
        monkeypatch.setattr(rp_mod, 'is_suitability_violation', lambda t: False)
        monkeypatch.setattr(rp_mod, 'is_experience_violation', lambda t: False)
        monkeypatch.setattr(rp_mod, 'is_kyc_violation', lambda t: False)
        monkeypatch.setattr(rp_mod, 'is_investment_too_agressive_for_horizon', lambda t: False)
        monkeypatch.setattr(rp_mod, 'is_investment_too_aggressive_for_objective', lambda t: False)
        
        result = predict_with_retrieval(trade, [])
        assert result["compliance_probability"] == 1.0
        assert result["compliance_label"] is True
        
        # Test just below threshold (score = 0.1, prob = 0.9)
        monkeypatch.setattr(rp_mod, 'is_investment_too_agressive_for_horizon', lambda t: True)
        result = predict_with_retrieval(trade, ["POLICY_SUIT_003"])
        assert result["compliance_probability"] == 0.8  # 1.0 - 0.2
        assert result["compliance_label"] is False