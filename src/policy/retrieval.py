import random
from typing import List

from src.policy.policy_corpus import POLICY_CORPUS

# Tunable parameters
RETRIEVAL_CONFIG = {
    "recall_rate": 0.7,     # probability of retrieving a relevant policy
    "noise_rate": 0.3,      # probability of adding irrelevant policy
    "max_noise": 2          # max number of noisy policies added
}

ALL_POLICY_IDS = list(POLICY_CORPUS.keys())


def retrieve_policies(trade) -> List[str]:
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

    if trade.risk_tolerance == "Low":
        if random.random() < RETRIEVAL_CONFIG["recall_rate"]:
            retrieved.add("POLICY_SUIT_001")

    if trade.investment_time_horizon == "Short":
        if random.random() < RETRIEVAL_CONFIG["recall_rate"]:
            retrieved.add("POLICY_SUIT_003")

    if not trade.has_rationale:
        if random.random() < RETRIEVAL_CONFIG["recall_rate"]:
            retrieved.add("POLICY_DOC_001")

    if trade.investment_experience == "Beginner":
        if random.random() < RETRIEVAL_CONFIG["recall_rate"]:
            retrieved.add("POLICY_EXP_001")

    # --- INTENTIONAL MISSES ---
    # Don't cover all signals in order to create some false negatives

    # --- NOISE INJECTION (false positives) ---
    if random.random() < RETRIEVAL_CONFIG["noise_rate"]:
        num_noise = random.randint(1, RETRIEVAL_CONFIG["max_noise"])

        noise_candidates = [
            pid for pid in ALL_POLICY_IDS if pid not in retrieved
        ]

        noise = random.sample(noise_candidates, min(num_noise, len(noise_candidates)))
        retrieved.update(noise)

    return list(retrieved)