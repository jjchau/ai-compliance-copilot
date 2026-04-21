import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from unittest.mock import Mock
from src.data.schema import Trade
from src.decisioning.conflict_detection import has_conflicting_signals


@pytest.fixture
def mock_trade():
    return Mock(spec=Trade)


class TestHasConflictingSignals:
    def test_aggressive_and_conservative_signals(self, monkeypatch):
        """Test when there are both aggressive and conservative signals"""
        trade = Mock(spec=Trade)
        import src.decisioning.conflict_detection as cd_mod
        monkeypatch.setattr(cd_mod, 'is_risk_too_high_for_profile', lambda t: True)
        monkeypatch.setattr(cd_mod, 'is_too_complex_for_experience', lambda t: False)
        monkeypatch.setattr(cd_mod, 'is_investment_too_aggressive_for_objective', lambda t: False)
        monkeypatch.setattr(cd_mod, 'is_investment_too_agressive_for_horizon', lambda t: False)
        monkeypatch.setattr(cd_mod, 'is_risk_too_low_for_profile', lambda t: True)
        monkeypatch.setattr(cd_mod, 'is_investment_too_conservative_for_objective', lambda t: False)
        monkeypatch.setattr(cd_mod, 'is_investment_too_conservative_for_horizon', lambda t: False)
        assert has_conflicting_signals(trade) is True

    def test_all_aggressive_signals(self, monkeypatch):
        """Test when there are only aggressive signals (no conflict)"""
        trade = Mock(spec=Trade)
        import src.decisioning.conflict_detection as cd_mod
        monkeypatch.setattr(cd_mod, 'is_risk_too_high_for_profile', lambda t: True)
        monkeypatch.setattr(cd_mod, 'is_too_complex_for_experience', lambda t: True)
        monkeypatch.setattr(cd_mod, 'is_investment_too_aggressive_for_objective', lambda t: True)
        monkeypatch.setattr(cd_mod, 'is_investment_too_agressive_for_horizon', lambda t: True)
        monkeypatch.setattr(cd_mod, 'is_risk_too_low_for_profile', lambda t: False)
        monkeypatch.setattr(cd_mod, 'is_investment_too_conservative_for_objective', lambda t: False)
        monkeypatch.setattr(cd_mod, 'is_investment_too_conservative_for_horizon', lambda t: False)
        assert has_conflicting_signals(trade) is False

    def test_all_conservative_signals(self, monkeypatch):
        """Test when there are only conservative signals (no conflict)"""
        trade = Mock(spec=Trade)
        import src.decisioning.conflict_detection as cd_mod
        monkeypatch.setattr(cd_mod, 'is_risk_too_high_for_profile', lambda t: False)
        monkeypatch.setattr(cd_mod, 'is_too_complex_for_experience', lambda t: False)
        monkeypatch.setattr(cd_mod, 'is_investment_too_aggressive_for_objective', lambda t: False)
        monkeypatch.setattr(cd_mod, 'is_investment_too_agressive_for_horizon', lambda t: False)
        monkeypatch.setattr(cd_mod, 'is_risk_too_low_for_profile', lambda t: True)
        monkeypatch.setattr(cd_mod, 'is_investment_too_conservative_for_objective', lambda t: True)
        monkeypatch.setattr(cd_mod, 'is_investment_too_conservative_for_horizon', lambda t: True)
        assert has_conflicting_signals(trade) is False

    def test_no_signals(self, monkeypatch):
        """Test when there are no signals (no conflict)"""
        trade = Mock(spec=Trade)
        import src.decisioning.conflict_detection as cd_mod
        monkeypatch.setattr(cd_mod, 'is_risk_too_high_for_profile', lambda t: False)
        monkeypatch.setattr(cd_mod, 'is_too_complex_for_experience', lambda t: False)
        monkeypatch.setattr(cd_mod, 'is_investment_too_aggressive_for_objective', lambda t: False)
        monkeypatch.setattr(cd_mod, 'is_investment_too_agressive_for_horizon', lambda t: False)
        monkeypatch.setattr(cd_mod, 'is_risk_too_low_for_profile', lambda t: False)
        monkeypatch.setattr(cd_mod, 'is_investment_too_conservative_for_objective', lambda t: False)
        monkeypatch.setattr(cd_mod, 'is_investment_too_conservative_for_horizon', lambda t: False)
        assert has_conflicting_signals(trade) is False

    def test_multiple_aggressive_one_conservative(self, monkeypatch):
        """Test with multiple aggressive and one conservative signal"""
        trade = Mock(spec=Trade)
        import src.decisioning.conflict_detection as cd_mod
        monkeypatch.setattr(cd_mod, 'is_risk_too_high_for_profile', lambda t: True)
        monkeypatch.setattr(cd_mod, 'is_too_complex_for_experience', lambda t: True)
        monkeypatch.setattr(cd_mod, 'is_investment_too_aggressive_for_objective', lambda t: True)
        monkeypatch.setattr(cd_mod, 'is_investment_too_agressive_for_horizon', lambda t: False)
        monkeypatch.setattr(cd_mod, 'is_risk_too_low_for_profile', lambda t: True)
        monkeypatch.setattr(cd_mod, 'is_investment_too_conservative_for_objective', lambda t: False)
        monkeypatch.setattr(cd_mod, 'is_investment_too_conservative_for_horizon', lambda t: False)
        assert has_conflicting_signals(trade) is True
