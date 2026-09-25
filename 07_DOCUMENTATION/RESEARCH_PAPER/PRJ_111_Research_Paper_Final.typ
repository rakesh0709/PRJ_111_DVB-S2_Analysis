#set page(
  paper: "us-letter",
  margin: (top: 0.75in, bottom: 0.75in, left: 0.65in, right: 0.65in),
  footer: context [
    #set text(font: "Times New Roman", size: 8.5pt)
    #set align(center)
    #counter(page).display("1")
  ]
)

#set text(font: "Times New Roman", size: 10pt)
#set par(justify: true, leading: 0.52em, first-line-indent: 1.2em)
#set math.equation(numbering: "(1)")

// IEEE Heading Styles
#show heading.where(level: 1): it => block(width: 100%, below: 0.55em, above: 0.95em)[
  #set align(center)
  #set text(size: 10pt, weight: "bold")
  #smallcaps(it.body)
]

#show heading.where(level: 2): it => block(below: 0.38em, above: 0.7em)[
  #set text(size: 10pt, weight: "bold", style: "italic")
  #it.body
]

#show heading.where(level: 3): it => block(below: 0.3em, above: 0.55em)[
  #set text(size: 10pt, style: "italic")
  #it.body
]

// Figure and Table Caption Settings (IEEE format)
#show figure.where(kind: table): set figure.caption(position: top)
#show figure: set block(spacing: 0.7em)
#show figure.caption: it => [
  #set text(font: "Times New Roman", size: 8.5pt)
  #if it.kind == table [
    #align(center)[
      #text(weight: "bold")[TABLE #it.counter.display("I")] \
      #text(weight: "bold")[#smallcaps(it.body)]
    ]
  ] else [
    *Fig. #it.counter.display("1").* #it.body
  ]
]

// Bibliography Styling (IEEE 8.5pt)
#show bibliography: set text(size: 8.5pt)
#show bibliography: set par(leading: 0.42em, spacing: 0.45em)

// Document Title & Authors
#align(center)[
  #v(0.08in)
  #text(size: 17pt, weight: "bold")[Development of a Multi-Format DVB-S2 Receiver Output \ Stream Analyzer with Anomaly Detection and Diagnostic Reporting]
  
  #v(1.0em)
  #grid(
    columns: (1fr, 1fr, 1fr),
    align: center,
    gutter: 1em,
    [
      #text(size: 11pt, weight: "bold")[Sk Samad] \
      #text(size: 9pt)[Roll No: 20231COM0031] \
      #text(size: 9pt, style: "italic")[Dept. of Computer Science & Engineering] \
      #text(size: 9pt)[Presidency University] \
      #text(size: 9pt)[Bengaluru, India]
    ],
    [
      #text(size: 11pt, weight: "bold")[Y Vengala Rao] \
      #text(size: 9pt)[Roll No: 20231COM0001] \
      #text(size: 9pt, style: "italic")[Dept. of Computer Science & Engineering] \
      #text(size: 9pt)[Presidency University] \
      #text(size: 9pt)[Bengaluru, India]
    ],
    [
      #text(size: 11pt, weight: "bold")[C Rakeshwar] \
      #text(size: 9pt)[Roll No: 20231COM0008] \
      #text(size: 9pt, style: "italic")[Dept. of Computer Science & Engineering] \
      #text(size: 9pt)[Presidency University] \
      #text(size: 9pt)[Bengaluru, India]
    ]
  )
  #v(0.8em)
]

#columns(2, gutter: 0.22in)[

#block(inset: (bottom: 0.4em))[
  #set par(first-line-indent: 0pt)
  #text(weight: "bold")[_Abstract_—]#text(size: 9pt)[Digital Video Broadcasting via Satellite (DVB-S2) provides the physical and data-link framing structure for satellite broadband, high-definition television distribution, and cellular backhaul. Modern satellite receivers demodulate radio-frequency downlinks and emit post-demodulator digital output streams across multiple heterogeneous encapsulation formats, primarily MPEG-2 Transport Streams (MPEG-TS), Generic Stream Encapsulation (GSE), and DVB-S2 Baseband Frames (BBFrame). Analyzing receiver output streams across these formats presents an operational engineering challenge: each format possesses fundamentally distinct framing boundaries, header structures, and error-propagation characteristics that conventional single-format protocol analyzers do not natively unify. This paper presents PRJ_111, an extensible software application engineered for multi-format DVB-S2 receiver output stream analysis, anomaly detection, and diagnostic reporting. The application establishes a unified analytical pipeline providing deterministic stream health evaluation inspired by ETSI TR 101 290 Priority-1 principles, unsupervised anomaly detection via format-isolated Isolation Forest models, structural pattern and Shannon entropy analysis, byte-indexed spatial activity timelines, bounded Z-score anomaly explanations, semantically guarded cross-format stream comparisons, and automated multi-format reporting organized under a tripartite epistemological taxonomy. Experimental validation across authoritative satellite broadcast captures demonstrates deterministic health accounting (100.0% on clean streams; 99.67% on corrupted streams with exact transport error tracking), unsupervised identification of multiplex bursts and truncation boundaries, and strict semantic isolation in cross-format differentials. The complete system is verified by an automated regression suite of 240 tests (207 backend and 33 frontend tests) achieving a 100% pass rate with zero failures and zero errors.]

  #v(0.5em)
  #text(weight: "bold")[_Index Terms_—]#text(size: 9pt, style: "italic")[Anomaly detection, Baseband frame, Digital video broadcasting, DVB-S2, Feature extraction, Generic stream encapsulation, Isolation Forest, MPEG transport stream, Receiver output analysis, Stream analysis.]
]

= I. Introduction

The Second Generation Digital Video Broadcasting via Satellite standard (DVB-S2, ETSI EN 302 307-1) represents the foundational physical and framing specification for modern satellite telecommunications @etsi_dvbs2. Operating downstream of the satellite low-noise block downconverter (LNB) and intermediate-frequency (IF) tuner, the satellite receiver demodulator performs carrier acquisition, matched filtering, forward error correction (FEC) decoding using coupled Low-Density Parity-Check (LDPC) and Bose-Chaudhuri-Hocquenghem (BCH) codes, and baseband deframing @morello2006. The resulting post-demodulator digital output stream forms the critical boundary between satellite physical-layer transmission and terrestrial networking appliances.

