"use client";

import React, { useState } from "react";

interface TooltipProps {
  content: string;
  children: React.ReactNode;
  position?: "top" | "bottom";
}

export const Tooltip: React.FC<TooltipProps> = ({ content, children, position = "top" }) => {
  const [visible, setVisible] = useState(false);

  return (
    <span
      className="relative inline-flex items-center cursor-help group"
      onMouseEnter={() => setVisible(true)}
      onMouseLeave={() => setVisible(false)}
      onFocus={() => setVisible(true)}
      onBlur={() => setVisible(false)}
      tabIndex={0}
      role="tooltip"
      aria-label={content}
    >
      <span className="border-b border-dotted border-[var(--text-muted)] group-hover:border-[#FF6B35] transition-colors">
        {children}
      </span>
      {visible && (
        <span
          className={`absolute left-1/2 -translate-x-1/2 z-50 px-2.5 py-1.5 bg-[var(--bg-surface)] border border-[var(--border-main)] text-[var(--text-main)] font-mono text-[11px] leading-tight whitespace-nowrap pointer-events-none ${
            position === "top" ? "bottom-full mb-1.5" : "top-full mt-1.5"
          } animate-in fade-in duration-150`}
        >
          {content}
        </span>
      )}
    </span>
  );
};
