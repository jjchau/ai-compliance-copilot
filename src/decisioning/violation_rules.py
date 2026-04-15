from src.data.schema import Trade

def is_kyc_violation(trade: Trade) -> bool:
    """
    A KYC violation occurs when the client's KYC completeness is 'Missing' or 'Partial'.
    """
    return trade.kyc_completeness in ['Missing', 'Partial']

def is_suitability_violation(trade: Trade) -> bool:
    """
    A suitability violation occurs when the investment type or amount is not suitable for the client's profile.
    For example:
    - A high-risk investment (e.g., Options) for a client with low risk tolerance.
    - An investment amount that exceeds a certain percentage of the client's income.
    """
    if trade.risk_tolerance == 'Low' and trade.investment_type in ['Options', 'Stocks']:
        return True
    if trade.investment_amount > 0.5 * trade.client_income:
        return True
    return False

def is_experience_violation(trade: Trade) -> bool:
    """
    An experience violation occurs when the investment type is not suitable for the client's investment experience.
    For example:
    - A beginner client investing in complex products like Options or ETFs.
    """
    return (
        trade.investment_experience == 'Beginner'
        and trade.investment_type == 'Options'
        )