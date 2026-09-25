# 05_CODE — Source Code Architecture & Implementation

## Overview
This directory contains the production codebase for **PRJ_111: Development of a Software Application for Analysis and Processing of DVB-S2 Receiver Output Stream**.

At the **Review-2 Milestone (~50%+ Functional Prototype)**, all core analytical engines (Features F1 through F7) and the modern web workstation frontend are fully implemented, verified, and frozen.

---

## Directory Structure

```
05_CODE/
├── dvbs2_analyzer/               # Core Python DVB-S2 Analysis Package
│   ├── ingestion/                # StreamHandler & content-aware format detection
│   ├── parsers/                  # Format decoders (TSParser, GSEParser, BBFrameParser)
│   ├── preprocessing/            # Stream sanitizer & unit validation
│   ├── features/                 # Unified feature extraction across windows
│   ├── analysis/                 # Analytical engines (F1-F3, F5-F7)
│   │   ├── health.py             # Feature F1: Stream Health & Integrity
│   │   ├── anomaly.py            # Feature F2: AI Anomaly Detection (Isolation Forest)
│   │   ├── patterns.py           # Feature F3: Pattern & Multiplex Recognition
│   │   ├── timeline.py           # Feature F4: Activity & Spatial Timeline
│   │   ├── explanation.py        # Feature F5: Bounded Z-score Attributions
│   │   ├── comparison.py         # Feature F6: Cross-Stream Comparison & Semantic Shield
│   │   └── report.py             # Feature F7: Multi-Format Automatic Report Synthesizer
│   └── frontend/                 # Backend REST API Server & Coordinator
│       ├── coordinator.py        # AnalysisCoordinator connecting backend engines
│       ├── server.py             # Threaded HTTP REST Server (port 8080)
│       └── static/               # Legacy Review-1 static assets (retained for backward compatibility)
├── web/                          # Next.js 15 + React 19 + Tailwind CSS v4 Workstation
│   ├── app/                      # Next.js App Router (layout.tsx, page.tsx, globals.css)
│   ├── components/               # Hand-built modular engineering workstation components
│   ├── lib/                      # Types, offline empirical dataset, and format adapters
│   └── tests/                    # Frontend verification test suite (Node test runner)
├── tests/                        # 240 Automated Python Unit & Integration Tests
├── test_inputs/                  # Deterministic test captures (corrupted_sample.ts)
├── uploads/                      # Local uploaded stream buffer
├── run_frontend.py               # Startup script for Python REST API backend
└── requirements.txt              # Python virtual environment dependencies
```

---

## Technology Stack

| Component | Technology | Version | Purpose |
| :--- | :--- | :--- | :--- |
| **Frontend Workstation** | Next.js (App Router) | 15.5+ | Industrial engineering workstation & technical showcase |
| **UI Framework** | React | 19.3+ | Component-driven declarative UI with zero 3rd-party component libraries |
| **Styling & Tokens** | Tailwind CSS | v4.3+ | Strict Swiss typography scale, industrial 0px radius, zero box-shadows |
| **Type Safety** | TypeScript | 5.9+ | End-to-end schema validation for all F1-F7 API responses |
| **Analysis Backend** | Python | 3.12+ | Bit-level stream parsers, feature extraction, health check |
| **HTTP / REST API** | ThreadingHTTPServer | Python 3.12 stdlib | High-throughput local REST API on port 8080 |
| **Machine Learning** | scikit-learn | 1.5+ | Feature F2 unsupervised Isolation Forest anomaly detection |
| **Numerical Processing** | NumPy | 1.26+ | Rolling window feature aggregation and bounded Z-scores |
| **Backend Testing** | Python unittest | 3.12 stdlib | 240 automated tests (207 unit/pipeline + 33 REST API & coordinator integration) |
| **Frontend Testing** | Node test runner | Node 24+ | 9 automated offline data & design token verification tests |

---

## Execution Instructions

### 1. Launch Python REST Backend (Port 8080)
```powershell
cd 05_CODE
.venv\Scripts\python.exe run_frontend.py
# Verified output: PRJ_111 Frontend Server running at http://127.0.0.1:8080
```

### 2. Launch Next.js 15 Workstation (Port 3000)
```powershell
cd 05_CODE/web
npm install
npm run dev
# Open http://localhost:3000 in modern web browser
```

### 3. Run Automated Tests
```powershell
# Run full 240-test Python regression suite:
cd 05_CODE
.venv\Scripts\python.exe -m unittest discover -s tests

# Run Next.js frontend verification suite:
cd 05_CODE/web
npm test

# Build production Next.js application:
cd 05_CODE/web
npm run build
```
