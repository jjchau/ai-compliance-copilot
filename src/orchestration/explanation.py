from typing import List
from src.data.schema import Trade
from src.policy.policy_signal_mapping import POLICY_SIGNAL_CHECKS


def generate_explanation(trade: Trade, retrieved_policies: List[str]) -> str:
    explanations = []

    for policy_id in retrieved_policies:
        signal_check = POLICY_SIGNAL_CHECKS.get(policy_id)
        
        if signal_check and signal_check(trade):
            explanations.append(POLICY_EXPLANATIONS.get(policy_id, "Unknown issue"))

    if not explanations:
        return "No significant compliance concerns detected."

    return "; ".join(explanations) + "."
    
POLICY_EXPLANATIONS = {
    "POLICY_KYC_001": "Missing KYC information",

    "POLICY_KYC_002": "Uncertain KYC information",

    "POLICY_SUIT_001": "Investment risk exceeds client risk tolerance",

    "POLICY_SUIT_002": "Investment objective mismatch",

    "POLICY_SUIT_003": "Short investment horizon exposed to high-risk assets",

    "POLICY_EXP_001": "Complex investment exceeds client experience level",

    "POLICY_RISK_001": "Investment amount exceeds concentration threshold",

#    "POLICY_RISK_002": "Leveraged investment without sufficient risk capacity",

    "POLICY_DOC_001": "Missing rationale for trade recommendation",

    "POLICY_SUP_001": "Advisor has high-risk history",

    "POLICY_KYC_003": "Conflicting client profile signals"

#    "POLICY_CLIENT_001": "Client interest not prioritized",

}