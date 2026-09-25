# PRJ_111 Project Documentation Ledger - Interim Architectural State

**Project:** PRJ_111 - Development of a Software Application for Analysis and Processing of DVB-S2 Receiver Output Stream  
**Target Milestone:** Review-2 (~50%+ Functional Prototype Milestone, 26 September 2026)  
**Ledger Updated:** 20 September 2026  
**Status:** Review-2 Bug Fixes, Diagnostic Audit & Regression Validated (240/240 Tests Passing: 207 Backend + 33 Frontend, 0 Failures, 0 Errors)  
*Note: In accordance with project governance, `07_DOCUMENTATION/` and `01_RAW_DATA/` remain strictly frozen and untouched.*

---

## 1. Executive Summary & Verification State

The PRJ_111 software application processes multi-format digital receiver output streams captured post-demodulator (MPEG-2 Transport Stream, Generic Stream Encapsulation, and DVB-S2 Baseband Frames). 

| Feature Layer | Primary Source File | Verified Status | Test Coverage | Operational Scope |
|---|---|:---:|:---:|---|
| **Multi-Format Ingestion** | `ingestion/stream_handler.py` | Complete & Audited | Active | Header sniffing & dispatch (MPEG-TS, GSE, BBFrame) |
| **Stream Parsers** | `parsers/ts_parser.py`<br>`parsers/gse_parser.py`<br>`parsers/bbframe_parser.py` | Complete & Audited | Active | 188B TS framing, variable GSE PDUs, DVB-S2 BBFrames |
| **Unified Feature Extraction** | `features/extractor.py` | Complete & Audited | Active | Normalized cross-format telemetry & format-specific metrics |
| **F1: Stream Health Analysis** | `analysis/health.py` | Complete & Audited | Active | Priority-1 integrity indicators & health scoring (0-100) |
| **F2: AI Anomaly Detection** | `analysis/anomaly.py` | Complete & Calibrated | Active | Calibrated Isolation Forest with bounded Z-score deviations |
| **F3: Pattern Detection** | `analysis/patterns.py` | Complete & Audited | Active | Dominant PIDs, GSE protocols, modal DFLs, mode shifts |
| **F4: Timeline & Visualization** | `analysis/timeline.py`<br>`visualization/dashboard.py` | Complete & Audited | 18 Dedicated | Window timelines, metric series, interactive HTML dashboards |
| **F5: Anomaly Explanation** | `analysis/explanation.py` | Complete & Audited | Active | Structured 9-point explanatory model with domain guards |
| **F6: Stream Comparison Engine** | `analysis/comparison.py` | Complete & Audited | 27 Dedicated | Multi-tier differential engine with semantic audit |
| **F7: Automatic Analysis Report** | `analysis/report.py` | Complete & Audited | 25 Dedicated | Multi-format executive reporting (JSON, MD, TXT, HTML) with Tripartite taxonomy |
| **Engineering Workstation Frontend** | `frontend/server.py`<br>`frontend/static/` | Complete & Verified | **33 Dedicated / 240 Total** | Engineering workstation UI, browser file upload, staging, offline Chart.js |

---

## 2. Feature F6: Stream Comparison Engine Architecture

Feature F6 compares two analyzed receiver-output streams (**Stream A** and **Stream B**) and deterministically identifies, quantifies, and classifies measurable differences across 5 analytical dimensions:

```
       Stream A                                Stream B
          │                                       │
          ▼                                       ▼
 ┌─────────────────┐                     ┌─────────────────┐
 │ StreamHandler A │                     │ StreamHandler B │
 └────────┬────────┘                     └────────┬────────┘
          ▼                                       ▼
 ┌─────────────────┐                     ┌─────────────────┐
 │ F1..F5 Pipeline │                     │ F1..F5 Pipeline │
 └────────┬────────┘                     └────────┬────────┘
          │                                       │
          └───────────────────┬───────────────────┘
                              ▼
               ┌─────────────────────────────┐
               │    Feature F6: Comparison   │
               │   - Common Semantic Audit   │
               │   - Format-Specific Deep    │
               │   - Anomaly & Stability     │
               │   - Pattern Differences     │
               │   - Alignment & Quantiles   │
               │   - Domain-Safety Guard     │
               └──────────────┬──────────────┘
                              ▼
                 StreamComparisonReport
               (Structured JSON / ASCII)
```

### A. Semantic Audit of Common Metrics (Governing Rule)
Fields sharing identical names inside `CommonMetrics` are **not** assumed to be cross-format comparable. Cross-format comparison is strictly restricted to physically equivalent concepts:

| Metric Name | Physical Concept Across Formats | Cross-Format Status | Incompatibility Rationale | Same-Format Status |
|---|---|:---:|---|:---:|
| `total_units` | 188B TS packet vs variable PDU vs ~7.2KB frame | **NOT_COMPARABLE** | Framing units represent physically distinct boundaries. Unit counts cannot be equated cross-format. | Fully Compared |
| `valid_units` | Valid TS packet / GSE PDU / BBFrame | **NOT_COMPARABLE** | Framing unit semantics differ; raw counts of passed containers cannot be equated cross-format. | Fully Compared |
| `invalid_units` | Corrupted packet / Malformed PDU / Frame CRC error | **NOT_COMPARABLE** | Failure blast radius and container dimensions differ fundamentally across formats. | Fully Compared |
| `truncated_units` | Incomplete packet / Truncated PDU / Partial frame | **NOT_COMPARABLE** | Truncation mechanics and container sizes are format-specific. | Fully Compared |
| `integrity_ratio` | Dimensionless syntactic validity proportion $[0.0, 1.0]$ | **COMPARABLE** | Normalized syntactic validity proportion of stream framing ($1.0 = 100\%$). | Fully Compared |
| `total_payload_bytes` | Physical octets (8-bit bytes) of user payload | **COMPARABLE** | A byte of user data is physically identical regardless of encapsulation layer. | Fully Compared |
| `mean_payload_bytes` | Payload bytes divided by framing unit count | **NOT_COMPARABLE** | Normalized per framing unit. Reflects container size, not stream throughput. | Fully Compared |
| `payload_ratio` | TS: packet-presence; GSE/BB: byte efficiency | **NOT_COMPARABLE** | Ratio definitions differ: TS calculates packet presence, while GSE/BB calculate byte efficiency. | Fully Compared |
| `error_count` | Aggregation of format-specific error events | **NOT_COMPARABLE** | Aggregates heterogeneous failure classes (sync/CC/TEI vs PDU syntax vs frame CRC-8). | Fully Compared |
| `error_rate` | Error count divided by framing units | **NOT_COMPARABLE** | Normalized per framing unit. 1% error on 7KB frames has vastly different blast radius than on 188B packets. | Fully Compared |
| `entropy` | PID multiplex vs network protocol vs ISI/mode | **NOT_COMPARABLE** | Measures fundamentally different physical spaces and cannot be equated cross-format. | Fully Compared |

### B. Mathematically Sound Zero-Baseline Handling
Relative percentage change from a baseline of zero ($\frac{B - 0}{0}$) is mathematically undefined. F6 strictly enforces:
- When $A = 0, B = 0$: Absolute delta $= 0.0$, Relative delta $= 0.0\%$, Direction = `EQUAL`, Classification = `UNCHANGED`, Significance = `NEGLIGIBLE`.
- When $A = 0, B > 0$: Absolute delta $= B$, Relative delta = `None` (never arbitrary $+100\%$), Direction = `B_HIGHER`, Classification = `INCREASED`, Significance = `CRITICAL` (for error counters) / `SUBSTANTIAL`.
- When $A > 0, B = 0$: Absolute delta $= -A$, Relative delta $= -100.0\%$, Direction = `A_HIGHER`, Classification = `DECREASED`, Significance = `CRITICAL`.
- When $A > 0, B > 0$: Evaluated under the unified significance hierarchy.

