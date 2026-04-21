import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from unittest.mock import patch, MagicMock
from src.decisioning.decision_engine import evaluate_trade
from src.data.schema import Trade


# Dummy trade factory for tests
def make_trade(**kwargs):
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


@patch('src.decisioning.decision_engine.get_conflict_signals')
@patch('src.decisioning.decision_engine.has_conflicting_signals')
@patch('src.decisioning.decision_engine.should_flag')
@patch('src.decisioning.decision_engine.compute_confidence_score')
@patch('src.decisioning.decision_engine.compute_risk_score')
@patch('src.decisioning.decision_engine.predict_compliance')
def test_evaluate_trade_compliant_trade(mock_predict, mock_risk, mock_confidence,
                                       mock_flag, mock_has_conflict, mock_get_conflict):
    """Test evaluation of a compliant trade with good scores."""
    # Setup mocks
    mock_predict.return_value = True
    mock_risk.return_value = 25
    mock_confidence.return_value = 0.85
    mock_flag.return_value = False
    mock_has_conflict.return_value = False
    mock_get_conflict.return_value = []

    # Create trade
    trade = make_trade(trade_id='TRADE-123')

    # Execute
    result = evaluate_trade(trade)

    # Verify all mocks were called with the trade
    mock_predict.assert_called_once_with(trade)
    mock_risk.assert_called_once_with(trade)
    mock_confidence.assert_called_once_with(trade)
    mock_flag.assert_called_once_with(trade, 25, 0.85)
    mock_has_conflict.assert_called_once_with(trade)
    mock_get_conflict.assert_called_once_with(trade)

    # Verify result structure
    expected = {
        'trade_id': 'TRADE-123',
        'compliance_prediction': True,
        'risk_score': 25,
        'confidence_score': 0.85,
        'flag_for_review': False,
        'has_conflicting_signals': False,
        'conflict_signals': []
    }
    assert result == expected


@patch('src.decisioning.decision_engine.get_conflict_signals')
@patch('src.decisioning.decision_engine.has_conflicting_signals')
@patch('src.decisioning.decision_engine.should_flag')
@patch('src.decisioning.decision_engine.compute_confidence_score')
@patch('src.decisioning.decision_engine.compute_risk_score')
@patch('src.decisioning.decision_engine.predict_compliance')
def test_evaluate_trade_non_compliant_trade(mock_predict, mock_risk, mock_confidence,
                                           mock_flag, mock_has_conflict, mock_get_conflict):
    """Test evaluation of a non-compliant trade."""
    # Setup mocks
    mock_predict.return_value = False
    mock_risk.return_value = 80
    mock_confidence.return_value = 0.45
    mock_flag.return_value = True
    mock_has_conflict.return_value = True
    mock_get_conflict.return_value = ['High risk with low confidence']

    # Create trade
    trade = make_trade(trade_id='TRADE-456')

    # Execute
    result = evaluate_trade(trade)

    # Verify result structure
    expected = {
        'trade_id': 'TRADE-456',
        'compliance_prediction': False,
        'risk_score': 80,
        'confidence_score': 0.45,
        'flag_for_review': True,
        'has_conflicting_signals': True,
        'conflict_signals': ['High risk with low confidence']
    }
    assert result == expected


@patch('src.decisioning.decision_engine.get_conflict_signals')
@patch('src.decisioning.decision_engine.has_conflicting_signals')
@patch('src.decisioning.decision_engine.should_flag')
@patch('src.decisioning.decision_engine.compute_confidence_score')
@patch('src.decisioning.decision_engine.compute_risk_score')
@patch('src.decisioning.decision_engine.predict_compliance')
def test_evaluate_trade_high_risk_flagged(mock_predict, mock_risk, mock_confidence,
                                         mock_flag, mock_has_conflict, mock_get_conflict):
    """Test trade flagged due to high risk score."""
    # Setup mocks
    mock_predict.return_value = True
    mock_risk.return_value = 85
    mock_confidence.return_value = 0.75
    mock_flag.return_value = True  # Flagged due to high risk
    mock_has_conflict.return_value = False
    mock_get_conflict.return_value = []

    # Create trade
    trade = make_trade()

    # Execute
    result = evaluate_trade(trade)

    # Verify flag is True despite compliant prediction
    assert result['compliance_prediction'] is True
    assert result['risk_score'] == 85
    assert result['flag_for_review'] is True
    assert result['has_conflicting_signals'] is False