In operational satellite ground stations, television distribution networks, and satellite broadband terminals, post-demodulator output is not uniform. Depending on transponder service profiles and downstream equipment, receivers emit digital data in one of three standardized digital framing representations:
1) *MPEG-2 Transport Stream (MPEG-TS):* Fixed 188-byte containers featuring periodic synchronization markers (`0x47`), 13-bit Program Identifiers (PIDs), and continuity counters, standard in linear television broadcasting @iso_mpegts.
2) *Generic Stream Encapsulation (GSE):* Variable-length protocol data units (PDUs) featuring 2-bit start/end fragmentation flags, 16-bit EtherType protocol identifiers, and cyclic redundancy checks, standard in satellite IP broadband @etsi_gse.
3) *DVB-S2 Baseband Frames (BBFrame):* The native physical-layer container defined by an 80-bit Baseband Header (BBHeader), Mode Adaptation flags (MATYPE-1/2), User Packet Length (UPL), Data Field Length (DFL), and CRC-8 header protection @etsi_dvbs2.

Analyzing receiver output streams is essential for ground station commissioning, transponder capacity verification, stream integrity assessment, and transmission debugging. However, analyzing these heterogeneous representations using conventional tools presents operational limitations @luisi2020. Generic packet analyzers (such as Wireshark) treat captures as Ethernet frames, requiring specialized external dissectors that lack native support for raw concatenated transport streams or raw baseband frame telemetry @minoli2015. Conversely, dedicated broadcast hardware instruments are tailored primarily to MPEG-TS, providing limited native support for modern DVB-S2 baseband frames or GSE IP encapsulation @luisi2020.

Furthermore, existing analysis tools suffer from three fundamental engineering deficiencies:
1) *Framing Heterogeneity and Parser Brittleness:* Digital captures arrive as unindexed raw binary bitstreams (`.ts`, `.gse`, `.bin`, `.pcap`). Naive file-extension parsers misidentify formats, while streaming parsers without robust synchronization recovery fail when encountering bit errors.
2) *Lack of Cross-Format Telemetry:* Comparing packet counts, PDU counts, and baseband frame counts directly creates false equivalence, misleading ground station operators by comparing metrics with incompatible physical dimensions.
3) *Epistemic Over-Claiming in Stream Telemetry:* Many commercial monitoring tools calculate synthetic clock timestamps or fictitious Megabits-per-second (Mbps) throughputs in offline files where no receiver clock telemetry exists, or assert speculative physical-layer causal inferences (e.g., attributing a continuity counter error to "rain fade" without demodulator signal-to-noise ratio measurements).

To resolve these challenges, this paper presents *PRJ_111*, a specialized, modular software application engineered for multi-format DVB-S2 receiver output stream analysis. PRJ_111 establishes an integrated seven-feature analytical pipeline (F1--F7) that performs content-aware format sniffer ingestion, deterministic framing parsing, unified feature extraction, rule-based stream health analysis (F1), unsupervised Isolation Forest anomaly detection (F2), structural pattern and entropy analysis (F3), physical spatial activity timelines (F4), bounded Z-score diagnostic anomaly explanations (F5), semantically guarded stream comparisons (F6), and automated multi-format diagnostic report generation (F7).

The remainder of this paper is organized as follows: Section II reviews related literature. Section III presents the system architecture. Section IV details multi-format parsing. Section V elaborates the seven-feature analytical pipeline. Section VI outlines the experimental setup and datasets. Section VII analyzes empirical results. Section VIII details automated software verification. Section IX presents limitations and domain-safety considerations. Section X concludes the paper with directions for future work.

= II. Related Work

The technical foundation of PRJ_111 synthesizes international telecommunications standards, satellite protocol engineering, unsupervised machine learning, and empirical stream monitoring.

== A. DVB-S2 Framing and Encapsulation Protocols
The DVB-S2 standard (ETSI EN 302 307-1) defines framing, channel coding, and modulation for satellite communications, establishing Adaptive Coding and Modulation (ACM) and Native Baseband Framing @etsi_dvbs2. Morello and Mignone @morello2006 analyzed the physical layer mechanisms of DVB-S2, demonstrating how variable-length user packets are encapsulated into baseband frames protected by inner LDPC and outer BCH codes. Casini et al. @casini2004 analyzed modulation constellations ranging from QPSK to 32-APSK, detailing the role of the 80-bit Baseband Header (BBHeader), Roll-Off factors ($alpha in {0.20, 0.25, 0.35}$), and Data Field Length (DFL) bit allocation. Sklar @sklar2001 provided the foundational framework for digital modulation, channel coding limits, and baseband framing boundaries in digital communication channels.

For network layer transport, Fairhurst and Collini-Nocker @fairhurst2010 formulated Generic Stream Encapsulation (ETSI TS 102 606-1) @etsi_gse to replace legacy Multi-Protocol Encapsulation (MPE over MPEG-TS) and Unidirectional Lightweight Encapsulation (ULE, RFC 4326) @rfc4326. GSE defines variable-size protocol data units carrying native IP datagrams with fragment-level CRC-32 protection, eliminating transport stream packing overhead. Digital television distribution continues to rely on the MPEG-2 Transport Stream (ISO/IEC 13818-1) @iso_mpegts. Operational measurement guidelines for DVB broadcast systems are standardized in ETSI TR 101 290 @etsi_tr101290, which defines Priority-1 stream parameters: loss of synchronization, Transport Error Indicator (TEI) assertions, and Continuity Counter (CC) errors. DVB Service Information (SI) standards are specified in ETSI EN 300 468 @etsi_si.

== B. Broadcast Stream Monitoring and Protocol Inspection
Luisi et al. @luisi2020 evaluated digital video broadcast stream monitoring techniques, demonstrating that while hardware TS analyzers reliably evaluate ETSI TR 101 290 Priority-1 errors, they lack native decoding for modern multi-protocol IP encapsulations (GSE and BBFrames) emitted by satellite broadband receivers. Minoli @minoli2015 surveyed network packet inspection tools, noting that packet sniffers treat raw digital bitstreams as unstructured payloads unless encapsulated in network capture wrappers (such as PCAP). PRJ_111 resolves these limitations by providing native, modular parsers for MPEG-TS, GSE, and BBFrames directly from raw receiver bitstreams.

