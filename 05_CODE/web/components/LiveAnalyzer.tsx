"use client";

import React, { useState, useEffect, useRef } from "react";
import {
  AnalysisResponse,
  BackendStatus,
  PresetDataset,
  StreamFormat,
} from "@/lib/types";
import { OFFLINE_DATA } from "@/lib/offlineData";

interface LiveAnalyzerProps {
  backendStatus: BackendStatus;
  currentAnalysis: AnalysisResponse | null;
  onAnalysisComplete: (result: AnalysisResponse) => void;
  onSelectOfflinePreset: (formatKey: "mpeg_ts" | "gse" | "bbframe") => void;
}

export const LiveAnalyzer: React.FC<LiveAnalyzerProps> = ({
  backendStatus,
  currentAnalysis,
  onAnalysisComplete,
  onSelectOfflinePreset,
}) => {
  const isOnline = backendStatus.status === "ONLINE";

  // State
  const [presets, setPresets] = useState<PresetDataset[]>([]);
  const [selectedPresetId, setSelectedPresetId] = useState<string>("");
  const [selectedFormat, setSelectedFormat] = useState<StreamFormat>("AUTO");
  const [windowSize, setWindowSize] = useState<number>(200);
  const [isAnalyzing, setIsAnalyzing] = useState<boolean>(false);
  const [loadingStep, setLoadingStep] = useState<string>("");
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
      // Offline mode: cannot upload to server, suggest switching to online or preset
      setErrorMsg(
        "Backend is offline. To analyze custom streams, start the Python backend (05_CODE/run_frontend.py). You can currently inspect verified captures below."
      );
      return;
    }

    try {
      setIsUploading(true);
      setLoadingStep("UPLOADING_STREAM_CHUNKS...");

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
    } catch (err: any) {
      setErrorMsg(err.message || "Failed to upload stream file.");
    } finally {
      setIsUploading(false);
    }
  };

  // Run Analysis
  const handleExecuteAnalysis = async () => {
    setErrorMsg(null);

    // If Offline Mode: switch to verified precompiled datasets
    if (!isOnline) {
      if (selectedPresetId.includes("gse") || selectedPresetId.includes("GSE")) {
        onSelectOfflinePreset("gse");
      } else if (
        selectedPresetId.includes("pcap") ||
        selectedPresetId.includes("bb_example")
      ) {
        onSelectOfflinePreset("bbframe");
      } else {
        onSelectOfflinePreset("mpeg_ts");
      }
      return;
    }

    // Live Backend Execution
    let targetFilePath = uploadedFilePath;
    if (!targetFilePath && selectedPresetId) {
      const found = presets.find((p) => p.id === selectedPresetId);
      if (found) targetFilePath = found.absolute_path;
    }

    if (!targetFilePath) {
      setErrorMsg("Please select a preset dataset or upload a stream capture first.");
      return;
    }

    setIsAnalyzing(true);
    setLoadingStep("SCANNING_STREAM... [F1-F7]");

    try {
      // Step simulator for industrial terminal feel
      const stepTimer1 = setTimeout(() => setLoadingStep("PARSING_INPUT_CONTAINERS..."), 300);
      const stepTimer2 = setTimeout(() => setLoadingStep("EXTRACTING_UNIFIED_FEATURES..."), 700);
      const stepTimer3 = setTimeout(() => setLoadingStep("RUNNING_ISOLATION_FOREST_F2..."), 1100);
      const stepTimer4 = setTimeout(() => setLoadingStep("SYNTHESIZING_F7_REPORTS..."), 1500);

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

      const resJson = await resp.json();
      if (!resp.ok || !resJson.success) {
        throw new Error(resJson.error || "Analysis failed.");
      }

      onAnalysisComplete(resJson);
    } catch (err: any) {
      setErrorMsg(err.message || "Execution failed. Check backend terminal logs.");
    } finally {
      setIsAnalyzing(false);
      setLoadingStep("");
    }
  };

  return (
    <section id="analyzer" className="w-full border-b border-[#262626] bg-[#0A0A0A] py-12">
      <div className="max-w-[1440px] mx-auto px-4">
        {/* Section Header */}
        <div className="flex flex-col md:flex-row md:items-end justify-between border-b border-[#262626] pb-4 mb-8">
          <div>
            <div className="font-mono text-[12px] text-[#737373] uppercase mb-1">
              WORKSTATION CONTROLLER // F1-F7 PIPELINE
            </div>
            <h2 className="text-[24px] md:text-[48px] font-bold uppercase tracking-tight text-[#E8E8E8]">
              STREAM INGESTION &amp; ANALYSIS
            </h2>
          </div>
          <div className="mt-4 md:mt-0 font-mono text-[12px]">
            <span
              className={`px-3 py-1 border ${
                isOnline
                  ? "border-[#262626] bg-[#141414] text-[#E8E8E8]"
                  : "border-[#FF6B35] bg-[#141414] text-[#FF6B35]"
              }`}
            >
              {isOnline
                ? "MODE A: LIVE BACKEND CONNECTED (127.0.0.1:8080)"
                : "MODE B: OFFLINE SHOWCASE (PRECOMPILED EMPIRICAL CAPTURE)"}
            </span>
          </div>
        </div>

        {/* Workstation Controls Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
          {/* Controls Column (8 cols) */}
          <div className="lg:col-span-8 space-y-6">
            {/* Source Selection Panel */}
            <div className="border border-[#262626] bg-[#141414] p-6">
              <div className="font-mono text-[12px] text-[#737373] uppercase border-b border-[#262626] pb-2 mb-4 flex justify-between">
                <span>[INPUT_CONFIGURATION]</span>
                <span>CONTENT-AWARE DETECTION ENABLED</span>
              </div>

              {/* Preset Selector */}
              <div className="space-y-4">
                <div>
                  <label className="block font-mono text-[12px] text-[#E8E8E8] uppercase mb-2">
                    SELECT AUTHORITATIVE BROADCAST PRESET:
                  </label>
                  {isOnline && presets.length > 0 ? (
                    <select
                      value={selectedPresetId}
                      onChange={(e) => handlePresetChange(e.target.value)}
                      className="w-full bg-[#0A0A0A] border border-[#262626] text-[#E8E8E8] font-mono text-[14px] p-3 focus:border-[#FF6B35] focus:outline-none"
                    >
                      {presets.map((p) => (
                        <option key={p.id} value={p.id}>
                          [{p.format}] {p.label} ({(p.file_size_bytes / 1024).toFixed(0)} KB)
                        </option>
                      ))}
                    </select>
                  ) : (
                    /* Offline Preset Selection Buttons */
                    <div className="grid grid-cols-1 sm:grid-cols-3 gap-2">
                      <button
                        onClick={() => {
                          setSelectedPresetId("mpeg_ts");
                          setWindowSize(200);
                          setSelectedFormat("MPEG_TS");
                          onSelectOfflinePreset("mpeg_ts");
                        }}
                        className={`p-3 text-left border font-mono text-[12px] transition-colors cursor-pointer ${
                          selectedPresetId === "mpeg_ts" || !selectedPresetId
                            ? "border-[#FF6B35] bg-[#0A0A0A] text-[#E8E8E8]"
                            : "border-[#262626] bg-[#0A0A0A] text-[#737373] hover:text-[#E8E8E8]"
                        }`}
                      >
                        <div className="font-bold text-[#E8E8E8]">[MPEG-TS]</div>
                        <div>sample.ts (3.4 MB)</div>
                        <div className="text-[12px] text-[#737373]">18,176 pkts // w=200</div>
                      </button>

                      <button
                        onClick={() => {
                          setSelectedPresetId("gse");
                          setWindowSize(3);
                          setSelectedFormat("GSE");
                          onSelectOfflinePreset("gse");
                        }}
                        className={`p-3 text-left border font-mono text-[12px] transition-colors cursor-pointer ${
                          selectedPresetId === "gse"
                            ? "border-[#FF6B35] bg-[#0A0A0A] text-[#E8E8E8]"
                            : "border-[#262626] bg-[#0A0A0A] text-[#737373] hover:text-[#E8E8E8]"
                        }`}
                      >
                        <div className="font-bold text-[#E8E8E8]">[GSE]</div>
                        <div>sample.ts (9.3 KB)</div>
                        <div className="text-[12px] text-[#737373]">14 PDUs // w=3</div>
                      </button>

                      <button
                        onClick={() => {
                          setSelectedPresetId("bbframe");
                          setWindowSize(50);
                          setSelectedFormat("BB_FRAME");
                          onSelectOfflinePreset("bbframe");
                        }}
                        className={`p-3 text-left border font-mono text-[12px] transition-colors cursor-pointer ${
                          selectedPresetId === "bbframe"
                            ? "border-[#FF6B35] bg-[#0A0A0A] text-[#E8E8E8]"
                            : "border-[#262626] bg-[#0A0A0A] text-[#737373] hover:text-[#E8E8E8]"
                        }`}
                      >
                        <div className="font-bold text-[#E8E8E8]">[BBFRAME]</div>
                        <div>dvb-s2_bb_example.pcap (2.3 MB)</div>
                        <div className="text-[12px] text-[#737373]">4,309 frames // w=50</div>
                      </button>
                    </div>
                  )}
                </div>

                {/* Upload Stream Alternative */}
                <div className="pt-2">
                  <div className="flex items-center justify-between mb-2">
                    <label className="font-mono text-[12px] text-[#737373] uppercase">
                      OR UPLOAD BINARY RECEIVER DUMP (.ts, .pcap, .bin):
                    </label>
                    {uploadedFile && (
                      <span className="font-mono text-[12px] text-[#E8E8E8]">
                        UPLOADED: {uploadedFile.name} ({(uploadedFile.size / 1024).toFixed(1)} KB)
                      </span>
                    )}
                  </div>
                  <input
                    ref={fileInputRef}
                    type="file"
                    onChange={handleFileUpload}
                    className="w-full bg-[#0A0A0A] border border-[#262626] text-[#737373] file:mr-4 file:py-2.5 file:px-4 file:border-0 file:bg-[#1f1f1f] file:text-[#E8E8E8] file:font-mono file:text-[12px] cursor-pointer"
                  />
                  <div className="font-mono text-[12px] text-[#737373] mt-1">
                    * Note: .ts extension does not force MPEG-TS. Backend detects GSE payload automatically.
                  </div>
                </div>
              </div>
            </div>

            {/* Analysis Parameters Bar */}
            <div className="border border-[#262626] bg-[#141414] p-6">
              <div className="font-mono text-[12px] text-[#737373] uppercase border-b border-[#262626] pb-2 mb-4">
                [PIPELINE_PARAMETERS]
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="block font-mono text-[12px] text-[#E8E8E8] uppercase mb-1">
                    STREAM FORMAT SELECTION:
                  </label>
                  <select
                    value={selectedFormat}
                    onChange={(e) => setSelectedFormat(e.target.value as StreamFormat)}
                    className="w-full bg-[#0A0A0A] border border-[#262626] text-[#E8E8E8] font-mono text-[14px] p-2.5 focus:border-[#FF6B35] focus:outline-none"
                  >
                    <option value="AUTO">AUTO (Content-Aware Detection)</option>
                    <option value="MPEG_TS">MPEG_TS (188B TS Packets)</option>
                    <option value="GSE">GSE (Generic Stream Encapsulation)</option>
                    <option value="BB_FRAME">BB_FRAME (DVB-S2 Baseband Frame)</option>
                  </select>
                </div>

                <div>
                  <label className="block font-mono text-[12px] text-[#E8E8E8] uppercase mb-1">
                    ANALYSIS WINDOW SIZE (UNITS):
                  </label>
                  <input
                    type="number"
                    min="1"
                    max="1000"
                    value={windowSize}
                    onChange={(e) => setWindowSize(Number(e.target.value))}
                    className="w-full bg-[#0A0A0A] border border-[#262626] text-[#E8E8E8] font-mono text-[14px] p-2.5 focus:border-[#FF6B35] focus:outline-none"
                  />
                  <span className="font-mono text-[12px] text-[#737373]">
                    Default: 200 (TS) // 3 (GSE) // 50 (BBFrame)
                  </span>
                </div>
              </div>

              {/* Execution CTA & Monospace Loading States */}
              <div className="mt-6 pt-4 border-t border-[#1A1A1A] flex flex-col sm:flex-row items-center justify-between gap-4">
                <button
                  onClick={handleExecuteAnalysis}
                  disabled={isAnalyzing || isUploading}
                  className={`w-full sm:w-auto font-mono text-[14px] font-bold px-8 py-3.5 border transition-colors cursor-pointer ${
                    isAnalyzing || isUploading
                      ? "border-[#737373] bg-[#141414] text-[#737373] cursor-not-allowed"
                      : "border-[#FF6B35] bg-[#FF6B35] text-[#0A0A0A] hover:bg-[#e05a28]"
                  }`}
                >
                  {isAnalyzing
                    ? "[PROCESSING_PIPELINE...]"
                    : isUploading
                    ? "[UPLOADING...]"
                    : isOnline
                    ? "[EXECUTE F1-F7 PIPELINE]"
                    : "[LOAD PRECOMPILED CAPTURE]"}
                </button>

                {/* Monospace Loading Indicator */}
                {(isAnalyzing || isUploading) && (
                  <div className="font-mono text-[12px] text-[#FF6B35] animate-pulse">
                    &gt; {loadingStep || "RUNNING_ANALYSIS..."}
                  </div>
                )}
              </div>

              {/* Error Notification */}
              {errorMsg && (
                <div className="mt-4 p-3 bg-[#0A0A0A] border border-[#FF6B35] text-[#FF6B35] font-mono text-[12px]">
                  ERROR: {errorMsg}
                </div>
              )}
            </div>
          </div>

          {/* Quick Summary / Status Column (4 cols) */}
          <div className="lg:col-span-4 flex flex-col gap-6">
            {/* Stream Execution Summary Card */}
            <div className="border border-[#262626] bg-[#141414] p-6">
              <div className="font-mono text-[12px] text-[#737373] uppercase border-b border-[#262626] pb-2 mb-4">
                [ACTIVE_STREAM_INSPECTION]
              </div>

              {currentAnalysis ? (
                <div className="space-y-3 font-mono text-[12px]">
                  <div className="flex justify-between border-b border-[#1A1A1A] pb-1.5">
                    <span className="text-[#737373]">FILE:</span>
                    <span className="text-[#E8E8E8] font-semibold truncate max-w-[180px]">
                      {currentAnalysis.stream_info.file_name}
                    </span>
                  </div>
                  <div className="flex justify-between border-b border-[#1A1A1A] pb-1.5">
                    <span className="text-[#737373]">DETECTED FORMAT:</span>
                    <span className="text-[#FF6B35] font-bold">
                      {currentAnalysis.stream_info.detected_format}
                    </span>
                  </div>
                  <div className="flex justify-between border-b border-[#1A1A1A] pb-1.5">
                    <span className="text-[#737373]">TOTAL UNITS:</span>
                    <span className="text-[#E8E8E8]">
                      {currentAnalysis.stream_info.total_units.toLocaleString()}
                    </span>
                  </div>
                  <div className="flex justify-between border-b border-[#1A1A1A] pb-1.5">
                    <span className="text-[#737373]">ANALYSIS WINDOWS:</span>
                    <span className="text-[#E8E8E8]">
                      {currentAnalysis.stream_info.total_windows} (w={currentAnalysis.stream_info.window_size})
                    </span>
                  </div>
                  <div className="flex justify-between border-b border-[#1A1A1A] pb-1.5">
                    <span className="text-[#737373]">PAYLOAD BYTES:</span>
                    <span className="text-[#E8E8E8]">
                      {(currentAnalysis.stream_info.total_payload_bytes / 1024).toFixed(1)} KB
                    </span>
                  </div>
                  <div className="flex justify-between border-b border-[#1A1A1A] pb-1.5">
                    <span className="text-[#737373]">INTEGRITY RATIO:</span>
                    <span className="text-[#E8E8E8] font-bold">
                      {currentAnalysis.f1_health.integrity_ratio.toFixed(1)}%
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-[#737373]">ANOMALIES (F2):</span>
                    <span className="text-[#FF6B35] font-semibold">
                      {currentAnalysis.f2_anomalies.anomaly_window_count} windows
                    </span>
                  </div>
                </div>
              ) : (
                <div className="font-mono text-[12px] text-[#737373] py-8 text-center">
                  NO STREAM CURRENTLY LOADED
                  <br />
                  <span className="text-[12px] text-[#262626]">
                    Select preset or upload capture to begin
                  </span>
                </div>
              )}
            </div>

            {/* F7 Multi-Format Report Export Controls */}
            <div className="border border-[#262626] bg-[#0A0A0A] p-6">
              <div className="font-mono text-[12px] text-[#737373] uppercase border-b border-[#1A1A1A] pb-2 mb-4">
                [F7_AUTOMATIC_REPORTS]
              </div>
              <p className="text-[12px] text-[#737373] mb-4">
                Export comprehensive multi-page analytical summaries synthesized directly by the F7 report engine.
              </p>

              <div className="grid grid-cols-2 gap-2 font-mono text-[12px]">
                <a
                  href="/api/export?format=markdown&mode=analysis"
                  download="PRJ_111_Report.md"
                  className="p-2.5 border border-[#262626] hover:border-[#E8E8E8] bg-[#141414] text-center text-[#E8E8E8] transition-colors"
                >
                  .MD (MARKDOWN)
                </a>
                <a
                  href="/api/export?format=html&mode=analysis"
                  download="PRJ_111_Report.html"
                  className="p-2.5 border border-[#262626] hover:border-[#E8E8E8] bg-[#141414] text-center text-[#E8E8E8] transition-colors"
                >
                  .HTML (HTML5)
                </a>
                <a
                  href="/api/export?format=json&mode=analysis"
                  download="PRJ_111_Report.json"
                  className="p-2.5 border border-[#262626] hover:border-[#E8E8E8] bg-[#141414] text-center text-[#E8E8E8] transition-colors"
                >
                  .JSON (RAW DATA)
                </a>
                <a
                  href="/api/export?format=text&mode=analysis"
                  download="PRJ_111_Report.txt"
                  className="p-2.5 border border-[#262626] hover:border-[#E8E8E8] bg-[#141414] text-center text-[#E8E8E8] transition-colors"
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
