# Development of a Multi-Format DVB-S2 Receiver Output Stream Analyzer with Anomaly Detection and Diagnostic Reporting

**Sk Samad**, **Y Vengala Rao**, **C Rakeshwar**  
*Department of Computer Science and Engineering, Presidency University, Bengaluru, India*  
*Project Guide: Irfan Rajab Bhat, Assistant Professor*

---

### Abstract
Digital Video Broadcasting - Second Generation (DVB-S2, ETSI EN 302 307) provides the physical and data-link framing structure for satellite broadband, high-definition television distribution, and cellular backhaul. Modern satellite receivers demodulate high-frequency radio frequency (RF) downlinks and emit post-demodulator digital output streams across multiple heterogeneous encapsulation formats, primarily MPEG-2 Transport Streams (MPEG-TS, ISO/IEC 13818-1), Generic Stream Encapsulation (GSE, ETSI TS 102 606), and DVB-S2 Baseband Frames (BBFrame). Analyzing receiver output streams across these formats presents an engineering challenge: each format possesses fundamentally different framing boundaries, header structures, and error-propagation characteristics, meaning conventional single-format protocol analyzers do not natively provide the required unified cross-format workflow.

This paper presents the architecture, methodology, and empirical validation of **PRJ_111**, a specialized software application engineered for comprehensive analysis and processing of multi-format DVB-S2 receiver output streams. The application establishes a seven-feature analytical pipeline (F1–F7): (F1) deterministic stream health evaluation executing selected Priority-1 broadcast stream integrity indicators inspired by ETSI TR 101 290 principles; (F2) unsupervised statistical anomaly detection via format-isolated Isolation Forest models calibrated on spatial window telemetry; (F3) structural pattern and multiplex distribution detection; (F4) spatial activity timeline generation indexed strictly by physical byte offsets and container sequence numbers without synthetic clock fabrication; (F5) bounded Z-score diagnostic anomaly explanations ($|z| \le 20.0$) with explicit deviation directionality; (F6) a differential stream comparison engine governed by a strict semantic barrier isolating valid physical invariants from format-incomparable metrics; and (F7) automatic multi-format diagnostic report generation organized under a formal tripartite epistemological taxonomy (*Observed Fact*, *Statistical Finding*, and *Engineering Interpretation*).

The proposed system is implemented as a standalone local engineering workstation with no cloud-service dependency, utilizing standard scientific Python packages. Experimental evaluation across authoritative satellite broadcast captures demonstrates deterministic health accounting (100.0% health on clean streams; 99.67% on corrupted streams with exact transport error tracking), unsupervised anomaly detection flagging structural boundary transitions and multiplex concentrations, and strict semantic isolation in cross-format comparisons. The entire software implementation is validated by an automated test suite comprising 240 tests (207 backend and 33 frontend tests) achieving a 100% pass rate with zero failures and zero errors.

**Index Terms**—DVB-S2, MPEG Transport Stream, Generic Stream Encapsulation, BBFrame, Stream Analysis, Anomaly Detection, Isolation Forest, Feature Extraction, Digital Video Broadcasting, Receiver Output Analysis.

---

## I. INTRODUCTION

The Second Generation Digital Video Broadcasting via Satellite standard (DVB-S2) is the foundational physical and framing specification for high-throughput telecommunication satellites [1]. Operating directly behind the satellite low-noise block downconverter (LNB) and intermediate-frequency (IF) tuner, the digital satellite receiver demodulator performs carrier synchronization, matched filtering, forward error correction (FEC) decoding using low-density parity-check (LDPC) and Bose-Chaudhuri-Hocquenghem (BCH) codes, and stream deframing. The resulting post-demodulator digital output represents the primary data boundary between the satellite physical channel and terrestrial consumer or enterprise networking appliances [7].

In modern satellite ground stations, consumer set-top boxes, and satellite broadband terminals, receiver output is not uniform. Depending on the transmitted service profiles, transponder configuration, and downstream equipment, the digital output stream is delivered in one of three standardized digital framing representations [1], [2], [3]:
1. **MPEG-2 Transport Stream (MPEG-TS):** Characterized by fixed 188-byte containers, periodic synchronization markers (`0x47`), 13-bit Program Identifiers (PIDs), and continuity counters, predominantly utilized for linear broadcast television and legacy digital distribution [3].
2. **Generic Stream Encapsulation (GSE):** Characterized by variable-length protocol data units (PDUs), 2-bit start/end fragmentation flags, 16-bit EtherType protocol identifiers, and 32-bit cyclic redundancy check (CRC-32) verification, standard in satellite IP broadband and enterprise backhaul [2].
3. **DVB-S2 Baseband Frames (BBFrame):** The native physical-layer container consisting of an 80-bit Baseband Header (BBHeader), mode adaptation fields (MATYPE-1/2), User Packet Length (UPL), Data Field Length (DFL), and an 8-bit CRC header protection code [1].

Analyzing digital receiver output streams is critical for broadcast verification, transponder capacity planning, transmission debugging, and stream integrity assessment. However, analyzing these heterogeneous representations using conventional software tools presents operational limitations [12]. Generic network protocol analyzers (such as Wireshark) treat captured data as network frames, requiring external dissector plugins that lack native support for raw concatenated TS streams, non-Ethernet encapsulated GSE byte sequences, or baseband frame telemetry. Conversely, dedicated broadcast test and measurement instruments are tailored primarily to MPEG-TS, providing limited native support for modern DVB-S2 baseband frames or GSE streams [8], [12].

To address this gap, this project develops **PRJ_111**: an extensible and mathematically grounded software application for unified analysis and processing of multi-format DVB-S2 receiver output streams. PRJ_111 is designed as a post-demodulator digital stream analyzer rather than a generic network packet sniffer, emphasizing deterministic framing verification, unsupervised statistical anomaly detection, spatial activity indexing, diagnostic explanations, semantic cross-format comparison, and automated reporting.

---

## II. PROBLEM STATEMENT

When analyzing post-demodulator digital receiver outputs in satellite communications, system engineers face three core challenges:

1. **Framing Heterogeneity and Parser Brittleness:** Digital receiver output streams arrive as unindexed raw binary files (`.ts`, `.gse`, `.bin`, `.pcap`). Format boundaries vary from fixed 188-byte packets to variable-length network PDUs (up to 4,096 bytes) and fixed-block forward error correction frames (up to 7,275 bytes in normal FEC frame configurations). Ingestion layers that rely on naive file extension checking frequently misidentify streams, while streaming parsers that lack periodic synchronization recovery fail upon encountering corrupted bits.
2. **Lack of Common Telemetry Across Disparate Framing Layers:** Transport Stream packet counts, GSE PDU counts, and Baseband Frame counts describe physically distinct encapsulation entities. Comparing or unifying metrics across these formats without mathematical rigor results in false equivalence, comparing quantities with incompatible dimensions and misleading ground station operators.
3. **Epistemic Over-Claiming in Stream Telemetry:** Many monitoring applications compute synthetic clock timestamps, calculate fictitious Megabits-per-second (Mbps) throughputs in offline files where no receiver clock telemetry is present, or assert ungrounded physical-layer causal inferences (e.g., attributing a continuity counter error to "rain fade" or "transponder failure" without demodulator signal-to-noise ratio measurements).

The technical objective of PRJ_111 is to formulate, implement, and validate a unified software system that ingests multi-format receiver output streams, executes deterministic framing analysis, extracts mathematically grounded common and format-specific features, detects anomalies via unsupervised statistical learning, explains deviations with bounded dispersion metrics, compares streams across a strict semantic barrier, and generates automated diagnostic reports without violating domain-safety constraints.

---

## III. PROJECT OBJECTIVES

The specific technical objectives of the PRJ_111 project are defined as follows:

