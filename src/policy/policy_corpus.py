POLICY_CORPUS = {

    # --- KYC / DATA INTEGRITY ---
    "POLICY_KYC_001": {
        "title": "KYC Completeness Requirement",
        "category": "KYC",
        "text": "All required client information must be collected and verified before executing any trade.",
        "severity": "critical",
        "tags": ["kyc", "data_completeness", "blocking"]
    },

    "POLICY_KYC_002": {
        "title": "KYC Accuracy and Consistency",
        "category": "KYC",
        "text": "Client information must be accurate, consistent, and updated to reflect current circumstances before making recommendations.",
        "severity": "high",
        "tags": ["kyc", "data_quality"]
    },

    # --- SUITABILITY ---
    "POLICY_SUIT_001": {
        "title": "Risk Tolerance Alignment",
        "category": "Suitability",
        "text": "Investment recommendations must align with the client’s stated risk tolerance.",
        "severity": "critical",
        "tags": ["suitability", "risk_profile"]
    },

    "POLICY_SUIT_002": {
        "title": "Investment Objective Alignment",
        "category": "Suitability",
        "text": "Investments must be consistent with the client’s stated financial objectives.",
        "severity": "high",
        "tags": ["suitability", "objective"]
    },

    "POLICY_SUIT_003": {
        "title": "Time Horizon Suitability",
        "category": "Suitability",
        "text": "Short-term investment horizons should not be exposed to high-volatility or illiquid assets.",
        "severity": "high",
        "tags": ["suitability", "horizon"]
    },

    # --- EXPERIENCE / PRODUCT COMPLEXITY ---
    "POLICY_EXP_001": {
        "title": "Product Complexity vs Experience",
        "category": "Suitability",
        "text": "Complex financial instruments should only be recommended to clients with sufficient investment knowledge and experience.",
        "severity": "critical",
        "tags": ["experience", "complexity"]
    },

    # --- PORTFOLIO RISK ---
    "POLICY_RISK_001": {
        "title": "Concentration Risk",
        "category": "Risk",
        "text": "Client portfolios should avoid excessive concentration in a single asset or asset class.",
        "severity": "medium",
        "tags": ["risk", "concentration"]
    },

    "POLICY_RISK_002": {
        "title": "Leverage Suitability",
        "category": "Risk",
        "text": "Leveraged investment strategies must only be recommended to clients who can تحمل the associated risks and losses.",
        "severity": "high",
        "tags": ["risk", "leverage"]
    },

    # --- DOCUMENTATION / PROCESS ---
    "POLICY_DOC_001": {
        "title": "Advisor Rationale Requirement",
        "category": "Documentation",
        "text": "Advisors must provide clear, documented rationale for all investment recommendations.",
        "severity": "medium",
        "tags": ["documentation", "rationale"]
    },

    # --- SUPERVISION ---
    "POLICY_SUP_001": {
        "title": "Enhanced Supervision Requirement",
        "category": "Supervision",
        "text": "Recommendations from advisors with prior compliance issues must be subject to additional review.",
        "severity": "medium",
        "tags": ["supervision", "advisor_risk"]
    },

    # --- CLIENT INTEREST ---
    "POLICY_CLIENT_001": {
        "title": "Client Interest First",
        "category": "Suitability",
        "text": "All recommendations must prioritize the client’s interests over the advisor’s or firm’s interests.",
        "severity": "critical",
        "tags": ["fiduciary", "ethics"]
    },

    # --- CONSISTENCY CHECKS ---
    "POLICY_KYC_003": {
        "title": "KYC Internal Consistency",
        "category": "KYC",
        "text": "Client profiles must not contain conflicting attributes (e.g., low risk tolerance with speculative objective).",
        "severity": "high",
        "tags": ["kyc", "consistency"]
    }
}