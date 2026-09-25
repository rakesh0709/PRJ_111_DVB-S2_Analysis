"use client";

import React, { useState, useEffect, useRef } from "react";
import {
  AnalysisResponse,
  BackendStatus,
  PresetDataset,
  StreamFormat,
} from "@/lib/types";
import { OFFLINE_DATA } from "@/lib/offlineData";
import { useToast } from "@/components/Toast";
import { Tooltip } from "@/components/Tooltip";

interface LiveAnalyzerProps {
  backendStatus: BackendStatus;
  currentAnalysis: AnalysisResponse | null;
  onAnalysisComplete: (result: AnalysisResponse) => void;
  onSelectOfflinePreset: (formatKey: "mpeg_ts" | "gse" | "bbframe") => void;
  onNavigateTab?: (tab: "dashboard" | "anomalies" | "timeline" | "comparison" | "architecture" | "docs") => void;
}

export const LiveAnalyzer: React.FC<LiveAnalyzerProps> = ({
  backendStatus,
  currentAnalysis,
  onAnalysisComplete,
  onSelectOfflinePreset,
  onNavigateTab,
}) => {
  const isOnline = backendStatus.status === "ONLINE";
  const { showToast } = useToast();

  // State
  const [presets, setPresets] = useState<PresetDataset[]>([]);
  const [selectedPresetId, setSelectedPresetId] = useState<string>("mpeg_ts");
  const [selectedFormat, setSelectedFormat] = useState<StreamFormat>("AUTO");
  const [windowSize, setWindowSize] = useState<number>(200);
  const [isAnalyzing, setIsAnalyzing] = useState<boolean>(false);
  const [loadingStep, setLoadingStep] = useState<string>("");
  const [progressPercent, setProgressPercent] = useState<number>(0);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  // Upload state
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);
  const [uploadedFilePath, setUploadedFilePath] = useState<string | null>(null);
  const [isUploading, setIsUploading] = useState<boolean>(false);

  const fileInputRef = useRef<HTMLInputElement>(null);

  // Fetch presets when online
  useEffect(() => {
    if (isOnline) {
      fetch("/api/presets")
        .then((res) => res.json())
        .then((data) => {
          if (data.success && Array.isArray(data.presets)) {
            setPresets(data.presets);
            if (data.presets.length > 0) {
              setSelectedPresetId(data.presets[0].id);
              setWindowSize(data.presets[0].default_window_size || 200);
            }
          }
        })
        .catch(() => {
          // Graceful fallback
        });
    }
  }, [isOnline]);

  // Handle Preset selection change
  const handlePresetChange = (presetId: string) => {
    setSelectedPresetId(presetId);
    setUploadedFile(null);
    setUploadedFilePath(null);
    setErrorMsg(null);

    const found = presets.find((p) => p.id === presetId);
    if (found) {
      setWindowSize(found.default_window_size);
      if (found.format === "GSE") {
        setSelectedFormat("GSE");
      } else if (found.format === "BB_FRAME") {
        setSelectedFormat("BB_FRAME");
      } else {
        setSelectedFormat("AUTO");
      }
      showToast(`Selected preset: ${found.label} (${found.format})`, "info");
    }
  };

  // Handle File Upload to backend
  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setUploadedFile(file);
    setSelectedPresetId("");
    setErrorMsg(null);

    if (!isOnline) {
      setErrorMsg(
        "Backend is offline. To analyze custom streams, run: .\\.venv\\Scripts\\python.exe run_frontend.py --port 8080. You can explore verified empirical captures below."
      );
      showToast("Backend offline: Custom file upload requires active backend", "warning");
      return;
    }

    try {
      setIsUploading(true);
      setLoadingStep("Uploading stream capture...");

      const resp = await fetch(`/api/upload?filename=${encodeURIComponent(file.name)}`, {
        method: "POST",
        body: file,
        headers: {
          "Content-Type": "application/octet-stream",
          "X-File-Name": file.name,
        },
      });

      const resJson = await resp.json();
      if (!resp.ok || !resJson.success) {
        throw new Error(resJson.error || "File upload failed.");
      }

      setUploadedFilePath(resJson.file_path);
      setLoadingStep("");
      showToast(`Upload complete: ${file.name} (${(file.size / 1024).toFixed(1)} KB)`, "success");
    } catch (err: any) {
      const msg = err.message || "Failed to upload stream file.";
      setErrorMsg(msg);
      showToast(msg, "error");
    } finally {
      setIsUploading(false);
    }
  };

  // Run Analysis
  const handleExecuteAnalysis = async () => {
    setErrorMsg(null);

    // If Offline Mode: switch to verified precompiled datasets
    if (!isOnline) {
      let key: "mpeg_ts" | "gse" | "bbframe" = "mpeg_ts";
      if (selectedPresetId === "gse" || selectedFormat === "GSE") {
        key = "gse";
      } else if (selectedPresetId === "bbframe" || selectedFormat === "BB_FRAME") {
        key = "bbframe";
      }

      onSelectOfflinePreset(key);
      showToast(`Loaded precompiled empirical dataset: ${key.toUpperCase()}`, "success");
      return;
    }

    // Online Mode: Trigger analysis via REST API
    let targetFilePath = uploadedFilePath;
    if (!targetFilePath && selectedPresetId) {
      const p = presets.find((item) => item.id === selectedPresetId);
      if (p) targetFilePath = p.absolute_path;
    }

    if (!targetFilePath) {
      setErrorMsg("Please select a preset or upload a valid stream file.");
      showToast("Please select a preset or upload a file", "warning");
      return;
    }

    try {
      setIsAnalyzing(true);
      setProgressPercent(10);
      setLoadingStep("Detecting format...");

      const stepTimer1 = setTimeout(() => {
        setProgressPercent(28);
        setLoadingStep("Parsing stream...");
      }, 350);

      const stepTimer2 = setTimeout(() => {
        setProgressPercent(50);
        setLoadingStep("Extracting features...");
      }, 750);

      const stepTimer3 = setTimeout(() => {
        setProgressPercent(70);
        setLoadingStep("Detecting anomalies...");
      }, 1200);

      const stepTimer4 = setTimeout(() => {
        setProgressPercent(88);
        setLoadingStep("Building diagnostics...");
      }, 1600);

      const stepTimer5 = setTimeout(() => {
        setProgressPercent(95);
        setLoadingStep("Generating report...");
      }, 1900);

      const resp = await fetch("/api/analyze", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          file_path: targetFilePath,
          format: selectedFormat,
          window_size: Number(windowSize),
        }),
      });

      clearTimeout(stepTimer1);
      clearTimeout(stepTimer2);
      clearTimeout(stepTimer3);
      clearTimeout(stepTimer4);
      clearTimeout(stepTimer5);

      const resJson = await resp.json();
      if (!resp.ok || !resJson.success) {
        throw new Error(resJson.error || "Analysis failed.");
      }

      setProgressPercent(100);
      onAnalysisComplete(resJson);
      showToast(`Analysis complete: ${resJson.stream_info.detected_format} (${resJson.stream_info.total_units} units)`, "success");
    } catch (err: any) {
      const msg = err.message || "Execution failed. Check backend terminal logs.";
      setErrorMsg(msg);
      showToast(msg, "error");
    } finally {
      setIsAnalyzing(false);
      setLoadingStep("");
      setProgressPercent(0);
    }
  };

  return (
    <section id="analyzer" className="w-full border-b border-[var(--border-main)] bg-[var(--bg-main)] py-12 transition-colors duration-150">
      <div className="max-w-[1440px] mx-auto px-4">
        {/* Section Header */}
        <div className="flex flex-col md:flex-row md:items-end justify-between border-b border-[var(--border-main)] pb-4 mb-6">
          <div>
            <div className="text-xs font-semibold text-[var(--text-muted)] tracking-wider uppercase mb-1 flex items-center gap-2">
              <span>WORKSTATION CONTROLLER</span>
              <span>•</span>
              <Tooltip content="Deterministic framing (F1), Isolation Forest (F2), cross-window tracking (F4), bounded Z-score explanations (F5), semantic comparison (F6), and automated reports (F7)">
                <span className="text-[var(--text-main)] font-mono cursor-help underline decoration-dotted underline-offset-2">
                  F1-F7 PIPELINE
                </span>
              </Tooltip>
            </div>
            <h2 className="text-[24px] md:text-[44px] font-bold uppercase tracking-tight text-[var(--text-main)]">
              STREAM INGESTION &amp; ANALYSIS
            </h2>
          </div>
          <div className="mt-4 md:mt-0 font-mono text-[12px]">
            <span
              className={`px-3 py-1.5 border ${
                isOnline
                  ? "border-[var(--border-main)] bg-[var(--bg-surface)] text-[var(--text-main)]"
                  : "border-[#FF6B35] bg-[var(--bg-surface)] text-[#FF6B35]"
              }`}
            >
              {isOnline
                ? "MODE A: LIVE BACKEND CONNECTED (127.0.0.1:8080)"
                : "MODE B: OFFLINE SHOWCASE (PRECOMPILED EMPIRICAL CAPTURE)"}
            </span>
          </div>
        </div>

        {/* 4-Step Visual Workflow Sequence Bar */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-8">
          <div className="p-3.5 border border-[var(--border-main)] bg-[var(--bg-surface)] flex items-center justify-between">
            <div className="flex items-center gap-2.5">
              <span className="font-mono font-bold text-sm text-[#FF6B35]">01</span>
              <span className="text-xs font-semibold uppercase text-[var(--text-main)] tracking-wide">SELECT INPUT</span>
            </div>
            <span className="font-mono text-[11px] text-[var(--text-muted)]">PRESET / FILE</span>
          </div>
          <div className="p-3.5 border border-[var(--border-main)] bg-[var(--bg-surface)] flex items-center justify-between">
            <div className="flex items-center gap-2.5">
              <span className="font-mono font-bold text-sm text-[#FF6B35]">02</span>
              <span className="text-xs font-semibold uppercase text-[var(--text-main)] tracking-wide">DETECT FORMAT</span>
            </div>
            <span className="font-mono text-[11px] text-[#FF6B35] font-semibold">{selectedFormat}</span>
          </div>
          <div
            className={`p-3.5 border ${
              isAnalyzing
                ? "border-[#FF6B35] bg-[var(--bg-surface-elevated)]"
                : "border-[var(--border-main)] bg-[var(--bg-surface)]"
            } flex items-center justify-between transition-colors`}
          >
            <div className="flex items-center gap-2.5">
              <span className="font-mono font-bold text-sm text-[#FF6B35]">03</span>
              <span className="text-xs font-semibold uppercase text-[var(--text-main)] tracking-wide">ANALYZE STREAM</span>
            </div>
            <span className="font-mono text-[11px] text-[var(--text-muted)]">
              {isAnalyzing ? "ACTIVE" : "READY"}
            </span>
          </div>
          <div
            className={`p-3.5 border ${
              currentAnalysis
                ? "border-[#FF6B35] bg-[var(--bg-surface)]"
                : "border-[var(--border-main)] bg-[var(--bg-surface)]"
            } flex items-center justify-between`}
          >
            <div className="flex items-center gap-2.5">
              <span className="font-mono font-bold text-sm text-[#FF6B35]">04</span>
              <span className="text-xs font-semibold uppercase text-[var(--text-main)] tracking-wide">INSPECT RESULTS</span>
            </div>
            <span className="font-mono text-[11px] text-[var(--text-muted)]">
              {currentAnalysis ? "SYNCED" : "AWAITING"}
            </span>
          </div>
        </div>

        {/* Staged Analysis Progress Indicator */}
        {isAnalyzing && (
          <div className="mb-6 p-4 border border-[#FF6B35] bg-[var(--bg-surface)] font-mono text-[12px] animate-in fade-in">
            <div className="flex justify-between items-center mb-2">
              <span className="text-[#FF6B35] font-bold">&gt; {loadingStep || "Analyzing stream..."}</span>
              <span className="text-[var(--text-main)] font-bold">{progressPercent}%</span>
            </div>
            <div className="w-full bg-[var(--bg-main)] h-2 border border-[var(--border-main)] overflow-hidden">
              <div
                className="bg-[#FF6B35] h-full transition-all duration-200"
                style={{ width: `${progressPercent}%` }}
              />
            </div>
          </div>
        )}

        {/* Workstation Controls Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
          {/* Controls Column (8 cols) */}
          <div className="lg:col-span-8 space-y-6">
            {/* Source Selection Panel */}
            <div className="border border-[var(--border-main)] bg-[var(--bg-surface)] p-6">
              <div className="flex items-center justify-between border-b border-[var(--border-dim)] pb-3 mb-5">
                <h3 className="text-xs font-semibold uppercase tracking-wider text-[var(--text-muted)]">
                  Stream Source Selection
                </h3>
                <span className="text-xs font-medium text-[#FF6B35]">
                  Content-Aware Detection Enabled
                </span>
              </div>

              {/* Preset Selector */}
              <div className="space-y-5">
                <div>
                  <label className="block text-xs font-medium text-[var(--text-main)] uppercase tracking-wider mb-2">
                    Authoritative Broadcast Capture:
                  </label>
                  {isOnline && presets.length > 0 ? (
                    <select
                      value={selectedPresetId}
                      onChange={(e) => handlePresetChange(e.target.value)}
                      className="w-full bg-[var(--bg-main)] border border-[var(--border-main)] text-[var(--text-main)] font-mono text-[14px] p-3 focus:border-[#FF6B35] focus:outline-none transition-colors"
                    >
                      {presets.map((p) => (
                        <option key={p.id} value={p.id}>
                          [{p.format}] {p.label} ({(p.file_size_bytes / 1024).toFixed(0)} KB)
                        </option>
                      ))}
                    </select>
                  ) : (
                    /* Offline Preset Selection Buttons */
                    <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                      <button
                        onClick={() => {
                          setSelectedPresetId("mpeg_ts");
                          setWindowSize(200);
                          setSelectedFormat("MPEG_TS");
                          onSelectOfflinePreset("mpeg_ts");
                          showToast("Loaded authoritative MPEG-TS capture (18,176 pkts)", "info");
                        }}
                        className={`p-3.5 text-left border font-mono text-[12px] transition-all cursor-pointer ${
                          selectedPresetId === "mpeg_ts" || !selectedPresetId
                            ? "border-[#FF6B35] bg-[var(--bg-surface-elevated)] text-[var(--text-main)] ring-1 ring-[#FF6B35]/30"
                            : "border-[var(--border-main)] bg-[var(--bg-main)] text-[var(--text-muted)] hover:text-[var(--text-main)] hover:border-[var(--text-muted)]"
                        }`}
                      >
                        <div className="font-bold text-[var(--text-main)] text-sm mb-0.5">[MPEG-TS]</div>
                        <div className="text-xs text-[var(--text-muted)]">sample.ts (3.4 MB)</div>
                        <div className="text-[11px] text-[var(--text-muted)] mt-1">18,176 pkts • w=200</div>
                      </button>

                      <button
                        onClick={() => {
                          setSelectedPresetId("gse");
                          setWindowSize(3);
                          setSelectedFormat("GSE");
                          onSelectOfflinePreset("gse");
                          showToast("Loaded authoritative GSE capture (14 PDUs)", "info");
                        }}
                        className={`p-3.5 text-left border font-mono text-[12px] transition-all cursor-pointer ${
                          selectedPresetId === "gse"
                            ? "border-[#FF6B35] bg-[var(--bg-surface-elevated)] text-[var(--text-main)] ring-1 ring-[#FF6B35]/30"
                            : "border-[var(--border-main)] bg-[var(--bg-main)] text-[var(--text-muted)] hover:text-[var(--text-main)] hover:border-[var(--text-muted)]"
                        }`}
                      >
                        <div className="font-bold text-[var(--text-main)] text-sm mb-0.5">[GSE]</div>
                        <div className="text-xs text-[var(--text-muted)]">sample.ts (9.3 KB)</div>
                        <div className="text-[11px] text-[var(--text-muted)] mt-1">14 PDUs • w=3</div>
                      </button>

                      <button
                        onClick={() => {
                          setSelectedPresetId("bbframe");
                          setWindowSize(50);
                          setSelectedFormat("BB_FRAME");
                          onSelectOfflinePreset("bbframe");
                          showToast("Loaded authoritative BBFrame capture (4,309 frames)", "info");
                        }}
                        className={`p-3.5 text-left border font-mono text-[12px] transition-all cursor-pointer ${
                          selectedPresetId === "bbframe"
                            ? "border-[#FF6B35] bg-[var(--bg-surface-elevated)] text-[var(--text-main)] ring-1 ring-[#FF6B35]/30"
                            : "border-[var(--border-main)] bg-[var(--bg-main)] text-[var(--text-muted)] hover:text-[var(--text-main)] hover:border-[var(--text-muted)]"
                        }`}
                      >
                        <div className="font-bold text-[var(--text-main)] text-sm mb-0.5">[BBFRAME]</div>
                        <div className="text-xs text-[var(--text-muted)]">dvb-s2_bb_example.pcap</div>
                        <div className="text-[11px] text-[var(--text-muted)] mt-1">4,309 frames • w=50</div>
                      </button>
                    </div>
                  )}
                </div>

                {/* Upload Stream Alternative */}
                <div className="pt-2">
                  <div className="flex items-center justify-between mb-2">
                    <label className="text-xs font-medium text-[var(--text-muted)] uppercase tracking-wider">
                      Or Upload Custom Stream Dump (.ts, .pcap, .bin):
                    </label>
                    {uploadedFile && (
                      <span className="font-mono text-[12px] text-[var(--text-main)] font-semibold">
                        {uploadedFile.name} ({(uploadedFile.size / 1024).toFixed(1)} KB)
                      </span>
                    )}
                  </div>
                  <input
                    ref={fileInputRef}
                    type="file"
                    onChange={handleFileUpload}
                    className="w-full bg-[var(--bg-main)] border border-[var(--border-main)] text-[var(--text-muted)] file:mr-4 file:py-2.5 file:px-4 file:border-0 file:bg-[var(--bg-surface-elevated)] file:text-[var(--text-main)] file:font-mono file:text-[12px] cursor-pointer hover:border-[var(--text-muted)] transition-colors"
                  />
                  <div className="text-xs text-[var(--text-muted)] mt-1.5">
                    * Note: File extension does not force format. Content-aware heuristics detect GSE, BBFrame, or MPEG-TS payloads automatically.
                  </div>
                </div>
              </div>
            </div>

            {/* Analysis Parameters Panel */}
            <div className="border border-[var(--border-main)] bg-[var(--bg-surface)] p-6">
              <div className="flex items-center justify-between border-b border-[var(--border-dim)] pb-3 mb-5">
                <h3 className="text-xs font-semibold uppercase tracking-wider text-[var(--text-muted)]">
                  Pipeline Configuration
                </h3>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-medium text-[var(--text-main)] uppercase tracking-wider mb-1.5">
                    Stream Format Selection:
                  </label>
                  <select
                    value={selectedFormat}
                    onChange={(e) => setSelectedFormat(e.target.value as StreamFormat)}
                    className="w-full bg-[var(--bg-main)] border border-[var(--border-main)] text-[var(--text-main)] font-mono text-[14px] p-2.5 focus:border-[#FF6B35] focus:outline-none transition-colors"
                  >
                    <option value="AUTO">AUTO (Content-Aware Detection)</option>
                    <option value="MPEG_TS">MPEG_TS (188B TS Packets)</option>
                    <option value="GSE">GSE (Generic Stream Encapsulation)</option>
                    <option value="BB_FRAME">BB_FRAME (DVB-S2 Baseband Frame)</option>
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-medium text-[var(--text-main)] uppercase tracking-wider mb-1.5">
                    Analysis Window Size (Units):
                  </label>
                  <input
                    type="number"
                    min="1"
                    max="1000"
                    value={windowSize}
                    onChange={(e) => setWindowSize(Number(e.target.value))}
                    className="w-full bg-[var(--bg-main)] border border-[var(--border-main)] text-[var(--text-main)] font-mono text-[14px] p-2.5 focus:border-[#FF6B35] focus:outline-none transition-colors"
                  />
                  <span className="text-[11px] text-[var(--text-muted)] font-mono">
                    Baseline: 200 (TS) // 3 (GSE) // 50 (BBFrame)
                  </span>
                </div>
              </div>

              {/* Execution CTA & Status */}
              <div className="mt-6 pt-4 border-t border-[var(--border-dim)] flex flex-col sm:flex-row items-center justify-between gap-4">
                <button
                  onClick={handleExecuteAnalysis}
                  disabled={isAnalyzing || isUploading}
                  className={`w-full sm:w-auto font-mono text-[14px] font-bold px-8 py-3.5 border transition-all cursor-pointer active:translate-y-[1px] focus-visible:outline-2 focus-visible:outline-[#FF6B35] ${
                    isAnalyzing || isUploading
                      ? "border-[var(--border-main)] bg-[var(--bg-surface-elevated)] text-[var(--text-muted)] cursor-not-allowed"
                      : "border-[#FF6B35] bg-[#FF6B35] text-[#0A0A0A] hover:bg-[#ff8555]"
                  }`}
                >
                  {isAnalyzing
                    ? "[PROCESSING_PIPELINE...]"
                    : isUploading
                    ? "[UPLOADING...]"
                    : isOnline
                    ? "[ANALYZE STREAM]"
                    : "[LOAD PRECOMPILED CAPTURE]"}
                </button>

                {/* Loading Indicator */}
                {(isAnalyzing || isUploading) && (
                  <div className="font-mono text-[12px] text-[#FF6B35] animate-pulse">
                    &gt; {loadingStep || "RUNNING_ANALYSIS..."}
                  </div>
                )}
              </div>

              {/* Error Notification with Troubleshooting Guide */}
              {errorMsg && (
                <div className="mt-4 p-4 bg-[var(--bg-main)] border border-[#FF4D4D] text-[var(--text-main)] font-mono text-[12px]">
                  <div className="flex items-start gap-2 mb-2">
                    <span className="text-[#FF4D4D] font-bold">✕ ERROR:</span>
                    <span className="leading-snug">{errorMsg}</span>
                  </div>
                  <div className="text-[var(--text-muted)] text-[11px] pt-2 border-t border-[var(--border-dim)] flex flex-wrap gap-2">
                    <span className="font-bold text-[var(--text-main)]">TROUBLESHOOTING:</span>
                    <span>1. Verify Python backend is listening at http://127.0.0.1:8080</span>
                    <span>•</span>
                    <span>2. Or select a precompiled empirical capture above to run offline</span>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Quick Summary / Status Column (4 cols) */}
          <div className="lg:col-span-4 flex flex-col gap-6">
            {/* Stream Execution Summary Card */}
            <div className="border border-[var(--border-main)] bg-[var(--bg-surface)] p-6">
              <div className="flex items-center justify-between border-b border-[var(--border-dim)] pb-3 mb-4">
                <h3 className="text-xs font-semibold uppercase tracking-wider text-[var(--text-muted)]">
                  Active Stream Telemetry
                </h3>
              </div>

              {currentAnalysis ? (
                <div className="space-y-3 font-mono text-[12px]">
                  <div className="flex justify-between border-b border-[var(--border-dim)] pb-1.5">
                    <span className="text-[var(--text-muted)] font-sans text-xs">FILE:</span>
                    <span className="text-[var(--text-main)] font-semibold truncate max-w-[180px]">
                      {currentAnalysis.stream_info.file_name}
                    </span>
                  </div>
                  <div className="flex justify-between border-b border-[var(--border-dim)] pb-1.5">
                    <span className="text-[var(--text-muted)] font-sans text-xs">DETECTED FORMAT:</span>
                    <span className="text-[#FF6B35] font-bold">
                      {currentAnalysis.stream_info.detected_format}
                    </span>
                  </div>
                  <div className="flex justify-between border-b border-[var(--border-dim)] pb-1.5">
                    <span className="text-[var(--text-muted)] font-sans text-xs">TOTAL UNITS:</span>
                    <span className="text-[var(--text-main)]">
                      {currentAnalysis.stream_info.total_units.toLocaleString("en-US")}
                    </span>
                  </div>
                  <div className="flex justify-between border-b border-[var(--border-dim)] pb-1.5">
                    <span className="text-[var(--text-muted)] font-sans text-xs">ANALYSIS WINDOWS:</span>
                    <span className="text-[var(--text-main)]">
                      {currentAnalysis.stream_info.total_windows} (w={currentAnalysis.stream_info.window_size})
                    </span>
                  </div>
                  <div className="flex justify-between border-b border-[var(--border-dim)] pb-1.5">
                    <span className="text-[var(--text-muted)] font-sans text-xs">PAYLOAD BYTES:</span>
                    <span className="text-[var(--text-main)]">
                      {(currentAnalysis.stream_info.total_payload_bytes / 1024).toFixed(1)} KB
                    </span>
                  </div>
                  <div className="flex justify-between border-b border-[var(--border-dim)] pb-1.5">
                    <span className="text-[var(--text-muted)] font-sans text-xs">INTEGRITY RATIO:</span>
                    <span className="text-[var(--text-main)] font-bold">
                      {currentAnalysis.f1_health.integrity_ratio.toFixed(1)}%
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-[var(--text-muted)] font-sans text-xs">ANOMALIES (F2):</span>
                    <span className="text-[#FF6B35] font-semibold">
                      {currentAnalysis.f2_anomalies.anomaly_window_count} windows
                    </span>
                  </div>

                  {onNavigateTab && (
                    <div className="pt-3 border-t border-[var(--border-dim)] flex flex-col sm:flex-row gap-2">
                      <button
                        onClick={() => onNavigateTab("timeline")}
                        className="flex-1 py-1.5 px-2 bg-[var(--bg-main)] border border-[#FF6B35] text-[var(--text-main)] hover:bg-[#FF6B35] hover:text-[#0A0A0A] font-bold text-[11px] text-center transition-colors cursor-pointer"
                      >
                        [03] VIEW TIMELINE (F4) &rarr;
                      </button>
                      <button
                        onClick={() => onNavigateTab("anomalies")}
                        className="flex-1 py-1.5 px-2 bg-[var(--bg-main)] border border-[var(--border-main)] text-[var(--text-main)] hover:border-[#FF6B35] text-[11px] text-center transition-colors cursor-pointer"
                      >
                        [02] VIEW ANOMALIES &rarr;
                      </button>
                    </div>
                  )}
                </div>
              ) : (
                <div className="font-mono text-[12px] text-[var(--text-muted)] py-8 text-center">
                  NO STREAM CURRENTLY LOADED
                  <br />
                  <span className="text-[11px] text-[var(--text-muted)]">
                    Select preset or upload capture to begin
                  </span>
                </div>
              )}
            </div>

            {/* F7 Multi-Format Report Export Controls */}
            <div className="border border-[var(--border-main)] bg-[var(--bg-surface)] p-6">
              <div className="flex items-center justify-between border-b border-[var(--border-dim)] pb-3 mb-4">
                <h3 className="text-xs font-semibold uppercase tracking-wider text-[var(--text-muted)]">
                  Export Diagnostics (F7 Engine)
                </h3>
              </div>
              <p className="text-xs text-[var(--text-muted)] mb-4 leading-normal">
                Export comprehensive multi-page analytical summaries synthesized directly by the F7 report engine.
              </p>

              <div className="grid grid-cols-2 gap-2 font-mono text-[12px]">
                <a
                  href="/api/export?format=markdown&mode=analysis"
                  download="PRJ_111_Report.md"
                  className="p-2.5 border border-[var(--border-main)] hover:border-[#FF6B35] bg-[var(--bg-main)] text-center text-[var(--text-main)] transition-colors active:translate-y-[1px]"
                >
                  .MD (MARKDOWN)
                </a>
                <a
                  href="/api/export?format=html&mode=analysis"
                  download="PRJ_111_Report.html"
                  className="p-2.5 border border-[var(--border-main)] hover:border-[#FF6B35] bg-[var(--bg-main)] text-center text-[var(--text-main)] transition-colors active:translate-y-[1px]"
                >
                  .HTML (HTML5)
                </a>
                <a
                  href="/api/export?format=json&mode=analysis"
                  download="PRJ_111_Report.json"
                  className="p-2.5 border border-[var(--border-main)] hover:border-[#FF6B35] bg-[var(--bg-main)] text-center text-[var(--text-main)] transition-colors active:translate-y-[1px]"
                >
                  .JSON (RAW DATA)
                </a>
                <a
                  href="/api/export?format=text&mode=analysis"
                  download="PRJ_111_Report.txt"
                  className="p-2.5 border border-[var(--border-main)] hover:border-[#FF6B35] bg-[var(--bg-main)] text-center text-[var(--text-main)] transition-colors active:translate-y-[1px]"
                >
                  .TXT (ASCII LOG)
                </a>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};
