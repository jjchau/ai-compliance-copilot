import random
from typing import Literal
from src.data.schema import Trade, LabeledTrade
from src.decisioning.labeling import *

RISK_TOLERANCES: list[Literal['Low', 'Medium', 'High']] = ['Low', 'Medium', 'High']
INVESTMENT_EXPERIENCE: list[Literal['Beginner', 'Intermediate', 'Advanced']] = ['Beginner', 'Intermediate', 'Advanced']
INVESTMENT_OBJECTIVES: list[Literal['Growth', 'Income', 'Preservation', 'Balanced']] = ['Growth', 'Income', 'Preservation', 'Balanced']
INVESTMENT_TIME_HORIZONS: list[Literal['Short', 'Medium', 'Long']] = ['Short', 'Medium', 'Long']
INVESTMENT_TYPES: list[Literal['Stocks', 'Bonds', 'GICs', 'T-Bills', 'Mutual Funds', 'ETFs', 'Options']] = ['Stocks', 'Bonds', 'GICs', 'T-Bills', 'Mutual Funds', 'ETFs', 'Options']
ADVISOR_EXPERIENCE: list[Literal['Junior', 'Mid', 'Senior']] = ['Junior', 'Mid', 'Senior']
ADVISOR_HISTORY_RISK: list[Literal['Low', 'Medium', 'High']] = ['Low', 'Medium', 'High']
KYC_COMPLETENESS: list[Literal['Complete', 'Partial', 'Missing']] = ['Complete', 'Partial', 'Missing']

advisor_profiles: dict[str, Literal['Low', 'Medium', 'High']] = {
    'ADV-001': 'Low',
	'ADV-002': 'Low',
	'ADV-003': 'Low',
	'ADV-004': 'Low',
	'ADV-005': 'Medium',
	'ADV-006': 'Low',
	'ADV-007': 'Medium',
	'ADV-008': 'Low',
	'ADV-009': 'High',
	'ADV-010': 'Low',
	'ADV-011': 'Medium',
	'ADV-012': 'Low',
	'ADV-013': 'Low',
	'ADV-014': 'Medium',
	'ADV-015': 'Medium',
	'ADV-016': 'Medium',
	'ADV-017': 'High',
	'ADV-018': 'Medium',
	'ADV-019': 'High',
	'ADV-020': 'Low',
	'ADV-021': 'Low',
	'ADV-022': 'Medium',
	'ADV-023': 'Low',
	'ADV-024': 'Low',
	'ADV-025': 'Low',
	'ADV-026': 'High',
	'ADV-027': 'Medium',
	'ADV-028': 'Low',
	'ADV-029': 'Low',
	'ADV-030': 'Low',
	'ADV-031': 'Medium',
	'ADV-032': 'Low',
	'ADV-033': 'Medium',
	'ADV-034': 'Low',
	'ADV-035': 'Low',
	'ADV-036': 'Medium',
	'ADV-037': 'Low',
	'ADV-038': 'Low',
	'ADV-039': 'Medium',
	'ADV-040': 'Low',
	'ADV-041': 'Low',
	'ADV-042': 'High',
	'ADV-043': 'Medium',
	'ADV-044': 'Medium',
	'ADV-045': 'Medium',
	'ADV-046': 'Medium',
	'ADV-047': 'Low',
	'ADV-048': 'Medium',
	'ADV-049': 'Low',
	'ADV-050': 'Medium'
    }

def generate_base_case() -> Trade:
    advisor_id = random.choice(list(advisor_profiles.keys()))
    return Trade(
        client_age=random.randint(18, 80),
        client_income=random.randint(30000, 200000),
        risk_tolerance=random.choice(RISK_TOLERANCES),
        investment_experience=random.choice(INVESTMENT_EXPERIENCE),
        investment_objective=random.choice(INVESTMENT_OBJECTIVES),
        investment_time_horizon=random.choice(INVESTMENT_TIME_HORIZONS),
        investment_type=random.choice(INVESTMENT_TYPES),
        investment_amount=round(random.uniform(100, 100000), 2),
        advisor_id=advisor_id,
        advisor_experience=random.choice(ADVISOR_EXPERIENCE),
        advisor_history_risk=advisor_profiles[advisor_id],
        has_rationale=random.choice([True, False]),
        advisor_notes=None if random.random() < 0.2 else "Sample note",
        kyc_completeness=random.choice(KYC_COMPLETENESS)
    )

def generate_labeled_case() -> LabeledTrade:
    base_case = generate_base_case()
    # Placeholder logic for labeling - in practice, this would be based on domain expertise
    true_compliance = compute_true_compliance(base_case)
    case_type: Literal["Suitability Violation", "KYC Missing", "Insufficient Experience", "Risk Signal", "Aligned Recommendation"] = assign_case_type(base_case)
    difficulty: Literal['Easy', 'Medium', 'Hard'] = random.choice(['Easy', 'Medium', 'Hard'])
    
    return LabeledTrade(
        **base_case.model_dump(),
        true_compliance=true_compliance,
        case_type=case_type,
        difficulty=difficulty
    )