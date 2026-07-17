from unittest.mock import patch

from src.api.models import aiAssessment
from src.data.schema import Trade
from src.decisioning.schema import ComplianceEvidenceSchema, ViolationType
from src.logging.ai_logger import log_ai_decision


def test_log_ai_decision_writes_expected_audit_payload():
    trade = Trade(
        trade_id="TRADE-AI",
        client_age=40,
        client_income=100000,
        risk_tolerance="Low",
        investment_experience="Beginner",
        investment_objective="Preservation",
        investment_time_horizon="Short",
        investment_type="Stocks",
        investment_amount=20000,
        advisor_id="ADV-001",
        advisor_experience="Junior",
        advisor_history_risk="Low",
        advisor_rationale="Rationale.",
        advisor_notes="Notes.",
        kyc_completeness="Complete",
    )
    evidence = ComplianceEvidenceSchema(
        violations=[ViolationType.RISK_TOLERANCE_VIOLATION],
        audit_reasoning="Policy-supported rationale.",
    )
    assessment = aiAssessment(
        retrieved_policies=["POL-001-SUITABILITY"],
        compliance_probability=0.42,
        compliance_label=False,
        risk_score=65,
        confidence_score=0.7,
        escalation_level="priority",
        priority_score=80,
        flag_reasons="Needs review.",
    )

    with patch("src.logging.ai_logger.append_jsonl") as mock_append:
        log_ai_decision(trade, evidence, assessment)

    path, payload = mock_append.call_args.args
    assert path.name == "ai_decisions.jsonl"
    assert payload["timestamp"] == trade.trade_timestamp.isoformat()
    assert payload["trade_id"] == "TRADE-AI"
    assert payload["evidence"]["violations"] == ["RISK_TOLERANCE_VIOLATION"]
    assert payload["assessment_reliability"] == 0.7
    assert payload["workflow_routing"] == "priority"
    assert payload["retrieved_policies"] == ["POL-001-SUITABILITY"]
