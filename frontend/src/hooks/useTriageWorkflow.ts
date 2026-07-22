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
  reviewStatus: "Not reviewed" | "Reviewed" | "Escalated";
  actionType?: "Rejected" | "Approved" | "Escalated" | null;
  notes: string;
}

interface WorkflowState {
  cases: TradeCase[];
  caseStates: Record<string, CaseAuditState>;
  selectedCaseId: string | null;
  activeView: "active" | "reviewed" | "passed";
}

type WorkflowView = WorkflowState["activeView"];
type VisibleListKey = "urgent" | "queued" | "reviewed" | "passed";

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

const getReviewStatus = (
  state: Pick<WorkflowState, "caseStates">,
  tradeId: string,
): CaseAuditState["reviewStatus"] => {
  return state.caseStates[tradeId]?.reviewStatus ?? "Not reviewed";
};

const getVisibleLists = (
  state: Pick<WorkflowState, "cases" | "caseStates">,
): Record<VisibleListKey, TradeCase[]> => {
  const urgent = state.cases.filter((c) => {
    if (!c || !c.trade_id) return false;
    return c.escalation_level === "urgent" && getReviewStatus(state, c.trade_id) === "Not reviewed";
  });

  const queued = state.cases
    .filter((c) => {
      if (!c || !c.trade_id) return false;
      const status = getReviewStatus(state, c.trade_id);
      return (c.escalation_level === "priority" || c.escalation_level === "queue") && status === "Not reviewed";
    })
    .sort((a, b) => (Number(b?.priority_score) || 0) - (Number(a?.priority_score) || 0));

  const reviewed = state.cases.filter((c) => {
    if (!c || !c.trade_id) return false;
    const status = getReviewStatus(state, c.trade_id);
    return status === "Reviewed" || status === "Escalated";
  });

  const passed = state.cases.filter((c) => {
    if (!c || !c.trade_id) return false;
    return c.escalation_level === "none" && getReviewStatus(state, c.trade_id) === "Not reviewed";
  });

  return { urgent, queued, reviewed, passed };
};

const getDefaultSelectedCaseId = (
  state: Pick<WorkflowState, "cases" | "caseStates">,
  view: WorkflowView,
): string | null => {
  const lists = getVisibleLists(state);

  if (view === "active") {
    return lists.urgent[0]?.trade_id ?? lists.queued[0]?.trade_id ?? null;
  }

  if (view === "reviewed") {
    return lists.reviewed[0]?.trade_id ?? null;
  }

  return lists.passed[0]?.trade_id ?? null;
};

const getVisibleListKeyForTrade = (
  state: Pick<WorkflowState, "cases" | "caseStates">,
  view: WorkflowView,
  tradeId: string,
): VisibleListKey | null => {
  const lists = getVisibleLists(state);

  if (view === "active") {
    if (lists.urgent.some((c) => c.trade_id === tradeId)) return "urgent";
    if (lists.queued.some((c) => c.trade_id === tradeId)) return "queued";
    return null;
  }

  if (view === "reviewed") {
    return lists.reviewed.some((c) => c.trade_id === tradeId) ? "reviewed" : null;
  }

  return lists.passed.some((c) => c.trade_id === tradeId) ? "passed" : null;
};

const getNextSelectedCaseIdAfterAction = (
  previousState: WorkflowState,
  nextState: WorkflowState,
  tradeId: string,
): string | null => {
  const sourceListKey = getVisibleListKeyForTrade(
    previousState,
    previousState.activeView,
    tradeId,
  );

  if (!sourceListKey) {
    return getDefaultSelectedCaseId(nextState, nextState.activeView);
  }

  const previousList = getVisibleLists(previousState)[sourceListKey];
  const nextList = getVisibleLists(nextState)[sourceListKey];
  const previousIndex = previousList.findIndex((c) => c.trade_id === tradeId);
  const nextCandidateId = previousList[previousIndex + 1]?.trade_id;

  if (nextCandidateId && nextList.some((c) => c.trade_id === nextCandidateId)) {
    return nextCandidateId;
  }

  return (
    nextList[previousIndex]?.trade_id
    ?? nextList[previousIndex - 1]?.trade_id
    ?? getDefaultSelectedCaseId(nextState, nextState.activeView)
  );
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
      const nextState = {
        ...state,
        cases: action.payload,
        caseStates: defaultStates,
      };

      return {
        ...nextState,
        selectedCaseId: getDefaultSelectedCaseId(nextState, nextState.activeView),
      };
    }
    case "SELECT_CASE":
      return { ...state, selectedCaseId: action.payload };
    case "SET_VIEW": {
      const nextState = { ...state, activeView: action.payload };
      return {
        ...nextState,
        selectedCaseId: getDefaultSelectedCaseId(nextState, action.payload),
      };
    }
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
      const nextState = {
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

      return {
        ...nextState,
        selectedCaseId: getNextSelectedCaseIdAfterAction(
          state,
          nextState,
          action.payload.tradeId,
        ),
      };
    }
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

  const visibleLists = getVisibleLists(state);
  const urgentCases = visibleLists.urgent;
  const queuedCases = visibleLists.queued;
  const reviewedCasesList = visibleLists.reviewed;
  const passedCasesList = visibleLists.passed;

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
