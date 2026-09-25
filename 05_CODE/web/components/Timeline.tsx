"use client";

import React, { useState } from "react";
import { TimelineData, TimelinePoint } from "@/lib/types";

interface TimelineProps {
  timeline: TimelineData | null;
}

export const Timeline: React.FC<TimelineProps> = ({ timeline }) => {
  const [selectedPointIndex, setSelectedPointIndex] = useState<number>(0);
  const [hoveredIndex, setHoveredIndex] = useState<number | null>(null);

  if (!timeline || !timeline.points || timeline.points.length === 0) {
    return (
      <section id="timeline" className="w-full border-b border-[var(--border-main)] bg-[var(--bg-main)] py-12 transition-colors duration-150">
        <div className="max-w-[1440px] mx-auto px-4 font-mono text-[12px] text-[var(--text-muted)]">
          NO TIMELINE DATA AVAILABLE
        </div>
      </section>
    );
  }

  const points = timeline.points;
  const currentPoint: TimelinePoint = points[selectedPointIndex] || points[0];
  const threshold = timeline.anomaly_threshold || 0.5;

  // SVG Chart Geometry
  const chartW = 900;
  const chartH = 140;
  const padL = 45;
  const padR = 45;
  const padT = 20;
  const padB = 25;
  const innerW = chartW - padL - padR;
  const innerH = chartH - padT - padB;
  const n = points.length;

  const getX = (idx: number) => {
    if (n <= 1) return padL + innerW / 2;
    return padL + (idx / (n - 1)) * innerW;
  };

  const getYHealth = (score: number) => {
    const clamped = Math.max(0, Math.min(100, score));
    return padT + (1 - clamped / 100) * innerH;
  };

  const getYAnom = (score: number) => {
    const clamped = Math.max(0, Math.min(1.0, score));
    return padT + (1 - clamped) * innerH;
  };

  // Build SVG Paths
  const healthPath = points.map((p, i) => `${i === 0 ? "M" : "L"} ${getX(i).toFixed(1)} ${getYHealth(p.health_score).toFixed(1)}`).join(" ");
  const healthArea = `${healthPath} L ${getX(n - 1).toFixed(1)} ${(padT + innerH).toFixed(1)} L ${getX(0).toFixed(1)} ${(padT + innerH).toFixed(1)} Z`;
  const anomPath = points.map((p, i) => `${i === 0 ? "M" : "L"} ${getX(i).toFixed(1)} ${getYAnom(p.anomaly_score).toFixed(1)}`).join(" ");
  const threshY = getYAnom(threshold);

  const activeIdx = hoveredIndex !== null ? hoveredIndex : selectedPointIndex;
  const activePt = points[activeIdx] || currentPoint;

  return (
    <section id="timeline" className="w-full border-b border-[var(--border-main)] bg-[var(--bg-main)] py-12 transition-colors duration-150">
      <div className="max-w-[1440px] mx-auto px-4">
        {/* Section Title */}
        <div className="flex flex-col md:flex-row md:items-end justify-between border-b border-[var(--border-main)] pb-4 mb-6">
          <div>
            <div className="text-xs font-semibold text-[var(--text-muted)] tracking-wider uppercase mb-1 flex items-center gap-2">
              <span>FEATURE F4</span>
              <span>•</span>
              <span className="text-[var(--text-main)] font-mono">ACTIVITY VISUALIZATION &amp; SPATIAL PROFILING</span>
            </div>
            <h2 className="text-[24px] md:text-[44px] font-bold uppercase tracking-tight text-[var(--text-main)]">
              STREAM HEALTH &amp; ANOMALY TIMELINE
            </h2>
          </div>
          <div className="mt-2 md:mt-0 font-mono text-[12px] text-[var(--text-muted)]">
            PARTITIONING: {timeline.total_windows} WINDOWS (w={timeline.window_size}) // SPATIAL BYTE OFFSETS
          </div>
        </div>

        {/* Dynamic Trajectory SVG Graph Card */}
        <div className="border border-[var(--border-main)] bg-[var(--bg-surface)] p-5 mb-6">
          <div className="flex flex-wrap items-center justify-between gap-4 mb-3 pb-3 border-b border-[var(--border-dim)]">
            <div className="flex items-center gap-2">
              <span className="text-xs font-semibold uppercase tracking-wider text-[var(--text-main)]">
                Rolling Trajectory Graph:
              </span>
              <span className="text-xs font-mono text-[var(--text-muted)]">
                (Click or hover point to inspect)
              </span>
            </div>

            {/* Trajectory Legend */}
            <div className="flex flex-wrap items-center gap-5 text-xs font-mono">
              <span className="flex items-center gap-1.5">
                <span className="w-3 h-1 bg-emerald-400 inline-block" />
                <span className="text-emerald-400 font-semibold">STREAM HEALTH (0-100%)</span>
              </span>
              <span className="flex items-center gap-1.5">
                <span className="w-3 h-1 bg-[#FF6B35] inline-block" />
                <span className="text-[#FF6B35] font-semibold">ANOMALY SCORE (0-1.0)</span>
              </span>
              <span className="flex items-center gap-1.5">
                <span className="w-3 h-0.5 border-t border-dashed border-[#FF6B35]/70 inline-block" />
                <span className="text-[var(--text-muted)]">THRESHOLD (&tau;={threshold.toFixed(2)})</span>
              </span>
              <span className="text-[var(--text-main)] font-bold bg-[var(--bg-main)] px-2 py-0.5 border border-[var(--border-main)]">
                ACTIVE: W{activePt.window_index}
              </span>
            </div>
          </div>

          {/* SVG Canvas */}
          <div className="w-full overflow-hidden select-none">
            <svg
              viewBox={`0 0 ${chartW} ${chartH}`}
              className="w-full h-auto max-h-[220px]"
              preserveAspectRatio="none"
            >
              {/* Horizontal Grid Lines */}
              {[0, 0.25, 0.5, 0.75, 1.0].map((ratio) => {
                const y = padT + (1 - ratio) * innerH;
                return (
                  <g key={ratio}>
                    <line
                      x1={padL}
                      y1={y}
                      x2={padL + innerW}
                      y2={y}
                      stroke="var(--border-dim)"
                      strokeWidth="1"
                    />
                    <text
                      x={padL - 6}
                      y={y + 3}
                      fill="var(--text-muted)"
                      fontSize="9"
                      fontFamily="monospace"
                      textAnchor="end"
                    >
                      {Math.round(ratio * 100)}%
                    </text>
                    <text
                      x={padL + innerW + 6}
                      y={y + 3}
                      fill="var(--text-muted)"
                      fontSize="9"
                      fontFamily="monospace"
                      textAnchor="start"
                    >
                      {ratio.toFixed(2)}
                    </text>
                  </g>
                );
              })}

              {/* Decision Threshold Line */}
              <line
                x1={padL}
                y1={threshY}
                x2={padL + innerW}
                y2={threshY}
                stroke="#FF6B35"
                strokeWidth="1.5"
                strokeDasharray="4 3"
                opacity="0.6"
              />

              {/* Health Area Fill */}
              <path d={healthArea} fill="rgba(16, 185, 129, 0.08)" />

              {/* Health Line (Emerald Green) */}
              <path
                d={healthPath}
                fill="none"
                stroke="#10B981"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              />

              {/* Anomaly Line (Orange) */}
              <path
                d={anomPath}
                fill="none"
                stroke="#FF6B35"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              />

              {/* Anomalous Outlier Marker Points */}
              {points.map((pt, idx) => {
                if (!pt.is_anomaly) return null;
                const cx = getX(idx);
                const cy = getYAnom(pt.anomaly_score);
                return (
                  <circle
                    key={`anom-pt-${idx}`}
                    cx={cx}
                    cy={cy}
                    r="4"
                    fill="#FF6B35"
                    stroke="#FFFFFF"
                    strokeWidth="1.5"
                    className="cursor-pointer"
                    onClick={() => setSelectedPointIndex(idx)}
                  />
                );
              })}

              {/* Active Inspection Cursor Vertical Guide */}
              <line
                x1={getX(activeIdx)}
                y1={padT}
                x2={getX(activeIdx)}
                y2={padT + innerH}
                stroke="var(--text-main)"
                strokeWidth="1.5"
                strokeDasharray="2 2"
                opacity="0.8"
              />

              {/* Active Marker on Health Curve */}
              <circle
                cx={getX(activeIdx)}
                cy={getYHealth(activePt.health_score)}
                r="4.5"
                fill="#10B981"
                stroke="var(--bg-main)"
                strokeWidth="2"
              />

              {/* Active Marker on Anomaly Curve */}
              <circle
                cx={getX(activeIdx)}
                cy={getYAnom(activePt.anomaly_score)}
                r="4.5"
                fill="#FF6B35"
                stroke="var(--bg-main)"
                strokeWidth="2"
              />

              {/* Interactive Hit Areas */}
              {points.map((pt, idx) => {
                const segW = innerW / Math.max(1, n - 1);
                const hitX = getX(idx) - segW / 2;
                return (
                  <rect
                    key={`hit-${idx}`}
                    x={Math.max(padL, hitX)}
                    y={padT}
                    width={Math.max(12, segW)}
                    height={innerH}
                    fill="transparent"
                    className="cursor-pointer"
                    onMouseEnter={() => setHoveredIndex(idx)}
                    onMouseLeave={() => setHoveredIndex(null)}
                    onClick={() => setSelectedPointIndex(idx)}
                  >
                    <title>{`Window W${pt.window_index}: Health=${pt.health_score.toFixed(1)}%, Anomaly=${pt.anomaly_score.toFixed(3)}`}</title>
                  </rect>
                );
              })}
            </svg>
          </div>
        </div>

        {/* Horizontal Segmented Window Scrub Bar */}
        <div className="border border-[var(--border-main)] bg-[var(--bg-surface)] p-4 mb-8">
          <div className="text-xs font-mono text-[var(--text-muted)] mb-2 flex justify-between">
            <span>SCROLL / CLICK WINDOW SEGMENT TO INSPECT OFFSETS:</span>
            <span className="text-[var(--text-main)] font-semibold">
              ACTIVE: WINDOW W{currentPoint.window_index} OF {points.length - 1}
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
                    title={`Window ${pt.window_index}: Anomaly=${pt.anomaly_score.toFixed(3)}, Severity=${pt.anomaly_severity || "NORMAL"}`}
                    className={`h-16 px-2.5 flex flex-col justify-between items-center border transition-all cursor-pointer select-none font-mono ${
                      isSelected
                        ? "border-[#FF6B35] bg-[#FF6B35]/20 ring-1 ring-[#FF6B35]"
                        : isAnomaly
                        ? "border-[#FF6B35] bg-[#FF6B35]/15 hover:bg-[#FF6B35]/30 text-[#FF6B35]"
                        : "border-[var(--border-main)] bg-[var(--bg-main)] hover:border-[var(--text-muted)] text-[var(--text-muted)]"
                    }`}
                    style={{ minWidth: "48px" }}
                  >
                    <span className="text-[12px] font-bold">W{pt.window_index}</span>
                    <span
                      className={`text-[12px] ${
                        isAnomaly ? "text-[#FF6B35] font-bold" : "text-[var(--text-muted)]"
                      }`}
                    >
                      {pt.anomaly_score.toFixed(2)}
                    </span>
                    <div
                      className={`w-full h-1 ${
                        isAnomaly ? "bg-[#FF6B35]" : isSelected ? "bg-emerald-400" : "bg-[var(--border-main)]"
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
          <div className="lg:col-span-8 border border-[var(--border-main)] bg-[var(--bg-surface)] p-6">
            <div className="flex flex-wrap items-center justify-between border-b border-[var(--border-main)] pb-3 mb-6">
              <div className="font-mono text-[14px] text-[var(--text-main)] font-bold">
                WINDOW INSPECTION // INDEX:{" "}
                <span className="text-[#FF6B35]">W{currentPoint.window_index}</span>
              </div>
              <div className="font-mono text-[12px] flex items-center gap-3">
                <span
                  className={`px-2 py-0.5 border ${
                    currentPoint.is_anomaly
                      ? "border-[#FF6B35] bg-[#FF6B35]/10 text-[#FF6B35]"
                      : "border-emerald-500/40 bg-emerald-500/10 text-emerald-400"
                  }`}
                >
                  CLASSIFICATION: {currentPoint.anomaly_severity || "NORMAL"}
                </span>
                <span className="text-[var(--text-muted)]">
                  SCORE: <span className="text-[var(--text-main)] font-semibold">{currentPoint.anomaly_score.toFixed(4)}</span>
                </span>
              </div>
            </div>

            {/* Metrics Breakdown Grid */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 font-mono text-[12px] mb-6">
              <div className="p-3 bg-[var(--bg-main)] border border-[var(--border-main)]">
                <div className="text-[var(--text-muted)] text-[12px]">UNIT SPAN:</div>
                <div className="text-[var(--text-main)] font-bold text-[14px] mt-0.5">
                  [{currentPoint.unit_offset_start} - {currentPoint.unit_offset_end}]
                </div>
                <div className="text-[12px] text-[var(--text-muted)] mt-0.5">
                  Count: {currentPoint.unit_count} units
                </div>
              </div>

              <div className="p-3 bg-[var(--bg-main)] border border-[var(--border-main)]">
                <div className="text-[var(--text-muted)] text-[12px]">BYTE OFFSET RANGE:</div>
                <div className="text-[var(--text-main)] font-bold text-[14px] mt-0.5 truncate">
                  0x{currentPoint.byte_offset_start.toString(16).toUpperCase()} - 0x
                  {currentPoint.byte_offset_end.toString(16).toUpperCase()}
                </div>
                <div className="text-[12px] text-[var(--text-muted)] mt-0.5">
                  Span: {(currentPoint.byte_offset_end - currentPoint.byte_offset_start).toLocaleString("en-US")} bytes
                </div>
              </div>

              <div className="p-3 bg-[var(--bg-main)] border border-[var(--border-main)]">
                <div className="text-[var(--text-muted)] text-[12px]">EXTRACTED PAYLOAD:</div>
                <div className="text-[var(--text-main)] font-bold text-[14px] mt-0.5">
                  {currentPoint.payload_bytes.toLocaleString("en-US")} bytes
                </div>
                <div className="text-[12px] text-emerald-400 mt-0.5">
                  Health: {currentPoint.health_score.toFixed(1)}%
                </div>
              </div>
            </div>

            {/* Diagnostic Diagnostic Summary & Explanations */}
            <div className="p-4 bg-[var(--bg-main)] border border-[var(--border-main)]">
              <div className="text-xs font-semibold text-[var(--text-muted)] uppercase mb-1.5 tracking-wider">
                ANOMALY EXPLANATION / FINDINGS:
              </div>
              <div className="text-[13px] text-[var(--text-main)] leading-relaxed">
                {currentPoint.anomaly_explanation ||
                  "Window adheres to baseline operational profile. Framing syntax, error rates, and multiplex entropy remain within expected Gaussian bounds."}
              </div>
            </div>
          </div>

          {/* Format Specific Parameters & Deviations (4 cols) */}
          <div className="lg:col-span-4 border border-[var(--border-main)] bg-[var(--bg-surface)] p-6 flex flex-col justify-between">
            <div>
              <div className="text-xs font-semibold text-[var(--text-muted)] uppercase border-b border-[var(--border-main)] pb-2 mb-4 tracking-wider">
                WINDOW INTERNAL FEATURES
              </div>

              <div className="space-y-2.5 font-mono text-[12px]">
                {currentPoint.format_specific_metrics &&
                Object.keys(currentPoint.format_specific_metrics).length > 0 ? (
                  Object.entries(currentPoint.format_specific_metrics).map(([k, v]) => (
                    <div
                      key={k}
                      className="flex justify-between items-center p-2 bg-[var(--bg-main)] border border-[var(--border-main)]"
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

            <div className="mt-6 pt-4 border-t border-[var(--border-dim)] text-[11px] text-[var(--text-muted)] leading-relaxed">
              * Note: Segments represent spatial analysis windows partitioned along the stream byte
              stream. Absolute physical timestamps are omitted as uncalibrated raw captures lack GPS/NTP reference.
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};
