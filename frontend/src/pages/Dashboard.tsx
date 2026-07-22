/* VERSION 15 - Refactored */

import React, { useState, useRef } from "react";
import { useTriageWorkflow } from "../hooks/useTriageWorkflow";
import { CaseAuditWorkspace } from "../components/triage/CaseAuditWorkspace";
import { Clock, ShieldAlert } from "lucide-react";

// Helper wrappers inside Dashboard to convert list item rows to standard enterprise bands
const getListRiskBadge = (score: number) => {
  if (score >= 75) return <span className="bg-rose-950/40 text-rose-400 px-2 py-0.5 rounded border border-rose-900/30 font-bold text-[9px]">CRITICAL</span>;
  if (score >= 70) return <span className="bg-orange-950/30 text-orange-400 px-2 py-0.5 rounded border border-orange-900/20 text-[9px]">HIGH</span>;
  if (score >= 35) return <span className="bg-amber-950/20 text-amber-400 px-2 py-0.5 rounded border border-amber-900/10 text-[9px]">MED</span>;
  return <span className="bg-emerald-950/20 text-emerald-400 px-2 py-0.5 rounded border border-emerald-900/10 text-[9px]">LOW</span>;
};

const getListConfidenceBadge = (score: number) => {
  if (score >= 0.8) return <span className="text-emerald-400 text-[10px] font-medium">HIGH</span>;
  if (score < 0.5) return <span className="text-rose-400 text-[10px] font-medium">LOW</span>;
  return <span className="text-amber-400 text-[10px] font-medium">MED</span>;
};