== C. Unsupervised Anomaly Detection in Telecommunications
Anomaly detection in streaming telemetry has been surveyed by Chandola et al. @chandola2009 and Pimentel et al. @pimentel2014. Traditional statistical process control relies on static thresholds, which present difficulties in multiplexed channels where bitrates fluctuate dynamically with statistical multiplexing. Supervised classification approaches require extensive ground-truth labeled anomaly datasets @chandola2009. In operational DVB-S2 receiver monitoring, labeled anomalous bitstreams are rarely available; captured receiver data reflects proprietary commercial broadcasts, encrypted carrier feeds, or transient operational anomalies.

To address unlabeled streaming data, Liu et al. @liu2008, @liu2012 introduced the *Isolation Forest* algorithm. Isolation Forest isolates anomalies explicitly rather than profiling normal instances, constructing ensembles of random isolation trees (iTrees). Because anomalies possess distinct feature attributes, they are isolated closer to tree roots, resulting in shorter average path lengths @liu2008. Baggio et al. @baggio2021 evaluated unsupervised machine learning models for network traffic anomaly detection, demonstrating that Isolation Forest achieves superior computational efficiency ($O(n log n)$ training complexity) and robust outlier detection in streaming feature spaces compared to distance-based models such as $k$-means++ @arthur2007 or density-based clustering such as DBSCAN @ester1996. Shannon @shannon1948 established the mathematical foundation of information entropy, utilized in this work to evaluate PID multiplex distribution concentration. PRJ_111 adapts Isolation Forest to DVB-S2 telemetry, executing format-isolated, spatial-window anomaly detection with calibrated logistic decision boundaries.

= III. System Architecture and Workstation Design

The architecture of PRJ_111 is illustrated in @fig_arch. The system is structured as a six-stage pipeline that ingests raw post-demodulator digital receiver output, processes framing syntax, extracts unified features, executes analytical engines (F1--F3), generates spatial timeline telemetry (F4), diagnoses deviations (F5), evaluates dual-stream differentials (F6), and synthesizes multi-format reports (F7) through a standalone engineering workstation interface.

#figure(
  placement: top,
  scope: "parent",
  image("paper_assets/architecture_diagram.png", width: 88%),
  caption: [End-to-End Architectural Pipeline of the PRJ_111 DVB-S2 Receiver Output Stream Analyzer (Stages 1 through 6).]
) <fig_arch>

== A. Ingestion and Local Workstation Architecture
PRJ_111 is implemented in Python 3.12 as a local engineering workstation with zero external cloud or proprietary licensing dependencies:
- *Backend Core:* Pure Python modular architecture (`dvbs2_analyzer/ingestion/`, `parsers/`, `features/`, `analysis/`).
- *Machine Learning Layer:* Scikit-learn (`IsolationForest`) coupled with NumPy and SciPy for numerical vector operations.
- *HTTP Gateway:* Multi-threaded native Python HTTP server (`ThreadingHTTPServer`) exposing a RESTful JSON API (`/api/status`, `/api/analyze`, `/api/compare`, `/api/upload`, `/api/export`).
- *Frontend Workstation:* Single-Page Application (SPA) built with vanilla HTML5, CSS3, and ES6 JavaScript. Visualizations are rendered offline using vendored Chart.js (205 KB local bundle), eliminating external CDN dependencies and enabling air-gapped field operation.
- *Local Staging Security:* Direct browser file uploads are staged locally under `05_CODE/uploads/` with alphanumeric token sanitization and directory traversal prevention (`os.path.commonpath`).

#figure(
  image("paper_assets/fig_dashboard_analyzed.png", width: 95%),
  caption: [PRJ_111 Engineering Workstation active analysis dashboard evaluating an off-air MPEG-TS capture (`sample.ts`).]
) <fig_ui>

= IV. Multi-Format Stream Processing

The parsing layer operates directly on raw binary stream captures, providing modular decoders tailored to each standard. Format selection is governed by a content-aware format sniffer that evaluates synchronization bytes, transport error flags, GSE headers, and BBHeader CRC-8 checksums.

== A. MPEG-2 Transport Stream (MPEG-TS) Processing
The MPEG-TS parser processes continuous 188-byte containers specified in ISO/IEC 13818-1 @iso_mpegts. Each packet header is decoded as:
- *Sync Byte:* Must equal `0x47` (01000111 binary). If the parser encounters a non-`0x47` byte, it increments `sync_byte_errors` and scans forward byte-by-byte for the next valid synchronization byte.
- *Transport Error Indicator (TEI):* Bit 7 of byte 1. When asserted ($"TEI" = 1$), indicates that an uncorrected error exists within the packet container.
- *Payload Unit Start Indicator (PUSI):* Bit 6 of byte 1. Indicates that the packet payload begins with a Program Association Table (PAT), Program Map Table (PMT), or Packetized Elementary Stream (PES) header.
- *Transport Priority:* Bit 5 of byte 1.
- *Program Identifier (PID):* 13-bit value ($[0, 8191]$) defining the logical elementary stream multiplex. Null packets are identified by $"PID" = 8191$ (`0x1FFF`).
- *Transport Scrambling Control (TSC):* Bits 7--6 of byte 3.
- *Adaptation Field Control (AFC):* Bits 5--4 of byte 3, indicating payload-only (`01`), adaptation-field-only (`10`), or adaptation-field followed by payload (`11`).
- *Continuity Counter (CC):* 4-bit cyclic counter ($[0, 15]$) incremented per PID. Discontinuities ($"CC"_"curr" eq.not ("CC"_"prev" + 1) mod 16$) indicate an observed sequence gap for the corresponding PID.

== B. Generic Stream Encapsulation (GSE) Processing
The GSE parser decodes variable-size protocol data units adhering to ETSI TS 102 606-1 @etsi_gse:
- *Start/End Flags (S, E):* 2 bits defining PDU fragmentation. $S=1, E=1$ indicates an unfragmented PDU; $S=1, E=0$ indicates the first fragment; $S=0, E=0$ intermediate fragments; $S=0, E=1$ the last fragment.
- *GSE Length Field Specification:* In ETSI TS 102 606-1, the `GSE Length` field is a 12-bit binary field encoding integer values from 0 to 4,095 ($2^(12) - 1 = 4095$). It explicitly indicates the length in octets of the GSE payload and optional fields following the 2-byte GSE base header. Therefore, the maximum representable encapsulated payload is 4,095 bytes, and including the 2-byte base header, the maximum theoretical total PDU length is 4,097 bytes. In our implementation and in the captured validation dataset, all PDUs satisfy this constraint, with the maximum observed PDU length being 1,444 bytes.
- *Protocol Type:* 16-bit EtherType identifier (e.g., `0x0800` for IPv4, `0x86DD` for IPv6) or GSE extension header type (`GSE_EXT_NPA`).
- *Label Type:* 2 bits specifying 6-byte (`LABEL_6B`), 3-byte (`LABEL_3B`), or label-less (`LABEL_NONE`) addressing.
- *Fragment ID & Total Length:* Present in fragmented PDUs to facilitate payload reassembly.
- *CRC-32 Verification:* 32-bit CRC polynomial calculated over the PDU payload and headers for complete PDUs and last fragments.

