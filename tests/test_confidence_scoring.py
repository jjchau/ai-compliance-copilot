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

def test_confidence_score_high(monkeypatch):
    trade = make_trade()
    import src.scoring.confidence_scoring as cs_mod
    monkeypatch.setattr(cs_mod, 'is_kyc_violation', lambda t: False)
    monkeypatch.setattr(cs_mod, 'is_suitability_violation', lambda t: False)
    monkeypatch.setattr(cs_mod, 'is_experience_violation', lambda t: False)
    monkeypatch.setattr(cs_mod, 'is_kyc_uncertain', lambda t: False)
    monkeypatch.setattr(cs_mod, 'is_overexposure', lambda t: False)
    monkeypatch.setattr(cs_mod, 'is_investment_too_agressive_for_horizon', lambda t: False)
    monkeypatch.setattr(cs_mod, 'is_investment_too_aggressive_for_objective', lambda t: False)
    monkeypatch.setattr(cs_mod, 'is_risk_too_low_for_profile', lambda t: False)
    monkeypatch.setattr(cs_mod, 'is_investment_too_conservative_for_objective', lambda t: False)
    monkeypatch.setattr(cs_mod, 'is_investment_too_conservative_for_horizon', lambda t: False)

    score = compute_confidence_score(trade)

    assert score['overall'] == 0.82
    assert score['data_completeness'] == 1.0
    assert score['signal_consistency'] == 0.7
    assert score['rule_coverage'] == 0.7

def test_confidence_score_kyc_violation(monkeypatch):
    trade = make_trade(kyc_completeness='Missing')
    import src.scoring.confidence_scoring as cs_mod
    monkeypatch.setattr(cs_mod, 'is_kyc_violation', lambda t: True)
    monkeypatch.setattr(cs_mod, 'is_suitability_violation', lambda t: False)
    monkeypatch.setattr(cs_mod, 'is_experience_violation', lambda t: False)
    monkeypatch.setattr(cs_mod, 'is_kyc_uncertain', lambda t: False)
    monkeypatch.setattr(cs_mod, 'is_overexposure', lambda t: False)
    monkeypatch.setattr(cs_mod, 'is_investment_too_agressive_for_horizon', lambda t: False)
    monkeypatch.setattr(cs_mod, 'is_investment_too_aggressive_for_objective', lambda t: False)
    monkeypatch.setattr(cs_mod, 'is_risk_too_low_for_profile', lambda t: False)
    monkeypatch.setattr(cs_mod, 'is_investment_too_conservative_for_objective', lambda t: False)
    monkeypatch.setattr(cs_mod, 'is_investment_too_conservative_for_horizon', lambda t: False)

    score = compute_confidence_score(trade)

    assert score['overall'] == 0.715
    assert score['data_completeness'] == 0.7
    assert score['signal_consistency'] == 0.7
    assert score['rule_coverage'] == 0.75

def test_confidence_score_uncertain(monkeypatch):
    trade = make_trade(kyc_completeness='Uncertain')
    import src.scoring.confidence_scoring as cs_mod
    monkeypatch.setattr(cs_mod, 'is_kyc_violation', lambda t: False)
    monkeypatch.setattr(cs_mod, 'is_kyc_uncertain', lambda t: True)
    monkeypatch.setattr(cs_mod, 'is_suitability_violation', lambda t: False)
    monkeypatch.setattr(cs_mod, 'is_experience_violation', lambda t: False)
    monkeypatch.setattr(cs_mod, 'is_overexposure', lambda t: False)
    monkeypatch.setattr(cs_mod, 'is_investment_too_agressive_for_horizon', lambda t: False)
    monkeypatch.setattr(cs_mod, 'is_investment_too_aggressive_for_objective', lambda t: False)
    monkeypatch.setattr(cs_mod, 'is_risk_too_low_for_profile', lambda t: False)
    monkeypatch.setattr(cs_mod, 'is_investment_too_conservative_for_objective', lambda t: False)
    monkeypatch.setattr(cs_mod, 'is_investment_too_conservative_for_horizon', lambda t: False)

    score = compute_confidence_score(trade)

    assert score['overall'] == 0.68
    assert score['data_completeness'] == 0.8
    assert score['signal_consistency'] == 0.7
    assert score['rule_coverage'] == 0.5

def test_confidence_score_single_negative_signal(monkeypatch):
    trade = make_trade()
    import src.scoring.confidence_scoring as cs_mod
    monkeypatch.setattr(cs_mod, 'is_kyc_violation', lambda t: False)
    monkeypatch.setattr(cs_mod, 'is_kyc_uncertain', lambda t: False)
    monkeypatch.setattr(cs_mod, 'is_suitability_violation', lambda t: True)
    monkeypatch.setattr(cs_mod, 'is_experience_violation', lambda t: False)
    monkeypatch.setattr(cs_mod, 'is_overexposure', lambda t: False)
    monkeypatch.setattr(cs_mod, 'is_investment_too_agressive_for_horizon', lambda t: False)
    monkeypatch.setattr(cs_mod, 'is_investment_too_aggressive_for_objective', lambda t: False)
    monkeypatch.setattr(cs_mod, 'is_risk_too_low_for_profile', lambda t: False)
    monkeypatch.setattr(cs_mod, 'is_investment_too_conservative_for_objective', lambda t: False)
    monkeypatch.setattr(cs_mod, 'is_investment_too_conservative_for_horizon', lambda t: False)

    score = compute_confidence_score(trade)

    assert score['signal_consistency'] == 0.6
    assert score['rule_coverage'] == 0.65
    assert score['overall'] == 0.775

def test_confidence_score_no_rationale(monkeypatch):
    trade = make_trade(has_rationale=False)
    import src.scoring.confidence_scoring as cs_mod
    monkeypatch.setattr(cs_mod, 'is_kyc_violation', lambda t: False)
    monkeypatch.setattr(cs_mod, 'is_kyc_uncertain', lambda t: False)
    monkeypatch.setattr(cs_mod, 'is_suitability_violation', lambda t: False)
    monkeypatch.setattr(cs_mod, 'is_experience_violation', lambda t: False)
    monkeypatch.setattr(cs_mod, 'is_overexposure', lambda t: False)
    monkeypatch.setattr(cs_mod, 'is_investment_too_agressive_for_horizon', lambda t: False)
    monkeypatch.setattr(cs_mod, 'is_investment_too_aggressive_for_objective', lambda t: False)
    monkeypatch.setattr(cs_mod, 'is_risk_too_low_for_profile', lambda t: False)
    monkeypatch.setattr(cs_mod, 'is_investment_too_conservative_for_objective', lambda t: False)
    monkeypatch.setattr(cs_mod, 'is_investment_too_conservative_for_horizon', lambda t: False)

    score = compute_confidence_score(trade)

    assert score['overall'] == 0.78
    assert score['data_completeness'] == 0.9
    assert score['signal_consistency'] == 0.7
    assert score['rule_coverage'] == 0.7
