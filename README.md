# AI Compliance Copilot (Prototype)

## Overview
AI copilot system for reviewing financial advisor recommendations for compliance risk, with an integrated evaluation framework.

## Problem
Manual compliance review is slow, error-prone, and does not scale.

## Solution
Human-in-the-loop AI system that:
- Flags high-risk and low-confidence cases
- Provides structured summaries
- Enables reviewer overrides
- Logs all decisions for audit

## Features (MVP)
- Rule-based compliance prediction
- Risk scoring
- Confidence scoring
- Flagging engine
- Dashboard UI (planned)
- Audit logging

## Evaluation Framework
Includes:
- Precision / Recall
- Calibration metrics (ECE, TCI)
- Trust metrics
- Error analysis

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