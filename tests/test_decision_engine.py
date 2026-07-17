import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from unittest.mock import patch, MagicMock
from src.decisioning.decision_engine import evaluate_evidence, compute_priority_score
from src.decisioning.llm_engine import ComplianceEvidenceSchema
from src.decisioning.schema import ConcernSignalType, ViolationType
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
        advisor_rationale='Advisor provided rationale.',
        kyc_completeness='Complete',
    )
    base.update(kwargs)
    return Trade(**base)


def build_evidence(**kwargs):
    """Helper to build ComplianceEvidenceSchema with defaults."""
    return ComplianceEvidenceSchema(
        violations=kwargs.get('violations', []),
        concern_signals=kwargs.get('concern_signals', []),
        confidence_level=kwargs.get('confidence_level', 0.8),
        reasoning=kwargs.get('reasoning', ''),
        additional_context=kwargs.get('additional_context', {}),
    )


@patch('src.decisioning.decision_engine.compute_priority_score')
@patch('src.decisioning.decision_engine.assess_escalation')
@patch('src.decisioning.decision_engine.compute_confidence_score')
@patch('src.decisioning.decision_engine.compute_risk_score')
def test_evaluate_evidence_compliant_trade(mock_risk, mock_confidence,
                                          mock_escalate, mock_priority):
    """Test evaluate_evidence with a compliant trade and good scores."""
    # Setup mocks
    mock_risk.return_value = 25
    mock_confidence.return_value = {'overall': 0.85, 'kyc': 0.9, 'suitability': 0.8}
    mock_escalate.return_value = 'none'
    mock_priority.return_value = 0.5

    # Create trade and evidence
    trade = make_trade()
    trade.trade_id = 'TRADE-123'
    compliance_prediction = {'compliance_probability': 0.95, 'compliance_label': True}
    evidence = build_evidence()

    # Execute
    result = evaluate_evidence(trade, compliance_prediction, evidence)

    # Verify all mocks were called with correct arguments
    mock_risk.assert_called_once_with(trade, evidence)
    mock_confidence.assert_called_once_with(trade, evidence)
    mock_escalate.assert_called_once_with(trade, 0.95, evidence, 25, 0.85)
    mock_priority.assert_called_once_with(trade, 25, 0.85, 'none')

    # Verify result structure
    assert result['risk_score'] == 25
    assert result['confidence_score'] == 0.85
    assert result['confidence_breakdown']['kyc'] == 0.9
    assert result['escalation_level'] == 'none'
    assert result['priority_score'] == 0.5


@patch('src.decisioning.decision_engine.compute_priority_score')
@patch('src.decisioning.decision_engine.assess_escalation')
@patch('src.decisioning.decision_engine.compute_confidence_score')
@patch('src.decisioning.decision_engine.compute_risk_score')
def test_evaluate_evidence_non_compliant_trade(mock_risk, mock_confidence,
                                              mock_escalate, mock_priority):
    """Test evaluate_evidence with a non-compliant trade."""
    # Setup mocks
    mock_risk.return_value = 80
    mock_confidence.return_value = {'overall': 0.45}
    mock_escalate.return_value = 'urgent'
    mock_priority.return_value = 0.9

    # Create trade and evidence
    trade = make_trade()
    trade.trade_id = 'TRADE-456'
    compliance_prediction = {'compliance_probability': 0.2, 'compliance_label': False}
    evidence = build_evidence(concern_signals=[
        ConcernSignalType.OVEREXPOSURE
    ])

    # Execute
    result = evaluate_evidence(trade, compliance_prediction, evidence)

    mock_risk.assert_called_once_with(trade, evidence)
    mock_confidence.assert_called_once_with(trade, evidence)
    mock_escalate.assert_called_once_with(trade, 0.2, evidence, 80, 0.45)
    mock_priority.assert_called_once_with(trade, 80, 0.45, 'urgent')

    # Verify result structure
    assert result['risk_score'] == 80
    assert result['confidence_score'] == 0.45
    assert result['escalation_level'] == 'urgent'
    assert result['priority_score'] == 0.9


@patch('src.decisioning.decision_engine.compute_priority_score')
@patch('src.decisioning.decision_engine.assess_escalation')
@patch('src.decisioning.decision_engine.compute_confidence_score')
@patch('src.decisioning.decision_engine.compute_risk_score')
def test_evaluate_evidence_high_risk_escalated(mock_risk, mock_confidence,
                                              mock_escalate, mock_priority):
    """Test trade escalated due to high risk score."""
    # Setup mocks
    mock_risk.return_value = 85
    mock_confidence.return_value = {'overall': 0.75}
    mock_escalate.return_value = 'priority'
    mock_priority.return_value = 0.7

    # Create trade and evidence
    trade = make_trade()
    compliance_prediction = {'compliance_probability': 0.85, 'compliance_label': True}
    evidence = build_evidence()

    # Execute
    result = evaluate_evidence(trade, compliance_prediction, evidence)

    mock_risk.assert_called_once_with(trade, evidence)

    # Verify escalation despite compliant prediction
    assert result['risk_score'] == 85
    assert result['escalation_level'] == 'priority'


