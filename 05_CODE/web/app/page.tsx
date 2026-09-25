"use client";

import React, { useState, useEffect } from "react";
import { Header, ActiveTabId } from "@/components/Header";
import { HeroSection } from "@/components/HeroSection";
import { LiveAnalyzer } from "@/components/LiveAnalyzer";
import { TelemetrySection } from "@/components/TelemetrySection";
import { Timeline } from "@/components/Timeline";
import { AnomalyPanel } from "@/components/AnomalyPanel";
import { ComparisonMatrix } from "@/components/ComparisonMatrix";
import { ArchitectureDiagram } from "@/components/ArchitectureDiagram";
import { DocumentationSection } from "@/components/DocumentationSection";
import { Footer } from "@/components/Footer";
import { AnalysisResponse, BackendStatus } from "@/lib/types";
import { getOfflineAnalysis } from "@/lib/formatOffline";

export default function Home() {
  const [activeTab, setActiveTab] = useState<ActiveTabId>("dashboard");

  const [backendStatus, setBackendStatus] = useState<BackendStatus>({
    status: "OFFLINE",
    milestone: "Review-2 Prototype",
    test_suite: "240 Tests Passing (207 Backend + 33 Frontend)",
  });

  const [currentAnalysis, setCurrentAnalysis] = useState<AnalysisResponse>(() =>
    getOfflineAnalysis("mpeg_ts")
  );

  const [activeFormatKey, setActiveFormatKey] = useState<
    "mpeg_ts" | "gse" | "bbframe"
  >("mpeg_ts");

  // Handle URL hash routing on mount and on hashchange
  useEffect(() => {
    const handleHash = () => {
      const hash = window.location.hash.replace("#", "").toLowerCase();
      if (
        hash === "dashboard" ||
        hash === "anomalies" ||
        hash === "timeline" ||
        hash === "comparison" ||
        hash === "architecture" ||
        hash === "docs"
      ) {
        setActiveTab(hash as ActiveTabId);
      } else if (hash === "documentation") {
        setActiveTab("docs");
      } else if (hash === "telemetry" || hash === "analyzer") {
        setActiveTab("dashboard");
      }
    };

    handleHash();
    window.addEventListener("hashchange", handleHash);
    return () => window.removeEventListener("hashchange", handleHash);
  }, []);

  // Ping backend to detect online/offline status
  useEffect(() => {
    const checkBackend = async () => {
      try {
        const res = await fetch("/api/status", { cache: "no-store" });
        if (res.ok) {
          const data = await res.json();
          setBackendStatus({
            status: "ONLINE",
            milestone: data.milestone,
            backend_status: data.backend_status,
            test_suite: data.test_suite,
            supported_formats: data.supported_formats,
            active_guards: data.active_guards,
          });
        } else {
          setBackendStatus((prev) => ({ ...prev, status: "OFFLINE" }));
        }
      } catch {
        setBackendStatus((prev) => ({ ...prev, status: "OFFLINE" }));
      }
    };

    checkBackend();
    const interval = setInterval(checkBackend, 10000);
    return () => clearInterval(interval);
  }, []);

  const handleAnalysisComplete = (result: AnalysisResponse) => {
    setCurrentAnalysis(result);
  };

  const handleSelectOfflinePreset = (
    formatKey: "mpeg_ts" | "gse" | "bbframe"
  ) => {
    setActiveFormatKey(formatKey);
    setCurrentAnalysis(getOfflineAnalysis(formatKey));
  };

  const handleSelectTab = (tab: ActiveTabId) => {
    setActiveTab(tab);
    window.location.hash = tab;
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  const scrollToSection = (id: string) => {
    const el = document.getElementById(id);
    if (el) {
      el.scrollIntoView({ behavior: "smooth" });
    }
  };

  return (
    <div className="min-h-screen bg-[var(--bg-main)] text-[var(--text-main)] flex flex-col font-sans selection:bg-[#FF6B35] selection:text-[#0A0A0A] transition-colors duration-150">
      {/* 1. Terminal Header with Version 1 Navigation Tabs */}
      <Header
        backendStatus={backendStatus}
        isLiveMode={backendStatus.status === "ONLINE"}
        activeTab={activeTab}
        onSelectTab={handleSelectTab}
        activeFormat={currentAnalysis?.stream_info?.detected_format || activeFormatKey.toUpperCase()}
      />

      {/* Main View Area: Shifts completely per feature page */}
      <main className="flex-1 w-full">
        {/* ==================================================================== */}
        {/* VIEW 1: DASHBOARD (Executive Overview, Ingestion & Telemetry)        */}
        {/* ==================================================================== */}
        {activeTab === "dashboard" && (
          <div className="w-full animate-in fade-in duration-200">
            {/* Hero Section */}
            <HeroSection
              onLaunchAnalyzerClick={() => scrollToSection("analyzer")}
              onExploreClick={() => handleSelectTab("timeline")}
            />

            {/* Ingestion & Analysis Workstation */}
            <LiveAnalyzer
              backendStatus={backendStatus}
              currentAnalysis={currentAnalysis}
              onAnalysisComplete={handleAnalysisComplete}
              onSelectOfflinePreset={handleSelectOfflinePreset}
              onNavigateTab={handleSelectTab}
            />

            {/* Multi-Format Telemetry Benchmarks */}
            <TelemetrySection
              currentAnalysis={currentAnalysis}
              onSelectFormatKey={handleSelectOfflinePreset}
              onNavigateTab={handleSelectTab}
            />

            {/* Quick Feature Navigation Grid */}
            <div className="w-full border-t border-[var(--border-main)] bg-[var(--bg-surface)] py-8">
              <div className="max-w-[1440px] mx-auto px-4">
                <div className="text-xs font-mono text-[var(--text-muted)] uppercase tracking-wider mb-4">
                  DEDICATED FEATURE WORKSPACES // SHIFT VIEW:
                </div>
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 font-mono text-xs">
                  <button
                    onClick={() => handleSelectTab("anomalies")}
                    className="p-4 border border-[var(--border-main)] bg-[var(--bg-main)] hover:border-[#FF6B35] text-left transition-colors cursor-pointer group"
                  >
                    <div className="flex items-center justify-between mb-2">
                      <span className="font-bold text-[#FF6B35]">[02] ANOMALIES</span>
                      <span className="text-[10px] text-[var(--text-muted)] group-hover:text-[var(--text-main)]">F2+F5 &rarr;</span>
                    </div>
                    <div className="text-[var(--text-main)] font-semibold text-sm mb-1">
                      Isolation Forest Attributions
                    </div>
                    <div className="text-[11px] text-[var(--text-muted)]">
                      Flagged window outlier scores, bounded Z-score explanations, and feature deviations.
                    </div>
                  </button>

                  <button
                    onClick={() => handleSelectTab("timeline")}
                    className="p-4 border border-[var(--border-main)] bg-[var(--bg-main)] hover:border-[#FF6B35] text-left transition-colors cursor-pointer group"
                  >
                    <div className="flex items-center justify-between mb-2">
                      <span className="font-bold text-[#FF6B35]">[03] TIMELINE</span>
                      <span className="text-[10px] text-[var(--text-muted)] group-hover:text-[var(--text-main)]">F4 &rarr;</span>
                    </div>
                    <div className="text-[var(--text-main)] font-semibold text-sm mb-1">
                      Spatial Stream Timeline
                    </div>
                    <div className="text-[11px] text-[var(--text-muted)]">
                      Interactive dual trajectory chart, rolling stream health, and byte offset inspection.
                    </div>
                  </button>

                  <button
                    onClick={() => handleSelectTab("comparison")}
                    className="p-4 border border-[var(--border-main)] bg-[var(--bg-main)] hover:border-[#FF6B35] text-left transition-colors cursor-pointer group"
                  >
                    <div className="flex items-center justify-between mb-2">
                      <span className="font-bold text-[#FF6B35]">[04] COMPARISON</span>
                      <span className="text-[10px] text-[var(--text-muted)] group-hover:text-[var(--text-main)]">F6 &rarr;</span>
                    </div>
                    <div className="text-[var(--text-main)] font-semibold text-sm mb-1">
                      Dual Stream &amp; Semantic Shield
                    </div>
                    <div className="text-[11px] text-[var(--text-muted)]">
                      Stream A &amp; B upload dropzones, presets, 2 permitted vs 9 masked barrier metrics.
                    </div>
                  </button>

                  <button
                    onClick={() => handleSelectTab("architecture")}
                    className="p-4 border border-[var(--border-main)] bg-[var(--bg-main)] hover:border-[#FF6B35] text-left transition-colors cursor-pointer group"
                  >
                    <div className="flex items-center justify-between mb-2">
                      <span className="font-bold text-[#FF6B35]">[05] ARCHITECTURE</span>
                      <span className="text-[10px] text-[var(--text-muted)] group-hover:text-[var(--text-main)]">DATAFLOW &rarr;</span>
                    </div>
                    <div className="text-[var(--text-main)] font-semibold text-sm mb-1">
                      Review-2 System Dataflow
                    </div>
                    <div className="text-[11px] text-[var(--text-muted)]">
                      Interactive dual perspective toggle, physical constraints, and pipeline invariants.
                    </div>
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* ==================================================================== */}
        {/* VIEW 2: ANOMALY ANALYSIS (F2 + F5)                                  */}
        {/* ==================================================================== */}
        {activeTab === "anomalies" && (
          <div className="w-full animate-in fade-in duration-200">
            {/* Page Header Bar */}
            <div className="w-full bg-[var(--bg-surface)] border-b border-[var(--border-main)] py-4">
              <div className="max-w-[1440px] mx-auto px-4 flex flex-col md:flex-row md:items-center justify-between gap-3 font-mono text-xs">
                <div className="flex items-center gap-2">
                  <span className="text-[#FF6B35] font-bold">[PAGE 02]</span>
                  <span className="text-[var(--text-muted)]">//</span>
                  <span className="text-[var(--text-main)] font-semibold uppercase">
                    FEATURE F2 &amp; F5: STATISTICAL ANOMALY INFERENCE &amp; ATTRIBUTION
                  </span>
                </div>

                {/* Preset switcher for instant format comparison */}
                <div className="flex items-center gap-2">
                  <span className="text-[var(--text-muted)]">LOAD PRESET:</span>
                  {(["mpeg_ts", "gse", "bbframe"] as const).map((fmt) => (
                    <button
                      key={fmt}
                      onClick={() => handleSelectOfflinePreset(fmt)}
                      className={`px-2 py-1 border transition-colors cursor-pointer ${
                        activeFormatKey === fmt
                          ? "border-[#FF6B35] bg-[var(--bg-main)] text-[#FF6B35] font-bold"
                          : "border-[var(--border-main)] bg-[var(--bg-surface)] text-[var(--text-muted)] hover:text-[var(--text-main)]"
                      }`}
                    >
                      {fmt === "mpeg_ts" ? "MPEG-TS" : fmt.toUpperCase()}
                    </button>
                  ))}
                </div>
              </div>
            </div>

            {/* Version 1 Domain Safety Notice Banner */}
            <div className="max-w-[1440px] mx-auto px-4 pt-6">
              <div className="border border-[var(--border-main)] bg-[var(--bg-surface)] p-4 flex items-start gap-3">
                <span className="text-[#FF6B35] font-bold text-sm">⚠</span>
                <div className="font-mono text-xs text-[var(--text-muted)] leading-relaxed">
                  <strong className="text-[var(--text-main)] block mb-0.5">
                    DOMAIN SAFETY &amp; CAPTURE BOUNDARY NOTICE:
                  </strong>
                  F2 Anomaly Detection evaluates post-demodulator digital receiver output against learned Isolation Forest baseline distributions.
                  Anomalous scores occurring at final window boundaries indicate recording termination (fewer units before capture end) and are not transmission or receiver hardware failures.
                </div>
              </div>
            </div>

            {/* Dedicated Anomaly Panel */}
            <AnomalyPanel
              f2Anomalies={currentAnalysis.f2_anomalies}
              explanations={currentAnalysis.f5_explanations}
            />

            {/* Sub-view Navigation Bar */}
            <div className="w-full border-t border-[var(--border-main)] bg-[var(--bg-surface)] py-4">
              <div className="max-w-[1440px] mx-auto px-4 flex justify-between items-center font-mono text-xs">
                <button
                  onClick={() => handleSelectTab("dashboard")}
                  className="px-3 py-1.5 border border-[var(--border-main)] hover:border-[#FF6B35] text-[var(--text-muted)] hover:text-[var(--text-main)] transition-colors cursor-pointer"
                >
                  &larr; [01] RETURN TO DASHBOARD
                </button>
                <div className="flex gap-2">
                  <button
                    onClick={() => handleSelectTab("timeline")}
                    className="px-3 py-1.5 border border-[#FF6B35] bg-[var(--bg-main)] text-[var(--text-main)] hover:bg-[#FF6B35] hover:text-[#0A0A0A] font-bold transition-colors cursor-pointer"
                  >
                    [03] SHIFT TO TIMELINE (F4) &rarr;
                  </button>
                  <button
                    onClick={() => handleSelectTab("comparison")}
                    className="px-3 py-1.5 border border-[var(--border-main)] hover:border-[#FF6B35] text-[var(--text-main)] transition-colors cursor-pointer"
                  >
                    [04] SHIFT TO COMPARISON (F6) &rarr;
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* ==================================================================== */}
        {/* VIEW 3: TIMELINE (F4)                                                */}
        {/* ==================================================================== */}
        {activeTab === "timeline" && (
          <div className="w-full animate-in fade-in duration-200">
            {/* Page Header Bar */}
            <div className="w-full bg-[var(--bg-surface)] border-b border-[var(--border-main)] py-4">
              <div className="max-w-[1440px] mx-auto px-4 flex flex-col md:flex-row md:items-center justify-between gap-3 font-mono text-xs">
                <div className="flex items-center gap-2">
                  <span className="text-[#FF6B35] font-bold">[PAGE 03]</span>
                  <span className="text-[var(--text-muted)]">//</span>
                  <span className="text-[var(--text-main)] font-semibold uppercase">
                    FEATURE F4: HORIZONTAL SEGMENTED ACTIVITY TIMELINE &amp; SPATIAL DIAGNOSTICS
                  </span>
                </div>

                {/* Preset switcher for instant format comparison */}
                <div className="flex items-center gap-2">
                  <span className="text-[var(--text-muted)]">LOAD PRESET:</span>
                  {(["mpeg_ts", "gse", "bbframe"] as const).map((fmt) => (
                    <button
                      key={fmt}
                      onClick={() => handleSelectOfflinePreset(fmt)}
                      className={`px-2 py-1 border transition-colors cursor-pointer ${
                        activeFormatKey === fmt
                          ? "border-[#FF6B35] bg-[var(--bg-main)] text-[#FF6B35] font-bold"
                          : "border-[var(--border-main)] bg-[var(--bg-surface)] text-[var(--text-muted)] hover:text-[var(--text-main)]"
                      }`}
                    >
                      {fmt === "mpeg_ts" ? "MPEG-TS" : fmt.toUpperCase()}
                    </button>
                  ))}
                </div>
              </div>
            </div>

            {/* Version 1 Physical Spatial Indexing Notice */}
            <div className="max-w-[1440px] mx-auto px-4 pt-6">
              <div className="border border-[var(--border-main)] bg-[var(--bg-surface)] p-4 flex items-start gap-3">
                <span className="text-[#FF6B35] font-bold text-sm">ℹ</span>
                <div className="font-mono text-xs text-[var(--text-muted)] leading-relaxed">
                  <strong className="text-[var(--text-main)] block mb-0.5">
                    PHYSICAL SPATIAL INDEXING NOTICE:
                  </strong>
                  Offline captured streams lack calibrated broadcast clock signals. The PRJ_111 timeline strictly indexes events and windows by physical byte offsets and unit sequence numbers, avoiding synthetic timestamps or fabricated throughput rates.
                </div>
              </div>
            </div>

            {/* Dedicated Timeline Component */}
            <Timeline timeline={currentAnalysis.f4_timeline} />

            {/* Sub-view Navigation Bar */}
            <div className="w-full border-t border-[var(--border-main)] bg-[var(--bg-surface)] py-4">
              <div className="max-w-[1440px] mx-auto px-4 flex justify-between items-center font-mono text-xs">
                <button
                  onClick={() => handleSelectTab("dashboard")}
                  className="px-3 py-1.5 border border-[var(--border-main)] hover:border-[#FF6B35] text-[var(--text-muted)] hover:text-[var(--text-main)] transition-colors cursor-pointer"
                >
                  &larr; [01] RETURN TO DASHBOARD
                </button>
                <div className="flex gap-2">
                  <button
                    onClick={() => handleSelectTab("anomalies")}
                    className="px-3 py-1.5 border border-[var(--border-main)] hover:border-[#FF6B35] text-[var(--text-main)] transition-colors cursor-pointer"
                  >
                    [02] SHIFT TO ANOMALIES (F2+F5) &rarr;
                  </button>
                  <button
                    onClick={() => handleSelectTab("comparison")}
                    className="px-3 py-1.5 border border-[#FF6B35] bg-[var(--bg-main)] text-[var(--text-main)] hover:bg-[#FF6B35] hover:text-[#0A0A0A] font-bold transition-colors cursor-pointer"
                  >
                    [04] SHIFT TO COMPARISON (F6) &rarr;
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* ==================================================================== */}
        {/* VIEW 4: COMPARISON (F6)                                              */}
        {/* ==================================================================== */}
        {activeTab === "comparison" && (
          <div className="w-full animate-in fade-in duration-200">
            {/* Page Header Bar */}
            <div className="w-full bg-[var(--bg-surface)] border-b border-[var(--border-main)] py-4">
              <div className="max-w-[1440px] mx-auto px-4 flex flex-col md:flex-row md:items-center justify-between gap-3 font-mono text-xs">
                <div className="flex items-center gap-2">
                  <span className="text-[#FF6B35] font-bold">[PAGE 04]</span>
                  <span className="text-[var(--text-muted)]">//</span>
                  <span className="text-[var(--text-main)] font-semibold uppercase">
                    FEATURE F6: MULTI-FORMAT STREAM COMPARISON MATRIX &amp; SEMANTIC SHIELD
                  </span>
                </div>
                <div className="text-[var(--text-muted)]">
                  SEMANTIC BARRIER: <span className="text-[#FF6B35] font-bold">2 COMPARABLE</span> vs. <span className="text-[var(--text-main)]">9 MASKED</span>
                </div>
              </div>
            </div>

            {/* Dedicated Comparison Matrix (with Version 1 Upload Dropzones) */}
            <ComparisonMatrix />

            {/* Sub-view Navigation Bar */}
            <div className="w-full border-t border-[var(--border-main)] bg-[var(--bg-surface)] py-4">
              <div className="max-w-[1440px] mx-auto px-4 flex justify-between items-center font-mono text-xs">
                <button
                  onClick={() => handleSelectTab("dashboard")}
                  className="px-3 py-1.5 border border-[var(--border-main)] hover:border-[#FF6B35] text-[var(--text-muted)] hover:text-[var(--text-main)] transition-colors cursor-pointer"
                >
                  &larr; [01] RETURN TO DASHBOARD
                </button>
                <div className="flex gap-2">
                  <button
                    onClick={() => handleSelectTab("timeline")}
                    className="px-3 py-1.5 border border-[var(--border-main)] hover:border-[#FF6B35] text-[var(--text-main)] transition-colors cursor-pointer"
                  >
                    [03] SHIFT TO TIMELINE (F4) &rarr;
                  </button>
                  <button
                    onClick={() => handleSelectTab("architecture")}
                    className="px-3 py-1.5 border border-[#FF6B35] bg-[var(--bg-main)] text-[var(--text-main)] hover:bg-[#FF6B35] hover:text-[#0A0A0A] font-bold transition-colors cursor-pointer"
                  >
                    [05] SHIFT TO ARCHITECTURE &rarr;
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* ==================================================================== */}
        {/* VIEW 5: ARCHITECTURE                                                 */}
        {/* ==================================================================== */}
        {activeTab === "architecture" && (
          <div className="w-full animate-in fade-in duration-200">
            {/* Page Header Bar */}
            <div className="w-full bg-[var(--bg-surface)] border-b border-[var(--border-main)] py-4">
              <div className="max-w-[1440px] mx-auto px-4 flex items-center justify-between font-mono text-xs">
                <div className="flex items-center gap-2">
                  <span className="text-[#FF6B35] font-bold">[PAGE 05]</span>
                  <span className="text-[var(--text-muted)]">//</span>
                  <span className="text-[var(--text-main)] font-semibold uppercase">
                    SYSTEM PIPELINE ARCHITECTURE &amp; MATHEMATICAL INVARIANTS
                  </span>
                </div>
              </div>
            </div>

            {/* Dedicated Architecture Diagram */}
            <ArchitectureDiagram />

            {/* Sub-view Navigation Bar */}
            <div className="w-full border-t border-[var(--border-main)] bg-[var(--bg-surface)] py-4">
              <div className="max-w-[1440px] mx-auto px-4 flex justify-between items-center font-mono text-xs">
                <button
                  onClick={() => handleSelectTab("dashboard")}
                  className="px-3 py-1.5 border border-[var(--border-main)] hover:border-[#FF6B35] text-[var(--text-muted)] hover:text-[var(--text-main)] transition-colors cursor-pointer"
                >
                  &larr; [01] RETURN TO DASHBOARD
                </button>
                <button
                  onClick={() => handleSelectTab("docs")}
                  className="px-3 py-1.5 border border-[#FF6B35] bg-[var(--bg-main)] text-[var(--text-main)] hover:bg-[#FF6B35] hover:text-[#0A0A0A] font-bold transition-colors cursor-pointer"
                >
                  [06] SHIFT TO DOCUMENTATION &rarr;
                </button>
              </div>
            </div>
          </div>
        )}

        {/* ==================================================================== */}
        {/* VIEW 6: DOCUMENTATION & STANDARDS                                   */}
        {/* ==================================================================== */}
        {activeTab === "docs" && (
          <div className="w-full animate-in fade-in duration-200">
            {/* Page Header Bar */}
            <div className="w-full bg-[var(--bg-surface)] border-b border-[var(--border-main)] py-4">
              <div className="max-w-[1440px] mx-auto px-4 flex items-center justify-between font-mono text-xs">
                <div className="flex items-center gap-2">
                  <span className="text-[#FF6B35] font-bold">[PAGE 06]</span>
                  <span className="text-[var(--text-muted)]">//</span>
                  <span className="text-[var(--text-main)] font-semibold uppercase">
                    TECHNICAL SPECIFICATIONS, ETSI STANDARDS &amp; 240-TEST AUDIT
                  </span>
                </div>
              </div>
            </div>

            {/* Dedicated Documentation Section */}
            <DocumentationSection />

            {/* Sub-view Navigation Bar */}
            <div className="w-full border-t border-[var(--border-main)] bg-[var(--bg-surface)] py-4">
              <div className="max-w-[1440px] mx-auto px-4 flex justify-between items-center font-mono text-xs">
                <button
                  onClick={() => handleSelectTab("dashboard")}
                  className="px-3 py-1.5 border border-[var(--border-main)] hover:border-[#FF6B35] text-[var(--text-muted)] hover:text-[var(--text-main)] transition-colors cursor-pointer"
                >
                  &larr; [01] RETURN TO DASHBOARD
                </button>
                <button
                  onClick={() => handleSelectTab("comparison")}
                  className="px-3 py-1.5 border border-[#FF6B35] bg-[var(--bg-main)] text-[var(--text-main)] hover:bg-[#FF6B35] hover:text-[#0A0A0A] font-bold transition-colors cursor-pointer"
                >
                  [04] SHIFT TO COMPARISON &rarr;
                </button>
              </div>
            </div>
          </div>
        )}
      </main>

      {/* Engineering Terminal Footer */}
      <Footer />
    </div>
  );
}
