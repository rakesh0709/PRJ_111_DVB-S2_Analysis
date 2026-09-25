"use client";

import React, { useState, useEffect } from "react";
import { Header } from "@/components/Header";
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

  const scrollToSection = (id: string) => {
    const el = document.getElementById(id);
    if (el) {
      el.scrollIntoView({ behavior: "smooth" });
    }
  };

  return (
    <div className="min-h-screen bg-[#0A0A0A] text-[#E8E8E8] flex flex-col font-sans selection:bg-[#FF6B35] selection:text-[#0A0A0A]">
      {/* 1. Terminal Header */}
      <Header
        backendStatus={backendStatus}
        isLiveMode={backendStatus.status === "ONLINE"}
      />

      <main className="flex-1 w-full">
        {/* 2. Hero Section (96px display typography, 8/4 grid, -1.5° verification card) */}
        <HeroSection
          onLaunchAnalyzerClick={() => scrollToSection("analyzer")}
          onExploreClick={() => scrollToSection("telemetry")}
        />

        {/* 3. Ingestion & Analysis Workstation (Live Mode A / Offline Mode B) */}
        <LiveAnalyzer
          backendStatus={backendStatus}
          currentAnalysis={currentAnalysis}
          onAnalysisComplete={handleAnalysisComplete}
          onSelectOfflinePreset={handleSelectOfflinePreset}
        />

        {/* 4. Multi-Format Telemetry Benchmarks & F1 Stream Health */}
        <TelemetrySection
          currentAnalysis={currentAnalysis}
          onSelectFormatKey={handleSelectOfflinePreset}
        />

        {/* 5. F4 Horizontal Segmented Activity Timeline & Byte Offset Inspection */}
        <Timeline timeline={currentAnalysis.f4_timeline} />

        {/* 6. F2 Isolation Forest Anomalies & F5 Bounded Z-Score Explanations */}
        <AnomalyPanel
          f2Anomalies={currentAnalysis.f2_anomalies}
          explanations={currentAnalysis.f5_explanations}
        />

        {/* 7. Architecture & System Dataflow (Perspectives A & B) */}
        <ArchitectureDiagram />

        {/* 8. F6 Semantic Comparison Matrix & Safety Shield */}
        <ComparisonMatrix />

        {/* 9. Specifications, Technologies Used, & Installation Protocol */}
        <DocumentationSection />
      </main>

      {/* 10. Engineering Terminal Footer */}
      <Footer />
    </div>
  );
}
