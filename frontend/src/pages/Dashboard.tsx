/* VERSION 15 - Refactored */

import React, { useState, useRef } from "react";
import { useTriageWorkflow } from "../hooks/useTriageWorkflow";
import { CaseAuditWorkspace } from "../components/triage/CaseAuditWorkspace";
import { CheckCircle, Clock, ShieldAlert } from "lucide-react";

export default function Dashboard() {
  const workflow = useTriageWorkflow();

  // --- Spreadsheet Column Resize Frameworks ---
  const [urgentWidths, setUrgentWidths] = useState({ tradeId: 100, risk: 85, conf: 85, reason: 320 });
  const [queuedWidths, setQueuedWidths] = useState({ tradeId: 100, priority: 75, risk: 85, conf: 85, reason: 280 });
  const [reviewedWidths, setReviewedWidths] = useState({ tradeId: 110, type: 130, amount: 110, status: 120, notes: 340 });
  const [passedWidths, setPassedWidths] = useState({ tradeId: 110, asset: 130, value: 120, confidence: 120, status: 140 });

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
    if (Array.isArray(policies)) items = policies;
    else if (typeof policies === "string" && policies.startsWith("[")) {
      items = policies.replace(/[\[\]']/g, "").split(",").map((p) => p.trim()).filter(Boolean);
    } else if (typeof policies === "string" && policies.trim().length > 0) {
      items = policies.split(",");
    }
    if (items.length === 0) return <span className="text-[10px] text-slate-500">No policies attached.</span>;
    return items.map((p, i) => (
      <span key={i} className="px-1.5 py-0.5 bg-slate-950 text-[10px] rounded border border-slate-800 text-purple-300 font-mono max-w-[140px] truncate">
        {String(p)}
      </span>
    ));
  };

  return (
    <div className="p-2 h-screen bg-slate-950 text-slate-100 flex flex-col gap-2 overflow-hidden select-none">
      {/* Top Header Metrics Row */}
      <div className="flex items-center justify-between border-b border-slate-900 pb-1 shrink-0">
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
      <div className="flex-1 grid grid-rows-[40fr_60fr] gap-2 min-h-0">
        
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
                <div className="flex-1 overflow-auto border border-slate-800/30 rounded min-h-0">
                  {workflow.urgentCases.length === 0 ? <p className="text-xs text-slate-500 p-2 italic">No urgent cases outstanding.</p> : (
                    <table className="text-left text-xs border-collapse table-fixed w-max min-w-full">
                      <thead className="sticky top-0 bg-slate-900 text-slate-400 font-bold uppercase text-[9px] border-b border-slate-800 z-10">
                        <tr>
                          <th style={{ width: urgentWidths.tradeId }} className="p-1 relative group">Trade ID<div onMouseDown={(e) => handleMouseDown("urgent", "tradeId", e)} className="absolute right-0 top-0 bottom-0 w-1 cursor-col-resize group-hover:bg-purple-500/30" /></th>
                          <th style={{ width: urgentWidths.risk }} className="p-1 text-right relative group">Risk Score<div onMouseDown={(e) => handleMouseDown("urgent", "risk", e)} className="absolute right-0 top-0 bottom-0 w-1 cursor-col-resize group-hover:bg-purple-500/30" /></th>
                          <th style={{ width: urgentWidths.conf }} className="p-1 text-right relative group">Confidence<div onMouseDown={(e) => handleMouseDown("urgent", "conf", e)} className="absolute right-0 top-0 bottom-0 w-1 cursor-col-resize group-hover:bg-purple-500/30" /></th>
                          <th style={{ width: urgentWidths.reason }} className="p-1 pl-2">Flag Reasons</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-800/30">
                        {workflow.urgentCases.map((c) => (
                          <tr key={c.trade_id} onClick={() => workflow.selectCase(c)} className={`cursor-pointer text-[11px] ${workflow.selectedCase?.trade_id === c.trade_id ? "bg-rose-950/40 font-semibold border-l-2 border-rose-500 text-rose-200" : "hover:bg-slate-800/20 text-slate-300"}`}>
                            <td className="p-1 font-mono truncate">{c.trade_id}</td>
                            {/* <td className="p-1 text-right font-mono text-rose-400">{(1 - (Number(c.compliance_probability) || 1)).toFixed(2)}</td> */}
                            <td className="p-1 text-right font-mono text-rose-400">{(Number(c.risk_score))}</td>
                            <td className="p-1 text-right font-mono text-sky-400">{(Number(c.confidence_score) || 0).toFixed(2)}</td>
                            <td className="p-1 pl-2 truncate text-[10px]">{c.flag_reason}</td>
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
                <div className="flex-1 overflow-auto border border-slate-800/30 rounded min-h-0">
                  {workflow.queuedCases.length === 0 ? <p className="text-xs text-slate-500 p-1 italic">Review queue empty.</p> : (
                    <table className="text-left text-xs border-collapse table-fixed w-max min-w-full">
                      <thead className="sticky top-0 bg-slate-900 text-slate-400 font-bold uppercase text-[9px] border-b border-slate-800 z-10">
                        <tr>
                          <th style={{ width: queuedWidths.tradeId }} className="p-1 relative group">Trade ID<div onMouseDown={(e) => handleMouseDown("queued", "tradeId", e)} className="absolute right-0 top-0 bottom-0 w-1 cursor-col-resize group-hover:bg-purple-500/30" /></th>
                          <th style={{ width: queuedWidths.priority }} className="p-1 text-right">Priority</th>
                          <th style={{ width: queuedWidths.risk }} className="p-1 text-right">Risk Score</th>
                          <th style={{ width: queuedWidths.conf }} className="p-1 text-right">Confidence</th>
                          <th style={{ width: queuedWidths.reason }} className="p-1 pl-2">Flag Reasons</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-800/30">
                        {workflow.queuedCases.map((c) => (
                          <tr key={c.trade_id} onClick={() => workflow.selectCase(c)} className={`cursor-pointer text-[11px] ${workflow.selectedCase?.trade_id === c.trade_id ? "bg-purple-950/40 font-semibold border-l-2 border-purple-500 text-purple-200" : "hover:bg-slate-800/20 text-slate-300"}`}>
                            <td className="p-1 font-mono truncate">{c.trade_id}</td>
                            <td className="p-1 text-right font-mono font-bold text-amber-400">{c.priority_score ?? "0"}</td>
                            <td className="p-1 text-right font-mono text-rose-400">{(Number(c.risk_score))}</td>
                            <td className="p-1 text-right font-mono text-sky-400">{(Number(c.confidence_score) || 0).toFixed(2)}</td>
                            <td className="p-1 pl-2 truncate text-[10px]">{c.flag_reason}</td>
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
              <div className="flex-1 overflow-auto border border-slate-800/30 rounded min-h-0">
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
                          <tr key={c.trade_id} onClick={() => workflow.selectCase(c)} className={`cursor-pointer text-[11px] ${workflow.selectedCase?.trade_id === c.trade_id ? "bg-emerald-950/40 font-semibold border-l-2 border-emerald-500 text-emerald-200" : "hover:bg-slate-800/20 text-slate-300"}`}>
                            <td className="p-1 font-mono truncate">{c.trade_id}</td>
                            <td className="p-1 truncate">{c.investment_type || "N/A"}</td>
                            <td className="p-1 text-right font-mono text-emerald-400">${Number(c.investment_amount || 0).toLocaleString()}</td>
                            <td className="p-1 text-center">
                              <span className={`px-2 py-0.5 rounded text-[9px] font-bold ${s?.userAction === "Approved" ? "bg-emerald-950 text-emerald-400" : "bg-rose-950 text-rose-400"}`}>{s?.userAction || "Processed"}</span>
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
              <div className="flex-1 overflow-auto border border-slate-800/30 rounded min-h-0">
                {workflow.passedCasesList.length === 0 ? <p className="text-slate-500 text-xs p-3 italic text-center">No auto-passed logs found.</p> : (
                  <table className="text-left text-xs border-collapse table-fixed w-max min-w-full">
                    <thead className="sticky top-0 bg-slate-900 text-slate-400 font-bold uppercase text-[9px] border-b border-slate-800 z-10">
                      <tr>
                        <th style={{ width: passedWidths.tradeId }} className="p-1 relative group">Trade ID<div onMouseDown={(e) => handleMouseDown("passed", "tradeId", e)} className="absolute right-0 top-0 bottom-0 w-1 cursor-col-resize group-hover:bg-purple-500/30" /></th>
                        <th style={{ width: passedWidths.asset }} className="p-1">Investment Type</th>
                        <th style={{ width: passedWidths.value }} className="p-1 text-right">Risk Score</th>
                        <th style={{ width: passedWidths.confidence }} className="p-1 text-right">Confidence</th>
                        <th style={{ width: passedWidths.status }} className="p-1 text-center">Flag type</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-800/30">
                      {workflow.passedCasesList.map((c) => (
                        <tr key={c.trade_id} onClick={() => workflow.selectCase(c)} className={`cursor-pointer text-[11px] ${workflow.selectedCase?.trade_id === c.trade_id ? "bg-indigo-950/40 font-semibold border-l-2 border-indigo-500 text-indigo-200" : "hover:bg-slate-800/20 text-slate-300"}`}>
                          <td className="p-1 font-mono truncate">{c.trade_id}</td>
                          <td className="p-1 truncate">{c.investment_type || "N/A"}</td>
                          <td className="p-1 text-right font-mono text-rose-400 truncate">{Number(c.risk_score).toLocaleString()}</td>
                          <td className="p-1 text-right font-mono text-sky-400">{(Number(c.confidence_score) || 1).toFixed(2)}</td>
                          <td className="p-1 text-center"><span className="text-[9px] font-bold bg-emerald-950/30 text-emerald-400 px-2 py-0.5 rounded border border-emerald-900/20">{String(c.escalation_level)}</span></td>
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
        <div className="bg-slate-900 border border-slate-800 rounded-md p-3 flex flex-col min-h-0 justify-between shadow-2xl">
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

// /* VERSION 14 */

// import React, { useState, useRef, useEffect } from "react";
// import { useTriageWorkflow } from "../hooks/useTriageWorkflow";
// import { CheckCircle, Clock, ShieldAlert, FileText, User, Briefcase, HelpCircle, Check, X, CornerUpRight } from "lucide-react";

// function Dashboard() {
//   const workflow = useTriageWorkflow();
//   const [currentNotes, setCurrentNotes] = useState<string>("");

//   useEffect(() => {
//     if (workflow.selectedCase?.trade_id) {
//       const savedState = workflow.caseStates[workflow.selectedCase.trade_id];
//       setCurrentNotes(savedState ? savedState.notes : "");
//     } else {
//       setCurrentNotes("");
//     }
//   }, [workflow.selectedCase, workflow.caseStates]);

//   const handleNotesChange = (text: string) => {
//     setCurrentNotes(text);
//     if (workflow.selectedCase?.trade_id) {
//       workflow.updateNotes(workflow.selectedCase.trade_id, text);
//     }
//   };

//   // --- Flexible Spreadsheet Column Resize States (4 Distinct Data Frameworks) ---
//   const [urgentWidths, setUrgentWidths] = useState({ tradeId: 100, risk: 85, conf: 85, reason: 320 });
//   const [queuedWidths, setQueuedWidths] = useState({ tradeId: 100, priority: 75, risk: 85, conf: 85, reason: 280 });
//   const [reviewedWidths, setReviewedWidths] = useState({ tradeId: 110, type: 130, amount: 110, status: 120, notes: 340 });
//   const [passedWidths, setPassedWidths] = useState({ tradeId: 110, asset: 130, value: 120, confidence: 120, status: 140 });

//   const dragInfo = useRef<{ table: 'urgent' | 'queued' | 'reviewed' | 'passed'; col: string; startX: number; startWidth: number } | null>(null);

//   const handleMouseDown = (table: 'urgent' | 'queued' | 'reviewed' | 'passed', col: string, e: React.MouseEvent) => {
//     e.preventDefault();
//     let currentWidths: any;
//     if (table === 'urgent') currentWidths = urgentWidths;
//     else if (table === 'queued') currentWidths = queuedWidths;
//     else if (table === 'reviewed') currentWidths = reviewedWidths;
//     else currentWidths = passedWidths;

//     dragInfo.current = { table, col, startX: e.clientX, startWidth: currentWidths[col] };
//     document.addEventListener("mousemove", handleMouseMove);
//     document.addEventListener("mouseup", handleMouseUp);
//   };

//   const handleMouseMove = (e: MouseEvent) => {
//     if (!dragInfo.current) return;
//     const { table, col, startX, startWidth } = dragInfo.current;
//     const deltaX = e.clientX - startX;
//     const newWidth = Math.max(60, startWidth + deltaX);

//     if (table === 'urgent') setUrgentWidths(prev => ({ ...prev, [col]: newWidth }));
//     else if (table === 'queued') setQueuedWidths(prev => ({ ...prev, [col]: newWidth }));
//     else if (table === 'reviewed') setReviewedWidths(prev => ({ ...prev, [col]: newWidth }));
//     else setPassedWidths(prev => ({ ...prev, [col]: newWidth }));
//   };

//   const handleMouseUp = () => {
//     dragInfo.current = null;
//     document.removeEventListener("mousemove", handleMouseMove);
//     document.removeEventListener("mouseup", handleMouseUp);
//   };

//   const handleDoubleClick = (table: 'urgent' | 'queued' | 'reviewed' | 'passed') => {
//     if (table === 'urgent') setUrgentWidths({ tradeId: 100, risk: 85, conf: 85, reason: 320 });
//     else if (table === 'queued') setQueuedWidths({ tradeId: 100, priority: 75, risk: 85, conf: 85, reason: 280 });
//     else if (table === 'reviewed') setReviewedWidths({ tradeId: 110, type: 130, amount: 110, status: 120, notes: 340 });
//     else setPassedWidths({ tradeId: 110, asset: 130, value: 120, confidence: 120, status: 140 });
//   };

//   const renderPolicies = (policies: any) => {
//     if (!policies) return <span className="text-[10px] text-slate-500">No policies attached.</span>;
//     let items: string[] = [];
//     if (Array.isArray(policies)) {
//       items = policies;
//     } else if (typeof policies === "string" && policies.startsWith("[")) {
//       items = policies.replace(/[\[\]']/g, "").split(",").map((p) => p.trim()).filter(Boolean);
//     } else if (typeof policies === "string" && policies.trim().length > 0) {
//       items = policies.split(",");
//     }
//     if (items.length === 0) return <span className="text-[10px] text-slate-500">No policies attached.</span>;
//     return items.map((p, i) => (
//       <span key={i} className="px-1.5 py-0.5 bg-slate-950 text-[10px] rounded border border-slate-800 text-purple-300 font-mono max-w-[140px] truncate">
//         {String(p)}
//       </span>
//     ));
//   };

//   return (
//     <div className="p-2 h-screen bg-slate-950 text-slate-100 flex flex-col gap-2 overflow-hidden select-none">
      
//       {/* Top Header Metrics Row */}
//       <div className="flex items-center justify-between border-b border-slate-900 pb-2 shrink-0">
//         <div className="flex items-center gap-6">
//           <h1 className="text-base font-bold tracking-tight text-slate-200">AI Compliance Review Copilot</h1>
          
//           <div className="flex bg-slate-900 p-0.5 rounded border border-slate-800 gap-0.5">
//             <button onClick={() => workflow.setView("active")} className={`px-4 py-1 text-xs font-semibold rounded transition-all ${workflow.activeView === 'active' ? 'bg-indigo-600 text-white shadow' : 'text-slate-400 hover:text-slate-200'}`}>
//               Active ({workflow.urgentCases.length + workflow.queuedCases.length})
//             </button>
//             <button onClick={() => workflow.setView("reviewed")} className={`px-4 py-1 text-xs font-semibold rounded transition-all ${workflow.activeView === 'reviewed' ? 'bg-indigo-600 text-white shadow' : 'text-slate-400 hover:text-slate-200'}`}>
//               Reviewed ({workflow.reviewedCasesList.length})
//             </button>
//             <button onClick={() => workflow.setView("passed")} className={`px-4 py-1 text-xs font-semibold rounded transition-all ${workflow.activeView === 'passed' ? 'bg-indigo-600 text-white shadow' : 'text-slate-400 hover:text-slate-200'}`}>
//               Passed ({workflow.passedCasesList.length})
//             </button>
//           </div>
//         </div>
        
//         {/* Top Right Master Counters Row */}
//         <div className="flex items-center gap-2">
//           <div className="bg-rose-950/20 border border-rose-500/20 rounded px-2.5 py-1 flex items-center gap-1.5 text-xs font-medium">
//             <span className="text-rose-400">Urgent:</span>
//             <span className="font-bold text-rose-200">{workflow.urgentCases.length}</span>
//           </div>
//           <div className="bg-amber-950/20 border border-amber-500/20 rounded px-2.5 py-1 flex items-center gap-1.5 text-xs font-medium">
//             <span className="text-amber-400">Review:</span>
//             <span className="font-bold text-amber-200">{workflow.queuedCases.length}</span>
//           </div>
//           <div className="bg-emerald-950/20 border border-emerald-500/20 rounded px-2.5 py-1 flex items-center gap-1.5 text-xs font-medium">
//             <span className="text-emerald-400">Reviewed Today:</span>
//             <span className="font-bold text-emerald-200">{workflow.reviewedTodayCount}</span>
//           </div>
//           <div className="bg-indigo-950/20 border border-indigo-500/20 rounded px-2.5 py-1 flex items-center gap-1.5 text-xs font-medium">
//             <span className="text-indigo-400">Passed:</span>
//             <span className="font-bold text-indigo-200">{workflow.passedCasesList.length}</span>
//           </div>
//         </div>
//       </div>

//       {/* Primary Split Workspace: Upper View 40% / Lower Workspace 60% */}
//       <div className="flex-1 grid grid-rows-[40fr_60fr] gap-2 min-h-0">
        
//         {/* UPPER VIEW SEGMENT */}
//         <div className="min-h-0">
//           {workflow.activeView === "active" && (
//             <div className="grid grid-cols-2 gap-2 h-full min-h-0">
              
//               {/* Table 1: Urgent Table */}
//               <div className="bg-slate-900 border border-slate-800 rounded-md p-1.5 flex flex-col min-h-0">
//                 <div className="flex items-center gap-1 border-b border-slate-800 pb-0.5 mb-1 shrink-0">
//                   <ShieldAlert className="w-3.5 h-3.5 text-rose-400" />
//                   <h2 className="text-[10px] font-bold text-rose-400 uppercase tracking-wider">Urgent Action Required</h2>
//                 </div>
//                 <div className="flex-1 overflow-x-auto overflow-y-auto border border-slate-800/30 rounded dynamic-scroll min-h-0">
//                   {workflow.urgentCases.length === 0 ? <p className="text-xs text-slate-500 p-2 italic">No urgent cases outstanding.</p> : (
//                     <table className="text-left text-xs border-collapse table-fixed w-max min-w-full">
//                       <thead className="sticky top-0 bg-slate-900 text-slate-400 font-bold uppercase text-[9px] border-b border-slate-800 z-10">
//                         <tr>
//                           <th style={{ width: urgentWidths.tradeId }} className="p-1 relative group">Trade ID
//                             <div onMouseDown={(e) => handleMouseDown('urgent', 'tradeId', e)} onDoubleClick={() => handleDoubleClick('urgent')} className="absolute right-0 top-0 bottom-0 w-1 bg-purple-500/0 group-hover:bg-purple-500/30 cursor-col-resize" />
//                           </th>
//                           <th style={{ width: urgentWidths.risk }} className="p-1 text-right relative group">Risk Score
//                             <div onMouseDown={(e) => handleMouseDown('urgent', 'risk', e)} onDoubleClick={() => handleDoubleClick('urgent')} className="absolute right-0 top-0 bottom-0 w-1 bg-purple-500/0 group-hover:bg-purple-500/30 cursor-col-resize" />
//                           </th>
//                           <th style={{ width: urgentWidths.conf }} className="p-1 text-right relative group">Conf.
//                             <div onMouseDown={(e) => handleMouseDown('urgent', 'conf', e)} onDoubleClick={() => handleDoubleClick('urgent')} className="absolute right-0 top-0 bottom-0 w-1 bg-purple-500/0 group-hover:bg-purple-500/30 cursor-col-resize" />
//                           </th>
//                           <th style={{ width: urgentWidths.reason }} className="p-1 pl-2 relative group">Flag Reason</th>
//                         </tr>
//                       </thead>
//                       <tbody className="divide-y divide-slate-800/30">
//                         {workflow.urgentCases.map((c, i) => {
//                           const isSelected = workflow.selectedCase?.trade_id === c?.trade_id;
//                           return (
//                             <tr key={`${c.trade_id}-${i}`} onClick={() => workflow.selectCase(c)} className={`cursor-pointer text-[11px] ${isSelected ? 'bg-rose-950/40 font-semibold border-l-2 border-rose-500 text-rose-200' : 'hover:bg-slate-800/20 text-slate-300'}`}>
//                               <td className="p-1 font-mono truncate">{c.trade_id}</td>
//                               <td className="p-1 text-right font-mono text-rose-400">{(1 - (Number(c.compliance_probability) || 1)).toFixed(2)}</td>
//                               <td className="p-1 text-right font-mono text-slate-400">{(Number(c.confidence_score) || 0).toFixed(2)}</td>
//                               <td className="p-1 pl-2 truncate text-[10px]">{c.flag_reason}</td>
//                             </tr>
//                           );
//                         })}
//                       </tbody>
//                     </table>
//                   )}
//                 </div>
//               </div>

//               {/* Table 2: Review Table */}
//               <div className="bg-slate-900 border border-slate-800 rounded-md p-1.5 flex flex-col min-h-0">
//                 <div className="flex items-center gap-1 border-b border-slate-800 pb-0.5 mb-1 shrink-0">
//                   <Clock className="w-3.5 h-3.5 text-amber-400" />
//                   <h2 className="text-[10px] font-bold text-amber-400 uppercase tracking-wider">Review</h2>
//                 </div>
//                 <div className="flex-1 overflow-x-auto overflow-y-auto border border-slate-800/30 rounded dynamic-scroll min-h-0">
//                   {workflow.queuedCases.length === 0 ? <p className="text-xs text-slate-500 p-1 italic">Review queue empty.</p> : (
//                     <table className="text-left text-xs border-collapse table-fixed w-max min-w-full">
//                       <thead className="sticky top-0 bg-slate-900 text-slate-400 font-bold uppercase text-[9px] border-b border-slate-800 z-10">
//                         <tr>
//                           <th style={{ width: queuedWidths.tradeId }} className="p-1 relative group">Trade ID
//                             <div onMouseDown={(e) => handleMouseDown('queued', 'tradeId', e)} onDoubleClick={() => handleDoubleClick('queued')} className="absolute right-0 top-0 bottom-0 w-1 bg-purple-500/0 group-hover:bg-purple-500/30 cursor-col-resize" />
//                           </th>
//                           <th style={{ width: queuedWidths.priority }} className="p-1 text-right relative group text-amber-400">Priority</th>
//                           <th style={{ width: queuedWidths.risk }} className="p-1 text-right relative group">Risk Score</th>
//                           <th style={{ width: queuedWidths.conf }} className="p-1 text-right relative group">Conf.</th>
//                           <th style={{ width: queuedWidths.reason }} className="p-1 pl-2 relative group">Flag Reason</th>
//                         </tr>
//                       </thead>
//                       <tbody className="divide-y divide-slate-800/30">
//                         {workflow.queuedCases.map((c, i) => {
//                           const isSelected = workflow.selectedCase?.trade_id === c?.trade_id;
//                           return (
//                             <tr key={`${c.trade_id}-${i}`} onClick={() => workflow.selectCase(c)} className={`cursor-pointer text-[11px] ${isSelected ? 'bg-purple-950/40 font-semibold border-l-2 border-purple-500 text-purple-200' : 'hover:bg-slate-800/20 text-slate-300'}`}>
//                               <td className="p-1 font-mono truncate">{c.trade_id}</td>
//                               <td className="p-1 text-right font-mono font-bold text-amber-400">{c.priority_score ?? "0"}</td>
//                               <td className="p-1 text-right font-mono text-rose-400">{(1 - (Number(c.compliance_probability) || 1)).toFixed(2)}</td>
//                               <td className="p-1 text-right font-mono text-slate-400">{(Number(c.confidence_score) || 0).toFixed(2)}</td>
//                               <td className="p-1 pl-2 truncate text-[10px]">{c.flag_reason}</td>
//                             </tr>
//                           );
//                         })}
//                       </tbody>
//                     </table>
//                   )}
//                 </div>
//               </div>

//             </div>
//           )}

//           {/* Table 3: Scrollable Resizable Reviewed View Panel */}
//           {workflow.activeView === "reviewed" && (
//             <div className="bg-slate-900 border border-slate-800 rounded-md p-1.5 flex flex-col h-full min-h-0">
//               <div className="flex items-center gap-1 border-b border-slate-800 pb-0.5 mb-1 shrink-0">
//                 <CheckCircle className="w-3.5 h-3.5 text-emerald-400" />
//                 <h2 className="text-[10px] font-bold text-emerald-400 uppercase tracking-wider">User Reviewed Logs</h2>
//               </div>
//               <div className="flex-1 overflow-x-auto overflow-y-auto border border-slate-800/30 rounded dynamic-scroll min-h-0">
//                 {workflow.reviewedCasesList.length === 0 ? <p className="text-slate-500 text-xs p-3 italic text-center">No logs audited yet.</p> : (
//                   <table className="text-left text-xs border-collapse table-fixed w-max min-w-full">
//                     <thead className="sticky top-0 bg-slate-900 text-slate-400 font-bold uppercase text-[9px] border-b border-slate-800 z-10">
//                       <tr>
//                         <th style={{ width: reviewedWidths.tradeId }} className="p-1 relative group">Trade ID
//                           <div onMouseDown={(e) => handleMouseDown('reviewed', 'tradeId', e)} onDoubleClick={() => handleDoubleClick('reviewed')} className="absolute right-0 top-0 bottom-0 w-1 bg-purple-500/0 group-hover:bg-purple-500/30 cursor-col-resize" />
//                         </th>
//                         <th style={{ width: reviewedWidths.type }} className="p-1 relative group">Investment Type
//                           <div onMouseDown={(e) => handleMouseDown('reviewed', 'type', e)} onDoubleClick={() => handleDoubleClick('reviewed')} className="absolute right-0 top-0 bottom-0 w-1 bg-purple-500/0 group-hover:bg-purple-500/30 cursor-col-resize" />
//                         </th>
//                         <th style={{ width: reviewedWidths.amount }} className="p-1 text-right relative group">Amount
//                           <div onMouseDown={(e) => handleMouseDown('reviewed', 'amount', e)} onDoubleClick={() => handleDoubleClick('reviewed')} className="absolute right-0 top-0 bottom-0 w-1 bg-purple-500/0 group-hover:bg-purple-500/30 cursor-col-resize" />
//                         </th>
//                         <th style={{ width: reviewedWidths.status }} className="p-1 text-center relative group">Outcome
//                           <div onMouseDown={(e) => handleMouseDown('reviewed', 'status', e)} onDoubleClick={() => handleDoubleClick('reviewed')} className="absolute right-0 top-0 bottom-0 w-1 bg-purple-500/0 group-hover:bg-purple-500/30 cursor-col-resize" />
//                         </th>
//                         <th style={{ width: reviewedWidths.notes }} className="p-1 pl-3 relative group">Auditor Justification Notes</th>
//                       </tr>
//                     </thead>
//                     <tbody className="divide-y divide-slate-800/30">
//                       {workflow.reviewedCasesList.map((c, i) => {
//                         const s = workflow.caseStates[c.trade_id];
//                         const isSelected = workflow.selectedCase?.trade_id === c?.trade_id;
//                         return (
//                           <tr key={`${c.trade_id}-${i}`} onClick={() => workflow.selectCase(c)} className={`cursor-pointer text-[11px] ${isSelected ? 'bg-emerald-950/40 font-semibold border-l-2 border-emerald-500 text-emerald-200' : 'hover:bg-slate-800/20 text-slate-300'}`}>
//                             <td className="p-1 font-mono truncate">{c.trade_id}</td>
//                             <td className="p-1 truncate">{c.investment_type || "N/A"}</td>
//                             <td className="p-1 text-right font-mono text-emerald-400 truncate">${Number(c.investment_amount || 0).toLocaleString()}</td>
//                             <td className="p-1 text-center truncate">
//                               <span className={`px-2 py-0.5 rounded text-[9px] font-bold ${s?.userAction === 'Approved' ? 'bg-emerald-950 text-emerald-400 border border-emerald-900/30' : s?.userAction === 'Rejected' ? 'bg-rose-950 text-rose-400 border border-rose-900/30' : 'bg-amber-950 text-amber-400 border border-amber-900/30'}`}>
//                                 {s?.userAction || 'Processed'}
//                               </span>
//                             </td>
//                             <td className="p-1 pl-3 italic text-slate-400 truncate">{s?.notes || "—"}</td>
//                           </tr>
//                         );
//                       })}
//                     </tbody>
//                   </table>
//                 )}
//               </div>
//             </div>
//           )}

//           {/* Table 4: Scrollable Resizable Passed View Panel */}
//           {workflow.activeView === "passed" && (
//             <div className="bg-slate-900 border border-slate-800 rounded-md p-1.5 flex flex-col h-full min-h-0">
//               <div className="flex items-center gap-1 border-b border-slate-800 pb-0.5 mb-1 shrink-0">
//                 <CheckCircle className="w-3.5 h-3.5 text-indigo-400" />
//                 <h2 className="text-[10px] font-bold text-indigo-400 uppercase tracking-wider">System Automatic Clearance Log</h2>
//               </div>
//               <div className="flex-1 overflow-x-auto overflow-y-auto border border-slate-800/30 rounded dynamic-scroll min-h-0">
//                 {workflow.passedCasesList.length === 0 ? <p className="text-slate-500 text-xs p-3 italic text-center">No auto-passed logs found.</p> : (
//                   <table className="text-left text-xs border-collapse table-fixed w-max min-w-full">
//                     <thead className="sticky top-0 bg-slate-900 text-slate-400 font-bold uppercase text-[9px] border-b border-slate-800 z-10">
//                       <tr>
//                         <th style={{ width: passedWidths.tradeId }} className="p-1 relative group">Trade ID
//                           <div onMouseDown={(e) => handleMouseDown('passed', 'tradeId', e)} onDoubleClick={() => handleDoubleClick('passed')} className="absolute right-0 top-0 bottom-0 w-1 bg-purple-500/0 group-hover:bg-purple-500/30 cursor-col-resize" />
//                         </th>
//                         <th style={{ width: passedWidths.asset }} className="p-1 relative group">Asset Class
//                           <div onMouseDown={(e) => handleMouseDown('passed', 'asset', e)} onDoubleClick={() => handleDoubleClick('passed')} className="absolute right-0 top-0 bottom-0 w-1 bg-purple-500/0 group-hover:bg-purple-500/30 cursor-col-resize" />
//                         </th>
//                         <th style={{ width: passedWidths.value }} className="p-1 text-right relative group">Notional Value
//                           <div onMouseDown={(e) => handleMouseDown('passed', 'value', e)} onDoubleClick={() => handleDoubleClick('passed')} className="absolute right-0 top-0 bottom-0 w-1 bg-purple-500/0 group-hover:bg-purple-500/30 cursor-col-resize" />
//                         </th>
//                         <th style={{ width: passedWidths.confidence }} className="p-1 text-right relative group">Confidence Score
//                           <div onMouseDown={(e) => handleMouseDown('passed', 'confidence', e)} onDoubleClick={() => handleDoubleClick('passed')} className="absolute right-0 top-0 bottom-0 w-1 bg-purple-500/0 group-hover:bg-purple-500/30 cursor-col-resize" />
//                         </th>
//                         <th style={{ width: passedWidths.status }} className="p-1 text-center relative group">Clearance Status</th>
//                       </tr>
//                     </thead>
//                     <tbody className="divide-y divide-slate-800/30">
//                       {workflow.passedCasesList.map((c, i) => {
//                         const isSelected = workflow.selectedCase?.trade_id === c?.trade_id;
//                         return (
//                           <tr key={`${c.trade_id}-${i}`} onClick={() => workflow.selectCase(c)} className={`cursor-pointer text-[11px] ${isSelected ? 'bg-indigo-950/40 font-semibold border-l-2 border-indigo-500 text-indigo-200' : 'hover:bg-slate-800/20 text-slate-300'}`}>
//                             <td className="p-1 font-mono truncate">{c.trade_id}</td>
//                             <td className="p-1 truncate">{c.investment_type || "N/A"}</td>
//                             <td className="p-1 text-right font-mono truncate">${Number(c.notional_value || 0).toLocaleString()}</td>
//                             <td className="p-1 text-right font-mono text-sky-400 truncate">{(Number(c.confidence_score) || 1).toFixed(4)}</td>
//                             <td className="p-1 text-center truncate">
//                               <span className="text-[9px] font-bold bg-emerald-950/30 text-emerald-400 px-2 py-0.5 rounded border border-emerald-900/20">Passed Engine</span>
//                             </td>
//                           </tr>
//                         );
//                       })}
//                     </tbody>
//                   </table>
//                 )}
//               </div>
//             </div>
//           )}
//         </div>

//         {/* LOWER WORKSPACE AREA (Expansive 60% Form Layout Framework) */}
//         <div className="bg-slate-900 border border-slate-800 rounded-md p-3 flex flex-col min-h-0 justify-between shadow-2xl">
//           {workflow.selectedCase ? (() => {
//             const c = workflow.selectedCase;
//             const currentState = workflow.caseStates[c.trade_id] || { reviewStatus: "Not reviewed", notes: "" };
            
//             // Safe variable mappings protecting lowercase rendering routes
//             const parsedProb = Number(c.compliance_probability);
//             const riskVal = isNaN(parsedProb) ? 0.000 : 1 - parsedProb;
//             const isRecCompliant = String(currentState.overriddenLabel || c.compliance_label || "").toLowerCase() === "compliant";
//             const isAutoPassed = workflow.activeView === "passed";

//             // Clean number extractions out of dirty CSV string profiles
//             const rawAmount = Number(String(c.investment_amount || "").replace(/[^0-9.-]/g, ""));
//             const displayAmount = isNaN(rawAmount) ? "0" : rawAmount.toLocaleString();

//             const rawNotional = Number(String(c.notional_value || "").replace(/[^0-9.-]/g, ""));
//             const displayNotional = isNaN(rawNotional) ? "0" : rawNotional.toLocaleString();

//             const rawIncome = Number(String(c.client_income || "").replace(/[^0-9.-]/g, ""));
//             const displayIncome = isNaN(rawIncome) || rawIncome === 0 ? "—" : `${Math.round(rawIncome / 1000)}k`;

//             return (
//               <div className="flex flex-col h-full justify-between min-h-0 space-y-3">
                
//                 {/* Workspace Module header block */}
//                 <div className="flex items-center justify-between border-b border-slate-800 pb-2 shrink-0">
//                   <div className="flex items-center gap-2">
//                     <span className="text-[9px] font-black uppercase bg-purple-950/40 px-2 py-0.5 rounded border border-purple-900/50 text-purple-400 tracking-wider">Selected Case Audit Space</span>
//                     <span className="text-xs font-mono font-bold text-slate-100 bg-slate-950 px-2 py-0.5 rounded border border-slate-800">{c.trade_id}</span>
//                   </div>

//                   {/* Restored Score metrics block badge back to the top-right position */}
//                   <div className="flex items-center gap-2 bg-slate-950/60 px-2.5 py-1 rounded-md border border-slate-800/80 text-[10px] font-mono">
//                     <div className="flex items-center gap-1.5 border-r border-slate-800 pr-2">
//                       <span className="text-slate-500 font-sans text-[9px] font-bold uppercase">AI Rec:</span>
//                       <span className={`px-1 rounded text-[9px] font-black ${isRecCompliant ? "bg-emerald-950 text-emerald-400" : "bg-rose-950 text-rose-400"}`}>
//                         {isRecCompliant ? "COMPLIANT" : "FLAGGED"}
//                       </span>
//                     </div>
//                     <div className="flex items-center gap-1.5 border-r border-slate-800 pr-2 pl-1">
//                       <span className="text-slate-500 font-sans text-[9px] font-bold uppercase">Risk:</span>
//                       <span className="text-rose-400 font-bold">{riskVal.toFixed(3)}</span>
//                     </div>
//                     <div className="flex items-center gap-1.5 pl-1">
//                       <span className="text-slate-500 font-sans text-[9px] font-bold uppercase">Conf:</span>
//                       <span className="text-sky-400 font-bold">{Number(c.confidence_score || 0).toFixed(3)}</span>
//                     </div>
//                   </div>
//                 </div>

//                 {/* Expanded 3 Column Matrix Grid Layout (Spaced for high-density zero overlap readability) */}
//                 <div className="grid grid-cols-3 gap-3 flex-1 min-h-0 py-1">
                  
//                   {/* MODULE A: Trade Details */}
//                   <div className="bg-slate-950/30 border border-slate-800/60 p-3 rounded-lg flex flex-col justify-between">
//                     <div className="flex items-center gap-1.5 border-b border-slate-800/80 pb-1.5 mb-2 text-purple-400 text-[10px] font-black uppercase tracking-widest shrink-0">
//                       <Briefcase className="w-3.5 h-3.5"/>
//                       <span>Trade Details</span>
//                     </div>
//                     <div className="text-xs grid grid-cols-2 gap-x-3 gap-y-3 flex-1 items-center text-slate-300">
//                       <div><span className="text-slate-500 text-[9px] uppercase font-bold tracking-wider block mb-0.5">Type</span><div className="truncate font-semibold text-slate-200">{c.investment_type || "N/A"}</div></div>
//                       <div><span className="text-slate-500 text-[9px] uppercase font-bold tracking-wider block mb-0.5">Amount</span><div className="truncate font-mono font-black text-emerald-400">${displayAmount}</div></div>
//                       <div><span className="text-slate-500 text-[9px] uppercase font-bold tracking-wider block mb-0.5">Notional</span><div className="truncate font-mono font-medium text-slate-400">${displayNotional}</div></div>
//                       <div><span className="text-slate-500 text-[9px] uppercase font-bold tracking-wider block mb-0.5">Timestamp</span><div className="truncate font-mono text-[10px] text-slate-400">{c.timestamp || "—"}</div></div>
//                     </div>
//                   </div>

//                   {/* MODULE B: Client Profile */}
//                   <div className="bg-slate-950/30 border border-slate-800/60 p-3 rounded-lg flex flex-col justify-between">
//                     <div className="flex items-center gap-1.5 border-b border-slate-800/80 pb-1.5 mb-2 text-sky-400 text-[10px] font-black uppercase tracking-widest shrink-0">
//                       <User className="w-3.5 h-3.5"/>
//                       <span>Client Profile</span>
//                     </div>
//                     <div className="text-xs grid grid-cols-2 gap-x-3 gap-y-3 flex-1 items-center text-slate-300">
//                       <div><span className="text-slate-500 text-[9px] uppercase font-bold tracking-wider block mb-0.5">Age / Income</span><div className="truncate font-mono font-semibold text-slate-200">{c.client_age ?? "—"} / ${displayIncome}</div></div>
//                       <div><span className="text-slate-500 text-[9px] uppercase font-bold tracking-wider block mb-0.5">Risk Profile</span><div className="truncate font-black text-amber-400">{c.risk_tolerance || "—"}</div></div>
//                       <div><span className="text-slate-500 text-[9px] uppercase font-bold tracking-wider block mb-0.5">Experience</span><div className="truncate text-slate-400">{c.investment_experience || "—"}</div></div>
//                       <div><span className="text-slate-500 text-[9px] uppercase font-bold tracking-wider block mb-0.5">Objective & Horizon</span><div className="truncate text-slate-400 font-medium">{c.investment_objective || "—"} {c?.investment_time_horizon ? `(${c.investment_time_horizon})` : ""}</div></div>
//                     </div>
//                   </div>

//                   {/* MODULE C: Advisor Info */}
//                   <div className="bg-slate-950/30 border border-slate-800/60 p-3 rounded-lg flex flex-col justify-between">
//                     <div className="flex items-center gap-1.5 border-b border-slate-800/80 pb-1.5 mb-2 text-amber-400 text-[10px] font-black uppercase tracking-widest shrink-0">
//                       <FileText className="w-3.5 h-3.5"/>
//                       <span>Advisor Info</span>
//                     </div>
//                     <div className="text-xs grid grid-cols-2 gap-x-3 gap-y-3 flex-1 items-center text-slate-300">
//                       <div><span className="text-slate-500 text-[9px] uppercase font-bold tracking-wider block mb-0.5">Advisor ID</span><div className="truncate font-mono font-semibold text-slate-200">{c.advisor_id || "—"}</div></div>
//                       <div><span className="text-slate-500 text-[9px] uppercase font-bold tracking-wider block mb-0.5">Exp / Risk History</span><div className="truncate text-slate-400">{c.advisor_experience || "—"} / <span className="text-rose-400 font-mono font-bold">{c.advisor_history_risk ?? 0}</span></div></div>
//                       <div><span className="text-slate-500 text-[9px] uppercase font-bold tracking-wider block mb-0.5">Rationale File</span><div className={`px-2 py-0.5 text-[9px] font-black rounded-md w-fit tracking-wider ${c.has_rationale ? "bg-emerald-950 text-emerald-400 border border-emerald-900/30" : "bg-slate-900 text-slate-500"}`}>{c.has_rationale ? "FILED" : "MISSING"}</div></div>
//                       <div><span className="text-slate-500 text-[9px] uppercase font-bold tracking-wider block mb-0.5">Desk Context</span><div className="truncate text-slate-400 text-[11px] italic font-serif leading-tight">{c.advisor_notes || "None"}</div></div>
//                     </div>
//                   </div>
//                 </div>

//                 {/* Policy Compliance Framework Bar Row */}
//                 <div className="border-t border-slate-800/80 pt-2 shrink-0 items-center bg-slate-950/40 p-2 rounded-lg text-xs flex justify-between gap-4">
//                   <div className="flex items-center gap-2 truncate max-w-xl">
//                     <HelpCircle className={`w-4 h-4 shrink-0 ${isAutoPassed ? "text-emerald-400" : "text-rose-400"}`}/>
//                     <span className="text-[9px] uppercase text-slate-500 font-black tracking-wider shrink-0">Exception Rule:</span>
//                     <span className={`font-semibold truncate text-[11px] ${isAutoPassed ? "text-emerald-300" : "text-rose-300"}`}>
//                       {isAutoPassed ? "Trade met all baseline validation parameters. No active human review required." : (c.flag_reason || "None.")}
//                     </span>
//                   </div>
//                   <div className="flex items-center gap-1.5 overflow-hidden truncate">
//                     <span className="text-[9px] uppercase text-slate-600 font-black tracking-wider shrink-0">Attached Regulations:</span>
//                     <div className="flex gap-1 items-center truncate">
//                       {c.retrieved_policies && (Array.isArray(c.retrieved_policies) || typeof c.retrieved_policies === 'string') ? (
//                         renderPolicies(c.retrieved_policies)
//                       ) : (
//                         <span className="text-[10px] text-slate-600 italic tracking-wide">No regulations attached</span>
//                       )}
//                     </div>
//                   </div>
//                 </div>

//                 {/* Execution Signature Action Form Tray */}
//                 <div className="pt-1 flex gap-3 items-end shrink-0 border-t border-slate-800/40">
//                   <div className="flex-1 flex flex-col">
//                     <label className="text-[9px] font-black text-slate-400 uppercase tracking-widest mb-1">Reviewer Sign-off Justification Matrix</label>
//                     <input type="text" value={currentNotes} onChange={(e) => handleNotesChange(e.target.value)} placeholder="Type definitive legal compliance assessment or operational arguments..." className="w-full bg-slate-950 border border-slate-800 rounded px-2.5 text-xs text-slate-200 focus:outline-none focus:border-indigo-500 transition-all shadow-inner h-8" />
//                   </div>
//                   <div className="flex gap-2 h-8">
//                     <button onClick={() => workflow.executeAction(c.trade_id, "Reviewed", "Rejected", currentNotes)} className="bg-rose-600 hover:bg-rose-500 text-white font-black text-[10px] px-4 rounded flex items-center gap-1.5 uppercase tracking-wider shadow-md transition-colors"><X className="w-3.5 h-3.5"/>Reject Trade</button>
//                     <button onClick={() => workflow.executeAction(c.trade_id, "Reviewed", "Approved", currentNotes)} className="bg-emerald-600 hover:bg-emerald-500 text-slate-950 font-black text-[10px] px-4 rounded flex items-center gap-1.5 uppercase tracking-wider shadow-md transition-colors"><Check className="w-3.5 h-3.5"/>Approve Trade</button>
//                     <button onClick={() => workflow.executeAction(c.trade_id, "Escalated", "Escalated", currentNotes)} className="bg-slate-800 hover:bg-slate-700 text-amber-400 border border-slate-700 font-black text-[10px] px-4 rounded flex items-center gap-1.5 uppercase tracking-wider shadow-md transition-colors"><CornerUpRight className="w-3.5 h-3.5"/>Escalate Review</button>
//                   </div>
//                 </div>

//               </div>
//             );
//           })() : (
//             <div className="h-full flex flex-col items-center justify-center text-slate-500 text-xs font-semibold border border-dashed border-slate-800 rounded p-6 text-center bg-slate-950/20">
//               <CheckCircle className="w-10 h-10 text-emerald-500/30 mb-2" />
//               <span className="text-slate-400 font-bold uppercase tracking-wider text-[11px]">All Tasks Cleared</span>
//               <p className="text-[10px] text-slate-600 font-normal max-w-xs mt-1">Select an item from any active stream or historical tab above to evaluate details.</p>
//             </div>
//           )}
//         </div>

//       </div>
//     </div>
//   );
// }

// export default Dashboard;

// /* VERSION 13 */

// import { useEffect, useState, useRef } from "react";
// import { getCases } from "../api/cases";
// import { AlertCircle, CheckCircle, Clock, ShieldAlert, FileText, User, Briefcase, HelpCircle, ArrowUpRight, CheckSquare } from "lucide-react";

// interface CaseAuditState {
//   reviewStatus: "Reviewed" | "Not reviewed" | "Escalated";
//   notes: string;
//   overriddenLabel?: string; 
// }

// function Dashboard() {
//   const [activeView, setActiveView] = useState<"active" | "reviewed" | "passed">("active");
//   const [cases, setCases] = useState<any[]>([]);
//   const [selectedCase, setSelectedCase] = useState<any | null>(null);
//   const [caseStates, setCaseStates] = useState<Record<string, CaseAuditState>>({});
//   const [currentNotes, setCurrentNotes] = useState<string>("");

//   // Spreadsheet Column Widths
//   const [urgentWidths, setUrgentWidths] = useState({ tradeId: 90, risk: 65, conf: 65, reason: 180 });
//   const [queuedWidths, setQueuedWidths] = useState({ tradeId: 90, priority: 60, risk: 65, conf: 65, reason: 160 });
//   const [tabTablesWidths, setTabTablesWidths] = useState({ tradeId: 105, priority: 65, risk: 70, conf: 70, reason: 260 });

//   const dragInfo = useRef<{ table: 'urgent' | 'queued' | 'tabbed'; col: string; startX: number; startWidth: number } | null>(null);

//   useEffect(() => {
//     getCases()
//       .then((data) => {
//         if (Array.isArray(data)) {
//           setCases(data);
          
//           const initialStates: Record<string, CaseAuditState> = {};
//           data.forEach((c) => {
//             if (c?.trade_id) {
//               initialStates[c.trade_id] = { 
//                 reviewStatus: "Not reviewed", 
//                 notes: "",
//                 overriddenLabel: c.compliance_label || "Non-compliant"
//               };
//             }
//           });
//           setCaseStates(initialStates);

//           const urgentCases = data.filter((c) => c?.escalation_level === "urgent");
//           const queuedCases = data
//             .filter((c) => c?.escalation_level === "priority" || c?.escalation_level === "queue")
//             .sort((a, b) => (Number(b?.priority_score) || 0) - (Number(a?.priority_score) || 0));

//           if (urgentCases.length > 0) handleCaseSelection(urgentCases[0], initialStates);
//           else if (queuedCases.length > 0) handleCaseSelection(queuedCases[0], initialStates);
//         }
//       })
//       .catch((err) => console.error("API Fetch Error:", err));
//   }, []);

//   const handleCaseSelection = (targetCase: any, latestStates = caseStates) => {
//     setSelectedCase(targetCase);
//     if (targetCase?.trade_id) {
//       const savedState = latestStates[targetCase.trade_id];
//       setCurrentNotes(savedState ? savedState.notes : "");
//     } else {
//       setCurrentNotes("");
//     }
//   };

//   const handleNotesChange = (text: string) => {
//     setCurrentNotes(text);
//     if (selectedCase?.trade_id) {
//       setCaseStates(prev => ({
//         ...prev,
//         [selectedCase.trade_id]: { ...prev[selectedCase.trade_id], notes: text }
//       }));
//     }
//   };

//   // Lists Processing Groupings
//   const urgentCases = cases.filter((c) => {
//     const status = caseStates[c.trade_id]?.reviewStatus || "Not reviewed";
//     return c?.escalation_level === "urgent" && status === "Not reviewed";
//   });

//   const queuedCases = cases
//     .filter((c) => {
//       const status = caseStates[c.trade_id]?.reviewStatus || "Not reviewed";
//       return (c?.escalation_level === "priority" || c?.escalation_level === "queue") && status === "Not reviewed";
//     })
//     .sort((a, b) => (Number(b?.priority_score) || 0) - (Number(a?.priority_score) || 0));

//   const reviewedCases = cases.filter((c) => {
//     const status = caseStates[c.trade_id]?.reviewStatus;
//     return status === "Reviewed" || status === "Escalated";
//   });

//   const passedCases = cases.filter((c) => {
//     return c?.escalation_level !== "urgent" && c?.escalation_level !== "priority" && c?.escalation_level !== "queue";
//   });

//   // Smart Sequential Focus Shift Progression Engine
//   const handleDecision = (decisionType: "Approved" | "Rejected" | "Escalated") => {
//     if (!selectedCase?.trade_id) return;

//     let nextCase: any = null;

//     if (activeView === "active") {
//       const isInUrgent = urgentCases.some(c => c.trade_id === selectedCase.trade_id);
//       if (isInUrgent) {
//         const idx = urgentCases.findIndex(c => c.trade_id === selectedCase.trade_id);
//         if (urgentCases.length > 1) {
//           nextCase = idx + 1 < urgentCases.length ? urgentCases[idx + 1] : urgentCases[idx - 1];
//         } else if (queuedCases.length > 0) {
//           nextCase = queuedCases[0];
//         }
//       } else {
//         const isInQueued = queuedCases.some(c => c.trade_id === selectedCase.trade_id);
//         if (isInQueued) {
//           const idx = queuedCases.findIndex(c => c.trade_id === selectedCase.trade_id);
//           if (queuedCases.length > 1) {
//             nextCase = idx + 1 < queuedCases.length ? queuedCases[idx + 1] : queuedCases[idx - 1];
//           } else if (urgentCases.length > 0) {
//             nextCase = urgentCases[0];
//           }
//         }
//       }
//     } else if (activeView === "passed") {
//       const idx = passedCases.findIndex(c => c.trade_id === selectedCase.trade_id);
//       if (passedCases.length > 1) {
//         nextCase = idx + 1 < passedCases.length ? passedCases[idx + 1] : passedCases[idx - 1];
//       }
//     } else if (activeView === "reviewed") {
//       const idx = reviewedCases.findIndex(c => c.trade_id === selectedCase.trade_id);
//       if (reviewedCases.length > 1) {
//         nextCase = idx + 1 < reviewedCases.length ? reviewedCases[idx + 1] : reviewedCases[idx - 1];
//       }
//     }

//     const reviewStatus = decisionType === "Escalated" ? "Escalated" : "Reviewed";
//     const overriddenLabel = decisionType === "Approved" ? "Compliant" : "Non-compliant";

//     setCaseStates(prev => {
//       const updated = {
//         ...prev,
//         [selectedCase.trade_id]: {
//           ...prev[selectedCase.trade_id],
//           reviewStatus,
//           notes: currentNotes,
//           overriddenLabel
//         }
//       };

//       if (nextCase) {
//         setTimeout(() => {
//           handleCaseSelection(nextCase, updated);
//         }, 0);
//       } else {
//         if (activeView === "active" && urgentCases.length <= 1 && queuedCases.length <= 1) {
//           setTimeout(() => {
//             setSelectedCase(null);
//             setCurrentNotes("");
//           }, 0);
//         }
//       }

//       return updated;
//     });
//   };

//   // Mouse Resize Drag Handlers
//   const handleMouseDown = (table: 'urgent' | 'queued' | 'tabbed', col: string, e: React.MouseEvent) => {
//     e.preventDefault();
//     let currentWidths = urgentWidths;
//     if (table === 'queued') currentWidths = queuedWidths;
//     if (table === 'tabbed') currentWidths = tabTablesWidths as any;

//     dragInfo.current = {
//       table,
//       col,
//       startX: e.clientX,
//       startWidth: (currentWidths as any)[col]
//     };
//     document.addEventListener("mousemove", handleMouseMove);
//     document.addEventListener("mouseup", handleMouseUp);
//   };

//   const handleMouseMove = (e: MouseEvent) => {
//     if (!dragInfo.current) return;
//     const { table, col, startX, startWidth } = dragInfo.current;
//     const deltaX = e.clientX - startX;
//     const newWidth = Math.max(50, startWidth + deltaX);

//     if (table === 'urgent') setUrgentWidths(prev => ({ ...prev, [col]: newWidth }));
//     else if (table === 'queued') setQueuedWidths(prev => ({ ...prev, [col]: newWidth }));
//     else setTabTablesWidths(prev => ({ ...prev, [col]: newWidth }));
//   };

//   const handleMouseUp = () => {
//     dragInfo.current = null;
//     document.removeEventListener("mousemove", handleMouseMove);
//     document.removeEventListener("mouseup", handleMouseUp);
//   };

//   const handleDoubleClick = (table: 'urgent' | 'queued' | 'tabbed') => {
//     if (table === 'urgent') setUrgentWidths({ tradeId: 90, risk: 65, conf: 65, reason: 180 });
//     else if (table === 'queued') setQueuedWidths({ tradeId: 90, priority: 60, risk: 65, conf: 65, reason: 160 });
//     else setTabTablesWidths({ tradeId: 105, priority: 65, risk: 70, conf: 70, reason: 260 });
//   };

//   // Top Header KPI Computations
//   const countUrgent = urgentCases.length;
//   const countReview = queuedCases.length;
//   const countReviewedToday = Object.values(caseStates).filter((s) => s.reviewStatus === "Reviewed" || s.reviewStatus === "Escalated").length;
//   const countPassed = passedCases.length;

//   const renderPolicies = (policies: any) => {
//     if (!policies) return <span className="text-[10px] text-slate-500">No policies attached.</span>;
//     let items: string[] = [];
//     if (Array.isArray(policies)) items = policies;
//     else if (typeof policies === "string" && policies.startsWith("[")) {
//       items = policies.replace(/[\[\]']/g, "").split(",").map((p) => p.trim()).filter(Boolean);
//     } else if (typeof policies === "string" && policies.trim().length > 0) {
//       items = policies.split(",").map((p) => p.trim());
//     }
    
//     if (items.length === 0) return <span className="text-[10px] text-slate-500">No policies attached.</span>;
//     return items.map((policy, i) => (
//       <span key={i} className="px-1.5 py-0.5 bg-slate-950 text-[10px] rounded border border-slate-800 text-purple-300 font-mono truncate max-w-[220px]">
//         {policy}
//       </span>
//     ));
//   };

//   return (
//     <div className="p-1 h-screen bg-slate-950 text-slate-100 flex flex-col gap-1 overflow-hidden select-none">
      
//       <style>{`
//         .dynamic-scroll { scrollbar-width: none; }
//         .dynamic-scroll::-webkit-scrollbar { width: 4px; height: 4px; display: none; }
//         .dynamic-scroll:hover { scrollbar-width: thin; }
//         .dynamic-scroll:hover::-webkit-scrollbar { display: block; }
//         .dynamic-scroll::-webkit-scrollbar-track { background: transparent; }
//         .dynamic-scroll::-webkit-scrollbar-thumb { background: rgba(148, 163, 184, 0.15); border-radius: 2px; }
//       `}</style>
      
//       {/* Top Header Metrics Layer */}
//       <div className="flex items-center justify-between border-b border-slate-900 pb-1 flex-shrink-0">
//         <h1 className="text-sm font-bold tracking-tight text-slate-200">
//           AI Compliance Review Copilot
//         </h1>
        
//         <div className="flex items-center gap-2">
//           <div className="bg-rose-950/30 border border-rose-500/30 rounded px-2 py-0.5 flex items-center gap-1.5 text-[11px] font-medium shadow-sm">
//             <AlertCircle className="w-3 h-3 text-rose-400" />
//             <span className="text-rose-300">Urgent:</span>
//             <span className="text-xs font-black text-rose-100">{countUrgent}</span>
//           </div>

//           <div className="bg-amber-950/30 border border-amber-500/30 rounded px-2 py-0.5 flex items-center gap-1.5 text-[11px] font-medium shadow-sm">
//             <Clock className="w-3 h-3 text-amber-400" />
//             <span className="text-amber-300">Review:</span>
//             <span className="text-xs font-black text-amber-100">{countReview}</span>
//           </div>

//           <div className="bg-purple-950/30 border border-purple-500/30 rounded px-2 py-0.5 flex items-center gap-1.5 text-[11px] font-medium shadow-sm">
//             <CheckSquare className="w-3 h-3 text-purple-400" />
//             <span className="text-purple-300">Reviewed Today:</span>
//             <span className="text-xs font-black text-purple-100">{countReviewedToday}</span>
//           </div>

//           <div className="bg-emerald-950/30 border border-emerald-500/30 rounded px-2 py-0.5 flex items-center gap-1.5 text-[11px] font-medium shadow-sm">
//             <CheckCircle className="w-3 h-3 text-emerald-400" />
//             <span className="text-emerald-300">Passed:</span>
//             <span className="text-xs font-black text-emerald-100">{countPassed}</span>
//           </div>
//         </div>
//       </div>

//       {/* Main Left/Right Side-by-Side Split Grid Container */}
//       <div className="flex-1 grid grid-cols-[38fr_62fr] gap-1.5 min-h-0 h-full overflow-hidden">
        
//         {/* LEFT COMPARTMENT: Filter Navigation Tabs + Viewport List Display */}
//         <div className="flex flex-col gap-1 min-h-0 h-full overflow-hidden">
          
//           {/* Tab Selection Bar Wrapper */}
//           <div className="flex bg-slate-900 p-0.5 rounded border border-slate-800/80 gap-0.5 flex-shrink-0">
//             <button
//               onClick={() => setActiveView("active")}
//               className={`flex-1 text-center py-1 text-[10px] font-bold uppercase tracking-wider rounded transition-all ${
//                 activeView === "active" ? "bg-slate-800 text-purple-400 shadow-sm border border-slate-700/50" : "text-slate-400 hover:text-slate-200"
//               }`}
//             >
//               Active
//             </button>
//             <button
//               onClick={() => setActiveView("reviewed")}
//               className={`flex-1 text-center py-1 text-[10px] font-bold uppercase tracking-wider rounded transition-all ${
//                 activeView === "reviewed" ? "bg-slate-800 text-purple-400 shadow-sm border border-slate-700/50" : "text-slate-400 hover:text-slate-200"
//               }`}
//             >
//               Reviewed
//             </button>
//             <button
//               onClick={() => setActiveView("passed")}
//               className={`flex-1 text-center py-1 text-[10px] font-bold uppercase tracking-wider rounded transition-all ${
//                 activeView === "passed" ? "bg-slate-800 text-purple-400 shadow-sm border border-slate-700/50" : "text-slate-400 hover:text-slate-200"
//               }`}
//             >
//               Passed
//             </button>
//           </div>

//           {/* Conditional Content Rendering Workspace Section */}
//           <div className="flex-1 min-h-0 h-full overflow-hidden">
            
//             {activeView === "active" && (
//               <div className="grid grid-rows-2 gap-1.5 min-h-0 h-full overflow-hidden">
//                 {/* URGENT TRACK PANEL */}
//                 <div className="bg-slate-900 border border-rose-500/10 rounded-md p-1.5 flex flex-col min-h-0 h-full overflow-hidden">
//                   <div className="flex items-center gap-1 border-b border-slate-800 pb-0.5 mb-1 flex-shrink-0">
//                     <ShieldAlert className="w-3 h-3 text-rose-400" />
//                     <h2 className="text-[10px] font-bold text-rose-400 uppercase tracking-wider">Urgent Action Required</h2>
//                   </div>
                  
//                   <div className="flex-1 overflow-auto min-h-0 relative border border-slate-800/30 rounded dynamic-scroll">
//                     {urgentCases.length === 0 ? (
//                       <p className="text-xs text-slate-500 p-1">No urgent cases outstanding.</p>
//                     ) : (
//                       <table className="text-left text-xs border-collapse table-fixed w-max min-w-full">
//                         <thead className="sticky top-0 bg-slate-900 text-slate-400 font-bold uppercase text-[9px] border-b border-slate-800 z-10">
//                           <tr>
//                             <th style={{ width: urgentWidths.tradeId }} className="p-1 relative group">
//                               Trade ID
//                               <div onMouseDown={(e) => handleMouseDown('urgent', 'tradeId', e)} onDoubleClick={() => handleDoubleClick('urgent')} className="absolute right-0 top-0 bottom-0 w-1 bg-slate-700/0 group-hover:bg-purple-500/50 cursor-col-resize transition-colors" />
//                             </th>
//                             <th style={{ width: urgentWidths.risk }} className="p-1 text-right relative group">
//                               Risk
//                               <div onMouseDown={(e) => handleMouseDown('urgent', 'risk', e)} onDoubleClick={() => handleDoubleClick('urgent')} className="absolute right-0 top-0 bottom-0 w-1 bg-slate-700/0 group-hover:bg-purple-500/50 cursor-col-resize transition-colors" />
//                             </th>
//                             <th style={{ width: urgentWidths.conf }} className="p-1 text-right relative group">
//                               Conf.
//                               <div onMouseDown={(e) => handleMouseDown('urgent', 'conf', e)} onDoubleClick={() => handleDoubleClick('urgent')} className="absolute right-0 top-0 bottom-0 w-1 bg-slate-700/0 group-hover:bg-purple-500/50 cursor-col-resize transition-colors" />
//                             </th>
//                             <th style={{ width: urgentWidths.reason }} className="p-1 pl-2 relative group">
//                               Flag Reason
//                               <div onMouseDown={(e) => handleMouseDown('urgent', 'reason', e)} onDoubleClick={() => handleDoubleClick('urgent')} className="absolute right-0 top-0 bottom-0 w-1 bg-slate-700/0 group-hover:bg-purple-500/50 cursor-col-resize transition-colors" />
//                             </th>
//                           </tr>
//                         </thead>
//                         <tbody className="divide-y divide-slate-800/30">
//                           {urgentCases.map((c, idx) => {
//                             const isSelected = selectedCase?.trade_id === c?.trade_id;
//                             const riskVal = 1 - (Number(c?.compliance_probability) ?? 1.0);
//                             return (
//                               <tr
//                                 key={`${c?.trade_id}-${idx}`}
//                                 onClick={() => handleCaseSelection(c)}
//                                 className={`cursor-pointer text-[11px] transition-colors ${isSelected ? 'bg-rose-950/40 font-semibold border-l-2 border-rose-500 text-rose-200' : 'hover:bg-slate-800/30 text-slate-300'}`}
//                               >
//                                 <td className="p-1 font-mono truncate">{c?.trade_id}</td>
//                                 <td className="p-1 text-right font-mono text-rose-400/90">{riskVal.toFixed(2)}</td>
//                                 <td className="p-1 text-right font-mono text-slate-400">{(Number(c?.confidence_score) || 0).toFixed(2)}</td>
//                                 <td className="p-1 pl-2 truncate text-[10px]">{c?.flag_reason}</td>
//                               </tr>
//                             );
//                           })}
//                         </tbody>
//                       </table>
//                     )}
//                   </div>
//                 </div>

//                 {/* REVIEW QUEUE PANEL */}
//                 <div className="bg-slate-900 border border-slate-800/80 rounded-md p-1.5 flex flex-col min-h-0 h-full overflow-hidden">
//                   <div className="flex items-center gap-1 border-b border-slate-800 pb-0.5 mb-1 flex-shrink-0">
//                     <Clock className="w-3 h-3 text-amber-400" />
//                     <h2 className="text-[10px] font-bold text-amber-400 uppercase tracking-wider">Review</h2>
//                   </div>
                  
//                   <div className="flex-1 overflow-auto min-h-0 relative border border-slate-800/30 rounded dynamic-scroll">
//                     {queuedCases.length === 0 ? (
//                       <p className="text-xs text-slate-500 p-1">Review queue empty.</p>
//                     ) : (
//                       <table className="text-left text-xs border-collapse table-fixed w-max min-w-full">
//                         <thead className="sticky top-0 bg-slate-900 text-slate-400 font-bold uppercase text-[9px] border-b border-slate-800 z-10">
//                           <tr>
//                             <th style={{ width: queuedWidths.tradeId }} className="p-1 relative group">
//                               Trade ID
//                               <div onMouseDown={(e) => handleMouseDown('queued', 'tradeId', e)} onDoubleClick={() => handleDoubleClick('queued')} className="absolute right-0 top-0 bottom-0 w-1 bg-slate-700/0 group-hover:bg-purple-500/50 cursor-col-resize transition-colors" />
//                             </th>
//                             <th style={{ width: queuedWidths.priority }} className="p-1 text-right relative group text-amber-400">
//                               Prio
//                               <div onMouseDown={(e) => handleMouseDown('queued', 'priority', e)} onDoubleClick={() => handleDoubleClick('queued')} className="absolute right-0 top-0 bottom-0 w-1 bg-slate-700/0 group-hover:bg-purple-500/50 cursor-col-resize transition-colors" />
//                             </th>
//                             <th style={{ width: queuedWidths.risk }} className="p-1 text-right relative group">
//                               Risk
//                               <div onMouseDown={(e) => handleMouseDown('queued', 'risk', e)} onDoubleClick={() => handleDoubleClick('queued')} className="absolute right-0 top-0 bottom-0 w-1 bg-slate-700/0 group-hover:bg-purple-500/50 cursor-col-resize transition-colors" />
//                             </th>
//                             <th style={{ width: queuedWidths.conf }} className="p-1 text-right relative group">
//                               Conf.
//                               <div onMouseDown={(e) => handleMouseDown('queued', 'conf', e)} onDoubleClick={() => handleDoubleClick('queued')} className="absolute right-0 top-0 bottom-0 w-1 bg-slate-700/0 group-hover:bg-purple-500/50 cursor-col-resize transition-colors" />
//                             </th>
//                             <th style={{ width: queuedWidths.reason }} className="p-1 pl-2 relative group">
//                               Flag Reason
//                               <div onMouseDown={(e) => handleMouseDown('queued', 'reason', e)} onDoubleClick={() => handleDoubleClick('queued')} className="absolute right-0 top-0 bottom-0 w-1 bg-slate-700/0 group-hover:bg-purple-500/50 cursor-col-resize transition-colors" />
//                             </th>
//                           </tr>
//                         </thead>
//                         <tbody className="divide-y divide-slate-800/30">
//                           {queuedCases.map((c, idx) => {
//                             const isSelected = selectedCase?.trade_id === c?.trade_id;
//                             const riskVal = 1 - (Number(c?.compliance_probability) ?? 1.0);
//                             return (
//                               <tr
//                                 key={`${c?.trade_id}-${idx}`}
//                                 onClick={() => handleCaseSelection(c)}
//                                 className={`cursor-pointer text-[11px] transition-colors ${isSelected ? 'bg-purple-950/40 font-semibold border-l-2 border-purple-500 text-purple-200' : 'hover:bg-slate-800/30 text-slate-300'}`}
//                               >
//                                 <td className="p-1 font-mono truncate">{c?.trade_id}</td>
//                                 <td className="p-1 text-right font-mono font-bold text-amber-400">{c?.priority_score ?? "0"}</td>
//                                 <td className="p-1 text-right font-mono text-rose-400/90">{riskVal.toFixed(2)}</td>
//                                 <td className="p-1 text-right font-mono text-slate-400">{(Number(c?.confidence_score) || 0).toFixed(2)}</td>
//                                 <td className="p-1 pl-2 truncate text-[10px]">{c?.flag_reason}</td>
//                               </tr>
//                             );
//                           })}
//                         </tbody>
//                       </table>
//                     )}
//                   </div>
//                 </div>
//               </div>
//             )}

//             {activeView === "reviewed" && (
//               <div className="bg-slate-900 border border-slate-800 rounded-md p-1.5 flex flex-col min-h-0 h-full overflow-hidden">
//                 <div className="flex items-center gap-1 border-b border-slate-800 pb-0.5 mb-1 flex-shrink-0">
//                   <ArrowUpRight className="w-3 h-3 text-purple-400" />
//                   <h2 className="text-[10px] font-bold text-purple-400 uppercase tracking-wider">Processed Review Logs</h2>
//                 </div>
//                 <div className="flex-1 overflow-auto min-h-0 relative border border-slate-800/30 rounded dynamic-scroll">
//                   {reviewedCases.length === 0 ? (
//                     <p className="text-xs text-slate-500 p-1">No cases reviewed or escalated yet.</p>
//                   ) : (
//                     <table className="text-left text-xs border-collapse table-fixed w-max min-w-full">
//                       <thead className="sticky top-0 bg-slate-900 text-slate-400 font-bold uppercase text-[9px] border-b border-slate-800 z-10">
//                         <tr>
//                           <th style={{ width: tabTablesWidths.tradeId }} className="p-1 relative group">
//                             Trade ID
//                             <div onMouseDown={(e) => handleMouseDown('tabbed', 'tradeId', e)} onDoubleClick={() => handleDoubleClick('tabbed')} className="absolute right-0 top-0 bottom-0 w-1 bg-slate-700/0 group-hover:bg-purple-500/50 cursor-col-resize transition-colors" />
//                           </th>
//                           <th style={{ width: tabTablesWidths.risk }} className="p-1 text-right relative group">
//                             Risk
//                             <div onMouseDown={(e) => handleMouseDown('tabbed', 'risk', e)} onDoubleClick={() => handleDoubleClick('tabbed')} className="absolute right-0 top-0 bottom-0 w-1 bg-slate-700/0 group-hover:bg-purple-500/50 cursor-col-resize transition-colors" />
//                           </th>
//                           <th style={{ width: tabTablesWidths.conf }} className="p-1 text-right relative group">
//                             Conf.
//                             <div onMouseDown={(e) => handleMouseDown('tabbed', 'conf', e)} onDoubleClick={() => handleDoubleClick('tabbed')} className="absolute right-0 top-0 bottom-0 w-1 bg-slate-700/0 group-hover:bg-purple-500/50 cursor-col-resize transition-colors" />
//                           </th>
//                           <th style={{ width: tabTablesWidths.reason }} className="p-1 pl-2 relative group">
//                             Status Signature
//                             <div onMouseDown={(e) => handleMouseDown('tabbed', 'reason', e)} onDoubleClick={() => handleDoubleClick('tabbed')} className="absolute right-0 top-0 bottom-0 w-1 bg-slate-700/0 group-hover:bg-purple-500/50 cursor-col-resize transition-colors" />
//                           </th>
//                         </tr>
//                       </thead>
//                       <tbody className="divide-y divide-slate-800/30">
//                         {reviewedCases.map((c, idx) => {
//                           const isSelected = selectedCase?.trade_id === c?.trade_id;
//                           const auditStatus = caseStates[c?.trade_id]?.reviewStatus;
//                           const riskVal = 1 - (Number(c?.compliance_probability) ?? 1.0);
//                           return (
//                             <tr
//                               key={`${c?.trade_id}-${idx}`}
//                               onClick={() => handleCaseSelection(c)}
//                               className={`cursor-pointer text-[11px] transition-colors ${isSelected ? 'bg-purple-950/40 font-semibold border-l-2 border-purple-500 text-purple-200' : 'hover:bg-slate-800/30 text-slate-300'}`}
//                             >
//                               <td className="p-1 font-mono truncate">{c?.trade_id}</td>
//                               <td className="p-1 text-right font-mono text-slate-400">{riskVal.toFixed(2)}</td>
//                               <td className="p-1 text-right font-mono text-slate-500">{(Number(c?.confidence_score) || 0).toFixed(2)}</td>
//                               <td className="p-1 pl-2 truncate font-semibold uppercase text-[10px]">
//                                 <span className={auditStatus === "Escalated" ? "text-rose-400" : "text-emerald-400"}>
//                                   {auditStatus}
//                                 </span>
//                               </td>
//                             </tr>
//                           );
//                         })}
//                       </tbody>
//                     </table>
//                   )}
//                 </div>
//               </div>
//             )}

//             {activeView === "passed" && (
//               <div className="bg-slate-900 border border-slate-800 rounded-md p-1.5 flex flex-col min-h-0 h-full overflow-hidden">
//                 <div className="flex items-center gap-1 border-b border-slate-800 pb-0.5 mb-1 flex-shrink-0">
//                   <CheckCircle className="w-3 h-3 text-emerald-400" />
//                   <h2 className="text-[10px] font-bold text-emerald-400 uppercase tracking-wider">Auto Passed (Compliant)</h2>
//                 </div>
//                 <div className="flex-1 overflow-auto min-h-0 relative border border-slate-800/30 rounded dynamic-scroll">
//                   {passedCases.length === 0 ? (
//                     <p className="text-xs text-slate-500 p-1">No automatic pass items.</p>
//                   ) : (
//                     <table className="text-left text-xs border-collapse table-fixed w-max min-w-full">
//                       <thead className="sticky top-0 bg-slate-900 text-slate-400 font-bold uppercase text-[9px] border-b border-slate-800 z-10">
//                         <tr>
//                           <th style={{ width: tabTablesWidths.tradeId }} className="p-1 relative group">
//                             Trade ID
//                             <div onMouseDown={(e) => handleMouseDown('tabbed', 'tradeId', e)} onDoubleClick={() => handleDoubleClick('tabbed')} className="absolute right-0 top-0 bottom-0 w-1 bg-slate-700/0 group-hover:bg-purple-500/50 cursor-col-resize transition-colors" />
//                           </th>
//                           <th style={{ width: tabTablesWidths.risk }} className="p-1 text-right relative group">
//                             Risk
//                             <div onMouseDown={(e) => handleMouseDown('tabbed', 'risk', e)} onDoubleClick={() => handleDoubleClick('tabbed')} className="absolute right-0 top-0 bottom-0 w-1 bg-slate-700/0 group-hover:bg-purple-500/50 cursor-col-resize transition-colors" />
//                           </th>
//                           <th style={{ width: tabTablesWidths.conf }} className="p-1 text-right relative group">
//                             Conf.
//                             <div onMouseDown={(e) => handleMouseDown('tabbed', 'conf', e)} onDoubleClick={() => handleDoubleClick('tabbed')} className="absolute right-0 top-0 bottom-0 w-1 bg-slate-700/0 group-hover:bg-purple-500/50 cursor-col-resize transition-colors" />
//                           </th>
//                           <th style={{ width: tabTablesWidths.reason }} className="p-1 pl-2 relative group">
//                             Classification
//                             <div onMouseDown={(e) => handleMouseDown('tabbed', 'reason', e)} onDoubleClick={() => handleDoubleClick('tabbed')} className="absolute right-0 top-0 bottom-0 w-1 bg-slate-700/0 group-hover:bg-purple-500/50 cursor-col-resize transition-colors" />
//                           </th>
//                         </tr>
//                       </thead>
//                       <tbody className="divide-y divide-slate-800/30">
//                         {passedCases.map((c, idx) => {
//                           const isSelected = selectedCase?.trade_id === c?.trade_id;
//                           const riskVal = 1 - (Number(c?.compliance_probability) ?? 1.0);
//                           return (
//                             <tr
//                               key={`${c?.trade_id}-${idx}`}
//                               onClick={() => handleCaseSelection(c)}
//                               className={`cursor-pointer text-[11px] transition-colors ${isSelected ? 'bg-emerald-950/40 font-semibold border-l-2 border-emerald-500 text-emerald-200' : 'hover:bg-slate-800/30 text-slate-300'}`}
//                             >
//                               <td className="p-1 font-mono truncate">{c?.trade_id}</td>
//                               <td className="p-1 text-right font-mono text-emerald-400/90">{riskVal.toFixed(2)}</td>
//                               <td className="p-1 text-right font-mono text-slate-400">{(Number(c?.confidence_score) || 0).toFixed(2)}</td>
//                               <td className="p-1 pl-2 truncate text-[10px] text-emerald-400 font-medium">Auto-Cleared Compliant</td>
//                             </tr>
//                           );
//                         })}
//                       </tbody>
//                     </table>
//                   )}
//                 </div>
//               </div>
//             )}

//           </div>
//         </div>

//         {/* RIGHT COMPARTMENT: Re-Architected Non-Overlapping Workspace Section */}
//         <div className="bg-slate-900 border border-slate-800 rounded-md p-2.5 flex flex-col min-h-0 h-full overflow-hidden shadow-2xl">
//           {selectedCase ? (
//             (() => {
//               const currentState = caseStates[selectedCase?.trade_id] || { reviewStatus: "Not reviewed", notes: "" };
              
//               // Safe number casting fallback
//               const rawProb = selectedCase?.compliance_probability !== undefined ? Number(selectedCase.compliance_probability) : 1;
//               const riskVal = 1 - rawProb;
              
//               const currentRec = currentState.overriddenLabel || selectedCase?.compliance_label || "Compliant";
//               const isRecCompliant = currentRec.toLowerCase().includes("compliant");
              
//               return (
//                 <div className="flex flex-col h-full justify-between min-h-0 overflow-hidden">
                  
//                   {/* Title & Top Summary Badges Line */}
//                   <div className="flex items-center justify-between border-b border-slate-800 pb-1.5 flex-shrink-0">
//                     <div className="flex flex-col gap-0.5">
//                       <div className="flex items-center gap-1.5">
//                         <span className="text-[9px] font-black uppercase tracking-wider text-purple-400 bg-purple-950/30 px-1.5 py-0.5 rounded border border-purple-900/40">
//                           Audit Space
//                         </span>
//                         <span className="text-xs font-mono font-bold text-slate-100">{selectedCase?.trade_id || "—"}</span>
//                       </div>
//                       <div>
//                         <span className={`px-1.5 py-0.2 rounded text-[8px] font-bold tracking-wide border ${
//                           currentState.reviewStatus === "Reviewed"
//                             ? "bg-emerald-950/40 text-emerald-400 border-emerald-800/40" 
//                             : currentState.reviewStatus === "Escalated"
//                             ? "bg-rose-950/40 text-rose-400 border-rose-800/40"
//                             : "bg-slate-950 text-amber-400 border-amber-900/40"
//                         }`}>
//                           {currentState.reviewStatus ? currentState.reviewStatus.toUpperCase() : "NOT REVIEWED"}
//                         </span>
//                       </div>
//                     </div>
                    
//                     {/* Horizontal Meta Scores Banner */}
//                     <div className="flex items-center gap-x-2 bg-slate-950/80 px-2 py-1 rounded border border-slate-800/60 text-[10px]">
//                       <div className="flex items-center gap-1">
//                         <span className="text-slate-500 font-medium text-[8px] uppercase">AI Rec:</span>
//                         <span className={`font-bold tracking-tight px-1 rounded text-[9px] ${
//                           isRecCompliant ? "bg-emerald-950/50 text-emerald-400" : "bg-rose-950/50 text-rose-400"
//                         }`}>
//                           {isRecCompliant ? "Compliant" : "Non-compliant"}
//                         </span>
//                       </div>
//                       <div className="border-l border-slate-800 h-3" />
//                       <div>
//                         <span className="text-slate-500 font-medium text-[8px] uppercase mr-0.5">Risk:</span>
//                         <span className="font-mono font-bold text-rose-400">{isNaN(riskVal) ? "0.000" : riskVal.toFixed(3)}</span>
//                       </div>
//                       <div className="border-l border-slate-800 h-3" />
//                       <div>
//                         <span className="text-slate-500 font-medium text-[8px] uppercase mr-0.5">Conf:</span>
//                         <span className="font-mono font-bold text-sky-400">{selectedCase?.confidence_score !== undefined ? Number(selectedCase.confidence_score).toFixed(3) : "1.000"}</span>
//                       </div>
//                       <div className="border-l border-slate-800 h-3" />
//                       <div>
//                         <span className="text-slate-500 font-medium text-[8px] uppercase mr-0.5">Prio:</span>
//                         <span className="font-mono font-bold text-amber-400">{selectedCase?.priority_score ?? "0"}</span>
//                       </div>
//                     </div>
//                   </div>

//                   {/* STRUCTURAL WORKSPACE WRAPPER */}
//                   <div className="flex-1 flex flex-col gap-1.5 justify-start min-h-0 pt-1.5 overflow-hidden">
                    
//                     {/* LAYOUT LAYER 1: Full-Width Trade Fields (Without Notional Value) */}
//                     <div className="bg-slate-950/20 border border-slate-800/40 p-1.5 rounded flex-shrink-0">
//                       <div className="flex items-center gap-1 border-b border-slate-800/60 pb-0.5 mb-1">
//                         <Briefcase className="w-3 h-3 text-purple-400" />
//                         <h4 className="text-[9px] font-bold text-purple-400 uppercase tracking-wider">Trade Fields</h4>
//                       </div>
//                       <div className="text-[11px] grid grid-cols-3 gap-2 text-slate-300">
//                         <div>
//                           <div className="text-slate-500 text-[8px] uppercase font-semibold">Investment Type</div>
//                           <div className="font-medium truncate">{selectedCase?.investment_type || selectedCase?.asset_class || "N/A"}</div>
//                         </div>
//                         <div>
//                           <div className="text-slate-500 text-[8px] uppercase font-semibold">Investment Amount</div>
//                           <div className="font-mono font-bold text-emerald-400">
//                             {selectedCase?.investment_amount ? `$${Number(selectedCase.investment_amount).toLocaleString(undefined, {minimumFractionDigits: 2})}` : "N/A"}
//                           </div>
//                         </div>
//                         <div>
//                           <div className="text-slate-500 text-[8px] uppercase font-semibold">Execution Timestamp</div>
//                           <div className="font-mono truncate text-slate-400">{selectedCase?.timestamp || "N/A"}</div>
//                         </div>
//                       </div>
//                     </div>

//                     {/* LAYOUT LAYER 2: Side-by-Side Dual Column Mix */}
//                     <div className="grid grid-cols-2 gap-1.5 flex-shrink-0">
                      
//                       {/* Column A: Client Profile */}
//                       <div className="bg-slate-950/20 border border-slate-800/40 p-1.5 rounded">
//                         <div className="flex items-center gap-1 border-b border-slate-800/60 pb-0.5 mb-1">
//                           <User className="w-3 h-3 text-sky-400" />
//                           <h4 className="text-[9px] font-bold text-sky-400 uppercase tracking-wider">Client Profile</h4>
//                         </div>
//                         <div className="text-[11px] space-y-1 text-slate-300">
//                           <div className="grid grid-cols-2 gap-1.5">
//                             <div>
//                               <div className="text-slate-500 text-[8px] uppercase font-semibold">Age</div>
//                               <div className="font-mono text-xs">{selectedCase?.client_age ?? "—"}</div>
//                             </div>
//                             <div>
//                               <div className="text-slate-500 text-[8px] uppercase font-semibold">Annual Income</div>
//                               <div className="font-mono truncate text-xs">{selectedCase?.client_income ? `$${Number(selectedCase.client_income).toLocaleString()}` : "—"}</div>
//                             </div>
//                           </div>
//                           <div className="grid grid-cols-2 gap-1.5 pt-0.5 border-t border-slate-800/30">
//                             <div>
//                               <div className="text-slate-500 text-[8px] uppercase font-semibold">Risk Tolerance</div>
//                               <div className="truncate text-[10px]">{selectedCase?.risk_tolerance || selectedCase?.client_risk_tolerance || "—"}</div>
//                             </div>
//                             <div>
//                               <div className="text-slate-500 text-[8px] uppercase font-semibold">Experience</div>
//                               <div className="truncate text-[10px]">{selectedCase?.investment_experience || "—"}</div>
//                             </div>
//                           </div>
//                           <div className="pt-0.5 border-t border-slate-800/30">
//                             <div className="text-slate-500 text-[8px] uppercase font-semibold">Objective & Horizon</div>
//                             <div className="text-[10px] leading-tight text-slate-400 truncate">
//                               {selectedCase?.investment_objective || "—"} {selectedCase?.investment_time_horizon ? `(${selectedCase.investment_time_horizon})` : ""}
//                             </div>
//                           </div>
//                         </div>
//                       </div>

//                       {/* Column B: Advisor Records */}
//                       <div className="bg-slate-950/20 border border-slate-800/40 p-1.5 rounded">
//                         <div className="flex items-center gap-1 border-b border-slate-800/60 pb-0.5 mb-1">
//                           <FileText className="w-3 h-3 text-amber-400" />
//                           <h4 className="text-[9px] font-bold text-amber-400 uppercase tracking-wider">Advisor Records</h4>
//                         </div>
//                         <div className="text-[11px] space-y-1 text-slate-300">
//                           <div className="grid grid-cols-2 gap-1.5 text-[10px]">
//                             <div>
//                               <span className="text-slate-500 block text-[8px] uppercase font-semibold">Advisor ID</span>
//                               <span className="font-mono font-medium truncate block">{selectedCase?.advisor_id || "—"}</span>
//                             </div>
//                             <div>
//                               <span className="text-slate-500 block text-[8px] uppercase font-semibold">Tenure Rate</span>
//                               <span className="truncate block text-[10px]">{selectedCase?.advisor_experience || "—"}</span>
//                             </div>
//                           </div>
//                           <div className="grid grid-cols-2 gap-1.5 pt-0.5 border-t border-slate-800/50 items-center">
//                             <div>
//                               <span className="text-slate-500 block text-[8px] uppercase font-semibold">History Risk</span>
//                               <span className="font-mono text-rose-400 text-xs">{selectedCase?.advisor_history_risk ?? "0.00"}</span>
//                             </div>
//                             <div>
//                               <span className="text-slate-500 block text-[8px] uppercase font-semibold">Rationale</span>
//                               <span className={`inline-block px-1 rounded text-[8px] font-bold ${
//                                 selectedCase?.has_rationale === true || selectedCase?.has_rationale === "true"
//                                   ? "bg-emerald-950 text-emerald-400 border border-emerald-800/50" 
//                                   : "bg-slate-950 text-slate-500 border border-slate-800"
//                               }`}>
//                                 {selectedCase?.has_rationale ? "FILED" : "STANDARD"}
//                               </span>
//                             </div>
//                           </div>
//                           <div className="pt-0.5 border-t border-slate-800/50">
//                             <span className="text-slate-500 block text-[8px] uppercase font-semibold mb-0.5">Desk Notes Context</span>
//                             <p className="text-[10px] text-slate-400 leading-none truncate">
//                               {selectedCase?.advisor_notes || "No transactional exceptions noted on account initialization."}
//                             </p>
//                           </div>
//                         </div>
//                       </div>

//                     </div>

//                     {/* LAYOUT LAYER 3: Full-Width Exception Breakdown Sits Directly Above Regulatory Policies */}
//                     <div className="bg-slate-950/20 border border-slate-800/40 p-1.5 rounded flex-1 flex flex-col min-h-0">
//                       <div className="flex items-center gap-1 border-b border-slate-800/60 pb-0.5 mb-1 flex-shrink-0">
//                         <HelpCircle className="w-3 h-3 text-rose-400" />
//                         <h4 className="text-[9px] font-bold text-rose-400 uppercase tracking-wider">Exception Breakdown</h4>
//                       </div>
//                       <div className="text-[11px] text-slate-300 flex-1 overflow-y-auto dynamic-scroll">
//                         <div className="text-slate-500 text-[8px] uppercase font-semibold mb-0.5">Flag Reason Details</div>
//                         <p className="text-[11px] leading-relaxed text-slate-300 font-medium">
//                           {selectedCase?.flag_reason || "No structural deviations or algorithmic rule violations flagged for this transaction pattern. File satisfies compliance parameters."}
//                         </p>
//                       </div>
//                     </div>

//                   </div>

//                   {/* Policy Box (Placed immediately below Exception Breakdown) */}
//                   <div className="bg-slate-950/40 border border-slate-800/50 p-2 rounded flex-shrink-0 my-1">
//                     <div className="text-[8px] font-black text-slate-500 uppercase tracking-wider mb-1">
//                       Retrieved Regulatory & Firm Policies:
//                     </div>
//                     <div className="flex flex-wrap gap-1 items-center max-h-[36px] overflow-y-auto dynamic-scroll">
//                       {renderPolicies(selectedCase?.retrieved_policies)}
//                     </div>
//                   </div>

//                   {/* Sign-off Form Area */}
//                   <div className="border-t border-slate-800/80 pt-1.5 flex flex-col gap-1.5 flex-shrink-0">
//                     <div className="flex flex-col">
//                       <label className="text-[9px] font-black text-slate-400 uppercase tracking-widest mb-0.5">
//                         Reviewer Sign-off Notes
//                       </label>
//                       <input
//                         type="text"
//                         value={currentNotes}
//                         onChange={(e) => handleNotesChange(e.target.value)}
//                         placeholder="Enter compliance justification or structural risk override arguments..."
//                         className="w-full bg-slate-950 border border-slate-800 rounded px-2.5 py-1 text-xs text-slate-200 focus:outline-none focus:border-purple-500/80 transition-colors placeholder:text-slate-600 font-medium"
//                       />
//                     </div>
                    
//                     {/* Action Buttons Row - Replaced and fully enabled for continuous state adjustments */}
//                     <div className="flex gap-2 justify-end">
//                       <button
//                         onClick={() => handleDecision("Rejected")}
//                         className="bg-rose-600 hover:bg-rose-500 text-slate-100 font-black text-[11px] px-3 py-1 rounded transition-colors uppercase tracking-wider whitespace-nowrap"
//                       >
//                         Reject Trade
//                       </button>
//                       <button
//                         onClick={() => handleDecision("Approved")}
//                         className="bg-emerald-600 hover:bg-emerald-500 text-slate-950 font-black text-[11px] px-3 py-1 rounded transition-colors uppercase tracking-wider whitespace-nowrap"
//                       >
//                         Approve Trade
//                       </button>
//                       <button
//                         onClick={() => handleDecision("Escalated")}
//                         className="bg-purple-600 hover:bg-purple-500 text-slate-100 font-black text-[11px] px-3 py-1 rounded transition-colors uppercase tracking-wider whitespace-nowrap"
//                       >
//                         Escalate Review
//                       </button>
//                     </div>
//                   </div>

//                 </div>
//               );
//             })()
//           ) : (
//             <div className="h-full flex items-center justify-center text-slate-500 text-xs font-semibold border border-dashed border-slate-800 rounded">
//               Select a risk transaction case row from the active lists to mount details in the workspace.
//             </div>
//           )}
//         </div>

//       </div>
//     </div>
//   );
// }

// export default Dashboard;

// /* VERSION 12 */

// import { useEffect, useState, useRef } from "react";
// import { getCases } from "../api/cases";
// import { AlertCircle, CheckCircle, Clock, ShieldAlert, FileText, User, Briefcase, HelpCircle, ArrowUpRight, CheckSquare } from "lucide-react";

// interface CaseAuditState {
//   reviewStatus: "Reviewed" | "Not reviewed" | "Escalated";
//   notes: string;
//   overriddenLabel?: string; 
// }

// function Dashboard() {
//   const [activeView, setActiveView] = useState<"active" | "reviewed" | "passed">("active");
//   const [cases, setCases] = useState<any[]>([]);
//   const [selectedCase, setSelectedCase] = useState<any | null>(null);
//   const [caseStates, setCaseStates] = useState<Record<string, CaseAuditState>>({});
//   const [currentNotes, setCurrentNotes] = useState<string>("");

//   // Spreadsheet Column Widths
//   const [urgentWidths, setUrgentWidths] = useState({ tradeId: 90, risk: 65, conf: 65, reason: 180 });
//   const [queuedWidths, setQueuedWidths] = useState({ tradeId: 90, priority: 60, risk: 65, conf: 65, reason: 160 });
//   const [tabTablesWidths, setTabTablesWidths] = useState({ tradeId: 105, priority: 65, risk: 70, conf: 70, reason: 260 });

//   const dragInfo = useRef<{ table: 'urgent' | 'queued' | 'tabbed'; col: string; startX: number; startWidth: number } | null>(null);

//   useEffect(() => {
//     getCases()
//       .then((data) => {
//         if (Array.isArray(data)) {
//           setCases(data);
          
//           const initialStates: Record<string, CaseAuditState> = {};
//           data.forEach((c) => {
//             if (c?.trade_id) {
//               initialStates[c.trade_id] = { 
//                 reviewStatus: "Not reviewed", 
//                 notes: "",
//                 overriddenLabel: c.compliance_label || "Non-compliant"
//               };
//             }
//           });
//           setCaseStates(initialStates);

//           const urgentCases = data.filter((c) => c?.escalation_level === "urgent");
//           const queuedCases = data
//             .filter((c) => c?.escalation_level === "priority" || c?.escalation_level === "queue")
//             .sort((a, b) => (Number(b?.priority_score) || 0) - (Number(a?.priority_score) || 0));

//           if (urgentCases.length > 0) handleCaseSelection(urgentCases[0], initialStates);
//           else if (queuedCases.length > 0) handleCaseSelection(queuedCases[0], initialStates);
//         }
//       })
//       .catch((err) => console.error("API Fetch Error:", err));
//   }, []);

//   const handleCaseSelection = (targetCase: any, latestStates = caseStates) => {
//     setSelectedCase(targetCase);
//     if (targetCase?.trade_id) {
//       const savedState = latestStates[targetCase.trade_id];
//       setCurrentNotes(savedState ? savedState.notes : "");
//     }
//   };

//   const handleNotesChange = (text: string) => {
//     setCurrentNotes(text);
//     if (selectedCase?.trade_id) {
//       setCaseStates(prev => ({
//         ...prev,
//         [selectedCase.trade_id]: { ...prev[selectedCase.trade_id], notes: text }
//       }));
//     }
//   };

//   const handleApproveAI = () => {
//     if (!selectedCase?.trade_id) return;
//     setCaseStates(prev => ({
//       ...prev,
//       [selectedCase.trade_id]: { ...prev[selectedCase.trade_id], reviewStatus: "Reviewed", notes: currentNotes }
//     }));
//   };

//   const handleOverrideAI = () => {
//     if (!selectedCase?.trade_id) return;
//     setCaseStates(prev => {
//       const currentLabel = prev[selectedCase.trade_id]?.overriddenLabel || selectedCase.compliance_label || "Non-compliant";
//       const flippedLabel = currentLabel.toLowerCase().includes("non") ? "Compliant" : "Non-compliant";
//       return {
//         ...prev,
//         [selectedCase.trade_id]: { ...prev[selectedCase.trade_id], reviewStatus: "Reviewed", overriddenLabel: flippedLabel, notes: currentNotes }
//       };
//     });
//   };

//   const handleEscalate = () => {
//     if (!selectedCase?.trade_id) return;
//     setCaseStates(prev => ({
//       ...prev,
//       [selectedCase.trade_id]: { ...prev[selectedCase.trade_id], reviewStatus: "Escalated", notes: currentNotes }
//     }));
//   };

//   const handleMouseDown = (table: 'urgent' | 'queued' | 'tabbed', col: string, e: React.MouseEvent) => {
//     e.preventDefault();
//     let currentWidths = urgentWidths;
//     if (table === 'queued') currentWidths = queuedWidths;
//     if (table === 'tabbed') currentWidths = tabTablesWidths as any;

//     dragInfo.current = {
//       table,
//       col,
//       startX: e.clientX,
//       startWidth: (currentWidths as any)[col]
//     };
//     document.addEventListener("mousemove", handleMouseMove);
//     document.addEventListener("mouseup", handleMouseUp);
//   };

//   const handleMouseMove = (e: MouseEvent) => {
//     if (!dragInfo.current) return;
//     const { table, col, startX, startWidth } = dragInfo.current;
//     const deltaX = e.clientX - startX;
//     const newWidth = Math.max(50, startWidth + deltaX);

//     if (table === 'urgent') setUrgentWidths(prev => ({ ...prev, [col]: newWidth }));
//     else if (table === 'queued') setQueuedWidths(prev => ({ ...prev, [col]: newWidth }));
//     else setTabTablesWidths(prev => ({ ...prev, [col]: newWidth }));
//   };

//   const handleMouseUp = () => {
//     dragInfo.current = null;
//     document.removeEventListener("mousemove", handleMouseMove);
//     document.removeEventListener("mouseup", handleMouseUp);
//   };

//   const handleDoubleClick = (table: 'urgent' | 'queued' | 'tabbed') => {
//     if (table === 'urgent') setUrgentWidths({ tradeId: 90, risk: 65, conf: 65, reason: 180 });
//     else if (table === 'queued') setQueuedWidths({ tradeId: 90, priority: 60, risk: 65, conf: 65, reason: 160 });
//     else setTabTablesWidths({ tradeId: 105, priority: 65, risk: 70, conf: 70, reason: 260 });
//   };

//   // Lists Processing Groupings
//   const urgentCases = cases.filter((c) => {
//     const status = caseStates[c.trade_id]?.reviewStatus || "Not reviewed";
//     return c?.escalation_level === "urgent" && status === "Not reviewed";
//   });

//   const queuedCases = cases
//     .filter((c) => {
//       const status = caseStates[c.trade_id]?.reviewStatus || "Not reviewed";
//       return (c?.escalation_level === "priority" || c?.escalation_level === "queue") && status === "Not reviewed";
//     })
//     .sort((a, b) => (Number(b?.priority_score) || 0) - (Number(a?.priority_score) || 0));

//   const reviewedCases = cases.filter((c) => {
//     const status = caseStates[c.trade_id]?.reviewStatus;
//     return status === "Reviewed" || status === "Escalated";
//   });

//   const passedCases = cases.filter((c) => {
//     return c?.escalation_level !== "urgent" && c?.escalation_level !== "priority" && c?.escalation_level !== "queue";
//   });

//   // Top Header KPI Computations
//   const countUrgent = urgentCases.length;
//   const countReview = queuedCases.length;
//   const countReviewedToday = Object.values(caseStates).filter((s) => s.reviewStatus === "Reviewed" || s.reviewStatus === "Escalated").length;
//   const countPassed = passedCases.length;

//   const renderPolicies = (policies: any) => {
//     if (!policies) return <span className="text-[10px] text-slate-500">No policies attached.</span>;
//     let items: string[] = [];
//     if (Array.isArray(policies)) items = policies;
//     else if (typeof policies === "string" && policies.startsWith("[")) {
//       items = policies.replace(/[\[\]']/g, "").split(",").map((p) => p.trim()).filter(Boolean);
//     } else if (typeof policies === "string" && policies.trim().length > 0) {
//       items = policies.split(",").map((p) => p.trim());
//     }
    
//     if (items.length === 0) return <span className="text-[10px] text-slate-500">No policies attached.</span>;
//     return items.map((policy, i) => (
//       <span key={i} className="px-1.5 py-0.5 bg-slate-950 text-[10px] rounded border border-slate-800 text-purple-300 font-mono truncate max-w-[220px]">
//         {policy}
//       </span>
//     ));
//   };

//   return (
//     <div className="p-1 h-screen bg-slate-950 text-slate-100 flex flex-col gap-1 overflow-hidden select-none">
      
//       <style>{`
//         .dynamic-scroll { scrollbar-width: none; }
//         .dynamic-scroll::-webkit-scrollbar { width: 4px; height: 4px; display: none; }
//         .dynamic-scroll:hover { scrollbar-width: thin; }
//         .dynamic-scroll:hover::-webkit-scrollbar { display: block; }
//         .dynamic-scroll::-webkit-scrollbar-track { background: transparent; }
//         .dynamic-scroll::-webkit-scrollbar-thumb { background: rgba(148, 163, 184, 0.15); border-radius: 2px; }
//       `}</style>
      
//       {/* Top Header Metrics Layer */}
//       <div className="flex items-center justify-between border-b border-slate-900 pb-1 flex-shrink-0">
//         <h1 className="text-sm font-bold tracking-tight text-slate-200">
//           AI Compliance Review Copilot
//         </h1>
        
//         <div className="flex items-center gap-2">
//           <div className="bg-rose-950/30 border border-rose-500/30 rounded px-2 py-0.5 flex items-center gap-1.5 text-[11px] font-medium shadow-sm">
//             <AlertCircle className="w-3 h-3 text-rose-400" />
//             <span className="text-rose-300">Urgent:</span>
//             <span className="text-xs font-black text-rose-100">{countUrgent}</span>
//           </div>

//           <div className="bg-amber-950/30 border border-amber-500/30 rounded px-2 py-0.5 flex items-center gap-1.5 text-[11px] font-medium shadow-sm">
//             <Clock className="w-3 h-3 text-amber-400" />
//             <span className="text-amber-300">Review:</span>
//             <span className="text-xs font-black text-amber-100">{countReview}</span>
//           </div>

//           <div className="bg-purple-950/30 border border-purple-500/30 rounded px-2 py-0.5 flex items-center gap-1.5 text-[11px] font-medium shadow-sm">
//             <CheckSquare className="w-3 h-3 text-purple-400" />
//             <span className="text-purple-300">Reviewed Today:</span>
//             <span className="text-xs font-black text-purple-100">{countReviewedToday}</span>
//           </div>

//           <div className="bg-emerald-950/30 border border-emerald-500/30 rounded px-2 py-0.5 flex items-center gap-1.5 text-[11px] font-medium shadow-sm">
//             <CheckCircle className="w-3 h-3 text-emerald-400" />
//             <span className="text-emerald-300">Passed:</span>
//             <span className="text-xs font-black text-emerald-100">{countPassed}</span>
//           </div>
//         </div>
//       </div>

//       {/* Main Left/Right Side-by-Side Split Grid Container */}
//       <div className="flex-1 grid grid-cols-[38fr_62fr] gap-1.5 min-h-0 h-full overflow-hidden">
        
//         {/* LEFT COMPARTMENT: Filter Navigation Tabs + Viewport List Display */}
//         <div className="flex flex-col gap-1 min-h-0 h-full overflow-hidden">
          
//           {/* Tab Selection Bar Wrapper */}
//           <div className="flex bg-slate-900 p-0.5 rounded border border-slate-800/80 gap-0.5 flex-shrink-0">
//             <button
//               onClick={() => setActiveView("active")}
//               className={`flex-1 text-center py-1 text-[10px] font-bold uppercase tracking-wider rounded transition-all ${
//                 activeView === "active" ? "bg-slate-800 text-purple-400 shadow-sm border border-slate-700/50" : "text-slate-400 hover:text-slate-200"
//               }`}
//             >
//               Active
//             </button>
//             <button
//               onClick={() => setActiveView("reviewed")}
//               className={`flex-1 text-center py-1 text-[10px] font-bold uppercase tracking-wider rounded transition-all ${
//                 activeView === "reviewed" ? "bg-slate-800 text-purple-400 shadow-sm border border-slate-700/50" : "text-slate-400 hover:text-slate-200"
//               }`}
//             >
//               Reviewed
//             </button>
//             <button
//               onClick={() => setActiveView("passed")}
//               className={`flex-1 text-center py-1 text-[10px] font-bold uppercase tracking-wider rounded transition-all ${
//                 activeView === "passed" ? "bg-slate-800 text-purple-400 shadow-sm border border-slate-700/50" : "text-slate-400 hover:text-slate-200"
//               }`}
//             >
//               Passed
//             </button>
//           </div>

//           {/* Conditional Content Rendering Workspace Section */}
//           <div className="flex-1 min-h-0 h-full overflow-hidden">
            
//             {activeView === "active" && (
//               <div className="grid grid-rows-2 gap-1.5 min-h-0 h-full overflow-hidden">
//                 {/* URGENT TRACK PANEL */}
//                 <div className="bg-slate-900 border border-rose-500/10 rounded-md p-1.5 flex flex-col min-h-0 h-full overflow-hidden">
//                   <div className="flex items-center gap-1 border-b border-slate-800 pb-0.5 mb-1 flex-shrink-0">
//                     <ShieldAlert className="w-3 h-3 text-rose-400" />
//                     <h2 className="text-[10px] font-bold text-rose-400 uppercase tracking-wider">Urgent Action Required</h2>
//                   </div>
                  
//                   <div className="flex-1 overflow-auto min-h-0 relative border border-slate-800/30 rounded dynamic-scroll">
//                     {urgentCases.length === 0 ? (
//                       <p className="text-xs text-slate-500 p-1">No urgent cases outstanding.</p>
//                     ) : (
//                       <table className="text-left text-xs border-collapse table-fixed w-max min-w-full">
//                         <thead className="sticky top-0 bg-slate-900 text-slate-400 font-bold uppercase text-[9px] border-b border-slate-800 z-10">
//                           <tr>
//                             <th style={{ width: urgentWidths.tradeId }} className="p-1 relative group">
//                               Trade ID
//                               <div onMouseDown={(e) => handleMouseDown('urgent', 'tradeId', e)} onDoubleClick={() => handleDoubleClick('urgent')} className="absolute right-0 top-0 bottom-0 w-1 bg-slate-700/0 group-hover:bg-purple-500/50 cursor-col-resize transition-colors" />
//                             </th>
//                             <th style={{ width: urgentWidths.risk }} className="p-1 text-right relative group">
//                               Risk
//                               <div onMouseDown={(e) => handleMouseDown('urgent', 'risk', e)} onDoubleClick={() => handleDoubleClick('urgent')} className="absolute right-0 top-0 bottom-0 w-1 bg-slate-700/0 group-hover:bg-purple-500/50 cursor-col-resize transition-colors" />
//                             </th>
//                             <th style={{ width: urgentWidths.conf }} className="p-1 text-right relative group">
//                               Conf.
//                               <div onMouseDown={(e) => handleMouseDown('urgent', 'conf', e)} onDoubleClick={() => handleDoubleClick('urgent')} className="absolute right-0 top-0 bottom-0 w-1 bg-slate-700/0 group-hover:bg-purple-500/50 cursor-col-resize transition-colors" />
//                             </th>
//                             <th style={{ width: urgentWidths.reason }} className="p-1 pl-2 relative group">
//                               Flag Reason
//                               <div onMouseDown={(e) => handleMouseDown('urgent', 'reason', e)} onDoubleClick={() => handleDoubleClick('urgent')} className="absolute right-0 top-0 bottom-0 w-1 bg-slate-700/0 group-hover:bg-purple-500/50 cursor-col-resize transition-colors" />
//                             </th>
//                           </tr>
//                         </thead>
//                         <tbody className="divide-y divide-slate-800/30">
//                           {urgentCases.map((c, idx) => {
//                             const isSelected = selectedCase?.trade_id === c?.trade_id;
//                             const riskVal = 1 - (Number(c?.compliance_probability) ?? 1.0);
//                             return (
//                               <tr
//                                 key={`${c?.trade_id}-${idx}`}
//                                 onClick={() => handleCaseSelection(c)}
//                                 className={`cursor-pointer text-[11px] transition-colors ${isSelected ? 'bg-rose-950/40 font-semibold border-l-2 border-rose-500 text-rose-200' : 'hover:bg-slate-800/30 text-slate-300'}`}
//                               >
//                                 <td className="p-1 font-mono truncate">{c?.trade_id}</td>
//                                 <td className="p-1 text-right font-mono text-rose-400/90">{riskVal.toFixed(2)}</td>
//                                 <td className="p-1 text-right font-mono text-slate-400">{(Number(c?.confidence_score) || 0).toFixed(2)}</td>
//                                 <td className="p-1 pl-2 truncate text-[10px]">{c?.flag_reason}</td>
//                               </tr>
//                             );
//                           })}
//                         </tbody>
//                       </table>
//                     )}
//                   </div>
//                 </div>

//                 {/* REVIEW QUEUE PANEL */}
//                 <div className="bg-slate-900 border border-slate-800/80 rounded-md p-1.5 flex flex-col min-h-0 h-full overflow-hidden">
//                   <div className="flex items-center gap-1 border-b border-slate-800 pb-0.5 mb-1 flex-shrink-0">
//                     <Clock className="w-3 h-3 text-amber-400" />
//                     <h2 className="text-[10px] font-bold text-amber-400 uppercase tracking-wider">Review</h2>
//                   </div>
                  
//                   <div className="flex-1 overflow-auto min-h-0 relative border border-slate-800/30 rounded dynamic-scroll">
//                     {queuedCases.length === 0 ? (
//                       <p className="text-xs text-slate-500 p-1">Review queue empty.</p>
//                     ) : (
//                       <table className="text-left text-xs border-collapse table-fixed w-max min-w-full">
//                         <thead className="sticky top-0 bg-slate-900 text-slate-400 font-bold uppercase text-[9px] border-b border-slate-800 z-10">
//                           <tr>
//                             <th style={{ width: queuedWidths.tradeId }} className="p-1 relative group">
//                               Trade ID
//                               <div onMouseDown={(e) => handleMouseDown('queued', 'tradeId', e)} onDoubleClick={() => handleDoubleClick('queued')} className="absolute right-0 top-0 bottom-0 w-1 bg-slate-700/0 group-hover:bg-purple-500/50 cursor-col-resize transition-colors" />
//                             </th>
//                             <th style={{ width: queuedWidths.priority }} className="p-1 text-right relative group text-amber-400">
//                               Prio
//                               <div onMouseDown={(e) => handleMouseDown('queued', 'priority', e)} onDoubleClick={() => handleDoubleClick('queued')} className="absolute right-0 top-0 bottom-0 w-1 bg-slate-700/0 group-hover:bg-purple-500/50 cursor-col-resize transition-colors" />
//                             </th>
//                             <th style={{ width: queuedWidths.risk }} className="p-1 text-right relative group">
//                               Risk
//                               <div onMouseDown={(e) => handleMouseDown('queued', 'risk', e)} onDoubleClick={() => handleDoubleClick('queued')} className="absolute right-0 top-0 bottom-0 w-1 bg-slate-700/0 group-hover:bg-purple-500/50 cursor-col-resize transition-colors" />
//                             </th>
//                             <th style={{ width: queuedWidths.conf }} className="p-1 text-right relative group">
//                               Conf.
//                               <div onMouseDown={(e) => handleMouseDown('queued', 'conf', e)} onDoubleClick={() => handleDoubleClick('queued')} className="absolute right-0 top-0 bottom-0 w-1 bg-slate-700/0 group-hover:bg-purple-500/50 cursor-col-resize transition-colors" />
//                             </th>
//                             <th style={{ width: queuedWidths.reason }} className="p-1 pl-2 relative group">
//                               Flag Reason
//                               <div onMouseDown={(e) => handleMouseDown('queued', 'reason', e)} onDoubleClick={() => handleDoubleClick('queued')} className="absolute right-0 top-0 bottom-0 w-1 bg-slate-700/0 group-hover:bg-purple-500/50 cursor-col-resize transition-colors" />
//                             </th>
//                           </tr>
//                         </thead>
//                         <tbody className="divide-y divide-slate-800/30">
//                           {queuedCases.map((c, idx) => {
//                             const isSelected = selectedCase?.trade_id === c?.trade_id;
//                             const riskVal = 1 - (Number(c?.compliance_probability) ?? 1.0);
//                             return (
//                               <tr
//                                 key={`${c?.trade_id}-${idx}`}
//                                 onClick={() => handleCaseSelection(c)}
//                                 className={`cursor-pointer text-[11px] transition-colors ${isSelected ? 'bg-purple-950/40 font-semibold border-l-2 border-purple-500 text-purple-200' : 'hover:bg-slate-800/30 text-slate-300'}`}
//                               >
//                                 <td className="p-1 font-mono truncate">{c?.trade_id}</td>
//                                 <td className="p-1 text-right font-mono font-bold text-amber-400">{c?.priority_score ?? "0"}</td>
//                                 <td className="p-1 text-right font-mono text-rose-400/90">{riskVal.toFixed(2)}</td>
//                                 <td className="p-1 text-right font-mono text-slate-400">{(Number(c?.confidence_score) || 0).toFixed(2)}</td>
//                                 <td className="p-1 pl-2 truncate text-[10px]">{c?.flag_reason}</td>
//                               </tr>
//                             );
//                           })}
//                         </tbody>
//                       </table>
//                     )}
//                   </div>
//                 </div>
//               </div>
//             )}

//             {activeView === "reviewed" && (
//               <div className="bg-slate-900 border border-slate-800 rounded-md p-1.5 flex flex-col min-h-0 h-full overflow-hidden">
//                 <div className="flex items-center gap-1 border-b border-slate-800 pb-0.5 mb-1 flex-shrink-0">
//                   <ArrowUpRight className="w-3 h-3 text-purple-400" />
//                   <h2 className="text-[10px] font-bold text-purple-400 uppercase tracking-wider">Processed Review Logs</h2>
//                 </div>
//                 <div className="flex-1 overflow-auto min-h-0 relative border border-slate-800/30 rounded dynamic-scroll">
//                   {reviewedCases.length === 0 ? (
//                     <p className="text-xs text-slate-500 p-1">No cases reviewed or escalated yet.</p>
//                   ) : (
//                     <table className="text-left text-xs border-collapse table-fixed w-max min-w-full">
//                       <thead className="sticky top-0 bg-slate-900 text-slate-400 font-bold uppercase text-[9px] border-b border-slate-800 z-10">
//                         <tr>
//                           <th style={{ width: tabTablesWidths.tradeId }} className="p-1 relative group">
//                             Trade ID
//                             <div onMouseDown={(e) => handleMouseDown('tabbed', 'tradeId', e)} onDoubleClick={() => handleDoubleClick('tabbed')} className="absolute right-0 top-0 bottom-0 w-1 bg-slate-700/0 group-hover:bg-purple-500/50 cursor-col-resize transition-colors" />
//                           </th>
//                           <th style={{ width: tabTablesWidths.risk }} className="p-1 text-right relative group">
//                             Risk
//                             <div onMouseDown={(e) => handleMouseDown('tabbed', 'risk', e)} onDoubleClick={() => handleDoubleClick('tabbed')} className="absolute right-0 top-0 bottom-0 w-1 bg-slate-700/0 group-hover:bg-purple-500/50 cursor-col-resize transition-colors" />
//                           </th>
//                           <th style={{ width: tabTablesWidths.conf }} className="p-1 text-right relative group">
//                             Conf.
//                             <div onMouseDown={(e) => handleMouseDown('tabbed', 'conf', e)} onDoubleClick={() => handleDoubleClick('tabbed')} className="absolute right-0 top-0 bottom-0 w-1 bg-slate-700/0 group-hover:bg-purple-500/50 cursor-col-resize transition-colors" />
//                           </th>
//                           <th style={{ width: tabTablesWidths.reason }} className="p-1 pl-2 relative group">
//                             Status Signature
//                             <div onMouseDown={(e) => handleMouseDown('tabbed', 'reason', e)} onDoubleClick={() => handleDoubleClick('tabbed')} className="absolute right-0 top-0 bottom-0 w-1 bg-slate-700/0 group-hover:bg-purple-500/50 cursor-col-resize transition-colors" />
//                           </th>
//                         </tr>
//                       </thead>
//                       <tbody className="divide-y divide-slate-800/30">
//                         {reviewedCases.map((c, idx) => {
//                           const isSelected = selectedCase?.trade_id === c?.trade_id;
//                           const auditStatus = caseStates[c?.trade_id]?.reviewStatus;
//                           const riskVal = 1 - (Number(c?.compliance_probability) ?? 1.0);
//                           return (
//                             <tr
//                               key={`${c?.trade_id}-${idx}`}
//                               onClick={() => handleCaseSelection(c)}
//                               className={`cursor-pointer text-[11px] transition-colors ${isSelected ? 'bg-purple-950/40 font-semibold border-l-2 border-purple-500 text-purple-200' : 'hover:bg-slate-800/30 text-slate-300'}`}
//                             >
//                               <td className="p-1 font-mono truncate">{c?.trade_id}</td>
//                               <td className="p-1 text-right font-mono text-slate-400">{riskVal.toFixed(2)}</td>
//                               <td className="p-1 text-right font-mono text-slate-500">{(Number(c?.confidence_score) || 0).toFixed(2)}</td>
//                               <td className="p-1 pl-2 truncate font-semibold uppercase text-[10px]">
//                                 <span className={auditStatus === "Escalated" ? "text-rose-400" : "text-emerald-400"}>
//                                   {auditStatus}
//                                 </span>
//                               </td>
//                             </tr>
//                           );
//                         })}
//                       </tbody>
//                     </table>
//                   )}
//                 </div>
//               </div>
//             )}

//             {activeView === "passed" && (
//               <div className="bg-slate-900 border border-slate-800 rounded-md p-1.5 flex flex-col min-h-0 h-full overflow-hidden">
//                 <div className="flex items-center gap-1 border-b border-slate-800 pb-0.5 mb-1 flex-shrink-0">
//                   <CheckCircle className="w-3 h-3 text-emerald-400" />
//                   <h2 className="text-[10px] font-bold text-emerald-400 uppercase tracking-wider">Auto Passed (Compliant)</h2>
//                 </div>
//                 <div className="flex-1 overflow-auto min-h-0 relative border border-slate-800/30 rounded dynamic-scroll">
//                   {passedCases.length === 0 ? (
//                     <p className="text-xs text-slate-500 p-1">No automatic pass items.</p>
//                   ) : (
//                     <table className="text-left text-xs border-collapse table-fixed w-max min-w-full">
//                       <thead className="sticky top-0 bg-slate-900 text-slate-400 font-bold uppercase text-[9px] border-b border-slate-800 z-10">
//                         <tr>
//                           <th style={{ width: tabTablesWidths.tradeId }} className="p-1 relative group">
//                             Trade ID
//                             <div onMouseDown={(e) => handleMouseDown('tabbed', 'tradeId', e)} onDoubleClick={() => handleDoubleClick('tabbed')} className="absolute right-0 top-0 bottom-0 w-1 bg-slate-700/0 group-hover:bg-purple-500/50 cursor-col-resize transition-colors" />
//                           </th>
//                           <th style={{ width: tabTablesWidths.risk }} className="p-1 text-right relative group">
//                             Risk
//                             <div onMouseDown={(e) => handleMouseDown('tabbed', 'risk', e)} onDoubleClick={() => handleDoubleClick('tabbed')} className="absolute right-0 top-0 bottom-0 w-1 bg-slate-700/0 group-hover:bg-purple-500/50 cursor-col-resize transition-colors" />
//                           </th>
//                           <th style={{ width: tabTablesWidths.conf }} className="p-1 text-right relative group">
//                             Conf.
//                             <div onMouseDown={(e) => handleMouseDown('tabbed', 'conf', e)} onDoubleClick={() => handleDoubleClick('tabbed')} className="absolute right-0 top-0 bottom-0 w-1 bg-slate-700/0 group-hover:bg-purple-500/50 cursor-col-resize transition-colors" />
//                           </th>
//                           <th style={{ width: tabTablesWidths.reason }} className="p-1 pl-2 relative group">
//                             Classification
//                             <div onMouseDown={(e) => handleMouseDown('tabbed', 'reason', e)} onDoubleClick={() => handleDoubleClick('tabbed')} className="absolute right-0 top-0 bottom-0 w-1 bg-slate-700/0 group-hover:bg-purple-500/50 cursor-col-resize transition-colors" />
//                           </th>
//                         </tr>
//                       </thead>
//                       <tbody className="divide-y divide-slate-800/30">
//                         {passedCases.map((c, idx) => {
//                           const isSelected = selectedCase?.trade_id === c?.trade_id;
//                           const riskVal = 1 - (Number(c?.compliance_probability) ?? 1.0);
//                           return (
//                             <tr
//                               key={`${c?.trade_id}-${idx}`}
//                               onClick={() => handleCaseSelection(c)}
//                               className={`cursor-pointer text-[11px] transition-colors ${isSelected ? 'bg-emerald-950/40 font-semibold border-l-2 border-emerald-500 text-emerald-200' : 'hover:bg-slate-800/30 text-slate-300'}`}
//                             >
//                               <td className="p-1 font-mono truncate">{c?.trade_id}</td>
//                               <td className="p-1 text-right font-mono text-emerald-400/90">{riskVal.toFixed(2)}</td>
//                               <td className="p-1 text-right font-mono text-slate-400">{(Number(c?.confidence_score) || 0).toFixed(2)}</td>
//                               <td className="p-1 pl-2 truncate text-[10px] text-emerald-400 font-medium">Auto-Cleared Compliant</td>
//                             </tr>
//                           );
//                         })}
//                       </tbody>
//                     </table>
//                   )}
//                 </div>
//               </div>
//             )}

//           </div>
//         </div>

// {/* RIGHT COMPARTMENT: Re-Architected Non-Overlapping Workspace Section */}
//         <div className="bg-slate-900 border border-slate-800 rounded-md p-2.5 flex flex-col min-h-0 h-full overflow-hidden shadow-2xl">
//           {selectedCase ? (
//             (() => {
//               const currentState = caseStates[selectedCase?.trade_id] || { reviewStatus: "Not reviewed", notes: "" };
//               const isFinalized = currentState.reviewStatus === "Reviewed" || currentState.reviewStatus === "Escalated";
              
//               // Safe number casting fallback
//               const rawProb = selectedCase?.compliance_probability !== undefined ? Number(selectedCase.compliance_probability) : 1;
//               const riskVal = 1 - rawProb;
              
//               const currentRec = currentState.overriddenLabel || selectedCase?.compliance_label || "Compliant";
//               const isRecCompliant = currentRec.toLowerCase().includes("compliant");
              
//               return (
//                 <div className="flex flex-col h-full justify-between min-h-0 overflow-hidden">
                  
//                   {/* Title & Top Summary Badges Line */}
//                   <div className="flex items-center justify-between border-b border-slate-800 pb-1.5 flex-shrink-0">
//                     <div className="flex flex-col gap-0.5">
//                       <div className="flex items-center gap-1.5">
//                         <span className="text-[9px] font-black uppercase tracking-wider text-purple-400 bg-purple-950/30 px-1.5 py-0.5 rounded border border-purple-900/40">
//                           Audit Space
//                         </span>
//                         <span className="text-xs font-mono font-bold text-slate-100">{selectedCase?.trade_id || "—"}</span>
//                       </div>
//                       <div>
//                         <span className={`px-1.5 py-0.2 rounded text-[8px] font-bold tracking-wide border ${
//                           currentState.reviewStatus === "Reviewed"
//                             ? "bg-emerald-950/40 text-emerald-400 border-emerald-800/40" 
//                             : currentState.reviewStatus === "Escalated"
//                             ? "bg-rose-950/40 text-rose-400 border-rose-800/40"
//                             : "bg-slate-950 text-amber-400 border-amber-900/40"
//                         }`}>
//                           {currentState.reviewStatus ? currentState.reviewStatus.toUpperCase() : "NOT REVIEWED"}
//                         </span>
//                       </div>
//                     </div>
                    
//                     {/* Horizontal Meta Scores Banner */}
//                     <div className="flex items-center gap-x-2 bg-slate-950/80 px-2 py-1 rounded border border-slate-800/60 text-[10px]">
//                       <div className="flex items-center gap-1">
//                         <span className="text-slate-500 font-medium text-[8px] uppercase">AI Rec:</span>
//                         <span className={`font-bold tracking-tight px-1 rounded text-[9px] ${
//                           isRecCompliant ? "bg-emerald-950/50 text-emerald-400" : "bg-rose-950/50 text-rose-400"
//                         }`}>
//                           {isRecCompliant ? "Compliant" : "Non-compliant"}
//                         </span>
//                       </div>
//                       <div className="border-l border-slate-800 h-3" />
//                       <div>
//                         <span className="text-slate-500 font-medium text-[8px] uppercase mr-0.5">Risk:</span>
//                         <span className="font-mono font-bold text-rose-400">{isNaN(riskVal) ? "0.000" : riskVal.toFixed(3)}</span>
//                       </div>
//                       <div className="border-l border-slate-800 h-3" />
//                       <div>
//                         <span className="text-slate-500 font-medium text-[8px] uppercase mr-0.5">Conf:</span>
//                         <span className="font-mono font-bold text-sky-400">{selectedCase?.confidence_score !== undefined ? Number(selectedCase.confidence_score).toFixed(3) : "1.000"}</span>
//                       </div>
//                       <div className="border-l border-slate-800 h-3" />
//                       <div>
//                         <span className="text-slate-500 font-medium text-[8px] uppercase mr-0.5">Prio:</span>
//                         <span className="font-mono font-bold text-amber-400">{selectedCase?.priority_score ?? "0"}</span>
//                       </div>
//                     </div>
//                   </div>

//                   {/* STRUCTURAL WORKSPACE WRAPPER */}
//                   <div className="flex-1 flex flex-col gap-1.5 justify-start min-h-0 pt-1.5 overflow-hidden">
                    
//                     {/* LAYOUT LAYER 1: Full-Width Trade Fields */}
//                     <div className="bg-slate-950/20 border border-slate-800/40 p-1.5 rounded flex-shrink-0">
//                       <div className="flex items-center gap-1 border-b border-slate-800/60 pb-0.5 mb-1">
//                         <Briefcase className="w-3 h-3 text-purple-400" />
//                         <h4 className="text-[9px] font-bold text-purple-400 uppercase tracking-wider">Trade Fields</h4>
//                       </div>
//                       <div className="text-[11px] grid grid-cols-3 gap-2 text-slate-300">
//                         <div>
//                           <div className="text-slate-500 text-[8px] uppercase font-semibold">Investment Type</div>
//                           <div className="font-medium truncate">{selectedCase?.investment_type || selectedCase?.asset_class || "N/A"}</div>
//                         </div>
//                         <div>
//                           <div className="text-slate-500 text-[8px] uppercase font-semibold">Investment Amount</div>
//                           <div className="font-mono font-bold text-emerald-400">
//                             {selectedCase?.investment_amount ? `$${Number(selectedCase.investment_amount).toLocaleString(undefined, {minimumFractionDigits: 2})}` : "N/A"}
//                           </div>
//                         </div>
//                         <div>
//                           <div className="text-slate-500 text-[8px] uppercase font-semibold">Execution Timestamp</div>
//                           <div className="font-mono truncate text-slate-400">{selectedCase?.timestamp || "N/A"}</div>
//                         </div>
//                       </div>
//                     </div>

//                     {/* LAYOUT LAYER 2: Side-by-Side Dual Column Mix */}
//                     <div className="grid grid-cols-2 gap-1.5 flex-shrink-0">
                      
//                       {/* Column A: Client Profile */}
//                       <div className="bg-slate-950/20 border border-slate-800/40 p-1.5 rounded">
//                         <div className="flex items-center gap-1 border-b border-slate-800/60 pb-0.5 mb-1">
//                           <User className="w-3 h-3 text-sky-400" />
//                           <h4 className="text-[9px] font-bold text-sky-400 uppercase tracking-wider">Client Profile</h4>
//                         </div>
//                         <div className="text-[11px] space-y-1 text-slate-300">
//                           <div className="grid grid-cols-2 gap-1.5">
//                             <div>
//                               <div className="text-slate-500 text-[8px] uppercase font-semibold">Age</div>
//                               <div className="font-mono text-xs">{selectedCase?.client_age ?? "—"}</div>
//                             </div>
//                             <div>
//                               <div className="text-slate-500 text-[8px] uppercase font-semibold">Annual Income</div>
//                               <div className="font-mono truncate text-xs">{selectedCase?.client_income ? `$${Number(selectedCase.client_income).toLocaleString()}` : "—"}</div>
//                             </div>
//                           </div>
//                           <div className="grid grid-cols-2 gap-1.5 pt-0.5 border-t border-slate-800/30">
//                             <div>
//                               <div className="text-slate-500 text-[8px] uppercase font-semibold">Risk Tolerance</div>
//                               <div className="truncate text-[10px]">{selectedCase?.risk_tolerance || selectedCase?.client_risk_tolerance || "—"}</div>
//                             </div>
//                             <div>
//                               <div className="text-slate-500 text-[8px] uppercase font-semibold">Experience</div>
//                               <div className="truncate text-[10px]">{selectedCase?.investment_experience || "—"}</div>
//                             </div>
//                           </div>
//                           <div className="pt-0.5 border-t border-slate-800/30">
//                             <div className="text-slate-500 text-[8px] uppercase font-semibold">Objective & Horizon</div>
//                             <div className="text-[10px] leading-tight text-slate-400 truncate">
//                               {selectedCase?.investment_objective || "—"} {selectedCase?.investment_time_horizon ? `(${selectedCase.investment_time_horizon})` : ""}
//                             </div>
//                           </div>
//                         </div>
//                       </div>

//                       {/* Column B: Advisor Records */}
//                       <div className="bg-slate-950/20 border border-slate-800/40 p-1.5 rounded">
//                         <div className="flex items-center gap-1 border-b border-slate-800/60 pb-0.5 mb-1">
//                           <FileText className="w-3 h-3 text-amber-400" />
//                           <h4 className="text-[9px] font-bold text-amber-400 uppercase tracking-wider">Advisor Records</h4>
//                         </div>
//                         <div className="text-[11px] space-y-1 text-slate-300">
//                           <div className="grid grid-cols-2 gap-1.5 text-[10px]">
//                             <div>
//                               <span className="text-slate-500 block text-[8px] uppercase font-semibold">Advisor ID</span>
//                               <span className="font-mono font-medium truncate block">{selectedCase?.advisor_id || "—"}</span>
//                             </div>
//                             <div>
//                               <span className="text-slate-500 block text-[8px] uppercase font-semibold">Tenure Rate</span>
//                               <span className="truncate block text-[10px]">{selectedCase?.advisor_experience || "—"}</span>
//                             </div>
//                           </div>
//                           <div className="grid grid-cols-2 gap-1.5 pt-0.5 border-t border-slate-800/50 items-center">
//                             <div>
//                               <span className="text-slate-500 block text-[8px] uppercase font-semibold">History Risk</span>
//                               <span className="font-mono text-rose-400 text-xs">{selectedCase?.advisor_history_risk ?? "0.00"}</span>
//                             </div>
//                             <div>
//                               <span className="text-slate-500 block text-[8px] uppercase font-semibold">Rationale</span>
//                               <span className={`inline-block px-1 rounded text-[8px] font-bold ${
//                                 selectedCase?.has_rationale === true || selectedCase?.has_rationale === "true"
//                                   ? "bg-emerald-950 text-emerald-400 border border-emerald-800/50" 
//                                   : "bg-slate-950 text-slate-500 border border-slate-800"
//                               }`}>
//                                 {selectedCase?.has_rationale ? "FILED" : "STANDARD"}
//                               </span>
//                             </div>
//                           </div>
//                           <div className="pt-0.5 border-t border-slate-800/50">
//                             <span className="text-slate-500 block text-[8px] uppercase font-semibold mb-0.5">Desk Notes Context</span>
//                             <p className="text-[10px] text-slate-400 leading-none truncate">
//                               {selectedCase?.advisor_notes || "No transactional exceptions noted on account initialization."}
//                             </p>
//                           </div>
//                         </div>
//                       </div>

//                     </div>

//                     {/* LAYOUT LAYER 3: Expanded Full-Width Exception Breakdown Banner */}
//                     <div className="bg-slate-950/20 border border-slate-800/40 p-1.5 rounded flex-1 flex flex-col min-h-0">
//                       <div className="flex items-center gap-1 border-b border-slate-800/60 pb-0.5 mb-1 flex-shrink-0">
//                         <HelpCircle className="w-3 h-3 text-rose-400" />
//                         <h4 className="text-[9px] font-bold text-rose-400 uppercase tracking-wider">Exception Breakdown</h4>
//                       </div>
//                       <div className="text-[11px] text-slate-300 flex-1 overflow-y-auto dynamic-scroll">
//                         <div className="text-slate-500 text-[8px] uppercase font-semibold mb-0.5">Flag Reason Details</div>
//                         <p className="text-[11px] leading-relaxed text-slate-300 font-medium">
//                           {selectedCase?.flag_reason || "No structural deviations or algorithmic rule violations flagged for this transaction pattern. File satisfies compliance parameters."}
//                         </p>
//                       </div>
//                     </div>

//                   </div>

//                   {/* Policy Box (Placed immediately below Exception Breakdown) */}
//                   <div className="bg-slate-950/40 border border-slate-800/50 p-2 rounded flex-shrink-0 my-1">
//                     <div className="text-[8px] font-black text-slate-500 uppercase tracking-wider mb-1">
//                       Retrieved Regulatory & Firm Policies:
//                     </div>
//                     <div className="flex flex-wrap gap-1 items-center max-h-[36px] overflow-y-auto dynamic-scroll">
//                       {renderPolicies(selectedCase?.retrieved_policies)}
//                     </div>
//                   </div>

//                   {/* Sign-off Form Area */}
//                   <div className="border-t border-slate-800/80 pt-1.5 flex flex-col gap-1.5 flex-shrink-0">
//                     <div className="flex flex-col">
//                       <label className="text-[9px] font-black text-slate-400 uppercase tracking-widest mb-0.5">
//                         Reviewer Sign-off Notes
//                       </label>
//                       <input
//                         type="text"
//                         value={currentNotes}
//                         disabled={isFinalized}
//                         onChange={(e) => handleNotesChange(e.target.value)}
//                         placeholder={isFinalized ? "Audit history signature locked." : "Enter compliance justification or structural risk override arguments..."}
//                         className="w-full bg-slate-950 border border-slate-800 rounded px-2.5 py-1 text-xs text-slate-200 focus:outline-none focus:border-purple-500/80 disabled:opacity-40 transition-colors placeholder:text-slate-600 font-medium"
//                       />
//                     </div>
                    
//                     {/* Action Buttons Row */}
//                     <div className="flex gap-2 justify-end">
//                       <button
//                         onClick={handleApproveAI}
//                         disabled={isFinalized}
//                         className="bg-emerald-600 hover:bg-emerald-500 disabled:bg-slate-800 disabled:text-slate-500 text-slate-950 font-black text-[11px] px-3 py-1 rounded transition-colors uppercase tracking-wider whitespace-nowrap"
//                       >
//                         Approve AI
//                       </button>
//                       <button
//                         onClick={handleOverrideAI}
//                         disabled={isFinalized}
//                         className="bg-purple-600 hover:bg-purple-500 disabled:bg-slate-800 disabled:text-slate-500 text-slate-100 font-black text-[11px] px-3 py-1 rounded transition-colors uppercase tracking-wider whitespace-nowrap"
//                       >
//                         Override AI
//                       </button>
//                       <button
//                         onClick={handleEscalate}
//                         disabled={isFinalized}
//                         className="bg-rose-600 hover:bg-rose-500 disabled:bg-slate-800 disabled:text-slate-500 text-slate-100 font-black text-[11px] px-3 py-1 rounded transition-colors uppercase tracking-wider whitespace-nowrap"
//                       >
//                         Escalate
//                       </button>
//                     </div>
//                   </div>

//                 </div>
//               );
//             })()
//           ) : (
//             <div className="h-full flex items-center justify-center text-slate-500 text-xs font-semibold border border-dashed border-slate-800 rounded">
//               Select a risk transaction case row from the active lists to mount details in the workspace.
//             </div>
//           )}
//         </div>
//       </div>
//     </div>
//   );
// }

// export default Dashboard;

// /* VERSION 11 */

// import { useEffect, useState, useRef } from "react";
// import { getCases } from "../api/cases";
// import { AlertCircle, CheckCircle, Clock, ShieldAlert, FileText, User, Briefcase, HelpCircle, ArrowUpRight } from "lucide-react";

// interface CaseAuditState {
//   reviewStatus: "Reviewed" | "Not reviewed" | "Escalated";
//   notes: string;
//   overriddenLabel?: string; // Tracks live modifications to the AI recommendation
// }

// function Dashboard() {
//   const [activeView, setActiveView] = useState<
//     "active" | "reviewed" | "passed"
//   >("active");

//   const [cases, setCases] = useState<any[]>([]);
//   const [selectedCase, setSelectedCase] = useState<any | null>(null);
  
//   // Per-case persistence engine keyed by trade_id
//   const [caseStates, setCaseStates] = useState<Record<string, CaseAuditState>>({});
//   const [currentNotes, setCurrentNotes] = useState<string>("");

//   // --- Spreadsheet Column Resize State ---
//   const [urgentWidths, setUrgentWidths] = useState({ tradeId: 90, risk: 65, conf: 65, reason: 180 });
//   const [queuedWidths, setQueuedWidths] = useState({ tradeId: 90, priority: 60, risk: 65, conf: 65, reason: 160 });

//   const dragInfo = useRef<{ table: 'urgent' | 'queued'; col: string; startX: number; startWidth: number } | null>(null);

//   useEffect(() => {
//     getCases()
//       .then((data) => {
//         if (Array.isArray(data)) {
//           setCases(data);
          
//           // Seed initial default auditing structures for all fetched trades
//           const initialStates: Record<string, CaseAuditState> = {};
//           data.forEach((c) => {
//             if (c?.trade_id) {
//               initialStates[c.trade_id] = { 
//                 reviewStatus: "Not reviewed", 
//                 notes: "",
//                 overriddenLabel: c.compliance_label || "Non-compliant"
//               };
//             }
//           });
//           setCaseStates(initialStates);

//           const urgentCases = data.filter((c) => c?.escalation_level === "urgent");
//           const queuedCases = data
//             .filter((c) => c?.escalation_level === "priority" || c?.escalation_level === "queue")
//             .sort((a, b) => (Number(b?.priority_score) || 0) - (Number(a?.priority_score) || 0));

//           if (urgentCases.length > 0) handleCaseSelection(urgentCases[0], initialStates);
//           else if (queuedCases.length > 0) handleCaseSelection(queuedCases[0], initialStates);
//         }
//       })
//       .catch((err) => console.error("API Fetch Error:", err));
//   }, []);

//   const handleCaseSelection = (targetCase: any, latestStates = caseStates) => {
//     setSelectedCase(targetCase);
//     if (targetCase?.trade_id) {
//       const savedState = latestStates[targetCase.trade_id];
//       setCurrentNotes(savedState ? savedState.notes : "");
//     }
//   };

//   const handleNotesChange = (text: string) => {
//     setCurrentNotes(text);
//     if (selectedCase?.trade_id) {
//       setCaseStates(prev => ({
//         ...prev,
//         [selectedCase.trade_id]: {
//           ...prev[selectedCase.trade_id],
//           notes: text
//         }
//       }));
//     }
//   };

//   // --- Audit State Updaters ---
//   const handleApproveAI = () => {
//     if (!selectedCase?.trade_id) return;
//     setCaseStates(prev => ({
//       ...prev,
//       [selectedCase.trade_id]: {
//         ...prev[selectedCase.trade_id],
//         reviewStatus: "Reviewed",
//         notes: currentNotes
//       }
//     }));
//   };

//   const handleOverrideAI = () => {
//     if (!selectedCase?.trade_id) return;
//     setCaseStates(prev => {
//       const currentLabel = prev[selectedCase.trade_id]?.overriddenLabel || selectedCase.compliance_label || "Non-compliant";
//       const flippedLabel = currentLabel.toLowerCase().includes("non") ? "Compliant" : "Non-compliant";
      
//       return {
//         ...prev,
//         [selectedCase.trade_id]: {
//           ...prev[selectedCase.trade_id],
//           reviewStatus: "Reviewed",
//           overriddenLabel: flippedLabel,
//           notes: currentNotes
//         }
//       };
//     });
//   };

//   const handleEscalate = () => {
//     if (!selectedCase?.trade_id) return;
//     setCaseStates(prev => ({
//       ...prev,
//       [selectedCase.trade_id]: {
//         ...prev[selectedCase.trade_id],
//         reviewStatus: "Escalated",
//         notes: currentNotes
//       }
//     }));
//   };

//   // --- Mouse Resize Handlers ---
//   const handleMouseDown = (table: 'urgent' | 'queued', col: string, e: React.MouseEvent) => {
//     e.preventDefault();
//     const currentWidths = table === 'urgent' ? urgentWidths : queuedWidths;
//     dragInfo.current = {
//       table,
//       col,
//       startX: e.clientX,
//       startWidth: (currentWidths as any)[col]
//     };
//     document.addEventListener("mousemove", handleMouseMove);
//     document.addEventListener("mouseup", handleMouseUp);
//   };

//   const handleMouseMove = (e: MouseEvent) => {
//     if (!dragInfo.current) return;
//     const { table, col, startX, startWidth } = dragInfo.current;
//     const deltaX = e.clientX - startX;
//     const newWidth = Math.max(50, startWidth + deltaX);

//     if (table === 'urgent') {
//       setUrgentWidths(prev => ({ ...prev, [col]: newWidth }));
//     } else {
//       setQueuedWidths(prev => ({ ...prev, [col]: newWidth }));
//     }
//   };

//   const handleMouseUp = () => {
//     dragInfo.current = null;
//     document.removeEventListener("mousemove", handleMouseMove);
//     document.removeEventListener("mouseup", handleMouseUp);
//   };

//   const handleDoubleClick = (table: 'urgent' | 'queued') => {
//     if (table === 'urgent') {
//       setUrgentWidths({ tradeId: 90, risk: 65, conf: 65, reason: 180 });
//     } else {
//       setQueuedWidths({ tradeId: 90, priority: 60, risk: 65, conf: 65, reason: 160 });
//     }
//   };

//   const urgentCases = cases.filter((c) => c?.escalation_level === "urgent");
//   const queuedCases = cases
//     .filter((c) => c?.escalation_level === "priority" || c?.escalation_level === "queue")
//     .sort((a, b) => (Number(b?.priority_score) || 0) - (Number(a?.priority_score) || 0));

//   const countUrgent = urgentCases.length;
//   const countReview = queuedCases.length;
//   const countEscalated = Object.values(caseStates).filter((s) => s.reviewStatus === "Escalated").length;
//   const countPassed = cases.filter(
//     (c) => c?.escalation_level !== "urgent" && c?.escalation_level !== "priority" && c?.escalation_level !== "queue"
//   ).length;

//   const renderPolicies = (policies: any) => {
//     if (!policies) return <span className="text-[10px] text-slate-500">No policies attached.</span>;
//     let items: string[] = [];
//     if (Array.isArray(policies)) items = policies;
//     else if (typeof policies === "string" && policies.startsWith("[")) {
//       items = policies.replace(/[\[\]']/g, "").split(",").map((p) => p.trim()).filter(Boolean);
//     } else if (typeof policies === "string" && policies.trim().length > 0) {
//       items = policies.split(",").map((p) => p.trim());
//     }
    
//     if (items.length === 0) return <span className="text-[10px] text-slate-500">No policies attached.</span>;
//     return items.map((policy, i) => (
//       <span key={i} className="px-1.5 py-0.5 bg-slate-950 text-[10px] rounded border border-slate-800 text-purple-300 font-mono truncate max-w-[220px]">
//         {policy}
//       </span>
//     ));
//   };

//   return (
//     <div className="p-1 h-screen bg-slate-950 text-slate-100 flex flex-col gap-1 overflow-hidden select-none">
      
//       <style>{`
//         .dynamic-scroll { scrollbar-width: none; }
//         .dynamic-scroll::-webkit-scrollbar { width: 4px; height: 4px; display: none; }
//         .dynamic-scroll:hover { scrollbar-width: thin; }
//         .dynamic-scroll:hover::-webkit-scrollbar { display: block; }
//         .dynamic-scroll::-webkit-scrollbar-track { background: transparent; }
//         .dynamic-scroll::-webkit-scrollbar-thumb { background: rgba(148, 163, 184, 0.15); border-radius: 2px; }
//       `}</style>
      
//       {/* Top Header Metrics Layer */}
//       <div className="flex items-center justify-between border-b border-slate-900 pb-1 flex-shrink-0">
//         <h1 className="text-sm font-bold tracking-tight text-slate-200">
//           AI Compliance Review Copilot
//         </h1>
        
//         <div className="flex items-center gap-2">
//           <div className="bg-rose-950/30 border border-rose-500/30 rounded px-2 py-0.5 flex items-center gap-1.5 text-[11px] font-medium shadow-sm">
//             <AlertCircle className="w-3 h-3 text-rose-400" />
//             <span className="text-rose-300">Urgent:</span>
//             <span className="text-xs font-black text-rose-100">{countUrgent}</span>
//           </div>

//           <div className="bg-amber-950/30 border border-amber-500/30 rounded px-2 py-0.5 flex items-center gap-1.5 text-[11px] font-medium shadow-sm">
//             <Clock className="w-3 h-3 text-amber-400" />
//             <span className="text-amber-300">Review:</span>
//             <span className="text-xs font-black text-amber-100">{countReview}</span>
//           </div>

//           <div className="bg-purple-950/30 border border-purple-500/30 rounded px-2 py-0.5 flex items-center gap-1.5 text-[11px] font-medium shadow-sm">
//             <ArrowUpRight className="w-3 h-3 text-purple-400" />
//             <span className="text-purple-300">Escalated:</span>
//             <span className="text-xs font-black text-purple-100">{countEscalated}</span>
//           </div>

//           <div className="bg-emerald-950/30 border border-emerald-500/30 rounded px-2 py-0.5 flex items-center gap-1.5 text-[11px] font-medium shadow-sm">
//             <CheckCircle className="w-3 h-3 text-emerald-400" />
//             <span className="text-emerald-300">Passed:</span>
//             <span className="text-xs font-black text-emerald-100">{countPassed}</span>
//           </div>
//         </div>
//       </div>

//       {/* Main Left/Right Side-by-Side Split Grid */}
//       <div className="flex-1 grid grid-cols-[38fr_62fr] gap-1.5 min-h-0 h-full overflow-hidden">
        
//         {/* LEFT PANE: Vertically Stacked Action Lists */}
//         <div className="grid grid-rows-2 gap-1.5 min-h-0 h-full overflow-hidden">
          
//           {/* URGENT TRACK PANEL */}
//           <div className="bg-slate-900 border border-rose-500/10 rounded-md p-1.5 flex flex-col min-h-0 h-full overflow-hidden">
//             <div className="flex items-center gap-1 border-b border-slate-800 pb-0.5 mb-1 flex-shrink-0">
//               <ShieldAlert className="w-3 h-3 text-rose-400" />
//               <h2 className="text-[10px] font-bold text-rose-400 uppercase tracking-wider">Urgent Action Required</h2>
//             </div>
            
//             <div className="flex-1 overflow-auto min-h-0 relative border border-slate-800/30 rounded dynamic-scroll">
//               {urgentCases.length === 0 ? (
//                 <p className="text-xs text-slate-500 p-1">No urgent cases outstanding.</p>
//               ) : (
//                 <table className="text-left text-xs border-collapse table-fixed w-max min-w-full">
//                   <thead className="sticky top-0 bg-slate-900 text-slate-400 font-bold uppercase text-[9px] border-b border-slate-800 z-10">
//                     <tr>
//                       <th style={{ width: urgentWidths.tradeId }} className="p-1 relative group">
//                         Trade ID
//                         <div onMouseDown={(e) => handleMouseDown('urgent', 'tradeId', e)} onDoubleClick={() => handleDoubleClick('urgent')} className="absolute right-0 top-0 bottom-0 w-1 bg-slate-700/0 group-hover:bg-purple-500/50 cursor-col-resize transition-colors" />
//                       </th>
//                       <th style={{ width: urgentWidths.risk }} className="p-1 text-right relative group">
//                         Risk
//                         <div onMouseDown={(e) => handleMouseDown('urgent', 'risk', e)} onDoubleClick={() => handleDoubleClick('urgent')} className="absolute right-0 top-0 bottom-0 w-1 bg-slate-700/0 group-hover:bg-purple-500/50 cursor-col-resize transition-colors" />
//                       </th>
//                       <th style={{ width: urgentWidths.conf }} className="p-1 text-right relative group">
//                         Conf.
//                         <div onMouseDown={(e) => handleMouseDown('urgent', 'conf', e)} onDoubleClick={() => handleDoubleClick('urgent')} className="absolute right-0 top-0 bottom-0 w-1 bg-slate-700/0 group-hover:bg-purple-500/50 cursor-col-resize transition-colors" />
//                       </th>
//                       <th style={{ width: urgentWidths.reason }} className="p-1 pl-2 relative group">
//                         Flag Reason
//                         <div onMouseDown={(e) => handleMouseDown('urgent', 'reason', e)} onDoubleClick={() => handleDoubleClick('urgent')} className="absolute right-0 top-0 bottom-0 w-1 bg-slate-700/0 group-hover:bg-purple-500/50 cursor-col-resize transition-colors" />
//                       </th>
//                     </tr>
//                   </thead>
//                   <tbody className="divide-y divide-slate-800/30">
//                     {urgentCases.map((c, idx) => {
//                       const isSelected = selectedCase?.trade_id === c?.trade_id;
//                       const riskVal = 1 - (Number(c?.compliance_probability) ?? 1.0);
//                       return (
//                         <tr
//                           key={`${c?.trade_id}-${idx}`}
//                           onClick={() => handleCaseSelection(c)}
//                           className={`cursor-pointer text-[11px] transition-colors ${isSelected ? 'bg-rose-950/40 font-semibold border-l-2 border-rose-500 text-rose-200' : 'hover:bg-slate-800/30 text-slate-300'}`}
//                         >
//                           <td className="p-1 font-mono truncate">{c?.trade_id}</td>
//                           <td className="p-1 text-right font-mono text-rose-400/90">{riskVal.toFixed(2)}</td>
//                           <td className="p-1 text-right font-mono text-slate-400">{(Number(c?.confidence_score) || 0).toFixed(2)}</td>
//                           <td className="p-1 pl-2 truncate text-[10px]">{c?.flag_reason}</td>
//                         </tr>
//                       );
//                     })}
//                   </tbody>
//                 </table>
//               )}
//             </div>
//           </div>

//           {/* REVIEW QUEUE PANEL */}
//           <div className="bg-slate-900 border border-slate-800/80 rounded-md p-1.5 flex flex-col min-h-0 h-full overflow-hidden">
//             <div className="flex items-center gap-1 border-b border-slate-800 pb-0.5 mb-1 flex-shrink-0">
//               <Clock className="w-3 h-3 text-amber-400" />
//               <h2 className="text-[10px] font-bold text-amber-400 uppercase tracking-wider">Review</h2>
//             </div>
            
//             <div className="flex-1 overflow-auto min-h-0 relative border border-slate-800/30 rounded dynamic-scroll">
//               {queuedCases.length === 0 ? (
//                 <p className="text-xs text-slate-500 p-1">Review queue empty.</p>
//               ) : (
//                 <table className="text-left text-xs border-collapse table-fixed w-max min-w-full">
//                   <thead className="sticky top-0 bg-slate-900 text-slate-400 font-bold uppercase text-[9px] border-b border-slate-800 z-10">
//                     <tr>
//                       <th style={{ width: queuedWidths.tradeId }} className="p-1 relative group">
//                         Trade ID
//                         <div onMouseDown={(e) => handleMouseDown('queued', 'tradeId', e)} onDoubleClick={() => handleDoubleClick('queued')} className="absolute right-0 top-0 bottom-0 w-1 bg-slate-700/0 group-hover:bg-purple-500/50 cursor-col-resize transition-colors" />
//                       </th>
//                       <th style={{ width: queuedWidths.priority }} className="p-1 text-right relative group text-amber-400">
//                         Prio
//                         <div onMouseDown={(e) => handleMouseDown('queued', 'priority', e)} onDoubleClick={() => handleDoubleClick('queued')} className="absolute right-0 top-0 bottom-0 w-1 bg-slate-700/0 group-hover:bg-purple-500/50 cursor-col-resize transition-colors" />
//                       </th>
//                       <th style={{ width: queuedWidths.risk }} className="p-1 text-right relative group">
//                         Risk
//                         <div onMouseDown={(e) => handleMouseDown('queued', 'risk', e)} onDoubleClick={() => handleDoubleClick('queued')} className="absolute right-0 top-0 bottom-0 w-1 bg-slate-700/0 group-hover:bg-purple-500/50 cursor-col-resize transition-colors" />
//                       </th>
//                       <th style={{ width: queuedWidths.conf }} className="p-1 text-right relative group">
//                         Conf.
//                         <div onMouseDown={(e) => handleMouseDown('queued', 'conf', e)} onDoubleClick={() => handleDoubleClick('queued')} className="absolute right-0 top-0 bottom-0 w-1 bg-slate-700/0 group-hover:bg-purple-500/50 cursor-col-resize transition-colors" />
//                       </th>
//                       <th style={{ width: queuedWidths.reason }} className="p-1 pl-2 relative group">
//                         Flag Reason
//                         <div onMouseDown={(e) => handleMouseDown('queued', 'reason', e)} onDoubleClick={() => handleDoubleClick('queued')} className="absolute right-0 top-0 bottom-0 w-1 bg-slate-700/0 group-hover:bg-purple-500/50 cursor-col-resize transition-colors" />
//                       </th>
//                     </tr>
//                   </thead>
//                   <tbody className="divide-y divide-slate-800/30">
//                     {queuedCases.map((c, idx) => {
//                       const isSelected = selectedCase?.trade_id === c?.trade_id;
//                       const riskVal = 1 - (Number(c?.compliance_probability) ?? 1.0);
//                       return (
//                         <tr
//                           key={`${c?.trade_id}-${idx}`}
//                           onClick={() => handleCaseSelection(c)}
//                           className={`cursor-pointer text-[11px] transition-colors ${isSelected ? 'bg-purple-950/40 font-semibold border-l-2 border-purple-500 text-purple-200' : 'hover:bg-slate-800/30 text-slate-300'}`}
//                         >
//                           <td className="p-1 font-mono truncate">{c?.trade_id}</td>
//                           <td className="p-1 text-right font-mono font-bold text-amber-400">{c?.priority_score ?? "0"}</td>
//                           <td className="p-1 text-right font-mono text-rose-400/90">{riskVal.toFixed(2)}</td>
//                           <td className="p-1 text-right font-mono text-slate-400">{(Number(c?.confidence_score) || 0).toFixed(2)}</td>
//                           <td className="p-1 pl-2 truncate text-[10px]">{c?.flag_reason}</td>
//                         </tr>
//                       );
//                     })}
//                   </tbody>
//                 </table>
//               )}
//             </div>
//           </div>

//         </div>

//         {/* RIGHT PANE: Ultra-Spacious Selected Case Audit Section */}
//         <div className="bg-slate-900 border border-slate-800 rounded-md p-2.5 flex flex-col min-h-0 h-full overflow-hidden shadow-2xl">
//           {selectedCase ? (
//             (() => {
//               const currentState = caseStates[selectedCase.trade_id] || { reviewStatus: "Not reviewed", notes: "" };
//               const isFinalized = currentState.reviewStatus === "Reviewed" || currentState.reviewStatus === "Escalated";
//               const riskVal = 1 - (Number(selectedCase.compliance_probability) || 0);
              
//               const currentRec = currentState.overriddenLabel || selectedCase.compliance_label || "Non-compliant";
//               const isRecCompliant = currentRec.toLowerCase() === "compliant";
              
//               return (
//                 <div className="flex flex-col h-full gap-2 min-h-0 overflow-hidden">
                  
//                   {/* Title & Micro Scores Strip */}
//                   <div className="flex items-center justify-between border-b border-slate-800 pb-1.5 flex-shrink-0">
//                     <div className="flex flex-col gap-0.5">
//                       <div className="flex items-center gap-1.5">
//                         <span className="text-[9px] font-black uppercase tracking-wider text-purple-400 bg-purple-950/30 px-1.5 py-0.5 rounded border border-purple-900/40">
//                           Audit Space
//                         </span>
//                         <span className="text-xs font-mono font-bold text-slate-100">{selectedCase.trade_id}</span>
//                       </div>
//                       <div>
//                         <span className={`px-1.5 py-0.2 rounded text-[8px] font-bold tracking-wide border ${
//                           currentState.reviewStatus === "Reviewed"
//                             ? "bg-emerald-950/40 text-emerald-400 border-emerald-800/40" 
//                             : currentState.reviewStatus === "Escalated"
//                             ? "bg-rose-950/40 text-rose-400 border-rose-800/40"
//                             : "bg-slate-950 text-amber-400 border-amber-900/40"
//                         }`}>
//                           {currentState.reviewStatus.toUpperCase()}
//                         </span>
//                       </div>
//                     </div>
                    
//                     {/* Scores Metrics Badge */}
//                     <div className="flex flex-wrap items-center gap-x-2 gap-y-1 bg-slate-950/80 px-2 py-1 rounded border border-slate-800/60 text-[10px]">
//                       <div className="flex items-center gap-1">
//                         <span className="text-slate-500 font-medium text-[8px] uppercase">AI Rec:</span>
//                         <span className={`font-bold tracking-tight px-1 rounded text-[9px] ${
//                           isRecCompliant ? "bg-emerald-950/50 text-emerald-400" : "bg-rose-950/50 text-rose-400"
//                         }`}>
//                           {isRecCompliant ? "Compliant" : "Non-compliant"}
//                         </span>
//                       </div>
//                       <div className="border-l border-slate-800 h-3" />
//                       <div>
//                         <span className="text-slate-500 font-medium text-[8px] uppercase mr-0.5">Risk:</span>
//                         <span className="font-mono font-bold text-rose-400">{riskVal.toFixed(3)}</span>
//                       </div>
//                       <div className="border-l border-slate-800 h-3" />
//                       <div>
//                         <span className="text-slate-500 font-medium text-[8px] uppercase mr-0.5">Conf:</span>
//                         <span className="font-mono font-bold text-sky-400">{Number(selectedCase.confidence_score || 0).toFixed(3)}</span>
//                       </div>
//                       <div className="border-l border-slate-800 h-3" />
//                       <div>
//                         <span className="text-slate-500 font-medium text-[8px] uppercase mr-0.5">Prio:</span>
//                         <span className="font-mono font-bold text-amber-400">{selectedCase.priority_score ?? "—"}</span>
//                       </div>
//                     </div>
//                   </div>

//                   {/* 2x2 Clean-Density Matrix Workspace */}
//                   <div className="grid grid-cols-2 gap-2 flex-1 min-h-0 overflow-y-auto dynamic-scroll pr-0.5 py-0.5">
                    
//                     {/* SECTION 1: Trade Fields */}
//                     <div className="bg-slate-950/20 border border-slate-800/40 p-2 rounded flex flex-col min-h-0 h-fit">
//                       <div className="flex items-center gap-1 border-b border-slate-800/60 pb-1 mb-1.5 flex-shrink-0">
//                         <Briefcase className="w-3 h-3 text-purple-400" />
//                         <h4 className="text-[9px] font-bold text-purple-400 uppercase tracking-wider">Trade Fields</h4>
//                       </div>
//                       <div className="text-[11px] space-y-2 text-slate-300">
//                         <div className="grid grid-cols-2 gap-2">
//                           <div>
//                             <div className="text-slate-500 text-[8px] uppercase font-semibold">Investment Type</div>
//                             <div className="font-medium truncate">{selectedCase.investment_type || selectedCase.asset_class || "N/A"}</div>
//                           </div>
//                           <div>
//                             <div className="text-slate-500 text-[8px] uppercase font-semibold">Investment Amount</div>
//                             <div className="font-mono font-bold text-emerald-400">
//                               {selectedCase.investment_amount ? `$${Number(selectedCase.investment_amount).toLocaleString(undefined, {minimumFractionDigits: 2})}` : "N/A"}
//                             </div>
//                           </div>
//                         </div>
//                         <div className="pt-1.5 border-t border-slate-800/50 text-[10px] text-slate-500 grid grid-cols-2 gap-1 font-mono">
//                           <div>Notional: ${Number(selectedCase.notional_value || 0).toLocaleString()}</div>
//                           <div className="truncate text-right">Time: {selectedCase.timestamp || "N/A"}</div>
//                         </div>
//                       </div>
//                     </div>

//                     {/* SECTION 2: Client Profile */}
//                     <div className="bg-slate-950/20 border border-slate-800/40 p-2 rounded flex flex-col min-h-0 h-fit">
//                       <div className="flex items-center gap-1 border-b border-slate-800/60 pb-1 mb-1.5 flex-shrink-0">
//                         <User className="w-3 h-3 text-sky-400" />
//                         <h4 className="text-[9px] font-bold text-sky-400 uppercase tracking-wider">Client Profile</h4>
//                       </div>
//                       <div className="text-[11px] space-y-1.5 text-slate-300">
//                         <div className="grid grid-cols-2 gap-2">
//                           <div>
//                             <div className="text-slate-500 text-[8px] uppercase font-semibold">Age</div>
//                             <div className="font-mono">{selectedCase.client_age ?? "—"}</div>
//                           </div>
//                           <div>
//                             <div className="text-slate-500 text-[8px] uppercase font-semibold">Income</div>
//                             <div className="font-mono truncate">{selectedCase.client_income ? `$${Number(selectedCase.client_income).toLocaleString()}` : "—"}</div>
//                           </div>
//                         </div>
//                         <div className="grid grid-cols-2 gap-2 pt-1 border-t border-slate-800/30">
//                           <div>
//                             <div className="text-slate-500 text-[8px] uppercase font-semibold">Risk Tolerance</div>
//                             <div className="truncate text-[10px]">{selectedCase.risk_tolerance || selectedCase.client_risk_tolerance || "—"}</div>
//                           </div>
//                           <div>
//                             <div className="text-slate-500 text-[8px] uppercase font-semibold">Experience</div>
//                             <div className="truncate text-[10px]">{selectedCase.investment_experience || "—"}</div>
//                           </div>
//                         </div>
//                         <div className="pt-1 border-t border-slate-800/30">
//                           <div className="text-slate-500 text-[8px] uppercase font-semibold">Objective & Horizon</div>
//                           <div className="text-[10px] leading-tight text-slate-400">
//                             {selectedCase.investment_objective || "—"} ({selectedCase.investment_time_horizon || "N/A"})
//                           </div>
//                         </div>
//                       </div>
//                     </div>

//                     {/* SECTION 3: Advisor Records */}
//                     <div className="bg-slate-950/20 border border-slate-800/40 p-2 rounded flex flex-col min-h-0 h-fit">
//                       <div className="flex items-center gap-1 border-b border-slate-800/60 pb-1 mb-1.5 flex-shrink-0">
//                         <FileText className="w-3 h-3 text-amber-400" />
//                         <h4 className="text-[9px] font-bold text-amber-400 uppercase tracking-wider">Advisor Records</h4>
//                       </div>
//                       <div className="text-[11px] space-y-1.5 text-slate-300">
//                         <div className="grid grid-cols-2 gap-2 text-[10px]">
//                           <div>
//                             <span className="text-slate-500 block text-[8px] uppercase font-semibold">Advisor ID</span>
//                             <span className="font-mono font-medium truncate block">{selectedCase.advisor_id || "—"}</span>
//                           </div>
//                           <div>
//                             <span className="text-slate-500 block text-[8px] uppercase font-semibold">Experience</span>
//                             <span className="truncate block">{selectedCase.advisor_experience || "—"}</span>
//                           </div>
//                         </div>
                        
//                         <div className="grid grid-cols-2 gap-2 pt-1 border-t border-slate-800/50 items-center">
//                           <div>
//                             <span className="text-slate-500 block text-[8px] uppercase font-semibold">History Risk</span>
//                             <span className="font-mono text-rose-400">{selectedCase.advisor_history_risk ?? "—"}</span>
//                           </div>
//                           <div>
//                             <span className="text-slate-500 block text-[8px] uppercase font-semibold">Rationale</span>
//                             <span className={`inline-block px-1 rounded text-[8px] font-bold ${
//                               selectedCase.has_rationale === true || selectedCase.has_rationale === "true"
//                                 ? "bg-emerald-950 text-emerald-400 border border-emerald-800/50" 
//                                 : "bg-slate-950 text-slate-500 border border-slate-800"
//                             }`}>
//                               {selectedCase.has_rationale ? "FILED" : "MISSING"}
//                             </span>
//                           </div>
//                         </div>

//                         <div className="pt-1 border-t border-slate-800/50">
//                           <span className="text-slate-500 block text-[8px] uppercase font-semibold mb-0.5">Desk Notes Context</span>
//                           <p className="text-[10px] text-slate-400 leading-snug max-h-[55px] overflow-y-auto dynamic-scroll">
//                             {selectedCase.advisor_notes || "No transactional notes filed on submission."}
//                           </p>
//                         </div>
//                       </div>
//                     </div>

//                     {/* SECTION 4: Exception Breakdown */}
//                     <div className="bg-slate-950/20 border border-slate-800/40 p-2 rounded flex flex-col min-h-0 h-fit">
//                       <div className="flex items-center gap-1 border-b border-slate-800/60 pb-1 mb-1.5 flex-shrink-0">
//                         <HelpCircle className="w-3 h-3 text-rose-400" />
//                         <h4 className="text-[9px] font-bold text-rose-400 uppercase tracking-wider">Exception Breakdown</h4>
//                       </div>
//                       <div className="text-[11px] text-slate-300 leading-snug flex-1 flex flex-col justify-between">
//                         <div>
//                           <div className="text-slate-500 text-[8px] uppercase font-semibold mb-0.5">Flag Reason</div>
//                           <p className="text-[10px] text-rose-300/90 max-h-[90px] overflow-y-auto dynamic-scroll">
//                             {selectedCase.flag_reason || "No structural exceptions found."}
//                           </p>
//                         </div>
//                       </div>
//                     </div>

//                   </div>

//                   {/* Dedicated Policy Badges Box Container */}
//                   <div className="bg-slate-950/40 border border-slate-800/50 p-2 rounded flex-shrink-0">
//                     <div className="text-[8px] font-black text-slate-500 uppercase tracking-wider mb-1">
//                       Retrieved Regulatory & Firm Policies:
//                     </div>
//                     <div className="flex flex-wrap gap-1 items-center max-h-[50px] overflow-y-auto dynamic-scroll">
//                       {renderPolicies(selectedCase.retrieved_policies)}
//                     </div>
//                   </div>

//                   {/* Persistent Sign-off Form Area */}
//                   <div className="border-t border-slate-800/80 pt-2 flex flex-col gap-2 flex-shrink-0">
//                     <div className="flex flex-col">
//                       <label className="text-[9px] font-black text-slate-400 uppercase tracking-widest mb-1">
//                         Reviewer Sign-off Notes
//                       </label>
//                       <input
//                         type="text"
//                         value={currentNotes}
//                         disabled={isFinalized}
//                         onChange={(e) => handleNotesChange(e.target.value)}
//                         placeholder={isFinalized ? "Audit history signature locked." : "Enter compliance justification or structural risk override arguments..."}
//                         className="w-full bg-slate-950 border border-slate-800 rounded px-2.5 py-1.5 text-xs text-slate-200 focus:outline-none focus:border-purple-500/80 disabled:opacity-40 transition-colors placeholder:text-slate-600 font-medium"
//                       />
//                     </div>
                    
//                     {/* Action Workflow Button Strips */}
//                     <div className="flex gap-2 justify-end">
//                       <button
//                         onClick={handleApproveAI}
//                         disabled={isFinalized}
//                         className="bg-emerald-600 hover:bg-emerald-500 disabled:bg-slate-800 disabled:text-slate-500 text-slate-950 font-black text-[11px] px-3 py-1.5 rounded transition-colors uppercase tracking-wider whitespace-nowrap"
//                       >
//                         Approve AI
//                       </button>
//                       <button
//                         onClick={handleOverrideAI}
//                         disabled={isFinalized}
//                         className="bg-purple-600 hover:bg-purple-500 disabled:bg-slate-800 disabled:text-slate-500 text-slate-100 font-black text-[11px] px-3 py-1.5 rounded transition-colors uppercase tracking-wider whitespace-nowrap"
//                       >
//                         Override AI
//                       </button>
//                       <button
//                         onClick={handleEscalate}
//                         disabled={isFinalized}
//                         className="bg-rose-600 hover:bg-rose-500 disabled:bg-slate-800 disabled:text-slate-500 text-slate-100 font-black text-[11px] px-3 py-1.5 rounded transition-colors uppercase tracking-wider whitespace-nowrap"
//                       >
//                         Escalate
//                       </button>
//                     </div>
//                   </div>

//                 </div>
//               );
//             })()
//           ) : (
//             <div className="h-full flex items-center justify-center text-slate-500 text-xs font-semibold border border-dashed border-slate-800 rounded">
//               Select an active risk file from the lists to load the compliance workspace.
//             </div>
//           )}
//         </div>

//       </div>
//     </div>
//   );
// }

// export default Dashboard;

// /* VERSION 10 */

// import { useEffect, useState, useRef } from "react";
// import { getCases } from "../api/cases";
// import { AlertCircle, CheckCircle, Clock, ShieldAlert, FileText, User, Briefcase, HelpCircle, ArrowUpRight } from "lucide-react";

// interface CaseAuditState {
//   reviewStatus: "Reviewed" | "Not reviewed" | "Escalated";
//   notes: string;
//   overriddenLabel?: string; 
// }

// function Dashboard() {
//   const [activeView, setActiveView] = useState<"active" | "reviewed" | "passed">("active");
//   const [cases, setCases] = useState<any[]>([]);
//   const [selectedCase, setSelectedCase] = useState<any | null>(null);
  
//   const [caseStates, setCaseStates] = useState<Record<string, CaseAuditState>>({});
//   const [currentNotes, setCurrentNotes] = useState<string>("");

//   // --- Spreadsheet Column Resize State ---
//   const [urgentWidths, setUrgentWidths] = useState({ tradeId: 100, risk: 75, conf: 75, reason: 260 });
//   const [queuedWidths, setQueuedWidths] = useState({ tradeId: 100, priority: 70, risk: 75, conf: 75, reason: 240 });

//   const dragInfo = useRef<{ table: 'urgent' | 'queued'; col: string; startX: number; startWidth: number } | null>(null);

//   useEffect(() => {
//     getCases()
//       .then((data) => {
//         if (Array.isArray(data)) {
//           setCases(data);
          
//           const initialStates: Record<string, CaseAuditState> = {};
//           data.forEach((c) => {
//             if (c?.trade_id) {
//               initialStates[c.trade_id] = { 
//                 reviewStatus: "Not reviewed", 
//                 notes: "",
//                 overriddenLabel: c.compliance_label || "Non-compliant"
//               };
//             }
//           });
//           setCaseStates(initialStates);

//           const urgentCases = data.filter((c) => c?.escalation_level === "urgent");
//           const queuedCases = data
//             .filter((c) => c?.escalation_level === "priority" || c?.escalation_level === "queue")
//             .sort((a, b) => (Number(b?.priority_score) || 0) - (Number(a?.priority_score) || 0));

//           if (urgentCases.length > 0) handleCaseSelection(urgentCases[0], initialStates);
//           else if (queuedCases.length > 0) handleCaseSelection(queuedCases[0], initialStates);
//         }
//       })
//       .catch((err) => console.error("API Fetch Error:", err));
//   }, []);

//   const handleCaseSelection = (targetCase: any, latestStates = caseStates) => {
//     setSelectedCase(targetCase);
//     if (targetCase?.trade_id) {
//       const savedState = latestStates[targetCase.trade_id];
//       setCurrentNotes(savedState ? savedState.notes : "");
//     }
//   };

//   const handleNotesChange = (text: string) => {
//     setCurrentNotes(text);
//     if (selectedCase?.trade_id) {
//       setCaseStates(prev => ({
//         ...prev,
//         [selectedCase.trade_id]: { ...prev[selectedCase.trade_id], notes: text }
//       }));
//     }
//   };

//   const handleApproveAI = () => {
//     if (!selectedCase?.trade_id) return;
//     setCaseStates(prev => ({
//       ...prev,
//       [selectedCase.trade_id]: { ...prev[selectedCase.trade_id], reviewStatus: "Reviewed", notes: currentNotes }
//     }));
//   };

//   const handleOverrideAI = () => {
//     if (!selectedCase?.trade_id) return;
//     setCaseStates(prev => {
//       const currentLabel = prev[selectedCase.trade_id]?.overriddenLabel || selectedCase.compliance_label || "Non-compliant";
//       const flippedLabel = currentLabel.toLowerCase().includes("non") ? "Compliant" : "Non-compliant";
//       return {
//         ...prev,
//         [selectedCase.trade_id]: { ...prev[selectedCase.trade_id], reviewStatus: "Reviewed", overriddenLabel: flippedLabel, notes: currentNotes }
//       };
//     });
//   };

//   const handleEscalate = () => {
//     if (!selectedCase?.trade_id) return;
//     setCaseStates(prev => ({
//       ...prev,
//       [selectedCase.trade_id]: { ...prev[selectedCase.trade_id], reviewStatus: "Escalated", notes: currentNotes }
//     }));
//   };

//   const handleMouseDown = (table: 'urgent' | 'queued', col: string, e: React.MouseEvent) => {
//     e.preventDefault();
//     const currentWidths = table === 'urgent' ? urgentWidths : queuedWidths;
//     dragInfo.current = { table, col, startX: e.clientX, startWidth: (currentWidths as any)[col] };
//     document.addEventListener("mousemove", handleMouseMove);
//     document.addEventListener("mouseup", handleMouseUp);
//   };

//   const handleMouseMove = (e: MouseEvent) => {
//     if (!dragInfo.current) return;
//     const { table, col, startX, startWidth } = dragInfo.current;
//     const deltaX = e.clientX - startX;
//     const newWidth = Math.max(50, startWidth + deltaX);
//     if (table === 'urgent') setUrgentWidths(prev => ({ ...prev, [col]: newWidth }));
//     else setQueuedWidths(prev => ({ ...prev, [col]: newWidth }));
//   };

//   const handleMouseUp = () => {
//     dragInfo.current = null;
//     document.removeEventListener("mousemove", handleMouseMove);
//     document.removeEventListener("mouseup", handleMouseUp);
//   };

//   const handleDoubleClick = (table: 'urgent' | 'queued') => {
//     if (table === 'urgent') setUrgentWidths({ tradeId: 100, risk: 75, conf: 75, reason: 260 });
//     else setQueuedWidths({ tradeId: 100, priority: 70, risk: 75, conf: 75, reason: 240 });
//   };

//   const urgentCases = cases.filter((c) => c?.escalation_level === "urgent");
//   const queuedCases = cases
//     .filter((c) => c?.escalation_level === "priority" || c?.escalation_level === "queue")
//     .sort((a, b) => (Number(b?.priority_score) || 0) - (Number(a?.priority_score) || 0));

//   const countUrgent = urgentCases.length;
//   const countReview = queuedCases.length;
//   const countEscalated = Object.values(caseStates).filter((s) => s.reviewStatus === "Escalated").length;
//   const countPassed = cases.filter((c) => c?.escalation_level !== "urgent" && c?.escalation_level !== "priority" && c?.escalation_level !== "queue").length;

//   const renderPolicies = (policies: any) => {
//     if (!policies) return <span className="text-[10px] text-slate-500">No policies attached.</span>;
//     let items: string[] = [];
//     if (Array.isArray(policies)) items = policies;
//     else if (typeof policies === "string" && policies.startsWith("[")) {
//       items = policies.replace(/[\[\]']/g, "").split(",").map((p) => p.trim()).filter(Boolean);
//     } else if (typeof policies === "string" && policies.trim().length > 0) {
//       items = policies.split(",").map((p) => p.trim());
//     }
//     if (items.length === 0) return <span className="text-[10px] text-slate-500">No policies attached.</span>;
//     return items.map((policy, i) => (
//       <span key={i} className="px-1.5 py-0.5 bg-slate-950 text-[10px] rounded border border-slate-800 text-purple-300 font-mono">
//         {policy}
//       </span>
//     ));
//   };

//   return (
//     <div className="p-1 h-screen bg-slate-950 text-slate-100 flex flex-col gap-1 overflow-hidden select-none">
      
//       {/* Top Header Metrics Layer */}
//       <div className="flex items-center justify-between border-b border-slate-900 pb-1 flex-shrink-0">
//         <h1 className="text-base font-bold tracking-tight text-slate-200">
//           AI Compliance Review Copilot
//         </h1>
        
//         <div className="flex items-center gap-2">
//           <div className="bg-rose-950/30 border border-rose-500/30 rounded px-2 py-0.5 flex items-center gap-1.5 text-xs font-medium shadow-sm">
//             <AlertCircle className="w-3.5 h-3.5 text-rose-400" />
//             <span className="text-rose-300">Urgent:</span>
//             <span className="text-sm font-black text-rose-100">{countUrgent}</span>
//           </div>
//           <div className="bg-amber-950/30 border border-amber-500/30 rounded px-2 py-0.5 flex items-center gap-1.5 text-xs font-medium shadow-sm">
//             <Clock className="w-3.5 h-3.5 text-amber-400" />
//             <span className="text-amber-300">Review:</span>
//             <span className="text-sm font-black text-amber-100">{countReview}</span>
//           </div>
//           <div className="bg-purple-950/30 border border-purple-500/30 rounded px-2 py-0.5 flex items-center gap-1.5 text-xs font-medium shadow-sm">
//             <ArrowUpRight className="w-3.5 h-3.5 text-purple-400" />
//             <span className="text-purple-300">Escalated:</span>
//             <span className="text-sm font-black text-purple-100">{countEscalated}</span>
//           </div>
//           <div className="bg-emerald-950/30 border border-emerald-500/30 rounded px-2 py-0.5 flex items-center gap-1.5 text-xs font-medium shadow-sm">
//             <CheckCircle className="w-3.5 h-3.5 text-emerald-400" />
//             <span className="text-emerald-300">Passed:</span>
//             <span className="text-sm font-black text-emerald-100">{countPassed}</span>
//           </div>
//         </div>
//       </div>

//       {/* Main Split Grid: 45% Upper Stream Viewers / 55% Lower Static Audit Matrix */}
//       <div className="flex-1 grid grid-rows-[45fr_55fr] gap-1 min-h-0">
        
//         <div className="grid grid-cols-2 gap-1 min-h-0">
//           {/* URGENT TRACK PANEL */}
//           <div className="bg-slate-900 border border-rose-500/10 rounded-md p-1.5 flex flex-col min-h-0">
//             <div className="flex items-center gap-1 border-b border-slate-800 pb-0.5 mb-1 flex-shrink-0">
//               <ShieldAlert className="w-3.5 h-3.5 text-rose-400" />
//               <h2 className="text-[10px] font-bold text-rose-400 uppercase tracking-wider">Urgent Action Required</h2>
//             </div>
//             <div className="flex-1 overflow-auto min-h-0 relative border border-slate-800/30 rounded">
//               {urgentCases.length === 0 ? <p className="text-xs text-slate-500 p-1">No urgent cases outstanding.</p> : (
//                 <table className="text-left text-xs border-collapse table-fixed w-max min-w-full">
//                   <thead className="sticky top-0 bg-slate-900 text-slate-400 font-bold uppercase text-[9px] border-b border-slate-800 z-10">
//                     <tr>
//                       <th style={{ width: urgentWidths.tradeId }} className="p-1 relative group">Trade ID
//                         <div onMouseDown={(e) => handleMouseDown('urgent', 'tradeId', e)} onDoubleClick={() => handleDoubleClick('urgent')} className="absolute right-0 top-0 bottom-0 w-1 bg-slate-700/0 group-hover:bg-purple-500/50 cursor-col-resize transition-colors" />
//                       </th>
//                       <th style={{ width: urgentWidths.risk }} className="p-1 text-right relative group">Risk Score
//                         <div onMouseDown={(e) => handleMouseDown('urgent', 'risk', e)} onDoubleClick={() => handleDoubleClick('urgent')} className="absolute right-0 top-0 bottom-0 w-1 bg-slate-700/0 group-hover:bg-purple-500/50 cursor-col-resize transition-colors" />
//                       </th>
//                       <th style={{ width: urgentWidths.conf }} className="p-1 text-right relative group">Conf.

//                         <div onMouseDown={(e) => handleMouseDown('urgent', 'conf', e)} onDoubleClick={() => handleDoubleClick('urgent')} className="absolute right-0 top-0 bottom-0 w-1 bg-slate-700/0 group-hover:bg-purple-500/50 cursor-col-resize transition-colors" />
//                       </th>
//                       <th style={{ width: urgentWidths.reason }} className="p-1 pl-2 relative group">Flag Reason</th>
//                     </tr>
//                   </thead>
//                   <tbody className="divide-y divide-slate-800/30">
//                     {urgentCases.map((c, idx) => {
//                       const isSelected = selectedCase?.trade_id === c?.trade_id;
//                       const riskVal = 1 - (Number(c?.compliance_probability) ?? 1.0);
//                       return (
//                         <tr key={`${c?.trade_id}-${idx}`} onClick={() => handleCaseSelection(c)} className={`cursor-pointer text-[11px] transition-colors ${isSelected ? 'bg-rose-950/40 font-semibold border-l-2 border-rose-500 text-rose-200' : 'hover:bg-slate-800/30 text-slate-300'}`}>
//                           <td className="p-1 font-mono truncate">{c?.trade_id}</td>
//                           <td className="p-1 text-right font-mono text-rose-400/90">{riskVal.toFixed(2)}</td>
//                           <td className="p-1 text-right font-mono text-slate-400">{(Number(c?.confidence_score) || 0).toFixed(2)}</td>
//                           <td className="p-1 pl-2 truncate text-[10px]">{c?.flag_reason}</td>
//                         </tr>
//                       );
//                     })}
//                   </tbody>
//                 </table>
//               )}
//             </div>
//           </div>

//           {/* REVIEW QUEUE PANEL */}
//           <div className="bg-slate-900 border border-slate-800/80 rounded-md p-1.5 flex flex-col min-h-0">
//             <div className="flex items-center gap-1 border-b border-slate-800 pb-0.5 mb-1 flex-shrink-0">
//               <Clock className="w-3.5 h-3.5 text-amber-400" />
//               <h2 className="text-[10px] font-bold text-amber-400 uppercase tracking-wider">Review</h2>
//             </div>
//             <div className="flex-1 overflow-auto min-h-0 relative border border-slate-800/30 rounded">
//               {queuedCases.length === 0 ? <p className="text-xs text-slate-500 p-1">Review queue empty.</p> : (
//                 <table className="text-left text-xs border-collapse table-fixed w-max min-w-full">
//                   <thead className="sticky top-0 bg-slate-900 text-slate-400 font-bold uppercase text-[9px] border-b border-slate-800 z-10">
//                     <tr>
//                       <th style={{ width: queuedWidths.tradeId }} className="p-1 relative group">Trade ID
//                         <div onMouseDown={(e) => handleMouseDown('queued', 'tradeId', e)} onDoubleClick={() => handleDoubleClick('queued')} className="absolute right-0 top-0 bottom-0 w-1 bg-slate-700/0 group-hover:bg-purple-500/50 cursor-col-resize transition-colors" />
//                       </th>
//                       <th style={{ width: queuedWidths.priority }} className="p-1 text-right relative group text-amber-400">Priority</th>
//                       <th style={{ width: queuedWidths.risk }} className="p-1 text-right relative group">Risk Score</th>
//                       <th style={{ width: queuedWidths.conf }} className="p-1 text-right relative group">Conf.</th>
//                       <th style={{ width: queuedWidths.reason }} className="p-1 pl-2 relative group">Flag Reason</th>
//                     </tr>
//                   </thead>
//                   <tbody className="divide-y divide-slate-800/30">
//                     {queuedCases.map((c, idx) => {
//                       const isSelected = selectedCase?.trade_id === c?.trade_id;
//                       const riskVal = 1 - (Number(c?.compliance_probability) ?? 1.0);
//                       return (
//                         <tr key={`${c?.trade_id}-${idx}`} onClick={() => handleCaseSelection(c)} className={`cursor-pointer text-[11px] transition-colors ${isSelected ? 'bg-purple-950/40 font-semibold border-l-2 border-purple-500 text-purple-200' : 'hover:bg-slate-800/30 text-slate-300'}`}>
//                           <td className="p-1 font-mono truncate">{c?.trade_id}</td>
//                           <td className="p-1 text-right font-mono font-bold text-amber-400">{c?.priority_score ?? "0"}</td>
//                           <td className="p-1 text-right font-mono text-rose-400/90">{riskVal.toFixed(2)}</td>
//                           <td className="p-1 text-right font-mono text-slate-400">{(Number(c?.confidence_score) || 0).toFixed(2)}</td>
//                           <td className="p-1 pl-2 truncate text-[10px]">{c?.flag_reason}</td>
//                         </tr>
//                       );
//                     })}
//                   </tbody>
//                 </table>
//               )}
//             </div>
//           </div>
//         </div>

//         {/* LOWER VIEW: High-Density Workspace (Fully Proportional, Layout Overlaps Prevented) */}
//         <div className="bg-slate-900 border border-slate-800 rounded-md p-2 flex flex-col min-h-0 shadow-2xl">
//           {selectedCase ? (() => {
//             const currentState = caseStates[selectedCase.trade_id] || { reviewStatus: "Not reviewed", notes: "" };
//             const isFinalized = currentState.reviewStatus === "Reviewed" || currentState.reviewStatus === "Escalated";
//             const riskVal = 1 - (Number(selectedCase.compliance_probability) || 0);
//             const currentRec = currentState.overriddenLabel || selectedCase.compliance_label || "Non-compliant";
//             const isRecCompliant = currentRec.toLowerCase() === "compliant";
            
//             return (
//               <div className="flex flex-col h-full gap-1.5 min-h-0 justify-between">
                
//                 {/* Title & Micro Scores Strip */}
//                 <div className="flex items-center justify-between border-b border-slate-800 pb-1 flex-shrink-0">
//                   <div className="flex items-center gap-1.5">
//                     <span className="text-[9px] font-black uppercase tracking-wider text-purple-400 bg-purple-950/30 px-1.5 py-0.5 rounded border border-purple-900/40">
//                       Selected Case Audit
//                     </span>
//                     <span className="text-xs font-mono font-bold text-slate-100">{selectedCase.trade_id}</span>
//                     <span className={`px-1.5 py-0.5 rounded text-[9px] font-bold tracking-wide border ${
//                       currentState.reviewStatus === "Reviewed" ? "bg-emerald-950/40 text-emerald-400 border-emerald-800/40" 
//                       : currentState.reviewStatus === "Escalated" ? "bg-rose-950/40 text-rose-400 border-rose-800/40" : "bg-slate-950 text-amber-400 border-amber-900/40"
//                     }`}>{currentState.reviewStatus.toUpperCase()}</span>
//                   </div>
                  
//                   <div className="flex items-center gap-3 bg-slate-950/80 px-2 py-0.5 rounded border border-slate-800/60 text-[11px]">
//                     <div className="flex items-center gap-1">
//                       <span className="text-slate-500 font-medium text-[9px] uppercase">AI Rec:</span>
//                       <span className={`font-bold tracking-tight px-1 rounded text-[10px] ${isRecCompliant ? "bg-emerald-950/50 text-emerald-400" : "bg-rose-950/50 text-rose-400"}`}>{currentRec}</span>
//                     </div>
//                     <div className="border-l border-slate-800 h-3" />
//                     <div><span className="text-slate-500 font-medium text-[9px] uppercase mr-1">Risk:</span><span className="font-mono font-bold text-rose-400">{riskVal.toFixed(4)}</span></div>
//                     <div className="border-l border-slate-800 h-3" />
//                     <div><span className="text-slate-500 font-medium text-[9px] uppercase mr-1">Conf:</span><span className="font-mono font-bold text-sky-400">{Number(selectedCase.confidence_score || 0).toFixed(4)}</span></div>
//                   </div>
//                 </div>

//                 {/* Structured Audit Grid (Flexbox heights inside prevent clipping/overlapping entirely) */}
//                 <div className="grid grid-cols-4 gap-1.5 flex-1 min-h-0 py-0.5">
                  
//                   {/* COLUMN 1: Trade Fields (Notional Value Row Completely Discarded) */}
//                   <div className="bg-slate-950/20 border border-slate-800/40 p-1.5 rounded flex flex-col justify-between min-h-0">
//                     <div className="flex items-center gap-1 border-b border-slate-800 pb-1 mb-1 flex-shrink-0">
//                       <Briefcase className="w-3 h-3 text-purple-400" />
//                       <h4 className="text-[9px] font-bold text-purple-400 uppercase tracking-wider">Trade Fields</h4>
//                     </div>
//                     <div className="text-[11px] flex-1 flex flex-col justify-around text-slate-300 min-h-0">
//                       <div>
//                         <div className="text-slate-500 text-[9px] uppercase font-semibold">Investment Type</div>
//                         <div className="font-medium truncate">{selectedCase.investment_type || selectedCase.asset_class || "N/A"}</div>
//                       </div>
//                       <div>
//                         <div className="text-slate-500 text-[9px] uppercase font-semibold">Investment Amount</div>
//                         <div className="font-mono font-bold text-emerald-400">
//                           {selectedCase.investment_amount ? `$${Number(selectedCase.investment_amount).toLocaleString(undefined, {minimumFractionDigits: 2})}` : "N/A"}
//                         </div>
//                       </div>
//                       <div className="pt-1 border-t border-slate-800/40">
//                         <div className="text-slate-500 text-[9px] uppercase font-semibold">Trade Execution Timestamp</div>
//                         {/* Direct variable lookup fixes the empty character fallback '-' bug */}
//                         <div className="font-mono text-[10px] text-slate-300 truncate">{selectedCase.timestamp || selectedCase.timestamp_utc || "N/A"}</div>
//                       </div>
//                     </div>
//                   </div>

//                   {/* COLUMN 2: Client Profile (Compact Matrix prevents overlaps from added Time Horizon line) */}
//                   <div className="bg-slate-950/20 border border-slate-800/40 p-1.5 rounded flex flex-col justify-between min-h-0">
//                     <div className="flex items-center gap-1 border-b border-slate-800 pb-1 mb-1 flex-shrink-0">
//                       <User className="w-3 h-3 text-sky-400" />
//                       <h4 className="text-[9px] font-bold text-sky-400 uppercase tracking-wider">Client Profile</h4>
//                     </div>
//                     <div className="text-[11px] flex-1 flex flex-col justify-between text-slate-300 min-h-0 space-y-0.5">
//                       <div className="grid grid-cols-2 gap-1">
//                         <div>
//                           <div className="text-slate-500 text-[9px] uppercase font-semibold">Age</div>
//                           <div className="font-mono truncate">{selectedCase.client_age ?? "—"}</div>
//                         </div>
//                         <div>
//                           <div className="text-slate-500 text-[9px] uppercase font-semibold">Income</div>
//                           <div className="font-mono truncate">{selectedCase.client_income ? `$${Number(selectedCase.client_income).toLocaleString()}` : "—"}</div>
//                         </div>
//                       </div>
//                       <div>
//                         <div className="text-slate-500 text-[9px] uppercase font-semibold">Risk Tolerance</div>
//                         <div className="truncate font-medium text-amber-400">{selectedCase.risk_tolerance || selectedCase.client_risk_tolerance || "—"}</div>
//                       </div>
//                       <div>
//                         <div className="text-slate-500 text-[9px] uppercase font-semibold">Experience Level</div>
//                         <div className="truncate">{selectedCase.investment_experience || "—"}</div>
//                       </div>
//                       <div>
//                         <div className="text-slate-500 text-[9px] uppercase font-semibold">Objective</div>
//                         <div className="truncate text-slate-300">{selectedCase.investment_objective || "—"}</div>
//                       </div>
//                       <div>
//                         <div className="text-slate-500 text-[9px] uppercase font-semibold text-indigo-400">Time Horizon</div>
//                         <div className="truncate font-medium text-indigo-300">{selectedCase.investment_time_horizon || "—"}</div>
//                       </div>
//                     </div>
//                   </div>

//                   {/* COLUMN 3: Advisor Records (Restored fully with discrete fields + inline notes) */}
//                   <div className="bg-slate-950/20 border border-slate-800/40 p-1.5 rounded flex flex-col justify-between min-h-0">
//                     <div className="flex items-center gap-1 border-b border-slate-800 pb-1 mb-1 flex-shrink-0">
//                       <FileText className="w-3 h-3 text-amber-400" />
//                       <h4 className="text-[9px] font-bold text-amber-400 uppercase tracking-wider">Advisor Records</h4>
//                     </div>
//                     <div className="text-[11px] flex-1 flex flex-col justify-between text-slate-300 min-h-0 space-y-1">
//                       <div className="grid grid-cols-2 gap-1 text-[10px]">
//                         <div>
//                           <span className="text-slate-500 block text-[9px] uppercase font-semibold">Advisor ID</span>
//                           <span className="font-mono font-medium truncate block">{selectedCase.advisor_id || "—"}</span>
//                         </div>
//                         <div>
//                           <span className="text-slate-500 block text-[9px] uppercase font-semibold">Experience</span>
//                           <span className="truncate block text-slate-300">{selectedCase.advisor_experience || "—"}</span>
//                         </div>
//                       </div>
//                       <div className="grid grid-cols-2 gap-1 items-center">
//                         <div>
//                           <span className="text-slate-500 block text-[9px] uppercase font-semibold">History Risk</span>
//                           <span className="font-mono text-rose-400 font-bold">{selectedCase.advisor_history_risk ?? "—"}</span>
//                         </div>
//                         <div>
//                           <span className="text-slate-500 block text-[9px] uppercase font-semibold">Rationale</span>
//                           <span className={`inline-block px-1 rounded text-[9px] font-bold ${
//                             selectedCase.has_rationale ? "bg-emerald-950 text-emerald-400 border border-emerald-800/50" : "bg-slate-950 text-slate-500 border border-slate-800"
//                           }`}>{selectedCase.has_rationale ? "FILED" : "MISSING"}</span>
//                         </div>
//                       </div>
//                       <div className="pt-1 border-t border-slate-800/50">
//                         <span className="text-slate-500 block text-[9px] uppercase font-semibold mb-0.5">advisor_notes</span>
//                         <p className="text-[10px] text-slate-400 leading-snug line-clamp-2 italic">
//                           "{selectedCase.advisor_notes || "No transactional desk notes found on filing submission."}"
//                         </p>
//                       </div>
//                     </div>
//                   </div>

//                   {/* COLUMN 4: Exception Breakdown */}
//                   <div className="bg-slate-950/20 border border-slate-800/40 p-1.5 rounded flex flex-col min-h-0">
//                     <div className="flex items-center gap-1 border-b border-slate-800 pb-1 mb-1 flex-shrink-0">
//                       <HelpCircle className="w-3 h-3 text-rose-400" />
//                       <h4 className="text-[9px] font-bold text-rose-400 uppercase tracking-wider">Exception Breakdown</h4>
//                     </div>
//                     <div className="text-[11px] text-slate-300 flex-1 flex flex-col justify-start min-h-0 leading-snug">
//                       <div className="text-slate-500 text-[9px] uppercase font-semibold mb-0.5">Flag Reason</div>
//                       <p className="text-[10px] text-rose-300/90 font-medium">{selectedCase.flag_reason || "No structural exceptions found on transaction parameters."}</p>
//                     </div>
//                   </div>

//                 </div>

//                 {/* Retained Policy Badges Row */}
//                 <div className="flex-shrink-0 py-0.5">
//                   <div className="flex flex-wrap gap-1 items-center">
//                     <span className="text-[9px] font-black text-slate-600 uppercase tracking-wider mr-1">Policies:</span>
//                     {renderPolicies(selectedCase.retrieved_policies)}
//                   </div>
//                 </div>

//                 {/* Persistent Sign-off Form Area */}
//                 <div className="border-t border-slate-800 pt-1 flex gap-2 items-end flex-shrink-0">
//                   <div className="flex-1 flex flex-col">
//                     <label className="text-[9px] font-black text-slate-400 uppercase tracking-widest mb-0.5">
//                       Reviewer Sign-off Notes
//                     </label>
//                     <input
//                       type="text"
//                       value={currentNotes}
//                       disabled={isFinalized}
//                       onChange={(e) => handleNotesChange(e.target.value)}
//                       placeholder={isFinalized ? "Audit history signature locked." : "Enter compliance justification or structural risk override arguments..."}
//                       className="w-full bg-slate-950 border border-slate-800 rounded px-2 py-1 text-xs text-slate-200 focus:outline-none focus:border-purple-500/80 disabled:opacity-40 transition-colors placeholder:text-slate-600"
//                     />
//                   </div>
                  
//                   <div className="flex gap-1.5">
//                     <button onClick={handleApproveAI} disabled={isFinalized} className="bg-emerald-600 hover:bg-emerald-500 disabled:bg-slate-800 disabled:text-slate-500 text-slate-950 font-black text-xs px-2.5 py-1 rounded transition-colors uppercase tracking-wider whitespace-nowrap">Approve AI</button>
//                     <button onClick={handleOverrideAI} disabled={isFinalized} className="bg-purple-600 hover:bg-purple-500 disabled:bg-slate-800 disabled:text-slate-500 text-slate-100 font-black text-xs px-2.5 py-1 rounded transition-colors uppercase tracking-wider whitespace-nowrap">Override AI</button>
//                     <button onClick={handleEscalate} disabled={isFinalized} className="bg-rose-600 hover:bg-rose-500 disabled:bg-slate-800 disabled:text-slate-500 text-slate-100 font-black text-xs px-2.5 py-1 rounded transition-colors uppercase tracking-wider whitespace-nowrap">Escalate</button>
//                   </div>
//                 </div>

//               </div>
//             );
//           })() : (
//             <div className="h-full flex items-center justify-center text-slate-500 text-xs font-semibold border border-dashed border-slate-800 rounded">
//               Select an active risk file from the lists above to load the compliance audit space.
//             </div>
//           )}
//         </div>

//       </div>
//     </div>
//   );
// }

// export default Dashboard;

// /* VERSION 9 - REFACTORED TO SEPARATE BUSINESS LOGIC FROM UI LOGIC */

// import React, { useState, useRef, useEffect } from "react";
// import { useTriageWorkflow } from "../hooks/useTriageWorkflow";
// import { CheckCircle, Clock, ShieldAlert, FileText, User, Briefcase, HelpCircle, Check, X, CornerUpRight } from "lucide-react";

// function Dashboard() {
//   const workflow = useTriageWorkflow();
//   const [currentNotes, setCurrentNotes] = useState<string>("");

//   useEffect(() => {
//     if (workflow.selectedCase?.trade_id) {
//       const savedState = workflow.caseStates[workflow.selectedCase.trade_id];
//       setCurrentNotes(savedState ? savedState.notes : "");
//     } else {
//       setCurrentNotes("");
//     }
//   }, [workflow.selectedCase, workflow.caseStates]);

//   const handleNotesChange = (text: string) => {
//     setCurrentNotes(text);
//     if (workflow.selectedCase?.trade_id) {
//       workflow.updateNotes(workflow.selectedCase.trade_id, text);
//     }
//   };

//   // --- Flexible Spreadsheet Column Resize States (4 Distinct Data Frameworks) ---
//   const [urgentWidths, setUrgentWidths] = useState({ tradeId: 100, risk: 85, conf: 85, reason: 320 });
//   const [queuedWidths, setQueuedWidths] = useState({ tradeId: 100, priority: 75, risk: 85, conf: 85, reason: 280 });
//   const [reviewedWidths, setReviewedWidths] = useState({ tradeId: 110, type: 130, amount: 110, status: 120, notes: 340 });
//   const [passedWidths, setPassedWidths] = useState({ tradeId: 110, asset: 130, value: 120, confidence: 120, status: 140 });

//   const dragInfo = useRef<{ table: 'urgent' | 'queued' | 'reviewed' | 'passed'; col: string; startX: number; startWidth: number } | null>(null);

//   const handleMouseDown = (table: 'urgent' | 'queued' | 'reviewed' | 'passed', col: string, e: React.MouseEvent) => {
//     e.preventDefault();
//     let currentWidths: any;
//     if (table === 'urgent') currentWidths = urgentWidths;
//     else if (table === 'queued') currentWidths = queuedWidths;
//     else if (table === 'reviewed') currentWidths = reviewedWidths;
//     else currentWidths = passedWidths;

//     dragInfo.current = { table, col, startX: e.clientX, startWidth: currentWidths[col] };
//     document.addEventListener("mousemove", handleMouseMove);
//     document.addEventListener("mouseup", handleMouseUp);
//   };

//   const handleMouseMove = (e: MouseEvent) => {
//     if (!dragInfo.current) return;
//     const { table, col, startX, startWidth } = dragInfo.current;
//     const deltaX = e.clientX - startX;
//     const newWidth = Math.max(60, startWidth + deltaX);

//     if (table === 'urgent') setUrgentWidths(prev => ({ ...prev, [col]: newWidth }));
//     else if (table === 'queued') setQueuedWidths(prev => ({ ...prev, [col]: newWidth }));
//     else if (table === 'reviewed') setReviewedWidths(prev => ({ ...prev, [col]: newWidth }));
//     else setPassedWidths(prev => ({ ...prev, [col]: newWidth }));
//   };

//   const handleMouseUp = () => {
//     dragInfo.current = null;
//     document.removeEventListener("mousemove", handleMouseMove);
//     document.removeEventListener("mouseup", handleMouseUp);
//   };

//   const handleDoubleClick = (table: 'urgent' | 'queued' | 'reviewed' | 'passed') => {
//     if (table === 'urgent') setUrgentWidths({ tradeId: 100, risk: 85, conf: 85, reason: 320 });
//     else if (table === 'queued') setQueuedWidths({ tradeId: 100, priority: 75, risk: 85, conf: 85, reason: 280 });
//     else if (table === 'reviewed') setReviewedWidths({ tradeId: 110, type: 130, amount: 110, status: 120, notes: 340 });
//     else setPassedWidths({ tradeId: 110, asset: 130, value: 120, confidence: 120, status: 140 });
//   };

//   const renderPolicies = (policies: any) => {
//     if (!policies) return <span className="text-[10px] text-slate-500">No policies attached.</span>;
//     let items: string[] = [];
//     if (Array.isArray(policies)) items = policies;
//     else if (typeof policies === "string" && policies.startsWith("[")) {
//       items = policies.replace(/[\[\]']/g, "").split(",").map((p) => p.trim()).filter(Boolean);
//     } else if (typeof policies === "string" && policies.trim().length > 0) {
//       items = policies.split(",").map((p) => p.trim());
//     }
//     if (items.length === 0) return <span className="text-[10px] text-slate-500">No policies attached.</span>;
//     return items.map((p, i) => (
//       <span key={i} className="px-1.5 py-0.5 bg-slate-950 text-[10px] rounded border border-slate-800 text-purple-300 font-mono max-w-[140px] truncate">{p}</span>
//     ));
//   };

//   return (
//     <div className="p-2 h-screen bg-slate-950 text-slate-100 flex flex-col gap-2 overflow-hidden select-none">
      
//       {/* Top Header Metrics Row */}
//       <div className="flex items-center justify-between border-b border-slate-900 pb-2 shrink-0">
//         <div className="flex items-center gap-6">
//           <h1 className="text-base font-bold tracking-tight text-slate-200">AI Compliance Review Copilot</h1>
          
//           <div className="flex bg-slate-900 p-0.5 rounded border border-slate-800 gap-0.5">
//             <button onClick={() => workflow.setView("active")} className={`px-4 py-1 text-xs font-semibold rounded transition-all ${workflow.activeView === 'active' ? 'bg-indigo-600 text-white shadow' : 'text-slate-400 hover:text-slate-200'}`}>
//               Active ({workflow.urgentCases.length + workflow.queuedCases.length})
//             </button>
//             <button onClick={() => workflow.setView("reviewed")} className={`px-4 py-1 text-xs font-semibold rounded transition-all ${workflow.activeView === 'reviewed' ? 'bg-indigo-600 text-white shadow' : 'text-slate-400 hover:text-slate-200'}`}>
//               Reviewed ({workflow.reviewedCasesList.length})
//             </button>
//             <button onClick={() => workflow.setView("passed")} className={`px-4 py-1 text-xs font-semibold rounded transition-all ${workflow.activeView === 'passed' ? 'bg-indigo-600 text-white shadow' : 'text-slate-400 hover:text-slate-200'}`}>
//               Passed ({workflow.passedCasesList.length})
//             </button>
//           </div>
//         </div>
        
//         {/* Top Right Master Counters Row */}
//         <div className="flex items-center gap-2">
//           <div className="bg-rose-950/20 border border-rose-500/20 rounded px-2.5 py-1 flex items-center gap-1.5 text-xs font-medium">
//             <span className="text-rose-400">Urgent:</span>
//             <span className="font-bold text-rose-200">{workflow.urgentCases.length}</span>
//           </div>
//           <div className="bg-amber-950/20 border border-amber-500/20 rounded px-2.5 py-1 flex items-center gap-1.5 text-xs font-medium">
//             <span className="text-amber-400">Review:</span>
//             <span className="font-bold text-amber-200">{workflow.queuedCases.length}</span>
//           </div>
//           <div className="bg-emerald-950/20 border border-emerald-500/20 rounded px-2.5 py-1 flex items-center gap-1.5 text-xs font-medium">
//             <span className="text-emerald-400">Reviewed Today:</span>
//             <span className="font-bold text-emerald-200">{workflow.reviewedTodayCount}</span>
//           </div>
//           <div className="bg-indigo-950/20 border border-indigo-500/20 rounded px-2.5 py-1 flex items-center gap-1.5 text-xs font-medium">
//             <span className="text-indigo-400">Passed:</span>
//             <span className="font-bold text-indigo-200">{workflow.passedCasesList.length}</span>
//           </div>
//         </div>
//       </div>

//       {/* Primary Split Workspace: Upper View 40% / Lower Workspace 60% */}
//       <div className="flex-1 grid grid-rows-[40fr_60fr] gap-2 min-h-0">
        
//         {/* UPPER VIEW SEGMENT */}
//         <div className="min-h-0">
//           {workflow.activeView === "active" && (
//             <div className="grid grid-cols-2 gap-2 h-full min-h-0">
              
//               {/* Table 1: Urgent Table */}
//               <div className="bg-slate-900 border border-slate-800 rounded-md p-1.5 flex flex-col min-h-0">
//                 <div className="flex items-center gap-1 border-b border-slate-800 pb-0.5 mb-1 shrink-0">
//                   <ShieldAlert className="w-3.5 h-3.5 text-rose-400" />
//                   <h2 className="text-[10px] font-bold text-rose-400 uppercase tracking-wider">Urgent Action Required</h2>
//                 </div>
//                 <div className="flex-1 overflow-x-auto overflow-y-auto border border-slate-800/30 rounded dynamic-scroll min-h-0">
//                   {workflow.urgentCases.length === 0 ? <p className="text-xs text-slate-500 p-2 italic">No urgent cases outstanding.</p> : (
//                     <table className="text-left text-xs border-collapse table-fixed w-max min-w-full">
//                       <thead className="sticky top-0 bg-slate-900 text-slate-400 font-bold uppercase text-[9px] border-b border-slate-800 z-10">
//                         <tr>
//                           <th style={{ width: urgentWidths.tradeId }} className="p-1 relative group">Trade ID
//                             <div onMouseDown={(e) => handleMouseDown('urgent', 'tradeId', e)} onDoubleClick={() => handleDoubleClick('urgent')} className="absolute right-0 top-0 bottom-0 w-1 bg-purple-500/0 group-hover:bg-purple-500/30 cursor-col-resize" />
//                           </th>
//                           <th style={{ width: urgentWidths.risk }} className="p-1 text-right relative group">Risk Score
//                             <div onMouseDown={(e) => handleMouseDown('urgent', 'risk', e)} onDoubleClick={() => handleDoubleClick('urgent')} className="absolute right-0 top-0 bottom-0 w-1 bg-purple-500/0 group-hover:bg-purple-500/30 cursor-col-resize" />
//                           </th>
//                           <th style={{ width: urgentWidths.conf }} className="p-1 text-right relative group">Conf.
//                             <div onMouseDown={(e) => handleMouseDown('urgent', 'conf', e)} onDoubleClick={() => handleDoubleClick('urgent')} className="absolute right-0 top-0 bottom-0 w-1 bg-purple-500/0 group-hover:bg-purple-500/30 cursor-col-resize" />
//                           </th>
//                           <th style={{ width: urgentWidths.reason }} className="p-1 pl-2 relative group">Flag Reason</th>
//                         </tr>
//                       </thead>
//                       <tbody className="divide-y divide-slate-800/30">
//                         {workflow.urgentCases.map((c, i) => {
//                           const isSelected = workflow.selectedCase?.trade_id === c?.trade_id;
//                           return (
//                             <tr key={`${c.trade_id}-${i}`} onClick={() => workflow.selectCase(c)} className={`cursor-pointer text-[11px] ${isSelected ? 'bg-rose-950/40 font-semibold border-l-2 border-rose-500 text-rose-200' : 'hover:bg-slate-800/20 text-slate-300'}`}>
//                               <td className="p-1 font-mono truncate">{c.trade_id}</td>
//                               <td className="p-1 text-right font-mono text-rose-400">{(1 - (c.compliance_probability ?? 1)).toFixed(2)}</td>
//                               <td className="p-1 text-right font-mono text-slate-400">{(c.confidence_score || 0).toFixed(2)}</td>
//                               <td className="p-1 pl-2 truncate text-[10px]">{c.flag_reason}</td>
//                             </tr>
//                           );
//                         })}
//                       </tbody>
//                     </table>
//                   )}
//                 </div>
//               </div>

//               {/* Table 2: Review Table */}
//               <div className="bg-slate-900 border border-slate-800 rounded-md p-1.5 flex flex-col min-h-0">
//                 <div className="flex items-center gap-1 border-b border-slate-800 pb-0.5 mb-1 shrink-0">
//                   <Clock className="w-3.5 h-3.5 text-amber-400" />
//                   <h2 className="text-[10px] font-bold text-amber-400 uppercase tracking-wider">Review</h2>
//                 </div>
//                 <div className="flex-1 overflow-x-auto overflow-y-auto border border-slate-800/30 rounded dynamic-scroll min-h-0">
//                   {workflow.queuedCases.length === 0 ? <p className="text-xs text-slate-500 p-1 italic">Review queue empty.</p> : (
//                     <table className="text-left text-xs border-collapse table-fixed w-max min-w-full">
//                       <thead className="sticky top-0 bg-slate-900 text-slate-400 font-bold uppercase text-[9px] border-b border-slate-800 z-10">
//                         <tr>
//                           <th style={{ width: queuedWidths.tradeId }} className="p-1 relative group">Trade ID
//                             <div onMouseDown={(e) => handleMouseDown('queued', 'tradeId', e)} onDoubleClick={() => handleDoubleClick('queued')} className="absolute right-0 top-0 bottom-0 w-1 bg-purple-500/0 group-hover:bg-purple-500/30 cursor-col-resize" />
//                           </th>
//                           <th style={{ width: queuedWidths.priority }} className="p-1 text-right relative group text-amber-400">Priority</th>
//                           <th style={{ width: queuedWidths.risk }} className="p-1 text-right relative group">Risk Score</th>
//                           <th style={{ width: queuedWidths.conf }} className="p-1 text-right relative group">Conf.</th>
//                           <th style={{ width: queuedWidths.reason }} className="p-1 pl-2 relative group">Flag Reason</th>
//                         </tr>
//                       </thead>
//                       <tbody className="divide-y divide-slate-800/30">
//                         {workflow.queuedCases.map((c, i) => {
//                           const isSelected = workflow.selectedCase?.trade_id === c?.trade_id;
//                           return (
//                             <tr key={`${c.trade_id}-${i}`} onClick={() => workflow.selectCase(c)} className={`cursor-pointer text-[11px] ${isSelected ? 'bg-purple-950/40 font-semibold border-l-2 border-purple-500 text-purple-200' : 'hover:bg-slate-800/20 text-slate-300'}`}>
//                               <td className="p-1 font-mono truncate">{c.trade_id}</td>
//                               <td className="p-1 text-right font-mono font-bold text-amber-400">{c.priority_score ?? "0"}</td>
//                               <td className="p-1 text-right font-mono text-rose-400">{(1 - (c.compliance_probability ?? 1)).toFixed(2)}</td>
//                               <td className="p-1 text-right font-mono text-slate-400">{(c.confidence_score || 0).toFixed(2)}</td>
//                               <td className="p-1 pl-2 truncate text-[10px]">{c.flag_reason}</td>
//                             </tr>
//                           );
//                         })}
//                       </tbody>
//                     </table>
//                   )}
//                 </div>
//               </div>

//             </div>
//           )}

//           {/* Table 3: Scrollable Resizable Reviewed View Panel */}
//           {workflow.activeView === "reviewed" && (
//             <div className="bg-slate-900 border border-slate-800 rounded-md p-1.5 flex flex-col h-full min-h-0">
//               <div className="flex items-center gap-1 border-b border-slate-800 pb-0.5 mb-1 shrink-0">
//                 <CheckCircle className="w-3.5 h-3.5 text-emerald-400" />
//                 <h2 className="text-[10px] font-bold text-emerald-400 uppercase tracking-wider">User Reviewed Logs</h2>
//               </div>
//               <div className="flex-1 overflow-x-auto overflow-y-auto border border-slate-800/30 rounded dynamic-scroll min-h-0">
//                 {workflow.reviewedCasesList.length === 0 ? <p className="text-slate-500 text-xs p-3 italic text-center">No logs audited yet.</p> : (
//                   <table className="text-left text-xs border-collapse table-fixed w-max min-w-full">
//                     <thead className="sticky top-0 bg-slate-900 text-slate-400 font-bold uppercase text-[9px] border-b border-slate-800 z-10">
//                       <tr>
//                         <th style={{ width: reviewedWidths.tradeId }} className="p-1 relative group">Trade ID
//                           <div onMouseDown={(e) => handleMouseDown('reviewed', 'tradeId', e)} onDoubleClick={() => handleDoubleClick('reviewed')} className="absolute right-0 top-0 bottom-0 w-1 bg-purple-500/0 group-hover:bg-purple-500/30 cursor-col-resize" />
//                         </th>
//                         <th style={{ width: reviewedWidths.type }} className="p-1 relative group">Investment Type
//                           <div onMouseDown={(e) => handleMouseDown('reviewed', 'type', e)} onDoubleClick={() => handleDoubleClick('reviewed')} className="absolute right-0 top-0 bottom-0 w-1 bg-purple-500/0 group-hover:bg-purple-500/30 cursor-col-resize" />
//                         </th>
//                         <th style={{ width: reviewedWidths.amount }} className="p-1 text-right relative group">Amount
//                           <div onMouseDown={(e) => handleMouseDown('reviewed', 'amount', e)} onDoubleClick={() => handleDoubleClick('reviewed')} className="absolute right-0 top-0 bottom-0 w-1 bg-purple-500/0 group-hover:bg-purple-500/30 cursor-col-resize" />
//                         </th>
//                         <th style={{ width: reviewedWidths.status }} className="p-1 text-center relative group">Outcome
//                           <div onMouseDown={(e) => handleMouseDown('reviewed', 'status', e)} onDoubleClick={() => handleDoubleClick('reviewed')} className="absolute right-0 top-0 bottom-0 w-1 bg-purple-500/0 group-hover:bg-purple-500/30 cursor-col-resize" />
//                         </th>
//                         <th style={{ width: reviewedWidths.notes }} className="p-1 pl-3 relative group">Auditor Justification Notes</th>
//                       </tr>
//                     </thead>
//                     <tbody className="divide-y divide-slate-800/30">
//                       {workflow.reviewedCasesList.map((c, i) => {
//                         const s = workflow.caseStates[c.trade_id];
//                         const isSelected = workflow.selectedCase?.trade_id === c?.trade_id;
//                         return (
//                           <tr key={`${c.trade_id}-${i}`} onClick={() => workflow.selectCase(c)} className={`cursor-pointer text-[11px] ${isSelected ? 'bg-emerald-950/40 font-semibold border-l-2 border-emerald-500 text-emerald-200' : 'hover:bg-slate-800/20 text-slate-300'}`}>
//                             <td className="p-1 font-mono truncate">{c.trade_id}</td>
//                             <td className="p-1 truncate">{c.investment_type || "N/A"}</td>
//                             <td className="p-1 text-right font-mono text-emerald-400 truncate">${Number(c.investment_amount || 0).toLocaleString()}</td>
//                             <td className="p-1 text-center truncate">
//                               <span className={`px-2 py-0.5 rounded text-[9px] font-bold ${s?.userAction === 'Approved' ? 'bg-emerald-950 text-emerald-400 border border-emerald-900/30' : s?.userAction === 'Rejected' ? 'bg-rose-950 text-rose-400 border border-rose-900/30' : 'bg-amber-950 text-amber-400 border border-amber-900/30'}`}>
//                                 {s?.userAction || 'Processed'}
//                               </span>
//                             </td>
//                             <td className="p-1 pl-3 italic text-slate-400 truncate">{s?.notes || "—"}</td>
//                           </tr>
//                         );
//                       })}
//                     </tbody>
//                   </table>
//                 )}
//               </div>
//             </div>
//           )}

//           {/* Table 4: Scrollable Resizable Passed View Panel */}
//           {workflow.activeView === "passed" && (
//             <div className="bg-slate-900 border border-slate-800 rounded-md p-1.5 flex flex-col h-full min-h-0">
//               <div className="flex items-center gap-1 border-b border-slate-800 pb-0.5 mb-1 shrink-0">
//                 <CheckCircle className="w-3.5 h-3.5 text-indigo-400" />
//                 <h2 className="text-[10px] font-bold text-indigo-400 uppercase tracking-wider">System Automatic Clearance Log</h2>
//               </div>
//               <div className="flex-1 overflow-x-auto overflow-y-auto border border-slate-800/30 rounded dynamic-scroll min-h-0">
//                 {workflow.passedCasesList.length === 0 ? <p className="text-slate-500 text-xs p-3 italic text-center">No auto-passed logs found.</p> : (
//                   <table className="text-left text-xs border-collapse table-fixed w-max min-w-full">
//                     <thead className="sticky top-0 bg-slate-900 text-slate-400 font-bold uppercase text-[9px] border-b border-slate-800 z-10">
//                       <tr>
//                         <th style={{ width: passedWidths.tradeId }} className="p-1 relative group">Trade ID
//                           <div onMouseDown={(e) => handleMouseDown('passed', 'tradeId', e)} onDoubleClick={() => handleDoubleClick('passed')} className="absolute right-0 top-0 bottom-0 w-1 bg-purple-500/0 group-hover:bg-purple-500/30 cursor-col-resize" />
//                         </th>
//                         <th style={{ width: passedWidths.asset }} className="p-1 relative group">Asset Class
//                           <div onMouseDown={(e) => handleMouseDown('passed', 'asset', e)} onDoubleClick={() => handleDoubleClick('passed')} className="absolute right-0 top-0 bottom-0 w-1 bg-purple-500/0 group-hover:bg-purple-500/30 cursor-col-resize" />
//                         </th>
//                         <th style={{ width: passedWidths.value }} className="p-1 text-right relative group">Notional Value
//                           <div onMouseDown={(e) => handleMouseDown('passed', 'value', e)} onDoubleClick={() => handleDoubleClick('passed')} className="absolute right-0 top-0 bottom-0 w-1 bg-purple-500/0 group-hover:bg-purple-500/30 cursor-col-resize" />
//                         </th>
//                         <th style={{ width: passedWidths.confidence }} className="p-1 text-right relative group">Confidence Score
//                           <div onMouseDown={(e) => handleMouseDown('passed', 'confidence', e)} onDoubleClick={() => handleDoubleClick('passed')} className="absolute right-0 top-0 bottom-0 w-1 bg-purple-500/0 group-hover:bg-purple-500/30 cursor-col-resize" />
//                         </th>
//                         <th style={{ width: passedWidths.status }} className="p-1 text-center relative group">Clearance Status</th>
//                       </tr>
//                     </thead>
//                     <tbody className="divide-y divide-slate-800/30">
//                       {workflow.passedCasesList.map((c, i) => {
//                         const isSelected = workflow.selectedCase?.trade_id === c?.trade_id;
//                         return (
//                           <tr key={`${c.trade_id}-${i}`} onClick={() => workflow.selectCase(c)} className={`cursor-pointer text-[11px] ${isSelected ? 'bg-indigo-950/40 font-semibold border-l-2 border-indigo-500 text-indigo-200' : 'hover:bg-slate-800/20 text-slate-300'}`}>
//                             <td className="p-1 font-mono truncate">{c.trade_id}</td>
//                             <td className="p-1 truncate">{c.investment_type || "N/A"}</td>
//                             <td className="p-1 text-right font-mono truncate">${Number(c.notional_value || 0).toLocaleString()}</td>
//                             <td className="p-1 text-right font-mono text-sky-400 truncate">{(c.confidence_score || 1).toFixed(4)}</td>
//                             <td className="p-1 text-center truncate">
//                               <span className="text-[9px] font-bold bg-emerald-950/30 text-emerald-400 px-2 py-0.5 rounded border border-emerald-900/20">Passed Engine</span>
//                             </td>
//                           </tr>
//                         );
//                       })}
//                     </tbody>
//                   </table>
//                 )}
//               </div>
//             </div>
//           )}
//         </div>

//         {/* LOWER WORKSPACE AREA (Expansive 60% Form Layout Framework) */}
//         <div className="bg-slate-900 border border-slate-800 rounded-md p-3 flex flex-col min-h-0 justify-between shadow-2xl">
//           {workflow.selectedCase ? (() => {
//             const c = workflow.selectedCase;
//             const currentState = workflow.caseStates[c.trade_id] || { reviewStatus: "Not reviewed", notes: "" };
//             const riskVal = 1 - (Number(c.compliance_probability) || 0);
//             const isRecCompliant = (currentState.overriddenLabel || c.compliance_label || "").toLowerCase() === "compliant";

//             return (
//               <div className="flex flex-col h-full justify-between min-h-0 space-y-3">
                
//                 {/* Workspace Module header block */}
//                 <div className="flex items-center justify-between border-b border-slate-800 pb-2 shrink-0">
//                   <div className="flex items-center gap-2">
//                     <span className="text-[9px] font-black uppercase bg-purple-950/40 px-2 py-0.5 rounded border border-purple-900/50 text-purple-400 tracking-wider">Selected Case Audit Space</span>
//                     <span className="text-xs font-mono font-bold text-slate-100 bg-slate-950 px-2 py-0.5 rounded border border-slate-800">{c.trade_id}</span>
//                   </div>

//                   {/* Score metrics block badge at top-right position */}
//                   <div className="flex items-center gap-2 bg-slate-950/60 px-2.5 py-1 rounded-md border border-slate-800/80 text-[10px] font-mono">
//                     <div className="flex items-center gap-1.5 border-r border-slate-800 pr-2">
//                       <span className="text-slate-500 font-sans text-[9px] font-bold uppercase">AI Rec:</span>
//                       <span className={`px-1 rounded text-[9px] font-black ${isRecCompliant ? "bg-emerald-950 text-emerald-400" : "bg-rose-950 text-rose-400"}`}>
//                         {isRecCompliant ? "COMPLIANT" : "FLAGGED"}
//                       </span>
//                     </div>
//                     <div className="flex items-center gap-1.5 border-r border-slate-800 pr-2 pl-1">
//                       <span className="text-slate-500 font-sans text-[9px] font-bold uppercase">Risk:</span>
//                       <span className="text-rose-400 font-bold">{riskVal.toFixed(3)}</span>
//                     </div>
//                     <div className="flex items-center gap-1.5 pl-1">
//                       <span className="text-slate-500 font-sans text-[9px] font-bold uppercase">Conf:</span>
//                       <span className="text-sky-400 font-bold">{Number(c.confidence_score || 0).toFixed(3)}</span>
//                     </div>
//                   </div>
//                 </div>

//                 {/* Expanded 3 Column Matrix Grid Layout (Spaced for high-density zero overlap readability) */}
//                 <div className="grid grid-cols-3 gap-3 flex-1 min-h-0 py-1">
                  
//                   {/* MODULE A: Trade Details */}
//                   <div className="bg-slate-950/30 border border-slate-800/60 p-3 rounded-lg flex flex-col justify-between">
//                     <div className="flex items-center gap-1.5 border-b border-slate-800/80 pb-1.5 mb-2 text-purple-400 text-[10px] font-black uppercase tracking-widest shrink-0">
//                       <Briefcase className="w-3.5 h-3.5"/>
//                       <span>Trade Details</span>
//                     </div>
//                     <div className="text-xs grid grid-cols-2 gap-x-3 gap-y-3 flex-1 items-center text-slate-300">
//                       <div><span className="text-slate-500 text-[9px] uppercase font-bold tracking-wider block mb-0.5">Type</span><div className="truncate font-semibold text-slate-200">{c.investment_type || "N/A"}</div></div>
//                       <div><span className="text-slate-500 text-[9px] uppercase font-bold tracking-wider block mb-0.5">Amount</span><div className="truncate font-mono font-black text-emerald-400">${Number(c.investment_amount || 0).toLocaleString()}</div></div>
//                       <div><span className="text-slate-500 text-[9px] uppercase font-bold tracking-wider block mb-0.5">Notional</span><div className="truncate font-mono font-medium text-slate-400">${Number(c.notional_value || 0).toLocaleString()}</div></div>
//                       <div><span className="text-slate-500 text-[9px] uppercase font-bold tracking-wider block mb-0.5">Timestamp</span><div className="truncate font-mono text-[10px] text-slate-400">{c.timestamp || c.timestamp_utc || c.created_at || "—"}</div></div>
//                     </div>
//                   </div>

//                   {/* MODULE B: Client Profile */}
//                   <div className="bg-slate-950/30 border border-slate-800/60 p-3 rounded-lg flex flex-col justify-between">
//                     <div className="flex items-center gap-1.5 border-b border-slate-800/80 pb-1.5 mb-2 text-sky-400 text-[10px] font-black uppercase tracking-widest shrink-0">
//                       <User className="w-3.5 h-3.5"/>
//                       <span>Client Profile</span>
//                     </div>
//                     <div className="text-xs grid grid-cols-2 gap-x-3 gap-y-2 flex-1 items-center text-slate-300">
//                       <div><span className="text-slate-500 text-[9px] uppercase font-bold tracking-wider block mb-0.5">Age / Income</span><div className="truncate font-mono font-semibold text-slate-200">{c.client_age ?? "—"} / ${Math.round((c.client_income || 0)/1000)}k</div></div>
//                       <div><span className="text-slate-500 text-[9px] uppercase font-bold tracking-wider block mb-0.5">Risk Profile</span><div className="truncate font-black text-amber-400">{c.risk_tolerance || "—"}</div></div>
//                       <div><span className="text-slate-500 text-[9px] uppercase font-bold tracking-wider block mb-0.5">Experience</span><div className="truncate text-slate-400">{c.investment_experience || "—"}</div></div>
//                       <div><span className="text-slate-500 text-[9px] uppercase font-bold tracking-wider block mb-0.5">Objective</span><div className="truncate text-slate-400 font-medium">{c.investment_objective || "—"}</div></div>
//                       <div className="col-span-2"><span className="text-slate-500 text-[9px] uppercase font-bold tracking-wider block mb-0.5">Time Horizon</span><div className="truncate text-indigo-300 font-medium">{c.investment_time_horizon || "—"}</div></div>
//                     </div>
//                   </div>

//                   {/* MODULE C: Rationale Text Block */}
//                   <div className="bg-slate-950/30 border border-slate-800/60 p-3 rounded-lg flex flex-col min-h-0">
//                     <div className="flex items-center justify-between border-b border-slate-800/80 pb-1.5 mb-2 shrink-0">
//                       <div className="flex items-center gap-1.5 text-amber-400 text-[10px] font-black uppercase tracking-widest">
//                         <FileText className="w-3.5 h-3.5"/>
//                         <span>Rationale</span>
//                       </div>
//                       <span className={`text-[9px] font-bold px-1.5 py-0.5 rounded ${c.has_rationale ? 'bg-emerald-950/80 text-emerald-400 border border-emerald-900/40' : 'bg-slate-950 text-slate-500'}`}>
//                         {c.has_rationale ? "FILED" : "MISSING"}
//                       </span>
//                     </div>
//                     <div className="flex-1 bg-slate-950/50 rounded border border-slate-800 p-2 overflow-y-auto text-[11px] leading-relaxed text-slate-300 font-mono italic">
//                       {c.advisor_notes || "No advisory filing notes or desk justification provided for this transaction."}
//                     </div>
//                   </div>
//                 </div>

//                 {/* Policy Compliance Framework Bar Row */}
//                 <div className="border-t border-slate-800/80 pt-2 shrink-0 items-center bg-slate-950/40 p-2 rounded-lg text-xs flex justify-between gap-4">
//                   <div className="flex items-center gap-2 truncate max-w-xl">
//                     <HelpCircle className="w-4 h-4 text-rose-400 shrink-0"/>
//                     <span className="text-[9px] uppercase text-slate-500 font-black tracking-wider shrink-0">Reasoning Summary:</span>
//                     <span className="text-rose-300 font-semibold truncate text-[11px]">{c.flag_reason || "None."}</span>
//                   </div>
//                   <div className="flex items-center gap-1.5 overflow-hidden truncate">
//                     <span className="text-[9px] uppercase text-slate-600 font-black tracking-wider shrink-0">Attached Regulations:</span>
//                     <div className="flex gap-1 items-center truncate">{renderPolicies(c.retrieved_policies)}</div>
//                   </div>
//                 </div>

//                 {/* Execution Signature Action Form Tray */}
//                 <div className="pt-1 flex gap-3 items-end shrink-0 border-t border-slate-800/40">
//                   <div className="flex-1 flex flex-col">
//                     <label className="text-[9px] font-black text-slate-400 uppercase tracking-widest mb-1">Reviewer Sign-off Justification Matrix</label>
//                     <input type="text" value={currentNotes} onChange={(e) => handleNotesChange(e.target.value)} placeholder="Type definitive legal compliance assessment or operational arguments..." className="w-full bg-slate-950 border border-slate-800 rounded px-2.5 text-xs text-slate-200 focus:outline-none focus:border-indigo-500 transition-all shadow-inner h-8" />
//                   </div>
//                   <div className="flex gap-2 h-8">
//                     <button onClick={() => workflow.executeAction(c.trade_id, "Reviewed", "Rejected", currentNotes)} className="bg-rose-600 hover:bg-rose-500 text-white font-black text-[10px] px-4 rounded flex items-center gap-1.5 uppercase tracking-wider shadow-md transition-colors"><X className="w-3.5 h-3.5"/>Reject Trade</button>
//                     <button onClick={() => workflow.executeAction(c.trade_id, "Reviewed", "Approved", currentNotes)} className="bg-emerald-600 hover:bg-emerald-500 text-slate-950 font-black text-[10px] px-4 rounded flex items-center gap-1.5 uppercase tracking-wider shadow-md transition-colors"><Check className="w-3.5 h-3.5"/>Approve Trade</button>
//                     <button onClick={() => workflow.executeAction(c.trade_id, "Escalated", "Escalated", currentNotes)} className="bg-slate-800 hover:bg-slate-700 text-amber-400 border border-slate-700 font-black text-[10px] px-4 rounded flex items-center gap-1.5 uppercase tracking-wider shadow-md transition-colors"><CornerUpRight className="w-3.5 h-3.5"/>Escalate Review</button>
//                   </div>
//                 </div>

//               </div>
//             );
//           })() : (
//             <div className="h-full flex flex-col items-center justify-center text-slate-500 text-xs font-semibold border border-dashed border-slate-800 rounded p-6 text-center bg-slate-950/20">
//               <CheckCircle className="w-10 h-10 text-emerald-500/30 mb-2" />
//               <span className="text-slate-400 font-bold uppercase tracking-wider text-[11px]">All Tasks Cleared</span>
//               <p className="text-[10px] text-slate-600 font-normal max-w-xs mt-1">Select an item from any active stream or historical tab above to evaluate details.</p>
//             </div>
//           )}
//         </div>

//       </div>
//     </div>
//   );
// }

// export default Dashboard;

// /* VERSION 8 */

// import { useEffect, useState, useRef } from "react";
// import { getCases } from "../api/cases";
// import { AlertCircle, CheckCircle, Clock, ShieldAlert, FileText, User, Briefcase, HelpCircle, Check, X, CornerUpRight } from "lucide-react";

// interface CaseAuditState {
//   reviewStatus: "Reviewed" | "Not reviewed" | "Escalated";
//   notes: string;
//   overriddenLabel?: string;
//   userAction?: "Rejected" | "Approved" | "Escalated"; // Track exact action chosen
// }

// function Dashboard() {
//   // --- Navigation Tabs ---
//   const [activeView, setActiveView] = useState<"active" | "reviewed" | "passed">("active");

//   const [cases, setCases] = useState<any[]>([]);
//   const [selectedCase, setSelectedCase] = useState<any | null>(null);
  
//   // Per-case persistence engine keyed by trade_id
//   const [caseStates, setCaseStates] = useState<Record<string, CaseAuditState>>({});
//   const [currentNotes, setCurrentNotes] = useState<string>("");
//   const [reviewedTodayCount, setReviewedTodayCount] = useState<number>(0);

//   // --- Spreadsheet Column Resize State ---
//   const [urgentWidths, setUrgentWidths] = useState({ tradeId: 100, risk: 75, conf: 75, reason: 260 });
//   const [queuedWidths, setQueuedWidths] = useState({ tradeId: 100, priority: 70, risk: 75, conf: 75, reason: 240 });

//   const dragInfo = useRef<{ table: 'urgent' | 'queued'; col: string; startX: number; startWidth: number } | null>(null);

//   useEffect(() => {
//     getCases()
//       .then((data) => {
//         if (Array.isArray(data)) {
//           setCases(data);
          
//           // Seed initial default auditing structures for all fetched trades
//           const initialStates: Record<string, CaseAuditState> = {};
//           data.forEach((c) => {
//             if (c?.trade_id) {
//               initialStates[c.trade_id] = { 
//                 reviewStatus: "Not reviewed", 
//                 notes: "",
//                 overriddenLabel: c.compliance_label || "Non-compliant"
//               };
//             }
//           });
//           setCaseStates(initialStates);

//           const urgentCases = data.filter((c) => c?.escalation_level === "urgent");
//           const queuedCases = data
//             .filter((c) => c?.escalation_level === "priority" || c?.escalation_level === "queue")
//             .sort((a, b) => (Number(b?.priority_score) || 0) - (Number(a?.priority_score) || 0));

//           if (urgentCases.length > 0) handleCaseSelection(urgentCases[0], initialStates);
//           else if (queuedCases.length > 0) handleCaseSelection(queuedCases[0], initialStates);
//         }
//       })
//       .catch((err) => console.error("API Fetch Error:", err));
//   }, []);

//   const handleCaseSelection = (targetCase: any, latestStates = caseStates) => {
//     setSelectedCase(targetCase);
//     if (targetCase?.trade_id) {
//       const savedState = latestStates[targetCase.trade_id];
//       setCurrentNotes(savedState ? savedState.notes : "");
//     }
//   };

//   const handleNotesChange = (text: string) => {
//     setCurrentNotes(text);
//     if (selectedCase?.trade_id) {
//       setCaseStates(prev => ({
//         ...prev,
//         [selectedCase.trade_id]: {
//           ...prev[selectedCase.trade_id],
//           notes: text
//         }
//       }));
//     }
//   };

//   // --- Automated Focus Triage Workflow Engine ---
//   const advanceTriageFocus = (completedTradeId: string) => {
//     const currentUrgentRemaining = cases.filter((c) => c?.escalation_level === "urgent" && caseStates[c.trade_id]?.reviewStatus === "Not reviewed" && c.trade_id !== completedTradeId);
//     const currentQueuedRemaining = cases
//       .filter((c) => (c?.escalation_level === "priority" || c?.escalation_level === "queue") && caseStates[c.trade_id]?.reviewStatus === "Not reviewed" && c.trade_id !== completedTradeId)
//       .sort((a, b) => (Number(b?.priority_score) || 0) - (Number(a?.priority_score) || 0));

//     const currentCase = cases.find(c => c.trade_id === completedTradeId);
//     const wasUrgent = currentCase?.escalation_level === "urgent";

//     let nextCase: any | null = null;

//     if (wasUrgent) {
//       const targetIndex = urgentCases.findIndex(c => c.trade_id === completedTradeId);
//       const activeUrgentPool = urgentCases.filter(c => caseStates[c.trade_id]?.reviewStatus === "Not reviewed" && c.trade_id !== completedTradeId);
      
//       if (activeUrgentPool.length > 0) {
//         const nextIndex = Math.min(targetIndex, activeUrgentPool.length - 1);
//         nextCase = activeUrgentPool[nextIndex >= 0 ? nextIndex : 0];
//       } else if (currentQueuedRemaining.length > 0) {
//         nextCase = currentQueuedRemaining[0];
//       }
//     } else {
//       const targetIndex = queuedCases.findIndex(c => c.trade_id === completedTradeId);
//       const activeQueuedPool = queuedCases.filter(c => caseStates[c.trade_id]?.reviewStatus === "Not reviewed" && c.trade_id !== completedTradeId);
      
//       if (activeQueuedPool.length > 0) {
//         const nextIndex = Math.min(targetIndex, activeQueuedPool.length - 1);
//         nextCase = activeQueuedPool[nextIndex >= 0 ? nextIndex : 0];
//       } else if (currentUrgentRemaining.length > 0) {
//         nextCase = currentUrgentRemaining[0];
//       }
//     }

//     if (nextCase) {
//       handleCaseSelection(nextCase);
//     } else {
//       setSelectedCase(null);
//     }
//     setReviewedTodayCount(prev => prev + 1);
//   };

//   // --- Unified Audit Action Pipeline ---
//   const executeAuditAction = (status: "Reviewed" | "Escalated", actionType: "Rejected" | "Approved" | "Escalated") => {
//     if (!selectedCase?.trade_id) return;
//     const targetId = selectedCase.trade_id;

//     setCaseStates(prev => ({
//       ...prev,
//       [targetId]: {
//         ...prev[targetId],
//         reviewStatus: status,
//         userAction: actionType,
//         notes: currentNotes
//       }
//     }));

//     advanceTriageFocus(targetId);
//   };

//   // --- Mouse Resize Handlers ---
//   const handleMouseDown = (table: 'urgent' | 'queued', col: string, e: React.MouseEvent) => {
//     e.preventDefault();
//     const currentWidths = table === 'urgent' ? urgentWidths : queuedWidths;
//     dragInfo.current = {
//       table,
//       col,
//       startX: e.clientX,
//       startWidth: (currentWidths as any)[col]
//     };
//     document.addEventListener("mousemove", handleMouseMove);
//     document.addEventListener("mouseup", handleMouseUp);
//   };

//   const handleMouseMove = (e: MouseEvent) => {
//     if (!dragInfo.current) return;
//     const { table, col, startX, startWidth } = dragInfo.current;
//     const deltaX = e.clientX - startX;
//     const newWidth = Math.max(50, startWidth + deltaX);

//     if (table === 'urgent') {
//       setUrgentWidths(prev => ({ ...prev, [col]: newWidth }));
//     } else {
//       setQueuedWidths(prev => ({ ...prev, [col]: newWidth }));
//     }
//   };

//   const handleMouseUp = () => {
//     dragInfo.current = null;
//     document.removeEventListener("mousemove", handleMouseMove);
//     document.removeEventListener("mouseup", handleMouseUp);
//   };

//   const handleDoubleClick = (table: 'urgent' | 'queued') => {
//     if (table === 'urgent') {
//       setUrgentWidths({ tradeId: 100, risk: 75, conf: 75, reason: 260 });
//     } else {
//       setQueuedWidths({ tradeId: 100, priority: 70, risk: 75, conf: 75, reason: 240 });
//     }
//   };

//   // --- Reactive Subqueue Computing ---
//   const urgentCases = cases.filter((c) => c?.escalation_level === "urgent" && caseStates[c.trade_id]?.reviewStatus === "Not reviewed");
//   const queuedCases = cases
//     .filter((c) => (c?.escalation_level === "priority" || c?.escalation_level === "queue") && caseStates[c.trade_id]?.reviewStatus === "Not reviewed")
//     .sort((a, b) => (Number(b?.priority_score) || 0) - (Number(a?.priority_score) || 0));

//   // Items designated as manually processed by the auditor
//   const reviewedCasesList = cases.filter((c) => caseStates[c.trade_id]?.reviewStatus === "Reviewed" || caseStates[c.trade_id]?.reviewStatus === "Escalated");
  
//   // Telemetry items filtered as automated passed stream from backend
//   const passedCasesList = cases.filter(
//     (c) => c?.escalation_level !== "urgent" && c?.escalation_level !== "priority" && c?.escalation_level !== "queue"
//   );

//   const countActiveTotal = urgentCases.length + queuedCases.length;
//   const countPassedTotal = passedCasesList.length;

//   const renderPolicies = (policies: any) => {
//     if (!policies) return <span className="text-[10px] text-slate-500">No policies attached.</span>;
//     let items: string[] = [];
//     if (Array.isArray(policies)) items = policies;
//     else if (typeof policies === "string" && policies.startsWith("[")) {
//       items = policies.replace(/[\[\]']/g, "").split(",").map((p) => p.trim()).filter(Boolean);
//     } else if (typeof policies === "string" && policies.trim().length > 0) {
//       items = policies.split(",").map((p) => p.trim());
//     }
    
//     if (items.length === 0) return <span className="text-[10px] text-slate-500">No policies attached.</span>;
//     return items.map((policy, i) => (
//       <span key={i} className="px-1.5 py-0.5 bg-slate-950 text-[10px] rounded border border-slate-800 text-purple-300 font-mono">
//         {policy}
//       </span>
//     ));
//   };

//   return (
//     <div className="p-2 h-screen bg-slate-950 text-slate-100 flex flex-col gap-2 overflow-hidden select-none">
      
//       <style>{`
//         .dynamic-scroll { scrollbar-width: none; }
//         .dynamic-scroll::-webkit-scrollbar { width: 4px; height: 4px; display: none; }
//         .dynamic-scroll:hover { scrollbar-width: thin; }
//         .dynamic-scroll:hover::-webkit-scrollbar { display: block; }
//         .dynamic-scroll::-webkit-scrollbar-track { background: transparent; }
//         .dynamic-scroll::-webkit-scrollbar-thumb { background: rgba(148, 163, 184, 0.15); border-radius: 2px; }
//       `}</style>
      
//       {/* Top Header Metrics Layer */}
//       <div className="flex items-center justify-between border-b border-slate-900 pb-2">
//         <div className="flex items-center gap-6">
//           <h1 className="text-base font-bold tracking-tight text-slate-200">
//             AI Compliance Review Copilot
//           </h1>
          
//           {/* Tab Selection Navigation Interface Row */}
//           <div className="flex bg-slate-900 p-0.5 rounded border border-slate-800 gap-0.5">
//             <button 
//               onClick={() => setActiveView("active")}
//               className={`px-4 py-1 text-xs font-semibold rounded transition-all ${activeView === 'active' ? 'bg-indigo-600 text-white shadow' : 'text-slate-400 hover:text-slate-200'}`}
//             >
//               Active ({countActiveTotal})
//             </button>
//             <button 
//               onClick={() => setActiveView("reviewed")}
//               className={`px-4 py-1 text-xs font-semibold rounded transition-all ${activeView === 'reviewed' ? 'bg-indigo-600 text-white shadow' : 'text-slate-400 hover:text-slate-200'}`}
//             >
//               Reviewed
//             </button>
//             <button 
//               onClick={() => setActiveView("passed")}
//               className={`px-4 py-1 text-xs font-semibold rounded transition-all ${activeView === 'passed' ? 'bg-indigo-600 text-white shadow' : 'text-slate-400 hover:text-slate-200'}`}
//             >
//               Passed ({countPassedTotal})
//             </button>
//           </div>
//         </div>
        
//         {/* Metric Counters Tracking Block Row */}
//         <div className="flex items-center gap-2">
//           <div className="bg-amber-950/30 border border-amber-500/30 rounded px-3 py-1 flex items-center gap-2 text-xs font-medium shadow-sm">
//             <Clock className="w-3.5 h-3.5 text-amber-400" />
//             <span className="text-amber-300">Active Queue:</span>
//             <span className="text-sm font-black text-amber-100">{countActiveTotal}</span>
//           </div>

//           <div className="bg-emerald-950/30 border border-emerald-500/30 rounded px-3 py-1 flex items-center gap-2 text-xs font-medium shadow-sm">
//             <CheckCircle className="w-3.5 h-3.5 text-emerald-400" />
//             <span className="text-emerald-300">Reviewed Today:</span>
//             <span className="text-sm font-black text-emerald-100">{reviewedTodayCount}</span>
//           </div>
//         </div>
//       </div>

//       {/* Main Viewport Upper/Lower Layout Frame */}
//       <div className="flex-1 grid grid-rows-[48fr_52fr] gap-2 min-h-0">
        
//         {/* UPPER VIEW: Shared Placement Segment Container Compartment */}
//         <div className="min-h-0">
          
//           {activeView === "active" && (
//             <div className="grid grid-cols-2 gap-2 h-full min-h-0">
//               {/* URGENT TRACK PANEL */}
//               <div className="bg-slate-900 border border-rose-500/10 rounded-md p-1.5 flex flex-col min-h-0">
//                 <div className="flex items-center gap-1 border-b border-slate-800 pb-0.5 mb-1">
//                   <ShieldAlert className="w-3.5 h-3.5 text-rose-400" />
//                   <h2 className="text-[10px] font-bold text-rose-400 uppercase tracking-wider">Urgent Action Required</h2>
//                 </div>
                
//                 <div className="flex-1 overflow-auto min-h-0 relative border border-slate-800/30 rounded dynamic-scroll">
//                   {urgentCases.length === 0 ? (
//                     <p className="text-xs text-slate-500 p-2 italic">No urgent cases outstanding.</p>
//                   ) : (
//                     <table className="text-left text-xs border-collapse table-fixed w-max min-w-full">
//                       <thead className="sticky top-0 bg-slate-900 text-slate-400 font-bold uppercase text-[9px] border-b border-slate-800 z-10">
//                         <tr>
//                           <th style={{ width: urgentWidths.tradeId }} className="p-1 relative group">
//                             Trade ID
//                             <div onMouseDown={(e) => handleMouseDown('urgent', 'tradeId', e)} onDoubleClick={() => handleDoubleClick('urgent')} className="absolute right-0 top-0 bottom-0 w-1 bg-slate-700/0 group-hover:bg-purple-500/50 cursor-col-resize transition-colors" />
//                           </th>
//                           <th style={{ width: urgentWidths.risk }} className="p-1 text-right relative group">
//                             Risk Score
//                             <div onMouseDown={(e) => handleMouseDown('urgent', 'risk', e)} onDoubleClick={() => handleDoubleClick('urgent')} className="absolute right-0 top-0 bottom-0 w-1 bg-slate-700/0 group-hover:bg-purple-500/50 cursor-col-resize transition-colors" />
//                           </th>
//                           <th style={{ width: urgentWidths.conf }} className="p-1 text-right relative group">
//                             Conf.
//                             <div onMouseDown={(e) => handleMouseDown('urgent', 'conf', e)} onDoubleClick={() => handleDoubleClick('urgent')} className="absolute right-0 top-0 bottom-0 w-1 bg-slate-700/0 group-hover:bg-purple-500/50 cursor-col-resize transition-colors" />
//                           </th>
//                           <th style={{ width: urgentWidths.reason }} className="p-1 pl-2 relative group">
//                             Flag Reason
//                             <div onMouseDown={(e) => handleMouseDown('urgent', 'reason', e)} onDoubleClick={() => handleDoubleClick('urgent')} className="absolute right-0 top-0 bottom-0 w-1 bg-slate-700/0 group-hover:bg-purple-500/50 cursor-col-resize transition-colors" />
//                           </th>
//                         </tr>
//                       </thead>
//                       <tbody className="divide-y divide-slate-800/30">
//                         {urgentCases.map((c, idx) => {
//                           const isSelected = selectedCase?.trade_id === c?.trade_id;
//                           const riskVal = 1 - (Number(c?.compliance_probability) ?? 1.0);
//                           return (
//                             <tr
//                               key={`${c?.trade_id}-${idx}`}
//                               onClick={() => handleCaseSelection(c)}
//                               className={`cursor-pointer text-[11px] transition-colors ${isSelected ? 'bg-rose-950/40 font-semibold border-l-2 border-rose-500 text-rose-200 shadow-[inner_0_1px_0_rgba(244,63,94,0.1)]' : 'hover:bg-slate-800/30 text-slate-300'}`}
//                             >
//                               <td className="p-1 font-mono truncate">{c?.trade_id}</td>
//                               <td className="p-1 text-right font-mono text-rose-400/90">{riskVal.toFixed(2)}</td>
//                               <td className="p-1 text-right font-mono text-slate-400">{(Number(c?.confidence_score) || 0).toFixed(2)}</td>
//                               <td className="p-1 pl-2 truncate text-[10px]">{c?.flag_reason}</td>
//                             </tr>
//                           );
//                         })}
//                       </tbody>
//                     </table>
//                   )}
//                 </div>
//               </div>

//               {/* REVIEW QUEUE PANEL */}
//               <div className="bg-slate-900 border border-slate-800/80 rounded-md p-1.5 flex flex-col min-h-0">
//                 <div className="flex items-center gap-1 border-b border-slate-800 pb-0.5 mb-1">
//                   <Clock className="w-3.5 h-3.5 text-amber-400" />
//                   <h2 className="text-[10px] font-bold text-amber-400 uppercase tracking-wider">Review</h2>
//                 </div>
                
//                 <div className="flex-1 overflow-auto min-h-0 relative border border-slate-800/30 rounded dynamic-scroll">
//                   {queuedCases.length === 0 ? (
//                     <p className="text-xs text-slate-500 p-1 italic">Review queue empty.</p>
//                   ) : (
//                     <table className="text-left text-xs border-collapse table-fixed w-max min-w-full">
//                       <thead className="sticky top-0 bg-slate-900 text-slate-400 font-bold uppercase text-[9px] border-b border-slate-800 z-10">
//                         <tr>
//                           <th style={{ width: queuedWidths.tradeId }} className="p-1 relative group">
//                             Trade ID
//                             <div onMouseDown={(e) => handleMouseDown('queued', 'tradeId', e)} onDoubleClick={() => handleDoubleClick('queued')} className="absolute right-0 top-0 bottom-0 w-1 bg-slate-700/0 group-hover:bg-purple-500/50 cursor-col-resize transition-colors" />
//                           </th>
//                           <th style={{ width: queuedWidths.priority }} className="p-1 text-right relative group text-amber-400">
//                             Priority
//                             <div onMouseDown={(e) => handleMouseDown('queued', 'priority', e)} onDoubleClick={() => handleDoubleClick('queued')} className="absolute right-0 top-0 bottom-0 w-1 bg-slate-700/0 group-hover:bg-purple-500/50 cursor-col-resize transition-colors" />
//                           </th>
//                           <th style={{ width: queuedWidths.risk }} className="p-1 text-right relative group">
//                             Risk Score
//                             <div onMouseDown={(e) => handleMouseDown('queued', 'risk', e)} onDoubleClick={() => handleDoubleClick('queued')} className="absolute right-0 top-0 bottom-0 w-1 bg-slate-700/0 group-hover:bg-purple-500/50 cursor-col-resize transition-colors" />
//                           </th>
//                           <th style={{ width: queuedWidths.conf }} className="p-1 text-right relative group">
//                             Conf.
//                             <div onMouseDown={(e) => handleMouseDown('queued', 'conf', e)} onDoubleClick={() => handleDoubleClick('queued')} className="absolute right-0 top-0 bottom-0 w-1 bg-slate-700/0 group-hover:bg-purple-500/50 cursor-col-resize transition-colors" />
//                           </th>
//                           <th style={{ width: queuedWidths.reason }} className="p-1 pl-2 relative group">
//                             Flag Reason
//                             <div onMouseDown={(e) => handleMouseDown('queued', 'reason', e)} onDoubleClick={() => handleDoubleClick('queued')} className="absolute right-0 top-0 bottom-0 w-1 bg-slate-700/0 group-hover:bg-purple-500/50 cursor-col-resize transition-colors" />
//                           </th>
//                         </tr>
//                       </thead>
//                       <tbody className="divide-y divide-slate-800/30">
//                         {queuedCases.map((c, idx) => {
//                           const isSelected = selectedCase?.trade_id === c?.trade_id;
//                           const riskVal = 1 - (Number(c?.compliance_probability) ?? 1.0);
//                           return (
//                             <tr
//                               key={`${c?.trade_id}-${idx}`}
//                               onClick={() => handleCaseSelection(c)}
//                               className={`cursor-pointer text-[11px] transition-colors ${isSelected ? 'bg-purple-950/40 font-semibold border-l-2 border-purple-500 text-purple-200 shadow-[inner_0_1px_0_rgba(168,85,247,0.1)]' : 'hover:bg-slate-800/30 text-slate-300'}`}
//                             >
//                               <td className="p-1 font-mono truncate">{c?.trade_id}</td>
//                               <td className="p-1 text-right font-mono font-bold text-amber-400">{c?.priority_score ?? "0"}</td>
//                               <td className="p-1 text-right font-mono text-rose-400/90">{riskVal.toFixed(2)}</td>
//                               <td className="p-1 text-right font-mono text-slate-400">{(Number(c?.confidence_score) || 0).toFixed(2)}</td>
//                               <td className="p-1 pl-2 truncate text-[10px]">{c?.flag_reason}</td>
//                             </tr>
//                           );
//                         })}
//                       </tbody>
//                     </table>
//                   )}
//                 </div>
//               </div>
//             </div>
//           )}

//           {activeView === "reviewed" && (
//             <div className="bg-slate-900 border border-slate-800 rounded-md p-2 h-full flex flex-col min-h-0">
//               <div className="flex items-center gap-1 border-b border-slate-800 pb-1 mb-1">
//                 <CheckCircle className="w-3.5 h-3.5 text-emerald-400" />
//                 <h2 className="text-[10px] font-bold text-emerald-400 uppercase tracking-wider">Reviewed Cases Stream</h2>
//               </div>
//               <div className="flex-1 overflow-auto border border-slate-800/40 rounded dynamic-scroll">
//                 {reviewedCasesList.length === 0 ? (
//                   <p className="text-xs text-slate-500 p-3 italic text-center">No trades evaluated in this user session.</p>
//                 ) : (
//                   <table className="text-left text-xs w-full border-collapse">
//                     <thead className="sticky top-0 bg-slate-900 text-slate-400 uppercase text-[9px] border-b border-slate-800 font-bold">
//                       <tr>
//                         <th className="p-2">Trade ID</th>
//                         <th className="p-2">Investment Type</th>
//                         <th className="p-2 text-right">Amount</th>
//                         <th className="p-2 text-center">Auditor Evaluation</th>
//                         <th className="p-2 pl-4">Review Notes Context</th>
//                       </tr>
//                     </thead>
//                     <tbody className="divide-y divide-slate-800/30 text-[11px] text-slate-300">
//                       {reviewedCasesList.map((c) => {
//                         const state = caseStates[c.trade_id];
//                         return (
//                           <tr key={c.trade_id} className="hover:bg-slate-800/20">
//                             <td className="p-2 font-mono text-slate-400">{c.trade_id}</td>
//                             <td className="p-2">{c.investment_type || "N/A"}</td>
//                             <td className="p-2 text-right font-mono text-emerald-400">${Number(c.investment_amount || 0).toLocaleString()}</td>
//                             <td className="p-2 text-center">
//                               <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
//                                 state?.userAction === 'Approved' ? 'bg-emerald-950 text-emerald-400 border border-emerald-900/40' :
//                                 state?.userAction === 'Rejected' ? 'bg-rose-950 text-rose-400 border border-rose-900/40' :
//                                 'bg-amber-950 text-amber-400 border border-amber-900/40'
//                               }`}>
//                                 {state?.userAction || 'Processed'}
//                               </span>
//                             </td>
//                             <td className="p-2 pl-4 truncate max-w-xs text-slate-400 italic">{state?.notes || "—"}</td>
//                           </tr>
//                         );
//                       })}
//                     </tbody>
//                   </table>
//                 )}
//               </div>
//             </div>
//           )}

//           {activeView === "passed" && (
//             <div className="bg-slate-900 border border-slate-800 rounded-md p-2 h-full flex flex-col min-h-0">
//               <div className="flex items-center gap-1 border-b border-slate-800 pb-1 mb-1">
//                 <CheckCircle className="w-3.5 h-3.5 text-indigo-400" />
//                 <h2 className="text-[10px] font-bold text-indigo-400 uppercase tracking-wider">Automated Passed Engine Streams (Unflagged Logs)</h2>
//               </div>
//               <div className="flex-1 overflow-auto border border-slate-800/40 rounded dynamic-scroll">
//                 {passedCasesList.length === 0 ? (
//                   <p className="text-xs text-slate-500 p-3 italic text-center">No automatically bypassed rows reported.</p>
//                 ) : (
//                   <table className="text-left text-xs w-full border-collapse">
//                     <thead className="sticky top-0 bg-slate-900 text-slate-400 uppercase text-[9px] border-b border-slate-800 font-bold">
//                       <tr>
//                         <th className="p-2">Trade ID</th>
//                         <th className="p-2">Asset Class</th>
//                         <th className="p-2 text-right">Notional Value</th>
//                         <th className="p-2 text-right">Confidence Score</th>
//                         <th className="p-2 text-center">System Clearance Status</th>
//                       </tr>
//                     </thead>
//                     <tbody className="divide-y divide-slate-800/30 text-[11px] text-slate-300">
//                       {passedCasesList.map((c) => (
//                         <tr key={c.trade_id} className="hover:bg-slate-800/20">
//                           <td className="p-2 font-mono text-slate-400">{c.trade_id}</td>
//                           <td className="p-2">{c.investment_type || c.asset_class || "N/A"}</td>
//                           <td className="p-2 text-right font-mono">${Number(c.notional_value || 0).toLocaleString()}</td>
//                           <td className="p-2 text-right font-mono text-sky-400">{(Number(c.confidence_score) || 1).toFixed(4)}</td>
//                           <td className="p-2 text-center">
//                             <span className="text-[10px] font-bold bg-emerald-950/40 text-emerald-400 px-2 py-0.5 rounded flex items-center justify-center w-fit mx-auto border border-emerald-900/30">
//                               Passed Engine
//                             </span>
//                           </td>
//                         </tr>
//                       ))}
//                     </tbody>
//                   </table>
//                 )}
//               </div>
//             </div>
//           )}

//         </div>

//         {/* LOWER VIEW: High-Density Workspace (Optimized Zero Scroll Framework) */}
//         <div className="bg-slate-900 border border-slate-800 rounded-md p-2.5 flex flex-col min-h-0 shadow-2xl justify-between">
//           {selectedCase ? (
//             (() => {
//               const currentState = caseStates[selectedCase.trade_id] || { reviewStatus: "Not reviewed", notes: "" };
//               const isFinalized = currentState.reviewStatus === "Reviewed" || currentState.reviewStatus === "Escalated";
//               const riskVal = 1 - (Number(selectedCase.compliance_probability) || 0);
//               const currentRec = currentState.overriddenLabel || selectedCase.compliance_label || "Non-compliant";
//               const isRecCompliant = currentRec.toLowerCase() === "compliant";
              
//               return (
//                 <div className="flex flex-col h-full justify-between min-h-0 space-y-2">
                  
//                   {/* Title Bar strip Area header */}
//                   <div className="flex items-center justify-between border-b border-slate-800 pb-1 shrink-0">
//                     <div className="flex items-center gap-2">
//                       <span className="text-[9px] font-black uppercase tracking-wider text-purple-400 bg-purple-950/30 px-1.5 py-0.5 rounded border border-purple-900/40">
//                         Selected Case Audit
//                       </span>
//                       <span className="text-xs font-mono font-bold text-slate-100">{selectedCase.trade_id}</span>
//                     </div>
//                   </div>

//                   {/* Dense Non-Scrolling Data Field Modules Grid (3 Grid Column Alignment Matrix) */}
//                   <div className="grid grid-cols-3 gap-3 flex-1 min-h-0 items-center py-0.5">
                    
//                     {/* COLUMN 1: Trade Details Block */}
//                     <div className="bg-slate-950/20 border border-slate-800/40 p-2 rounded h-full flex flex-col justify-center">
//                       <div className="flex items-center gap-1 border-b border-slate-800/60 pb-1 mb-1 shrink-0">
//                         <Briefcase className="w-3 h-3 text-purple-400" />
//                         <h4 className="text-[9px] font-bold text-purple-400 uppercase tracking-wider">Trade Details</h4>
//                       </div>
//                       <div className="text-[11px] grid grid-cols-2 gap-x-2 gap-y-1.5 text-slate-300">
//                         <div>
//                           <div className="text-slate-500 text-[9px] uppercase font-semibold">Type</div>
//                           <div className="font-medium truncate">{selectedCase.investment_type || "N/A"}</div>
//                         </div>
//                         <div>
//                           <div className="text-slate-500 text-[9px] uppercase font-semibold">Amount</div>
//                           <div className="font-mono font-bold text-emerald-400 truncate">
//                             {selectedCase.investment_amount ? `$${Number(selectedCase.investment_amount).toLocaleString()}` : "N/A"}
//                           </div>
//                         </div>
//                         <div>
//                           <div className="text-slate-500 text-[9px] uppercase font-semibold">Notional</div>
//                           <div className="font-mono text-slate-400 truncate">${Number(selectedCase.notional_value || 0).toLocaleString()}</div>
//                         </div>
//                         <div>
//                           <div className="text-slate-500 text-[9px] uppercase font-semibold">Timestamp</div>
//                           <div className="text-slate-400 truncate text-[10px] font-mono">{selectedCase.timestamp || "—"}</div>
//                         </div>
//                       </div>
//                     </div>

//                     {/* COLUMN 2: Client Profile Block */}
//                     <div className="bg-slate-950/20 border border-slate-800/40 p-2 rounded h-full flex flex-col justify-center">
//                       <div className="flex items-center gap-1 border-b border-slate-800/60 pb-1 mb-1 shrink-0">
//                         <User className="w-3 h-3 text-sky-400" />
//                         <h4 className="text-[9px] font-bold text-sky-400 uppercase tracking-wider">Client Profile</h4>
//                       </div>
//                       <div className="text-[11px] grid grid-cols-2 gap-x-2 gap-y-1.5 text-slate-300">
//                         <div>
//                           <div className="text-slate-500 text-[9px] uppercase font-semibold">Age / Income</div>
//                           <div className="font-mono truncate">{selectedCase.client_age ?? "—"} / {selectedCase.client_income ? `$${Math.round(selectedCase.client_income/1000)}k` : "—"}</div>
//                         </div>
//                         <div>
//                           <div className="text-slate-500 text-[9px] uppercase font-semibold">Risk Profile</div>
//                           <div className="truncate font-medium text-amber-400">{selectedCase.risk_tolerance || selectedCase.client_risk_tolerance || "—"}</div>
//                         </div>
//                         <div>
//                           <div className="text-slate-500 text-[9px] uppercase font-semibold">Experience</div>
//                           <div className="truncate text-slate-400">{selectedCase.investment_experience || "—"}</div>
//                         </div>
//                         <div>
//                           <div className="text-slate-500 text-[9px] uppercase font-semibold">Objective</div>
//                           <div className="truncate text-slate-400 text-[10px]">{selectedCase.investment_objective || "—"}</div>
//                         </div>
//                       </div>
//                     </div>

//                     {/* COLUMN 3: Advisor Info Block */}
//                     <div className="bg-slate-950/20 border border-slate-800/40 p-2 rounded h-full flex flex-col justify-center">
//                       <div className="flex items-center gap-1 border-b border-slate-800/60 pb-1 mb-1 shrink-0">
//                         <FileText className="w-3 h-3 text-amber-400" />
//                         <h4 className="text-[9px] font-bold text-amber-400 uppercase tracking-wider">Advisor Info</h4>
//                       </div>
//                       <div className="text-[11px] grid grid-cols-2 gap-x-2 gap-y-1.5 text-slate-300">
//                         <div>
//                           <div className="text-slate-500 text-[9px] uppercase font-semibold">Advisor ID</div>
//                           <div className="font-mono text-slate-200 truncate">{selectedCase.advisor_id || "—"}</div>
//                         </div>
//                         <div>
//                           <div className="text-slate-500 text-[9px] uppercase font-semibold">Exp / Risk</div>
//                           <div className="truncate text-slate-400">{selectedCase.advisor_experience || "—"} / <span className="text-rose-400 font-mono">{selectedCase.advisor_history_risk ?? "0"}</span></div>
//                         </div>
//                         <div>
//                           <div className="text-slate-500 text-[9px] uppercase font-semibold">Rationale</div>
//                           <span className={`inline-block text-center px-1 rounded text-[9px] font-bold ${
//                             selectedCase.has_rationale ? "bg-emerald-950 text-emerald-400" : "bg-slate-900 text-slate-500"
//                           }`}>{selectedCase.has_rationale ? "FILED" : "MISSING"}</span>
//                         </div>
//                         <div>
//                           <div className="text-slate-500 text-[9px] uppercase font-semibold">Desk Context</div>
//                           <div className="text-slate-400 truncate max-w-[120px] text-[10px] italic">{selectedCase.advisor_notes || "None submitted."}</div>
//                         </div>
//                       </div>
//                     </div>

//                   </div>

//                   {/* Operational Controls Area (Retaining Exception Breakdown + Policy streams stacked together) */}
//                   <div className="grid grid-cols-4 gap-2 border-t border-slate-800/60 pt-1.5 shrink-0 items-center bg-slate-950/30 p-1.5 rounded-lg">
//                     <div className="col-span-3 text-[11px] space-y-1">
//                       <div className="flex items-center gap-1">
//                         <HelpCircle className="w-3.5 h-3.5 text-rose-400 shrink-0" />
//                         <span className="text-[9px] uppercase font-black text-slate-500 tracking-wider">Exception Flag Reason:</span>
//                         <span className="text-rose-300 truncate text-[10px]">{selectedCase.flag_reason || "No structural exceptions found."}</span>
//                       </div>
//                       <div className="flex flex-wrap gap-1 items-center">
//                         <span className="text-[9px] font-black text-slate-600 uppercase tracking-wider">Policies:</span>
//                         {renderPolicies(selectedCase.retrieved_policies)}
//                       </div>
//                     </div>
                    
//                     {/* Dedicated Compact Inline Score Strip Component */}
//                     <div className="bg-slate-950 px-2 py-1.5 rounded border border-slate-800 flex flex-col space-y-0.5 text-[10px] font-medium font-mono text-right">
//                       <div className="flex justify-between gap-2"><span className="text-slate-500 font-sans text-[9px] uppercase font-semibold">AI REC:</span><span className={`font-bold px-1 rounded text-[9px] ${isRecCompliant ? "bg-emerald-950 text-emerald-400" : "bg-rose-950 text-rose-400"}`}>{isRecCompliant ? "COMPLIANT" : "FLAGGED"}</span></div>
//                       <div className="flex justify-between gap-2"><span className="text-slate-500 font-sans text-[9px] uppercase font-semibold">RISK:</span><span className="text-rose-400 font-bold">{riskVal.toFixed(3)}</span></div>
//                       <div className="flex justify-between gap-2"><span className="text-slate-500 font-sans text-[9px] uppercase font-semibold">CONF:</span><span className="text-sky-400 font-bold">{Number(selectedCase.confidence_score || 0).toFixed(3)}</span></div>
//                     </div>
//                   </div>

//                   {/* Persistent Sign-off Actions row */}
//                   <div className="pt-1 flex gap-2 items-end shrink-0">
//                     <div className="flex-1 flex flex-col">
//                       <label className="text-[9px] font-black text-slate-400 uppercase tracking-widest mb-0.5">
//                         Reviewer Sign-off Notes Context
//                       </label>
//                       <input
//                         type="text"
//                         value={currentNotes}
//                         disabled={isFinalized}
//                         onChange={(e) => handleNotesChange(e.target.value)}
//                         placeholder={isFinalized ? "Audit history signature locked." : "Enter compliance justification or structural risk override arguments..."}
//                         className="w-full bg-slate-950 border border-slate-800 rounded px-2 py-1 text-xs text-slate-200 focus:outline-none focus:border-indigo-500 disabled:opacity-40 transition-colors placeholder:text-slate-600 h-7"
//                       />
//                     </div>
                    
//                     {/* Renamed Interface Call Action Controls Panel */}
//                     <div className="flex gap-1.5 h-7">
//                       <button
//                         onClick={() => executeAuditAction("Reviewed", "Rejected")}
//                         disabled={isFinalized}
//                         className="bg-rose-600 hover:bg-rose-500 disabled:bg-slate-800 disabled:text-slate-500 text-white font-black text-[10px] px-3 py-1 rounded transition-colors uppercase tracking-wider whitespace-nowrap flex items-center gap-1 shadow-sm"
//                       >
//                         <X className="w-3 h-3" />
//                         <span>Reject Trade</span>
//                       </button>
//                       <button
//                         onClick={() => executeAuditAction("Reviewed", "Approved")}
//                         disabled={isFinalized}
//                         className="bg-emerald-600 hover:bg-emerald-500 disabled:bg-slate-800 disabled:text-slate-500 text-slate-950 font-black text-[10px] px-3 py-1 rounded transition-colors uppercase tracking-wider whitespace-nowrap flex items-center gap-1 shadow-sm"
//                       >
//                         <Check className="w-3 h-3" />
//                         <span>Approve Trade</span>
//                       </button>
//                       <button
//                         onClick={() => executeAuditAction("Escalated", "Escalated")}
//                         disabled={isFinalized}
//                         className="bg-slate-800 hover:bg-slate-700 disabled:bg-slate-800 disabled:text-slate-500 text-amber-400 border border-slate-700 font-black text-[10px] px-3 py-1 rounded transition-colors uppercase tracking-wider whitespace-nowrap flex items-center gap-1 shadow-sm"
//                       >
//                         <CornerUpRight className="w-3 h-3" />
//                         <span>Escalate Review</span>
//                       </button>
//                     </div>
//                   </div>

//                 </div>
//               );
//             })()
//           ) : (
//             <div className="h-full flex flex-col items-center justify-center text-slate-500 text-xs font-semibold border border-dashed border-slate-800 rounded p-4 text-center">
//               <CheckCircle className="w-8 h-8 text-emerald-500/40 mb-1" />
//               <span>All Active Triage Tasks Completed</span>
//               <p className="text-[10px] text-slate-600 font-normal max-w-xs mt-0.5">Outstanding files inside resizable Urgent and Review telemetry metrics have been cleared.</p>
//             </div>
//           )}
//         </div>

//       </div>
//     </div>
//   );
// }

// export default Dashboard;

// /* VERSION 7 */

// import { useEffect, useState, useRef } from "react";
// import { getCases } from "../api/cases";
// import { AlertCircle, CheckCircle, Clock, ShieldAlert, FileText, User, Briefcase, HelpCircle, ArrowUpRight } from "lucide-react";

// interface CaseAuditState {
//   reviewStatus: "Reviewed" | "Not reviewed" | "Escalated";
//   notes: string;
//   overriddenLabel?: string; // Tracks live modifications to the AI recommendation
// }

// function Dashboard() {
//   const [cases, setCases] = useState<any[]>([]);
//   const [selectedCase, setSelectedCase] = useState<any | null>(null);
  
//   // Per-case persistence engine keyed by trade_id
//   const [caseStates, setCaseStates] = useState<Record<string, CaseAuditState>>({});
//   const [currentNotes, setCurrentNotes] = useState<string>("");

//   // --- Spreadsheet Column Resize State ---
//   const [urgentWidths, setUrgentWidths] = useState({ tradeId: 100, risk: 75, conf: 75, reason: 260 });
//   const [queuedWidths, setQueuedWidths] = useState({ tradeId: 100, priority: 70, risk: 75, conf: 75, reason: 240 });

//   const dragInfo = useRef<{ table: 'urgent' | 'queued'; col: string; startX: number; startWidth: number } | null>(null);

//   useEffect(() => {
//     getCases()
//       .then((data) => {
//         if (Array.isArray(data)) {
//           setCases(data);
          
//           // Seed initial default auditing structures for all fetched trades
//           const initialStates: Record<string, CaseAuditState> = {};
//           data.forEach((c) => {
//             if (c?.trade_id) {
//               initialStates[c.trade_id] = { 
//                 reviewStatus: "Not reviewed", 
//                 notes: "",
//                 overriddenLabel: c.compliance_label || "Non-compliant"
//               };
//             }
//           });
//           setCaseStates(initialStates);

//           const urgentCases = data.filter((c) => c?.escalation_level === "urgent");
//           const queuedCases = data
//             .filter((c) => c?.escalation_level === "priority" || c?.escalation_level === "queue")
//             .sort((a, b) => (Number(b?.priority_score) || 0) - (Number(a?.priority_score) || 0));

//           if (urgentCases.length > 0) handleCaseSelection(urgentCases[0], initialStates);
//           else if (queuedCases.length > 0) handleCaseSelection(queuedCases[0], initialStates);
//         }
//       })
//       .catch((err) => console.error("API Fetch Error:", err));
//   }, []);

//   const handleCaseSelection = (targetCase: any, latestStates = caseStates) => {
//     setSelectedCase(targetCase);
//     if (targetCase?.trade_id) {
//       const savedState = latestStates[targetCase.trade_id];
//       setCurrentNotes(savedState ? savedState.notes : "");
//     }
//   };

//   const handleNotesChange = (text: string) => {
//     setCurrentNotes(text);
//     if (selectedCase?.trade_id) {
//       setCaseStates(prev => ({
//         ...prev,
//         [selectedCase.trade_id]: {
//           ...prev[selectedCase.trade_id],
//           notes: text
//         }
//       }));
//     }
//   };

//   // --- Audit State Updaters ---
//   const handleApproveAI = () => {
//     if (!selectedCase?.trade_id) return;
//     setCaseStates(prev => ({
//       ...prev,
//       [selectedCase.trade_id]: {
//         ...prev[selectedCase.trade_id],
//         reviewStatus: "Reviewed",
//         notes: currentNotes
//       }
//     }));
//     console.log(`Approved AI for ${selectedCase.trade_id}. Notes: ${currentNotes}`);
//   };

//   const handleOverrideAI = () => {
//     if (!selectedCase?.trade_id) return;
//     setCaseStates(prev => {
//       const currentLabel = prev[selectedCase.trade_id]?.overriddenLabel || selectedCase.compliance_label || "Non-compliant";
//       // Toggle logic between Compliant / Non-compliant states
//       const flippedLabel = currentLabel.toLowerCase().includes("non") ? "Compliant" : "Non-compliant";
      
//       return {
//         ...prev,
//         [selectedCase.trade_id]: {
//           ...prev[selectedCase.trade_id],
//           reviewStatus: "Reviewed",
//           overriddenLabel: flippedLabel,
//           notes: currentNotes
//         }
//       };
//     });
//     console.log(`Overrode AI classification for ${selectedCase.trade_id}. Notes: ${currentNotes}`);
//   };

//   const handleEscalate = () => {
//     if (!selectedCase?.trade_id) return;
//     setCaseStates(prev => ({
//       ...prev,
//       [selectedCase.trade_id]: {
//         ...prev[selectedCase.trade_id],
//         reviewStatus: "Escalated",
//         notes: currentNotes
//       }
//     }));
//     console.log(`Escalated case file ${selectedCase.trade_id}. Notes: ${currentNotes}`);
//   };

//   // --- Mouse Resize Handlers ---
//   const handleMouseDown = (table: 'urgent' | 'queued', col: string, e: React.MouseEvent) => {
//     e.preventDefault();
//     const currentWidths = table === 'urgent' ? urgentWidths : queuedWidths;
//     dragInfo.current = {
//       table,
//       col,
//       startX: e.clientX,
//       startWidth: (currentWidths as any)[col]
//     };
//     document.addEventListener("mousemove", handleMouseMove);
//     document.addEventListener("mouseup", handleMouseUp);
//   };

//   const handleMouseMove = (e: MouseEvent) => {
//     if (!dragInfo.current) return;
//     const { table, col, startX, startWidth } = dragInfo.current;
//     const deltaX = e.clientX - startX;
//     const newWidth = Math.max(50, startWidth + deltaX);

//     if (table === 'urgent') {
//       setUrgentWidths(prev => ({ ...prev, [col]: newWidth }));
//     } else {
//       setQueuedWidths(prev => ({ ...prev, [col]: newWidth }));
//     }
//   };

//   const handleMouseUp = () => {
//     dragInfo.current = null;
//     document.removeEventListener("mousemove", handleMouseMove);
//     document.removeEventListener("mouseup", handleMouseUp);
//   };

//   const handleDoubleClick = (table: 'urgent' | 'queued') => {
//     if (table === 'urgent') {
//       setUrgentWidths({ tradeId: 100, risk: 75, conf: 75, reason: 260 });
//     } else {
//       setQueuedWidths({ tradeId: 100, priority: 70, risk: 75, conf: 75, reason: 240 });
//     }
//   };

//   const urgentCases = cases.filter((c) => c?.escalation_level === "urgent");
//   const queuedCases = cases
//     .filter((c) => c?.escalation_level === "priority" || c?.escalation_level === "queue")
//     .sort((a, b) => (Number(b?.priority_score) || 0) - (Number(a?.priority_score) || 0));

//   // Dynamic status counters pulling from the state engine
//   const countUrgent = urgentCases.length;
//   const countReview = queuedCases.length;
//   const countEscalated = Object.values(caseStates).filter((s) => s.reviewStatus === "Escalated").length;
//   const countPassed = cases.filter(
//     (c) => c?.escalation_level !== "urgent" && c?.escalation_level !== "priority" && c?.escalation_level !== "queue"
//   ).length;

//   const renderPolicies = (policies: any) => {
//     if (!policies) return <span className="text-[10px] text-slate-500">No policies attached.</span>;
//     let items: string[] = [];
//     if (Array.isArray(policies)) items = policies;
//     else if (typeof policies === "string" && policies.startsWith("[")) {
//       items = policies.replace(/[\[\]']/g, "").split(",").map((p) => p.trim()).filter(Boolean);
//     } else if (typeof policies === "string" && policies.trim().length > 0) {
//       items = policies.split(",").map((p) => p.trim());
//     }
    
//     if (items.length === 0) return <span className="text-[10px] text-slate-500">No policies attached.</span>;
//     return items.map((policy, i) => (
//       <span key={i} className="px-1.5 py-0.5 bg-slate-950 text-[10px] rounded border border-slate-800 text-purple-300 font-mono">
//         {policy}
//       </span>
//     ));
//   };

//   return (
//     <div className="p-1 h-screen bg-slate-950 text-slate-100 flex flex-col gap-1 overflow-hidden select-none">
      
//       <style>{`
//         .dynamic-scroll { scrollbar-width: none; }
//         .dynamic-scroll::-webkit-scrollbar { width: 4px; height: 4px; display: none; }
//         .dynamic-scroll:hover { scrollbar-width: thin; }
//         .dynamic-scroll:hover::-webkit-scrollbar { display: block; }
//         .dynamic-scroll::-webkit-scrollbar-track { background: transparent; }
//         .dynamic-scroll::-webkit-scrollbar-thumb { background: rgba(148, 163, 184, 0.15); border-radius: 2px; }
//       `}</style>
      
//       {/* Top Header Metrics Layer */}
//       <div className="flex items-center justify-between border-b border-slate-900 pb-1">
//         <h1 className="text-base font-bold tracking-tight text-slate-200">
//           AI Compliance Review Copilot
//         </h1>
        
//         <div className="flex items-center gap-2">
//           <div className="bg-rose-950/30 border border-rose-500/30 rounded px-2 py-0.5 flex items-center gap-1.5 text-xs font-medium shadow-sm">
//             <AlertCircle className="w-3.5 h-3.5 text-rose-400" />
//             <span className="text-rose-300">Urgent:</span>
//             <span className="text-sm font-black text-rose-100">{countUrgent}</span>
//           </div>

//           <div className="bg-amber-950/30 border border-amber-500/30 rounded px-2 py-0.5 flex items-center gap-1.5 text-xs font-medium shadow-sm">
//             <Clock className="w-3.5 h-3.5 text-amber-400" />
//             <span className="text-amber-300">Review:</span>
//             <span className="text-sm font-black text-amber-100">{countReview}</span>
//           </div>

//           <div className="bg-purple-950/30 border border-purple-500/30 rounded px-2 py-0.5 flex items-center gap-1.5 text-xs font-medium shadow-sm">
//             <ArrowUpRight className="w-3.5 h-3.5 text-purple-400" />
//             <span className="text-purple-300">Escalated:</span>
//             <span className="text-sm font-black text-purple-100">{countEscalated}</span>
//           </div>

//           <div className="bg-emerald-950/30 border border-emerald-500/30 rounded px-2 py-0.5 flex items-center gap-1.5 text-xs font-medium shadow-sm">
//             <CheckCircle className="w-3.5 h-3.5 text-emerald-400" />
//             <span className="text-emerald-300">Passed:</span>
//             <span className="text-sm font-black text-emerald-100">{countPassed}</span>
//           </div>
//         </div>
//       </div>

//       {/* Main Viewport Grid Layout: 48% Upper Split / 52% Workspace Expansion */}
//       <div className="flex-1 grid grid-rows-[48fr_52fr] gap-1 min-h-0">
        
//         {/* UPPER VIEW: Side-by-Side Monitoring Lists */}
//         <div className="grid grid-cols-2 gap-1 min-h-0">
          
//           {/* URGENT TRACK PANEL */}
//           <div className="bg-slate-900 border border-rose-500/10 rounded-md p-1.5 flex flex-col min-h-0">
//             <div className="flex items-center gap-1 border-b border-slate-800 pb-0.5 mb-1">
//               <ShieldAlert className="w-3.5 h-3.5 text-rose-400" />
//               <h2 className="text-[10px] font-bold text-rose-400 uppercase tracking-wider">Urgent Action Required</h2>
//             </div>
            
//             <div className="flex-1 overflow-auto min-h-0 relative border border-slate-800/30 rounded dynamic-scroll">
//               {urgentCases.length === 0 ? (
//                 <p className="text-xs text-slate-500 p-1">No urgent cases outstanding.</p>
//               ) : (
//                 <table className="text-left text-xs border-collapse table-fixed w-max min-w-full">
//                   <thead className="sticky top-0 bg-slate-900 text-slate-400 font-bold uppercase text-[9px] border-b border-slate-800 z-10">
//                     <tr>
//                       <th style={{ width: urgentWidths.tradeId }} className="p-1 relative group">
//                         Trade ID
//                         <div onMouseDown={(e) => handleMouseDown('urgent', 'tradeId', e)} onDoubleClick={() => handleDoubleClick('urgent')} className="absolute right-0 top-0 bottom-0 w-1 bg-slate-700/0 group-hover:bg-purple-500/50 cursor-col-resize transition-colors" />
//                       </th>
//                       <th style={{ width: urgentWidths.risk }} className="p-1 text-right relative group">
//                         Risk Score
//                         <div onMouseDown={(e) => handleMouseDown('urgent', 'risk', e)} onDoubleClick={() => handleDoubleClick('urgent')} className="absolute right-0 top-0 bottom-0 w-1 bg-slate-700/0 group-hover:bg-purple-500/50 cursor-col-resize transition-colors" />
//                       </th>
//                       <th style={{ width: urgentWidths.conf }} className="p-1 text-right relative group">
//                         Conf.
//                         <div onMouseDown={(e) => handleMouseDown('urgent', 'conf', e)} onDoubleClick={() => handleDoubleClick('urgent')} className="absolute right-0 top-0 bottom-0 w-1 bg-slate-700/0 group-hover:bg-purple-500/50 cursor-col-resize transition-colors" />
//                       </th>
//                       <th style={{ width: urgentWidths.reason }} className="p-1 pl-2 relative group">
//                         Flag Reason
//                         <div onMouseDown={(e) => handleMouseDown('urgent', 'reason', e)} onDoubleClick={() => handleDoubleClick('urgent')} className="absolute right-0 top-0 bottom-0 w-1 bg-slate-700/0 group-hover:bg-purple-500/50 cursor-col-resize transition-colors" />
//                       </th>
//                     </tr>
//                   </thead>
//                   <tbody className="divide-y divide-slate-800/30">
//                     {urgentCases.map((c, idx) => {
//                       const isSelected = selectedCase?.trade_id === c?.trade_id;
//                       const riskVal = 1 - (Number(c?.compliance_probability) ?? 1.0);
//                       return (
//                         <tr
//                           key={`${c?.trade_id}-${idx}`}
//                           onClick={() => handleCaseSelection(c)}
//                           className={`cursor-pointer text-[11px] transition-colors ${isSelected ? 'bg-rose-950/40 font-semibold border-l-2 border-rose-500 text-rose-200 shadow-[inner_0_1px_0_rgba(244,63,94,0.1)]' : 'hover:bg-slate-800/30 text-slate-300'}`}
//                         >
//                           <td className="p-1 font-mono truncate">{c?.trade_id}</td>
//                           <td className="p-1 text-right font-mono text-rose-400/90">{riskVal.toFixed(2)}</td>
//                           <td className="p-1 text-right font-mono text-slate-400">{(Number(c?.confidence_score) || 0).toFixed(2)}</td>
//                           <td className="p-1 pl-2 truncate text-[10px]">{c?.flag_reason}</td>
//                         </tr>
//                       );
//                     })}
//                   </tbody>
//                 </table>
//               )}
//             </div>
//           </div>

//           {/* REVIEW QUEUE PANEL */}
//           <div className="bg-slate-900 border border-slate-800/80 rounded-md p-1.5 flex flex-col min-h-0">
//             <div className="flex items-center gap-1 border-b border-slate-800 pb-0.5 mb-1">
//               <Clock className="w-3.5 h-3.5 text-amber-400" />
//               <h2 className="text-[10px] font-bold text-amber-400 uppercase tracking-wider">Review</h2>
//             </div>
            
//             <div className="flex-1 overflow-auto min-h-0 relative border border-slate-800/30 rounded dynamic-scroll">
//               {queuedCases.length === 0 ? (
//                 <p className="text-xs text-slate-500 p-1">Review queue empty.</p>
//               ) : (
//                 <table className="text-left text-xs border-collapse table-fixed w-max min-w-full">
//                   <thead className="sticky top-0 bg-slate-900 text-slate-400 font-bold uppercase text-[9px] border-b border-slate-800 z-10">
//                     <tr>
//                       <th style={{ width: queuedWidths.tradeId }} className="p-1 relative group">
//                         Trade ID
//                         <div onMouseDown={(e) => handleMouseDown('queued', 'tradeId', e)} onDoubleClick={() => handleDoubleClick('queued')} className="absolute right-0 top-0 bottom-0 w-1 bg-slate-700/0 group-hover:bg-purple-500/50 cursor-col-resize transition-colors" />
//                       </th>
//                       <th style={{ width: queuedWidths.priority }} className="p-1 text-right relative group text-amber-400">
//                         Priority
//                         <div onMouseDown={(e) => handleMouseDown('queued', 'priority', e)} onDoubleClick={() => handleDoubleClick('queued')} className="absolute right-0 top-0 bottom-0 w-1 bg-slate-700/0 group-hover:bg-purple-500/50 cursor-col-resize transition-colors" />
//                       </th>
//                       <th style={{ width: queuedWidths.risk }} className="p-1 text-right relative group">
//                         Risk Score
//                         <div onMouseDown={(e) => handleMouseDown('queued', 'risk', e)} onDoubleClick={() => handleDoubleClick('queued')} className="absolute right-0 top-0 bottom-0 w-1 bg-slate-700/0 group-hover:bg-purple-500/50 cursor-col-resize transition-colors" />
//                       </th>
//                       <th style={{ width: queuedWidths.conf }} className="p-1 text-right relative group">
//                         Conf.
//                         <div onMouseDown={(e) => handleMouseDown('queued', 'conf', e)} onDoubleClick={() => handleDoubleClick('queued')} className="absolute right-0 top-0 bottom-0 w-1 bg-slate-700/0 group-hover:bg-purple-500/50 cursor-col-resize transition-colors" />
//                       </th>
//                       <th style={{ width: queuedWidths.reason }} className="p-1 pl-2 relative group">
//                         Flag Reason
//                         <div onMouseDown={(e) => handleMouseDown('queued', 'reason', e)} onDoubleClick={() => handleDoubleClick('queued')} className="absolute right-0 top-0 bottom-0 w-1 bg-slate-700/0 group-hover:bg-purple-500/50 cursor-col-resize transition-colors" />
//                       </th>
//                     </tr>
//                   </thead>
//                   <tbody className="divide-y divide-slate-800/30">
//                     {queuedCases.map((c, idx) => {
//                       const isSelected = selectedCase?.trade_id === c?.trade_id;
//                       const riskVal = 1 - (Number(c?.compliance_probability) ?? 1.0);
//                       return (
//                         <tr
//                           key={`${c?.trade_id}-${idx}`}
//                           onClick={() => handleCaseSelection(c)}
//                           className={`cursor-pointer text-[11px] transition-colors ${isSelected ? 'bg-purple-950/40 font-semibold border-l-2 border-purple-500 text-purple-200 shadow-[inner_0_1px_0_rgba(168,85,247,0.1)]' : 'hover:bg-slate-800/30 text-slate-300'}`}
//                         >
//                           <td className="p-1 font-mono truncate">{c?.trade_id}</td>
//                           <td className="p-1 text-right font-mono font-bold text-amber-400">{c?.priority_score ?? "0"}</td>
//                           <td className="p-1 text-right font-mono text-rose-400/90">{riskVal.toFixed(2)}</td>
//                           <td className="p-1 text-right font-mono text-slate-400">{(Number(c?.confidence_score) || 0).toFixed(2)}</td>
//                           <td className="p-1 pl-2 truncate text-[10px]">{c?.flag_reason}</td>
//                         </tr>
//                       );
//                     })}
//                   </tbody>
//                 </table>
//               )}
//             </div>
//           </div>

//         </div>

//         {/* LOWER VIEW: High-Density Workspace (Optimized Layout Matrix) */}
//         <div className="bg-slate-900 border border-slate-800 rounded-md p-2 flex flex-col min-h-0 shadow-2xl">
//           {selectedCase ? (
//             (() => {
//               const currentState = caseStates[selectedCase.trade_id] || { reviewStatus: "Not reviewed", notes: "" };
//               const isFinalized = currentState.reviewStatus === "Reviewed" || currentState.reviewStatus === "Escalated";
//               const riskVal = 1 - (Number(selectedCase.compliance_probability) || 0);
              
//               // Resolve active recommendation dynamically based on override status
//               const currentRec = currentState.overriddenLabel || selectedCase.compliance_label || "Non-compliant";
//               const isRecCompliant = currentRec.toLowerCase() === "compliant";
              
//               return (
//                 <div className="flex flex-col h-full gap-1.5 min-h-0">
                  
//                   {/* Title & Micro Scores Strip */}
//                   <div className="flex items-center justify-between border-b border-slate-800 pb-1 flex-shrink-0">
//                     <div className="flex items-center gap-1.5">
//                       <span className="text-[9px] font-black uppercase tracking-wider text-purple-400 bg-purple-950/30 px-1.5 py-0.5 rounded border border-purple-900/40">
//                         Selected Case Audit
//                       </span>
//                       <span className="text-xs font-mono font-bold text-slate-100">{selectedCase.trade_id}</span>
                      
//                       <span className={`px-1.5 py-0.5 rounded text-[9px] font-bold tracking-wide border ${
//                         currentState.reviewStatus === "Reviewed"
//                           ? "bg-emerald-950/40 text-emerald-400 border-emerald-800/40" 
//                           : currentState.reviewStatus === "Escalated"
//                           ? "bg-rose-950/40 text-rose-400 border-rose-800/40"
//                           : "bg-slate-950 text-amber-400 border-amber-900/40"
//                       }`}>
//                         {currentState.reviewStatus.toUpperCase()}
//                       </span>
//                     </div>
                    
//                     {/* Compact Scores Interface with Conspicuous AI Recommendation Badge */}
//                     <div className="flex items-center gap-3 bg-slate-950/80 px-2 py-0.5 rounded border border-slate-800/60 text-[11px]">
//                       <div className="flex items-center gap-1">
//                         <span className="text-slate-500 font-medium text-[9px] uppercase">AI Rec:</span>
//                         <span className={`font-bold tracking-tight px-1 rounded text-[10px] ${
//                           isRecCompliant 
//                             ? "bg-emerald-950/50 text-emerald-400" 
//                             : "bg-rose-950/50 text-rose-400"
//                         }`}>
//                           {isRecCompliant ? "Compliant" : "Non-compliant"}
//                         </span>
//                       </div>
//                       <div className="border-l border-slate-800 h-3" />
//                       <div>
//                         <span className="text-slate-500 font-medium text-[9px] uppercase mr-1">Risk:</span>
//                         <span className="font-mono font-bold text-rose-400">{riskVal.toFixed(4)}</span>
//                       </div>
//                       <div className="border-l border-slate-800 h-3" />
//                       <div>
//                         <span className="text-slate-500 font-medium text-[9px] uppercase mr-1">Conf:</span>
//                         <span className="font-mono font-bold text-sky-400">{Number(selectedCase.confidence_score || 0).toFixed(4)}</span>
//                       </div>
//                       <div className="border-l border-slate-800 h-3" />
//                       <div>
//                         <span className="text-slate-500 font-medium text-[9px] uppercase mr-1">Priority:</span>
//                         <span className="font-mono font-bold text-amber-400">{selectedCase.priority_score ?? "—"}</span>
//                       </div>
//                     </div>
//                   </div>

//                   {/* High-Density 4-Column Structured Audit Grid */}
//                   <div className="grid grid-cols-4 gap-2 flex-1 min-h-0 py-0.5">
                    
//                     {/* COLUMN 1: Trade Fields */}
//                     <div className="bg-slate-950/20 border border-slate-800/40 p-1.5 rounded flex flex-col min-h-0">
//                       <div className="flex items-center gap-1 border-b border-slate-800 pb-1 mb-1.5 flex-shrink-0">
//                         <Briefcase className="w-3 h-3 text-purple-400" />
//                         <h4 className="text-[9px] font-bold text-purple-400 uppercase tracking-wider">Trade Fields</h4>
//                       </div>
//                       <div className="text-[11px] space-y-1.5 overflow-y-auto dynamic-scroll text-slate-300">
//                         <div>
//                           <div className="text-slate-500 text-[9px] uppercase font-semibold">Investment Type</div>
//                           <div className="font-medium truncate">{selectedCase.investment_type || selectedCase.asset_class || "N/A"}</div>
//                         </div>
//                         <div>
//                           <div className="text-slate-500 text-[9px] uppercase font-semibold">Investment Amount</div>
//                           <div className="font-mono font-bold text-emerald-400">
//                             {selectedCase.investment_amount ? `$${Number(selectedCase.investment_amount).toLocaleString(undefined, {minimumFractionDigits: 2})}` : "N/A"}
//                           </div>
//                         </div>
//                         <div className="pt-1 border-t border-slate-800/50 text-[10px] text-slate-500 space-y-0.5 font-mono">
//                           <div>Notional: ${Number(selectedCase.notional_value || 0).toLocaleString()}</div>
//                           <div className="truncate">Time: {selectedCase.timestamp || "N/A"}</div>
//                         </div>
//                       </div>
//                     </div>

//                     {/* COLUMN 2: Client Profile */}
//                     <div className="bg-slate-950/20 border border-slate-800/40 p-1.5 rounded flex flex-col min-h-0">
//                       <div className="flex items-center gap-1 border-b border-slate-800 pb-1 mb-1.5 flex-shrink-0">
//                         <User className="w-3 h-3 text-sky-400" />
//                         <h4 className="text-[9px] font-bold text-sky-400 uppercase tracking-wider">Client Profile</h4>
//                       </div>
//                       <div className="text-[11px] space-y-1 overflow-y-auto dynamic-scroll text-slate-300 grid grid-cols-1 gap-y-1.5">
//                         <div className="grid grid-cols-2 gap-1">
//                           <div>
//                             <div className="text-slate-500 text-[9px] uppercase font-semibold">Age</div>
//                             <div className="font-mono">{selectedCase.client_age ?? "—"}</div>
//                           </div>
//                           <div>
//                             <div className="text-slate-500 text-[9px] uppercase font-semibold">Income</div>
//                             <div className="font-mono truncate">{selectedCase.client_income ? `$${Number(selectedCase.client_income).toLocaleString()}` : "—"}</div>
//                           </div>
//                         </div>
//                         <div>
//                           <div className="text-slate-500 text-[9px] uppercase font-semibold">Risk Tolerance</div>
//                           <div className="truncate">{selectedCase.risk_tolerance || selectedCase.client_risk_tolerance || "—"}</div>
//                         </div>
//                         <div>
//                           <div className="text-slate-500 text-[9px] uppercase font-semibold">Experience Level</div>
//                           <div className="truncate">{selectedCase.investment_experience || "—"}</div>
//                         </div>
//                         <div>
//                           <div className="text-slate-500 text-[9px] uppercase font-semibold">Objective</div>
//                           <div className="truncate text-[10px] leading-tight">{selectedCase.investment_objective || "—"}</div>
//                         </div>
//                         <div>
//                           <div className="text-slate-500 text-[9px] uppercase font-semibold">Time Horizon</div>
//                           <div className="truncate">{selectedCase.investment_time_horizon || "—"}</div>
//                         </div>
//                       </div>
//                     </div>

//                     {/* COLUMN 3: Advisor Records */}
//                     <div className="bg-slate-950/20 border border-slate-800/40 p-1.5 rounded flex flex-col min-h-0">
//                       <div className="flex items-center gap-1 border-b border-slate-800 pb-1 mb-1.5 flex-shrink-0">
//                         <FileText className="w-3 h-3 text-amber-400" />
//                         <h4 className="text-[9px] font-bold text-amber-400 uppercase tracking-wider">Advisor Records</h4>
//                       </div>
//                       <div className="text-[11px] space-y-1.5 overflow-y-auto dynamic-scroll flex-1 text-slate-300">
//                         <div className="grid grid-cols-2 gap-1 text-[10px]">
//                           <div>
//                             <span className="text-slate-500 block text-[9px] uppercase font-semibold">Advisor ID</span>
//                             <span className="font-mono font-medium truncate block">{selectedCase.advisor_id || "—"}</span>
//                           </div>
//                           <div>
//                             <span className="text-slate-500 block text-[9px] uppercase font-semibold">Experience</span>
//                             <span className="truncate block">{selectedCase.advisor_experience || "—"}</span>
//                           </div>
//                         </div>
                        
//                         <div className="grid grid-cols-2 gap-1 pt-1 border-t border-slate-800/50 items-center">
//                           <div>
//                             <span className="text-slate-500 block text-[9px] uppercase font-semibold">History Risk</span>
//                             <span className="font-mono text-rose-400">{selectedCase.advisor_history_risk ?? "—"}</span>
//                           </div>
//                           <div>
//                             <span className="text-slate-500 block text-[9px] uppercase font-semibold">Rationale</span>
//                             <span className={`inline-block px-1 rounded text-[9px] font-bold ${
//                               selectedCase.has_rationale === true || selectedCase.has_rationale === "true"
//                                 ? "bg-emerald-950 text-emerald-400 border border-emerald-800/50" 
//                                 : "bg-slate-950 text-slate-500 border border-slate-800"
//                             }`}>
//                               {selectedCase.has_rationale ? "FILED" : "MISSING"}
//                             </span>
//                           </div>
//                         </div>

//                         <div className="pt-1 border-t border-slate-800/50">
//                           <span className="text-slate-500 block text-[9px] uppercase font-semibold mb-0.5">Desk Notes Context</span>
//                           <p className="text-[10px] text-slate-400 leading-snug max-h-[48px] overflow-y-auto dynamic-scroll">
//                             {selectedCase.advisor_notes || "No transactional notes filed on submission."}
//                           </p>
//                         </div>
//                       </div>
//                     </div>

//                     {/* COLUMN 4: Exception Breakdown */}
//                     <div className="bg-slate-950/20 border border-slate-800/40 p-1.5 rounded flex flex-col min-h-0">
//                       <div className="flex items-center gap-1 border-b border-slate-800 pb-1 mb-1.5 flex-shrink-0">
//                         <HelpCircle className="w-3 h-3 text-rose-400" />
//                         <h4 className="text-[9px] font-bold text-rose-400 uppercase tracking-wider">Exception Breakdown</h4>
//                       </div>
//                       <div className="text-[11px] text-slate-300 overflow-y-auto dynamic-scroll flex-1 pr-0.5 leading-snug">
//                         <div className="text-slate-500 text-[9px] uppercase font-semibold mb-0.5">Flag Reason</div>
//                         <p className="text-[10px] text-rose-300/90">{selectedCase.flag_reason || "No structural exceptions found."}</p>
//                       </div>
//                     </div>

//                   </div>

//                   {/* Retained Policy Badges Row */}
//                   <div className="flex-shrink-0">
//                     <div className="flex flex-wrap gap-1 items-center">
//                       <span className="text-[9px] font-black text-slate-600 uppercase tracking-wider mr-1">Policies:</span>
//                       {renderPolicies(selectedCase.retrieved_policies)}
//                     </div>
//                   </div>

//                   {/* Persistent Sign-off Form Area */}
//                   <div className="border-t border-slate-800 pt-1 flex gap-2 items-end flex-shrink-0">
//                     <div className="flex-1 flex flex-col">
//                       <label className="text-[9px] font-black text-slate-400 uppercase tracking-widest mb-0.5">
//                         Reviewer Sign-off Notes
//                       </label>
//                       <input
//                         type="text"
//                         value={currentNotes}
//                         disabled={isFinalized}
//                         onChange={(e) => handleNotesChange(e.target.value)}
//                         placeholder={isFinalized ? "Audit history signature locked." : "Enter compliance justification or structural risk override arguments..."}
//                         className="w-full bg-slate-950 border border-slate-800 rounded px-2 py-1 text-xs text-slate-200 focus:outline-none focus:border-purple-500/80 disabled:opacity-40 transition-colors placeholder:text-slate-600"
//                       />
//                     </div>
                    
//                     <div className="flex gap-1.5">
//                       <button
//                         onClick={handleApproveAI}
//                         disabled={isFinalized}
//                         className="bg-emerald-600 hover:bg-emerald-500 disabled:bg-slate-800 disabled:text-slate-500 text-slate-950 font-black text-xs px-2.5 py-1 rounded transition-colors uppercase tracking-wider whitespace-nowrap"
//                       >
//                         Approve AI
//                       </button>
//                       <button
//                         onClick={handleOverrideAI}
//                         disabled={isFinalized}
//                         className="bg-purple-600 hover:bg-purple-500 disabled:bg-slate-800 disabled:text-slate-500 text-slate-100 font-black text-xs px-2.5 py-1 rounded transition-colors uppercase tracking-wider whitespace-nowrap"
//                       >
//                         Override AI
//                       </button>
//                       <button
//                         onClick={handleEscalate}
//                         disabled={isFinalized}
//                         className="bg-rose-600 hover:bg-rose-500 disabled:bg-slate-800 disabled:text-slate-500 text-slate-100 font-black text-xs px-2.5 py-1 rounded transition-colors uppercase tracking-wider whitespace-nowrap"
//                       >
//                         Escalate
//                       </button>
//                     </div>
//                   </div>

//                 </div>
//               );
//             })()
//           ) : (
//             <div className="h-full flex items-center justify-center text-slate-500 text-xs font-semibold border border-dashed border-slate-800 rounded">
//               Select an active risk file from the lists above to load the compliance audit space.
//             </div>
//           )}
//         </div>

//       </div>
//     </div>
//   );
// }

// export default Dashboard;

// /* VERSION 6 */

// import { useEffect, useState, useRef } from "react";
// import { getCases } from "../api/cases";
// import { AlertCircle, CheckCircle, Clock, ShieldAlert, FileText, User, Briefcase, HelpCircle } from "lucide-react";

// interface CaseAuditState {
//   reviewStatus: "Reviewed" | "Not reviewed";
//   notes: string;
// }

// function Dashboard() {
//   const [cases, setCases] = useState<any[]>([]);
//   const [selectedCase, setSelectedCase] = useState<any | null>(null);
  
//   // Per-case persistence engine keyed by trade_id
//   const [caseStates, setCaseStates] = useState<Record<string, CaseAuditState>>({});
//   const [currentNotes, setCurrentNotes] = useState<string>("");

//   // --- Spreadsheet Column Resize State ---
//   const [urgentWidths, setUrgentWidths] = useState({ tradeId: 100, risk: 75, conf: 75, reason: 260 });
//   const [queuedWidths, setQueuedWidths] = useState({ tradeId: 100, priority: 70, risk: 75, conf: 75, reason: 240 });

//   const dragInfo = useRef<{ table: 'urgent' | 'queued'; col: string; startX: number; startWidth: number } | null>(null);

//   useEffect(() => {
//     getCases()
//       .then((data) => {
//         if (Array.isArray(data)) {
//           setCases(data);
          
//           // Seed initial default auditing structures for all fetched trades
//           const initialStates: Record<string, CaseAuditState> = {};
//           data.forEach((c) => {
//             if (c?.trade_id) {
//               initialStates[c.trade_id] = { reviewStatus: "Not reviewed", notes: "" };
//             }
//           });
//           setCaseStates(initialStates);

//           const urgentCases = data.filter((c) => c?.escalation_level === "urgent");
//           const queuedCases = data
//             .filter((c) => c?.escalation_level === "priority" || c?.escalation_level === "queue")
//             .sort((a, b) => (Number(b?.priority_score) || 0) - (Number(a?.priority_score) || 0));

//           if (urgentCases.length > 0) handleCaseSelection(urgentCases[0], initialStates);
//           else if (queuedCases.length > 0) handleCaseSelection(queuedCases[0], initialStates);
//         }
//       })
//       .catch((err) => console.error("API Fetch Error:", err));
//   }, []);

//   const handleCaseSelection = (targetCase: any, latestStates = caseStates) => {
//     setSelectedCase(targetCase);
//     if (targetCase?.trade_id) {
//       const savedState = latestStates[targetCase.trade_id];
//       setCurrentNotes(savedState ? savedState.notes : "");
//     }
//   };

//   const handleNotesChange = (text: string) => {
//     setCurrentNotes(text);
//     if (selectedCase?.trade_id) {
//       setCaseStates(prev => ({
//         ...prev,
//         [selectedCase.trade_id]: {
//           ...prev[selectedCase.trade_id],
//           notes: text
//         }
//       }));
//     }
//   };

//   const commitAuditStatus = () => {
//     if (!selectedCase?.trade_id) return;
//     setCaseStates(prev => ({
//       ...prev,
//       [selectedCase.trade_id]: {
//         reviewStatus: "Reviewed",
//         notes: currentNotes
//       }
//     }));
//     console.log(`Log committed for ${selectedCase.trade_id}: Status -> Reviewed. Notes -> ${currentNotes}`);
//   };

//   // --- Mouse Resize Handlers ---
//   const handleMouseDown = (table: 'urgent' | 'queued', col: string, e: React.MouseEvent) => {
//     e.preventDefault();
//     const currentWidths = table === 'urgent' ? urgentWidths : queuedWidths;
//     dragInfo.current = {
//       table,
//       col,
//       startX: e.clientX,
//       startWidth: (currentWidths as any)[col]
//     };
//     document.addEventListener("mousemove", handleMouseMove);
//     document.addEventListener("mouseup", handleMouseUp);
//   };

//   const handleMouseMove = (e: MouseEvent) => {
//     if (!dragInfo.current) return;
//     const { table, col, startX, startWidth } = dragInfo.current;
//     const deltaX = e.clientX - startX;
//     const newWidth = Math.max(50, startWidth + deltaX);

//     if (table === 'urgent') {
//       setUrgentWidths(prev => ({ ...prev, [col]: newWidth }));
//     } else {
//       setQueuedWidths(prev => ({ ...prev, [col]: newWidth }));
//     }
//   };

//   const handleMouseUp = () => {
//     dragInfo.current = null;
//     document.removeEventListener("mousemove", handleMouseMove);
//     document.removeEventListener("mouseup", handleMouseUp);
//   };

//   const handleDoubleClick = (table: 'urgent' | 'queued') => {
//     if (table === 'urgent') {
//       setUrgentWidths({ tradeId: 100, risk: 75, conf: 75, reason: 260 });
//     } else {
//       setQueuedWidths({ tradeId: 100, priority: 70, risk: 75, conf: 75, reason: 240 });
//     }
//   };

//   const urgentCases = cases.filter((c) => c?.escalation_level === "urgent");
//   const queuedCases = cases
//     .filter((c) => c?.escalation_level === "priority" || c?.escalation_level === "queue")
//     .sort((a, b) => (Number(b?.priority_score) || 0) - (Number(a?.priority_score) || 0));

//   const countUrgent = urgentCases.length;
//   const countReview = queuedCases.length;
//   const countPassed = cases.filter(
//     (c) => c?.escalation_level !== "urgent" && c?.escalation_level !== "priority" && c?.escalation_level !== "queue"
//   ).length;

//   const renderPolicies = (policies: any) => {
//     if (!policies) return <span className="text-[10px] text-slate-500">No policies attached.</span>;
//     let items: string[] = [];
//     if (Array.isArray(policies)) items = policies;
//     else if (typeof policies === "string" && policies.startsWith("[")) {
//       items = policies.replace(/[\[\]']/g, "").split(",").map((p) => p.trim()).filter(Boolean);
//     } else if (typeof policies === "string" && policies.trim().length > 0) {
//       items = policies.split(",").map((p) => p.trim());
//     }
    
//     if (items.length === 0) return <span className="text-[10px] text-slate-500">No policies attached.</span>;
//     return items.map((policy, i) => (
//       <span key={i} className="px-1.5 py-0.5 bg-slate-950 text-[10px] rounded border border-slate-800 text-purple-300 font-mono">
//         {policy}
//       </span>
//     ));
//   };

//   return (
//     <div className="p-1 h-screen bg-slate-950 text-slate-100 flex flex-col gap-1 overflow-hidden select-none">
      
//       <style>{`
//         .dynamic-scroll { scrollbar-width: none; }
//         .dynamic-scroll::-webkit-scrollbar { width: 4px; height: 4px; display: none; }
//         .dynamic-scroll:hover { scrollbar-width: thin; }
//         .dynamic-scroll:hover::-webkit-scrollbar { display: block; }
//         .dynamic-scroll::-webkit-scrollbar-track { background: transparent; }
//         .dynamic-scroll::-webkit-scrollbar-thumb { background: rgba(148, 163, 184, 0.15); border-radius: 2px; }
//       `}</style>
      
//       {/* Top Header Metrics Layer */}
//       <div className="flex items-center justify-between border-b border-slate-900 pb-1">
//         <h1 className="text-base font-bold tracking-tight text-slate-200">
//           AI Compliance Review Copilot
//         </h1>
        
//         <div className="flex items-center gap-2">
//           <div className="bg-rose-950/30 border border-rose-500/30 rounded px-2 py-0.5 flex items-center gap-1.5 text-xs font-medium shadow-sm">
//             <AlertCircle className="w-3.5 h-3.5 text-rose-400" />
//             <span className="text-rose-300">Urgent:</span>
//             <span className="text-sm font-black text-rose-100">{countUrgent}</span>
//           </div>

//           <div className="bg-amber-950/30 border border-amber-500/30 rounded px-2 py-0.5 flex items-center gap-1.5 text-xs font-medium shadow-sm">
//             <Clock className="w-3.5 h-3.5 text-amber-400" />
//             <span className="text-amber-300">Review:</span>
//             <span className="text-sm font-black text-amber-100">{countReview}</span>
//           </div>

//           <div className="bg-emerald-950/30 border border-emerald-500/30 rounded px-2 py-0.5 flex items-center gap-1.5 text-xs font-medium shadow-sm">
//             <CheckCircle className="w-3.5 h-3.5 text-emerald-400" />
//             <span className="text-emerald-300">Passed:</span>
//             <span className="text-sm font-black text-emerald-100">{countPassed}</span>
//           </div>
//         </div>
//       </div>

//       {/* Main Viewport Grid Layout: 48% Upper Split / 52% Workspace Expansion */}
//       <div className="flex-1 grid grid-rows-[48fr_52fr] gap-1 min-h-0">
        
//         {/* UPPER VIEW: Side-by-Side Monitoring Lists */}
//         <div className="grid grid-cols-2 gap-1 min-h-0">
          
//           {/* URGENT TRACK PANEL */}
//           <div className="bg-slate-900 border border-rose-500/10 rounded-md p-1.5 flex flex-col min-h-0">
//             <div className="flex items-center gap-1 border-b border-slate-800 pb-0.5 mb-1">
//               <ShieldAlert className="w-3.5 h-3.5 text-rose-400" />
//               <h2 className="text-[10px] font-bold text-rose-400 uppercase tracking-wider">Urgent Action Required</h2>
//             </div>
            
//             <div className="flex-1 overflow-auto min-h-0 relative border border-slate-800/30 rounded dynamic-scroll">
//               {urgentCases.length === 0 ? (
//                 <p className="text-xs text-slate-500 p-1">No urgent cases outstanding.</p>
//               ) : (
//                 <table className="text-left text-xs border-collapse table-fixed w-max min-w-full">
//                   <thead className="sticky top-0 bg-slate-900 text-slate-400 font-bold uppercase text-[9px] border-b border-slate-800 z-10">
//                     <tr>
//                       <th style={{ width: urgentWidths.tradeId }} className="p-1 relative group">
//                         Trade ID
//                         <div onMouseDown={(e) => handleMouseDown('urgent', 'tradeId', e)} onDoubleClick={() => handleDoubleClick('urgent')} className="absolute right-0 top-0 bottom-0 w-1 bg-slate-700/0 group-hover:bg-purple-500/50 cursor-col-resize transition-colors" />
//                       </th>
//                       <th style={{ width: urgentWidths.risk }} className="p-1 text-right relative group">
//                         Risk Score
//                         <div onMouseDown={(e) => handleMouseDown('urgent', 'risk', e)} onDoubleClick={() => handleDoubleClick('urgent')} className="absolute right-0 top-0 bottom-0 w-1 bg-slate-700/0 group-hover:bg-purple-500/50 cursor-col-resize transition-colors" />
//                       </th>
//                       <th style={{ width: urgentWidths.conf }} className="p-1 text-right relative group">
//                         Conf.
//                         <div onMouseDown={(e) => handleMouseDown('urgent', 'conf', e)} onDoubleClick={() => handleDoubleClick('urgent')} className="absolute right-0 top-0 bottom-0 w-1 bg-slate-700/0 group-hover:bg-purple-500/50 cursor-col-resize transition-colors" />
//                       </th>
//                       <th style={{ width: urgentWidths.reason }} className="p-1 pl-2 relative group">
//                         Flag Reason
//                         <div onMouseDown={(e) => handleMouseDown('urgent', 'reason', e)} onDoubleClick={() => handleDoubleClick('urgent')} className="absolute right-0 top-0 bottom-0 w-1 bg-slate-700/0 group-hover:bg-purple-500/50 cursor-col-resize transition-colors" />
//                       </th>
//                     </tr>
//                   </thead>
//                   <tbody className="divide-y divide-slate-800/30">
//                     {urgentCases.map((c, idx) => {
//                       const isSelected = selectedCase?.trade_id === c?.trade_id;
//                       const riskVal = 1 - (Number(c?.compliance_probability) ?? 1.0);
//                       return (
//                         <tr
//                           key={`${c?.trade_id}-${idx}`}
//                           onClick={() => handleCaseSelection(c)}
//                           className={`cursor-pointer text-[11px] transition-colors ${isSelected ? 'bg-rose-950/40 font-semibold border-l-2 border-rose-500 text-rose-200 shadow-[inner_0_1px_0_rgba(244,63,94,0.1)]' : 'hover:bg-slate-800/30 text-slate-300'}`}
//                         >
//                           <td className="p-1 font-mono truncate">{c?.trade_id}</td>
//                           <td className="p-1 text-right font-mono text-rose-400/90">{riskVal.toFixed(2)}</td>
//                           <td className="p-1 text-right font-mono text-slate-400">{(Number(c?.confidence_score) || 0).toFixed(2)}</td>
//                           <td className="p-1 pl-2 truncate text-[10px]">{c?.flag_reason}</td>
//                         </tr>
//                       );
//                     })}
//                   </tbody>
//                 </table>
//               )}
//             </div>
//           </div>

//           {/* REVIEW QUEUE PANEL */}
//           <div className="bg-slate-900 border border-slate-800/80 rounded-md p-1.5 flex flex-col min-h-0">
//             <div className="flex items-center gap-1 border-b border-slate-800 pb-0.5 mb-1">
//               <Clock className="w-3.5 h-3.5 text-amber-400" />
//               <h2 className="text-[10px] font-bold text-amber-400 uppercase tracking-wider">Review</h2>
//             </div>
            
//             <div className="flex-1 overflow-auto min-h-0 relative border border-slate-800/30 rounded dynamic-scroll">
//               {queuedCases.length === 0 ? (
//                 <p className="text-xs text-slate-500 p-1">Review queue empty.</p>
//               ) : (
//                 <table className="text-left text-xs border-collapse table-fixed w-max min-w-full">
//                   <thead className="sticky top-0 bg-slate-900 text-slate-400 font-bold uppercase text-[9px] border-b border-slate-800 z-10">
//                     <tr>
//                       <th style={{ width: queuedWidths.tradeId }} className="p-1 relative group">
//                         Trade ID
//                         <div onMouseDown={(e) => handleMouseDown('queued', 'tradeId', e)} onDoubleClick={() => handleDoubleClick('queued')} className="absolute right-0 top-0 bottom-0 w-1 bg-slate-700/0 group-hover:bg-purple-500/50 cursor-col-resize transition-colors" />
//                       </th>
//                       <th style={{ width: queuedWidths.priority }} className="p-1 text-right relative group text-amber-400">
//                         Priority
//                         <div onMouseDown={(e) => handleMouseDown('queued', 'priority', e)} onDoubleClick={() => handleDoubleClick('queued')} className="absolute right-0 top-0 bottom-0 w-1 bg-slate-700/0 group-hover:bg-purple-500/50 cursor-col-resize transition-colors" />
//                       </th>
//                       <th style={{ width: queuedWidths.risk }} className="p-1 text-right relative group">
//                         Risk Score
//                         <div onMouseDown={(e) => handleMouseDown('queued', 'risk', e)} onDoubleClick={() => handleDoubleClick('queued')} className="absolute right-0 top-0 bottom-0 w-1 bg-slate-700/0 group-hover:bg-purple-500/50 cursor-col-resize transition-colors" />
//                       </th>
//                       <th style={{ width: queuedWidths.conf }} className="p-1 text-right relative group">
//                         Conf.
//                         <div onMouseDown={(e) => handleMouseDown('queued', 'conf', e)} onDoubleClick={() => handleDoubleClick('queued')} className="absolute right-0 top-0 bottom-0 w-1 bg-slate-700/0 group-hover:bg-purple-500/50 cursor-col-resize transition-colors" />
//                       </th>
//                       <th style={{ width: queuedWidths.reason }} className="p-1 pl-2 relative group">
//                         Flag Reason
//                         <div onMouseDown={(e) => handleMouseDown('queued', 'reason', e)} onDoubleClick={() => handleDoubleClick('queued')} className="absolute right-0 top-0 bottom-0 w-1 bg-slate-700/0 group-hover:bg-purple-500/50 cursor-col-resize transition-colors" />
//                       </th>
//                     </tr>
//                   </thead>
//                   <tbody className="divide-y divide-slate-800/30">
//                     {queuedCases.map((c, idx) => {
//                       const isSelected = selectedCase?.trade_id === c?.trade_id;
//                       const riskVal = 1 - (Number(c?.compliance_probability) ?? 1.0);
//                       return (
//                         <tr
//                           key={`${c?.trade_id}-${idx}`}
//                           onClick={() => handleCaseSelection(c)}
//                           className={`cursor-pointer text-[11px] transition-colors ${isSelected ? 'bg-purple-950/40 font-semibold border-l-2 border-purple-500 text-purple-200 shadow-[inner_0_1px_0_rgba(168,85,247,0.1)]' : 'hover:bg-slate-800/30 text-slate-300'}`}
//                         >
//                           <td className="p-1 font-mono truncate">{c?.trade_id}</td>
//                           <td className="p-1 text-right font-mono font-bold text-amber-400">{c?.priority_score ?? "0"}</td>
//                           <td className="p-1 text-right font-mono text-rose-400/90">{riskVal.toFixed(2)}</td>
//                           <td className="p-1 text-right font-mono text-slate-400">{(Number(c?.confidence_score) || 0).toFixed(2)}</td>
//                           <td className="p-1 pl-2 truncate text-[10px]">{c?.flag_reason}</td>
//                         </tr>
//                       );
//                     })}
//                   </tbody>
//                 </table>
//               )}
//             </div>
//           </div>

//         </div>

//         {/* LOWER VIEW: High-Density Workspace (Optimized Layout Matrix) */}
//         <div className="bg-slate-900 border border-slate-800 rounded-md p-2 flex flex-col min-h-0 shadow-2xl">
//           {selectedCase ? (
//             (() => {
//               const currentState = caseStates[selectedCase.trade_id] || { reviewStatus: "Not reviewed", notes: "" };
//               const isReviewed = currentState.reviewStatus === "Reviewed";
//               const riskVal = 1 - (Number(selectedCase.compliance_probability) || 0);
              
//               return (
//                 <div className="flex flex-col h-full gap-1.5 min-h-0">
                  
//                   {/* Title & Micro Scores Strip */}
//                   <div className="flex items-center justify-between border-b border-slate-800 pb-1 flex-shrink-0">
//                     <div className="flex items-center gap-1.5">
//                       <span className="text-[9px] font-black uppercase tracking-wider text-purple-400 bg-purple-950/30 px-1.5 py-0.5 rounded border border-purple-900/40">
//                         Selected Case Audit
//                       </span>
//                       <span className="text-xs font-mono font-bold text-slate-100">{selectedCase.trade_id}</span>
                      
//                       <span className={`px-1.5 py-0.5 rounded text-[9px] font-bold tracking-wide border ${
//                         isReviewed 
//                           ? "bg-emerald-950/40 text-emerald-400 border-emerald-800/40" 
//                           : "bg-slate-950 text-amber-400 border-amber-900/40"
//                       }`}>
//                         {currentState.reviewStatus.toUpperCase()}
//                       </span>
//                     </div>
                    
//                     {/* Compact Scores Interface */}
//                     <div className="flex items-center gap-3 bg-slate-950/80 px-2 py-0.5 rounded border border-slate-800/60 text-[11px]">
//                       <div>
//                         <span className="text-slate-500 font-medium text-[9px] uppercase mr-1">Risk:</span>
//                         <span className="font-mono font-bold text-rose-400">{riskVal.toFixed(4)}</span>
//                       </div>
//                       <div className="border-l border-slate-800 h-3" />
//                       <div>
//                         <span className="text-slate-500 font-medium text-[9px] uppercase mr-1">Conf:</span>
//                         <span className="font-mono font-bold text-sky-400">{Number(selectedCase.confidence_score || 0).toFixed(4)}</span>
//                       </div>
//                       <div className="border-l border-slate-800 h-3" />
//                       <div>
//                         <span className="text-slate-500 font-medium text-[9px] uppercase mr-1">Priority:</span>
//                         <span className="font-mono font-bold text-amber-400">{selectedCase.priority_score ?? "—"}</span>
//                       </div>
//                     </div>
//                   </div>

//                   {/* High-Density 4-Column Structured Audit Grid */}
//                   <div className="grid grid-cols-4 gap-2 flex-1 min-h-0 py-0.5">
                    
//                     {/* COLUMN 1: Trade Fields */}
//                     <div className="bg-slate-950/20 border border-slate-800/40 p-1.5 rounded flex flex-col min-h-0">
//                       <div className="flex items-center gap-1 border-b border-slate-800 pb-1 mb-1.5 flex-shrink-0">
//                         <Briefcase className="w-3 h-3 text-purple-400" />
//                         <h4 className="text-[9px] font-bold text-purple-400 uppercase tracking-wider">Trade Fields</h4>
//                       </div>
//                       <div className="text-[11px] space-y-1.5 overflow-y-auto dynamic-scroll text-slate-300">
//                         <div>
//                           <div className="text-slate-500 text-[9px] uppercase font-semibold">Investment Type</div>
//                           <div className="font-medium truncate">{selectedCase.investment_type || selectedCase.asset_class || "N/A"}</div>
//                         </div>
//                         <div>
//                           <div className="text-slate-500 text-[9px] uppercase font-semibold">Investment Amount</div>
//                           <div className="font-mono font-bold text-emerald-400">
//                             {selectedCase.investment_amount ? `$${Number(selectedCase.investment_amount).toLocaleString(undefined, {minimumFractionDigits: 2})}` : "N/A"}
//                           </div>
//                         </div>
//                         <div className="pt-1 border-t border-slate-800/50 text-[10px] text-slate-500 space-y-0.5 font-mono">
//                           <div>Notional: ${Number(selectedCase.notional_value || 0).toLocaleString()}</div>
//                           <div className="truncate">Time: {selectedCase.timestamp || "N/A"}</div>
//                         </div>
//                       </div>
//                     </div>

//                     {/* COLUMN 2: Client Profile */}
//                     <div className="bg-slate-950/20 border border-slate-800/40 p-1.5 rounded flex flex-col min-h-0">
//                       <div className="flex items-center gap-1 border-b border-slate-800 pb-1 mb-1.5 flex-shrink-0">
//                         <User className="w-3 h-3 text-sky-400" />
//                         <h4 className="text-[9px] font-bold text-sky-400 uppercase tracking-wider">Client Profile</h4>
//                       </div>
//                       <div className="text-[11px] space-y-1 overflow-y-auto dynamic-scroll text-slate-300 grid grid-cols-1 gap-y-1.5">
//                         <div className="grid grid-cols-2 gap-1">
//                           <div>
//                             <div className="text-slate-500 text-[9px] uppercase font-semibold">Age</div>
//                             <div className="font-mono">{selectedCase.client_age ?? "—"}</div>
//                           </div>
//                           <div>
//                             <div className="text-slate-500 text-[9px] uppercase font-semibold">Income</div>
//                             <div className="font-mono truncate">{selectedCase.client_income ? `$${Number(selectedCase.client_income).toLocaleString()}` : "—"}</div>
//                           </div>
//                         </div>
//                         <div>
//                           <div className="text-slate-500 text-[9px] uppercase font-semibold">Risk Tolerance</div>
//                           <div className="truncate">{selectedCase.risk_tolerance || selectedCase.client_risk_tolerance || "—"}</div>
//                         </div>
//                         <div>
//                           <div className="text-slate-500 text-[9px] uppercase font-semibold">Experience Level</div>
//                           <div className="truncate">{selectedCase.investment_experience || "—"}</div>
//                         </div>
//                         <div>
//                           <div className="text-slate-500 text-[9px] uppercase font-semibold">Objective</div>
//                           <div className="truncate text-[10px] leading-tight">{selectedCase.investment_objective || "—"}</div>
//                         </div>
//                         <div>
//                           <div className="text-slate-500 text-[9px] uppercase font-semibold">Time Horizon</div>
//                           <div className="truncate">{selectedCase.investment_time_horizon || "—"}</div>
//                         </div>
//                       </div>
//                     </div>

//                     {/* COLUMN 3: Advisor Records */}
//                     <div className="bg-slate-950/20 border border-slate-800/40 p-1.5 rounded flex flex-col min-h-0">
//                       <div className="flex items-center gap-1 border-b border-slate-800 pb-1 mb-1.5 flex-shrink-0">
//                         <FileText className="w-3 h-3 text-amber-400" />
//                         <h4 className="text-[9px] font-bold text-amber-400 uppercase tracking-wider">Advisor Records</h4>
//                       </div>
//                       <div className="text-[11px] space-y-1.5 overflow-y-auto dynamic-scroll flex-1 text-slate-300">
//                         <div className="grid grid-cols-2 gap-1 text-[10px]">
//                           <div>
//                             <span className="text-slate-500 block text-[9px] uppercase font-semibold">Advisor ID</span>
//                             <span className="font-mono font-medium truncate block">{selectedCase.advisor_id || "—"}</span>
//                           </div>
//                           <div>
//                             <span className="text-slate-500 block text-[9px] uppercase font-semibold">Experience</span>
//                             <span className="truncate block">{selectedCase.advisor_experience || "—"}</span>
//                           </div>
//                         </div>
                        
//                         <div className="grid grid-cols-2 gap-1 pt-1 border-t border-slate-800/50 items-center">
//                           <div>
//                             <span className="text-slate-500 block text-[9px] uppercase font-semibold">History Risk</span>
//                             <span className="font-mono text-rose-400">{selectedCase.advisor_history_risk ?? "—"}</span>
//                           </div>
//                           <div>
//                             <span className="text-slate-500 block text-[9px] uppercase font-semibold">Rationale</span>
//                             <span className={`inline-block px-1 rounded text-[9px] font-bold ${
//                               selectedCase.has_rationale === true || selectedCase.has_rationale === "true"
//                                 ? "bg-emerald-950 text-emerald-400 border border-emerald-800/50" 
//                                 : "bg-slate-950 text-slate-500 border border-slate-800"
//                             }`}>
//                               {selectedCase.has_rationale ? "FILED" : "MISSING"}
//                             </span>
//                           </div>
//                         </div>

//                         <div className="pt-1 border-t border-slate-800/50">
//                           <span className="text-slate-500 block text-[9px] uppercase font-semibold mb-0.5">Desk Notes Context</span>
//                           <p className="text-[10px] text-slate-400 leading-snug max-h-[48px] overflow-y-auto dynamic-scroll">
//                             {selectedCase.advisor_notes || "No transactional notes filed on submission."}
//                           </p>
//                         </div>
//                       </div>
//                     </div>

//                     {/* COLUMN 4: Exception Breakdown */}
//                     <div className="bg-slate-950/20 border border-slate-800/40 p-1.5 rounded flex flex-col min-h-0">
//                       <div className="flex items-center gap-1 border-b border-slate-800 pb-1 mb-1.5 flex-shrink-0">
//                         <HelpCircle className="w-3 h-3 text-rose-400" />
//                         <h4 className="text-[9px] font-bold text-rose-400 uppercase tracking-wider">Exception Breakdown</h4>
//                       </div>
//                       <div className="text-[11px] text-slate-300 overflow-y-auto dynamic-scroll flex-1 pr-0.5 leading-snug">
//                         <div className="text-slate-500 text-[9px] uppercase font-semibold mb-0.5">Flag Reason</div>
//                         <p className="text-[10px] text-rose-300/90">{selectedCase.flag_reason || "No structural exceptions found."}</p>
//                       </div>
//                     </div>

//                   </div>

//                   {/* Retained Policy Badges Row */}
//                   <div className="flex-shrink-0">
//                     <div className="flex flex-wrap gap-1 items-center">
//                       <span className="text-[9px] font-black text-slate-600 uppercase tracking-wider mr-1">Policies:</span>
//                       {renderPolicies(selectedCase.retrieved_policies)}
//                     </div>
//                   </div>

//                   {/* Persistent Sign-off Form Area */}
//                   <div className="border-t border-slate-800 pt-1 flex gap-2 items-end flex-shrink-0">
//                     <div className="flex-1 flex flex-col">
//                       <label className="text-[9px] font-black text-slate-400 uppercase tracking-widest mb-0.5">
//                         Reviewer Sign-off Notes
//                       </label>
//                       <input
//                         type="text"
//                         value={currentNotes}
//                         disabled={isReviewed}
//                         onChange={(e) => handleNotesChange(e.target.value)}
//                         placeholder={isReviewed ? "Audit completed. History log committed." : "Enter compliance justification or structural risk override arguments..."}
//                         className="w-full bg-slate-950 border border-slate-800 rounded px-2 py-1 text-xs text-slate-200 focus:outline-none focus:border-purple-500/80 disabled:opacity-40 transition-colors placeholder:text-slate-600"
//                       />
//                     </div>
                    
//                     <div className="flex gap-1.5">
//                       <button
//                         onClick={commitAuditStatus}
//                         disabled={isReviewed}
//                         className="bg-emerald-600 hover:bg-emerald-500 disabled:bg-slate-800 disabled:text-slate-500 text-slate-950 font-black text-xs px-3 py-1 rounded transition-colors uppercase tracking-wider"
//                       >
//                         Approve
//                       </button>
//                       <button
//                         onClick={commitAuditStatus}
//                         disabled={isReviewed}
//                         className="bg-purple-600 hover:bg-purple-500 disabled:bg-slate-800 disabled:text-slate-500 text-slate-100 font-black text-xs px-3 py-1 rounded transition-colors uppercase tracking-wider"
//                       >
//                         Override
//                       </button>
//                     </div>
//                   </div>

//                 </div>
//               );
//             })()
//           ) : (
//             <div className="h-full flex items-center justify-center text-slate-500 text-xs font-semibold border border-dashed border-slate-800 rounded">
//               Select an active risk file from the lists above to load the compliance audit space.
//             </div>
//           )}
//         </div>

//       </div>
//     </div>
//   );
// }

// export default Dashboard;

// /* VERSION 5 */

// import { useEffect, useState, useRef } from "react";
// import { getCases } from "../api/cases";
// import { AlertCircle, CheckCircle, Clock, ShieldAlert } from "lucide-react";

// // Track states locally per trade_id (Status & User input persistence)
// interface CaseAuditState {
//   reviewStatus: "Reviewed" | "Not reviewed";
//   notes: string;
// }

// function Dashboard() {
//   const [cases, setCases] = useState<any[]>([]);
//   const [selectedCase, setSelectedCase] = useState<any | null>(null);
  
//   // Per-case persistence engine keyed by trade_id
//   const [caseStates, setCaseStates] = useState<Record<string, CaseAuditState>>({});
//   const [currentNotes, setCurrentNotes] = useState<string>("");

//   // --- Spreadsheet Column Resize State ---
//   const [urgentWidths, setUrgentWidths] = useState({ tradeId: 100, risk: 75, conf: 75, reason: 260 });
//   const [queuedWidths, setQueuedWidths] = useState({ tradeId: 100, priority: 70, risk: 75, conf: 75, reason: 240 });

//   const dragInfo = useRef<{ table: 'urgent' | 'queued'; col: string; startX: number; startWidth: number } | null>(null);

//   useEffect(() => {
//     getCases()
//       .then((data) => {
//         if (Array.isArray(data)) {
//           setCases(data);
          
//           // Seed initial default auditing structures for all fetched trades
//           const initialStates: Record<string, CaseAuditState> = {};
//           data.forEach((c) => {
//             if (c?.trade_id) {
//               initialStates[c.trade_id] = { reviewStatus: "Not reviewed", notes: "" };
//             }
//           });
//           setCaseStates(initialStates);

//           const urgentCases = data.filter((c) => c?.escalation_level === "urgent");
//           const queuedCases = data
//             .filter((c) => c?.escalation_level === "priority" || c?.escalation_level === "queue")
//             .sort((a, b) => (Number(b?.priority_score) || 0) - (Number(a?.priority_score) || 0));

//           if (urgentCases.length > 0) handleCaseSelection(urgentCases[0], initialStates);
//           else if (queuedCases.length > 0) handleCaseSelection(queuedCases[0], initialStates);
//         }
//       })
//       .catch((err) => console.error("API Fetch Error:", err));
//   }, []);

//   // Sync state cleanly when switching active case cards
//   const handleCaseSelection = (targetCase: any, latestStates = caseStates) => {
//     setSelectedCase(targetCase);
//     if (targetCase?.trade_id) {
//       const savedState = latestStates[targetCase.trade_id];
//       setCurrentNotes(savedState ? savedState.notes : "");
//     }
//   };

//   // Sync live text area inputs to memory buffer on keystroke
//   const handleNotesChange = (text: string) => {
//     setCurrentNotes(text);
//     if (selectedCase?.trade_id) {
//       setCaseStates(prev => ({
//         ...prev,
//         [selectedCase.trade_id]: {
//           ...prev[selectedCase.trade_id],
//           notes: text
//         }
//       }));
//     }
//   };

//   // Commit review action handler
//   const commitAuditStatus = () => {
//     if (!selectedCase?.trade_id) return;
//     setCaseStates(prev => ({
//       ...prev,
//       [selectedCase.trade_id]: {
//         reviewStatus: "Reviewed",
//         notes: currentNotes
//       }
//     }));
//     // Optional placeholder logic to broadcast log data to a server component
//     console.log(`Log committed for ${selectedCase.trade_id}: Status -> Reviewed. Notes -> ${currentNotes}`);
//   };

//   // --- Mouse Resize Handlers ---
//   const handleMouseDown = (table: 'urgent' | 'queued', col: string, e: React.MouseEvent) => {
//     e.preventDefault();
//     const currentWidths = table === 'urgent' ? urgentWidths : queuedWidths;
//     dragInfo.current = {
//       table,
//       col,
//       startX: e.clientX,
//       startWidth: (currentWidths as any)[col]
//     };
//     document.addEventListener("mousemove", handleMouseMove);
//     document.addEventListener("mouseup", handleMouseUp);
//   };

//   const handleMouseMove = (e: MouseEvent) => {
//     if (!dragInfo.current) return;
//     const { table, col, startX, startWidth } = dragInfo.current;
//     const deltaX = e.clientX - startX;
//     const newWidth = Math.max(50, startWidth + deltaX);

//     if (table === 'urgent') {
//       setUrgentWidths(prev => ({ ...prev, [col]: newWidth }));
//     } else {
//       setQueuedWidths(prev => ({ ...prev, [col]: newWidth }));
//     }
//   };

//   const handleMouseUp = () => {
//     dragInfo.current = null;
//     document.removeEventListener("mousemove", handleMouseMove);
//     document.removeEventListener("mouseup", handleMouseUp);
//   };

//   const handleDoubleClick = (table: 'urgent' | 'queued') => {
//     if (table === 'urgent') {
//       setUrgentWidths({ tradeId: 100, risk: 75, conf: 75, reason: 260 });
//     } else {
//       setQueuedWidths({ tradeId: 100, priority: 70, risk: 75, conf: 75, reason: 240 });
//     }
//   };

//   // Data Separation Layers
//   const urgentCases = cases.filter((c) => c?.escalation_level === "urgent");
//   const queuedCases = cases
//     .filter((c) => c?.escalation_level === "priority" || c?.escalation_level === "queue")
//     .sort((a, b) => (Number(b?.priority_score) || 0) - (Number(a?.priority_score) || 0));

//   const countUrgent = urgentCases.length;
//   const countReview = queuedCases.length;
//   const countPassed = cases.filter(
//     (c) => c?.escalation_level !== "urgent" && c?.escalation_level !== "priority" && c?.escalation_level !== "queue"
//   ).length;

//   const renderPolicies = (policies: any) => {
//     if (!policies) return <span className="text-[11px] text-slate-500">No policies attached.</span>;
//     let items: string[] = [];
//     if (Array.isArray(policies)) items = policies;
//     else if (typeof policies === "string" && policies.startsWith("[")) {
//       items = policies.replace(/[\[\]']/g, "").split(",").map((p) => p.trim()).filter(Boolean);
//     } else if (typeof policies === "string" && policies.trim().length > 0) {
//       items = policies.split(",").map((p) => p.trim());
//     }
    
//     if (items.length === 0) return <span className="text-[11px] text-slate-500">No policies attached.</span>;
//     return items.map((policy, i) => (
//       <span key={i} className="px-1.5 py-0.5 bg-slate-950 text-[10px] rounded border border-slate-800 text-purple-300 font-mono">
//         {policy}
//       </span>
//     ));
//   };

//   return (
//     // Height locked layout context containing ultra minimal padding profiles
//     <div className="p-1 h-screen bg-slate-950 text-slate-100 flex flex-col gap-1 overflow-hidden select-none">
      
//       <style>{`
//         .dynamic-scroll { scrollbar-width: none; }
//         .dynamic-scroll::-webkit-scrollbar { width: 5px; height: 5px; display: none; }
//         .dynamic-scroll:hover { scrollbar-width: thin; }
//         .dynamic-scroll:hover::-webkit-scrollbar { display: block; }
//         .dynamic-scroll::-webkit-scrollbar-track { background: rgba(15, 23, 42, 0.3); }
//         .dynamic-scroll::-webkit-scrollbar-thumb { background: rgba(148, 163, 184, 0.2); border-radius: 4px; }
//         .dynamic-scroll::-webkit-scrollbar-thumb:hover { background: rgba(148, 163, 184, 0.5); }
//       `}</style>
      
//       {/* --- Flattened Top Horizontal Layer (Zero excess layout margins) --- */}
//       <div className="flex items-center justify-between border-b border-slate-900 pb-1">
//         <h1 className="text-base font-bold tracking-tight text-slate-200">
//           AI Compliance Review Copilot
//         </h1>
        
//         <div className="flex items-center gap-2">
//           <div className="bg-rose-950/30 border border-rose-500/30 rounded px-2 py-0.5 flex items-center gap-1.5 text-xs font-medium shadow-sm">
//             <AlertCircle className="w-3.5 h-3.5 text-rose-400" />
//             <span className="text-rose-300">Urgent:</span>
//             <span className="text-sm font-black text-rose-100">{countUrgent}</span>
//           </div>

//           <div className="bg-amber-950/30 border border-amber-500/30 rounded px-2 py-0.5 flex items-center gap-1.5 text-xs font-medium shadow-sm">
//             <Clock className="w-3.5 h-3.5 text-amber-400" />
//             <span className="text-amber-300">Review:</span>
//             <span className="text-sm font-black text-amber-100">{countReview}</span>
//           </div>

//           <div className="bg-emerald-950/30 border border-emerald-500/30 rounded px-2 py-0.5 flex items-center gap-1.5 text-xs font-medium shadow-sm">
//             <CheckCircle className="w-3.5 h-3.5 text-emerald-400" />
//             <span className="text-emerald-300">Passed:</span>
//             <span className="text-sm font-black text-emerald-100">{countPassed}</span>
//           </div>
//         </div>
//       </div>

//       {/* --- Main Viewport Flex-Grid Stack: Upper split gets remaining 50% allocations --- */}
//       <div className="flex-1 grid grid-rows-[48fr_52fr] gap-1 min-h-0">
        
//         {/* UPPER VIEW: Horizontal Split Lists */}
//         <div className="grid grid-cols-2 gap-1 min-h-0">
          
//           {/* URGENT ACTION REQUIRED TRACK PANEL */}
//           <div className="bg-slate-900 border border-rose-500/10 rounded-md p-1.5 flex flex-col min-h-0">
//             <div className="flex items-center gap-1 border-b border-slate-800 pb-0.5 mb-1">
//               <ShieldAlert className="w-3.5 h-3.5 text-rose-400" />
//               <h2 className="text-[10px] font-bold text-rose-400 uppercase tracking-wider">Urgent Action Required</h2>
//             </div>
            
//             <div className="flex-1 overflow-auto min-h-0 relative border border-slate-800/30 rounded dynamic-scroll">
//               {urgentCases.length === 0 ? (
//                 <p className="text-xs text-slate-500 p-1">No urgent cases outstanding.</p>
//               ) : (
//                 <table className="text-left text-xs border-collapse table-fixed w-max min-w-full">
//                   <thead className="sticky top-0 bg-slate-900 text-slate-400 font-bold uppercase text-[9px] border-b border-slate-800 z-10">
//                     <tr>
//                       <th style={{ width: urgentWidths.tradeId }} className="p-1 relative group">
//                         Trade ID
//                         <div onMouseDown={(e) => handleMouseDown('urgent', 'tradeId', e)} onDoubleClick={() => handleDoubleClick('urgent')} className="absolute right-0 top-0 bottom-0 w-1 bg-slate-700/0 group-hover:bg-purple-500/50 cursor-col-resize transition-colors" />
//                       </th>
//                       <th style={{ width: urgentWidths.risk }} className="p-1 text-right relative group">
//                         Risk Score
//                         <div onMouseDown={(e) => handleMouseDown('urgent', 'risk', e)} onDoubleClick={() => handleDoubleClick('urgent')} className="absolute right-0 top-0 bottom-0 w-1 bg-slate-700/0 group-hover:bg-purple-500/50 cursor-col-resize transition-colors" />
//                       </th>
//                       <th style={{ width: urgentWidths.conf }} className="p-1 text-right relative group">
//                         Conf.
//                         <div onMouseDown={(e) => handleMouseDown('urgent', 'conf', e)} onDoubleClick={() => handleDoubleClick('urgent')} className="absolute right-0 top-0 bottom-0 w-1 bg-slate-700/0 group-hover:bg-purple-500/50 cursor-col-resize transition-colors" />
//                       </th>
//                       <th style={{ width: urgentWidths.reason }} className="p-1 pl-2 relative group">
//                         Flag Reason
//                         <div onMouseDown={(e) => handleMouseDown('urgent', 'reason', e)} onDoubleClick={() => handleDoubleClick('urgent')} className="absolute right-0 top-0 bottom-0 w-1 bg-slate-700/0 group-hover:bg-purple-500/50 cursor-col-resize transition-colors" />
//                       </th>
//                     </tr>
//                   </thead>
//                   <tbody className="divide-y divide-slate-800/30">
//                     {urgentCases.map((c, idx) => {
//                       const isSelected = selectedCase?.trade_id === c?.trade_id;
//                       const riskVal = 1 - (Number(c?.compliance_probability) ?? 1.0);
//                       return (
//                         <tr
//                           key={`${c?.trade_id}-${idx}`}
//                           onClick={() => handleCaseSelection(c)}
//                           className={`cursor-pointer text-[11px] transition-colors ${isSelected ? 'bg-rose-950/30 font-semibold border-l-2 border-rose-500 text-rose-200' : 'hover:bg-slate-800/30 text-slate-300'}`}
//                         >
//                           <td className="p-1 font-mono truncate">{c?.trade_id}</td>
//                           <td className="p-1 text-right font-mono text-rose-400/90">{riskVal.toFixed(2)}</td>
//                           <td className="p-1 text-right font-mono text-slate-400">{(Number(c?.confidence_score) || 0).toFixed(2)}</td>
//                           <td className="p-1 pl-2 truncate text-[10px]">{c?.flag_reason}</td>
//                         </tr>
//                       );
//                     })}
//                   </tbody>
//                 </table>
//               )}
//             </div>
//           </div>

//           {/* REVIEW TRACK PANEL (Renamed layout matching requirements) */}
//           <div className="bg-slate-900 border border-slate-800/80 rounded-md p-1.5 flex flex-col min-h-0">
//             <div className="flex items-center gap-1 border-b border-slate-800 pb-0.5 mb-1">
//               <Clock className="w-3.5 h-3.5 text-amber-400" />
//               <h2 className="text-[10px] font-bold text-amber-400 uppercase tracking-wider">Review</h2>
//             </div>
            
//             <div className="flex-1 overflow-auto min-h-0 relative border border-slate-800/30 rounded dynamic-scroll">
//               {queuedCases.length === 0 ? (
//                 <p className="text-xs text-slate-500 p-1">Review queue empty.</p>
//               ) : (
//                 <table className="text-left text-xs border-collapse table-fixed w-max min-w-full">
//                   <thead className="sticky top-0 bg-slate-900 text-slate-400 font-bold uppercase text-[9px] border-b border-slate-800 z-10">
//                     <tr>
//                       <th style={{ width: queuedWidths.tradeId }} className="p-1 relative group">
//                         Trade ID
//                         <div onMouseDown={(e) => handleMouseDown('queued', 'tradeId', e)} onDoubleClick={() => handleDoubleClick('queued')} className="absolute right-0 top-0 bottom-0 w-1 bg-slate-700/0 group-hover:bg-purple-500/50 cursor-col-resize transition-colors" />
//                       </th>
//                       <th style={{ width: queuedWidths.priority }} className="p-1 text-right relative group text-amber-400">
//                         Priority
//                         <div onMouseDown={(e) => handleMouseDown('queued', 'priority', e)} onDoubleClick={() => handleDoubleClick('queued')} className="absolute right-0 top-0 bottom-0 w-1 bg-slate-700/0 group-hover:bg-purple-500/50 cursor-col-resize transition-colors" />
//                       </th>
//                       <th style={{ width: queuedWidths.risk }} className="p-1 text-right relative group">
//                         Risk Score
//                         <div onMouseDown={(e) => handleMouseDown('queued', 'risk', e)} onDoubleClick={() => handleDoubleClick('queued')} className="absolute right-0 top-0 bottom-0 w-1 bg-slate-700/0 group-hover:bg-purple-500/50 cursor-col-resize transition-colors" />
//                       </th>
//                       <th style={{ width: queuedWidths.conf }} className="p-1 text-right relative group">
//                         Conf.
//                         <div onMouseDown={(e) => handleMouseDown('queued', 'conf', e)} onDoubleClick={() => handleDoubleClick('queued')} className="absolute right-0 top-0 bottom-0 w-1 bg-slate-700/0 group-hover:bg-purple-500/50 cursor-col-resize transition-colors" />
//                       </th>
//                       <th style={{ width: queuedWidths.reason }} className="p-1 pl-2 relative group">
//                         Flag Reason
//                         <div onMouseDown={(e) => handleMouseDown('queued', 'reason', e)} onDoubleClick={() => handleDoubleClick('queued')} className="absolute right-0 top-0 bottom-0 w-1 bg-slate-700/0 group-hover:bg-purple-500/50 cursor-col-resize transition-colors" />
//                       </th>
//                     </tr>
//                   </thead>
//                   <tbody className="divide-y divide-slate-800/30">
//                     {queuedCases.map((c, idx) => {
//                       const isSelected = selectedCase?.trade_id === c?.trade_id;
//                       const riskVal = 1 - (Number(c?.compliance_probability) ?? 1.0);
//                       return (
//                         <tr
//                           key={`${c?.trade_id}-${idx}`}
//                           onClick={() => handleCaseSelection(c)}
//                           className={`cursor-pointer text-[11px] transition-colors ${isSelected ? 'bg-purple-950/30 font-semibold border-l-2 border-purple-500 text-purple-200' : 'hover:bg-slate-800/30 text-slate-300'}`}
//                         >
//                           <td className="p-1 font-mono truncate">{c?.trade_id}</td>
//                           <td className="p-1 text-right font-mono font-bold text-amber-400">{c?.priority_score ?? "0"}</td>
//                           <td className="p-1 text-right font-mono text-rose-400/90">{riskVal.toFixed(2)}</td>
//                           <td className="p-1 text-right font-mono text-slate-400">{(Number(c?.confidence_score) || 0).toFixed(2)}</td>
//                           <td className="p-1 pl-2 truncate text-[10px]">{c?.flag_reason}</td>
//                         </tr>
//                       );
//                     })}
//                   </tbody>
//                 </table>
//               )}
//             </div>
//           </div>

//         </div>

//         {/* LOWER VIEW: High Density Selected Case Audit Panel (~52% Window Expansion) */}
//         <div className="bg-slate-900 border border-slate-800 rounded-lg p-2 flex flex-col min-h-0 shadow-xl">
//           {selectedCase ? (
//             (() => {
//               const currentState = caseStates[selectedCase.trade_id] || { reviewStatus: "Not reviewed", notes: "" };
//               const isReviewed = currentState.reviewStatus === "Reviewed";
              
//               return (
//                 <div className="flex flex-col h-full gap-2 min-h-0">
                  
//                   {/* Row 1: Primary Control Header */}
//                   <div className="flex items-center justify-between border-b border-slate-800 pb-1">
//                     <div className="flex items-center gap-2">
//                       <span className="text-[10px] font-black uppercase tracking-wider text-purple-400 bg-purple-950/40 px-1.5 py-0.5 rounded border border-purple-800/30">
//                         Selected Case Audit
//                       </span>
//                       <h2 className="text-sm font-mono font-black text-slate-100">{selectedCase.trade_id}</h2>
                      
//                       {/* Interactive Review Status Indicator */}
//                       <span className={`ml-2 px-1.5 py-0.5 rounded text-[10px] font-bold tracking-wide border ${
//                         isReviewed 
//                           ? "bg-emerald-950/50 text-emerald-400 border-emerald-500/30" 
//                           : "bg-slate-950 text-amber-400 border-amber-500/20"
//                       }`}>
//                         STATUS: {currentState.reviewStatus}
//                       </span>
//                     </div>
                    
//                     <div className="flex items-center gap-2">
//                       {selectedCase.escalation_level === "urgent" ? (
//                         <span className="px-1.5 py-0.5 bg-rose-500 text-slate-950 text-[10px] font-black rounded uppercase">Urgent Intervene</span>
//                       ) : (
//                         <span className="px-1.5 py-0.5 bg-amber-500 text-slate-950 text-[10px] font-black rounded uppercase">Review ({selectedCase.escalation_level})</span>
//                       )}
//                     </div>
//                   </div>

//                   {/* Row 2: Secondary Metadata Grid Matrix */}
//                   <div className="grid grid-cols-3 gap-1.5">
//                     <div className="bg-slate-950/60 border border-slate-800/60 px-2 py-1 rounded flex justify-between items-center">
//                       <span className="text-slate-500 font-bold text-[10px] uppercase">Risk Score:</span>
//                       <span className="text-xs font-black text-rose-400 font-mono">{(1 - (Number(selectedCase.compliance_probability) || 0)).toFixed(4)}</span>
//                     </div>
//                     <div className="bg-slate-950/60 border border-slate-800/60 px-2 py-1 rounded flex justify-between items-center">
//                       <span className="text-slate-500 font-bold text-[10px] uppercase">Model Conf:</span>
//                       <span className="text-xs font-black text-sky-400 font-mono">{(Number(selectedCase.confidence_score) || 0).toFixed(4)}</span>
//                     </div>
//                     <div className="bg-slate-950/60 border border-slate-800/60 px-2 py-1 rounded flex justify-between items-center">
//                       <span className="text-slate-500 font-bold text-[10px] uppercase">Priority Weight:</span>
//                       <span className="text-xs font-black text-amber-400 font-mono">{selectedCase.priority_score ?? "N/A"}</span>
//                     </div>
//                   </div>

//                   {/* Row 3: Extended Trade Properties Framework Split (Scroll-free mapping) */}
//                   <div className="grid grid-cols-4 gap-1.5 flex-1 min-h-0">
                    
//                     {/* Block A: Core Trade Fields */}
//                     <div className="bg-slate-950/30 border border-slate-800/40 p-1.5 rounded flex flex-col min-h-0">
//                       <h4 className="text-[9px] font-bold text-purple-400/90 uppercase tracking-wider border-b border-slate-800 pb-0.5 mb-1">Trade Fields</h4>
//                       <div className="text-[11px] space-y-1 overflow-y-auto dynamic-scroll pr-0.5 text-slate-300">
//                         <div><span className="text-slate-500 font-mono">Asset:</span> {selectedCase.asset_class || selectedCase.asset_id || "Equity"}</div>
//                         <div><span className="text-slate-500 font-mono">Size:</span> {selectedCase.trade_size || selectedCase.volume || "N/A"}</div>
//                         <div><span className="text-slate-500 font-mono">Value:</span> ${selectedCase.notional_value?.toLocaleString() || "0.00"}</div>
//                         <div><span className="text-slate-500 font-mono">Timestamp:</span> <span className="text-[10px] font-mono">{selectedCase.timestamp || "N/A"}</span></div>
//                       </div>
//                     </div>

//                     {/* Block B: Client Profile Metadata */}
//                     <div className="bg-slate-950/30 border border-slate-800/40 p-1.5 rounded flex flex-col min-h-0">
//                       <h4 className="text-[9px] font-bold text-purple-400/90 uppercase tracking-wider border-b border-slate-800 pb-0.5 mb-1">Client Profile</h4>
//                       <div className="text-[11px] space-y-1 overflow-y-auto dynamic-scroll pr-0.5 text-slate-300">
//                         <div><span className="text-slate-500 font-mono">ID:</span> <span className="font-mono">{selectedCase.client_id || "N/A"}</span></div>
//                         <div><span className="text-slate-500 font-mono">Risk Profile:</span> {selectedCase.client_risk_tolerance || "Growth/Aggressive"}</div>
//                         <div><span className="text-slate-500 font-mono">Jurisdiction:</span> {selectedCase.client_jurisdiction || "Ontario, CA"}</div>
//                         <div><span className="text-slate-500 font-mono">KYC Status:</span> <span className="text-emerald-400 text-[10px] font-bold">Verified</span></div>
//                       </div>
//                     </div>

//                     {/* Block C: Core Advisor Context Records */}
//                     <div className="bg-slate-950/30 border border-slate-800/40 p-1.5 rounded flex flex-col min-h-0">
//                       <h4 className="text-[9px] font-bold text-purple-400/90 uppercase tracking-wider border-b border-slate-800 pb-0.5 mb-1">Advisor Notes</h4>
//                       <div className="text-[11px] text-slate-300 overflow-y-auto dynamic-scroll pr-0.5 leading-tight">
//                         {selectedCase.advisor_notes || selectedCase.submission_context || "No standard override notes filed by submitting Desk Advisor during transaction assembly."}
//                       </div>
//                     </div>

//                     {/* Block D: Exception Reason Details */}
//                     <div className="bg-slate-950/30 border border-slate-800/40 p-1.5 rounded flex flex-col min-h-0">
//                       <h4 className="text-[9px] font-bold text-purple-400/90 uppercase tracking-wider border-b border-slate-800 pb-0.5 mb-1">Exception Breakdown</h4>
//                       <div className="text-[11px] text-slate-300 overflow-y-auto dynamic-scroll pr-0.5 leading-tight">
//                         {selectedCase.flag_reason || "No structural audit rules triggered."}
//                       </div>
//                     </div>

//                   </div>

//                   {/* Row 4: Policy Tokens Mapping */}
//                   <div className="pt-0.5">
//                     <h3 className="text-[9px] font-black text-slate-500 uppercase tracking-widest mb-0.5">Retrieved Regulatory Policies</h3>
//                     <div className="flex flex-wrap gap-1">
//                       {renderPolicies(selectedCase.retrieved_policies)}
//                     </div>
//                   </div>

//                   {/* Row 5: Action Processing Desk (Persistent logging layout) */}
//                   <div className="border-t border-slate-800 pt-1.5 mt-0.5 flex gap-2 items-end">
//                     <div className="flex-1 flex flex-col">
//                       <label className="text-[9px] font-black text-slate-400 uppercase tracking-widest mb-0.5">
//                         Reviewer Sign-off Notes
//                       </label>
//                       <input
//                         type="text"
//                         value={currentNotes}
//                         disabled={isReviewed}
//                         onChange={(e) => handleNotesChange(e.target.value)}
//                         placeholder={isReviewed ? "Audit finalized. Logs locked." : "Input justification, regulatory code alignment, or compliance overrides details..."}
//                         className="w-full bg-slate-950 border border-slate-800 rounded px-2 py-1 text-xs text-slate-200 focus:outline-none focus:border-purple-500/80 disabled:opacity-50 transition-colors placeholder:text-slate-600"
//                       />
//                     </div>
                    
//                     <div className="flex gap-1.5">
//                       <button
//                         onClick={commitAuditStatus}
//                         disabled={isReviewed}
//                         className="bg-emerald-600 hover:bg-emerald-500 disabled:bg-slate-800 disabled:text-slate-500 text-slate-950 font-black text-xs px-3 py-1 rounded transition-colors uppercase tracking-wider"
//                       >
//                         Approve
//                       </button>
//                       <button
//                         onClick={commitAuditStatus}
//                         disabled={isReviewed}
//                         className="bg-purple-600 hover:bg-purple-500 disabled:bg-slate-800 disabled:text-slate-500 text-slate-100 font-black text-xs px-3 py-1 rounded transition-colors uppercase tracking-wider"
//                       >
//                         Override
//                       </button>
//                     </div>
//                   </div>

//                 </div>
//               );
//             })()
//           ) : (
//             <div className="h-full flex items-center justify-center text-slate-500 text-xs font-semibold border border-dashed border-slate-800 rounded">
//               Select an entry from the tracking tables above to open the compliance audit workspace.
//             </div>
//           )}
//         </div>

//       </div>
//     </div>
//   );
// }

// export default Dashboard;

// /* VERSION 4 */
// import { useEffect, useState, useRef } from "react";
// import { getCases } from "../api/cases";
// import { AlertCircle, CheckCircle, Clock, ShieldAlert } from "lucide-react";

// function Dashboard() {
//   const [cases, setCases] = useState<any[]>([]);
//   const [selectedCase, setSelectedCase] = useState<any | null>(null);

//   // --- Spreadsheet Column Resize State ---
//   const [urgentWidths, setUrgentWidths] = useState({ tradeId: 100, nonComp: 75, conf: 75, reason: 220 });
//   const [queuedWidths, setQueuedWidths] = useState({ tradeId: 100, priority: 70, nonComp: 75, conf: 75, reason: 200 });

//   const dragInfo = useRef<{ table: 'urgent' | 'queued'; col: string; startX: number; startWidth: number } | null>(null);

//   useEffect(() => {
//     getCases()
//       .then((data) => {
//         if (Array.isArray(data)) {
//           setCases(data);
//           const urgentCases = data.filter((c) => c?.escalation_level === "urgent");
//           const queuedCases = data
//             .filter((c) => c?.escalation_level === "priority" || c?.escalation_level === "queue")
//             .sort((a, b) => (Number(b?.priority_score) || 0) - (Number(a?.priority_score) || 0));

//           if (urgentCases.length > 0) setSelectedCase(urgentCases[0]);
//           else if (queuedCases.length > 0) setSelectedCase(queuedCases[0]);
//         }
//       })
//       .catch((err) => console.error("API Fetch Error:", err));
//   }, []);

//   // --- Mouse Resize Handlers ---
//   const handleMouseDown = (table: 'urgent' | 'queued', col: string, e: React.MouseEvent) => {
//     e.preventDefault();
//     const currentWidths = table === 'urgent' ? urgentWidths : queuedWidths;
//     dragInfo.current = {
//       table,
//       col,
//       startX: e.clientX,
//       startWidth: (currentWidths as any)[col]
//     };
//     document.addEventListener("mousemove", handleMouseMove);
//     document.addEventListener("mouseup", handleMouseUp);
//   };

//   const handleMouseMove = (e: MouseEvent) => {
//     if (!dragInfo.current) return;
//     const { table, col, startX, startWidth } = dragInfo.current;
//     const deltaX = e.clientX - startX;
//     const newWidth = Math.max(50, startWidth + deltaX);

//     if (table === 'urgent') {
//       setUrgentWidths(prev => ({ ...prev, [col]: newWidth }));
//     } else {
//       setQueuedWidths(prev => ({ ...prev, [col]: newWidth }));
//     }
//   };

//   const handleMouseUp = () => {
//     dragInfo.current = null;
//     document.removeEventListener("mousemove", handleMouseMove);
//     document.removeEventListener("mouseup", handleMouseUp);
//   };

//   const handleDoubleClick = (table: 'urgent' | 'queued') => {
//     if (table === 'urgent') {
//       setUrgentWidths({ tradeId: 100, nonComp: 75, conf: 75, reason: 220 });
//     } else {
//       setQueuedWidths({ tradeId: 100, priority: 70, nonComp: 75, conf: 75, reason: 200 });
//     }
//   };

//   // Data Splitters & Sorters
//   const urgentCases = cases.filter((c) => c?.escalation_level === "urgent");
//   const queuedCases = cases
//     .filter((c) => c?.escalation_level === "priority" || c?.escalation_level === "queue")
//     .sort((a, b) => (Number(b?.priority_score) || 0) - (Number(a?.priority_score) || 0));

//   const countUrgent = urgentCases.length;
//   const countReview = queuedCases.length; // Renamed counter
//   const countPassed = cases.filter(
//     (c) => c?.escalation_level !== "urgent" && c?.escalation_level !== "priority" && c?.escalation_level !== "queue"
//   ).length;

//   const renderPolicies = (policies: any) => {
//     if (!policies) return <span className="text-xs text-slate-500">No policies attached.</span>;
//     let items: string[] = [];
//     if (Array.isArray(policies)) items = policies;
//     else if (typeof policies === "string" && policies.startsWith("[")) {
//       items = policies.replace(/[\[\]']/g, "").split(",").map((p) => p.trim()).filter(Boolean);
//     } else if (typeof policies === "string" && policies.trim().length > 0) {
//       items = policies.split(",").map((p) => p.trim());
//     }
    
//     if (items.length === 0) return <span className="text-xs text-slate-500">No policies attached.</span>;
//     return items.map((policy, i) => (
//       <span key={i} className="px-2 py-1 bg-slate-950 text-xs rounded border border-slate-700 text-purple-300 font-mono font-semibold">
//         {policy}
//       </span>
//     ));
//   };

//   return (
//     <div className="p-2 h-screen bg-slate-950 text-slate-100 flex flex-col gap-1.5 overflow-hidden select-none">
      
//       {/* Injecting CSS targeting dynamic scrollbar display on hover */}
//       <style>{`
//         .dynamic-scroll {
//           scrollbar-width: none; /* Hide standard Firefox scrollbar */
//         }
//         .dynamic-scroll::-webkit-scrollbar {
//           width: 5px;
//           height: 5px;
//           display: none; /* Hide standard Webkit scrollbar */
//         }
//         .dynamic-scroll:hover {
//           scrollbar-width: thin; /* Restore Firefox on hover */
//         }
//         .dynamic-scroll:hover::-webkit-scrollbar {
//           display: block; /* Restore Webkit on hover */
//         }
//         .dynamic-scroll::-webkit-scrollbar-track {
//           background: rgba(15, 23, 42, 0.3);
//         }
//         .dynamic-scroll::-webkit-scrollbar-thumb {
//           background: rgba(148, 163, 184, 0.2);
//           border-radius: 4px;
//         }
//         .dynamic-scroll::-webkit-scrollbar-thumb:hover {
//           background: rgba(148, 163, 184, 0.5);
//         }
//       `}</style>
      
//       {/* --- Unified Header --- */}
//       <div className="flex items-center justify-between border-b border-slate-800 pb-1.5">
//         <h1 className="text-lg font-bold tracking-tight text-slate-100">
//           AI Compliance Review Copilot
//         </h1>
        
//         {/* Top-Right Metrics Panel */}
//         <div className="flex items-center gap-3">
//           <div className="bg-rose-950/30 border-2 border-rose-500/40 rounded-md px-3 py-1 flex items-center gap-2 text-sm font-semibold shadow-sm">
//             <AlertCircle className="w-4 h-4 text-rose-400 animate-pulse" />
//             <span className="text-rose-300">Urgent:</span>
//             <span className="text-base font-black text-rose-100">{countUrgent}</span>
//           </div>

//           {/* Renamed to Review */}
//           <div className="bg-amber-950/30 border-2 border-amber-500/40 rounded-md px-3 py-1 flex items-center gap-2 text-sm font-semibold shadow-sm">
//             <Clock className="w-4 h-4 text-amber-400" />
//             <span className="text-amber-300">Review:</span>
//             <span className="text-base font-black text-amber-100">{countReview}</span>
//           </div>

//           <div className="bg-emerald-950/30 border-2 border-emerald-500/40 rounded-md px-3 py-1 flex items-center gap-2 text-sm font-semibold shadow-sm">
//             <CheckCircle className="w-4 h-4 text-emerald-400" />
//             <span className="text-emerald-300">Passed:</span>
//             <span className="text-base font-black text-emerald-100">{countPassed}</span>
//           </div>
//         </div>
//       </div>

//       {/* --- Main Viewport Stack Split --- */}
//       <div className="flex-1 grid grid-rows-[52fr_48fr] gap-1.5 min-h-0">
        
//         {/* UPPER PORTION: Side-by-Side Lists */}
//         <div className="grid grid-cols-2 gap-1.5 min-h-0">
          
//           {/* LEFT PANEL: Urgent Action Required */}
//           <div className="bg-slate-900 border border-rose-500/20 rounded-lg p-2 flex flex-col min-h-0">
//             <div className="flex items-center gap-1.5 border-b border-slate-800 pb-1 mb-1">
//               <ShieldAlert className="w-4 h-4 text-rose-400" />
//               <h2 className="text-xs font-bold text-rose-400 uppercase tracking-wider">Urgent Action Required</h2>
//             </div>
            
//             <div className="flex-1 overflow-auto min-h-0 relative border border-slate-800/40 rounded dynamic-scroll">
//               {urgentCases.length === 0 ? (
//                 <p className="text-xs text-slate-500 p-2">No urgent cases outstanding.</p>
//               ) : (
//                 <table className="text-left text-xs border-collapse table-fixed w-max min-w-full">
//                   <thead className="sticky top-0 bg-slate-900 text-slate-400 font-bold uppercase text-[10px] border-b border-slate-800 z-10">
//                     <tr>
//                       <th style={{ width: urgentWidths.tradeId }} className="p-1.5 relative group">
//                         Trade ID
//                         <div onMouseDown={(e) => handleMouseDown('urgent', 'tradeId', e)} onDoubleClick={() => handleDoubleClick('urgent')} className="absolute right-0 top-0 bottom-0 w-1 bg-slate-700/0 group-hover:bg-purple-500/50 cursor-col-resize transition-colors" />
//                       </th>
//                       <th style={{ width: urgentWidths.nonComp }} className="p-1.5 text-right relative group">
//                         Non-Comp.
//                         <div onMouseDown={(e) => handleMouseDown('urgent', 'nonComp', e)} onDoubleClick={() => handleDoubleClick('urgent')} className="absolute right-0 top-0 bottom-0 w-1 bg-slate-700/0 group-hover:bg-purple-500/50 cursor-col-resize transition-colors" />
//                       </th>
//                       <th style={{ width: urgentWidths.conf }} className="p-1.5 text-right relative group">
//                         Conf.
//                         <div onMouseDown={(e) => handleMouseDown('urgent', 'conf', e)} onDoubleClick={() => handleDoubleClick('urgent')} className="absolute right-0 top-0 bottom-0 w-1 bg-slate-700/0 group-hover:bg-purple-500/50 cursor-col-resize transition-colors" />
//                       </th>
//                       <th style={{ width: urgentWidths.reason }} className="p-1.5 pl-3 relative group">
//                         Flag Reason
//                         <div onMouseDown={(e) => handleMouseDown('urgent', 'reason', e)} onDoubleClick={() => handleDoubleClick('urgent')} className="absolute right-0 top-0 bottom-0 w-1 bg-slate-700/0 group-hover:bg-purple-500/50 cursor-col-resize transition-colors" />
//                       </th>
//                     </tr>
//                   </thead>
//                   <tbody className="divide-y divide-slate-800/40">
//                     {urgentCases.map((c, idx) => {
//                       const compProb = c?.compliance_probability !== undefined ? Number(c.compliance_probability) : 1.0;
//                       return (
//                         <tr
//                           key={`${c?.trade_id}-${idx}`}
//                           onClick={() => setSelectedCase(c)}
//                           className={`cursor-pointer text-[11px] transition-colors hover:bg-rose-950/10 ${selectedCase?.trade_id === c?.trade_id ? 'bg-rose-950/20 border-l-2 border-rose-500' : ''}`}
//                         >
//                           <td className="p-1.5 font-mono font-bold text-rose-300 truncate">{c?.trade_id}</td>
//                           <td className="p-1.5 text-right text-rose-400 font-mono">{(1 - compProb).toFixed(2)}</td>
//                           <td className="p-1.5 text-right text-slate-400 font-mono">{(Number(c?.confidence_score) || 0).toFixed(2)}</td>
//                           <td className="p-1.5 pl-3 truncate text-slate-300 text-[10px]">{c?.flag_reason}</td>
//                         </tr>
//                       );
//                     })}
//                   </tbody>
//                 </table>
//               )}
//             </div>
//           </div>

//           {/* RIGHT PANEL: Review (Renamed from Queued) */}
//           <div className="bg-slate-900 border border-slate-800 rounded-lg p-2 flex flex-col min-h-0">
//             <div className="flex items-center gap-1.5 border-b border-slate-800 pb-1 mb-1">
//               <Clock className="w-4 h-4 text-amber-400" />
//               {/* Header Label Renamed */}
//               <h2 className="text-xs font-bold text-amber-400 uppercase tracking-wider">Review</h2>
//             </div>
            
//             <div className="flex-1 overflow-auto min-h-0 relative border border-slate-800/40 rounded dynamic-scroll">
//               {queuedCases.length === 0 ? (
//                 <p className="text-xs text-slate-500 p-2">Review queue is empty.</p>
//               ) : (
//                 <table className="text-left text-xs border-collapse table-fixed w-max min-w-full">
//                   <thead className="sticky top-0 bg-slate-900 text-slate-400 font-bold uppercase text-[10px] border-b border-slate-800 z-10">
//                     <tr>
//                       <th style={{ width: queuedWidths.tradeId }} className="p-1.5 relative group">
//                         Trade ID
//                         <div onMouseDown={(e) => handleMouseDown('queued', 'tradeId', e)} onDoubleClick={() => handleDoubleClick('queued')} className="absolute right-0 top-0 bottom-0 w-1 bg-slate-700/0 group-hover:bg-purple-500/50 cursor-col-resize transition-colors" />
//                       </th>
//                       <th style={{ width: queuedWidths.priority }} className="p-1.5 text-right relative group text-amber-400">
//                         Priority
//                         <div onMouseDown={(e) => handleMouseDown('queued', 'priority', e)} onDoubleClick={() => handleDoubleClick('queued')} className="absolute right-0 top-0 bottom-0 w-1 bg-slate-700/0 group-hover:bg-purple-500/50 cursor-col-resize transition-colors" />
//                       </th>
//                       <th style={{ width: queuedWidths.nonComp }} className="p-1.5 text-right relative group">
//                         Non-Comp.
//                         <div onMouseDown={(e) => handleMouseDown('queued', 'nonComp', e)} onDoubleClick={() => handleDoubleClick('queued')} className="absolute right-0 top-0 bottom-0 w-1 bg-slate-700/0 group-hover:bg-purple-500/50 cursor-col-resize transition-colors" />
//                       </th>
//                       <th style={{ width: queuedWidths.conf }} className="p-1.5 text-right relative group">
//                         Conf.
//                         <div onMouseDown={(e) => handleMouseDown('queued', 'conf', e)} onDoubleClick={() => handleDoubleClick('queued')} className="absolute right-0 top-0 bottom-0 w-1 bg-slate-700/0 group-hover:bg-purple-500/50 cursor-col-resize transition-colors" />
//                       </th>
//                       <th style={{ width: queuedWidths.reason }} className="p-1.5 pl-3 relative group">
//                         Flag Reason
//                         <div onMouseDown={(e) => handleMouseDown('queued', 'reason', e)} onDoubleClick={() => handleDoubleClick('queued')} className="absolute right-0 top-0 bottom-0 w-1 bg-slate-700/0 group-hover:bg-purple-500/50 cursor-col-resize transition-colors" />
//                       </th>
//                     </tr>
//                   </thead>
//                   <tbody className="divide-y divide-slate-800/40">
//                     {queuedCases.map((c, idx) => {
//                       const compProb = c?.compliance_probability !== undefined ? Number(c.compliance_probability) : 1.0;
//                       return (
//                         <tr
//                           key={`${c?.trade_id}-${idx}`}
//                           onClick={() => setSelectedCase(c)}
//                           className={`cursor-pointer text-[11px] transition-colors hover:bg-slate-800/40 ${selectedCase?.trade_id === c?.trade_id ? 'bg-purple-950/20 border-l-2 border-purple-500' : ''}`}
//                         >
//                           <td className="p-1.5 font-mono font-bold text-slate-200 truncate">{c?.trade_id}</td>
//                           <td className="p-1.5 text-right font-bold text-amber-400 font-mono">{c?.priority_score ?? "0"}</td>
//                           <td className="p-1.5 text-right text-rose-400 font-mono">{(1 - compProb).toFixed(2)}</td>
//                           <td className="p-1.5 text-right text-slate-400 font-mono">{(Number(c?.confidence_score) || 0).toFixed(2)}</td>
//                           <td className="p-1.5 pl-3 truncate text-slate-400 text-[10px]">{c?.flag_reason}</td>
//                         </tr>
//                       );
//                     })}
//                   </tbody>
//                 </table>
//               )}
//             </div>
//           </div>

//         </div>

//         {/* LOWER PORTION: Selected Case Audit Panel */}
//         <div className="bg-slate-900 border border-slate-800 rounded-lg p-3 flex flex-col min-h-0 shadow-lg">
//           {selectedCase ? (
//             <div className="flex flex-col h-full gap-2">
              
//               <div className="flex items-center justify-between border-b border-slate-800 pb-1.5">
//                 <div className="flex items-center gap-3">
//                   <span className="text-xs font-black uppercase tracking-widest text-purple-400 bg-purple-950/40 px-2 py-0.5 rounded border border-purple-800/30">
//                     Selected Case Audit
//                   </span>
//                   <h2 className="text-base font-mono font-extrabold text-slate-50 tracking-wide">{selectedCase.trade_id}</h2>
//                 </div>
//                 <div>
//                   {selectedCase.escalation_level === "urgent" ? (
//                     <span className="px-2 py-0.5 bg-rose-500 text-slate-950 text-xs font-black rounded uppercase tracking-wider shadow">Urgent Intervene</span>
//                   ) : (
//                     /* Badge Label Renamed from Queue to Review */
//                     <span className="px-2 py-0.5 bg-amber-500 text-slate-950 text-xs font-black rounded uppercase tracking-wider shadow">Review ({selectedCase.escalation_level})</span>
//                   )}
//                 </div>
//               </div>

//               {/* Data Blocks */}
//               <div className="grid grid-cols-3 gap-2">
//                 <div className="bg-slate-950 border border-slate-800/80 px-3 py-1.5 rounded-md flex justify-between items-center">
//                   <span className="text-slate-400 font-bold text-xs uppercase tracking-wide">Compliance Probability:</span>
//                   <span className="text-sm font-black text-emerald-400 font-mono">{(Number(selectedCase.compliance_probability) || 0).toFixed(4)}</span>
//                 </div>
//                 <div className="bg-slate-950 border border-slate-800/80 px-3 py-1.5 rounded-md flex justify-between items-center">
//                   <span className="text-slate-400 font-bold text-xs uppercase tracking-wide">Model Confidence:</span>
//                   <span className="text-sm font-black text-sky-400 font-mono">{(Number(selectedCase.confidence_score) || 0).toFixed(4)}</span>
//                 </div>
//                 <div className="bg-slate-950 border border-slate-800/80 px-3 py-1.5 rounded-md flex justify-between items-center">
//                   <span className="text-slate-400 font-bold text-xs uppercase tracking-wide">Priority Score:</span>
//                   <span className="text-sm font-black text-amber-400 font-mono">{selectedCase.priority_score ?? "N/A"}</span>
//                 </div>
//               </div>

//               {/* Breakdown Text Box */}
//               <div className="flex-1 flex flex-col min-h-0">
//                 <h3 className="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-1">Reasoning Summary</h3>
//                 <div className="flex-1 p-2 bg-slate-950 rounded border border-slate-800/80 text-xs font-medium text-slate-200 leading-relaxed overflow-y-auto custom-scrollbar">
//                   {selectedCase.flag_reason || "No structural audit rules violated."}
//                 </div>
//               </div>

//               {/* Rule Tags Row */}
//               <div className="pt-0.5">
//                 <h3 className="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-1">Retrieved Regulatory Policies</h3>
//                 <div className="flex flex-wrap gap-1.5">
//                   {renderPolicies(selectedCase.retrieved_policies)}
//                 </div>
//               </div>

//             </div>
//           ) : (
//             <div className="h-full flex items-center justify-center text-slate-400 text-sm font-semibold border border-dashed border-slate-800 rounded">
//               Select an entry from the tracking tables above to open the compliance audit workspace.
//             </div>
//           )}
//         </div>

//       </div>
//     </div>
//   );
// }

// export default Dashboard;

/* VERSION 3 */

// import { useEffect, useState } from "react";
// import { getCases } from "../api/cases";
// import { AlertCircle, CheckCircle, Clock, XCircle, ShieldAlert } from "lucide-react";

// function Dashboard() {
//   const [cases, setCases] = useState<any[]>([]);
//   const [selectedCase, setSelectedCase] = useState<any | null>(null);

//   useEffect(() => {
//     getCases()
//       .then((data) => {
//         if (Array.isArray(data)) {
//           setCases(data);
//           // Auto-select the first urgent case if it exists, otherwise the first queued one
//           const urgentCases = data.filter((c) => c?.escalation_level === "urgent");
//           const queuedCases = data
//             .filter((c) => c?.escalation_level === "priority" || c?.escalation_level === "queue")
//             .sort((a, b) => (Number(b?.priority_score) || 0) - (Number(a?.priority_score) || 0));

//           if (urgentCases.length > 0) {
//             setSelectedCase(urgentCases[0]);
//           } else if (queuedCases.length > 0) {
//             setSelectedCase(queuedCases[0]);
//           }
//         }
//       })
//       .catch((err) => console.error("API Fetch Error:", err));
//   }, []);

//   // --- Data Splitters & Sorters ---
  
//   // 1. Urgent Cases (Kept in natural data order, no priority column needed)
//   const urgentCases = cases.filter((c) => c?.escalation_level === "urgent");

//   // 2. Queued Cases (Priority or Queue escalation, sorted descending by priority score)
//   const queuedCases = cases
//     .filter((c) => c?.escalation_level === "priority" || c?.escalation_level === "queue")
//     .sort((a, b) => (Number(b?.priority_score) || 0) - (Number(a?.priority_score) || 0));

//   // --- Metric Banner Calculations ---
//   const countUrgent = urgentCases.length;
//   const countQueued = queuedCases.length;
  
//   // A case is "Passed" (compliant) if it's in the data but not explicitly hitting compliance exceptions.
//   // If your data has an explicit "passed" state, update this logic accordingly!
//   const countPassed = cases.filter(
//     (c) => c?.escalation_level !== "urgent" && c?.escalation_level !== "priority" && c?.escalation_level !== "queue"
//   ).length;

//   // --- Policy String Parser Helper ---
//   const renderPolicies = (policies: any) => {
//     if (!policies) return <span className="text-xs text-slate-500">No policies attached.</span>;
//     if (Array.isArray(policies)) {
//       return policies.map((policy: string, i: number) => (
//         <span key={i} className="px-2 py-1 bg-slate-800 text-xs rounded border border-slate-700 text-slate-300 font-mono">
//           {policy}
//         </span>
//       ));
//     }
//     if (typeof policies === "string" && policies.startsWith("[")) {
//       return policies
//         .replace(/[\[\]']/g, "")
//         .split(",")
//         .map((p) => p.trim())
//         .filter(Boolean)
//         .map((policy: string, i: number) => (
//           <span key={i} className="px-2 py-1 bg-slate-800 text-xs rounded border border-slate-700 text-slate-300 font-mono">
//             {policy}
//           </span>
//         ));
//     }
//     if (typeof policies === "string" && policies.trim().length > 0) {
//       return policies.split(",").map((policy: string, i: number) => (
//         <span key={i} className="px-2 py-1 bg-slate-800 text-xs rounded border border-slate-700 text-slate-300 font-mono">
//           {policy.trim()}
//         </span>
//       ));
//     }
//     return <span className="text-xs text-slate-500">No policies attached.</span>;
//   };

//   return (
//     <div className="p-6 min-h-screen bg-slate-950 text-slate-100 flex flex-col gap-6">
      
//       {/* Title Header */}
//       <div>
//         <h1 className="text-3xl font-bold tracking-tight text-slate-100">
//           AI Compliance Review Copilot
//         </h1>
//         <p className="text-sm text-slate-400 mt-1">Human-in-the-Loop Agentic Compliance Portal</p>
//       </div>

//       {/* --- 1. Metrics Counter Banner --- */}
//       <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
//         <div className="bg-rose-950/20 border border-rose-500/30 rounded-xl p-4 flex items-center gap-4 shadow-sm">
//           <div className="p-3 bg-rose-500/10 rounded-lg text-rose-400">
//             <AlertCircle className="w-6 h-6 animate-pulse" />
//           </div>
//           <div>
//             <div className="text-xs font-semibold uppercase tracking-wider text-rose-400/80">Urgent Intervention</div>
//             <div className="text-2xl font-bold text-rose-200 mt-0.5">{countUrgent} <span className="text-sm font-normal text-rose-400/60">cases</span></div>
//           </div>
//         </div>

//         <div className="bg-amber-950/10 border border-amber-500/20 rounded-xl p-4 flex items-center gap-4 shadow-sm">
//           <div className="p-3 bg-amber-500/10 rounded-lg text-amber-400">
//             <Clock className="w-6 h-6" />
//           </div>
//           <div>
//             <div className="text-xs font-semibold uppercase tracking-wider text-amber-400/80">Queued for Review</div>
//             <div className="text-2xl font-bold text-amber-200 mt-0.5">{countQueued} <span className="text-sm font-normal text-amber-400/60">cases</span></div>
//           </div>
//         </div>

//         <div className="bg-emerald-950/10 border border-emerald-500/20 rounded-xl p-4 flex items-center gap-4 shadow-sm">
//           <div className="p-3 bg-emerald-500/10 rounded-lg text-emerald-400">
//             <CheckCircle className="w-6 h-6" />
//           </div>
//           <div>
//             <div className="text-xs font-semibold uppercase tracking-wider text-emerald-400/80">Compliant (Passed)</div>
//             <div className="text-2xl font-bold text-emerald-200 mt-0.5">{countPassed} <span className="text-sm font-normal text-emerald-400/60">cases</span></div>
//           </div>
//         </div>
//       </div>

//       {/* --- Main Vertical Layout Stack --- */}
//       <div className="flex flex-col gap-6">

//         {/* --- 2. URGENT CASES SECTION (At the top) --- */}
//         <div className="bg-slate-900 border border-rose-500/20 rounded-xl p-5 shadow-md">
//           <div className="flex items-center gap-2 border-b border-slate-800 pb-3 mb-4">
//             <ShieldAlert className="w-5 h-5 text-rose-400" />
//             <h2 className="text-lg font-bold text-rose-400">Urgent Action Required</h2>
//           </div>
          
//           {urgentCases.length === 0 ? (
//             <p className="text-sm text-slate-500 py-2">No urgent high-risk exemptions outstanding.</p>
//           ) : (
//             <div className="overflow-x-auto">
//               <table className="w-full text-left border-collapse">
//                 <thead>
//                   <tr className="border-b border-slate-800 text-slate-400 text-xs font-semibold uppercase">
//                     <th className="p-3">Trade ID</th>
//                     <th className="p-3 text-right">Non-Compliance Prob.</th>
//                     <th className="p-3 text-right">Confidence</th>
//                     <th className="p-3 pl-6">Flag Reason</th>
//                   </tr>
//                 </thead>
//                 <tbody className="divide-y divide-slate-800/50">
//                   {urgentCases.map((c, index) => {
//                     const compProb = c?.compliance_probability !== undefined && c?.compliance_probability !== null ? Number(c.compliance_probability) : 1.0;
//                     return (
//                       <tr
//                         key={`${c?.trade_id}-${index}`}
//                         onClick={() => setSelectedCase(c)}
//                         className={`text-sm cursor-pointer transition-colors hover:bg-rose-950/10 ${selectedCase?.trade_id === c?.trade_id ? 'bg-rose-950/20 border-l-2 border-rose-500' : ''}`}
//                       >
//                         <td className="p-3 font-mono font-bold text-rose-300">{c?.trade_id}</td>
//                         <td className="p-3 text-right font-medium text-rose-400">{(1 - compProb).toFixed(2)}</td>
//                         <td className="p-3 text-right text-slate-400">{c?.confidence_score !== undefined && c?.confidence_score !== null ? Number(c.confidence_score).toFixed(2) : "0.00"}</td>
//                         <td className="p-3 pl-6 truncate max-w-[400px] text-slate-300 text-xs">{c?.flag_reason || "Immediate agent intervention required."}</td>
//                       </tr>
//                     );
//                   })}
//                 </tbody>
//               </table>
//             </div>
//           )}
//         </div>

//         {/* --- 3. QUEUED CASES SECTION --- */}
//         <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-md">
//           <div className="flex items-center gap-2 border-b border-slate-800 pb-3 mb-4">
//             <Clock className="w-5 h-5 text-amber-400" />
//             <h2 className="text-lg font-bold text-amber-400">Queued</h2>
//           </div>

//           {queuedCases.length === 0 ? (
//             <p className="text-sm text-slate-500 py-2">Review queue is empty.</p>
//           ) : (
//             <div className="overflow-x-auto">
//               <table className="w-full text-left border-collapse">
//                 <thead>
//                   <tr className="border-b border-slate-800 text-slate-400 text-xs font-semibold uppercase">
//                     <th className="p-3">Trade ID</th>
//                     <th className="p-3 text-right text-amber-400">Priority Score</th>
//                     <th className="p-3 text-right">Non-Compliance Prob.</th>
//                     <th className="p-3 text-right">Confidence</th>
//                     <th className="p-3 pl-6">Flag Reason</th>
//                   </tr>
//                 </thead>
//                 <tbody className="divide-y divide-slate-800/50">
//                   {queuedCases.map((c, index) => {
//                     const compProb = c?.compliance_probability !== undefined && c?.compliance_probability !== null ? Number(c.compliance_probability) : 1.0;
//                     return (
//                       <tr
//                         key={`${c?.trade_id}-${index}`}
//                         onClick={() => setSelectedCase(c)}
//                         className={`text-sm cursor-pointer transition-colors hover:bg-slate-800/40 ${selectedCase?.trade_id === c?.trade_id ? 'bg-purple-950/20 border-l-2 border-purple-500' : ''}`}
//                       >
//                         <td className="p-3 font-mono font-bold text-slate-200">{c?.trade_id}</td>
//                         <td className="p-3 text-right font-bold text-amber-400">{c?.priority_score ?? "0"}</td>
//                         <td className="p-3 text-right text-rose-400">{(1 - compProb).toFixed(2)}</td>
//                         <td className="p-3 text-right text-slate-400">{c?.confidence_score !== undefined && c?.confidence_score !== null ? Number(c.confidence_score).toFixed(2) : "0.00"}</td>
//                         <td className="p-3 pl-6 truncate max-w-[400px] text-slate-400 text-xs">{c?.flag_reason || "Flagged by AI Engine."}</td>
//                       </tr>
//                     );
//                   })}
//                 </tbody>
//               </table>
//             </div>
//           )}
//         </div>

//         {/* --- 4. SELECTED CASE DETAILS PANEL (Placed beneath queues) --- */}
//         {selectedCase ? (
//           <div className="bg-slate-900 border border-purple-500/20 rounded-xl p-6 shadow-lg flex flex-col gap-4">
//             <div className="flex flex-wrap items-center justify-between border-b border-slate-800 pb-4 gap-4">
//               <div>
//                 <span className="text-xs font-semibold uppercase tracking-wider text-purple-400 font-mono">Selected Case Audit Profile</span>
//                 <h2 className="text-2xl font-mono font-bold text-slate-100 mt-0.5">{selectedCase.trade_id}</h2>
//               </div>
//               <div className="flex items-center gap-2">
//                 {selectedCase.escalation_level === "urgent" ? (
//                   <span className="flex items-center gap-1.5 px-3 py-1 bg-rose-950/40 text-rose-400 text-xs font-bold rounded-full border border-rose-500/30 uppercase">
//                     <XCircle className="w-3.5 h-3.5" /> High Risk Urgent
//                   </span>
//                 ) : (
//                   <span className="flex items-center gap-1.5 px-3 py-1 bg-amber-950/40 text-amber-400 text-xs font-bold rounded-full border border-amber-500/30 uppercase">
//                     <Clock className="w-3.5 h-3.5" /> Queue Review ({selectedCase.escalation_level})
//                   </span>
//                 )}
//               </div>
//             </div>

//             <div className="grid grid-cols-1 md:grid-cols-3 gap-4 border-b border-slate-800 pb-4">
//               <div className="bg-slate-950/40 border border-slate-800 p-3 rounded-lg">
//                 <div className="text-xs text-slate-500 font-medium">Compliance Probability</div>
//                 <div className="text-lg font-semibold text-slate-200 mt-0.5">
//                   {(selectedCase.compliance_probability !== undefined && selectedCase.compliance_probability !== null ? Number(selectedCase.compliance_probability).toFixed(2) : "0.00")}
//                 </div>
//               </div>
//               <div className="bg-slate-950/40 border border-slate-800 p-3 rounded-lg">
//                 <div className="text-xs text-slate-500 font-medium">Model Evaluation Confidence</div>
//                 <div className="text-lg font-semibold text-slate-200 mt-0.5">
//                   {(selectedCase.confidence_score !== undefined && selectedCase.confidence_score !== null ? Number(selectedCase.confidence_score).toFixed(2) : "0.00")}
//                 </div>
//               </div>
//               <div className="bg-slate-950/40 border border-slate-800 p-3 rounded-lg">
//                 <div className="text-xs text-slate-500 font-medium">System Priority Weight</div>
//                 <div className="text-lg font-semibold text-amber-400 mt-0.5">{selectedCase.priority_score ?? "N/A"}</div>
//               </div>
//             </div>

//             <div>
//               <h3 className="text-sm font-semibold text-slate-300 uppercase tracking-wider mb-2">Primary Exception Breakdown</h3>
//               <div className="p-4 bg-slate-950/50 rounded-xl border border-slate-800 text-sm text-slate-300 leading-relaxed">
//                 {selectedCase.flag_reason || "No explicit structural audit notes provided for this transaction flag."}
//               </div>
//             </div>

//             <div>
//               <h3 className="text-sm font-semibold text-slate-300 uppercase tracking-wider mb-2">Retrieved Regulatory Policies</h3>
//               <div className="flex flex-wrap gap-2 pt-1">
//                 {renderPolicies(selectedCase.retrieved_policies)}
//               </div>
//             </div>
//           </div>
//         ) : (
//           <div className="bg-slate-900 border border-slate-800 border-dashed rounded-xl p-8 text-center text-slate-500 text-sm">
//             Select a trade record from either section above to open the compliance deep dive terminal.
//           </div>
//         )}
//       </div>
//     </div>
//   );
// }

// export default Dashboard;

///* VERSION 2 */

// import { useEffect, useState } from "react";
// import { getCases } from "../api/cases";
// /*import { ReviewCase } from "../types/case";*/
// import { AlertCircle, ArrowUpRight, CheckCircle2, XCircle } from "lucide-react";

// // Inline Type definition to completely bypass the Vite module import bug:
// export interface ReviewCase {
//   trade_id: string;
//   escalation_level: string;
//   priority_score: number;
//   confidence_score: number;
//   compliance_probability: number;
//   flag_reason: string;
//   retrieved_policies: string[];
//   risk_tolerance: string;
//   investment_objective: string;
//   investment_time_horizon: string;
// }

// function Dashboard() {
//   // Fix 1: Properly typed state using your interface
//   const [cases, setCases] = useState<ReviewCase[]>([]);
//   const [selectedCase, setSelectedCase] = useState<ReviewCase | null>(null);

// /*   useEffect(() => {
//     getCases().then((data) => {
//       setCases(data);
//       if (data.length > 0) setSelectedCase(data[0]); // Default select the first case
//     });
//   }, []);
//  */

//   useEffect(() => {
//     getCases()
//       .then((data) => {
//         console.log("API RAW DATA TYPE:", typeof data, data); // Look at this in your console!
        
//         if (Array.isArray(data)) {
//           setCases(data);
//           if (data.length > 0) setSelectedCase(data[0]);
//         } else if (data && typeof data === 'object' && Array.isArray(data.cases)) {
//           // If your backend wrapped it like: {"cases": [...]}
//           setCases(data.cases);
//           if (data.cases.length > 0) setSelectedCase(data.cases[0]);
//         } else if (data && typeof data === 'object' && Array.isArray(data.data)) {
//           // If your backend wrapped it like: {"data": [...]}
//           setCases(data.data);
//           if (data.data.length > 0) setSelectedCase(data.data[0]);
//         } else {
//           console.error("API did not return an array. Received:", data);
//         }
//       })
//       .catch((err) => {
//         console.error("Failed to fetch cases from FastAPI:", err);
//       });
//   }, []);  

//   // Compute stats dynamically for the top bar
//   const urgentCount = cases.filter(c => c.escalation_level === "urgent").length;
//   const highPriorityCount = cases.filter(c => c.priority_score > 70).length;

//   return (
//     <div className="flex flex-col h-screen bg-slate-950 text-slate-100 font-sans selection:bg-purple-500/30">
//       {/* 1. TOP METRICS METRIC BAR */}
//       <header className="border-b border-slate-800 bg-slate-900/50 px-6 py-3 flex gap-6 text-sm font-medium tracking-wide">
//         <span className="text-rose-400">Urgent: <span className="font-bold text-white">{urgentCount}</span></span>
//         <span className="text-amber-400">Priority Warning: <span className="font-bold text-white">{highPriorityCount}</span></span>
//         <span className="text-slate-400">Total Queue: <span className="font-bold text-white">{cases.length}</span></span>
//       </header>

//       {/* MAIN CONTAINER: Split screen */}
//       <div className="flex flex-1 overflow-hidden">
        
//         {/* 2. LEFT COLUMN: TRADE QUEUE TABLE */}
//         <main className="w-7/12 border-r border-slate-800 p-6 overflow-y-auto">
//           <h2 className="text-lg font-semibold text-slate-300 mb-4 tracking-tight">Active Queue</h2>
          
//           <div className="overflow-hidden border border-slate-800 rounded-lg bg-slate-900/20">
//             <table className="w-full text-left border-collapse text-sm">
//               <thead>
//                 <tr className="border-b border-slate-800 bg-slate-900/60 text-slate-400 font-medium">
//                   <th className="p-3">TRADE ID</th>
//                   <th className="p-3 text-right">PRIORITY</th>
//                   <th className="p-3 text-right">RISK</th>
//                   <th className="p-3 text-right">CONFIDENCE</th>
//                   <th className="p-3">FLAGS</th>
//                 </tr>
//               </thead>
//               <tbody className="divide-y divide-slate-800/60">
//                 {cases.map((c, index) => {
//                 // 1. Safe Fallback for Compliance Probability Calculation
//                 const complianceProb = c.compliance_probability !== undefined && c.compliance_probability !== null 
//                     ? Number(c.compliance_probability) 
//                     : 1.0; // Assume 100% compliant if field is missing, making non-compliance 0.00
                    
//                 const nonComplianceScore = (1 - complianceProb).toFixed(2);

//                 return (
//                     <tr 
//                     // 2. Using index fallback ensures the React Key is strictly unique even if DB has duplicate IDs
//                     key={`${c.trade_id}-${index}`}
//                     onClick={() => setSelectedCase(c)}
//                     className={`cursor-pointer transition-colors hover:bg-slate-800/40 ${
//                         selectedCase?.trade_id === c.trade_id 
//                         ? 'bg-purple-950/30 border-l-2 border-purple-500' 
//                         : ''
//                     }`}
//                     >
//                     <td className="p-3 font-mono text-xs font-bold text-slate-200">{c.trade_id}</td>
//                     <td className="p-3 text-right font-semibold text-amber-400">{c.priority_score ?? 0}</td>
//                     <td className="p-3 text-right text-rose-400">{nonComplianceScore}</td>
//                     <td className="p-3 text-right text-slate-400">
//                         {c.confidence_score !== undefined && c.confidence_score !== null 
//                         ? Number(c.confidence_score).toFixed(2) 
//                         : "0.00"}
//                     </td>
//                     <td className="p-3 max-w-[200px] truncate text-slate-300 text-xs">{c.flag_reason || "No flag reason provided."}</td>
//                     </tr>
//                 );
//                 })}
//               </tbody>
//             </table>
//           </div>
//         </main>

//         {/* 3. RIGHT COLUMN: SELECTED CASE WORKSPACE */}
//         <aside className="w-5/12 p-6 flex flex-col justify-between overflow-y-auto bg-slate-900/10">
//           {selectedCase ? (
//             <div className="flex flex-col h-full justify-between">
//               <div className="space-y-6">
//                 <div>
//                   <span className="text-xs font-mono uppercase tracking-widest text-purple-400 font-bold">Inspection Workspace</span>
//                   <h2 className="text-2xl font-bold tracking-tight text-white mt-1">{selectedCase.trade_id}</h2>
//                 </div>

//                 {/* Client Profile Panel */}
//                 <div className="border border-slate-800 rounded-lg p-4 bg-slate-900/40">
//                   <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-3">Client Profile</h3>
//                   <div className="grid grid-cols-3 gap-2 text-xs">
//                     <div><p className="text-slate-500">Risk Profile</p><p className="font-semibold text-slate-200 mt-0.5">{selectedCase.risk_tolerance}</p></div>
//                     <div><p className="text-slate-500">Objective</p><p className="font-semibold text-slate-200 mt-0.5">{selectedCase.investment_objective}</p></div>
//                     <div><p className="text-slate-500">Horizon</p><p className="font-semibold text-slate-200 mt-0.5">{selectedCase.investment_time_horizon}</p></div>
//                   </div>
//                 </div>

//                 {/* Policies matched */}
//                 <div>
//                   <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-2">Retrieved Policies</h3>
//                   <div className="flex flex-wrap gap-2">
//                     {(() => {
//                     const policies = selectedCase?.retrieved_policies;
                    
//                     // 1. If it's already an array, use it directly
//                     if (Array.isArray(policies)) {
//                         return policies.map((policy: string, i: number) => (
//                         <span key={i} className="px-2 py-1 bg-slate-800 text-xs rounded border border-slate-700">
//                             {policy}
//                         </span>
//                         ));
//                     }
                    
//                     // 2. If it's a string looking like a Python list representation: "['Policy 1', 'Policy 2']"
//                     if (typeof policies === 'string' && policies.startsWith('[')) {
//                         try {
//                         // Clean up brackets/quotes and split by comma
//                         const parsed = policies
//                             .replace(/[\[\]']/g, '') // Strips [, ], and '
//                             .split(',')
//                             .map(p => p.trim())
//                             .filter(Boolean);
                            
//                         return parsed.map((policy: string, i: number) => (
//                             <span key={i} className="px-2 py-1 bg-slate-800 text-xs rounded border border-slate-700">
//                             {policy}
//                             </span>
//                         ));
//                         } catch (e) {
//                         console.error("Failed to parse policy string array", e);
//                         }
//                     }

//                     // 3. If it's just a regular comma-separated text string: "Policy 1, Policy 2"
//                     if (typeof policies === 'string' && policies.trim().length > 0) {
//                         return policies.split(',').map((policy: string, i: number) => (
//                         <span key={i} className="px-2 py-1 bg-slate-800 text-xs rounded border border-slate-700">
//                             {policy.trim()}
//                         </span>
//                         ));
//                     }

//                     // 4. Fallback if empty
//                     return <span className="text-xs text-slate-500">No policies attached.</span>;
//                     })()}
//                   </div>
//                 </div>

//                 {/* Recommendation Framework */}
//                 <div className="border border-slate-800 rounded-lg p-4 bg-slate-900/40">
//                   <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-2">AI Copilot Evaluation</h3>
//                   <div className="flex items-center gap-2 mb-3">
//                     {selectedCase.compliance_probability > 0.5 ? (
//                       <div className="flex items-center gap-2 text-emerald-400 font-bold bg-emerald-950/30 px-2.5 py-1 rounded-full text-xs border border-emerald-500/20">
//                         <CheckCircle2 className="w-4 h-4" /> COMPLIANT ({(selectedCase.compliance_probability).toFixed(2)})
//                       </div>
//                     ) : (
//                       <div className="flex items-center gap-2 text-rose-400 font-bold bg-rose-950/30 px-2.5 py-1 rounded-full text-xs border border-rose-500/20">
//                         <XCircle className="w-4 h-4" /> NON-COMPLIANT ({selectedCase?.compliance_probability !== undefined && selectedCase?.compliance_probability !== null ? Number(selectedCase.compliance_probability).toFixed(2) : "0.00"})
//                       </div>
//                     )}
//                   </div>
//                   <p className="text-xs text-slate-300 leading-relaxed bg-slate-950/40 p-2.5 rounded border border-slate-800/80 font-mono">
//                     System flag generated due to: {selectedCase.flag_reason}. Cross-referencing against structural investment parameters suggests systemic operational friction.
//                   </p>
//                 </div>
//               </div>

//               {/* ACTION TOOLBAR FOOTER */}
//               <div className="grid grid-cols-3 gap-3 pt-6 border-t border-slate-800 mt-6">
//                 <button className="flex items-center justify-center gap-1.5 bg-emerald-600 hover:bg-emerald-500 active:bg-emerald-700 text-white font-medium py-2 px-3 rounded text-sm transition-colors shadow-lg shadow-emerald-900/20">
//                   Approve
//                 </button>
//                 <button className="flex items-center justify-center gap-1.5 bg-slate-800 hover:bg-slate-700 active:bg-slate-900 text-slate-200 border border-slate-700 font-medium py-2 px-3 rounded text-sm transition-colors">
//                   Override
//                 </button>
//                 <button className="flex items-center justify-center gap-1.5 bg-purple-600 hover:bg-purple-500 active:bg-purple-700 text-white font-medium py-2 px-3 rounded text-sm transition-colors shadow-lg shadow-purple-900/20">
//                   Add Notes
//                 </button>
//               </div>
//             </div>
//           ) : (
//             <div className="h-full flex flex-col items-center justify-center text-slate-500 text-sm gap-2">
//               <AlertCircle className="w-5 h-5 stroke-[1.5]" />
//               Select a trade row to inspect case parameters.
//             </div>
//           )}
//         </aside>
//       </div>
//     </div>
//   );
// }

// export default Dashboard;

///* VERSION 1 */
// import { useEffect, useState } from "react";
// import { getCases } from "../api/cases";

// function Dashboard() {
//   const [cases, setCases] = useState<any[]>([]);

//   useEffect(() => {
//     getCases()
//       .then((data) => {
//         // Safety Guard: Ensure we are setting a flat array
//         if (Array.isArray(data)) {
//           setCases(data);
//         } else if (data && typeof data === "object" && Array.isArray(data.cases)) {
//           setCases(data.cases);
//         } else {
//           console.warn("API did not return a direct array. Got:", data);
//         }
//       })
//       .catch((err) => console.error("API Fetch Error:", err));
//   }, []);

//   return (
//     // Added min-h-screen, bg-slate-900 (dark gray/black), and text-slate-100 (bright white text)
//     <div className="p-6 min-h-screen bg-slate-900 text-slate-100">
//       <h1 className="text-3xl font-bold border-b text-slate-700 pb-4">
//         AI Compliance Review Copilot
//       </h1>

//       {cases.map((c: any, index: number) => (
//         <div
//           key={`${c?.trade_id || 'case'}-${index}`}
//           // Updated border color to match dark mode and added a slight background tint to the cards
//           className="border border-slate-700 bg-slate-800/50 rounded p-4 mt-4"
//         >
//           <div className="font-mono text-sm text-purple-400 font-bold">
//             ID: {c?.trade_id || "N/A"}
//           </div>
//           <div className="mt-1">
//             <span className="text-slate-400">Level:</span> {c?.escalation_level || "Unknown"}
//           </div>
//           <div>
//             <span className="text-slate-400">Priority:</span> {c?.priority_score ?? "N/A"}
//           </div>
//           <div className="text-slate-300 text-sm mt-2 pt-2 border-t border-slate-800">
//             {c?.flag_reason || "No reason logged."}
//           </div>
//         </div>
//       ))}
//     </div>
//   );
// }

// export default Dashboard;

// 