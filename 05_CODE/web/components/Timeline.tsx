"use client";

import React, { useState } from "react";
import { TimelineData, TimelinePoint } from "@/lib/types";

interface TimelineProps {
  timeline: TimelineData | null;
}

export const Timeline: React.FC<TimelineProps> = ({ timeline }) => {
  const [selectedPointIndex, setSelectedPointIndex] = useState<number>(0);

  if (!timeline || !timeline.points || timeline.points.length === 0) {
    return (
      <section id="timeline" className="w-full border-b border-[#262626] bg-[#0A0A0A] py-12">
        <div className="max-w-[1440px] mx-auto px-4 font-mono text-[12px] text-[#737373]">
          NO TIMELINE DATA AVAILABLE
        </div>
      </section>
    );
  }

  const points = timeline.points;
  const currentPoint: TimelinePoint = points[selectedPointIndex] || points[0];

  return (
    <section id="timeline" className="w-full border-b border-[#262626] bg-[#0A0A0A] py-12">
      <div className="max-w-[1440px] mx-auto px-4">
        {/* Section Title */}
        <div className="flex flex-col md:flex-row md:items-end justify-between border-b border-[#262626] pb-4 mb-6">
          <div>
            <div className="font-mono text-[12px] text-[#737373] uppercase mb-1">
              FEATURE F4 // ACTIVITY VISUALIZATION &amp; SPATIAL PROFILING
            </div>
            <h2 className="text-[24px] md:text-[48px] font-bold uppercase tracking-tight text-[#E8E8E8]">
              HORIZONTAL ANALYSIS TIMELINE
            </h2>
          </div>
          <div className="mt-2 md:mt-0 font-mono text-[12px] text-[#737373]">
            PARTITIONING: {timeline.total_windows} WINDOWS (w={timeline.window_size}) // SPATIAL BYTE OFFSETS
          </div>
        </div>

        {/* Legend */}
        <div className="flex flex-wrap items-center gap-6 font-mono text-[12px] mb-6 p-3 border border-[#262626] bg-[#141414]">
          <span className="text-[#737373] uppercase">TIMELINE LEGEND:</span>
          <span className="flex items-center gap-2">
            <span className="inline-block w-3.5 h-3.5 border border-[#262626] bg-[#0A0A0A]" />
            <span className="text-[#E8E8E8]">NORMAL WINDOW</span>
          </span>
          <span className="flex items-center gap-2">
            <span className="inline-block w-3.5 h-3.5 border border-[#FF6B35] bg-[#FF6B35]/20" />
            <span className="text-[#FF6B35] font-semibold">ANOMALY WINDOW (F2)</span>
          </span>
          <span className="flex items-center gap-2">
            <span className="inline-block w-1 h-3.5 bg-[#262626]" />
            <span className="text-[#737373]">WINDOW BOUNDARY</span>
          </span>
          <span className="flex items-center gap-2">
            <span className="inline-block w-3.5 h-3.5 border border-[#737373] bg-[#141414]" />
            <span className="text-[#E8E8E8]">STREAM EVENT</span>
          </span>
        </div>

        {/* Horizontal Segmented Window Scrub Bar */}
        <div className="border border-[#262626] bg-[#141414] p-4 mb-8">
          <div className="text-[12px] font-mono text-[#737373] mb-2 flex justify-between">
            <span>SCROLL / CLICK WINDOW SEGMENT TO INSPECT OFFSETS:</span>
            <span>
              ACTIVE: WINDOW {currentPoint.window_index} OF {points.length - 1}
            </span>
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
                    title={`Window ${pt.window_index}: Anomaly=${pt.anomaly_score.toFixed(3)}, Severity=${pt.anomaly_severity}`}
                    className={`h-16 px-2.5 flex flex-col justify-between items-center border transition-all cursor-pointer select-none font-mono ${
                      isSelected
                        ? "border-[#E8E8E8] bg-[#1f1f1f] ring-1 ring-[#E8E8E8]"
                        : isAnomaly
                        ? "border-[#FF6B35] bg-[#FF6B35]/15 hover:bg-[#FF6B35]/30 text-[#FF6B35]"
                        : "border-[#262626] bg-[#0A0A0A] hover:border-[#737373] text-[#737373]"
                    }`}
                    style={{ minWidth: "48px" }}
                  >
                    <span className="text-[12px] font-bold">W{pt.window_index}</span>
                    <span
                      className={`text-[12px] ${
                        isAnomaly ? "text-[#FF6B35] font-bold" : "text-[#737373]"
                      }`}
                    >
                      {pt.anomaly_score.toFixed(2)}
                    </span>
                    <div
                      className={`w-full h-1 ${
                        isAnomaly ? "bg-[#FF6B35]" : "bg-[#262626]"
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
          <div className="lg:col-span-8 border border-[#262626] bg-[#141414] p-6">
            <div className="flex flex-wrap items-center justify-between border-b border-[#262626] pb-3 mb-6">
              <div className="font-mono text-[14px] text-[#E8E8E8] font-bold">
                WINDOW INSPECTION // INDEX:{" "}
                <span className="text-[#FF6B35]">W{currentPoint.window_index}</span>
              </div>
              <div className="font-mono text-[12px] flex items-center gap-3">
                <span
                  className={`px-2 py-0.5 border ${
                    currentPoint.is_anomaly
                      ? "border-[#FF6B35] bg-[#FF6B35]/10 text-[#FF6B35]"
                      : "border-[#262626] bg-[#0A0A0A] text-[#737373]"
                  }`}
                >
                  CLASSIFICATION: {currentPoint.anomaly_severity || "NORMAL"}
                </span>
                <span className="text-[#737373]">
                  SCORE: {currentPoint.anomaly_score.toFixed(4)}
                </span>
              </div>
            </div>

            {/* Metrics Breakdown Grid */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 font-mono text-[12px] mb-6">
              <div className="p-3 bg-[#0A0A0A] border border-[#262626]">
                <div className="text-[#737373] text-[12px]">UNIT SPAN:</div>
                <div className="text-[#E8E8E8] font-bold text-[14px] mt-0.5">
                  [{currentPoint.unit_offset_start} - {currentPoint.unit_offset_end}]
                </div>
                <div className="text-[12px] text-[#737373] mt-0.5">
                  Count: {currentPoint.unit_count} units
                </div>
              </div>

              <div className="p-3 bg-[#0A0A0A] border border-[#262626]">
                <div className="text-[#737373] text-[12px]">BYTE OFFSET RANGE:</div>
                <div className="text-[#E8E8E8] font-bold text-[14px] mt-0.5 truncate">
                  0x{currentPoint.byte_offset_start.toString(16).toUpperCase()} - 0x
                  {currentPoint.byte_offset_end.toString(16).toUpperCase()}
                </div>
                <div className="text-[12px] text-[#737373] mt-0.5">
                  Span: {(currentPoint.byte_offset_end - currentPoint.byte_offset_start).toLocaleString("en-US")} bytes
                </div>
              </div>

              <div className="p-3 bg-[#0A0A0A] border border-[#262626]">
                <div className="text-[#737373] text-[12px]">EXTRACTED PAYLOAD:</div>
                <div className="text-[#E8E8E8] font-bold text-[14px] mt-0.5">
                  {currentPoint.payload_bytes.toLocaleString("en-US")} bytes
                </div>
                <div className="text-[12px] text-[#737373] mt-0.5">
                  Health: {currentPoint.health_score.toFixed(1)}%
                </div>
              </div>
            </div>

            {/* Diagnostic Diagnostic Summary & Explanations */}
            <div className="p-4 bg-[#0A0A0A] border border-[#262626] font-mono text-[12px]">
              <div className="text-[#737373] uppercase mb-1">ANOMALY EXPLANATION / FINDINGS:</div>
              <div className="text-[#E8E8E8] leading-relaxed">
                {currentPoint.anomaly_explanation ||
                  "Window adheres to baseline operational profile. Framing syntax, error rates, and multiplex entropy remain within expected Gaussian bounds."}
              </div>
            </div>
          </div>

          {/* Format Specific Parameters & Deviations (4 cols) */}
          <div className="lg:col-span-4 border border-[#262626] bg-[#141414] p-6 flex flex-col justify-between">
            <div>
              <div className="font-mono text-[12px] text-[#737373] uppercase border-b border-[#262626] pb-2 mb-4">
                [WINDOW_INTERNAL_FEATURES]
              </div>

              <div className="space-y-2.5 font-mono text-[12px]">
                {currentPoint.format_specific_metrics &&
                Object.keys(currentPoint.format_specific_metrics).length > 0 ? (
                  Object.entries(currentPoint.format_specific_metrics).map(([k, v]) => (
                    <div
                      key={k}
                      className="flex justify-between items-center p-2 bg-[#0A0A0A] border border-[#262626]"
                    >
                      <span className="text-[#737373] text-[12px] truncate max-w-[140px]">
                        {k}:
                      </span>
                      <span className="text-[#E8E8E8] font-semibold">
                        {typeof v === "number" ? (Number.isInteger(v) ? v : v.toFixed(4)) : String(v)}
                      </span>
                    </div>
                  ))
                ) : (
                  <div className="text-[#737373] text-[12px]">
                    Standard framing metrics registered for this analysis window.
                  </div>
                )}
              </div>
            </div>

            <div className="mt-6 pt-4 border-t border-[#1A1A1A] font-mono text-[12px] text-[#737373]">
              * Note: Segments represent spatial analysis windows partitioned along the stream byte
              stream. Absolute physical timestamps are omitted as uncalibrated raw captures lack GPS/NTP reference.
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};