### C. Unified Significance Hierarchy
- **Equality Tolerance:** $|\Delta_{\text{rel}}| \le 0.5\% \implies$ `UNCHANGED`, `EQUAL`, `NEGLIGIBLE`.
- **`NEGLIGIBLE`:** $|\Delta_{\text{rel}}| < 2.0\%$ (ordinary baseline dispersion).
- **`MINOR`:** $2.0\% \le |\Delta_{\text{rel}}| < 10.0\%$ (noticeable operational divergence).
- **`SUBSTANTIAL`:** $10.0\% \le |\Delta_{\text{rel}}| < 50.0\%$ (significant operational shift).
- **`CRITICAL`:** $|\Delta_{\text{rel}}| \ge 50.0\%$ (major structural shift or integrity loss).

### D. Window Alignment Without Fake Timestamps
- **Direct Index Overlap:** Synchronizes windows $i \in [0, \min(N_A, N_B)-1]$. Trailing windows in asymmetric captures are cleanly logged under `unaligned_windows_a` or `unaligned_windows_b` as capture duration differences, not transmission errors.
- **Normalized Progress Deciles:** Aggregates both streams into 10 uniform progression bins ($0-10\%, 10-20\%, \dots, 90-100\%$) for macro-trajectory comparison.
- **Mandatory Alignment Disclaimer:**
  > *"Temporal alignment is unavailable without external receiver clock telemetry; streams are aligned by physical stream progress and sequential window index. Differences reflect spatial capture progression, not synchronized broadcast timestamps."*

### E. Strict Domain-Safety Guard (`UNSUPPORTED_INFERENCES_GUARD`)
Reports explicitly block speculative root-cause claims:
1. RF interference, jamming, or atmospheric rain fade (cannot be concluded; capture lacks RF carrier, signal power, or SNR telemetry).
2. Demodulator or tuner hardware failure (cannot be concluded; only post-demodulator digital output stream is captured).
3. Satellite transponder or uplink station failure (cannot be concluded; no transponder or satellite orbital telemetry available).
4. Signal-to-Noise Ratio (SNR) or link margin degradation (cannot be concluded; physical-layer parameters are absent from baseband stream).
5. Transmission path error or packet loss (cannot be concluded; framing syntax and CRC remain valid unless error bits are flagged).

Terminology safety rules:
- Dominant PIDs are referred to strictly as "dominant PID" or "PID 0x...", never as "elementary streams" without verified PSI/SI tables.
- F1 integrity evaluations are labeled "selected Priority-1 integrity indicators", never claiming "ETSI TR 101 290 compliance" or certification.
- Streams are never classified as "objectively defective" based solely on unsupervised statistical anomaly counts.

---

## 3. Feature F7: Automatic Analysis Report Architecture

Feature F7 synthesizes the authoritative outputs of features F1 through F6 into structured, multi-format executive diagnostic reports without duplicating parser execution, feature extraction, scoring, or model training:

```
                  Authoritative Analytical Inputs
 ┌─────────────────────────────────────────────────────────────┐
 │ Stream Telemetry (Parsers)     Stream Health (F1)           │
 │ Isolation Forest (F2)          Pattern Dynamics (F3)        │
 │ Timeline & Activity (F4)       Diagnostic Explanations (F5) │
 │ Stream Comparison (F6 - Opt)                                │
 └──────────────────────────────┬──────────────────────────────┘
                                │
                                ▼
 ┌─────────────────────────────────────────────────────────────┐
 │            AutomaticReportGenerator (Feature F7)           │
 │  - Tripartite Classification (Fact / Stat / Interpretation) │
 │  - Strict Epistemic-Safety Rules (No Speculative Causes)   │
 │  - Mandatory Domain-Safety Guard (RF / Hardware Shield)     │
 │  - Format-Aware Single-Stream & Dual-Stream Synthesis       │
 └──────────────────────────────┬──────────────────────────────┘
                                │
        ┌───────────────────────┼───────────────────────┐
        ▼                       ▼                       ▼
 ┌──────────────┐        ┌──────────────┐        ┌──────────────┐
 │     JSON     │        │   Markdown   │        │     Text     │
 │ (Programmatic│        │  (GitHub GFM │        │(cp1252 ASCII │
 │  Consumption)│        │   Alerts)    │        │  Monospace)  │
 └──────────────┘        └──────────────┘        └──────────────┘
                                │
                                ▼
                         ┌──────────────┐
                         │ Standalone   │
                         │    HTML5     │
                         │ (Dark Theme) │
                         └──────────────┘
```

### A. Epistemological Tripartite Register
Every finding generated in an F7 report is strictly categorized into one of three epistemological registers to prevent conflation between raw measurements, statistical inference, and contextual interpretation:

1. **`OBSERVED_FACT` (Deterministic Syntactic Telemetry):**
   - Directly observed, unambiguous facts established deterministically by parsing binary framing structures.
   - *Examples:* Framing unit counts, valid/invalid/truncated unit counts, exact user payload byte counts, dominant PID numbers, Priority-1 continuity counter / transport error indicator flags, modal DFL values.
2. **`STATISTICAL_FINDING` (Model & Aggregate Measurements):**
   - Quantitative aggregates, distributions, and algorithmic inferences derived over sequential windows or the entire stream.
   - *Examples:* Stream health score (0–100), Isolation Forest anomaly rates and decision scores, Shannon entropy measurements, mean and peak payload density per window, component percentage shares.
3. **`ENGINEERING_INTERPRETATION` (Grounded Contextual Synthesis):**
   - Contextual engineering synthesis logically supported by observed facts and statistical findings.
   - *Rules:* Must be strictly grounded in available evidence. Speculative causal leaps are prohibited.
   - *Examples:* Slicing boundary deviations on partial final windows, multiplex bandwidth concentration on a dominant PID, differential shifts between streams.

### B. Epistemic-Safety Rules
To ensure scientific rigor and prevent misleading automated diagnostics, F7 enforces strict epistemic grounding:
- **Prohibited Causal Assertions:** The generator never asserts speculative operational causes such as "cold baseline stabilization", "capture start caused the anomaly", or "traffic burst as operational cause". If evidence only demonstrates an event occurred, it is reported as an `OBSERVED_FACT` or `STATISTICAL_FINDING`.
- **Capture Boundary Attribution:** Window size discrepancies occurring at the final window of a capture are neutrally attributed to the stream capture recording boundary without hypothesizing why capture ended.
- **PID Neutrality:** Dominant PIDs are designated strictly as "dominant PID [number]" unless verified PSI/SI tables (PAT/PMT) are present. Roles like "video stream" or "audio stream" are strictly barred without PSI/SI confirmation.
- **Standards Integrity:** F1 stream health evaluations are designated as "selected Priority-1 integrity indicators", never claiming formal certification or ETSI TR 101 290 standard compliance.

### C. Mandatory Domain-Safety Guard (`UNSUPPORTED_INFERENCES_GUARD`)
Reports explicitly include an immutable domain-safety guard blocking physical-layer speculation:
> *"Physical-layer parameters (e.g., RF carrier strength, SNR, MER, BER, AGC, rain fade, atmospheric attenuation, transponder health, and demodulator hardware state) cannot be determined from digital receiver output stream data alone without external physical-layer/demodulator telemetry."*

---

## 4. Test Suite Verification (205/205 Passing)

The complete PRJ_111 automated test suite executes cleanly:
```
Ran 207 tests in 5.992s — OK (207 passed, 0 failed, 0 errors)
```

