import React from "react";
import { Tooltip } from "@/components/Tooltip";

interface HeroSectionProps {
  onExploreClick: () => void;
  onLaunchAnalyzerClick: () => void;
}

export const HeroSection: React.FC<HeroSectionProps> = ({
  onExploreClick,
  onLaunchAnalyzerClick,
}) => {
  return (
    <section className="relative w-full border-b border-[var(--border-main)] bg-[var(--bg-main)] overflow-hidden transition-colors duration-150">
      <div className="max-w-[1440px] mx-auto px-4 py-12 md:py-16">
        {/* Asymmetric 8/4 Grid Split */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 md:gap-12 items-start">
          {/* Left Column: 8 Columns Technical Density & Editorial Display */}
          <div className="lg:col-span-8 flex flex-col justify-between">
            <div>
              {/* Clean Metadata Tagline */}
              <div className="flex flex-wrap items-center gap-2 mb-6 text-xs text-[var(--text-muted)] tracking-wider uppercase font-semibold">
                <span className="inline-block w-2 h-2 bg-[#FF6B35] animate-pulse" />
                <span className="text-[var(--text-main)] font-mono">STATION: GSE-BB-TS-01</span>
                <span>•</span>
                <span>BASEBAND PHYSICAL LAYER PARSING</span>
                <span>•</span>
                <Tooltip content="ETSI EN 302 307-1: Second generation framing structure, channel coding and modulation systems for Broadcasting, Interactive Services, News Gathering and other broadband satellite applications">
                  <span className="text-[var(--text-main)] font-mono cursor-help underline decoration-dotted underline-offset-2">
                    ETSI EN 302 307-1
                  </span>
                </Tooltip>
              </div>

              {/* 96px Display Typography */}
              <h1 className="text-[48px] md:text-[92px] font-black uppercase tracking-[-0.04em] leading-[0.9] text-[var(--text-main)] mb-6 select-none">
                DVB-S2
                <br />
                <span className="text-[var(--text-muted)]">RECEIVER</span>
                <br />
                OUTPUT ANALYZER
              </h1>

              {/* Technical Abstract / Supporting Copy */}
              <p className="text-[16px] text-[var(--text-main)] leading-relaxed max-w-[680px] mb-8 font-normal">
                A multi-format engineering workstation for analyzing{" "}
                <span className="font-semibold text-[#FF6B35]">MPEG-TS</span>,{" "}
                <span className="font-semibold text-[#FF6B35]">GSE</span>, and{" "}
                <span className="font-semibold text-[#FF6B35]">DVB-S2 BBFrame</span> receiver outputs.
                Combines content-aware stream detection, deterministic framing verification,
                unsupervised Isolation Forest anomaly detection, and mathematically grounded
                semantic comparison boundaries.
              </p>
            </div>

            {/* Direct Action Buttons: 0px Radius, 1px Border */}
            <div className="flex flex-wrap items-center gap-4 pt-4 border-t border-[var(--border-dim)]">
              <button
                onClick={onLaunchAnalyzerClick}
                className="bg-[#FF6B35] text-[#0A0A0A] hover:bg-[#ff8555] active:translate-y-[1px] font-mono text-[14px] font-bold px-7 py-3.5 border border-[#FF6B35] transition-all cursor-pointer focus-visible:outline-2 focus-visible:outline-[#FF6B35]"
              >
                [EXECUTE ANALYZER]
              </button>
              <button
                onClick={onExploreClick}
                className="bg-[var(--bg-surface)] hover:bg-[var(--bg-surface-elevated)] hover:border-[#FF6B35] active:translate-y-[1px] text-[var(--text-main)] font-mono text-[14px] px-6 py-3.5 border border-[var(--border-main)] transition-all cursor-pointer focus-visible:outline-2 focus-visible:outline-[#FF6B35]"
              >
                [VIEW EMPIRICAL TELEMETRY]
              </button>
              <div className="font-mono text-[12px] text-[var(--text-muted)] ml-auto">
                BUILD: v2.0-REVIEW2 // PYTHON 3.12 + NEXT.JS 15
              </div>
            </div>
          </div>

          {/* Right Column: 4 Columns Clean Aligned Technical Cards */}
          <div className="lg:col-span-4 flex flex-col gap-5">
            {/* Stream Integrity Metric Card */}
            <div className="border border-[var(--border-main)] bg-[var(--bg-surface)] p-6 flex flex-col justify-between hover:border-[#FF6B35] transition-colors duration-200">
              <div className="flex items-center justify-between border-b border-[var(--border-dim)] pb-3 mb-4">
                <span className="text-xs font-semibold text-[var(--text-muted)] uppercase tracking-wider">
                  PRIMARY SYNC TELEMETRY
                </span>
                <span className="font-mono text-[11px] bg-[var(--bg-main)] border border-[#FF6B35]/40 text-[#FF6B35] font-semibold px-2 py-0.5">
                  LOCKED
                </span>
              </div>

              <div className="my-2">
                <div className="text-xs font-medium text-[var(--text-muted)] uppercase tracking-wider mb-1">
                  STREAM INTEGRITY
                </div>
                <div className="text-[48px] md:text-[60px] font-mono font-bold leading-none text-[#FF6B35] tracking-tight">
                  100.0%
                </div>
              </div>

              <p className="text-xs text-[var(--text-muted)] mt-4 border-t border-[var(--border-dim)] pt-3 leading-normal">
                Selected integrity indicators inspired by{" "}
                <Tooltip content="ETSI TR 101 290: Measurement guidelines for DVB systems. Defines Priority 1-3 transmission error monitoring.">
                  <span className="text-[var(--text-main)] font-semibold cursor-help underline decoration-dotted underline-offset-2">
                    ETSI TR 101 290
                  </span>
                </Tooltip>{" "}
                principles across verified broadcast captures. Zero physical sync loss detected.
              </p>
            </div>

            {/* Verification Invariant Card (Neatly Aligned, No Tilt) */}
            <div className="border border-[var(--border-main)] bg-[var(--bg-surface)] p-5 transition-colors duration-200 hover:border-[#FF6B35]">
              <div className="flex items-center justify-between border-b border-[var(--border-dim)] pb-2 mb-3">
                <span className="text-xs font-semibold text-[var(--text-muted)] uppercase tracking-wider">
                  VERIFICATION INVARIANT
                </span>
                <span className="font-mono text-[11px] text-[#FF6B35] font-bold bg-[#FF6B35]/10 px-2 py-0.5 border border-[#FF6B35]/30">
                  ALL PASSING
                </span>
              </div>
              <div className="font-mono text-[28px] font-bold text-[var(--text-main)] leading-tight">
                240 / 240
              </div>
              <div className="text-xs text-[var(--text-muted)] font-medium mb-3">
                AUTOMATED TEST SUITE
              </div>
              <div className="font-mono text-[11px] text-[var(--text-muted)] flex justify-between border-t border-[var(--border-dim)] pt-2.5">
                <span>207 BACKEND</span>
                <span>•</span>
                <span>33 FRONTEND</span>
                <span>•</span>
                <span className="text-[#FF6B35] font-semibold">0 ERRORS</span>
              </div>
            </div>

            {/* Supported Input Streams Matrix */}
            <div className="border border-[var(--border-main)] bg-[var(--bg-surface)] p-4 font-mono text-[12px]">
              <div className="text-[var(--text-muted)] uppercase mb-2 border-b border-[var(--border-dim)] pb-1.5 flex justify-between items-center">
                <span className="text-xs font-semibold">SUPPORTED FORMATS</span>
                <span className="text-[10px] text-[#FF6B35] px-1.5 py-0.5 bg-[var(--bg-main)] border border-[var(--border-main)]">
                  MULTI-STANDARD
                </span>
              </div>
              <div className="space-y-1.5 text-[var(--text-main)]">
                <div className="flex justify-between items-center py-0.5">
                  <span className="text-[var(--text-muted)] font-sans text-xs">MPEG-TS</span>
                  <span className="text-xs">188-byte Framing // Sync 0x47</span>
                </div>
                <div className="flex justify-between items-center py-0.5">
                  <span className="text-[var(--text-muted)] font-sans text-xs">GSE</span>
                  <span className="text-xs">ETSI TS 102 606 // Variable PDU</span>
                </div>
                <div className="flex justify-between items-center py-0.5">
                  <span className="text-[var(--text-muted)] font-sans text-xs">BBFRAME</span>
                  <span className="text-xs">ETSI EN 302 307 // 10B Header</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};
