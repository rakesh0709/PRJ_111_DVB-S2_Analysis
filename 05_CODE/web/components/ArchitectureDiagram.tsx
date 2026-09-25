"use client";

import React, { useState } from "react";

export const ArchitectureDiagram: React.FC = () => {
  const [activeTab, setActiveTab] = useState<"analysis" | "application">("analysis");

  return (
    <section id="architecture" className="w-full border-b border-[#262626] bg-[#0A0A0A] py-12">
      <div className="max-w-[1440px] mx-auto px-4">
        {/* Section Header */}
        <div className="flex flex-col md:flex-row md:items-end justify-between border-b border-[#262626] pb-4 mb-8">
          <div>
            <div className="font-mono text-[12px] text-[#737373] uppercase mb-1">
              SYSTEM DESIGN // DUAL PERSPECTIVE SCHEMATICS
            </div>
            <h2 className="text-[24px] md:text-[48px] font-bold uppercase tracking-tight text-[#E8E8E8]">
              ARCHITECTURE &amp; DATAFLOW
            </h2>
          </div>

          <div className="flex gap-2 mt-4 md:mt-0 font-mono text-[12px]">
            <button
              onClick={() => setActiveTab("analysis")}
              className={`px-4 py-2 border transition-colors cursor-pointer ${
                activeTab === "analysis"
                  ? "border-[#FF6B35] bg-[#141414] text-[#E8E8E8] font-bold"
                  : "border-[#262626] bg-[#0A0A0A] text-[#737373] hover:text-[#E8E8E8]"
              }`}
            >
              [A] SOFTWARE PIPELINE
            </button>
            <button
              onClick={() => setActiveTab("application")}
              className={`px-4 py-2 border transition-colors cursor-pointer ${
                activeTab === "application"
                  ? "border-[#FF6B35] bg-[#141414] text-[#E8E8E8] font-bold"
                  : "border-[#262626] bg-[#0A0A0A] text-[#737373] hover:text-[#E8E8E8]"
              }`}
            >
              [B] FULL-STACK RUNTIME
            </button>
          </div>
        </div>

        {/* View A: Software Pipeline */}
        {activeTab === "analysis" && (
          <div className="border border-[#262626] bg-[#141414] p-8">
            <div className="font-mono text-[12px] text-[#737373] uppercase border-b border-[#262626] pb-3 mb-6 flex justify-between">
              <span>PERSPECTIVE A: MULTI-FORMAT PARSING &amp; ANALYTICAL ENGINE</span>
              <span className="text-[#FF6B35]">NON-SEQUENTIAL INPUT ALTERNATIVES</span>
            </div>

            {/* Swiss Block Diagram */}
            <div className="space-y-4 font-mono text-[12px]">
              {/* Level 0: Ingestion */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                <div className="p-4 border border-[#262626] bg-[#0A0A0A] text-center">
                  <div className="text-[12px] text-[#737373] uppercase">INPUT STREAM 01</div>
                  <div className="font-bold text-[#E8E8E8] text-[14px] mt-1">MPEG-TS (.ts)</div>
                  <div className="text-[12px] text-[#737373] mt-1">188-byte Packets // Sync 0x47</div>
                </div>
                <div className="p-4 border border-[#262626] bg-[#0A0A0A] text-center">
                  <div className="text-[12px] text-[#737373] uppercase">INPUT STREAM 02</div>
                  <div className="font-bold text-[#E8E8E8] text-[14px] mt-1">GSE (.ts / .bin)</div>
                  <div className="text-[12px] text-[#737373] mt-1">ETSI TS 102 606 // Variable PDU</div>
                </div>
                <div className="p-4 border border-[#262626] bg-[#0A0A0A] text-center">
                  <div className="text-[12px] text-[#737373] uppercase">INPUT STREAM 03</div>
                  <div className="font-bold text-[#E8E8E8] text-[14px] mt-1">BBFRAME (.pcap / .bin)</div>
                  <div className="text-[12px] text-[#737373] mt-1">ETSI EN 302 307 // 10B BBHeader</div>
                </div>
              </div>

              {/* Connecting Down Arrow */}
              <div className="text-center text-[#737373] font-bold text-[14px]">&darr;</div>

              {/* Level 1: Stream Handler & Content Detection */}
              <div className="p-4 border border-[#262626] bg-[#0A0A0A] text-center">
                <div className="text-[12px] text-[#737373] uppercase">STREAM HANDLER // INGESTION</div>
                <div className="font-bold text-[#E8E8E8] text-[14px] mt-1">
                  CONTENT-AWARE FORMAT DETECTOR
                </div>
                <div className="text-[12px] text-[#737373] mt-1 max-w-[600px] mx-auto">
                  Header synchronization voting, magic byte heuristics, and GSE payload detection inside .ts wrappers.
                </div>
              </div>

              {/* Connecting Down Arrow */}
              <div className="text-center text-[#737373] font-bold text-[14px]">&darr;</div>

              {/* Level 2: Parsers */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                <div className="p-3 border border-[#262626] bg-[#0A0A0A] text-center">
                  <div className="text-[12px] text-[#737373]">PARSER A</div>
                  <div className="font-bold text-[#E8E8E8]">TSParser</div>
                  <div className="text-[12px] text-[#737373]">PID / CC / TEI / Payload</div>
                </div>
                <div className="p-3 border border-[#262626] bg-[#0A0A0A] text-center">
                  <div className="text-[12px] text-[#737373]">PARSER B</div>
                  <div className="font-bold text-[#E8E8E8]">GSEParser</div>
                  <div className="text-[12px] text-[#737373]">PDU / EtherType / Frag</div>
                </div>
                <div className="p-3 border border-[#262626] bg-[#0A0A0A] text-center">
                  <div className="text-[12px] text-[#737373]">PARSER C</div>
                  <div className="font-bold text-[#E8E8E8]">BBFrameParser</div>
                  <div className="text-[12px] text-[#737373]">DFL / CRC-8 / MATYPE</div>
                </div>
              </div>

              {/* Connecting Down Arrow */}
              <div className="text-center text-[#737373] font-bold text-[14px]">&darr;</div>

              {/* Level 3: Unified Feature Extraction */}
              <div className="p-4 border border-[#262626] bg-[#0A0A0A] text-center">
                <div className="text-[12px] text-[#737373] uppercase">STANDARDIZATION LAYER</div>
                <div className="font-bold text-[#E8E8E8] text-[14px] mt-1">
                  UNIFIED FEATURE EXTRACTOR
                </div>
                <div className="text-[12px] text-[#737373] mt-1">
                  Normalizes spatial metrics across heterogeneous window partitions (w=200 pkts / 3 PDUs / 50 frames).
                </div>
              </div>

              {/* Connecting Down Arrow */}
              <div className="text-center text-[#737373] font-bold text-[14px]">&darr;</div>

              {/* Level 4: Core Analytics F1, F2, F3 */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                <div className="p-4 border border-[#262626] bg-[#0A0A0A]">
                  <div className="text-[#FF6B35] font-bold">[F1] STREAM HEALTH</div>
                  <div className="text-[#737373] text-[12px] mt-1">
                    ETSI TR 101 290 inspired indicators (Sync, TEI, CC, CRC-8, PDU bounds).
                  </div>
                </div>
                <div className="p-4 border border-[#262626] bg-[#0A0A0A]">
                  <div className="text-[#FF6B35] font-bold">[F2] ANOMALY DETECTION</div>
                  <div className="text-[#737373] text-[12px] mt-1">
                    Unsupervised Isolation Forest baseline with upper 5% contamination threshold.
                  </div>
                </div>
                <div className="p-4 border border-[#262626] bg-[#0A0A0A]">
                  <div className="text-[#FF6B35] font-bold">[F3] PATTERN ANALYSIS</div>
                  <div className="text-[#737373] text-[12px] mt-1">
                    PID entropy, protocol distribution, mode transitions, and modal DFL dispersion.
                  </div>
                </div>
              </div>

              {/* Connecting Down Arrow */}
              <div className="text-center text-[#737373] font-bold text-[14px]">&darr;</div>

              {/* Level 5: High-Level Analytics F4, F5, F6, F7 */}
              <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-3">
                <div className="p-3 border border-[#262626] bg-[#0A0A0A]">
                  <div className="font-bold text-[#E8E8E8]">[F4] TIMELINE</div>
                  <div className="text-[#737373] text-[12px] mt-1">Spatial byte offset profiling</div>
                </div>
                <div className="p-3 border border-[#262626] bg-[#0A0A0A]">
                  <div className="font-bold text-[#E8E8E8]">[F5] EXPLANATIONS</div>
                  <div className="text-[#737373] text-[12px] mt-1">Bounded |Z| &le; 20.0&sigma; attribution</div>
                </div>
                <div className="p-3 border border-[#262626] bg-[#0A0A0A]">
                  <div className="font-bold text-[#E8E8E8]">[F6] COMPARISON</div>
                  <div className="text-[#737373] text-[12px] mt-1">Semantic comparability shield</div>
                </div>
                <div className="p-3 border border-[#262626] bg-[#0A0A0A]">
                  <div className="font-bold text-[#E8E8E8]">[F7] REPORTING</div>
                  <div className="text-[#737373] text-[12px] mt-1">Markdown / HTML / JSON / TXT</div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* View B: Full-Stack Application Runtime */}
        {activeTab === "application" && (
          <div className="border border-[#262626] bg-[#141414] p-8">
            <div className="font-mono text-[12px] text-[#737373] uppercase border-b border-[#262626] pb-3 mb-6 flex justify-between">
              <span>PERSPECTIVE B: CLIENT-SERVER ARCHITECTURE &amp; HYBRID RUNTIME</span>
              <span className="text-[#FF6B35]">NEXT.JS 15 + REACT 19 + PYTHON 3.12</span>
            </div>

            <div className="space-y-4 font-mono text-[12px]">
              {/* Client Layer */}
              <div className="p-4 border border-[#262626] bg-[#0A0A0A]">
                <div className="text-[12px] text-[#737373] uppercase">CLIENT BROWSER LAYER</div>
                <div className="font-bold text-[#E8E8E8] text-[14px] mt-1">
                  WORKSTATION INTERFACE (ENGINEERING TERMINAL)
                </div>
                <div className="text-[#737373] text-[12px] mt-1">
                  Industrial UI, 0px border-radius, zero box-shadows, strict 12/14/16/24/48/96px typography scale.
                </div>
              </div>

              {/* Connecting Double Arrow */}
              <div className="text-center text-[#737373] font-bold text-[14px]">&updownarrow; HTTP / JSON / SSE</div>

              {/* Web Application Framework Layer */}
              <div className="p-4 border border-[#262626] bg-[#0A0A0A]">
                <div className="text-[12px] text-[#737373] uppercase">NEXT.JS 15 APPLICATION (PORT 3000)</div>
                <div className="font-bold text-[#E8E8E8] text-[14px] mt-1">
                  REACT 19 + APP ROUTER + TAILWIND CSS V4
                </div>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-3 mt-3">
                  <div className="p-2 border border-[#262626] bg-[#141414]">
                    <div className="text-[#E8E8E8] font-semibold">Live Analyzer</div>
                    <div className="text-[#737373] text-[12px]">Upload / Presets / Execution</div>
                  </div>
                  <div className="p-2 border border-[#262626] bg-[#141414]">
                    <div className="text-[#E8E8E8] font-semibold">Telemetry Components</div>
                    <div className="text-[#737373] text-[12px]">Timeline / Tables / Deviations</div>
                  </div>
                  <div className="p-2 border border-[#262626] bg-[#141414]">
                    <div className="text-[#E8E8E8] font-semibold">Offline Fallback Engine</div>
                    <div className="text-[#737373] text-[12px]">Precompiled empirical telemetries</div>
                  </div>
                </div>
              </div>

              {/* Connecting Double Arrow */}
              <div className="text-center text-[#737373] font-bold text-[14px]">&updownarrow; REST API (GET / POST)</div>

              {/* Python Backend Layer */}
              <div className="p-4 border border-[#262626] bg-[#0A0A0A]">
                <div className="text-[12px] text-[#737373] uppercase">PYTHON ANALYSIS BACKEND (PORT 8080)</div>
                <div className="font-bold text-[#E8E8E8] text-[14px] mt-1">
                  THREADED HTTP SERVER + ANALYSIS COORDINATOR
                </div>
                <div className="text-[#737373] text-[12px] mt-1">
                  Executes frozen algorithms F1-F7. Zero frontend calculations; analytical authority resides strictly in Python.
                </div>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-2 mt-3 text-[12px]">
                  <div className="p-2 border border-[#262626] bg-[#141414] text-center">
                    POST /api/analyze
                  </div>
                  <div className="p-2 border border-[#262626] bg-[#141414] text-center">
                    POST /api/compare
                  </div>
                  <div className="p-2 border border-[#262626] bg-[#141414] text-center">
                    POST /api/upload
                  </div>
                  <div className="p-2 border border-[#262626] bg-[#141414] text-center">
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
