import { OFFLINE_DATA } from "./offlineData";
import { AnalysisResponse, StreamFormat } from "./types";

export function getOfflineAnalysis(
  formatKey: "mpeg_ts" | "gse" | "bbframe"
): AnalysisResponse {
  const data = (OFFLINE_DATA as any)[formatKey];
  const pts = data.timeline?.points || [];
  const anomPts = pts.filter((p: any) => p.is_anomaly);

  return {
    success: true,
    stream_info: {
      file_name: data.file_name,
      file_path: data.relative_path,
      file_size_bytes: data.file_size_bytes,
      file_size_kb: Math.round(data.file_size_bytes / 1024),
      detected_format: data.format as StreamFormat,
      total_units: data.total_units,
      total_payload_bytes: data.total_payload_bytes,
      total_payload_kb: Math.round(data.total_payload_bytes / 1024),
      window_size: data.window_size,
      total_windows: data.total_windows,
    },
    f1_health: {
      overall_health_score: data.health_score,
      health_classification: data.health_classification,
      integrity_ratio: data.integrity_ratio,
      valid_units: data.total_units,
      invalid_units: 0,
      total_errors: 0,
      priority_1_checks: [
        {
          name:
            data.format === "MPEG_TS"
              ? "Sync Byte (0x47) Integrity"
              : data.format === "BB_FRAME"
              ? "BBHeader CRC-8 Checksum"
              : "GSE PDU Syntax Length",
          status: "PASS",
          details: data.sync_integrity,
        },
        {
          name:
            data.format === "MPEG_TS"
              ? "Transport Error Indicator (TEI)"
              : data.format === "BB_FRAME"
              ? "MATYPE Compatibility"
              : "S/E Framing Semantics",
          status: "PASS",
          details: "0 errors asserted",
        },
        {
          name:
            data.format === "MPEG_TS"
              ? "Continuity Counter (CC)"
              : data.format === "BB_FRAME"
              ? "Data Field Length (DFL) Bound"
              : "Protocol ID Classification",
          status: "PASS",
          details: "0 packet loss/drop discontinuities",
        },
      ],
    },
    f2_anomalies: {
      total_windows: data.total_windows,
      anomaly_window_count: data.anomaly_window_count,
      anomaly_rate_pct: (data.anomaly_window_count / data.total_windows) * 100,
      peak_anomaly_score: data.peak_anomaly_score,
      decision_threshold: data.decision_threshold,
      anomalous_windows: anomPts.map((p: any) => ({
        window_index: p.window_index,
        score: p.anomaly_score,
        severity: p.anomaly_severity || "ANOMALOUS",
        unit_range: [p.unit_offset_start, p.unit_offset_end],
        byte_range: [p.byte_offset_start, p.byte_offset_end],
        top_deviations: p.top_deviations || {
          framing_density: { z_score: 4.8, direction: "ABOVE_BASELINE", observed: 1.0, baseline: 0.8 },
        },
        explanation:
          p.anomaly_explanation ||
          `Window ${p.window_index} displays covariance divergence in feature space exceeding decision threshold &tau;=${data.decision_threshold}.`,
      })),
    },
    f3_patterns: {
      dominant_component: data.dominant_pattern,
      active_components: data.active_components,
      entropy: data.entropy,
      transition_count: 0,
      transitions: [],
    },
    f4_timeline: data.timeline,
    f5_explanations: data.explanations || {},
    f7_report: {
      tripartite_findings: data.report_findings || [],
    },
    report_renders: {
      markdown: `# PRJ_111 Analysis Report (${data.format})\n- File: ${data.file_name}\n- Integrity: 100.0%\n- Anomalies: ${data.anomaly_window_count}`,
      text: `PRJ_111 Analysis Report (${data.format})\nFile: ${data.file_name}\nIntegrity: 100.0%`,
      html: `<h1>PRJ_111 Analysis Report (${data.format})</h1><p>File: ${data.file_name}</p>`,
    },
  };
}
