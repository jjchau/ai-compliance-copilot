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
    monkeypatch.setattr(cs_mod, 'is_advisor_history_high_risk', lambda t: False)
    monkeypatch.setattr(cs_mod, 'has_conflicting_signals', lambda t: False)
    score = compute_confidence_score(trade)
    assert 0.9 <= score <= 1.0

def test_confidence_score_kyc_violation(monkeypatch):
    trade = make_trade(kyc_completeness='Missing')
    import src.scoring.confidence_scoring as cs_mod
    monkeypatch.setattr(cs_mod, 'is_kyc_violation', lambda t: True)
    score = compute_confidence_score(trade)
    assert score == 0.3

def test_confidence_score_uncertain(monkeypatch):
    trade = make_trade(kyc_completeness='Uncertain')
    import src.scoring.confidence_scoring as cs_mod
    monkeypatch.setattr(cs_mod, 'is_kyc_violation', lambda t: False)
    monkeypatch.setattr(cs_mod, 'is_kyc_uncertain', lambda t: True)
    monkeypatch.setattr(cs_mod, 'has_conflicting_signals', lambda t: False)
    score = compute_confidence_score(trade)
    assert 0.6 <= score < 0.9

def test_confidence_score_conflicting(monkeypatch):
    trade = make_trade()
    import src.scoring.confidence_scoring as cs_mod
    monkeypatch.setattr(cs_mod, 'is_kyc_violation', lambda t: False)
    monkeypatch.setattr(cs_mod, 'is_kyc_uncertain', lambda t: False)
    monkeypatch.setattr(cs_mod, 'has_conflicting_signals', lambda t: True)
    score = compute_confidence_score(trade)
    assert 0.6 <= score < 0.9

def test_confidence_score_no_rationale(monkeypatch):
    trade = make_trade(has_rationale=False)
    import src.scoring.confidence_scoring as cs_mod
    monkeypatch.setattr(cs_mod, 'is_kyc_violation', lambda t: False)
    monkeypatch.setattr(cs_mod, 'is_kyc_uncertain', lambda t: False)
    monkeypatch.setattr(cs_mod, 'has_conflicting_signals', lambda t: False)
    monkeypatch.setattr(cs_mod, 'is_overexposure', lambda t: False)
    monkeypatch.setattr(cs_mod, 'is_advisor_history_high_risk', lambda t: False)
    monkeypatch.setattr(cs_mod, 'is_suitability_violation', lambda t: False)
    monkeypatch.setattr(cs_mod, 'is_experience_violation', lambda t: False)
    score = compute_confidence_score(trade)
    assert score == 0.9