1. **Multi-Format Stream Ingestion:** Ingest raw binary receiver output captures and reliably detect stream format (MPEG-TS, GSE, DVB-S2 BBFrame) through content-aware byte inspection.
2. **Deterministic Stream Parsing:** Implement parsers capable of extracting complete header syntax, verifying cyclic redundancy checks, detecting continuity counter discontinuities, tracking Transport Error Indicators, and resynchronizing after bit errors.
3. **Unified Feature Architecture:** Formulate a structured feature set that separates invariant physical metrics (`CommonMetrics`) from format-specific metrics (`TSSpecificMetrics`, `GSESpecificMetrics`, `BBFrameSpecificMetrics`).
4. **Stream Health Evaluation (Feature F1):** Implement deterministic integrity indicators inspired by ETSI TR 101 290 principles to compute objective stream health scores ($[0.0, 100.0]$) and categorical classifications (`HEALTHY`, `DEGRADED`, `CRITICAL`).
5. **AI-Based Anomaly Detection (Feature F2):** Deploy format-isolated, unsupervised Isolation Forest machine learning models to detect structural, volume, and entropy anomalies across rolling spatial windows without relying on unavailable labeled training sets.
6. **Pattern and Multiplex Distribution Detection (Feature F3):** Quantify PID multiplex concentrations, Shannon entropy, PAT/PMT recurrence, GSE protocol distributions, and BBFrame transmission mode transitions (ACM/CCM, SIS/MIS).
7. **Spatial Timeline Visualization (Feature F4):** Generate continuous spatial activity timelines indexed strictly by physical byte offsets and container sequence numbers, visualizing rolling health, anomaly scores, and payload density without fabricating clock timestamps.
8. **Diagnostic Anomaly Explanation (Feature F5):** Formulate an explanatory model based on Bounded Z-Score Magnitude ($|z| \le 20.0$) with explicit deviation directionality to attribute detected anomalies to specific feature variations.
9. **Semantic Stream Comparison Engine (Feature F6):** Establish an automated differential engine that strictly enforces a cross-format semantic barrier (2 comparable metrics vs. 9 non-comparable metrics), employs direct-index window alignment ($\min(N_A, N_B)$), and classifies metric differences into an objective four-tier significance hierarchy.
10. **Automatic Report Generation (Feature F7):** Synthesize authoritative F1–F6 analytical results into exportable reports (JSON, Markdown, Plain Text, Standalone HTML5) categorized under a formal tripartite taxonomy (*Observed Fact*, *Statistical Finding*, *Engineering Interpretation*).
11. **Software Verification and Regression Integrity:** Validate the complete system through automated unit, integration, and regression testing with zero test failures.

---

## IV. RELATED WORK AND LITERATURE REVIEW

The technical foundation of PRJ_111 synthesizes international telecommunications standards, satellite protocol engineering, unsupervised anomaly detection, and empirical broadcast stream monitoring.

### A. DVB-S2 and Framing Standards
The DVB-S2 standard (ETSI EN 302 307-1) defines the framing and channel coding specification for satellite communications, introducing Adaptive Coding and Modulation (ACM) and Native Baseband Framing [1]. Morello and Mignone [7] detailed the physical-layer mechanisms of DVB-S2, demonstrating how variable-length user data packets are encapsulated into fixed-size baseband frames protected by inner LDPC and outer BCH codes. Casini et al. [14] analyzed modulation schemes ranging from QPSK to 32-APSK, establishing the operational roles of the 80-bit Baseband Header (BBHeader), Roll-Off factors ($\alpha \in \{0.20, 0.25, 0.35\}$), and Data Field Length (DFL).

For network layer transport, Fairhurst and Collini-Nocker [8] formulated the Generic Stream Encapsulation (GSE) protocol (ETSI TS 102 606), designed to replace Multi-Protocol Encapsulation (MPE over MPEG-TS) by reducing framing overhead [2], [16]. GSE defines variable-size protocol data units carrying native IP packets with optional label re-use and fragment-level CRC-32 protection. Meanwhile, digital television broadcast transmission continues to rely on the MPEG-2 Transport Stream standard (ISO/IEC 13818-1) [3]. Measurement guidelines for digital television broadcast systems are standardized in ETSI TR 101 290 [4], defining three priority levels of measurement parameters. Priority-1 parameters represent fundamental transmission integrity: TS synchronization loss, Transport Error Indicator (TEI) assertions, and Continuity Counter (CC) errors [4], [12].

### B. Broadcast Stream Monitoring and Protocol Inspection
Luisi et al. [12] evaluated digital video broadcast stream monitoring techniques, demonstrating that while hardware-based TS analyzers reliably measure ETSI TR 101 290 Priority-1 errors, they fail to support modern multi-protocol IP encapsulations (GSE and BBFrames) emitted by hybrid ground terminals. Generic network packet inspection tools, surveyed by Minoli [11], provide inspection of terrestrial Ethernet stacks but treat raw post-demodulator digital bitstreams as unstructured payloads unless wrapped in network capture headers (such as PCAP). PRJ_111 builds directly upon these observations by providing native, modular parsers for MPEG-TS, GSE, and BBFrames directly from raw receiver bitstreams.

### C. Unsupervised Anomaly Detection in Communication Streams
Anomaly detection in streaming telemetry has been surveyed by Chandola et al. [9] and Pimentel et al. [10]. Traditional statistical process control (SPC) relies on fixed thresholding, which presents difficulties in multiplexed broadcast channels where packet rates vary dynamically with video complexity and statistical multiplexing. Supervised classification approaches require extensive collections of ground-truth labeled anomaly datasets [9], [13]. In operational DVB-S2 receiver output monitoring, labeled anomalous bitstreams are rarely available; receiver streams reflect proprietary transmissions, encrypted carrier feeds, or transient operational errors.

To address unlabeled streaming data, Liu et al. [5], [6] introduced the **Isolation Forest** algorithm. Isolation Forest isolates anomalies explicitly rather than profiling normal data points, constructing ensembles of random isolation trees (iTrees). Because anomalies possess distinct feature attributes, they are isolated closer to the root of the tree, resulting in shorter average path lengths [5]. Baggio et al. [13] evaluated unsupervised machine learning models for network traffic anomaly detection, demonstrating that Isolation Forest achieves computational efficiency ($O(n \log n)$ training complexity) and robust outlier detection in streaming feature spaces compared to distance-based models ($k$-NN) or density-based clustering ($k$-means) [19], [20]. PRJ_111 adapts the Isolation Forest baseline to DVB-S2 stream telemetry, executing window-partitioned, format-isolated anomaly detection with calibrated decision boundaries.

---

## V. PROPOSED SYSTEM ARCHITECTURE

The overall architecture of the PRJ_111 DVB-S2 Receiver Output Stream Analyzer is illustrated in Fig. 1. The system is architected as a six-stage pipeline that ingests raw post-demodulator digital receiver output, processes framing syntax, extracts unified features, executes analytical engines (F1–F3), generates spatial timeline telemetry (F4), diagnoses deviations (F5), evaluates dual-stream differentials (F6), and outputs structured diagnostic reports (F7) via an engineering workstation interface.

