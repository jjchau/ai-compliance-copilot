import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from unittest.mock import Mock
from src.data.schema import Trade
from src.decisioning.violation_rules import (
    is_kyc_violation,
    is_suitability_violation,
    is_experience_violation
)


@pytest.fixture
def mock_trade():
    return Mock(spec=Trade)


class TestIsKycViolation:
    def test_kyc_violation_missing(self, monkeypatch):
        """Test KYC violation when completeness is Missing"""
        trade = Mock(spec=Trade)
        import src.decisioning.violation_rules as vr_mod
        monkeypatch.setattr(vr_mod, 'is_kyc_missing', lambda t: True)
        assert is_kyc_violation(trade) is True

    def test_kyc_violation_complete(self, monkeypatch):
        """Test no KYC violation when completeness is Complete"""
        trade = Mock(spec=Trade)
        import src.decisioning.violation_rules as vr_mod
        monkeypatch.setattr(vr_mod, 'is_kyc_missing', lambda t: False)
        assert is_kyc_violation(trade) is False


class TestIsSuitabilityViolation:
    def test_suitability_violation_high_risk(self, monkeypatch):
        """Test suitability violation when risk is too high for profile"""
        trade = Mock(spec=Trade)
        import src.decisioning.violation_rules as vr_mod
        monkeypatch.setattr(vr_mod, 'is_risk_too_high_for_profile', lambda t: True)
        assert is_suitability_violation(trade) is True

    def test_suitability_violation_low_risk(self, monkeypatch):
        """Test no suitability violation when risk is acceptable"""
        trade = Mock(spec=Trade)
        import src.decisioning.violation_rules as vr_mod
        monkeypatch.setattr(vr_mod, 'is_risk_too_high_for_profile', lambda t: False)
        assert is_suitability_violation(trade) is False


class TestIsExperienceViolation:
    def test_experience_violation_too_complex(self, monkeypatch):
        """Test experience violation when investment is too complex for experience level"""
        trade = Mock(spec=Trade)
        import src.decisioning.violation_rules as vr_mod
        monkeypatch.setattr(vr_mod, 'is_too_complex_for_experience', lambda t: True)
        assert is_experience_violation(trade) is True

    def test_experience_violation_acceptable(self, monkeypatch):
        """Test no experience violation when investment matches experience level"""
        trade = Mock(spec=Trade)
        import src.decisioning.violation_rules as vr_mod
        monkeypatch.setattr(vr_mod, 'is_too_complex_for_experience', lambda t: False)
        assert is_experience_violation(trade) is False
