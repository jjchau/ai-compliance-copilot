from src.data.schema import Trade
from src.policy.retrieval import retrieve_policies
from src.decisioning.retrieval_prediction import predict_with_retrieval
from src.decisioning.decision_engine import evaluate_prediction
from src.decisioning.conflict_detection import (
    has_conflicting_signals,
    get_signals
)
from src.orchestration.explanation import generate_explanation
from src.logging.ai_logger import log_ai_decision
from src.api.models import aiAssessment

# For retrieval-based compliance prediction, consumed by backend API
def build_review_case(trade: Trade) -> dict:
    retrieved_policies = retrieve_policies(trade)
    compliance_prediction = predict_with_retrieval(trade, retrieved_policies)
    evaluated_prediction = evaluate_prediction(trade, compliance_prediction)
    flag_reasons = generate_explanation(trade, retrieved_policies)
    
    log_ai_decision(
        trade,
        aiAssessment(
            retrieved_policies = retrieved_policies,
            compliance_probability = evaluated_prediction["compliance_probability"],
            compliance_label = evaluated_prediction["compliance_label"],
            risk_score = evaluated_prediction["risk_score"],
            confidence_score = evaluated_prediction["confidence_score"],
            escalation_level = evaluated_prediction["escalation_level"],
            priority_score = evaluated_prediction["priority_score"],
            flag_reasons = flag_reasons
        )
    )

    return {
        "trade_id": trade.trade_id,
        **trade.model_dump(),
        **evaluated_prediction,
        "retrieved_policies": retrieved_policies,
        "has_conflicting_signals": has_conflicting_signals(trade),
        "conflict_signals": get_signals(trade),
        "flag_reasons": flag_reasons
    }