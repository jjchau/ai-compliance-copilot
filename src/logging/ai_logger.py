"""
ai_logger.py

AI decision audit logging.

Purpose:
    Logs model predictions, routing decisions,
    and supporting metadata for auditability.

Author: Jason Chau
Date: 2026-05-27
"""

from src.data.schema import Trade
from src.api.models import aiAssessment
from src.logging.logger import append_jsonl
from pathlib import Path
from src.config.paths import LOG_DIR
from src.decisioning.schema import ComplianceEvidenceSchema

# def log_ai_decision(case: dict) -> None:
def log_ai_decision(trade: Trade, evidence: ComplianceEvidenceSchema, ai_assessment: aiAssessment) -> None:
    """
    Logs an AI-generated trade assessment.
    """

    log_entry = {
        "timestamp": trade.trade_timestamp.isoformat(),
        "trade_id": trade.trade_id,
        "evidence": evidence.model_dump(mode="json"),
        "compliance_label": ai_assessment.compliance_label,
        "compliance_probability": ai_assessment.compliance_probability,
        "risk_score": ai_assessment.risk_score,
        "assessment_reliability": ai_assessment.confidence_score,
        "workflow_routing": ai_assessment.escalation_level,
        "priority_score": ai_assessment.priority_score,
        "retrieved_policies": ai_assessment.retrieved_policies,
        "flag_reasons": ai_assessment.flag_reasons
    }

    append_jsonl(
        LOG_DIR / "ai_decisions.jsonl",
        log_entry
    )