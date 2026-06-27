# AI Compliance Review Copilot
A human-in-the-loop, RAG-enabled decision-support workflow for investment compliance review.

## 1. Overview
This project implements and evaluates a human-in-the-loop, RAG-enabled workflow for reviewing simulated investment recommendations. It combines AI compliance assessment, risk-based workflow routing, a reviewer-dashboard prototype, and retrieval diagnostics to evaluate where automation may be appropriate and where human review remains necessary.

## 2. Problem
Wealth management firms must review advisor investment recommendations for regulatory and suitability risks, but human-only review is difficult to scale. Existing rule-based systems can generate large volumes of low-quality alerts while struggling with complex cases and unstructured client-advisor information, contributing to reviewer backlogs and inconsistent decisions.

The product challenge is not simply to maximize model accuracy, but to automate each case at the lowest safe workflow level while minimizing both missed compliance risks and unnecessary reviewer escalation.

## 3. Product Concept
```mermaid
flowchart LR
    A[Advisor investment 
    recommendation]
    --> B[RAG policy retrieval]
    --> C[AI compliance assessment]
    --> D[Risk and confidence scoring]
    --> E{Workflow routing}

    E --> F[Auto-pass]
    E --> G[Queue]
    E --> H[Priority]
    E --> I[Urgent]

    G --> J[Human review]
    H --> J
    I --> J
    J --> K[Decision and audit log]
```

## 4. Implemented Scope
### 4.1 AI and decision pipeline
- Synthetic case generation and ground-truth labeling
- RAG-based policy retrieval and structured AI assessment
- Compliance, risk, and confidence scoring
- Risk-based workflow routing and audit logging

### 4.2 Evaluation
- North Star Metric, compliance, and workflow-routing evaluation
- Safety and reviewer-burden analysis
- Retrieval and calibration diagnostics
- Overconfidence, trust-evolution, and failure-mode analysis

### 4.3 Reviewer experience
- Risk-prioritized review queues
- Structured case, assessment, and policy-evidence summaries
- Approval, rejection, escalation, and reviewer-comment controls
- Decision history and audit trail

## 5. Primary Evaluation Question
**Can the system correctly resolve investment compliance cases at the lowest safe workflow level while limiting regulatory risk and unnecessary reviewer escalation?**

## 6. Evaluation Scorecard
### Product Safety and Workflow Outcomes:
|Metric|Result|Product implication|
|:-----|:-----|:---------------------|
|North Star Metric*|77.7%|22.3% of cases were either under-routed or sent to a more burdensome workflow than necessary.|
|Compliance accuracy|99.5%|One of 220 cases received an incorrect compliance classification.|
|Compliance false-negative rate [%]|1.1%|One non-compliant case was incorrectly classified as compliant, although it was still routed for human review.|
|Urgent case recall|66.7%|Eight of 24 urgent cases were routed as priority, delaying the intended urgency of review.|
|Auto-pass over-escalation|41.3%|Twenty-six of 63 eligible auto-pass cases were unnecessarily sent to the review queue.|
|Escalation precision|85.6%|Most escalated cases required review, although conservative routing created avoidable reviewer burden.|

*The North Star Metric is the percentage of cases correctly resolved at the lowest safe workflow level. In this framework, it is equivalent to workflow-routing accuracy.

### Trust and Confidence:
|Metric|Result|Product implication|
|:-----|:-----|:------------------|
|Overconfidence Rate (@threshold=0.5) [%]|0.5%|Only one in two hundred plus cases was incorrectly classified with high confidence; because  this result is based on so few incorrect classifications it's not necessarily reflective of reliable calibration.|
|Trust proxy change|0.700 → 0.901|The simulated trust proxy rose over the evaluation sequence, but it's not validated against observed reviewer behaviour.|

<p align="center">
  <img src="docs/images/trust_proxy_evolution.png"
       alt="Simulated reviewer trust proxy over sequential case evaluations"
       width="750"><br>
  <i>Simulated trust-proxy evolution across the evaluation sequence. This is an analytical simulation, not observed user behaviour.</i>
</p>

### Retrieval and System Diagnostics:
|Metric|Result|Product implication|
|:-----|:-----|:------------------|
|Average precision@k (k=10)|35.2%|Retrieval was broad and frequently included policies not labelled relevant to the case.|
|Average recall@k (k=10)|54%|The retriever returned slightly more than half of all policies labelled relevant across the evaluated cases.|
|Primary policy retrieval rate [%]|66.2%|The most important relevant policy was absent from the retrieved context in roughly one-third of applicable cases.|
|Any relevant policy retrieval rate [%]|89.7%|Most cases received at least some relevant policy context despite weaker precision and primary-policy coverage.|
|Most frequent failure mode|Auto-pass over-routing|Twenty-six 'auto-pass' cases were unnecessarily escalated to 'queue', accounting for 53.1% of all failure cases.|

[View full evaluation notebook](notebooks/AI_compliance_copilot_evaluation.ipynb)


