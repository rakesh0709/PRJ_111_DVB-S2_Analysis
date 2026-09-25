export type StreamFormat = 'MPEG_TS' | 'GSE' | 'BB_FRAME' | 'UNKNOWN' | 'AUTO';

export interface Priority1Check {
  name: string;
  status: 'PASS' | 'FAIL';
  details: string;
}

export interface F1HealthSummary {
  overall_health_score: number;
  health_classification: string;
  integrity_ratio: number;
  valid_units: number;
  invalid_units: number;
  total_errors: number;
  priority_1_checks: Priority1Check[];
}

export interface AnomalousWindow {
  window_index: number;
  score: number;
  severity: string;
  unit_range: [number, number];
  byte_range: [number, number];
  top_deviations: Record<string, any>;
  explanation: string;
}

export interface F2AnomalySummary {
  total_windows: number;
  anomaly_window_count: number;
  anomaly_rate_pct: number;
  peak_anomaly_score: number;
  decision_threshold: number;
  anomalous_windows: AnomalousWindow[];
}

export interface F3PatternSummary {
  dominant_component: string;
  active_components: string;
  entropy: string;
  transition_count: number;
  transitions: Array<{ window: number; desc: string }>;
}

export interface TimelinePoint {
  window_index: number;
  unit_offset_start: number;
  unit_offset_end: number;
  byte_offset_start: number;
  byte_offset_end: number;
  unit_count: number;
  payload_bytes: number;
  valid_units: number;
  invalid_units: number;
  error_count: number;
  health_score: number;
  anomaly_score: number;
  is_anomaly: boolean;
  anomaly_severity: string;
  anomaly_explanation: string;
  format_specific_metrics: Record<string, any>;
  has_transition?: boolean;
  transition_description?: string;
}

export interface TimelineData {
  stream_name: string;
  format: StreamFormat;
  total_units: number;
  total_bytes: number;
  window_size: number;
  total_windows: number;
  anomaly_threshold: number;
  points: TimelinePoint[];
  events?: any[];
  summary_stats?: {
    mean_health_score: number;
    peak_anomaly_score: number;
    anomaly_window_count: number;
  };
}

export interface StreamInfo {
  file_name: string;
  file_path: string;
  file_size_bytes: number;
  file_size_kb: number;
  detected_format: StreamFormat;
  total_units: number;
  total_payload_bytes: number;
  total_payload_kb: number;
  window_size: number;
  total_windows: number;
}

export interface AnalysisResponse {
  success: boolean;
  stream_info: StreamInfo;
  f1_health: F1HealthSummary;
  f2_anomalies: F2AnomalySummary;
  f3_patterns: F3PatternSummary;
  f4_timeline: TimelineData;
  f5_explanations: Record<string, any>;
  f7_report: Record<string, any>;
  report_renders?: {
    markdown?: string;
    text?: string;
    html?: string;
  };
}

export interface PresetDataset {
  id: string;
  label: string;
  format: StreamFormat;
  relative_path: string;
  absolute_path: string;
  file_size_bytes: number;
  default_window_size: number;
  description: string;
}

export interface BackendStatus {
  status: 'ONLINE' | 'OFFLINE';
  milestone?: string;
  backend_status?: string;
  test_suite?: string;
  supported_formats?: string[];
  active_guards?: string[];
}
