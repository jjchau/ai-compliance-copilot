"""
text_generation.py

Purpose:
    Generate realistic advisor rationale and advisor notes
    directly during synthetic case generation.

Author: Jason Chau
Date: 2026-06-04
"""

from pathlib import Path
import sys

sys.path.append(
    str(Path(__file__).resolve().parents[2])
)

import random

from src.data.schema import Trade


# ==========================================================
# RATIONALE TEMPLATES
# ==========================================================

RATIONALES = {

    # ------------------------------------------------------
    # Clean Advisors
    # ------------------------------------------------------

    "Junior_Low": [

        "Discussed client's {objective} objective and selected {product} consistent with their {horizon} investment horizon.",

        "Reviewed risks, fees, and expected performance characteristics of {product}. Client demonstrated understanding prior to execution.",

        "Recommended diversified exposure through {product} based on the client's documented profile and investment goals."
    ],

    "Mid_Low": [

        "Position established in {product} to maintain alignment with the client's broader portfolio strategy and target allocation.",

        "Trade executed following suitability review confirming consistency with documented objectives and risk tolerance.",

        "Recommended {product} as part of a diversified asset allocation strategy designed to support the client's stated objectives."
    ],

    "Senior_Low": [

        "Allocation to {product} completed following comprehensive suitability review and confirmation of long-term objectives.",

        "Trade implemented to support strategic portfolio positioning while maintaining consistency with client risk parameters.",

        "Recommendation reflects documented objectives, investment horizon, and current portfolio construction considerations."
    ],

    # ------------------------------------------------------
    # Medium Risk Advisors
    # ------------------------------------------------------

    "Junior_Medium": [

        "Client requested exposure to {product}. Risks reviewed and trade processed following discussion of suitability considerations.",

        "Executed trade in {product} after discussing expected volatility and alignment with client objectives.",

        "Client expressed interest in expanding exposure to {product}; suitability factors reviewed before execution."
    ],

    "Mid_Medium": [

        "Trade completed in {product} to pursue potential growth opportunities while monitoring overall portfolio risk.",

        "Recommended allocation to {product} based on current market conditions and client investment objectives.",

        "Position established following client discussion regarding potential return expectations and associated risks."
    ],

    "Senior_Medium": [

        "Client requested increased exposure to {product}; recommendation approved following suitability assessment.",

        "Trade executed after discussion of market opportunities and associated risk factors.",

        "Recommendation intended to support portfolio objectives while acknowledging elevated market uncertainty."
    ],

    # ------------------------------------------------------
    # High Risk Advisors
    # ------------------------------------------------------

    "Junior_High": [

        "Client requested immediate purchase of {product}. Risks discussed and trade processed per client instruction.",

        "Trade executed following client request to pursue higher potential returns despite elevated volatility.",

        "Client expressed strong conviction regarding {product}; transaction completed after brief suitability discussion."
    ],

    "Mid_High": [

        "Position established in {product} to capitalize on anticipated market opportunities. Client acknowledged increased risk.",

        "Trade completed following client request for additional exposure despite elevated volatility expectations.",

        "Recommendation focused on return potential while recognizing deviation from more conservative positioning."
    ],

    "Senior_High": [

        "Client directed allocation into {product}. Risks discussed and documented prior to execution.",

        "Trade completed based on client conviction regarding future performance of {product}.",

        "Recommendation pursued despite elevated risk characteristics after client confirmed desire to proceed."
    ]
}


# ==========================================================
# NOTES TEMPLATES
# ==========================================================

