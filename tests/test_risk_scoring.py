import pytest
from src.scoring.risk_scoring import compute_risk_score, assign_risk_tier, detect_conflicts
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
    monkeypatch.setattr(rs_mod, 'is_horizon_mismatch', lambda t: False)
    monkeypatch.setattr(rs_mod, 'is_objective_mismatch', lambda t: False)
    monkeypatch.setattr(rs_mod, 'is_overexposure', lambda t: False)
    monkeypatch.setattr(rs_mod, 'is_kyc_uncertain', lambda t: False)
    score = compute_risk_score(trade)
    assert score >= 40

def test_assign_risk_tier():
    assert assign_risk_tier(0) == 'Low'
    assert assign_risk_tier(7) == 'Medium'
    assert assign_risk_tier(15) == 'High'

def test_detect_conflicts():
    t1 = make_trade(risk_tolerance='Low', investment_type='Stocks')
    t2 = make_trade(risk_tolerance='High', investment_type='Bonds')
    t3 = make_trade(investment_experience='Beginner', investment_type='Options')
    t4 = make_trade(risk_tolerance='Medium', investment_type='ETFs')
    assert detect_conflicts(t1) is True
    assert detect_conflicts(t2) is True
    assert detect_conflicts(t3) is True
    assert detect_conflicts(t4) is False
