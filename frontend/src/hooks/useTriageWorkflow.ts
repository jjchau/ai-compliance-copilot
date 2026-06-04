import { useReducer, useEffect, useCallback } from "react";
import { getCases, submitReview } from "../api/cases";

export interface TradeCase {
  trade_id: string;
  trade_timestamp: string;
  client_age: number;
  client_income: number;
  risk_tolerance: string;
  investment_experience: "Beginner" | "Intermediate" | "Advanced" | string;
  investment_objective: string;
  investment_time_horizon: string;
  investment_type: string;
  investment_amount: number;
  advisor_id: string;
  advisor_experience: string;
  advisor_history_risk: string;
  advisor_rationale: string;
  advisor_notes: string;
  kyc_completeness: string;
  
  // Enriched Analytical Fields saved in SQLite
  true_compliance: string;
  case_type: string;

  retrieved_policies?: string[] | string;
  retrieved_chunks?: string[] | string;
  compliance_probability: number;
  compliance_label: boolean | number; // SQLite saves booleans as 1 or 0
  risk_score: number;
  confidence_score: number;
  escalation_level: "urgent" | "priority" | "queue" | "none";
  priority_score: number;
  flag_reasons: string;
}

export interface CaseAuditState {
  reviewStatus: "Not reviewed" | "Reviewed";
  actionType?: "Rejected" | "Approved" | "Escalated" | null;
  notes: string;
}

interface WorkflowState {
  cases: TradeCase[];
  caseStates: Record<string, CaseAuditState>;
  selectedCaseId: string | null;
  activeView: "active" | "reviewed" | "passed";
}

type WorkflowAction =
  | { type: "SET_CASES"; payload: TradeCase[] }
  | { type: "SELECT_CASE"; payload: string | null }
  | { type: "SET_VIEW"; payload: "active" | "reviewed" | "passed" }
  | { type: "UPDATE_NOTES"; payload: { tradeId: string; notes: string } }
  | { type: "EXECUTE_ACTION"; payload: { tradeId: string; status: "Reviewed" | "Escalated"; actionType: "Rejected" | "Approved" | "Escalated"; notes: string } };

const initialWorkflowState: WorkflowState = {
  cases: [],
  caseStates: {},
  selectedCaseId: null,
  activeView: "active",
};

function workflowReducer(state: WorkflowState, action: WorkflowAction): WorkflowState {
  switch (action.type) {
    case "SET_CASES": {
      const defaultStates: Record<string, CaseAuditState> = {};
      action.payload.forEach((c) => {
        defaultStates[c.trade_id] = {
          reviewStatus: "Not reviewed",
          actionType: null,
          notes: "",
        };
      });
      return {
        ...state,
        cases: action.payload,
        caseStates: defaultStates,
        selectedCaseId: action.payload.length > 0 ? action.payload[0].trade_id : null,
      };
    }
    case "SELECT_CASE":
      return { ...state, selectedCaseId: action.payload };
    case "SET_VIEW":
      return { ...state, activeView: action.payload, selectedCaseId: null };
    case "UPDATE_NOTES":
      return {
        ...state,
        caseStates: {
          ...state.caseStates,
          [action.payload.tradeId]: {
            ...state.caseStates[action.payload.tradeId],
            notes: action.payload.notes,
          },
        },
      };
    case "EXECUTE_ACTION":
      return {
        ...state,
        caseStates: {
          ...state.caseStates,
          [action.payload.tradeId]: {
            reviewStatus: action.payload.status,
            actionType: action.payload.actionType,
            notes: action.payload.notes,
          },
        },
      };
    default:
      return state;
  }
}

export function useTriageWorkflow() {
  const [state, dispatch] = useReducer(workflowReducer, initialWorkflowState);

  useEffect(() => {
    let isMounted = true;
    getCases()
      .then((data) => {
        if (isMounted) dispatch({ type: "SET_CASES", payload: data });
      })
      .catch((err) => console.error("Error loading optimized queue dataset:", err));
    return () => {
      isMounted = false;
    };
  }, []);

  const selectCase = useCallback((tradeId: string | null) => {
    dispatch({ type: "SELECT_CASE", payload: tradeId });
  }, []);

  const setView = useCallback((view: "active" | "reviewed" | "passed") => {
    dispatch({ type: "SET_VIEW", payload: view });
  }, []);

  const updateNotes = useCallback((tradeId: string, text: string) => {
    dispatch({ type: "UPDATE_NOTES", payload: { tradeId, notes: text } });
  }, []);

  const executeAction = useCallback(async (
    tradeId: string,
    status: "Reviewed" | "Escalated",
    actionType: "Rejected" | "Approved" | "Escalated",
    notes: string
  ) => {
    const targetCase = state.cases.find((c) => c.trade_id === tradeId);
    // SQLite boolean conversion fallback
    const aiRec = targetCase?.compliance_label === 1 || targetCase?.compliance_label === true 
      ? "compliant" 
      : "non-compliant";

    try {
      await submitReview(tradeId, actionType, notes, aiRec);
    } catch (error) {
      console.error("Critical: Frontend could not commit review log entry upstream:", error);
    }

    dispatch({
      type: "EXECUTE_ACTION",
      payload: { tradeId, status, actionType, notes },
    });
  }, [state.cases]);

  const selectedCase = state.cases.find((c) => c && c.trade_id === state.selectedCaseId) || null;

  // Defensively filter urgent cases while accounting for empty state initializations
  const urgentCases = state.cases.filter((c) => {
    if (!c || !c.trade_id) return false;
    const tracking = state.caseStates[c.trade_id];
    const status = tracking ? tracking.reviewStatus : "Not reviewed";
    return c.escalation_level === "urgent" && status === "Not reviewed";
  });
  
  // Defensively filter and sort queued cases
  const queuedCases = state.cases
    .filter((c) => {
      if (!c || !c.trade_id) return false;
      const tracking = state.caseStates[c.trade_id];
      const status = tracking ? tracking.reviewStatus : "Not reviewed";
      return (c.escalation_level === "priority" || c.escalation_level === "queue") && status === "Not reviewed";
    })
    .sort((a, b) => (Number(b?.priority_score) || 0) - (Number(a?.priority_score) || 0));

  // Defensively filter reviewed cases
  const reviewedCasesList = state.cases.filter((c) => {
    if (!c || !c.trade_id) return false;
    const tracking = state.caseStates[c.trade_id];
    const status = tracking ? tracking.reviewStatus : "Not reviewed";
    return status === "Reviewed" || status === "Escalated";
  });

  // Defensively filter auto-passed cases
  const passedCasesList = state.cases.filter((c) => {
    if (!c || !c.trade_id) return false;
    const tracking = state.caseStates[c.trade_id];
    const status = tracking ? tracking.reviewStatus : "Not reviewed";
    return c.escalation_level === "none" && status === "Not reviewed";
  });

  return {
    cases: state.cases,
    caseStates: state.caseStates,
    selectedCase,
    activeView: state.activeView,
    urgentCases,
    queuedCases,
    reviewedCasesList: reviewedCasesList,
    passedCasesList: passedCasesList,
    reviewedTodayCount: reviewedCasesList.length,
    selectCase,
    setView,
    updateNotes,
    executeAction,
  };
}