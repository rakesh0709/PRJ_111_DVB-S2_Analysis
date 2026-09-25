"use client";

import React from "react";

export const Footer: React.FC = () => {
  return (
    <footer className="w-full border-t border-[var(--border-main)] bg-[var(--bg-main)] py-8 font-mono text-[12px] transition-colors duration-150">
      <div className="max-w-[1440px] mx-auto px-4 flex flex-col md:flex-row items-center justify-between gap-4 text-[var(--text-muted)]">
        <div className="flex flex-wrap items-center gap-3">
          <span className="font-bold text-[var(--text-main)]">PRJ_111</span>
          <span>//</span>
          <span>DVB-S2 RECEIVER OUTPUT STREAM ANALYZER</span>
          <span>//</span>
          <span>REVIEW-2 ENGINEERING MILESTONE</span>
        </div>

        <div className="flex items-center gap-4">
          <span className="text-[#FF6B35] font-semibold">240/240 TESTS PASSING</span>
          <span className="text-[var(--border-main)]">|</span>
          <span>NEXT.JS 15 + REACT 19 + TAILWIND V4</span>
        </div>
      </div>

      <div className="max-w-[1440px] mx-auto px-4 mt-4 pt-4 border-t border-[var(--border-dim)] text-[11px] text-[var(--text-muted)] leading-relaxed">
        Selected integrity indicators inspired by ETSI TR 101 290 principles. The project does not claim
        formal ETSI compliance certification. Post-demodulator digital output stream analysis only; no RF
        hardware carrier telemetry is inferred.
      </div>
    </footer>
  );
};
