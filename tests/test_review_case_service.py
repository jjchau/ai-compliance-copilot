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
        'has_rationale': True,
        'kyc_completeness': 'Complete',
    }


def test_load_review_cases_builds_one_case_per_raw_record(monkeypatch):
    import src.data.data_loader as data_loader_mod
    import src.orchestration.review_pipeline as pipeline_mod

    raw_cases = [make_raw_trade('T001'), make_raw_trade('T002')]
    monkeypatch.setattr(data_loader_mod, 'raw_cases', raw_cases)

    def build_case_side_effect(trade):
        return {'trade_id': trade.trade_id}

    mock_build_review_case = MagicMock(side_effect=build_case_side_effect)
    monkeypatch.setattr(pipeline_mod, 'build_review_case', mock_build_review_case)

    sys.modules.pop('src.services.review_case_service', None)
    import importlib
    service_mod = importlib.import_module('src.services.review_case_service')
    mock_build_review_case.reset_mock()

    review_cases = service_mod.load_review_cases()

    assert review_cases == [{'trade_id': 'T001'}, {'trade_id': 'T002'}]
    assert mock_build_review_case.call_count == 2
    assert isinstance(mock_build_review_case.call_args_list[0].args[0], Trade)
    assert mock_build_review_case.call_args_list[0].args[0].trade_id == 'T001'
    assert isinstance(mock_build_review_case.call_args_list[1].args[0], Trade)
    assert mock_build_review_case.call_args_list[1].args[0].trade_id == 'T002'


def test_import_reloads_cases_and_case_lookup(monkeypatch):
    import src.data.data_loader as data_loader_mod
    import src.orchestration.review_pipeline as pipeline_mod

    raw_cases = [make_raw_trade('T123'), make_raw_trade('T456')]
    monkeypatch.setattr(data_loader_mod, 'raw_cases', raw_cases)

    case_one = {'trade_id': 'T123', 'status': 'mocked'}
    case_two = {'trade_id': 'T456', 'status': 'mocked'}
    mock_build_review_case = MagicMock(side_effect=[case_one, case_two])
    monkeypatch.setattr(pipeline_mod, 'build_review_case', mock_build_review_case)

    import src.services.review_case_service as service_mod
    importlib.reload(service_mod)

    assert service_mod.cases == [case_one, case_two]
    assert service_mod.case_lookup == {
        'T123': case_one,
        'T456': case_two,
    }
    assert mock_build_review_case.call_count == 2
    assert mock_build_review_case.call_args_list[0].args[0].trade_id == 'T123'
    assert mock_build_review_case.call_args_list[1].args[0].trade_id == 'T456'