export default function Dashboard() {
  const workflow = useTriageWorkflow();

  // --- Spreadsheet Column Resize Frameworks ---
  const [urgentWidths, setUrgentWidths] = useState({ tradeId: 80, risk: 80, conf: 80, reason: 120 });
  const [queuedWidths, setQueuedWidths] = useState({ tradeId: 80, priority: 100, risk: 80, conf: 80, reason: 120 });
  const [reviewedWidths, setReviewedWidths] = useState({ tradeId: 80, type: 80, amount: 80, status: 80, notes: 340 });
  const [passedWidths, setPassedWidths] = useState({ tradeId: 80, asset: 80, value: 80, confidence: 80, status: 140 });

  const dragInfo = useRef<{ table: "urgent" | "queued" | "reviewed" | "passed"; col: string; startX: number; startWidth: number } | null>(null);

  const handleMouseDown = (table: "urgent" | "queued" | "reviewed" | "passed", col: string, e: React.MouseEvent) => {
    e.preventDefault();
    let currentWidths: any = table === "urgent" ? urgentWidths : table === "queued" ? queuedWidths : table === "reviewed" ? reviewedWidths : passedWidths;
    dragInfo.current = { table, col, startX: e.clientX, startWidth: currentWidths[col] };
    document.addEventListener("mousemove", handleMouseMove);
    document.addEventListener("mouseup", handleMouseUp);
  };

  const handleMouseMove = (e: MouseEvent) => {
    if (!dragInfo.current) return;
    const { table, col, startX, startWidth } = dragInfo.current;
    const deltaX = e.clientX - startX;
    const newWidth = Math.max(60, startWidth + deltaX);

    if (table === "urgent") setUrgentWidths((prev) => ({ ...prev, [col]: newWidth }));
    else if (table === "queued") setQueuedWidths((prev) => ({ ...prev, [col]: newWidth }));
    else if (table === "reviewed") setReviewedWidths((prev) => ({ ...prev, [col]: newWidth }));
    else setPassedWidths((prev) => ({ ...prev, [col]: newWidth }));
  };

  const handleMouseUp = () => {
    dragInfo.current = null;
    document.removeEventListener("mousemove", handleMouseMove);
    document.removeEventListener("mouseup", handleMouseUp);
  };

  const renderPolicies = (policies: any) => {
    if (!policies) return <span className="text-[10px] text-slate-500">No policies attached.</span>;
    
    let items: string[] = [];
    
    // If it's already an array, flatten any nested string elements just in case
    if (Array.isArray(policies)) {
      items = policies.flatMap(p => {
        if (typeof p === 'string' && (p.startsWith('[') || p.includes(','))) {
          return p.replace(/[\[\]"']/g, "").split(",").map(str => str.trim());
        }
        return String(p).replace(/[\[\]"']/g, "").trim();
      });
    } else if (typeof policies === "string") {
      // If it's a raw string representation
      items = policies.replace(/[\[\]"']/g, "").split(",").map((p) => p.trim());
    }

    // Filter out empty spaces or null string artifacts
    const cleanItems = items.map(p => p.trim()).filter(p => p.length > 0 && p !== "None" && p !== "null");

    if (cleanItems.length === 0) {
      return <span className="text-[10px] text-slate-500">No policies attached.</span>;
    }

    return cleanItems.map((p, i) => (
      <span key={i} className="px-1.5 py-0.5 bg-slate-950 text-[10px] rounded border border-slate-800 text-purple-300 font-mono max-w-[140px] truncate">
        {p}
      </span>
    ));
  };

  return (
    <div className="p-2 h-screen bg-slate-950 text-slate-100 flex flex-col gap-0 overflow-hidden select-none">
      {/* Top Header Metrics Row */}
      <div className="flex items-center justify-between border-b border-slate-900 pb-0 shrink-0">
        <div className="flex items-center gap-4">
          <h1 className="text-sm font-black uppercase tracking-wider text-slate-200 m-4 leading-none">
            AI Compliance Review Copilot
          </h1>
          
          {/* Tightened View Navigation Tabs */}
          <div className="flex bg-slate-900 p-0.5 rounded border border-slate-800 gap-0.5 scale-95 origin-left">
            <button 
              onClick={() => workflow.setView("active")} 
              className={`px-3 py-0.5 text-[11px] font-semibold rounded transition-all ${workflow.activeView === "active" ? "bg-indigo-600 text-white" : "text-slate-400 hover:text-slate-200"}`}
            >
              Active ({workflow.urgentCases.length + workflow.queuedCases.length})
            </button>
            <button 
              onClick={() => workflow.setView("reviewed")} 
              className={`px-3 py-0.5 text-[11px] font-semibold rounded transition-all ${workflow.activeView === "reviewed" ? "bg-indigo-600 text-white" : "text-slate-400 hover:text-slate-200"}`}
            >
              Reviewed ({workflow.reviewedCasesList.length})
            </button>
            <button 
              onClick={() => workflow.setView("passed")} 
              className={`px-3 py-0.5 text-[11px] font-semibold rounded transition-all ${workflow.activeView === "passed" ? "bg-indigo-600 text-white" : "text-slate-400 hover:text-slate-200"}`}
            >
              Passed ({workflow.passedCasesList.length})
            </button>
          </div>
        </div>

        {/* Denser Counter Badges */}
        <div className="flex items-center gap-1.5 transform scale-95 origin-right">
          <div className="bg-rose-950/20 border border-rose-500/20 rounded px-2 py-0.5 text-[11px] font-medium">
            <span className="text-rose-400">Urgent:</span> <span className="font-bold text-rose-200">{workflow.urgentCases.length}</span>
          </div>
          <div className="bg-amber-950/20 border border-amber-500/20 rounded px-2 py-0.5 text-[11px] font-medium">
            <span className="text-amber-400">Review:</span> <span className="font-bold text-amber-200">{workflow.queuedCases.length}</span>
          </div>
          <div className="bg-emerald-950/20 border border-emerald-500/20 rounded px-2 py-0.5 text-[11px] font-medium">
            <span className="text-emerald-400">Reviewed Today:</span> <span className="font-bold text-emerald-200">{workflow.reviewedTodayCount}</span>
          </div>
        </div>
      </div>

      {/* Primary Split Workspace */}
      <div className="flex-1 grid grid-rows-[33fr_67fr] gap-2 min-h-0">
        
        {/* UPPER VIEW GRIDS */}
        <div className="min-h-0">
          {workflow.activeView === "active" && (
            <div className="grid grid-cols-2 gap-2 h-full min-h-0">
              {/* Table A: Urgent Items */}
              <div className="bg-slate-900 border border-slate-800 rounded-md p-1.5 flex flex-col min-h-0">
                <div className="flex items-center gap-1 border-b border-slate-800 pb-0.5 mb-1 shrink-0">
                  <ShieldAlert className="w-3.5 h-3.5 text-rose-400" />
                  <h2 className="text-[10px] font-bold text-rose-400 uppercase tracking-wider">Urgent Action Required</h2>
                </div>
                <div className="flex-1 overflow-auto custom-scrollbar border border-slate-800/30 rounded min-h-0">
                  {workflow.urgentCases.length === 0 ? <p className="text-xs text-slate-500 p-2 italic">No urgent cases outstanding.</p> : (
                    <table className="text-left text-xs border-collapse table-fixed w-max min-w-full">
                      <thead className="sticky top-0 bg-slate-900 text-slate-400 font-bold uppercase text-[9px] border-b border-slate-800 z-10">
                        <tr>
                          <th style={{ width: urgentWidths.tradeId }} className="p-1 relative group">Trade ID<div onMouseDown={(e) => handleMouseDown("urgent", "tradeId", e)} className="absolute right-0 top-0 bottom-0 w-1 cursor-col-resize group-hover:bg-purple-500/30" /></th>
                          <th style={{ width: urgentWidths.risk }} className="p-1 text-center relative group">Risk<div onMouseDown={(e) => handleMouseDown("urgent", "risk", e)} className="absolute right-0 top-0 bottom-0 w-1 cursor-col-resize group-hover:bg-purple-500/30" /></th>
                          <th style={{ width: urgentWidths.conf }} className="p-1 text-center relative group">Confidence<div onMouseDown={(e) => handleMouseDown("urgent", "conf", e)} className="absolute right-0 top-0 bottom-0 w-1 cursor-col-resize group-hover:bg-purple-500/30" /></th>
                          <th style={{ width: urgentWidths.reason }} className="p-1 pl-2">Flag Reasons</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-800/30">
                        {workflow.urgentCases.map((c) => (
                          <tr key={c.trade_id} onClick={() => workflow.selectCase(c.trade_id)} className={`cursor-pointer text-[11px] ${workflow.selectedCase?.trade_id === c.trade_id ? "bg-rose-950/40 font-semibold border-l-2 border-rose-500 text-rose-200" : "hover:bg-slate-800/20 text-slate-300"}`}>
                            <td className="p-1 font-mono truncate">{c.trade_id}</td>
                            {/* <td className="p-1 text-right font-mono text-rose-400">{(1 - (Number(c.compliance_probability) || 1)).toFixed(2)}</td> */}
                            <td className="p-1 text-center font-mono truncate">
                              {getListRiskBadge(c.risk_score)}
                            </td>
                            <td className="p-1 text-center font-mono truncate">
                              {getListConfidenceBadge(c.confidence_score)}
                            </td>
                            {/* <td className="p-1 text-right font-mono text-fuchsia-400">{(Number(c.risk_score))}</td>
                            <td className="p-1 text-right font-mono text-sky-400">{(Number(c.confidence_score) || 0).toFixed(2)}</td> */}
                            <td className="p-1 pl-2 truncate text-[10px]">
                              {typeof c.flag_reasons === 'string' ? c.flag_reasons.replace(/[\[\]"']/g, "") : String(c.flag_reasons || '')}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  )}
                </div>
              </div>

              {/* Table B: Review/Queued Items */}
              <div className="bg-slate-900 border border-slate-800 rounded-md p-1.5 flex flex-col min-h-0">
                <div className="flex items-center gap-1 border-b border-slate-800 pb-0.5 mb-1 shrink-0">
                  <Clock className="w-3.5 h-3.5 text-amber-400" />
                  <h2 className="text-[10px] font-bold text-amber-400 uppercase tracking-wider">Review Queue</h2>
                </div>
                <div className="flex-1 overflow-auto custom-scrollbar border border-slate-800/30 rounded min-h-0">
                  {workflow.queuedCases.length === 0 ? <p className="text-xs text-slate-500 p-1 italic">Review queue empty.</p> : (
                    <table className="text-left text-xs border-collapse table-fixed w-max min-w-full">
                      <thead className="sticky top-0 bg-slate-900 text-slate-400 font-bold uppercase text-[9px] border-b border-slate-800 z-10">
                        <tr>
                          <th style={{ width: queuedWidths.tradeId }} className="p-1 relative group">Trade ID<div onMouseDown={(e) => handleMouseDown("queued", "tradeId", e)} className="absolute right-0 top-0 bottom-0 w-1 cursor-col-resize group-hover:bg-purple-500/30" /></th>
                          <th style={{ width: queuedWidths.priority }} className="p-1 text-center">Priority Score</th>
                          <th style={{ width: queuedWidths.risk }} className="p-1 text-center">Risk</th>
                          <th style={{ width: queuedWidths.conf }} className="p-1 text-center">Confidence</th>
                          <th style={{ width: queuedWidths.reason }} className="p-1 pl-2">Flag Reasons</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-800/30">
                        {workflow.queuedCases.map((c) => (
                          <tr key={c.trade_id} onClick={() => workflow.selectCase(c.trade_id)} className={`cursor-pointer text-[11px] ${workflow.selectedCase?.trade_id === c.trade_id ? "bg-purple-950/40 font-semibold border-l-2 border-purple-500 text-purple-200" : "hover:bg-slate-800/20 text-slate-300"}`}>
                            <td className="p-1 font-mono truncate">{c.trade_id}</td>
                            <td className="p-1 text-center font-mono font-bold text-amber-400">{c.priority_score.toFixed(0) ?? "0"}</td>
                            <td className="p-1 text-center font-mono truncate">
                              {getListRiskBadge(c.risk_score)}
                            </td>
                            <td className="p-1 text-center font-mono truncate">
                              {getListConfidenceBadge(c.confidence_score)}
                            </td>
                            {/* <td className="p-1 text-right font-mono text-fuchsia-400">{(Number(c.risk_score))}</td>
                            <td className="p-1 text-right font-mono text-sky-400">{(Number(c.confidence_score) || 0).toFixed(2)}</td> */}
                            <td className="p-1 pl-2 truncate text-[10px]">
                              {typeof c.flag_reasons === 'string' ? c.flag_reasons.replace(/[\[\]"']/g, "") : String(c.flag_reasons || '')}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  )}
                </div>
              </div>
            </div>
          )}

          {/* Table C: Historical Audited Logs */}
          {workflow.activeView === "reviewed" && (
            <div className="bg-slate-900 border border-slate-800 rounded-md p-1.5 flex flex-col h-full min-h-0">
              <div className="flex-1 overflow-auto custom-scrollbar border border-slate-800/30 rounded min-h-0">
                {workflow.reviewedCasesList.length === 0 ? <p className="text-slate-500 text-xs p-3 italic text-center">No logs audited yet.</p> : (
                  <table className="text-left text-xs border-collapse table-fixed w-max min-w-full">
                    <thead className="sticky top-0 bg-slate-900 text-slate-400 font-bold uppercase text-[9px] border-b border-slate-800 z-10">
                      <tr>
                        <th style={{ width: reviewedWidths.tradeId }} className="p-1 relative group">Trade ID<div onMouseDown={(e) => handleMouseDown("reviewed", "tradeId", e)} className="absolute right-0 top-0 bottom-0 w-1 cursor-col-resize group-hover:bg-purple-500/30" /></th>
                        <th style={{ width: reviewedWidths.type }} className="p-1">Investment Type</th>
                        <th style={{ width: reviewedWidths.amount }} className="p-1 text-right">Amount</th>
                        <th style={{ width: reviewedWidths.status }} className="p-1 text-center">Review Outcome</th>
                        <th style={{ width: reviewedWidths.notes }} className="p-1 pl-3">Reviewer Notes</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-800/30">
                      {workflow.reviewedCasesList.map((c) => {
                        const s = workflow.caseStates[c.trade_id];
                        return (
                          <tr key={c.trade_id} onClick={() => workflow.selectCase(c.trade_id)} className={`cursor-pointer text-[11px] ${workflow.selectedCase?.trade_id === c.trade_id ? "bg-emerald-950/40 font-semibold border-l-2 border-emerald-500 text-emerald-200" : "hover:bg-slate-800/20 text-slate-300"}`}>
                            <td className="p-1 font-mono truncate">{c.trade_id}</td>
                            <td className="p-1 truncate">{c.investment_type || "N/A"}</td>
                            <td className="p-1 text-right font-mono text-emerald-400">${Number(c.investment_amount || 0).toLocaleString()}</td>
                            <td className="p-1 text-center">
                              <span className={`px-2 py-0.5 rounded text-[9px] font-bold ${s?.actionType === "Approved" ? "bg-emerald-950 text-emerald-400" : s?.actionType === "Rejected" ? "bg-rose-950 text-rose-400" : s?.actionType === "Escalated" ? "bg-amber-950 text-amber-400" : "bg-slate-950 text-slate-400 "}`}>{s?.actionType || "Processed"}</span>
                            </td>
                            <td className="p-1 pl-3 italic text-slate-400 truncate">{s?.notes || "—"}</td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                )}
              </div>
            </div>
          )}

          {/* Table D: Straight-Through System Passed Logs */}
          {workflow.activeView === "passed" && (
            <div className="bg-slate-900 border border-slate-800 rounded-md p-1.5 flex flex-col h-full min-h-0">
              <div className="flex-1 overflow-auto custom-scrollbar border border-slate-800/30 rounded min-h-0">
                {workflow.passedCasesList.length === 0 ? <p className="text-slate-500 text-xs p-3 italic text-center">No auto-passed logs found.</p> : (
                  <table className="text-left text-xs border-collapse table-fixed w-max min-w-full">
                    <thead className="sticky top-0 bg-slate-900 text-slate-400 font-bold uppercase text-[9px] border-b border-slate-800 z-10">
                      <tr>
                        <th style={{ width: passedWidths.tradeId }} className="p-1 relative group">Trade ID<div onMouseDown={(e) => handleMouseDown("passed", "tradeId", e)} className="absolute right-0 top-0 bottom-0 w-1 cursor-col-resize group-hover:bg-purple-500/30" /></th>
                        <th style={{ width: passedWidths.asset }} className="p-1">Investment Type</th>
                        <th style={{ width: passedWidths.value }} className="p-1 text-right">Risk</th>
                        <th style={{ width: passedWidths.confidence }} className="p-1 text-right">Confidence</th>
                        <th style={{ width: passedWidths.status }} className="p-1 text-center">Status</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-800/30">
                      {workflow.passedCasesList.map((c) => (
                        <tr key={c.trade_id} onClick={() => workflow.selectCase(c.trade_id)} className={`cursor-pointer text-[11px] ${workflow.selectedCase?.trade_id === c.trade_id ? "bg-indigo-950/40 font-semibold border-l-2 border-indigo-500 text-indigo-200" : "hover:bg-slate-800/20 text-slate-300"}`}>
                          <td className="p-1 font-mono truncate">{c.trade_id}</td>
                          <td className="p-1 truncate">{c.investment_type || "N/A"}</td>
                          <td className="p-1 text-right font-mono truncate">
                            {getListRiskBadge(c.risk_score)}
                          </td>
                          <td className="p-1 text-right font-mono truncate">
                            {getListConfidenceBadge(c.confidence_score)}
                          </td>
                          {/* <td className="p-1 text-right font-mono text-fuchsia-400 truncate">{Number(c.risk_score).toLocaleString()}</td>
                          <td className="p-1 text-right font-mono text-sky-400">{(Number(c.confidence_score) || 1).toFixed(2)}</td> */}
                          <td className="p-1 text-center"><span className="text-[9px] font-bold bg-emerald-950/30 text-emerald-400 px-2 py-0.5 rounded border border-emerald-900/20">{c.escalation_level==="none" ? "AUTO-PASSED" : c.escalation_level.toUpperCase()}</span></td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                )}
              </div>
            </div>
          )}
        </div>

        {/* LOWER WORKSPACE AREA */}
        <div className="bg-slate-900 border border-slate-800 rounded-md p-0 flex flex-col min-h-0 justify-between shadow-2xl">
          <CaseAuditWorkspace
            selectedCase={workflow.selectedCase}
            caseStates={workflow.caseStates}
            activeView={workflow.activeView}
            onUpdateNotes={workflow.updateNotes}
            onExecuteAction={workflow.executeAction}
            renderPolicies={renderPolicies}
          />
        </div>

      </div>
    </div>
  );
}