## 7. Key Findings
The following findings are based on the 220-case development set:
- Compliance classification was strong, but workflow routing remained the primary performance constraint. The system achieved 99.5% compliance accuracy, while the North Star Metric reached 77.7%, showing that most remaining errors involved selecting the appropriate review route rather than determining whether a case was compliant.
- Routing behaviour was generally conservative, creating reviewer burden rather than widespread unsafe automation. Auto-pass over-routing was the most common failure mode: 26 of 63 cases eligible for auto-pass were unnecessarily sent to the review queue. Overall, over-routing accounted for most identified routing failures.
- Urgent-case prioritization requires improvement. Eight of 24 cases expected to receive urgent review were instead routed as priority. Although these cases would still reach a human reviewer, the reduced urgency could delay attention to the highest-risk cases.
- Retrieval usually returned some relevant evidence, but often failed to identify the most important policy cleanly. At least one relevant policy was retrieved for 89.7% of cases, but primary-policy retrieval reached only 66.2% and average precision@10 was 35.2%. This indicates broad retrieval with substantial irrelevant context and inconsistent coverage of the strongest supporting policy.
- Confidence and trust results should be treated as preliminary. Only one high-confidence compliance error occurred, providing too little error data to establish robust calibration. The simulated trust proxy increased from 0.700 to 0.901, but it represents an analytical model rather than observed reviewer behaviour.

## 8. Product Recommendation
The current prototype is best positioned as a human decision-support system rather than an autonomous compliance-review system.

The development-set results support continued use of the pipeline to organize cases, surface policy evidence, and assist reviewer triage. However, unattended deployment is not yet recommended because urgent-case recall and primary-policy retrieval remain below the level required for reliable risk-based automation.

Before broader deployment:

Improve urgent-case routing so that high-risk cases are consistently surfaced at the required review priority.
Increase primary-policy retrieval and reduce repetitive or irrelevant context.
Reduce unnecessary auto-pass over-routing without weakening false-negative or urgent-case safeguards.
Freeze the updated pipeline and validate it on the 780-case held-out dataset.
Conduct review with compliance-domain experts and test the dashboard with representative users before relying on the system in an operational workflow.

A limited future auto-pass capability may be appropriate for narrowly defined, low-risk cases, but only after held-out evaluation confirms that safety metrics remain stable.

## 9. Reviewer Workflow Prototype
<p align="center">
  <img src="docs/images/frontend_dashboard.png"
       alt="Frontend dashboard for compliance reviewers"
       width="1250"><br>
  <i>Reviewer dashboard prototype showing prioritized case queues, structured assessment evidence, policy references, and reviewer decision controls.</i>
</p>

