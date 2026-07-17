import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from src.decisioning.policy_rules import assess_escalation
from src.data.schema import Trade
from src.decisioning.schema import (
    ComplianceEvidenceSchema,
    ConcernSignalType,
    EvidenceQualityType,
    ViolationType,
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


def test_assess_escalation_low_compliance_high_risk_urgent(monkeypatch):
    """Test that low compliance + high risk escalates to urgent."""
    trade = make_trade()
    ev = ComplianceEvidenceSchema()

    result = assess_escalation(trade, compliance_probability=0.2, evidence=ev, risk_score=70, confidence_score=0.8)
    assert result == "urgent"


def test_assess_escalation_high_risk_score_priority(monkeypatch):
    """Test that high risk score (>= 75) escalates to priority."""
    trade = make_trade()
    ev = ComplianceEvidenceSchema()

    result = assess_escalation(trade, compliance_probability=0.9, evidence=ev, risk_score=75, confidence_score=0.8)
    assert result == "priority"


def test_assess_escalation_low_compliance_queue(monkeypatch):
    """Test that low compliance with moderate risk routes to queue."""
    trade = make_trade()
    ev = ComplianceEvidenceSchema()

    result = assess_escalation(trade, compliance_probability=0.4, evidence=ev, risk_score=50, confidence_score=0.8)
    assert result == "priority"


def test_assess_escalation_low_confidence_queue(monkeypatch):
    """Test that low confidence (< 0.6) escalates to queue."""
    trade = make_trade()
    ev = ComplianceEvidenceSchema()

    result = assess_escalation(trade, compliance_probability=0.9, evidence=ev, risk_score=50, confidence_score=0.5)
    assert result == "priority"


def test_assess_escalation_conflicting_signals_queue(monkeypatch):
    """Test that conflicting signals escalate to queue."""
    trade = make_trade()
    ev = ComplianceEvidenceSchema(
        concern_signals=[
            ConcernSignalType.AGGRESSIVE_FOR_SHORT_HORIZON,
            ConcernSignalType.TOO_CONSERVATIVE_FOR_HORIZON,
        ]
    )

    result = assess_escalation(trade, compliance_probability=0.9, evidence=ev, risk_score=50, confidence_score=0.8)
    assert result == "priority"


def test_assess_escalation_all_clear_none(monkeypatch):
    """Test that all clear conditions return none."""
    trade = make_trade()
    ev = ComplianceEvidenceSchema()

    result = assess_escalation(trade, compliance_probability=0.9, evidence=ev, risk_score=20, confidence_score=0.8)
    assert result == "none"


def test_assess_escalation_boundary_risk_score_74(monkeypatch):
    """Test that risk score of 74 returns priority under current rules."""
    trade = make_trade()
    ev = ComplianceEvidenceSchema()

    result = assess_escalation(trade, compliance_probability=0.9, evidence=ev, risk_score=74, confidence_score=0.8)
    assert result == "priority"


def test_assess_escalation_boundary_risk_score_75(monkeypatch):
    """Test that risk score of 75 (at priority threshold) returns priority."""
    trade = make_trade()
    ev = ComplianceEvidenceSchema()

    result = assess_escalation(trade, compliance_probability=0.9, evidence=ev, risk_score=75, confidence_score=0.8)
    assert result == "priority"


def test_assess_escalation_boundary_compliance_0_3(monkeypatch):
    """Test that compliance of 0.3 with high risk does not trigger urgent."""
    trade = make_trade()
    ev = ComplianceEvidenceSchema()

    result = assess_escalation(trade, compliance_probability=0.3, evidence=ev, risk_score=70, confidence_score=0.8)
    assert result == "priority"


def test_assess_escalation_boundary_compliance_0_29(monkeypatch):
    """Test that compliance < 0.3 with high risk triggers urgent."""
    trade = make_trade()
    ev = ComplianceEvidenceSchema()

    result = assess_escalation(trade, compliance_probability=0.29, evidence=ev, risk_score=70, confidence_score=0.8)
    assert result == "urgent"


def test_assess_escalation_boundary_compliance_0_5(monkeypatch):
    """Test that compliance of 0.5 does not force a special escalation when risk is low."""
    trade = make_trade()
    ev = ComplianceEvidenceSchema()

    result = assess_escalation(trade, compliance_probability=0.5, evidence=ev, risk_score=20, confidence_score=0.8)
    assert result == "none"


def test_assess_escalation_boundary_compliance_0_49(monkeypatch):
    """Test that compliance < 0.5 with low risk routes to queue."""
    trade = make_trade()
    ev = ComplianceEvidenceSchema()

    result = assess_escalation(trade, compliance_probability=0.49, evidence=ev, risk_score=20, confidence_score=0.8)
    assert result == "queue"


def test_assess_escalation_boundary_confidence_0_6(monkeypatch):
    """Test that confidence of 0.6 does not trigger queue when risk is low."""
    trade = make_trade()
    ev = ComplianceEvidenceSchema()

    result = assess_escalation(trade, compliance_probability=0.9, evidence=ev, risk_score=20, confidence_score=0.6)
    assert result == "none"


def test_assess_escalation_boundary_confidence_0_59(monkeypatch):
    """Test that confidence < 0.6 triggers queue."""
    trade = make_trade()
    ev = ComplianceEvidenceSchema()

    result = assess_escalation(trade, compliance_probability=0.9, evidence=ev, risk_score=20, confidence_score=0.59)
    assert result == "none"


def test_assess_escalation_zero_values(monkeypatch):
    """Test with zero values routes to queue because of low compliance."""
    trade = make_trade()
    ev = ComplianceEvidenceSchema()

    result = assess_escalation(trade, compliance_probability=0.0, evidence=ev, risk_score=0, confidence_score=0.0)
    assert result == "queue"


def test_assess_escalation_max_values(monkeypatch):
    """Test with maximum values returns urgent due to critical risk."""
    trade = make_trade()
    ev = ComplianceEvidenceSchema()

    result = assess_escalation(trade, compliance_probability=1.0, evidence=ev, risk_score=100, confidence_score=1.0)
    assert result == "urgent"


def test_assess_escalation_conflicting_signals_routes_queue(monkeypatch):
    """Test that conflicting signals route to queue."""
    trade = make_trade()
    ev = ComplianceEvidenceSchema(
        concern_signals=[
            ConcernSignalType.AGGRESSIVE_FOR_SHORT_HORIZON,
            ConcernSignalType.TOO_CONSERVATIVE_FOR_HORIZON,
        ]
    )

    result = assess_escalation(trade, compliance_probability=0.4, evidence=ev, risk_score=50, confidence_score=0.8)
    assert result == "priority"


def test_assess_escalation_compound_hard_violations_with_context_is_urgent():
    trade = make_trade()
    ev = ComplianceEvidenceSchema(
        violations=[
            ViolationType.KYC_MISSING,
            ViolationType.EXPERIENCE_COMPLEXITY_MISMATCH,
        ],
        concern_signals=[ConcernSignalType.OVEREXPOSURE],
    )

    result = assess_escalation(
        trade,
        compliance_probability=0.2,
        evidence=ev,
        risk_score=30,
        confidence_score=0.9,
    )

    assert result == "urgent"


def test_assess_escalation_senior_client_context_priority_only_with_material_risk():
    trade = make_trade()
    senior_only = ComplianceEvidenceSchema(
        concern_signals=[ConcernSignalType.SENIOR_CLIENT_RISK]
    )
    senior_with_risk = ComplianceEvidenceSchema(
        concern_signals=[
            ConcernSignalType.SENIOR_CLIENT_RISK,
            ConcernSignalType.AGGRESSIVE_FOR_OBJECTIVE,
        ]
    )

    assert assess_escalation(trade, 0.9, senior_only, 10, 0.9) == "none"
    assert assess_escalation(trade, 0.9, senior_with_risk, 10, 0.9) == "priority"


def test_assess_escalation_evidence_quality_and_weak_documentation_queue_rules():
    trade = make_trade()
    uncertain = ComplianceEvidenceSchema(
        evidence_quality=[EvidenceQualityType.KYC_UNCERTAIN]
    )
    weak_only = ComplianceEvidenceSchema(
        evidence_quality=[EvidenceQualityType.WEAK_RATIONALE]
    )
    weak_with_context = ComplianceEvidenceSchema(
        concern_signals=[ConcernSignalType.HIGH_RISK_ADVISOR],
        evidence_quality=[EvidenceQualityType.MISSING_RATIONALE],
    )
    soft_low_confidence = ComplianceEvidenceSchema(
        concern_signals=[ConcernSignalType.TOO_CONSERVATIVE_FOR_HORIZON]
    )

    assert assess_escalation(trade, 0.9, uncertain, 0, 0.9) == "queue"
    assert assess_escalation(trade, 0.9, weak_only, 0, 0.9) == "none"
    assert assess_escalation(trade, 0.9, weak_with_context, 0, 0.9) == "queue"
    assert assess_escalation(trade, 0.9, soft_low_confidence, 0, 0.59) == "queue"
