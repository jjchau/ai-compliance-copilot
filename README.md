# AI Compliance Review Copilot
A human-in-the-loop, RAG-enabled decision-support workflow for investment compliance review.

## 1. Overview
This project implements and evaluates a human-in-the-loop, RAG-enabled workflow for reviewing simulated investment recommendations, with a focus on safe routing, regulatory risk, reviewer burden, confidence calibration, and evidence-based decision support.

The project combines a functional AI evaluation pipeline, risk-based workflow routing, retrieval diagnostics, and a reviewer dashboard prototype. Its purpose is to assess where automation may be appropriate and where human review remains necessary.

## 2. Problem
Wealth management firms must review advisor investment recommendations for regulatory and suitability risks, but human-only review is difficult to scale. Existing rule-based systems can generate large volumes of low-quality alerts while struggling with complex cases and unstructured client-advisor information, contributing to reviewer backlogs and inconsistent decisions.

The product challenge is not simply to maximize model accuracy, but to automate each case at the lowest safe workflow level while minimizing both missed compliance risks and unnecessary reviewer escalation.

## 3. Product Concept
Simulated advisor recommendation
        ↓
Policy retrieval
        ↓
AI compliance assessment
        ↓
Compliance probability, risk and confidence scoring
        ↓
Workflow routing
        ↓
Auto-pass / Queue / Priority / Urgent
        ↓
Human review and audit logging

## 4. Implemented Scope
### 4.1. AI and decision pipeline:
- Synthetic recommendation generation and labeling
- Policy retrieval using RAG
- Structured compliance assessment
- Compliance probability, risk, and confidence scoring
- Rule- and signal-based workflow routing
- Audit event generation

### 4.2. Evaluation:
- Classification and routing accuracy
- Safety and reviewer-burden metrics
- Retrieval diagnostics
- Confidence and overconfidence analysis
- Trust proxy analysis
- Failure-mode analysis

### 4.3. Reviewer experience:
- Dashboard prototype for case triage
- Structured case and evidence summaries
- Approve, reject, and escalate actions
- Reviewer comments and audit history

## 5. Evaluation Question
**Can the system correctly resolve investment compliance cases at the lowest safe workflow level while limiting regulatory risk and unnecessary reviewer escalation?**

## 6. Dataset and Assumptions
|Component|Description|
|:--------|:----------|
|Cases|1000 synthetic advisor investment recommendations stratified across 13 compliance scenario types (including 1 "aligned," 3 "hard violation," and 10 "risk signal" scenario types), 4 client profile archetypes, and 9 different advisor experience and risk profile combinations, representing a simplified yet sufficiently complex model of the target domain. 220 cases were used for training, 780 cases were used for testing.|
|Policy corpus|10 synthetic internal-policy documents modeled on themes reflected in publicly accessible [HighPoint Advisor Group](https://highpointplanningpartners.com/wp-content/uploads/2024/03/Compliance-Manual-11-2022.pdf) and [AE Wealth Management](https://aewealthmanagement.com/advisor-login/wp-content/uploads/sites/7/2022/09/Compliance-Policy-Manual_AEWM_Jan-10-2023_FINAL.pdf) compliance manuals, supplemented by broader Canadian and U.S. wealth-management compliance concepts. The corpus is simplified for evaluation and does not reproduce either firm’s policies. Two of the ten policy documents in the corpus are not relevant to current case data but were left in as "noise" to challenge the implemented system's precision.|
|Ground truth|Expected compliance (*true* or *false*), relevant policies, primary relevant policy, and workflow routing (*urgent*, *priority*, *queue*, and *auto-pass*) values annotated per case using programmatically determined rule-based logic. Workflow routing represents the urgency bucket with which human compliance reviewers need to manually review case data to minimize overall legal and/or regulatory exposure to the firm in this framework.|
|AI model|Gemini 3.1 Flash-Lite used for structured assessment of cases. It's assumed this LLM has enough sophistication to reason with sufficient scope and accuracy as embodied by the case variations and 10-document policy corpus of this project.|
|Risk score|A deterministic rule-base score calculated per case to represent the potential downside impact of a false negative (i.e. a missed compliance violation case) to the investment firm.| 
|Confidence||
|Human behaviour||

## 7. Evaluation Scorecard
### Product Safety and Workflow Outcomes:
|Metric|Result|Product interpretation|
|:-----|:-----|:---------------------|
|North Star Metric|77.7%|Percentage of cases the system resolved at the lowest safe workflow level|
||||

### Trust and Confidence:
|Metric|Result|Product interpretation|
|:-----|:-----|:---------------------|
|Overconfidence Rate|||

### Retrieval and System Diagnostics:
|Metric|Result|Product interpretation|
|:-----|:-----|:---------------------|
|Primary Policy Retrieval Rate|||


## 8. Key Findings

## 9. Product Recommendation

## 10. Reviewer Workflow Prototype

## 11. Limitations and Next Steps

## 12. Repository Guide

## 13. Setup and Reproduction


## Tech Stack
- Python
- (Optional) FastAPI
- (Optional) React / simple frontend

## Project Structure
```
ai-compliance-copilot/
│
├── README.md
├── requirements.txt
├── .gitignore
├── .venv/                              # Virtual environment (ignored)
|
├── docs/
│   ├── product_vision.md
│   ├── product_requirements.md
│   ├── user_persona.md
│   ├── metric_hierarchy.md
│   ├── risk_register.md
│   ├── definition_of_ready.md
│   ├── definition_of_done.md
│   └── data_schema.md
│
├── data/
│   ├── raw/                            # Generated or source datasets
|   │   └── simulated_cases.json        # Simulated dataset for testing
│   ├── processed/                      # Cleaned / transformed data
|   │   └── labeled_cases.json          # Ground truth + expected outcomes
│   ├── schema.json                     # Case schema definition
│
├── configs/
│   └── thresholds.yaml                 # Decision thresholds
│
├── src/
│   ├── data/
│   │   └── generator.py                # Simulated data generation
│   │
│   ├── scoring/
│   │   ├── risk_scoring.py             # Risk scoring logic
│   │   ├── confidence_scoring.py       # Confidence scoring
│   │   └── compliance_scoring.py       # Compliance prediction
│   │
│   ├── decisioning/
│   │   ├── decision_engine.py          # Decision orchestration
│   │   └── policy_rules.py             # Escalation/Approval rules
│   │
│   ├── logging/
│   │   └── audit_logger.py             # Audit logging logic
│   │
│   ├── evaluation/
│   │   ├── metrics.py
│   │   ├── calibration.py
│   │   └── error_analysis.py
│   │
│   └── api/                            # (Optional - later)
│       └── app.py
|
├── sql/
│   ├── schema/
│   │   └── create_tables.sql
│   └── queries/
|
├── frontend/
|
├── notebooks/                          # Exploration / evaluation (optional)
|   └── analysis/
│
├── tests/                              # Unit tests (optional for now)
|   ├── test_scoring.py
|   └── test_pipeline.py
|
└── logs/
    └── sample_logs.json                # Generated logs
```

## Setup
```bash
pip install -r requirements.txt

## Run
python notebooks/S1_evaluation.ipynb

## Status
Sprint 1 in progress
