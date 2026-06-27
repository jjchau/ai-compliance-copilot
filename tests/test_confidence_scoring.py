import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from src.scoring.confidence_scoring import compute_confidence_score
from src.data.schema import Trade
from src.decisioning.schema import (
    ComplianceEvidenceSchema,
    ViolationType,
    ConcernSignalType,
    EvidenceQualityType,
)


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
        advisor_rationale='This rationale explains the trade.',
        kyc_completeness='Complete',
    )
    base.update(kwargs)
    return Trade(**base)


def build_evidence(**flags):
    ev = ComplianceEvidenceSchema()

    if flags.get('is_kyc_violation'):
        ev.violations.append(ViolationType.KYC_MISSING)

    if flags.get('is_suitability_violation'):
        ev.violations.append(ViolationType.RISK_TOLERANCE_VIOLATION)

    if flags.get('is_experience_violation'):
        ev.violations.append(ViolationType.EXPERIENCE_COMPLEXITY_MISMATCH)

    if flags.get('is_kyc_uncertain'):
        ev.evidence_quality.append(EvidenceQualityType.KYC_UNCERTAIN)

    if flags.get('is_investment_too_aggressive_for_horizon'):
        ev.concern_signals.append(ConcernSignalType.AGGRESSIVE_FOR_SHORT_HORIZON)

    if flags.get('is_investment_too_aggressive_for_objective'):
        ev.concern_signals.append(ConcernSignalType.AGGRESSIVE_FOR_OBJECTIVE)

    if flags.get('is_overexposure'):
        ev.concern_signals.append(ConcernSignalType.OVEREXPOSURE)

    if flags.get('is_risk_too_low_for_profile'):
        ev.concern_signals.append(ConcernSignalType.TOO_CONSERVATIVE_FOR_RISK_PROFILE)

    if flags.get('is_investment_too_conservative_for_objective'):
        ev.concern_signals.append(ConcernSignalType.TOO_CONSERVATIVE_FOR_OBJECTIVE)

    if flags.get('is_investment_too_conservative_for_horizon'):
        ev.concern_signals.append(ConcernSignalType.TOO_CONSERVATIVE_FOR_HORIZON)

    if flags.get('missing_rationale'):
        ev.evidence_quality.append(EvidenceQualityType.MISSING_RATIONALE)

    return ev


def test_confidence_score_high(monkeypatch):
    trade = make_trade()
    ev = build_evidence()

    score = compute_confidence_score(trade, evidence=ev)

    assert isinstance(score, dict)
    assert score['overall'] == 0.82
    assert score['data_completeness'] == 1.0
    assert score['directional_consistency'] == 0.7
    assert score['rule_coverage'] == 0.7


def test_confidence_score_kyc_violation(monkeypatch):
    trade = make_trade(kyc_completeness='Missing')
    ev = build_evidence(is_kyc_violation=True)

    score = compute_confidence_score(trade, evidence=ev)

    assert score['overall'] == 0.715
    assert score['data_completeness'] == 0.7
    assert score['directional_consistency'] == 0.7
    assert score['rule_coverage'] == 0.75


def test_confidence_score_uncertain(monkeypatch):
    trade = make_trade(kyc_completeness='Uncertain')
    ev = build_evidence(is_kyc_uncertain=True)

    score = compute_confidence_score(trade, evidence=ev)

    assert score['overall'] == 0.68
    assert score['data_completeness'] == 0.8
    assert score['directional_consistency'] == 0.7
    assert score['rule_coverage'] == 0.5


def test_confidence_score_conflicting_ignored(monkeypatch):
    trade = make_trade()
    ev = build_evidence()

    score = compute_confidence_score(trade, evidence=ev)

    assert score['overall'] == 0.82


def test_confidence_score_no_rationale(monkeypatch):
    trade = make_trade(advisor_rationale=None)
    ev = build_evidence(missing_rationale=True)

    score = compute_confidence_score(trade, evidence=ev)

    assert score['overall'] == 0.72
    assert score['data_completeness'] == 0.9
    assert score['directional_consistency'] == 0.7
    assert score['rule_coverage'] == 0.5


def test_confidence_score_single_directional_consistency(monkeypatch):
    trade = make_trade()
    ev = build_evidence(is_overexposure=True)

    score = compute_confidence_score(trade, evidence=ev)

    assert score['directional_consistency'] == 0.6
    assert score['rule_coverage'] == 0.5
    assert score['overall'] == 0.73


def test_confidence_score_two_strong_violations(monkeypatch):
    trade = make_trade()
    ev = build_evidence(
        is_suitability_violation=True,
        is_experience_violation=True
    )

    score = compute_confidence_score(trade, evidence=ev)

    assert score['data_completeness'] == 1.0
    assert score['directional_consistency'] == 1.0
    assert score['rule_coverage'] == 0.8
    assert score['overall'] == 0.94


def test_confidence_score_soft_signals_consistent(monkeypatch):
    trade = make_trade()
    ev = build_evidence(
        is_investment_too_aggressive_for_horizon=True,
        is_investment_too_aggressive_for_objective=True
    )

    score = compute_confidence_score(trade, evidence=ev)

    assert score['directional_consistency'] == 1.0
    assert score['rule_coverage'] == 0.65
    assert score['overall'] == 0.895


def test_confidence_score_soft_signals_conflicting_reduces_rule_coverage(monkeypatch):
    trade = make_trade()
    ev = build_evidence(
        is_investment_too_aggressive_for_horizon=True,
        is_investment_too_aggressive_for_objective=True,
        is_risk_too_low_for_profile=True
    )

    score = compute_confidence_score(trade, evidence=ev)

    assert score['directional_consistency'] == 0.667
    assert score['rule_coverage'] == 0.3
    assert score['overall'] == 0.69