@patch('src.decisioning.decision_engine.compute_priority_score')
@patch('src.decisioning.decision_engine.assess_escalation')
@patch('src.decisioning.decision_engine.compute_confidence_score')
@patch('src.decisioning.decision_engine.compute_risk_score')
def test_evaluate_evidence_low_confidence_escalated(mock_risk, mock_confidence,
                                                   mock_escalate, mock_priority):
    """Test trade escalated due to low confidence score."""
    # Setup mocks
    mock_risk.return_value = 30
    mock_confidence.return_value = {'overall': 0.4}
    mock_escalate.return_value = 'queue'
    mock_priority.return_value = 0.6

    # Create trade and evidence
    trade = make_trade()
    compliance_prediction = {'compliance_probability': 0.85, 'compliance_label': True}
    evidence = build_evidence()

    # Execute
    result = evaluate_evidence(trade, compliance_prediction, evidence)

    mock_risk.assert_called_once_with(trade, evidence)

    # Verify escalation despite compliant prediction and low risk
    assert result['risk_score'] == 30
    assert result['confidence_score'] == 0.4
    assert result['escalation_level'] == 'queue'


@patch('src.decisioning.decision_engine.compute_priority_score')
@patch('src.decisioning.decision_engine.assess_escalation')
@patch('src.decisioning.decision_engine.compute_confidence_score')
@patch('src.decisioning.decision_engine.compute_risk_score')
def test_evaluate_evidence_with_evidence_signals(mock_risk, mock_confidence,
                                                mock_escalate, mock_priority):
    """Test trade with evidence-based signals."""
    # Setup mocks
    mock_risk.return_value = 45
    mock_confidence.return_value = {'overall': 0.7}
    mock_escalate.return_value = 'queue'
    mock_priority.return_value = 0.5

    # Create trade and evidence with concern signals
    trade = make_trade()
    compliance_prediction = {'compliance_probability': 0.75, 'compliance_label': True}
    evidence = build_evidence(concern_signals=[
        ConcernSignalType.AGGRESSIVE_FOR_SHORT_HORIZON
    ])

    # Execute
    result = evaluate_evidence(trade, compliance_prediction, evidence)

    mock_risk.assert_called_once_with(trade, evidence)

    # Verify evaluation with evidence
    assert result['escalation_level'] == 'queue'


@patch('src.decisioning.decision_engine.compute_priority_score')
@patch('src.decisioning.decision_engine.assess_escalation')
@patch('src.decisioning.decision_engine.compute_confidence_score')
@patch('src.decisioning.decision_engine.compute_risk_score')
def test_evaluate_evidence_zero_scores(mock_risk, mock_confidence,
                                      mock_escalate, mock_priority):
    """Test trade with zero risk and confidence scores."""
    # Setup mocks
    mock_risk.return_value = 0
    mock_confidence.return_value = {'overall': 0.0}
    mock_escalate.return_value = 'queue'
    mock_priority.return_value = 0.1

    # Create trade and evidence
    trade = make_trade()
    compliance_prediction = {'compliance_probability': 0.2, 'compliance_label': False}
    evidence = build_evidence()

    # Execute
    result = evaluate_evidence(trade, compliance_prediction, evidence)

    # Verify zero scores are handled correctly
    assert result['risk_score'] == 0
    assert result['confidence_score'] == 0.0
    assert result['escalation_level'] == 'queue'


@patch('src.decisioning.decision_engine.compute_priority_score')
@patch('src.decisioning.decision_engine.assess_escalation')
@patch('src.decisioning.decision_engine.compute_confidence_score')
@patch('src.decisioning.decision_engine.compute_risk_score')
def test_evaluate_evidence_max_scores(mock_risk, mock_confidence,
                                     mock_escalate, mock_priority):
    """Test trade with maximum risk and confidence scores."""
    # Setup mocks
    mock_risk.return_value = 100
    mock_confidence.return_value = {'overall': 1.0}
    mock_escalate.return_value = 'priority'
    mock_priority.return_value = 0.95

    # Create trade and evidence
    trade = make_trade()
    compliance_prediction = {'compliance_probability': 0.85, 'compliance_label': True}
    evidence = build_evidence()

    # Execute
    result = evaluate_evidence(trade, compliance_prediction, evidence)

    # Verify max scores
    assert result['risk_score'] == 100
    assert result['confidence_score'] == 1.0
    assert result['escalation_level'] == 'priority'


