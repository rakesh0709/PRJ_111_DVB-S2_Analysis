# 05_CODE — Source Code Architecture & Implementation

## Overview
This directory contains the production codebase for **PRJ_111: Development of a Software Application for Analysis and Processing of DVB-S2 Receiver Output Stream**.

The full-stack analytical engine (Features F1 through F7), incremental streaming ingestion (Chunk 1), controlled fault injection engine (Chunk 2), high-throughput streaming generator (Chunk 3), robustness hardening (Chunk 4), investigation workflow & semantic comparability barrier (Chunk 5), and interactive single-page application (SPA) workstation are fully implemented, verified, and frozen.

---

## Directory Structure

```
05_CODE/
├── dvbs2_analyzer/               # Core Python DVB-S2 Analysis Package
│   ├── ingestion/                # StreamHandler, chunk_reader & content-aware format detection
│   │   ├── stream_handler.py     # Main ingestion and format dispatcher
│   │   ├── chunk_reader.py       # Chunk 1: Incremental chunked reading & memoryviews
│   │   └── format_detector.py    # Heuristic & magic-byte format identification
│   ├── parsers/                  # Format decoders
│   │   ├── base.py               # Abstract base parser & CommonUnit definitions
│   │   ├── ts_parser.py          # MPEG-2 Transport Stream decoder (188-byte packets, 0x47 sync)
│   │   ├── gse_parser.py         # Generic Stream Encapsulation decoder (ETSI TS 102 606)
│   │   └── bbframe_parser.py     # DVB-S2 Baseband Frame decoder (10-byte BBHeader, CRC-8)
│   ├── preprocessing/            # Stream sanitizer & unit validation
│   ├── features/                 # Unified feature extraction across sliding/hopping windows
│   ├── analysis/                 # Analytical engines (F1-F3, F5-F7)
│   │   ├── health.py             # Feature F1: Stream Health & Integrity (ETSI TR 101 290 principles)
│   │   ├── anomaly.py            # Feature F2: AI Anomaly Detection (Isolation Forest)
│   │   ├── patterns.py           # Feature F3: Pattern & Multiplex Recognition
│   │   ├── timeline.py           # Feature F4: Activity & Spatial Timeline
│   │   ├── explanation.py        # Feature F5: Bounded Z-score Attributions (|Z| <= 20.0 sigma)
│   │   ├── comparison.py         # Feature F6: Cross-Stream Comparison & Semantic Shield
│   │   └── report.py             # Feature F7: Multi-Format Automatic Report Synthesizer
│   ├── fault_injection/          # Chunk 2: Controlled synthetic fault injection engine
│   │   ├── injector.py           # Bit-level corruption injector (TEI, CC, PID, GSE, BBFrame)
│   │   └── scenarios.py          # Standardized degradation profiles
│   ├── streaming/                # Chunk 3: High-throughput streaming pipeline
│   │   └── engine.py             # Cursor-based compaction & bounded memory streaming generator
│   └── frontend/                 # Backend REST API Server & Workstation Host
│       ├── coordinator.py        # AnalysisCoordinator connecting backend engines
│       ├── server.py             # Threaded HTTP REST Server (port 8080)
│       └── static/               # Interactive Single-Page Application (SPA) Workstation
│           ├── index.html        # Tabbed Engineering UI (Dashboard, Anomaly, Timeline, Compare, Report)
│           ├── styles.css        # Clean industrial dark theme (vanilla CSS3)
│           ├── app.js            # Frontend application controller & REST client (ES6)
│           └── chart.umd.min.js  # Vendored offline Chart.js engine (v4.4.x)
├── tests/                        # 304 Automated Python Unit, Streaming, Fault Injection, and Integration Tests
│   ├── test_ts_parser.py         # MPEG-TS parser verification
│   ├── test_gse_parser.py        # GSE parser verification
│   ├── test_bbframe_parser.py    # BBFrame parser verification
│   ├── test_format_detector.py   # Content-aware detection verification
│   ├── test_features.py          # Unified feature extractor verification
│   ├── test_health.py            # Feature F1 health checks
│   ├── test_anomaly.py           # Feature F2 Isolation Forest verification
│   ├── test_patterns.py          # Feature F3 multiplex patterns
│   ├── test_timeline.py          # Feature F4 spatial window timelines
│   ├── test_explanation.py       # Feature F5 bounded Z-score explanations
│   ├── test_comparison.py        # Feature F6 cross-stream semantic shield
│   ├── test_report.py            # Feature F7 multi-format report generator
│   ├── test_frontend.py          # REST API & static server integration tests (36 tests)
│   ├── test_chunk_processing.py  # Chunk 1: Incremental chunked reading & whole-file equivalence
│   ├── test_fault_injection.py   # Chunk 2: Fault injection & sensitivity validation
│   ├── test_high_throughput.py   # Chunk 3: High-throughput streaming & memory boundedness
│   ├── test_chunk4_robustness.py # Chunk 4: Robustness hardening (empty, truncated, malformed)
│   └── test_chunk5_investigation.py # Chunk 5: Investigation workflow, F5/F6 & semantic shield
├── test_inputs/                  # Deterministic test captures (corrupted_sample.ts, synthetic profiles)
├── uploads/                      # Local uploaded stream buffer
├── run_frontend.py               # Startup script for full-stack HTTP server (port 8080)
└── requirements.txt              # Python virtual environment dependencies
```