== C. DVB-S2 Baseband Frame (BBFrame) Processing
The BBFrame parser decodes native satellite baseband frames specified in ETSI EN 302 307-1 @etsi_dvbs2. Each frame contains an 80-bit (10-byte) BBHeader followed by the data field:
- *MATYPE-1 (Mode Adaptation Type 1):*
  - Stream Input (TS/GS): Bits 7--6 indicate Single Input Stream (SIS) or Multiple Input Streams (MIS).
  - Modulation & Coding: Bit 5 indicates Constant Coding & Modulation (CCM) or Adaptive Coding & Modulation (ACM).
  - ISSYI / NPD: Input Stream Synchronization Indicator and Null Packet Deletion flags.
  - Roll-Off Factor ($alpha$): Bits 1--0 specify $alpha = 0.35$ (`00`), $alpha = 0.25$ (`01`), or $alpha = 0.20$ (`10`).
- *MATYPE-2:* Input Stream Identifier (ISI) when MIS is active.
- *User Packet Length (UPL):* 16-bit integer defining the length of encapsulated user packets.
- *Data Field Length (DFL):* 16-bit integer defining the active payload bits in the frame ($[0, K_"bch"]$). *DFL is expressed in bits*, representing the usable user data field within the physical baseband frame.
- *SYNC & SYNCD:* 8-bit copy of user packet synchronization marker and 16-bit distance in bits to the first user packet.
- *CRC-8 Checksum:* 8-bit error detection code computed over the preceding 72 bits using polynomial $G(x) = x^8 + x^7 + x^6 + x^4 + x^2 + 1$. Frames failing CRC-8 validation are flagged as corrupted.

#figure(
  caption: [Supported Input Format Characteristics],
  table(
    columns: (1.1fr, 1.2fr, 0.9fr, 1.6fr, 1.4fr),
    stroke: none,
    table.hline(stroke: 1.2pt),
    table.header(
      [*Format*], [*Structure*], [*Header*], [*Container Dimension*], [*Checksum*]
    ),
    table.hline(stroke: 0.6pt),
    [MPEG-TS], [Fixed Packet], [4 Bytes], [Fixed 188 Bytes], [Continuity Counter (4b)],
    [GSE], [Variable PDU], [2--8 Bytes], [45--1,444 Bytes (Var.)], [CRC-32 (32 bits)],
    [BBFrame], [Fixed Frame], [10 Bytes], [216--10,000 Bits (DFL)], [CRC-8 (8 bits)],
    table.hline(stroke: 1.2pt),
  )
) <tab_formats>

= V. Feature Engineering and Analytical Pipeline

To analyze streams across disparate formats without creating invalid semantic conflations, PRJ_111 establishes the `UnifiedStreamFeatureSet` architecture. Telemetry is bifurcated into physical invariants (`CommonMetrics`) and native format-specific metrics (`TSSpecificMetrics`, `GSESpecificMetrics`, `BBFrameSpecificMetrics`).

== A. Feature F1: Stream Health Analysis
Feature F1 executes deterministic stream health analysis, evaluating selected stream integrity indicators inspired by ETSI TR 101 290 principles @etsi_tr101290.

Rather than employing arbitrary penalty weight sums, PRJ_111 implements a transparent threshold-driven deductive scoring model encoded in `analysis/health.py`. Each evaluated spatial window $W_i$ starts from an initial healthy score of $100.0%$. Deductions are applied transparently based on threshold triggers:
- *Sync Integrity (ETSI TR 101 290 P1.1):* Critical ($< 95.00%$): deducts $40.0%$; Warning ($< 99.99%$): deducts $20.0%$.
- *Transport Error Indicator (ETSI TR 101 290 P1.3):* Critical ($> 1.00%$ error rate): deducts $30.0%$; Warning ($> 0.00%$ error rate): deducts $15.0%$.
- *Continuity Counter Errors (ETSI TR 101 290 P1.4):* Critical ($> 0.50%$ error rate): deducts $30.0%$; Warning ($> 0.01%$ error rate): deducts $15.0%$.
- *Null Packet Ratio:* Idle Transponder Beacon ($> 99.90%$ null packets): deducts $10.0%$; High Padding ($> 95.00%$ null packets): deducts $5.0%$.
- *Header Malformations:* Critical ($> 10$ malformed headers): deducts $20.0%$; Warning ($> 1$ malformed header): deducts $10.0%$.

The health score of window $W_i$ is evaluated by:
$ H(W_i) = max(0.0, 100.0 + sum Delta H) $ <eq_health_win>
The overall stream health score $H$ is the arithmetic mean across all $N$ evaluated spatial windows:
$ H = 1 / N sum_(i=1)^N H(W_i) $ <eq_health_total>

Streams are categorized into operational states:
- *`HEALTHY`:* $H >= 99.0%$
- *`DEGRADED` / `WARNING`:* $80.0% <= H < 99.0%$
- *`CRITICAL`:* $H < 80.0%$

== B. Feature F2: AI-Based Anomaly Detection
Feature F2 implements unsupervised anomaly detection across rolling spatial windows using the *Isolation Forest* algorithm @liu2008 through Scikit-learn.

Given a spatial window $W_i$ containing $K$ units ($K=200$ for TS, $K=3$ for GSE, $K=50$ for BBFrame), an $m$-dimensional feature vector $bold(x)_i in RR^m$ is extracted, capturing payload volume, integrity ratio, error rate, entropy, unit size variance, and format-specific telemetry.