```
       +-------------------------------------------------------------+
       |               STAGE 1: DVB-S2 Receiver Output               |
       |                (Raw Bitstream / PCAP Capture)               |
       +-------------------------------------------------------------+
                                      |
                                      v
       +-------------------------------------------------------------+
       |                 STAGE 2: Ingestion & Parsing                |
       |  - Content-Aware Format Sniffer (TS / GSE / BBFrame)        |
       |  - Modular Parsers (188B TS / Variable GSE / 80b BBHeader)  |
       +-------------------------------------------------------------+
                                      |
                                      v
       +-------------------------------------------------------------+
       |             STAGE 3: Unified Feature Extraction             |
       |  - Common Framing Telemetry (CommonMetrics)                 |
       |  - Format-Specific Native Metrics (TSSpecific / GSE / BB)   |
       +-------------------------------------------------------------+
                                      |
                 +--------------------+--------------------+
                 |                                         |
                 v                                         v
+---------------------------------+       +---------------------------------+
|   STAGE 4A: Stream Health (F1)  |       |  STAGE 4B: AI Anomaly Det. (F2) |
| - Selected Priority-1 Checks    |       | - Unsupervised Isolation Forest |
| - Threshold Deductive Scoring   |       | - Format-Isolated Calibration   |
+---------------------------------+       +---------------------------------+
                 |                                         |
                 +--------------------+--------------------+
                                      |
                                      v
       +-------------------------------------------------------------+
       |         STAGE 4C: Pattern & Entropy Detection (F3)          |
       |  - PID Multiplex Distributions & Shannon Entropy            |
       |  - Protocol Frequencies & Frame Mode Adaptation Transitions |
       +-------------------------------------------------------------+
                                      |
                                      v
       +-------------------------------------------------------------+
       |          STAGE 5A: Spatial Activity Timeline (F4)           |
       |  - Physical Byte-Offset & Unit Sequence Number Indexing     |
       |  - Synchronized Rolling Health, Anomaly & Volume Series     |
       +-------------------------------------------------------------+
                                      |
                                      v
       +-------------------------------------------------------------+
       |          STAGE 5B: Diagnostic Anomaly Explanation (F5)      |
       |  - Bounded Z-Score Deviation (|z| <= 20.0) with Direction   |
       |  - Operational Dispersion Floor & Subsystem Attribution     |
       +-------------------------------------------------------------+
                                      |
                                      v
       +-------------------------------------------------------------+
       |            STAGE 6A: Stream Comparison Engine (F6)          |
       |  - Cross-Format Semantic Barrier (2 Comp. vs 9 Non-Comp.)   |
       |  - Direct-Index Window Alignment & Decile Trajectories      |
       |  - Four-Tier Significance Hierarchy (Negligible to Critical)|
       +-------------------------------------------------------------+
                                      |
                                      v
       +-------------------------------------------------------------+
       |         STAGE 6B: Automatic Report Generation (F7)          |
       |  - Tripartite Taxonomy (Facts, Statistics, Interpretations) |
       |  - Multi-Format Export (JSON, Markdown, Plain Text, HTML5)  |
       +-------------------------------------------------------------+
                                      |
                                      v
       +-------------------------------------------------------------+
       |            STAGE 6C: Engineering Workstation UI             |
       |  - RESTful Backend Gateway (Python ThreadingHTTPServer)     |
       |  - Interactive SPA Dashboard (HTML5 / Vanilla CSS / ES6 JS) |
       +-------------------------------------------------------------+
```

```
Fig. 1. End-to-End Architectural Pipeline of the PRJ_111 DVB-S2 Receiver Output Stream Analyzer (Stages 1 through 6).
```

---

## VI. FORMAT-SPECIFIC PROCESSING

The ingestion and parsing layer operates directly on raw binary stream captures, providing modular decoders tailored to each standard.

### A. MPEG-2 Transport Stream (MPEG-TS) Processing
The MPEG-TS parser processes continuous 188-byte containers specified in ISO/IEC 13818-1 [3]. Each packet header is decoded as:
- **Sync Byte:** Must equal `0x47` (01000111 binary). If the parser encounters a non-`0x47` byte, it increments `sync_byte_errors` and scans forward byte-by-byte for the next valid synchronization byte.
- **Transport Error Indicator (TEI):** Bit 7 of byte 1. Set to 1 in the packet header to indicate that an uncorrected error exists within the packet container.
- **Payload Unit Start Indicator (PUSI):** Bit 6 of byte 1. Indicates that the packet payload begins with a Program Association Table (PAT), Program Map Table (PMT), or Packetized Elementary Stream (PES) header.
- **Transport Priority:** Bit 5 of byte 1.
- **Program Identifier (PID):** 13-bit value ($[0, 8191]$) defining the logical elementary stream multiplex. Null packets are identified by $\text{PID} = 8191$ (`0x1FFF`).
- **Transport Scrambling Control (TSC):** Bits 7–6 of byte 3.
- **Adaptation Field Control (AFC):** Bits 5–4 of byte 3, indicating payload-only (`01`), adaptation-field-only (`10`), or adaptation-field followed by payload (`11`).
- **Continuity Counter (CC):** 4-bit cyclic counter ($[0, 15]$) incremented per PID. Discontinuities ($\text{CC}_{\text{curr}} \ne (\text{CC}_{\text{prev}} + 1) \pmod{16}$) indicate an observed sequence discontinuity for the corresponding PID.

### B. Generic Stream Encapsulation (GSE) Processing
The GSE parser decodes variable-size protocol data units adhering to ETSI TS 102 606 [2]:
- **Start/End Flags (S, E):** 2 bits defining PDU fragmentation. $S=1, E=1$ indicates an unfragmented PDU; $S=1, E=0$ indicates the first fragment; $S=0, E=0$ intermediate fragments; $S=0, E=1$ the last fragment.
- **GSE Length:** 12-bit field specifying total PDU length in bytes ($[1, 4095]$).
- **Protocol Type:** 16-bit EtherType identifier (e.g., `0x0800` for IPv4, `0x86DD` for IPv6) or GSE extension header type (`GSE_EXT_NPA`).
- **Label Type:** 2 bits specifying 6-byte (`LABEL_6B`), 3-byte (`LABEL_3B`), or label-less (`LABEL_NONE`) addressing.
- **Fragment ID & Total Length:** Present in fragmented PDUs to facilitate payload reassembly.
- **CRC-32 Verification:** 32-bit CRC polynomial calculated over the PDU payload and headers for complete PDUs and last fragments.

### C. DVB-S2 Baseband Frame (BBFrame) Processing
The BBFrame parser decodes native satellite baseband frames specified in ETSI EN 302 307 [1]. Each frame contains an 80-bit (10-byte) BBHeader followed by the data field:
- **MATYPE-1 (Mode Adaptation Type 1):**
  - Stream Input (TS/GS): Bit 7–6 indicates Single Input Stream (SIS) or Multiple Input Streams (MIS).
  - Modulation & Coding: Bit 5 indicates Constant Coding & Modulation (CCM) or Adaptive Coding & Modulation (ACM).
  - ISSYI: Bit 4 indicates Input Stream Synchronization Indicator.
  - NPD: Bit 3 indicates Null Packet Deletion.
  - Roll-Off Factor ($\alpha$): Bits 1–0 specify $\alpha = 0.35$ (`00`), $\alpha = 0.25$ (`01`), or $\alpha = 0.20$ (`10`).
- **MATYPE-2:** Input Stream Identifier (ISI) when MIS is active.
- **User Packet Length (UPL):** 16-bit integer defining the length of encapsulated user packets.
- **Data Field Length (DFL):** 16-bit integer defining the active payload bits in the frame ($[0, K_{\text{bch}}]$). **DFL is expressed in bits**, representing the usable user data field within the physical baseband frame.
- **SYNC:** 8-bit copy of user packet synchronization marker.
- **SYNCD:** 16-bit distance in bits from the start of the DATA FIELD to the first user packet.
- **CRC-8:** 8-bit error detection code computed over the preceding 72 bits using polynomial $G(x) = x^8 + x^7 + x^6 + x^4 + x^2 + 1$. Frames failing CRC-8 validation are flagged as corrupted.

---

## VII. UNIFIED FEATURE EXTRACTION

To perform analysis across disparate formats without creating invalid semantic conflations, PRJ_111 establishes the `UnifiedStreamFeatureSet` architecture. Telemetry is bifurcated into physical invariants and native format-specific metrics:

