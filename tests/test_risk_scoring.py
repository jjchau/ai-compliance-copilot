import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from src.scoring.risk_scoring import compute_risk_score
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

def test_compute_risk_score_low():
    trade = make_trade()
    score = compute_risk_score(trade)
    assert isinstance(score, int)
    assert 0 <= score <= 100

def test_compute_risk_score_high_suitability(monkeypatch):
    trade = make_trade()
    import src.scoring.risk_scoring as rs_mod
    monkeypatch.setattr(rs_mod, 'is_suitability_violation', lambda t: True)
    monkeypatch.setattr(rs_mod, 'is_experience_violation', lambda t: False)
    monkeypatch.setattr(rs_mod, 'is_kyc_violation', lambda t: False)
    monkeypatch.setattr(rs_mod, 'is_investment_too_agressive_for_horizon', lambda t: False)
    monkeypatch.setattr(rs_mod, 'is_investment_too_aggressive_for_objective', lambda t: False)
    monkeypatch.setattr(rs_mod, 'is_overexposure', lambda t: False)
    monkeypatch.setattr(rs_mod, 'is_kyc_uncertain', lambda t: False)
    monkeypatch.setattr(rs_mod, 'is_advisor_history_high_risk', lambda t: False)
    monkeypatch.setattr(rs_mod, 'is_risk_too_low_for_profile', lambda t: False)
    monkeypatch.setattr(rs_mod, 'is_investment_too_conservative_for_horizon', lambda t: False)
    monkeypatch.setattr(rs_mod, 'is_investment_too_conservative_for_objective', lambda t: False)
    score = compute_risk_score(trade)
    assert score >= 40