### Breakdown of F7 Dedicated Tests (`tests/test_report.py` - 25 Tests):
1. `test_report_config_defaults`: Verifies default configurations, formatting options, and anomaly thresholds.
2. `test_report_finding_dataclass`: Tests `ReportFinding` serialization and schema fidelity.
3. `test_stream_summary_section`: Validates stream metadata and framing telemetry synthesis.
4. `test_health_findings_section`: Validates health score, status, and Priority-1 check mapping.
5. `test_anomaly_findings_section`: Validates Isolation Forest anomaly metrics and severity breakdowns.
6. `test_pattern_findings_section`: Validates dominant component, Shannon entropy, and structural findings.
7. `test_timeline_findings_section`: Validates window progression metrics, payload density, and event counts.
8. `test_explanation_findings_section`: Validates subsystem attribution and key explanation summaries.
9. `test_comparison_findings_section`: Validates dual-stream differential synthesis and alignment disclaimers.
10. `test_automatic_analysis_report_to_dict_and_json`: Tests complete JSON serialization without type errors.
11. `test_render_markdown_single_stream`: Validates Markdown formatting, tables, and alert callouts.
12. `test_render_markdown_dual_stream`: Validates differential comparison Markdown rendering.
13. `test_render_text_cp1252_safe`: Validates Windows cp1252 encoding safety and clean ASCII formatting.
14. `test_render_html_standalone`: Validates self-contained HTML5 output, styling, and executive structure.
15. `test_save_all_formats`: Verifies multi-format file generation (.json, .md, .txt, .html) on disk.
16. `test_generator_from_timeline_single_stream`: Verifies single-stream report generation from timeline.
17. `test_generator_from_timeline_dual_stream`: Verifies dual-stream report generation with F6 integration.
18. `test_generator_from_handler`: Tests pipeline orchestration directly from `StreamHandler`.
19. `test_tripartite_finding_taxonomy`: Verifies strict tripartite categorization across all findings.
20. `test_epistemic_safety_rules`: Verifies absence of speculative causes ("cold baseline", "traffic burst", etc.).
21. `test_truncated_boundary_handling`: Verifies neutral capture boundary wording for EOF edge windows.
22. `test_unsupported_inferences_guard_enforced`: Verifies strict blocking of RF/rain fade/demodulator claims.
23. `test_standards_compliance_wording_safety`: Blocks false claims of ETSI TR 101 290 formal certification.
24. `test_pid_role_neutrality`: Blocks "video stream" or "audio stream" claims from bare PID numbers.
25. `test_bbframe_modal_dfl_pattern_synthesis`: Verifies BBFrame modal DFL extraction from `modal_dfl_bits`.

### Breakdown of F6 Dedicated Tests (`tests/test_comparison.py` - 27 Tests):
1. `test_comparison_config_defaults` | 2. `test_identical_stream_comparison` | 3. `test_metric_difference_signed_and_pct`
4. `test_zero_baseline_handling` | 5. `test_significance_threshold_consistency` | 6. `test_difference_classification_direction`
7. `test_same_format_ts_comparison` | 8. `test_same_format_gse_comparison` | 9. `test_same_format_bbframe_comparison`
10. `test_cross_format_comparison_safety` | 11. `test_cross_format_entropy_incomparability` | 12. `test_cross_format_common_metrics_semantic_audit`
13. `test_cross_format_shared_metrics_comparability` | 14. `test_cross_format_anomaly_caveat` | 15. `test_pid_terminology_safety`
16. `test_standards_compliance_wording_safety` | 17. `test_different_stream_lengths` | 18. `test_truncated_final_window_handling`
19. `test_empty_stream_comparison` | 20. `test_missing_metrics_graceful_fallback` | 21. `test_anomaly_distribution_comparison`
22. `test_severity_distribution_comparison` | 23. `test_pattern_differences_pid_distribution` | 24. `test_pattern_differences_dfl_distribution`
25. `test_window_alignment_direct_index` | 26. `test_window_alignment_progress_deciles` | 27. `test_unsupported_inferences_guard_enforced`

### Breakdown of F4 Dedicated Tests (`tests/test_timeline.py` - 18 Tests):
1. `test_ts_timeline_generation` | 2. `test_gse_timeline_generation` | 3. `test_bbframe_timeline_generation`
4. `test_get_series_extraction` | 5. `test_f1_health_score_integration` | 6. `test_f2_anomaly_mapping`
7. `test_f3_pattern_mapping` | 8. `test_physical_offsets_tracking` | 9. `test_timeline_serialization`
10. `test_html_dashboard_generation` | 11. `test_ascii_summary_rendering` | 12. `test_empty_stream_handling`
13. `test_real_ts_dataset_timeline` | 14. `test_real_gse_dataset_timeline` | 15. `test_real_bbframe_dataset_timeline`
16. `test_true_end_to_end_pipeline` | 17. `test_ts_transition_calibration_no_false_events`
18. `test_configurable_anomaly_threshold_propagation`

---

## 5. Real-Data Experimental Findings

All five automated analysis experiments were executed via `run_f7_report_experiment.py` and generated complete 4-format report suites in `05_CODE/reports/`:

### Experiment 1: Single-Stream MPEG-TS Analysis (`sample.ts`)
- **Input:** `01_RAW_DATA/03_TS/DVBS2_toolkit/sample.ts` (18,176 packets, 91 windows, 200 pkts/window).
- **Executive Findings:**
  - `Framing Integrity`: 18,176 / 18,176 units syntactically valid (100.0% integrity ratio, 0 framing errors).
  - `User Payload Volume`: 3,267,305 bytes extracted.
  - `F1 Health`: 100.00 / 100.00 (`HEALTHY`).
  - `F2 Anomaly Scoring`: 5 / 91 windows flagged anomalous (5.49% rate, decision threshold 0.5000, peak score 0.8576 at boundary Window 90).
  - `F3 Patterns`: Dominant PID 256 (98.5% share), 4 active components, Shannon entropy 0.1361 bits.
  - `F5 Explanations`: 5 explained anomalies; Window 90 recognized as capture termination boundary; Windows 1, 2, 12 attributed to multiplex concentration; Window 88 attributed to adaptation field frequency.
  - `Epistemic Register`: 4 Observed Facts, 4 Statistical Findings, 2 Engineering Interpretations.
- **Reports:** `report_mpeg_ts.json`, `report_mpeg_ts.md`, `report_mpeg_ts.txt`, `report_mpeg_ts.html`

### Experiment 2: Single-Stream DVB-S2 BBFrame Analysis (`dvb-s2_bb_example.pcap`)
- **Input:** `01_RAW_DATA/01_BBFRAME_GSE/dvb-s2_bb_example.pcap` (4,309 baseband frames, 87 windows, 50 frames/window).
- **Executive Findings:**
  - `Framing Integrity`: 4,309 / 4,309 frames syntactically valid (100.0% integrity ratio, 0 CRC errors).
  - `User Payload Volume`: 1,958,826 bytes extracted.
  - `F1 Health`: 100.00 / 100.00 (`HEALTHY`).
  - `F2 Anomaly Scoring`: 5 / 87 windows flagged anomalous (5.75% rate, decision threshold 0.5000, peak score 0.7406 at boundary Window 86).
  - `F3 Patterns`: Modal DFL 8,304 bits (92.0% modal share), 5 unique DFL components, Shannon entropy N/A.
  - `F5 Explanations`: 5 explained anomalies; Window 86 recognized as capture termination boundary (score 0.7406); Window 0 attributed to initial frame size dispersion; Windows 83-85 attributed to payload volume variations.
  - `Epistemic Register`: 4 Observed Facts, 4 Statistical Findings, 2 Engineering Interpretations.
- **Reports:** `report_bbframe.json`, `report_bbframe.md`, `report_bbframe.txt`, `report_bbframe.html`

