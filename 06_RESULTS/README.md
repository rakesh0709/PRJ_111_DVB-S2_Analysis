# 06_RESULTS — Experimental Results & Analysis Outputs

## Purpose
This directory stores verified empirical evaluation outputs, analysis artifacts, spatial window timelines, cross-format comparisons, and automated diagnostic reports produced by the PRJ_111 application across authoritative DVB-S2 datasets.

---

## Directory Inventory & Artifact Structure

```
06_RESULTS/
├── comparisons/                # Cross-format and sub-stream comparison audits (Feature F6)
│   ├── comparison_cross_format_ts_bbframe.json    # TS vs BBFrame comparison with semantic shield
│   ├── comparison_ts_substreams.json              # First half vs second half temporal TS comparison
│   ├── comparison_bbframe_substreams.json         # BBFrame sub-stream comparison
│   └── comparison_ts_synthetic_degradation.json   # Clean vs degraded TS comparison audit
├── explanations/               # Feature-level diagnostic attribution summaries (Feature F5)
│   ├── explanations_mpeg_ts.json                  # Bounded Z-score attributions for MPEG-TS anomalies
│   ├── explanations_gse.json                      # Bounded Z-score attributions for GSE anomalies
│   └── explanations_bbframe.json                  # Bounded Z-score attributions for BBFrame anomalies
├── reports/                    # Multi-format automated diagnostic reports (Feature F7)
│   ├── report_mpeg_ts.{json, md, txt, html}       # MPEG-TS inspection report in 4 export formats
│   ├── report_gse.{json, md, txt, html}           # GSE inspection report in 4 export formats
│   ├── report_bbframe.{json, md, txt, html}       # BBFrame inspection report in 4 export formats
│   ├── report_comparison_cross_format.{json, md, txt, html} # Cross-format audit reports
│   └── report_comparison_ts_halves.{json, md, txt, html}    # Temporal comparison audit reports
└── timelines/                  # Full spatial window activity logs with byte offsets (Feature F4)
    ├── timeline_mpeg_ts.{json, html}              # MPEG-TS spatial window timeline & visualization
    ├── timeline_gse.{json, html}                  # GSE spatial window timeline & visualization
    └── timeline_bbframe.{json, html}              # BBFrame spatial window timeline & visualization
```

---

## Artifact Descriptions

### 1. `comparisons/` (Feature F6: Semantic Comparison Shield)
Stores JSON output records of cross-stream comparisons. Enforces the strict distinction between **comparable metrics** (e.g., `total_payload_bytes`, `integrity_ratio`) and **shielded incommensurable metrics** (e.g., PID entropy vs. DFL dispersion, unit counts) with domain rationales preventing invalid cross-layer inferences.

### 2. `explanations/` (Feature F5: Diagnostic Attribution Engine)
Stores feature-level attribution records for detected anomalous windows. Attributions use bounded Z-scores ($|Z| \le 20.0\,\sigma$) to quantify the primary structural contributors to anomaly flags (e.g., packet truncation at capture boundary, extreme PID concentration).

### 3. `reports/` (Feature F7: Multi-Format Report Synthesizer)
Stores comprehensive, structured diagnostic reports generated in four formats:
- **JSON:** Complete machine-readable data schema for external ingestion.
- **Markdown:** Formatted summary tables for documentation and GitHub.
- **Plain Text:** Formatted fixed-width tables for CLI viewing and logging.
- **HTML5:** Standalone, self-contained report with CSS styling for printing and archiving.

### 4. `timelines/` (Feature F4: Spatial Activity Timeline)
Stores window-by-window sequential activity data, mapping window indices to exact raw byte offsets (`0x...`), unit counts, payload bytes, health ratios, and anomaly flags. Includes interactive HTML exports with embedded Chart.js graphs.
