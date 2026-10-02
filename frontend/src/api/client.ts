import axios from "axios";

export const API_BASE_URL = "http://127.0.0.1:8000";

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

// Attach JWT token automatically if logged in
api.interceptors.request.use((config) => {
  const token = localStorage.getItem("agentiq_token");
  if (token && config.headers) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Authentication APIs
export const authApi = {
  register: (data: { email: string; password: string; full_name: string }) =>
    api.post("/api/v1/auth/register", data),
  login: (data: { email: string; password: string }) =>
    api.post("/api/v1/auth/login", data),
  getMe: () => api.get("/api/v1/auth/me"),
};

// Dataset APIs
export const datasetApi = {
  list: () => api.get("/api/v1/datasets"),
  get: (id: number) => api.get(`/api/v1/datasets/${id}`),
  getProfile: (id: number) => api.get(`/api/v1/datasets/${id}/profile`),
  upload: (file: File) => {
    const formData = new FormData();
    formData.append("file", file);
    return api.post("/api/v1/datasets/upload", formData, {
      headers: { "Content-Type": "multipart/form-data" },
    });
  },
  loadSample: (sampleName: string) =>
    api.post(`/api/v1/datasets/load-sample/${sampleName}`),
  delete: (id: number) => api.delete(`/api/v1/datasets/${id}`),
};

// Analysis APIs
export const analysisApi = {
  query: (data: { dataset_id: number; question: string; conversation_id?: number; language?: string }) =>
    api.post("/api/v1/analysis/query", data),
  getSuggestedQuestions: (datasetId: number) =>
    api.get(`/api/v1/analysis/suggested-questions/${datasetId}`),
  getHistory: (datasetId?: number) =>
    api.get("/api/v1/analysis/history", { params: { dataset_id: datasetId } }),
};

// Dashboard APIs
export const dashboardApi = {
  list: () => api.get("/api/v1/dashboards"),
  get: (id: number) => api.get(`/api/v1/dashboards/${id}`),
  create: (data: any) => api.post("/api/v1/dashboards", data),
  update: (id: number, data: any) => api.put(`/api/v1/dashboards/${id}`, data),
  delete: (id: number) => api.delete(`/api/v1/dashboards/${id}`),
};

// Data Source Connector APIs
export const dataSourceApi = {
  list: () => api.get("/api/v1/data-sources"),
  test: (source_type: string, config: any) =>
    api.post("/api/v1/data-sources/test", { source_type, config }),
};

// Export APIs
export const exportApi = {
  downloadCsvUrl: (datasetId: number) =>
    `${API_BASE_URL}/api/v1/export/csv/${datasetId}`,
  downloadPdfReport: (data: any) =>
    api.post("/api/v1/export/pdf", data, { responseType: "blob" }),
};

export default api;
