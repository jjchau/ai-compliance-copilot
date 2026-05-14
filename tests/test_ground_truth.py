"""Unit tests for src/policy/ground_truth.py"""

from src.policy.ground_truth import get_relevant_policies
from src.data.schema import Trade


def make_trade(**kwargs):
    """Create a base Trade object for tests."""
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


def test_get_relevant_policies_returns_empty_list_for_normal_trade():
    trade = make_trade()
    result = get_relevant_policies(trade)

    assert isinstance(result, list)
    assert result == []


def test_get_relevant_policies_detects_missing_kyc():
    trade = make_trade(kyc_completeness='Missing')
    result = get_relevant_policies(trade)

    assert 'POLICY_KYC_001' in result
    assert all(isinstance(policy, str) for policy in result)


def test_get_relevant_policies_detects_uncertain_kyc():
    trade = make_trade(kyc_completeness='Uncertain')
    result = get_relevant_policies(trade)

    assert 'POLICY_KYC_002' in result
    assert all(isinstance(policy, str) for policy in result)


def test_get_relevant_policies_detects_missing_rationale():
    trade = make_trade(has_rationale=False)
    result = get_relevant_policies(trade)

    assert 'POLICY_DOC_001' in result


def test_get_relevant_policies_detects_overexposure():
    trade = make_trade(client_income=50000, investment_amount=20000)
    result = get_relevant_policies(trade)

    assert 'POLICY_RISK_001' in result


def test_get_relevant_policies_detects_high_risk_advisor_history():
    trade = make_trade(advisor_history_risk='High')
    result = get_relevant_policies(trade)

    assert 'POLICY_SUP_001' in result


def test_get_relevant_policies_detects_experience_violation():
    trade = make_trade(investment_experience='Beginner', investment_type='Options')
    result = get_relevant_policies(trade)

    assert 'POLICY_EXP_001' in result


def test_get_relevant_policies_detects_suitability_violation():
    trade = make_trade(risk_tolerance='Low', investment_type='Stocks')
    result = get_relevant_policies(trade)

    assert 'POLICY_SUIT_001' in result

