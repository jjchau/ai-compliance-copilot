import React from "react";
import { Briefcase, User, FileText, HelpCircle, CheckCircle } from "lucide-react";
import type { TradeCase, CaseAuditState } from "../../hooks/useTriageWorkflow";
import { ExecutionFormTray } from "./ExecutionFormTray";
import { formatCurrency, formatIncomeK, formatFloatString, cleanComplianceRisk } from "../../utils/formatters";

interface CaseAuditWorkspaceProps {
  selectedCase: TradeCase | null;
  caseStates: Record<string, CaseAuditState>;
  activeView: "active" | "reviewed" | "passed";
  onUpdateNotes: (tradeId: string, text: string) => void;
  onExecuteAction: (tradeId: string, status: "Reviewed" | "Escalated", actionType: "Rejected" | "Approved" | "Escalated", notes: string) => void;
  renderPolicies: (policies: any) => React.ReactNode;
}

export const CaseAuditWorkspace: React.FC<CaseAuditWorkspaceProps> = ({
  selectedCase,
  caseStates,
  activeView,
  onUpdateNotes,
  onExecuteAction,
  renderPolicies,
}) => {
  if (!selectedCase) {
    return (
      <div className="h-full flex flex-col items-center justify-center text-slate-500 text-xs font-semibold border border-dashed border-slate-800 rounded p-6 text-center bg-slate-950/20">
        <CheckCircle className="w-10 h-10 text-emerald-500/30 mb-2" />
        <span className="text-slate-400 font-bold uppercase tracking-wider text-[11px]">All Tasks Cleared</span>
        <p className="text-[10px] text-slate-600 font-normal max-w-xs mt-1">
          Select an item from any active stream or historical tab above to evaluate details.
        </p>
      </div>
    );
  }

  const c = selectedCase;
  const currentState = caseStates[c.trade_id] || { reviewStatus: "Not reviewed", notes: "" };
  const isAutoPassed = activeView === "passed";
  const isRecCompliant = String(currentState.overriddenLabel || c.compliance_label || "").toLowerCase() === "compliant";

  return (
    <div className="flex flex-col h-full justify-between min-h-0 space-y-3">
      {/* Workspace Header Panel */}
      <div className="flex items-center justify-between border-b border-slate-800 pb-2 shrink-0">
        <div className="flex items-center gap-2">
          <span className="text-[9px] font-black uppercase bg-purple-950/40 px-2 py-0.5 rounded border border-purple-900/50 text-purple-400 tracking-wider">
            Selected Case Audit Space
          </span>
          <span className="text-xs font-mono font-bold text-slate-100 bg-slate-950 px-2 py-0.5 rounded border border-slate-800">
            {c.trade_id}
          </span>
        </div>

        <div className="flex items-center gap-2 bg-slate-950/60 px-2.5 py-1 rounded-md border border-slate-800/80 text-[10px] font-mono">
          <div className="flex items-center gap-1.5 border-r border-slate-800 pr-2">
            <span className="text-slate-500 font-sans text-[9px] font-bold uppercase">AI Rec:</span>
            <span className={`px-1 rounded text-[9px] font-black ${isRecCompliant ? "bg-emerald-950 text-emerald-400" : "bg-rose-950 text-rose-400"}`}>
              {isRecCompliant ? "COMPLIANT" : "FLAGGED"}
            </span>
          </div>
          <div className="flex items-center gap-1.5 border-r border-slate-800 pr-2 pl-1">
            <span className="text-slate-500 font-sans text-[9px] font-bold uppercase">Risk:</span>
            <span className="text-rose-400 font-bold">{formatFloatString(cleanComplianceRisk(c.compliance_probability))}</span>
          </div>
          <div className="flex items-center gap-1.5 pl-1">
            <span className="text-slate-500 font-sans text-[9px] font-bold uppercase">Conf:</span>
            <span className="text-sky-400 font-bold">{formatFloatString(c.confidence_score)}</span>
          </div>
        </div>
      </div>

      {/* Expanded 3 Column Matrix Grid Layout */}
      <div className="grid grid-cols-3 gap-3 flex-1 min-h-0 py-1">
        {/* MODULE A: Trade Details */}
        <div className="bg-slate-950/30 border border-slate-800/60 p-3 rounded-lg flex flex-col justify-between">
          <div className="flex items-center gap-1.5 border-b border-slate-800/80 pb-1.5 mb-2 text-purple-400 text-[10px] font-black uppercase tracking-widest shrink-0">
            <Briefcase className="w-3.5 h-3.5" />
            <span>Trade Details</span>
          </div>
          <div className="text-xs grid grid-cols-2 gap-x-3 gap-y-3 flex-1 items-center text-slate-300">
            <div>
              <span className="text-slate-500 text-[9px] uppercase font-bold tracking-wider block mb-0.5">Type</span>
              <div className="truncate font-semibold text-slate-200">{c.investment_type || "N/A"}</div>
            </div>
            <div>
              <span className="text-slate-500 text-[9px] uppercase font-bold tracking-wider block mb-0.5">Amount</span>
              <div className="truncate font-mono font-black text-emerald-400">${formatCurrency(c.investment_amount)}</div>
            </div>
            <div>
              <span className="text-slate-500 text-[9px] uppercase font-bold tracking-wider block mb-0.5">Notional</span>
              <div className="truncate font-mono font-medium text-slate-400">${formatCurrency(c.notional_value)}</div>
            </div>
            <div>
              <span className="text-slate-500 text-[9px] uppercase font-bold tracking-wider block mb-0.5">Timestamp</span>
              <div className="truncate font-mono text-[10px] text-slate-400">{c.timestamp || "—"}</div>
            </div>
          </div>
        </div>

        {/* MODULE B: Client Profile */}
        <div className="bg-slate-950/30 border border-slate-800/60 p-3 rounded-lg flex flex-col justify-between">
          <div className="flex items-center gap-1.5 border-b border-slate-800/80 pb-1.5 mb-2 text-sky-400 text-[10px] font-black uppercase tracking-widest shrink-0">
            <User className="w-3.5 h-3.5" />
            <span>Client Profile</span>
          </div>
          <div className="text-xs grid grid-cols-2 gap-x-3 gap-y-3 flex-1 items-center text-slate-300">
            <div>
              <span className="text-slate-500 text-[9px] uppercase font-bold tracking-wider block mb-0.5">Age / Income</span>
              <div className="truncate font-mono font-semibold text-slate-200">{c.client_age ?? "—"} / ${formatIncomeK(c.client_income)}</div>
            </div>
            <div>
              <span className="text-slate-500 text-[9px] uppercase font-bold tracking-wider block mb-0.5">Risk Profile</span>
              <div className="truncate font-black text-amber-400">{c.risk_tolerance || "—"}</div>
            </div>
            <div>
              <span className="text-slate-500 text-[9px] uppercase font-bold tracking-wider block mb-0.5">Experience</span>
              <div className="truncate text-slate-400">{c.investment_experience || "—"}</div>
            </div>
            <div>
              <span className="text-slate-500 text-[9px] uppercase font-bold tracking-wider block mb-0.5">Objective & Horizon</span>
              <div className="truncate text-slate-400 font-medium">
                {c.investment_objective || "—"} {c?.investment_time_horizon ? `(${c.investment_time_horizon})` : ""}
              </div>
            </div>
          </div>
        </div>

        {/* MODULE C: Advisor Info */}
        <div className="bg-slate-950/30 border border-slate-800/60 p-3 rounded-lg flex flex-col justify-between">
          <div className="flex items-center gap-1.5 border-b border-slate-800/80 pb-1.5 mb-2 text-amber-400 text-[10px] font-black uppercase tracking-widest shrink-0">
            <FileText className="w-3.5 h-3.5" />
            <span>Advisor Info</span>
          </div>
          <div className="text-xs grid grid-cols-2 gap-x-3 gap-y-3 flex-1 items-center text-slate-300">
            <div>
              <span className="text-slate-500 text-[9px] uppercase font-bold tracking-wider block mb-0.5">Advisor ID</span>
              <div className="truncate font-mono font-semibold text-slate-200">{c.advisor_id || "—"}</div>
            </div>
            <div>
              <span className="text-slate-500 text-[9px] uppercase font-bold tracking-wider block mb-0.5">Exp / Risk History</span>
              <div className="truncate text-slate-400">
                {c.advisor_experience || "—"} / <span className="text-rose-400 font-mono font-bold">{c.advisor_history_risk ?? 0}</span>
              </div>
            </div>
            <div>
              <span className="text-slate-500 text-[9px] uppercase font-bold tracking-wider block mb-0.5">Rationale File</span>
              <div className={`px-2 py-0.5 text-[9px] font-black rounded-md w-fit tracking-wider ${c.has_rationale ? "bg-emerald-950 text-emerald-400 border border-emerald-900/30" : "bg-slate-900 text-slate-500"}`}>
                {c.has_rationale ? "FILED" : "MISSING"}
              </div>
            </div>
            <div>
              <span className="text-slate-500 text-[9px] uppercase font-bold tracking-wider block mb-0.5">Desk Context</span>
              <div className="truncate text-slate-400 text-[11px] italic font-serif leading-tight">{c.advisor_notes || "None"}</div>
            </div>
          </div>
        </div>
      </div>

      {/* Policy Compliance Framework Bar Row */}
      <div className="border-t border-slate-800/80 pt-2 shrink-0 items-center bg-slate-950/40 p-2 rounded-lg text-xs flex justify-between gap-4">
        <div className="flex items-center gap-2 truncate max-w-xl">
          <HelpCircle className={`w-4 h-4 shrink-0 ${isAutoPassed ? "text-emerald-400" : "text-rose-400"}`} />
          <span className="text-[9px] uppercase text-slate-500 font-black tracking-wider shrink-0">Exception Rule:</span>
          <span className={`font-semibold truncate text-[11px] ${isAutoPassed ? "text-emerald-300" : "text-rose-300"}`}>
            {isAutoPassed ? "Trade met all baseline validation parameters. No active human review required." : (c.flag_reason || "None.")}
          </span>
        </div>
        <div className="flex items-center gap-1.5 overflow-hidden truncate">
          <span className="text-[9px] uppercase text-slate-600 font-black tracking-wider shrink-0">Attached Regulations:</span>
          <div className="flex gap-1 items-center truncate">
            {c.retrieved_policies && (Array.isArray(c.retrieved_policies) || typeof c.retrieved_policies === "string") ? (
              renderPolicies(c.retrieved_policies)
            ) : (
              <span className="text-[10px] text-slate-600 italic tracking-wide">No regulations attached</span>
            )}
          </div>
        </div>
      </div>

      {/* Action Tray Container */}
      <ExecutionFormTray
        tradeId={c.trade_id}
        initialNotes={currentState.notes}
        isAutoPassed={isAutoPassed}
        onUpdateNotes={onUpdateNotes}
        onExecuteAction={onExecuteAction}
      />
    </div>
  );
};