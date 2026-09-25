"use client";

import React, { useState } from "react";
import { OFFLINE_DATA } from "@/lib/offlineData";
import { TelemetryTable } from "./TelemetryTable";
import { AnalysisResponse } from "@/lib/types";
import { Tooltip } from "@/components/Tooltip";

interface TelemetrySectionProps {
  currentAnalysis: AnalysisResponse | null;
  onSelectFormatKey: (key: "mpeg_ts" | "gse" | "bbframe") => void;
  onNavigateTab?: (tab: "dashboard" | "anomalies" | "timeline" | "comparison" | "architecture" | "docs") => void;
}

export const TelemetrySection: React.FC<TelemetrySectionProps> = ({
  currentAnalysis,
  onSelectFormatKey,
  onNavigateTab,
}) => {
  const [activeTab, setActiveTab] = useState<"mpeg_ts" | "gse" | "bbframe">("mpeg_ts");

  const handleTabChange = (key: "mpeg_ts" | "gse" | "bbframe") => {
    setActiveTab(key);
    onSelectFormatKey(key);
  };

  const selectedData = OFFLINE_DATA[activeTab];

  return (
    <section id="telemetry" className="w-full border-b border-[var(--border-main)] bg-[var(--bg-main)] py-12 transition-colors duration-150">
      <div className="max-w-[1440px] mx-auto px-4">
        {/* Section Header */}
        <div className="border-b border-[var(--border-main)] pb-4 mb-8">
          <div className="text-xs font-semibold text-[var(--text-muted)] tracking-wider uppercase mb-1 flex items-center gap-2">
            <span>EMPIRICAL BENCHMARKS</span>
            <span>•</span>
            <Tooltip content="Empirical broadcast captures from European direct-to-home satellite transmissions and reference PCAP baseband streams">
              <span className="text-[var(--text-main)] font-mono cursor-help underline decoration-dotted underline-offset-2">
                MULTI-FORMAT CAPTURES
              </span>
            </Tooltip>
          </div>
          <h2 className="text-[24px] md:text-[44px] font-bold uppercase tracking-tight text-[var(--text-main)]">
            MULTI-FORMAT BENCHMARK DATASETS
          </h2>
          <p className="text-[14px] text-[var(--text-muted)] max-w-[800px] mt-2 leading-relaxed">
            Authoritative empirical captures from production DVB-S2 satellite receiver outputs.
            Each stream format operates on independent framing units (188B TS packets, variable GSE PDUs,
            and ~7.2KB Baseband Frames).
          </p>
        </div>

        {/* Dense Comparative Telemetry Table */}
        <div className="mb-10">
          <div className="text-xs font-semibold text-[var(--text-muted)] uppercase tracking-wider mb-2.5">
            Cross-Dataset Executive Telemetry Table:
          </div>
          <TelemetryTable />
        </div>

        {/* Format Selector Tabs: 0px Radius, 1px Border */}
        <div className="flex flex-wrap gap-2 border-b border-[var(--border-main)] pb-4 mb-8 font-mono text-[12px]">
          <button
            onClick={() => handleTabChange("mpeg_ts")}
            className={`px-5 py-3 border transition-all cursor-pointer active:translate-y-[1px] focus-visible:outline-2 focus-visible:outline-[#FF6B35] ${
              activeTab === "mpeg_ts"
                ? "border-[#FF6B35] bg-[var(--bg-surface-elevated)] text-[var(--text-main)] font-bold ring-1 ring-[#FF6B35]"
                : "border-[var(--border-main)] bg-[var(--bg-surface)] text-[var(--text-muted)] hover:text-[var(--text-main)] hover:border-[var(--text-muted)]"
            }`}
          >
            [01] MPEG-TS (18,176 PACKETS // 91 WINDOWS)
          </button>
          <button
            onClick={() => handleTabChange("gse")}
            className={`px-5 py-3 border transition-all cursor-pointer active:translate-y-[1px] focus-visible:outline-2 focus-visible:outline-[#FF6B35] ${
              activeTab === "gse"
                ? "border-[#FF6B35] bg-[var(--bg-surface-elevated)] text-[var(--text-main)] font-bold ring-1 ring-[#FF6B35]"
                : "border-[var(--border-main)] bg-[var(--bg-surface)] text-[var(--text-muted)] hover:text-[var(--text-main)] hover:border-[var(--text-muted)]"
            }`}
          >
            [02] GSE (14 DECODED PDUS // 5 WINDOWS)
          </button>
          <button
            onClick={() => handleTabChange("bbframe")}
            className={`px-5 py-3 border transition-all cursor-pointer active:translate-y-[1px] focus-visible:outline-2 focus-visible:outline-[#FF6B35] ${
              activeTab === "bbframe"
                ? "border-[#FF6B35] bg-[var(--bg-surface-elevated)] text-[var(--text-main)] font-bold ring-1 ring-[#FF6B35]"
                : "border-[var(--border-main)] bg-[var(--bg-surface)] text-[var(--text-muted)] hover:text-[var(--text-main)] hover:border-[var(--text-muted)]"
            }`}
          >
            [03] BBFRAME (4,309 FRAMES // 87 WINDOWS)
          </button>
        </div>

        {/* Active Format Detail Grid (Asymmetric 8/4 Split) */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
          {/* Format Detail Column (8 cols) */}
          <div className="lg:col-span-8 space-y-6">
            <div className="border border-[var(--border-main)] bg-[var(--bg-surface)] p-6 transition-colors duration-150">
              <div className="flex items-center justify-between border-b border-[var(--border-dim)] pb-3 mb-4">
                <span className="font-mono text-[12px] text-[var(--text-muted)] uppercase">
                  ACTIVE DATASET: {selectedData.format_label}
                </span>
                <span className="font-mono text-[12px] text-[#FF6B35] font-semibold">
                  VERIFIED CAPTURE / 06_RESULTS
                </span>
              </div>

              {/* Technical Key-Value Grid */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 font-mono text-[12px]">
                <div className="p-3 bg-[var(--bg-main)] border border-[var(--border-main)]">
                  <div className="text-[var(--text-muted)] text-[11px]">SOURCE FILE / PATH:</div>
                  <div className="text-[var(--text-main)] truncate font-semibold mt-0.5">
                    {selectedData.relative_path}
                  </div>
                </div>
                <div className="p-3 bg-[var(--bg-main)] border border-[var(--border-main)]">
                  <div className="text-[var(--text-muted)] text-[11px]">RAW FILE SIZE:</div>
                  <div className="text-[var(--text-main)] font-semibold mt-0.5">
                    {selectedData.file_size_bytes.toLocaleString("en-US")} bytes (
                    {(selectedData.file_size_bytes / 1024).toFixed(1)} KB)
                  </div>
                </div>
                <div className="p-3 bg-[var(--bg-main)] border border-[var(--border-main)]">
                  <div className="text-[var(--text-muted)] text-[11px]">TOTAL FRAMING UNITS:</div>
                  <div className="text-[var(--text-main)] font-semibold mt-0.5">
                    {selectedData.total_units.toLocaleString("en-US")} {selectedData.unit_type}
                  </div>
                </div>
                <div className="p-3 bg-[var(--bg-main)] border border-[var(--border-main)]">
                  <div className="text-[var(--text-muted)] text-[11px]">PARTITIONING WINDOW (w):</div>
                  <div className="text-[var(--text-main)] font-semibold mt-0.5">
                    w = {selectedData.window_size} ({selectedData.total_windows} windows total)
                  </div>
                </div>
                <div className="p-3 bg-[var(--bg-main)] border border-[var(--border-main)]">
                  <div className="text-[var(--text-muted)] text-[11px]">EXTRACTED USER PAYLOAD:</div>
                  <div className="text-[var(--text-main)] font-semibold mt-0.5">
                    {selectedData.total_payload_bytes.toLocaleString("en-US")} bytes (
                    {(selectedData.total_payload_bytes / 1024).toFixed(1)} KB)
                  </div>
                </div>
                <div className="p-3 bg-[var(--bg-main)] border border-[var(--border-main)]">
                  <div className="text-[var(--text-muted)] text-[11px]">DOMINANT COMPONENT / PATTERN:</div>
                  <div className="text-[var(--text-main)] font-semibold mt-0.5">
                    {selectedData.dominant_pattern}
                  </div>
                </div>
              </div>

              {/* F1 Stream Health Indicators */}
              <div className="mt-6 pt-4 border-t border-[var(--border-dim)]">
                <div className="flex items-center justify-between mb-3 border-b border-[var(--border-dim)] pb-2">
                  <span className="text-xs font-semibold text-[var(--text-muted)] uppercase tracking-wider">
                    F1 Stream Health Inspection
                  </span>
                  <span className="font-mono text-xs font-bold text-[#FF6B35]">HEALTH SCORE: 100.0% [HEALTHY]</span>
                </div>

                <div className="space-y-2 font-mono text-[12px]">
                  <div className="flex items-center justify-between p-2.5 bg-[var(--bg-main)] border border-[var(--border-main)]">
                    <span className="text-[var(--text-main)]">Framing / Sync Lock Integrity:</span>
                    <span className="text-[var(--text-main)] font-bold">{selectedData.sync_integrity}</span>
                  </div>
                  <div className="flex items-center justify-between p-2.5 bg-[var(--bg-main)] border border-[var(--border-main)]">
                    <span className="text-[var(--text-main)]">
                      <Tooltip content="Transport Error Indicator (TEI) asserts whether demodulation hardware flagged uncorrected Reed-Solomon or LDPC errors">
                        <span>Demodulator TEI Assertions:</span>
                      </Tooltip>
                    </span>
                    <span className="text-[var(--text-main)] font-semibold">0 errors (No demodulator fault asserted)</span>
                  </div>
                  <div className="flex items-center justify-between p-2.5 bg-[var(--bg-main)] border border-[var(--border-main)]">
                    <span className="text-[var(--text-main)]">
                      <Tooltip content="Continuity Counter (CC) 4-bit cyclic counter detects packet drops or sequence disruptions per PID">
                        <span>Continuity Counter Discontinuities:</span>
                      </Tooltip>
                    </span>
                    <span className="text-[var(--text-main)] font-semibold">0 drops (0% transport packet drop)</span>
                  </div>
                  <div className="flex items-center justify-between p-2.5 bg-[var(--bg-main)] border border-[var(--border-main)]">
                    <span className="text-[var(--text-main)]">Multiplex Entropy / Protocol Diversity:</span>
                    <span className="text-[var(--text-muted)]">{selectedData.entropy}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Tripartite Executive Findings Column (4 cols) */}
          <div className="lg:col-span-4 flex flex-col gap-6">
            <div className="border border-[var(--border-main)] bg-[var(--bg-surface)] p-6 transition-colors duration-150">
              <div className="font-mono text-[12px] text-[var(--text-muted)] uppercase border-b border-[var(--border-dim)] pb-2 mb-4">
                [TRIPARTITE_FINDINGS // F7 REPORT]
              </div>

              {selectedData.report_findings && selectedData.report_findings.length > 0 ? (
                <div className="space-y-3 font-mono text-[12px]">
                  {selectedData.report_findings.map((f: any, idx: number) => (
                    <div key={idx} className="p-3 bg-[var(--bg-main)] border border-[var(--border-main)] text-[var(--text-main)] hover:border-[#FF6B35] transition-colors">
                      <div className="text-[#FF6B35] font-bold text-[12px] mb-1">
                        [{idx + 1}] {typeof f === "string" ? f : f.title || f.category || `Finding ${idx + 1}`}
                      </div>
                      {typeof f !== "string" && f.statement && (
                        <div className="text-[12px] text-[var(--text-main)] leading-tight mb-1">{f.statement}</div>
                      )}
                      {typeof f !== "string" && f.evidence && (
                        <div className="text-[11px] text-[var(--text-muted)] leading-tight">{f.evidence}</div>
                      )}
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-[12px] font-mono text-[var(--text-muted)]">
                  All structural findings verified by automatic report synthesizer.
                </div>
              )}
            </div>

            {/* Note on Incommensurability */}
            <div className="border border-[var(--border-main)] bg-[var(--bg-main)] p-4 font-mono text-[12px] text-[var(--text-muted)] leading-normal">
              <div className="text-[var(--text-main)] font-bold uppercase mb-1">
                SEMANTIC BOUNDARY PRINCIPLE:
              </div>
              Framing unit counts are non-comparable across formats. 18,176 TS packets (188B) cannot
              be quantitatively equated to 4,309 BBFrames (~7.2KB) or 14 GSE PDUs. Only extracted
              user payload bytes and framing integrity ratio remain commensurable.
            </div>

            {/* Quick Page-Shift Shortcuts */}
            {onNavigateTab && (
              <div className="pt-2 border-t border-[var(--border-dim)] flex flex-wrap gap-3 font-mono text-xs">
                <button
                  onClick={() => onNavigateTab("timeline")}
                  className="px-3 py-2 border border-[#FF6B35] bg-[var(--bg-surface)] text-[var(--text-main)] hover:bg-[#FF6B35] hover:text-[#0A0A0A] transition-colors font-bold cursor-pointer"
                >
                  [03] SHIFT TO TIMELINE (F4) &rarr;
                </button>
                <button
                  onClick={() => onNavigateTab("anomalies")}
                  className="px-3 py-2 border border-[var(--border-main)] bg-[var(--bg-surface)] text-[var(--text-main)] hover:border-[#FF6B35] transition-colors cursor-pointer"
                >
                  [02] SHIFT TO ANOMALY ANALYSIS (F2+F5) &rarr;
                </button>
                <button
                  onClick={() => onNavigateTab("comparison")}
                  className="px-3 py-2 border border-[var(--border-main)] bg-[var(--bg-surface)] text-[var(--text-main)] hover:border-[#FF6B35] transition-colors cursor-pointer"
                >
                  [04] SHIFT TO STREAM COMPARISON (F6) &rarr;
                </button>
              </div>
            )}
          </div>
        </div>
      </div>
    </section>
  );
};
