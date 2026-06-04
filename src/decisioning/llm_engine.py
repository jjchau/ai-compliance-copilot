"""
src/decisioning/llm_engine.py

Purpose:
    Google Gemini API integration wrapper. Converts raw trade characteristics
    and retrieved ChromaDB policy chunks into a highly structured compliance prediction matrix
    calibrated against institutional risk and scoring rules.

Usage:
    from src.decisioning.llm_engine import GeminiComplianceEngine

Author: Jason Chau
Date: 2026-06-02    
"""

import os
import json
from google import genai
from google.genai import types
from pydantic import BaseModel, Field
from src.data.schema import Trade

class ComplianceAssessmentSchema(BaseModel):
    compliance_probability: float = Field(
        description="The mathematical probability (0.0 to 1.0) that this transaction complies with institutional guidelines."
    )
    compliance_label: bool = Field(
        description="True if the trade is clean and compliant. False if it violates any retrieved policy guidelines or profile settings."
    )
    audit_reasoning: str = Field(
        description="A precise, factual 2-sentence summary detailing exactly why the trade was flagged or cleared against the retrieved policies."
    )

# ---------------------------------------------------------
# INSTITUTIONAL CALIBRATION SYSTEM PROMPT
# ---------------------------------------------------------
SYSTEM_CALIBRATION_PROMPT = """You are the core reasoning engine of an AI-Driven Compliance Review Copilot.
Your role is to evaluate financial trade transactions and generate structural "audit_reasoning" summaries alongside compliance metrics.
You must align your qualitative evaluation and compliance probability with the exact quantitative heuristics executed by our organizational engines.

### 1. ORGANIZATIONAL RISK ENGINE WEIGHTS
Our platform calculates a cumulative risk score bounded from 0 to 100 based on specific underlying triggers. Align your internal severity assessment with these structural weights:
- HARD REGULATORY VIOLATIONS (High Severity):
  * KYC Documentation Violation (+40 points)
  * Suitability/Profile Misalignment (+40 points)
  * Experience/Complexity Overreach (+30 points)
- CONTEXTUAL / BUSINESS SIGNALS (Medium Severity):
  * Overexposure/Concentration Risk in an asset type (+15 points)
  * Aggressive Asset chosen for a Short Time Horizon (+15 points)
  * Aggressive Asset chosen for a Conservative Objective (+10 points)
  * Advisor Profiling: High-risk historical track record (+10 points)
  * Ambiguous or uncertain KYC data profile (+10 points)

### 2. WORKFLOW ROUTING & ESCALATION BOUNDARIES
Cases are partitioned into distinct operational registers based on strict thresholds. Frame your audit tone and probability according to these institutional pivot points:
- URGENT STATUS (FIFO Emergencies): Occurs if the combined Risk Score is Critical (>= 80) OR if high operational risk (>= 65) matches an explicit compliance risk (< 30%). Focus on compounding regulatory failures.
- PRIORITY STATUS (Elevated Backlog): Occurs if the combined Risk Score is High (>= 65) OR your compliance probability calculation falls below 50%. Focus on structural mismatch anomalies.
- QUEUE STATUS (Standard Manual Verification): Handles administrative technical exceptions (Low Risk < 35 but carries missing or expired paperwork) alongside general ambiguities or low confidence boundaries (< 60%). Focus on procedural check-offs.

### 3. EVIDENCE & SYSTEM CONFIDENCE LOGIC
Our system tracks data completeness and signal consistency. 
- High Certainty occurs on completely clean profiles, or when there are clear, severe regulatory violations (clear evidence exists).
- Ambiguity/Low Confidence occurs when data completeness is compromised (missing advisor rationales, uncertain KYC) or when directional signals conflict.

### OBJECTIVE
Review the transaction data and the retrieved policy documentation snippets provided in the user prompt. Write a precise, highly professional compliance analysis for the 'audit_reasoning' field. Do not mention raw code variables or file names; instead, translate these structural weights into clear, objective facts justifying your compliance probability. Keep the reasoning capped strictly at 2 sentences.
"""