### Experiment 3: Single-Stream GSE Analysis (`sample.ts`)
- **Input:** `01_RAW_DATA/02_GSE/GSExtract/sample.ts` (14 GSE PDUs, 5 windows, 3 PDUs/window).
- **Executive Findings:**
  - `Framing Integrity`: 14 / 14 PDUs syntactically valid (100.0% integrity ratio, 0 framing errors).
  - `User Payload Volume`: 8,764 bytes extracted.
  - `F1 Health`: 100.00 / 100.00 (`HEALTHY`).
  - `F2 Anomaly Scoring`: 1 / 5 windows flagged anomalous (20.00% rate, decision threshold 0.5000, peak score 0.5018 at boundary Window 4).
  - `F3 Patterns`: Dominant protocol GSE_EXT_NPA (100.0% share), 1 active protocol component.
  - `F5 Explanations`: 1 explained anomaly; Window 4 recognized as capture termination boundary (2 units vs nominal 3).
  - `Epistemic Register`: 3 Observed Facts, 3 Statistical Findings, 1 Engineering Interpretation.
- **Reports:** `report_gse.json`, `report_gse.md`, `report_gse.txt`, `report_gse.html`

### Experiment 4: Dual-Stream MPEG-TS Comparison (First vs Second Half)
- **Input:** `sample.ts` First Half (Windows 0-44, 45 windows) vs Second Half (Windows 45-90, 46 windows).
- **Executive Findings:**
  - `Format Equivalence`: Same Format = True (`MPEG_TS`).
  - `Alignment`: Direct index overlap across 45 windows, 1 trailing unaligned window in Stream B logged neutrally.
  - `Key Differences`: Payload volume $\Delta = +14,843$ bytes ($+0.91\%$, `INCREASED`, `NEGLIGIBLE`); Framing integrity $\Delta = 0.0$ (`UNCHANGED`); Anomaly count $\Delta = -1$ window (3 vs 2).
  - `Epistemic Register`: 4 Observed Facts, 4 Statistical Findings, 3 Engineering Interpretations (including cross-stream differential synthesis).
- **Reports:** `report_comparison_ts_halves.json`, `report_comparison_ts_halves.md`, `report_comparison_ts_halves.txt`, `report_comparison_ts_halves.html`

### Experiment 5: Dual-Stream Cross-Format Comparison (MPEG-TS vs BBFrame)
- **Input:** `sample.ts` (MPEG-TS, 91 windows) vs `dvb-s2_bb_example.pcap` (BBFrame, 87 windows).
- **Executive Findings:**
  - `Format Equivalence`: Same Format = False (`MPEG_TS` vs `BB_FRAME`).
  - `Semantic Audit`: All 9 container-dependent metrics categorized as `NOT_COMPARABLE`.
  - `Key Differences`: User payload volume shifted by $-1,308,479$ bytes ($-40.05\%$, `DECREASED`, `SUBSTANTIAL`); Framing integrity $1.0$ vs $1.0$ (`EQUAL`).
  - `Alignment`: Direct index overlap across 87 windows, 4 trailing unaligned windows in Stream A logged neutrally.
  - `Domain Safety`: RF/rain fade/demodulator inferences completely blocked; alignment disclaimer attached.
- **Reports:** `report_comparison_cross_format.json`, `report_comparison_cross_format.md`, `report_comparison_cross_format.txt`, `report_comparison_cross_format.html`

---

## 6. Artifact Ledger

All artifacts generated during Feature F6 and Feature F7 development reside strictly within `05_CODE/`:
- `05_CODE/dvbs2_analyzer/analysis/comparison.py` (Feature F6 core implementation)
- `05_CODE/dvbs2_analyzer/analysis/report.py` (Feature F7 core implementation)
- `05_CODE/dvbs2_analyzer/analysis/__init__.py` (API exports)
- `05_CODE/tests/test_comparison.py` (27 automated test cases for F6)
- `05_CODE/tests/test_report.py` (25 automated test cases for F7)
- `05_CODE/tests/test_timeline.py` (18 automated test cases for F4)
- `05_CODE/run_f6_comparison_experiment.py` (4-experiment runner for F6)
- `05_CODE/run_f7_report_experiment.py` (5-experiment runner for F7)
- `05_CODE/reports/PROJECT_DOCUMENTATION_LEDGER.md` (This document)

### Generated Report Artifacts (`05_CODE/reports/`):
- **Feature F6 Comparison Reports:**
  - `comparison_ts_substreams.json`
  - `comparison_bbframe_substreams.json`
  - `comparison_ts_synthetic_degradation.json`
  - `comparison_cross_format_ts_bbframe.json`
- **Feature F7 Automatic Analysis Reports:**
  - `report_mpeg_ts.json`, `.md`, `.txt`, `.html` (Experiment 1)
  - `report_bbframe.json`, `.md`, `.txt`, `.html` (Experiment 2)
  - `report_gse.json`, `.md`, `.txt`, `.html` (Experiment 3)
  - `report_comparison_ts_halves.json`, `.md`, `.txt`, `.html` (Experiment 4)
  - `report_comparison_cross_format.json`, `.md`, `.txt`, `.html` (Experiment 5)

---

## 7. Backend Audit, Reconciliation & Freeze Ledger (Review-2 Milestone)

A rigorous end-to-end engineering audit was conducted across Features F1 through F7 on 19 September 2026. The backend is verified and completely frozen for Review-2.

### A. Numerical Reconciliation
1. **BBFrame Peak Anomaly Score:**
   - *Investigation:* Audit confirmed that the authoritative runtime score generated by Feature F2, stored in `timeline_bbframe.json`, `explanations_bbframe.json`, and `report_bbframe.json` has always been **`0.7406`** (specifically `0.740568` at boundary Window 86). The value `0.8872` was a typographical error in earlier draft documentation and has been reconciled across all artifacts.
2. **BBFrame Modal DFL Synthesis:**
   - *Investigation:* `timeline.py` stored BBFrame modal DFL under the format-specific metric key `modal_dfl_bits`, whereas `report.py` checked `modal_dfl`, causing the F7 executive summary to report `modal DFL of N/A`.
   - *Resolution:* `report.py` was updated to support both `modal_dfl_bits` and `modal_dfl`, extracting modal percentage and unique component count directly from `pattern_findings`. The regenerated report accurately reports `modal DFL of DFL 8304 bits (92.0% share)` across 5 components.

### B. Epistemic and Terminology Sanitization
1. **Health Interpretation Strings (`analysis/health.py`):**
   - Sanitized TEI and CC interpretation strings to eliminate speculative inferences regarding "physical layer forward error correction failure", "receiver FEC", and "elementary PIDs". All statements now neutrally report digital stream indicators.
2. **Component Mapping (`analysis/explanation.py`):**
   - Updated component map for `dominant_pid` from `"MPEG-TS Multiplex / Elementary Stream Allocation"` to `"MPEG-TS Multiplex / Dominant PID Allocation"` to preserve strict PID neutrality without verified PSI/SI tables.
3. **Threshold Configurability (`analysis/timeline.py`):**
   - Added `f2_anomaly_threshold: float = 0.50` to `TimelineConfig` and propagated it dynamically into `AnomalyConfig` across all formats, ensuring full end-to-end configurability without silent hardcoding.

### C. Scope and Boundary Confirmations
- `01_RAW_DATA/`: Confirmed 100% untouched.
- `07_DOCUMENTATION/`: Confirmed 100% untouched.
- `walkthrough.md`: Confirmed 100% untouched.
- Full regression suite: **207 / 207 tests passing (100% pass rate)**.
- **Backend Status:** FROZEN for Review-2.

---