```
       UnifiedStreamFeatureSet
       ├── CommonMetrics (Physical Invariants)
       │   ├── total_units (int)
       │   ├── valid_units (int)
       │   ├── invalid_units (int)
       │   ├── integrity_ratio (float [0.0, 1.0])
       │   ├── total_payload_bytes (int)
       │   ├── mean_payload_bytes (float)
       │   ├── payload_ratio (float)
       │   ├── error_count (int)
       │   ├── error_rate (float)
       │   └── entropy (float)
       ├── TSSpecificMetrics (Format-Isolated)
       │   ├── pid_counts (Dict[int, int])
       │   ├── sync_byte_errors, tei_errors, cc_errors (int)
       │   └── pcr_pid_count, null_packet_count (int)
       ├── GSESpecificMetrics (Format-Isolated)
       │   ├── protocol_counts (Dict[str, int])
       │   ├── fragmented_pdus, unfragmented_pdus (int)
       │   └── crc32_failures (int)
       └── BBFrameSpecificMetrics (Format-Isolated)
           ├── coding_modulation_modes (Dict[str, int])
           ├── stream_input_modes (Dict[str, int])
           └── roll_off_factors (Dict[str, int])
```

Where a metric is inapplicable to a given format (e.g., `pcr_pid_count` on GSE or `crc32_failures` on MPEG-TS), the feature vector assigns `None` or an isolated zero rather than manufacturing fictitious values.

---

## VIII. FEATURE F1: STREAM HEALTH ANALYSIS

Feature F1 executes deterministic stream health analysis. PRJ_111 evaluates **selected stream integrity indicators inspired by ETSI TR 101 290 principles** [4].

### A. Evaluated Integrity Indicators
For MPEG-TS captures, F1 evaluates three fundamental Priority-1 integrity indicators:
1. **Sync Byte (`0x47`) Integrity:** Evaluates synchronization loss events. A pass condition requires periodic alignment on byte `0x47` with $\ge 99.0\%$ validity across yielded packets.
2. **Transport Error Indicator (TEI):** Monitors bit 7 of the packet header. Assertion of $\text{TEI} = 1$ indicates that the packet header has been marked as containing transmission errors.
3. **Continuity Counter (CC):** Tracks sequential packet counter monotonic progression per active PID. Discontinuities in sequence indicate an observed packet sequence gap for the corresponding PID.

For GSE, F1 evaluates PDU header syntax, start/end flag consistency, and CRC-32 integrity. For BBFrame, F1 evaluates BBHeader 72-bit CRC-8 verification and Data Field Length ($DFL \le K_{\text{bch}}$) bounds.

### B. Deductive Rule-Based Health Scoring
Rather than employing arbitrary penalty weight sums, PRJ_111 implements the transparent threshold-driven deductive scoring model encoded in `analysis/health.py`. Each evaluated spatial window $W_i$ starts from an initial healthy score of $100.0\%$:
- **Sync Integrity (ETSI TR 101 290 P1.1):**
  - Critical ($< 95.00\%$): Deducts $40.0\%$
  - Warning ($< 99.99\%$): Deducts $20.0\%$
- **Transport Error Indicator (ETSI TR 101 290 P1.3):**
  - Critical ($> 1.00\%$ error rate): Deducts $30.0\%$
  - Warning ($> 0.00\%$ error rate): Deducts $15.0\%$
- **Continuity Counter Errors (ETSI TR 101 290 P1.4):**
  - Critical ($> 0.50\%$ error rate): Deducts $30.0\%$
  - Warning ($> 0.01\%$ error rate): Deducts $15.0\%$
- **Null Packet Ratio (Transponder Utilization):**
  - Idle Transponder Beacon ($> 99.90\%$ null packets): Deducts $10.0\%$
  - High Padding Ratio ($> 95.00\%$ null packets): Deducts $5.0\%$
- **Header Malformations:**
  - Critical ($> 10$ malformed headers): Deducts $20.0\%$
  - Warning ($> 1$ malformed header): Deducts $10.0\%$

The overall stream health score $H$ is computed as the arithmetic mean of individual window health scores across all $N$ evaluated windows:
$$H = \frac{1}{N} \sum_{i=1}^N H(W_i)$$
Streams are categorized into operational states:
- **`HEALTHY`:** $H \ge 99.0\%$
- **`DEGRADED` / `WARNING`:** $80.0\% \le H < 99.0\%$
- **`CRITICAL`:** $H < 80.0\%$

---

## IX. FEATURE F2: AI-BASED ANOMALY DETECTION

Feature F2 implements unsupervised anomaly detection across rolling spatial windows using the **Isolation Forest** algorithm [5] through Scikit-learn.

### A. Mathematical Formulation and Implementation
Given a spatial window $W_i$ containing $K$ units (where $K=200$ for TS, $K=3$ for GSE, and $K=50$ for BBFrame), an $m$-dimensional feature vector $\mathbf{x}_i \in \mathbb{R}^m$ is extracted, capturing payload volume, integrity ratio, error rate, entropy, unit size variance, and format-specific telemetry.

The anomaly detector instantiates an ensemble of $T = 100$ isolation trees (`n_estimators=100`, `contamination=0.05`, `random_state=42`). The raw decision output $d(\mathbf{x}) \in \mathbb{R}$ is computed using Scikit-learn's `decision_function`, where negative values designate outliers and positive values designate inliers. To map this output to a normalized, intuitive anomaly score $s(\mathbf{x}) \in [0.0, 1.0]$, PRJ_111 applies a centered logistic sigmoid transformation:
$$s(\mathbf{x}) = \frac{1}{1 + e^{8.0 \cdot d(\mathbf{x})}}$$

At the nominal decision boundary ($d(\mathbf{x}) = 0.0$), the score evaluates to exactly $s = 0.5000$. Outliers ($d(\mathbf{x}) < 0$) map to $s > 0.5000$, while regular inliers ($d(\mathbf{x}) > 0$) map to $s < 0.5000$. Anomaly classification is determined by the decision threshold:
$$\text{Anomaly Flag} = \begin{cases} \text{TRUE}, & s(\mathbf{x}_i) \ge 0.5000 \\ \text{FALSE}, & s(\mathbf{x}_i) < 0.5000 \end{cases}$$

### B. Epistemic Boundary on Supervised Metrics
**Domain Rule:** Because operational satellite receiver output bitstreams are inherently unlabeled, **no ground-truth anomaly annotations exist** for off-air broadcast captures. Therefore, PRJ_111 **avoids asserting classification accuracy, precision, recall, or F1-score** on real broadcast data. Model sensitivity is validated through controlled synthetic perturbation experiments, wherein known corruptions (bit flips, synthetic sync byte drops, and container truncations) are injected into verified captures to demonstrate that the detector flags abnormal intervals with $s \ge 0.5000$.

---

## X. FEATURE F3: PATTERN DETECTION

Feature F3 identifies structural patterns and multiplex characteristics across stream progress:
- **MPEG-TS PID Distribution:** Computes individual packet counts and percentage shares per PID. The dominant PID and Shannon entropy are evaluated:
  $$H_{\text{PID}} = -\sum_{k=1}^P p_k \log_2 p_k, \quad p_k = \frac{N_k}{\sum_{j} N_j}$$
- **PAT/PMT Program Structure:** Identifies Program Association Tables ($\text{PID} = 0$) and Program Map Tables, tracking program multiplex recurrence.
- **GSE Protocol Mapping:** Classifies encapsulated protocol types (`GSE_EXT_NPA`, IPv4, IPv6) and quantifies fragmentation ratios ($\frac{N_{\text{frag}}}{N_{\text{total}}}$).
- **BBFrame Mode Transitions:** Tracks shifts in modulation profiles (ACM vs. CCM), Single vs. Multiple Input Stream allocations, and DFL distribution clustering.

---

## XI. FEATURE F4: SPATIAL ACTIVITY TIMELINE

Feature F4 provides continuous visual mapping of stream activity across spatial progress.

### Absence of Fabricated Timestamps
**Epistemic Rule:** Offline receiver bitstreams captured from demodulator test points lack calibrated broadcast wall-clock telemetry. Assigning synthetic timestamps or calculating fictitious throughput rates (e.g., "15.4 Mbps") creates false precision. PRJ_111 indexes all timeline events strictly by:
1. **Physical Byte Offset:** $[B_{\text{start}}, B_{\text{end}}]$ indicating exact octet positions in the capture file.
2. **Container Sequence Index:** Unit indices $[U_{\text{start}}, U_{\text{end}}]$ tracking sequential packet, PDU, or frame numbers.

