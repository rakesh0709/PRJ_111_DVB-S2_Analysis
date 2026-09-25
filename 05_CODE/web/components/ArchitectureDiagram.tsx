"use client";

import React, { useState } from "react";
import { Tooltip } from "@/components/Tooltip";

export const ArchitectureDiagram: React.FC = () => {
  const [activeTab, setActiveTab] = useState<"analysis" | "application">("analysis");

  return (
    <section id="architecture" className="w-full border-b border-[var(--border-main)] bg-[var(--bg-main)] py-12 transition-colors duration-150">
      <div className="max-w-[1440px] mx-auto px-4">
        {/* Section Header */}
        <div className="flex flex-col md:flex-row md:items-end justify-between border-b border-[var(--border-main)] pb-4 mb-8">
          <div>
            <div className="font-mono text-[12px] text-[var(--text-muted)] uppercase mb-1 flex items-center gap-2">
              <span>SYSTEM DESIGN</span>
              <span>//</span>
              <Tooltip content="Toggle between Perspective A (analytical pipeline architecture) and Perspective B (full-stack runtime architecture)">
                <span>DUAL PERSPECTIVE SCHEMATICS</span>
              </Tooltip>
            </div>
            <h2 className="text-[24px] md:text-[48px] font-bold uppercase tracking-tight text-[var(--text-main)]">
              ARCHITECTURE &amp; DATAFLOW
            </h2>
          </div>

          <div className="flex gap-2 mt-4 md:mt-0 font-mono text-[12px]">
            <button
              onClick={() => setActiveTab("analysis")}
              className={`px-4 py-2 border transition-all cursor-pointer active:translate-y-[1px] ${
                activeTab === "analysis"
                  ? "border-[#FF6B35] bg-[var(--bg-surface-elevated)] text-[var(--text-main)] font-bold ring-1 ring-[#FF6B35]"
                  : "border-[var(--border-main)] bg-[var(--bg-surface)] text-[var(--text-muted)] hover:text-[var(--text-main)] hover:border-[var(--text-muted)]"
              }`}
            >
              [A] SOFTWARE PIPELINE
            </button>
            <button
              onClick={() => setActiveTab("application")}
              className={`px-4 py-2 border transition-all cursor-pointer active:translate-y-[1px] ${
                activeTab === "application"
                  ? "border-[#FF6B35] bg-[var(--bg-surface-elevated)] text-[var(--text-main)] font-bold ring-1 ring-[#FF6B35]"
                  : "border-[var(--border-main)] bg-[var(--bg-surface)] text-[var(--text-muted)] hover:text-[var(--text-main)] hover:border-[var(--text-muted)]"
              }`}
            >
              [B] FULL-STACK RUNTIME
            </button>
          </div>
        </div>

        {/* View A: Software Pipeline */}
        {activeTab === "analysis" && (
          <div className="border border-[var(--border-main)] bg-[var(--bg-surface)] p-8 transition-colors duration-150">
            <div className="font-mono text-[12px] text-[var(--text-muted)] uppercase border-b border-[var(--border-dim)] pb-3 mb-6 flex flex-wrap justify-between items-center gap-2">
              <span>PERSPECTIVE A: MULTI-FORMAT PARSING &amp; ANALYTICAL ENGINE</span>
              <span className="text-[#FF6B35] font-bold px-2 py-0.5 bg-[var(--bg-main)] border border-[var(--border-main)]">
                MUTUALLY EXCLUSIVE ALTERNATIVE INPUTS (NON-SEQUENTIAL)
              </span>
            </div>

            {/* Swiss Block Diagram */}
            <div className="space-y-4 font-mono text-[12px]">
              {/* Level 0: Ingestion (Alternative Inputs) */}
              <div>
                <div className="text-[11px] text-[var(--text-muted)] uppercase mb-2 flex items-center justify-between">
                  <span>ALTERNATIVE INPUT STREAMS (CHOOSE EXACTLY ONE):</span>
                  <span className="text-[#FF6B35]">* NOT sequential stages; each capture is parsed independently</span>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                  <div className="p-4 border border-[var(--border-main)] bg-[var(--bg-main)] text-center hover:border-[#FF6B35] transition-colors">
                    <div className="text-[11px] text-[var(--text-muted)] uppercase">ALTERNATIVE FORMAT 01</div>
                    <div className="font-bold text-[var(--text-main)] text-[14px] mt-1">MPEG-TS (.ts)</div>
                    <div className="text-[11px] text-[var(--text-muted)] mt-1">188-byte Packets // Sync 0x47</div>
                  </div>
                  <div className="p-4 border border-[var(--border-main)] bg-[var(--bg-main)] text-center hover:border-[#FF6B35] transition-colors">
                    <div className="text-[11px] text-[var(--text-muted)] uppercase">ALTERNATIVE FORMAT 02</div>
                    <div className="font-bold text-[var(--text-main)] text-[14px] mt-1">GSE (.ts / .bin)</div>
                    <div className="text-[11px] text-[var(--text-muted)] mt-1">ETSI TS 102 606 // Variable PDU</div>
                  </div>
                  <div className="p-4 border border-[var(--border-main)] bg-[var(--bg-main)] text-center hover:border-[#FF6B35] transition-colors">
                    <div className="text-[11px] text-[var(--text-muted)] uppercase">ALTERNATIVE FORMAT 03</div>
                    <div className="font-bold text-[var(--text-main)] text-[14px] mt-1">BBFRAME (.pcap / .bin)</div>
                    <div className="text-[11px] text-[var(--text-muted)] mt-1">ETSI EN 302 307 // 10B BBHeader</div>
                  </div>
                </div>
              </div>

              {/* Connecting Down Arrow */}
              <div className="text-center text-[var(--text-muted)] font-bold text-[14px]">&darr;</div>

              {/* Level 1: Stream Handler & Content Detection */}
              <div className="p-4 border border-[var(--border-main)] bg-[var(--bg-main)] text-center">
                <div className="text-[11px] text-[var(--text-muted)] uppercase">STREAM HANDLER // INGESTION</div>
                <div className="font-bold text-[var(--text-main)] text-[14px] mt-1">
                  CONTENT-AWARE FORMAT DETECTOR
                </div>
                <div className="text-[11px] text-[var(--text-muted)] mt-1 max-w-[640px] mx-auto leading-normal">
                  Header synchronization voting, magic byte heuristics, and GSE payload detection inside .ts wrappers.
                </div>
              </div>

              {/* Connecting Down Arrow */}
              <div className="text-center text-[var(--text-muted)] font-bold text-[14px]">&darr;</div>

              {/* Level 2: Parsers */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                <div className="p-3 border border-[var(--border-main)] bg-[var(--bg-main)] text-center">
                  <div className="text-[11px] text-[var(--text-muted)]">PARSER A</div>
                  <div className="font-bold text-[var(--text-main)]">TSParser</div>
                  <div className="text-[11px] text-[var(--text-muted)]">PID / CC / TEI / Payload</div>
                </div>
                <div className="p-3 border border-[var(--border-main)] bg-[var(--bg-main)] text-center">
                  <div className="text-[11px] text-[var(--text-muted)]">PARSER B</div>
                  <div className="font-bold text-[var(--text-main)]">GSEParser</div>
                  <div className="text-[11px] text-[var(--text-muted)]">PDU / EtherType / Frag</div>
                </div>
                <div className="p-3 border border-[var(--border-main)] bg-[var(--bg-main)] text-center">
                  <div className="text-[11px] text-[var(--text-muted)]">PARSER C</div>
                  <div className="font-bold text-[var(--text-main)]">BBFrameParser</div>
                  <div className="text-[11px] text-[var(--text-muted)]">DFL / CRC-8 / MATYPE</div>
                </div>
              </div>

              {/* Connecting Down Arrow */}
              <div className="text-center text-[var(--text-muted)] font-bold text-[14px]">&darr;</div>

              {/* Level 3: Unified Feature Extraction */}
              <div className="p-4 border border-[var(--border-main)] bg-[var(--bg-main)] text-center">
                <div className="text-[11px] text-[var(--text-muted)] uppercase">STANDARDIZATION LAYER</div>
                <div className="font-bold text-[var(--text-main)] text-[14px] mt-1">
                  UNIFIED FEATURE EXTRACTOR
                </div>
                <div className="text-[11px] text-[var(--text-muted)] mt-1">
                  Normalizes spatial metrics across heterogeneous window partitions (w=200 pkts / 3 PDUs / 50 frames).
                </div>
              </div>

              {/* Connecting Down Arrow */}
              <div className="text-center text-[var(--text-muted)] font-bold text-[14px]">&darr;</div>

              {/* Level 4: Core Analytics F1, F2, F3 */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                <div className="p-4 border border-[var(--border-main)] bg-[var(--bg-main)]">
                  <div className="text-[#FF6B35] font-bold">[F1] STREAM HEALTH</div>
                  <div className="text-[var(--text-muted)] text-[11px] mt-1 leading-normal">
                    ETSI TR 101 290 inspired indicators (Sync, TEI, CC, CRC-8, PDU bounds).
                  </div>
                </div>
                <div className="p-4 border border-[var(--border-main)] bg-[var(--bg-main)]">
                  <div className="text-[#FF6B35] font-bold">[F2] ANOMALY DETECTION</div>
                  <div className="text-[var(--text-muted)] text-[11px] mt-1 leading-normal">
                    Unsupervised Isolation Forest baseline with upper 5% contamination threshold.
                  </div>
                </div>
                <div className="p-4 border border-[var(--border-main)] bg-[var(--bg-main)]">
                  <div className="text-[#FF6B35] font-bold">[F3] PATTERN ANALYSIS</div>
                  <div className="text-[var(--text-muted)] text-[11px] mt-1 leading-normal">
                    PID entropy, protocol distribution, mode transitions, and modal DFL dispersion.
                  </div>
                </div>
              </div>

              {/* Connecting Down Arrow */}
              <div className="text-center text-[var(--text-muted)] font-bold text-[14px]">&darr;</div>

              {/* Level 5: High-Level Analytics F4, F5, F6, F7 */}
              <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-3">
                <div className="p-3 border border-[var(--border-main)] bg-[var(--bg-main)]">
                  <div className="font-bold text-[var(--text-main)]">[F4] TIMELINE</div>
                  <div className="text-[var(--text-muted)] text-[11px] mt-1">Spatial byte offset profiling</div>
                </div>
                <div className="p-3 border border-[var(--border-main)] bg-[var(--bg-main)]">
                  <div className="font-bold text-[var(--text-main)]">[F5] EXPLANATIONS</div>
                  <div className="text-[var(--text-muted)] text-[11px] mt-1">Bounded |Z| &le; 20.0&sigma; attribution</div>
                </div>
                <div className="p-3 border border-[var(--border-main)] bg-[var(--bg-main)]">
                  <div className="font-bold text-[var(--text-main)]">[F6] COMPARISON</div>
                  <div className="text-[var(--text-muted)] text-[11px] mt-1">Semantic comparability shield</div>
                </div>
                <div className="p-3 border border-[var(--border-main)] bg-[var(--bg-main)]">
                  <div className="font-bold text-[var(--text-main)]">[F7] REPORTING</div>
                  <div className="text-[var(--text-muted)] text-[11px] mt-1">Markdown / HTML / JSON / TXT</div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* View B: Full-Stack Application Runtime */}
        {activeTab === "application" && (
          <div className="border border-[var(--border-main)] bg-[var(--bg-surface)] p-8 transition-colors duration-150">
            <div className="font-mono text-[12px] text-[var(--text-muted)] uppercase border-b border-[var(--border-dim)] pb-3 mb-6 flex justify-between">
              <span>PERSPECTIVE B: CLIENT-SERVER ARCHITECTURE &amp; HYBRID RUNTIME</span>
              <span className="text-[#FF6B35] font-bold">NEXT.JS 15 + REACT 19 + PYTHON 3.12</span>
            </div>

            <div className="space-y-4 font-mono text-[12px]">
              {/* Client Layer */}
              <div className="p-4 border border-[var(--border-main)] bg-[var(--bg-main)]">
                <div className="text-[11px] text-[var(--text-muted)] uppercase">CLIENT BROWSER LAYER</div>
                <div className="font-bold text-[var(--text-main)] text-[14px] mt-1">
                  WORKSTATION INTERFACE (ENGINEERING TERMINAL)
                </div>
                <div className="text-[var(--text-muted)] text-[11px] mt-1">
                  Industrial UI, 0px border-radius, zero box-shadows, strict 12/14/16/24/48/96px typography scale.
                </div>
              </div>

              {/* Connecting Double Arrow */}
              <div className="text-center text-[var(--text-muted)] font-bold text-[14px]">&updownarrow; HTTP / JSON / SSE</div>

              {/* Web Application Framework Layer */}
              <div className="p-4 border border-[var(--border-main)] bg-[var(--bg-main)]">
                <div className="text-[11px] text-[var(--text-muted)] uppercase">NEXT.JS 15 APPLICATION (PORT 3000)</div>
                <div className="font-bold text-[var(--text-main)] text-[14px] mt-1">
                  REACT 19 + APP ROUTER + TAILWIND CSS V4
                </div>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-3 mt-3">
                  <div className="p-3 border border-[var(--border-main)] bg-[var(--bg-surface)]">
                    <div className="text-[var(--text-main)] font-semibold">Live Analyzer</div>
                    <div className="text-[var(--text-muted)] text-[11px]">Upload / Presets / Execution</div>
                  </div>
                  <div className="p-3 border border-[var(--border-main)] bg-[var(--bg-surface)]">
                    <div className="text-[var(--text-main)] font-semibold">Telemetry Components</div>
                    <div className="text-[var(--text-muted)] text-[11px]">Timeline / Tables / Deviations</div>
                  </div>
                  <div className="p-3 border border-[var(--border-main)] bg-[var(--bg-surface)]">
                    <div className="text-[var(--text-main)] font-semibold">Offline Fallback Engine</div>
                    <div className="text-[var(--text-muted)] text-[11px]">Precompiled empirical telemetries</div>
                  </div>
                </div>
              </div>

              {/* Connecting Double Arrow */}
              <div className="text-center text-[var(--text-muted)] font-bold text-[14px]">&updownarrow; REST API (GET / POST)</div>

              {/* Python Backend Layer */}
              <div className="p-4 border border-[var(--border-main)] bg-[var(--bg-main)]">
                <div className="text-[11px] text-[var(--text-muted)] uppercase">PYTHON ANALYSIS BACKEND (PORT 8080)</div>
                <div className="font-bold text-[var(--text-main)] text-[14px] mt-1">
                  THREADED HTTP SERVER + ANALYSIS COORDINATOR
                </div>
                <div className="text-[var(--text-muted)] text-[11px] mt-1">
                  Executes frozen algorithms F1-F7. Zero frontend calculations; analytical authority resides strictly in Python.
                </div>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-2 mt-3 text-[11px]">
                  <div className="p-2 border border-[var(--border-main)] bg-[var(--bg-surface)] text-center">
                    POST /api/analyze
                  </div>
                  <div className="p-2 border border-[var(--border-main)] bg-[var(--bg-surface)] text-center">
                    POST /api/compare
                  </div>
                  <div className="p-2 border border-[var(--border-main)] bg-[var(--bg-surface)] text-center">
                    POST /api/upload
                  </div>
                  <div className="p-2 border border-[var(--border-main)] bg-[var(--bg-surface)] text-center">
                    GET /api/export
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </section>
  );
};
