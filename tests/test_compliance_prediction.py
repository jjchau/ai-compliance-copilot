import pytest
from unittest.mock import patch, MagicMock
from src.decisioning.compliance_prediction import predict_compliance
from src.data.schema import Trade


class TestPredictCompliance:
    @patch('src.decisioning.compliance_prediction.random.random')
    @patch('src.decisioning.compliance_prediction.is_suitability_violation')
    @patch('src.decisioning.compliance_prediction.is_experience_violation')
    @patch('src.decisioning.compliance_prediction.is_kyc_violation')
    @patch('src.decisioning.compliance_prediction.is_horizon_mismatch')
    @patch('src.decisioning.compliance_prediction.is_objective_mismatch')
    def test_predict_compliance_no_violations(self, mock_obj_mismatch, mock_horizon_mismatch, mock_kyc, mock_exp, mock_suit, mock_random):
        # Arrange
        mock_suit.return_value = False
        mock_exp.return_value = False
        mock_kyc.return_value = False
        mock_horizon_mismatch.return_value = False
        mock_obj_mismatch.return_value = False
        mock_random.side_effect = [0.1]  # > 0.05, no noise
        trade = MagicMock()

        # Act
        result = predict_compliance(trade)

        # Assert
        assert result is True

    @patch('src.decisioning.compliance_prediction.random.random')
    @patch('src.decisioning.compliance_prediction.is_suitability_violation')
    @patch('src.decisioning.compliance_prediction.is_experience_violation')
    @patch('src.decisioning.compliance_prediction.is_kyc_violation')
    @patch('src.decisioning.compliance_prediction.is_horizon_mismatch')
    @patch('src.decisioning.compliance_prediction.is_objective_mismatch')
    def test_predict_compliance_suitability_violation(self, mock_obj_mismatch, mock_horizon_mismatch, mock_kyc, mock_exp, mock_suit, mock_random):
        # Arrange
        mock_suit.return_value = True
        mock_exp.return_value = False
        mock_kyc.return_value = False
        mock_horizon_mismatch.return_value = False
        mock_obj_mismatch.return_value = False
        mock_random.side_effect = [0.1]  # > 0.05, no noise
        trade = MagicMock()

        # Act
        result = predict_compliance(trade)

        # Assert
        assert result is False

    @patch('src.decisioning.compliance_prediction.random.random')
    @patch('src.decisioning.compliance_prediction.is_suitability_violation')
    @patch('src.decisioning.compliance_prediction.is_experience_violation')
    @patch('src.decisioning.compliance_prediction.is_kyc_violation')
    @patch('src.decisioning.compliance_prediction.is_horizon_mismatch')
    @patch('src.decisioning.compliance_prediction.is_objective_mismatch')
    def test_predict_compliance_kyc_violation_detected(self, mock_obj_mismatch, mock_horizon_mismatch, mock_kyc, mock_exp, mock_suit, mock_random):
        # Arrange
        mock_suit.return_value = False
        mock_exp.return_value = False
        mock_kyc.return_value = True
        mock_horizon_mismatch.return_value = False
        mock_obj_mismatch.return_value = False
        mock_random.side_effect = [0.5, 0.1]  # 0.5 < 0.6 detect kyc, 0.1 > 0.05 no noise
        trade = MagicMock()

        # Act
        result = predict_compliance(trade)

        # Assert
        assert result is False

    @patch('src.decisioning.compliance_prediction.random.random')
    @patch('src.decisioning.compliance_prediction.is_suitability_violation')
    @patch('src.decisioning.compliance_prediction.is_experience_violation')
    @patch('src.decisioning.compliance_prediction.is_kyc_violation')
    @patch('src.decisioning.compliance_prediction.is_horizon_mismatch')
    @patch('src.decisioning.compliance_prediction.is_objective_mismatch')
    def test_predict_compliance_kyc_violation_missed(self, mock_obj_mismatch, mock_horizon_mismatch, mock_kyc, mock_exp, mock_suit, mock_random):
        # Arrange
        mock_suit.return_value = False
        mock_exp.return_value = False
        mock_kyc.return_value = True
        mock_horizon_mismatch.return_value = False
        mock_obj_mismatch.return_value = False
        mock_random.side_effect = [0.7, 0.1]  # 0.7 > 0.6 miss kyc, 0.1 > 0.05 no noise
        trade = MagicMock()

        # Act
        result = predict_compliance(trade)

        # Assert
        assert result is True

    @patch('src.decisioning.compliance_prediction.random.random')
    @patch('src.decisioning.compliance_prediction.is_suitability_violation')
    @patch('src.decisioning.compliance_prediction.is_experience_violation')
    @patch('src.decisioning.compliance_prediction.is_kyc_violation')
    @patch('src.decisioning.compliance_prediction.is_horizon_mismatch')
    @patch('src.decisioning.compliance_prediction.is_objective_mismatch')
    def test_predict_compliance_false_positive_noise(self, mock_obj_mismatch, mock_horizon_mismatch, mock_kyc, mock_exp, mock_suit, mock_random):
        # Arrange
        mock_suit.return_value = False
        mock_exp.return_value = False
        mock_kyc.return_value = False
        mock_horizon_mismatch.return_value = False
        mock_obj_mismatch.return_value = False
        mock_random.side_effect = [0.04]  # < 0.05 noise
        trade = MagicMock()

        # Act
        result = predict_compliance(trade)

        # Assert
        assert result is False

    @patch('src.decisioning.compliance_prediction.random.random')
    @patch('src.decisioning.compliance_prediction.is_suitability_violation')
    @patch('src.decisioning.compliance_prediction.is_experience_violation')
    @patch('src.decisioning.compliance_prediction.is_kyc_violation')
    @patch('src.decisioning.compliance_prediction.is_horizon_mismatch')
    @patch('src.decisioning.compliance_prediction.is_objective_mismatch')
    def test_predict_compliance_horizon_mismatch_fp(self, mock_obj_mismatch, mock_horizon_mismatch, mock_kyc, mock_exp, mock_suit, mock_random):
        # Arrange
        mock_suit.return_value = False
        mock_exp.return_value = False
        mock_kyc.return_value = False
        mock_horizon_mismatch.return_value = True
        mock_obj_mismatch.return_value = False
        mock_random.side_effect = [0.3, 0.1]  # 0.3 < 0.4 horizon fp, 0.1 > 0.05 no noise
        trade = MagicMock()

        # Act
        result = predict_compliance(trade)

        # Assert
        assert result is False

    @patch('src.decisioning.compliance_prediction.random.random')
    @patch('src.decisioning.compliance_prediction.is_suitability_violation')
    @patch('src.decisioning.compliance_prediction.is_experience_violation')
    @patch('src.decisioning.compliance_prediction.is_kyc_violation')
    @patch('src.decisioning.compliance_prediction.is_horizon_mismatch')
    @patch('src.decisioning.compliance_prediction.is_objective_mismatch')
    def test_predict_compliance_objective_mismatch_fp(self, mock_obj_mismatch, mock_horizon_mismatch, mock_kyc, mock_exp, mock_suit, mock_random):
        # Arrange
        mock_suit.return_value = False
        mock_exp.return_value = False
        mock_kyc.return_value = False
        mock_horizon_mismatch.return_value = False
        mock_obj_mismatch.return_value = True
        mock_random.side_effect = [0.2, 0.1]  # 0.2 < 0.3 objective fp, 0.1 > 0.05 no noise
        trade = MagicMock()

        # Act
        result = predict_compliance(trade)

        # Assert
        assert result is False