NOTES = {

    "Junior_Low": [

        "Detailed educational discussion completed. Client demonstrated understanding of product risks and expected outcomes.",

        "Onboarding documentation reviewed and client questions addressed during suitability discussion.",

        "Client confirmed understanding of investment objectives and associated risks."
    ],

    "Mid_Low": [

        "Suitability review completed successfully. No material concerns identified during discussion.",

        "Portfolio impact reviewed and found consistent with documented investment profile.",

        "Client confirmed financial circumstances remain unchanged since last review."
    ],

    "Senior_Low": [

        "Annual review completed. Existing objectives and risk profile remain appropriate.",

        "Comprehensive portfolio review performed with no material suitability concerns identified.",

        "Client remains comfortable with current strategy and long-term investment approach."
    ],

    "Junior_Medium": [

        "Client required additional discussion regarding volatility expectations before proceeding.",

        "Some uncertainty observed regarding long-term expectations; additional education provided.",

        "Suitability factors reviewed due to client interest in higher-risk opportunities."
    ],

    "Mid_Medium": [

        "Trade increases exposure to existing position. Concentration monitored as part of ongoing review.",

        "Client expressed interest in improving returns while maintaining overall portfolio discipline.",

        "Market volatility discussed during suitability review."
    ],

    "Senior_Medium": [

        "Recommendation involves elevated risk relative to some existing holdings but remains within profile limits.",

        "Client acknowledged current market uncertainty before authorizing transaction.",

        "Portfolio concentration metrics reviewed as part of trade approval process."
    ],

    "Junior_High": [

        "Client appeared highly focused on recent market performance during discussion.",

        "Limited suitability discussion completed due to client desire for rapid execution.",

        "Additional documentation may be warranted if trading activity continues."
    ],

    "Mid_High": [

        "Trade increases concentration exposure and should be monitored during future reviews.",

        "Client demonstrated strong conviction regarding speculative opportunity.",

        "Potential profile drift noted and may require follow-up review."
    ],

    "Senior_High": [

        "Client requested transaction despite discussion of downside risk considerations.",

        "Trade reflects elevated risk appetite relative to portions of existing portfolio.",

        "Recommendation may warrant additional supervisory review depending on future activity."
    ]
}


# ==========================================================
# SPECIAL CASE TEXT
# ==========================================================

MISSING_RATIONALE_TEXT = (
    ""
)

WEAK_RATIONALE_TEXT = (
    "Client requested purchase."
)

MINIMAL_NOTE_TEXT = (
    "Standard client interaction completed."
)


# ==========================================================
# Helpers
# ==========================================================

def advisor_bucket(trade: Trade) -> str:

    return (
        f"{trade.advisor_experience}_"
        f"{trade.advisor_history_risk}"
    )


def generate_rationale(trade: Trade) -> str:

    bucket = advisor_bucket(trade)

    templates = RATIONALES.get(bucket)

    if not templates:
        return MISSING_RATIONALE_TEXT

    template = random.choice(templates)

    return template.format(
        product=trade.investment_type,
        objective=trade.investment_objective.lower(),
        horizon=trade.investment_time_horizon.lower()
    )


def generate_notes(trade: Trade) -> str:

    bucket = advisor_bucket(trade)

    templates = NOTES.get(bucket)

    if not templates:
        return MINIMAL_NOTE_TEXT

    return random.choice(templates)


# ==========================================================
# Scenario Overrides
# ==========================================================

def apply_text_overrides(
    trade: Trade,
    scenario_name: str
) -> Trade:
    """
    Injects scenario-specific language.

    This creates realistic documentation quality
    differences that can later be surfaced in UI.
    """

    # --------------------------------------
    # Missing rationale scenario
    # --------------------------------------

    if scenario_name == "KYC Missing":

        trade.advisor_rationale = MISSING_RATIONALE_TEXT

        trade.advisor_notes = (trade.advisor_notes or "") + (
            " Client information appears incomplete."
        )

    # --------------------------------------
    # Low priority exception
    # --------------------------------------

    elif scenario_name == "Low Priority Exception":

        trade.advisor_rationale = WEAK_RATIONALE_TEXT

        trade.advisor_notes = (
            "Client requested transaction. "
            "No additional concerns documented."
        )

    # --------------------------------------
    # Compound violation
    # --------------------------------------

    elif scenario_name == "Compound Violation":

        trade.advisor_notes = (trade.advisor_notes or "") + (
            " Client insisted on proceeding despite "
            "discussion of elevated risks."
        )

    return trade


# ==========================================================
# Main Entry Point
# ==========================================================

def enrich_trade_text(
    trade: Trade,
    scenario_name: str
) -> Trade:

    trade.advisor_rationale = generate_rationale(trade)

    trade.advisor_notes = generate_notes(trade)

    trade = apply_text_overrides(
        trade,
        scenario_name
    )

    return trade