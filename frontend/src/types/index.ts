export interface User {
  id: number;
  email: string;
  full_name: string;
  is_active: boolean;
  created_at: string;
}

export interface Dataset {
  id: number;
  name: string;
  file_format: string;
  file_size_bytes: number;
  row_count: number;
  column_count: number;
  quality_score: number;
  created_at?: string;
  preview?: any[];
}

export interface ColumnMeta {
  name: string;
  type: string;
  raw_dtype: string;
  null_count: number;
  null_percentage: number;
  unique_count: number;
  is_sensitive: boolean;
  sample_values: any[];
}

export interface DatasetProfile {
  dataset_id: number;
  name: string;
  row_count: number;
  column_count: number;
  columns: ColumnMeta[];
  numerical_columns: string[];
  categorical_columns: string[];
  datetime_columns: string[];
  text_columns: string[];
  missing_values: Record<string, { count: number; percentage: number }>;
  duplicate_rows: number;
  quality_score: number;
  sensitive_columns: Array<{ column: string; reason: string; risk_level: string }>;
  summary_statistics: Record<string, any>;
  sample_preview: any[];
}

export interface AgentTraceStep {
  agent: string;
  status: string;
  message: string;
  duration_ms: number;
}

export interface AnalysisResponse {
  query_id: number;
  conversation_id: number;
  schema: {
    user_question: string;
    detected_intent: string;
    target_columns: string[];
    group_by: string[];
    aggregation?: string;
    language?: string;
  };
  plan: {
    steps: string[];
    compute_engine: string;
  };
  result_data: any[];
  summary_kpis: Record<string, any>;
  row_count: number;
  execution_time_ms: number;
  validation: {
    is_valid: boolean;
    integrity_checks: Array<{ check: string; passed: boolean; detail: string }>;
    privacy_log: Array<{ column: string; action: string; rule: string }>;
    privacy_warning?: string;
  };
  visualization: {
    chart_type: string;
    x_axis: string;
    y_axis: string;
    title: string;
    alternatives: string[];
    data: any[];
  };
  dashboards: {
    active_design: string;
    designs: Array<{
      id: string;
      name: string;
      description: string;
      components: any[];
    }>;
  };
  explanation: {
    short_answer: string;
    key_insights: string[];
    observations: string[];
    limitations?: string;
  };
  agent_trace: AgentTraceStep[];
}

export interface Dashboard {
  id: number;
  dataset_id: number;
  dataset_name: string;
  title: string;
  description?: string;
  theme: string;
  layout_type: string;
  components: any[];
  created_at: string;
  updated_at: string;
}
