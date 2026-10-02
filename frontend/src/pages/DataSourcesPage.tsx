import React, { useState, useEffect } from "react";
import { Navbar, Sidebar } from "../components/layout/Navigation";
import { dataSourceApi } from "../api/client";
import { 
  Database, 
  Table, 
  FileSpreadsheet, 
  FileCode, 
  Boxes, 
  CheckCircle2, 
  AlertCircle, 
  ExternalLink,
  RefreshCw,
  X
} from "lucide-react";

export const DataSourcesPage: React.FC = () => {
  const [connectors, setConnectors] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedConnector, setSelectedConnector] = useState<any>(null);
  const [configInput, setConfigInput] = useState<any>({});
  const [testResult, setTestResult] = useState<any>(null);
  const [testing, setTesting] = useState(false);

  useEffect(() => {
    fetchConnectors();
  }, []);

  const fetchConnectors = async () => {
    try {
      const res = await dataSourceApi.list();
      setConnectors(res.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const getIcon = (iconName: string) => {
    switch (iconName) {
      case "FileSpreadsheet": return <FileSpreadsheet className="w-5 h-5 text-emerald-600" />;
      case "FileCode": return <FileCode className="w-5 h-5 text-amber-600" />;
      case "Table": return <Table className="w-5 h-5 text-blue-600" />;
      case "Database": return <Database className="w-5 h-5 text-brand-600" />;
      case "Boxes": return <Boxes className="w-5 h-5 text-purple-600" />;
      default: return <Database className="w-5 h-5 text-gray-500" />;
    }
  };

  const handleTestConnection = async () => {
    setTesting(true);
    setTestResult(null);
    try {
      const res = await dataSourceApi.test(selectedConnector.id, configInput);
      setTestResult(res.data);
    } catch (err: any) {
      setTestResult({ valid: false, message: err.response?.data?.detail || "Connection test failed." });
    } finally {
      setTesting(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      <Navbar />

      <div className="flex flex-1">
        <Sidebar />

        <main className="flex-1 p-8 max-w-6xl mx-auto space-y-6">
          <div className="space-y-1">
            <h1 className="text-2xl font-extrabold text-gray-900 tracking-tight">Data Source Connectors</h1>
            <p className="text-xs text-gray-500">
              Unified DataSourceConnector abstraction supporting heterogeneous sources (Batch-08 Slide 7).
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {connectors.map((c) => (
              <div 
                key={c.id} 
                className="bg-white border border-gray-200 rounded-2xl p-5 shadow-2xs space-y-4 flex flex-col justify-between"
              >
                <div className="space-y-3">
                  <div className="flex items-start justify-between">
                    <div className="w-10 h-10 rounded-xl bg-gray-50 border border-gray-200 flex items-center justify-center">
                      {getIcon(c.icon)}
                    </div>
                    <span className={`text-[11px] font-bold px-2 py-0.5 rounded-full uppercase tracking-wider ${
                      c.status === "available" ? "bg-emerald-50 text-emerald-700 border border-emerald-200" :
                      c.status === "configured" ? "bg-blue-50 text-blue-700 border border-blue-200" :
                      "bg-gray-100 text-gray-600"
                    }`}>
                      {c.status}
                    </span>
                  </div>

                  <div>
                    <h3 className="text-sm font-bold text-gray-900">{c.name}</h3>
                    <p className="text-[11px] text-gray-400 font-semibold uppercase">{c.category}</p>
                    <p className="text-xs text-gray-600 mt-2 leading-relaxed">{c.description}</p>
                  </div>
                </div>

                <div className="pt-3 border-t border-gray-100">
                  <button
                    onClick={() => {
                      setSelectedConnector(c);
                      setConfigInput({});
                      setTestResult(null);
                    }}
                    className="w-full text-xs font-semibold text-brand-600 hover:text-brand-700 bg-brand-50/60 hover:bg-brand-100/60 py-2 rounded-xl transition"
                  >
                    Configure & Test
                  </button>
                </div>
              </div>
            ))}
          </div>

          {/* Test Modal */}
          {selectedConnector && (
            <div className="fixed inset-0 bg-black/40 backdrop-blur-xs flex items-center justify-center z-50 p-4">
              <div className="bg-white rounded-2xl max-w-md w-full p-6 shadow-xl space-y-4">
                <div className="flex items-center justify-between pb-2 border-b border-gray-100">
                  <h3 className="text-sm font-bold text-gray-900">
                    Configure {selectedConnector.name}
                  </h3>
                  <button onClick={() => setSelectedConnector(null)} className="text-gray-400 hover:text-gray-600 font-bold">
                    ✕
                  </button>
                </div>

                <div className="space-y-3 text-xs">
                  {selectedConnector.id === "google_sheets" && (
                    <div>
                      <label className="block font-semibold text-gray-700 mb-1">Google Sheets Public URL</label>
                      <input
                        type="text"
                        placeholder="https://docs.google.com/spreadsheets/d/.../edit"
                        onChange={(e) => setConfigInput({ url: e.target.value })}
                        className="w-full p-2.5 border border-gray-200 rounded-xl"
                      />
                    </div>
                  )}

                  {["postgresql", "mysql"].includes(selectedConnector.id) && (
                    <div>
                      <label className="block font-semibold text-gray-700 mb-1">Database Connection URI</label>
                      <input
                        type="text"
                        placeholder={`${selectedConnector.id}://user:password@localhost:5432/dbname`}
                        onChange={(e) => setConfigInput({ connection_uri: e.target.value })}
                        className="w-full p-2.5 border border-gray-200 rounded-xl"
                      />
                    </div>
                  )}

                  {selectedConnector.id === "mongodb" && (
                    <div>
                      <label className="block font-semibold text-gray-700 mb-1">MongoDB Connection URI</label>
                      <input
                        type="text"
                        placeholder="mongodb://localhost:27017"
                        onChange={(e) => setConfigInput({ uri: e.target.value, database: "agentiq", collection: "data" })}
                        className="w-full p-2.5 border border-gray-200 rounded-xl"
                      />
                    </div>
                  )}

                  {["csv", "excel", "json"].includes(selectedConnector.id) && (
                    <div className="bg-blue-50 border border-blue-200 p-3 rounded-xl text-blue-900 leading-relaxed">
                      File format native parser active. Upload directly via the <b>AI Studio</b> workspace or the <b>Datasets</b> tab.
                    </div>
                  )}

                  {testResult && (
                    <div className={`p-3 rounded-xl border text-xs ${
                      testResult.valid 
                        ? "bg-emerald-50 border-emerald-200 text-emerald-800" 
                        : "bg-red-50 border-red-200 text-red-800"
                    }`}>
                      <p className="font-bold">{testResult.valid ? "Validation Successful" : "Validation Failed"}</p>
                      <p className="text-[11px] mt-0.5">{testResult.message}</p>
                    </div>
                  )}

                  {!["csv", "excel", "json"].includes(selectedConnector.id) && (
                    <button
                      onClick={handleTestConnection}
                      disabled={testing}
                      className="w-full bg-brand-600 hover:bg-brand-700 text-white font-semibold py-2.5 rounded-xl transition mt-2 disabled:opacity-50"
                    >
                      {testing ? "Testing Connection..." : "Validate Connection"}
                    </button>
                  )}
                </div>
              </div>
            </div>
          )}
        </main>
      </div>
    </div>
  );
};