The anomaly detector instantiates an ensemble of $T = 100$ isolation trees (`n_estimators=100`, `contamination=0.05`, `random_state=42`). The raw decision output $d(bold(x)) in RR$ is computed using Scikit-learn's `decision_function`, where negative values designate outliers and positive values designate inliers. To map this output to a normalized, intuitive anomaly score $s(bold(x)) in [0.0, 1.0]$, PRJ_111 applies a centered logistic sigmoid transformation:
$ s(bold(x)) = 1 / (1 + e^(8.0 d(bold(x)))) $ <eq_anomaly>

At the nominal decision boundary ($d(bold(x)) = 0.0$), the score evaluates to exactly $s = 0.5000$. Outliers ($d(bold(x)) < 0$) map to $s > 0.5000$, while regular inliers ($d(bold(x)) > 0$) map to $s < 0.5000$. Anomaly classification is determined by the decision threshold:
$ "Anomaly Flag" = cases(
  "TRUE" & "if " s(bold(x)_i) >= 0.5000,
  "FALSE" & "if " s(bold(x)_i) < 0.5000,
) $ <eq_thresh>

*Domain Safety Guard on Machine Learning Metrics:* Because operational satellite receiver output bitstreams are inherently unlabeled, *no ground-truth anomaly annotations exist* for off-air broadcast captures. Therefore, PRJ_111 *avoids asserting classification accuracy, precision, recall, or F1-score* on real broadcast data. Model sensitivity is validated through controlled synthetic perturbation experiments, wherein known corruptions (bit flips, synthetic sync byte drops, and container truncations) are injected into verified captures to demonstrate that the detector flags abnormal intervals with $s >= 0.5000$.

== C. Feature F3: Pattern and Entropy Analysis
Feature F3 identifies structural patterns and multiplex characteristics across stream progress:
- *MPEG-TS PID Distribution & Shannon Entropy:* Computes individual packet counts and percentage shares per PID. The dominant PID and Shannon entropy @shannon1948 are evaluated:
  $ H_"PID" = - sum_(k=1)^P p_k log_2 p_k, quad p_k = N_k / (sum_(j=1)^P N_j) $ <eq_entropy>
- *PAT/PMT Program Structure:* Identifies Program Association Tables ($"PID" = 0$) and Program Map Tables, tracking program multiplex recurrence @etsi_si.
- *GSE Protocol Mapping:* Classifies encapsulated protocol types (`GSE_EXT_NPA`, IPv4, IPv6) and quantifies fragmentation ratios ($N_"frag" / N_"total"$).
- *BBFrame Mode Transitions:* Tracks shifts in modulation profiles (ACM vs. CCM), Single vs. Multiple Input Stream allocations, and DFL distribution clustering.

== D. Feature F4: Spatial Activity Timeline
Feature F4 provides continuous visual mapping of stream activity across spatial progress (@fig_timeline).

*Absence of Fabricated Timestamps:* Offline receiver bitstreams captured from demodulator test points lack calibrated broadcast wall-clock telemetry. Assigning synthetic timestamps or calculating fictitious throughput rates (e.g., "15.4 Mbps") creates false precision. PRJ_111 indexes all timeline events strictly by:
1) *Physical Byte Offset:* $[B_"start", B_"end"]$ indicating exact octet positions in the capture file.
2) *Container Sequence Index:* Unit indices $[U_"start", U_"end"]$ tracking sequential packet, PDU, or frame numbers.

The timeline visualizes rolling F1 stream health ($[0, 100%]$), F2 anomaly scores ($[0.0, 1.0]$) alongside the $0.5000$ threshold line, payload density (KB per window), and format-specific telemetry without fabricating clock timestamps.

#figure(
  image("paper_assets/fig_timeline_view.png", width: 95%),
  caption: [Spatial activity timeline (Feature F4) charting rolling stream health, anomaly scores with decision threshold ($s = 0.5000$), payload density, and PID entropy indexed strictly by physical byte offsets.]
) <fig_timeline>

== E. Feature F5: Diagnostic Anomaly Explanation
Feature F5 bridges unsupervised machine learning and domain engineering by attributing flagged anomalies to specific metric deviations (@fig_anomaly).

For each feature $j$ in anomalous window $W_i$, deviation from the stream baseline is evaluated using an operational dispersion model:
$ z_(i, j) = (x_(i, j) - mu_j) / (max(sigma_j, epsilon_j)) $ <eq_zscore>
where $mu_j$ is the stream mean for feature $j$, $sigma_j$ is standard deviation, and $epsilon_j$ is an operational dispersion floor preventing division-by-zero on invariant channels.

To eliminate unbounded numerical artifacts while maintaining mathematical interpretability, PRJ_111 bounds the Z-score:
$ z_"bounded" = "clamp"(z_(i, j), -20.0, +20.0) $ <eq_zclamp>
The magnitude $|z_"bounded"|$ is accompanied by an explicit deviation direction: `ABOVE_BASELINE` ($z > 0$) or `BELOW_BASELINE` ($z < 0$).

*Physical-Layer Domain Safety Guard:* PRJ_111 operates strictly on digital post-demodulator bitstreams. Without access to baseband constellation measurements or RF tuner AGC levels, the application *avoids asserting physical-layer root causes*. F5 diagnoses are constrained to digital observations (e.g., "Elevated adaptation field frequency" or "Recording termination boundary"), avoiding speculative claims such as "rain fade," "LNB drift," or "transponder power drop."

#figure(
  image("paper_assets/fig_anomaly_view.png", width: 95%),
  caption: [Flagged anomaly windows and diagnostic attribution table (Features F2 and F5) displaying unit ranges, byte offsets, anomaly scores, and Bounded Z-Score explanations with deviation directionality.]
) <fig_anomaly>

== F. Feature F6: Semantic Stream Comparison Engine
Feature F6 provides differential comparison between two analyzed streams (*Stream A* and *Stream B*) as shown in @fig_comparison.

*The Cross-Format Semantic Barrier:* A key architectural contribution of PRJ_111 is the *Cross-Format Semantic Barrier*. Metrics sharing identical nomenclature inside `CommonMetrics` are *not* assumed to be comparable across formats:
- *Comparable Metrics (2):* `total_payload_bytes` (an octet of user data represents an invariant physical quantity) and `integrity_ratio` (dimensionless syntactic compliance proportion $[0.0, 1.0]$).
- *Non-Comparable Metrics (9):* `total_units`, `valid_units`, `invalid_units`, `truncated_units`, `mean_payload_bytes`, `payload_ratio`, `error_count`, `error_rate`, and `entropy` are blocked cross-format with explicit engineering justifications.

