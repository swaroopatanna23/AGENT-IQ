import React from "react";
import { Link, useNavigate, useLocation } from "react-router-dom";
import { useAuth } from "../../context/AuthContext";
import { 
  Bot, 
  LayoutDashboard, 
  FileSpreadsheet, 
  Sparkles, 
  History, 
  Network, 
  Settings, 
  LogOut, 
  PlusCircle,
  Database,
  Layers
} from "lucide-react";

export const Navbar: React.FC = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  return (
    <header className="h-16 border-b border-gray-200 bg-white sticky top-0 z-40 px-6 flex items-center justify-between">
      <div className="flex items-center gap-3">
        <Link to="/" className="flex items-center gap-2 text-brand-600 font-bold text-xl tracking-tight">
          <div className="w-9 h-9 rounded-lg bg-brand-600 text-white flex items-center justify-center shadow-sm">
            <Bot className="w-5 h-5" />
          </div>
          <span className="text-gray-900 font-extrabold text-lg">Agent<span className="text-brand-600">IQ</span></span>
          <span className="text-xs font-semibold px-2 py-0.5 rounded-full bg-blue-50 text-blue-700 border border-blue-200">
            Batch 08
          </span>
        </Link>
      </div>

      <div className="flex items-center gap-4">
        <Link 
          to="/architecture" 
          className="text-sm font-semibold text-gray-700 hover:text-brand-600 flex items-center gap-1.5 transition"
        >
          <Network className="w-4 h-4 text-gray-700" />
          How It Works
        </Link>
        <Link 
          to="/datasets" 
          className="text-sm font-semibold text-gray-700 hover:text-brand-600 transition"
        >
          Datasets
        </Link>
        <Link 
          to="/workspace" 
          className="text-sm font-semibold text-white bg-brand-600 hover:bg-brand-700 px-4 py-2 rounded-lg shadow-sm transition flex items-center gap-2"
        >
          <Sparkles className="w-4 h-4" />
          AI Studio
        </Link>

        {user ? (
          <div className="flex items-center gap-3 border-l pl-4 border-gray-200">
            <div className="text-right">
              <p className="text-xs font-bold text-gray-900 leading-tight">{user.full_name}</p>
              <p className="text-xs text-gray-700 font-medium leading-tight">{user.email}</p>
            </div>
            <button 
              onClick={logout}
              title="Sign Out"
              className="p-2 text-gray-700 hover:text-red-600 hover:bg-red-50 rounded-lg transition"
            >
              <LogOut className="w-4 h-4" />
            </button>
          </div>
        ) : (
          <div className="flex items-center gap-2 border-l pl-4 border-gray-200">
            <Link to="/login" className="text-sm font-semibold text-gray-800 hover:text-brand-600 px-3 py-1.5 transition">
              Sign In
            </Link>
            <Link to="/register" className="text-sm font-bold text-brand-700 bg-brand-50 hover:bg-brand-100 border border-brand-200 px-3 py-1.5 rounded-lg transition">
              Create Account
            </Link>
          </div>
        )}
      </div>
    </header>
  );
};

export const Sidebar: React.FC = () => {
  const location = useLocation();
  const navigate = useNavigate();

  const navItems = [
    { label: "Overview", path: "/overview", icon: LayoutDashboard },
    { label: "AI Analysis", path: "/workspace", icon: Sparkles },
    { label: "Datasets", path: "/datasets", icon: FileSpreadsheet },
    { label: "Dashboards", path: "/dashboards", icon: Layers },
    { label: "Data Sources", path: "/data-sources", icon: Database },
    { label: "Query History", path: "/history", icon: History },
    { label: "Architecture", path: "/architecture", icon: Network },
  ];

  return (
    <aside className="w-64 border-r border-gray-200 bg-white flex flex-col justify-between p-4 h-[calc(100vh-4rem)] sticky top-16 select-none">
      <div className="space-y-6">
        <button
          onClick={() => navigate("/workspace")}
          className="w-full bg-brand-600 hover:bg-brand-700 text-white font-bold py-2.5 px-4 rounded-xl shadow-sm flex items-center justify-center gap-2 transition"
        >
          <PlusCircle className="w-5 h-5" />
          <span>New Analysis</span>
        </button>

        <div className="space-y-1">
          <p className="text-xs font-bold tracking-wider text-gray-700 uppercase px-3 mb-2">
            Platform Menu
          </p>
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = location.pathname === item.path || location.pathname.startsWith(`${item.path}/`);
            return (
              <Link
                key={item.path}
                to={item.path}
                className={`flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-semibold transition ${
                  isActive
                    ? "bg-brand-50 text-brand-700 font-bold"
                    : "text-gray-700 hover:bg-gray-100 hover:text-gray-900"
                }`}
              >
                <Icon className={`w-4 h-4 ${isActive ? "text-brand-600" : "text-gray-600"}`} />
                {item.label}
              </Link>
            );
          })}
        </div>

        <div className="border-t border-gray-200 pt-4">
          <p className="text-xs font-bold tracking-wider text-gray-700 uppercase px-3 mb-2">
            RECENT SESSIONS (Slide 12)
          </p>
          <div className="space-y-1">
            <Link to="/workspace" className="block text-xs font-medium text-gray-700 hover:text-brand-700 hover:bg-gray-100 px-3 py-1.5 rounded-lg truncate">
              • Online Retail Analysis
            </Link>
            <Link to="/workspace" className="block text-xs font-medium text-gray-700 hover:text-brand-700 hover:bg-gray-100 px-3 py-1.5 rounded-lg truncate">
              • Student Performance
            </Link>
            <Link to="/workspace" className="block text-xs font-medium text-gray-700 hover:text-brand-700 hover:bg-gray-100 px-3 py-1.5 rounded-lg truncate">
              • Sales Analysis
            </Link>
          </div>
        </div>
      </div>

      <div className="border-t border-gray-200 pt-4 space-y-1">
        <Link
          to="/settings"
          className="flex items-center gap-3 px-3 py-2 rounded-xl text-sm font-semibold text-gray-700 hover:bg-gray-100 hover:text-gray-900 transition"
        >
          <Settings className="w-4 h-4 text-gray-600" />
          Settings
        </Link>
      </div>
    </aside>
  );
};
