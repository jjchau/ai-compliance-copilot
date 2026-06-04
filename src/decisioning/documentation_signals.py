from src.data.schema import Trade

def is_missing_rationale(trade: Trade) -> bool:
    """
    A documentation signal indicating that the trade is missing a rationale for the investment decision.
    This can be a strong indicator of non-compliance, especially for high-risk trades, as it suggests a lack of proper documentation and justification for the trade.
    """
    return not trade.advisor_rationale