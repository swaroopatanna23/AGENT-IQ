import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { Navbar, Sidebar } from "../components/layout/Navigation";
import { analysisApi } from "../api/client";
import { History as HistoryIcon, Clock, Sparkles, FileText, ArrowRight } from "lucide-react";

export const HistoryPage: React.FC = () => {
  const [history, setHistory] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchHistory();
  }, []);

  const fetchHistory = async () => {
    try {
      const res = await analysisApi.getHistory();
      setHistory(res.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      <Navbar />

      <div className="flex flex-1">
        <Sidebar />

        <main className="flex-1 p-8 max-w-5xl mx-auto space-y-6">
          <div className="space-y-1">
            <h1 className="text-2xl font-extrabold text-gray-900 tracking-tight">Query Audit History</h1>
            <p className="text-xs text-gray-500">Chronological history of all natural language questions processed by the multi-agent pipeline.</p>
          </div>

          {loading ? (
            <div className="p-12 text-center text-xs text-gray-400">Loading query history...</div>
          ) : history.length === 0 ? (
            <div className="bg-white border border-gray-200 rounded-2xl p-12 text-center space-y-3">
              <HistoryIcon className="w-10 h-10 text-gray-300 mx-auto" />
              <p className="text-sm font-semibold text-gray-700">No queries recorded yet</p>
              <p className="text-xs text-gray-400">Ask questions in the AI Studio to build an audit history.</p>
            </div>
          ) : (
            <div className="space-y-3">
              {history.map((item) => (
                <div key={item.id} className="bg-white border border-gray-200 rounded-2xl p-5 shadow-2xs space-y-3 hover:shadow-sm transition">
                  <div className="flex items-start justify-between">
                    <div>
                      <span className="text-[10px] font-bold uppercase tracking-wider text-brand-600 bg-blue-50 px-2 py-0.5 rounded-full border border-blue-200">
                        {item.intent}
                      </span>
                      <h3 className="text-sm font-bold text-gray-900 mt-1">"{item.question}"</h3>
                    </div>
                    <div className="flex items-center gap-1 text-[11px] text-gray-400 font-mono">
                      <Clock className="w-3.5 h-3.5" />
                      <span>{item.execution_time_ms}ms</span>
                    </div>
                  </div>

                  <p className="text-xs text-gray-700 font-medium bg-gray-50/80 p-3 rounded-xl border border-gray-100">
                    {item.short_answer || "Analysis completed successfully."}
                  </p>

                  <div className="flex items-center justify-between text-xs text-gray-400 pt-1 border-t border-gray-100">
                    <span className="flex items-center gap-1.5">
                      <FileText className="w-3.5 h-3.5 text-gray-400" />
                      Dataset: <b className="text-gray-700">{item.dataset_name}</b>
                    </span>
                    <Link
                      to="/workspace"
                      className="text-brand-600 font-semibold hover:underline flex items-center gap-1"
                    >
                      Re-open in Studio
                      <ArrowRight className="w-3 h-3" />
                    </Link>
                  </div>
                </div>
              ))}
            </div>
          )}
        </main>
      </div>
    </div>
  );
};
