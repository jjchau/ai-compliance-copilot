import React, { useState, useEffect } from "react";
import { Check, X, CornerUpRight } from "lucide-react";

interface ExecutionFormTrayProps {
  tradeId: string;
  initialNotes: string;
  isAutoPassed: boolean;
  onUpdateNotes: (tradeId: string, text: string) => void;
  onExecuteAction: (
    tradeId: string,
    status: "Reviewed" | "Escalated",
    actionType: "Rejected" | "Approved" | "Escalated",
    notes: string
  ) => void;
}

export const ExecutionFormTray: React.FC<ExecutionFormTrayProps> = ({
  tradeId,
  initialNotes,
  onUpdateNotes,
  onExecuteAction,
}) => {
  const [localNotes, setLocalNotes] = useState<string>(initialNotes);

  useEffect(() => {
    setLocalNotes(initialNotes);
  }, [tradeId, initialNotes]);

  return (
    <div className="pt-1 flex gap-3 items-end shrink-0 border-t border-slate-800/40">
      <div className="flex-1 flex flex-col">
        <label className="text-[9px] font-black text-slate-400 uppercase tracking-widest mb-1">
          Reviewer Sign-off Justification Matrix
        </label>
        <input
          type="text"
          value={localNotes}
          onChange={(e) => setLocalNotes(e.target.value)}
          onBlur={() => onUpdateNotes(tradeId, localNotes)}
          placeholder="Type definitive legal compliance assessment or operational arguments..."
          className="w-full bg-slate-950 border border-slate-800 rounded px-2.5 text-xs text-slate-200 focus:outline-none focus:border-indigo-500 transition-all shadow-inner h-8"
        />
      </div>
      <div className="flex gap-2 h-8">
        <button
          onClick={() => onExecuteAction(tradeId, "Reviewed", "Rejected" as any, localNotes)}
          className="bg-rose-600 hover:bg-rose-500 text-white font-black text-[10px] px-4 rounded flex items-center gap-1.5 uppercase tracking-wider shadow-md transition-colors"
        >
          <X className="w-3.5 h-3.5" />
          Reject Trade
        </button>
        <button
          onClick={() => onExecuteAction(tradeId, "Reviewed", "Approved", localNotes)}
          className="bg-emerald-600 hover:bg-emerald-500 text-slate-950 font-black text-[10px] px-4 rounded flex items-center gap-1.5 uppercase tracking-wider shadow-md transition-colors"
        >
          <Check className="w-3.5 h-3.5" />
          Approve Trade
        </button>
        <button
          onClick={() => onExecuteAction(tradeId, "Escalated", "Escalated", localNotes)}
          className="bg-slate-800 hover:bg-slate-700 text-amber-400 border border-slate-700 font-black text-[10px] px-4 rounded flex items-center gap-1.5 uppercase tracking-wider shadow-md transition-colors"
        >
          <CornerUpRight className="w-3.5 h-3.5" />
          Escalate Review
        </button>
      </div>
    </div>
  );
};