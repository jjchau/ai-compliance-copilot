import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from src.decisioning.policy_rules import should_flag
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


def test_should_flag_kyc_violation(monkeypatch):
    """Test that KYC violation triggers flagging."""
    trade = make_trade()
    import src.decisioning.policy_rules as pr_mod
    monkeypatch.setattr(pr_mod, 'is_kyc_violation', lambda t: True)
    monkeypatch.setattr(pr_mod, 'is_suitability_violation', lambda t: False)
    monkeypatch.setattr(pr_mod, 'is_too_complex_for_experience', lambda t: False)

    result = should_flag(trade, risk_score=50, confidence_score=0.8)
    assert result is True


def test_should_flag_suitability_violation(monkeypatch):
    """Test that suitability violation triggers flagging."""
    trade = make_trade()
    import src.decisioning.policy_rules as pr_mod
    monkeypatch.setattr(pr_mod, 'is_kyc_violation', lambda t: False)
    monkeypatch.setattr(pr_mod, 'is_suitability_violation', lambda t: True)
    monkeypatch.setattr(pr_mod, 'is_too_complex_for_experience', lambda t: False)

    result = should_flag(trade, risk_score=50, confidence_score=0.8)
    assert result is True


def test_should_flag_too_complex_for_experience(monkeypatch):
    """Test that complexity violation triggers flagging."""
    trade = make_trade()
    import src.decisioning.policy_rules as pr_mod
    monkeypatch.setattr(pr_mod, 'is_kyc_violation', lambda t: False)
    monkeypatch.setattr(pr_mod, 'is_suitability_violation', lambda t: False)
    monkeypatch.setattr(pr_mod, 'is_too_complex_for_experience', lambda t: True)

    result = should_flag(trade, risk_score=50, confidence_score=0.8)
    assert result is True


def test_should_flag_high_risk_score(monkeypatch):
    """Test that high risk score (>70) triggers flagging."""
    trade = make_trade()
    import src.decisioning.policy_rules as pr_mod
    monkeypatch.setattr(pr_mod, 'is_kyc_violation', lambda t: False)
    monkeypatch.setattr(pr_mod, 'is_suitability_violation', lambda t: False)
    monkeypatch.setattr(pr_mod, 'is_too_complex_for_experience', lambda t: False)

    result = should_flag(trade, risk_score=75, confidence_score=0.8)
    assert result is True


def test_should_flag_risk_score_boundary_71(monkeypatch):
    """Test that risk score of 71 (just above threshold) triggers flagging."""
    trade = make_trade()
    import src.decisioning.policy_rules as pr_mod
    monkeypatch.setattr(pr_mod, 'is_kyc_violation', lambda t: False)
    monkeypatch.setattr(pr_mod, 'is_suitability_violation', lambda t: False)
    monkeypatch.setattr(pr_mod, 'is_too_complex_for_experience', lambda t: False)

    result = should_flag(trade, risk_score=71, confidence_score=0.8)
    assert result is True


def test_should_flag_risk_score_boundary_70(monkeypatch):
    """Test that risk score of 70 (at threshold) does not trigger flagging alone."""
    trade = make_trade()
    import src.decisioning.policy_rules as pr_mod
    monkeypatch.setattr(pr_mod, 'is_kyc_violation', lambda t: False)
    monkeypatch.setattr(pr_mod, 'is_suitability_violation', lambda t: False)
    monkeypatch.setattr(pr_mod, 'is_too_complex_for_experience', lambda t: False)

    result = should_flag(trade, risk_score=70, confidence_score=0.8)
    assert result is False


def test_should_flag_low_confidence_score(monkeypatch):
    """Test that low confidence score (<0.6) triggers flagging."""
    trade = make_trade()
    import src.decisioning.policy_rules as pr_mod
    monkeypatch.setattr(pr_mod, 'is_kyc_violation', lambda t: False)
    monkeypatch.setattr(pr_mod, 'is_suitability_violation', lambda t: False)
    monkeypatch.setattr(pr_mod, 'is_too_complex_for_experience', lambda t: False)

    result = should_flag(trade, risk_score=50, confidence_score=0.5)
    assert result is True


def test_should_flag_confidence_boundary_0_59(monkeypatch):
    """Test that confidence score of 0.59 (just below threshold) triggers flagging."""
    trade = make_trade()
    import src.decisioning.policy_rules as pr_mod
    monkeypatch.setattr(pr_mod, 'is_kyc_violation', lambda t: False)
    monkeypatch.setattr(pr_mod, 'is_suitability_violation', lambda t: False)
    monkeypatch.setattr(pr_mod, 'is_too_complex_for_experience', lambda t: False)

    result = should_flag(trade, risk_score=50, confidence_score=0.59)
    assert result is True


def test_should_flag_confidence_boundary_0_6(monkeypatch):
    """Test that confidence score of 0.6 (at threshold) does not trigger flagging alone."""
    trade = make_trade()
    import src.decisioning.policy_rules as pr_mod
    monkeypatch.setattr(pr_mod, 'is_kyc_violation', lambda t: False)
    monkeypatch.setattr(pr_mod, 'is_suitability_violation', lambda t: False)
    monkeypatch.setattr(pr_mod, 'is_too_complex_for_experience', lambda t: False)

    result = should_flag(trade, risk_score=50, confidence_score=0.6)
    assert result is False


