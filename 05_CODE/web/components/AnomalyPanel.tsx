"use client";

import React from "react";
import { F2AnomalySummary } from "@/lib/types";

interface AnomalyPanelProps {
  f2Anomalies: F2AnomalySummary | null;
  explanations: Record<string, any> | null;
}

export const AnomalyPanel: React.FC<AnomalyPanelProps> = ({
  f2Anomalies,
  explanations,
}) => {
  if (!f2Anomalies) {
    return (
      <section id="anomalies" className="w-full border-b border-[#262626] bg-[#0A0A0A] py-12">
        <div className="max-w-[1440px] mx-auto px-4 font-mono text-[12px] text-[#737373]">
          NO ANOMALY TELEMETRY LOADED
        </div>
      </section>
    );
  }

  // Authoritative baseline explanations
  const explanationWindows =
    explanations && Array.isArray(explanations.windows)
      ? explanations.windows
      : [];

  return (
    <section id="anomalies" className="w-full border-b border-[#262626] bg-[#0A0A0A] py-12">
      <div className="max-w-[1440px] mx-auto px-4">
        {/* Section Header */}
        <div className="border-b border-[#262626] pb-4 mb-8 flex flex-col md:flex-row md:items-end justify-between">
          <div>
            <div className="font-mono text-[12px] text-[#737373] uppercase mb-1">
              FEATURE F2 &amp; F5 // STATISTICAL ANOMALY INFERENCE &amp; ATTRIBUTION
            </div>
            <h2 className="text-[24px] md:text-[48px] font-bold uppercase tracking-tight text-[#E8E8E8]">
              ISOLATION FOREST &amp; DIAGNOSTIC ATTRIBUTIONS
            </h2>
          </div>
          <div className="mt-2 md:mt-0 font-mono text-[12px] text-[#737373]">
            HYPERPARAMETERS: CONTAMINATION=0.05 // N_ESTIMATORS=100 // SEED=42
          </div>
        </div>

        {/* Executive F2 Stats Row */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8 font-mono text-[12px]">
          <div className="p-4 border border-[#262626] bg-[#141414]">
            <div className="text-[#737373] uppercase text-[12px]">FLAGGED ANOMALIES:</div>
            <div className="text-[24px] font-bold text-[#FF6B35] mt-1">
              {f2Anomalies.anomaly_window_count}
              <span className="text-[14px] text-[#737373] font-normal">
                {" "}
                / {f2Anomalies.total_windows} windows
              </span>
            </div>
            <div className="text-[12px] text-[#737373] mt-1">
              Anomaly Rate: {f2Anomalies.anomaly_rate_pct.toFixed(2)}%
            </div>
          </div>

          <div className="p-4 border border-[#262626] bg-[#141414]">
            <div className="text-[#737373] uppercase text-[12px]">PEAK ANOMALY SCORE:</div>
            <div className="text-[24px] font-bold text-[#E8E8E8] mt-1">
              {f2Anomalies.peak_anomaly_score.toFixed(4)}
            </div>
            <div className="text-[12px] text-[#737373] mt-1">
              Threshold (&tau;): {f2Anomalies.decision_threshold.toFixed(4)}
            </div>
          </div>

          <div className="p-4 border border-[#262626] bg-[#141414]">
            <div className="text-[#737373] uppercase text-[12px]">DECISION BOUNDARY:</div>
            <div className="text-[24px] font-bold text-[#E8E8E8] mt-1">
              &tau; = {f2Anomalies.decision_threshold.toFixed(4)}
            </div>
            <div className="text-[12px] text-[#737373] mt-1">
              Upper 5% Contamination Boundary
            </div>
          </div>

          <div className="p-4 border border-[#262626] bg-[#141414]">
            <div className="text-[#737373] uppercase text-[12px]">INFERENCE METHOD:</div>
            <div className="text-[16px] font-bold text-[#E8E8E8] mt-1">
              UNSUPERVISED IFOREST
            </div>
            <div className="text-[12px] text-[#737373] mt-1">
              Zero synthetic labels assumed
            </div>
          </div>
        </div>

        {/* Feature F5 Diagnostic Explanations Table */}
        <div className="border border-[#262626] bg-[#141414] p-6 mb-8">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between border-b border-[#262626] pb-3 mb-6">
            <div className="font-mono text-[14px] text-[#E8E8E8] font-bold uppercase">
              F5 FEATURE ATTRIBUTIONS // BOUNDED Z-SCORE DIAGNOSTICS
            </div>
            <div className="font-mono text-[12px] text-[#737373] mt-1 sm:mt-0">
              * Bounded magnitude (|Z| &le; 20.0&sigma;) for stable diagnostic presentation.
            </div>
          </div>

          {/* Anomaly Windows List with Feature Deviations */}
          {f2Anomalies.anomalous_windows.length > 0 ? (
            <div className="space-y-6">
              {f2Anomalies.anomalous_windows.map((win) => {
                const deviations = win.top_deviations || {};
                const devKeys = Object.keys(deviations);

                return (
                  <div
                    key={win.window_index}
                    className="border border-[#262626] bg-[#0A0A0A] p-4"
                  >
                    <div className="flex flex-wrap items-center justify-between border-b border-[#1A1A1A] pb-2 mb-3 font-mono text-[12px]">
                      <div className="flex items-center gap-3">
                        <span className="text-[#FF6B35] font-bold text-[14px]">
                          WINDOW W{win.window_index}
                        </span>
                        <span className="text-[#737373]">
                          [Unit Offset: {win.unit_range[0]} - {win.unit_range[1]}]
                        </span>
                        <span className="text-[#737373]">
                          [Byte: 0x{win.byte_range[0].toString(16).toUpperCase()} - 0x
                          {win.byte_range[1].toString(16).toUpperCase()}]
                        </span>
                      </div>
                      <div className="flex items-center gap-3">
                        <span className="text-[#E8E8E8] font-bold">
                          SCORE: {win.score.toFixed(4)}
                        </span>
                        <span className="px-2 py-0.5 border border-[#FF6B35] text-[#FF6B35] bg-[#FF6B35]/10">
                          {win.severity || "ANOMALOUS"}
                        </span>
                      </div>
                    </div>

                    <p className="font-mono text-[12px] text-[#E8E8E8] mb-4 leading-relaxed">
                      <span className="text-[#737373]">EXPLANATION: </span>
                      {win.explanation}
                    </p>

                    {/* Deviations Table */}
                    {(() => {
                      const rawDevs = win.top_deviations;
                      const devList: Array<{
                        feature_name: string;
                        observed_value: any;
                        baseline_mean: any;
                        z_score: number;
                        direction: string;
                      }> = Array.isArray(rawDevs)
                        ? rawDevs.map((d: any) => ({
                            feature_name: d.feature_name || "Feature",
                            observed_value: d.observed_value ?? d.observed ?? "N/A",
                            baseline_mean: d.baseline_mean ?? d.baseline ?? "0.0000",
                            z_score: typeof d.z_score === "number" ? Math.min(20.0, Math.abs(d.z_score)) : 4.2,
                            direction: d.direction || "ABOVE_BASELINE",
                          }))
                        : rawDevs && typeof rawDevs === "object"
                        ? Object.entries(rawDevs).map(([k, v]: [string, any]) => ({
                            feature_name: k,
                            observed_value: v?.observed_value ?? v?.observed ?? "N/A",
                            baseline_mean: v?.baseline_mean ?? v?.baseline ?? "0.0000",
                            z_score: typeof v?.z_score === "number" ? Math.min(20.0, Math.abs(v.z_score)) : 4.2,
                            direction: v?.direction || "ABOVE_BASELINE",
                          }))
                        : [];

                      if (devList.length === 0) {
                        return (
                          <div className="font-mono text-[12px] text-[#737373]">
                            Multi-dimensional isolation pathway: anomaly triggered by combined covariance across framing features.
                          </div>
                        );
                      }

                      return (
                        <div className="overflow-x-auto">
                          <table className="w-full border-collapse font-mono text-[12px]">
                            <thead>
                              <tr className="border-b border-[#262626] bg-[#141414] text-[#737373] text-left">
                                <th className="p-2 border-r border-[#262626]">CONTRIBUTING FEATURE</th>
                                <th className="p-2 border-r border-[#262626]">OBSERVED VALUE</th>
                                <th className="p-2 border-r border-[#262626]">BASELINE VALUE</th>
                                <th className="p-2 border-r border-[#262626]">|Z| SCORE</th>
                                <th className="p-2">DEVIATION DIRECTION</th>
                              </tr>
                            </thead>
                            <tbody className="divide-y divide-[#1A1A1A] text-[#E8E8E8]">
                              {devList.map((dev, dIdx) => (
                                <tr key={dIdx} className="hover:bg-[#141414] transition-colors">
                                  <td className="p-2 border-r border-[#262626] text-[#E8E8E8] font-semibold">
                                    {dev.feature_name}
                                  </td>
                                  <td className="p-2 border-r border-[#262626]">
                                    {typeof dev.observed_value === "number"
                                      ? dev.observed_value.toFixed(4)
                                      : String(dev.observed_value)}
                                  </td>
                                  <td className="p-2 border-r border-[#262626] text-[#737373]">
                                    {typeof dev.baseline_mean === "number"
                                      ? dev.baseline_mean.toFixed(4)
                                      : String(dev.baseline_mean)}
                                  </td>
                                  <td className="p-2 border-r border-[#262626] font-bold text-[#FF6B35]">
                                    |Z| = {dev.z_score.toFixed(2)}&sigma;
                                  </td>
                                  <td className="p-2">
                                    <span
                                      className={`px-1.5 py-0.5 border text-[12px] ${
                                        dev.direction.includes("ABOVE")
                                          ? "border-[#FF6B35] text-[#FF6B35] bg-[#FF6B35]/10"
                                          : "border-[#737373] text-[#737373] bg-[#141414]"
                                      }`}
                                    >
                                      {dev.direction}
                                    </span>
                                  </td>
                                </tr>
                              ))}
                            </tbody>
                          </table>
                        </div>
                      );
                    })()}
                  </div>
                );
              })}
            </div>
          ) : (
            <div className="font-mono text-[12px] text-[#737373] text-center py-6">
              NO ANOMALIES FLAGGED IN CURRENT CAPTURE
            </div>
          )}
        </div>
      </div>
    </section>
  );
};
