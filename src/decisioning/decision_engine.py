from src.data.schema import Trade
from src.decisioning.compliance_prediction import predict_compliance
from src.scoring.risk_scoring import compute_risk_score
from src.scoring.confidence_scoring import compute_confidence_score
from src.decisioning.policy_rules import should_flag
from src.decisioning.conflict_detection import (
    has_conflicting_signals,
    get_conflict_signals
)

def evaluate_trade(trade: Trade) -> dict:
    compliance_prediction = predict_compliance(trade)
    risk_score = compute_risk_score(trade)
    confidence_score = compute_confidence_score(trade)
    flag_for_review = should_flag(trade, risk_score, confidence_score)
    has_conflict = has_conflicting_signals(trade)
    conflict_signals = get_conflict_signals(trade)

    return {
        'trade_id': trade.trade_id,
        'compliance_prediction': compliance_prediction,
        'risk_score': risk_score,
        'confidence_score': confidence_score,
        'flag_for_review': flag_for_review,
        'has_conflicting_signals': has_conflict,
        'conflict_signals': conflict_signals
    }