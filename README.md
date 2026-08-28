# Development of a Software Application for Analysis and Processing of DVB-S2 Receiver Output Stream

[![Project ID: PRJ_111](https://img.shields.io/badge/Project%20ID-PRJ__111-blue.svg)](#project-information)
[![Phase: Review-1](https://img.shields.io/badge/Status-Review--1%20Completed%20%7C%20Active%20Development-success.svg)](#current-project-status)
[![Track: B.Tech CSE Mini-Project](https://img.shields.io/badge/Track-B.Tech%20CSE%20Mini--Project-orange.svg)](#team-members)
[![Repository: GitHub](https://img.shields.io/badge/GitHub-PRJ__111--DVB--S2--Analysis-black?logo=github)](https://github.com/rakesh0709/PRJ_111_DVB-S2_Analysis.git)

---

## 1. Project Title
**Development of a Software Application for Analysis and Processing of DVB-S2 Receiver Output Stream**

---

## 2. Project ID & Academic Details
* **Project ID:** `PRJ_111`
* **Program:** B.Tech Computer Science & Engineering (Mini Project)
* **Milestone:** Review-1 Completed | Phase 2 Development Ongoing
* **Repository:** [https://github.com/rakesh0709/PRJ_111_DVB-S2_Analysis.git](https://github.com/rakesh0709/PRJ_111_DVB-S2_Analysis.git)

---

## 3. Project Description
Satellite communication and broadcasting networks operating under the **DVB-S2** (*Digital Video Broadcasting — Satellite — Second Generation*, ETSI EN 302 307) standard deliver high-throughput, spectrally efficient data and broadcast streams. Modern satellite receivers output streams across multiple encapsulation and framing layers, primarily:
1. **Baseband (BB) Frames** (Link/physical layer encapsulation)
2. **Generic Stream Encapsulation (GSE)** (Efficient IP network packet transport)
3. **MPEG Transport Stream (MPEG-TS)** (Standard broadcast audio/video multiplex container)

This project develops a unified software application engineered to ingest DVB-S2 receiver output in any of these three formats, process and extract structural telemetry, evaluate stream health, detect transmission anomalies and recurring patterns using AI/ML, present interactive temporal visualizations and comparisons, and generate automated diagnostic inspection reports.

---

## 4. Problem Statement
Monitoring, verifying, and debugging satellite receiver output streams presents several critical challenges:
* **Format Heterogeneity:** Satellite receiver outputs vary depending on the transponder profile (Baseband Frames, GSE packets, or MPEG Transport Streams), often requiring disconnected, proprietary command-line utilities for inspection.
* **Lack of Intelligent Anomaly Detection:** Conventional stream analyzers rely on basic threshold checks, failing to detect subtle temporal anomalies, sudden jitter variations, corrupted modulation frames, or unexpected multiplex behaviors.
* **Absence of Unified Diagnostic Platforms:** Existing open-source tools typically focus only on one isolated format (e.g., MPEG-TS only or PCAP inspection only) without providing unified health metrics, explainable AI diagnostics, comparative stream analysis, or automated report generation.

---

## 5. Objectives
1. **Multi-Format Ingestion:** Ingest and parse DVB-S2 receiver output streams across three alternative formats: Baseband (BB) Frames, GSE frames, and MPEG-TS packets.
2. **Stream Health Assessment:** Compute quantitative stream integrity indicators including packet loss rate, Continuity Counter (CC) error frequency, sync byte validation, and jitter.
3. **AI/ML Anomaly Detection:** Implement machine learning algorithms to identify irregular stream behavior, transmission degradation, and signal anomalies.
4. **Pattern Recognition:** Discover recurring patterns in stream transmission, PID multiplex allocations, and modulation parameters.
5. **Interactive Visualization:** Provide dynamic timeline views and graphical charts of stream activity, bandwidth utilization, and error occurrences.
6. **Explainable Diagnostics:** Provide root-cause contextual explanations for flagged anomalies to assist operators and engineers.
7. **Stream Comparison & Benchmarking:** Provide side-by-side differential analysis of multiple stream captures.
8. **Automated Diagnostic Reporting:** Automatically generate structured summary reports consolidating health metrics, anomalies, and recommendations.

---

## 6. Supported Input Formats

The application is designed to support three distinct, alternative input formats produced at various stages of the DVB-S2 receiver demodulation and demultiplexing pipeline:

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

> **Note:** These formats are treated as **alternative input types** that the application independently parses and analyzes, rather than a mandatory sequential conversion pipeline.

---

## 7. Seven Core Project Features

| Feature ID | Feature Name | Description & Capability | Target Role |
| :--- | :--- | :--- | :--- |
| **F1** | **Stream Health Analysis** | Quantifies stream transmission quality by evaluating Continuity Counter errors, sync byte consistency, packet drop rates, PCR jitter, and payload integrity. | Diagnostic Engine |
| **F2** | **AI-based Anomaly Detection** | Utilizes machine learning models (e.g., Isolation Forests, Autoencoders, LSTM networks) to flag atypical stream deviations, packet bursts, and corrupted frame structures. | Intelligent Analysis |
| **F3** | **Pattern Detection** | Identifies recurring temporal behaviors, cyclic PID multiplex patterns, burst characteristics, and modulation trends across the transmission. | Statistical & ML Mining |
| **F4** | **Timeline / Activity Visualization** | Interactive visual dashboards plotting packet arrival rates, bandwidth consumption over time, error occurrences, and stream events along a navigable timeline. | Visual Interface |
| **F5** | **Anomaly Explanation** | Delivers interpretable reasoning and contextual evidence for flagged anomalies (e.g., specific PID deviation, abnormal byte distribution, header violation). | Explainable AI |
| **F6** | **Stream Comparison** | Side-by-side comparison of two stream captures to highlight structural differences, error rates, and metric disparities for regression or differential testing. | Comparative Analysis |
| **F7** | **Automatic Analysis Report** | Generates exportable, structured diagnostic reports (PDF/HTML/JSON) summarizing stream health status, detected anomalies, pattern summaries, and telemetry metrics. | Automated Reporting |

---

## 8. Proposed System Architecture

The overall system architecture is organized into five modular functional layers:

```
+-----------------------------------------------------------------------------------+
|                           1. Stream Ingestion Layer                               |
|        [ Baseband (BB) Frames ]  |  [ GSE Packets ]  |  [ MPEG Transport Stream ] |
+-----------------------------------------------------------------------------------+
                                         |
                                         v
+-----------------------------------------------------------------------------------+
|                       2. Parsing & Preprocessing Layer                            |
|    - BBFrame Header / MODCOD Parser    - GSE De-encapsulator / Header Inspector   |
|    - MPEG-TS Demux & PID Extractor     - Timestamp & Packet Alignment Synchronizer|
+-----------------------------------------------------------------------------------+
                                         |
                                         v
+-----------------------------------------------------------------------------------+
|                         3. Feature Extraction Layer                               |
|    - Continuity Counter Metrics        - Bandwidth & PID Distribution             |
|    - Jitter & Timestamp Delta          - Frame Structural & Statistical Features  |
+-----------------------------------------------------------------------------------+
                                         |
                                         v
+-----------------------------------------------------------------------------------+
|                      4. Intelligent Analysis & AI/ML Layer                        |
|    - F1: Health Assessment Engine      - F2: ML Anomaly Detection (Unsupervised)  |
|    - F3: Pattern & Trend Extractor     - F5: Anomaly Reasoner / Explainer        |
+-----------------------------------------------------------------------------------+
                                         |
                                         v
+-----------------------------------------------------------------------------------+
|                       5. Application & Reporting Layer                            |
|    - F4: Interactive Timeline Dashboard - F6: Stream Comparison Engine             |
|    - F7: Automated Diagnostic Report Generator (PDF / HTML Export)                |
+-----------------------------------------------------------------------------------+
```

The system architecture diagram is available at [`07_DOCUMENTATION/Architecture_Diagram.png`](07_DOCUMENTATION/Architecture_Diagram.png).

---

## 9. Dataset Strategy

To ensure comprehensive real-world validation across all supported stream formats, a structured multi-dataset strategy has been established:

```
01_RAW_DATA/
├── 01_BBFRAME_GSE/    --> Wireshark DVB-S2 BBFrame and GSE capture samples (.pcap)
├── 02_GSE/            --> GSExtract parser sample streams (.ts)
├── 03_TS/             --> Real Astra 19.2°E satellite captures (France/Spain) & toolkit streams (.ts)
├── 04_RFI_AI/         --> Reference RFI classification & modulation recognition archives (.zip)
└── 05_REAL_DVB_S2/    --> Over-the-air Blockstream DVB-S2 capture (.ts + .pcap)
```

> **Data Storage & Repository Policy:**  
> All raw binary dataset files (`.ts`, `.pcap`, `.zip`, `.raw`) are retained **locally** on development workstations and are excluded from the GitHub repository via `.gitignore` to maintain repository performance and adhere to storage best practices. Refer to [`01_RAW_DATA/README.md`](01_RAW_DATA/README.md) for dataset documentation.

---

## 10. Project Folder Structure

```
PRJ_111_DVB-S2_Analysis/
├── .gitignore                      # Git exclusion rules for large datasets, binaries, and envs
├── README.md                       # Main project repository documentation
├── 01_RAW_DATA/                    # Real collected raw datasets (kept locally)
│   ├── 01_BBFRAME_GSE/             # DVB-S2 Baseband frame and GSE captures
│   ├── 02_GSE/                     # GSE extraction sample streams
│   ├── 03_TS/                      # MPEG Transport Stream satellite captures
│   ├── 04_RFI_AI/                  # RFI and modulation reference data archives
│   ├── 05_REAL_DVB_S2/             # Real-world over-the-air DVB-S2 broadcast data
│   └── README.md                   # Dataset inventory, organization, and local retention rules
├── 02_PROCESSED_DATA/              # Cleaned, de-encapsulated, and normalized intermediate streams
│   └── README.md                   # Description of processed data specifications
├── 03_FEATURE_DATA/                # Extracted numerical features, PID distributions, jitter series
│   └── README.md                   # Feature engineering and metric descriptions
├── 04_AI_MODELS/                   # Trained machine learning model architectures and serialized weights
│   └── README.md                   # Planned AI/ML model specifications
├── 05_CODE/                        # Application source code (Parsers, Analytics, UI, Reporting)
│   └── README.md                   # Code architecture and planned module structure
├── 06_RESULTS/                     # Generated experimental outputs, plots, benchmarks, reports
│   └── README.md                   # Analysis output and benchmarking log specifications
└── 07_DOCUMENTATION/               # Project reviews, academic documentation, and media assets
    ├── Architecture_Diagram.png    # System architecture diagram
    ├── Gantt_chart.png             # Five-phase project roadmap & schedule
    ├── PRJ_111_Review1_Documentation.docx # Comprehensive Review-1 technical report
    ├── Review-1_ppt.pptx           # Review-1 presentation slide deck
    ├── Review_0.pptx               # Review-0 project proposal deck
    └── README.md                   # Documentation index and review details
```

---

## 11. Current Project Status

The project is actively progressing through the planned milestones. A transparent breakdown of status is maintained below:

```
[==================== 35% Completed ====================>                    ]
```

### Completed Work
* [x] **Problem Formulation & Scope Definition:** Clear definition of DVB-S2 multi-format analysis challenges and boundaries.
* [x] **Seven Target Features Finalized:** Specification of Features F1 through F7.
* [x] **Multi-Dataset Strategy & Organization:** Ingestion hierarchy established across BBFrame, GSE, TS, and RFI datasets.
* [x] **System Architecture Concept:** Five-layer architecture designed and mapped.
* [x] **Project Review-0 Presentation:** Initial project proposal successfully submitted.
* [x] **Project Review-1 Documentation & Presentation:** Comprehensive Review-1 report, presentation deck, and Gantt roadmap finalized.

### Ongoing Work
* [/] **Dataset Inspection & Compatibility Validation:** Analyzing packet structure and integrity of existing raw captures.
* [/] **Literature Review Refinement:** Deep-dive into anomaly detection techniques for satellite telemetry.
* [/] **Parser Design & Prototyping:** Designing modular parsers for BBFrame, GSE, and MPEG-TS formats.
* [/] **Repository Preparation:** Establishing clean project structure and version control practices.

### Planned / Not Yet Implemented
* [ ] **Full Stream Parsing Implementation:** Complete decoding engines for BBFrame, GSE, and TS containers.
* [ ] **Data Preprocessing Pipelines:** Automated filtering, time-series alignment, and normalization.
* [ ] **Feature Extraction Engine:** Quantitative calculation of health indices, CC errors, and jitter metrics.
* [ ] **AI/ML Model Training & Inference:** Training anomaly detection and pattern classification models.
* [ ] **Application Dashboard & Visualizations:** Frontend timeline navigation and metric visualization.
* [ ] **Automated Report Generation Module:** PDF/HTML diagnostic report export.
* [ ] **End-to-End Testing & Validation:** Rigorous testing on real-world satellite streams and benchmark reporting.

---

## 12. Planned Development Phases

Project execution is structured across five sequential phases as illustrated in [`07_DOCUMENTATION/Gantt_chart.png`](07_DOCUMENTATION/Gantt_chart.png):

```
+-------------------------------------------------------------------------------+
| Phase 1: Foundation               | Problem Scope, Literature, Data Plan      | [COMPLETED / ONGOING]
+-------------------------------------------------------------------------------+
| Phase 2: Data & Core Processing   | Dataset Validation, Parsers, Features     | [CURRENT FOCUS]
+-------------------------------------------------------------------------------+
| Phase 3: Intelligent Analysis     | AI/ML Anomaly Detection, Patterns, XAI    | [PLANNED]
+-------------------------------------------------------------------------------+
| Phase 4: Application Layer        | UI Dashboard, Comparison, Reports, App    | [PLANNED]
+-------------------------------------------------------------------------------+
| Phase 5: Validation & Delivery    | Comprehensive Testing, Final Review       | [PLANNED]
+-------------------------------------------------------------------------------+
```

---

## 13. Team Members

| Name | Role | Primary Responsibilities |
| :--- | :--- | :--- |
| **Rakeshwar** | **Core Development & Technical Lead** | Backend architecture, frontend integration, AI/ML model development, stream processing, parser implementation, feature extraction, system integration. |
| **Samad** | **Testing, Validation & Development** | Testing lead, validation protocols, literature review, technical documentation lead, report preparation, supporting development. |
| **Vengal Rao** | **Frontend, Visualization & Development** | Frontend development, interactive visualization components, dashboard design, presentation preparation, supporting development. |

---

## 14. Future Development
* **Live Real-Time Streaming:** Extending stream parsers to process live UDP/IP multicast and SDR baseband inputs.
* **Hardware Acceleration:** Exploring accelerated parsing for high-bitrate satellite transponders.
* **Extended Anomaly Taxonomy:** Expanding machine learning classifications for complex RF interference and transponder failure profiles.
* **Cloud & Edge Deployment:** Packaging the analysis platform as a lightweight containerized diagnostic service.

---

## References & Standards
1. **ETSI EN 302 307-1:** *Digital Video Broadcasting (DVB); Second Generation framing structure, channel coding and modulation systems for Broadcasting, Interactive Services, News Gathering and other broadband satellite applications; Part 1: DVB-S2.*
2. **ETSI TS 102 606-1:** *Digital Video Broadcasting (DVB); Generic Stream Encapsulation (GSE) Protocol.*
3. **ISO/IEC 13818-1:** *Information technology — Generic coding of moving pictures and associated audio information: Systems (MPEG-2 Transport Stream).*
