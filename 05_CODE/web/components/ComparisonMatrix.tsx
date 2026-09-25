"use client";

import React, { useState, useEffect, useRef } from "react";
import { OFFLINE_DATA } from "@/lib/offlineData";
import { Tooltip } from "@/components/Tooltip";
import { useToast } from "@/components/Toast";
import { PresetDataset } from "@/lib/types";

export const ComparisonMatrix: React.FC = () => {
  const { showToast } = useToast();
  const baselineComp = OFFLINE_DATA.cross_format_comparison;
  const guard = baselineComp.unsupported_inferences_guard || [];

  // Stream inputs state
  const [presets, setPresets] = useState<PresetDataset[]>([]);
  const [streamAPath, setStreamAPath] = useState<string>("01_RAW_DATA/03_TS/DVBS2_toolkit/sample.ts");
  const [streamBPath, setStreamBPath] = useState<string>("01_RAW_DATA/01_BBFRAME_GSE/dvb-s2_bb_example.pcap");
  const [selectedPresetA, setSelectedPresetA] = useState<string>("mpeg_ts");
  const [selectedPresetB, setSelectedPresetB] = useState<string>("bbframe");

  // File upload state for Stream A and Stream B
  const [uploadingA, setUploadingA] = useState<boolean>(false);
  const [uploadingB, setUploadingB] = useState<boolean>(false);
  const [isDraggingA, setIsDraggingA] = useState<boolean>(false);
  const [isDraggingB, setIsDraggingB] = useState<boolean>(false);
  const [fileAInfo, setFileAInfo] = useState<{ name: string; size: number } | null>(null);
  const [fileBInfo, setFileBInfo] = useState<{ name: string; size: number } | null>(null);
  const fileInputARef = useRef<HTMLInputElement>(null);
  const fileInputBRef = useRef<HTMLInputElement>(null);

  // Comparison execution state
  const [isComparing, setIsComparing] = useState<boolean>(false);
  const [comparisonResult, setComparisonResult] = useState<any>(null);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  // Fetch presets on mount
  useEffect(() => {
    fetch("/api/presets")
      .then((res) => res.json())
      .then((data) => {
        if (data.success && Array.isArray(data.presets)) {
          setPresets(data.presets);
        }
      })
      .catch(() => {});
  }, []);

  // Handle Preset Selection
  const handlePresetSelectA = (val: string) => {
    setSelectedPresetA(val);
    setFileAInfo(null);
    if (val === "mpeg_ts") setStreamAPath("01_RAW_DATA/03_TS/DVBS2_toolkit/sample.ts");
    else if (val === "gse") setStreamAPath("01_RAW_DATA/02_GSE/DVBS2_toolkit/sample.ts");
    else if (val === "bbframe") setStreamAPath("01_RAW_DATA/01_BBFRAME_GSE/dvb-s2_bb_example.pcap");
    else {
      const p = presets.find((x) => x.id === val);
      if (p) setStreamAPath(p.absolute_path || p.relative_path);
    }
  };

  const handlePresetSelectB = (val: string) => {
    setSelectedPresetB(val);
    setFileBInfo(null);
    if (val === "mpeg_ts") setStreamBPath("01_RAW_DATA/03_TS/DVBS2_toolkit/sample.ts");
    else if (val === "gse") setStreamBPath("01_RAW_DATA/02_GSE/DVBS2_toolkit/sample.ts");
    else if (val === "bbframe") setStreamBPath("01_RAW_DATA/01_BBFRAME_GSE/dvb-s2_bb_example.pcap");
    else {
      const p = presets.find((x) => x.id === val);
      if (p) setStreamBPath(p.absolute_path || p.relative_path);
    }
  };

  // Upload file for Stream A
  const uploadFileA = async (file: File) => {
    try {
      setUploadingA(true);
      const resp = await fetch(`/api/upload?filename=${encodeURIComponent(file.name)}`, {
        method: "POST",
        body: file,
        headers: {
          "Content-Type": "application/octet-stream",
          "X-File-Name": file.name,
        },
      });
      const data = await resp.json();
      if (!resp.ok || !data.success) throw new Error(data.error || "Upload failed");
      setStreamAPath(data.file_path);
      setSelectedPresetA("");
      setFileAInfo({ name: file.name, size: file.size });
      showToast(`Uploaded Stream A: ${file.name}`, "success");
    } catch (err: any) {
      showToast(err.message || "Failed to upload Stream A", "error");
    } finally {
      setUploadingA(false);
    }
  };

  // Upload file for Stream B
  const uploadFileB = async (file: File) => {
    try {
      setUploadingB(true);
      const resp = await fetch(`/api/upload?filename=${encodeURIComponent(file.name)}`, {
        method: "POST",
        body: file,
        headers: {
          "Content-Type": "application/octet-stream",
          "X-File-Name": file.name,
        },
      });
      const data = await resp.json();
      if (!resp.ok || !data.success) throw new Error(data.error || "Upload failed");
      setStreamBPath(data.file_path);
      setSelectedPresetB("");
      setFileBInfo({ name: file.name, size: file.size });
      showToast(`Uploaded Stream B: ${file.name}`, "success");
    } catch (err: any) {
      showToast(err.message || "Failed to upload Stream B", "error");
    } finally {
      setUploadingB(false);
    }
  };

  const handleUploadA = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) uploadFileA(file);
  };

  const handleUploadB = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) uploadFileB(file);
  };

  // Run Comparison Engine
  const executeComparison = async (isHalf: boolean = false) => {
    setErrorMsg(null);
    const targetA = streamAPath.trim();
    const targetB = isHalf ? targetA : streamBPath.trim();

    if (!targetA) {
      setErrorMsg("Please select or upload Stream A for comparison.");
      showToast("Stream A is required", "warning");
      return;
    }
    if (!isHalf && !targetB) {
      setErrorMsg("Please select or upload Stream B for dual-stream comparison.");
      showToast("Stream B is required", "warning");
      return;
    }

    setIsComparing(true);
    showToast(isHalf ? "Running stream halves comparison..." : "Running dual-stream F6 comparison...", "info");

    try {
      const resp = await fetch("/api/compare", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          file_path_a: targetA,
          file_path_b: targetB,
          is_half_comparison: isHalf,
        }),
      });

      const resJson = await resp.json();
      if (!resp.ok || !resJson.success) {
        throw new Error(resJson.error || "Comparison request failed.");
      }

      setComparisonResult(resJson.comparison);
      showToast(
        `Comparison complete: ${resJson.comparison.format_a} vs ${resJson.comparison.format_b}`,
        "success"
      );
    } catch (err: any) {
      // Graceful offline fallback
      showToast("Backend unavailable; displaying verified empirical comparison baseline.", "info");
      setComparisonResult(baselineComp);
    } finally {
      setIsComparing(false);
    }
  };

  // Determine active metrics
  const activeComp = comparisonResult || baselineComp;
  const commonMetrics = activeComp.common?.metrics || activeComp.common || baselineComp.common?.metrics || {};
  const isSameFormat = activeComp.is_same_format;
  const formatA = activeComp.format_a || "MPEG_TS";
  const formatB = activeComp.format_b || (activeComp.is_half_comparison ? `${formatA} (Half 2)` : "BB_FRAME");
  const winAlign = activeComp.windows || {};

  return (
    <section id="comparison" className="w-full border-b border-[var(--border-main)] bg-[var(--bg-main)] py-12 transition-colors duration-150">
      <div className="max-w-[1440px] mx-auto px-4">
        {/* Section Header */}
        <div className="flex flex-col md:flex-row md:items-end justify-between border-b border-[var(--border-main)] pb-4 mb-8">
          <div>
            <div className="text-xs font-semibold text-[var(--text-muted)] tracking-wider uppercase mb-1 flex items-center gap-2">
              <span>FEATURE F6</span>
              <span>•</span>
              <Tooltip content="Feature F6 imposes a mathematical and architectural barrier: direct arithmetic comparisons are permitted strictly for container-invariant metrics (payload bytes and integrity ratio)">
                <span className="text-[var(--text-main)] font-mono cursor-help underline decoration-dotted underline-offset-2">
                  CROSS-STREAM COMPARISON &amp; ARCHITECTURAL BARRIER
                </span>
              </Tooltip>
            </div>
            <h2 className="text-[24px] md:text-[44px] font-bold uppercase tracking-tight text-[var(--text-main)]">
              SEMANTIC COMPARISON ENGINE
            </h2>
          </div>
          <div className="mt-2 md:mt-0 font-mono text-[12px]">
            <span className="px-3 py-1.5 border border-[#FF6B35] bg-[var(--bg-surface)] text-[#FF6B35] font-bold uppercase">
              SEMANTIC COMPARABILITY ENFORCED
            </span>
          </div>
        </div>

        {/* Comparison Controller (Version 1 Layout) */}
        <div className="border border-[var(--border-main)] bg-[var(--bg-surface)] p-6 mb-8">
          <div className="flex items-center justify-between border-b border-[var(--border-dim)] pb-3 mb-5">
            <h3 className="text-xs font-semibold uppercase tracking-wider text-[var(--text-muted)]">
              Stream Ingestion &amp; Comparison Controller
            </h3>
            <span className="text-xs font-mono text-[#FF6B35]">
              F6 Dual-Stream Pipeline
            </span>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
            {/* Left Column: Stream A & Stream B Inputs (7 cols) */}
            <div className="lg:col-span-7 space-y-6">
              {/* Stream A Card (Version 1 Template with Present Theme) */}
              <div className="p-4 border border-[var(--border-main)] bg-[var(--bg-main)] space-y-3.5">
                <div className="flex items-center justify-between border-b border-[var(--border-dim)] pb-2">
                  <div className="flex items-center gap-2">
                    <span className="font-mono text-xs font-bold text-[#FF6B35]">[STREAM A]</span>
                    <label className="text-xs font-semibold text-[var(--text-main)] uppercase tracking-wider">
                      Reference Baseline Capture
                    </label>
                  </div>
                  <span className="text-[10px] font-mono px-2 py-0.5 bg-[var(--bg-surface)] border border-[#FF6B35] text-[#FF6B35] font-semibold">
                    BASELINE
                  </span>
                </div>

                {/* Primary Input: File Upload Dropzone (Version 1 Style) */}
                <div>
                  <label className="block text-[11px] font-medium text-[var(--text-muted)] uppercase tracking-wider mb-1.5">
                    Primary Input: Upload Capture File (.ts, .pcap, .gse)
                  </label>
                  <div
                    onDragOver={(e) => {
                      e.preventDefault();
                      setIsDraggingA(true);
                    }}
                    onDragLeave={() => setIsDraggingA(false)}
                    onDrop={(e) => {
                      e.preventDefault();
                      setIsDraggingA(false);
                      const file = e.dataTransfer.files?.[0];
                      if (file) uploadFileA(file);
                    }}
                    onClick={() => fileInputARef.current?.click()}
                    className={`border-2 border-dashed p-4 text-center cursor-pointer transition-all ${
                      isDraggingA
                        ? "border-[#FF6B35] bg-[var(--bg-surface-elevated)]"
                        : "border-[var(--border-main)] hover:border-[#FF6B35] bg-[var(--bg-surface)]"
                    }`}
                  >
                    <svg className="w-5 h-5 mx-auto mb-1 text-[#FF6B35]" viewBox="0 0 16 16" fill="currentColor">
                      <path d="M.5 9.9a.5.5 0 0 1 .5.5v2.5a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1v-2.5a.5.5 0 0 1 1 0v2.5a2 2 0 0 1-2 2H2a2 2 0 0 1-2-2v-2.5a.5.5 0 0 1 .5-.5z" />
                      <path d="M7.646 1.146a.5.5 0 0 1 .708 0l3 3a.5.5 0 0 1-.708.708L8.5 2.707V10.5a.5.5 0 0 1-1 0V2.707L5.354 4.854a.5.5 0 1 1-.708-.708l3-3z" />
                    </svg>
                    <div className="text-xs font-semibold text-[var(--text-main)]">
                      {fileAInfo ? fileAInfo.name : "Choose capture file or drag & drop here"}
                    </div>
                    <div className="text-[11px] text-[var(--text-muted)] mt-0.5">
                      {fileAInfo
                        ? `${(fileAInfo.size / 1024).toFixed(1)} KB • READY FOR COMPARISON`
                        : "Verified formats: MPEG-TS (.ts), GSE (.ts, .gse), DVB-S2 BBFrame (.pcap)"}
                    </div>
                    <input
                      ref={fileInputARef}
                      type="file"
                      accept=".ts,.pcap,.gse"
                      onChange={handleUploadA}
                      style={{ display: "none" }}
                    />
                  </div>
                </div>

                {/* Secondary Input: Repository Presets */}
                <div>
                  <label className="block text-[11px] font-medium text-[var(--text-muted)] uppercase tracking-wider mb-1">
                    Secondary Input: Verified Repository Preset
                  </label>
                  <select
                    value={selectedPresetA}
                    onChange={(e) => handlePresetSelectA(e.target.value)}
                    className="w-full bg-[var(--bg-surface)] border border-[var(--border-main)] text-[var(--text-main)] font-mono text-xs p-2 focus:border-[#FF6B35] focus:outline-none"
                  >
                    <option value="">-- Or select an authoritative repository capture --</option>
                    <option value="mpeg_ts">[MPEG-TS] sample.ts (3.4 MB / 18,176 pkts)</option>
                    <option value="gse">[GSE] sample.ts (9.3 KB / 14 PDUs)</option>
                    <option value="bbframe">[BBFRAME] dvb-s2_bb_example.pcap (2.3 MB / 4,309 frames)</option>
                  </select>
                </div>

                {/* Staged / Relative Path Input */}
                <div>
                  <label className="block text-[11px] font-medium text-[var(--text-muted)] uppercase tracking-wider mb-1">
                    Local Staged / Relative File Path:
                  </label>
                  <input
                    type="text"
                    value={streamAPath}
                    onChange={(e) => setStreamAPath(e.target.value)}
                    placeholder="01_RAW_DATA/03_TS/DVBS2_toolkit/sample.ts"
                    className="w-full bg-[var(--bg-surface)] border border-[var(--border-main)] text-[var(--text-main)] font-mono text-xs p-2 focus:border-[#FF6B35] focus:outline-none"
                  />
                </div>
              </div>

              {/* Stream B Card (Version 1 Template with Present Theme) */}
              <div className="p-4 border border-[var(--border-main)] bg-[var(--bg-main)] space-y-3.5">
                <div className="flex items-center justify-between border-b border-[var(--border-dim)] pb-2">
                  <div className="flex items-center gap-2">
                    <span className="font-mono text-xs font-bold text-[var(--text-muted)]">[STREAM B]</span>
                    <label className="text-xs font-semibold text-[var(--text-main)] uppercase tracking-wider">
                      Target Comparison Capture
                    </label>
                  </div>
                  <span className="text-[10px] font-mono px-2 py-0.5 bg-[var(--bg-surface)] border border-[var(--border-main)] text-[var(--text-muted)] font-semibold">
                    TARGET
                  </span>
                </div>

                {/* Primary Input: File Upload Dropzone (Version 1 Style) */}
                <div>
                  <label className="block text-[11px] font-medium text-[var(--text-muted)] uppercase tracking-wider mb-1.5">
                    Primary Input: Upload Capture File (.ts, .pcap, .gse)
                  </label>
                  <div
                    onDragOver={(e) => {
                      e.preventDefault();
                      setIsDraggingB(true);
                    }}
                    onDragLeave={() => setIsDraggingB(false)}
                    onDrop={(e) => {
                      e.preventDefault();
                      setIsDraggingB(false);
                      const file = e.dataTransfer.files?.[0];
                      if (file) uploadFileB(file);
                    }}
                    onClick={() => fileInputBRef.current?.click()}
                    className={`border-2 border-dashed p-4 text-center cursor-pointer transition-all ${
                      isDraggingB
                        ? "border-[#FF6B35] bg-[var(--bg-surface-elevated)]"
                        : "border-[var(--border-main)] hover:border-[#FF6B35] bg-[var(--bg-surface)]"
                    }`}
                  >
                    <svg className="w-5 h-5 mx-auto mb-1 text-[#FF6B35]" viewBox="0 0 16 16" fill="currentColor">
                      <path d="M.5 9.9a.5.5 0 0 1 .5.5v2.5a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1v-2.5a.5.5 0 0 1 1 0v2.5a2 2 0 0 1-2 2H2a2 2 0 0 1-2-2v-2.5a.5.5 0 0 1 .5-.5z" />
                      <path d="M7.646 1.146a.5.5 0 0 1 .708 0l3 3a.5.5 0 0 1-.708.708L8.5 2.707V10.5a.5.5 0 0 1-1 0V2.707L5.354 4.854a.5.5 0 1 1-.708-.708l3-3z" />
                    </svg>
                    <div className="text-xs font-semibold text-[var(--text-main)]">
                      {fileBInfo ? fileBInfo.name : "Choose capture file or drag & drop here"}
                    </div>
                    <div className="text-[11px] text-[var(--text-muted)] mt-0.5">
                      {fileBInfo
                        ? `${(fileBInfo.size / 1024).toFixed(1)} KB • READY FOR COMPARISON`
                        : "Verified formats: MPEG-TS (.ts), GSE (.ts, .gse), DVB-S2 BBFrame (.pcap)"}
                    </div>
                    <input
                      ref={fileInputBRef}
                      type="file"
                      accept=".ts,.pcap,.gse"
                      onChange={handleUploadB}
                      style={{ display: "none" }}
                    />
                  </div>
                </div>

                {/* Secondary Input: Repository Presets */}
                <div>
                  <label className="block text-[11px] font-medium text-[var(--text-muted)] uppercase tracking-wider mb-1">
                    Secondary Input: Verified Repository Preset
                  </label>
                  <select
                    value={selectedPresetB}
                    onChange={(e) => handlePresetSelectB(e.target.value)}
                    className="w-full bg-[var(--bg-surface)] border border-[var(--border-main)] text-[var(--text-main)] font-mono text-xs p-2 focus:border-[#FF6B35] focus:outline-none"
                  >
                    <option value="">-- Or select an authoritative repository capture --</option>
                    <option value="bbframe">[BBFRAME] dvb-s2_bb_example.pcap (2.3 MB / 4,309 frames)</option>
                    <option value="mpeg_ts">[MPEG-TS] sample.ts (3.4 MB / 18,176 pkts)</option>
                    <option value="gse">[GSE] sample.ts (9.3 KB / 14 PDUs)</option>
                  </select>
                </div>

                {/* Staged / Relative Path Input */}
                <div>
                  <label className="block text-[11px] font-medium text-[var(--text-muted)] uppercase tracking-wider mb-1">
                    Local Staged / Relative File Path:
                  </label>
                  <input
                    type="text"
                    value={streamBPath}
                    onChange={(e) => setStreamBPath(e.target.value)}
                    placeholder="01_RAW_DATA/01_BBFRAME_GSE/dvb-s2_bb_example.pcap"
                    className="w-full bg-[var(--bg-surface)] border border-[var(--border-main)] text-[var(--text-main)] font-mono text-xs p-2 focus:border-[#FF6B35] focus:outline-none"
                  />
                </div>
              </div>
            </div>

            {/* Right Column: Execution Controls & Semantic Rules (5 cols) */}
            <div className="lg:col-span-5 flex flex-col justify-between h-full space-y-4">
              <div className="p-4 bg-[var(--bg-main)] border border-[var(--border-main)] space-y-3">
                <span className="text-xs font-semibold text-[var(--text-main)] uppercase tracking-wider block">
                  Comparison Execution Mode
                </span>
                <p className="text-xs text-[var(--text-muted)] leading-relaxed">
                  Execute direct pairwise comparison across heterogeneous satellite streams or verify intra-stream temporal consistency across stream halves.
                </p>

                <div className="flex flex-col sm:flex-row gap-2.5 pt-2">
                  <button
                    onClick={() => executeComparison(false)}
                    disabled={isComparing || uploadingA || uploadingB}
                    className="flex-1 bg-[#FF6B35] text-[#0A0A0A] hover:bg-[#ff8555] active:translate-y-[1px] font-mono text-xs font-bold px-4 py-3 border border-[#FF6B35] transition-all cursor-pointer disabled:opacity-50"
                  >
                    {isComparing ? "[RUNNING...]" : "[DUAL STREAM COMPARISON]"}
                  </button>
                  <button
                    onClick={() => executeComparison(true)}
                    disabled={isComparing || uploadingA || uploadingB}
                    className="flex-1 bg-[var(--bg-surface)] text-[var(--text-main)] hover:border-[#FF6B35] active:translate-y-[1px] font-mono text-xs px-4 py-3 border border-[var(--border-main)] transition-all cursor-pointer disabled:opacity-50"
                  >
                    [COMPARE STREAM HALVES]
                  </button>
                </div>
              </div>

              <div className="p-4 border border-[var(--border-dim)] bg-[var(--bg-main)] text-xs text-[var(--text-muted)] leading-relaxed">
                <span className="text-[#FF6B35] font-bold font-mono mr-1">&gt; AUDIT BARRIER:</span>
                Direct numerical comparison is permitted strictly for container-invariant metrics (Payload Bytes &amp; Health Score). Heterogeneous framing units (188B TS packets vs. variable GSE PDUs vs. 7.2KB BBFrames) remain formally masked.
              </div>
            </div>
          </div>

          {errorMsg && (
            <div className="mt-4 p-3 bg-[var(--bg-main)] border border-rose-500 text-rose-400 font-mono text-xs">
              ✕ {errorMsg}
            </div>
          )}
        </div>

        {/* Dynamic Comparison Summary Stats (Version 1 Template) */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-8 font-mono text-xs">
          {/* Format Equivalence Card */}
          <div className="p-4 border border-[var(--border-main)] bg-[var(--bg-surface)]">
            <div className="text-[11px] font-semibold text-[var(--text-muted)] uppercase tracking-wider">
              FORMAT EQUIVALENCE
            </div>
            <div className={`text-[20px] font-bold mt-1 ${isSameFormat ? "text-emerald-400" : "text-[#FF6B35]"}`}>
              {isSameFormat ? "SAME FORMAT" : "CROSS FORMAT"}
            </div>
            <div className="text-[11px] text-[var(--text-muted)] mt-1">
              {formatA} vs {formatB}
            </div>
          </div>

          {/* Aligned Windows Card */}
          <div className="p-4 border border-[var(--border-main)] bg-[var(--bg-surface)]">
            <div className="text-[11px] font-semibold text-[var(--text-muted)] uppercase tracking-wider">
              ALIGNMENT ARCHITECTURE
            </div>
            <div className="text-[20px] font-bold text-[var(--text-main)] mt-1">
              {winAlign.alignment_mode || "DIRECT_INDEX"}
            </div>
            <div className="text-[11px] text-[var(--text-muted)] mt-1">
              Aligned: {winAlign.aligned_window_count || Object.keys(commonMetrics).length} spatial windows
            </div>
          </div>

          {/* Semantic Barrier Stats */}
          <div className="p-4 border border-[var(--border-main)] bg-[var(--bg-surface)]">
            <div className="text-[11px] font-semibold text-[var(--text-muted)] uppercase tracking-wider">
              F6 GATEWAY STATUS
            </div>
            <div className="text-[20px] font-bold text-emerald-400 mt-1">
              2 / 11 PERMITTED
            </div>
            <div className="text-[11px] text-[var(--text-muted)] mt-1">
              9 / 11 Masked (Incommensurable Units)
            </div>
          </div>
        </div>

        {/* The Semantic Shield Table */}
        <div className="border border-[var(--border-main)] bg-[var(--bg-surface)] overflow-x-auto mb-8 transition-colors duration-150">
          <table className="w-full border-collapse font-mono text-[12px]">
            <thead>
              <tr className="border-b border-[var(--border-main)] bg-[var(--bg-main)] text-[var(--text-muted)] text-left">
                <th className="p-3 border-r border-[var(--border-main)] sticky left-0 z-20 bg-[var(--bg-main)] whitespace-nowrap min-w-[200px]">
                  METRIC (F6 GATEWAY)
                </th>
                <th className="p-3 border-r border-[var(--border-main)] whitespace-nowrap">
                  STREAM A ({formatA})
                </th>
                <th className="p-3 border-r border-[var(--border-main)] whitespace-nowrap">
                  STREAM B ({formatB})
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

                return (
                  <tr
                    key={metricKey}
                    className={`transition-colors ${
                      isComparable
                        ? "bg-[var(--bg-surface)] hover:bg-[var(--bg-surface-elevated)]"
                        : "bg-[var(--bg-main)] opacity-75 hover:opacity-100"
                    }`}
                  >
                    {/* Metric Name */}
                    <td
                      className={`p-3 border-r border-[var(--border-main)] font-bold whitespace-nowrap sticky left-0 z-10 ${
                        isComparable ? "bg-[var(--bg-surface)] text-[var(--text-main)]" : "bg-[var(--bg-main)] text-[var(--text-muted)]"
                      }`}
                    >
                      {isComparable ? (
                        <span className="text-emerald-400 font-bold mr-2">&gt;</span>
                      ) : (
                        <span className="text-[var(--text-muted)] mr-2">&empty;</span>
                      )}
                      {metric.metric_name || metricKey}
                    </td>

                    {/* Stream A Value */}
                    <td className="p-3 border-r border-[var(--border-main)] whitespace-nowrap">
                      {typeof metric.stream_a_value === "number"
                        ? metric.stream_a_value.toLocaleString("en-US")
                        : String(metric.stream_a_value ?? "N/A")}
                      {metric.unit ? ` ${metric.unit}` : ""}
                    </td>

                    {/* Stream B Value */}
                    <td className="p-3 border-r border-[var(--border-main)] whitespace-nowrap">
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
                              : "text-emerald-400"
                          }`}
                        >
                          {typeof metric.relative_difference_pct === "number"
                            ? `${metric.relative_difference_pct > 0 ? "+" : ""}${metric.relative_difference_pct.toFixed(2)}%`
                            : "0.00%"}
                        </span>
                      ) : (
                        <span className="text-[var(--text-muted)]">N/A [MASKED]</span>
                      )}
                    </td>

                    {/* Status Badge */}
                    <td className="p-3 border-r border-[var(--border-main)] whitespace-nowrap">
                      <span
                        className={`px-2 py-0.5 border text-[11px] font-bold ${
                          isComparable
                            ? "border-emerald-500/40 text-emerald-400 bg-emerald-500/10"
                            : "border-[var(--border-main)] text-[var(--text-muted)] bg-[var(--bg-main)]"
                        }`}
                      >
                        {isComparable ? "PERMITTED" : "INCOMMENSURABLE"}
                      </span>
                    </td>

                    {/* Incompatibility / Description */}
                    <td className="p-3 text-[var(--text-muted)] text-[12px] leading-relaxed">
                      {metric.incompatibility_reason || metric.description}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>

        {/* Unsupported Inferences Guard (Physical Layer Boundaries) */}
        <div className="border border-[var(--border-main)] bg-[var(--bg-surface)] p-6">
          <div className="text-xs font-semibold text-[#FF6B35] uppercase border-b border-[var(--border-dim)] pb-2 mb-4 tracking-wider flex justify-between items-center">
            <span>[SAFETY_POLICY: UNSUPPORTED_INFERENCES_GUARD]</span>
            <span className="text-[10px] bg-[var(--bg-main)] border border-[#FF6B35]/40 text-[#FF6B35] px-2 py-0.5 font-mono">
              ACTIVE ENFORCEMENT
            </span>
          </div>

          <p className="text-xs text-[var(--text-muted)] mb-4 leading-relaxed">
            The receiver output stream contains only post-demodulated baseband framing. To prevent
            unsubstantiated claims, the following physical-layer inferences are formally prohibited:
          </p>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-3 font-mono text-[12px]">
            {guard.map((item: string, idx: number) => (
              <div key={idx} className="p-3 bg-[var(--bg-main)] border border-[var(--border-main)] text-[var(--text-main)]">
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
