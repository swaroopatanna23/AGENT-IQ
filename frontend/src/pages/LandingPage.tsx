import React from "react";
import { Link } from "react-router-dom";
import { 
  Bot, 
  Sparkles, 
  ArrowRight, 
  Database, 
  ShieldCheck, 
  Layers, 
  FileSpreadsheet, 
  Cpu, 
  CheckCircle, 
  Network 
} from "lucide-react";

export const LandingPage: React.FC = () => {
  return (
    <div className="min-h-screen bg-gradient-to-b from-blue-50/50 via-white to-gray-50 flex flex-col justify-between">
      {/* Top Banner / Navbar */}
      <header className="max-w-7xl mx-auto w-full px-6 py-6 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-brand-600 text-white flex items-center justify-center shadow-md">
            <Bot className="w-6 h-6" />
          </div>
          <div>
            <span className="text-gray-900 font-extrabold text-2xl tracking-tight">Agent<span className="text-brand-600">IQ</span></span>
            <span className="ml-2 text-xs font-semibold px-2.5 py-0.5 rounded-full bg-blue-100 text-blue-800">
              Batch 08
            </span>
          </div>
        </div>

        <div className="flex items-center gap-4">
          <Link to="/architecture" className="text-sm font-semibold text-gray-600 hover:text-brand-600 transition">
            Architecture
          </Link>
          <Link to="/login" className="text-sm font-semibold text-gray-700 hover:text-brand-600 px-4 py-2 transition">
            Sign In
          </Link>
          <Link 
            to="/workspace" 
            className="text-sm font-semibold text-white bg-brand-600 hover:bg-brand-700 px-5 py-2.5 rounded-xl shadow-sm transition flex items-center gap-2"
          >
            Launch Studio
            <ArrowRight className="w-4 h-4" />
          </Link>
        </div>
      </header>

      {/* Hero Section (Faithfully matching Slide 11) */}
      <main className="max-w-5xl mx-auto px-6 py-16 text-center space-y-8">
        <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-blue-50 border border-blue-200 text-blue-700 text-xs font-bold tracking-wide uppercase shadow-2xs">
          <Sparkles className="w-3.5 h-3.5" />
          Multilingual & Heterogeneous Data Intelligence
        </div>

        <h1 className="text-5xl sm:text-6xl font-black text-gray-900 tracking-tight leading-tight">
          AgentIQ
          <span className="block text-3xl sm:text-4xl font-extrabold text-brand-600 mt-2">
            Domain-Agnostic AI Analytics
          </span>
        </h1>

        <p className="max-w-2xl mx-auto text-lg text-gray-600 font-normal leading-relaxed">
          Analyze heterogeneous data using natural-language queries and generate meaningful interactive insights.
        </p>

        <div className="flex items-center justify-center gap-4 pt-2">
          <Link
            to="/workspace"
            className="bg-brand-600 hover:bg-brand-700 text-white font-bold text-base px-8 py-3.5 rounded-xl shadow-md hover:shadow-lg transition flex items-center gap-2.5"
          >
            Get Started
            <ArrowRight className="w-5 h-5" />
          </Link>
          <Link
            to="/architecture"
            className="bg-white hover:bg-gray-50 text-gray-800 border border-gray-300 font-semibold text-base px-6 py-3.5 rounded-xl shadow-2xs transition flex items-center gap-2"
          >
            <Network className="w-5 h-5 text-gray-500" />
            System Design
          </Link>
        </div>

        {/* Feature Cards 01 & 02 (Directly from Slide 11) */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 pt-12 text-left">
          <div className="bg-white border border-gray-200/80 rounded-2xl p-6 shadow-sm hover:shadow-md transition space-y-3">
            <span className="text-xs font-black text-brand-600 uppercase tracking-widest">01</span>
            <h3 className="text-lg font-bold text-gray-900">Domain-Agnostic Analytics</h3>
            <p className="text-sm text-gray-600 leading-relaxed">
              Designed to work across diverse datasets and data sources without requiring domain-specific configuration. Supports Education, Healthcare, Business, and Sales.
            </p>
          </div>

          <div className="bg-white border border-gray-200/80 rounded-2xl p-6 shadow-sm hover:shadow-md transition space-y-3">
            <span className="text-xs font-black text-brand-600 uppercase tracking-widest">02</span>
            <h3 className="text-lg font-bold text-gray-900">Heterogeneous Data Sources</h3>
            <p className="text-sm text-gray-600 leading-relaxed">
              Connect files, spreadsheets, and databases through a unified data input layer for analysis. Accepts CSV, Excel, JSON, Google Sheets, MySQL, PostgreSQL, and MongoDB.
            </p>
          </div>
        </div>

        {/* Academic Project Credits */}
        <div className="pt-8 border-t border-gray-200 text-xs text-gray-500 space-y-1">
          <p className="font-semibold text-gray-700">Major Project • Department of Data Engineering • CSE-Data Science • Regulation R23</p>
          <p>Project Title: AgentIQ: An AI Framework for Universal File Analysis and Interactive Dashboard Generation over Data</p>
          <p className="text-gray-400">Batch 08: Tanna Swaroopa, Chevvuri Devi Amrutha, Sakala Yezna Priya, Pentapati Ratna Sravani</p>
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t border-gray-200 py-6 text-center text-xs text-gray-400">
        © 2026 AgentIQ Academic Project. All rights reserved.
      </footer>
    </div>
  );
};
