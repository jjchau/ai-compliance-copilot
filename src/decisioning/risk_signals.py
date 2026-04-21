from src.data.schema import Trade

# --- KYC ---
def is_kyc_missing(trade: Trade) -> bool:
    """
    A KYC missing violation occurs when the client's KYC completeness is 'Missing', which is a critical compliance failure.
    """
    return trade.kyc_completeness == 'Missing'

def is_kyc_uncertain(trade: Trade) -> bool:
    """
    A KYC uncertain signal occurs when the client's KYC completeness is 'Uncertain', which may indicate an outdated KYC profile, inconsistent responses vs behaviour, vague/incomplete answers, or a stale risk profile that could impact compliance decisions.
    """
    return trade.kyc_completeness == 'Uncertain'

# --- Risk alignment ---
def is_risk_too_high_for_profile(trade: Trade) -> bool:
    """
    A risk too high for profile violation occurs when the client's risk tolerance is low but they are investing in high-risk products like Stocks or Options. This is a strong signal of non-compliance, but not the only factor to consider.
    """
    return trade.risk_tolerance == "Low" and trade.investment_type in ["Stocks", "Options"]

def is_risk_too_low_for_profile(trade: Trade) -> bool:
    """
    A risk too low for profile signal occurs when the client's risk tolerance is high but they are investing in very low-risk products like Bonds, GICs, or T-Bills. This may not be a direct violation, but it could indicate a mismatch between the client's stated risk tolerance and their investment choices, which could be a contextual risk factor to consider.
    """
    return trade.risk_tolerance == "High" and trade.investment_type in ["Bonds", "GICs", "T-Bills"]

# --- Experience ---
def is_too_complex_for_experience(trade: Trade) -> bool:
    """
    A complexity mismatch occurs when the client's investment experience is not aligned with the complexity of the investment type. For example, a beginner client investing in complex products like Options may be a strong signal of non-compliance, but it should be considered in the context of other factors such as suitability and risk alignment.
    """
    return trade.investment_experience == "Beginner" and trade.investment_type == "Options"

# --- Horizon ---
def is_investment_too_agressive_for_horizon(trade: Trade) -> bool:
    """
    An investment too aggressive for the time horizon occurs when the client's investment time horizon is not aligned with the investment type. For example, a short-term investor investing in long-term products like Mutual Funds or ETFs may be a signal of non-compliance, but it should be evaluated alongside other factors such as suitability and risk alignment.
    """
    return trade.investment_time_horizon == "Short" and trade.investment_type in ["Stocks", "Options"]

def is_investment_too_conservative_for_horizon(trade: Trade) -> bool:
    """
    An investment too conservative for the time horizon occurs when the client's investment time horizon is long but they are investing in very low-risk products like Bonds, GICs, or T-Bills. This may not be a direct violation, but it could indicate a mismatch between the client's stated time horizon and their investment choices, which could be a contextual risk factor to consider.
    """
    return trade.investment_time_horizon == "Long" and trade.investment_type in ["Bonds", "GICs", "T-Bills"]

# --- Objective ---
def is_investment_too_aggressive_for_objective(trade: Trade) -> bool:
    """
    An investment too aggressive for the objective occurs when the client's investment objective is Preservation but they are investing in high-risk products like Stocks or Options. This is a strong signal of non-compliance, but it should be considered in the context of other factors such as suitability and risk alignment.
    """
    return trade.investment_objective == "Preservation" and trade.investment_type in ["Stocks", "Options"]

def is_investment_too_conservative_for_objective(trade: Trade) -> bool:
    """
    An investment too conservative for the objective occurs when the client's investment objective is Growth but they are investing in very low-risk products like Bonds, GICs, or T-Bills. This may not be a direct violation, but it could indicate a mismatch between the client's stated investment objective and their investment choices, which could be a contextual risk factor to consider.
    """
    return trade.investment_objective == "Growth" and trade.investment_type in ["Bonds", "GICs", "T-Bills"]

# --- Exposure ---
def is_overexposure(trade: Trade) -> bool:
    """
    An overexposure signal occurs when the investment amount exceeds a certain percentage of the client's income, even if it doesn't trigger a hard suitability violation.
    """
    return trade.investment_amount > 0.3 * trade.client_income

# --- Advisor ---
def is_advisor_history_high_risk(trade: Trade) -> bool:
    """
    An advisor history high risk signal occurs when the advisor has a history of compliance issues or regulatory actions, which could increase the risk profile of the trade.
    """
    return trade.advisor_history_risk == "High"