## 10. Dataset and Assumptions
|Component|Description|
|:--------|:----------|
|Cases|1,000 synthetic advisor investment recommendations spanning multiple compliance scenarios, client archetypes, and advisor profiles. A 220-case development set was used to diagnose and tune pipeline behaviour; 780 held-out cases were reserved for final evaluation.|
|Policy corpus|Ten synthetic internal-policy documents informed by themes in publicly accessible [HighPoint Advisor Group](https://highpointplanningpartners.com/wp-content/uploads/2024/03/Compliance-Manual-11-2022.pdf) and [AE Wealth Management](https://aewealthmanagement.com/advisor-login/wp-content/uploads/sites/7/2022/09/Compliance-Policy-Manual_AEWM_Jan-10-2023_FINAL.pdf) compliance manuals and broader Canadian and U.S. wealth-management compliance concepts. Two intentionally irrelevant documents were retained as retrieval noise. The corpus is simplified for evaluation and does not reproduce either firm’s policies.|
|Ground truth|Expected compliance labels, relevant and primary policies, and workflow routes were generated using deterministic ground-truth rules separate from the prediction and routing algorithms. The labels reflect the project’s simplified domain assumptions rather than expert regulatory adjudication.|
|AI assessment|Gemini 3.1 Flash-Lite generates structured compliance assessments using case data and retrieved policy context. Model outputs are evaluated against the programmatically assigned labels and expected routes.|
|Risk score|A deterministic severity proxy representing the potential firm-level regulatory or legal impact of failing to identify a non-compliant case.| 
|Synthetic confidence proxy|A deterministic score that increases with data completeness, evidence quality, and directional consistency, and decreases with missing or conflicting signals. It is used in workflow routing logic and not treated as the model’s internal probability of correctness.|
|Trust simulation|A synthetic trust score is updated sequentially based on compliance and routing correctness, with penalties for incorrect outcomes. It is an analytical proxy rather than a validated model of reviewer behaviour; no real-user study was conducted.|

## 11. Limitations and Next Steps
### 11.1 Limitations
- Synthetic rather than firm-provided investment recommendation data
- Synthetic and limited policy corpus
- Labels based on designed rules and assumptions rather than expert legal adjudication
- No real compliance-reviewer usability or trust study
- No production latency, security, or scalability evaluation
- Reviewer feedback not connected to recalibration
- Calibration evaluation limited by sample size

### 11.2 Next Steps
- Evaluate the frozen pipeline on the 780-case held-out dataset
- Expand the policy corpus
- Conduct reviewer usability testing
- Add feedback-based recalibration

## 12. Technology

- **Backend and evaluation:** Python, FastAPI, SQLite, Jupyter
- **Retrieval:** Sentence Transformers (`all-MiniLM-L6-v2`)
- **AI assessment:** Gemini 3.1 Flash-Lite
- **Frontend:** React

## 13. Repository Guide
```
├── docs/          Product, requirements, metrics and risk artifacts
├── data/          Synthetic cases, ground truth labels, and policy corpus documents 
├── src/           Retrieval, scoring, decisioning, logging, data synthesis, and backend API code
├── frontend/      Reviewer dashboard prototype
├── notebooks/     Evaluation and analysis
└── tests/         Automated tests
```
Quicklinks to selected artifacts:
- [Product Vision](/docs/product_vision.md)
- [Product Requirements Document](/docs/product_requirements.md)
- [Metric Hierarchy](/docs/metric_hierarchy.md)
- [Evaluation Notebook](/notebooks/AI_compliance_copilot_evaluation.ipynb)
- [Executive Memo]

## 14. Setup and Reproduction
These instructions were tested on Windows using PowerShell. Replace `C:\install-directory-path` with the directory where you want to install the project. Commands for other operating systems or shells may differ.

### 14.1 Clone and Set Up the Project
Run the first command from the parent directory where the repository will be installed.
```powershell
PS C:\install-directory-path> git clone https://github.com/jjchau/ai-compliance-copilot.git
PS C:\install-directory-path> Set-Location .\ai-compliance-copilot
PS C:\install-directory-path\ai-compliance-copilot> python -m venv .venv
PS C:\install-directory-path\ai-compliance-copilot> .\.venv\Scripts\Activate.ps1
PS (.venv) C:\install-directory-path\ai-compliance-copilot> python -m pip install --upgrade pip
PS (.venv) C:\install-directory-path\ai-compliance-copilot> python -m pip install -r requirements.txt
```

After activation, PowerShell will normally display `(.venv)` at the beginning of the prompt.
If PowerShell prevents the activation script from running, allow locally created scripts for the current user:
```powershell
PS C:\install-directory-path\ai-compliance-copilot> Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
PS C:\install-directory-path\ai-compliance-copilot> .\.venv\Scripts\Activate.ps1
```

### 14.2 Configure the Gemini API
Create a Gemini API key using Google AI Studio, then expose it through an environment variable. Do not commit API keys to the repository.

Run this command in the same PowerShell session that will execute the AI pipeline:
```powershell
(.venv) PS C:\install-directory-path\ai-compliance-copilot> $env:GEMINI_API_KEY = "your-api-key"
```

Confirm that the variable is available without displaying the key itself:
```powershell
(.venv) PS C:\install-directory-path\ai-compliance-copilot> if ($env:GEMINI_API_KEY) { Write-Output "GEMINI_API_KEY is configured." }
```

The environment variable applies only to the current PowerShell session. It must be set again in a new session unless another secure configuration method is used.

### 14.3 Generate Case Data
```powershell
(.venv) PS C:\install-directory-path\ai-compliance-copilot> python .\src\data\dataset_generator.py
```

### 14.4 Embed the Policy Corpus
```powershell
(.venv) PS C:\install-directory-path\ai-compliance-copilot> python .\src\rag\ingestion.py
```

### 14.5 Run the AI Pipeline and Store Results in SQLite
Ensure that `GEMINI_API_KEY` is configured in the current PowerShell session before running this command:
```powershell
(.venv) PS C:\install-directory-path\ai-compliance-copilot> python .\enrich_dataset.py
```

### 14.6 Run the Frontend Dashboard Prototype (Optional)
The backend API and frontend development server must run in separate PowerShell windows.

#### PowerShell Window 1: Start the Backend API
```powershell
PS C:\install-directory-path> Set-Location .\ai-compliance-copilot
PS C:\install-directory-path\ai-compliance-copilot> .\.venv\Scripts\Activate.ps1
(.venv) PS C:\install-directory-path\ai-compliance-copilot> python -m uvicorn src.api.main:app --reload
```

#### PowerShell Window 2: Install and Start the Frontend
```powershell
PS C:\install-directory-path> Set-Location .\ai-compliance-copilot\frontend
PS C:\install-directory-path\ai-compliance-copilot\frontend> npm install
PS C:\install-directory-path\ai-compliance-copilot\frontend> npm run dev -- --force
```

After both servers are running, open the following address in a browser:
```text
http://localhost:5173/
```

### 14.7 Run the Evaluation Notebook
```powershell
PS C:\install-directory-path> Set-Location .\ai-compliance-copilot
PS C:\install-directory-path\ai-compliance-copilot> .\.venv\Scripts\Activate.ps1
(.venv) PS C:\install-directory-path\ai-compliance-copilot> python -m jupyter notebook .\notebooks\AI_compliance_copilot_evaluation.ipynb
```