@patch('src.decisioning.decision_engine.compute_priority_score')
@patch('src.decisioning.decision_engine.assess_escalation')
@patch('src.decisioning.decision_engine.compute_confidence_score')
@patch('src.decisioning.decision_engine.compute_risk_score')
def test_evaluate_evidence_multiple_concern_signals(mock_risk, mock_confidence,
                                                   mock_escalate, mock_priority):
    """Test trade with multiple conflicting concern signals."""
    # Setup mocks
    mock_risk.return_value = 60
    mock_confidence.return_value = {'overall': 0.65}
    mock_escalate.return_value = 'queue'
    mock_priority.return_value = 0.4

    # Create trade and evidence with multiple signals
    trade = make_trade()
    compliance_prediction = {'compliance_probability': 0.3, 'compliance_label': False}
    evidence = build_evidence(concern_signals=[
        ConcernSignalType.OVEREXPOSURE,
        ConcernSignalType.AGGRESSIVE_FOR_SHORT_HORIZON
    ])

    # Execute
    result = evaluate_evidence(trade, compliance_prediction, evidence)

    # Verify multiple concern signals handled
    assert result['escalation_level'] == 'queue'


@patch('src.decisioning.decision_engine.compute_priority_score')
@patch('src.decisioning.decision_engine.assess_escalation')
@patch('src.decisioning.decision_engine.compute_confidence_score')
@patch('src.decisioning.decision_engine.compute_risk_score')
def test_evaluate_evidence_call_order(mock_risk, mock_confidence,
                                     mock_escalate, mock_priority):
    """Test that functions are called in the correct order."""
    # Setup mocks
    mock_risk.return_value = 40
    mock_confidence.return_value = {'overall': 0.8}
    mock_escalate.return_value = 'none'
    mock_priority.return_value = 0.8

    # Create trade and evidence
    trade = make_trade()
    compliance_prediction = {'compliance_probability': 0.9, 'compliance_label': True}
    evidence = build_evidence()

    # Execute
    result = evaluate_evidence(trade, compliance_prediction, evidence)

    # Verify call order by checking that compliance_probability, risk_score and confidence_score
    # are passed to assess_escalation
    mock_escalate.assert_called_once_with(trade, 0.9, evidence, 40, 0.8)


@patch('src.decisioning.decision_engine.compute_priority_score')
@patch('src.decisioning.decision_engine.assess_escalation')
@patch('src.decisioning.decision_engine.compute_confidence_score')
@patch('src.decisioning.decision_engine.compute_risk_score')
def test_evaluate_evidence_different_trade_ids(mock_risk, mock_confidence,
                                              mock_escalate, mock_priority):
    """Test that different trade IDs are preserved in results."""
    # Setup mocks
    mock_risk.return_value = 35
    mock_confidence.return_value = {'overall': 0.75}
    mock_escalate.return_value = 'none'
    mock_priority.return_value = 0.7

    # Test with different trade IDs
    trade_ids = ['TRADE-001', 'TRADE-999', 'TRADE-ABC123']
    compliance_prediction = {'compliance_probability': 0.85, 'compliance_label': True}
    evidence = build_evidence()

    for trade_id in trade_ids:
        trade = make_trade()
        trade.trade_id = trade_id
        result = evaluate_evidence(trade, compliance_prediction, evidence)
        # Verify result contains expected keys
        assert 'risk_score' in result
        assert 'confidence_score' in result
        assert 'escalation_level' in result
        assert 'priority_score' in result

    assert mock_risk.call_count == len(trade_ids)


@patch('src.decisioning.decision_engine.compute_priority_score')
@patch('src.decisioning.decision_engine.assess_escalation')
@patch('src.decisioning.decision_engine.compute_confidence_score')
@patch('src.decisioning.decision_engine.compute_risk_score')
def test_evaluate_evidence_empty_evidence(mock_risk, mock_confidence,
                                         mock_escalate, mock_priority):
    """Test trade with minimal evidence."""
    # Setup mocks
    mock_escalate.return_value = 'none'
    mock_priority.return_value = 0.6

    # Create trade and evidence
    trade = make_trade()
    compliance_prediction = {'compliance_probability': 0.8, 'compliance_label': True}
    evidence = build_evidence()

    # Execute
    result = evaluate_evidence(trade, compliance_prediction, evidence)

    # Verify minimal evidence handled
    assert result['escalation_level'] == 'none'


