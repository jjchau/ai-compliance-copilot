from src.decisioning.compliance_scoring import compute_compliance_probability
from src.decisioning.schema import ComplianceEvidenceSchema, ViolationType


def test_compliance_probability_clean_evidence_auto_passes():
    result = compute_compliance_probability(ComplianceEvidenceSchema())

    assert result == {
        "compliance_probability": 1.0,
        "compliance_label": True,
    }


def test_compliance_probability_sums_known_violations_and_rounds():
    evidence = ComplianceEvidenceSchema(
        violations=[
            ViolationType.RISK_TOLERANCE_VIOLATION,
            ViolationType.EXPERIENCE_COMPLEXITY_MISMATCH,
        ]
    )

    result = compute_compliance_probability(evidence)

    assert result["compliance_probability"] == 0.1
    assert result["compliance_label"] is False


def test_compliance_probability_clamps_non_compliance_at_one():
    evidence = ComplianceEvidenceSchema(
        violations=[
            ViolationType.KYC_MISSING,
            ViolationType.RISK_TOLERANCE_VIOLATION,
        ]
    )

    result = compute_compliance_probability(evidence)

    assert result["compliance_probability"] == 0.0
    assert result["compliance_label"] is False
