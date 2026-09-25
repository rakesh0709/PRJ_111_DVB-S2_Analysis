"use client";

import React from "react";
import { OFFLINE_DATA } from "@/lib/offlineData";

export const TelemetryTable: React.FC = () => {
  const formats = [
    {
      format: "MPEG_TS",
      label: "MPEG-TS (Transport Stream)",
      file: OFFLINE_DATA.mpeg_ts.file_name,
      units: `${OFFLINE_DATA.mpeg_ts.total_units.toLocaleString("en-US")} packets`,
      window: `200 pkts (${OFFLINE_DATA.mpeg_ts.total_windows} windows)`,
      payload: `${(OFFLINE_DATA.mpeg_ts.total_payload_bytes / 1024).toFixed(1)} KB`,
      integrity: `${OFFLINE_DATA.mpeg_ts.integrity_ratio.toFixed(1)}%`,
      anomalies: `${OFFLINE_DATA.mpeg_ts.anomaly_window_count} windows [1, 2, 12, 88, 90]`,
      peakScore: OFFLINE_DATA.mpeg_ts.peak_anomaly_score.toFixed(4),
      dominant: OFFLINE_DATA.mpeg_ts.dominant_pattern,
      entropy: OFFLINE_DATA.mpeg_ts.entropy,
    },
    {
      format: "GSE",
      label: "GSE (Generic Stream Encapsulation)",
      file: OFFLINE_DATA.gse.file_name,
      units: `${OFFLINE_DATA.gse.total_units} PDUs`,
      window: `3 PDUs (${OFFLINE_DATA.gse.total_windows} windows)`,
      payload: `${(OFFLINE_DATA.gse.total_payload_bytes / 1024).toFixed(1)} KB`,
      integrity: `${OFFLINE_DATA.gse.integrity_ratio.toFixed(1)}%`,
      anomalies: `${OFFLINE_DATA.gse.anomaly_window_count} window [4]`,
      peakScore: OFFLINE_DATA.gse.peak_anomaly_score.toFixed(4),
      dominant: OFFLINE_DATA.gse.dominant_pattern,
      entropy: OFFLINE_DATA.gse.entropy,
    },
    {
      format: "BB_FRAME",
      label: "DVB-S2 Baseband Frame",
      file: OFFLINE_DATA.bbframe.file_name,
      units: `${OFFLINE_DATA.bbframe.total_units.toLocaleString("en-US")} frames`,
      window: `50 frames (${OFFLINE_DATA.bbframe.total_windows} windows)`,
      payload: `${(OFFLINE_DATA.bbframe.total_payload_bytes / 1024).toFixed(1)} KB`,
      integrity: `${OFFLINE_DATA.bbframe.integrity_ratio.toFixed(1)}%`,
      anomalies: `${OFFLINE_DATA.bbframe.anomaly_window_count} windows [0, 83, 84, 85, 86]`,
      peakScore: OFFLINE_DATA.bbframe.peak_anomaly_score.toFixed(4),
      dominant: OFFLINE_DATA.bbframe.dominant_pattern,
      entropy: OFFLINE_DATA.bbframe.entropy,
    },
  ];

  return (
    <div className="w-full overflow-x-auto border border-[var(--border-main)] bg-[var(--bg-surface)] transition-colors duration-150">
      <table className="w-full border-collapse text-left font-mono text-[12px]">
        <thead>
          <tr className="border-b border-[var(--border-main)] bg-[var(--bg-main)] text-[var(--text-muted)]">
            <th className="p-3 border-r border-[var(--border-main)]">FORMAT</th>
            <th className="p-3 border-r border-[var(--border-main)]">RAW UNITS</th>
            <th className="p-3 border-r border-[var(--border-main)]">WINDOW (w)</th>
            <th className="p-3 border-r border-[var(--border-main)]">USER PAYLOAD</th>
            <th className="p-3 border-r border-[var(--border-main)]">INTEGRITY</th>
            <th className="p-3 border-r border-[var(--border-main)]">F2 ANOMALIES</th>
            <th className="p-3 border-r border-[var(--border-main)]">PEAK SCORE</th>
            <th className="p-3 border-r border-[var(--border-main)]">DOMINANT COMPONENT</th>
            <th className="p-3">ENTROPY / DISPERSION</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-[var(--border-dim)] text-[var(--text-main)]">
          {formats.map((row) => (
            <tr key={row.format} className="hover:bg-[var(--bg-surface-elevated)] transition-colors">
              <td className="p-3 border-r border-[var(--border-main)] font-bold text-[var(--text-main)] whitespace-nowrap">
                <span className="text-[#FF6B35] mr-1.5 font-bold">&gt;</span>
                {row.format}
              </td>
              <td className="p-3 border-r border-[var(--border-main)] whitespace-nowrap">{row.units}</td>
              <td className="p-3 border-r border-[var(--border-main)] whitespace-nowrap">{row.window}</td>
              <td className="p-3 border-r border-[var(--border-main)] whitespace-nowrap">{row.payload}</td>
              <td className="p-3 border-r border-[var(--border-main)] font-semibold text-[var(--text-main)] whitespace-nowrap">
                {row.integrity}
              </td>
              <td className="p-3 border-r border-[var(--border-main)] whitespace-nowrap text-[#FF6B35] font-semibold">
                {row.anomalies}
              </td>
              <td className="p-3 border-r border-[var(--border-main)] whitespace-nowrap">{row.peakScore}</td>
              <td className="p-3 border-r border-[var(--border-main)] whitespace-nowrap text-[var(--text-muted)]">
                {row.dominant}
              </td>
              <td className="p-3 whitespace-nowrap text-[var(--text-muted)]">{row.entropy}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};
