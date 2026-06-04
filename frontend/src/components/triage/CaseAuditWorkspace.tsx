import React, { useState } from "react";
import { Briefcase, ShieldCheck, Scale, Database, Bookmark, User, Layers, BrainCircuit } from "lucide-react";
import { type TradeCase, type CaseAuditState } from "../../hooks/useTriageWorkflow";
import { ExecutionFormTray } from "./ExecutionFormTray";
import { formatCurrency, formatIncomeK } from "../../utils/formatters";

interface CaseAuditWorkspaceProps {
  selectedCase: TradeCase | null;
  caseStates: Record<string, CaseAuditState>;
  activeView: "active" | "reviewed" | "passed";
  onUpdateNotes: (tradeId: string, text: string) => void;
  onExecuteAction: (tradeId: string, status: "Reviewed" | "Escalated", actionType: "Rejected" | "Approved" | "Escalated", notes: string) => void;
  renderPolicies: (policies: any) => React.ReactNode;
}

// Fixed to provide distinct visual indicators for system confidence thresholds
const getReliabilityTier = (score: number): { label: string; color: string } => {
  if (score >= 0.8) return { label: "HIGH", color: "text-emerald-400 border-emerald-900/50 bg-emerald-950/20" };
  if (score < 0.5) return { label: "LOW", color: "text-rose-400 border-rose-900/50 bg-rose-950/20 animate-pulse" };
  return { label: "MEDIUM", color: "text-amber-400 border-amber-900/50 bg-amber-950/20" };
};

// New risk tiering utility synchronized with policy_rules.py boundaries
const getRiskTier = (score: number): { label: string; color: string } => {
  if (score >= 75) return { label: "CRITICAL", color: "text-rose-400 border-rose-900/50 bg-rose-950/30 font-black" };
  if (score >= 70) return { label: "HIGH", color: "text-orange-400 border-orange-900/50 bg-orange-950/20" };
  if (score >= 35) return { label: "MEDIUM", color: "text-amber-400 border-amber-900/50 bg-amber-950/10" };
  return { label: "LOW", color: "text-emerald-400 border-emerald-900/50 bg-emerald-950/10" };
};

const getManualReviewBadge = (status: string, action: string | null) => {
  if (status === "Escalated") {
    return { label: "MANUALLY ESCALATED", color: "bg-amber-950/40 text-amber-400 border-amber-700/40" };
  }
  if (status === "Reviewed") {
    if (action === "Approved") return { label: "MANUALLY APPROVED", color: "bg-emerald-950/50 text-emerald-400 border-emerald-700/40" };
    if (action === "Rejected") return { label: "MANUALLY REJECTED", color: "bg-rose-950/50 text-rose-400 border-rose-700/40" };
  }
  return { label: "UNREVIEWED", color: "bg-slate-900 text-white border-slate-800" };
};

