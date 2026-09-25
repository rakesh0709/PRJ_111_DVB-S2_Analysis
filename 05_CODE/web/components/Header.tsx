"use client";

import React from "react";
import { BackendStatus } from "@/lib/types";
import { useTheme } from "./ThemeProvider";
import { useToast } from "./Toast";

export type ActiveTabId =
  | "dashboard"
  | "anomalies"
  | "timeline"
  | "comparison"
  | "architecture"
  | "docs";

interface HeaderProps {
  backendStatus: BackendStatus;
  isLiveMode: boolean;
  activeTab: ActiveTabId;
  onSelectTab: (tab: ActiveTabId) => void;
  activeFormat?: string;
}

export const Header: React.FC<HeaderProps> = ({
  backendStatus,
  activeTab,
  onSelectTab,
  activeFormat,
}) => {
  const isOnline = backendStatus.status === "ONLINE";
  const { theme, toggleTheme } = useTheme();
  const { showToast } = useToast();

  const handleToggleTheme = () => {
    toggleTheme();
    showToast(`Switched theme to ${theme === "dark" ? "Light" : "Dark"} Mode`, "info");
  };

  const navTabs: Array<{
    id: ActiveTabId;
    label: string;
    stage: string;
    icon: React.ReactNode;
  }> = [
    {
      id: "dashboard",
      label: "DASHBOARD",
      stage: "F1/F3",
      icon: (
        <svg className="w-3.5 h-3.5" viewBox="0 0 16 16" fill="currentColor">
          <path d="M1 2.5A1.5 1.5 0 0 1 2.5 1h11A1.5 1.5 0 0 1 15 2.5v11a1.5 1.5 0 0 1-1.5 1.5h-11A1.5 1.5 0 0 1 1 13.5v-11zM2.5 2a.5.5 0 0 0-.5.5V6h12V2.5a.5.5 0 0 0-.5-.5h-11zM14 7H2v6.5a.5.5 0 0 0 .5.5h11a.5.5 0 0 0 .5-.5V7z" />
        </svg>
      ),
    },
    {
      id: "anomalies",
      label: "ANOMALY ANALYSIS",
      stage: "F2+F5",
      icon: (
        <svg className="w-3.5 h-3.5" viewBox="0 0 16 16" fill="currentColor">
          <path d="M11.742 10.344a6.5 6.5 0 1 0-1.397 1.398h-.001c.03.04.062.078.098.115l3.85 3.85a1 1 0 0 0 1.415-1.414l-3.85-3.85a1.007 1.007 0 0 0-.115-.1zM12 6.5a5.5 5.5 0 1 1-11 0 5.5 5.5 0 0 1 11 0z" />
        </svg>
      ),
    },
    {
      id: "timeline",
      label: "TIMELINE",
      stage: "F4",
      icon: (
        <svg className="w-3.5 h-3.5" viewBox="0 0 16 16" fill="currentColor">
          <path d="M0 0h1v15h15v1H0V0zm10 3.5a.5.5 0 0 1 .5-.5h4a.5.5 0 0 1 .5.5v4a.5.5 0 0 1-1 0V4.707l-4.146 4.147a.5.5 0 0 1-.708 0L7 6.707 3.354 10.354a.5.5 0 1 1-.708-.708l4-4a.5.5 0 0 1 .708 0L9.5 7.793 13.293 4H10.5a.5.5 0 0 1-.5-.5z" />
        </svg>
      ),
    },
    {
      id: "comparison",
      label: "COMPARISON",
      stage: "F6",
      icon: (
        <svg className="w-3.5 h-3.5" viewBox="0 0 16 16" fill="currentColor">
          <path d="M7 2a1 1 0 0 1 2 0v1h4.5a.5.5 0 0 1 0 1H12v8.5a1.5 1.5 0 0 1-1.5 1.5h-5A1.5 1.5 0 0 1 4 12.5V4h-.5a.5.5 0 0 1 0-1H8V2zM5 4v8.5a.5.5 0 0 0 .5.5h5a.5.5 0 0 0 .5-.5V4H5z" />
        </svg>
      ),
    },
    {
      id: "architecture",
      label: "ARCHITECTURE",
      stage: "DATAFLOW",
      icon: (
        <svg className="w-3.5 h-3.5" viewBox="0 0 16 16" fill="currentColor">
          <path d="M1 2.5A1.5 1.5 0 0 1 2.5 1h3A1.5 1.5 0 0 1 7 2.5v3A1.5 1.5 0 0 1 5.5 7h-3A1.5 1.5 0 0 1 1 5.5v-3zm8 0A1.5 1.5 0 0 1 10.5 1h3A1.5 1.5 0 0 1 15 2.5v3A1.5 1.5 0 0 1 13.5 7h-3A1.5 1.5 0 0 1 9 5.5v-3zm-8 8A1.5 1.5 0 0 1 2.5 9h3A1.5 1.5 0 0 1 7 10.5v3A1.5 1.5 0 0 1 5.5 15h-3A1.5 1.5 0 0 1 1 13.5v-3zm8 0A1.5 1.5 0 0 1 10.5 9h3a1.5 1.5 0 0 1 1.5 1.5v3a1.5 1.5 0 0 1-1.5 1.5h-3A1.5 1.5 0 0 1 9 13.5v-3z" />
        </svg>
      ),
    },
    {
      id: "docs",
      label: "DOCUMENTATION",
      stage: "F7/SPECS",
      icon: (
        <svg className="w-3.5 h-3.5" viewBox="0 0 16 16" fill="currentColor">
          <path d="M14 4.5V14a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V2a2 2 0 0 1 2-2h5.5L14 4.5zm-3 0A1.5 1.5 0 0 1 9.5 3V1H4a1 1 0 0 0-1 1v12a1 1 0 0 0 1 1h8a1 1 0 0 0 1-1V4.5h-2z" />
        </svg>
      ),
    },
  ];

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

      {/* Main brand bar */}
      <div className="max-w-[1440px] mx-auto px-4 py-3 flex flex-col md:flex-row md:items-center md:justify-between gap-3">
        <div className="flex items-center gap-3">
          <span className="font-mono text-[14px] bg-[var(--bg-surface)] border border-[var(--border-main)] text-[#FF6B35] px-2.5 py-1 font-semibold">
            PRJ_111
          </span>
          <div>
            <h1 className="text-[16px] md:text-[20px] font-bold tracking-tight text-[var(--text-main)] uppercase">
              DVB-S2 Receiver Output Stream Analyzer
            </h1>
            <p className="text-[11px] font-mono text-[var(--text-muted)]">
              MULTI-FORMAT TELEMETRY / ANOMALY DETECTION / SEMANTIC SHIELD
            </p>
          </div>
        </div>

        {/* Status / Active Format Badge */}
        <div className="flex items-center gap-2 font-mono text-[11px]">
          <span className="text-[var(--text-muted)] uppercase">ACTIVE VIEW:</span>
          <span className="bg-[var(--bg-surface)] border border-[#FF6B35] text-[#FF6B35] font-bold px-2 py-0.5 uppercase">
            {activeTab}
          </span>
          {activeFormat && (
            <>
              <span className="text-[var(--border-main)]">|</span>
              <span className="text-[var(--text-muted)] uppercase">FORMAT:</span>
              <span className="bg-[var(--bg-surface)] border border-[var(--border-main)] text-[var(--text-main)] px-2 py-0.5 uppercase">
                {activeFormat}
              </span>
            </>
          )}
        </div>
      </div>

      {/* Version 1 Navigation Tabs Bar (With Present Theme) */}
      <nav
        className="w-full border-t border-[var(--border-main)] bg-[var(--bg-surface)]/60 px-4"
        aria-label="Feature Pages Navigation"
      >
        <div className="max-w-[1440px] mx-auto flex items-center overflow-x-auto gap-0.5 font-mono text-[12px]">
          {navTabs.map((tab) => {
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => onSelectTab(tab.id)}
                className={`px-3.5 py-2.5 border-b-2 font-mono text-[12px] flex items-center gap-2 transition-all cursor-pointer whitespace-nowrap ${
                  isActive
                    ? "border-[#FF6B35] bg-[var(--bg-surface)] text-[var(--text-main)] font-bold shadow-none"
                    : "border-transparent text-[var(--text-muted)] hover:text-[var(--text-main)] hover:bg-[var(--bg-surface)]"
                }`}
                title={`Shift page view to ${tab.label}`}
              >
                <span className={isActive ? "text-[#FF6B35]" : "text-[var(--text-muted)]"}>
                  {tab.icon}
                </span>
                <span>{tab.label}</span>
                <span
                  className={`text-[10px] px-1 py-0.2 border ${
                    isActive
                      ? "border-[#FF6B35]/50 text-[#FF6B35] bg-[var(--bg-main)]"
                      : "border-[var(--border-dim)] text-[var(--text-muted)]"
                  }`}
                >
                  {tab.stage}
                </span>
              </button>
            );
          })}
        </div>
      </nav>
    </header>
  );
};
