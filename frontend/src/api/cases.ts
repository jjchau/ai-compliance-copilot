import axios from "axios";

const api=axios.create({

    baseURL:"http://127.0.0.1:8000"
});

export const getCases=async()=>{

    const response=
        await api.get("/cases");

    return response.data;
};

export interface ReviewSubmissionPayload {
  ai_recommendation: string;
  review_action: "reject" | "approve" | "escalate";
  case_status: "pending" | "reviewed" | "awaiting_senior_review";
  review_outcome: "compliant" | "non-compliant" | null;
  reviewer: string;
  notes: string;
}

/**
 * Dispatches an audited case review payload to the FastAPI logging endpoint.
 */
export async function submitReview(
  tradeId: string,
  actionType: "Rejected" | "Approved" | "Escalated",
  notes: string,
  aiRecommendation: string = "non-compliant"
): Promise<any> {
  // 1. Map frontend UI Action Types to strict backend review_action Literals
  let review_action: "reject" | "approve" | "escalate" = "escalate";
  if (actionType === "Rejected") review_action = "reject";
  if (actionType === "Approved") review_action = "approve";

  // 2. Map frontend UI Statuses to strict backend case_status Literals
  let case_status: "pending" | "reviewed" | "awaiting_senior_review" = "awaiting_senior_review";
  if (actionType === "Rejected" || actionType === "Approved") case_status = "reviewed";

  // 3. Map final decision states to strict backend review_outcome Literals
  let review_outcome: "compliant" | "non-compliant" | null = aiRecommendation === "compliant" ? "compliant" : "non-compliant";
  if (actionType === "Rejected") review_outcome = "non-compliant";
  if (actionType === "Approved") review_outcome = "compliant";
  if (actionType === "Escalated") review_outcome = null; // Matches None in Python

  const payload: ReviewSubmissionPayload = {
    ai_recommendation: aiRecommendation,
    review_action,
    case_status,
    review_outcome,
    reviewer: "demo_user",
    notes: notes || "No audit justification notes appended.",
  };

  const response = await fetch(`/api/cases/${tradeId}/review`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    throw new Error(`FastAPI Review Logging Failure: ${response.statusText}`);
  }

  return response.json();
}