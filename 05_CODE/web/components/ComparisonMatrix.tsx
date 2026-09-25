"use client";

import React from "react";
import { OFFLINE_DATA } from "@/lib/offlineData";

export const ComparisonMatrix: React.FC = () => {
  const compData = OFFLINE_DATA.cross_format_comparison;
  const commonMetrics = compData.common?.metrics || compData.common || {};
  const guard = compData.unsupported_inferences_guard || [];

  return (
    <section id="comparison" className="w-full border-b border-[#262626] bg-[#0A0A0A] py-12">
      <div className="max-w-[1440px] mx-auto px-4">
        {/* Section Header */}
        <div className="flex flex-col md:flex-row md:items-end justify-between border-b border-[#262626] pb-4 mb-8">
          <div>
            <div className="font-mono text-[12px] text-[#737373] uppercase mb-1">
              FEATURE F6 // CROSS-STREAM COMPARISON &amp; ARCHITECTURAL BARRIER
            </div>
            <h2 className="text-[24px] md:text-[48px] font-bold uppercase tracking-tight text-[#E8E8E8]">
              SEMANTIC COMPARISON MATRIX
            </h2>
          </div>
          <div className="mt-2 md:mt-0 font-mono text-[12px]">
            <span className="px-3 py-1 border border-[#FF6B35] bg-[#141414] text-[#FF6B35] font-bold uppercase">
              SEMANTIC COMPARABILITY ENFORCED
            </span>
          </div>
        </div>

        {/* Narrative Description */}
        <div className="p-4 border border-[#262626] bg-[#141414] mb-8 font-mono text-[12px] text-[#E8E8E8] leading-relaxed">
          <span className="text-[#FF6B35] font-bold mr-2">&gt; AUDIT PRINCIPLE:</span>
          Comparing heterogeneous satellite formats requires strict semantic fencing. Direct numerical
          comparison is permitted <span className="font-bold underline text-white">only</span> for
          extracted user payload bytes and container integrity ratios. Format-specific framing units
          (188B TS packets vs. variable GSE PDUs vs. 7.2KB Baseband Frames) are fundamentally incommensurable.
        </div>

        {/* The Semantic Shield Table */}
        <div className="border border-[#262626] bg-[#141414] overflow-x-auto mb-8">
          <table className="w-full border-collapse font-mono text-[12px]">
            <thead>
              <tr className="border-b border-[#262626] bg-[#0A0A0A] text-[#737373] text-left">
                <th className="p-3 border-r border-[#262626]">METRIC</th>
                <th className="p-3 border-r border-[#262626]">STREAM A (MPEG-TS)</th>
                <th className="p-3 border-r border-[#262626]">STREAM B (BBFRAME)</th>
                <th className="p-3 border-r border-[#262626]">DELTA (&Delta;)</th>
                <th className="p-3 border-r border-[#262626]">STATUS</th>
                <th className="p-3">SEMANTIC JUSTIFICATION / INCOMPATIBILITY REASON</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#1A1A1A] text-[#E8E8E8]">
              {Object.entries(commonMetrics).map(([metricKey, metric]: [string, any]) => {
                const isComparable =
                  metric.classification !== "NOT_COMPARABLE" &&
                  metric.direction !== "NOT_COMPARABLE";

                return (
                  <tr
                    key={metricKey}
                    className={`transition-colors ${
                      isComparable
                        ? "bg-[#141414] hover:bg-[#1a1a1a]"
                        : "bg-[#0A0A0A] opacity-60 hover:opacity-100"
                    }`}
                  >
                    {/* Metric Name */}
                    <td className="p-3 border-r border-[#262626] font-bold whitespace-nowrap">
                      {isComparable ? (
                        <span className="text-[#FF6B35] mr-1.5">&gt;</span>
                      ) : (
                        <span className="text-[#737373] mr-1.5">&empty;</span>
                      )}
                      {metric.metric_name}
                    </td>

                    {/* Stream A Value */}
                    <td className="p-3 border-r border-[#262626] whitespace-nowrap">
                      {typeof metric.stream_a_value === "number"
                        ? metric.stream_a_value.toLocaleString("en-US")
                        : String(metric.stream_a_value ?? "N/A")}
                      {metric.unit || ""}
                    </td>

                    {/* Stream B Value */}
                    <td className="p-3 border-r border-[#262626] whitespace-nowrap">
                      {typeof metric.stream_b_value === "number"
                        ? metric.stream_b_value.toLocaleString("en-US")
                        : String(metric.stream_b_value ?? "N/A")}
                      {metric.unit || ""}
                    </td>

                    {/* Delta */}
                    <td className="p-3 border-r border-[#262626] whitespace-nowrap">
                      {isComparable ? (
                        <span
                          className={
                            typeof metric.relative_difference_pct === "number" &&
                            metric.relative_difference_pct < 0
                              ? "text-[#FF6B35] font-semibold"
                              : "text-[#E8E8E8]"
                          }
                        >
                          {typeof metric.relative_difference_pct === "number"
                            ? `${metric.relative_difference_pct > 0 ? "+" : ""}${metric.relative_difference_pct.toFixed(2)}%`
                            : "0.00%"}
                        </span>
                      ) : (
                        <span className="text-[#737373]">N/A [MASKED]</span>
                      )}
                    </td>

                    {/* Status Badge */}
                    <td className="p-3 border-r border-[#262626] whitespace-nowrap">
                      <span
                        className={`px-2 py-0.5 border text-[12px] ${
                          isComparable
                            ? "border-[#E8E8E8] text-[#E8E8E8] bg-[#1f1f1f] font-bold"
                            : "border-[#262626] text-[#737373] bg-[#0A0A0A]"
                        }`}
                      >
                        {isComparable ? "PERMITTED" : "INCOMMENSURABLE"}
                      </span>
                    </td>

                    {/* Incompatibility / Description */}
                    <td className="p-3 text-[#737373] text-[12px] leading-relaxed">
                      {metric.incompatibility_reason || metric.description}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>

        {/* Unsupported Inferences Guard (Physical Layer Boundaries) */}
        <div className="border border-[#262626] bg-[#141414] p-6">
          <div className="font-mono text-[12px] text-[#FF6B35] uppercase border-b border-[#262626] pb-2 mb-4 font-bold flex justify-between">
            <span>[SAFETY_POLICY: UNSUPPORTED_INFERENCES_GUARD]</span>
            <span>ACTIVE PROTECTION</span>
          </div>

          <p className="font-mono text-[12px] text-[#737373] mb-4">
            The receiver output stream contains only post-demodulated baseband framing. To prevent
            unsubstantiated claims, the following physical-layer inferences are formally prohibited:
          </p>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-3 font-mono text-[12px]">
            {guard.map((item: string, idx: number) => (
              <div key={idx} className="p-3 bg-[#0A0A0A] border border-[#262626] text-[#E8E8E8]">
                <span className="text-[#FF6B35] font-bold mr-2">[GUARD-{idx + 1}]</span>
                {item}
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
};
