import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from unittest.mock import Mock, patch
from src.data.schema import Trade
from src.orchestration.review_pipeline import build_review_case


class TestBuildReviewCase:
    @patch('src.orchestration.review_pipeline.retrieve_policies')
    @patch('src.orchestration.review_pipeline.predict_with_retrieval')
    @patch('src.orchestration.review_pipeline.evaluate_prediction')
    @patch('src.orchestration.review_pipeline.has_conflicting_signals')
    @patch('src.orchestration.review_pipeline.get_signals')
    @patch('src.orchestration.review_pipeline.generate_explanation')
    def test_build_review_case_structure(self, mock_generate_explanation, mock_get_signals, 
                                        mock_has_conflicting, mock_evaluate_prediction, 
                                        mock_predict, mock_retrieve):
        """Test that build_review_case returns correctly structured dictionary."""
        # Setup mocks
        mock_retrieve.return_value = ["POLICY_KYC_001", "POLICY_SUIT_001"]
        mock_predict.return_value = {"compliance_probability": 0.8, "some_other_field": "value"}
        mock_evaluate_prediction.return_value = {
            "compliance_label": True,
            "risk_score": 25,
            "confidence_score": 0.85
        }
        mock_has_conflicting.return_value = False
        mock_get_signals.return_value = []
        mock_generate_explanation.return_value = "Test explanation"
        
        # Create test trade
        trade = Trade(
            trade_id="TEST-123",
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
        
        result = build_review_case(trade)
        
        # Verify structure
        assert isinstance(result, dict)
        assert result["trade_id"] == "TEST-123"
        
        # Verify all trade fields are included
        trade_dict = trade.model_dump()
        for key, value in trade_dict.items():
            assert key in result
            assert result[key] == value
        
        # Verify evaluation results are included
        assert result["compliance_label"] is True
        assert result["risk_score"] == 25
        assert result["confidence_score"] == 0.85
        
        # Verify retrieved policies
        assert result["retrieved_policies"] == ["POLICY_KYC_001", "POLICY_SUIT_001"]
        
        # Verify conflict detection
        assert result["has_conflicting_signals"] is False
        assert result["conflict_signals"] == []
        
        # Verify explanation
        assert result["flag_reasons"] == "Test explanation"

    @patch('src.orchestration.review_pipeline.retrieve_policies')
    @patch('src.orchestration.review_pipeline.predict_with_retrieval')
    @patch('src.orchestration.review_pipeline.evaluate_prediction')
    @patch('src.orchestration.review_pipeline.has_conflicting_signals')
    @patch('src.orchestration.review_pipeline.get_signals')
    @patch('src.orchestration.review_pipeline.generate_explanation')
    def test_build_review_case_calls_all_components(self, mock_generate_explanation, mock_get_signals,
                                                   mock_has_conflicting, mock_evaluate_prediction,
                                                   mock_predict, mock_retrieve):
        """Test that build_review_case calls all required components."""
        # Setup mocks
        mock_retrieve.return_value = ["POLICY_KYC_001"]
        mock_predict.return_value = {"compliance_probability": 0.9}
        mock_evaluate_prediction.return_value = {"compliance_label": True}
        mock_has_conflicting.return_value = True
        mock_get_signals.return_value = ["signal1", "signal2"]
        mock_generate_explanation.return_value = "Explanation"
        
        trade = Trade(
            client_age=30,
            client_income=50000,
            risk_tolerance='Low',
            investment_experience='Beginner',
            investment_objective='Preservation',
            investment_time_horizon='Short',
            investment_type='Bonds',
            investment_amount=5000.0,
            advisor_id='A456',
            advisor_experience='Junior',
            advisor_history_risk='Low',
            advisor_rationale='Advisor rationale provided.',
            kyc_completeness='Complete'
        )
        
        result = build_review_case(trade)
        
        # Verify all functions were called with correct parameters
        mock_retrieve.assert_called_once_with(trade)
        mock_predict.assert_called_once_with(trade, ["POLICY_KYC_001"])
        mock_evaluate_prediction.assert_called_once_with(trade, {"compliance_probability": 0.9})
        mock_has_conflicting.assert_called_once_with(trade)
        mock_get_signals.assert_called_once_with(trade)
        mock_generate_explanation.assert_called_once_with(trade, ["POLICY_KYC_001"])

    @patch('src.orchestration.review_pipeline.retrieve_policies')
    @patch('src.orchestration.review_pipeline.predict_with_retrieval')
    @patch('src.orchestration.review_pipeline.evaluate_prediction')
    @patch('src.orchestration.review_pipeline.has_conflicting_signals')
    @patch('src.orchestration.review_pipeline.get_signals')
    @patch('src.orchestration.review_pipeline.generate_explanation')
    def test_build_review_case_with_conflicting_signals(self, mock_generate_explanation, mock_get_signals,
                                                       mock_has_conflicting, mock_evaluate_prediction,
                                                       mock_predict, mock_retrieve):
        """Test build_review_case when conflicting signals are detected."""
        mock_retrieve.return_value = ["POLICY_KYC_001"]
        mock_predict.return_value = {"compliance_probability": 0.6}
        mock_evaluate_prediction.return_value = {"compliance_label": False}
        mock_has_conflicting.return_value = True
        mock_get_signals.return_value = ["risk_too_high", "experience_insufficient"]
        mock_generate_explanation.return_value = "Multiple compliance issues detected"
        
        trade = Trade(
            client_age=25,
            client_income=30000,
            risk_tolerance='Low',
            investment_experience='Beginner',
            investment_objective='Preservation',
            investment_time_horizon='Short',
            investment_type='Options',  # High risk
            investment_amount=20000.0,  # Large amount
            advisor_id='A789',
            advisor_experience='Junior',
            advisor_history_risk='High',
            advisor_rationale=None,
            kyc_completeness='Missing'
        )
        
        result = build_review_case(trade)
        
        assert result["has_conflicting_signals"] is True
        assert result["conflict_signals"] == ["risk_too_high", "experience_insufficient"]
        assert result["flag_reasons"] == "Multiple compliance issues detected"

    @patch('src.orchestration.review_pipeline.retrieve_policies')
    @patch('src.orchestration.review_pipeline.predict_with_retrieval')
    @patch('src.orchestration.review_pipeline.evaluate_prediction')
    @patch('src.orchestration.review_pipeline.has_conflicting_signals')
    @patch('src.orchestration.review_pipeline.get_signals')
    @patch('src.orchestration.review_pipeline.generate_explanation')
    def test_build_review_case_preserves_trade_id(self, mock_generate_explanation, mock_get_signals,
                                                 mock_has_conflicting, mock_evaluate_prediction,
                                                 mock_predict, mock_retrieve):
        """Test that build_review_case preserves the original trade_id."""
        mock_retrieve.return_value = []
        mock_predict.return_value = {}
        mock_evaluate_prediction.return_value = {}
        mock_has_conflicting.return_value = False
        mock_get_signals.return_value = []
        mock_generate_explanation.return_value = ""
        
        custom_trade_id = "CUSTOM-TRADE-123"
        trade = Trade(
            trade_id=custom_trade_id,
            client_age=40,
            client_income=80000,
            risk_tolerance='High',
            investment_experience='Advanced',
            investment_objective='Growth',
            investment_time_horizon='Long',
            investment_type='ETFs',
            investment_amount=50000.0,
            advisor_id='A999',
            advisor_experience='Senior',
            advisor_history_risk='Low',
            advisor_rationale='Advisor rationale provided.',
            kyc_completeness='Complete'
        )
        
        result = build_review_case(trade)
        
        assert result["trade_id"] == custom_trade_id