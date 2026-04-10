# Product Requirements Document 

## 1. Problem Statement 

Human financial advisor investment recommendations that breach regulatory requirements can result in severe consequences for customers, advisors, and firms. However, human-only compliance review is infeasible at scale, and existing rule-based automated compliance systems generate high volumes of low-quality alerts, struggle with complex portfolios, and cannot effectively interpret unstructured client-advisor communications. As a result, compliance teams face long alert backlogs, fragmented data across systems, portfolios, and jurisdictions, and inconsistent decision-making across reviewers and over time, limiting their ability to identify true compliance risks in a consistent and timely manner. 

## 2. Users 

Compliance reviewers of financial advisor recommendations at investment firms. 

## 3. Proposed System 

A human-in-the-loop AI copilot system for human advisor investment recommendation compliance review. The system analyzes advisor recommendations alongside client KYC profiles and relevant regulatory documents to assess compliance risk and flag recommendations requiring human review.  

## 4. Value Proposition 

Automated compliance review of advisor recommendations against a variety of KYC profiles, complex portfolio compositions, and jurisdictional and firm-specific regulatory differences, enabling compliance teams to focus review effort on the highest-risk cases while reducing time spent on compliant recommendations. 

## 5. Goals / Success Metrics 

1. Improve compliance violation detection quality (i.e. non-compliant cases flagged, compliant cases automatically approved) 
2. Initial evaluation benchmark targets (to be validated through offline testing): 
    - Flagging precision: 90%
    - Flagging recall: 90%
        - Notes:
            - Confidence thresholds subject to calibration based on firm-defined compliance risk tolerance 
            - Recall prioritized over precision to minimize compliance violations for medium- and high-risk cases 
3. Improve review efficiency 
    -  % increase in total # cases reviewed / reviewer ≥ 30% 
4. Increase reviewer trust 
    - Trust(x) increases and plateaus over time, where: Trust(t+1) = Trust(t) + α*(correct assessment) − β*(confidently incorrect assessment) − γ*(friction from unnecessary escalation) − δ*(recoverable error)
        - where: 
            - δ < β  
            - δ ≈ small penalty
        - Intuition:        
            |Situation|User reaction|
            |---------|-------------|
            |Correct + confident|“This is great”|
            |Correct + unsure|“Okay, cautious system”|
            |Wrong + unsure|“Fine, that’s why I’m here”|
            |Wrong + confident|“I don’t trust this anymore”|

    - Qualitative user feedback confirming: 
        - Willingness to rely on AI assessments in review workflow over purely human judgement 
        - Increased user trust in AI assessments over time 

## 6. Scope (MVP) 

The initial MVP will prototype core system capabilities across four epics: 

1. Advisor recommendation/trade flagging 
    - Flagging high-risk trades for human compliance review 
    - Flagging low-confidence trades for human compliance review 
2. Human compliance review 
    - Presenting flagged trades in a structured summary on screen for quick and easy human understanding 
    - Sorting flagged trades by risk so human reviewers can tackle the riskiest cases first 
3. AI assessment explainability 
    - Showing the AI’s reasoning grounded in retrieved policies and cited evidence for human reviewers to review, upon request 
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

## 8. Non-goals (MVP) 

1. Advisor-facing interactions 
2. Fully automated approvals without human oversight 
3. Continuous learning based on reviewer feedback 

## 9. User Workflow 

1. Advisor submits recommendation / trade. 
2. AI evaluates trade, generating compliance prediction, a confidence score, and a risk score within 5 minutes of advisor’s submission. 
3. AI flags predicted compliance violation, low-confidence, and high-risk cases, visibly displaying them in a list prioritized for risk on a dashboard. 
4. Compliance reviewers select highest priority flagged cases from dashboard list to review; cases being reviewed by reviewers are marked as such on the dashboard list to avoid duplicate work. 
5. Compliance reviewer reviews structured summary of selected case, and can ask AI to: 
    - Show its reasoning. 
    - Retrieve and show the policies and documents, and their specific sections, it referenced in its reasoning. 
6. Compliance reviewer accepts or overrides the AI’s assessment of the case and can add notes to be logged with a timestamped record of their review. If no notes are input, the system will generate a warning message for the reviewer, which the reviewer may choose to ignore. 

## 10. Requirements 

See “Acceptance Criteria” for the Trello cards in the “Reference (User Stories)” list of this Trello Kanban board:
[AI Compliance Compilot Kanban](https://trello.com/invite/b/69bae1b9abc0feda4e98bc66/ATTIcbb9b514c5571a1a32b212ad05b0f354745241B3/ai-copilot-for-financial-compliance-review) 