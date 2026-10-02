import React, { useState, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Navbar, Sidebar } from "../components/layout/Navigation";
import { useAuth } from "../context/AuthContext";
import { datasetApi, analysisApi, dashboardApi } from "../api/client";
import { 
  FileSpreadsheet, 
  Sparkles, 
  Layers, 
  CheckCircle, 
  ArrowRight, 
  Clock, 
  Database,
  BarChart3
} from "lucide-react";

export const OverviewPage: React.FC = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [datasetsCount, setDatasetsCount] = useState(0);
  const [dashboardsCount, setDashboardsCount] = useState(0);
  const [recentQueries, setRecentQueries] = useState<any[]>([]);
  const [recentDatasets, setRecentDatasets] = useState<any[]>([]);

  useEffect(() => {
    loadOverview();
  }, []);

  const loadOverview = async () => {
    try {
      const [dsRes, dbRes, hRes] = await Promise.all([
        datasetApi.list(),
        dashboardApi.list(),
        analysisApi.getHistory()
      ]);
      setDatasetsCount(dsRes.data.length);
      setRecentDatasets(dsRes.data.slice(0, 3));
      setDashboardsCount(dbRes.data.length);
      setRecentQueries(hRes.data.slice(0, 5));
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      <Navbar />

      <div className="flex flex-1">
        <Sidebar />

        <main className="flex-1 p-8 max-w-6xl mx-auto space-y-8">
          {/* Welcome Banner */}
          <div className="bg-gradient-to-r from-brand-600 to-indigo-700 rounded-3xl p-8 text-white shadow-md flex items-center justify-between">
            <div className="space-y-2 max-w-xl">
              <span className="text-xs font-semibold uppercase tracking-wider text-blue-200">
                AgentIQ Analytics Platform
              </span>
              <h1 className="text-2xl sm:text-3xl font-black tracking-tight">
                Welcome back, {user?.full_name || "Researcher"}!
              </h1>
              <p className="text-sm text-blue-100 font-normal leading-relaxed">
                Connect your heterogeneous data sources, query in plain natural language, and let multi-agent AI generate interactive dashboards.
              </p>
              <div className="pt-2">
                <button
                  onClick={() => navigate("/workspace")}
                  className="bg-white hover:bg-blue-50 text-brand-700 font-bold text-xs px-5 py-2.5 rounded-xl shadow-sm transition flex items-center gap-2"
                >
                  <Sparkles className="w-4 h-4 text-brand-600" />
                  Start New AI Query
                </button>
              </div>
            </div>

            <div className="hidden lg:block">
              <div className="w-32 h-32 rounded-2xl bg-white/10 backdrop-blur-xs border border-white/20 flex items-center justify-center p-4 text-center">
                <div>
                  <BarChart3 className="w-10 h-10 mx-auto text-blue-200 mb-1" />
                  <span className="text-[11px] font-semibold text-white">Batch 08 Major Project</span>
                </div>
              </div>
            </div>
          </div>

          {/* Quick Metrics Cards */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div className="bg-white border border-gray-200 rounded-2xl p-5 shadow-2xs space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold uppercase text-gray-400">Connected Datasets</span>
                <FileSpreadsheet className="w-4 h-4 text-brand-600" />
              </div>
              <p className="text-3xl font-black text-gray-900">{datasetsCount}</p>
              <Link to="/datasets" className="text-xs text-brand-600 font-medium hover:underline inline-block">
                View all datasets →
              </Link>
            </div>

            <div className="bg-white border border-gray-200 rounded-2xl p-5 shadow-2xs space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold uppercase text-gray-400">Saved Dashboards</span>
                <Layers className="w-4 h-4 text-purple-600" />
              </div>
              <p className="text-3xl font-black text-gray-900">{dashboardsCount}</p>
              <Link to="/dashboards" className="text-xs text-brand-600 font-medium hover:underline inline-block">
                Manage dashboards →
              </Link>
            </div>

            <div className="bg-white border border-gray-200 rounded-2xl p-5 shadow-2xs space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold uppercase text-gray-400">Total Inquiries</span>
                <Sparkles className="w-4 h-4 text-emerald-600" />
              </div>
              <p className="text-3xl font-black text-gray-900">{recentQueries.length}</p>
              <Link to="/history" className="text-xs text-brand-600 font-medium hover:underline inline-block">
                Review query audit log →
              </Link>
            </div>
          </div>

          {/* Recent Activity */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Recent Queries */}
            <div className="bg-white border border-gray-200 rounded-2xl p-5 shadow-2xs space-y-4">
              <div className="flex items-center justify-between border-b border-gray-100 pb-3">
                <h3 className="text-sm font-bold text-gray-900">Recent Analytical Questions</h3>
                <Link to="/history" className="text-xs text-brand-600 font-medium hover:underline">
                  View all
                </Link>
              </div>

              {recentQueries.length === 0 ? (
                <p className="text-xs text-gray-400 py-6 text-center italic">No queries executed yet.</p>
              ) : (
                <div className="space-y-3">
                  {recentQueries.map((q) => (
                    <div key={q.id} className="p-3 bg-gray-50/70 border border-gray-100 rounded-xl space-y-1">
                      <p className="text-xs font-bold text-gray-900 truncate">"{q.question}"</p>
                      <p className="text-[11px] text-gray-600 line-clamp-1">{q.short_answer}</p>
                      <div className="flex items-center justify-between text-[10px] text-gray-400 pt-1">
                        <span>Dataset: {q.dataset_name}</span>
                        <span>{q.execution_time_ms}ms</span>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Recent Datasets */}
            <div className="bg-white border border-gray-200 rounded-2xl p-5 shadow-2xs space-y-4">
              <div className="flex items-center justify-between border-b border-gray-100 pb-3">
                <h3 className="text-sm font-bold text-gray-900">Recent Datasets</h3>
                <Link to="/datasets" className="text-xs text-brand-600 font-medium hover:underline">
                  View all
                </Link>
              </div>

              {recentDatasets.length === 0 ? (
                <p className="text-xs text-gray-400 py-6 text-center italic">No datasets connected yet.</p>
              ) : (
                <div className="space-y-3">
                  {recentDatasets.map((d) => (
                    <div key={d.id} className="p-3 bg-gray-50/70 border border-gray-100 rounded-xl flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <div className="w-8 h-8 rounded-lg bg-blue-100 text-brand-700 flex items-center justify-center font-bold text-[10px] uppercase">
                          {d.file_format}
                        </div>
                        <div>
                          <p className="text-xs font-bold text-gray-900 truncate max-w-[180px]">{d.name}</p>
                          <p className="text-[10px] text-gray-500">{d.row_count} rows · {d.column_count} cols</p>
                        </div>
                      </div>

                      <button
                        onClick={() => navigate("/workspace")}
                        className="text-xs font-semibold text-brand-600 hover:text-brand-700 bg-white border border-gray-200 px-2.5 py-1.5 rounded-lg shadow-2xs transition"
                      >
                        Analyze
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </main>
      </div>
    </div>
  );
};