For comparable metrics, differences are quantified without mathematical singularities:
$ Delta_"abs" = B - A $ <eq_delta_abs>
$ Delta_"rel" = cases(
  (B - A) / A times 100% & "if " A > 0,
  "Undefined (Critical)" & "if " A = 0 " and " B > 0,
  0.0% & "if " A = 0 " and " B = 0,
) $ <eq_delta_rel>

Differences are classified into a four-tier significance hierarchy:
- *`NEGLIGIBLE`:* $|Delta_"rel"| < 2.0%$
- *`MINOR`:* $2.0% <= |Delta_"rel"| < 10.0%$
- *`SUBSTANTIAL`:* $10.0% <= |Delta_"rel"| < 50.0%$
- *`CRITICAL`:* $|Delta_"rel"| >= 50.0%$ (or non-zero error emergence from zero baseline)

Windows are synchronized via direct-index overlap: $i in [0, min(N_A, N_B) - 1]$. Trailing windows in asymmetric captures are recorded under `unaligned_windows` as capture duration differences, not transmission loss.

#figure(
  image("paper_assets/fig_comparison_view.png", width: 95%),
  caption: [Stream comparison interface (Feature F6) evaluating MPEG-TS against corrupted TS, highlighting direct-index window alignment, payload delta (-0.06%), and the dynamic semantic audit table.]
) <fig_comparison>

== G. Feature F7: Automatic Multi-Format Reporting
Feature F7 synthesizes F1--F6 analytical results into exportable executive reports (JSON, Markdown, CP-1252-safe Plain Text, and Standalone HTML5) as illustrated in @fig_report.

All findings generated by F7 are categorized under a formal tripartite epistemological taxonomy:
1) *`OBSERVED_FACT`:* Direct, deterministic physical measurements directly verifiable in stream syntax (e.g., `total_units = 18176`, `sync_byte_errors = 0`).
2) *`STATISTICAL_FINDING`:* Quantities derived through statistical or machine learning models (e.g., `health_score = 100.0`, `anomalous_windows = 5`, `peak_anomaly_score = 0.8576`).
3) *`ENGINEERING_INTERPRETATION`:* Domain-bounded diagnostic attributions constrained strictly to digital bitstream characteristics (e.g., "Capture termination boundary accounts for partial trailing window").

#figure(
  image("paper_assets/fig_report_view.png", width: 95%),
  caption: [Multi-format diagnostic report generation view (Feature F7) showing tripartite findings categorization and one-click export controls.]
) <fig_report>

= VI. Experimental Setup and Datasets

The system was evaluated against four authoritative satellite captures stored in `01_RAW_DATA/`:
1) *MPEG-TS Clean Capture (`01_RAW_DATA/03_TS/DVBS2_toolkit/sample.ts`):* 3,417,088 bytes of off-air DVB-S2 satellite television broadcast, captured via DVBS2_toolkit, containing 18,176 fixed 188-byte packets.
2) *MPEG-TS Corrupted Capture (`01_RAW_DATA/03_TS/DVBS2_toolkit/corrupted_sample.ts`):* 3,417,088 bytes containing 11 corrupted synchronization bytes in the initial segment.
3) *GSE Authoritative Capture (`01_RAW_DATA/02_GSE/GSExtract/sample.ts`):* 9,324 bytes containing 14 variable-length GSE PDUs carrying encapsulated IPv4 datagrams, captured via GSExtract. (The filename `sample.ts` is preserved as the authoritative project container file).
4) *DVB-S2 Baseband Frame Capture (`01_RAW_DATA/01_BBFRAME_GSE/dvb-s2_bb_example.pcap`):* 2,349,376 bytes containing 4,309 DVB-S2 Baseband Frames with ACM and SIS/MIS configuration.

= VII. Results and Discussion

Empirical results across the authoritative captures are documented in Tables II through VI.

#figure(
  placement: top,
  scope: "parent",
  caption: [MPEG-TS Health and Priority-1 Integrity Results],
  table(
    columns: (2.2fr, 1.1fr, 1.1fr, 1.0fr, 1.0fr, 1.5fr, 1.1fr, 1.3fr),
    stroke: none,
    table.hline(stroke: 1.2pt),
    table.header(
      [*Stream Capture*], [*Yielded Pkts*], [*Sync Int.*], [*TEI*], [*CC*], [*Net Payload*], [*Health*], [*Status*]
    ),
    table.hline(stroke: 0.6pt),
    [`sample.ts` (Clean)], [18,176], [100.0%], [0 (0.00%)], [0 (0.00%)], [3,267,305 B], [100.0%], [HEALTHY],
    [`corrupted_sample.ts`], [18,168], [100.0%], [4 (0.02%)], [0 (0.00%)], [3,265,277 B], [99.67%], [HEALTHY],
    table.hline(stroke: 1.2pt),
  )
) <tab_ts>

== A. MPEG-TS Health and Priority-1 Verification
As shown in Table II, the clean capture `sample.ts` achieved 100.0% sync byte integrity across all 18,176 packets, with 0 TEI errors and 0 continuity counter discontinuities. Net extracted user payload was 3,267,305 bytes, calculated by subtracting 72,704 bytes of fixed 4-byte headers and 77,079 bytes of adaptation field overhead from the 3,417,088-byte file volume. Stream health evaluated to 100.0% (`HEALTHY`).

*Diagnostic Trace of Corrupted TS:* `TSParser` encountered 11 corrupted sync bytes in the initial segment and resynchronized, dropping exactly 8 unaligned packets. The 18,168 yielded packets exhibited 100.0% sync byte integrity. Four packets suffered false sync alignment in payload data resulting in $"TEI" = 4$ in Window 0 (Window 0 health = 70.0%). Windows 1--90 exhibited 100.0% health, yielding an average stream health of $99.67%$, satisfying the $>= 99.0%$ threshold for `HEALTHY`.

== B. GSE Encapsulation and Protocol Results
Telemetry for the authoritative GSE capture (`01_RAW_DATA/02_GSE/GSExtract/sample.ts`) is documented in Table III. The capture contained 14 PDUs totaling 9,324 bytes, yielding 8,764 bytes of net extracted payload (626.0 bytes mean length, ranging from 45 to 1,444 bytes). Fragmentation analysis revealed 6 unfragmented PDUs (42.9%) and 8 fragmented PDUs (57.1%), consisting of 5 first fragments, 0 intermediate fragments, and 3 last fragments. Protocol analysis showed 11 PDUs encapsulated via `GSE_EXT_NPA` (100% of outer headers) and 9 PDUs carrying IPv4 datagrams. Addressing labels comprised 11 6-byte labels and 3 label-less PDUs. All PDUs passed CRC-32 verification with zero failures, yielding 100.0% stream health (`HEALTHY`).