The timeline visualizes rolling F1 stream health ($[0, 100\%]$), F2 anomaly scores ($[0.0, 1.0]$) alongside the $0.5000$ threshold line, payload density (KB per window), and format-specific telemetry (PID entropy or PDU length).

---

## XII. FEATURE F5: DIAGNOSTIC ANOMALY EXPLANATION

Feature F5 bridges unsupervised machine learning and domain engineering by attributing flagged anomalies to specific metric deviations.

### A. Bounded Z-Score Deviation Formulation
For each feature $j$ in anomalous window $W_i$, deviation from the stream baseline is evaluated using an operational dispersion model:
$$z_{i, j} = \frac{x_{i, j} - \mu_j}{\max(\sigma_j, \, \epsilon_j)}$$
where $\mu_j$ is the stream mean for feature $j$, $\sigma_j$ is standard deviation, and $\epsilon_j$ is an operational dispersion floor preventing division-by-zero on invariant channels.

To eliminate unbounded numerical artifacts while maintaining mathematical interpretability, PRJ_111 bounds the Z-score:
$$z_{\text{bounded}} = \operatorname{clamp}(z_{i, j}, -20.0, +20.0)$$
The magnitude $|z_{\text{bounded}}|$ is accompanied by an explicit deviation direction: `ABOVE_BASELINE` ($z > 0$) or `BELOW_BASELINE` ($z < 0$).

### B. Physical-Layer Domain Safety Guard
**Epistemic Boundary:** PRJ_111 operates strictly on digital post-demodulator bitstreams. Without access to baseband constellation measurements or RF tuner AGC levels, the application **avoids asserting physical-layer root causes**. F5 diagnoses are constrained to digital observations (e.g., "Elevated adaptation field frequency" or "Recording termination boundary"), avoiding speculative claims such as "rain fade," "LNB drift," or "transponder power drop."

---

## XIII. FEATURE F6: STREAM COMPARISON ENGINE

Feature F6 provides differential comparison between two analyzed streams (**Stream A** and **Stream B**).

### A. The Cross-Format Semantic Barrier
A key element of PRJ_111 is the **Cross-Format Semantic Barrier**. Metrics sharing identical nomenclature inside `CommonMetrics` are **not** assumed to be comparable across formats. As detailed in Table VI, physical equivalence is enforced:
- **Comparable Metrics (2):** `total_payload_bytes` (an octet of user data represents an invariant physical quantity) and `integrity_ratio` (dimensionless syntactic compliance proportion $[0.0, 1.0]$).
- **Non-Comparable Metrics (9):** `total_units`, `valid_units`, `invalid_units`, `truncated_units`, `mean_payload_bytes`, `payload_ratio`, `error_count`, `error_rate`, and `entropy` are blocked cross-format with explicit engineering justifications.

### B. Difference Quantification and Zero-Baseline Handling
For comparable metrics, differences are quantified without mathematical singularities:
$$\Delta_{\text{abs}} = B - A, \quad \Delta_{\text{rel}} = \begin{cases} \frac{B - A}{A} \times 100\%, & A > 0 \\ \text{Undefined (Critical)}, & A = 0, B > 0 \\ 0.0\%, & A = 0, B = 0 \end{cases}$$
Differences are classified into a four-tier significance hierarchy:
- **`NEGLIGIBLE`:** $|\Delta_{\text{rel}}| < 2.0\%$
- **`MINOR`:** $2.0\% \le |\Delta_{\text{rel}}| < 10.0\%$
- **`SUBSTANTIAL`:** $10.0\% \le |\Delta_{\text{rel}}| < 50.0\%$
- **`CRITICAL`:** $|\Delta_{\text{rel}}| \ge 50.0\%$ (or non-zero error emergence from zero baseline)

### C. Direct-Index Window Alignment
Windows are synchronized via direct-index overlap: $i \in [0, \min(N_A, N_B) - 1]$. Trailing windows in asymmetric captures are recorded under `unaligned_windows` as capture duration differences, not transmission loss.

---

## XIV. FEATURE F7: AUTOMATIC REPORT GENERATION

Feature F7 synthesizes F1–F6 outputs into multi-format executive reports (JSON, Markdown, CP-1252-safe Plain Text, and Standalone HTML5).

### Tripartite Findings Taxonomy
All findings generated by F7 are categorized under a strict epistemological taxonomy:
1. **`OBSERVED_FACT`:** Direct, deterministic physical measurements directly verifiable in stream syntax (e.g., `total_units = 18176`, `sync_byte_errors = 0`).
2. **`STATISTICAL_FINDING`:** Quantities derived through statistical or machine learning models (e.g., `health_score = 100.0`, `anomalous_windows = 5`, `peak_anomaly_score = 0.8576`).
3. **`ENGINEERING_INTERPRETATION`:** Domain-bounded diagnostic attributions constrained strictly to digital bitstream characteristics (e.g., "Capture termination boundary accounts for partial trailing window").

---

## XV. IMPLEMENTATION

PRJ_111 is implemented in Python 3.12 as a standalone local engineering workstation with no external cloud or proprietary licensing dependencies:
- **Backend Core:** Pure Python modular architecture (`dvbs2_analyzer/ingestion/`, `parsers/`, `features/`, `analysis/`).
- **Machine Learning Layer:** Scikit-learn (`IsolationForest`) with NumPy for vector operations.
- **HTTP Gateway:** Multi-threaded native Python HTTP server (`ThreadingHTTPServer`) exposing a RESTful JSON API (`/api/status`, `/api/analyze`, `/api/compare`, `/api/upload`, `/api/export`).
- **Frontend Workstation:** Single-Page Application (SPA) built with vanilla HTML5, CSS3, and ES6 JavaScript. Visualizations are rendered offline using vendored Chart.js (205 KB local bundle), eliminating external CDN dependencies and enabling air-gapped field operation.
- **Local Staging Security:** Direct browser file uploads are staged locally under `05_CODE/uploads/` with alphanumeric token sanitization and directory traversal prevention (`os.path.commonpath`).

---

## XVI. EXPERIMENTAL DATASETS

The system was evaluated against authoritative satellite captures stored in `01_RAW_DATA/`:
1. **MPEG-TS Clean Capture (`01_RAW_DATA/03_TS/DVBS2_toolkit/sample.ts`):** 3,417,088 bytes of off-air DVB-S2 satellite television broadcast, captured via DVBS2_toolkit, containing 18,176 fixed 188-byte packets.
2. **MPEG-TS Corrupted Capture (`01_RAW_DATA/03_TS/DVBS2_toolkit/corrupted_sample.ts`):** 3,417,088 bytes containing 11 corrupted synchronization bytes in the initial segment.
3. **GSE Authoritative Capture (`01_RAW_DATA/02_GSE/GSExtract/sample.ts`):** 9,324 bytes containing 14 variable-length GSE PDUs carrying encapsulated IPv4 datagrams, captured via GSExtract.
4. **DVB-S2 Baseband Frame Capture (`01_RAW_DATA/01_BBFRAME_GSE/dvb-s2_bb_example.pcap`):** 2,349,376 bytes containing 4,309 DVB-S2 Baseband Frames with ACM and SIS/MIS configuration.

---

## XVII. EXPERIMENTAL RESULTS AND DISCUSSION

Empirical results across the authoritative captures are documented in Tables I through VI.

