import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from unittest.mock import patch
from src.scoring.risk_scoring import compute_risk_score
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
        advisor_rationale='Advisor provided rationale.',
        kyc_completeness='Complete',
    )
    base.update(kwargs)
    return Trade(**base)

def test_compute_risk_score_zero():
    """Test that a clean trade gets zero risk score."""
    trade = make_trade()
    ev = ComplianceEvidenceSchema()
    score = compute_risk_score(trade, evidence=ev)
    assert isinstance(score, int)
    assert score == 0

def test_compute_risk_score_kyc_violation():
    """Test KYC violation adds 40 points."""
    trade = make_trade()
    ev = ComplianceEvidenceSchema(violations=[ViolationType.KYC_MISSING])
    score = compute_risk_score(trade, evidence=ev)
    assert score == 40

def test_compute_risk_score_suitability_violation():
    """Test suitability violation adds 40 points."""
    trade = make_trade()
    ev = ComplianceEvidenceSchema(violations=[ViolationType.RISK_TOLERANCE_VIOLATION])
    score = compute_risk_score(trade, evidence=ev)
    assert score == 40

def test_compute_risk_score_experience_violation():
    """Test experience violation adds 30 points."""
    trade = make_trade()
    ev = ComplianceEvidenceSchema(violations=[ViolationType.EXPERIENCE_COMPLEXITY_MISMATCH])
    score = compute_risk_score(trade, evidence=ev)
    assert score == 30

def test_compute_risk_score_overexposure():
    """Test overexposure adds 15 points."""
    trade = make_trade()
    ev = ComplianceEvidenceSchema(concern_signals=[ConcernSignalType.OVEREXPOSURE])
    score = compute_risk_score(trade, evidence=ev)
    assert score == 15

def test_compute_risk_score_advisor_history_high_risk():
    """Test high risk advisor history adds 10 points."""
    trade = make_trade()
    ev = ComplianceEvidenceSchema(concern_signals=[ConcernSignalType.HIGH_RISK_ADVISOR])
    score = compute_risk_score(trade, evidence=ev)
    assert score == 10

def test_compute_risk_score_kyc_uncertain():
    """Test uncertain KYC adds 10 points."""
    trade = make_trade()
    ev = ComplianceEvidenceSchema(evidence_quality=[EvidenceQualityType.KYC_UNCERTAIN])
    score = compute_risk_score(trade, evidence=ev)
    assert score == 10

def test_compute_risk_score_aggressive_for_horizon():
    """Test investment too aggressive for horizon adds 15 points."""
    trade = make_trade()
    ev = ComplianceEvidenceSchema(concern_signals=[ConcernSignalType.AGGRESSIVE_FOR_SHORT_HORIZON])
    score = compute_risk_score(trade, evidence=ev)
    assert score == 15

def test_compute_risk_score_aggressive_for_objective():
    """Test investment too aggressive for objective adds 10 points."""
    trade = make_trade()
    ev = ComplianceEvidenceSchema(concern_signals=[ConcernSignalType.AGGRESSIVE_FOR_OBJECTIVE])
    score = compute_risk_score(trade, evidence=ev)
    assert score == 10

def test_compute_risk_score_risk_too_low():
    """Test risk too low for profile adds 5 points."""
    trade = make_trade()
    ev = ComplianceEvidenceSchema(concern_signals=[ConcernSignalType.TOO_CONSERVATIVE_FOR_RISK_PROFILE])
    score = compute_risk_score(trade, evidence=ev)
    assert score == 5

def test_compute_risk_score_conservative_for_horizon():
    """Test investment too conservative for horizon adds 5 points."""
    trade = make_trade()
    ev = ComplianceEvidenceSchema(concern_signals=[ConcernSignalType.TOO_CONSERVATIVE_FOR_HORIZON])
    score = compute_risk_score(trade, evidence=ev)
    assert score == 5

def test_compute_risk_score_conservative_for_objective():
    """Test investment too conservative for objective adds 5 points."""
    trade = make_trade()
    ev = ComplianceEvidenceSchema(concern_signals=[ConcernSignalType.TOO_CONSERVATIVE_FOR_OBJECTIVE])
    score = compute_risk_score(trade, evidence=ev)
    assert score == 5

def test_compute_risk_score_multiple_violations():
    """Test multiple violations are summed correctly."""
    trade = make_trade()
    ev = ComplianceEvidenceSchema(
        violations=[ViolationType.KYC_MISSING, ViolationType.RISK_TOLERANCE_VIOLATION],
        concern_signals=[ConcernSignalType.OVEREXPOSURE]
    )
    score = compute_risk_score(trade, evidence=ev)
    # 40 (kyc) + 40 (suitability) + 15 (overexposure) = 95
    assert score == 95

def test_compute_risk_score_max_clamp():
    """Test that score is clamped at 100."""
    trade = make_trade()
    ev = ComplianceEvidenceSchema(
        violations=[
            ViolationType.KYC_MISSING,
            ViolationType.RISK_TOLERANCE_VIOLATION,
            ViolationType.EXPERIENCE_COMPLEXITY_MISMATCH,
        ],
        concern_signals=[
            ConcernSignalType.OVEREXPOSURE,
            ConcernSignalType.HIGH_RISK_ADVISOR,
        ]
    )
    score = compute_risk_score(trade, evidence=ev)
    # 40 + 40 + 30 + 15 + 10 = 135, but should be clamped to 100
    assert score == 100

def test_compute_risk_score_regulatory_vs_contextual():
    """Test separation between regulatory and contextual risk."""
    trade = make_trade()
    ev = ComplianceEvidenceSchema(
        violations=[ViolationType.RISK_TOLERANCE_VIOLATION],
        concern_signals=[ConcernSignalType.OVEREXPOSURE],
        evidence_quality=[EvidenceQualityType.KYC_UNCERTAIN]
    )
    score = compute_risk_score(trade, evidence=ev)
    # Regulatory: 40 (suitability)
    # Contextual: 15 (overexposure) + 10 (kyc_uncertain) = 25
    # Total: 65
    assert score == 65

def test_compute_risk_score_all_soft_signals():
    """Test all soft signals combined."""
    trade = make_trade()
    ev = ComplianceEvidenceSchema(
        concern_signals=[
            ConcernSignalType.AGGRESSIVE_FOR_SHORT_HORIZON,
            ConcernSignalType.AGGRESSIVE_FOR_OBJECTIVE,
            ConcernSignalType.TOO_CONSERVATIVE_FOR_RISK_PROFILE,
            ConcernSignalType.TOO_CONSERVATIVE_FOR_HORIZON,
            ConcernSignalType.TOO_CONSERVATIVE_FOR_OBJECTIVE,
        ]
    )
    score = compute_risk_score(trade, evidence=ev)
    # 15 + 10 + 5 + 5 + 5 = 40
    assert score == 40