export const CaseAuditWorkspace: React.FC<CaseAuditWorkspaceProps> = ({
  selectedCase,
  caseStates,
  activeView,
  onUpdateNotes,
  onExecuteAction,
  renderPolicies,
}) => {
  const c = selectedCase;
  const [activeTab, setActiveTab] = useState<"client" | "advisor">("client");

  if (!c) {
    return (
      <div className="flex-1 flex flex-col items-center justify-center text-slate-500 py-12 border border-dashed border-slate-800 rounded bg-slate-950/10">
        <Scale className="w-8 h-8 mb-2 text-slate-700 animate-pulse" />
        <p className="text-xs font-mono tracking-wider">SELECT A CASE ROW FROM THE PRIORITY REGISTERS TO MOUNT WORKSPACE</p>
      </div>
    );
  }

  const currentState = caseStates[c.trade_id] || { reviewStatus: "Unreviewed", actionType: null, notes: "" };
  
  const rawConfidence = c.confidence_score !== undefined && c.confidence_score !== null ? Number(c.confidence_score) : 1.0;
  const reliability = getReliabilityTier(rawConfidence);
  
  const rawRisk = c.risk_score !== undefined && c.risk_score !== null ? Number(c.risk_score) : 0;
  const isCompliant = c.compliance_label === true || c.compliance_label === 1;
  const manualReview = getManualReviewBadge(currentState.reviewStatus || "Unreviewed", currentState.actionType || null);

  const rawChunks: any[] = Array.isArray(c.retrieved_chunks)
    ? c.retrieved_chunks
    : typeof c.retrieved_chunks === "string" && (c.retrieved_chunks as string).startsWith("[")
    ? (() => { try { return JSON.parse(c.retrieved_chunks as string); } catch { return []; } })()
    : [];

  return (
    <div className="w-full flex flex-col lg:flex-row gap-4 min-h-0 bg-slate-900/40 text-slate-200 select-none">
      
      {/* ================================================================= */}
      {/* LEFT COLUMN: CRITICAL METADATA AND WORKSPACE TRAY (50% Width)    */}
      {/* ================================================================= */}
      <div className="flex-[50] flex flex-col gap-0 min-w-0 bg-slate-950/40 p-3 rounded border border-slate-800/50 justify-between">
        
        <div className="flex flex-col gap-0">
          
          {/* Strict Single-Row Title & Metrics Control Panel Header */}
          <div className="flex items-center justify-between border-b border-slate-800/80 pb-1.5 gap-2 overflow-hidden w-full">
            <div className="flex items-center gap-1.5 min-w-0 shrink-0">
              <div className="p-1 rounded bg-purple-950/50 border border-purple-800/30 text-purple-400 shrink-0">
                <Briefcase className="w-3 h-3" />
              </div>
              <span className="font-mono text-xs font-bold tracking-tight text-slate-100 shrink-0">{c.trade_id}</span>
              
              <span className="text-[10px] px-1.5 py-0.5 rounded font-mono font-bold bg-fuchsia-950/40 border border-fuchsia-900/40 text-fuchsia-400 truncate max-w-[170px]">
                ${formatCurrency(c.investment_amount.toFixed(2))} ({c.investment_type || "ASSET"})
              </span>
            </div>

            <div className="flex items-center gap-1 font-mono text-[11px] shrink-0">
              <span className="bg-slate-950 px-1.5 py-0.5 rounded border border-slate-800/60 text-slate-400 uppercase">
                RISK: <span className={`${getRiskTier(selectedCase.risk_score).color} font-bold`}>{getRiskTier(selectedCase.risk_score).label}</span>
              </span>
              <span className="bg-slate-950 px-1.5 py-0.5 rounded border border-slate-800/60 text-slate-400 uppercase">
                CONF: <span className={`${getReliabilityTier(selectedCase.confidence_score).color} font-bold`}>{getReliabilityTier(selectedCase.confidence_score).label}</span>
              </span>
              <span className="bg-slate-950 px-1.5 py-0.5 rounded border border-slate-800/60 text-slate-400 uppercase">
                ROUTING: <span className={`font-bold ${
                  {
                    urgent: "text-rose-400",
                    priority: "text-amber-400",
                    queue: "text-amber-400",
                    none: "text-emerald-400"
                  }[(c.escalation_level || "QUEUE").toLowerCase()] || "text-purple-400"
                }`}>
                  {c.escalation_level || "QUEUE"}
                </span>
              </span>
              <span className={`font-mono font-bold px-1.5 py-0.5 rounded border ${manualReview.color}`}>
                {manualReview.label}
              </span>
            </div>
          </div>

          {/* Micro Tabs Navigation Layout */}
          <div className="flex border-b border-slate-800/40 gap-1 text-[10px] font-mono mt-0.5">
            <button
              onClick={() => setActiveTab("client")}
              className={`px-2.5 py-0.5 border-t border-x rounded-t transition-all ${
                activeTab === "client"
                  ? "bg-slate-900/60 border-slate-800 text-sky-400 font-bold"
                  : "border-transparent text-slate-500 hover:text-slate-300"
              }`}
            >
              <div className="flex items-center gap-1">
                <User className="w-2.5 h-2.5" /> Client Profile
              </div>
            </button>
            <button
              onClick={() => setActiveTab("advisor")}
              className={`px-2.5 py-0.5 border-t border-x rounded-t transition-all ${
                activeTab === "advisor"
                  ? "bg-slate-900/60 border-slate-800 text-purple-400 font-bold"
                  : "border-transparent text-slate-500 hover:text-slate-300"
              }`}
            >
              <div className="flex items-center gap-1">
                <Layers className="w-2.5 h-2.5" /> Advisor Context
              </div>
            </button>
          </div>

          {/* Expanded Micro Tab Viewscreen Frame */}
          <div className="min-h-[120px] max-h-[120px] overflow-y-auto custom-scrollbar bg-slate-900/30 p-2 rounded border border-slate-800/40 font-mono text-[11px] leading-relaxed">
            {activeTab === "client" ? (
              <div className="grid grid-cols-2 gap-x-3 gap-y-1">
                <div>
                  <span className="text-[9px] block text-slate-500 uppercase tracking-wider">Age / Income</span>
                  <span className="text-slate-300">{c.client_age || "??"} Yrs / ${formatIncomeK(c.client_income)}</span>
                </div>
                <div>
                  <span className="text-[9px] block text-slate-500 uppercase tracking-wider">Objective / Horizon</span>
                  <span className="text-slate-300 truncate block">{c.investment_objective || "N/A"} / {c.investment_time_horizon || "N/A"}</span>
                </div>
                <div>
                  <span className="text-[9px] block text-slate-500 uppercase tracking-wider">KYC Status</span>
                  <span className="text-slate-300 font-bold truncate block">{c.kyc_completeness || "N/A"}</span>
                </div>
                <div>
                  <span className="text-[9px] block text-slate-500 uppercase tracking-wider">Experience / Risk Profile</span>
                  <span className="text-slate-300 truncate block">{c.investment_experience || "Intermediate"} / {c.risk_tolerance || "N/A"}</span>
                </div>
              </div>
            ) : (
              <div className="flex flex-col gap-2 w-full">
                {/* Clean Advisor Metadata Top Row */}
                <div className="flex items-center gap-4 bg-slate-950/30 p-1 px-1.5 rounded border border-slate-800/40 w-full text-[10px]">
                  <div>
                    <span className="text-slate-500 font-bold mr-1">ID:</span>
                    <span className="text-slate-300 font-mono">{c.advisor_id || "N/A"}</span>
                  </div>
                  <div className="truncate">
                    <span className="text-slate-500 font-bold mr-1">Tenure / Risk History:</span>
                    <span className="text-slate-300 truncate">{c.advisor_experience || "N/A"} / {c.advisor_history_risk || "Clear Profile"}</span>
                  </div>
                </div>

                {/* Remade Rationale Text Area (Wrapping + Scrollbars) */}
                <div className="flex flex-col gap-0.5">
                  <span className="text-[9px] text-slate-500 uppercase font-bold tracking-wider">Suitability Rationale File</span>
                  <div className="max-h-[48px] overflow-y-auto custom-scrollbar bg-slate-950/20 p-1 rounded border border-slate-800/30">
                    <p className="text-[10px] text-slate-300 whitespace-pre-wrap select-all break-words leading-tight">
                      {c.advisor_rationale || "No explicit rationale filed."}
                    </p>
                  </div>
                </div>

                {/* Remade Internal Notes Text Area (Wrapping + Scrollbars) */}
                <div className="flex flex-col gap-0.5">
                  <span className="text-[9px] text-slate-500 uppercase font-bold tracking-wider">Internal Advisor Notes</span>
                  <div className="max-h-[48px] overflow-y-auto custom-scrollbar bg-slate-950/20 p-1 rounded border border-slate-800/30">
                    <p className="text-[10px] text-slate-400 italic whitespace-pre-wrap select-all break-words leading-tight">
                      {c.advisor_notes || "—"}
                    </p>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* AI Evaluation Box */}
          <div className="flex flex-col gap-0 bg-slate-900/30 p-2 rounded border border-slate-800/60 h-[120px] shrink-0 mt-1.5">
            <div className="flex items-center justify-between border-b border-slate-800/50 pb-1 mb-1">
              <div className="flex items-center gap-1.5">
                <BrainCircuit className="w-3 h-3 text-sky-400" />
                <span className="text-[9px] font-black uppercase text-sky-400 tracking-wider">AI Audit Evaluation Analysis</span>
              </div>
              <span className={`text-[9px] font-mono font-black px-1.5 py-0.5 rounded border tracking-widest ${
                isCompliant 
                  ? "bg-emerald-950/50 border-emerald-800/80 text-emerald-400" 
                  : "bg-rose-950/50 border-rose-800/80 text-rose-400"
              }`}>
                {isCompliant ? "COMPLIANT" : "NON-COMPLIANT"}
              </span>
            </div>
            <p className="text-[11px] text-slate-300 leading-relaxed font-sans select-text overflow-y-auto max-h-[85px] custom-scrollbar pr-1">
              {c.flag_reasons || "No risk summaries compiled for this transaction ledger row."}
            </p>
          </div>
        </div>

        {/* Form Tray Area Featuring Expanded Notes Workspace */}
        <div className="mt-1 pt-1 border-t border-slate-800/60">
          <ExecutionFormTray
            tradeId={c.trade_id}
            initialNotes={currentState.notes}
            isAutoPassed={activeView === "passed"}
            onUpdateNotes={onUpdateNotes}
            onExecuteAction={onExecuteAction}
          />
        </div>
      </div>

      {/* ================================================================= */}
      {/* RIGHT COLUMN: RAG EVIDENCE & POLICY VAULT                        */}
      {/* ================================================================= */}
      <div className="flex-[50] flex flex-col gap-2.5 min-w-0 bg-slate-950/40 p-3 rounded border border-slate-800/50 max-h-[460px] lg:max-h-none">
        
        {/* Attached Regulations Badge Header Ribbon */}
        <div className="flex flex-col gap-1.5">
          <div className="flex items-center gap-1.5 text-purple-400">
            <Scale className="w-3.5 h-3.5" />
            <span className="text-[10px] font-black uppercase tracking-wider">Retrieved Attached Regulations</span>
          </div>
          <div className="flex flex-wrap gap-1 items-start content-start overflow-y-auto max-h-[48px] bg-slate-900/30 p-2 rounded border border-slate-800/50 w-full custom-scrollbar">
            {c.retrieved_policies && (Array.isArray(c.retrieved_policies) || typeof c.retrieved_policies === "string") ? (
              renderPolicies(c.retrieved_policies)
            ) : (
              <span className="text-[10px] text-slate-600 italic tracking-wide">No policy IDs attached to case metadata.</span>
            )}
          </div>
        </div>

        {/* Source RAG Text Chunk Document Vault */}
        <div className="flex flex-col flex-1 min-h-0 gap-1 mt-1">
          <div className="flex items-center justify-between text-emerald-400 border-b border-slate-800/80 pb-1">
            <div className="flex items-center gap-1.5">
              <Database className="w-3.5 h-3.5" />
              <span className="text-[10px] font-black uppercase tracking-wider">Vector Corpus Source Evidence Text Blocks</span>
            </div>
            <span className="text-[9px] font-mono bg-emerald-950/40 px-1.5 py-0.2 rounded border border-emerald-900/40 text-emerald-500 font-bold">
              COUNT: {rawChunks.length}
            </span>
          </div>

          <div className="flex-1 overflow-y-auto pr-1 flex flex-col gap-2.5 custom-scrollbar max-h-[290px] lg:max-h-[310px]">
            {rawChunks.length > 0 ? (
              rawChunks.map((chunk, index) => {
                const isObject = chunk !== null && typeof chunk === "object";
                const textContent = isObject ? chunk.text || "" : String(chunk);
                const policyId = isObject ? chunk.policy_id : null;
                const scope = isObject ? chunk.section_scope : null;

                return (
                  <div key={index} className="p-2.5 rounded bg-slate-950/90 border border-slate-800 text-[11px] font-mono leading-relaxed relative group hover:border-slate-700/60 transition-colors">
                    <div className="flex flex-wrap items-center justify-between gap-2 mb-1.5 border-b border-slate-900 pb-1 text-slate-500 text-[9px] font-bold">
                      <div className="flex items-center gap-2">
                        <span className="text-purple-400/80 font-mono">SECTION CORPUS ANALYSIS MODULE</span>
                        {policyId && (
                          <span className="flex items-center gap-1 text-amber-500 bg-amber-950/20 px-1 rounded border border-amber-900/30">
                            <Bookmark className="w-2.5 h-2.5" /> {policyId}
                          </span>
                        )}
                        {scope && (
                          <span className="text-sky-400 bg-sky-950/20 px-1 rounded border border-sky-900/30">
                            Scope: {scope}
                          </span>
                        )}
                      </div>
                      <span className="bg-slate-900 px-1 rounded border border-slate-800 text-slate-400 uppercase tracking-widest text-[8px]">
                        BLOCK {index + 1}
                      </span>
                    </div>
                    <p className="text-slate-300 whitespace-pre-wrap select-all selection:bg-purple-950 selection:text-purple-200">
                      {textContent}
                    </p>
                  </div>
                );
              })
            ) : (
              <div className="flex flex-col items-center justify-center p-8 text-center rounded border border-dashed border-slate-800 text-[11px] text-slate-500 bg-slate-950/20 italic h-full">
                <ShieldCheck className="w-5 h-5 mb-1.5 text-slate-700 stroke-[1.5]" />
                No raw policy chunks retrieved from the semantic vector space for this audit.
              </div>
            )}
          </div>
        </div>

      </div>

    </div>
  );
};