@patch('src.decisioning.decision_engine.compute_priority_score')
@patch('src.decisioning.decision_engine.assess_escalation')
@patch('src.decisioning.decision_engine.compute_confidence_score')
@patch('src.decisioning.decision_engine.compute_risk_score')
def test_evaluate_evidence_result_structure(mock_risk, mock_confidence,
                                           mock_escalate, mock_priority):
    """Test that result dictionary has all required keys."""
    # Setup mocks with various values
    mock_risk.return_value = 67
    mock_confidence.return_value = {'overall': 0.52, 'kyc': 0.6, 'suitability': 0.45}
    mock_escalate.return_value = 'urgent'
    mock_priority.return_value = 0.8

    # Create trade and evidence
    trade = make_trade()
    trade.trade_id = 'TEST-123'
    compliance_prediction = {'compliance_probability': 0.35, 'compliance_label': False}
    evidence = build_evidence()

    # Execute
    result = evaluate_evidence(trade, compliance_prediction, evidence)

    # Verify result is a dictionary
    assert isinstance(result, dict)

    # Verify all expected keys are present
    expected_keys = {
        'risk_score',
        'confidence_score',
        'confidence_breakdown',
        'escalation_level',
        'priority_score'
    }
    assert set(result.keys()) == expected_keys

    # Verify types
    assert isinstance(result['risk_score'], int)
    assert isinstance(result['confidence_score'], float)
    assert isinstance(result['confidence_breakdown'], dict)
    assert isinstance(result['escalation_level'], str)
    assert isinstance(result['priority_score'], (float, int))


# Tests for compute_priority_score
def test_compute_priority_score_urgent_level():
    """Test priority score calculation for urgent escalation."""
    trade = make_trade()
    risk_score = 75.0
    confidence_score = 0.6
    
    result = compute_priority_score(trade, risk_score, confidence_score, 'urgent')
    
    # urgent adds 100.0 to base score
    base = 0.7 * 75.0 + 0.3 * (1 - 0.6) * 100
    expected = base + 100.0
    assert result == expected


def test_compute_priority_score_priority_level():
    """Test priority score calculation for priority escalation."""
    trade = make_trade()
    risk_score = 50.0
    confidence_score = 0.7
    
    result = compute_priority_score(trade, risk_score, confidence_score, 'priority')
    
    # priority adds 50.0 to base score
    base = 0.7 * 50.0 + 0.3 * (1 - 0.7) * 100
    expected = base + 50.0
    assert result == expected


def test_compute_priority_score_queue_level_high_risk():
    """Test priority score for queue escalation with high risk."""
    trade = make_trade()
    risk_score = 50.0
    confidence_score = 0.8
    
    result = compute_priority_score(trade, risk_score, confidence_score, 'queue')
    
    # queue with risk >= 35 returns base score
    base = 0.7 * 50.0 + 0.3 * (1 - 0.8) * 100
    expected = base
    assert result == expected


def test_compute_priority_score_queue_level_low_risk():
    """Test priority score for queue escalation with low risk (technical exception)."""
    trade = make_trade()
    risk_score = 30.0
    confidence_score = 0.9
    
    result = compute_priority_score(trade, risk_score, confidence_score, 'queue')
    
    # queue with risk < 35 returns max(5.0, risk_score - 20.0)
    expected = float(max(5.0, 30.0 - 20.0))
    assert result == expected


def test_compute_priority_score_none_level():
    """Test priority score calculation for no escalation."""
    trade = make_trade()
    risk_score = 20.0
    confidence_score = 0.95
    
    result = compute_priority_score(trade, risk_score, confidence_score, 'none')
    
    # no escalation returns 0.0
    assert result == 0.0


def test_compute_priority_score_edge_case_zero_risk():
    """Test priority score with zero risk."""
    trade = make_trade()
    risk_score = 0.0
    confidence_score = 0.5
    
    result = compute_priority_score(trade, risk_score, confidence_score, 'priority')
    
    base = 0.7 * 0.0 + 0.3 * (1 - 0.5) * 100
    expected = base + 50.0
    assert result == expected


def test_compute_priority_score_edge_case_max_risk():
    """Test priority score with maximum risk."""
    trade = make_trade()
    risk_score = 100.0
    confidence_score = 0.0
    
    result = compute_priority_score(trade, risk_score, confidence_score, 'urgent')
    
    base = 0.7 * 100.0 + 0.3 * (1 - 0.0) * 100
    expected = base + 100.0
    assert result == expected


def test_compute_priority_score_queue_boundary_case():
    """Test priority score at queue boundary (risk = 35)."""
    trade = make_trade()
    risk_score = 35.0
    confidence_score = 0.75
    
    result = compute_priority_score(trade, risk_score, confidence_score, 'queue')
    
    # At risk == 35, should return base score (not special override)
    base = 0.7 * 35.0 + 0.3 * (1 - 0.75) * 100
    expected = base
    assert result == expected
