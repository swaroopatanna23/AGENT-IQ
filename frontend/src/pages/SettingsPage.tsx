import React, { useState } from "react";
import { Navbar, Sidebar } from "../components/layout/Navigation";
import { useAuth } from "../context/AuthContext";
import { Settings as SettingsIcon, Key, Database, Shield, Bot, CheckCircle } from "lucide-react";

export const SettingsPage: React.FC = () => {
  const { user } = useAuth();
  const [apiKey, setApiKey] = useState("");
  const [saved, setSaved] = useState(false);

  const handleSaveApiKey = () => {
    if (apiKey) {
      localStorage.setItem("agentiq_gemini_key", apiKey);
      setSaved(true);
      setTimeout(() => setSaved(false), 2500);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      <Navbar />

      <div className="flex flex-1">
        <Sidebar />

        <main className="flex-1 p-8 max-w-4xl mx-auto space-y-6">
          <div className="space-y-1">
            <h1 className="text-2xl font-extrabold text-gray-900 tracking-tight">Platform Settings</h1>
            <p className="text-xs text-gray-500">Configure AI keys, storage paths, and view environment telemetry.</p>
          </div>

          {/* Account Profile Card */}
          <div className="bg-white border border-gray-200 rounded-2xl p-6 shadow-2xs space-y-4">
            <h3 className="text-sm font-bold text-gray-900 flex items-center gap-2">
              <Shield className="w-4 h-4 text-brand-600" />
              Researcher Profile
            </h3>

            <div className="grid grid-cols-2 gap-4 text-xs">
              <div>
                <span className="text-gray-400 uppercase font-semibold text-[10px]">Full Name</span>
                <p className="font-bold text-gray-900 text-sm mt-0.5">{user?.full_name || "AgentIQ Researcher"}</p>
              </div>
              <div>
                <span className="text-gray-400 uppercase font-semibold text-[10px]">Email Address</span>
                <p className="font-bold text-gray-900 text-sm mt-0.5">{user?.email || "demo@agentiq.ai"}</p>
              </div>
            </div>
          </div>

          {/* AI Settings */}
          <div className="bg-white border border-gray-200 rounded-2xl p-6 shadow-2xs space-y-4">
            <h3 className="text-sm font-bold text-gray-900 flex items-center gap-2">
              <Key className="w-4 h-4 text-purple-600" />
              Google GenAI (Gemini) Key Configuration
            </h3>

            <p className="text-xs text-gray-600 leading-relaxed">
              AgentIQ uses Google Gemini 2.5 Flash for natural language parsing and explanation generation.
              When an API key is not supplied, the built-in deterministic <b>TF-IDF + LinearSVC</b> baseline engine operates seamlessly.
            </p>

            <div className="space-y-2">
              <label className="block text-xs font-semibold text-gray-700">GEMINI_API_KEY</label>
              <div className="flex gap-2">
                <input
                  type="password"
                  value={apiKey}
                  onChange={(e) => setApiKey(e.target.value)}
                  placeholder="AIzaSy..."
                  className="flex-1 px-3.5 py-2.5 border border-gray-200 rounded-xl text-xs focus:ring-2 focus:ring-brand-500 outline-none"
                />
                <button
                  onClick={handleSaveApiKey}
                  className="bg-brand-600 hover:bg-brand-700 text-white font-semibold text-xs px-4 py-2.5 rounded-xl transition shadow-2xs"
                >
                  Save Key
                </button>
              </div>
              {saved && (
                <p className="text-xs text-emerald-600 font-semibold flex items-center gap-1">
                  <CheckCircle className="w-3.5 h-3.5" />
                  API key saved to browser session
                </p>
              )}
            </div>
          </div>

          {/* System Specs */}
          <div className="bg-white border border-gray-200 rounded-2xl p-6 shadow-2xs space-y-4">
            <h3 className="text-sm font-bold text-gray-900 flex items-center gap-2">
              <Bot className="w-4 h-4 text-emerald-600" />
              System Information
            </h3>

            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
              <div className="bg-gray-50 p-3 rounded-xl">
                <span className="text-gray-400 text-[10px] uppercase font-semibold">Backend</span>
                <p className="font-bold text-gray-900 mt-1">FastAPI 0.115</p>
              </div>
              <div className="bg-gray-50 p-3 rounded-xl">
                <span className="text-gray-400 text-[10px] uppercase font-semibold">Database</span>
                <p className="font-bold text-gray-900 mt-1">SQLAlchemy ORM</p>
              </div>
              <div className="bg-gray-50 p-3 rounded-xl">
                <span className="text-gray-400 text-[10px] uppercase font-semibold">Compute Engine</span>
                <p className="font-bold text-gray-900 mt-1">Pandas & NumPy</p>
              </div>
              <div className="bg-gray-50 p-3 rounded-xl">
                <span className="text-gray-400 text-[10px] uppercase font-semibold">Academic Batch</span>
                <p className="font-bold text-gray-900 mt-1">Batch 08 (R23)</p>
              </div>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
};
