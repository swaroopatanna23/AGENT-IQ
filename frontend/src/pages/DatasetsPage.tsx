import React, { useState, useEffect } from "react";
import { Navbar, Sidebar } from "../components/layout/Navigation";
import { Dataset, DatasetProfile } from "../types";
import { datasetApi, exportApi } from "../api/client";
import { 
  FileSpreadsheet, 
  Upload, 
  Trash2, 
  Download, 
  Eye, 
  CheckCircle, 
  AlertTriangle, 
  ShieldAlert, 
  Search,
  Plus
} from "lucide-react";

export const DatasetsPage: React.FC = () => {
  const [datasets, setDatasets] = useState<Dataset[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [selectedProfile, setSelectedProfile] = useState<DatasetProfile | null>(null);
  const [loadingProfile, setLoadingProfile] = useState(false);

  useEffect(() => {
    fetchDatasets();
  }, []);

  const fetchDatasets = async () => {
    try {
      const res = await datasetApi.list();
      setDatasets(res.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm("Are you sure you want to delete this dataset?")) return;
    try {
      await datasetApi.delete(id);
      fetchDatasets();
    } catch (err) {
      alert("Failed to delete dataset");
    }
  };

  const handleViewProfile = async (id: number) => {
    setLoadingProfile(true);
    try {
      const res = await datasetApi.getProfile(id);
      setSelectedProfile(res.data);
    } catch {
      alert("Failed to fetch profile");
    } finally {
      setLoadingProfile(false);
    }
  };

  const filtered = datasets.filter((d) =>
    d.name.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      <Navbar />

      <div className="flex flex-1">
        <Sidebar />

        <main className="flex-1 p-8 max-w-6xl mx-auto space-y-6">
          <div className="flex items-center justify-between">
            <div className="space-y-1">
              <h1 className="text-2xl font-extrabold text-gray-900 tracking-tight">Dataset Catalog</h1>
              <p className="text-xs text-gray-700 font-medium">Manage uploaded datasets, inspect data schemas, and examine quality scores.</p>
            </div>

            <div className="flex items-center gap-3">
              <div className="relative">
                <Search className="w-4 h-4 text-gray-600 absolute left-3 top-3" />
                <input
                  type="text"
                  value={search}
                  onChange={(e) => setSearch(e.target.value)}
                  placeholder="Search datasets..."
                  className="pl-9 pr-4 py-2 bg-white border border-gray-300 rounded-xl text-xs text-gray-900 placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-brand-500 w-64 font-medium"
                />
              </div>
            </div>
          </div>

          {/* Dataset Cards Grid */}
          {loading ? (
            <div className="p-12 text-center text-xs text-gray-700 font-medium">Loading datasets...</div>
          ) : filtered.length === 0 ? (
            <div className="bg-white border border-gray-200 rounded-2xl p-12 text-center space-y-3">
              <FileSpreadsheet className="w-10 h-10 text-gray-400 mx-auto" />
              <p className="text-sm font-bold text-gray-800">No datasets found</p>
              <p className="text-xs text-gray-700 font-medium">Attach or upload your first dataset in the AI Studio.</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {filtered.map((d) => (
                <div key={d.id} className="bg-white border border-gray-200 rounded-2xl p-5 shadow-2xs space-y-4 hover:shadow-sm transition">
                  <div className="flex items-start justify-between">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 rounded-xl bg-blue-50 border border-blue-200 text-brand-600 flex items-center justify-center font-bold text-xs uppercase">
                        {d.file_format}
                      </div>
                      <div>
                        <h3 className="text-sm font-bold text-gray-900 truncate max-w-[180px]">{d.name}</h3>
                        <p className="text-xs text-gray-700 font-medium">{(d.file_size_bytes / 1024).toFixed(1)} KB</p>
                      </div>
                    </div>

                    <span className="text-xs font-semibold px-2 py-0.5 rounded-full bg-emerald-50 text-emerald-700 border border-emerald-200 flex items-center gap-1">
                      <CheckCircle className="w-3 h-3" />
                      {d.quality_score}% Quality
                    </span>
                  </div>

                  <div className="grid grid-cols-2 gap-2 text-xs bg-gray-50 border border-gray-200 p-2.5 rounded-xl">
                    <div>
                      <span className="text-gray-700 text-xs uppercase font-bold">Rows</span>
                      <p className="font-extrabold text-gray-900 text-sm">{d.row_count}</p>
                    </div>
                    <div>
                      <span className="text-gray-700 text-xs uppercase font-bold">Columns</span>
                      <p className="font-extrabold text-gray-900 text-sm">{d.column_count}</p>
                    </div>
                  </div>

                  <div className="flex items-center justify-between pt-2 border-t border-gray-100">
                    <button
                      onClick={() => handleViewProfile(d.id)}
                      className="text-xs font-bold text-brand-700 hover:text-brand-800 flex items-center gap-1.5"
                    >
                      <Eye className="w-3.5 h-3.5" />
                      Inspect Profile
                    </button>

                    <div className="flex items-center gap-1">
                      <a
                        href={exportApi.downloadCsvUrl(d.id)}
                        download
                        className="p-2 text-gray-700 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition"
                        title="Download CSV"
                      >
                        <Download className="w-3.5 h-3.5" />
                      </a>
                      <button
                        onClick={() => handleDelete(d.id)}
                        className="p-2 text-gray-700 hover:text-red-600 hover:bg-red-50 rounded-lg transition"
                        title="Delete"
                      >
                        <Trash2 className="w-3.5 h-3.5" />
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Profile Inspection Drawer / Modal */}
          {selectedProfile && (
            <div className="fixed inset-0 bg-black/40 backdrop-blur-xs flex items-center justify-center z-50 p-4">
              <div className="bg-white rounded-2xl max-w-3xl w-full p-6 shadow-xl max-h-[85vh] overflow-y-auto space-y-6">
                <div className="flex items-center justify-between pb-3 border-b border-gray-100">
                  <div>
                    <h3 className="text-base font-bold text-gray-900">Dataset Profile: {selectedProfile.name}</h3>
                    <p className="text-xs text-gray-700 font-medium">
                      {selectedProfile.row_count} Rows · {selectedProfile.column_count} Columns · Quality Score: {selectedProfile.quality_score}%
                    </p>
                  </div>
                  <button onClick={() => setSelectedProfile(null)} className="text-gray-600 hover:text-gray-900 font-bold">
                    ✕
                  </button>
                </div>

                {/* Sensitive Columns Notice */}
                {selectedProfile.sensitive_columns?.length > 0 && (
                  <div className="bg-amber-50 border border-amber-200 text-amber-900 text-xs px-4 py-3 rounded-xl space-y-1">
                    <p className="font-bold flex items-center gap-1.5">
                      <ShieldAlert className="w-4 h-4 text-amber-600" />
                      Detected Sensitive Attributes ({selectedProfile.sensitive_columns.length})
                    </p>
                    <ul className="list-disc list-inside text-xs text-amber-800 font-medium">
                      {selectedProfile.sensitive_columns.map((s, i) => (
                        <li key={i}>
                          <b>{s.column}:</b> {s.reason} ({s.risk_level} Risk)
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {/* Column Table */}
                <div>
                  <h4 className="text-xs font-bold text-gray-900 uppercase tracking-wider mb-2">Column Breakdown</h4>
                  <div className="border border-gray-200 rounded-xl overflow-hidden max-h-60 overflow-y-auto">
                    <table className="w-full text-left text-xs">
                      <thead className="bg-gray-100 text-gray-900 font-bold border-b border-gray-200">
                        <tr>
                          <th className="px-3.5 py-2">Column</th>
                          <th className="px-3.5 py-2">Inferred Type</th>
                          <th className="px-3.5 py-2">Nulls</th>
                          <th className="px-3.5 py-2">Unique</th>
                          <th className="px-3.5 py-2">Samples</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-gray-200">
                        {selectedProfile.columns?.map((c) => (
                          <tr key={c.name} className="hover:bg-blue-50/40">
                            <td className="px-3.5 py-2 font-bold text-gray-900">{c.name}</td>
                            <td className="px-3.5 py-2">
                              <span className="px-2 py-0.5 rounded-md bg-gray-200 text-gray-900 text-[11px] font-mono font-bold capitalize">
                                {c.type}
                              </span>
                            </td>
                            <td className="px-3.5 py-2 text-gray-800 font-medium">{c.null_count} ({c.null_percentage}%)</td>
                            <td className="px-3.5 py-2 text-gray-800 font-medium">{c.unique_count}</td>
                            <td className="px-3.5 py-2 text-gray-700 font-mono text-xs truncate max-w-[200px]">
                              {c.sample_values?.join(", ")}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>

                {/* Data Preview */}
                {selectedProfile.sample_preview?.length > 0 && (
                  <div>
                    <h4 className="text-xs font-bold text-gray-800 uppercase tracking-wider mb-2">Data Sample (First 10 Rows)</h4>
                    <div className="border border-gray-200 rounded-xl overflow-x-auto max-h-48 overflow-y-auto">
                      <table className="w-full text-left text-xs">
                        <thead className="bg-gray-50 text-gray-600 font-semibold border-b border-gray-200">
                          <tr>
                            {Object.keys(selectedProfile.sample_preview[0] || {}).map((k) => (
                              <th key={k} className="px-3 py-1.5 whitespace-nowrap">{k}</th>
                            ))}
                          </tr>
                        </thead>
                        <tbody className="divide-y divide-gray-100">
                          {selectedProfile.sample_preview.map((row, idx) => (
                            <tr key={idx}>
                              {Object.keys(row).map((k) => (
                                <td key={k} className="px-3 py-1.5 whitespace-nowrap text-gray-600">{String(row[k])}</td>
                              ))}
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}
        </main>
      </div>
    </div>
  );
};
