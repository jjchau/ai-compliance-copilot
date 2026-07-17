import os
import sys
from unittest.mock import Mock, patch

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.data.schema import Trade
from src.decisioning.schema import (
    ComplianceEvidenceSchema,
    EvidenceQualityType,
    ViolationType,
)
from src.orchestration.review_pipeline import (
    MAX_DISTANCE,
    build_llm_chunks,
    build_reasoning_output,
    build_retrieval_context,
    build_review_case,
    normalize_evidence_with_structured_facts,
    select_llm_retrieval_chunks,
)


def make_trade(**kwargs):
    base = dict(
        trade_id="TEST-123",
        client_age=35,
        client_income=75000,
        risk_tolerance="Medium",
        investment_experience="Intermediate",
        investment_objective="Growth",
        investment_time_horizon="Medium",
        investment_type="Stocks",
        investment_amount=10000.0,
        advisor_id="A123",
        advisor_experience="Mid",
        advisor_history_risk="Low",
        advisor_rationale="Advisor rationale provided.",
        advisor_notes="Advisor notes provided.",
        kyc_completeness="Complete",
    )
    base.update(kwargs)
    return Trade(**base)


def make_evidence(**kwargs):
    return ComplianceEvidenceSchema(
        violations=kwargs.get("violations", []),
        concern_signals=kwargs.get("concern_signals", []),
        mitigating_factors=kwargs.get("mitigating_factors", []),
        evidence_quality=kwargs.get("evidence_quality", []),
        audit_reasoning=kwargs.get("audit_reasoning", "Evidence-based audit reasoning."),
    )


def test_build_llm_chunks_extracts_text_fields():
    chunks = [
        {"text": "KYC policy text", "policy_id": "POL-002-KYC"},
        {"text": "Suitability policy text", "policy_id": "POL-001-SUITABILITY"},
    ]

    assert build_llm_chunks(chunks) == ["KYC policy text", "Suitability policy text"]


def test_build_llm_chunks_rejects_empty_policy_text():
    with pytest.raises(ValueError, match="empty policy text"):
        build_llm_chunks([{"text": "   ", "policy_id": "POL-001"}])


def test_normalize_evidence_adds_kyc_missing_violation():
    trade = make_trade(kyc_completeness="Missing")
    evidence = make_evidence()

    normalized = normalize_evidence_with_structured_facts(trade, evidence)

    assert ViolationType.KYC_MISSING in normalized.violations


def test_normalize_evidence_adds_kyc_uncertain_quality_signal():
    trade = make_trade(kyc_completeness="Uncertain")
    evidence = make_evidence()

    normalized = normalize_evidence_with_structured_facts(trade, evidence)

    assert EvidenceQualityType.KYC_UNCERTAIN in normalized.evidence_quality


@patch("src.orchestration.review_pipeline.retriever")
def test_build_retrieval_context_filters_policy_ids_by_distance(mock_retriever):
    trade = make_trade()
    mock_retriever.retrieve_policy_evidence.return_value = [
        {
            "chunk_id": "POL-002-KYC::1",
            "policy_id": "POL-002-KYC",
            "similarity_distance": MAX_DISTANCE,
            "section_scope": "KYC",
            "text": "KYC policy text",
        },
        {
            "chunk_id": "POL-001-SUITABILITY::1",
            "policy_id": "POL-001-SUITABILITY",
            "similarity_distance": MAX_DISTANCE + 0.01,
            "section_scope": "Suitability",
            "text": "Suitability policy text",
        },
        {
            "chunk_id": "POL-002-KYC::2",
            "policy_id": "POL-002-KYC",
            "similarity_distance": 0.2,
            "section_scope": "KYC duplicate",
            "text": "More KYC text",
        },
    ]

    result = build_retrieval_context(trade)

    mock_retriever.retrieve_policy_evidence.assert_called_once()
    assert [chunk["rank"] for chunk in result["raw_chunks"]] == [1, 2, 3]
    assert result["retrieved_chunks"] == [
        {
            **mock_retriever.retrieve_policy_evidence.return_value[0],
            "rank": 1,
        }
    ]
    assert result["retrieved_policies"] == ["POL-002-KYC"]
    assert result["retrieval_configuration"]["semantic_top_k"] == 10
    assert result["retrieval_configuration"]["max_distance"] == MAX_DISTANCE
    assert "Client age: 35" in result["query_context"]
    assert "KYC status: Complete" in result["query_context"]


def test_select_llm_retrieval_chunks_rejects_missing_chunk_id():
    with pytest.raises(ValueError, match="has no chunk_id"):
        select_llm_retrieval_chunks(
            [
                {
                    "policy_id": "POL-002-KYC",
                    "similarity_distance": 0.1,
                    "text": "KYC policy text",
                }
            ]
        )