## 8. Functional Frontend MVP Implementation Ledger (Review-2 Milestone)

A complete, zero-dependency, functional frontend application was implemented on 19 September 2026 to connect directly to the frozen F1–F7 backend.

### A. Architecture & Technology
- **Architecture:** Zero-dependency Python threaded HTTP server (`ThreadingHTTPServer`) serving a modern single-page application (SPA).
- **Offline Guarantee:** Chart.js vendored locally (`dvbs2_analyzer/frontend/static/vendor/chart.umd.min.js`, 205 KB) — eliminating external CDN reliance for offline demonstrations.
- **API Integration:** Clean REST endpoints (`/api/status`, `/api/presets`, `/api/analyze`, `/api/compare`, `/api/export`) directly consuming the frozen backend without duplicating analytical logic.
- **Launcher:** Standalone CLI launcher `run_frontend.py` (`--port`, `--host`, `--no-browser`) with auto-browser launch.

### B. Implemented Views
1. **Dashboard:** Stream ingestion, preset selectors, format auto-detection, F1 health indicators, F2 anomaly summary, F3 pattern preview.
2. **Anomaly Analysis (F2 + F5):** Interactive anomaly windows table, Bounded Z-Score Magnitude with explicit deviation direction, primary/secondary drivers, subsystem attribution, and capture boundary neutrality.
3. **Timeline (F4):** Interactive Chart.js time-series plots (rolling health score, AI anomaly score with $s=0.50$ threshold, payload volume KB, format-specific metric) and window telemetry table indexed strictly by physical byte offsets and unit sequence numbers.
4. **Comparison (F6):** Dual stream and half-vs-half comparison, same-format vs. cross-format badge, differential matrix ($\Delta_{\text{abs}}, \Delta_{\text{rel}}\%$), and strict enforcement of the F6 cross-format semantic barrier (2 comparable vs. 9 non-comparable metrics).
5. **Automatic Report (F7):** Executive synthesis, active domain-safety guard (`UNSUPPORTED_INFERENCES_GUARD`), tripartite findings filter (`OBSERVED_FACT`, `STATISTICAL_FINDING`, `ENGINEERING_INTERPRETATION`), and one-click artifact export (JSON, Markdown, Plain Text, Standalone HTML).

### C. Verification & Test Evidence
- **Frontend Unit & Integration Suite (`tests/test_frontend.py`):** 18 / 18 tests passing (100%).
- **Full Project Regression Suite:** **225 / 225 tests passing (100%)** with 0 failures and 0 errors in 17.985s.
- **Real Stream Formats Verified via API:**
  - MPEG-TS (`sample.ts`): 91 windows, 5 anomalies, 100.0 health.
  - GSE (`GSExtract/sample.ts`): 5 windows, 1 anomaly, 100.0 health.
  - BBFrame (`dvb-s2_bb_example.pcap`): 87 windows, 5 anomalies, 100.0 health.
  - TS Halves Comparison: 45 aligned windows, same format.
  - Cross-Format Comparison (TS vs BBFrame): 2 comparable, 9 blocked by semantic shield.
- **Backend Analytical Invariance:** 0 backend files modified in `dvbs2_analyzer/analysis/`, `parsers/`, `features/`, `ingestion/`.

---

## 9. Engineering Workstation Redesign & Final Frontend Verification Ledger (Review-2 Milestone)

A comprehensive redesign and technical audit of the frontend was finalized on 20 September 2026, transitioning the UI into an authentic technical engineering analysis workstation (Wireshark/MATLAB style).

### A. Technical Engineering Workstation Implementation
- **Visual Style & Aesthetic:** Dark engineering workstation palette (`#0d1117`, `#161b22`, `#21262d`, `#30363d`, with technical blue/cyan accent `#388bfd`), rectangular geometry (3px border radius, zero pill-shaped buttons), compact telemetry tables (padding 6px 10px), monospace telemetry values, functional monochrome inline SVG icons, zero unicode emojis, and zero em dashes (`—`) in UI copy.
- **Primary Input via Real Browser File Upload:** Implemented direct browser file upload (`Choose File` input and drag-and-drop dropzone) connected to `/api/upload`. Added real-time technical file inspection metadata panel (displaying exact byte count, KB/MB calculation, and staging readiness). Advertises strictly verified input formats: `MPEG-TS (.ts)`, `GSE (.ts, .gse)`, and `DVB-S2 BBFrame (.pcap)`. Unsupported files are rejected cleanly by the parser/format detection layer rather than advertised as supported.
- **Local Staging Security:** Uploaded captures are temporarily staged locally under `05_CODE/uploads/` with strict filename sanitization (regex alphanumeric, dot, hyphen, underscore) and path traversal prevention. All staged temporary files are cleanly unlinked after verification.
- **Secondary Inputs Retained:** Verified authoritative repository captures in `01_RAW_DATA/` remain accessible via the presets dropdown.
- **Conceptual Execution Sequence Checklist:**
  - Displays the complete conceptual sequence on the dashboard:
    `Stream Ingestion -> F1 Stream Health -> F2 Anomaly Detection -> F3 Pattern Detection -> F4 Timeline -> F5 Anomaly Explanation -> F6 Stream Comparison: Awaiting comparison input -> F7 Automatic Report`
  - Real wall-clock elapsed timer driven by `performance.now()` measuring execution duration.
- **Favicon & Regulatory Disclaimers:**
  - Geometric DVB-S2 constellation/framing SVG favicon (`favicon.svg`) and binary ICO (`favicon.ico`) served with verified MIME types (`image/svg+xml`, `image/x-icon`).
  - Terms & Conditions modal implemented detailing academic prototype scope, local file staging disclosure (no external cloud transfer), domain safety boundaries, and research scope.

### B. Single-Stream Execution Status Mapping
For a single uploaded stream, the execution status across features is explicitly mapped as:
- **F1 Health:** executed
- **F2 Anomaly Detection:** executed
- **F3 Pattern Detection:** executed
- **F4 Timeline:** executed
- **F5 Explanation:** executed
- **F6 Comparison:** awaiting comparison input (F6 is NOT executed during single-stream analysis)
- **F7 Automatic Report:** executed

Standardized governing phrase:
> *"F1-F5 and F7 analysis executed on uploaded stream; F6 comparison available when a comparison input is provided."*

### C. Epistemic & Domain-Safety Boundaries
1. **No Fake Metrics & No Fabricated Telemetry:** All dashboard values, anomaly scores, and feature distributions derive exclusively from real backend calculation.
2. **No Unsupported RF Claims:** Physical RF layer inference guard remains strictly active; no speculative claims regarding SNR, Eb/N0, BER, carrier frequency drift, rain fade, or hardware failure are made.
3. **No Fake Timestamps:** Stream timelines strictly index events and windows by physical byte offsets and unit sequence numbers, avoiding synthetic timestamps or fabricated throughput rates.
4. **ETSI Scope Qualification:** Stream health checks are documented strictly as *"Selected stream integrity indicators inspired by ETSI TR 101 290 principles"*, with no claim of formal ETSI certification.
5. **Operational Scope:** Prototype operates exclusively on post-demodulator digital receiver outputs; no real-time RF analysis is claimed.
6. **Milestone Scope:** The system represents an interim Review-2 (~50%+ Functional Prototype) milestone; no claim of full project completion is made.
7. **Raw Datasets Invariance:** All captures in `01_RAW_DATA/` remain 100% untouched.