@patch('src.decisioning.decision_engine.get_conflict_signals')
@patch('src.decisioning.decision_engine.has_conflicting_signals')
@patch('src.decisioning.decision_engine.should_flag')
@patch('src.decisioning.decision_engine.compute_confidence_score')
@patch('src.decisioning.decision_engine.compute_risk_score')
@patch('src.decisioning.decision_engine.predict_compliance')
def test_evaluate_trade_low_confidence_flagged(mock_predict, mock_risk, mock_confidence,
                                              mock_flag, mock_has_conflict, mock_get_conflict):
    """Test trade flagged due to low confidence score."""
    # Setup mocks
    mock_predict.return_value = True
    mock_risk.return_value = 30
    mock_confidence.return_value = 0.4
    mock_flag.return_value = True  # Flagged due to low confidence
    mock_has_conflict.return_value = False
    mock_get_conflict.return_value = []

    # Create trade
    trade = make_trade()

    # Execute
    result = evaluate_trade(trade)

    # Verify flag is True despite compliant prediction and low risk
    assert result['compliance_prediction'] is True
    assert result['risk_score'] == 30
    assert result['confidence_score'] == 0.4
    assert result['flag_for_review'] is True


@patch('src.decisioning.decision_engine.get_conflict_signals')
@patch('src.decisioning.decision_engine.has_conflicting_signals')
@patch('src.decisioning.decision_engine.should_flag')
@patch('src.decisioning.decision_engine.compute_confidence_score')
@patch('src.decisioning.decision_engine.compute_risk_score')
@patch('src.decisioning.decision_engine.predict_compliance')
def test_evaluate_trade_with_conflicts(mock_predict, mock_risk, mock_confidence,
                                     mock_flag, mock_has_conflict, mock_get_conflict):
    """Test trade with conflicting signals."""
    # Setup mocks
    mock_predict.return_value = True
    mock_risk.return_value = 45
    mock_confidence.return_value = 0.7
    mock_flag.return_value = False
    mock_has_conflict.return_value = True
    mock_get_conflict.return_value = ['Conflicting risk signals detected']

    # Create trade
    trade = make_trade()

    # Execute
    result = evaluate_trade(trade)

    # Verify conflict information
    assert result['has_conflicting_signals'] is True
    assert result['conflict_signals'] == ['Conflicting risk signals detected']


@patch('src.decisioning.decision_engine.get_conflict_signals')
@patch('src.decisioning.decision_engine.has_conflicting_signals')
@patch('src.decisioning.decision_engine.should_flag')
@patch('src.decisioning.decision_engine.compute_confidence_score')
@patch('src.decisioning.decision_engine.compute_risk_score')
@patch('src.decisioning.decision_engine.predict_compliance')
def test_evaluate_trade_zero_scores(mock_predict, mock_risk, mock_confidence,
                                   mock_flag, mock_has_conflict, mock_get_conflict):
    """Test trade with zero risk and confidence scores."""
    # Setup mocks
    mock_predict.return_value = False
    mock_risk.return_value = 0
    mock_confidence.return_value = 0.0
    mock_flag.return_value = True
    mock_has_conflict.return_value = False
    mock_get_conflict.return_value = []

    # Create trade
    trade = make_trade()

    # Execute
    result = evaluate_trade(trade)

    # Verify zero scores are handled correctly
    assert result['risk_score'] == 0
    assert result['confidence_score'] == 0.0
    assert result['flag_for_review'] is True


