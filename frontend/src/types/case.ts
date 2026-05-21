export interface ReviewCase {
    trade_id: string;
    escalation_level: string;
    priority_score: number;
    confidence_score: number;
    compliance_probability: number;
    flag_reason: string;
    retrieved_policies: string[];
    risk_tolerance: string;
    investment_objective: string;
    investment_time_horizon: string;
}