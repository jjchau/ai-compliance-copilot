from src.data.schema import Trade
from src.decisioning.decision_engine import evaluate_trade
from src.policy.retrieval import retrieve_policies
from src.decisioning.retrieval_prediction import predict_with_retrieval
from src.decisioning.decision_engine import evaluate_prediction
from src.decisioning.conflict_detection import (
    has_conflicting_signals,
    get_signals
)
from src.orchestration.explanation import generate_explanation

def build_review_case(trade: Trade) -> dict:
    retrieved_policies = retrieve_policies(trade)
    compliance_prediction = predict_with_retrieval(trade, retrieved_policies)
    evaluated_prediction = evaluate_prediction(trade, compliance_prediction)

    return {
        "trade_id": trade.trade_id,
        **trade.model_dump(),
        **evaluated_prediction,
        "retrieved_policies": retrieved_policies,
        "has_conflicting_signals": has_conflicting_signals(trade),
        "conflict_signals": get_signals(trade),
        "flag_reason": generate_explanation(trade, retrieved_policies)
    }