# METRIC HIERARCHY 

## 1. North Star Metric 

- **% cases correctly resolved at the lowest safe workflow level**:
	- $\frac{(\text{\# cases correctly resolved at lowest safe workflow level})}{(\text{total \# cases})}$ 
		- where:
			- “lowest safe workflow level” is the least burdensome review level that a case can be routed to that still protects against compliance risk. 
	- Data needed: 
		- Publicly available policy and regulatory compliance documentation
		- 1000 simulated cases correctly and incorrectly routed at different levels (system auto-approved, queue, priority, urgent) 
	- Simulation method:
		1. Using Python, create "profile factories" for different client and advisor archetypes and "scenario builders" for different compliance outcomes (e.g. aligned recommendation, KYC missing violation, etc.), then specify a distribution of cases generate 1000 cases with randomly sampled variable values fitting within the constraints of the profiles and scenarios sampled under that distribution. 
		2. Use ChatGPT to craft a small synthetic regulatory policy document corpus based on language sampled from real publicly available policy and regulatory compliance documentation. 

## 2. Product Success Metrics 

Note: All metrics in this section to be calculated ‘overall’ for all data points, and by risk tier, unless otherwise noted. 

- Decision Quality 
	- **Compliance classification accuracy**
	- Compliance classification precision / recall
	- False negative rate for compliance classification
	- **Expected regulatory risk exposure = $\frac{\sum(FN_i \times Severity)}{N}$**
		- where:
			- $FN_i = 1$ if false negative, else $0$
			- $Severity =$ Severity weighting (e.g. risk tier weights: 1, 5, 10) of $i^{th}$ case
			- $N =$ # of cases automatically approved 
	- Workflow routing accuracy
	- Workflow routing precision / recall
	- "Urgent" routing recall
	- "Auto-pass" over-routing
	- **Expected operational cost** = $\sum(\text{Probability of false positive} × \text{Review cost})$
	- % cases auto-approved correctly (or **auto-approval accuracy**)
	- % cases escalated unnecessarily 
	- Escalation efficiency 
		- ~~$\text{Useful escalation rate} = \frac{(\text{\# escalations that changed outcomes})}{(\text{total escalations})}$~~
		- ~~$\text{Avoidable escalation rate} = \frac{(\text{\# escalations where AI was already correct})}{(\text{total escalations})}$~~
		- **Escalation precision** = $\frac{(\text{\# correctly escalated cases})}{(\text{total escalated cases})}$
- Efficiency 
	- Review time per case 
	- Case throughput per reviewer 
- Trust 
	- ~~Override / Acceptance rate~~ 
		- ~~Override rate = $\frac{(\text{\# flagged cases overridden by humans})}{(\text{total \# flagged cases})}$~~
		- ~~Data needed: Simulation subset of cases that are “flagged” (should include cases both correctly and incorrectly assessed by AI system)~~
	- ~~Override / Acceptance vs correctness alignment~~
	- ~~Follow-up question rate~~ 
	- ~~Trust change direction over time (overall only)~~
	- ~~Time to trust stabilization (overall only)~~
	- ~~Qualitative user sentiment~~
	- **UPDATE**: **Trust Calibration Index**:
		- $TCI=\Pr(\text{correct \& handled correctly by system policy})+\Pr(\text{incorrect \& handled correctly by system policy})−λ_1\Pr(\text{high conf \& wrong})−λ_2\Pr(\text{low conf \& correct})$
			- where:
				- $λ_1$ is the overconfidence penalty weight
				- $λ_2$ is the underconfidence pentaly weight
- Top failure modes

## 3. System performance 

Note: All metrics to be calculated ‘overall’ for all data points, and by risk tier, unless otherwise noted 

- Retrieval 
	- Top retrieved policies
	- Retrieval coverage by policy
	- **Precision@k**
	- **Recall@k**
	- Context sufficiency 
	- **Retrieval correctness**
- Generation 
	- Reasoning faithfulnes 
	- Logical consistency
	- Instruction adherence
	- Regulatory constraint adherence
	- Hallucination rate
	- Context utilization score 
- Calibration 
	- **Expected Calibration Error**:  
		$\text{ECE} = \sum_{m=1}^{M} \frac{|B_m|}{n} \left| \frac{1}{|B_m|} \sum_{i \in B_m} \mathbf{1}(\hat{y}_i = y_i) - \frac{1}{|B_m|} \sum_{i \in B_m} \hat{p}_i \right|$
		- where: 
			- $M$ is the number of bins we split the confidence range into 
			- $B_m$ is the mth bin 
			- $\mathbf{1}$ is the indicator function  
			- $\hat{y}_i$ is the predicted label of the ith element
			- $y_i$ is the true label of the ith element 
			- $\hat{p}_i$ is the maximum probability of the predicted label for the ith element 

		- Data needed: All simulated cases having simulated confidence values (and therefore compliance outcomes) and simulated true compliance outcomes. 
		- Simulation method: Using Python, define ranges or categorical states for all case variables, then create a dictionary of 10000 cases containing randomly sampled values for each variable unless it’s correlated with one or more other variables. Correlated variables: 
			- high-risk clients → more complex portfolios  
			- missing data → higher uncertainty  
			- edge cases clustered in specific categories 
	- **Brier score**
	- **Overconfidence Rate** 
	- Confidence vs accuracy alignment 
- End-to-end 
	- Correctness (% cases system worked correctly for – cases requiring flagging flagged, cases ok to auto-approve auto-approved) 
	- % failures due to retrieval 
	- % failures due to generation (retrieval ok but reasoning fails) 
	- % failures due to confidence calibration (retrieval and reasoning ok but decision wrong) 

## 4. Component Diagnostic 

- Embedding drift  
- Prompt truncation effects  
- Token budget saturation  
- Chunk boundary fragmentation  