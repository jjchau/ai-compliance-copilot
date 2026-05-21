import { useReducer, useEffect, useCallback } from "react";
import { getCases } from "../api/cases";

export interface TradeCase {
  trade_id: string;
  escalation_level: "urgent" | "priority" | "queue" | string;
  compliance_probability?: number;
  confidence_score?: number;
  flag_reason?: string;
  investment_type?: string;
  investment_amount?: number;
  notional_value?: number;
  timestamp?: string;
  client_age?: number;
  client_income?: number;
  risk_tolerance?: string;
  investment_experience?: string;
  investment_objective?: string;
  advisor_id?: string;
  advisor_experience?: string;
  advisor_history_risk?: number;
  has_rationale?: boolean;
  advisor_notes?: string;
  retrieved_policies?: any;
  compliance_label?: string;
  priority_score?: number;
}

export interface CaseAuditState {
  reviewStatus: "Reviewed" | "Not reviewed" | "Escalated";
  notes: string;
  overriddenLabel?: string;
  userAction?: "Rejected" | "Approved" | "Escalated";
}

interface WorkflowState {
  activeView: "active" | "reviewed" | "passed";
  cases: TradeCase[];
  selectedCase: TradeCase | null;
  caseStates: Record<string, CaseAuditState>;
  reviewedTodayCount: number;
}

type WorkflowAction =
  | { type: "FETCH_SUCCESS"; payload: TradeCase[] }
  | { type: "SET_VIEW"; payload: "active" | "reviewed" | "passed" }
  | { type: "SELECT_CASE"; payload: TradeCase }
  | { type: "UPDATE_NOTES"; payload: { tradeId: string; notes: string } }
  | { type: "EXECUTE_ACTION"; payload: { tradeId: string; status: "Reviewed" | "Escalated"; actionType: "Rejected" | "Approved" | "Escalated"; notes: string } };

function workflowReducer(state: WorkflowState, action: WorkflowAction): WorkflowState {
  switch (action.type) {
    case "FETCH_SUCCESS": {
      const initialStates: Record<string, CaseAuditState> = {};
      action.payload.forEach((c) => {
        if (c?.trade_id) {
          initialStates[c.trade_id] = {
            reviewStatus: "Not reviewed",
            notes: "",
            overriddenLabel: c.compliance_label || "Non-compliant",
          };
        }
      });

      const urgent = action.payload.filter((c) => c?.escalation_level === "urgent");
      const queued = action.payload
        .filter((c) => c?.escalation_level === "priority" || c?.escalation_level === "queue")
        .sort((a, b) => (Number(b?.priority_score) || 0) - (Number(a?.priority_score) || 0));
      
      const defaultFocus = urgent.length > 0 ? urgent[0] : queued.length > 0 ? queued[0] : null;

      return {
        ...state,
        cases: action.payload,
        caseStates: initialStates,
        selectedCase: defaultFocus,
      };
    }

    case "SET_VIEW": {
      // Automatically focus the first item in the newly opened view to maintain smooth workflow
      let nextFocus = state.selectedCase;
      const urgent = state.cases.filter((c) => c?.escalation_level === "urgent" && state.caseStates[c.trade_id]?.reviewStatus === "Not reviewed");
      const queued = state.cases
        .filter((c) => (c?.escalation_level === "priority" || c?.escalation_level === "queue") && state.caseStates[c.trade_id]?.reviewStatus === "Not reviewed")
        .sort((a, b) => (Number(b?.priority_score) || 0) - (Number(a?.priority_score) || 0));
      const reviewed = state.cases.filter((c) => state.caseStates[c.trade_id]?.reviewStatus === "Reviewed" || state.caseStates[c.trade_id]?.reviewStatus === "Escalated");
      const passed = state.cases.filter((c) => c?.escalation_level !== "urgent" && c?.escalation_level !== "priority" && c?.escalation_level !== "queue");

      if (action.payload === "active") {
        nextFocus = urgent.length > 0 ? urgent[0] : queued.length > 0 ? queued[0] : null;
      } else if (action.payload === "reviewed") {
        nextFocus = reviewed.length > 0 ? reviewed[0] : null;
      } else if (action.payload === "passed") {
        nextFocus = passed.length > 0 ? passed[0] : null;
      }

      return { ...state, activeView: action.payload, selectedCase: nextFocus };
    }

    case "SELECT_CASE":
      return { ...state, selectedCase: action.payload };

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

    case "EXECUTE_ACTION": {
      const { tradeId, status, actionType, notes } = action.payload;
      const isReReview = state.caseStates[tradeId]?.reviewStatus !== "Not reviewed";
      
      const updatedCaseStates = {
        ...state.caseStates,
        [tradeId]: {
          ...state.caseStates[tradeId],
          reviewStatus: status,
          userAction: actionType,
          notes,
        },
      };

      let nextFocus: TradeCase | null = null;

      // Only calculate next focus auto-advance if we are modifying an item inside the Active tab streams
      if (state.activeView === "active" && !isReReview) {
        const remainingUrgent = state.cases.filter(
          (c) => c?.escalation_level === "urgent" && updatedCaseStates[c.trade_id]?.reviewStatus === "Not reviewed" && c.trade_id !== tradeId
        );
        const remainingQueued = state.cases
          .filter((c) => (c?.escalation_level === "priority" || c?.escalation_level === "queue") && updatedCaseStates[c.trade_id]?.reviewStatus === "Not reviewed" && c.trade_id !== tradeId)
          .sort((a, b) => (Number(b?.priority_score) || 0) - (Number(a?.priority_score) || 0));

        const targetCase = state.cases.find((c) => c.trade_id === tradeId);
        const wasUrgent = targetCase?.escalation_level === "urgent";

        if (wasUrgent) {
          const pool = state.cases.filter((c) => c?.escalation_level === "urgent" && state.caseStates[c.trade_id]?.reviewStatus === "Not reviewed");
          const currentIndex = pool.findIndex((c) => c.trade_id === tradeId);
          const dynamicUrgentPool = pool.filter((c) => c.trade_id !== tradeId);

          if (dynamicUrgentPool.length > 0) {
            const idx = Math.min(currentIndex, dynamicUrgentPool.length - 1);
            nextFocus = dynamicUrgentPool[idx >= 0 ? idx : 0];
          } else if (remainingQueued.length > 0) {
            nextFocus = remainingQueued[0];
          }
        } else {
          const pool = state.cases.filter((c) => (c?.escalation_level === "priority" || c?.escalation_level === "queue") && state.caseStates[c.trade_id]?.reviewStatus === "Not reviewed").sort((a, b) => (Number(b?.priority_score) || 0) - (Number(a?.priority_score) || 0));
          const currentIndex = pool.findIndex((c) => c.trade_id === tradeId);
          const dynamicQueuedPool = pool.filter((c) => c.trade_id !== tradeId);

          if (dynamicQueuedPool.length > 0) {
            const idx = Math.min(currentIndex, dynamicQueuedPool.length - 1);
            nextFocus = dynamicQueuedPool[idx >= 0 ? idx : 0];
          } else if (remainingUrgent.length > 0) {
            nextFocus = remainingUrgent[0];
          }
        }
      } else {
        // If reviewing inside Reviewed or Passed tab list, maintain focus on current item
        nextFocus = state.cases.find((c) => c.trade_id === tradeId) || null;
      }

      return {
        ...state,
        caseStates: updatedCaseStates,
        selectedCase: nextFocus,
        reviewedTodayCount: isReReview ? state.reviewedTodayCount : state.reviewedTodayCount + 1,
      };
    }

    default:
      return state;
  }
}