### TABLE I: Supported Input Format Characteristics
| Format Identifier | Framing Structure | Header Size | Typical Container Dimension | Checksum Algorithm | Primary Use Case |
|:---|:---:|:---:|:---:|:---:|:---|
| **MPEG-TS** | Fixed Packet | 4 Bytes (32 bits) | Fixed 188 Bytes | Continuity Counter (4b) | Linear Broadcast TV |
| **GSE** | Variable PDU | 2–8 Bytes | 45–1,444 Bytes (Variable) | CRC-32 (32 bits) | Satellite IP Broadband |
| **BBFrame** | Fixed Frame | 10 Bytes (80 bits) | 216–10,000 Bits (DFL) | CRC-8 (8 bits) | Native Physical Layer |

### TABLE II: MPEG-TS Health and Priority-1 Integrity Results
| Stream Capture | Total Packets | Sync Integrity | TEI Errors | CC Errors | Extracted Payload | Health Score | Classification |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| `sample.ts` (Clean) | 18,176 | 100.0% (18,176/18,176) | 0 (0.00%) | 0 (0.00%) | 3,267,305 B | 100.0% | **`HEALTHY`** |
| `corrupted_sample.ts` | 18,168 | 100.0% (18,168/18,168) | 4 (0.02%) | 0 (0.00%) | 3,265,277 B | 99.67% | **`HEALTHY`** |

*Diagnostic Trace of Corrupted TS:* `TSParser` encountered 11 corrupted sync bytes in the initial segment and resynchronized, dropping exactly 8 unaligned packets. The 18,168 yielded packets exhibited 100.0% sync byte integrity. Four packets suffered false sync alignment in payload data resulting in $\text{TEI} = 4$ in Window 0 (Window 0 health = 70.0%). Windows 1–90 exhibited 100.0% health, yielding an average stream health of $99.67\%$, satisfying the $\ge 99.0\%$ threshold for `HEALTHY`.

### TABLE III: GSE Encapsulation & Protocol Analysis Results
| Metric Parameter | Experimental Observed Value | Epistemic Category |
|:---|:---:|:---:|
| Total Ingested PDUs | 14 PDUs | `OBSERVED_FACT` |
| Valid Framing Compliance | 100.0% (14 / 14 PDUs) | `OBSERVED_FACT` |
| Total Payload Extracted | 8,764 Bytes | `OBSERVED_FACT` |
| Mean PDU Length | 626.0 Bytes (Min: 45 B, Max: 1,444 B) | `STATISTICAL_FINDING` |
| Fragmentation Breakdown | 6 Unfragmented (42.9%), 8 Fragmented (57.1%) | `OBSERVED_FACT` |
| First / Interm. / Last Fragments | 5 First / 0 Intermediate / 3 Last Fragments | `OBSERVED_FACT` |
| Encapsulated Protocols | `GSE_EXT_NPA`: 11 PDUs (100%), `IPv4`: 9 PDUs | `OBSERVED_FACT` |
| Addressing Labels | 6-Byte Label: 11 PDUs, No Label: 3 PDUs | `OBSERVED_FACT` |
| CRC-32 Verification | 100.0% Pass (0 Checksum Failures) | `OBSERVED_FACT` |
| F1 Stream Health Score | 100.0% (`HEALTHY`) | `STATISTICAL_FINDING` |

### TABLE IV: DVB-S2 Baseband Frame Transmission Analysis
| Parameter Dimension | Observed Parameter Value | Percentage Distribution | Epistemic Category |
|:---|:---:|:---:|:---:|
| Total Baseband Frames | 4,309 Frames | 100.0% | `OBSERVED_FACT` |
| BBHeader CRC-8 Validity | 4,309 Passed / 0 Failed | 100.0% Valid | `OBSERVED_FACT` |
| Stream Input Mode (MATYPE-1) | SIS: 4,308 / MIS: 1 | 99.98% SIS / 0.02% MIS | `OBSERVED_FACT` |
| Coding & Modulation Mode | Adaptive Coding & Modulation (ACM) | 100.0% (4,309 / 4,309) | `OBSERVED_FACT` |
| Transmission Profile | `GENERIC_CONTINUOUS` | 100.0% (4,309 / 4,309) | `OBSERVED_FACT` |
| Roll-off Factor ($\alpha$) | $\alpha = 0.35$ | 100.0% (4,309 / 4,309) | `OBSERVED_FACT` |
| Total Data Field Payload | 1,958,826 Bytes | — | `OBSERVED_FACT` |
| Data Field Length (DFL) Range | 216 to 10,000 Bits (Mean: 3,636.72 Bits) | Mode: 2,992 Bits (85.82%) | `STATISTICAL_FINDING` |

### TABLE V: Unsupervised Isolation Forest Anomaly Detection Results
| Stream Format & Capture | Window Dimension | Total Windows | Anomalous Windows | Anomaly Proportion | Peak Anomaly Score | Anomalous Window Indices |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|
| **MPEG-TS** (`sample.ts`) | 200 Packets | 91 | 5 | 5.49% | 0.8576 (Window 90) | `[1, 2, 12, 88, 90]` |
| **GSE** (`sample.ts`) | 3 PDUs | 5 | 1 | 20.00% | 0.5018 (Window 4) | `[4]` |
| **BBFrame** (`bb_example.pcap`) | 50 Frames | 87 | 5 | 5.75% | 0.7406 (Window 86) | `[0, 83, 84, 85, 86]` |

*Analysis of Anomaly Distribution:* In all three formats, an elevated anomaly score consistently occurs at the final window boundary (Window 90 in TS, Window 4 in GSE, Window 86 in BBFrame). This demonstrates the sensitivity of the Isolation Forest to container volume truncation caused by capture termination. Intermediate anomalies (e.g., TS Windows 1, 2, and 12) correspond to localized statistical multiplexing bursts where single PIDs concentrate up to 98.5% of window bandwidth.

### TABLE VI: Cross-Format Stream Comparison Audit (TS vs. BBFrame)
| Metric Identifier | Semantic Status | Stream A (MPEG-TS) | Stream B (BBFrame) | Absolute Delta ($\Delta_{\text{abs}}$) | Relative Delta ($\Delta_{\text{rel}}$) | Significance Classification |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|
| `total_payload_bytes` | **`COMPARABLE`** | 3,267,305 B | 1,958,826 B | -1,308,479 B | -40.05% | **`SUBSTANTIAL`** |
| `integrity_ratio` | **`COMPARABLE`** | 1.0000 | 1.0000 | 0.0000 | 0.00% | **`NEGLIGIBLE`** |
| `total_units` | `NOT_COMPARABLE` | 18,176 pkts | 4,309 frames | Blocked by Shield | Blocked | `INCOMPATIBLE_DIMENSION` |
| `valid_units` | `NOT_COMPARABLE` | 18,176 pkts | 4,309 frames | Blocked by Shield | Blocked | `INCOMPATIBLE_DIMENSION` |
| `invalid_units` | `NOT_COMPARABLE` | 0 pkts | 0 frames | Blocked by Shield | Blocked | `INCOMPATIBLE_DIMENSION` |
| `mean_payload_bytes` | `NOT_COMPARABLE` | 179.76 B/pkt | 454.59 B/frame | Blocked by Shield | Blocked | `INCOMPATIBLE_CONTAINER` |
| `payload_ratio` | `NOT_COMPARABLE` | 1.0000 | 1.0000 | Blocked by Shield | Blocked | `DIVERGENT_FORMULATION` |
| `error_count` | `NOT_COMPARABLE` | 0 errors | 0 errors | Blocked by Shield | Blocked | `HETEROGENEOUS_FAILURES` |
| `error_rate` | `NOT_COMPARABLE` | 0.0000 | 0.0000 | Blocked by Shield | Blocked | `HETEROGENEOUS_FAILURES` |
| `entropy` | `NOT_COMPARABLE` | 0.1361 bits | 0.0000 bits | Blocked by Shield | Blocked | `DISTINCT_STATE_SPACES` |

---

## XVIII. FRONTEND APPLICATION WORKSTATION DEMONSTRATION

The PRJ_111 user interface is engineered in the aesthetic of professional telecommunications workstations. Captured views of the live application are presented below.

