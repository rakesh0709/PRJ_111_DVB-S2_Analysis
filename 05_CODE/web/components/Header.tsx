"use client";

import React from "react";
import { BackendStatus } from "@/lib/types";
import { useTheme } from "./ThemeProvider";
import { useToast } from "./Toast";

interface HeaderProps {
  backendStatus: BackendStatus;
  isLiveMode: boolean;
}

export const Header: React.FC<HeaderProps> = ({ backendStatus }) => {
  const isOnline = backendStatus.status === "ONLINE";
  const { theme, toggleTheme } = useTheme();
  const { showToast } = useToast();

  const handleToggleTheme = () => {
    toggleTheme();
    showToast(`Switched theme to ${theme === "dark" ? "Light" : "Dark"} Mode`, "info");
  };

  return (
    <header className="sticky top-0 z-50 w-full bg-[var(--bg-main)]/95 border-b border-[var(--border-main)] backdrop-blur-none transition-colors duration-200">
      {/* Top micro-terminal bar */}
      <div className="w-full border-b border-[var(--divider-main)] px-4 py-1.5 flex flex-wrap items-center justify-between text-[12px] font-mono text-[var(--text-muted)]">
        <div className="flex items-center gap-4">
          <span className="text-[var(--text-main)] font-bold tracking-wider">PROJECT: PRJ_111</span>
          <span className="hidden sm:inline text-[var(--border-main)]">|</span>
          <span className="hidden sm:inline">ETSI EN 302 307-1 / TR 101 290 INSPIRED</span>
          <span className="hidden md:inline text-[var(--border-main)]">|</span>
          <span className="hidden md:inline">F1-F7 MULTI-FORMAT WORKSTATION</span>
        </div>
        <div className="flex items-center gap-3">
          <span className="flex items-center gap-1.5">
            <span
              className={`inline-block w-2 h-2 ${
                isOnline ? "bg-[#FF6B35]" : "bg-[var(--text-muted)]"
              }`}
            />
            <span className={isOnline ? "text-[var(--text-main)] font-semibold" : "text-[var(--text-muted)]"}>
              {isOnline ? "BACKEND ONLINE" : "OFFLINE SHOWCASE"}
            </span>
          </span>
          <span className="text-[var(--border-main)]">|</span>
          <span className="text-[var(--text-muted)] hidden sm:inline">VERIFIED BUILD (240 TESTS PASSING)</span>
          <span className="text-[var(--border-main)]">|</span>
          {/* Interactive Theme Switcher */}
          <button
            onClick={handleToggleTheme}
            className="px-2 py-0.5 border border-[var(--border-main)] bg-[var(--bg-surface)] hover:border-[#FF6B35] text-[var(--text-main)] font-mono text-[11px] cursor-pointer transition-colors"
            title={`Toggle Theme (Current: ${theme.toUpperCase()})`}
            aria-label="Toggle visual theme between Dark and Light mode"
          >
            [THEME: {theme.toUpperCase()}]
          </button>
        </div>
      </div>

      {/* Main navigation header */}
      <div className="max-w-[1440px] mx-auto px-4 py-4 flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div className="flex items-baseline gap-3">
          <span className="font-mono text-[14px] bg-[var(--bg-surface)] border border-[var(--border-main)] text-[#FF6B35] px-2 py-0.5 font-semibold">
            PRJ_111
          </span>
          <div>
            <h1 className="text-[16px] md:text-[24px] font-bold tracking-tight text-[var(--text-main)] uppercase">
              DVB-S2 Receiver Output Stream Analyzer
            </h1>
            <p className="text-[12px] font-mono text-[var(--text-muted)]">
              MULTI-FORMAT TELEMETRY / ANOMALY DETECTION / SEMANTIC SHIELD
            </p>
          </div>
        </div>

        {/* Monospace Navigation Anchor Links */}
        <nav className="flex flex-wrap items-center gap-1 font-mono text-[12px]" aria-label="Main Navigation">
          {[
            { href: "#analyzer", label: "[01] ANALYZER" },
            { href: "#telemetry", label: "[02] TELEMETRY" },
            { href: "#timeline", label: "[03] TIMELINE" },
            { href: "#anomalies", label: "[04] ANOMALIES" },
            { href: "#architecture", label: "[05] ARCHITECTURE" },
            { href: "#comparison", label: "[06] COMPARISON" },
            { href: "#documentation", label: "[07] DOCS" },
          ].map((item) => (
            <a
              key={item.href}
              href={item.href}
              className="px-2.5 py-1.5 border border-transparent hover:border-[var(--border-main)] hover:bg-[var(--bg-surface)] text-[var(--text-main)] transition-colors duration-150 focus-visible:border-[#FF6B35]"
            >
              {item.label}
            </a>
          ))}
        </nav>
      </div>
    </header>
  );
};
