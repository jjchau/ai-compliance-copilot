# Product Requirements Document 

## 1. Problem Statement 

Human financial advisor investment recommendations that breach regulatory requirements can result in severe consequences for customers, advisors, and firms. However, human-only compliance review is infeasible at scale, and existing rule-based automated compliance systems generate high volumes of low-quality alerts, struggle with complex portfolios, and cannot effectively interpret unstructured client-advisor communications. As a result, compliance teams face long alert backlogs, fragmented data across systems, portfolios, and jurisdictions, and inconsistent decision-making across reviewers and over time, limiting their ability to identify true compliance risks in a consistent and timely manner. 

## 2. Users 

Compliance reviewers of financial advisor recommendations at investment firms. 

## 3. Proposed System 

A human-in-the-loop AI compliance review copilot for advisor investment recommendations. The system retrieves relevant policy evidence, uses AI to extract structured compliance signals from case data and retrieved context, and applies deterministic scoring and routing logic to recommend the lowest safe workflow level: auto-pass, queue, priority, or urgent review.

## 4. Value Proposition 

AI-assisted compliance review that helps teams prioritize high-risk cases, surface relevant policy evidence, and reduce unnecessary reviewer burden while keeping human review in control for higher-risk or uncertain cases.

## 5. Goals & Success Metrics

1. Improve safe workflow routing
   - Measure: % cases correctly resolved at the lowest safe workflow level
   - Workflow levels: auto-pass, queue, priority, urgent

2. Preserve compliance safety
   - Measure: compliance false-negative rate
   - Measure: urgent-case recall
   - Measure: unsafe auto-pass rate

3. Improve review efficiency
   - Reduce unnecessary escalation of low-risk cases
   - Prioritize higher-risk cases earlier in the reviewer workflow
   - Operational metrics would include case throughput per reviewer and review time per case

4. Support reviewer trust and auditability
   - Provide structured rationale, retrieved policy evidence, and decision traceability
   - Validation criteria would include explanation usefulness, reviewer workflow fit, appropriate reliance, and override behaviour

5. Evaluate trust dynamics using a simulated proxy
   - Measure whether simulated reviewer trust improves or degrades over sequential case outcomes
   - Penalize confidently incorrect decisions more heavily than cautious or recoverable errors
   - Treat the trust proxy as an analytical model for reasoning about trust dynamics, not as validated evidence of real reviewer trust

## 6. Scope (MVP) 

The initial MVP will prototype core system capabilities across four epics: 

1. Advisor recommendation workflow routing
    - Routing cases to the lowest safe workflow level based on compliance signals, risk, and confidence
    - Escalating high-risk, low-confidence, or potentially non-compliant cases for human review
2. Human compliance review 
    - Presenting routed cases in a structured summary on screen for quick human understanding
    - Sorting review cases by risk and urgency so human reviewers can tackle the highest-priority cases first
3. AI assessment explainability 
    - Producing AI-extracted signals in a structured format suitable for deterministic scoring and audit logging
    - Showing structured AI-extracted signals, rationale, and retrieved policy evidence for human reviewers to inspect 
4. Human case control 
    - Allowing human reviewers to manually override the AI’s case assessments and enter case review notes 

## 7. Future Considerations 

The following capabilities will be considered for future product iterations: 

1. Decision support 
    - Surfacing and showing similar past cases to assist user on borderline cases 
2. Feedback learning loop 
    - Logging reviewer feedback as input for improving AI via governed learning loops 
3. Interactive chat 
    - Answering follow-up questions on trade assessments from human reviewers 
    - Providing AI feedback on human reviewer assessments 
4. Reviewer collaboration controls
    - Marking cases as "in review" to avoid duplicate work across reviewers
    - Assignment, ownership, and queue-management controls

## 8. Non-goals (MVP) 

1. Advisor-facing interactions 
2. Autonomous compliance adjudication or broad unattended deployment 
3. Continuous learning based on reviewer feedback 

## 9. User Workflow 

1. Advisor submits recommendation / trade. 
2. The system retrieves relevant policy context, uses AI to extract structured compliance signals, and applies deterministic scoring and routing logic to generate a compliance outcome, confidence proxy, risk score, and workflow route.
3. Cases routed to queue, priority, or urgent review are displayed in a risk-prioritized reviewer dashboard.
4. Compliance reviewers select cases from a risk-prioritized dashboard for review.
5. Compliance reviewer reviews the structured case summary, AI-extracted signals, rationale, and retrieved policy evidence. 
6. Compliance reviewer accepts or overrides the AI’s assessment of the case and can add notes to be logged with a timestamped record of their review. If no notes are input, the system will generate a warning message for the reviewer, which the reviewer may choose to ignore. 

## 10. Requirements

Requirements were implemented through user stories covering policy retrieval, AI signal extraction, deterministic scoring, workflow routing, reviewer dashboard functionality, audit logging, and evaluation diagnostics. The implemented scope is summarized in the README and evaluated in the accompanying notebooks.