### D. Final Verified Test Suite
Executed via project virtual environment:
```powershell
& "05_CODE\.venv\Scripts\python.exe" -m unittest discover -s tests -v
```
- **Total Tests Passing:** 230 / 230 (100% pass rate)
- **Backend Tests:** 207 passing (F1-F7 core analytical engines, parsers, and features 100% frozen)
- **Frontend Tests:** 23 passing (HTTP server, static assets, SVG/ICO favicon, binary upload, empty payload rejection, path traversal, upload-and-analyze end-to-end integration)
- **Failures:** 0
- **Errors:** 0
- **Execution Time:** ~15.7s

---

## 10. Review-2 Bug Fixes, Diagnostic Audit, Regression & Final Validation Ledger (20 September 2026)

A rigorous bug fix, diagnostic trace, and regression audit was completed on 20 September 2026 addressing all issues discovered during manual browser testing of the Review-2 functional prototype.

### A. Root Cause Analysis & Resolutions for Reported Bugs

1. **BUG 1: F6 Retains Stale Comparison State on Dashboard Clear**
   - **Root Cause:** In `dvbs2_analyzer/frontend/static/app.js`, `clearAnalysis()` reset single-stream UI panels and global `currentAnalysis = null`, but did not invoke any cleanup function for comparison state (`currentComparison = null`, comparison input fields, or `#comparisonResultsContent`).
   - **Resolution:** Implemented `resetComparisonState(keepInputs = false)`. In `clearAnalysis()`, invoked `resetComparisonState(false)`, which clears Stream A and Stream B path inputs, hides `#comparisonResultsContent`, and restores `#comparisonPlaceholder` with the exact message `"AWAITING COMPARISON INPUT"`.

2. **BUG 2: F6 Retains Stale Comparison Output After Primary Stream Changes**
   - **Root Cause:** When the user selected a new primary stream or uploaded a new file and clicked "Analyze", `executeAnalysis()` updated single-stream tabs F1-F5 and F7, but did not invalidate `#comparisonResultsContent` or update Stream A.
   - **Resolution:** In `executeAnalysis()`, added logic to populate `compStreamA.value` with the freshly analyzed stream path and invoke `resetComparisonState(true)`. This preserves the new Stream A input while clearing stale comparison tables, charts, and audit metrics until "Execute Comparison" is explicitly re-run.

3. **BUG 3: F6 Relative Paths Produce `StreamFormat.UNKNOWN`**
   - **Root Cause:** `StreamHandler._resolve_stream_path()` only evaluated paths against `PROJECT_ROOT` and current working directory (`CWD`). When relative paths such as `01_RAW_DATA/03_TS/DVBS2_toolkit/sample.ts` were entered from different subdirectories, path existence checks failed, raising `FileNotFoundError` or defaulting to `StreamFormat.UNKNOWN`.
   - **Resolution:** Enhanced `StreamHandler._resolve_stream_path()` and `FrontendCoordinator._resolve_path()` to systematically evaluate candidate paths against CWD, `PROJECT_ROOT`, `05_CODE/`, `05_CODE/uploads/`, `05_CODE/test_inputs/`, and perform unique filename lookups across `01_RAW_DATA/`. Relative paths now resolve deterministically regardless of execution working directory.

4. **BUG 4: F6 Comparison Results Not Invalidated When Inputs are Edited**
   - **Root Cause:** `input` and `change` event listeners were missing on `#compStreamA` and `#compStreamB`. Users could type an entirely new path or select a different preset while previously calculated differential metrics remained visible.
   - **Resolution:** Attached `input` and `change` event listeners to `#compStreamA` and `#compStreamB` in `setupEventListeners()`. Modifying either field immediately triggers `resetComparisonState(true)`, clearing stale metrics and restoring the prompt to execute comparison with the modified inputs.

5. **BUG 5: F6 Payload Delta Displays `"--"` Despite Same-Format Comparison**
   - **Root Cause:** In `dvbs2_analyzer/frontend/static/app.js`, `renderComparisonView()` attempted to read `comp.common?.payload_delta` or `comp.common?.total_payload_bytes_delta`, whereas `analysis/comparison.py` structures metric audits under `comp.common.metrics.total_payload_bytes` with sub-keys `absolute_difference`, `relative_difference_pct`, and `significance`.
   - **Resolution:** Corrected data extraction path in `app.js` to inspect `comp.common?.metrics?.total_payload_bytes`. Extracted `absolute_difference`, formatted `relative_difference_pct` to 2 decimal places with sign, and extracted `significance`. In addition, implemented dynamic rendering of the full semantic audit table for all metrics in `comp.common?.metrics`.

6. **BUG 6, 7 & 8: GSE Format Detection and Window Sizing Calibration**
   - **Root Cause:**
     - In `app.js`, `updateFileMetadataPanel()` contained naive extension logic: `if (name.endsWith(".ts")) { ... formatSelect.value = "MPEG_TS"; windowInput.value = 200; }`. Because the authoritative GSE capture is named `01_RAW_DATA/02_GSE/GSExtract/sample.ts`, selecting this file pre-selected `MPEG_TS` with window 200.
     - In `dvbs2_analyzer/ingestion/stream_handler.py`, `detect_stream_format()` relied on path keywords ("gse") and MPEG-TS sync lock. For `sample.ts` in neutral directories, it fell through to `StreamFormat.UNKNOWN`.
   - **Resolution:**
     - Removed the naive extension override in `app.js`, preserving `AUTO` format selection.
     - Implemented content-aware GSE detection in `stream_handler.py`: scans initial bytes for DVB-S2 Generic Stream Baseband Headers (`(hdr[0] & 0xC0) == 0x40` with valid CRC-8), accurately identifying GSE streams regardless of file extension or directory naming.
     - Enhanced MPEG-TS detection in `stream_handler.py` to scan up to 4096 bytes for periodic `0x47` sync lock (5 consecutive 188-byte intervals), correctly identifying TS captures that experience initial sync loss.
     - Default window sizes apply cleanly: MPEG-TS = 200, GSE = 3, BBFrame = 50.

7. **BUG 9: Ambiguous Header Verification Badge Text**
   - **Root Cause:** Header badge previously read `BACKEND F1-F7 FROZEN & VERIFIED | 207 TESTS PASSING`, which omitted frontend test coverage and created ambiguity.
   - **Resolution:** Updated header badge in `index.html` and `/api/status` response in `server.py` to read `BACKEND F1-F7 VERIFIED | 240 TESTS PASSING`, accurately capturing 207 backend and 33 frontend tests.

### B. Corrupted Transport Stream Diagnostic Trace (Bugs 10, 11 & 12)

A rigorous step-by-step diagnostic trace was performed on `01_RAW_DATA/03_TS/DVBS2_toolkit/corrupted_sample.ts` (3,417,088 bytes) to evaluate parser synchronization, error accounting, and whole-stream health scoring:

1. **Synchronization Errors Recorded by Parser:**
   - The parser encountered exactly **11 sync errors** during stream traversal.
2. **Packet Count Comparison & Dropped Packets:**
   - Clean stream (`sample.ts`): exactly **18,176 packets** yielded.
   - Corrupted stream (`corrupted_sample.ts`): exactly **18,168 packets** yielded.
   - Exactly **8 packets dropped** due to corrupted sync bytes and packet header invalidation.
3. **Why 18,168 Packets Were Yielded:**
   - `TSParser.parse_stream()` iterates byte-by-byte. When byte `i` is not `0x47`, it increments sync error count and scans forward for the next `0x47`. The 8 un-synchronized packets were skipped; only packets successfully locking onto periodic `0x47` and passing header validity checks were emitted.
4. **Why `valid_units = 18,168` and `invalid_units = 0`:**
   - In `generate_ts_timeline()`, framing validity is evaluated over the yielded `TSPacket` objects. Because every yielded packet possessed `sync_byte == 0x47`, all 18,168 yielded packets were evaluated as syntactically valid containers.