```
+---------------------------------------------------------------------------------------+
|  Fig. 2. PRJ_111 Stream Ingestion & Analysis Controls Dashboard (Workstation Standby) |
+---------------------------------------------------------------------------------------+
```
*(Image Reference: `paper_assets/fig2_dashboard_empty.png`)*  
Fig. 2 depicts the standby workstation interface, illustrating the primary binary upload dropzone, authoritative preset selector, format override controls, and the conceptual execution sequence checklist in standby status.

```
+---------------------------------------------------------------------------------------+
|  Fig. 3. PRJ_111 Stream Ingestion & Analysis Dashboard (Active Stream Analyzed)       |
+---------------------------------------------------------------------------------------+
```
*(Image Reference: `paper_assets/fig_dashboard_analyzed.png`)*  
Fig. 3 illustrates the active dashboard following completion of analysis on `sample.ts`. Key telemetry cards display 100.0% stream health, 100.00% framing integrity (18,176 units), 5 anomaly windows, and 3,337 KB container payload. The execution sequence confirms completion of F1–F5 and F7, while F6 correctly awaits comparison input.

```
+---------------------------------------------------------------------------------------+
|  Fig. 4. PRJ_111 Stream Comparison Interface (Feature F6 Dual-Stream Evaluation)      |
+---------------------------------------------------------------------------------------+
```
*(Image Reference: `paper_assets/fig_comparison_view.png`)*  
Fig. 4 displays the Feature F6 comparison interface evaluating `sample.ts` against `corrupted_sample.ts`. The view highlights format equivalence (`SAME FORMAT`), direct-index alignment (91 windows), relative payload delta (-0.06%, `NEGLIGIBLE`), and the dynamic semantic audit table evaluating all 11 metrics with exact engineering rationales.

```
+---------------------------------------------------------------------------------------+
|  Fig. 5. PRJ_111 Spatial Activity Timeline & Metric Trajectory (Feature F4)           |
+---------------------------------------------------------------------------------------+
```
*(Image Reference: `paper_assets/fig_timeline_view.png`)*  
Fig. 5 illustrates the Feature F4 spatial activity timeline, charting rolling stream health alongside the F2 anomaly score with decision threshold ($s = 0.5000$). Lower panels chart payload density (KB) and PID multiplex Shannon entropy across window progress without fabricating timestamps.

```
+---------------------------------------------------------------------------------------+
|  Fig. 6. PRJ_111 Flagged Anomaly Windows & Diagnostic Attribution (Features F2 + F5)  |
+---------------------------------------------------------------------------------------+
```
*(Image Reference: `paper_assets/fig_anomaly_view.png`)*  
Fig. 6 demonstrates the anomaly explanation table. Flagged windows are listed alongside unit ranges, byte offsets, anomaly scores, and Bounded Z-Score diagnostic attributions identifying multiplex concentration and recording boundaries.

```
+---------------------------------------------------------------------------------------+
|  Fig. 7. PRJ_111 Automatic Multi-Format Report Generation (Feature F7)                |
+---------------------------------------------------------------------------------------+
```
*(Image Reference: `paper_assets/fig_report_view.png`)*  
Fig. 7 shows the Feature F7 report generation view, demonstrating tripartite categorization (`OBSERVED_FACT`, `STATISTICAL_FINDING`, `ENGINEERING_INTERPRETATION`) and one-click export controls for JSON, Markdown, Plain Text, and standalone HTML5.

---

## XIX. SOFTWARE VERIFICATION AND REGRESSION TESTING

System stability and algorithmic correctness are verified through an automated test suite.

### Automated Test Suite Execution
Executed via the isolated project environment:
```powershell
python -m unittest discover -s tests -v
```
**Outcome:** **240 / 240 Tests Passing (100% Pass Rate)** with **0 Failures** and **0 Errors** in 19.86s.

### Test Coverage Architecture
- **Backend Analytical Suite (207 Tests):** Validates deterministic framing parsers (`test_ts_parser.py`, `test_gse_parser.py`, `test_bbframe_parser.py`), feature extraction (`test_unified_features.py`), F1 stream health (`test_f1_health.py`), F2 anomaly detection (`test_anomaly.py`), F3 pattern detection (`test_patterns.py`), F4 timeline generation (`test_timeline.py`), F5 anomaly explanations (`test_explanation.py`), F6 stream comparison (`test_comparison.py`), and F7 report generation (`test_report.py`).
- **Frontend Server & Integration Suite (33 Tests):** Validates threaded HTTP server lifecycle, static asset delivery, SVG/ICO favicon MIME types, binary file upload staging, directory traversal security guards, F6 state reset lifecycle, relative path multi-candidate resolution, content-aware GSE detection, corrupted TS diagnostic accounting, sequential stream replacement lifecycle, and semantically correct HTTP 400 invalid-file handling.

*Note on Epistemic Integrity:* Passing 240/240 automated software tests constitutes rigorous **software verification and regression integrity**. It is explicitly **not** presented as machine learning classification accuracy.

---

## XX. LIMITATIONS

To maintain scientific integrity, the limitations of the current prototype are documented:
1. **Unlabeled Real-World Datasets:** Due to the absence of public, ground-truth-labeled DVB-S2 anomaly datasets, machine learning models are evaluated via unsupervised isolation and synthetic perturbation, rather than supervised benchmark metrics (ROC-AUC).
2. **Post-Demodulator Scope:** The application operates exclusively on digital receiver output bitstreams. It cannot diagnose analog RF physical-layer conditions (e.g., signal-to-noise ratio, carrier frequency offset, or transponder compression).
3. **ETSI TR 101 290 Scope:** Health analysis evaluates selected Priority-1 indicators inspired by ETSI TR 101 290 principles; it does not claim formal certification across all Priority-2 and Priority-3 measurement guidelines.
4. **Offline Spatial Windowing:** Analysis is structured over discrete spatial unit windows rather than real-time continuous sliding windows.
5. **No Sequence Memory:** The Isolation Forest treats each window independently; temporal sequence dependencies across successive windows are not modeled.

---

## XXI. FUTURE WORK

Future research and development directions include:
1. **Deep Sequential Models:** Investigating bidirectional long short-term memory (Bi-LSTM) networks and temporal transformers to capture long-range sequential correlations across broadcast streams.
2. **Software-Defined Radio (SDR) Demodulation:** Exploring integration with an upstream GNU Radio or gr-dvbs2 physical-layer front-end to capture simultaneous RF constellation metrics (EVM, MER, SNR) alongside digital framing telemetry.
3. **Hardware Acceleration:** Exploring offloading of PDU and packet header parsing to FPGA or eBPF kernel bypass engines to support high-throughput transponder aggregation.
4. **Standardized Benchmark Dataset Publication:** Curating and releasing an open, expert-annotated multi-format DVB-S2 anomaly dataset for the research community.

---

## XXII. CONCLUSION

This paper has presented the architectural design, algorithmic foundation, and empirical verification of **PRJ_111**, a specialized software application for the analysis and processing of multi-format DVB-S2 receiver output streams. By implementing content-aware format detection and modular parsing across MPEG-TS, GSE, and DVB-S2 Baseband Frames, the system overcomes the structural fragmentation that limits single-format protocol analyzers.

The seven-feature analytical pipeline achieves deterministic stream health evaluation (F1), unsupervised Isolation Forest anomaly detection (F2), structural pattern and entropy analysis (F3), physical spatial activity timelines (F4), bounded Z-score diagnostic anomaly explanations (F5), semantically guarded stream comparisons (F6), and automated tripartite diagnostic reporting (F7). Operating as a local engineering workstation, PRJ_111 enforces epistemic safeguards: barring fictitious clock timestamps, preventing speculative physical-layer inferences, and strictly isolating physically incomparable quantities across framing boundaries. Validated across authoritative satellite captures with 240/240 passing automated tests, PRJ_111 establishes a robust, extensible prototype for satellite ground station monitoring, telecommunications education, and broadcast stream verification.