#figure(
  caption: [GSE Encapsulation & Protocol Analysis Results],
  table(
    columns: (1.8fr, 2.3fr, 1.0fr),
    stroke: none,
    table.hline(stroke: 1.2pt),
    table.header(
      [*Metric Parameter*], [*Experimental Observed Value*], [*Category*]
    ),
    table.hline(stroke: 0.6pt),
    [Total Ingested PDUs], [14 PDUs (9,324 Bytes file size)], [`FACT`],
    [Framing Compliance], [100.0% (14 / 14 PDUs Valid)], [`FACT`],
    [Total Payload Extracted], [8,764 Bytes], [`FACT`],
    [Mean PDU Length], [626.0 Bytes (Min: 45 B, Max: 1,444 B)], [`STAT`],
    [Fragmentation Breakdown], [6 Unfrag. (42.9%), 8 Frag. (57.1%)], [`FACT`],
    [Fragment Subtypes], [5 First, 0 Interm., 3 Last Frags.], [`FACT`],
    [Encapsulated Protocols], [`GSE_EXT_NPA`: 11 (100%), `IPv4`: 9], [`FACT`],
    [Addressing Labels], [6-Byte Label: 11, No Label: 3 PDUs], [`FACT`],
    [CRC-32 Checksums], [100.0% Pass (0 Failures)], [`FACT`],
    [F1 Stream Health], [100.0% (`HEALTHY`)], [`STAT`],
    table.hline(stroke: 1.2pt),
  )
) <tab_gse>

== C. DVB-S2 Baseband Frame Transmission Analysis
Results for the baseband frame capture (`dvb-s2_bb_example.pcap`) are presented in Table IV. The file contained 4,309 frames totaling 2,349,376 bytes. All 4,309 frames passed 72-bit BBHeader CRC-8 verification (100.0% valid). MATYPE-1 analysis revealed that 100.0% of frames utilized Adaptive Coding & Modulation (ACM), 99.98% utilized Single Input Stream (SIS, 4,308 frames), 0.02% utilized Multiple Input Stream (MIS, 1 frame), and 100.0% specified a roll-off factor of $alpha = 0.35$.

Net user payload extracted was 1,958,826 bytes. Data Field Length (DFL), *expressed in bits*, ranged from 216 to 10,000 bits (mean: 3,636.72 bits). The DFL distribution exhibited strong modality: 3,698 frames (85.82% modal share) concentrated at exactly 2,992 bits, with a secondary peak at 8,304 bits (406 frames, 9.42%). Stream health evaluated to 100.0% (`HEALTHY`).

#figure(
  caption: [DVB-S2 Baseband Frame Transmission Analysis],
  table(
    columns: (1.7fr, 2.0fr, 1.4fr),
    stroke: none,
    table.hline(stroke: 1.2pt),
    table.header(
      [*Parameter Dimension*], [*Observed Value*], [*Distribution / Share*]
    ),
    table.hline(stroke: 0.6pt),
    [Total Baseband Frames], [4,309 Frames (2,349,376 B)], [100.0% (`FACT`)],
    [BBHeader CRC-8 Checks], [4,309 Passed / 0 Failed], [100.0% Valid (`FACT`)],
    [Stream Input Mode], [SIS: 4,308 / MIS: 1 Frame], [99.98% / 0.02% (`FACT`)],
    [Coding & Modulation], [Adaptive Coding & Mod. (ACM)], [100.0% (4,309/4,309)],
    [Roll-off Factor ($alpha$)], [$alpha = 0.35$], [100.0% (4,309/4,309)],
    [Data Field Payload], [1,958,826 Bytes], [Mean: 454.59 B/frame],
    [Data Field Length (DFL)], [216 to 10,000 Bits], [Mode: 2,992 b (85.8%)],
    table.hline(stroke: 1.2pt),
  )
) <tab_bbframe>

== D. Unsupervised Isolation Forest Anomaly Analysis
Anomaly detection results across all three formats are summarized in Table V. In all three streams, an elevated anomaly score consistently flagged the final window boundary (Window 90 in TS, Window 4 in GSE, Window 86 in BBFrame). This demonstrates the sensitivity of the Isolation Forest to container volume truncation caused by capture termination. Intermediate anomalies (e.g., TS Windows 1, 2, and 12) corresponded to localized statistical multiplexing bursts where single PIDs concentrated up to 98.5% of window bandwidth.

#figure(
  caption: [Isolation Forest Anomaly Detection Results],
  table(
    columns: (1.1fr, 0.9fr, 0.7fr, 0.8fr, 0.8fr, 1.7fr),
    stroke: none,
    table.hline(stroke: 1.2pt),
    table.header(
      [*Format*], [*Window*], [*Total*], [*Anom.*], [*Peak*], [*Anomalous Indices*]
    ),
    table.hline(stroke: 0.6pt),
    [MPEG-TS], [200 Pkts], [91], [5], [0.8576], [`[1, 2, 12, 88, 90]`],
    [GSE], [3 PDUs], [5], [1], [0.5018], [`[4]`],
    [BBFrame], [50 Frms], [87], [5], [0.7406], [`[0, 83, 84, 85, 86]`],
    table.hline(stroke: 1.2pt),
  )
) <tab_anomaly>