def test_should_flag_all_conditions_false(monkeypatch):
    """Test that all conditions false returns False."""
    trade = make_trade()
    import src.decisioning.policy_rules as pr_mod
    monkeypatch.setattr(pr_mod, 'is_kyc_violation', lambda t: False)
    monkeypatch.setattr(pr_mod, 'is_suitability_violation', lambda t: False)
    monkeypatch.setattr(pr_mod, 'is_too_complex_for_experience', lambda t: False)

    result = should_flag(trade, risk_score=50, confidence_score=0.8)
    assert result is False


def test_should_flag_multiple_violations(monkeypatch):
    """Test that multiple violations all trigger flagging (returns True on first match)."""
    trade = make_trade()
    import src.decisioning.policy_rules as pr_mod
    monkeypatch.setattr(pr_mod, 'is_kyc_violation', lambda t: True)
    monkeypatch.setattr(pr_mod, 'is_suitability_violation', lambda t: True)
    monkeypatch.setattr(pr_mod, 'is_too_complex_for_experience', lambda t: True)

    result = should_flag(trade, risk_score=80, confidence_score=0.3)
    assert result is True


def test_should_flag_kyc_takes_precedence(monkeypatch):
    """Test that KYC violation is checked first."""
    trade = make_trade()
    import src.decisioning.policy_rules as pr_mod
    monkeypatch.setattr(pr_mod, 'is_kyc_violation', lambda t: True)
    # Other conditions not mocked but KYC should trigger immediately

    result = should_flag(trade, risk_score=50, confidence_score=0.8)
    assert result is True


def test_should_flag_with_zero_risk_score(monkeypatch):
    """Test flagging with zero risk score."""
    trade = make_trade()
    import src.decisioning.policy_rules as pr_mod
    monkeypatch.setattr(pr_mod, 'is_kyc_violation', lambda t: False)
    monkeypatch.setattr(pr_mod, 'is_suitability_violation', lambda t: False)
    monkeypatch.setattr(pr_mod, 'is_too_complex_for_experience', lambda t: False)

    result = should_flag(trade, risk_score=0, confidence_score=0.8)
    assert result is False


def test_should_flag_with_max_risk_score(monkeypatch):
    """Test flagging with maximum risk score (100)."""
    trade = make_trade()
    import src.decisioning.policy_rules as pr_mod
    monkeypatch.setattr(pr_mod, 'is_kyc_violation', lambda t: False)
    monkeypatch.setattr(pr_mod, 'is_suitability_violation', lambda t: False)
    monkeypatch.setattr(pr_mod, 'is_too_complex_for_experience', lambda t: False)

    result = should_flag(trade, risk_score=100, confidence_score=0.8)
    assert result is True


def test_should_flag_with_zero_confidence(monkeypatch):
    """Test flagging with zero confidence score."""
    trade = make_trade()
    import src.decisioning.policy_rules as pr_mod
    monkeypatch.setattr(pr_mod, 'is_kyc_violation', lambda t: False)
    monkeypatch.setattr(pr_mod, 'is_suitability_violation', lambda t: False)
    monkeypatch.setattr(pr_mod, 'is_too_complex_for_experience', lambda t: False)

    result = should_flag(trade, risk_score=50, confidence_score=0.0)
    assert result is True


def test_should_flag_with_max_confidence(monkeypatch):
    """Test flagging with maximum confidence score (1.0)."""
    trade = make_trade()
    import src.decisioning.policy_rules as pr_mod
    monkeypatch.setattr(pr_mod, 'is_kyc_violation', lambda t: False)
    monkeypatch.setattr(pr_mod, 'is_suitability_violation', lambda t: False)
    monkeypatch.setattr(pr_mod, 'is_too_complex_for_experience', lambda t: False)

    result = should_flag(trade, risk_score=50, confidence_score=1.0)
    assert result is False


def test_should_flag_combined_high_risk_low_confidence(monkeypatch):
    """Test combined condition: high risk and low confidence both trigger flagging."""
    trade = make_trade()
    import src.decisioning.policy_rules as pr_mod
    monkeypatch.setattr(pr_mod, 'is_kyc_violation', lambda t: False)
    monkeypatch.setattr(pr_mod, 'is_suitability_violation', lambda t: False)
    monkeypatch.setattr(pr_mod, 'is_too_complex_for_experience', lambda t: False)

    # High risk alone triggers
    result = should_flag(trade, risk_score=75, confidence_score=0.8)
    assert result is True

    # Low confidence alone triggers
    result = should_flag(trade, risk_score=50, confidence_score=0.5)
    assert result is True


def test_should_flag_midrange_values(monkeypatch):
    """Test with mid-range values that should not trigger flagging."""
    trade = make_trade()
    import src.decisioning.policy_rules as pr_mod
    monkeypatch.setattr(pr_mod, 'is_kyc_violation', lambda t: False)
    monkeypatch.setattr(pr_mod, 'is_suitability_violation', lambda t: False)
    monkeypatch.setattr(pr_mod, 'is_too_complex_for_experience', lambda t: False)

    result = should_flag(trade, risk_score=35, confidence_score=0.75)
    assert result is False