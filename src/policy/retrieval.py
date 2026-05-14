import random
from typing import List

from src.data.schema import Trade
from src.decisioning.conflict_detection import has_conflicting_signals
from src.policy.policy_corpus import POLICY_CORPUS

# Tunable parameters
RETRIEVAL_CONFIG = {
    "recall_rate": 0.8,     # probability of retrieving a relevant policy
    "noise_rate": 0.3,      # probability of adding irrelevant policy
    "max_noise": 2          # max number of noisy policies added
}

ALL_POLICY_IDS = list(POLICY_CORPUS.keys())


def retrieve_policies(trade: Trade) -> List[str]:
    """
    Simulates imperfect retrieval:
    - Misses some relevant policies (false negatives)
    - Adds some irrelevant policies (false positives)
    - Uses partial logic (not full rule coverage)
    """

    retrieved = set()

    # --- PARTIAL SIGNAL MATCHING (not perfect!) ---
    if trade.kyc_completeness == "Missing":
        if random.random() < RETRIEVAL_CONFIG["recall_rate"]:
            retrieved.add("POLICY_KYC_001")

    if trade.kyc_completeness == "Uncertain":
        if random.random() < RETRIEVAL_CONFIG["recall_rate"]:
            retrieved.add("POLICY_KYC_002")

    if has_conflicting_signals(trade):
        if random.random() < RETRIEVAL_CONFIG["recall_rate"]:
            retrieved.add("POLICY_KYC_003")

    if trade.risk_tolerance == "Low":
        if random.random() < RETRIEVAL_CONFIG["recall_rate"]:
            retrieved.add("POLICY_SUIT_001")

    if trade.investment_objective == "Preservation":
        if random.random() < RETRIEVAL_CONFIG["recall_rate"]:
            retrieved.add("POLICY_SUIT_002")

    if trade.investment_time_horizon == "Short":
        if random.random() < RETRIEVAL_CONFIG["recall_rate"]:
            retrieved.add("POLICY_SUIT_003")

    if trade.investment_experience == "Beginner":
        if random.random() < RETRIEVAL_CONFIG["recall_rate"]:
            retrieved.add("POLICY_EXP_001")

    if trade.investment_amount > 0.3 * trade.client_income:
        if random.random() < RETRIEVAL_CONFIG["recall_rate"]:
            retrieved.add("POLICY_RISK_001")

    if not trade.has_rationale:
        if random.random() < RETRIEVAL_CONFIG["recall_rate"]:
            retrieved.add("POLICY_DOC_001")

    if trade.advisor_history_risk == "High":
        if random.random() < RETRIEVAL_CONFIG["recall_rate"]:
            retrieved.add("POLICY_SUP_001")

    # --- NOISE INJECTION (false positives) ---
    if random.random() < RETRIEVAL_CONFIG["noise_rate"]:
        num_noise = random.randint(1, RETRIEVAL_CONFIG["max_noise"])

        noise_candidates = [
            pid for pid in ALL_POLICY_IDS if pid not in retrieved
        ]

        noise = random.sample(noise_candidates, min(num_noise, len(noise_candidates)))
        retrieved.update(noise)
    
    return list(retrieved)