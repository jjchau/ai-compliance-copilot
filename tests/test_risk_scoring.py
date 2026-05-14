import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from unittest.mock import patch
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

def test_compute_risk_score_zero():
    """Test that a clean trade gets zero risk score."""
    trade = make_trade()
    score = compute_risk_score(trade)
    assert isinstance(score, int)
    assert score == 0

def test_compute_risk_score_kyc_violation():
    """Test KYC violation adds 40 points."""
    trade = make_trade()
    with patch('src.scoring.risk_scoring.is_kyc_violation', return_value=True):
        score = compute_risk_score(trade)
        assert score == 40

def test_compute_risk_score_suitability_violation():
    """Test suitability violation adds 40 points."""
    trade = make_trade()
    with patch('src.scoring.risk_scoring.is_suitability_violation', return_value=True):
        score = compute_risk_score(trade)
        assert score == 40

def test_compute_risk_score_experience_violation():
    """Test experience violation adds 30 points."""
    trade = make_trade()
    with patch('src.scoring.risk_scoring.is_experience_violation', return_value=True):
        score = compute_risk_score(trade)
        assert score == 30

def test_compute_risk_score_overexposure():
    """Test overexposure adds 15 points."""
    trade = make_trade()
    with patch('src.scoring.risk_scoring.is_overexposure', return_value=True):
        score = compute_risk_score(trade)
        assert score == 15

def test_compute_risk_score_advisor_history_high_risk():
    """Test high risk advisor history adds 10 points."""
    trade = make_trade()
    with patch('src.scoring.risk_scoring.is_advisor_history_high_risk', return_value=True):
        score = compute_risk_score(trade)
        assert score == 10

def test_compute_risk_score_kyc_uncertain():
    """Test uncertain KYC adds 10 points."""
    trade = make_trade()
    with patch('src.scoring.risk_scoring.is_kyc_uncertain', return_value=True):
        score = compute_risk_score(trade)
        assert score == 10

def test_compute_risk_score_aggressive_for_horizon():
    """Test investment too aggressive for horizon adds 15 points."""
    trade = make_trade()
    with patch('src.scoring.risk_scoring.is_investment_too_aggressive_for_horizon', return_value=True):
        score = compute_risk_score(trade)
        assert score == 15

def test_compute_risk_score_aggressive_for_objective():
    """Test investment too aggressive for objective adds 10 points."""
    trade = make_trade()
    with patch('src.scoring.risk_scoring.is_investment_too_aggressive_for_objective', return_value=True):
        score = compute_risk_score(trade)
        assert score == 10

def test_compute_risk_score_risk_too_low():
    """Test risk too low for profile adds 5 points."""
    trade = make_trade()
    with patch('src.scoring.risk_scoring.is_risk_too_low_for_profile', return_value=True):
        score = compute_risk_score(trade)
        assert score == 5

def test_compute_risk_score_conservative_for_horizon():
    """Test investment too conservative for horizon adds 5 points."""
    trade = make_trade()
    with patch('src.scoring.risk_scoring.is_investment_too_conservative_for_horizon', return_value=True):
        score = compute_risk_score(trade)
        assert score == 5

def test_compute_risk_score_conservative_for_objective():
    """Test investment too conservative for objective adds 5 points."""
    trade = make_trade()
    with patch('src.scoring.risk_scoring.is_investment_too_conservative_for_objective', return_value=True):
        score = compute_risk_score(trade)
        assert score == 5

def test_compute_risk_score_multiple_violations():
    """Test multiple violations are summed correctly."""
    trade = make_trade()
    with patch('src.scoring.risk_scoring.is_kyc_violation', return_value=True), \
         patch('src.scoring.risk_scoring.is_suitability_violation', return_value=True), \
         patch('src.scoring.risk_scoring.is_overexposure', return_value=True):
        score = compute_risk_score(trade)
        # 40 (kyc) + 40 (suitability) + 15 (overexposure) = 95
        assert score == 95

def test_compute_risk_score_max_clamp():
    """Test that score is clamped at 100."""
    trade = make_trade()
    with patch('src.scoring.risk_scoring.is_kyc_violation', return_value=True), \
         patch('src.scoring.risk_scoring.is_suitability_violation', return_value=True), \
         patch('src.scoring.risk_scoring.is_experience_violation', return_value=True), \
         patch('src.scoring.risk_scoring.is_overexposure', return_value=True), \
         patch('src.scoring.risk_scoring.is_advisor_history_high_risk', return_value=True):
        score = compute_risk_score(trade)
        # 40 + 40 + 30 + 15 + 10 = 135, but should be clamped to 100
        assert score == 100

def test_compute_risk_score_regulatory_vs_contextual():
    """Test separation between regulatory and contextual risk."""
    trade = make_trade()
    with patch('src.scoring.risk_scoring.is_suitability_violation', return_value=True), \
         patch('src.scoring.risk_scoring.is_overexposure', return_value=True), \
         patch('src.scoring.risk_scoring.is_kyc_uncertain', return_value=True):
        score = compute_risk_score(trade)
        # Regulatory: 40 (suitability)
        # Contextual: 15 (overexposure) + 10 (kyc_uncertain) = 25
        # Total: 65
        assert score == 65

def test_compute_risk_score_all_soft_signals():
    """Test all soft signals combined."""
    trade = make_trade()
    with patch('src.scoring.risk_scoring.is_investment_too_aggressive_for_horizon', return_value=True), \
         patch('src.scoring.risk_scoring.is_investment_too_aggressive_for_objective', return_value=True), \
         patch('src.scoring.risk_scoring.is_risk_too_low_for_profile', return_value=True), \
         patch('src.scoring.risk_scoring.is_investment_too_conservative_for_horizon', return_value=True), \
         patch('src.scoring.risk_scoring.is_investment_too_conservative_for_objective', return_value=True):
        score = compute_risk_score(trade)
        # 15 + 10 + 5 + 5 + 5 = 40
        assert score == 40

