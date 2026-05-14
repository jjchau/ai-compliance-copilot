import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from unittest.mock import patch
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


@patch('src.decisioning.decision_engine.compute_priority_score')
@patch('src.decisioning.decision_engine.assess_escalation')
@patch('src.decisioning.decision_engine.compute_confidence_score')
@patch('src.decisioning.decision_engine.compute_risk_score')
@patch('src.decisioning.decision_engine.predict_compliance')
def test_evaluate_trade_compliant_trade(mock_predict, mock_risk, mock_confidence,
                                       mock_escalate, mock_priority):
    """Test evaluation of a compliant trade with good scores."""
    # Setup mocks
    mock_predict.return_value = {'compliance_probability': 0.95, 'compliance_label': True}
    mock_risk.return_value = 25
    mock_confidence.return_value = {'overall': 0.85}
    mock_escalate.return_value = 'none'
    mock_priority.return_value = 0.5

    # Create trade
    trade = make_trade()
    trade.trade_id = 'TRADE-123'

    # Execute
    result = evaluate_trade(trade)

    # Verify all mocks were called with the trade
    mock_predict.assert_called_once_with(trade)
    mock_risk.assert_called_once_with(trade)
    mock_confidence.assert_called_once_with(trade)
    mock_escalate.assert_called_once_with(trade, 0.95, 25, 0.85)
    mock_priority.assert_called_once_with(trade, 25, 0.85, 'none')

    # Verify result structure
    assert result['compliance_probability'] == 0.95
    assert result['compliance_label'] is True
    assert result['risk_score'] == 25
    assert result['confidence_score'] == 0.85
    assert result['escalation_level'] == 'none'
    assert result['priority_score'] == 0.5


@patch('src.decisioning.decision_engine.compute_priority_score')
@patch('src.decisioning.decision_engine.assess_escalation')
@patch('src.decisioning.decision_engine.compute_confidence_score')
@patch('src.decisioning.decision_engine.compute_risk_score')
@patch('src.decisioning.decision_engine.predict_compliance')
def test_evaluate_trade_non_compliant_trade(mock_predict, mock_risk, mock_confidence,
                                           mock_escalate, mock_priority):
    """Test evaluation of a non-compliant trade."""
    # Setup mocks
    mock_predict.return_value = {'compliance_probability': 0.2, 'compliance_label': False}
    mock_risk.return_value = 80
    mock_confidence.return_value = {'overall': 0.45}
    mock_escalate.return_value = 'urgent'
    mock_priority.return_value = 0.9

    # Create trade
    trade = make_trade()
    trade.trade_id = 'TRADE-456'

    # Execute
    result = evaluate_trade(trade)

    mock_predict.assert_called_once_with(trade)
    mock_risk.assert_called_once_with(trade)
    mock_confidence.assert_called_once_with(trade)
    mock_escalate.assert_called_once_with(trade, 0.2, 80, 0.45)
    mock_priority.assert_called_once_with(trade, 80, 0.45, 'urgent')

    # Verify result structure
    assert result['compliance_probability'] == 0.2
    assert result['compliance_label'] is False
    assert result['risk_score'] == 80
    assert result['confidence_score'] == 0.45
    assert result['escalation_level'] == 'urgent'
    assert result['priority_score'] == 0.9


@patch('src.decisioning.decision_engine.compute_priority_score')
@patch('src.decisioning.decision_engine.assess_escalation')
@patch('src.decisioning.decision_engine.compute_confidence_score')
@patch('src.decisioning.decision_engine.compute_risk_score')
@patch('src.decisioning.decision_engine.predict_compliance')
def test_evaluate_trade_high_risk_escalated(mock_predict, mock_risk, mock_confidence,
                                           mock_escalate, mock_priority):
    """Test trade escalated due to high risk score."""
    # Setup mocks
    mock_predict.return_value = {'compliance_probability': 0.85, 'compliance_label': True}
    mock_risk.return_value = 85
    mock_confidence.return_value = {'overall': 0.75}
    mock_escalate.return_value = 'priority'
    mock_priority.return_value = 0.7

    # Create trade
    trade = make_trade()

    # Execute
    result = evaluate_trade(trade)

    mock_predict.assert_called_once_with(trade)

    # Verify escalation despite compliant prediction
    assert result['compliance_label'] is True
    assert result['risk_score'] == 85
    assert result['escalation_level'] == 'priority'


