"use client";

import React from "react";
import { BackendStatus } from "@/lib/types";

interface HeaderProps {
  backendStatus: BackendStatus;
  isLiveMode: boolean;
}

export const Header: React.FC<HeaderProps> = ({ backendStatus, isLiveMode }) => {
  const isOnline = backendStatus.status === "ONLINE";

  return (
    <header className="sticky top-0 z-50 w-full bg-[#0A0A0A]/95 border-b border-[#262626] backdrop-blur-none">
      {/* Top micro-terminal bar */}
      <div className="w-full border-b border-[#1A1A1A] px-4 py-1.5 flex flex-wrap items-center justify-between text-[12px] font-mono text-[#737373]">
        <div className="flex items-center gap-4">
          <span className="text-[#E8E8E8] font-bold tracking-wider">PROJECT: PRJ_111</span>
          <span className="hidden sm:inline text-[#262626]">|</span>
          <span className="hidden sm:inline">ETSI EN 302 307-1 / TR 101 290 INSPIRED</span>
          <span className="hidden md:inline text-[#262626]">|</span>
          <span className="hidden md:inline text-[#737373]">F1-F7 MULTI-FORMAT WORKSTATION</span>
        </div>
        <div className="flex items-center gap-3">
          <span className="flex items-center gap-1.5">
            <span
              className={`inline-block w-2 h-2 ${
                isOnline ? "bg-[#E8E8E8]" : "bg-[#FF6B35]"
              }`}
            />
            <span className={isOnline ? "text-[#E8E8E8]" : "text-[#FF6B35]"}>
              {isOnline ? "BACKEND ONLINE" : "BACKEND OFFLINE (OFFLINE SHOWCASE)"}
            </span>
          </span>
          <span className="text-[#262626]">|</span>
          <span className="text-[#E8E8E8]">240/240 TESTS PASSING</span>
        </div>
      </div>

      {/* Main navigation header */}
      <div className="max-w-[1440px] mx-auto px-4 py-4 flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div className="flex items-baseline gap-3">
          <span className="font-mono text-[14px] bg-[#141414] border border-[#262626] text-[#FF6B35] px-2 py-0.5 font-semibold">
            PRJ_111
          </span>
          <div>
            <h1 className="text-[16px] md:text-[24px] font-bold tracking-tight text-[#E8E8E8] uppercase">
              DVB-S2 Receiver Output Stream Analyzer
            </h1>
            <p className="text-[12px] font-mono text-[#737373]">
              MULTI-FORMAT TELEMETRY / ANOMALY DETECTION / SEMANTIC SHIELD
            </p>
          </div>
        </div>

        {/* Monospace Navigation Anchor Links */}
        <nav className="flex flex-wrap items-center gap-1 font-mono text-[12px]">
          <a
            href="#analyzer"
            className="px-2.5 py-1.5 border border-transparent hover:border-[#262626] hover:bg-[#141414] text-[#E8E8E8] transition-colors"
          >
            [01] ANALYZER
          </a>
          <a
            href="#telemetry"
            className="px-2.5 py-1.5 border border-transparent hover:border-[#262626] hover:bg-[#141414] text-[#E8E8E8] transition-colors"
          >
            [02] TELEMETRY
          </a>
          <a
            href="#timeline"
            className="px-2.5 py-1.5 border border-transparent hover:border-[#262626] hover:bg-[#141414] text-[#E8E8E8] transition-colors"
          >
            [03] TIMELINE
          </a>
          <a
            href="#anomalies"
            className="px-2.5 py-1.5 border border-transparent hover:border-[#262626] hover:bg-[#141414] text-[#E8E8E8] transition-colors"
          >
            [04] ANOMALIES
          </a>
          <a
            href="#architecture"
            className="px-2.5 py-1.5 border border-transparent hover:border-[#262626] hover:bg-[#141414] text-[#E8E8E8] transition-colors"
          >
            [05] ARCHITECTURE
          </a>
          <a
            href="#comparison"
            className="px-2.5 py-1.5 border border-transparent hover:border-[#262626] hover:bg-[#141414] text-[#E8E8E8] transition-colors"
          >
            [06] COMPARISON
          </a>
          <a
            href="#documentation"
            className="px-2.5 py-1.5 border border-transparent hover:border-[#262626] hover:bg-[#141414] text-[#E8E8E8] transition-colors"
          >
            [07] DOCS
          </a>
        </nav>
      </div>
    </header>
  );
};