---

## Technology Stack

| Component | Technology | Version | Purpose |
| :--- | :--- | :--- | :--- |
| **Frontend Workstation** | Single-Page Application (SPA) | HTML5 / Vanilla CSS3 / ES6 | Industrial engineering workstation & live diagnostic telemetry UI |
| **Visualization Engine** | Chart.js (Vendored) | v4.4.x | Offline client-side spatial timelines, rolling health score tracking, and payload density |
| **Analysis Backend** | Python | 3.12+ | Bit-level stream parsers, feature extraction, health check |
| **HTTP / REST API** | ThreadingHTTPServer | Python 3.12 stdlib | Full-stack REST API & static web server on port 8080 |
| **Machine Learning** | scikit-learn | 1.5+ | Feature F2 unsupervised Isolation Forest anomaly detection |
| **Numerical Processing** | NumPy | 1.26+ | Rolling window feature aggregation and bounded Z-scores |
| **Regression Testing** | Python unittest | 3.12 stdlib | 304 automated tests (268 backend unit, streaming, fault injection, robustness & investigation + 36 REST API integration) |

---

## Execution Instructions

### 1. Launch Full-Stack Application (Port 8080)
The application is entirely self-contained within Python standard library and dependencies, serving the SPA frontend and REST API simultaneously:

```powershell
cd 05_CODE
.venv\Scripts\python.exe run_frontend.py --host 127.0.0.1 --port 8080
```
Verified output:
```
PRJ_111 Frontend Server running at http://127.0.0.1:8080
Serving static assets from: ...\05_CODE\dvbs2_analyzer\frontend\static
Press Ctrl+C to stop.
```
Open `http://127.0.0.1:8080` in any modern web browser.

Alternatively, from the repository root, run:
```powershell
.\RUN_PROJECT.bat
```

### 2. Run Complete Regression Test Suite
Run the authoritative 304-test regression suite:

```powershell
cd 05_CODE
.venv\Scripts\python.exe -m unittest discover -s tests
```
Expected result:
```
Ran 304 tests in ~74s
OK
```

Alternatively, from the repository root, run:
```powershell
.\RUN_TESTS.bat
```

### 3. Key REST API Endpoints
When the server is running on `http://127.0.0.1:8080`:
- `GET /` — Interactive Single-Page Application (SPA) Dashboard
- `GET /api/status` — Operational status, pipeline metrics, and system health
- `GET /api/presets` — Discovers available raw test datasets across TS, GSE, and BBFrame
- `POST /api/analyze` — Executes full F1–F5 analysis pipeline on specified stream
- `POST /api/compare` - Executes Feature F6 cross-stream semantic shield audit
- `POST /api/upload` - Ingests user-supplied stream files into local upload buffer
- `POST /api/fault-inject` - Injects controlled synthetic mutations (TEI, CC, PID, GSE, BBFrame) and runs sensitivity audit
- `GET /api/export` - Generates and downloads Feature F7 diagnostic reports (JSON, Markdown, TXT, HTML)
