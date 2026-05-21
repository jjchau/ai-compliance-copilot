from src.data.data_loader import raw_cases
from src.data.schema import Trade
from src.orchestration.review_pipeline import build_review_case

def load_review_cases():
    review_cases = []

    for row in raw_cases:
        trade=Trade(**row)
        review_cases.append(build_review_case(trade))

    return review_cases

cases = load_review_cases()

case_lookup = {case["trade_id"] : case for case in cases}