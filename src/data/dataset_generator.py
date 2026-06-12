"""
dataset_generator.py

Purpose:
    Generate realistic synthetic compliance datasets
    using:

    - realistic investor profiles
    - deterministic compliance scenarios
    - realistic advisor documentation
    - existing labeling engine

Author: Jason Chau
Date: 2026-06-04
"""

from pathlib import Path
import random
import pandas as pd
import sys

sys.path.append(str(Path(__file__).resolve().parents[2]))

from src.data.schema import LabeledTrade
from src.data.profile_factories import PROFILE_FACTORIES
from src.data.scenario_builders import SCENARIO_BUILDERS
from src.data.text_generation import enrich_trade_text
from src.decisioning.labeling import (
    compute_true_compliance,
    assign_case_type,
    assign_difficulty,
    assign_severity_tier,
    assign_expected_workflow_bucket,
    assign_primary_policy
)
from src.policy.ground_truth import get_relevant_policies


# ==========================================================
# Dataset Configuration
# ==========================================================

DEFAULT_DATASET_SIZE = 1000

SCENARIO_WEIGHTS = {
    # ----------------------------------
    # Compliant
    # ----------------------------------

    "Aligned Recommendation": 0.30,

    # ----------------------------------    
    # Hard violations
    # ----------------------------------

    "KYC Missing": 0.08,
    "Suitability Violation": 0.10,
    "Insufficient Experience": 0.08,

    # ----------------------------------
    # Soft signals
    # ----------------------------------

    "Risk Signal": 0.10,
    "Overexposure": 0.08,
    "Aggressive Horizon": 0.05,
    "Aggressive Objective": 0.05,
    "Conflicting Signals": 0.05,

    # ----------------------------------
    # Advisor supervision
    # ----------------------------------

    "High Risk Advisor": 0.04,

    # ----------------------------------
    # Senior supervision
    # ----------------------------------

    "Retiree Speculation": 0.03,
    "Retiree Options": 0.02,

    # ----------------------------------
    # Queue testing
    # ----------------------------------

    "Low Priority Exception": 0.08,

    # ----------------------------------
    # Urgent review testing
    # ----------------------------------

    "Compound Violation": 0.04
}

# ==========================================================
# Scenario Selection
# ==========================================================

def choose_scenario() -> str:

    names = list(SCENARIO_WEIGHTS.keys())
    weights = list(SCENARIO_WEIGHTS.values())

    return random.choices(
        population=names,
        weights=weights,
        k=1
    )[0]


# ==========================================================
# Profile Selection
# ==========================================================

def choose_profile_factory():

    return random.choice(PROFILE_FACTORIES)


# ==========================================================
# Single Case Generation
# ==========================================================

def generate_case() -> LabeledTrade:

    # ----------------------------------
    # Create realistic investor
    # ----------------------------------

    profile_factory = choose_profile_factory()
    trade = profile_factory()

    # ----------------------------------
    # Apply scenario
    # ----------------------------------

    scenario_name = choose_scenario()
    scenario_builder = SCENARIO_BUILDERS[scenario_name]
    trade = scenario_builder(trade)

    # ----------------------------------
    # Generate documentation
    # ----------------------------------

    trade = enrich_trade_text(trade, scenario_name)

    # ----------------------------------
    # Ground truth generation
    # ----------------------------------

    true_compliance = compute_true_compliance(trade)
    case_type = assign_case_type(trade)
    difficulty = assign_difficulty(trade)
    relevant_policies = get_relevant_policies(trade)
    primary_policy = assign_primary_policy(trade)
    severity_tier = assign_severity_tier(trade)
    expected_workflow_bucket = assign_expected_workflow_bucket(trade)

    # ----------------------------------
    # Build labeled record
    # ----------------------------------

    return LabeledTrade(
        **trade.model_dump(),
        true_compliance=true_compliance,
        case_type=case_type,
        scenario_name=scenario_name,
        difficulty=difficulty,
        relevant_policies=relevant_policies,
        primary_policy=primary_policy,
        severity_tier=severity_tier,
        expected_workflow_bucket=expected_workflow_bucket
    )


# ==========================================================
# Dataset Generation
# ==========================================================

def generate_dataset(num_cases: int = DEFAULT_DATASET_SIZE) -> pd.DataFrame:
    rows = []

    for _ in range(num_cases):
        case = generate_case()
        rows.append(case.model_dump())

    return pd.DataFrame(rows)


# ==========================================================
# Dataset Statistics
# ==========================================================

def print_dataset_summary(df):

    print("\n==============================")
    print("DATASET SUMMARY")
    print("==============================")
    print(f"\nTotal Cases: {len(df)}")
    print("\nCase Type Distribution:")
    print(df["case_type"].value_counts(normalize=True).round(3))
    print("\nCompliance Distribution:")
    print(df["true_compliance"].value_counts(normalize=True).round(3))
    print("\nDifficulty Distribution:")
    print(df["difficulty"].value_counts(normalize=True).round(3))


# ==========================================================
# Export
# ==========================================================

def save_dataset(df, output_path):

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)

    print(
        f"\n[✓] Saved dataset to:"
        f"\n{output_path}"
    )


# ==========================================================
# Main
# ==========================================================

if __name__ == "__main__":

    random.seed(42)

    df = generate_dataset(num_cases=1000)
    print_dataset_summary(df)

    save_dataset(df, "data/runtime/trades_runtime_v7.csv")