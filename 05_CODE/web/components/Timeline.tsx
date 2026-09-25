"use client";

import React, { useState, useEffect } from "react";
import { TimelineData, TimelinePoint } from "@/lib/types";
import { Tooltip } from "@/components/Tooltip";

interface TimelineProps {
  timeline: TimelineData | null;
}

export const Timeline: React.FC<TimelineProps> = ({ timeline }) => {
  const [selectedPointIndex, setSelectedPointIndex] = useState<number>(0);

  const points = timeline?.points || [];

  // Keyboard navigation for Timeline scrubbing
  useEffect(() => {
    if (points.length === 0) return;

    const handleKeyDown = (e: KeyboardEvent) => {
      if (
        document.activeElement?.tagName === "INPUT" ||
        document.activeElement?.tagName === "TEXTAREA" ||
        document.activeElement?.tagName === "SELECT"
      ) {
        return;
      }
      if (e.key === "ArrowLeft") {
        e.preventDefault();
        setSelectedPointIndex((prev) => Math.max(0, prev - 1));
      } else if (e.key === "ArrowRight") {
        e.preventDefault();
        setSelectedPointIndex((prev) => Math.min(points.length - 1, prev + 1));
      }
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [points.length]);

  if (!timeline || !timeline.points || timeline.points.length === 0) {
    return (
      <section id="timeline" className="w-full border-b border-[var(--border-main)] bg-[var(--bg-main)] py-12 transition-colors duration-150">
        <div className="max-w-[1440px] mx-auto px-4 font-mono text-[12px] text-[var(--text-muted)]">
          NO TIMELINE DATA AVAILABLE
        </div>
      </section>
    );
  }

  const currentPoint: TimelinePoint = points[selectedPointIndex] || points[0];

  return (
    <section id="timeline" className="w-full border-b border-[var(--border-main)] bg-[var(--bg-main)] py-12 transition-colors duration-150">
      <div className="max-w-[1440px] mx-auto px-4">
        {/* Section Title */}
        <div className="flex flex-col md:flex-row md:items-end justify-between border-b border-[var(--border-main)] pb-4 mb-6">
          <div>
            <div className="font-mono text-[12px] text-[var(--text-muted)] uppercase mb-1 flex items-center gap-2">
              <span>FEATURE F4</span>
              <span>//</span>
              <Tooltip content="F4 partitions streaming byte payloads into contiguous fixed-size framing windows to map health, anomaly density, and byte ranges">
                <span>ACTIVITY VISUALIZATION &amp; SPATIAL PROFILING</span>
              </Tooltip>
            </div>
            <h2 className="text-[24px] md:text-[48px] font-bold uppercase tracking-tight text-[var(--text-main)]">
              HORIZONTAL ANALYSIS TIMELINE
            </h2>
          </div>
          <div className="mt-2 md:mt-0 font-mono text-[12px] text-[var(--text-muted)]">
            PARTITIONING: {timeline.total_windows} WINDOWS (w={timeline.window_size}) // SPATIAL BYTE OFFSETS
          </div>
        </div>

        {/* Legend & Navigation Hint */}
        <div className="flex flex-wrap items-center justify-between gap-4 font-mono text-[12px] mb-6 p-3 border border-[var(--border-main)] bg-[var(--bg-surface)]">
          <div className="flex flex-wrap items-center gap-6">
            <span className="text-[var(--text-muted)] uppercase">TIMELINE LEGEND:</span>
            <span className="flex items-center gap-2">
              <span className="inline-block w-3.5 h-3.5 border border-[var(--border-main)] bg-[var(--bg-main)]" />
              <span className="text-[var(--text-main)]">NORMAL WINDOW</span>
            </span>
            <span className="flex items-center gap-2">
              <span className="inline-block w-3.5 h-3.5 border border-[#FF6B35] bg-[#FF6B35]/20" />
              <span className="text-[#FF6B35] font-semibold">ANOMALY WINDOW (F2)</span>
            </span>
            <span className="flex items-center gap-2">
              <span className="inline-block w-1 h-3.5 bg-[var(--border-main)]" />
              <span className="text-[var(--text-muted)]">WINDOW BOUNDARY</span>
            </span>
          </div>

          <div className="text-[11px] text-[var(--text-muted)] flex items-center gap-2">
            <span>NAVIGATE:</span>
            <kbd className="px-1.5 py-0.5 border border-[var(--border-main)] bg-[var(--bg-main)] text-[var(--text-main)]">←</kbd>
            <kbd className="px-1.5 py-0.5 border border-[var(--border-main)] bg-[var(--bg-main)] text-[var(--text-main)]">→</kbd>
            <span>OR CLICK SEGMENTS</span>
          </div>
        </div>

        {/* Horizontal Segmented Window Scrub Bar */}
        <div className="border border-[var(--border-main)] bg-[var(--bg-surface)] p-4 mb-8">
          <div className="text-[12px] font-mono text-[var(--text-muted)] mb-3 flex flex-wrap items-center justify-between gap-2">
            <span>SCROLL / CLICK WINDOW SEGMENT TO INSPECT OFFSETS:</span>
            <div className="flex items-center gap-3">
              <span className="text-[var(--text-main)] font-semibold">
                ACTIVE: WINDOW W{currentPoint.window_index} OF {points.length - 1}
              </span>
              <div className="flex items-center gap-1">
                <button
                  onClick={() => setSelectedPointIndex((prev) => Math.max(0, prev - 1))}
                  disabled={selectedPointIndex === 0}
                  className="px-2 py-0.5 border border-[var(--border-main)] bg-[var(--bg-main)] text-[var(--text-main)] hover:border-[#FF6B35] disabled:opacity-30 disabled:hover:border-[var(--border-main)] cursor-pointer text-[11px] transition-all active:translate-y-[1px]"
                  title="Previous window (or Left Arrow)"
                >
                  [&lt; PREV]
                </button>
                <button
                  onClick={() => setSelectedPointIndex((prev) => Math.min(points.length - 1, prev + 1))}
                  disabled={selectedPointIndex === points.length - 1}
                  className="px-2 py-0.5 border border-[var(--border-main)] bg-[var(--bg-main)] text-[var(--text-main)] hover:border-[#FF6B35] disabled:opacity-30 disabled:hover:border-[var(--border-main)] cursor-pointer text-[11px] transition-all active:translate-y-[1px]"
                  title="Next window (or Right Arrow)"
                >
                  [NEXT &gt;]
                </button>
              </div>
            </div>
          </div>

          <div className="overflow-x-auto pb-2">
            <div className="flex items-stretch min-w-max gap-[2px] py-2">
              {points.map((pt, idx) => {
                const isSelected = idx === selectedPointIndex;
                const isAnomaly = pt.is_anomaly;

                return (
                  <button
                    key={pt.window_index}
                    onClick={() => setSelectedPointIndex(idx)}
                    title={`Window ${pt.window_index}: Anomaly Score=${pt.anomaly_score.toFixed(3)}, Severity=${pt.anomaly_severity || "NORMAL"}`}
                    className={`h-16 px-2.5 flex flex-col justify-between items-center border transition-all cursor-pointer select-none font-mono ${
                      isSelected
                        ? "border-[#FF6B35] bg-[var(--bg-surface-elevated)] ring-1 ring-[#FF6B35]"
                        : isAnomaly
                        ? "border-[#FF6B35] bg-[#FF6B35]/15 hover:bg-[#FF6B35]/25 text-[#FF6B35]"
                        : "border-[var(--border-main)] bg-[var(--bg-main)] hover:border-[var(--text-muted)] text-[var(--text-muted)]"
                    }`}
                    style={{ minWidth: "48px" }}
                  >
                    <span className="text-[12px] font-bold">W{pt.window_index}</span>
                    <span
                      className={`text-[11px] ${
                        isAnomaly ? "text-[#FF6B35] font-bold" : "text-[var(--text-muted)]"
                      }`}
                    >
                      {pt.anomaly_score.toFixed(2)}
                    </span>
                    <div
                      className={`w-full h-1 ${
                        isAnomaly ? "bg-[#FF6B35]" : isSelected ? "bg-[var(--text-main)]" : "bg-[var(--border-main)]"
                      }`}
                    />
                  </button>
                );
              })}
            </div>
          </div>
        </div>

        {/* Selected Window Deep Inspection Panel (Asymmetric 8/4 Grid) */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
          {/* Spatial Byte Offset & Framing Diagnostics (8 cols) */}
          <div className="lg:col-span-8 border border-[var(--border-main)] bg-[var(--bg-surface)] p-6 transition-colors duration-150">
            <div className="flex flex-wrap items-center justify-between border-b border-[var(--border-dim)] pb-3 mb-6">
              <div className="font-mono text-[14px] text-[var(--text-main)] font-bold">
                WINDOW INSPECTION // INDEX:{" "}
                <span className="text-[#FF6B35]">W{currentPoint.window_index}</span>
              </div>
              <div className="font-mono text-[12px] flex items-center gap-3">
                <span
                  className={`px-2 py-0.5 border ${
                    currentPoint.is_anomaly
                      ? "border-[#FF6B35] bg-[#FF6B35]/10 text-[#FF6B35]"
                      : "border-[var(--border-main)] bg-[var(--bg-main)] text-[var(--text-muted)]"
                  }`}
                >
                  CLASSIFICATION: {currentPoint.anomaly_severity || "NORMAL"}
                </span>
                <span className="text-[var(--text-muted)]">
                  SCORE: <span className="font-semibold text-[var(--text-main)]">{currentPoint.anomaly_score.toFixed(4)}</span>
                </span>
              </div>
            </div>

            {/* Metrics Breakdown Grid */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 font-mono text-[12px] mb-6">
              <div className="p-3 bg-[var(--bg-main)] border border-[var(--border-main)]">
                <div className="text-[var(--text-muted)] text-[11px]">
                  <Tooltip content="Index range of framing units analyzed within this specific sliding window">
                    <span>UNIT SPAN:</span>
                  </Tooltip>
                </div>
                <div className="text-[var(--text-main)] font-bold text-[14px] mt-0.5">
                  [{currentPoint.unit_offset_start} - {currentPoint.unit_offset_end}]
                </div>
                <div className="text-[11px] text-[var(--text-muted)] mt-0.5">
                  Count: {currentPoint.unit_count} units
                </div>
              </div>

              <div className="p-3 bg-[var(--bg-main)] border border-[var(--border-main)]">
                <div className="text-[var(--text-muted)] text-[11px]">
                  <Tooltip content="Physical byte offsets within the stream file corresponding to this window's framing units">
                    <span>BYTE OFFSET RANGE:</span>
                  </Tooltip>
                </div>
                <div className="text-[var(--text-main)] font-bold text-[14px] mt-0.5 truncate">
                  0x{currentPoint.byte_offset_start.toString(16).toUpperCase()} - 0x
                  {currentPoint.byte_offset_end.toString(16).toUpperCase()}
                </div>
                <div className="text-[11px] text-[var(--text-muted)] mt-0.5">
                  Span: {(currentPoint.byte_offset_end - currentPoint.byte_offset_start).toLocaleString("en-US")} bytes
                </div>
              </div>

              <div className="p-3 bg-[var(--bg-main)] border border-[var(--border-main)]">
                <div className="text-[var(--text-muted)] text-[11px]">
                  <Tooltip content="Pure user data payload extracted after removing framing headers, adaptation fields, or padding">
                    <span>EXTRACTED PAYLOAD:</span>
                  </Tooltip>
                </div>
                <div className="text-[var(--text-main)] font-bold text-[14px] mt-0.5">
                  {currentPoint.payload_bytes.toLocaleString("en-US")} bytes
                </div>
                <div className="text-[11px] text-[var(--text-muted)] mt-0.5">
                  Health: {currentPoint.health_score.toFixed(1)}%
                </div>
              </div>
            </div>

            {/* Diagnostic Summary & Explanations */}
            <div className="p-4 bg-[var(--bg-main)] border border-[var(--border-main)] font-mono text-[12px]">
              <div className="text-[var(--text-muted)] uppercase mb-1">ANOMALY EXPLANATION / FINDINGS:</div>
              <div className="text-[var(--text-main)] leading-relaxed">
                {currentPoint.anomaly_explanation ||
                  "Window adheres to baseline operational profile. Framing syntax, error rates, and multiplex entropy remain within expected Gaussian bounds."}
              </div>
            </div>
          </div>

          {/* Format Specific Parameters & Deviations (4 cols) */}
          <div className="lg:col-span-4 border border-[var(--border-main)] bg-[var(--bg-surface)] p-6 flex flex-col justify-between transition-colors duration-150">
            <div>
              <div className="font-mono text-[12px] text-[var(--text-muted)] uppercase border-b border-[var(--border-dim)] pb-2 mb-4">
                [WINDOW_INTERNAL_FEATURES]
              </div>

              <div className="space-y-2.5 font-mono text-[12px]">
                {currentPoint.format_specific_metrics &&
                Object.keys(currentPoint.format_specific_metrics).length > 0 ? (
                  Object.entries(currentPoint.format_specific_metrics).map(([k, v]) => (
                    <div
                      key={k}
                      className="flex justify-between items-center p-2.5 bg-[var(--bg-main)] border border-[var(--border-main)] hover:border-[#FF6B35] transition-colors"
                    >
                      <span className="text-[var(--text-muted)] text-[12px] truncate max-w-[140px]">
                        {k}:
                      </span>
                      <span className="text-[var(--text-main)] font-semibold">
                        {typeof v === "number" ? (Number.isInteger(v) ? v : v.toFixed(4)) : String(v)}
                      </span>
                    </div>
                  ))
                ) : (
                  <div className="text-[var(--text-muted)] text-[12px]">
                    Standard framing metrics registered for this analysis window.
                  </div>
                )}
              </div>
            </div>

            <div className="mt-6 pt-4 border-t border-[var(--border-dim)] font-mono text-[11px] text-[var(--text-muted)] leading-normal">
              * Note: Segments represent spatial analysis windows partitioned along the stream byte
              stream. Absolute physical timestamps are omitted as uncalibrated raw captures lack GPS/NTP reference.
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};
