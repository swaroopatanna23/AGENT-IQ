import React, { useState, useEffect, useRef } from "react";
import { Navbar, Sidebar } from "../components/layout/Navigation";
import { Dataset, AnalysisResponse } from "../types";
import { datasetApi, analysisApi, exportApi, dashboardApi } from "../api/client";
import { ChartRenderer } from "../components/analysis/ChartRenderer";
import { AgentTrace } from "../components/analysis/AgentTrace";
import { 
  Sparkles, 
  Upload, 
  FileText, 
  X, 
  ArrowRight, 
  RefreshCw, 
  Download, 
  Layers, 
  ShieldAlert, 
  Check, 
  Database,
  BarChart3,
  LineChart as LineChartIcon,
  PieChart as PieChartIcon,
  Table as TableIcon
} from "lucide-react";

export const WorkspacePage: React.FC = () => {
  const [datasets, setDatasets] = useState<Dataset[]>([]);
  const [activeDataset, setActiveDataset] = useState<Dataset | null>(null);
  const [query, setQuery] = useState("What is average marks by age?");
  const [suggestedQuestions, setSuggestedQuestions] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [showAttachModal, setShowAttachModal] = useState(false);
  
  // Multi-Agent Pipeline Result
  const [analysisResult, setAnalysisResult] = useState<AnalysisResponse | null>(null);
  const [selectedChartType, setSelectedChartType] = useState<string>("bar");
  const [activeDashboardDesign, setActiveDashboardDesign] = useState<string>("design_a");
  const [savedSuccess, setSavedSuccess] = useState(false);

  const fileInputRef = useRef<HTMLInputElement>(null);

  // Load existing datasets on mount
  useEffect(() => {
    loadDatasets();
  }, []);

  const loadDatasets = async () => {
    try {
      const res = await datasetApi.list();
      setDatasets(res.data);
      if (res.data.length > 0 && !activeDataset) {
        selectDataset(res.data[0]);
      }
    } catch (err) {
      console.error("Failed to load datasets", err);
    }
  };

  const selectDataset = async (ds: Dataset) => {
    setActiveDataset(ds);
    try {
      const qRes = await analysisApi.getSuggestedQuestions(ds.id);
      setSuggestedQuestions(qRes.data);
    } catch {
      setSuggestedQuestions([]);
    }
  };

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!e.target.files || e.target.files.length === 0) return;
    const file = e.target.files[0];
    setUploading(true);
    try {
      const res = await datasetApi.upload(file);
      await loadDatasets();
      selectDataset(res.data);
      setShowAttachModal(false);
    } catch (err: any) {
      alert(err.response?.data?.detail || "Upload failed");
    } finally {
      setUploading(false);
    }
  };

  const handleLoadSample = async (sampleName: string) => {
    setUploading(true);
    try {
      const res = await datasetApi.loadSample(sampleName);
      await loadDatasets();
      selectDataset(res.data);
      setShowAttachModal(false);
      // Auto-set matching query
      if (sampleName === "students") setQuery("What is average marks by age?");
      else if (sampleName === "retail") setQuery("Which region has the highest sales?");
      else if (sampleName === "employee") setQuery("Compare salary across departments");
      else if (sampleName === "healthcare") setQuery("What is the average treatment cost by diagnosis?");
    } catch (err: any) {
      alert("Failed to load sample dataset");
    } finally {
      setUploading(false);
    }
  };

  const handleAnalyze = async (customQuery?: string) => {
    const qText = customQuery || query;
    if (!qText.trim() || !activeDataset) return;

    setLoading(true);
    try {
      const res = await analysisApi.query({
        dataset_id: activeDataset.id,
        question: qText,
        conversation_id: analysisResult?.conversation_id,
        language: "en"
      });
      setAnalysisResult(res.data);
      setSelectedChartType(res.data.visualization?.chart_type || "bar");
      setActiveDashboardDesign("design_a");
      setSavedSuccess(false);
    } catch (err: any) {
      alert(err.response?.data?.detail || "Analysis failed. Please verify query.");
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleAnalyze();
    }
  };

  const handleSaveToDashboard = async () => {
    if (!activeDataset || !analysisResult) return;
    try {
      await dashboardApi.create({
        dataset_id: activeDataset.id,
        title: `${activeDataset.name} Dashboard`,
        description: `Analysis for: "${analysisResult.schema.user_question}"`,
        layout_type: "grid",
        components: [
          {
            title: analysisResult.visualization.title,
            component_type: selectedChartType,
            config: {
              ...analysisResult.visualization,
              chart_type: selectedChartType
            },
            data_cache: analysisResult.result_data,
            query_id: analysisResult.query_id
          }
        ]
      });
      setSavedSuccess(true);
      setTimeout(() => setSavedSuccess(false), 3000);
    } catch {
      alert("Failed to save to dashboard");
    }
  };

  const handleExportPdf = async () => {
    if (!activeDataset || !analysisResult) return;
    try {
      const res = await exportApi.downloadPdfReport({
        title: "AgentIQ Analysis Report",
        dataset_name: activeDataset.name,
        question: analysisResult.schema.user_question,
        short_answer: analysisResult.explanation.short_answer,
        key_insights: analysisResult.explanation.key_insights,
        kpis: analysisResult.summary_kpis,
        table_data: analysisResult.result_data
      });
      const blob = new Blob([res.data], { type: "application/pdf" });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = `AgentIQ_${activeDataset.name}_Report.pdf`;
      link.click();
    } catch (err) {
      alert("Failed to export PDF report");
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      <Navbar />

      <div className="flex flex-1">
        <Sidebar />

        <main className="flex-1 p-8 max-w-6xl mx-auto space-y-6">
          {/* Header matching Slide 12 */}
          <div className="space-y-1">
            <h1 className="text-2xl font-extrabold text-gray-900 tracking-tight">Analyze Your Data</h1>
            <p className="text-xs text-gray-700 font-medium">Upload your data and ask questions in natural language.</p>
          </div>

          {/* Attach Data Box / Active File Pill (Slide 12) */}
          <div className="bg-white border border-gray-200/90 rounded-2xl p-4 shadow-sm space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold text-gray-800 uppercase tracking-wider">
                Attach Data (csv, xlsx, json)
              </span>
              <button
                onClick={() => setShowAttachModal(true)}
                className="text-xs font-semibold text-brand-600 hover:text-brand-700 bg-brand-50 hover:bg-brand-100 border border-brand-200 px-3 py-1.5 rounded-lg transition flex items-center gap-1.5"
              >
                <Upload className="w-3.5 h-3.5" />
                Attach Data
              </button>
            </div>

            {/* Selected File Chip (Directly from Slide 12) */}
            {activeDataset ? (
              <div className="inline-flex items-center gap-3 bg-blue-50/70 border border-blue-200 px-3 py-2 rounded-xl text-xs">
                <FileText className="w-4 h-4 text-brand-600" />
                <span className="font-semibold text-gray-900">{activeDataset.name}</span>
                <span className="text-gray-700 font-mono text-xs font-medium">
                  {activeDataset.file_format.toUpperCase()} · {(activeDataset.file_size_bytes / 1024).toFixed(1)} KB
                </span>
                <span className="flex items-center gap-1 text-emerald-700 font-semibold pl-2 border-l border-blue-200">
                  <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
                  Analyzing {activeDataset.name}
                </span>
                <button
                  onClick={() => setActiveDataset(null)}
                  className="text-gray-600 hover:text-gray-900 p-0.5 rounded-md"
                >
                  <X className="w-3.5 h-3.5" />
                </button>
              </div>
            ) : (
              <div 
                onClick={() => setShowAttachModal(true)}
                className="border-2 border-dashed border-gray-300 rounded-xl p-6 text-center cursor-pointer hover:border-brand-400 hover:bg-blue-50/40 transition"
              >
                <Upload className="w-6 h-6 text-gray-600 mx-auto mb-2" />
                <p className="text-xs font-bold text-gray-800">Click to attach a dataset or choose demo data</p>
                <p className="text-xs text-gray-600 font-medium">CSV, Excel (.xlsx), or JSON</p>
              </div>
            )}
          </div>

          {/* Natural Language Query Bar (Slide 12) */}
          <div className="bg-white border border-gray-200/90 rounded-2xl p-4 shadow-sm space-y-3">
            <textarea
              rows={3}
              maxLength={500}
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="What is average marks by age?"
              className="w-full text-sm text-gray-900 placeholder-gray-500 border border-gray-300 rounded-xl p-3 focus:outline-none focus:ring-2 focus:ring-brand-500 resize-none font-medium"
            />

            <div className="flex items-center justify-between pt-1">
              <span className="text-xs text-gray-700 font-medium">
                Press Enter to analyze, Shift + Enter for newline
              </span>
              <div className="flex items-center gap-3">
                <span className="text-xs text-gray-700 font-mono font-medium">
                  {query.length} / 500
                </span>
                <button
                  onClick={() => handleAnalyze()}
                  disabled={loading || !activeDataset || !query.trim()}
                  className="bg-brand-600 hover:bg-brand-700 text-white font-semibold text-xs px-5 py-2.5 rounded-xl shadow-sm transition flex items-center gap-2 disabled:opacity-50"
                >
                  {loading ? (
                    <>
                      <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                      Analyzing...
                    </>
                  ) : (
                    <>
                      Analyze
                      <ArrowRight className="w-3.5 h-3.5" />
                    </>
                  )}
                </button>
              </div>
            </div>

            {/* Dynamic Suggested Questions */}
            {suggestedQuestions.length > 0 && (
              <div className="pt-2 border-t border-gray-200 flex flex-wrap gap-2 items-center">
                <span className="text-xs font-bold text-gray-700 uppercase tracking-wider">Suggestions:</span>
                {suggestedQuestions.map((q, i) => (
                  <button
                    key={i}
                    onClick={() => {
                      setQuery(q);
                      handleAnalyze(q);
                    }}
                    className="text-xs bg-gray-100 hover:bg-blue-50 text-gray-800 font-medium hover:text-brand-700 border border-gray-300 rounded-lg px-2.5 py-1 transition"
                  >
                    {q}
                  </button>
                ))}
              </div>
            )}
          </div>

          {/* Multi-Agent Results Canvas */}
          {analysisResult && (
            <div className="space-y-6 pt-2">
              {/* Agent Observability Trace */}
              <AgentTrace 
                traces={analysisResult.agent_trace}
                planSteps={analysisResult.plan?.steps}
                executionTimeMs={analysisResult.execution_time_ms}
              />

              {/* Privacy Warning Banner if PII was detected & masked */}
              {analysisResult.validation?.privacy_warning && (
                <div className="bg-amber-50 border border-amber-200 text-amber-800 text-xs px-4 py-2.5 rounded-xl font-medium flex items-center gap-2">
                  <ShieldAlert className="w-4 h-4 text-amber-600 shrink-0" />
                  {analysisResult.validation.privacy_warning}
                </div>
              )}

              {/* Multi-Dashboard Layout Switcher Tabs (Slide 8-9) */}
              <div className="bg-white border border-gray-200/90 rounded-2xl p-6 shadow-sm space-y-6">
                <div className="flex flex-wrap items-center justify-between gap-4 pb-4 border-b border-gray-100">
                  <div>
                    <h2 className="text-lg font-bold text-gray-900">{analysisResult.visualization?.title}</h2>
                    <p className="text-xs text-gray-700 font-medium">
                      Query Intent: <span className="font-semibold text-brand-700">{analysisResult.schema.detected_intent}</span> · Processed {analysisResult.row_count} records in {analysisResult.execution_time_ms}ms
                    </p>
                  </div>

                  {/* Actions: Chart Switcher & Save & Export */}
                  <div className="flex items-center gap-2">
                    <div className="flex items-center bg-gray-100 p-1 rounded-xl">
                      <button
                        onClick={() => setSelectedChartType("bar")}
                        title="Bar Chart"
                        className={`p-1.5 rounded-lg ${selectedChartType === "bar" ? "bg-white text-brand-700 shadow-2xs font-bold" : "text-gray-700"}`}
                      >
                        <BarChart3 className="w-4 h-4" />
                      </button>
                      <button
                        onClick={() => setSelectedChartType("line")}
                        title="Line Chart"
                        className={`p-1.5 rounded-lg ${selectedChartType === "line" ? "bg-white text-brand-700 shadow-2xs font-bold" : "text-gray-700"}`}
                      >
                        <LineChartIcon className="w-4 h-4" />
                      </button>
                      <button
                        onClick={() => setSelectedChartType("donut")}
                        title="Donut Chart"
                        className={`p-1.5 rounded-lg ${selectedChartType === "donut" ? "bg-white text-brand-700 shadow-2xs font-bold" : "text-gray-700"}`}
                      >
                        <PieChartIcon className="w-4 h-4" />
                      </button>
                      <button
                        onClick={() => setSelectedChartType("table")}
                        title="Table View"
                        className={`p-1.5 rounded-lg ${selectedChartType === "table" ? "bg-white text-brand-700 shadow-2xs font-bold" : "text-gray-700"}`}
                      >
                        <TableIcon className="w-4 h-4" />
                      </button>
                    </div>

                    <button
                      onClick={handleSaveToDashboard}
                      className="text-xs font-semibold text-gray-800 bg-white hover:bg-gray-50 border border-gray-300 px-3 py-2 rounded-xl transition flex items-center gap-1.5 shadow-2xs"
                    >
                      {savedSuccess ? (
                        <>
                          <Check className="w-3.5 h-3.5 text-emerald-600" />
                          <span className="text-emerald-700 font-bold">Saved!</span>
                        </>
                      ) : (
                        <>
                          <Layers className="w-3.5 h-3.5 text-gray-700" />
                          Add to Dashboard
                        </>
                      )}
                    </button>

                    <button
                      onClick={handleExportPdf}
                      className="text-xs font-semibold text-brand-700 bg-brand-50 hover:bg-brand-100 border border-brand-200 px-3 py-2 rounded-xl transition flex items-center gap-1.5"
                    >
                      <Download className="w-3.5 h-3.5" />
                      Export Report
                    </button>
                  </div>
                </div>

                {/* Dashboard Design Alternative Selector Tabs */}
                <div className="flex gap-2">
                  {analysisResult.dashboards?.designs.map((d) => (
                    <button
                      key={d.id}
                      onClick={() => setActiveDashboardDesign(d.id)}
                      className={`text-xs font-bold px-3 py-1.5 rounded-lg transition ${
                        activeDashboardDesign === d.id
                          ? "bg-brand-600 text-white shadow-2xs"
                          : "bg-gray-100 text-gray-800 hover:bg-gray-200"
                      }`}
                    >
                      {d.name}
                    </button>
                  ))}
                </div>

                {/* KPI Metrics Highlight Cards */}
                {Object.keys(analysisResult.summary_kpis || {}).length > 0 && (
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                    {Object.entries(analysisResult.summary_kpis).map(([k, v]) => (
                      <div key={k} className="bg-gray-50 border border-gray-200 rounded-xl p-3 space-y-1">
                        <p className="text-xs font-bold text-gray-700 truncate capitalize">{k}</p>
                        <p className="text-lg font-black text-gray-900">{String(v)}</p>
                      </div>
                    ))}
                  </div>
                )}

                {/* Primary Chart Canvas */}
                <div className="pt-2">
                  <ChartRenderer
                    chartType={selectedChartType}
                    data={analysisResult.result_data}
                    xAxis={analysisResult.visualization?.x_axis}
                    yAxis={analysisResult.visualization?.y_axis}
                  />
                </div>

                {/* Grounded Explanation & Insights Box (Explanation Agent) */}
                <div className="bg-gradient-to-r from-blue-50/60 to-indigo-50/40 border border-blue-200/80 rounded-2xl p-5 space-y-3">
                  <div className="flex items-center gap-2">
                    <Sparkles className="w-4 h-4 text-brand-600" />
                    <h3 className="text-xs font-bold uppercase tracking-wider text-brand-900">
                      Grounded Insights & Analytical Findings (Explanation Agent)
                    </h3>
                  </div>

                  <p className="text-sm text-gray-900 font-bold leading-relaxed">
                    {analysisResult.explanation.short_answer}
                  </p>

                  <div className="space-y-1.5 pt-1">
                    {analysisResult.explanation.key_insights?.map((ins, i) => (
                      <div key={i} className="flex items-start gap-2 text-xs text-gray-800 font-medium leading-relaxed">
                        <span className="w-1.5 h-1.5 rounded-full bg-brand-500 mt-1.5 shrink-0" />
                        <span>{ins}</span>
                      </div>
                    ))}
                  </div>

                  {analysisResult.explanation.observations?.length > 0 && (
                    <div className="pt-2 border-t border-blue-200/50 text-xs text-gray-700 font-medium flex flex-wrap gap-4">
                      {analysisResult.explanation.observations.map((obs, i) => (
                        <span key={i}>• {obs}</span>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}
        </main>
      </div>

      {/* Attach Data Modal (Slide 12) */}
      {showAttachModal && (
        <div className="fixed inset-0 bg-black/40 backdrop-blur-xs flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-2xl max-w-lg w-full p-6 shadow-xl space-y-6">
            <div className="flex items-center justify-between pb-3 border-b border-gray-100">
              <h3 className="text-base font-bold text-gray-900">Attach Dataset</h3>
              <button onClick={() => setShowAttachModal(false)} className="text-gray-600 hover:text-gray-900">
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="space-y-4">
              {/* File Upload Option */}
              <div>
                <p className="text-xs font-bold text-gray-800 uppercase tracking-wider mb-2">Upload Local File</p>
                <input
                  type="file"
                  ref={fileInputRef}
                  accept=".csv,.xlsx,.xls,.json"
                  onChange={handleFileUpload}
                  className="hidden"
                />
                <button
                  onClick={() => fileInputRef.current?.click()}
                  disabled={uploading}
                  className="w-full border-2 border-dashed border-gray-300 hover:border-brand-500 hover:bg-blue-50/40 p-6 rounded-xl text-center transition cursor-pointer flex flex-col items-center justify-center gap-2"
                >
                  <Upload className="w-6 h-6 text-brand-600" />
                  <span className="text-xs font-bold text-gray-800">
                    {uploading ? "Uploading & Profiling..." : "Choose CSV, Excel (.xlsx), or JSON file"}
                  </span>
                </button>
              </div>

              {/* Preloaded Demo Datasets */}
              <div>
                <p className="text-xs font-bold text-gray-800 uppercase tracking-wider mb-2">Or Quick Load Demo Data</p>
                <div className="grid grid-cols-2 gap-2">
                  <button
                    onClick={() => handleLoadSample("students")}
                    disabled={uploading}
                    className="p-3 text-left border border-gray-200 hover:border-brand-400 hover:bg-blue-50/40 rounded-xl transition space-y-1"
                  >
                    <p className="text-xs font-bold text-gray-900">Students.csv</p>
                    <p className="text-xs text-gray-600 font-medium">Education · 60 rows</p>
                  </button>

                  <button
                    onClick={() => handleLoadSample("retail")}
                    disabled={uploading}
                    className="p-3 text-left border border-gray-200 hover:border-brand-400 hover:bg-blue-50/40 rounded-xl transition space-y-1"
                  >
                    <p className="text-xs font-bold text-gray-900">Online Retail Sales</p>
                    <p className="text-xs text-gray-600 font-medium">E-Commerce · 120 rows</p>
                  </button>

                  <button
                    onClick={() => handleLoadSample("employee")}
                    disabled={uploading}
                    className="p-3 text-left border border-gray-200 hover:border-brand-400 hover:bg-blue-50/40 rounded-xl transition space-y-1"
                  >
                    <p className="text-xs font-bold text-gray-900">Employee Workforce</p>
                    <p className="text-xs text-gray-600 font-medium">Business/HR · 80 rows</p>
                  </button>

                  <button
                    onClick={() => handleLoadSample("healthcare")}
                    disabled={uploading}
                    className="p-3 text-left border border-gray-200 hover:border-brand-400 hover:bg-blue-50/40 rounded-xl transition space-y-1"
                  >
                    <p className="text-xs font-bold text-gray-900">Healthcare Patients</p>
                    <p className="text-xs text-gray-600 font-medium">Clinical · 90 rows</p>
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