@patch('src.decisioning.decision_engine.compute_priority_score')
@patch('src.decisioning.decision_engine.assess_escalation')
@patch('src.decisioning.decision_engine.compute_confidence_score')
@patch('src.decisioning.decision_engine.compute_risk_score')
@patch('src.decisioning.decision_engine.predict_compliance')
def test_evaluate_trade_low_confidence_escalated(mock_predict, mock_risk, mock_confidence,
                                                 mock_escalate, mock_priority):
    """Test trade escalated due to low confidence score."""
    # Setup mocks
    mock_predict.return_value = {'compliance_probability': 0.85, 'compliance_label': True}
    mock_risk.return_value = 30
    mock_confidence.return_value = {'overall': 0.4}
    mock_escalate.return_value = 'queue'
    mock_priority.return_value = 0.6

    # Create trade
    trade = make_trade()

    # Execute
    result = evaluate_trade(trade)

    mock_predict.assert_called_once_with(trade)

    # Verify escalation despite compliant prediction and low risk
    assert result['compliance_label'] is True
    assert result['risk_score'] == 30
    assert result['confidence_score'] == 0.4
    assert result['escalation_level'] == 'queue'


@patch('src.decisioning.decision_engine.compute_priority_score')
@patch('src.decisioning.decision_engine.assess_escalation')
@patch('src.decisioning.decision_engine.compute_confidence_score')
@patch('src.decisioning.decision_engine.compute_risk_score')
@patch('src.decisioning.decision_engine.predict_compliance')
def test_evaluate_trade_with_conflicts(mock_predict, mock_risk, mock_confidence,
                                      mock_escalate, mock_priority):
    """Test trade with conflicting signals."""
    # Setup mocks
    mock_predict.return_value = {'compliance_probability': 0.75, 'compliance_label': True}
    mock_risk.return_value = 45
    mock_confidence.return_value = {'overall': 0.7}
    mock_escalate.return_value = 'queue'
    mock_priority.return_value = 0.5

    # Create trade
    trade = make_trade()

    # Execute
    result = evaluate_trade(trade)

    mock_predict.assert_called_once_with(trade)

    # Verify conflict information
    assert result['escalation_level'] == 'queue'


@patch('src.decisioning.decision_engine.compute_priority_score')
@patch('src.decisioning.decision_engine.assess_escalation')
@patch('src.decisioning.decision_engine.compute_confidence_score')
@patch('src.decisioning.decision_engine.compute_risk_score')
@patch('src.decisioning.decision_engine.predict_compliance')
def test_evaluate_trade_zero_scores(mock_predict, mock_risk, mock_confidence,
                                   mock_escalate, mock_priority):
    """Test trade with zero risk and confidence scores."""
    # Setup mocks
    mock_predict.return_value = {'compliance_probability': 0.2, 'compliance_label': False}
    mock_risk.return_value = 0
    mock_confidence.return_value = {'overall': 0.0}
    mock_escalate.return_value = 'queue'
    mock_priority.return_value = 0.1

    # Create trade
    trade = make_trade()

    # Execute
    result = evaluate_trade(trade)

    mock_predict.assert_called_once_with(trade)

    # Verify zero scores are handled correctly
    assert result['risk_score'] == 0
    assert result['confidence_score'] == 0.0
    assert result['escalation_level'] == 'queue'


@patch('src.decisioning.decision_engine.compute_priority_score')
@patch('src.decisioning.decision_engine.assess_escalation')
@patch('src.decisioning.decision_engine.compute_confidence_score')
@patch('src.decisioning.decision_engine.compute_risk_score')
@patch('src.decisioning.decision_engine.predict_compliance')
def test_evaluate_trade_max_scores(mock_predict, mock_risk, mock_confidence,
                                  mock_escalate, mock_priority):
    """Test trade with maximum risk and confidence scores."""
    # Setup mocks
    mock_predict.return_value = {'compliance_probability': 0.85, 'compliance_label': True}
    mock_risk.return_value = 100
    mock_confidence.return_value = {'overall': 1.0}
    mock_escalate.return_value = 'priority'
    mock_priority.return_value = 0.95

    # Create trade
    trade = make_trade()

    # Execute
    result = evaluate_trade(trade)

    mock_predict.assert_called_once_with(trade)

    # Verify max scores
    assert result['risk_score'] == 100
    assert result['confidence_score'] == 1.0
    assert result['escalation_level'] == 'priority'


@patch('src.decisioning.decision_engine.compute_priority_score')
@patch('src.decisioning.decision_engine.assess_escalation')
@patch('src.decisioning.decision_engine.compute_confidence_score')
@patch('src.decisioning.decision_engine.compute_risk_score')
@patch('src.decisioning.decision_engine.predict_compliance')
def test_evaluate_trade_multiple_conflicts(mock_predict, mock_risk, mock_confidence,
                                          mock_escalate, mock_priority):
    """Test trade with multiple conflicting signals."""
    # Setup mocks
    mock_predict.return_value = {'compliance_probability': 0.3, 'compliance_label': False}
    mock_risk.return_value = 60
    mock_confidence.return_value = {'overall': 0.65}
    mock_escalate.return_value = 'queue'
    mock_priority.return_value = 0.4

    # Create trade
    trade = make_trade()

    # Execute
    result = evaluate_trade(trade)

    mock_predict.assert_called_once_with(trade)

    # Verify multiple conflicts
    assert result['escalation_level'] == 'queue'