const initialState: WorkflowState = {
  activeView: "active",
  cases: [],
  selectedCase: null,
  caseStates: {},
  reviewedTodayCount: 0,
};

export function useTriageWorkflow() {
  const [state, dispatch] = useReducer(workflowReducer, initialState);

  useEffect(() => {
    getCases()
      .then((data) => {
        if (Array.isArray(data)) dispatch({ type: "FETCH_SUCCESS", payload: data });
      })
      .catch((err) => console.error("Workflow Ingestion Fail:", err));
  }, []);

  const setView = useCallback((view: "active" | "reviewed" | "passed") => {
    dispatch({ type: "SET_VIEW", payload: view });
  }, []);

  const selectCase = useCallback((c: TradeCase) => {
    dispatch({ type: "SELECT_CASE", payload: c });
  }, []);

  const updateNotes = useCallback((tradeId: string, notes: string) => {
    dispatch({ type: "UPDATE_NOTES", payload: { tradeId, notes } });
  }, []);

  const executeAction = useCallback((tradeId: string, status: "Reviewed" | "Escalated", actionType: "Rejected" | "Approved" | "Escalated", notes: string) => {
    dispatch({ type: "EXECUTE_ACTION", payload: { tradeId, status, actionType, notes } });
  }, []);

  const urgentCases = state.cases.filter((c) => c?.escalation_level === "urgent" && state.caseStates[c.trade_id]?.reviewStatus === "Not reviewed");
  const queuedCases = state.cases
    .filter((c) => (c?.escalation_level === "priority" || c?.escalation_level === "queue") && state.caseStates[c.trade_id]?.reviewStatus === "Not reviewed")
    .sort((a, b) => (Number(b?.priority_score) || 0) - (Number(a?.priority_score) || 0));

  const reviewedCasesList = state.cases.filter((c) => state.caseStates[c.trade_id]?.reviewStatus === "Reviewed" || state.caseStates[c.trade_id]?.reviewStatus === "Escalated");
  const passedCasesList = state.cases.filter((c) => c?.escalation_level !== "urgent" && c?.escalation_level !== "priority" && c?.escalation_level !== "queue");

  return {
    ...state,
    urgentCases,
    queuedCases,
    reviewedCasesList,
    passedCasesList,
    setView,
    selectCase,
    updateNotes,
    executeAction,
  };
}