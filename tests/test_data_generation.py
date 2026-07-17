import random

import pandas as pd
import pytest

from src.data.schema import LabeledTrade, Trade
from src.data import dataset_generator, profile_factories, scenario_builders, text_generation


def make_trade(**overrides):
    values = {
        "trade_id": "TRADE-BASE",
        "client_age": 40,
        "client_income": 100000,
        "risk_tolerance": "Medium",
        "investment_experience": "Intermediate",
        "investment_objective": "Growth",
        "investment_time_horizon": "Medium",
        "investment_type": "ETFs",
        "investment_amount": 10000.0,
        "advisor_id": "ADV-001",
        "advisor_experience": "Mid",
        "advisor_history_risk": "Low",
        "advisor_rationale": "Original rationale.",
        "advisor_notes": "Original notes.",
        "kyc_completeness": "Complete",
    }
    values.update(overrides)
    return Trade(**values)


def make_labeled_trade(**overrides):
    values = {
        **make_trade().model_dump(),
        "true_compliance": True,
        "case_type": "Aligned Recommendation",
        "scenario_name": "Aligned Recommendation",
        "difficulty": "Easy",
        "severity_tier": "Low",
        "expected_workflow_bucket": "Auto_pass",
        "relevant_policies": [],
        "primary_policy": "",
    }
    values.update(overrides)
    return LabeledTrade(**values)


def test_profile_factories_create_valid_archetypes():
    random.seed(7)

    young = profile_factories.create_young_growth_investor()
    midcareer = profile_factories.create_midcareer_balanced_investor()
    retiree = profile_factories.create_retiree_preservation_investor()
    active = profile_factories.create_active_trader()

    assert 22 <= young.client_age <= 35
    assert young.investment_objective == "Growth"
    assert young.investment_type in {"ETFs", "Mutual Funds"}

    assert 36 <= midcareer.client_age <= 60
    assert midcareer.investment_objective in {"Balanced", "Income"}
    assert midcareer.investment_type in {"Mutual Funds", "ETFs", "Bonds"}

    assert 65 <= retiree.client_age <= 85
    assert retiree.risk_tolerance == "Low"
    assert retiree.investment_type in {"Bonds", "GICs", "T-Bills"}

    assert 25 <= active.client_age <= 60
    assert active.risk_tolerance == "High"
    assert active.investment_experience == "Advanced"


def test_base_trade_uses_advisor_registry(monkeypatch):
    monkeypatch.setattr(
        profile_factories.random,
        "choice",
        lambda values: "ADV-009" if "ADV-009" in list(values) else list(values)[0],
    )
    monkeypatch.setattr(
        profile_factories.random,
        "choices",
        lambda **kwargs: ["Senior"],
    )

    trade = profile_factories.base_trade(
        client_age=45,
        client_income=90000,
        risk_tolerance="Medium",
        investment_experience="Intermediate",
        investment_objective="Growth",
        investment_time_horizon="Long",
        investment_type="ETFs",
        investment_amount=5000,
        kyc_completeness="Complete",
    )

    assert trade.advisor_id == "ADV-009"
    assert trade.advisor_history_risk == "High"
    assert trade.advisor_experience == "Senior"
    assert trade.advisor_rationale is None
    assert trade.advisor_notes is None


@pytest.mark.parametrize(
    ("scenario_name", "expected"),
    [
        ("Aligned Recommendation", {"kyc_completeness": "Complete"}),
        ("KYC Missing", {"kyc_completeness": "Missing"}),
        (
            "Suitability Violation",
            {
                "risk_tolerance": "Low",
                "investment_objective": "Preservation",
                "investment_type": "Stocks",
            },
        ),
        (
            "Insufficient Experience",
            {"investment_experience": "Beginner", "investment_type": "Options"},
        ),
        ("Risk Signal", {"kyc_completeness": "Uncertain", "investment_amount": 50000.0}),
        ("Low Priority Exception", {"kyc_completeness": "Uncertain", "investment_amount": 2500}),
        (
            "Retiree Speculation",
            {
                "client_age": 75,
                "risk_tolerance": "Low",
                "investment_objective": "Preservation",
                "investment_type": "Stocks",
            },
        ),
        (
            "Retiree Options",
            {
                "client_age": 78,
                "risk_tolerance": "Low",
                "investment_experience": "Beginner",
                "investment_type": "Options",
            },
        ),
        ("Overexposure", {"investment_amount": 60000.0}),
        (
            "Aggressive Horizon",
            {"investment_time_horizon": "Short", "investment_type": "Stocks"},
        ),
        (
            "Aggressive Objective",
            {"investment_objective": "Preservation", "investment_type": "Stocks"},
        ),
        (
            "Conflicting Signals",
            {
                "risk_tolerance": "High",
                "investment_objective": "Growth",
                "investment_type": "T-Bills",
                "investment_time_horizon": "Long",
            },
        ),
        ("High Risk Advisor", {"advisor_history_risk": "High"}),
        (
            "Compound Violation",
            {
                "kyc_completeness": "Missing",
                "risk_tolerance": "Low",
                "investment_experience": "Beginner",
                "investment_type": "Options",
                "investment_amount": 70000.0,
                "advisor_history_risk": "High",
            },
        ),
    ],
)
def test_scenario_builders_apply_expected_mutations_without_mutating_input(
    scenario_name,
    expected,
):
    original = make_trade()
    original_snapshot = original.model_dump()

    result = scenario_builders.SCENARIO_BUILDERS[scenario_name](original)

    assert result is not original
    assert original.model_dump() == original_snapshot
    for field, value in expected.items():
        assert getattr(result, field) == value


