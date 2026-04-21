from src.data.schema import Trade
from src.decisioning.violation_rules import (
    is_kyc_violation,
    is_suitability_violation,
    is_experience_violation,
)
from src.decisioning.risk_signals import (
    is_investment_too_agressive_for_horizon,
    is_investment_too_aggressive_for_objective
)
import random

# TODO: Refactor into a config file:
DETECTION_RATES = {
    "kyc": 0.6,
    "horizon_fp": 0.4,
    "objective_fp": 0.3,
    "noise": 0.05
}

def predict_compliance(trade: Trade) -> bool:
    """
    A simple heuristic-based compliance prediction function that combines violation rules and risk signals.
    Returns True if predicted compliant, False if predicted non-compliant.
    In a real implementation, this could be replaced with a more sophisticated machine learning model trained on historical data.
    """
    violation_evidence = []

    # Detect strong violations (but NOT all)
    if is_suitability_violation(trade):
        violation_evidence.append(True)

    if is_experience_violation(trade):
        violation_evidence.append(True)

    # Intentionally MISS KYC sometimes (major FN source)
    if is_kyc_violation(trade):
        if random.random() < DETECTION_RATES["kyc"]:  # only catch 60% of the time
            violation_evidence.append(True)

    # Soft signals → cause false positives
    if is_investment_too_agressive_for_horizon(trade):
        if random.random() < DETECTION_RATES["horizon_fp"]:
            violation_evidence.append(True)

    if is_investment_too_aggressive_for_objective(trade):
        if random.random() < DETECTION_RATES["objective_fp"]:
            violation_evidence.append(True)

    # Small random noise
    if random.random() < DETECTION_RATES["noise"]:
        return False  # random false positive

    return not any(violation_evidence)