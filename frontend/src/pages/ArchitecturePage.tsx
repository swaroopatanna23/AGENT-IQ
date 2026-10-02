import React from "react";
import { Navbar, Sidebar } from "../components/layout/Navigation";
import { 
  Bot, 
  Database, 
  Cpu, 
  Sparkles, 
  FileCode, 
  ShieldCheck, 
  PieChart, 
  Layers, 
  MessageSquare, 
  CheckCircle2, 
  ArrowDown, 
  ArrowRight 
} from "lucide-react";

export const ArchitecturePage: React.FC = () => {
  const steps = [
    {
      num: "01",
      name: "USER & DATA SOURCES",
      role: "Heterogeneous Data Ingestion",
      desc: "Accepts CSV, Excel (.xlsx, .xls), JSON, Google Sheets, MySQL, PostgreSQL, and MongoDB through a unified DataSourceConnector abstraction.",
      icon: Database,
      color: "bg-blue-50 text-blue-700 border-blue-200"
    },
    {
      num: "02",
      name: "DATA AGENT",
      role: "Schema Detection & Profiling (Slide 10)",
      desc: "Deterministic Pandas analysis detecting row/col counts, datatypes, missing values, duplicates, outliers (IQR), and PII fields to compute a composite Quality Score.",
      icon: Cpu,
      color: "bg-indigo-50 text-indigo-700 border-indigo-200"
    },
    {
      num: "03",
      name: "QUERY UNDERSTANDING AGENT",
      role: "Multilingual Query Parsing (Slide 9)",
      desc: "Combines a TF-IDF + LinearSVC baseline intent classifier with Google Gemini 2.5 GenAI structured slot-filling across English, Hindi, Telugu, and European languages.",
      icon: Sparkles,
      color: "bg-purple-50 text-purple-700 border-purple-200"
    },
    {
      num: "04",
      name: "ANALYSIS SCHEMA",
      role: "Formal Intermediate Contract",
      desc: "Validates intent, metric columns, dimensions, filter predicates, aggregations, and sorting rules using strict Pydantic models. Zero column hallucination.",
      icon: FileCode,
      color: "bg-amber-50 text-amber-700 border-amber-200"
    },
    {
      num: "05",
      name: "PLANNING AGENT",
      role: "Adaptive Workflow Formulation",
      desc: "Formulates an ordered, verifiable step-by-step execution plan for the Pandas/SQL compute engine, transparently displayed in the UI.",
      icon: Bot,
      color: "bg-cyan-50 text-cyan-700 border-cyan-200"
    },
    {
      num: "06",
      name: "ANALYSIS AGENT",
      role: "Deterministic Tool Execution",
      desc: "Executes mathematical operations strictly using curated Pandas/NumPy functions (filter, group_by, trend, correlation, statistics). Zero arbitrary LLM code execution.",
      icon: Cpu,
      color: "bg-emerald-50 text-emerald-700 border-emerald-200"
    },
    {
      num: "07",
      name: "VALIDATION & PRIVACY AGENT",
      role: "Integrity & PII Protection",
      desc: "Verifies non-empty partitions and data validity. Scans and masks sensitive PII attributes (emails, phone numbers, identifiers) before visualization.",
      icon: ShieldCheck,
      color: "bg-green-50 text-green-700 border-green-200"
    },
    {
      num: "08",
      name: "VISUALIZATION AGENT",
      role: "Automated Visualization Selection",
      desc: "Heuristic decision matrix recommending optimal charts (Bar, Line, Donut, Scatter, KPI Card) and synthesizing 3 interactive dashboard alternatives (Designs A, B, C).",
      icon: PieChart,
      color: "bg-pink-50 text-pink-700 border-pink-200"
    },
    {
      num: "09",
      name: "EXPLANATION AGENT",
      role: "Grounded Explainable AI (XAI)",
      desc: "Generates natural language takeaways strictly grounded in the calculated numbers. Never invents values or hallucinations.",
      icon: MessageSquare,
      color: "bg-brand-50 text-brand-700 border-brand-200"
    },
    {
      num: "10",
      name: "INTERACTIVE DASHBOARD",
      role: "Studio Customization & Export",
      desc: "Allows multi-turn conversational follow-up questions, component rearrangement, and PDF/CSV reporting.",
      icon: Layers,
      color: "bg-blue-50 text-blue-700 border-blue-200"
    }
  ];

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      <Navbar />

      <div className="flex flex-1">
        <Sidebar />

        <main className="flex-1 p-8 max-w-5xl mx-auto space-y-8">
          <div className="space-y-1">
            <h1 className="text-2xl font-extrabold text-gray-900 tracking-tight">System Design & Methodology</h1>
            <p className="text-xs text-gray-500">
              The AgentIQ 11-stage multi-agent orchestration architecture directly mirroring Batch-08.pdf (Slides 8 & 9).
            </p>
          </div>

          {/* Sequential Agent Flow List */}
          <div className="space-y-4">
            {steps.map((step, idx) => {
              const Icon = step.icon;
              return (
                <div key={step.num} className="relative">
                  <div className="bg-white border border-gray-200 rounded-2xl p-5 shadow-2xs flex items-start gap-4 hover:shadow-sm transition">
                    <div className={`w-12 h-12 rounded-xl flex items-center justify-center shrink-0 border ${step.color}`}>
                      <Icon className="w-6 h-6" />
                    </div>

                    <div className="flex-1 space-y-1">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          <span className="text-xs font-mono font-bold text-gray-400">{step.num}</span>
                          <h3 className="text-sm font-bold text-gray-900">{step.name}</h3>
                        </div>
                        <span className="text-xs font-semibold text-brand-600 bg-brand-50 border border-brand-100 px-2.5 py-0.5 rounded-full">
                          {step.role}
                        </span>
                      </div>
                      <p className="text-xs text-gray-600 leading-relaxed pt-1">
                        {step.desc}
                      </p>
                    </div>
                  </div>

                  {idx < steps.length - 1 && (
                    <div className="flex justify-center my-1">
                      <ArrowDown className="w-4 h-4 text-gray-300" />
                    </div>
                  )}
                </div>
              );
            })}
          </div>

          {/* Project Details Footer */}
          <div className="bg-white border border-gray-200 rounded-2xl p-6 shadow-2xs text-xs text-gray-500 space-y-2">
            <h4 className="font-bold text-gray-900 text-sm">Academic Project Attribution</h4>
            <p>Department of Data Engineering • CSE-Data Science • Regulation R23 • Course Code: R23MSCSP003</p>
            <p>Guide: Mr. M. Aswini Kumar, Assistant Professor | Coordinator: Dr. P. Srinivasa Rao | HOD: Dr. V. Jyothi</p>
          </div>
        </main>
      </div>
    </div>
  );
};
