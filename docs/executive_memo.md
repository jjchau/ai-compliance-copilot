# Executive Memo: AI Compliance Review Copilot

## Problem

Compliance teams in wealth management must review advisor investment recommendations for suitability and regulatory risk. Human-only review is difficult to scale, while traditional rules-based alerting can create excessive reviewer burden and still miss complex cases.

The core product problem is not simply whether AI can classify a recommendation as compliant or non-compliant. For this prototype, I defined the harder product challenge as determining whether AI-assisted signals and deterministic routing logic could identify the lowest safe workflow level for each case: auto-pass for low-risk cases, queue for standard human review, priority for higher-risk review, and urgent for the highest-risk cases requiring immediate attention.

## Proposed Solution

I built an AI Compliance Review Copilot: a human-in-the-loop, RAG-enabled decision-support workflow for simulated investment compliance review.

The prototype combines:

- RAG-based retrieval over a synthetic compliance-policy corpus
- Structured AI signal extraction using case data and retrieved policy evidence
- Deterministic scoring and routing logic that converts AI-extracted signals into workflow decisions
- Audit logging for decision traceability
- Evaluation notebooks for metric analysis, retrieval diagnostics, and failure-mode analysis
- A reviewer dashboard prototype for triage, evidence review, and decision history

The product goal was to evaluate whether AI could safely reduce reviewer workload while preserving escalation for higher-risk cases.

## Evaluation Results

The system was evaluated on a 780-case held-out dataset after development and tuning on a separate 220-case set.

| Area | Result | Interpretation |
|---|---:|---|
| Workflow-routing accuracy / North Star Metric | 79.6% | Most cases were routed correctly, but routing remained the main product constraint. |
| Compliance accuracy | 99.7% | The system was strong at classifying compliance outcomes. |
| Compliance false-negative rate | 0.0% | No non-compliant cases were incorrectly classified as compliant. |
| Urgent case recall | 35.4% | Many urgent cases were routed to priority rather than urgent review. |
| Auto-pass over-escalation | 33.5% | Many low-risk cases were unnecessarily escalated to review workflows. |
| Escalation precision | 84.7% | Escalations were usually justified by the ground-truth review requirement. |
| Primary policy retrieval rate | 66.0% | Retrieval often found relevant evidence, but did not reliably surface the most important policy. |

The key result is that compliance classification was strong, but workflow routing was not yet reliable enough for unattended automation.

## Product Implication

The prototype is promising as a reviewer decision-support system: it can organize case queues, surface policy evidence, present structured AI rationale, and support auditability.

However, the results do not support autonomous compliance review. Urgent-case recall was too low, and primary-policy retrieval was inconsistent. The system was generally conservative, favouring regulatory caution over efficiency, but this created reviewer burden through unnecessary escalation.

A follow-up retrieval benchmark showed that improving retrieval quality did not materially improve the end-to-end workflow-routing metric. This was an important product finding: better subsystem metrics do not automatically translate into better product outcomes.

The remaining bottleneck is likely a combination of routing thresholds, risk scoring, confidence scoring, retrieval quality, and alignment between ground-truth workflow labels and prediction logic.

## Recommendation

The current system should be positioned as a human-in-the-loop compliance review copilot, not an autonomous decision system.

Recommended next steps:

- Improve urgent-case routing so high-risk cases receive the intended review priority.
- Reduce unnecessary escalation of low-risk cases without increasing false negatives.
- Improve primary-policy retrieval and reduce irrelevant context.
- Validate revised logic on a new untouched held-out dataset.
- Review labels, thresholds, and workflow assumptions with compliance-domain experts.
- Validate the prototype with compliance-domain users, including reviewer workflow fit, trust calibration, explanation usefulness, and feedback loops.

A limited future auto-pass capability may be appropriate for narrowly defined low-risk cases, but only after additional held-out validation confirms that safety metrics remain stable.

## Project Significance

This project demonstrates applied AI product judgment in a high-stakes workflow. The main takeaway is not production readiness, but the disciplined evaluation of where AI can and cannot safely support compliance review. The value is in showing how to define the right product-level metric, evaluate AI performance beyond model accuracy, identify safety and workflow tradeoffs, and translate evaluation results into a practical product recommendation.

The project reflects the kind of work required for AI product management, AI evaluation, and human-in-the-loop workflow design: building a working prototype, measuring it against operational goals, identifying where automation is appropriate, and knowing where human review must remain in control.