@patch('src.decisioning.decision_engine.get_conflict_signals')
@patch('src.decisioning.decision_engine.has_conflicting_signals')
@patch('src.decisioning.decision_engine.should_flag')
@patch('src.decisioning.decision_engine.compute_confidence_score')
@patch('src.decisioning.decision_engine.compute_risk_score')
@patch('src.decisioning.decision_engine.predict_compliance')
def test_evaluate_trade_max_scores(mock_predict, mock_risk, mock_confidence,
                                  mock_flag, mock_has_conflict, mock_get_conflict):
    """Test trade with maximum risk and confidence scores."""
    # Setup mocks
    mock_predict.return_value = True
    mock_risk.return_value = 100
    mock_confidence.return_value = 1.0
    mock_flag.return_value = True  # High risk triggers flag
    mock_has_conflict.return_value = False
    mock_get_conflict.return_value = []

    # Create trade
    trade = make_trade()

    # Execute
    result = evaluate_trade(trade)

    # Verify max scores
    assert result['risk_score'] == 100
    assert result['confidence_score'] == 1.0
    assert result['flag_for_review'] is True  # Due to high risk


@patch('src.decisioning.decision_engine.get_conflict_signals')
@patch('src.decisioning.decision_engine.has_conflicting_signals')
@patch('src.decisioning.decision_engine.should_flag')
@patch('src.decisioning.decision_engine.compute_confidence_score')
@patch('src.decisioning.decision_engine.compute_risk_score')
@patch('src.decisioning.decision_engine.predict_compliance')
def test_evaluate_trade_multiple_conflicts(mock_predict, mock_risk, mock_confidence,
                                          mock_flag, mock_has_conflict, mock_get_conflict):
    """Test trade with multiple conflicting signals."""
    # Setup mocks
    mock_predict.return_value = False
    mock_risk.return_value = 60
    mock_confidence.return_value = 0.65
    mock_flag.return_value = False
    mock_has_conflict.return_value = True
    mock_get_conflict.return_value = [
        'High risk with uncertain KYC',
        'Complex investment for beginner',
        'Advisor history conflicts with recommendation'
    ]

    # Create trade
    trade = make_trade()

    # Execute
    result = evaluate_trade(trade)

    # Verify multiple conflicts
    assert result['has_conflicting_signals'] is True
    assert len(result['conflict_signals']) == 3
    assert 'High risk with uncertain KYC' in result['conflict_signals']
    assert 'Complex investment for beginner' in result['conflict_signals']
    assert 'Advisor history conflicts with recommendation' in result['conflict_signals']


@patch('src.decisioning.decision_engine.get_conflict_signals')
@patch('src.decisioning.decision_engine.has_conflicting_signals')
@patch('src.decisioning.decision_engine.should_flag')
@patch('src.decisioning.decision_engine.compute_confidence_score')
@patch('src.decisioning.decision_engine.compute_risk_score')
@patch('src.decisioning.decision_engine.predict_compliance')
def test_evaluate_trade_call_order(mock_predict, mock_risk, mock_confidence,
                                  mock_flag, mock_has_conflict, mock_get_conflict):
    """Test that functions are called in the correct order."""
    # Setup mocks
    mock_predict.return_value = True
    mock_risk.return_value = 40
    mock_confidence.return_value = 0.8
    mock_flag.return_value = False
    mock_has_conflict.return_value = False
    mock_get_conflict.return_value = []

    # Create trade
    trade = make_trade()

    # Execute
    result = evaluate_trade(trade)

    # Verify call order by checking that risk_score and confidence_score
    # are passed to should_flag
    mock_flag.assert_called_once_with(trade, 40, 0.8)