---

## ACKNOWLEDGMENT

The authors express their sincere gratitude to the **Department of Computer Science and Engineering, Presidency University, Bengaluru**, for providing the laboratory facilities, computing infrastructure, and academic environment necessary to conduct this research. The authors extend special thanks to our project guide, **Irfan Rajab Bhat, Assistant Professor**, for his guidance, insightful technical critiques, and continued support throughout the development and verification of this project.

---

## REFERENCES

[1] ETSI EN 302 307-1 V1.4.1, "Digital Video Broadcasting (DVB); Second generation framing structure, channel coding and modulation systems for Broadcasting, Interactive Services, News Gathering and other broadband satellite applications; Part 1: DVB-S2," European Telecommunications Standards Institute (ETSI), Sophia Antipolis, France, Nov. 2014.

[2] ETSI TS 102 606-1 V1.2.1, "Digital Video Broadcasting (DVB); Generic Stream Encapsulation (GSE); Part 1: Protocol," European Telecommunications Standards Institute (ETSI), Sophia Antipolis, France, Jul. 2014.

[3] ISO/IEC 13818-1:2022, "Information technology — Generic coding of moving pictures and associated audio information — Part 1: Systems (MPEG-2 Transport Stream)," International Organization for Standardization / International Electrotechnical Commission, Geneva, Switzerland, 2022.

[4] ETSI TR 101 290 V1.4.1, "Digital Video Broadcasting (DVB); Measurement guidelines for DVB systems," European Telecommunications Standards Institute (ETSI), Technical Report, Sophia Antipolis, France, Jun. 2020.

[5] F. T. Liu, K. M. Ting, and Z.-H. Zhou, "Isolation Forest," in *Proc. 8th IEEE International Conference on Data Mining (ICDM)*, Pisa, Italy, Dec. 2008, pp. 413–422.

[6] F. T. Liu, K. M. Ting, and Z.-H. Zhou, "Isolation-based anomaly detection," *ACM Transactions on Knowledge Discovery from Data (TKDD)*, vol. 6, no. 1, pp. 1–39, Mar. 2012.

[7] A. Morello and V. Mignone, "DVB-S2: The second generation standard for satellite broadband services," *Proceedings of the IEEE*, vol. 94, no. 1, pp. 210–227, Jan. 2006.

[8] G. Fairhurst and B. Collini-Nocker, "Generic Stream Encapsulation (GSE) for DVB-S2: Design and Evaluation," *International Journal of Satellite Communications and Networking*, vol. 28, no. 5–6, pp. 287–305, Sep. 2010.

[9] V. Chandola, A. Banerjee, and V. Kumar, "Anomaly detection: A survey," *ACM Computing Surveys (CSUR)*, vol. 41, no. 3, pp. 1–58, Jul. 2009.

[10] M. A. Pimentel, D. A. Clifton, L. Clifton, and L. Tarassenko, "A review of novelty detection," *Signal Processing*, vol. 99, pp. 215–249, Jun. 2014.

[11] D. Minoli, *Innovations in Satellite Communications and the Global Information Infrastructure*, Hoboken, NJ, USA: John Wiley & Sons, 2015.

[12] P. L. Luisi, A. B. Sampaio, and C. A. C. Marcondes, "Empirical Evaluation of Digital Video Broadcasting Systems and Transport Stream Analysis," *IEEE Transactions on Broadcasting*, vol. 66, no. 2, pp. 431–444, Jun. 2020.

[13] R. S. Baggio, P. R. L. Gondim, and F. L. L. Mendonca, "Network Traffic Anomaly Detection Using Unsupervised Learning Models: A Comparative Study," *IEEE Access*, vol. 9, pp. 15982–15998, Jan. 2021.

[14] E. Casini, R. De Gaudenzi, and A. Ginesi, "DVB-S2 modern modulation and coding techniques for satellite broadcast and broadband transmissions," *IEEE Communications Magazine*, vol. 42, no. 11, pp. 146–156, Nov. 2004.

[15] B. Sklar, *Digital Communications: Fundamentals and Applications*, 2nd ed., Upper Saddle River, NJ, USA: Prentice Hall PTR, 2001.

[16] IETF RFC 4326, G. Fairhurst and B. Collini-Nocker, "Unidirectional Lightweight Encapsulation (ULE) for Transmission of IP Datagrams over an MPEG-2 Transport Stream," Internet Engineering Task Force (IETF), Dec. 2005.

[17] ETSI EN 300 468 V1.17.1, "Digital Video Broadcasting (DVB); Specification for Service Information (SI) in DVB systems," European Telecommunications Standards Institute (ETSI), Sophia Antipolis, France, 2021.

[18] C. E. Shannon, "A Mathematical Theory of Communication," *Bell System Technical Journal*, vol. 27, no. 3, pp. 379–423, Jul. 1948.

[19] D. Arthur and S. Vassilvitskii, "k-means++: The advantages of careful seeding," in *Proc. 18th Annual ACM-SIAM Symposium on Discrete Algorithms (SODA)*, New Orleans, LA, USA, 2007, pp. 1027–1035.

[20] M. Ester, H.-P. Kriegel, J. Sander, and X. Xu, "A density-based algorithm for discovering clusters in large spatial databases with noise," in *Proc. 2nd International Conference on Knowledge Discovery and Data Mining (KDD)*, Portland, OR, USA, 1996, pp. 226–231.

---

## AUTHOR BIOGRAPHIES

```
+---------------------------+
| [Photo: Sk Samad]         |
| paper_assets/             |
| author_samad.jpg          |
+---------------------------+
```
**Sk Samad** is currently pursuing his Bachelor of Technology (B.Tech) in Computer Science and Engineering at Presidency University, Bengaluru, Karnataka, India. His academic interests encompass digital signal processing, satellite communications protocols, and machine learning applications in network security. Within the PRJ_111 project, he contributed to the ingestion layer design, format sniffer calibration, and unsupervised Isolation Forest anomaly detection pipeline across heterogeneous stream representations.  
*Roll No: 20231COM0031 | Department of CSE, Presidency University, Bengaluru.*

```
+---------------------------+
| [Photo: Y Vengala Rao]    |
| paper_assets/             |
| author_vengala_rao.jpg    |
+---------------------------+
```
**Y Vengala Rao** is currently pursuing his Bachelor of Technology (B.Tech) in Computer Science and Engineering at Presidency University, Bengaluru, Karnataka, India. His areas of interest include telecommunications systems, protocol parsing, and lightweight neural network architectures for resource-constrained embedded environments. In PRJ_111, he focused on stream parsing implementations for MPEG-TS, GSE, and DVB-S2 Baseband Frames, as well as the deterministic stream health scoring formulation.  
*Roll No: 20231COM0001 | Department of CSE, Presidency University, Bengaluru.*

```
+---------------------------+
| [Photo: C Rakeshwar]      |
| paper_assets/             |
| author_rakeshwar.jpg      |
+---------------------------+
```
**C Rakeshwar** is currently pursuing his Bachelor of Technology (B.Tech) in Computer Science and Engineering at Presidency University, Bengaluru, Karnataka, India. His research interests include distributed systems, software engineering methodologies, and cybersecurity telemetry analysis. For PRJ_111, he developed the cross-format stream comparison engine, the bounded Z-score explanatory model, the engineering workstation single-page application, and automated regression test suites.  
*Roll No: 20231COM0008 | Department of CSE, Presidency University, Bengaluru.*

---

## TEAM PRESENTATION

```
+---------------------------------------------------------------------------------------+
|  Fig. 8. PRJ_111 project team during project presentation at Presidency University    |
+---------------------------------------------------------------------------------------+
```
*(Image Reference: `paper_assets/team_presentation.jpg`)*  
**Fig. 8.** PRJ_111 project team during project presentation at Presidency University (Sk Samad, Y Vengala Rao, and C Rakeshwar).
