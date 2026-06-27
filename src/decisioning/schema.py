"""
# src/decisioning/schema.py

Purpose:
    
    Define schema and enumerate 'codes' for evidence found/reasoned by LLM

Usage:
    from src.decisioning.schema import ViolationType, MissingEvidenceType, etc.

Author: Jason Chau
Date: 2026-06-15
"""

from pydantic import BaseModel, Field
from typing import List
from enum import Enum


class ViolationType(str, Enum):
    KYC_MISSING = "KYC_MISSING"
    RISK_TOLERANCE_VIOLATION = "RISK_TOLERANCE_VIOLATION"
    EXPERIENCE_COMPLEXITY_MISMATCH = "EXPERIENCE_COMPLEXITY_MISMATCH"

class ConcernSignalType(str, Enum):
    OVEREXPOSURE = "OVEREXPOSURE"
    AGGRESSIVE_FOR_SHORT_HORIZON = "AGGRESSIVE_FOR_SHORT_HORIZON"
    AGGRESSIVE_FOR_OBJECTIVE = "AGGRESSIVE_FOR_OBJECTIVE"
    HIGH_RISK_ADVISOR = "HIGH_RISK_ADVISOR"
    SENIOR_CLIENT_RISK = "SENIOR_CLIENT_RISK"
    TOO_CONSERVATIVE_FOR_RISK_PROFILE = "TOO_CONSERVATIVE_FOR_RISK_PROFILE"
    TOO_CONSERVATIVE_FOR_HORIZON = "TOO_CONSERVATIVE_FOR_HORIZON"
    TOO_CONSERVATIVE_FOR_OBJECTIVE = "TOO_CONSERVATIVE_FOR_OBJECTIVE"

class EvidenceQualityType(str, Enum):
    KYC_UNCERTAIN = "KYC_UNCERTAIN"
    MISSING_RATIONALE = "MISSING_RATIONALE"
    WEAK_RATIONALE = "WEAK_RATIONALE"
    MINIMAL_ADVISOR_NOTES = "MINIMAL_ADVISOR_NOTES"

class MitigatingFactorType(str, Enum):
    CLIENT_INITIATED_REQUEST = "CLIENT_INITIATED_REQUEST"
    CLIENT_HAS_PRIOR_PRODUCT_EXPERIENCE = "CLIENT_HAS_PRIOR_PRODUCT_EXPERIENCE"
    SMALL_POSITION_SIZE = "SMALL_POSITION_SIZE"
    DOCUMENTED_EXCEPTION_APPROVAL = "DOCUMENTED_EXCEPTION_APPROVAL"

# class RiskSignalType(str, Enum):
#     TOO_CONSERVATIVE_FOR_RISK_PROFILE = "TOO_CONSERVATIVE_FOR_RISK_PROFILE"
#     TOO_CONSERVATIVE_FOR_HORIZON = "TOO_CONSERVATIVE_FOR_HORIZON"
#     TOO_CONSERVATIVE_FOR_OBJECTIVE = "TOO_CONSERVATIVE_FOR_OBJECTIVE"

class ComplianceEvidenceSchema(BaseModel):

    violations: List[ViolationType] = Field(
        default_factory=list,
        description="""
        Compliance conclusions supported by trade facts and
        retrieved policy evidence.
        """
    )

    concern_signals: List[ConcernSignalType] = Field(
        default_factory=list,
        description="""
        Facts that introduce contextual concerns but are not
        compliance violations in and of themselves.
        """
    )

    mitigating_factors: List[MitigatingFactorType] = Field(
        default_factory=list,
        description="""
        Facts that reduce the severity of a concern without
        contradicting the concern itself.
        """
    )

    evidence_quality: List[EvidenceQualityType] = Field(
        default_factory=list,
        description="""
        Missing information, documentation, or explanations
        that reduce confidence in the compliance assessment.
        """
    )

    audit_reasoning: str = Field(
        default_factory=str,
        description="""
        Professional 2-3 sentence explanation citing
        the policy context and trade facts.
        """
    )