def test_select_llm_retrieval_chunks_validation_and_max_chunk_limit():
    valid = {
        "chunk_id": "chunk-1",
        "policy_id": "POL-001",
        "similarity_distance": "0.1",
        "text": "Policy text",
    }

    with pytest.raises(ValueError, match="max_chunks"):
        select_llm_retrieval_chunks([valid], max_chunks=0)

    with pytest.raises(ValueError, match="has no policy_id"):
        select_llm_retrieval_chunks([{**valid, "policy_id": ""}])

    with pytest.raises(ValueError, match="empty policy text"):
        select_llm_retrieval_chunks([{**valid, "text": ""}])

    with pytest.raises(ValueError, match="has no similarity_distance"):
        select_llm_retrieval_chunks([{**valid, "similarity_distance": None}])

    with pytest.raises(ValueError, match="invalid .*similarity_distance"):
        select_llm_retrieval_chunks([{**valid, "similarity_distance": "far"}])

    selected = select_llm_retrieval_chunks(
        [
            valid,
            {
                "chunk_id": "chunk-2",
                "policy_id": "POL-002",
                "similarity_distance": 0.2,
                "text": "Second policy text",
            },
        ],
        max_chunks=1,
    )
    assert selected == [{**valid, "rank": 1, "similarity_distance": 0.1}]


@patch("src.orchestration.review_pipeline.retriever", None)
def test_build_retrieval_context_handles_missing_retriever():
    result = build_retrieval_context(make_trade())

    assert result["retrieved_policies"] == []
    assert result["retrieved_chunks"] == []
    assert result["raw_chunks"] == []
    assert result["retrieval_configuration"]["max_llm_chunks"] == 5
    assert result["query_context"]


@patch("src.orchestration.review_pipeline.retriever")
def test_build_retrieval_context_handles_retrieval_exception(mock_retriever, capsys):
    mock_retriever.retrieve_policy_evidence.side_effect = RuntimeError("boom")

    result = build_retrieval_context(make_trade())

    assert result["raw_chunks"] == []
    assert result["retrieved_chunks"] == []
    assert "Retrieval exception" in capsys.readouterr().out


@patch("src.orchestration.review_pipeline.evaluate_evidence")
@patch("src.orchestration.review_pipeline.compute_compliance_probability")
@patch("src.orchestration.review_pipeline.gemini_engine")
def test_build_reasoning_output_uses_gemini_evidence_and_scores(
    mock_gemini_engine,
    mock_compute_compliance,
    mock_evaluate_evidence,
):
    trade = make_trade()
    retrieved_policies = ["POL-002-KYC"]
    retrieved_chunks = [
        {
            "chunk_id": "POL-002-KYC::1",
            "policy_id": "POL-002-KYC",
            "similarity_distance": 0.4,
            "section_scope": "KYC",
            "text": "KYC policy text",
        }
    ]
    mock_gemini_engine.evaluate_with_llm.return_value = {
        "violations": [],
        "concern_signals": [],
        "mitigating_factors": [],
        "evidence_quality": [],
        "audit_reasoning": "The case is supported by retrieved policy evidence.",
    }
    mock_compute_compliance.return_value = {
        "compliance_probability": 0.92,
        "compliance_label": True,
    }
    mock_evaluate_evidence.return_value = {
        "risk_score": 10,
        "confidence_score": 0.86,
        "confidence_breakdown": {"overall": 0.86},
        "escalation_level": "none",
        "priority_score": 0.0,
    }

    evidence, payload = build_reasoning_output(trade, retrieved_policies, retrieved_chunks)

    mock_gemini_engine.evaluate_with_llm.assert_called_once_with(
        trade,
        ["KYC policy text"],
    )
    mock_compute_compliance.assert_called_once_with(evidence)
    mock_evaluate_evidence.assert_called_once_with(
        trade,
        {"compliance_probability": 0.92, "compliance_label": True},
        evidence,
    )
    assert isinstance(evidence, ComplianceEvidenceSchema)
    assert payload["compliance_probability"] == 0.92
    assert payload["compliance_label"] is True
    assert payload["risk_score"] == 10
    assert payload["confidence_score"] == 0.86
    assert payload["flag_reasons"] == "The case is supported by retrieved policy evidence."
    assert payload["retrieved_policies"] == retrieved_policies
    assert payload["retrieved_chunks"] == retrieved_chunks
    assert payload["evidence"] == evidence.model_dump(mode="json")