@patch('src.decisioning.decision_engine.get_conflict_signals')
@patch('src.decisioning.decision_engine.has_conflicting_signals')
@patch('src.decisioning.decision_engine.should_flag')
@patch('src.decisioning.decision_engine.compute_confidence_score')
@patch('src.decisioning.decision_engine.compute_risk_score')
@patch('src.decisioning.decision_engine.predict_compliance')
def test_evaluate_trade_different_trade_ids(mock_predict, mock_risk, mock_confidence,
                                           mock_flag, mock_has_conflict, mock_get_conflict):
    """Test that different trade IDs are preserved in results."""
    # Setup mocks
    mock_predict.return_value = True
    mock_risk.return_value = 35
    mock_confidence.return_value = 0.75
    mock_flag.return_value = False
    mock_has_conflict.return_value = False
    mock_get_conflict.return_value = []

    # Test with different trade IDs
    trade_ids = ['TRADE-001', 'TRADE-999', 'TRADE-ABC123']

    for trade_id in trade_ids:
        trade = make_trade(trade_id=trade_id)
        result = evaluate_trade(trade)
        assert result['trade_id'] == trade_id


@patch('src.decisioning.decision_engine.get_conflict_signals')
@patch('src.decisioning.decision_engine.has_conflicting_signals')
@patch('src.decisioning.decision_engine.should_flag')
@patch('src.decisioning.decision_engine.compute_confidence_score')
@patch('src.decisioning.decision_engine.compute_risk_score')
@patch('src.decisioning.decision_engine.predict_compliance')
def test_evaluate_trade_empty_conflict_signals(mock_predict, mock_risk, mock_confidence,
                                              mock_flag, mock_has_conflict, mock_get_conflict):
    """Test trade with empty conflict signals list."""
    # Setup mocks
    mock_predict.return_value = True
    mock_risk.return_value = 50
    mock_confidence.return_value = 0.7
    mock_flag.return_value = False
    mock_has_conflict.return_value = False
    mock_get_conflict.return_value = []  # Empty list

    # Create trade
    trade = make_trade()

    # Execute
    result = evaluate_trade(trade)

    # Verify empty conflict signals
    assert result['has_conflicting_signals'] is False
    assert result['conflict_signals'] == []


@patch('src.decisioning.decision_engine.get_conflict_signals')
@patch('src.decisioning.decision_engine.has_conflicting_signals')
@patch('src.decisioning.decision_engine.should_flag')
@patch('src.decisioning.decision_engine.compute_confidence_score')
@patch('src.decisioning.decision_engine.compute_risk_score')
@patch('src.decisioning.decision_engine.predict_compliance')
def test_evaluate_trade_result_structure(mock_predict, mock_risk, mock_confidence,
                                        mock_flag, mock_has_conflict, mock_get_conflict):
    """Test that result dictionary has all required keys."""
    # Setup mocks with various values
    mock_predict.return_value = False
    mock_risk.return_value = 67
    mock_confidence.return_value = 0.52
    mock_flag.return_value = True
    mock_has_conflict.return_value = True
    mock_get_conflict.return_value = ['Test conflict']

    # Create trade
    trade = make_trade(trade_id='TEST-123')

    # Execute
    result = evaluate_trade(trade)

    # Verify result is a dictionary
    assert isinstance(result, dict)

    # Verify all expected keys are present
    expected_keys = {
        'trade_id',
        'compliance_prediction',
        'risk_score',
        'confidence_score',
        'flag_for_review',
        'has_conflicting_signals',
        'conflict_signals'
    }
    assert set(result.keys()) == expected_keys

    # Verify types
    assert isinstance(result['trade_id'], str)
    assert isinstance(result['compliance_prediction'], bool)
    assert isinstance(result['risk_score'], int)
    assert isinstance(result['confidence_score'], float)
    assert isinstance(result['flag_for_review'], bool)
    assert isinstance(result['has_conflicting_signals'], bool)
    assert isinstance(result['conflict_signals'], list)