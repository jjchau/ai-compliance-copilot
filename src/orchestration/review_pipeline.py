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
from src.orchestration.explanation import generate_explanation
from src.policy.retrieval import retrieve_policies
from src.rag.rag import ComplianceRetriever

MAX_DISTANCE = 0.55

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
    Converts vector retrieval objects into plain
    policy text chunks for Gemini.
    """

    return [chunk["text"] for chunk in retrieved_chunks]


def build_retrieval_context(trade: Trade) -> dict:
    """
    Stage 1:
    Retrieval only.
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

    retrieved_chunks = []
    retrieved_policies = set()

    if retriever:
        try:
            retrieved_chunks = retriever.retrieve_policy_evidence(
                query_context,
                top_k=10
            )

            for chunk in retrieved_chunks:

                if (
                    chunk["similarity_distance"] <= MAX_DISTANCE
                    and chunk["policy_id"] not in retrieved_policies
                ):
                    retrieved_policies.add(chunk["policy_id"])

                if len(retrieved_policies) >= 5:
                    break

        except Exception as e:
            print(f"[X] Retrieval exception on trade {trade.trade_id}: {e}")

    return {
        "query_context": query_context,
        "retrieved_policies": list(retrieved_policies),
        "retrieved_chunks": retrieved_chunks
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

    reasoning = build_reasoning_output(
        trade,
        retrieval["retrieved_policies"],
        retrieval["retrieved_chunks"]
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
                reasoning[1]["flag_reasons"]
        )
    )

    return {
        "trade_id": trade.trade_id,
        **trade.model_dump(),
        **reasoning[1],
        "has_conflicting_signals":
            has_conflicting_signals(trade),
        "conflict_signals":
            get_signals(trade)
    }

# # OLD FUNCTION, BUT KEPT ACTIVE FOR NOW FOR DEBUGGING --> NEED TO ASK CHATGPT ABOUT evaluate_with_llm() function
# def build_review_case(trade: Trade) -> dict:
#     """
#     Builds a comprehensive audit case by cross-referencing all 16 CSV metrics 
#     with the Vector DB and Gemini AI engine.
#     """
#     query_context = f"""
#     Client age: {trade.client_age}
#     Client income: {trade.client_income}

#     Risk tolerance: {trade.risk_tolerance}
#     Investment experience: {trade.investment_experience}
#     Investment objective: {trade.investment_objective}
#     Investment horizon: {trade.investment_time_horizon}

#     Investment product: {trade.investment_type}
#     Investment amount: {trade.investment_amount}

#     Advisor history risk: {trade.advisor_history_risk}

#     KYC status: {trade.kyc_completeness}
#     """


#     # Create a rich text overview of trade to give ChromaDB maximum context
#     # query_context = f"""
#     # risk_tolerance={trade.risk_tolerance}
#     # investment_experience={trade.investment_experience}
#     # investment_objective={trade.investment_objective}
#     # time_horizon={trade.investment_time_horizon}

#     # investment_type={trade.investment_type}
#     # investment_amount={trade.investment_amount}

#     # client_age={trade.client_age}
#     # client_income={trade.client_income}

#     # advisor_history_risk={trade.advisor_history_risk}

#     # kyc_status={trade.kyc_completeness}
#     # """


#     # query_context = f"""
#     # [TRANSACTION CONTEXT]
#     # Product: {trade.investment_type} | Amount: ${trade.investment_amount:,}
#     # Client Profile: Age {trade.client_age} | Income: ${trade.client_income:,} | Experience: {trade.investment_experience}
#     # Objectives: Risk Tolerance is {trade.risk_tolerance}, Objective is {trade.investment_objective}, Horizon is {trade.investment_time_horizon}
#     # KYC Status: {trade.kyc_completeness}
    
#     # [ADVISOR INPUTS]
#     # History Risk Level: {trade.advisor_history_risk}
#     # Written Rationale: "{trade.advisor_rationale}"
#     # Internal Notes: "{trade.advisor_notes}"
#     # """

#     retrieved_chunks = []
#     retrieved_policies = set()
    
#     if retriever:
#         try:
#             # Query top 10 closest policies using the comprehensive summary block
#             retrieved_chunks = retriever.retrieve_policy_evidence(query_context, top_k=10)

#             for chunk in retrieved_chunks:
#                 if chunk["similarity_distance"] <= MAX_DISTANCE and chunk["policy_id"] not in retrieved_policies:
#                     retrieved_policies.add(chunk["policy_id"])
#                     print(
#                         chunk["policy_id"],
#                         chunk["section_scope"],
#                         chunk["similarity_distance"]
#                     )    
#                 if len(retrieved_policies) >= 5:
#                     break
    
#         except Exception as e:
#             print(f"[X] RAG exception on trade {trade.trade_id}: {e}")
            
#     # Create policy ID string list for frontend UI badges
#     #retrieved_policies = retrieve_policies(trade)

#     # 2. Native compliance prediction stage from retrieved policies
#     llm_assessment = predict_with_retrieval(trade, list(retrieved_policies))
#     compliance_probability = llm_assessment.get("compliance_probability", 1.0)
#     compliance_label = llm_assessment.get("compliance_label", compliance_probability >= 0.9)

#     flag_reasons = generate_explanation(trade, list(retrieved_policies))

#     # 3. Create a bridge packet to satisfy your scoring calculations in decision_engine.py
#     compliance_prediction = {
#         "compliance_probability": compliance_probability
#     }
#     if "compliance_label" in llm_assessment:
#         compliance_prediction["compliance_label"] = compliance_label
    
#     # Run through risk scoring, confidence scoring, escalation assessment, and prioritization algorithms
#     evaluated_prediction = evaluate_prediction(trade, compliance_prediction)
    
#     compliance_probability = evaluated_prediction.get("compliance_probability", compliance_probability)
#     compliance_label = evaluated_prediction.get("compliance_label", compliance_label)
#     risk_score = evaluated_prediction.get("risk_score", 0)
#     confidence_score = evaluated_prediction.get("confidence_score", 0.0)
#     escalation_level = evaluated_prediction.get("escalation_level", "none")
#     priority_score = evaluated_prediction.get("priority_score", 0)

#     # 4. Write to AI decision logs
#     log_ai_decision(
#         trade,
#         aiAssessment(
#             retrieved_policies = list(retrieved_policies),
#             compliance_probability = compliance_probability,
#             compliance_label = compliance_label,
#             risk_score = risk_score,
#             confidence_score = confidence_score,
#             escalation_level = escalation_level,
#             priority_score = priority_score,
#             flag_reasons = flag_reasons
#         )
#     )

#     # 5. Compile the final case data packet to be sent directly out to FastAPI API endpoints
#     return {
#         "trade_id": trade.trade_id,
#         **trade.model_dump(),
#         **evaluated_prediction,
#         "retrieved_policies": list(retrieved_policies),
#         "retrieved_chunks": retrieved_chunks,   # Full textual evidence blocks
#         "has_conflicting_signals": has_conflicting_signals(trade),
#         "conflict_signals": get_signals(trade),
#         "flag_reasons": flag_reasons    # Contains dynamic 2-sentence Gemini reasoning summary
#     }