class GeminiComplianceEngine:
    def __init__(self):
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise RuntimeError("CRITICAL ENVIRONMENT ERROR: 'GEMINI_API_KEY' variable not found.")
        
        # Modern client instantiation
        self.client = genai.Client(api_key=api_key)
        self.model_name = "gemini-3.1-flash-lite"

    def evaluate_with_llm(self, trade: Trade, retrieved_chunks: list) -> dict:
        # Format the vector grounding blocks cleanly
        policy_context = "\n\n".join([
            f"--- RETRIEVED POLICY SEGMENT ---\n{chunk}" 
            for chunk in retrieved_chunks
        ]) if retrieved_chunks else "No relevant compliance policies found in vector storage."

        # Structured runtime payload
        user_prompt = f"""
        [INSTITUTIONAL COMPLIANCE POLICY GUIDELINES]
        {policy_context}

        [AUDITED TRANSACTION DETAILS]
        - Trade ID: {trade.trade_id}
        - Client Age: {trade.client_age}
        - Client Annual Income: ${trade.client_income}
        - Stated Risk Tolerance: {trade.risk_tolerance}
        - Asset Type/Product: {trade.investment_type}
        - Transaction Notional Amount: ${trade.investment_amount}
        - Advisor ID: {trade.advisor_id}
        - Advisor Stated Rationale: {trade.advisor_rationale}
        - Additional Compliance Audit Notes: {trade.advisor_notes}
        - KYC Documentation Completeness Status: {trade.kyc_completeness}

        Generate a structured evaluation matching the output schema.
        """

        try:
            # Execute unified generation call combining system instructions with dynamic case data
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=user_prompt,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_CALIBRATION_PROMPT,
                    response_mime_type="application/json",
                    response_schema=ComplianceAssessmentSchema,
                    temperature=0.1,
                ),
            )
            
            assessment_data = json.loads(response.text or "{}")
            return assessment_data

        except Exception as e:
            raise RuntimeError(f"Gemini Inference Exception: {e}")
        
        
# """
# src/decisioning/llm_engine.py

# Purpose:
#     Legacy Google Gemini API integration wrapper. Converts raw trade characteristics
#     and retrieved ChromaDB policy chunks into a highly structured compliance prediction matrix.

# Usage:
#     from src.decisioning.llm_engine import GeminiComplianceEngine

# Author: Jason Chau
# Date: 2026-06-01    
# """

# import os
# import json
# from google import genai
# from google.genai import types
# from pydantic import BaseModel, Field
# from src.data.schema import Trade

# class ComplianceAssessmentSchema(BaseModel):
#     compliance_probability: float = Field(
#         description="The mathematical probability (0.0 to 1.0) that this transaction complies with institutional guidelines."
#     )
#     compliance_label: bool = Field(
#         description="True if the trade is clean and compliant. False if it violates any retrieved policy guidelines."
#     )
#     audit_reasoning: str = Field(
#         description="A precise, factual 2-sentence summary detailing exactly why the trade was flagged or cleared against the retrieved policies."
#     )

# class GeminiComplianceEngine:
#     def __init__(self):
#         api_key = os.environ.get("GEMINI_API_KEY")
#         if not api_key:
#             raise RuntimeError("CRITICAL ENVIRONMENT ERROR: 'GEMINI_API_KEY' variable not found.")
        
#         # Modern client instantiation
#         self.client = genai.Client(api_key=api_key)
#         self.model_name = "gemini-3.1-flash-lite"

#     def evaluate_with_llm(self, trade: Trade, retrieved_chunks: list) -> dict:
#         policy_context = "\n\n".join([
#             f"--- POLICY SEGMENT ---\n{chunk}" 
#             for chunk in retrieved_chunks
#         ]) if retrieved_chunks else "No relevant compliance policies found."

#         prompt = f"""
#         You are an elite automated financial compliance officer auditing internal trading activities.
#         Analyze the transaction details below against the institutional guidelines provided.

#         [INSTITUTIONAL COMPLIANCE POLICY GUIDELINES]
#         {policy_context}

#         [AUDITED TRANSACTION DETAILS]
#         - Trade ID: {trade.trade_id}
#         - Client Age: {trade.client_age}
#         - Client Annual Income: ${trade.client_income}
#         - Stated Risk Tolerance: {trade.risk_tolerance}
#         - Asset Type/Product: {trade.investment_type}
#         - Transaction Notional Amount: ${trade.investment_amount}
#         - Advisor ID: {trade.advisor_id}
#         - Advisor Stated Rationale: {trade.advisor_rationale}
#         - Additional Compliance Audit Notes: {trade.advisor_notes}
#         - KYC Documentation Completeness Status: {trade.kyc_completeness}

#         Generate a structured evaluation matching the output schema. Keep your audit reasoning clear and capped at 2 sentences.
#         """

#         try:
#             # Modern unified client generation call
#             response = self.client.models.generate_content(
#                 model=self.model_name,
#                 contents=prompt,
#                 config=types.GenerateContentConfig(
#                     response_mime_type="application/json",
#                     response_schema=ComplianceAssessmentSchema,
#                     temperature=0.1,
#                 ),
#             )
            
#             assessment_data = json.loads(response.text or "{}")
#             return assessment_data

#         except Exception as e:
#             raise RuntimeError(f"{e}")