def test_risk_signal_case_converts_short_horizon_to_stock_exposure():
    result = scenario_builders.build_risk_signal_case(
        make_trade(investment_time_horizon="Short", investment_type="Bonds")
    )

    assert result.investment_type == "Stocks"
    assert result.kyc_completeness == "Uncertain"


def test_text_generation_templates_and_overrides(monkeypatch):
    trade = make_trade(
        advisor_experience="Junior",
        advisor_history_risk="High",
        investment_type="Options",
        investment_objective="Growth",
        investment_time_horizon="Short",
    )
    monkeypatch.setattr(text_generation.random, "choice", lambda values: values[0])

    assert text_generation.advisor_bucket(trade) == "Junior_High"
    assert "Options" in text_generation.generate_rationale(trade)
    assert text_generation.generate_notes(trade)

    kyc_trade = text_generation.enrich_trade_text(trade, "KYC Missing")
    assert kyc_trade.advisor_rationale == ""
    assert "incomplete" in kyc_trade.advisor_notes

    low_priority = text_generation.apply_text_overrides(
        make_trade(advisor_notes="Base."), "Low Priority Exception"
    )
    assert low_priority.advisor_rationale == "Client requested purchase."
    assert low_priority.advisor_notes == (
        "Client requested transaction. No additional concerns documented."
    )

    compound = text_generation.apply_text_overrides(
        make_trade(advisor_notes="Base."), "Compound Violation"
    )
    assert "elevated risks" in compound.advisor_notes


def test_text_generation_unknown_bucket_uses_fallbacks():
    trade = make_trade()
    trade.advisor_experience = "Unknown"
    trade.advisor_history_risk = "Unknown"

    assert text_generation.generate_rationale(trade) == ""
    assert text_generation.generate_notes(trade) == "Standard client interaction completed."


def test_generate_case_for_scenario_and_generate_case(monkeypatch):
    monkeypatch.setattr(dataset_generator, "choose_profile_factory", lambda: make_trade)
    monkeypatch.setattr(dataset_generator, "choose_scenario", lambda: "KYC Missing")

    generated = dataset_generator.generate_case()
    targeted = dataset_generator.generate_case_for_scenario("Aligned Recommendation")

    assert isinstance(generated, LabeledTrade)
    assert generated.scenario_name == "KYC Missing"
    assert generated.kyc_completeness == "Missing"
    assert isinstance(targeted, LabeledTrade)
    assert targeted.scenario_name == "Aligned Recommendation"


def test_generate_dataset_stratified_summary_and_save(monkeypatch, tmp_path, capsys):
    calls = []

    def fake_case():
        return make_labeled_trade(trade_id=f"TRADE-{len(calls)}")

    def fake_case_for_scenario(scenario_name):
        calls.append(scenario_name)
        return make_labeled_trade(
            trade_id=f"TRADE-{len(calls)}",
            scenario_name=scenario_name,
        )

    monkeypatch.setattr(dataset_generator, "generate_case", fake_case)
    monkeypatch.setattr(dataset_generator, "generate_case_for_scenario", fake_case_for_scenario)
    monkeypatch.setattr(dataset_generator.random, "shuffle", lambda rows: rows.reverse())

    df = dataset_generator.generate_dataset(num_cases=2)
    stratified = dataset_generator.generate_stratified_evaluation_dataset(
        {"KYC Missing": 2, "Aligned Recommendation": 1}
    )

    assert len(df) == 2
    assert list(stratified["scenario_name"]) == [
        "Aligned Recommendation",
        "KYC Missing",
        "KYC Missing",
    ]

    dataset_generator.print_dataset_summary(stratified)
    assert "DATASET SUMMARY" in capsys.readouterr().out

    output_path = tmp_path / "nested" / "dataset.csv"
    dataset_generator.save_dataset(stratified, output_path)
    assert pd.read_csv(output_path).shape[0] == 3


def test_generate_stratified_evaluation_dataset_rejects_unknown_scenario():
    with pytest.raises(ValueError, match="Unknown scenario_name"):
        dataset_generator.generate_stratified_evaluation_dataset({"Not Real": 1})
