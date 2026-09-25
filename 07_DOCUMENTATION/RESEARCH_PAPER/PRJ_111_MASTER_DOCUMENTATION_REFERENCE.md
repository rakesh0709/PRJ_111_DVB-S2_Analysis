# PRJ_111: MASTER DOCUMENTATION REFERENCE
## Final Verified F1–F7 Implementation Evidence Base
**Project Title:** Development of a Software Application for Analysis and Processing of DVB-S2 Receiver Output Stream  
**Project ID:** PRJ_111  
**Document Classification:** Master Technical Reference & Implementation Evidence Base  
**Target Milestone:** Review-2 (~50%+ Functional Prototype Milestone, 26 September 2026)  
**Creation Date:** 19 September 2026  
**System Status:** Full Stack Implemented (Features F1–F7 + Review-2 Interactive HTML5/CSS SPA Dashboard), Audited, Reconciled, and Frozen (240/240 Tests Passing)  
**Notice:** *This document serves as the single authoritative source of truth for preparing Review-2 documentation, the final project thesis, research paper drafts, presentation slide decks (PPT), viva defense notes, and technical demonstration scripts. It preserves the Review-1 historical baseline without rewriting history while establishing verified implementation evidence.*

---

## Table of Contents
1. [Section 1 — Project Identity](#section-1--project-identity)
2. [Section 2 — Review-1 Baseline](#section-2--review-1-baseline)
3. [Section 3 — Review-1 → Review-2 Evolution](#section-3--review-1--review-2-evolution)
4. [Section 4 — Final System Architecture](#section-4--final-system-architecture)
5. [Section 5 — Input Format Implementation](#section-5--input-format-implementation)
6. [Section 6 — Unified Feature Extraction](#section-6--unified-feature-extraction)
7. [Section 7 — Feature F1: Stream Health Analysis](#section-7--feature-f1-stream-health-analysis)
8. [Section 8 — Feature F2: AI-based Anomaly Detection](#section-8--feature-f2-ai-based-anomaly-detection)
9. [Section 9 — Feature F3: Pattern Detection](#section-9--feature-f3-pattern-detection)
10. [Section 10 — Feature F4: Timeline / Activity Visualization](#section-10--feature-f4-timeline--activity-visualization)
11. [Section 11 — Feature F5: Anomaly Explanation Engine](#section-11--feature-f5-anomaly-explanation-engine)
12. [Section 12 — Feature F6: Stream Comparison Engine](#section-12--feature-f6-stream-comparison-engine)
13. [Section 13 — Feature F7: Automatic Analysis Report Generator](#section-13--feature-f7-automatic-analysis-report-generator)
14. [Section 14 — Final Engineering Audit & Freeze](#section-14--final-engineering-audit--freeze)
15. [Section 15 — Bugs / Issues Discovered and Resolved](#section-15--bugs--issues-discovered-and-resolved)
16. [Section 16 — Numerical Reconciliation & Ground Truth Ledger](#section-16--numerical-reconciliation--ground-truth-ledger)
17. [Section 17 — Datasets & Data Strategy](#section-17--datasets--data-strategy)
18. [Section 18 — Experiments & Empirical Validation Registry](#section-18--experiments--empirical-validation-registry)
19. [Section 19 — Comprehensive Testing Evidence](#section-19--comprehensive-testing-evidence)
20. [Section 20 — Safety, Epistemic Boundaries & Terminology Discipline](#section-20--safety-epistemic-boundaries--terminology-discipline)
21. [Section 21 — Current Verified Limitations](#section-21--current-verified-limitations)
22. [Section 22 — Future Work Roadmap](#section-22--future-work-roadmap)
23. [Section 23 — Research Paper Drafting Material](#section-23--research-paper-drafting-material)
24. [Section 24 — Review-2 Presentation & Defense Material](#section-24--review-2-presentation--defense-material)
25. [Section 25 — Evidence Mapping Matrix (Docs / PPT / Viva)](#section-25--evidence-mapping-matrix-docs--ppt--viva)
26. [Section 26 — Academically Safe Claims We Can Defend](#section-26--academically-safe-claims-we-can-defend)
27. [Section 27 — Prohibited & Unsupported Claims We Must Reject](#section-27--prohibited--unsupported-claims-we-must-reject)
28. [Section 28 — Comprehensive File, Code & Artifact Index](#section-28--comprehensive-file-code--artifact-index)
29. [Section 29 — Documentation Trigger Points (F1–F7 & System)](#section-29--documentation-trigger-points-f1f7--system)
30. [Section 30 — Evidence Quality Classification Matrix](#section-30--evidence-quality-classification-matrix)

---

## Section 1 — Project Identity

- **Project Identifier:** PRJ_111
- **Full Academic Project Title:** Development of a Software Application for Analysis and Processing of DVB-S2 Receiver Output Stream
- **Degree & Curriculum Track:** Bachelor of Technology (B.Tech) in Computer Science and Engineering (CSE), Mini Project Curriculum.
- **Academic Context:** Undergrad Capstone Mini Project focusing on digital satellite communications, telecommunications software engineering, automated protocol analysis, and machine learning application.
- **Project Team Members & Assigned Responsibilities (Preserved from Review-1 Baseline):**
  - **Rakeshwar:** Core Development & Technical Lead
    - *Primary Responsibilities:* Backend architecture, frontend development, AI/ML model integration, data processing, stream parsing algorithms, feature extraction engineering, system integration, and technical implementation.
  - **Samad:** Testing, Validation & Documentation Lead
    - *Primary Responsibilities:* Verification and testing lead, literature review, technical documentation authoring, experimental validation, report preparation, and supporting development activities.
  - **Vengal Rao:** Frontend, Visualization & Development
    - *Primary Responsibilities:* Frontend user interface development, interactive data visualization, dashboard components, presentation slide authoring, and supporting development activities.
- **Review-1 Milestone Checkpoint:** 29 August 2026 (11:00 AM – 2:00 PM | Total Marks: 20). Phase 1 foundation and early Phase 2 parser design checkpoint.
- **Review-2 Target Checkpoint:** 26 September 2026 (~50%+ Functional Prototype Milestone).
- **Current Technical State:** Full system implementation across both backend and frontend is 100% completed, verified, and frozen. Backend Features F1 through F7 are fully implemented and verified across 11 test modules (207 passing tests), reconciled against 5 real-data validation experiments, and audited for epistemic safety. The frontend is implemented as a lightweight, zero-dependency interactive Single-Page Application (SPA) using HTML5, vanilla CSS3, and ES6 JavaScript with offline vendored Chart.js (v4.4.x) in `05_CODE/dvbs2_analyzer/frontend/static/`, served directly by the Python HTTP server on port 8080 (`run_frontend.py`), integrated via 33 automated HTTP/API integration tests, achieving 240/240 tests passing overall (0 failures, 0 errors).

---

## Section 2 — Review-1 Baseline

At Review-1 (29 August 2026), the project was formally presented at a conceptual, architectural, and early design stage. In accordance with strict academic integrity, this baseline is recorded as it existed in `PRJ_111_Review1_Documentation.docx`:

### 2.1 Problem Statement (Review-1)
DVB-S2 receiver output is available in multiple formats (Baseband Frames, Generic Stream Encapsulation, and MPEG Transport Stream), and there is a critical need for a unified software application capable of analyzing and processing this output to determine stream health, detect anomalies and patterns, and present results in an interpretable form. Existing tools tend to focus on narrow, isolated aspects (manual packet inspection, physical RF-level signal analysis, or generic network intrusion detection) rather than providing an integrated analysis workflow across all three native DVB-S2 receiver-output formats.

### 2.2 Objectives (Review-1)
1. Analyze DVB-S2 receiver output streams across BBFrame, GSE, and TS formats.
2. Process and parse the three input formats to extract structural and content information.
3. Extract meaningful stream-level features relevant to stream health and transmission behavior.
4. Identify stream health characteristics and support anomaly/pattern detection (Features 1–3).
5. Present analysis results—including timelines, diagnostic explanations, stream comparisons, and automated executive reports—through an understandable application interface (Features 4–7).

### 2.3 Existing System & Engineering Gap (Review-1)
Existing commercial and research tooling was surveyed across three categories:
- *Protocol / Packet Inspection Tools (e.g., Wireshark dissectors):* Provide manual inspection of individual packets and headers, but lack automated health scoring, AI-based anomaly detection, continuous timeline tracking, and executive report compilation.
- *Signal-Level RF Research (RFI & Modulation Classification):* Focuses on raw physical-layer I/Q samples, RF carrier properties, and modulation recognition (QPSK/8PSK), but operates below the de-encapsulated digital stream layer.
- *Generic Network Traffic Anomaly Detection:* Applies machine learning to IP networks, but is unsuited for DVB-S2 native link-layer framing structures (BBHeaders, GSE fragmentation, MPEG-TS PIDs).
- *The Engineering Gap:* No existing open-source or unified tool integrates multi-format DVB-S2 post-demodulation parsing, standardized feature extraction, machine learning anomaly detection, diagnostic attribution, multi-stream differential comparison, and automated multi-format reporting in a cohesive software pipeline.

### 2.4 Scope (Review-1)
- **In Scope:** Post-demodulation digital receiver output processing for MPEG-TS, GSE, and BBFrame; execution of the 7 proposed features; utilization of multiple complementary real-world and reference datasets.
- **Out of Scope (Phase 1/2):** Live physical receiver hardware integration (SDR hardware tuners); cloud infrastructure deployment; proprietary RF-layer diagnostic instrumentation.

### 2.5 Architectural Concept (Review-1)
The foundational principle established at Review-1 is that **Baseband Frames (BBFrame), Generic Stream Encapsulation (GSE), and MPEG Transport Stream (TS) are alternative receiver-output input formats**. They do **not** form a mandatory sequential conversion pipeline (`BBFrame → GSE → TS`). The application accepts whichever format is emitted by the receiver/demodulator or test file.

### 2.6 Dataset Strategy & Folder Structure (Review-1)
Due to the absence of a single public dataset covering all aspects, a five-directory raw data taxonomy was established:
- `01_BBFRAME_GSE/`: Baseband frame and GSE Wireshark capture reference (`dvb-s2_bb_example.pcap`).
- `02_GSE/`: Generic stream encapsulation sample (`GSExtract/sample.ts`).
- `03_TS/`: Real-world satellite transport streams (`DVBS2_toolkit/sample.ts`, `Astra_19.2E_France/`, `Astra_19.2E_Spain/`).
- `04_RFI_AI/`: Supporting signal-level reference archives for AI feature exploration (`Modulation Recognition.zip`, `RFI classification.zip`).
- `05_REAL_DVB_S2/`: Real-world satellite capture containing simultaneous TS and IP traffic (`GRCon22_Blockstream/blockstream.ts`, `ip_packets.pcap`).

### 2.7 Seven Proposed Target Features (Review-1 Status: PLANNED / DESIGN)
1. *Stream Health Analysis:* Extract health-related integrity metrics from parsed streams. Status: Planned.
2. *AI-based Anomaly Detection:* Unsupervised model to flag abnormal stream behavior. Status: Planned.
3. *Pattern Detection:* Identify recurring structural patterns, PID shares, and protocol distributions. Status: Planned.
4. *Timeline / Activity Visualization:* Aggregate stream metrics and events across a sequential axis. Status: Planned.
5. *Anomaly Explanation:* Provide human-interpretable contributing factors for anomalies. Status: Planned.
6. *Stream Comparison:* Differential quantitative comparison between two streams. Status: Planned.
7. *Automatic Analysis Report:* Consolidated multi-format diagnostic report. Status: Planned.

### 2.8 Review-1 Lifecycle State
- **Established / Completed:** Problem definition, scope, core concept, 7 target features defined, dataset strategy established, folder structure created, literature review direction set, initial architecture diagram created.
- **Ongoing:** Dataset collection/inspection, parser design, technical documentation.
- **Planned:** Parser implementation, feature extraction, AI/ML model development, analytics engine, visualization dashboard, reporting engine, testing suite.

---

## Section 3 — Review-1 → Review-2 Evolution

The following registry documents the exact technical progression from Review-1 conceptual planning to the Review-2 frozen implementation:

| Component / Layer | Review-1 Planned State | Implementation Path (Post Review-1) | Validation Performed | Issues Discovered & Corrected | Final Verified Status (Review-2) |
|---|---|---|---|---|---|
| **Stream Ingestion & Dispatch** | Conceptual input block accepting 3 formats | Implemented `StreamHandler` with multi-tier magic byte & heuristic sniffing | Unit tests for auto-detection and format enforcement | Handled ambiguous file extensions (e.g. `.ts` containing GSE packets) | **Complete & Audited** (14 dedicated tests passing) |
| **MPEG-TS Parser** | Ongoing architectural design | Implemented `TSParser` reading 188B packets, tracking sync loss, PUSI, AFC, CC, TEI, and PIDs | Verified against 10,000 pkts of `sample.ts` and `blockstream.ts` | Corrupted packet resynchronization edge cases addressed | **Complete & Audited** (20 dedicated tests passing) |
| **GSE Parser** | Ongoing architectural design | Implemented `GSEParser` decoding variable PDUs, S/E fragmentation flags, LT types, and Protocol IDs | Verified against `01_RAW_DATA/02_GSE/GSExtract/sample.ts` (14 decoded PDUs) | Handled partial/truncated PDUs gracefully without parser crash | **Complete & Audited** (18 dedicated tests passing) |
| **BBFrame Parser** | Ongoing architectural design | Implemented `BBFrameParser` decoding 10B BBHeaders, MATYPE, UPL, DFL, and table-driven CRC-8 | Verified against 4,309 frames in `dvb-s2_bb_example.pcap` | Resolved PCAP link-layer wrapper stripping to access raw BBFrames | **Complete & Audited** (23 dedicated tests passing) |
| **Unified Feature Extraction** | Planned concept | Built `FeatureExtractor` generating `CommonMetrics` and format-specific telemetry | Verified mathematical determinism across all formats | Prevented cross-format flattening; native metrics preserved | **Complete & Audited** (10 dedicated tests passing) |
| **F1: Stream Health** | Planned feature | Built `HealthAnalyzer` evaluating Priority-1 indicators and scoring $[0, 100]$ | Tested on clean and synthetic degraded streams | Sanitized speculative physical-layer RF/FEC claims | **Complete & Audited** (12 dedicated tests passing) |
| **F2: AI Anomaly Detection** | Planned AI module (LSTM/Bi-LSTM cited in lit) | Selected & calibrated `IsolationForest` ($c=0.05$) with configurable format-specific windowing and sigmoid normalization | Tested on real datasets and controlled synthetic perturbations | Calibrated threshold to $0.50$; handled baseline edge cases | **Complete & Calibrated** (16 dedicated tests passing) |
| **F3: Pattern Detection** | Planned feature | Built `PatternDetector` tracking dominant PIDs, GSE protocols, modal DFL, and Shannon entropy | Tested across all 3 formats on real data | Fixed false state transitions on minor PID fluctuations | **Complete & Audited** (20 dedicated tests passing) |
| **F4: Timeline Visualization** | Planned visualization | Built `TimelineGenerator` tracking metrics over physical offsets & interactive HTML dashboards | Tested time-series extraction and event mapping | Added dynamic threshold propagation from `TimelineConfig` | **Complete & Audited** (18 dedicated tests passing) |
| **F5: Anomaly Explanation** | Planned feature | Built `AnomalyExplanationEngine` computing bounded signed Z-scores and component attributions | Tested against real anomalies across all formats | Reconciled BBFrame anomaly window count (5 windows); enforced signed $Z$ | **Complete & Audited** (21 dedicated tests passing) |
| **F6: Stream Comparison** | Planned feature | Built `StreamComparisonEngine` with semantic cross-format guards and significance thresholds | Validated on TS halves, degradation, and cross-format | Reconciled significance threshold hierarchy; 9 metrics barred cross-format | **Complete & Audited** (10 dedicated tests passing) |
| **F7: Automatic Reporting** | Planned report generator | Built `AutomaticReportGenerator` rendering JSON, Markdown, ASCII text, and HTML5 reports | Validated across 5 real-data experiment tracks (20 reports) | Fixed BBFrame modal DFL key extraction bug (`modal_dfl_bits`) | **Complete & Audited** (25 dedicated tests passing) |
| **Automated Test Suite** | Planned testing strategy (0 tests executed) | Developed comprehensive `unittest` test suite covering all layers | Executed regression runs continuously during development | Resolved all edge cases and assertions | **207 / 207 Passing Tests** (0 failures, 0 errors) |

---

## Section 4 — Final System Architecture

### 4.1 Foundational Architecture Principle
Baseband Frames (BBFrame), Generic Stream Encapsulation (GSE), and MPEG Transport Stream (TS) are **alternative input formats**. The system does not enforce or expect a sequential transformation (`BBFrame → GSE → TS`). Each stream is ingested natively, dispatched to its dedicated parser, and transformed into unified features.

### 4.2 End-to-End Architectural Pipeline Flow

```
                      DVB-S2 Receiver Output Stream
              (MPEG-TS .ts / GSE .ts,.pcap / BBFrame .pcap,.bin)
                                      │
                                      ▼
                        ┌───────────────────────────┐
                        │       StreamHandler       │
                        │ (Header Sniffing/Dispatch)│
                        └─────────────┬─────────────┘
                                      │
         ┌────────────────────────────┼────────────────────────────┐
         ▼                            ▼                            ▼
┌──────────────────┐         ┌──────────────────┐         ┌──────────────────┐
│     TSParser     │         │    GSEParser     │         │  BBFrameParser   │
│  - 188B Packets  │         │  - Variable PDUs │         │  - 10B BBHeader  │
│  - Sync Byte 0x47│         │  - S/E Frag Flags│         │  - MATYPE/UPL/DFL│
│  - PID / CC / TEI│         │  - Protocol IDs  │         │  - Table CRC-8   │
└────────┬─────────┘         └────────┬─────────┘         └────────┬─────────┘
         │                            │                            │
         └────────────────────────────┼────────────────────────────┘
                                      ▼
                        ┌───────────────────────────┐
                        │ FeatureExtractor (Unified)│
                        │ - CommonMetrics           │
                        │ - FormatSpecificMetrics   │
                        └─────────────┬─────────────┘
                                      │
         ┌────────────────────────────┴────────────────────────────┐
         ▼                                                         ▼
┌──────────────────┐                                     ┌──────────────────┐
│    Feature F1    │                                     │    Feature F3    │
│  Stream Health   │                                     │ Pattern Detection│
│  - Priority-1    │                                     │ - Dominant PIDs  │
│  - Score [0-100] │                                     │ - Modal DFL / ISI│
└────────┬─────────┘                                     │ - Shannon Entropy│
         │                                               └────────┬─────────┘
         ├────────────────────────────┬────────────────────────────┤
         │                            ▼                            │
         │                  ┌──────────────────┐                   │
         │                  │    Feature F2    │                   │
         │                  │ Anomaly Detection│                   │
         │                  │ - IsolationForest│                   │
         │                  │ - Sigmoid [0-1]  │                   │
         │                  └─────────┬────────┘                   │
         │                            │                            │
         ▼                            ▼                            ▼
┌──────────────────────────────────────────────────────────────────────────┐
│                         Feature F4: StreamTimeline                       │
│ - Window Slicing over Physical Byte Offsets & Sequential Packet Indices  │
│ - Time-Series Extraction (Health, Anomaly Score, Payload Density)        │
│ - Event Mapping (Health Drops, Anomaly Peaks, Structural Transitions)    │
└─────────────────────────────────────┬────────────────────────────────────┘
                                      │
                                      ▼
┌──────────────────────────────────────────────────────────────────────────┐
│                   Feature F5: Anomaly Explanation Engine                 │
│ - Feature Deviation Analysis via Signed & Bounded Z-Scores               │
│ - Subsystem / Component Attribution (Dominant PID, Framing, CRC)         │
│ - Ranked Diagnostic Hypothesis Generation with Epistemic Guards          │
└─────────────────────────────────────┬────────────────────────────────────┘
                                      │
         ┌────────────────────────────┴────────────────────────────┐
         ▼                                                         ▼
┌─────────────────────────────────────┐   ┌────────────────────────────────┐
│      Feature F6: Stream Comparison  │   │  Feature F7: Automatic Report  │
│ - Dual-Stream Differential Analysis │   │ - Tripartite Register Synthesis│
│ - Semantic Cross-Format Audit       │──▶│ - Multi-Format Renderers       │
│ - Progress Decile Alignment         │   │   (JSON, Markdown, TXT, HTML)  │
│ - Unified Significance Thresholds   │   │ - Mandatory Domain Guard       │
└─────────────────────────────────────┘   └────────────────┬───────────────┘
                                                           │
                                                           ▼
                                          ┌────────────────────────────────┐
                                          │ Application & Presentation     │
                                          │ - Standalone HTML Dashboards   │
                                          │ - Review-2 Web UI (Scheduled)  │
                                          └────────────────────────────────┘
```

### 4.3 Architecture Layer Separation
1. **Ingestion & Parsing Layer (`dvbs2_analyzer/ingestion/`, `dvbs2_analyzer/parsers/`):** Handles binary stream I/O, format auto-detection, packet synchronization, frame header parsing, syntactic validation, and raw error counting.
2. **Feature Extraction Layer (`dvbs2_analyzer/features/`):** Transforms raw parser statistics into standardized dataclasses (`CommonMetrics`, `FormatSpecificMetrics`, `UnifiedStreamFeatureSet`).
3. **Core Analytical Layer (`dvbs2_analyzer/analysis/`):** Houses F1 (Health), F2 (Isolation Forest), and F3 (Patterns). Executes statistical modeling without external system dependencies.
4. **Timeline & Diagnostic Layer (`analysis/timeline.py`, `analysis/explanation.py`):** Correlates analytical outputs over physical spatial windows and generates diagnostic attributions for detected outliers.
5. **Comparative & Executive Reporting Layer (`analysis/comparison.py`, `analysis/report.py`):** Performs multi-stream differential auditing and multi-format report synthesis.
6. **Presentation Layer (`visualization/dashboard.py`, `dvbs2_analyzer/frontend/`):** Renders interactive standalone HTML dashboards and provides the zero-dependency Review-2 HTML5/CSS SPA dashboard for live demonstrations.

### 4.4 Application & Dashboard Architecture (HTML5 + Vanilla CSS + Python REST Backend)

The Review-2 frontend is implemented as a zero-dependency, high-performance Single-Page Application (SPA) located at `05_CODE/dvbs2_analyzer/frontend/static/`, served directly by the Python HTTP server (`run_frontend.py`) on port 8080.

```
BROWSER (OPERATOR DASHBOARD)
   │
   ▼ HTTP (PORT 8080)
PYTHON ANALYSIS BACKEND (`dvbs2_analyzer.frontend.server`)
   ├── Static File Server (`05_CODE/dvbs2_analyzer/frontend/static/`)
   │   ├── index.html (Responsive HTML5 Single-Page Application)
   │   ├── styles.css (Pure Vanilla CSS3, zero external CSS frameworks)
   │   ├── app.js (Native ES6 JavaScript dashboard controller)
   │   └── vendor/chart.umd.min.js (Offline vendored Chart.js v4.4.x)
   ├── ThreadingHTTPServer (Standard Library HTTP server on port 8080)
   ├── AnalysisCoordinator (Thin integration layer calling frozen F1–F7 engines)
   └── REST API Endpoints:
       ├── GET  /api/status   --> Real-time backend status & test suite verification
       ├── GET  /api/presets  --> Authoritative broadcast preset datasets
       ├── POST /api/upload   --> Raw stream binary chunk buffer
       ├── POST /api/analyze  --> Single-stream F1–F5 + F7 pipeline execution
       ├── POST /api/compare  --> Dual-stream F6 differential comparison & semantic shield
       └── GET  /api/export   --> Direct report download (.md, .html, .json, .txt)
```

### 4.5 Operational Model & Standalone Verification
1. **Interactive Review-2 Dashboard:** Operating directly on `http://127.0.0.1:8080`, the SPA provides separate dedicated tabs for each feature: Dashboard, Anomaly Analysis (F2+F5), Timeline (F4), Comparison (F6), and Automatic Report (F7).
2. **Zero External Dependencies:** Built with pure HTML5, vanilla CSS3, and ES6 JavaScript, with Chart.js vendored locally in `static/vendor/chart.umd.min.js`, ensuring 100% offline air-gapped reproducibility with zero CDN reliance.

---

## Section 5 — Input Format Implementation

### 5.1 MPEG-2 Transport Stream (MPEG-TS) Implementation
- **Governing Standard:** ISO/IEC 13818-1 / ETSI EN 300 468.
- **Physical Framing:** Fixed 188-byte packet length.
- **Header Structure (4 bytes, 32 bits):**
  - *Sync Byte (8 bits):* Must equal `0x47` (ASCII `'G'`).
  - *Transport Error Indicator (TEI, 1 bit):* Set by receiver demodulator when uncorrectable baseband errors occur.
  - *Payload Unit Start Indicator (PUSI, 1 bit):* Signals commencement of PES packets or PSI/SI sections.
  - *Transport Priority (1 bit):* Priority marking for downstream demultiplexers.
  - *Packet Identifier (PID, 13 bits):* Identifies elementary stream or control table (`0x0000` to `0x1FFF`).
  - *Transport Scrambling Control (TSC, 2 bits):* `00` (unscrambled), `01` (reserved), `10`/`11` (scrambled).
  - *Adaptation Field Control (AFC, 2 bits):* `01` (payload only), `10` (adaptation field only), `11` (adaptation field followed by payload), `00` (reserved/invalid).
  - *Continuity Counter (CC, 4 bits):* Modulo-16 sequence counter incrementing per PID for payload-bearing packets.
- **Parser Logic & Error Handling (`parsers/ts_parser.py`):**
  - Re-synchronization: If sync byte `0x47` is lost, the parser scans sequentially byte-by-byte for a valid `0x47` followed by another `0x47` exactly 188 bytes later.
  - Discontinuity Detection: Tracks expected CC per PID. Accounts for duplicate packets (same CC with adaptation field), empty null packets (`PID 0x1FFF`), and discontinuities flagged in adaptation headers.
- **Unit Test Coverage:** 20 dedicated unit tests in `tests/test_ts_parser.py`.
- **Real-Data Validation:** Validated against `sample.ts` (18,176 packets) and `blockstream.ts` (over-the-air capture).

### 5.2 Generic Stream Encapsulation (GSE) Implementation
- **Governing Standard:** ETSI TS 102 606-1.
- **Physical Framing:** Variable-length Protocol Data Units (PDUs) designed for efficient IP and network layer packet transport over DVB-S2 baseband links.
- **Header Structure:**
  - *Start/End Flags (S, E, 2 bits):* `11` (unfragmented PDU), `10` (first fragment), `00` (intermediate fragment), `01` (last fragment).
  - *Label Type (LT, 2 bits):* `00` (6-byte MAC address), `01` (3-byte address), `10` (no label / broadcast), `11` (reserved).
  - *GSE Length (12 bits):* Total length of GSE PDU excluding the first 2 bytes (maximum 4095 bytes).
  - *Protocol Type (16 bits):* EtherType indicating encapsulated network protocol (e.g., `0x0800` IPv4, `0x86DD` IPv6, `0x00A1` GSE Extension Header NPA).
  - *Optional CRC-32 (32 bits):* Mandatory on end fragments (`E=1`) and unfragmented PDUs when specified.
- **Parser Logic & Edge Handling (`parsers/gse_parser.py`):**
  - Decodes PDU structures embedded in binary files or encapsulated in PCAP frames.
  - Detects padding bytes (`0x00` or `0xFF`) at the boundary of carrying containers.
  - Handles truncated PDUs at stream boundaries without throwing unhandled exceptions.
- **Unit Test Coverage:** 18 dedicated unit tests in `tests/test_gse_parser.py`.
- **Real-Data Validation:** Validated against `01_RAW_DATA/02_GSE/GSExtract/sample.ts` (9,324 bytes). Note on representation: `sample.ts` is stored in `.ts` container format from which the GSE parser de-encapsulates GSE PDUs; PDU-level analysis therefore reports the decoded PDU count (14 valid PDUs) rather than the carrier packet count. Historical mentions of 458 packets were draft errors, as a 9.3 KB file contains at most ~49 188-byte blocks.

### 5.3 DVB-S2 Baseband Frame (BBFrame) Implementation
- **Governing Standard:** ETSI EN 302 307-1 (Clause 5.1).
- **Physical Framing:** Fixed-size physical containers (Normal FECFRAME: 64,800 bits; Short FECFRAME: 16,200 bits) carrying a 10-byte Baseband Header (`BBHeader`) followed by a variable Data Field (`DFL`).
- **BBHeader Structure (10 bytes, 80 bits):**
  - *MATYPE-1 (1 byte):*
    - TS/GS field (2 bits): Transport Stream (`11`), Generic Packetized (`00`), Generic Continuous (`01`), Reserved (`10`).
    - SIS/MIS field (1 bit): Single Input Stream (`1`), Multiple Input Stream (`0`).
    - CCM/ACM field (1 bit): Constant Coding & Modulation (`1`), Adaptive Coding & Modulation (`0`).
    - ISSYI (1 bit): Input Stream Synchronization Indicator active (`1`).
    - NPD (1 bit): Null Packet Deletion active (`1`).
    - RO (Roll-off factor, 2 bits): `00` ($\alpha = 0.35$), `01` ($\alpha = 0.25$), `10` ($\alpha = 0.20$), `11` (reserved).
  - *MATYPE-2 (1 byte):* Input Stream Identifier (ISI) for MIS mode; reserved/zero for SIS mode.
  - *UPL (User Packet Length, 2 bytes, 16 bits):* Bit length of user packet (e.g., 1504 bits for 188-byte MPEG-TS).
  - *DFL (Data Field Length, 2 bytes, 16 bits):* Bit length of payload data field ($DFL \le K_{bch} - 80$).
  - *SYNC (1 byte):* Copy of user packet sync byte (e.g., `0x47` for TS).
  - *SYNCD (2 bytes, 16 bits):* Distance in bits from start of Data Field to first user packet sync.
  - *CRC-8 (1 byte):* Error detection code over first 9 bytes of BBHeader.
- **Table-Driven CRC-8 Implementation (`parsers/bbframe_parser.py`):**
  - Generator polynomial: $g(x) = x^8 + x^7 + x^4 + x^3 + x^2 + 1$ (`0x1D5` / normal representation `0xD5`).
  - Precomputed 256-entry lookup table (`CRC8_TABLE`) executes bitwise verification in constant time $\mathcal{O}(1)$ per byte.
- **Unit Test Coverage:** 23 dedicated unit tests in `tests/test_bbframe_parser.py`.
- **Real-Data Validation:** Validated against `dvb-s2_bb_example.pcap` (4,309 baseband frames, 100% CRC-8 validity).

---

## Section 6 — Unified Feature Extraction

### 6.1 Architectural Rationale: Native Semantics Preservation
A central engineering decision in PRJ_111 is **avoiding artificial flattening**. Forcing MPEG-TS, GSE, and BBFrame into an identical schema destroys critical format-specific telemetry (such as PID distributions, GSE fragmentation flags, or BBHeader roll-off factors). Therefore, the feature layer exposes:
1. `CommonMetrics`: Universally meaningful physical abstractions across all stream formats.
2. `FormatSpecificMetrics`: High-fidelity telemetry native to each respective standard.
3. `UnifiedStreamFeatureSet`: A composite dataclass binding common and native metrics.

### 6.2 Data Structures (`dvbs2_analyzer/features/extractor.py`)

#### `CommonMetrics`
```python
@dataclass
class CommonMetrics:
    total_units: int               # Count of framing units (packets / PDUs / frames)
    valid_units: int               # Count of syntactically valid units
    invalid_units: int             # Count of corrupted / errored units
    truncated_units: int           # Units cut off at boundary
    integrity_ratio: float         # valid_units / total_units in [0.0, 1.0]
    total_payload_bytes: int       # Total octets of extracted user payload
    mean_payload_bytes: float      # Average payload bytes per framing unit
    payload_ratio: float           # Ratio of payload to total bytes
    error_count: int               # Aggregate format-specific errors
    error_rate: float              # error_count / total_units
    entropy: float                 # Shannon entropy of primary structural multiplex
```

#### `TSSpecificMetrics`
```python
@dataclass
class TSSpecificMetrics:
    sync_loss_count: int           # Occurrences of out-of-sync framing
    tei_count: int                 # Packets with Transport Error Indicator = 1
    cc_error_count: int            # Packets violating Continuity Counter sequence
    null_packet_count: int         # Packets with PID 0x1FFF
    null_packet_ratio: float       # null_packet_count / total_units
    adaptation_count: int          # Packets containing Adaptation Fields
    pusi_count: int                # Packets with Payload Unit Start Indicator = 1
    unique_pids: int               # Count of distinct PIDs observed
    pid_distribution: Dict[int, int] # Frequency map of PID occurrences
    dominant_pid: Optional[int]    # PID with highest packet frequency
    dominant_pid_share: float      # Dominant PID count / total_units
```

#### `GSESpecificMetrics`
```python
@dataclass
class GSESpecificMetrics:
    total_pdus: int                # Total GSE PDUs parsed
    unfragmented_pdus: int         # PDUs with S=1, E=1
    frag_start_pdus: int           # PDUs with S=1, E=0
    frag_cont_pdus: int            # PDUs with S=0, E=0
    frag_end_pdus: int             # PDUs with S=0, E=1
    protocol_distribution: Dict[int, int] # EtherType frequency map
    dominant_protocol: Optional[int]      # Most frequent protocol
    dominant_protocol_share: float       # Share of dominant protocol
    label_type_distribution: Dict[int, int] # LT type frequency map
    extension_header_count: int    # PDUs carrying GSE extension headers
    avg_pdu_length: float          # Average PDU length in octets
    max_pdu_length: int            # Peak PDU length in octets
```

#### `BBFrameSpecificMetrics`
```python
@dataclass
class BBFrameSpecificMetrics:
    total_frames: int              # Total baseband frames parsed
    ts_gs_distribution: Dict[str, int]   # TS vs GS mode counts
    sis_mis_distribution: Dict[str, int] # Single vs Multiple stream counts
    ccm_acm_distribution: Dict[str, int] # Constant vs Adaptive coding counts
    rolloff_distribution: Dict[str, int] # Roll-off factor counts (0.35, 0.25, 0.20)
    issyi_count: int               # Frames with ISSY active
    npd_count: int                 # Frames with Null Packet Deletion active
    modal_dfl_bits: Optional[int]  # Most frequent Data Field Length in bits
    unique_dfl_count: int          # Count of distinct DFL values
    mean_dfl_bits: float           # Average Data Field Length
    dfl_variance: float            # Variance of Data Field Length
    crc_error_count: int           # Frames failing BBHeader CRC-8
```

### 6.3 Feature Extraction Dispatcher Logic
The `FeatureExtractor` inspects incoming `StreamStatistics` and automatically invokes format-specific dispatch methods (`_extract_ts_features`, `_extract_gse_features`, `_extract_bbframe_features`). Shannon entropy is calculated over primary structural keys:
$$H(X) = -\sum_{i=1}^{n} p(x_i) \log_2 p(x_i)$$
Where $p(x_i)$ represents PID shares in MPEG-TS, EtherType shares in GSE, or DFL distributions in BBFrame. Missing metrics for non-applicable formats are explicitly set to neutral sentinel values (`None` or $0.0$) rather than being fabricated.

---

## Section 7 — Feature F1: Stream Health Analysis

### 7.1 Objective & Scope
Feature F1 executes deterministic, rule-based stream integrity assessment. It provides an immediate, transparent quantitative health rating on a scale of $[0, 100]$ based on fundamental framing synchronization and transmission integrity indicators.

### 7.2 Selected Priority-1 Integrity Indicators
To maintain rigorous epistemic discipline, F1 checks are explicitly designated as **selected Priority-1 broadcast stream integrity indicators** inspired by ETSI TR 101 290 principles, rather than claiming formal certification:
- **TS-1 (Sync Lock):** Continuous presence of sync byte `0x47` on 188-byte boundaries.
- **TS-2 (Sync Byte Alignment):** Detection of sync loss intervals or corrupted sync headers.
- **TS-3 (Transport Error Indicator - TEI):** Tracking demodulator-asserted uncorrectable packet flags.
- **TS-4 (Continuity Counter Discontinuity):** Tracking missing, out-of-sequence, or unexpectedly dropped packets per PID.
- **GSE-1 (PDU Syntactic Integrity):** Header validity, length field consistency, and CRC-32 pass rate.
- **BB-1 (BBHeader CRC-8 Verification):** Mathematical verification of the 8-bit header checksum over the first 9 header bytes.

### 7.3 Health Scoring & Classification Algorithm
The health score starts at a baseline of $100.0$ and applies weighted deductions based on detected structural errors:
$$\text{HealthScore} = \max\left(0.0, 100.0 - \sum_{i} w_i \cdot \text{penalty}_i\right)$$
- Deductions:
  - Sync Loss / CRC-8 Error: $-50.0$ per event (catastrophic framing loss).
  - TEI Assertions: $-10.0 \times \text{TEI Rate}$ (demodulator-flagged corruptions).
  - Continuity Counter Discontinuities: $-15.0 \times \text{CC Error Rate}$ (packet sequence drops).
- **Classification Categories:**
  - `HEALTHY`: $\text{Score} \ge 95.0$
  - `DEGRADED`: $70.0 \le \text{Score} < 95.0$
  - `CRITICAL`: $\text{Score} < 70.0$

### 7.4 Real-Data Results & Testing
- `sample.ts` (MPEG-TS): Score = $100.00$ (`HEALTHY`), TEI = $0$, CC Errors = $0$.
- `dvb-s2_bb_example.pcap` (BBFrame): Score = $100.00$ (`HEALTHY`), CRC Errors = $0$.
- `sample.ts` (GSE): Score = $100.00$ (`HEALTHY`), Invalid PDUs = $0$.
- Unit Tests: 12 dedicated tests in `tests/test_health.py`.

---

## Section 8 — Feature F2: AI-based Anomaly Detection

### 8.1 Machine Learning Baseline Selection: Isolation Forest
At Review-1, deep learning architectures (LSTM/Bi-LSTM) were surveyed in the literature. During Phase 2 development, **Isolation Forest** was selected and implemented as the authoritative anomaly detection baseline for the following defensible engineering reasons:
1. *Unsupervised Execution:* Operates without labeled training datasets, directly addressing the Review-1 limitation regarding the scarcity of labeled ground-truth anomaly data.
2. *Linear Computational Complexity:* With $\mathcal{O}(n \log n)$ time complexity, Isolation Forest is highly suitable for windowed telemetry processing over high-rate stream output.
3. *Subsampling & Contamination Control:* Explicit parameterization ($c = 0.05$) enables controlled sensitivity without catastrophic overfitting on small real-world samples.
4. *Algorithmic Isolation Principle:* Anomalies have shorter path lengths in random isolation trees because they require fewer feature splits to separate from nominal clusters:
$$s(x, n) = 2^{-\frac{E(h(x))}{c(n)}}$$
Where $h(x)$ is path length, $E(h(x))$ is average path length across trees, and $c(n)$ is average path length of unsuccessful searches in a Binary Search Tree.

### 8.2 Operational Configuration & Normalization
- **Window Slicing:**
  - *Default Framework Settings (`TimelineConfig`):* `ts_window_size=100` pkts, `gse_window_size=10` PDUs, `bbframe_window_size=50` frames.
  - *Authoritative Review-2 Experiment Configurations (`run_f7_report_experiment.py`):*
    - **MPEG-TS (`sample.ts`):** Window size $w = 200$ packets, producing 91 sequential windows across 18,176 packets (Windows 0–90). (Early exploratory calibration tests also evaluated $w = 100$ packets over 10,000 packets, producing 101 windows).
    - **BBFrame (`dvb-s2_bb_example.pcap`):** Window size $w = 50$ frames, producing 87 sequential windows across 4,309 frames (Windows 0–86).
    - **GSE (`GSExtract/sample.ts`):** Window size $w = 3$ PDUs, producing 5 sequential windows across 14 decoded PDUs (Windows 0–4).
- **Model Hyperparameters:** `n_estimators=100`, `contamination=0.05`, `random_state=42`.
- **Score Normalization:** Raw Isolation Forest decision functions $f(\mathbf{x})$ are mapped into $[0.0, 1.0]$ using a calibrated monotonically decreasing sigmoid:
$$s_{\text{norm}}(\mathbf{x}) = \frac{1}{1 + \exp(k \cdot f(\mathbf{x}))}$$
Where $s_{\text{norm}} \ge 0.50$ designates an anomalous window.
- **Baseline Calibration Architecture:** `AnomalyDetector` implements support for fitting on external reference/golden baselines via `detector.fit(reference_samples)` and serialization via `save()`/`load()`. However, in the **authoritative Review-2 real-data experiments**, external golden reference captures were not used; all reported results were generated using **empirical self-baseline modeling** fitted directly across the analyzed stream's own sequential windows.

### 8.3 Controlled Synthetic Perturbation vs. Real-Data Validation
- *Controlled Perturbation Validation:* Model capability was verified by injecting synthetic corruptions (truncation, CC sequence scrambling, null packet flooding, DFL shifts). The detector flagged 100% of synthetic anomaly injections ($s \ge 0.70$).
- *Real-Data Empirical Observations:*
  - MPEG-TS (`sample.ts`, 91 windows, $w=200$ pkts): 5 anomalous windows (5.49% rate). Anomalous window indices: Windows 1, 2, 12 (multiplex allocation shifts), Window 88 (adaptation field frequency), and Window 90 (final capture termination boundary truncation: 176 packets vs nominal 200). Peak score = `0.8576` (Window 90). (Note: References to Windows 97–100 pertained to the earlier exploratory 10,000-packet slice with $w=100$; the authoritative 18,176-packet stream with $w=200$ contains exactly 91 windows, indices 0–90).
  - BBFrame (`dvb-s2_bb_example.pcap`, 87 windows, $w=50$ frames): 5 anomalous windows (5.75% rate). Anomalous window indices: Window 0 (initiation dispersion), Windows 83–85 (payload volume variations), and Window 86 (final capture termination boundary truncation: 9 frames vs nominal 50). Peak score = `0.7406` (Window 86).
  - GSE (`GSExtract/sample.ts`, 5 windows, $w=3$ PDUs): 1 anomalous window (20.00% rate). Anomalous window index: Window 4 (final capture termination boundary truncation: 2 PDUs vs nominal 3). Peak score = `0.5018` (Window 4).
- **Academic Grounding Rule:** Real-data anomaly counts represent statistical deviations from windowed central tendencies; they must **never** be conflated with physical receiver hardware defects or transmission bit errors.

---

## Section 9 — Feature F3: Pattern Detection

### 9.1 Multi-Format Pattern Detection Methodology
Feature F3 monitors continuous structural dynamics and multiplex distributions across rolling windows:
- **MPEG-TS Pattern Tracking:**
  - *Dominant PID Identification:* Detects the PID carrying the highest packet volume and measures its multiplex share percentage.
  - *Shannon Entropy Stability:* Monitors multiplex dispersion over time. A sharp drop in entropy indicates multiplex collapse or single-PID monopolization.
  - *Null Packet Ratio Dynamics:* Tracks bandwidth stuffing variations.
- **GSE Pattern Tracking:**
  - *Protocol Share Distribution:* Tracks EtherType percentages (IPv4 vs IPv6 vs Extension Headers).
  - *Fragmentation Profiling:* Measures ratio of unfragmented PDUs (`S=1, E=1`) to fragmented bursts.
  - *Label Type Patterns:* Tracks broadcast (`LT=10`) vs addressed traffic shares.
- **BBFrame Pattern Tracking:**
  - *Modal DFL Detection:* Identifies the statistical mode of Data Field Length (e.g., 8,304 bits) and its modal dominance percentage.
  - *Transmission Mode Verification:* Tracks consistency of SIS/MIS, CCM/ACM, and Roll-Off factors across consecutive frames.

### 9.2 Bug Resolution & Calibration
During initial development, slight PID percentage fluctuations in MPEG-TS streams triggered false F3 state-transition events. The state-transition detector was calibrated with an activity threshold filter ($\Delta_{\text{share}} \ge 15.0\%$ required to trigger a state transition), permanently resolving false transition noise.

---

## Section 10 — Feature F4: Timeline / Activity Visualization

### 10.1 Physical Spatial Indexing vs. Artificial Timestamps
In offline captured streams, wall-clock broadcast timestamps are absent or uncalibrated. Feature F4 strictly enforces **physical spatial indexing**:
- Windows and events are indexed by **physical byte offsets** (`start_offset_bytes`, `end_offset_bytes`) and **framing unit indices** (`start_unit_idx`, `end_unit_idx`).
- The system **never** fabricates synthetic wall-clock timestamps or converts byte counts into "throughput (Mbps)" without a verified hardware clock basis.

### 10.2 Data Structures & Series Extraction (`analysis/timeline.py`)
- `TimelinePoint`: Encapsulates spatial window bounds, health score, F2 anomaly score, unit counts, payload bytes, and format-specific telemetry.
- `TimelineEvent`: Discrete event markers (`ANOMALY_START`, `ANOMALY_PEAK`, `ANOMALY_END`, `HEALTH_DEGRADATION`, `STATE_TRANSITION`).
- `TimelineSeries`: Time-series extraction vectors for health scores, anomaly scores, and payload density.
- `StreamTimeline`: Comprehensive serialization container supporting JSON export and HTML rendering.

### 10.3 Dynamic Threshold Propagation
In the final audit, `TimelineConfig` was enhanced to include `f2_anomaly_threshold: float = 0.50`, which dynamically propagates to `AnomalyConfig` across all format generators, eliminating hardcoded detection thresholds.

---

## Section 11 — Feature F5: Anomaly Explanation Engine

### 11.1 Diagnostic Attribution Architecture
Feature F5 serves as the diagnostic explanatory layer for F2. It does **not** make independent anomaly decisions; rather, it inspects windows flagged anomalous by F2 and identifies the mathematical drivers:
1. *Feature Deviation Calculation:* Evaluates window metrics against baseline distributions:
$$\Delta f_j = x_j - \mu_{\text{baseline}, j}$$
2. *Signed & Bounded Z-Score Evaluation:*
$$Z_j = \frac{|x_j - \mu_{\text{baseline}, j}|}{\text{effective\_scale}_j}$$
Where $\text{effective\_scale} = \sigma_{\text{baseline}}$ when $\sigma_{\text{baseline}} \ge 10^{-4}$, and $\text{effective\_scale} = \max(|\mu_{\text{baseline}}| \times 0.05, 0.01)$ as an operational dispersion floor for invariant baseline features. Z-score magnitude is strictly capped at $20.0\,\sigma$ to preserve numerical stability and interpretability, with directional sign tracked explicitly via the `direction` attribute (`"ABOVE_BASELINE"`, `"BELOW_BASELINE"`, `"NORMAL"`).
3. *Subsystem Attribution (`FEATURE_NATIVE_COMPONENT_MAP`):* Maps deviated features to physical subsystems:
   - `dominant_pid` $\rightarrow$ `"MPEG-TS Multiplex / Dominant PID Allocation"`
   - `null_packet_ratio` $\rightarrow$ `"Bandwidth Adaptation / Null Stuffing"`
   - `crc_error_count` $\rightarrow$ `"Baseband Header Integrity / CRC Checksum"`
   - `modal_dfl_bits` $\rightarrow$ `"Frame Sizing / Mode Adaptation"`
4. *Ranked Diagnostic Hypothesis Generation:* Ranks features by $|Z|$ and constructs human-readable, evidence-grounded explanatory sentences.

---

## Section 12 — Feature F6: Stream Comparison Engine

### 12.1 Purpose & Comparative Scope
Feature F6 performs quantitative, multi-tier differential analysis between two analyzed streams (**Stream A** and **Stream B**).

### 12.2 Semantic Audit of Common Metrics (Governing Rule)
A critical engineering achievement of F6 is the **Semantic Audit**. Fields sharing identical names in `CommonMetrics` are **not** assumed to be cross-format comparable:

| Metric Name | Cross-Format Status | Incompatibility Rationale | Same-Format Status |
|---|:---:|---|:---:|
| `total_payload_bytes` | **COMPARABLE** | An octet of user data represents the identical physical quantity regardless of encapsulation. | Fully Compared |
| `integrity_ratio` | **COMPARABLE** | Normalized syntactic validity proportion $[0.0, 1.0]$. | Fully Compared |
| `total_units` | **NOT_COMPARABLE** | 188B TS packet vs variable GSE PDU vs ~7.2KB BBFrame represent physically incompatible units. | Fully Compared |
| `valid_units` | **NOT_COMPARABLE** | Unit boundaries and container capacities differ fundamentally. | Fully Compared |
| `invalid_units` | **NOT_COMPARABLE** | BBFrames and MPEG-TS packets represent substantially different framing capacities; therefore unit-level error counts are not directly comparable across formats. | Fully Compared |
| `truncated_units` | **NOT_COMPARABLE** | Truncation mechanisms are format-specific. | Fully Compared |
| `mean_payload_bytes` | **NOT_COMPARABLE** | Reflects framing container capacity, not transmission throughput. | Fully Compared |
| `payload_ratio` | **NOT_COMPARABLE** | TS measures packet presence; GSE/BBFrame measure byte packing efficiency. | Fully Compared |
| `error_count` | **NOT_COMPARABLE** | Aggregates heterogeneous failure classes (sync vs CRC vs PDU syntax). | Fully Compared |
| `error_rate` | **NOT_COMPARABLE** | Normalized per framing unit; physically incomparable denominators. | Fully Compared |
| `entropy` | **NOT_COMPARABLE** | Measures distinct state spaces (PID multiplex vs EtherType network vs DFL sizing). | Fully Compared |

### 12.3 Mathematically Sound Zero-Baseline Handling
Relative percentage change from a zero baseline ($\frac{B - 0}{0}$) is undefined. F6 strictly enforces:
- $A = 0, B = 0 \implies \Delta_{\text{abs}} = 0.0, \Delta_{\text{rel}} = 0.0\%$, `EQUAL`, `UNCHANGED`, `NEGLIGIBLE`.
- $A = 0, B > 0 \implies \Delta_{\text{abs}} = B, \Delta_{\text{rel}} = \text{None}$, `B_HIGHER`, `INCREASED`, `CRITICAL` (for error counters) / `SUBSTANTIAL`.
- $A > 0, B = 0 \implies \Delta_{\text{abs}} = -A, \Delta_{\text{rel}} = -100.0\%$, `A_HIGHER`, `DECREASED`, `CRITICAL`.

### 12.4 Unified Significance Hierarchy
- **Equality Tolerance:** $|\Delta_{\text{rel}}| \le 0.5\% \implies$ `UNCHANGED`, `NEGLIGIBLE`.
- **`NEGLIGIBLE`:** $|\Delta_{\text{rel}}| < 2.0\%$ (nominal baseline dispersion).
- **`MINOR`:** $2.0\% \le |\Delta_{\text{rel}}| < 10.0\%$ (observable operational divergence).
- **`SUBSTANTIAL`:** $10.0\% \le |\Delta_{\text{rel}}| < 50.0\%$ (significant structural/traffic shift).
- **`CRITICAL`:** $|\Delta_{\text{rel}}| \ge 50.0\%$ (major structural shift or integrity loss).

### 12.5 Window Alignment Without Fabricated Clocks
- *Direct Index Overlap:* Synchronizes windows $i \in [0, \min(N_A, N_B)-1]$. Trailing windows in asymmetric captures are cleanly logged under `unaligned_windows` as capture duration differences, not transmission errors.
- *Normalized Progress Deciles:* Aggregates both streams into 10 uniform progression deciles ($0-10\%, \dots, 90-100\%$) for macro-trajectory comparison.
- *Mandatory Alignment Disclaimer Attached to All Outputs.*

---

## Section 13 — Feature F7: Automatic Analysis Report Generator

### 13.1 Architecture & Non-Duplication Principle
Feature F7 acts as the executive synthesis layer. It directly consumes authoritative outputs from F1 through F6 without re-parsing streams, re-extracting features, re-scoring health, or re-running Isolation Forest inference.

### 13.2 Epistemological Tripartite Register
Every finding generated by F7 is categorized into one of three strict epistemological registers:
1. **`OBSERVED_FACT` (Deterministic Syntactic Telemetry):** Unambiguous facts established deterministically by parsing binary framing structures (e.g., packet counts, byte volumes, CRC passes, dominant PID numbers).
2. **`STATISTICAL_FINDING` (Model & Aggregate Measurements):** Quantitative aggregates, windowed distributions, and algorithmic inferences (e.g., health scores, anomaly rates, Isolation Forest decision scores, Shannon entropy).
3. **`ENGINEERING_INTERPRETATION` (Grounded Contextual Synthesis):** Contextual engineering explanations supported by facts and statistics. Prohibits speculative causal assertions.

### 13.3 Multi-Format Report Renderers
- **Structured JSON (`.json`):** Full programmatic schema with complete finding objects and metadata.
- **GitHub-Flavored Markdown (`.md`):** Executive tables, bulleted findings, and callout blocks.
- **Plain Text (`.txt`):** Formatted ASCII monospace layout safe for CP-1252 Windows console display.
- **Standalone Offline HTML5 (`.html`):** Clean, modern presentation with responsive dark styling and embedded CSS.

---

## Section 14 — Final Engineering Audit & Freeze

### 14.1 Audit Scope & Objective
On 19 September 2026, an exhaustive engineering audit was performed across all 15 pipeline phases (Parsers, Ingestion, Features, F1–F7) to eliminate all inconsistencies, terminology ambiguities, and reporting bugs ahead of Review-2.

### 14.2 Audit Outcomes & Freeze Signoff
- All 11 test modules executed cleanly.
- Two new regression tests were authored to permanently safeguard threshold propagation and BBFrame modal DFL extraction.
- **Final Test Result:** **207 / 207 Passing Tests (0 failures, 0 errors) in 8.710s**.
- All 20 report artifacts under `05_CODE/reports/` were regenerated and verified.
- `01_RAW_DATA/`, `07_DOCUMENTATION/`, and `walkthrough.md` confirmed 100% untouched.
- **Authoritative Freeze Recommendation:** **"Backend F1–F7 audit complete and frozen for Review-2"**.

---

## Section 15 — Bugs / Issues Discovered and Resolved

The following table records every verified engineering issue identified and resolved during project development:

| Ref ID | Issue Classification | Observed Symptom | Underlying Root Cause | Affected Component | Engineering Fix Applied | Regression Test Added | Validation Verification |
|---|---|---|---|---|---|---|---|
| **BUG-01** | Software Bug | False F3 state transitions generated on static MPEG-TS stream | Minor PID percentage shifts crossed zero-tolerance transition threshold | `analysis/patterns.py` | Added activity threshold ($\ge 15\%$ change required) | `test_ts_transition_calibration_no_false_events` | Verified: 0 false transitions on `sample.ts` |
| **BUG-02** | Numerical Bug | Unstable and extreme Z-score values (e.g. $Z = 450.0$) in anomaly explanations | Near-zero variance on static features caused division-by-zero spikes | `analysis/anomaly.py` / `analysis/explanation.py` | Implemented operational dispersion floor for invariant features and capped magnitude at $20.0\,\sigma$ | `test_bounded_z_score_calculation` | Verified: stable Z-scores across all features |
| **EPI-01** | Epistemic Issue | F1 health explanations asserted "physical layer FEC failure" | Speculative interpretation text introduced without physical RF telemetry | `analysis/health.py` | Sanitized strings to report observed digital stream indicators only | `test_health_interpretation_sanitization` | Verified: zero unsupported FEC claims |
| **TRM-01** | Terminology Issue | F5 explanation labeled PID 256 as "Elementary Stream / Video Allocation" | Inferred stream content type from PID number alone without parsed PMT/PAT | `analysis/explanation.py` | Renamed component map to `"MPEG-TS Multiplex / Dominant PID Allocation"` | `test_pid_role_neutrality` | Verified: neutral dominant PID reporting |
| **ARC-01** | Architecture Deficiency | Anomaly threshold hardcoded in timeline generator, ignoring custom config | `TimelineGenerator` instantiated default `AnomalyConfig` internally | `analysis/timeline.py` | Added `f2_anomaly_threshold` to `TimelineConfig` and propagated it | `test_configurable_anomaly_threshold_propagation` | Verified: dynamic threshold propagation |
| **BUG-03** | Integration Bug | F7 executive report for BBFrame output `modal DFL of N/A` | Key mismatch: `timeline.py` saved `modal_dfl_bits`, `report.py` checked `modal_dfl` | `analysis/report.py` | Updated key lookup to check both keys and extract modal share | `test_bbframe_modal_dfl_pattern_synthesis` | Verified: outputs `DFL 8304 bits (92.0% share)` |
| **DOC-01** | Documentation / Reporting Issue | Inconsistent BBFrame anomaly window count (6 reported in text vs 5 in table) | Interim draft counted Window 0 twice in preliminary summary notes | `05_CODE/reports/` (interim notes) | Reconciled count across all documentation to authoritative 5 windows | Verified in `test_anomaly.py` | Authoritative count: 5 anomalous windows |
| **DOC-02** | Documentation / Reporting Issue | BBFrame peak anomaly score reported as `0.8872` in draft ledger vs `0.7406` in runtime | Typographical error in earlier draft documentation ledger text | `PROJECT_DOCUMENTATION_LEDGER.md` | Reconciled documentation to authoritative runtime output `0.7406` | Verified in `test_report.py` & JSON reports | Runtime output: `0.7406` (`0.740568`) |

---

## Section 16 — Numerical Reconciliation & Ground Truth Ledger

The following table establishes the authoritative, verified numerical ground truth across all real-data validation experiments:

| Metric Dimension | Experiment 1: MPEG-TS Single-Stream | Experiment 2: BBFrame Single-Stream | Experiment 3: GSE Single-Stream | Experiment 4: TS Halves Comparison | Experiment 5: Cross-Format Comparison |
|---|---|---|---|---|---|
| **Input File Path** | `01_RAW_DATA/03_TS/DVBS2_toolkit/sample.ts` | `01_RAW_DATA/01_BBFRAME_GSE/dvb-s2_bb_example.pcap` | `01_RAW_DATA/02_GSE/GSExtract/sample.ts` | `sample.ts` First Half vs Second Half | `sample.ts` (TS) vs `dvb-s2_bb_example.pcap` (BB) |
| **Stream Format** | `MPEG_TS` | `BB_FRAME` | `GSE` | `MPEG_TS` vs `MPEG_TS` | `MPEG_TS` vs `BB_FRAME` |
| **Total Units Parsed** | 18,176 packets | 4,309 frames | 14 PDUs | 9,000 pkts vs 9,176 pkts | 18,176 pkts vs 4,309 frames |
| **Syntactic Validity** | 100.0% (18,176 / 18,176) | 100.0% (4,309 / 4,309) | 100.0% (14 / 14) | 100.0% vs 100.0% | 100.0% vs 100.0% |
| **Framing Errors** | 0 sync loss, 0 TEI, 0 CC err | 0 CRC-8 errors | 0 invalid PDUs | 0 errors vs 0 errors | 0 errors vs 0 errors |
| **Extracted Payload** | 3,267,305 bytes | 1,958,826 bytes | 8,764 bytes | 1,626,231 B vs 1,641,074 B | 3,267,305 B vs 1,958,826 B |
| **Payload Delta ($\Delta_{\text{rel}}$)** | N/A (Single Stream) | N/A (Single Stream) | N/A (Single Stream) | $+14,843\text{ B } (+0.91\%)$ `NEGLIGIBLE` | $-1,308,479\text{ B } (-40.05\%)$ `SUBSTANTIAL` |
| **Windowing Scheme** | 91 windows (200 pkts/win) | 87 windows (50 frames/win) | 5 windows (3 PDUs/win) | 45 windows vs 46 windows | 91 windows vs 87 windows |
| **F1 Health Score** | 100.00 / 100 (`HEALTHY`) | 100.00 / 100 (`HEALTHY`) | 100.00 / 100 (`HEALTHY`) | 100.00 vs 100.00 (`UNCHANGED`) | 100.00 vs 100.00 (`COMPARABLE`) |
| **F2 Anomaly Count** | 5 anomalous windows | 5 anomalous windows | 1 anomalous window | 3 windows vs 2 windows | 9 metrics `NOT_COMPARABLE` |
| **F2 Anomaly Rate** | 5.49% | 5.75% | 20.00% | $-1\text{ window } (-33.3\%)$ | Non-comparable anomaly spaces |
| **Peak Anomaly Score** | **0.8576** (Window 90, EOF) | **0.7406** (Window 86, EOF) | **0.5018** (Window 4, EOF) | Window 44 ($0.5891$) vs Win 90 ($0.8576$) | Format-specific anomaly models |
| **Dominant Feature** | PID 256 (98.5% share) | Modal DFL 8304b (92.0% share) | Protocol GSE_EXT_NPA (100%) | PID 256 ($98.5\%$ vs $98.5\%$) | Structural metrics not comparable |
| **Shannon Entropy** | 0.1361 bits | N/A (Continuous DFL) | 0.0000 bits (Single Proto) | $0.1361\text{ b}$ vs $0.1361\text{ b}$ (`EQUAL`) | `NOT_COMPARABLE` cross-format |
| **Overall Classification** | `HEALTHY` / Low Anomaly | `HEALTHY` / Low Anomaly | `HEALTHY` / Baseline Valid | **`MATCH`** | **`PARTIAL_COMPARISON`** |

*Note on Reconciled BBFrame Peak:* The runtime output of Feature F2 on `dvb-s2_bb_example.pcap` produces exactly `0.740568` (rounded to `0.7406`) at final boundary Window 86 (9 frames vs nominal 50). The value `0.8872` was a typographical error in earlier draft documentation and has been reconciled across all artifacts.

---

## Section 17 — Datasets & Data Strategy

### 17.1 Dataset Categorization & Academic Usage Roles
In strict adherence to Review-1 documentation principles, the datasets in `01_RAW_DATA/` are categorized by their specific engineering roles:

| Directory Path | File Identifier | Format Encapsulation | File Size | Academic Role |
|---|---|---|---|---|
| `01_RAW_DATA/01_BBFRAME_GSE/` | `dvb-s2_bb_example.pcap` | PCAP / DVB-S2 Baseband Frame | 2,349,376 bytes (~2.35 MB) | **Real DVB-S2 Validation Dataset** for BBFrame parser, F1–F5 analysis, and F7 reporting (4,309 frames) |
| `01_RAW_DATA/02_GSE/` | `GSExtract/sample.ts` | TS / GSE Encapsulation (Variable PDUs) | 9,324 bytes (~9.3 KB) | **Real Protocol Validation Dataset** for GSE parser, F1–F5 analysis, and F7 reporting (14 decoded PDUs) |
| `01_RAW_DATA/03_TS/` | `DVBS2_toolkit/sample.ts` | MPEG-2 Transport Stream | 3,417,088 bytes (~3.42 MB) | **Real DVB-S2 Validation Dataset** for TS parser, F1–F5 analysis, F6 comparison, and F7 reporting (18,176 pkts) |
| `01_RAW_DATA/03_TS/` | `Astra_19.2E_France/` | MPEG-2 Transport Stream (`.ts`) | `ts1080`: ~436 MB, `ts1120`: ~327 MB | **Supporting Satellite Broadcast Reference** for multi-transponder TS inspection |
| `01_RAW_DATA/03_TS/` | `Astra_19.2E_Spain/` | MPEG-2 Transport Stream (`.ts`) | `astra-10847V`: ~262 MB | **Supporting Satellite Broadcast Reference** for multi-transponder TS inspection |
| `01_RAW_DATA/04_RFI_AI/` | `Modulation Recognition.zip` | Signal I/Q Archives | 367,161,059 bytes (~367 MB) | **Supporting AI Exploration Data** for physical RF signal modulation classification |
| `01_RAW_DATA/04_RFI_AI/` | `RFI classification.zip` | Spectrogram / Signal Data | 367,042,363 bytes (~367 MB) | **Supporting AI Exploration Data** for radio frequency interference profiling |
| `01_RAW_DATA/05_REAL_DVB_S2/` | `GRCon22_Blockstream/blockstream.ts` | Over-the-air DVB-S2 TS | 4,203,304 bytes (~4.20 MB) | **Real DVB-S2 Over-the-Air Reference Capture** for cross-stream verification |
| `01_RAW_DATA/05_REAL_DVB_S2/` | `GRCon22_Blockstream/ip_packets.pcap` | PCAP / Encapsulated IP Traffic | 4,080,213 bytes (~4.08 MB) | **Real DVB-S2 Encapsulated IP Reference** for network payload verification |

---

## Section 18 — Experiments & Empirical Validation Registry

The following registry details the primary experiment runners and validation executions:

1. **`run_f7_report_experiment.py` (Authoritative 5-Track Suite):**
   - *Track 1:* MPEG-TS Single-Stream Analysis (`sample.ts`, 91 windows). Produces `report_mpeg_ts.*` (.json, .md, .txt, .html).
   - *Track 2:* DVB-S2 BBFrame Single-Stream Analysis (`dvb-s2_bb_example.pcap`, 87 windows). Produces `report_bbframe.*`.
   - *Track 3:* GSE Single-Stream Analysis (`01_RAW_DATA/02_GSE/GSExtract/sample.ts`, 5 windows, $w=3$ PDUs). Produces `report_gse.*`.
   - *Track 4:* MPEG-TS Dual-Stream Comparison (First 45 vs Second 46 windows of `sample.ts`). Produces `report_comparison_ts_halves.*`.
   - *Track 5:* Cross-Format Comparison (MPEG-TS 91 windows vs BBFrame 87 windows). Produces `report_comparison_cross_format.*`.
2. **`run_f6_comparison_experiment.py` (Comparative Engine Suite):**
   - Evaluates TS halves, BBFrame halves, synthetic degradation injection, and cross-format semantic barriers. Produces structured comparison JSONs in `05_CODE/reports/`.
3. **`run_f4_visualization_experiment.py` (Timeline & Dashboard Suite):**
   - Extracts time-series metrics over physical offsets and compiles standalone interactive HTML dashboards (`timeline_mpeg_ts.html`, `timeline_bbframe.html`, `timeline_gse.html`).
4. **`run_f5_explanation_experiment.py` (Anomaly Diagnostic Suite):**
   - Evaluates anomaly windows and produces structured diagnostic explanations in `05_CODE/reports/` (`explanations_mpeg_ts.json`, `explanations_bbframe.json`, `explanations_gse.json`).
5. **`run_f2_anomaly_experiment.py` (Isolation Forest Validation Suite):**
   - Executes baseline calibration and controlled synthetic perturbation runs.

---

## Section 19 — Comprehensive Testing Evidence

The PRJ_111 automated test suite executes under Python's native `unittest` framework alongside Node.js frontend verification. All 240 tests execute deterministically without external internet connectivity or GPU dependencies.

### 19.1 Automated Python Test Suite Breakdown (240 / 240 Passing)

| Module Path | Primary Class Under Test | Test Count | Pass Rate | Core Verification Scope |
|---|---|:---:|:---:|---|
| `tests/test_ts_parser.py` | `TSParser` | 20 | 100% (20/20) | 188B packet parsing, sync recovery, PID filtering, CC checking, TEI detection, AFC handling |
| `tests/test_gse_parser.py` | `GSEParser` | 18 | 100% (18/18) | Variable PDU lengths, S/E fragmentation flags, LT types, EtherType extraction, padding handling |
| `tests/test_bbframe_parser.py` | `BBFrameParser` | 23 | 100% (23/23) | 10B BBHeader parsing, MATYPE flags, UPL/DFL consistency, table-driven CRC-8 verification |
| `tests/test_stream_handler.py` | `StreamHandler` | 14 | 100% (14/14) | Multi-tier format auto-detection, stream ingestion dispatch, boundary error handling |
| `tests/test_unified_features.py` | `FeatureExtractor` | 10 | 100% (10/10) | Common metrics extraction, format-specific telemetry mapping, Shannon entropy determinism |
| `tests/test_health.py` | `HealthAnalyzer` | 12 | 100% (12/12) | Priority-1 indicator checks, penalty scoring, health classification, epistemic sanitization |
| `tests/test_anomaly.py` | `AnomalyDetector` | 16 | 100% (16/16) | Isolation Forest calibration, sigmoid score normalization, synthetic perturbation detection |
| `tests/test_patterns.py` | `PatternDetector` | 20 | 100% (20/20) | Dominant PID shares, GSE protocol distribution, modal DFL extraction, state-transition filtering |
| `tests/test_timeline.py` | `TimelineGenerator` | 18 | 100% (18/18) | Physical byte offset tracking, event generation, dashboard HTML rendering, threshold propagation |
| `tests/test_explanation.py` | `AnomalyExplanationEngine`| 21 | 100% (21/21) | Bounded signed Z-score computation, component attribution, epistemic guard enforcement |
| `tests/test_comparison.py` | `StreamComparisonEngine` | 10 | 100% (10/10) | Same-format comparison, cross-format semantic audit, zero-baseline handling, progress deciles |
| `tests/test_report.py` | `AutomaticReportGenerator`| 25 | 100% (25/25) | Tripartite taxonomy, multi-format renderers (JSON/MD/TXT/HTML), domain-safety guard enforcement |
| `tests/test_frontend.py` | `AnalysisCoordinator` & `Server` | 33 | 100% (33/33) | Multi-format REST endpoints, upload chunking, preset loading, report export, security paths |
| **TOTAL** | **Full System Pipeline** | **240** | **100% (240/240)** | **Complete End-to-End Functional Verification (0 Failures, 0 Errors)** |

### 19.2 Frontend Server & Integration Test Suite
In addition to the core pipeline unit tests, the zero-dependency HTML5 / Vanilla CSS / ES6 JavaScript Single-Page Application (SPA) dashboard is verified by an extensive automated Python integration test suite (`tests/test_frontend.py`):
- **REST API Endpoint Contract Verification:** Confirms all endpoints (`/api/status`, `/api/presets`, `/api/analyze`, `/api/compare`, `/api/upload`, `/api/export`) respond with exact schema envelopes and standard HTTP status codes.
- **Multipart Upload & Chunk Processing:** Verifies that raw stream file uploads (MPEG-TS, GSE, BBFrame) are received and parsed without memory leaks or buffer truncation.
- **Static Asset Delivery & Security:** Confirms that `index.html`, `styles.css`, `app.js`, and vendored `chart.umd.min.js` are served with correct MIME types and strict path-traversal security boundaries.
- **Report Export & Preset Integration:** Validates on-the-fly report generation across all 4 output formats (Markdown, HTML, JSON, Plaintext) directly through the HTTP interface.
- **Result:** 33 / 33 Passing (100% Pass Rate).

---

## Section 20 — Safety, Epistemic Boundaries & Terminology Discipline

### 20.1 Physical Demodulation Reality: What the System Can and Cannot Determine
The PRJ_111 software processes **post-demodulator digital receiver output**. It operates exclusively on digital bits, bytes, packets, and frames.

#### What the System CAN Safely Determine:
- Framing synchronization lock and sync byte integrity (`0x47` presence, BBHeader CRC-8).
- Digital packet loss or sequence discontinuity (MPEG-TS Continuity Counter).
- Demodulator-asserted error flags (Transport Error Indicator `TEI = 1`).
- Exact user payload byte volumes and packaging efficiency.
- Statistical multiplex concentration and protocol distributions.
- Statistical deviations from nominal windowed telemetry using Isolation Forest.
- Quantitative differential shifts between two digital streams.

#### What the System CANNOT Determine (Without External RF Telemetry):
- Signal-to-Noise Ratio (SNR) or Modulation Error Ratio (MER).
- Physical Carrier-to-Noise ($C/N$) or link margin.
- Atmospheric attenuation, rain fade, or scintillation.
- Physical satellite transponder anomalies or uplink station hardware failures.
- Receiver demodulator internal LDPC/BCH decoder iteration counts.
- Low-Noise Block downconverter (LNB) local oscillator drift.

### 20.2 Mandatory Domain-Safety Guard (`UNSUPPORTED_INFERENCES_GUARD`)
To prevent misleading diagnostic assertions, all reports and analytical engines incorporate an immutable domain-safety guard that explicitly blocks speculation regarding RF or hardware failures.

### 20.3 Capture-Boundary Neutrality
Anomalous scores occurring at the final window of a capture (e.g. Window 86 in BBFrame, Window 90 in TS) are caused by unit truncation (fewer packets recorded before recording stopped). The system neutrally documents these as **stream capture recording boundaries**, never asserting that the satellite broadcast failed.

### 20.4 Neutral Component Terminology
Without verified Program Specific Information / Service Information (PSI/SI) tables (PAT/PMT), PID numbers are reported neutrally as `"dominant PID [number]"` or `"Dominant PID Allocation"`, strictly barring ungrounded claims like "video stream" or "audio stream".

---

## Section 21 — Current Verified Limitations

1. **Absence of Dedicated PSI/SI Parsing:** Program Association Tables (PAT) and Program Map Tables (PMT) are tracked by PID frequency, but elementary stream descriptors (e.g., AVC/H.264 video, AC-3 audio) are not parsed in the current stage.
2. **Absence of Physical RF Telemetry:** Baseband receiver output streams do not carry physical-layer RF parameters (SNR, MER, AGC levels, constellation diagrams).
3. **Scarcity of Public Labeled Ground Truth:** No publicly available, standardized benchmark exists with frame-by-frame ground-truth fault labels for DVB-S2 anomalies. Anomaly detection is unsupervised.
4. **GSE Sample Size Limitation:** The public GSE validation capture contains 14 PDUs. While sufficient for parsing and structural validation, it does not support extensive statistical dispersion modeling.
5. **Offline Stream Analysis:** Processing executes on recorded stream captures; live software-defined radio (SDR) tuner hardware streaming is not currently integrated.
6. **Frontend Presentation Scope:** Standalone HTML dashboards are implemented; the dedicated Web UI MVP is scheduled next for Review-2 presentation delivery.

---

## Section 22 — Future Work Roadmap

The following roadmap clearly demarcates currently implemented features from future extensions:

| System Dimension | Current Implementation (Review-2 Frozen Backend) | Planned Future Work (Post Review-2 / Final Phase) |
|---|---|---|
| **PSI/SI Table Parsing** | Dominant PID frequency tracking & neutral multiplex share | Full PAT/PMT/SDT/NIT descriptor decoders resolving audio/video codecs |
| **RF / Physical Correlation** | Explicit domain-safety guard blocking physical speculation | Ingestion of external demodulator telemetry logs (SNR/AGC) for cross-layer correlation |
| **Machine Learning Models** | Calibrated Isolation Forest baseline ($c=0.05$, $w=100$) | Semi-supervised Autoencoders and LSTM networks trained on synthetic fault injections |
| **Real-Time Streaming** | High-throughput batch/windowed file processing | Real-time circular buffer streaming integration via GNU Radio or USRP SDRs |
| **User Interface** | Self-contained standalone HTML5 dashboards with embedded CSS | Polished React / Vite web dashboard with real-time stream inspection controls |
| **Cloud Deployment** | Local cross-platform execution (Windows/Linux) | Optional containerized microservice deployment (Docker / FastAPI) |

---

## Section 23 — Research Paper Drafting Material

### 23.1 Proposed Title Candidates
1. *An Integrated Multi-Format Analysis and Anomaly Detection Framework for DVB-S2 Receiver Output Streams*
2. *Unsupervised Anomaly Detection and Diagnostic Explanation in Post-Demodulation Satellite Baseband Streams*
3. *Cross-Format Telemetry Extraction and Stream Health Verification for DVB-S2 Broadcast Networks*

### 23.2 Abstract Outline
- **Context:** DVB-S2 satellite broadcast systems emit digital receiver output in multiple encapsulation formats (MPEG-TS, GSE, BBFrame).
- **Problem:** Existing tools focus on isolated manual protocol inspection or physical-layer RF analysis, lacking an integrated, multi-format analytical pipeline.
- **Proposed Framework:** A unified software application integrating format-specific parsing, standardized feature extraction, rule-based health scoring (F1), calibrated Isolation Forest anomaly detection (F2), pattern recognition (F3), spatial timeline tracking (F4), diagnostic attribution (F5), semantically guarded stream comparison (F6), and automated multi-format reporting (F7).
- **Key Contributions:** Preservation of native format semantics, rigorous semantic audit preventing invalid cross-format metric comparison, bounded diagnostic Z-score attribution, and strict epistemic separation between observed facts and statistical inferences.
- **Empirical Validation:** Demonstrated on real-world satellite broadcast streams (18,176 MPEG-TS packets, 4,309 BBFrames, 14 GSE PDUs) with 207 automated tests achieving 100% pass rate.

---

## Section 24 — Review-2 Presentation & Defense Material

### 24.1 Review-2 Core Narrative: Transition from Concept to Functional Backend
- **Review-1:** Established project identity, literature review, architecture diagram, 7 planned features, and 5-folder dataset strategy. All implementation was planned/ongoing.
- **Review-2 Achievement:** Features F1 through F7 are **100% implemented, tested, reconciled, audited, and frozen**. The analytical core is fully functional across all three native DVB-S2 formats.
- **Key Metric for Reviewers:** **207 / 207 tests passing in 8.710s (0 failures, 0 errors)**, verified against 5 real-data validation tracks.

### 24.2 Recommended Demonstration Flow
1. **Multi-Format Ingestion:** Demonstrate automatic format detection on MPEG-TS, BBFrame, and GSE.
2. **Stream Health Assessment (F1):** Show immediate calculation of Priority-1 indicators and health score ($100.0/100$).
3. **Anomaly & Pattern Detection (F2 & F3):** Highlight rolling-window Isolation Forest anomaly scoring and dominant PID / modal DFL extraction.
4. **Spatial Timeline & Dashboards (F4):** Display interactive HTML dashboard showing metric trajectories across physical byte offsets.
5. **Diagnostic Explanation (F5):** Inspect an anomalous window and show ranked signed Z-score feature attributions.
6. **Stream Comparison Engine (F6):** Demonstrate side-by-side comparison of stream halves and cross-format comparison with semantic guards.
7. **Executive Report Generation (F7):** Present generated reports in Markdown, JSON, plain text, and standalone HTML.

---

## Section 25 — Evidence Mapping Matrix (Docs / PPT / Viva)

The following matrix cross-references project components to documentation sections, presentation slides, viva defense topics, and source files:

| Project Component | Documentation Section | Slide Candidate (Review-2 PPT) | Key Viva Defense Question | Authoritative Source / Artifact |
|---|---|---|---|---|
| **Multi-Format Architecture** | Section 4 | Slide 3: System Architecture | "Why are BBFrame, GSE, and TS not a sequential pipeline?" | `ingestion/stream_handler.py`, Review-1 baseline |
| **Stream Parsers** | Section 5 | Slide 4: Multi-Format Parsers | "How do you verify BBHeader integrity in DVB-S2?" | `parsers/bbframe_parser.py`, `parsers/ts_parser.py` |
| **Feature Extraction** | Section 6 | Slide 5: Unified Feature Engineering | "Why not flatten all formats into identical metrics?" | `features/extractor.py`, `CommonMetrics` |
| **F1 Stream Health** | Section 7 | Slide 6: Stream Health Engine | "Are your health checks ETSI TR 101 290 certified?" | `analysis/health.py`, `test_health.py` |
| **F2 Isolation Forest** | Section 8 | Slide 7: AI Anomaly Detection | "Why did you choose Isolation Forest over LSTM?" | `analysis/anomaly.py`, `test_anomaly.py` |
| **F3 Pattern Dynamics** | Section 9 | Slide 8: Pattern & Entropy Analysis | "How did you eliminate false MPEG-TS transitions?" | `analysis/patterns.py`, `test_patterns.py` |
| **F4 Spatial Timeline** | Section 10 | Slide 9: Timeline & Activity Dashboards | "Why do you index by byte offsets instead of timestamps?" | `analysis/timeline.py`, `timeline_*.html` |
| **F5 Anomaly Explanation** | Section 11 | Slide 10: Diagnostic Attribution Engine | "How do you calculate feature contributions to anomalies?" | `analysis/explanation.py`, `explanations_*.json` |
| **F6 Comparison Engine** | Section 12 | Slide 11: Stream Comparison & Semantic Audit | "Why can't you compare packet counts between TS and BBFrame?" | `analysis/comparison.py`, `comparison_*.json` |
| **F7 Automatic Reporting** | Section 13 | Slide 12: Executive Diagnostic Reports | "What is the Tripartite findings taxonomy?" | `analysis/report.py`, `report_*.html` |
| **Testing & Regression** | Section 14, 19 | Slide 13: Verification & Test Results | "What is your test coverage and verification state?" | `tests/` (207 tests), `unittest` log |
| **Bug Resolution** | Section 15 | Slide 14: Engineering Challenges & Fixes | "What technical bugs did you discover and resolve?" | Section 15 issue table, audit report |

---

## Section 26 — Academically Safe Claims We Can Defend

The project team can confidently and defensibly make the following claims:
1. The software application successfully ingests, parses, and validates three native post-demodulation DVB-S2 receiver output formats: MPEG-2 Transport Stream, Generic Stream Encapsulation, and DVB-S2 Baseband Frames.
2. The system implements a table-driven CRC-8 verification algorithm for DVB-S2 Baseband Headers in accordance with ETSI EN 302 307-1.
3. Feature F1 evaluates selected Priority-1 broadcast stream integrity indicators and computes an objective health score on a $[0, 100]$ scale.
4. Feature F2 provides an unsupervised Isolation Forest anomaly detection pipeline calibrated with a contamination factor of $c = 0.05$ and sigmoid score normalization.
5. Feature F3 profiles structural multiplex dynamics, dominant PIDs, modal Data Field Lengths, and Shannon entropy over rolling windows.
6. Feature F4 visualizes stream activity and events indexed strictly by physical byte offsets and sequential unit indices, avoiding fabricated wall-clock clocks.
7. Feature F5 provides diagnostic attribution for statistical outliers using bounded, signed Z-scores and subsystem component mapping.
8. Feature F6 implements a formal semantic audit that strictly blocks invalid cross-format comparisons while enabling differential comparison of comparable payload metrics.
9. Feature F7 automatically compiles structured executive reports across JSON, Markdown, CP-1252-safe plain text, and standalone HTML5.
10. The backend is verified by an automated regression suite of **207 / 207 passing tests** with zero failures and zero errors.

---

## Section 27 — Prohibited & Unsupported Claims We Must Reject

Under no circumstances should team members or documentation assert the following unsupported claims:
1. **DO NOT CLAIM formal ETSI TR 101 290 certification or complete standard compliance.** (Claim only "selected Priority-1 integrity indicators").
2. **DO NOT CLAIM physical-layer RF diagnostics** (e.g., measuring SNR, MER, $C/N$, carrier frequency offset, or AGC signal strength from post-demodulator digital stream bytes).
3. **DO NOT CLAIM rain fade, weather attenuation, or satellite transponder failure** as confirmed root causes of stream anomalies.
4. **DO NOT CLAIM supervised classification accuracy, precision, recall, or F1-scores** for anomaly detection without verified, frame-by-frame labeled ground-truth datasets.
5. **DO NOT CLAIM elementary stream identities (e.g., "AVC Video", "AC-3 Audio")** from raw PID numbers alone without parsed and verified PSI/SI tables (PAT/PMT).
6. **DO NOT CLAIM that capture termination unit truncations are transmission or broadcast failures.**
7. **DO NOT CLAIM live satellite dish hardware integration or cloud deployment** as current operational capabilities.

---

## Section 28 — Comprehensive File, Code & Artifact Index

### 28.1 Core Source Code Files (`05_CODE/dvbs2_analyzer/`)
- `ingestion/stream_handler.py`: Stream ingestion, format sniffing, and parser dispatching.
- `parsers/ts_parser.py`: MPEG-TS 188-byte packet parser, CC tracking, and TEI evaluation.
- `parsers/gse_parser.py`: GSE variable-length PDU parser, fragmentation, and EtherType tracking.
- `parsers/bbframe_parser.py`: DVB-S2 Baseband Frame parser and table-driven CRC-8 verifier.
- `features/extractor.py`: Unified feature extraction engine (`CommonMetrics`, format-specific metrics).
- `analysis/health.py`: Feature F1 Stream Health analyzer and scoring engine.
- `analysis/anomaly.py`: Feature F2 Isolation Forest anomaly detector and score normalizer.
- `analysis/patterns.py`: Feature F3 pattern detection and Shannon entropy calculator.
- `analysis/timeline.py`: Feature F4 spatial timeline generator and event mapper.
- `analysis/explanation.py`: Feature F5 diagnostic attribution and signed Z-score engine.
- `analysis/comparison.py`: Feature F6 stream comparison engine and semantic audit enforcer.
- `analysis/report.py`: Feature F7 automatic report generator and multi-format renderer.
- `visualization/dashboard.py`: Feature F4 standalone HTML dashboard builder.

### 28.2 Automated Test Suite (`05_CODE/tests/`)
- `tests/test_ts_parser.py`: 20 unit tests for MPEG-TS parsing.
- `tests/test_gse_parser.py`: 18 unit tests for GSE parsing.
- `tests/test_bbframe_parser.py`: 23 unit tests for BBFrame parsing and CRC-8.
- `tests/test_stream_handler.py`: 14 unit tests for ingestion and auto-detection.
- `tests/test_unified_features.py`: 10 unit tests for feature extraction and entropy.
- `tests/test_health.py`: 12 unit tests for F1 health scoring and classification.
- `tests/test_anomaly.py`: 16 unit tests for F2 Isolation Forest anomaly detection.
- `tests/test_patterns.py`: 20 unit tests for F3 pattern tracking and transition filtering.
- `tests/test_timeline.py`: 18 unit tests for F4 timeline generation and threshold propagation.
- `tests/test_explanation.py`: 21 unit tests for F5 diagnostic attribution and Z-scores.
- `tests/test_comparison.py`: 10 unit tests for F6 stream comparison and semantic guards.
- `tests/test_report.py`: 25 unit tests for F7 reporting and multi-format rendering.

### 28.3 Verified Report Artifacts (`05_CODE/reports/`)
- `PROJECT_DOCUMENTATION_LEDGER.md`: Verified interim engineering ledger.
- `PRJ_111_MASTER_DOCUMENTATION_REFERENCE.md`: This comprehensive master reference document.
- `report_mpeg_ts.*` (.json, .md, .txt, .html): Single-stream MPEG-TS analysis reports.
- `report_bbframe.*` (.json, .md, .txt, .html): Single-stream BBFrame analysis reports.
- `report_gse.*` (.json, .md, .txt, .html): Single-stream GSE analysis reports.
- `report_comparison_ts_halves.*` (.json, .md, .txt, .html): MPEG-TS halves comparison reports.
- `report_comparison_cross_format.*` (.json, .md, .txt, .html): Cross-format comparison reports.
- `timeline_*.html`: Standalone interactive HTML timeline dashboards.
- `explanations_*.json`: Structured diagnostic explanation exports.
- `comparison_*.json`: Structured differential comparison exports.

---

## Section 29 — Documentation Trigger Points (F1–F7 & System)

The following quick-reference guide specifies ready-to-use narrative blocks, tables, and figures for assembling final project documentation:

- **System Architecture Diagram:** Use ASCII diagram in Section 4.2 or embed `07_DOCUMENTATION/Architecture_Diagram.png`.
- **Feature F1 Documentation:** Copy Section 7 (Objective, Priority-1 metrics table, health equation, real-data score $100.0/100$).
- **Feature F2 Documentation:** Copy Section 8 (Isolation Forest rationale, equation, sigmoid conversion, controlled perturbation vs real data).
- **Feature F3 Documentation:** Copy Section 9 (MPEG-TS dominant PID, Shannon entropy formula, GSE protocol share, BBFrame modal DFL).
- **Feature F4 Documentation:** Copy Section 10 (Physical offset indexing, series extraction, dashboard generation).
- **Feature F5 Documentation:** Copy Section 11 (Bounded signed Z-score formula, component attribution table, explanation ranking).
- **Feature F6 Documentation:** Copy Section 12 (Semantic audit compatibility table, zero-baseline rules, significance thresholds).
- **Feature F7 Documentation:** Copy Section 13 (Tripartite taxonomy definitions, renderers, domain-safety guard text).
- **Testing & Verification Chapter:** Copy Section 19 (11-module breakdown, 207 passing tests) and Section 15 (Bug resolution history).
- **Experimental Results Chapter:** Copy Section 16 (Authoritative numerical reconciliation table across all 5 experiment tracks).

---

## Section 30 — Evidence Quality Classification Matrix

Every major statement, metric, and finding in this master reference is classified under the standardized epistemological quality system:

| Finding / Statement / Metric Dimension | Evidence Classification | Authoritative Source / Evidence Basis |
|---|:---:|---|
| MPEG-TS 188-byte fixed packet parsing & sync loss recovery | `VERIFIED_IMPLEMENTATION` | `parsers/ts_parser.py`, `tests/test_ts_parser.py` (20 tests) |
| Table-driven BBHeader CRC-8 verification ($g(x) = \text{0x1D5}$) | `VERIFIED_IMPLEMENTATION` | `parsers/bbframe_parser.py`, `CRC8_TABLE` verification |
| Priority-1 stream health score calculation ($[0, 100]$) | `VERIFIED_IMPLEMENTATION` | `analysis/health.py`, `tests/test_health.py` (12 tests) |
| Isolation Forest rolling window anomaly detection ($c=0.05$) | `VERIFIED_IMPLEMENTATION` | `analysis/anomaly.py`, `tests/test_anomaly.py` (16 tests) |
| Multi-stream comparison with semantic cross-format audit | `VERIFIED_IMPLEMENTATION` | `analysis/comparison.py`, `tests/test_comparison.py` (10 tests) |
| Tripartite report generation across JSON, MD, TXT, HTML | `VERIFIED_IMPLEMENTATION` | `analysis/report.py`, `tests/test_report.py` (25 tests) |
| Total test suite pass count: 207 / 207 passing in 8.710s | `VERIFIED_TEST` | `unittest discover -s tests -v` (11 test modules) |
| Synthetic perturbation detection rate: 100% | `CONTROLLED_SYNTHETIC_VALIDATION` | Controlled injection experiments in `test_anomaly.py` |
| `sample.ts` MPEG-TS metrics: 18,176 pkts, 100% integrity, 5 anomalies | `VERIFIED_REAL_DATA_RESULT` | `05_CODE/reports/report_mpeg_ts.json` |
| `dvb-s2_bb_example.pcap` metrics: 4,309 frames, 100% CRC, 5 anomalies | `VERIFIED_REAL_DATA_RESULT` | `05_CODE/reports/report_bbframe.json` |
| Reconciled BBFrame peak anomaly score: 0.7406 (Window 86) | `VERIFIED_REAL_DATA_RESULT` | Reconciled runtime output; doc discrepancy resolved |
| `GSExtract/sample.ts` metrics: 14 PDUs, 100% integrity, 1 anomaly | `VERIFIED_REAL_DATA_RESULT` | `05_CODE/reports/report_gse.json` |
| Review-1 baseline: 7 planned features, 5 dataset folders | `REVIEW_1_BASELINE` | `07_DOCUMENTATION/PRJ_111_Review1_Documentation.docx` |
| Boundary anomaly attribution: unit truncation at capture edge | `ENGINEERING_INTERPRETATION` | Grounded observation; no speculative transmission claims |
| Future PSI/SI descriptor decoding and live SDR integration | `FUTURE_WORK` | System roadmap; not implemented in frozen backend |
| Absence of physical RF carrier telemetry in baseband data | `LIMITATION` | Physical constraint of post-demodulator digital output |
| Historical BBFrame peak score `0.8872` was a typographical error | `DOCUMENTATION_ONLY` | Corrected in Section 15; runtime output is `0.7406` |

---
*End of Master Documentation Reference (PRJ_111)*  
*Authored and Verified: 19 September 2026*  
*Backend Frozen for Review-2 Milestone*
