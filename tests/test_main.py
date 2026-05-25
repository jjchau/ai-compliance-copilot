import sys
import os
import importlib
from unittest.mock import patch, MagicMock, mock_open

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


# Mock data_loader before importing main
mock_cases = [
    {
        'trade_id': 'T001',
        'client_age': 35,
        'risk_tolerance': 'Medium',
        'advisor_id': 'A123',
        'investment_amount': 10000.0,
        'escalation_level': 'urgent'
    },
    {
        'trade_id': 'T002',
        'client_age': 45,
        'risk_tolerance': 'High',
        'advisor_id': 'A456',
        'investment_amount': 25000.0,
        'escalation_level': 'priority'
    },
    {
        'trade_id': 'T003',
        'client_age': 55,
        'risk_tolerance': 'Low',
        'advisor_id': 'A789',
        'investment_amount': 15000.0,
        'escalation_level': 'queue'
    }
]

mock_case_lookup = {
    'T001': mock_cases[0],
    'T002': mock_cases[1],
    'T003': mock_cases[2]
}


@pytest.fixture
def client():
    """Provide a TestClient for the FastAPI app."""
    # Remove cached modules so the app is imported fresh with mocked dependencies
    for module_name in ('src.api.main', 'src.services.review_case_service'):
        sys.modules.pop(module_name, None)

    old_service_module = sys.modules.get('src.services.review_case_service')
    sys.modules['src.services.review_case_service'] = MagicMock(cases=mock_cases, case_lookup=mock_case_lookup)
    try:
        main_module = importlib.import_module('src.api.main')

        # Directly patch the app's data
        main_module.cases = mock_cases
        main_module.case_lookup = mock_case_lookup

        return TestClient(main_module.app)
    finally:
        if old_service_module is None:
            sys.modules.pop('src.services.review_case_service', None)
        else:
            sys.modules['src.services.review_case_service'] = old_service_module


class TestRootEndpoint:
    """Test the root endpoint."""

    def test_root_endpoint_returns_success(self, client):
        """Test that root endpoint returns 200 status."""
        response = client.get("/")
        assert response.status_code == 200

    def test_root_endpoint_returns_message(self, client):
        """Test that root endpoint returns correct message."""
        response = client.get("/")
        data = response.json()
        assert "message" in data
        assert "Compliance Copilot API is running" in data["message"]

    def test_root_endpoint_response_type(self, client):
        """Test that root endpoint returns JSON dict."""
        response = client.get("/")
        assert response.headers["content-type"] == "application/json"
        assert isinstance(response.json(), dict)


class TestGetCasesEndpoint:
    """Test the /cases endpoint."""

    def test_get_cases_returns_success(self, client):
        """Test that /cases endpoint returns 200 status."""
        response = client.get("/cases")
        assert response.status_code == 200

    def test_get_cases_returns_list(self, client):
        """Test that /cases endpoint returns a list."""
        response = client.get("/cases")
        data = response.json()
        assert isinstance(data, list)

    def test_get_cases_returns_all_cases(self, client):
        """Test that /cases endpoint returns all cases."""
        response = client.get("/cases")
        data = response.json()
        assert len(data) == 3

    def test_get_cases_contains_correct_trade_ids(self, client):
        """Test that /cases returns cases with correct trade_ids."""
        response = client.get("/cases")
        data = response.json()
        trade_ids = [case["trade_id"] for case in data]
        assert "T001" in trade_ids
        assert "T002" in trade_ids
        assert "T003" in trade_ids

    def test_get_cases_contains_correct_data(self, client):
        """Test that /cases returns cases with correct data."""
        response = client.get("/cases")
        data = response.json()

        case_t001 = next((case for case in data if case["trade_id"] == "T001"), None)
        assert case_t001 is not None
        assert case_t001["client_age"] == 35
        assert case_t001["risk_tolerance"] == "Medium"
        assert case_t001["advisor_id"] == "A123"

    def test_get_cases_response_type(self, client):
        """Test that /cases returns JSON."""
        response = client.get("/cases")
        assert response.headers["content-type"].startswith("application/json")

    def test_get_cases_filters_by_escalation_urgent(self, client):
        """Test that /cases filters by escalation=urgent."""
        patched_cases = [
            {"trade_id": "T001", "escalation_level": "urgent"},
            {"trade_id": "T002", "escalation_level": "priority"}
        ]
        patched_lookup = {case["trade_id"]: case for case in patched_cases}

        for module_name in ('src.api.main', 'src.services.review_case_service'):
            sys.modules.pop(module_name, None)

        old_service_module = sys.modules.get('src.services.review_case_service')
        sys.modules['src.services.review_case_service'] = MagicMock(cases=patched_cases, case_lookup=patched_lookup)
        try:
            main_module = importlib.import_module('src.api.main')
            main_module.cases = patched_cases
            main_module.case_lookup = patched_lookup
            client_override = TestClient(main_module.app)
        finally:
            if old_service_module is None:
                sys.modules.pop('src.services.review_case_service', None)
            else:
                sys.modules['src.services.review_case_service'] = old_service_module

            response = client_override.get("/cases?escalation=urgent")
            assert response.status_code == 200
            assert response.json() == [patched_cases[0]]

    def test_get_cases_filters_by_escalation_priority(self, client):
        """Test that /cases filters by escalation=priority."""
        response = client.get("/cases?escalation=priority")
        assert response.status_code == 200
        assert response.json() == [mock_cases[1]]

    def test_get_cases_filters_by_escalation_queue(self, client):
        """Test that /cases filters by escalation=queue."""
        response = client.get("/cases?escalation=queue")
        assert response.status_code == 200
        assert response.json() == [mock_cases[2]]


