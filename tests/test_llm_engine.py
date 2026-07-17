import json
from types import SimpleNamespace

import pytest

from src.data.schema import Trade
from src.decisioning import llm_engine
from src.decisioning.llm_engine import GeminiComplianceEngine
from src.decisioning.schema import ComplianceEvidenceSchema


def make_trade(**overrides):
    values = {
        "trade_id": "TRADE-LLM",
        "client_age": 40,
        "client_income": 100000,
        "risk_tolerance": "Low",
        "investment_experience": "Beginner",
        "investment_objective": "Preservation",
        "investment_time_horizon": "Short",
        "investment_type": "Stocks",
        "investment_amount": 25000.0,
        "advisor_id": "ADV-001",
        "advisor_experience": "Junior",
        "advisor_history_risk": "Low",
        "advisor_rationale": "Client requested purchase.",
        "advisor_notes": "Minimal notes.",
        "kyc_completeness": "Complete",
    }
    values.update(overrides)
    return Trade(**values)


def test_engine_requires_gemini_api_key(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)

    with pytest.raises(RuntimeError, match="GEMINI_API_KEY"):
        GeminiComplianceEngine()


def test_engine_initializes_client_with_api_key(monkeypatch):
    created = {}

    class FakeGenAI:
        class Client:
            def __init__(self, api_key):
                created["api_key"] = api_key

    monkeypatch.setenv("GEMINI_API_KEY", "secret")
    monkeypatch.setattr(llm_engine, "genai", FakeGenAI)

    engine = GeminiComplianceEngine()

    assert created["api_key"] == "secret"
    assert engine.model_name == "gemini-3.1-flash-lite"


def test_evaluate_with_llm_builds_prompt_and_parses_json(monkeypatch):
    engine = object.__new__(GeminiComplianceEngine)
    captured = {}

    class FakeModels:
        def generate_content(self, **kwargs):
            captured.update(kwargs)
            return SimpleNamespace(
                text=json.dumps(
                    {
                        "violations": ["RISK_TOLERANCE_VIOLATION"],
                        "concern_signals": [],
                        "mitigating_factors": [],
                        "evidence_quality": [],
                        "audit_reasoning": "Policy text supports review.",
                    }
                )
            )

    engine.client = SimpleNamespace(models=FakeModels())
    engine.model_name = "fake-model"

    result = engine.evaluate_with_llm(make_trade(), ["Policy one", "Policy two"])

    assert result["violations"] == ["RISK_TOLERANCE_VIOLATION"]
    assert captured["model"] == "fake-model"
    assert "Policy one" in captured["contents"]
    assert "Investment Amount as Percentage" in captured["contents"]
    assert captured["config"].response_schema is ComplianceEvidenceSchema


def test_evaluate_with_llm_uses_no_policy_fallback():
    engine = object.__new__(GeminiComplianceEngine)

    class FakeModels:
        def generate_content(self, **kwargs):
            assert "No relevant compliance policies found" in kwargs["contents"]
            return SimpleNamespace(text="{}")

    engine.client = SimpleNamespace(models=FakeModels())
    engine.model_name = "fake-model"

    assert engine.evaluate_with_llm(make_trade(), []) == {}


def test_evaluate_with_llm_wraps_client_errors():
    engine = object.__new__(GeminiComplianceEngine)

    class FakeModels:
        def generate_content(self, **kwargs):
            raise ValueError("boom")

    engine.client = SimpleNamespace(models=FakeModels())
    engine.model_name = "fake-model"

    with pytest.raises(RuntimeError, match="Gemini Inference Exception"):
        engine.evaluate_with_llm(make_trade(), ["Policy"])
