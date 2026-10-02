import React from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { AuthProvider } from "./context/AuthContext";
import { LandingPage } from "./pages/LandingPage";
import { LoginPage, RegisterPage } from "./pages/AuthPages";
import { OverviewPage } from "./pages/OverviewPage";
import { WorkspacePage } from "./pages/WorkspacePage";
import { DatasetsPage } from "./pages/DatasetsPage";
import { DashboardsPage } from "./pages/DashboardsPage";
import { DataSourcesPage } from "./pages/DataSourcesPage";
import { HistoryPage } from "./pages/HistoryPage";
import { SettingsPage } from "./pages/SettingsPage";
import { ArchitecturePage } from "./pages/ArchitecturePage";

export const App: React.FC = () => {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          <Route path="/" element={<LandingPage />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
          <Route path="/overview" element={<OverviewPage />} />
          <Route path="/workspace" element={<WorkspacePage />} />
          <Route path="/datasets" element={<DatasetsPage />} />
          <Route path="/dashboards" element={<DashboardsPage />} />
          <Route path="/data-sources" element={<DataSourcesPage />} />
          <Route path="/history" element={<HistoryPage />} />
          <Route path="/settings" element={<SettingsPage />} />
          <Route path="/architecture" element={<ArchitecturePage />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  );
};

export default App;
