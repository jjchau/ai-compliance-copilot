from src.data.schema import Trade

def is_horizon_mismatch(trade: Trade) -> bool:
    """
    A time horizon mismatch occurs when the client's investment time horizon is not aligned with the investment type.
    For example:
    - A short-term investor investing in long-term products like Mutual Funds or ETFs.
    """
    if trade.investment_time_horizon == 'Short' and trade.investment_type in ['Stocks', 'Options']:
        return True
    return False

def is_objective_mismatch(trade: Trade) -> bool:
    """
    An investment objective mismatch occurs when the client's investment objective is not aligned with the investment type.
    For example:
    - An investor with a preservation objective investing in high-risk products like Stocks or Options.
    """
    if trade.investment_objective == 'Preservation' and trade.investment_type in ['Stocks', 'Options']:
        return True
    return False

def is_overexposure(trade: Trade) -> bool:
    """
    An overexposure signal occurs when the investment amount exceeds a certain percentage of the client's income, even if it doesn't trigger a hard suitability violation.
    For example:
    - An investment amount that exceeds 30% of the client's income may be a soft signal of overexposure.
    """
    return trade.investment_amount > 0.3 * trade.client_income