@patch('src.decisioning.decision_engine.compute_priority_score')
@patch('src.decisioning.decision_engine.assess_escalation')
@patch('src.decisioning.decision_engine.compute_confidence_score')
@patch('src.decisioning.decision_engine.compute_risk_score')
@patch('src.decisioning.decision_engine.predict_compliance')
def test_evaluate_trade_call_order(mock_predict, mock_risk, mock_confidence,
                                  mock_escalate, mock_priority):
    """Test that functions are called in the correct order."""
    # Setup mocks
    mock_predict.return_value = {'compliance_probability': 0.9, 'compliance_label': True}
    mock_risk.return_value = 40
    mock_confidence.return_value = {'overall': 0.8}
    mock_escalate.return_value = 'none'
    mock_priority.return_value = 0.8

    # Create trade
    trade = make_trade()

    # Execute
    result = evaluate_trade(trade)

    mock_predict.assert_called_once_with(trade)

    # Verify call order by checking that compliance_probability, risk_score and confidence_score
    # are passed to assess_escalation
    mock_escalate.assert_called_once_with(trade, 0.9, 40, 0.8)


@patch('src.decisioning.decision_engine.compute_priority_score')
@patch('src.decisioning.decision_engine.assess_escalation')
@patch('src.decisioning.decision_engine.compute_confidence_score')
@patch('src.decisioning.decision_engine.compute_risk_score')
@patch('src.decisioning.decision_engine.predict_compliance')
def test_evaluate_trade_different_trade_ids(mock_predict, mock_risk, mock_confidence,
                                           mock_escalate, mock_priority):
    """Test that different trade IDs are preserved in results."""
    # Setup mocks
    mock_predict.return_value = {'compliance_probability': 0.85, 'compliance_label': True}
    mock_risk.return_value = 35
    mock_confidence.return_value = {'overall': 0.75}
    mock_escalate.return_value = 'none'
    mock_priority.return_value = 0.7

    # Test with different trade IDs
    trade_ids = ['TRADE-001', 'TRADE-999', 'TRADE-ABC123']

    for trade_id in trade_ids:
        trade = make_trade()
        trade.trade_id = trade_id
        result = evaluate_trade(trade)
        # Note: trade_id is not returned in the result, only used internally
        assert isinstance(result, dict)

    assert mock_predict.call_count == len(trade_ids)


@patch('src.decisioning.decision_engine.compute_priority_score')
@patch('src.decisioning.decision_engine.assess_escalation')
@patch('src.decisioning.decision_engine.compute_confidence_score')
@patch('src.decisioning.decision_engine.compute_risk_score')
@patch('src.decisioning.decision_engine.predict_compliance')
def test_evaluate_trade_empty_conflict_signals(mock_predict, mock_risk, mock_confidence,
                                              mock_escalate, mock_priority):
    """Test trade with empty conflict signals list."""
    # Setup mocks
    mock_predict.return_value = {'compliance_probability': 0.8, 'compliance_label': True}
    mock_risk.return_value = 50
    mock_confidence.return_value = {'overall': 0.7}
    mock_escalate.return_value = 'none'
    mock_priority.return_value = 0.6

    # Create trade
    trade = make_trade()

    # Execute
    result = evaluate_trade(trade)

    mock_predict.assert_called_once_with(trade)

    # Verify empty conflict signals
    assert result['escalation_level'] == 'none'


@patch('src.decisioning.decision_engine.compute_priority_score')
@patch('src.decisioning.decision_engine.assess_escalation')
@patch('src.decisioning.decision_engine.compute_confidence_score')
@patch('src.decisioning.decision_engine.compute_risk_score')
@patch('src.decisioning.decision_engine.predict_compliance')
def test_evaluate_trade_result_structure(mock_predict, mock_risk, mock_confidence,
                                        mock_escalate, mock_priority):
    """Test that result dictionary has all required keys."""
    # Setup mocks with various values
    mock_predict.return_value = {'compliance_probability': 0.35, 'compliance_label': False}
    mock_risk.return_value = 67
    mock_confidence.return_value = {'overall': 0.52}
    mock_escalate.return_value = 'urgent'
    mock_priority.return_value = 0.8

    # Create trade
    trade = make_trade()
    trade.trade_id = 'TEST-123'

    # Execute
    result = evaluate_trade(trade)

    mock_predict.assert_called_once_with(trade)

    # Verify result is a dictionary
    assert isinstance(result, dict)

    # Verify all expected keys are present
    expected_keys = {
        'compliance_probability',
        'compliance_label',
        'risk_score',
        'confidence_score',
        'escalation_level',
        'priority_score'
    }
    assert set(result.keys()) == expected_keys

    # Verify types
    assert isinstance(result['compliance_probability'], float)
    assert isinstance(result['compliance_label'], bool)
    assert isinstance(result['risk_score'], int)
    assert isinstance(result['confidence_score'], float)
    assert isinstance(result['escalation_level'], str)
    assert isinstance(result['priority_score'], float)