#figure(
  placement: top,
  scope: "parent",
  caption: [Cross-Format Stream Comparison Audit (TS vs. BBFrame)],
  table(
    columns: (2.0fr, 1.2fr, 1.4fr, 1.4fr, 2.0fr),
    stroke: none,
    table.hline(stroke: 1.2pt),
    table.header(
      [*Metric Identifier*], [*Semantic Status*], [*Stream A (MPEG-TS)*], [*Stream B (BBFrame)*], [*Relative Delta / Status*]
    ),
    table.hline(stroke: 0.6pt),
    [`total_payload_bytes`], [Comparable], [3,267,305 Bytes], [1,958,826 Bytes], [-40.05% (`SUBSTANTIAL`)],
    [`integrity_ratio`], [Comparable], [1.0000], [1.0000], [0.00% (`NEGLIGIBLE`)],
    [`total_units`], [Shielded], [18,176 packets], [4,309 frames], [Incompatible Dimension],
    [`valid_units`], [Shielded], [18,176 packets], [4,309 frames], [Incompatible Dimension],
    [`invalid_units`], [Shielded], [0 packets], [0 frames], [Incompatible Dimension],
    [`mean_payload_bytes`], [Shielded], [179.76 B/packet], [454.59 B/frame], [Incompatible Container],
    [`payload_ratio`], [Shielded], [1.0000], [1.0000], [Divergent Formulation],
    [`error_count`], [Shielded], [0 errors], [0 errors], [Heterogeneous Failure Modes],
    [`error_rate`], [Shielded], [0.0000], [0.0000], [Heterogeneous Failure Modes],
    [`entropy`], [Shielded], [0.1361 bits], [0.0000 bits], [Distinct State Spaces],
    table.hline(stroke: 1.2pt),
  )
) <tab_comparison>

== E. Cross-Format Stream Comparison Audit
Table VI documents the differential comparison between MPEG-TS (`sample.ts`) and BBFrame (`dvb-s2_bb_example.pcap`). For comparable metrics, `total_payload_bytes` decreased from 3,267,305 B to 1,958,826 B ($Delta_"abs" = -1,308,479.0$ B, $Delta_"rel" = -40.05%$), classified as `SUBSTANTIAL`. The `integrity_ratio` evaluated to 1.0000 for both streams ($Delta_"rel" = 0.00%$, `NEGLIGIBLE`). Exactly nine non-comparable metrics were shielded by the semantic barrier with clear domain rationales.

= VIII. Software Verification and Testing

System stability, regression integrity, and parsing accuracy are verified through an automated test suite executed via Python's standard `unittest` framework:
```powershell
python -m unittest discover -s tests -v
```
*Verification Outcome:* *240 / 240 Tests Passing (100% Pass Rate)* with *0 Failures* and *0 Errors* in 19.86s.
- *Backend Analytical Suite (207 Tests):* Validates deterministic framing decoders (`test_ts_parser.py`, `test_gse_parser.py`, `test_bbframe_parser.py`), unified feature extraction (`test_unified_features.py`), F1 stream health (`test_f1_health.py`), F2 anomaly detection (`test_anomaly.py`), F3 pattern detection (`test_patterns.py`), F4 timeline generation (`test_timeline.py`), F5 anomaly explanations (`test_explanation.py`), F6 stream comparison (`test_comparison.py`), and F7 reporting (`test_report.py`).
- *Frontend Server & Integration Suite (33 Tests):* Validates threaded HTTP server lifecycle, static asset delivery, MIME types, binary file upload staging, directory traversal guards, F6 state reset lifecycle, relative path multi-candidate resolution, content-aware GSE detection, corrupted TS diagnostic accounting, sequential stream replacement lifecycle, and semantically correct HTTP 400 invalid-file handling.

*Note on Epistemic Integrity:* Passing 240/240 automated software tests constitutes rigorous *software verification and regression integrity*. It is explicitly *not* presented as machine learning classification accuracy.

= IX. Limitations and Domain Safety

To maintain scientific integrity, Prototype limitations are documented:
1) *Unlabeled Operational Datasets:* Due to the absence of public, ground-truth-labeled DVB-S2 anomaly datasets, machine learning models are evaluated via unsupervised isolation and synthetic perturbation, rather than supervised benchmark metrics (ROC-AUC).
2) *Post-Demodulator Scope:* The application operates exclusively on digital receiver output bitstreams. It cannot diagnose analog RF physical-layer conditions (e.g., signal-to-noise ratio, carrier frequency offset, or transponder compression).
3) *ETSI TR 101 290 Scope:* Health analysis evaluates selected Priority-1 indicators inspired by ETSI TR 101 290 principles; it does not claim formal certification across all Priority-2 and Priority-3 guidelines.
4) *Offline Spatial Windowing:* Analysis is structured over discrete spatial unit windows rather than real-time continuous sliding windows.
5) *No Temporal Sequence Memory:* The Isolation Forest treats each window independently; temporal sequence dependencies across successive windows are not modeled.

= X. Conclusion and Future Work

This paper has presented the design, implementation, and verification of *PRJ_111*, a specialized software application for analyzing multi-format DVB-S2 receiver output streams. By providing content-aware format detection and modular parsing across MPEG-TS, GSE, and DVB-S2 Baseband Frames, the system overcomes the structural fragmentation of single-format analyzers.

The seven-feature analytical pipeline achieves deterministic stream health evaluation (F1), unsupervised Isolation Forest anomaly detection (F2), structural pattern and entropy analysis (F3), physical spatial activity timelines (F4), bounded Z-score diagnostic anomaly explanations (F5), semantically guarded stream comparisons (F6), and automated tripartite diagnostic reporting (F7). Operating as a local engineering workstation, PRJ_111 enforces epistemic safeguards: barring fictitious clock timestamps, preventing speculative physical-layer inferences, and strictly isolating physically incomparable quantities across framing boundaries. Validated across authoritative satellite captures with 240/240 passing automated tests, PRJ_111 establishes a robust, extensible prototype for satellite ground station monitoring, telecommunications education, and broadcast stream verification.

Future research directions include:
1) *Deep Sequential Architectures:* Investigating bidirectional LSTM and temporal transformer networks to capture long-range sequential correlations across broadcast multiplexes.
2) *Software-Defined Radio Demodulation:* Integrating an upstream GNU Radio or gr-dvbs2 physical-layer front-end to capture simultaneous RF constellation metrics (EVM, MER, SNR) alongside digital framing telemetry.
3) *Hardware Acceleration:* Exploring offloading of PDU and packet header parsing to FPGA or eBPF kernel bypass engines to support high-throughput transponder aggregation.
4) *Benchmark Dataset Publication:* Curating and releasing an open, expert-annotated multi-format DVB-S2 anomaly dataset for the satellite communications research community.

= Acknowledgment

The authors express their sincere gratitude to the *Department of Computer Science and Engineering, Presidency University, Bengaluru*, for providing the laboratory facilities and computing infrastructure necessary to conduct this research. The authors extend special thanks to our project guide, *Irfan Rajab Bhat, Assistant Professor*, for his technical guidance, insightful critiques, and support throughout the development and verification of this project.

#v(0.6em)
#bibliography("references.bib", title: [References], style: "ieee")

]
