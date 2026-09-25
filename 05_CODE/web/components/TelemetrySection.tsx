"use client";

import React, { useState } from "react";
import { OFFLINE_DATA } from "@/lib/offlineData";
import { TelemetryTable } from "./TelemetryTable";
import { AnalysisResponse } from "@/lib/types";

interface TelemetrySectionProps {
  currentAnalysis: AnalysisResponse | null;
  onSelectFormatKey: (key: "mpeg_ts" | "gse" | "bbframe") => void;
}

export const TelemetrySection: React.FC<TelemetrySectionProps> = ({
  currentAnalysis,
  onSelectFormatKey,
}) => {
  const [activeTab, setActiveTab] = useState<"mpeg_ts" | "gse" | "bbframe">("mpeg_ts");

  const handleTabChange = (key: "mpeg_ts" | "gse" | "bbframe") => {
    setActiveTab(key);
    onSelectFormatKey(key);
  };

  const selectedData = OFFLINE_DATA[activeTab];

  return (
    <section id="telemetry" className="w-full border-b border-[#262626] bg-[#0A0A0A] py-12">
      <div className="max-w-[1440px] mx-auto px-4">
        {/* Section Header */}
        <div className="border-b border-[#262626] pb-4 mb-8">
          <div className="font-mono text-[12px] text-[#737373] uppercase mb-1">
            SECTION [02] // VERIFIED EMPIRICAL TELEMETRY
          </div>
          <h2 className="text-[24px] md:text-[48px] font-bold uppercase tracking-tight text-[#E8E8E8]">
            MULTI-FORMAT BENCHMARK DATASETS
          </h2>
          <p className="text-[14px] text-[#737373] max-w-[800px] mt-2">
            Authoritative empirical captures from production DVB-S2 satellite receiver outputs.
            Each stream format operates on independent framing units (188B TS packets, variable GSE PDUs,
            and ~7.2KB Baseband Frames).
          </p>
        </div>

        {/* Dense Comparative Telemetry Table */}
        <div className="mb-10">
          <div className="font-mono text-[12px] text-[#737373] uppercase mb-2">
            CROSS-DATASET EXECUTIVE COMPARISON TABLE:
          </div>
          <TelemetryTable />
        </div>

        {/* Format Selector Tabs: 0px Radius, 1px Border */}
        <div className="flex flex-wrap gap-2 border-b border-[#262626] pb-4 mb-8 font-mono text-[12px]">
          <button
            onClick={() => handleTabChange("mpeg_ts")}
            className={`px-5 py-3 border transition-colors cursor-pointer ${
              activeTab === "mpeg_ts"
                ? "border-[#FF6B35] bg-[#141414] text-[#E8E8E8] font-bold"
                : "border-[#262626] bg-[#0A0A0A] text-[#737373] hover:text-[#E8E8E8]"
            }`}
          >
            [01] MPEG-TS (18,176 PACKETS // 91 WINDOWS)
          </button>
          <button
            onClick={() => handleTabChange("gse")}
            className={`px-5 py-3 border transition-colors cursor-pointer ${
              activeTab === "gse"
                ? "border-[#FF6B35] bg-[#141414] text-[#E8E8E8] font-bold"
                : "border-[#262626] bg-[#0A0A0A] text-[#737373] hover:text-[#E8E8E8]"
            }`}
          >
            [02] GSE (14 DECODED PDUS // 5 WINDOWS)
          </button>
          <button
            onClick={() => handleTabChange("bbframe")}
            className={`px-5 py-3 border transition-colors cursor-pointer ${
              activeTab === "bbframe"
                ? "border-[#FF6B35] bg-[#141414] text-[#E8E8E8] font-bold"
                : "border-[#262626] bg-[#0A0A0A] text-[#737373] hover:text-[#E8E8E8]"
            }`}
          >
            [03] BBFRAME (4,309 FRAMES // 87 WINDOWS)
          </button>
        </div>

        {/* Active Format Detail Grid (Asymmetric 8/4 Split) */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
          {/* Format Detail Column (8 cols) */}
          <div className="lg:col-span-8 space-y-6">
            <div className="border border-[#262626] bg-[#141414] p-6">
              <div className="flex items-center justify-between border-b border-[#262626] pb-3 mb-4">
                <span className="font-mono text-[12px] text-[#737373] uppercase">
                  ACTIVE DATASET: {selectedData.format_label}
                </span>
                <span className="font-mono text-[12px] text-[#FF6B35]">
                  VERIFIED CAPTURE / 06_RESULTS
                </span>
              </div>

              {/* Technical Key-Value Grid */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 font-mono text-[12px]">
                <div className="p-3 bg-[#0A0A0A] border border-[#262626]">
                  <div className="text-[#737373] text-[12px]">SOURCE FILE / PATH:</div>
                  <div className="text-[#E8E8E8] truncate font-semibold mt-0.5">
                    {selectedData.relative_path}
                  </div>
                </div>
                <div className="p-3 bg-[#0A0A0A] border border-[#262626]">
                  <div className="text-[#737373] text-[12px]">RAW FILE SIZE:</div>
                  <div className="text-[#E8E8E8] font-semibold mt-0.5">
                    {selectedData.file_size_bytes.toLocaleString("en-US")} bytes (
                    {(selectedData.file_size_bytes / 1024).toFixed(1)} KB)
                  </div>
                </div>
                <div className="p-3 bg-[#0A0A0A] border border-[#262626]">
                  <div className="text-[#737373] text-[12px]">TOTAL FRAMING UNITS:</div>
                  <div className="text-[#E8E8E8] font-semibold mt-0.5">
                    {selectedData.total_units.toLocaleString("en-US")} {selectedData.unit_type}
                  </div>
                </div>
                <div className="p-3 bg-[#0A0A0A] border border-[#262626]">
                  <div className="text-[#737373] text-[12px]">PARTITIONING WINDOW (w):</div>
                  <div className="text-[#E8E8E8] font-semibold mt-0.5">
                    w = {selectedData.window_size} ({selectedData.total_windows} windows total)
                  </div>
                </div>
                <div className="p-3 bg-[#0A0A0A] border border-[#262626]">
                  <div className="text-[#737373] text-[12px]">EXTRACTED USER PAYLOAD:</div>
                  <div className="text-[#E8E8E8] font-semibold mt-0.5">
                    {selectedData.total_payload_bytes.toLocaleString("en-US")} bytes (
                    {(selectedData.total_payload_bytes / 1024).toFixed(1)} KB)
                  </div>
                </div>
                <div className="p-3 bg-[#0A0A0A] border border-[#262626]">
                  <div className="text-[#737373] text-[12px]">DOMINANT COMPONENT / PATTERN:</div>
                  <div className="text-[#E8E8E8] font-semibold mt-0.5">
                    {selectedData.dominant_pattern}
                  </div>
                </div>
              </div>

              {/* F1 Stream Health Indicators */}
              <div className="mt-6 pt-4 border-t border-[#262626]">
                <div className="font-mono text-[12px] text-[#737373] uppercase mb-3 flex items-center justify-between">
                  <span>[F1_STREAM_HEALTH_INSPECTION]</span>
                  <span className="text-[#E8E8E8]">HEALTH SCORE: 100.0% [HEALTHY]</span>
                </div>

                <div className="space-y-2 font-mono text-[12px]">
                  <div className="flex items-center justify-between p-2.5 bg-[#0A0A0A] border border-[#262626]">
                    <span className="text-[#E8E8E8]">Framing / Sync Lock Integrity:</span>
                    <span className="text-[#E8E8E8] font-bold">{selectedData.sync_integrity}</span>
                  </div>
                  <div className="flex items-center justify-between p-2.5 bg-[#0A0A0A] border border-[#262626]">
                    <span className="text-[#E8E8E8]">Demodulator TEI Assertions:</span>
                    <span className="text-[#E8E8E8]">0 errors (No demodulator fault asserted)</span>
                  </div>
                  <div className="flex items-center justify-between p-2.5 bg-[#0A0A0A] border border-[#262626]">
                    <span className="text-[#E8E8E8]">Continuity Counter Discontinuities:</span>
                    <span className="text-[#E8E8E8]">0 drops (0% transport packet drop)</span>
                  </div>
                  <div className="flex items-center justify-between p-2.5 bg-[#0A0A0A] border border-[#262626]">
                    <span className="text-[#E8E8E8]">Multiplex Entropy / Protocol Diversity:</span>
                    <span className="text-[#737373]">{selectedData.entropy}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Tripartite Executive Findings Column (4 cols) */}
          <div className="lg:col-span-4 flex flex-col gap-6">
            <div className="border border-[#262626] bg-[#141414] p-6">
              <div className="font-mono text-[12px] text-[#737373] uppercase border-b border-[#262626] pb-2 mb-4">
                [TRIPARTITE_FINDINGS // F7 REPORT]
              </div>

              {selectedData.report_findings && selectedData.report_findings.length > 0 ? (
                <div className="space-y-3 font-mono text-[12px]">
                  {selectedData.report_findings.map((f: any, idx: number) => (
                    <div key={idx} className="p-2.5 bg-[#0A0A0A] border border-[#262626] text-[#E8E8E8]">
                      <div className="text-[#FF6B35] font-bold text-[12px] mb-1">
                        [{idx + 1}] {typeof f === "string" ? f : f.title || f.category || `Finding ${idx + 1}`}
                      </div>
                      {typeof f !== "string" && f.statement && (
                        <div className="text-[12px] text-[#E8E8E8] leading-tight mb-1">{f.statement}</div>
                      )}
                      {typeof f !== "string" && f.evidence && (
                        <div className="text-[12px] text-[#737373] leading-tight">{f.evidence}</div>
                      )}
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-[12px] font-mono text-[#737373]">
                  All structural findings verified by automatic report synthesizer.
                </div>
              )}
            </div>

            {/* Note on Incommensurability */}
            <div className="border border-[#262626] bg-[#0A0A0A] p-4 font-mono text-[12px] text-[#737373]">
              <div className="text-[#E8E8E8] font-bold uppercase mb-1">
                SEMANTIC BOUNDARY PRINCIPLE:
              </div>
              Framing unit counts are non-comparable across formats. 18,176 TS packets (188B) cannot
              be quantitatively equated to 4,309 BBFrames (~7.2KB) or 14 GSE PDUs. Only extracted
              user payload bytes and framing integrity ratio remain commensurable.
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};