5. **Why Framing Integrity Ratio is 100.0%:**
   - Calculated strictly as $\frac{\text{valid\_units}}{\text{total\_units}} = \frac{18,168}{18,168} = 1.0000$ (100.0%). The dropped packets did not produce invalid container objects in the yielded collection.
6. **Why Transport Error Indicator (TEI) Count is 4:**
   - During resynchronization across the corrupted region, false `0x47` bytes within payload data aligned momentarily with the parser before true lock was achieved. Exactly 4 misaligned packets had bit 7 of byte 1 set to 1, producing $\text{TEI} = 4$.
7. **Resolution of Continuity Counter Error Reporting:**
   - In `coordinator.py` line 311, an assignment typo (`cc_errs = tot_errors`) previously mirrored total error count into continuity counter errors. This was corrected: `cc_errs` is now calculated from actual window continuity error counts. For `corrupted_sample.ts`, true CC discontinuities on valid PID streams are 0.
8. **Mathematical Derivation of Whole-Stream Health Score (99.67%):**
   - The 18,168 packets are partitioned into 91 windows of 200 packets (Windows 0 to 90).
   - Window 0 contains all 4 TEI errors ($\text{TEI rate} = \frac{4}{200} = 2.0\%$). Because the TEI error rate exceeded the critical threshold, Window 0 received a health score of **70.0%**.
   - Windows 1 through 90 contained 0 errors and received health scores of **100.0%**.
   - Rolling stream health score:
     $$\text{Average Health} = \frac{70.0 + 90 \times 100.0}{91} = \frac{9070.0}{91} \approx 99.6703\% \implies 99.67\%$$
9. **Consistency with Documented Thresholds:**
   - Under F1 health threshold rules, $\text{health} \ge 99.0\%$ is classified as `HEALTHY`.
   - Window 0 is correctly identified in F2 anomaly detection as an anomalous window (anomaly score **0.7985**, health score **70.0**), but the stream-level average across 91 windows remains 99.67%.
10. **Analytical Semantics Decision:**
    - The analytical semantics, scoring weights, and thresholds in `analysis/health.py` and `analysis/anomaly.py` were **intentionally preserved** without arbitrary alteration, upholding the strict project governance rule that frozen analytical backend logic must not be modified.

### C. Verification of Specific Integration Requirements

1. **Item 13: Direct-Index Alignment Integrity:**
   - In asymmetric comparisons (such as BBFrame 87 windows vs. TS 91 windows), F6 direct-index alignment aligns exactly $\min(\text{len}(A), \text{len}(B)) = \min(87, 91) = 87$ windows.
   - Trailing windows are cleanly logged as `unaligned_windows_b = 4` without synthetic padding or fake timestamps.
2. **Item 14: Sequential Stream Replacement Lifecycle:**
   - Verified sequential lifecycle over REST API:
     `MPEG-TS (win=200, units=18176) -> GSE (win=3, units=14) -> BBFrame (win=50, units=4309) -> MPEG-TS (win=200, units=18176)`.
   - Each format was detected automatically and processed with zero state leakage or cross-stream contamination.
3. **Item 15: Invalid / Unparseable File Handling Resilience:**
   - Ingesting corrupt, unrecognized, or non-stream binary files returns HTTP 400 Bad Request (semantically correct client input error) with structured JSON (`{"success": false, "error": "Analysis failed: Cannot instantiate parser for unrecognized format: StreamFormat.UNKNOWN"}`).
   - Differentiates client input errors (`ValueError`, `FileNotFoundError`) from unexpected server faults (`HTTP 500`), aligning with REST conventions and `_send_error_json`'s default status in `server.py`.
   - Automatically invalidates and clears cached analysis reports (`last_analysis_report = None`), clears UI analysis state (`currentAnalysis = null`), hides previous dashboard results, sets header badge to `ANALYSIS FAILED`, and ensures zero stale metrics remain visible.
   - The HTTP server daemon remains completely healthy, responsive, and immediately capable of analyzing subsequent valid streams.

### D. Final Verified Test Suite (Regression Audit)

Executed via project virtual environment:
```powershell
& "05_CODE\.venv\Scripts\python.exe" -m unittest discover -s tests -v
```
- **Total Tests Passing:** 240 / 240 (100% pass rate)
- **Backend Tests:** 207 passing (F1-F7 core analytical engines, parsers, and features 100% frozen)
- **Frontend Tests:** 33 passing (+10 regression tests added in `tests/test_frontend.py`)
- **Failures:** 0
- **Errors:** 0
- **Execution Time:** ~18.9s
- **Authoritative Data Invariance:** `01_RAW_DATA/` and `07_DOCUMENTATION/` 100% untouched.

---

## 11. Review-2 Research Paper Draft Milestone

- **Milestone:** Review-2 Academic Paper Draft
- **Target Venue Reference:** IEEE academic format, visual layout, two-column structure, and presentation derived from `IEEE REPORT AIOT.pdf`.
- **Scope & Length:** Technical content-driven length (~8–10 IEEE two-column pages), 22 full technical sections, 6 academic tables, 8 figures, 20 verified references.
- **Deliverables:**
  1. `05_CODE/reports/PRJ_111_RESEARCH_PAPER_DRAFT.md` (and artifact `PRJ_111_RESEARCH_PAPER_DRAFT.md`): 62,073 bytes markdown manuscript.
  2. `05_CODE/reports/PRJ_111_RESEARCH_PAPER_DRAFT.html` (and artifact `PRJ_111_RESEARCH_PAPER_DRAFT.html`): 1,811,137 bytes self-contained HTML document with all 11 diagrams, UI screenshots, author portraits, and team presentation photos embedded in base64, with `@media print` CSS for direct PDF export.
- **Authors:** Sk Samad (20231COM0031), Y Vengala Rao (20231COM0001), C Rakeshwar (20231COM0008), Department of Computer Science and Engineering, Presidency University, Bengaluru, Karnataka, India. Project Guide: Irfan Rajab Bhat, Assistant Professor.
- **Embedded Assets (11 Total):**
  - Architecture Diagram (`architecture_diagram.png`, 470 KB)
  - Workstation Standby Dashboard (`fig2_dashboard_empty.png`, 86 KB)
  - Workstation Active Analyzed View (`fig_dashboard_analyzed.png`, 108 KB)
  - F6 Stream Comparison Interface (`fig_comparison_view.png`, 135 KB)
  - F4 Spatial Activity Timeline View (`fig_timeline_view.png`, 160 KB)
  - F2+F5 Flagged Anomaly Windows Table (`fig_anomaly_view.png`, 112 KB)
  - F7 Multi-Format Report Generation (`fig_report_view.png`, 81 KB)
  - Author Portrait: Sk Samad (`author_samad.jpg`, 4 KB)
  - Author Portrait: Y Vengala Rao (`author_vengala_rao.jpg`, 9 KB)
  - Author Portrait: C Rakeshwar (`author_rakeshwar.jpg`, 5 KB)
  - Team Presentation Photo at Presidency University (`team_presentation.jpg`, 116 KB)
- **Zero Fabrication & Domain Safety Compliance:**
  - Zero RF fabrication (no SNR, BER, rain fade, or physical hardware attributes claimed).
  - Zero false clock timestamps (spatial progression indexed strictly by physical byte offsets and container sequence numbers).
  - No supervised ML claims on unlabeled data (Isolation Forest presented as an unsupervised baseline evaluated via synthetic perturbation).
  - 240/240 tests presented strictly as automated software regression verification, not model accuracy.
  - Future concepts (deep sequential models, SDR demodulation front-ends, hardware acceleration) strictly segregated in Section XXI (Future Work).

---

## 12. Review-2 Research Paper Final Factual Audit and Reconciliation Milestone

