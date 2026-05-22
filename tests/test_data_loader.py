import sys
import os
from pathlib import Path
from unittest.mock import patch, MagicMock
import pandas as pd

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


class TestDataLoaderImport:
    """Test data_loader module imports and initialization."""

    @patch('src.data.data_loader.pd.read_csv')
    def test_data_loader_loads_csv(self, mock_read_csv):
        """Test that data_loader attempts to read CSV file."""
        # Create mock DataFrame
        mock_df = pd.DataFrame({
            'trade_id': ['T001', 'T002'],
            'client_age': [35, 45],
            'advisor_id': ['A123', 'A456']
        })
        mock_read_csv.return_value = mock_df

        # Reload module with mocked read_csv
        import importlib
        import src.data.data_loader as data_loader_module
        importlib.reload(data_loader_module)

        mock_read_csv.assert_called_once()

    @patch('src.data.data_loader.pd.read_csv')
    def test_cases_list_created_from_dataframe(self, mock_read_csv):
        """Test that cases list is created from DataFrame."""
        mock_df = pd.DataFrame({
            'trade_id': ['T001', 'T002', 'T003'],
            'client_age': [35, 45, 55],
            'risk_tolerance': ['Medium', 'High', 'Low']
        })
        mock_df = mock_df.fillna("")
        mock_read_csv.return_value = mock_df

        import importlib
        import src.data.data_loader as data_loader_module
        importlib.reload(data_loader_module)

        # Verify cases is a list of dicts
        assert isinstance(data_loader_module.raw_cases, list)
        assert len(data_loader_module.raw_cases) == 3
        assert all(isinstance(case, dict) for case in data_loader_module.raw_cases)

    @patch('src.data.data_loader.pd.read_csv')
    def test_case_lookup_created_from_dataframe(self, mock_read_csv):
        """Test that case_lookup dict is created with trade_id as key."""
        mock_df = pd.DataFrame({
            'trade_id': ['T001', 'T002', 'T003'],
            'client_age': [35, 45, 55],
            'advisor_id': ['A123', 'A456', 'A789']
        })
        mock_read_csv.return_value = mock_df

        import importlib
        import src.data.data_loader as data_loader_module
        importlib.reload(data_loader_module)

        # Verify raw_cases is a list of dicts with trade_id keys
        assert isinstance(data_loader_module.raw_cases, list)
        assert len(data_loader_module.raw_cases) == 3
        trade_ids = [case['trade_id'] for case in data_loader_module.raw_cases]
        assert 'T001' in trade_ids
        assert 'T002' in trade_ids
        assert 'T003' in trade_ids

    @patch('src.data.data_loader.pd.read_csv')
    def test_case_lookup_values_are_case_records(self, mock_read_csv):
        """Test that case_lookup values contain the correct case data."""
        mock_df = pd.DataFrame({
            'trade_id': ['T001', 'T002'],
            'client_age': [35, 45],
            'advisor_id': ['A123', 'A456']
        })
        mock_read_csv.return_value = mock_df

        import importlib
        import src.data.data_loader as data_loader_module
        importlib.reload(data_loader_module)

        # Verify raw_cases data is correct
        raw_cases_dict = {case['trade_id']: case for case in data_loader_module.raw_cases}
        case_t001 = raw_cases_dict['T001']
        assert case_t001['trade_id'] == 'T001'
        assert case_t001['client_age'] == 35
        assert case_t001['advisor_id'] == 'A123'

        case_t002 = raw_cases_dict['T002']
        assert case_t002['trade_id'] == 'T002'
        assert case_t002['client_age'] == 45
        assert case_t002['advisor_id'] == 'A456'

    @patch('src.data.data_loader.pd.read_csv')
    def test_fillna_replaces_nan_with_empty_string(self, mock_read_csv):
        """Test that NaN values are replaced with empty strings."""
        mock_df = pd.DataFrame({
            'trade_id': ['T001', 'T002'],
            'client_age': [35, 45],
            'advisor_notes': [None, 'Some notes']
        })
        mock_read_csv.return_value = mock_df

        import importlib
        import src.data.data_loader as data_loader_module
        importlib.reload(data_loader_module)

        # Verify NaN is replaced with empty string
        raw_cases_dict = {case['trade_id']: case for case in data_loader_module.raw_cases}
        case_t001 = raw_cases_dict['T001']
        assert case_t001['advisor_notes'] == ''

        case_t002 = raw_cases_dict['T002']
        assert case_t002['advisor_notes'] == 'Some notes'

    @patch('src.data.data_loader.pd.read_csv')
    def test_data_loader_handles_empty_dataframe(self, mock_read_csv):
        """Test that data_loader handles empty DataFrame gracefully."""
        mock_df = pd.DataFrame({
            'trade_id': [],
            'client_age': [],
            'advisor_id': []
        })
        mock_read_csv.return_value = mock_df

        import importlib
        import src.data.data_loader as data_loader_module
        importlib.reload(data_loader_module)

        # Verify empty structures
        assert isinstance(data_loader_module.raw_cases, list)
        assert len(data_loader_module.raw_cases) == 0

    @patch('src.data.data_loader.pd.read_csv')
    def test_data_loader_with_multiple_columns(self, mock_read_csv):
        """Test data_loader with realistic DataFrame structure."""
        mock_df = pd.DataFrame({
            'trade_id': ['T001', 'T002'],
            'client_age': [35, 45],
            'client_income': [50000, 75000],
            'risk_tolerance': ['Medium', 'High'],
            'investment_experience': ['Beginner', 'Intermediate'],
            'investment_objective': ['Growth', 'Income'],
            'investment_time_horizon': ['Medium', 'Long'],
            'investment_type': ['Stocks', 'Bonds'],
            'investment_amount': [10000.0, 25000.0],
            'advisor_id': ['A123', 'A456'],
            'advisor_experience': ['Mid', 'Senior'],
            'advisor_history_risk': ['Low', 'Medium'],
            'has_rationale': [True, False],
            'kyc_completeness': ['Complete', 'Incomplete']
        })
        mock_read_csv.return_value = mock_df

        import importlib
        import src.data.data_loader as data_loader_module
        importlib.reload(data_loader_module)

        # Verify all columns are present in raw_cases
        case = data_loader_module.raw_cases[0]
        assert case['trade_id'] == 'T001'
        assert case['client_age'] == 35
        assert case['advisor_id'] == 'A123'
        assert case['investment_amount'] == 10000.0

    @patch('src.data.data_loader.pd.read_csv')
    def test_cases_maintain_insertion_order(self, mock_read_csv):
        """Test that cases maintain the order from DataFrame."""
        mock_df = pd.DataFrame({
            'trade_id': ['T003', 'T001', 'T002'],
            'client_age': [55, 35, 45]
        })
        mock_read_csv.return_value = mock_df

        import importlib
        import src.data.data_loader as data_loader_module
        importlib.reload(data_loader_module)

        # Verify order is maintained
        assert data_loader_module.raw_cases[0]['trade_id'] == 'T003'
        assert data_loader_module.raw_cases[1]['trade_id'] == 'T001'
        assert data_loader_module.raw_cases[2]['trade_id'] == 'T002'
