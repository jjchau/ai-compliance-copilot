# METRIC HIERARCHY 

## 1. North Star Metric 

- % cases correctly resolved at the lowest appropriate review level:
	- $\frac{(\text{\# cases correctly resolved at lowest appropriate level})}{(\text{total \# cases})}$ 
		- where:
			- “lowest appropriate level” is the lowest level that a case can be resolved at without violating policy constraints; a ground truth value for  the lowest appropriate level will be defined per case in simulation. 
	- Data needed: 
		- Publicly available policy and regulatory compliance documentation 
		- 10000 simulated cases correctly and incorrectly resolved at different levels (system auto-approved, front-line reviewer, escalation 1, escalation 2) 
	- Simulation method: 
		1. Using Python, define ranges or categorical states for all case variables, then create a dictionary of 10000 cases containing randomly sampled values for each variable unless it’s correlated with one or more other variables. Correlated variables: 
			- high-risk clients → more complex portfolios  
			- missing data → higher uncertainty  
			- edge cases clustered in specific categories 
		2. Use ChatGPT to simulate advisor notes and communications for each case. 

## 2. Product Success Metrics 

Note: All metrics in this section to be calculated ‘overall’ for all data points, and by risk tier, unless otherwise noted. 

- Decision Quality 
	- Risk classification accuracy 
	- Precision / Recall for flagging decisions 
	- False negative rate 
	- Expected regulatory risk exposure = $\frac{\sum(FN_i \times Severity)}{N}$ 
		- where:
			- $FN_i = 1$ if false negative, else $0$
			- $Severity =$ Severity weighting of $i^{th}$ case
			- $N =$ # of cases automatically approved 
	- Expected operational cost = $\sum(\text{Probability of false positive} × \text{Review cost})$
	- Severity-weighted error rate (overall only) = $\frac{\sum(Error \times Severity)}{\text{Total Cases}}$
		- where:
			- $Error = 1$ if wrong and $0$ if correct
			- $Severity =$ risk tier weight (e.g. 1, 5, 10) 
	- % cases auto-approved correctly 
	- % cases escalated unnecessarily 
	- Escalation efficiency 
		- $\text{Useful escalation rate} = \frac{(\text{\# escalations that changed outcomes})}{(\text{total escalations})}$
		- $\text{Avoidable escalation rate} = \frac{(\text{\# escalations where AI was already correct})}{(\text{total escalations})}$
		- $\text{Escalation precision} = \frac{(\text{\# correctly escalated cases})}{(\text{total escalated cases})}$
- Efficiency 
	- Review time per case 
	- Case throughput per reviewer 
- Trust 
	- Override / Acceptance rate 
		- $\text{Override rate} = \frac{(\text{\# flagged cases overridden by humans})}{(\text{total \# flagged cases})}$ 
		- Data needed: Simulation subset of cases that are “flagged” (should include cases both correctly and incorrectly assessed by AI system) 
		- Simulation method: 
			1. Using Python, define ranges or categorical states for all case variables, then create a dictionary of 10000 cases containing randomly sampled values for each variable unless it’s correlated with one or more other variables. Correlated variables: 
				- high-risk clients → more complex portfolios  
				- missing data → higher uncertainty  
				- edge cases clustered in specific categories 
			2. Use ChatGPT to simulate advisor notes and communications for each case. 
	- Override / Acceptance vs correctness alignment 
	- Follow-up question rate 
	- Trust change direction over time (overall only) 
	- Time to trust stabilization (overall only) 
	- Qualitative user sentiment 
	- Trust Calibration Index:
		- $TCI=\Pr(\text{correct \& handled correctly by system policy})+\Pr(\text{incorrect \& handled correctly by system policy})−λ_1\Pr(\text{high conf \& wrong})−λ_2\Pr(\text{low conf \& correct})$
			- where:
				- $λ_1$ is the overconfidence penalty weight
				- $λ_2$ is the underconfidence pentaly weight

## 3. System performance 

Note: All metrics to be calculated ‘overall’ for all data points, and by risk tier, unless otherwise noted 

- Retrieval 
	- Precision@k 
	- Recall@k 
	- Context sufficiency 
	- Retrieval correctness 
- Generation 
	- Reasoning faithfulness 
	- Logical consistency 
	- Instruction adherence 
	- Regulatory constraint adherence 
	- Hallucination rate 
	- Context utilization score 
- Calibration 
	- Expected Calibration Error:  
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
	- Brier score 
	- Overconfidence Rate 
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