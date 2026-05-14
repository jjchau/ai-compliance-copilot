from typing import List
from src.data.schema import Trade
from src.policy.policy_signal_mapping import POLICY_SIGNAL_CHECKS

def get_relevant_policies(trade: Trade) -> List[str]:
    """
    Ground truth mapping:
    Returns all policies that SHOULD apply to this trade.
    Deterministic and aligned with rule logic.
    """

    policies = []

    for policy_id, check_fn in POLICY_SIGNAL_CHECKS.items():
        if check_fn(trade):
            policies.append(policy_id)

    return policies