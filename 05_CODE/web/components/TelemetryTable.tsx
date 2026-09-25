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
    <div className="w-full overflow-x-auto border border-[#262626] bg-[#141414]">
      <table className="w-full border-collapse text-left font-mono text-[12px]">
        <thead>
          <tr className="border-b border-[#262626] bg-[#0A0A0A] text-[#737373]">
            <th className="p-3 border-r border-[#262626]">FORMAT</th>
            <th className="p-3 border-r border-[#262626]">RAW UNITS</th>
            <th className="p-3 border-r border-[#262626]">WINDOW (w)</th>
            <th className="p-3 border-r border-[#262626]">USER PAYLOAD</th>
            <th className="p-3 border-r border-[#262626]">INTEGRITY</th>
            <th className="p-3 border-r border-[#262626]">F2 ANOMALIES</th>
            <th className="p-3 border-r border-[#262626]">PEAK SCORE</th>
            <th className="p-3 border-r border-[#262626]">DOMINANT COMPONENT</th>
            <th className="p-3">ENTROPY / DISPERSION</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-[#1A1A1A] text-[#E8E8E8]">
          {formats.map((row) => (
            <tr key={row.format} className="hover:bg-[#1a1a1a] transition-colors">
              <td className="p-3 border-r border-[#262626] font-bold text-white whitespace-nowrap">
                <span className="text-[#FF6B35] mr-1.5">&gt;</span>
                {row.format}
              </td>
              <td className="p-3 border-r border-[#262626] whitespace-nowrap">{row.units}</td>
              <td className="p-3 border-r border-[#262626] whitespace-nowrap">{row.window}</td>
              <td className="p-3 border-r border-[#262626] whitespace-nowrap">{row.payload}</td>
              <td className="p-3 border-r border-[#262626] font-semibold text-white whitespace-nowrap">
                {row.integrity}
              </td>
              <td className="p-3 border-r border-[#262626] whitespace-nowrap text-[#FF6B35]">
                {row.anomalies}
              </td>
              <td className="p-3 border-r border-[#262626] whitespace-nowrap">{row.peakScore}</td>
              <td className="p-3 border-r border-[#262626] whitespace-nowrap text-[#737373]">
                {row.dominant}
              </td>
              <td className="p-3 whitespace-nowrap text-[#737373]">{row.entropy}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};
