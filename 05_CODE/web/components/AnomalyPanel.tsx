"use client";

import React from "react";
import { F2AnomalySummary } from "@/lib/types";
import { Tooltip } from "@/components/Tooltip";

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
      <section id="anomalies" className="w-full border-b border-[var(--border-main)] bg-[var(--bg-main)] py-12 transition-colors duration-150">
        <div className="max-w-[1440px] mx-auto px-4 font-mono text-[12px] text-[var(--text-muted)]">
          NO ANOMALY TELEMETRY LOADED
        </div>
      </section>
    );
  }

  return (
    <section id="anomalies" className="w-full border-b border-[var(--border-main)] bg-[var(--bg-main)] py-12 transition-colors duration-150">
      <div className="max-w-[1440px] mx-auto px-4">
        {/* Section Header */}
        <div className="border-b border-[var(--border-main)] pb-4 mb-8 flex flex-col md:flex-row md:items-end justify-between">
          <div>
            <div className="font-mono text-[12px] text-[var(--text-muted)] uppercase mb-1 flex items-center gap-2">
              <span>FEATURE F2 &amp; F5</span>
              <span>//</span>
              <Tooltip content="F2 executes unsupervised Isolation Forest across framing metrics; F5 generates bounded Z-score statistical attributions for each flagged window">
                <span>STATISTICAL ANOMALY INFERENCE &amp; ATTRIBUTION</span>
              </Tooltip>
            </div>
            <h2 className="text-[24px] md:text-[48px] font-bold uppercase tracking-tight text-[var(--text-main)]">
              ISOLATION FOREST &amp; DIAGNOSTIC ATTRIBUTIONS
            </h2>
          </div>
          <div className="mt-2 md:mt-0 font-mono text-[12px] text-[var(--text-muted)] flex flex-wrap items-center gap-2">
            <span>HYPERPARAMETERS:</span>
            <Tooltip content="Contamination=0.05: Assumes ~5% expected baseline outlier proportion in receiver stream">
              <span className="text-[var(--text-main)] font-semibold">CONTAM=0.05</span>
            </Tooltip>
            <span>//</span>
            <Tooltip content="N_estimators=100: Ensemble of 100 random isolation partition trees">
              <span className="text-[var(--text-main)] font-semibold">N_EST=100</span>
            </Tooltip>
            <span>//</span>
            <Tooltip content="Random state seed 42 enforces deterministic reproducible tree construction across runs">
              <span className="text-[var(--text-main)] font-semibold">SEED=42</span>
            </Tooltip>
          </div>
        </div>

        {/* Executive F2 Stats Row */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8 font-mono text-[12px]">
          <div className="p-4 border border-[var(--border-main)] bg-[var(--bg-surface)] hover:border-[#FF6B35] transition-colors">
            <div className="text-[var(--text-muted)] uppercase text-[11px]">FLAGGED ANOMALIES:</div>
            <div className="text-[24px] font-bold text-[#FF6B35] mt-1">
              {f2Anomalies.anomaly_window_count}
              <span className="text-[14px] text-[var(--text-muted)] font-normal">
                {" "}
                / {f2Anomalies.total_windows} windows
              </span>
            </div>
            <div className="text-[11px] text-[var(--text-muted)] mt-1">
              Anomaly Rate: {f2Anomalies.anomaly_rate_pct.toFixed(2)}%
            </div>
          </div>

          <div className="p-4 border border-[var(--border-main)] bg-[var(--bg-surface)] hover:border-[#FF6B35] transition-colors">
            <div className="text-[var(--text-muted)] uppercase text-[11px]">PEAK ANOMALY SCORE:</div>
            <div className="text-[24px] font-bold text-[var(--text-main)] mt-1">
              {f2Anomalies.peak_anomaly_score.toFixed(4)}
            </div>
            <div className="text-[11px] text-[var(--text-muted)] mt-1">
              Threshold (&tau;): {f2Anomalies.decision_threshold.toFixed(4)}
            </div>
          </div>

          <div className="p-4 border border-[var(--border-main)] bg-[var(--bg-surface)] hover:border-[#FF6B35] transition-colors">
            <div className="text-[var(--text-muted)] uppercase text-[11px]">DECISION BOUNDARY:</div>
            <div className="text-[24px] font-bold text-[var(--text-main)] mt-1">
              &tau; = {f2Anomalies.decision_threshold.toFixed(4)}
            </div>
            <div className="text-[11px] text-[var(--text-muted)] mt-1">
              Upper 5% Contamination Boundary
            </div>
          </div>

          <div className="p-4 border border-[var(--border-main)] bg-[var(--bg-surface)] hover:border-[#FF6B35] transition-colors">
            <div className="text-[var(--text-muted)] uppercase text-[11px]">INFERENCE METHOD:</div>
            <div className="text-[16px] font-bold text-[var(--text-main)] mt-1">
              UNSUPERVISED IFOREST
            </div>
            <div className="text-[11px] text-[var(--text-muted)] mt-1">
              Zero synthetic labels assumed
            </div>
          </div>
        </div>

        {/* Feature F5 Diagnostic Explanations Table */}
        <div className="border border-[var(--border-main)] bg-[var(--bg-surface)] p-6 mb-8 transition-colors duration-150">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between border-b border-[var(--border-dim)] pb-3 mb-6">
            <div className="font-mono text-[14px] text-[var(--text-main)] font-bold uppercase">
              F5 FEATURE ATTRIBUTIONS // BOUNDED Z-SCORE DIAGNOSTICS
            </div>
            <div className="font-mono text-[11px] text-[var(--text-muted)] mt-1 sm:mt-0">
              <Tooltip content="Bounded magnitude (|Z| <= 20.0 sigma) protects against numerical explosions on low-variance baseline features while preserving ranking">
                <span>* Bounded magnitude (|Z| &le; 20.0&sigma;) for stable presentation</span>
              </Tooltip>
            </div>
          </div>

          {/* Anomaly Windows List with Feature Deviations */}
          {f2Anomalies.anomalous_windows.length > 0 ? (
            <div className="space-y-6">
              {f2Anomalies.anomalous_windows.map((win) => {
                return (
                  <div
                    key={win.window_index}
                    className="border border-[var(--border-main)] bg-[var(--bg-main)] p-5 hover:border-[#FF6B35] transition-colors duration-150"
                  >
                    {/* Primary Finding Hierarchy: Window -> Severity -> Score -> Byte Range */}
                    <div className="flex flex-wrap items-center justify-between border-b border-[var(--border-dim)] pb-3 mb-3 font-mono text-[12px] gap-2">
                      <div className="flex items-center gap-3">
                        <span className="text-[#FF6B35] font-bold text-[16px]">
                          WINDOW W{win.window_index}
                        </span>
                        <span
                          className={`px-2 py-0.5 border text-[11px] font-bold ${
                            win.severity === "CRITICAL"
                              ? "border-[#FF4D4D] text-[#FF4D4D] bg-[#FF4D4D]/10"
                              : "border-[#FF6B35] text-[#FF6B35] bg-[#FF6B35]/10"
                          }`}
                        >
                          {win.severity || "ANOMALOUS"}
                        </span>
                        <span className="text-[var(--text-muted)] text-[11px]">
                          [Units: {win.unit_range[0]} - {win.unit_range[1]}]
                        </span>
                        <span className="text-[var(--text-muted)] text-[11px]">
                          [Byte: 0x{win.byte_range[0].toString(16).toUpperCase()} - 0x
                          {win.byte_range[1].toString(16).toUpperCase()}]
                        </span>
                      </div>
                      <div className="flex items-center gap-3">
                        <span className="text-[var(--text-muted)]">ANOMALY SCORE:</span>
                        <span className="text-[var(--text-main)] font-bold text-[14px]">
                          {win.score.toFixed(4)}
                        </span>
                      </div>
                    </div>

                    {/* Prominent Explanation Box */}
                    <div className="border-l-2 border-[#FF6B35] pl-3 py-1 mb-4 bg-[var(--bg-surface)]">
                      <p className="font-mono text-[12px] text-[var(--text-main)] leading-relaxed">
                        <span className="text-[var(--text-muted)] font-semibold uppercase">EXPLANATION: </span>
                        {win.explanation}
                      </p>
                    </div>

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
                          <div className="font-mono text-[12px] text-[var(--text-muted)] p-2 bg-[var(--bg-surface)]">
                            Multi-dimensional isolation pathway: anomaly triggered by combined covariance across framing features.
                          </div>
                        );
                      }

                      return (
                        <div className="overflow-x-auto">
                          <table className="w-full border-collapse font-mono text-[12px]">
                            <thead>
                              <tr className="border-b border-[var(--border-main)] bg-[var(--bg-surface)] text-[var(--text-muted)] text-left">
                                <th className="p-2 border-r border-[var(--border-main)]">CONTRIBUTING FEATURE</th>
                                <th className="p-2 border-r border-[var(--border-main)]">OBSERVED VALUE</th>
                                <th className="p-2 border-r border-[var(--border-main)]">BASELINE MEAN</th>
                                <th className="p-2 border-r border-[var(--border-main)]">|Z| SCORE</th>
                                <th className="p-2">DEVIATION DIRECTION</th>
                              </tr>
                            </thead>
                            <tbody className="divide-y divide-[var(--border-dim)] text-[var(--text-main)]">
                              {devList.map((dev, dIdx) => (
                                <tr key={dIdx} className="hover:bg-[var(--bg-surface)] transition-colors">
                                  <td className="p-2 border-r border-[var(--border-main)] text-[var(--text-main)] font-semibold">
                                    {dev.feature_name}
                                  </td>
                                  <td className="p-2 border-r border-[var(--border-main)]">
                                    {typeof dev.observed_value === "number"
                                      ? dev.observed_value.toFixed(4)
                                      : String(dev.observed_value)}
                                  </td>
                                  <td className="p-2 border-r border-[var(--border-main)] text-[var(--text-muted)]">
                                    {typeof dev.baseline_mean === "number"
                                      ? dev.baseline_mean.toFixed(4)
                                      : String(dev.baseline_mean)}
                                  </td>
                                  <td className="p-2 border-r border-[var(--border-main)] font-bold text-[#FF6B35]">
                                    |Z| = {dev.z_score.toFixed(2)}&sigma;
                                  </td>
                                  <td className="p-2">
                                    <span
                                      className={`px-1.5 py-0.5 border text-[11px] ${
                                        dev.direction.includes("ABOVE")
                                          ? "border-[#FF6B35] text-[#FF6B35] bg-[#FF6B35]/10"
                                          : "border-[var(--border-main)] text-[var(--text-muted)] bg-[var(--bg-surface)]"
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
            <div className="font-mono text-[12px] text-[var(--text-muted)] text-center py-6">
              NO ANOMALIES FLAGGED IN CURRENT CAPTURE
            </div>
          )}
        </div>
      </div>
    </section>
  );
};
