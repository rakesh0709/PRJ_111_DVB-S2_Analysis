# Development of a Software Application for Analysis and Processing of DVB-S2 Receiver Output Stream

[![Project ID: PRJ_111](https://img.shields.io/badge/Project%20ID-PRJ__111-blue.svg)](#project-information)
[![Phase: Review-2](https://img.shields.io/badge/Status-Review--2%20Functional%20Prototype%20Verified-success.svg)](#current-project-status)
[![Track: B.Tech CSE Mini-Project](https://img.shields.io/badge/Track-B.Tech%20CSE%20Mini--Project-orange.svg)](#team-members)
[![Tests: 240 Passing](https://img.shields.io/badge/Tests-240%2F240%20Passing-brightgreen.svg)](#verification--testing)
[![Frontend: Next.js 15](https://img.shields.io/badge/Frontend-Next.js%2015%20%7C%20React%2019%20%7C%20Tailwind%20v4-black?logo=next.js)](05_CODE/web)
[![Repository: GitHub](https://img.shields.io/badge/GitHub-PRJ__111--DVB--S2--Analysis-black?logo=github)](https://github.com/rakesh0709/PRJ_111_DVB-S2_Analysis.git)

---

## 1. Project Title
**Development of a Software Application for Analysis and Processing of DVB-S2 Receiver Output Stream**

---

## 2. Project ID & Academic Details
* **Project ID:** `PRJ_111`
* **Program:** B.Tech Computer Science & Engineering (Mini Project)
* **Milestone:** Review-2 Milestone (~50%+ Functional Prototype Implemented & Verified)
* **Repository:** [https://github.com/rakesh0709/PRJ_111_DVB-S2_Analysis.git](https://github.com/rakesh0709/PRJ_111_DVB-S2_Analysis.git)

---

## 3. Project Description
Satellite communication and broadcasting networks operating under the **DVB-S2** (*Digital Video Broadcasting — Satellite — Second Generation*, ETSI EN 302 307) standard deliver high-throughput, spectrally efficient data and broadcast streams. Modern satellite receivers output streams across multiple encapsulation and framing layers, primarily:
1. **Baseband (BB) Frames** (Link/physical layer encapsulation with 10-byte BBHeaders)
2. **Generic Stream Encapsulation (GSE)** (Variable-length IP/network PDU packet transport under ETSI TS 102 606)
3. **MPEG Transport Stream (MPEG-TS)** (Standard broadcast audio/video multiplex container with 188-byte packets and 0x47 sync)

This project develops a unified software application and industrial workstation engineered to ingest DVB-S2 receiver outputs across these three alternative formats, extract standardized temporal feature metrics, evaluate stream health (F1), detect transmission anomalies using unsupervised machine learning (F2), analyze multiplex patterns (F3), render spatial activity timelines with byte-level precision (F4), produce bounded diagnostic explanations (F5), enforce strict semantic comparison barriers between heterogeneous containers (F6), and synthesize multi-format inspection reports (F7).

---

## 4. Problem Statement
Monitoring, verifying, and debugging satellite receiver output streams presents several critical challenges:
* **Format Heterogeneity:** Satellite receiver outputs vary depending on the transponder profile (Baseband Frames, GSE packets, or MPEG Transport Streams), historically requiring disconnected command-line utilities for inspection.
* **Lack of Intelligent Anomaly Detection:** Conventional stream analyzers rely on basic threshold alerts, failing to detect subtle temporal anomalies, sudden jitter variations, corrupted modulation frames, or unexpected multiplex behaviors.
* **Absence of Unified Diagnostic Platforms:** Existing open-source tools typically focus only on one isolated format (e.g., MPEG-TS only or PCAP inspection only) without providing unified health metrics, explainable AI diagnostics, comparative stream analysis, or automated report generation.

---

## 5. Supported Input Formats

The application supports three distinct, alternative input formats produced at various stages of the DVB-S2 receiver demodulation and demultiplexing pipeline:

```
                  +----------------------------------------------+
                  |         DVB-S2 Receiver Output Stream        |
                  +----------------------------------------------+
                                         |
         +-------------------------------+-------------------------------+
         |                               |                               |
         v                               v                               v
+------------------+           +-------------------+           +-------------------+
|  Baseband Frames |           |  Generic Stream   |           |  MPEG Transport   |
|   (BB Frames)    |           |Encapsulation (GSE)|           |    Stream (TS)    |
+------------------+           +-------------------+           +-------------------+
| Physical/Link    |           | IP & Data Network |           | Audio, Video &    |
| Framing (Header, |           | Packet Transport  |           | PSI/SI Multiplex  |
| MODCOD, Payload) |           | (ETSI TS 102 606) |           | (ISO/IEC 13818-1) |
+------------------+           +-------------------+           +-------------------+
```

> **Important Architectural Rule:** These formats are treated as **alternative input formats** that the application independently parses and analyzes, rather than a mandatory sequential conversion pipeline (`BBFrame → GSE → TS`).

---

## 6. Seven Core Project Features (F1–F7)

| Feature ID | Feature Name | Description & Capability | Verified Status |
| :--- | :--- | :--- | :--- |
| **F1** | **Stream Health Analysis** | Quantifies stream transmission quality inspired by ETSI TR 101 290 principles (Sync byte 0x47, TEI assertion rate, CC continuity error rate, CRC-8 validation, and framing bounds). | **Verified (100.0% Integrity)** |
| **F2** | **AI-based Anomaly Detection** | Unsupervised Isolation Forest baseline (contamination=0.05, n_estimators=100) flagging structural anomalies without assuming synthetic ground truth. | **Verified (IForest Baseline)** |
| **F3** | **Pattern Detection** | Extracts multiplex characteristics: PID distribution, Shannon entropy (0.1361 bits on TS), EtherType classification on GSE, and modal DFL dispersion on BBFrame. | **Verified (Multi-Format)** |
| **F4** | **Timeline / Activity Visualization** | Spatial analysis window timeline with byte offset indexing (0x offsets), window segmentation (w=200/3/50), and anomaly markers. | **Verified (Interactive UI)** |
| **F5** | **Anomaly Explanation** | Delivers interpretable feature-level attribution cards using bounded z-scores ($|Z| \le 20.0\,\sigma$) for stable diagnostic triage. | **Verified (Bounded XAI)** |
| **F6** | **Stream Comparison** | Strict semantic shield enforcing cross-format comparison boundaries: exactly 2 comparable metrics (payload bytes, integrity ratio) vs. 9 masked incommensurable metrics. | **Verified (Semantic Shield)** |
| **F7** | **Automatic Analysis Report** | Generates exportable, multi-page structured diagnostic reports across Markdown, HTML5, plain text, and JSON formats. | **Verified (Export Engine)** |

---

## 7. Technology Stack

| Layer | Technology | Version | Purpose |
| :--- | :--- | :--- | :--- |
| **Frontend Framework** | Next.js (App Router) | 15.5+ | High-performance industrial engineering workstation & hybrid showcase |
| **UI Component Core** | React | 19.3+ | Component-driven declarative UI with zero 3rd-party component libraries |
| **Styling & Design Tokens** | Tailwind CSS | v4.3+ | Strict Swiss typography scale, industrial 0px radius, zero box-shadows |
| **Type Safety** | TypeScript | 5.9+ | End-to-end schema validation for all F1-F7 API responses |
| **Analysis Backend** | Python | 3.12+ | Bit-level stream parsers, feature extraction, health check |
| **HTTP / REST API** | ThreadingHTTPServer | Python stdlib | High-throughput local REST API on port 8080 |
| **Machine Learning** | scikit-learn | 1.5+ | Feature F2 unsupervised Isolation Forest anomaly detection |
| **Numerical Processing** | NumPy | 1.26+ | Rolling window feature aggregation and bounded Z-scores |
| **Backend Testing** | Python unittest | 3.12 stdlib | 240 automated tests (207 unit/pipeline + 33 REST API & coordinator integration) |
| **Frontend Testing** | Node test runner | Node 24+ | 9 automated offline data & design token verification tests |

---

## 8. Dual-Mode Operation

The redesigned workstation operates seamlessly across two operational modes:

* **Mode A — Live Backend Workstation:** When the Python backend is active at `http://127.0.0.1:8080`, users can upload custom `.ts`, `.pcap`, or `.bin` binary dumps, execute content-aware stream detection, configure analysis windows, run live F1-F7 pipelines, and export generated reports.
* **Mode B — Offline Technical Showcase:** When the backend is offline, the interface displays an explicit `BACKEND OFFLINE (OFFLINE SHOWCASE)` status indicator and renders verified, precompiled empirical telemetries from `06_RESULTS/` across MPEG-TS (`sample.ts`), GSE (`sample.ts`), and BBFrame (`dvb-s2_bb_example.pcap`) with zero broken states and zero fabricated values.

---

## 9. System Architecture

```
BROWSER (CLIENT WORKSTATION)
   |
   ↓
NEXT.JS 15 APPLICATION (PORT 3000)
   ├── App Router & React 19 Components
   ├── Tailwind CSS v4 Design System (0px radius, strict 12/14/16/24/48/96px typography)
   ├── Live Analyzer & File Uploader
   ├── Horizontal Activity Timeline (F4) & Anomaly Inspector (F2 & F5)
   ├── Semantic Comparison Matrix (F6)
   └── Precompiled Empirical Offline Data Engine
   |
   ↓ HTTP REST API (PORT 8080)
PYTHON ANALYSIS BACKEND (PRJ_111 ENGINE)
   ├── Stream Ingestion & Content-Aware Format Detector
   ├── Format Decoders (TSParser, GSEParser, BBFrameParser)
   ├── Unified Feature Extractor
   ├── F1: Stream Health Analyzer (ETSI TR 101 290 principles)
   ├── F2: Isolation Forest Anomaly Detector
   ├── F3: Multiplex Pattern & Entropy Extractor
   ├── F5: Diagnostic Explanation Engine (|Z| <= 20.0 sigma)
   ├── F6: Stream Comparison Engine & Semantic Shield
   └── F7: Multi-Format Automatic Report Synthesizer
```

---

## 10. Repository Organization

```
PRJ_111_DVB-S2_Analysis/
├── README.md                       # Main project repository documentation (this file)
├── RUN_PROJECT.bat                 # One-click dual-stack startup script (Backend + Workstation + Browser)
├── START_BACKEND.bat               # Python analysis REST API backend launcher (Port 8080)
├── START_WEB_WORKSTATION.bat       # Next.js 15 Web Workstation launcher (Port 3000)
├── RUN_TESTS.bat                   # Full automated test verification runner (240 Python + 9 Next.js)
├── 01_RAW_DATA/                    # Real collected raw datasets (kept locally & immutable)
│   ├── 01_BBFRAME_GSE/             # DVB-S2 Baseband frame and GSE captures (.pcap)
│   ├── 02_GSE/                     # GSE extraction sample streams (.ts)
│   ├── 03_TS/                      # MPEG Transport Stream broadcast captures (.ts)
│   ├── 04_RFI_AI/                  # RFI and modulation reference data archives (.zip)
│   └── 05_REAL_DVB_S2/             # Real-world over-the-air DVB-S2 broadcast data (.ts)
├── 02_PROCESSED_DATA/              # Cleaned intermediate streams and normalized dumps
├── 03_FEATURE_DATA/                # Extracted feature series and PID distributions
├── 04_AI_MODELS/                   # Serialized Isolation Forest model configurations
├── 05_CODE/                        # Full production source code
│   ├── dvbs2_analyzer/             # Python analytical engines, parsers, and HTTP server
│   ├── web/                        # Next.js 15 + React 19 + Tailwind v4 Web Workstation
│   ├── tests/                      # 240 Automated Python unit and integration tests
│   └── run_frontend.py             # Python REST API server entrypoint (port 8080)
├── 06_RESULTS/                     # Authoritative empirical experiment outputs & reports
│   ├── reports/                    # Generated Markdown, HTML, JSON, TXT reports
│   ├── timelines/                  # Full spatial window JSON timelines
│   ├── comparisons/                # Cross-format and sub-stream comparison audits
│   └── explanations/               # Diagnostic attribution summaries
└── 07_DOCUMENTATION/               # Project reviews, academic papers, and master reference
    ├── RESEARCH_PAPER/             # Research paper manuscripts, assets, and master reference
    │   └── PRJ_111_MASTER_DOCUMENTATION_REFERENCE.md # Single source of truth
    └── PRJ_111_Review2_Final_Documentation.docx # Comprehensive Review-2 documentation
```

---

## 11. Verification & Testing

The project maintains a strict 100% pass verification invariant:

* **Backend Unit & Pipeline Suite:** 207 tests passing (`tests/test_*.py`)
* **HTTP REST API & Coordinator Integration Suite:** 33 tests passing (`tests/test_frontend.py`)
* **Total Automated Python Suite:** **240 / 240 Tests Passing (0 failures, 0 errors)**
* **Next.js Workstation Test Suite:** 9 / 9 tests passing (`web/tests/frontend.test.mjs` via `npm test`)
* **Production Build:** `npm run build` inside `05_CODE/web/` compiles cleanly with zero TypeScript or CSS warnings.

---

## 12. Quick Start Guide

### Prerequisites
* Windows 11 / Linux / macOS
* Python 3.12+ (virtual environment located in `05_CODE/.venv`)
* Node.js 20+ / 24+ and npm 10+ / 11+

### Step 1: Start Python REST Backend
```powershell
cd 05_CODE
.venv\Scripts\python.exe run_frontend.py
# Server binds to http://127.0.0.1:8080
```

### Step 2: Start Next.js 15 Web Workstation
```powershell
cd 05_CODE/web
npm install
npm run dev
# Workstation accessible at http://localhost:3000
```

### Step 3: Run Automated Test Suites
```powershell
# Python regression suite (240 tests):
cd 05_CODE
.venv\Scripts\python.exe -m unittest discover -s tests

# Frontend verification suite:
cd 05_CODE/web
npm test
```

---

## 13. Current Project Status

```
[================================ 65% Completed ====================>            ]
```

### Review-2 Completed Milestones
* [x] **Multi-Format Bit-Level Parsers:** Operational decoders for MPEG-TS, GSE, and BBFrame containers.
* [x] **Content-Aware Format Detection:** Dynamic payload detection handling `.ts` wrappers containing GSE streams.
* [x] **Unified Feature Extraction Engine:** Window-partitioned feature aggregation across heterogeneous framing types.
* [x] **F1 Stream Health Assessment:** Stream integrity ratio calculation (100.0%) and priority checks.
* [x] **F2 Unsupervised Anomaly Detection:** Isolation Forest baseline with upper 5% contamination boundary.
* [x] **F3 Pattern & Entropy Analysis:** Multiplex Shannon entropy, PID allocations, and modal DFL dispersion.
* [x] **F4 Activity & Spatial Timeline:** Window-segmented timeline with byte offset indexing.
* [x] **F5 Diagnostic Explanations:** Bounded z-scores ($|Z| \le 20.0\,\sigma$) for stable attribution.
* [x] **F6 Semantic Comparison Shield:** Enforces mathematical boundaries between incompatible stream types.
* [x] **F7 Automatic Multi-Format Reporting:** Generates Markdown, HTML5, plain text, and JSON summaries.
* [x] **Next.js 15 + React 19 Frontend Workstation:** High-density industrial terminal adhering strictly to Swiss typography and zero-rounding constraints.
* [x] **240/240 Test Verification Invariant:** Fully verified regression suite with zero failures.

---

## 14. Team Members

| Name | Role | Primary Responsibilities |
| :--- | :--- | :--- |
| **Rakeshwar** | **Core Development & Technical Lead** | Backend architecture, Next.js workstation integration, AI/ML model development, stream processing, parser implementation, feature extraction, system integration. |
| **Samad** | **Testing, Validation & Documentation Lead** | Testing lead, validation protocols, literature review, technical documentation lead, experimental report preparation, supporting development. |
| **Vengal Rao** | **Frontend, Visualization & Development** | Frontend UI architecture, interactive data visualization, dashboard styling, presentation preparation, supporting development. |

---

## References & Standards
1. **ETSI EN 302 307-1:** *Digital Video Broadcasting (DVB); Second Generation framing structure, channel coding and modulation systems for Broadcasting, Interactive Services, News Gathering and other broadband satellite applications; Part 1: DVB-S2.*
2. **ETSI TS 102 606-1:** *Digital Video Broadcasting (DVB); Generic Stream Encapsulation (GSE) Protocol.*
3. **ISO/IEC 13818-1:** *Information technology — Generic coding of moving pictures and associated audio information: Systems (MPEG-2 Transport Stream).*
4. **ETSI TR 101 290:** *Digital Video Broadcasting (DVB); Measurement guidelines for DVB systems (Principles referenced for stream integrity indicators).*
