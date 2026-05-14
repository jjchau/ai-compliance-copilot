import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from src.scoring.confidence_scoring import compute_confidence_score
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


def patch_all_signals(monkeypatch, cs_mod, **overrides):
    defaults = {
        'is_kyc_violation': False,
        'is_suitability_violation': False,
        'is_experience_violation': False,
        'is_kyc_uncertain': False,
        'is_investment_too_aggressive_for_horizon': False,
        'is_investment_too_aggressive_for_objective': False,
        'is_overexposure': False,
        'is_risk_too_low_for_profile': False,
        'is_investment_too_conservative_for_objective': False,
        'is_investment_too_conservative_for_horizon': False,
    }
    defaults.update(overrides)

    for name, value in defaults.items():
        monkeypatch.setattr(cs_mod, name, (lambda v: (lambda t: v))(value))


def test_confidence_score_high(monkeypatch):
    trade = make_trade()
    import src.scoring.confidence_scoring as cs_mod
    patch_all_signals(monkeypatch, cs_mod)

    score = compute_confidence_score(trade)

    assert isinstance(score, dict)
    assert score['overall'] == 0.82
    assert score['data_completeness'] == 1.0
    assert score['signal_consistency'] == 0.7
    assert score['rule_coverage'] == 0.7


def test_confidence_score_kyc_violation(monkeypatch):
    trade = make_trade(kyc_completeness='Missing')
    import src.scoring.confidence_scoring as cs_mod
    patch_all_signals(monkeypatch, cs_mod, is_kyc_violation=True)

    score = compute_confidence_score(trade)

    assert score['overall'] == 0.715
    assert score['data_completeness'] == 0.7
    assert score['signal_consistency'] == 0.7
    assert score['rule_coverage'] == 0.75


def test_confidence_score_uncertain(monkeypatch):
    trade = make_trade(kyc_completeness='Uncertain')
    import src.scoring.confidence_scoring as cs_mod
    patch_all_signals(monkeypatch, cs_mod, is_kyc_uncertain=True)

    score = compute_confidence_score(trade)

    assert score['overall'] == 0.68
    assert score['data_completeness'] == 0.8
    assert score['signal_consistency'] == 0.7
    assert score['rule_coverage'] == 0.5


def test_confidence_score_conflicting_ignored(monkeypatch):
    trade = make_trade()
    import src.scoring.confidence_scoring as cs_mod
    patch_all_signals(monkeypatch, cs_mod)
    # has_conflicting_signals is not used in compute_confidence_score
    monkeypatch.setattr(cs_mod, 'has_conflicting_signals', lambda t: True)

    score = compute_confidence_score(trade)

    assert score['overall'] == 0.82


def test_confidence_score_no_rationale(monkeypatch):
    trade = make_trade(has_rationale=False)
    import src.scoring.confidence_scoring as cs_mod
    patch_all_signals(monkeypatch, cs_mod)

    score = compute_confidence_score(trade)

    assert score['overall'] == 0.78
    assert score['data_completeness'] == 0.9
    assert score['signal_consistency'] == 0.7
    assert score['rule_coverage'] == 0.7


def test_confidence_score_single_signal_consistency(monkeypatch):
    trade = make_trade()
    import src.scoring.confidence_scoring as cs_mod
    patch_all_signals(monkeypatch, cs_mod, is_overexposure=True)

    score = compute_confidence_score(trade)

    assert score['signal_consistency'] == 0.6
    assert score['rule_coverage'] == 0.5
    assert score['overall'] == 0.73


def test_confidence_score_two_strong_violations(monkeypatch):
    trade = make_trade()
    import src.scoring.confidence_scoring as cs_mod
    patch_all_signals(
        monkeypatch,
        cs_mod,
        is_suitability_violation=True,
        is_experience_violation=True
    )

    score = compute_confidence_score(trade)

    assert score['data_completeness'] == 1.0
    assert score['signal_consistency'] == 1.0
    assert score['rule_coverage'] == 0.8
    assert score['overall'] == 0.94


def test_confidence_score_soft_signals_consistent(monkeypatch):
    trade = make_trade()
    import src.scoring.confidence_scoring as cs_mod
    patch_all_signals(
        monkeypatch,
        cs_mod,
        is_investment_too_aggressive_for_horizon=True,
        is_investment_too_aggressive_for_objective=True
    )

    score = compute_confidence_score(trade)

    assert score['signal_consistency'] == 1.0
    assert score['rule_coverage'] == 0.65
    assert score['overall'] == 0.895


def test_confidence_score_soft_signals_conflicting_reduces_rule_coverage(monkeypatch):
    trade = make_trade()
    import src.scoring.confidence_scoring as cs_mod
    patch_all_signals(
        monkeypatch,
        cs_mod,
        is_investment_too_aggressive_for_horizon=True,
        is_investment_too_aggressive_for_objective=True,
        is_risk_too_low_for_profile=True
    )

    score = compute_confidence_score(trade)

    assert score['signal_consistency'] == 0.667
    assert score['rule_coverage'] == 0.3
    assert score['overall'] == 0.69
