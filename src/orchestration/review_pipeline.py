"""
src/orchestration/review_pipeline.py

Purpose:
    Orchestration pipeline connecting live local ChromaDB retrieval vectors 
    with native Google Gemini LLM reasoning models.

Usage:
    from src.orchestration.review_pipeline import build_review_case

Author: Jason Chau
Date: 2026-05-31
"""

import os
from typing import Any

from src.data.schema import Trade
from src.decisioning.decision_engine import evaluate_evidence
from src.decisioning.compliance_scoring import compute_compliance_probability
from src.decisioning.conflict_detection import (
    has_conflicting_signals,
    get_signals
)
from src.decisioning.llm_engine import GeminiComplianceEngine
from src.decisioning.schema import *
from src.logging.ai_logger import log_ai_decision
from src.api.models import aiAssessment
from src.rag.rag import ComplianceRetriever
from src.logging.retrieval_logger import log_retrieval_context

RETRIEVAL_TOP_K = 10
MAX_DISTANCE = 0.55
MAX_LLM_CHUNKS = 5

# Initialize singletons at server launch
try:
    retriever = ComplianceRetriever()
    print("[✓] RAG Compliance Vector Database active in pipeline.")
except Exception as e:
    retriever = None
    print(f"[X] RAG Init Error: {e}")

try:
    gemini_engine = GeminiComplianceEngine()
    print("[✓] Gemini LLM Reasoning Engine active in pipeline.")
except Exception as e:
    print(f"[X] Gemini LLM Init Error: {e}")

def normalize_evidence_with_structured_facts(
    trade: Trade,
    evidence: ComplianceEvidenceSchema,
) -> ComplianceEvidenceSchema:
    violations = set(evidence.violations)
    evidence_quality = set(evidence.evidence_quality)

    if trade.kyc_completeness == "Missing":
        violations.add(ViolationType.KYC_MISSING)

    elif trade.kyc_completeness == "Uncertain":
        evidence_quality.add(EvidenceQualityType.KYC_UNCERTAIN)

    evidence.violations = list(violations)
    evidence.evidence_quality = list(evidence_quality)

    return evidence

def build_llm_chunks(retrieved_chunks: list[dict]) -> list[str]:
    """
    Convert the exact selected retrieval chunks into the ordered
    policy-text list passed to Gemini.
    """

    llm_chunks = [
        str(chunk["text"]).strip()
        for chunk in retrieved_chunks
    ]

    if any(not text for text in llm_chunks):
        raise ValueError(
            "The final Gemini retrieval context contains empty policy text."
        )

    return llm_chunks

def select_llm_retrieval_chunks(
    raw_chunks: list[dict[str, Any]],
    *,
    max_distance: float = MAX_DISTANCE,
    max_chunks: int = MAX_LLM_CHUNKS,
) -> list[dict[str, Any]]:
    """
    Select the ordered retrieval context sent to Gemini.

    Selection rules:
    1. Preserve the retriever's original rank order.
    2. Reject chunks above the distance threshold.
    3. Keep only the highest-ranked eligible chunk for each policy.
    4. Stop after `max_chunks` unique policies.

    The input is not mutated.
    """

    if max_chunks < 1:
        raise ValueError("max_chunks must be at least 1.")

    selected_chunks: list[dict[str, Any]] = []
    seen_policy_ids: set[str] = set()

    for fallback_rank, raw_chunk in enumerate(raw_chunks, start=1):
        chunk = dict(raw_chunk)

        policy_id = str(chunk.get("policy_id") or "").strip()
        chunk_id = str(chunk.get("chunk_id") or "").strip()
        text = str(chunk.get("text") or "").strip()
        distance = chunk.get("similarity_distance")

        if not policy_id:
            raise ValueError(
                f"Retrieved chunk at rank {fallback_rank} has no policy_id."
            )

        if not chunk_id:
            raise ValueError(
                f"Retrieved chunk at rank {fallback_rank} has no chunk_id."
            )

        if not text:
            raise ValueError(
                f"Retrieved chunk {chunk_id} has empty policy text."
            )

        if distance is None:
            raise ValueError(
                f"Retrieved chunk {chunk_id} has no similarity_distance."
            )

        try:
            numeric_distance = float(distance)
        except (TypeError, ValueError) as exc:
            raise ValueError(
                f"Retrieved chunk {chunk_id} has an invalid "
                f"similarity_distance: {distance!r}"
            ) from exc

        # Preserve the retriever's original global rank.
        chunk["rank"] = int(chunk.get("rank") or fallback_rank)
        chunk["similarity_distance"] = numeric_distance

        if numeric_distance > max_distance:
            continue

        if policy_id in seen_policy_ids:
            continue

        seen_policy_ids.add(policy_id)
        selected_chunks.append(chunk)

        if len(selected_chunks) >= max_chunks:
            break

    return selected_chunks