@patch("src.orchestration.review_pipeline.log_ai_decision")
@patch("src.orchestration.review_pipeline.log_retrieval_context")
@patch("src.orchestration.review_pipeline.get_signals")
@patch("src.orchestration.review_pipeline.has_conflicting_signals")
@patch("src.orchestration.review_pipeline.build_reasoning_output")
@patch("src.orchestration.review_pipeline.build_retrieval_context")
def test_build_review_case_returns_current_payload_shape(
    mock_build_retrieval_context,
    mock_build_reasoning_output,
    mock_has_conflicting_signals,
    mock_get_signals,
    mock_log_retrieval_context,
    mock_log_ai_decision,
):
    trade = make_trade()
    evidence = make_evidence(audit_reasoning="Current audit reasoning.")
    retrieved_chunks = [
        {
            "chunk_id": "POL-002-KYC::1",
            "policy_id": "POL-002-KYC",
            "similarity_distance": 0.4,
            "section_scope": "KYC",
            "text": "KYC policy text",
        }
    ]
    retrieval_configuration = {
        "semantic_top_k": 10,
        "max_distance": MAX_DISTANCE,
        "deduplication_unit": "policy_id",
        "deduplication_strategy": "highest_ranked_eligible_chunk_per_policy",
        "max_llm_chunks": 5,
    }
    reasoning_payload = {
        "compliance_probability": 0.91,
        "compliance_label": True,
        "risk_score": 12,
        "confidence_score": 0.88,
        "confidence_breakdown": {"overall": 0.88},
        "escalation_level": "none",
        "priority_score": 0.0,
        "evidence": evidence.model_dump(mode="json"),
        "flag_reasons": "Current audit reasoning.",
        "retrieved_policies": ["POL-002-KYC"],
        "retrieved_chunks": retrieved_chunks,
    }
    mock_build_retrieval_context.return_value = {
        "query_context": "query",
        "raw_chunks": retrieved_chunks,
        "retrieved_policies": ["POL-002-KYC"],
        "retrieved_chunks": retrieved_chunks,
        "retrieval_configuration": retrieval_configuration,
    }
    mock_build_reasoning_output.return_value = (evidence, reasoning_payload)
    mock_has_conflicting_signals.return_value = False
    mock_get_signals.return_value = []

    result = build_review_case(trade)

    mock_build_retrieval_context.assert_called_once_with(trade)
    mock_build_reasoning_output.assert_called_once_with(
        trade,
        ["POL-002-KYC"],
        retrieved_chunks,
    )
    mock_log_retrieval_context.assert_called_once_with(
        trade_id="TEST-123",
        query_context="query",
        raw_chunks=retrieved_chunks,
        selected_chunks=retrieved_chunks,
        logged_retrieved_policies=["POL-002-KYC"],
        retrieval_configuration=retrieval_configuration,
    )
    mock_has_conflicting_signals.assert_called_once_with(trade)
    mock_get_signals.assert_called_once_with(trade)
    mock_log_ai_decision.assert_called_once()

    assert result["trade_id"] == "TEST-123"
    for key, value in trade.model_dump().items():
        assert result[key] == value
    assert result["compliance_probability"] == 0.91
    assert result["compliance_label"] is True
    assert result["risk_score"] == 12
    assert result["confidence_score"] == 0.88
    assert result["escalation_level"] == "none"
    assert result["priority_score"] == 0.0
    assert result["retrieved_policies"] == ["POL-002-KYC"]
    assert result["retrieved_chunks"] == retrieved_chunks
    assert result["flag_reasons"] == "Current audit reasoning."
    assert result["has_conflicting_signals"] is False
    assert result["conflict_signals"] == []


@patch("src.orchestration.review_pipeline.log_ai_decision")
@patch("src.orchestration.review_pipeline.log_retrieval_context")
@patch("src.orchestration.review_pipeline.get_signals")
@patch("src.orchestration.review_pipeline.has_conflicting_signals")
@patch("src.orchestration.review_pipeline.build_reasoning_output")
@patch("src.orchestration.review_pipeline.build_retrieval_context")
def test_build_review_case_preserves_conflict_signals(
    mock_build_retrieval_context,
    mock_build_reasoning_output,
    mock_has_conflicting_signals,
    mock_get_signals,
    mock_log_retrieval_context,
    mock_log_ai_decision,
):
    trade = make_trade(trade_id="CUSTOM-TRADE-123")
    evidence = make_evidence()
    mock_build_retrieval_context.return_value = {
        "query_context": "query",
        "raw_chunks": [],
        "retrieved_policies": [],
        "retrieved_chunks": [],
        "retrieval_configuration": {"max_llm_chunks": 5},
    }
    mock_build_reasoning_output.return_value = (
        evidence,
        {
            "compliance_probability": 0.5,
            "compliance_label": False,
            "risk_score": 55,
            "confidence_score": 0.61,
            "confidence_breakdown": {"overall": 0.61},
            "escalation_level": "priority",
            "priority_score": 72.0,
            "evidence": evidence.model_dump(mode="json"),
            "flag_reasons": "Review is required.",
            "retrieved_policies": [],
            "retrieved_chunks": [],
        },
    )
    mock_has_conflicting_signals.return_value = True
    mock_get_signals.return_value = ["risk_too_high", "too_conservative"]

    result = build_review_case(trade)

    assert result["trade_id"] == "CUSTOM-TRADE-123"
    assert result["has_conflicting_signals"] is True
    assert result["conflict_signals"] == ["risk_too_high", "too_conservative"]
    mock_log_retrieval_context.assert_called_once()
    mock_log_ai_decision.assert_called_once()


class TestBuildReviewCase:
    """Compatibility node IDs for VS Code test discovery caches."""

    def test_build_review_case_structure(self):
        test_build_review_case_returns_current_payload_shape()

    def test_build_review_case_calls_all_components(self):
        test_build_review_case_returns_current_payload_shape()

    def test_build_review_case_with_conflicting_signals(self):
        test_build_review_case_preserves_conflict_signals()

    def test_build_review_case_preserves_trade_id(self):
        test_build_review_case_preserves_conflict_signals()
