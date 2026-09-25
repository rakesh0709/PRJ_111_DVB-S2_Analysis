"use client";

import React, { useState } from "react";
import { OFFLINE_DATA } from "@/lib/offlineData";
import { Tooltip } from "@/components/Tooltip";

export const ComparisonMatrix: React.FC = () => {
  const compData = OFFLINE_DATA.cross_format_comparison;
  const commonMetrics = compData.common?.metrics || compData.common || {};
  const guard = compData.unsupported_inferences_guard || [];

  const [expandedMetric, setExpandedMetric] = useState<string | null>(null);

  const toggleExpand = (metricKey: string) => {
    setExpandedMetric((prev) => (prev === metricKey ? null : metricKey));
  };

  return (
    <section id="comparison" className="w-full border-b border-[var(--border-main)] bg-[var(--bg-main)] py-12 transition-colors duration-150">
      <div className="max-w-[1440px] mx-auto px-4">
        {/* Section Header */}
        <div className="flex flex-col md:flex-row md:items-end justify-between border-b border-[var(--border-main)] pb-4 mb-8">
          <div>
            <div className="font-mono text-[12px] text-[var(--text-muted)] uppercase mb-1 flex items-center gap-2">
              <span>FEATURE F6</span>
              <span>//</span>
              <Tooltip content="Feature F6 imposes a mathematical and architectural barrier: direct arithmetic comparisons are permitted strictly for container-invariant metrics (payload bytes and integrity ratio)">
                <span>CROSS-STREAM COMPARISON &amp; ARCHITECTURAL BARRIER</span>
              </Tooltip>
            </div>
            <h2 className="text-[24px] md:text-[48px] font-bold uppercase tracking-tight text-[var(--text-main)]">
              SEMANTIC COMPARISON MATRIX
            </h2>
          </div>
          <div className="mt-2 md:mt-0 font-mono text-[12px]">
            <span className="px-3 py-1.5 border border-[#FF6B35] bg-[var(--bg-surface)] text-[#FF6B35] font-bold uppercase">
              SEMANTIC COMPARABILITY ENFORCED
            </span>
          </div>
        </div>

        {/* Narrative Description */}
        <div className="p-4 border border-[var(--border-main)] bg-[var(--bg-surface)] mb-8 font-mono text-[12px] text-[var(--text-main)] leading-relaxed">
          <span className="text-[#FF6B35] font-bold mr-2">&gt; AUDIT PRINCIPLE:</span>
          Comparing heterogeneous satellite formats requires strict semantic fencing. Direct numerical
          comparison is permitted <span className="font-bold underline text-[#FF6B35]">only</span> for
          extracted user payload bytes and container integrity ratios. Format-specific framing units
          (188B TS packets vs. variable GSE PDUs vs. 7.2KB Baseband Frames) are fundamentally incommensurable.
        </div>

        {/* The Semantic Shield Table with Sticky First Column */}
        <div className="border border-[var(--border-main)] bg-[var(--bg-surface)] overflow-x-auto mb-8 transition-colors duration-150">
          <table className="w-full border-collapse font-mono text-[12px]">
            <thead>
              <tr className="border-b border-[var(--border-main)] bg-[var(--bg-main)] text-[var(--text-muted)] text-left">
                <th className="p-3 border-r border-[var(--border-main)] sticky left-0 z-20 bg-[var(--bg-main)] whitespace-nowrap min-w-[200px]">
                  METRIC (F6 GATEWAY)
                </th>
                <th className="p-3 border-r border-[var(--border-main)] whitespace-nowrap">
                  STREAM A (MPEG-TS)
                </th>
                <th className="p-3 border-r border-[var(--border-main)] whitespace-nowrap">
                  STREAM B (BBFRAME)
                </th>
                <th className="p-3 border-r border-[var(--border-main)] whitespace-nowrap">
                  DELTA (&Delta;)
                </th>
                <th className="p-3 border-r border-[var(--border-main)] whitespace-nowrap">
                  SEMANTIC STATUS
                </th>
                <th className="p-3 min-w-[340px]">
                  JUSTIFICATION / MATHEMATICAL BARRIER
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[var(--border-dim)] text-[var(--text-main)]">
              {Object.entries(commonMetrics).map(([metricKey, metric]: [string, any]) => {
                const isComparable =
                  metric.classification !== "NOT_COMPARABLE" &&
                  metric.direction !== "NOT_COMPARABLE";
                const isExpanded = expandedMetric === metricKey;

                return (
                  <tr
                    key={metricKey}
                    className={`transition-colors ${
                      isComparable
                        ? "bg-[var(--bg-surface)] hover:bg-[var(--bg-surface-elevated)]"
                        : "bg-[var(--bg-main)] opacity-75 hover:opacity-100"
                    }`}
                  >
                    {/* Sticky Metric Name Column */}
                    <td
                      className={`p-3 border-r border-[var(--border-main)] font-bold whitespace-nowrap sticky left-0 z-10 ${
                        isComparable ? "bg-[var(--bg-surface)]" : "bg-[var(--bg-main)]"
                      }`}
                    >
                      {isComparable ? (
                        <span className="text-[#FF6B35] font-black mr-2">&gt;</span>
                      ) : (
                        <span className="text-[var(--text-muted)] mr-2">&empty;</span>
                      )}
                      <span className={isComparable ? "text-[var(--text-main)]" : "text-[var(--text-muted)]"}>
                        {metric.metric_name}
                      </span>
                    </td>

                    {/* Stream A Value */}
                    <td className="p-3 border-r border-[var(--border-main)] whitespace-nowrap font-medium">
                      {typeof metric.stream_a_value === "number"
                        ? metric.stream_a_value.toLocaleString("en-US")
                        : String(metric.stream_a_value ?? "N/A")}
                      {metric.unit ? ` ${metric.unit}` : ""}
                    </td>

                    {/* Stream B Value */}
                    <td className="p-3 border-r border-[var(--border-main)] whitespace-nowrap font-medium">
                      {typeof metric.stream_b_value === "number"
                        ? metric.stream_b_value.toLocaleString("en-US")
                        : String(metric.stream_b_value ?? "N/A")}
                      {metric.unit ? ` ${metric.unit}` : ""}
                    </td>

                    {/* Delta */}
                    <td className="p-3 border-r border-[var(--border-main)] whitespace-nowrap">
                      {isComparable ? (
                        <span
                          className={`font-semibold ${
                            typeof metric.relative_difference_pct === "number" &&
                            metric.relative_difference_pct < 0
                              ? "text-[#FF6B35]"
                              : "text-[var(--text-main)]"
                          }`}
                        >
                          {typeof metric.relative_difference_pct === "number"
                            ? `${metric.relative_difference_pct > 0 ? "+" : ""}${metric.relative_difference_pct.toFixed(2)}%`
                            : "0.00%"}
                        </span>
                      ) : (
                        <span className="text-[var(--text-muted)] text-[11px] font-mono">
                          [MASKED]
                        </span>
                      )}
                    </td>

                    {/* Distinct Status Badge */}
                    <td className="p-3 border-r border-[var(--border-main)] whitespace-nowrap">
                      {isComparable ? (
                        <span className="px-2 py-0.5 border border-[#FF6B35] text-[#FF6B35] bg-[#FF6B35]/10 font-bold text-[11px] inline-flex items-center gap-1">
                          <span>✓</span> PERMITTED
                        </span>
                      ) : (
                        <span className="px-2 py-0.5 border border-[var(--border-main)] text-[var(--text-muted)] bg-[var(--bg-main)] text-[11px] inline-flex items-center gap-1">
                          <span>∅</span> INCOMMENSURABLE
                        </span>
                      )}
                    </td>

                    {/* Expandable Incompatibility / Description */}
                    <td className="p-3 text-[12px] leading-relaxed">
                      <div className="flex flex-col">
                        <div
                          onClick={() => toggleExpand(metricKey)}
                          className="cursor-pointer flex items-center justify-between text-[var(--text-muted)] hover:text-[var(--text-main)] transition-colors select-none"
                        >
                          <span className="truncate max-w-[280px]">
                            {metric.incompatibility_reason || metric.description}
                          </span>
                          <span className="text-[10px] text-[#FF6B35] ml-2 shrink-0">
                            {isExpanded ? "[COLLAPSE -]" : "[EXPAND +]"}
                          </span>
                        </div>
                        {isExpanded && (
                          <div className="mt-2 p-2.5 bg-[var(--bg-main)] border border-[var(--border-main)] text-[var(--text-main)] text-[11px] leading-normal animate-in fade-in duration-150">
                            <div className="text-[var(--text-muted)] uppercase mb-1 font-semibold">
                              FULL SEMANTIC JUSTIFICATION:
                            </div>
                            {metric.incompatibility_reason || metric.description}
                          </div>
                        )}
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>

        {/* Unsupported Inferences Guard (Physical Layer Boundaries) */}
        <div className="border border-[var(--border-main)] bg-[var(--bg-surface)] p-6 transition-colors duration-150">
          <div className="font-mono text-[12px] text-[#FF6B35] uppercase border-b border-[var(--border-main)] pb-2 mb-4 font-bold flex justify-between items-center">
            <span className="flex items-center gap-2">
              <span className="inline-block w-2 h-2 bg-[#FF6B35]" />
              <span>[SAFETY_POLICY: UNSUPPORTED_INFERENCES_GUARD]</span>
            </span>
            <span className="text-[10px] px-2 py-0.5 bg-[var(--bg-main)] border border-[var(--border-main)] text-[var(--text-main)]">
              ACTIVE ENFORCEMENT
            </span>
          </div>

          <p className="font-mono text-[12px] text-[var(--text-muted)] mb-4 leading-normal">
            The receiver output stream contains only post-demodulated baseband framing. To prevent
            unsubstantiated claims, the following physical-layer inferences are formally prohibited:
          </p>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-3 font-mono text-[12px]">
            {guard.map((item: string, idx: number) => (
              <div
                key={idx}
                className="p-3 bg-[var(--bg-main)] border border-[var(--border-main)] text-[var(--text-main)] hover:border-[#FF6B35] transition-colors"
              >
                <span className="text-[#FF6B35] font-bold mr-2">[GUARD-{idx + 1}]</span>
                <span>{item}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
};