def build_retrieval_context(trade: Trade) -> dict:
    """
    Stage 1: retrieval and production LLM-context selection.

    Returns both:
    - raw_chunks: the complete ranked top-k retrieval result;
    - retrieved_chunks: the exact filtered, deduplicated, ordered chunks
      that will be sent to Gemini.
    """

    query_context = f"""
    Client age: {trade.client_age}
    Client income: {trade.client_income}

    Risk tolerance: {trade.risk_tolerance}
    Investment experience: {trade.investment_experience}
    Investment objective: {trade.investment_objective}
    Investment horizon: {trade.investment_time_horizon}

    Investment product: {trade.investment_type}
    Investment amount: {trade.investment_amount}
    Investment amount as percentage of income: X%
    Potential concentration or overexposure if amount is large relative to income.

    Advisor history risk: {trade.advisor_history_risk}

    KYC status: {trade.kyc_completeness}
    """

    raw_chunks: list[dict] = []
    selected_chunks: list[dict] = []

    if retriever is not None:
        try:
            retrieved = retriever.retrieve_policy_evidence(
                query_context,
                top_k=RETRIEVAL_TOP_K,
            )

            # Add explicit global rank without changing retrieval order.
            raw_chunks = [
                {
                    **chunk,
                    "rank": rank,
                }
                for rank, chunk in enumerate(retrieved, start=1)
            ]

            selected_chunks = select_llm_retrieval_chunks(
                raw_chunks,
                max_distance=MAX_DISTANCE,
                max_chunks=MAX_LLM_CHUNKS,
            )

        except Exception as exc:
            print(
                f"[X] Retrieval exception on trade "
                f"{trade.trade_id}: {exc}"
            )

    # A list comprehension preserves selected-chunk order.
    retrieved_policies = [
        chunk["policy_id"]
        for chunk in selected_chunks
    ]

    return {
        "query_context": query_context,

        # Full ranked semantic result for diagnostics.
        "raw_chunks": raw_chunks,

        # Exact final context sent to Gemini.
        "retrieved_chunks": selected_chunks,

        # Exact ordered policies represented in Gemini context.
        "retrieved_policies": retrieved_policies,

        "retrieval_configuration": {
            "semantic_top_k": RETRIEVAL_TOP_K,
            "max_distance": MAX_DISTANCE,
            "deduplication_unit": "policy_id",
            "deduplication_strategy":
                "highest_ranked_eligible_chunk_per_policy",
            "max_llm_chunks": MAX_LLM_CHUNKS,
        },
    }

def build_reasoning_output(
    trade: Trade,
    retrieved_policies: list[str],
    retrieved_chunks: list[dict]
) -> tuple[ComplianceEvidenceSchema, dict]:
    """
    Stage 2:
    Everything AFTER retrieval.
    """

    llm_chunks = build_llm_chunks(retrieved_chunks)

    assert llm_chunks == [chunk["text"] for chunk in retrieved_chunks]

    evidence_dict = gemini_engine.evaluate_with_llm(trade, llm_chunks)
    evidence = ComplianceEvidenceSchema(**evidence_dict)

    evidence = normalize_evidence_with_structured_facts(trade, evidence)

    compliance_prediction = compute_compliance_probability(evidence)

    evaluated_prediction = evaluate_evidence(trade, compliance_prediction, evidence)

    flag_reasons = evidence.audit_reasoning

    return (
        evidence,
            {
                **compliance_prediction,
                **evaluated_prediction,
                "evidence": evidence.model_dump(mode="json"),
                "flag_reasons": flag_reasons,
                "retrieved_policies": retrieved_policies,
                "retrieved_chunks": retrieved_chunks
            }
        )

def build_review_case(trade: Trade) -> dict:
    retrieval = build_retrieval_context(trade)

    # This is the exact final ordered context that Gemini will receive.
    selected_chunks = retrieval["retrieved_chunks"]
    retrieved_policies = retrieval["retrieved_policies"]

    # Log before Gemini so retrieval evidence remains available even if
    # the external model call later fails.
    log_retrieval_context(
        trade_id=trade.trade_id,
        query_context=retrieval["query_context"],
        raw_chunks=retrieval["raw_chunks"],
        selected_chunks=selected_chunks,
        logged_retrieved_policies=retrieved_policies,
        retrieval_configuration=
            retrieval["retrieval_configuration"],
    )

    reasoning = build_reasoning_output(
        trade,
        retrieved_policies,
        selected_chunks,
    )

    log_ai_decision(
        trade,
        reasoning[0],
        aiAssessment(
            retrieved_policies=
                reasoning[1]["retrieved_policies"],

            compliance_probability=
                reasoning[1]["compliance_probability"],

            compliance_label=
                reasoning[1]["compliance_label"],

            risk_score=
                reasoning[1]["risk_score"],

            confidence_score=
                reasoning[1]["confidence_score"],

            escalation_level=
                reasoning[1]["escalation_level"],

            priority_score=
                reasoning[1]["priority_score"],

            flag_reasons=
                reasoning[1]["flag_reasons"],
        ),
    )

    return {
        "trade_id": trade.trade_id,
        **trade.model_dump(),
        **reasoning[1],
        "has_conflicting_signals":
            has_conflicting_signals(trade),
        "conflict_signals":
            get_signals(trade),
    }