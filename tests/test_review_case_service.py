import sys
import os
import importlib
from unittest.mock import MagicMock

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.data.schema import Trade


def make_raw_trade(trade_id: str):
    return {
        'trade_id': trade_id,
        'client_age': 30,
        'client_income': 100000,
        'risk_tolerance': 'Medium',
        'investment_experience': 'Intermediate',
        'investment_objective': 'Growth',
        'investment_time_horizon': 'Medium',
        'investment_type': 'Stocks',
        'investment_amount': 10000.0,
        'advisor_id': 'A1',
        'advisor_experience': 'Mid',
        'advisor_history_risk': 'Low',
        'advisor_rationale': 'Advisor provided rationale.',
        'kyc_completeness': 'Complete',
    }


def test_serialize_case_strips_privileged_fields():
    import src.services.review_case_service as service_mod

    raw_case = {
        'trade_id': 'T001',
        'compliance_label': 1,
        'true_compliance': 'sensitive',
        'case_type': 'secret',
        'relevant_policies': ['POLICY_RISK_001'],
        'retrieved_policies': '["POLICY_KYC_001"]',
        'retrieved_chunks': '["chunk1"]',
        'escalation_level': 'PRIORITY'
    }

    serialized = service_mod._serialize_case(raw_case.copy())

    assert serialized['trade_id'] == 'T001'
    assert serialized['compliance_label'] is True
    assert 'true_compliance' not in serialized
    assert 'case_type' not in serialized
    assert 'relevant_policies' not in serialized
    assert serialized['retrieved_policies'] == ['POLICY_KYC_001']
    assert serialized['retrieved_chunks'] == ['chunk1']
    assert serialized['escalation_level'] == 'priority'


def test_get_single_case_from_db_returns_serialized_case(monkeypatch):
    import sqlite3
    import src.services.review_case_service as service_mod

    expected_row = {
        'trade_id': 'T123',
        'compliance_label': 0,
        'retrieved_policies': '["POLICY_KYC_001"]',
        'retrieved_chunks': '["chunk1"]',
        'escalation_level': 'PRIORITY'
    }

    class DummyCursor:
        def execute(self, query, params):
            assert query == "SELECT * FROM audited_trades WHERE trade_id = ?"
            assert params == ('T123',)
        def fetchone(self):
            return expected_row

    class DummyConn:
        def __init__(self):
            self.row_factory = None
            self.cursor_obj = DummyCursor()
        def cursor(self):
            return self.cursor_obj
        def close(self):
            pass

    monkeypatch.setattr(sqlite3, 'connect', lambda db_path: DummyConn())

    result = service_mod.get_single_case_from_db('T123')

    assert result['trade_id'] == 'T123'
    assert result['compliance_label'] is False
    assert result['retrieved_policies'] == ['POLICY_KYC_001']
    assert result['retrieved_chunks'] == ['chunk1']
    assert result['escalation_level'] == 'priority'


def test_dict_factory_and_serialize_case_handles_bad_json_and_empty_values():
    import src.services.review_case_service as service_mod

    cursor = MagicMock()
    cursor.description = [("trade_id",), ("compliance_label",)]

    assert service_mod.dict_factory(cursor, ("T1", 1)) == {
        "trade_id": "T1",
        "compliance_label": 1,
    }
    assert service_mod._serialize_case({}) == {}

    serialized = service_mod._serialize_case(
        {
            "trade_id": "T2",
            "compliance_label": True,
            "retrieved_policies": "[bad json",
            "retrieved_chunks": None,
        }
    )

    assert serialized["retrieved_policies"] == []
    assert serialized["retrieved_chunks"] == []


def test_get_all_enriched_cases_filters_and_sorts(monkeypatch):
    import sqlite3
    import src.services.review_case_service as service_mod

    executed = []

    class DummyCursor:
        def execute(self, query, params=None):
            executed.append((query, params))

        def fetchall(self):
            return [
                {
                    "trade_id": "T1",
                    "compliance_label": 1,
                    "retrieved_policies": "[]",
                    "retrieved_chunks": "[]",
                }
            ]

    class DummyConn:
        def __init__(self):
            self.row_factory = None
            self.cursor_obj = DummyCursor()

        def cursor(self):
            return self.cursor_obj

        def close(self):
            pass

    monkeypatch.setattr(sqlite3, "connect", lambda db_path: DummyConn())

    filtered = service_mod.get_all_enriched_cases("priority")
    sorted_cases = service_mod.get_all_enriched_cases("invalid")

    assert filtered[0]["trade_id"] == "T1"
    assert sorted_cases[0]["trade_id"] == "T1"
    assert executed[0] == (
        "SELECT * FROM audited_trades WHERE escalation_level = ?",
        ("priority",),
    )
    assert executed[1] == (
        "SELECT * FROM audited_trades ORDER BY priority_score DESC",
        None,
    )


def test_get_single_case_from_db_returns_none(monkeypatch):
    import sqlite3
    import src.services.review_case_service as service_mod

    class DummyCursor:
        def execute(self, query, params):
            pass

        def fetchone(self):
            return None

    class DummyConn:
        def __init__(self):
            self.row_factory = None

        def cursor(self):
            return DummyCursor()

        def close(self):
            pass

    monkeypatch.setattr(sqlite3, "connect", lambda db_path: DummyConn())

    assert service_mod.get_single_case_from_db("missing") is None
