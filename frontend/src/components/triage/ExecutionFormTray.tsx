import React, { useState, useEffect } from "react";
import { Check, X, CornerUpRight, PencilLine } from "lucide-react";

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
  isAutoPassed,
  onUpdateNotes,
  onExecuteAction,
}) => {
  const [localNotes, setLocalNotes] = useState<string>(initialNotes);

  useEffect(() => {
    setLocalNotes(initialNotes);
  }, [tradeId, initialNotes]);

  return (
    <div data-auto-passed={isAutoPassed} className="pt-0 flex flex-col gap-1.5 shrink-0 border-t border-slate-800/40 w-full">
      <div className="flex flex-col gap-0 w-full">
        {/* Added flex, items-center, and a horizontal gap to align icon and text */}
        <label className="flex items-center gap-1.5 text-[9px] font-black text-white uppercase tracking-widest mb-1">
          <PencilLine className="w-3 h-3 shrink-0" />
          <span>Reviewer Assessment Comments</span>
        </label>
        {/* Converted to a multi-row custom textarea to give maximum spacing to notes typing */}
        <textarea
          value={localNotes}
          onChange={(e) => {
            setLocalNotes(e.target.value);
            onUpdateNotes(tradeId, e.target.value);
          }}
          placeholder="Type definitive legal/regulatory compliance assessment reasoning..."
          className="w-full bg-slate-950 border border-slate-800 rounded p-2 text-[11px] text-slate-200 focus:outline-none focus:border-indigo-500 transition-all shadow-inner h-15 resize-none font-sans leading-relaxed custom-scrollbar"
        />
      </div>      
      <div className="flex flex-wrap sm:flex-nowrap gap-2 justify-end w-full">
        <button
          onClick={() => onExecuteAction(tradeId, "Reviewed", "Rejected", localNotes)}
          className="flex-1 sm:flex-none bg-rose-600 hover:bg-rose-500 text-white font-black text-[10px] h-8 px-4 rounded flex items-center justify-center gap-1.5 uppercase tracking-wider shadow-md transition-colors"
        >
          <X className="w-3.5 h-3.5" />
          Reject Trade
        </button>
        <button
          onClick={() => onExecuteAction(tradeId, "Reviewed", "Approved", localNotes)}
          className="flex-1 sm:flex-none bg-emerald-600 hover:bg-emerald-500 text-slate-950 font-black text-[10px] h-8 px-4 rounded flex items-center justify-center gap-1.5 uppercase tracking-wider shadow-md transition-colors"
        >
          <Check className="w-3.5 h-3.5" />
          Approve Trade
        </button>
        <button
          onClick={() => onExecuteAction(tradeId, "Escalated", "Escalated", localNotes)}
          className="flex-1 sm:flex-none bg-slate-800 hover:bg-slate-700 border border-slate-700 text-amber-400 font-black text-[10px] h-8 px-4 rounded flex items-center justify-center gap-1.5 uppercase tracking-wider shadow-md transition-colors"
        >
          <CornerUpRight className="w-3.5 h-3.5" />
          Escalate Case
        </button>
      </div>
    </div>
  );
};