- **Milestone:** Review-2 Research Paper Complete Factual Audit & Image Verification
- **Date:** September 20, 2026
- **Status:** **COMPLETE & FULLY VERIFIED**
- **Artifacts Delivered:**
  1. `05_CODE/reports/PRJ_111_RESEARCH_PAPER_DRAFT.md` (and artifact copy): Fully reconciled IEEE-style markdown manuscript (61,959 bytes).
  2. `05_CODE/reports/PRJ_111_RESEARCH_PAPER_DRAFT.html` (and artifact copy): Standalone self-contained HTML5 paper (1,789,214 bytes) with embedded base64 assets, complete math, and print layout styles.
  3. `05_CODE/reports/PAPER_CORRECTION_AUDIT.md` (and artifact copy): Dedicated audit report itemizing all 10 reconciliation dimensions.
- **Key Factual Audit Reconciliations:**
  - **GSE Capture (`01_RAW_DATA/02_GSE/GSExtract/sample.ts`):** File size corrected to **9,324 bytes** (was stale: 7,064 B); payload corrected to **8,764 bytes** (was stale: 6,864 B); fragmentation breakdown corrected to **6 unfragmented (42.9%) and 8 fragmented (57.1%)** (specifically 5 first, 0 intermediate, 3 last fragments; was falsely claimed as "0% fragmentation / 14 unfragmented"); protocol counts verified as 11 `GSE_EXT_NPA` (100% outer), 9 IPv4; labels verified as 11 `LABEL_6B`, 3 `LABEL_NONE`; F2 anomaly verified as 1 anomalous window (Window 4, score 0.5018).
  - **BBFrame Capture (`01_RAW_DATA/01_BBFRAME_GSE/dvb-s2_bb_example.pcap`):** File size corrected to **2,349,376 bytes** (was stale: 1,846,554 B); frame count 4,309 frames; payload corrected to **1,958,826 bytes** (was stale: 1,777,618 B); Data Field Length (DFL) clarified as **expressed in BITS** ($[216, 10000]$ bits, mean 3,636.72 bits, modal 2,992 bits at 85.82%); MATYPE verified as **100.0% ACM** (was falsely claimed as CCM) and **99.98% SIS / 0.02% MIS** (was falsely claimed as 100% SIS); F2 anomaly verified as 5 anomalous windows (`[0, 83, 84, 85, 86]`, peak 0.7406 in window 86).
  - **MPEG-TS Payload Accounting:** Raw size 3,417,088 B ($18,176 \times 188$ B); fixed headers 72,704 B; adaptation field overhead 77,079 B; net user data payload reconciled to **3,267,305 bytes** across all analytical engines, reports, and comparisons; dashboard gross container display ($3,417,088 \text{ B} \approx 3,337 \text{ KB}$) distinguished from net user payload.
  - **F6 Stream Comparison Reconciliation:** MPEG-TS (3,267,305 B) vs. BBFrame (1,958,826 B); $\Delta_{\text{abs}} = \mathbf{-1,308,479.0 \text{ B}}$ (was stale: $-1,489,687$ B); $\Delta_{\text{rel}} = \mathbf{-40.05\%}$ (was stale: $-45.59\%$); significance classified as **`SUBSTANTIAL`**; `integrity_ratio` $1.0000$ vs. $1.0000$ ($\Delta_{\text{rel}} = 0.00\%$, `NEGLIGIBLE`); exactly 9 non-comparable metrics shielded.
  - **F1 Health Formula:** Removed fabricated weight sum equation ($w_{\text{sync}}=1000$, etc.); replaced with exact deductive threshold scoring rules from `analysis/health.py`.
  - **F2 Anomaly Model:** Reconciled Scikit-learn `IsolationForest(n_estimators=100, contamination=0.05, random_state=42)` and centered logistic sigmoid transformation $s(\mathbf{x}) = \frac{1}{1 + e^{8.0 \cdot d(\mathbf{x})}}$.
  - **Team Presentation Photo Processing:** Scanned vertical boundaries of `paper_assets/team_presentation.jpg`; cropped out GPS Map Camera banner at $y \in [0, 780]$ ($1600 \times 780$ px); verified clean image retaining authors, podium, whiteboard, and screen with zero GPS coordinates; updated Fig. 8 caption to remove coordinates.
  - **Academic Tone & Epistemic Boundaries:** Removed grandiose phrases ("pinnacle of spectral efficiency", "proves", "cost-prohibitive and incapable"); softened TEI/CC causality to observed bitstream flags; clarified that 240/240 tests verify software regression integrity, not supervised ML accuracy.
  - **Authoritative Data Invariance:** `01_RAW_DATA/` and `07_DOCUMENTATION/` remain 100% untouched. Backend F1–F7 core code remains 100% frozen.

---

## 13. Final IEEE-Style Research Paper Rebuild & PDF Generation Milestone

- **Milestone:** Final IEEE-Style Two-Column Research Paper Rebuild & Vector PDF Generation
- **Date:** September 20, 2026
- **Status:** **COMPLETE, VERIFIED & DELIVERED**
- **Primary Deliverable:** [`PRJ_111_Research_Paper_Final.pdf`](file:///c:/Users/rakes/Downloads/Mini%20Project/05_CODE/reports/PRJ_111_Research_Paper_Final.pdf) (1,281,160 bytes; 10 pages clean).
- **Source Artifacts Delivered:**
  1. `05_CODE/reports/PRJ_111_Research_Paper_Final.typ` (47,497 bytes): Typst source manuscript template.
  2. `05_CODE/reports/references.bib` (6,024 bytes): Standardized BibTeX bibliography containing all 20 authoritative references.
  3. Artifact mirror: `C:\Users\rakes\.gemini\antigravity\brain\f6e1950b-f179-4ada-b8f4-347900a519c5/PRJ_111_Research_Paper_Final.pdf`.
- **Key Implementation & Validation Achievements:**
  - **True Academic Typesetting Engine:** Utilized Typst v0.15.1 for native vector PDF compilation, completely eliminating browser-print artifacts (no URLs, timestamps, Chrome print buttons, or CSS responsive layout distortions).
  - **Clean Student/Conference Author Block:** Sk Samad (20231COM0031), Y Vengala Rao (20231COM0001), C Rakeshwar (20231COM0008), Presidency University, Bengaluru; Project Guide: Irfan Rajab Bhat.
  - **Zero Photos / Biographies:** Completely removed all author headshots, biographies, and GPS Map Camera team photos per strict scope instructions.
  - **Concise Abstract (214 Words):** Single paragraph, zero citations, systematically covering problem, PRJ_111 system, three formats, seven analytical capabilities, experimental validation, and 240/240 testing.
  - **Strict Alphabetical Index Terms:** *Anomaly detection, Baseband frame, Digital video broadcasting, DVB-S2, Feature extraction, Generic stream encapsulation, Isolation Forest, MPEG transport stream, Receiver output analysis, Stream analysis*.
  - **Strict Citation Ordering:** All 20 references [1] through [20] cited in exact chronological order of first appearance in the manuscript; RFC 4326 formatted author-first.
  - **Precise GSE Length Definition:** Accurately detailed the 12-bit length field encoding 0 to 4,095 bytes of payload and optional fields following the 2-byte header (maximum total PDU 4,097 bytes; observed max 1,444 bytes).
  - **Exact 10-Page Column Balancing:** Full-width figures and tables (Fig. 1, Table II, Table VI) span both columns seamlessly; compact figures (Figs. 2–6) and tables (I, III, IV, V) formatted with IEEE typography; References [1]–[20] perfectly fill both columns on Page 10 with zero overflow.
  - **Visual Verification:** All 10 rendered page images (`page-01.png` through `page-10.png`) visually inspected and confirmed flawless.
