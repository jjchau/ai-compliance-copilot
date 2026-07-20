# Metric Hierarchy

## 1. Purpose

This document defines the evaluation framework for the AI Compliance Review Copilot.

The goal of the metric hierarchy is to evaluate whether the system can safely support human compliance review, route cases to the appropriate workflow level, reduce unnecessary reviewer burden, and provide evidence-backed, auditable decision support.

Metrics are grouped into:

- North Star Metric
- MVP evaluation metrics
- Supporting diagnostics
- Future validation candidates

This document defines what should be measured and why. Metric definitions are kept separate from evaluation results so the framework can remain stable as experiments and artifacts evolve.

## 2. North Star Metric

**% cases correctly resolved at the lowest safe workflow level**

This measures whether the system routes each case to the least burdensome workflow level that still protects against compliance risk.

Workflow levels:

- Auto-pass: low-risk case can be resolved without human review
- Queue: standard human review
- Priority: higher-risk human review
- Urgent: highest-risk cases requiring immediate attention

Formula:

`North Star Metric = cases correctly resolved at the lowest safe workflow level / total cases`

Why it matters:

- Accuracy alone does not capture whether the case was routed to the right workflow.
- A compliant case sent to unnecessary review creates operational burden.
- A high-risk case routed below the required priority creates safety and timeliness risk.

## 3. MVP Evaluation Metrics

These metrics are required to evaluate whether the prototype is credible as a human-in-the-loop decision-support workflow.

### 3.1 Compliance safety

- Compliance classification accuracy
- Compliance false-negative rate
- Unsafe auto-pass rate
- Urgent-case recall

Purpose:

- Ensure the system does not miss non-compliant or high-risk cases.
- Treat false compliance and under-prioritized urgent cases as higher-severity failures than unnecessary escalation.

### 3.2 Reviewer workload and review efficiency

- Workflow-routing accuracy
- Auto-pass over-escalation
- Escalation precision
- Failure-mode breakdown by route transition

Purpose:

- Measure whether the system reduces reviewer burden without weakening safety.
- Identify whether errors are mainly unsafe under-routing or conservative over-routing.

### 3.3 Retrieval quality

- Selected-policy precision: proportion of policies included in the final LLM context that are labelled relevant
- Selected-policy recall: proportion of labelled relevant policies included in the final LLM context
- Primary policy retrieval rate: whether the most important relevant policy was included in the final context
- Any relevant policy retrieval rate: whether at least one relevant policy was included

Purpose:

- Evaluate whether the system surfaces useful policy evidence for AI signal extraction and reviewer inspection.
- Distinguish broad-but-noisy retrieval from focused, high-value evidence retrieval.

### 3.4 Confidence and trust proxy

- Overconfidence rate
- Confidence vs. correctness alignment
- Simulated trust-proxy change over time

Purpose:

- Evaluate whether high-confidence outputs are reliable enough to support reviewer trust.
- Explore how repeated correct, incorrect, cautious, or overconfident outcomes could affect reviewer trust over time.

Note: the trust proxy is an analytical simulation and should not be interpreted as validated reviewer behaviour.

## 4. Supporting Diagnostics

These diagnostics help explain why the system succeeds or fails. They are secondary to the product-level metrics above.

### 4.1 Retrieval diagnostics

- Retrieval noise by scenario
- Retrieval coverage by policy
- Duplicate or repetitive retrieved policy context
- Primary policy rank in raw retrieval candidates

Purpose:

- Diagnose whether retrieval failures are caused by missing relevant policies, noisy context, duplication, or low ranking of the primary policy.
- Evaluate whether retrieval improvements translate into better downstream workflow-routing performance.

### 4.2 Confidence and calibration diagnostics

- Confidence distribution by correctness
- Confidence distribution by workflow route
- Expected Calibration Error
- Brier score

Purpose:

- Understand whether the confidence proxy aligns with observed correctness.
- Identify whether certain workflow routes are associated with lower confidence or higher error risk.

## 5. Future Validation Candidates

These metrics are valuable for later product validation but are outside the core synthetic offline evaluation.

### 5.1 Reviewer efficiency

- Review time per case
- Case throughput per reviewer
- Queue aging and time-to-review by workflow priority
- Reduction in manual policy lookup time

### 5.2 Reviewer behaviour and trust

- Reviewer acceptance / override rate
- Override correctness
- Explanation usefulness rating
- Appropriate reliance on AI-assisted recommendations
- Reviewer trust calibration

### 5.3 Operational deployment

- Latency from case submission to routing decision
- System uptime and failure recovery
- Audit-log completeness
- Security and access-control validation

### 5.4 AI signal quality validation

- Structured output validity / parsing success
- Missing or conflicting signal detection
- Rationale consistency with retrieved evidence
- Instruction adherence
- Logical consistency

These diagnostics would require additional schema-level validation, ground-truth signal labels, automated consistency checks, or human review of rationale quality.

## 6. Evaluation Design Principles

- Product-level workflow-routing quality is more important than isolated model accuracy.
- Compliance false negatives and unsafe auto-pass errors are higher-severity failures than unnecessary escalation.
- Retrieval improvements should be evaluated by downstream product impact, not only by retrieval metrics.
- Human-in-the-loop systems should be evaluated for both safety and reviewer burden.
- Trust-related metrics require real user validation before being treated as product adoption evidence.
- Diagnostic/tuning data should be separated from final validation data. Development cases are used for iteration and failure analysis; held-out cases are reserved for final evaluation after the pipeline is frozen.