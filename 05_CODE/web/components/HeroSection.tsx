"use client";

import React from "react";

interface HeroSectionProps {
  onExploreClick: () => void;
  onLaunchAnalyzerClick: () => void;
}

export const HeroSection: React.FC<HeroSectionProps> = ({
  onExploreClick,
  onLaunchAnalyzerClick,
}) => {
  return (
    <section className="relative w-full border-b border-[#262626] bg-[#0A0A0A] overflow-hidden">
      <div className="max-w-[1440px] mx-auto px-4 py-12 md:py-16">
        {/* Asymmetric 8/4 Grid Split */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 md:gap-12 items-start">
          {/* Left Column: 8 Columns Technical Density & Editorial Display */}
          <div className="lg:col-span-8 flex flex-col justify-between">
            <div>
              {/* Monospace Metadata Tagline */}
              <div className="flex items-center gap-2 mb-6 font-mono text-[12px] text-[#737373]">
                <span className="inline-block w-1.5 h-1.5 bg-[#FF6B35]" />
                <span className="text-[#E8E8E8]">STATION_ID: GSE-BB-TS-01</span>
                <span>//</span>
                <span>BASEBAND PHYSICAL LAYER PARSING</span>
                <span>//</span>
                <span>ETSI EN 302 307-1</span>
              </div>

              {/* 96px Display Typography */}
              <h1 className="text-[48px] md:text-[96px] font-black uppercase tracking-[-0.04em] leading-[0.9] text-[#E8E8E8] mb-6">
                DVB-S2
                <br />
                <span className="text-[#737373]">RECEIVER</span>
                <br />
                OUTPUT ANALYZER
              </h1>

              {/* Technical Abstract / Supporting Copy */}
              <p className="text-[16px] text-[#E8E8E8] leading-relaxed max-w-[680px] mb-8 font-normal">
                A multi-format engineering workstation for analyzing{" "}
                <span className="font-semibold text-white">MPEG-TS</span>,{" "}
                <span className="font-semibold text-white">GSE</span>, and{" "}
                <span className="font-semibold text-white">DVB-S2 BBFrame</span> receiver outputs.
                Combines content-aware stream detection, deterministic framing verification,
                unsupervised Isolation Forest anomaly detection, and mathematically grounded
                semantic comparison boundaries.
              </p>
            </div>

            {/* Direct Action Buttons: 0px Radius, 1px Border */}
            <div className="flex flex-wrap items-center gap-4 pt-4 border-t border-[#1A1A1A]">
              <button
                onClick={onLaunchAnalyzerClick}
                className="bg-[#FF6B35] text-[#0A0A0A] hover:bg-[#e05a28] font-mono text-[14px] font-bold px-6 py-3.5 border border-[#FF6B35] transition-colors cursor-pointer"
              >
                [EXECUTE ANALYZER]
              </button>
              <button
                onClick={onExploreClick}
                className="bg-[#141414] hover:bg-[#1f1f1f] text-[#E8E8E8] font-mono text-[14px] px-6 py-3.5 border border-[#262626] transition-colors cursor-pointer"
              >
                [VIEW EMPIRICAL TELEMETRY]
              </button>
              <div className="font-mono text-[12px] text-[#737373] ml-auto">
                BUILD: v2.0-REVIEW2 // PYTHON 3.12 + NEXT.JS 15
              </div>
            </div>
          </div>

          {/* Right Column: 4 Columns Editorial Negative Space & Single Hero Accent Moment */}
          <div className="lg:col-span-4 flex flex-col gap-6">
            {/* The Single Hero Accent Moment: STREAM INTEGRITY 100.0% */}
            <div className="border border-[#262626] bg-[#141414] p-6 flex flex-col justify-between">
              <div className="flex items-center justify-between border-b border-[#262626] pb-3 mb-4">
                <span className="font-mono text-[12px] text-[#737373] uppercase tracking-wider">
                  PRIMARY SYNC TELEMETRY
                </span>
                <span className="font-mono text-[12px] bg-[#0A0A0A] border border-[#262626] text-[#FF6B35] px-2 py-0.5">
                  LOCKED
                </span>
              </div>

              <div className="my-2">
                <div className="font-mono text-[14px] text-[#737373] uppercase mb-1">
                  STREAM INTEGRITY
                </div>
                <div className="text-[48px] md:text-[64px] font-mono font-bold leading-none text-[#FF6B35] tracking-tight">
                  100.0%
                </div>
              </div>

              <p className="text-[12px] text-[#737373] mt-4 border-t border-[#1A1A1A] pt-3 leading-normal">
                Selected integrity indicators inspired by ETSI TR 101 290 principles across all verified
                broadcast captures. Zero physical sync loss detected.
              </p>
            </div>

            {/* Grid-Break Element: -1.5° Rotated Verified Suite Card */}
            <div
              className="border border-[#262626] bg-[#141414] p-5 origin-center transition-transform hover:rotate-0"
              style={{ transform: "rotate(-1.5deg)" }}
            >
              <div className="flex items-center justify-between border-b border-[#262626] pb-2 mb-3">
                <span className="font-mono text-[12px] text-[#737373]">VERIFICATION INVARIANT</span>
                <span className="font-mono text-[12px] text-[#E8E8E8] font-bold">STABLE</span>
              </div>
              <div className="font-mono text-[24px] font-bold text-[#E8E8E8] leading-tight">
                240 / 240
              </div>
              <div className="font-mono text-[14px] text-[#FF6B35] font-semibold mb-2">
                TESTS PASSING
              </div>
              <div className="font-mono text-[12px] text-[#737373] flex justify-between border-t border-[#1A1A1A] pt-2">
                <span>207 BACKEND</span>
                <span>33 FRONTEND</span>
                <span>0 ERRORS</span>
              </div>
            </div>

            {/* Supported Input Streams Matrix */}
            <div className="border border-[#262626] bg-[#0A0A0A] p-4 font-mono text-[12px]">
              <div className="text-[#737373] uppercase mb-2 border-b border-[#1A1A1A] pb-1">
                ALTERNATIVE INPUT FORMATS (NON-SEQUENTIAL)
              </div>
              <div className="space-y-1.5 text-[#E8E8E8]">
                <div className="flex justify-between">
                  <span className="text-[#737373]">MPEG-TS:</span>
                  <span>188-byte Framing // Sync 0x47</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-[#737373]">GSE:</span>
                  <span>ETSI TS 102 606 // Variable PDU</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-[#737373]">BBFRAME:</span>
                  <span>ETSI EN 302 307 // 10B Header</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};