class TestGetCaseByIdEndpoint:
    """Test the /cases/{trade_id} endpoint."""

    def test_get_case_by_id_returns_success(self, client):
        """Test that /cases/{trade_id} returns 200 for valid trade_id."""
        response = client.get("/cases/T001")
        assert response.status_code == 200

    def test_get_case_by_id_returns_correct_case(self, client):
        """Test that /cases/{trade_id} returns the correct case."""
        response = client.get("/cases/T001")
        data = response.json()["case"]
        assert data["trade_id"] == "T001"
        assert data["client_age"] == 35
        assert data["risk_tolerance"] == "Medium"
        assert data["advisor_id"] == "A123"

    def test_get_case_by_id_with_different_ids(self, client):
        """Test /cases/{trade_id} with different trade_ids."""
        response = client.get("/cases/T002")
        data = response.json()["case"]
        assert data["trade_id"] == "T002"
        assert data["client_age"] == 45

        response = client.get("/cases/T003")
        data = response.json()["case"]
        assert data["trade_id"] == "T003"
        assert data["client_age"] == 55

    def test_get_case_by_id_invalid_id_returns_404(self, client):
        """Test that /cases/{trade_id} returns 404 for non-existent trade_id."""
        response = client.get("/cases/INVALID_ID")
        assert response.status_code == 404

    def test_get_case_by_id_invalid_id_error_detail(self, client):
        """Test that 404 error has correct detail message."""
        response = client.get("/cases/INVALID_ID")
        data = response.json()
        assert "detail" in data
        assert "Case not found" in data["detail"]

    def test_get_case_by_id_response_type(self, client):
        """Test that /cases/{trade_id} returns JSON."""
        response = client.get("/cases/T001")
        assert response.headers["content-type"].startswith("application/json")

    def test_get_case_by_id_with_special_characters(self, client):
        """Test /cases/{trade_id} with special characters in ID."""
        response = client.get("/cases/T_INVALID")
        assert response.status_code == 404

    def test_get_case_by_id_case_sensitive(self, client):
        """Test that trade_id lookup is case-sensitive."""
        response = client.get("/cases/t001")
        assert response.status_code == 404

    def test_submit_review_returns_success(self, client):
        """Test that review submission succeeds for a valid case."""
        review_body = {
            "ai_recommendation": "approve",
            "review_action": "approve",
            "case_status": "reviewed",
            "review_outcome": "compliant",
            "reviewer": "Auditor",
            "notes": "Looks compliant"
        }
        with patch('builtins.open', mock_open()) as mocked_file, \
             patch('src.api.main.datetime') as mock_datetime:
            mock_datetime.now.return_value.isoformat.return_value = "2026-05-13T12:00:00"
            response = client.post("/cases/T001/review", json=review_body)

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "review posted successfully"
        assert data["review"]["trade_id"] == "T001"
        assert data["review"]["reviewer"] == "Auditor"
        assert data["review"]["reviewer_action"] == "approve"
        assert data["review"]["notes"] == "Looks compliant"
        assert data["review"]["timestamp"] == "2026-05-13T12:00:00"

    def test_submit_review_invalid_case_returns_404(self, client):
        """Test that review submission returns 404 for missing trade_id."""
        review_body = {
            "ai_recommendation": "approve",
            "review_action": "approve",
            "case_status": "reviewed",
            "review_outcome": "compliant",
            "reviewer": "Auditor",
            "notes": "Looks compliant"
        }
        response = client.post("/cases/UNKNOWN/review", json=review_body)
        assert response.status_code == 404
        assert response.json()["detail"] == "Case not found"

    def test_submit_review_invalid_body_returns_422(self, client):
        """Test that review submission returns validation error for missing fields."""
        review_body = {
            "ai_recommendation": "approve",
            # missing review_action to trigger validation error
            "case_status": "reviewed",
            "review_outcome": "compliant",
            "reviewer": "Auditor",
            "notes": "Missing action"
        }
        response = client.post("/cases/T001/review", json=review_body)
        assert response.status_code == 422


class TestAPIIntegration:
    """Integration tests for the API."""

    def test_all_endpoints_available(self, client):
        """Test that all endpoints are available."""
        # Test root
        assert client.get("/").status_code == 200
        
        # Test /cases
        assert client.get("/cases").status_code == 200
        
        # Test /cases/{trade_id}
        assert client.get("/cases/T001").status_code == 200

    def test_cases_consistency_between_endpoints(self, client):
        """Test that data is consistent between /cases and /cases/{trade_id}."""
        # Get all cases
        all_cases_response = client.get("/cases")
        all_cases = all_cases_response.json()

        # Verify each case can be retrieved individually
        for case in all_cases:
            trade_id = case['trade_id']
            individual_response = client.get(f"/cases/{trade_id}")
            individual_case = individual_response.json()["case"]
            
            # Verify data matches
            assert individual_case == case

    def test_api_handles_empty_cases(self):
        """Test API behavior with empty cases list."""
        with patch('src.api.main.cases', []), \
             patch('src.api.main.case_lookup', {}):
            from src.api.main import app
            client = TestClient(app)
            
            # Root should still work
            assert client.get("/").status_code == 200
            
            # /cases should return empty list
            response = client.get("/cases")
            assert response.status_code == 200
            assert response.json() == []
            
            # /cases/{trade_id} should return 404
            assert client.get("/cases/T001").status_code == 404

    def test_api_response_consistency(self, client):
        """Test that multiple requests return consistent data."""
        # Make multiple requests to the same endpoint
        response1 = client.get("/cases/T001")
        response2 = client.get("/cases/T001")
        
        assert response1.json() == response2.json()
        assert response1.status_code == response2.status_code
