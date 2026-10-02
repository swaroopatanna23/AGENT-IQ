import React, { useState } from "react";
import { AgentTraceStep } from "../../types";
import { 
  CheckCircle2, 
  ChevronDown, 
  ChevronUp, 
  Bot, 
  Sparkles, 
  Clock, 
  ShieldCheck, 
  Cpu, 
  FileCode, 
  PieChart 
} from "lucide-react";

interface AgentTraceProps {
  traces: AgentTraceStep[];
  planSteps?: string[];
  executionTimeMs?: number;
}

export const AgentTrace: React.FC<AgentTraceProps> = ({
  traces,
  planSteps = [],
  executionTimeMs = 0,
}) => {
  const [isOpen, setIsOpen] = useState<boolean>(true);
  const [showPlan, setShowPlan] = useState<boolean>(false);

  const getAgentIcon = (name: string) => {
    switch (name.toLowerCase()) {
      case "data agent": return <Cpu className="w-4 h-4 text-blue-500" />;
      case "query understanding agent": return <Sparkles className="w-4 h-4 text-purple-500" />;
      case "analysis schema": return <FileCode className="w-4 h-4 text-amber-500" />;
      case "planning agent": return <Bot className="w-4 h-4 text-indigo-500" />;
      case "analysis agent": return <Cpu className="w-4 h-4 text-emerald-500" />;
      case "validation & privacy agent": return <ShieldCheck className="w-4 h-4 text-green-500" />;
      case "visualization agent": return <PieChart className="w-4 h-4 text-pink-500" />;
      case "explanation agent": return <Sparkles className="w-4 h-4 text-brand-600" />;
      default: return <Bot className="w-4 h-4 text-gray-500" />;
    }
  };

  return (
    <div className="border border-blue-100 bg-blue-50/40 rounded-2xl p-4 shadow-sm space-y-3">
      <div 
        className="flex items-center justify-between cursor-pointer select-none"
        onClick={() => setIsOpen(!isOpen)}
      >
        <div className="flex items-center gap-2.5">
          <div className="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-pulse" />
          <h4 className="text-xs font-bold text-gray-900 tracking-wide uppercase flex items-center gap-1.5">
            AgentIQ Execution Pipeline
            <span className="text-xs font-semibold text-gray-700 lowercase">({traces.length} agents coordinated in {executionTimeMs}ms)</span>
          </h4>
        </div>
        <div className="flex items-center gap-2">
          {planSteps.length > 0 && (
            <button
              onClick={(e) => {
                e.stopPropagation();
                setShowPlan(!showPlan);
              }}
              className="text-xs font-bold text-brand-800 bg-brand-100 hover:bg-brand-200 px-2.5 py-1 rounded-lg transition"
            >
              {showPlan ? "Hide Plan" : "View Planning Agent Steps"}
            </button>
          )}
          {isOpen ? <ChevronUp className="w-4 h-4 text-gray-700" /> : <ChevronDown className="w-4 h-4 text-gray-700" />}
        </div>
      </div>

      {isOpen && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-2 pt-2 border-t border-blue-100/60">
          {traces.map((trace, i) => (
            <div 
              key={i} 
              className="bg-white border border-gray-200 rounded-xl p-3 shadow-2xs flex flex-col justify-between"
            >
              <div className="flex items-center justify-between mb-1.5">
                <div className="flex items-center gap-1.5">
                  {getAgentIcon(trace.agent)}
                  <span className="text-xs font-bold text-gray-900 truncate">{trace.agent}</span>
                </div>
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600 shrink-0" />
              </div>
              <p className="text-xs text-gray-800 font-medium line-clamp-2 leading-relaxed">
                {trace.message}
              </p>
              <div className="flex items-center gap-1 text-[11px] text-gray-700 font-mono font-semibold mt-2">
                <Clock className="w-3.5 h-3.5 text-gray-600" />
                <span>{trace.duration_ms}ms</span>
              </div>
            </div>
          ))}
        </div>
      )}

      {showPlan && planSteps.length > 0 && (
        <div className="bg-white border border-gray-200 rounded-xl p-4 mt-2">
          <h5 className="text-xs font-bold text-gray-900 mb-2 uppercase tracking-wide">
            Deterministic Analysis Plan Formulation (Planning Agent)
          </h5>
          <ol className="list-decimal list-inside space-y-1 text-xs text-gray-700">
            {planSteps.map((step, idx) => (
              <li key={idx} className="leading-relaxed">
                <span className="font-medium text-gray-800">{step}</span>
              </li>
            ))}
          </ol>
        </div>
      )}
    </div>
  );
};
