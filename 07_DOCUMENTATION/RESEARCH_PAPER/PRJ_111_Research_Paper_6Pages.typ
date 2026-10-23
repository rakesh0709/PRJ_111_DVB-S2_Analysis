#set page(
  paper: "us-letter",
  margin: (top: 0.70in, bottom: 0.70in, left: 0.65in, right: 0.65in),
  footer: context [
    #set text(font: "Times New Roman", size: 8.5pt)
    #set align(center)
    #counter(page).display("1")
  ]
)

#set text(font: "Times New Roman", size: 10pt)
#set par(justify: true, leading: 0.50em, first-line-indent: 1.15em)
#set math.equation(numbering: "(1)")

#show heading.where(level: 1): it => block(width: 100%, below: 0.45em, above: 0.80em)[
  #set align(center)
  #set text(size: 10pt, weight: "bold")
  #smallcaps(it.body)
]

#show heading.where(level: 2): it => block(below: 0.32em, above: 0.58em)[
  #set text(size: 10pt, weight: "bold", style: "italic")
  #it.body
]

#show figure.where(kind: table): set figure.caption(position: top)
#show figure: set block(spacing: 0.6em)
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

#show bibliography: set text(size: 8.2pt)
#show bibliography: set par(leading: 0.38em, spacing: 0.40em)

#align(center)[
  #v(0.04in)
  #text(size: 16.5pt, weight: "bold")[Development of a Multi-Format DVB-S2 Receiver Output \ Stream Analyzer with Anomaly Detection and Diagnostic Reporting]
  
  #v(0.8em)
  #grid(
    columns: (1fr, 1fr, 1fr),
    align: center,
    gutter: 1em,
    [
      #text(size: 10.5pt, weight: "bold")[Y Vengala Rao] \
      #text(size: 8.5pt)[Roll No: 20231COM0001] \
      #text(size: 8.5pt, style: "italic")[Dept. of Computer Science & Eng.] \
      #text(size: 8.5pt)[Presidency University, India]
    ],
    [
      #text(size: 10.5pt, weight: "bold")[Sk Samad] \
      #text(size: 8.5pt)[Roll No: 20231COM0031] \
      #text(size: 8.5pt, style: "italic")[Dept. of Computer Science & Eng.] \
      #text(size: 8.5pt)[Presidency University, India]
    ],
    [
      #text(size: 10.5pt, weight: "bold")[C Rakeshwar] \
      #text(size: 8.5pt)[Roll No: 20231COM0008] \
      #text(size: 8.5pt, style: "italic")[Dept. of Computer Science & Eng.] \
      #text(size: 8.5pt)[Presidency University, India]
    ]
  )
  #v(0.6em)
]

#columns(2, gutter: 0.20in)[

#block(inset: (bottom: 0.35em))[
  #set par(first-line-indent: 0pt)
  #text(weight: "bold")[_Abstract_—]#text(size: 9pt)[Satellite communication networks rely on DVB-S2 to carry broadband data, cellular backhaul, and high-definition video over geostationary and non-geostationary links. In physical ground stations, receiver demodulators hand off decoded bitstreams across three fundamentally incompatible container formats: MPEG-2 Transport Streams (MPEG-TS), Generic Stream Encapsulation (GSE), and native DVB-S2 Baseband Frames (BBFrames). Diagnosing faults across these disparate streams is frustratingly difficult. Each format uses different packet boundaries, synchronization schemes, and error markers, while conventional network analyzers and broadcast tools generally support only one format at a time. In this paper, we present PRJ_111, a self-contained software suite for multi-format DVB-S2 receiver stream analysis. The system incorporates an integrated seven-stage analytical pipeline providing deterministic stream health accounting rooted in ETSI TR 101 290 Priority-1 criteria, unsupervised anomaly isolation utilizing format-segregated Isolation Forest ensembles, Shannon entropy and multiplex distribution profiling, byte-referenced physical activity mapping, clamped Z-score diagnostic attribution, semantically shielded cross-format stream differentials, and automated diagnostic synthesis structured around an empirical tripartite epistemology. Empirical validation on broadcast satellite captures demonstrates deterministic stream accounting (100.0% integrity on nominal streams; 99.67% on corrupted captures with byte-accurate transport error tracking), unsupervised localization of multiplex burst transients and file truncation boundaries, and rigorous semantic separation in cross-format differentials. System robustness is validated through an automated regression suite of 304 tests (268 backend modules and 36 frontend integration tests) attaining a 100% verification pass rate with zero failures, zero errors, and zero omissions.]

  #v(0.4em)
  #text(weight: "bold")[_Index Terms_—]#text(size: 9pt, style: "italic")[Anomaly detection, Baseband frame, Digital video broadcasting, DVB-S2, Feature extraction, Generic stream encapsulation, Isolation Forest, MPEG transport stream, Receiver output analysis, Stream analysis.]
]

= I. Introduction

In contemporary broadband satellite communications, physical-layer signaling and frame boundary synchronization under impaired channel conditions require robust joint detection methods as established by Liao et al. @liao2024. Furthermore, evaluating receiver resilience against malformed stream containers requires rigorous test-creation methodologies such as the transport stream fuzzing framework established by Izumi et al. @izumi2023. Additionally, monitoring continuous streaming telemetry under concept drift necessitates modern streaming anomaly detection benchmarks, as systematically evaluated by Cao et al. @cao2024. Satellite links operating under the DVB-S2 standard @etsi_dvbs2 handle massive volumes of broadcast video, broadband Internet traffic, and corporate trunking. Following carrier recovery, matched filtering, and dual-stage forward error correction (FEC) using inner LDPC and outer BCH codes @morello2006, the demodulator delivers a raw digital stream to host processing hardware.

In real-world ground stations and teleports, however, this post-demodulator output does not come in a single neat format. Depending on how the transponder was provisioned, operators receive one of three distinct framing layers:
(1) *MPEG-2 Transport Stream (MPEG-TS):* The long-standing broadcast standard @iso_mpegts, packaging data into rigid 188-byte packets synchronized by `0x47` sync octets, with 13-bit Program Identifiers (PIDs) and 4-bit continuity counters.
(2) *Generic Stream Encapsulation (GSE):* The modern IP encapsulation protocol @etsi_gse, which wraps variable-length network datagrams (IPv4, IPv6) with 2-bit fragmentation headers and CRC-32 checksums, avoiding MPEG-TS overhead.
(3) *DVB-S2 Baseband Frames (BBFrame):* The direct physical-link container @etsi_dvbs2, containing an 80-bit baseband header, Mode Adaptation flags (MATYPE), a Data Field Length (DFL) indicator, and an 8-bit CRC.

Troubleshooting these streams during station commissioning or downlink outages is often a painful process @luisi2020. General-purpose network analyzers (such as Wireshark) assume Ethernet frame encapsulation, necessitating custom external dissector plugins that lack native support for raw concatenated transport streams or unencapsulated baseband bitstreams @minoli2015. In contrast, specialized broadcast hardware appliances remain overwhelmingly locked to MPEG-TS, providing minimal native parsing for modern DVB-S2 baseband frames or GSE IP encapsulation @luisi2020.

Furthermore, field engineers face three recurring traps when analyzing captured streams:
1) *Brittle Parsers and Misidentified Files:* Raw captures arrive as unlabeled binary files (`.ts`, `.bin`, `.pcap`). Simple file-extension checks frequently guess wrong, and fragile parsers crash whenever they hit a corrupted packet or lost sync byte.
2) *Comparing Apples to Oranges:* Naively comparing packet counts between 188-byte MPEG-TS packets and 7-kilobyte Baseband Frames leads to meaningless conclusions, confusing operators during multi-feed audits.
3) *Speculative Root Causes and Fake Timestamps:* Many commercial tools invent smooth Megabit-per-second rate charts or guess at physical-layer issues (like blaming rain fade for packet drops) without access to actual receiver clock signals or signal-to-noise ratios.

To overcome these limitations, this paper presents *PRJ_111*, a specialized, modular software application engineered for multi-format DVB-S2 receiver output stream analysis. PRJ_111 establishes an integrated seven-feature analytical pipeline (F1--F7) that performs content-aware format sniffer ingestion, deterministic framing parsing, unified feature extraction, rule-based stream health analysis (F1), unsupervised Isolation Forest anomaly detection (F2), structural pattern and entropy analysis (F3), physical spatial activity timelines (F4), bounded Z-score diagnostic anomaly explanations (F5), semantically guarded stream comparisons (F6), and automated multi-format diagnostic report generation (F7).

= II. Related Work

The DVB-S2 standard (ETSI EN 302 307-1) governs physical framing, forward error correction, and modulation, specifying Adaptive Coding and Modulation (ACM) alongside native baseband containers @etsi_dvbs2. Morello et al. @morello2006 evaluated the physical-layer mechanisms of DVB-S2, demonstrating how variable user datagrams are packed into baseband structures safeguarded by concatenated inner LDPC and outer BCH codes. Casini et al. @casini2004 explored higher-order modulation schemes spanning QPSK through 32-APSK, examining the 80-bit Baseband Header (BBHeader), square-root raised cosine roll-off values ($alpha in {0.20, 0.25, 0.35}$), and Data Field Length (DFL) bit allocation. For physical-layer signaling identification and frame boundary synchronization under low-SNR reception, Liao et al. @liao2024 developed an efficient joint detection method for DVB-S2 signaling codes.

For network-layer packet distribution, Fairhurst et al. @fairhurst2010 formulated Generic Stream Encapsulation (ETSI TS 102 606-1) @etsi_gse as a low-overhead successor to Multi-Protocol Encapsulation (MPE over MPEG-TS) and Unidirectional Lightweight Encapsulation (ULE, RFC 4326) @rfc4326. GSE standardizes variable-length protocol data units carrying native IP datagrams with per-fragment CRC-32 protection, eliminating the transport stream encapsulation overhead. Meanwhile, digital television transport continues to rely upon the MPEG-2 Transport Stream (ISO/IEC 13818-1) @iso_mpegts. Measurement guidelines for broadcast verification are codified in ETSI TR 101 290 @etsi_tr101290, specifying Priority-1 operational parameters: synchronization loss, Transport Error Indicator (TEI) flags, and Continuity Counter (CC) sequence violations.

Luisi et al. @luisi2020 evaluated satellite broadcast monitoring tools, observing that while specialized hardware instruments accurately flag ETSI TR 101 290 Priority-1 defects, they generally lack native parsing capabilities for emerging IP encapsulation schemes (GSE and BBFrames) output by contemporary broadband receivers. Minoli @minoli2015 surveyed network packet inspection software, highlighting that general-purpose sniffers treat raw stream dumps as opaque binary blobs unless enveloped in standard network capture headers (e.g., PCAP). To systematically expose vulnerability and boundary errors in digital TV receivers, Izumi et al. @izumi2023 pioneered a fuzzing-based test-creation methodology that mutates transport stream headers and payloads. PRJ_111 adapts these concepts to incorporate a deterministic fault injection module for empirical parser validation across raw post-demodulator binary bitstreams.

Surveys by Chandola et al. @chandola2009 and Pimentel et al. @pimentel2014 trace the evolution of telemetry anomaly detection. Traditional statistical monitoring depends on rigid, static thresholds, which struggle in statistically multiplexed channels where instantaneous bitrates fluctuate dynamically. Conversely, supervised classification demands extensive ground-truth anomaly annotations @chandola2009. In live satellite telemetry, labeled anomaly corpora are practically nonexistent. To analyze unannotated streaming telemetry, Liu et al. @liu2008 introduced the *Isolation Forest* algorithm, constructing ensembles of random isolation trees (iTrees). Abnormal instances require fewer random partitions to isolate, yielding significantly shorter average tree paths @liu2008. Baggio et al. @baggio2021 proved that Isolation Forest @liu2012 achieves linear computational efficiency ($O(n log n)$) and robust outlier sensitivity compared to distance or density-based clustering models such as k-means++ @arthur2007 and DBSCAN @ester1996. Furthermore, Cao et al. @cao2024 established a systematic benchmark for streaming anomaly detection under continuous concept drift, validating that windowed tree ensembles effectively capture evolving temporal anomalies without requiring external ground truth. PRJ_111 grounds its streaming anomaly detection on these windowed principles.

= III. System Architecture and Workstation Design

We designed PRJ_111 around a clean six-stage pipeline, illustrated in @fig_arch. The software takes raw binary captures from satellite receiver outputs, decodes the container syntax, extracts normalized features, runs analytical engines (F1--F3), plots byte-accurate timelines (F4), explains detected anomalies (F5), performs semantically guarded comparisons (F6), and generates structured diagnostic reports (F7).

#figure(
  placement: top,
  scope: "parent",
  image("assets/architecture_diagram.png", width: 88%),
  caption: [End-to-End Architectural Pipeline of the PRJ_111 DVB-S2 Receiver Output Stream Analyzer (Stages 1 through 6).]
) <fig_arch>

PRJ_111 is implemented in Python 3.12 as a local engineering workstation with zero external cloud or proprietary licensing dependencies:
(a) *Backend Core & Ingestion Engine:* Pure Python modular architecture (`parsers/`, `features/`, `analysis/`, `streaming/`). Supports multi-mode stream processing: Standard in-memory sequential parsing, 64 KB block-buffered Chunked streaming for large continuous captures, and High-Throughput zero-copy memory-mapped (`mmap`) processing.
(b) *Machine Learning Layer:* Scikit-learn (`IsolationForest`) coupled with NumPy and SciPy for numerical vector operations, windowed temporal scoring, and bounded Z-score feature attribution.
(c) *Controlled Fault-Injection Benchmark:* Multi-format synthetic mutation framework inspired by Izumi et al. @izumi2023 (TEI corruption, CC discontinuities, PDU truncation, BBFrame CRC-8 corruption) enabling empirical before-vs-after anomaly sensitivity scoring.
(d) *HTTP Gateway & Workstation:* Multi-threaded native Python HTTP server (`ThreadingHTTPServer`) exposing a RESTful JSON API (`/api/status`, `/api/analyze`, `/api/compare`, `/api/upload`, `/api/export`, `/api/fault-inject`) and Single-Page Application (SPA) dashboard.
(e) *Printable Certification:* Standalone laboratory diagnostic test sheet export with evaluator sign-off blocks.



= IV. Multi-Format Stream Processing

The parsing layer operates directly on raw binary stream captures, providing modular decoders tailored to each standard. Format selection is governed by a content-aware format sniffer:
(1) *MPEG-2 Transport Stream (MPEG-TS):* The MPEG-TS parser processes continuous 188-byte containers specified in ISO/IEC 13818-1 @iso_mpegts. Validates `0x47` sync cadence, flags Transport Error Indicator (TEI) bits, extracts 13-bit Program Identifiers (PIDs), and tracks 4-bit cyclic Continuity Counters (CC) per PID.
(2) *Generic Stream Encapsulation (GSE):* Decodes variable-size protocol data units adhering to ETSI TS 102 606-1 @etsi_gse. Parses 2-bit start/end fragmentation flags, 12-bit length field ($<= 4,095$ bytes payload), 16-bit EtherType (`0x0800` IPv4), label addressing, and CRC-32 syndrome validation.
(3) *DVB-S2 Baseband Frames (BBFrame):* Decodes native baseband frames specified in ETSI EN 302 307-1 @etsi_dvbs2 and analyzed by Liao et al. @liao2024. Validates 80-bit headers via CRC-8 ($G(x) = x^8 + x^7 + x^6 + x^4 + x^2 + 1$), extracts MATYPE-1/2 (SIS/MIS, ACM/CCM, roll-off $alpha$), and measures Data Field Length ($"DFL" in [216, 10000]$ bits).

#figure(
  caption: [Supported Input Format Characteristics],
  table(
    columns: (1.1fr, 1.2fr, 0.9fr, 1.5fr, 1.3fr),
    stroke: none,
    table.hline(stroke: 1.1pt),
    table.header([*Format*], [*Structure*], [*Header*], [*Container Dimension*], [*Checksum*]),
    table.hline(stroke: 0.5pt),
    [MPEG-TS], [Fixed Packet], [4 Bytes], [Fixed 188 Bytes], [Continuity Counter (4b)],
    [GSE], [Variable PDU], [2--8 Bytes], [45--1,444 Bytes (Var.)], [CRC-32 (32 bits)],
    [BBFrame], [Fixed Frame], [10 Bytes], [216--10,000 Bits (DFL)], [CRC-8 (8 bits)],
    table.hline(stroke: 1.1pt),
  )
) <tab_formats>

= V. Feature Engineering and Analytical Pipeline

Telemetry is bifurcated into physical invariants (`CommonMetrics`) and native format-specific metrics (`TSMetrics`, `GSEMetrics`, `BBFrameMetrics`).
(1) *Feature F1 (Stream Health Analysis):* Implements transparent threshold-driven deductive scoring from a 100.0% baseline based on ETSI TR 101 290 P1 criteria @etsi_tr101290:
  $ H(W_i) = max(0.0, 100.0 + sum Delta H) $ <eq_health_win>
  The overall stream health score $H$ is the arithmetic mean across all $N$ evaluated spatial windows:
  $ H = 1 / N sum_(i=1)^N H(W_i) $ <eq_health_total>
  Categorized into `HEALTHY` ($H >= 99.0%$), `WARNING` ($80.0% <= H < 99.0%$), and `CRITICAL` ($H < 80.0%$).
(2) *Feature F2 (AI Anomaly Detection):* Instantiates an ensemble of $T = 100$ isolation trees (`n_estimators=100`, `contamination=0.05`) @liu2008. Following streaming evaluation benchmarks from Cao et al. @cao2024, decision scores $d(bold(x))$ are mapped through a centered logistic sigmoid:
  $ s(bold(x)) = 1 / (1 + e^(8.0 d(bold(x)))) $ <eq_anomaly>
  Flagged anomalous if $s(bold(x)) >= 0.5000$. Operational telemetry is evaluated via synthetic perturbation rather than ungrounded ROC-AUC metrics.
(3) *Feature F3 (Pattern and Entropy Analysis):* Evaluates individual PID shares and Shannon multiplex entropy:
  $ H_"PID" = - sum_(k=1)^P p_k log_2 p_k, quad p_k = N_k / (sum_(j=1)^P N_j) $ <eq_entropy>
(4) *Feature F4 (Spatial Activity Timeline):* Charts rolling health, anomaly scores, and payload density indexed strictly by physical byte offsets ($[B_"start", B_"end"]$) and container indices, eliminating fabricated clock time axes.
(5) *Feature F5 (Diagnostic Anomaly Explanation):* Attributes flagged anomalies to specific metric drivers using bounded Z-scores:
  $ z_"bounded" = "clamp"((x_(i,j) - mu_j) / max(sigma_j, epsilon_j), -20.0, +20.0) $ <eq_zclamp>
(6) *Feature F6 (Semantic Comparison Engine):* Protects cross-format comparisons via an automated semantic barrier. Audits 2 comparable physical invariants (`total_payload_bytes`, `integrity_ratio`) while shielding 9 format-incompatible framing metrics.
(7) *Feature F7 (Automatic Reporting):* Synthesizes diagnostics into JSON, Markdown, HTML, and CSV organized under a tripartite epistemology (`OBSERVED_FACT`, `STATISTICAL_FINDING`, `ENGINEERING_INTERPRETATION`).



= VI. Experimental Results and Discussion

The system was evaluated against four authoritative satellite captures in `01_RAW_DATA/` (Tables II through VI).

#figure(
  caption: [MPEG-TS Health and Priority-1 Integrity Results],
  table(
    columns: (1.8fr, 0.9fr, 0.9fr, 0.8fr, 0.8fr, 1.3fr, 1.0fr),
    stroke: none,
    table.hline(stroke: 1.1pt),
    table.header([*Stream*], [*Pkts*], [*Sync*], [*TEI*], [*CC*], [*Net Payload*], [*Health*]),
    table.hline(stroke: 0.5pt),
    [`sample.ts` (Clean)], [18,176], [100%], [0 (0%)], [0 (0%)], [3,267,305 B], [100.0%],
    [`corrupted_sample`], [18,168], [100%], [4 (0.02%)], [0 (0%)], [3,265,277 B], [99.67%],
    table.hline(stroke: 1.1pt),
  )
) <tab_ts>

(1) *MPEG-TS Health Verification:* Clean `sample.ts` achieved 100.0% sync integrity and 100.0% health across 18,176 packets (3,267,305 B payload). The corrupted stream dropped 8 unaligned packets, yielding 18,168 packets with 4 TEI errors in Window 0, achieving 99.67% average health (`HEALTHY`).
(2) *GSE Protocol Results:* Evaluated 14 PDUs (9,324 B, 8,764 B payload), comprising 6 unfragmented (42.9%) and 8 fragmented PDUs (57.1%). Passed 100% CRC-32 checksums with 100.0% health.
(3) *BBFrame Transmission:* Evaluated 4,309 frames (2,349,376 B, 1,958,826 B payload). Verified 100.0% CRC-8 checks, 100% ACM, and modal DFL of 2,992 bits (85.82% share).
(4) *Isolation Forest Findings:* Consistently flagged container volume truncation at stream termination boundaries (Window 90 in TS, Window 4 in GSE, Window 86 in BBFrame) and localized multiplex burst concentrations.
(5) *Cross-Format Comparison Audit:* Comparing TS against BBFrame revealed a -40.05% payload delta (3,267,305 B vs 1,958,826 B, `SUBSTANTIAL`) and identical 1.0000 integrity ratio (`NEGLIGIBLE`), with 9 framing fields shielded.

#figure(
  caption: [GSE Encapsulation & Protocol Analysis Results],
  table(
    columns: (1.8fr, 2.2fr, 1.0fr),
    stroke: none,
    table.hline(stroke: 1.1pt),
    table.header([*Metric Parameter*], [*Experimental Observed Value*], [*Category*]),
    table.hline(stroke: 0.5pt),
    [Total Ingested PDUs], [14 PDUs (9,324 Bytes)], [`FACT`],
    [Framing Compliance], [100.0% (14 / 14 PDUs Valid)], [`FACT`],
    [Total Payload Extracted], [8,764 Bytes], [`FACT`],
    [Mean PDU Length], [626.0 Bytes (Min: 45 B, Max: 1,444 B)], [`STAT`],
    [Fragmentation Breakdown], [6 Unfrag. (42.9%), 8 Frag. (57.1%)], [`FACT`],
    [Encapsulated Protocols], [`GSE_EXT_NPA`: 11 (100%), `IPv4`: 9], [`FACT`],
    [CRC-32 Checksums], [100.0% Pass (0 Failures)], [`FACT`],
    [F1 Stream Health], [100.0% (`HEALTHY`)], [`STAT`],
    table.hline(stroke: 1.1pt),
  )
) <tab_gse>

#figure(
  caption: [DVB-S2 Baseband Frame Transmission Analysis],
  table(
    columns: (1.7fr, 2.0fr, 1.4fr),
    stroke: none,
    table.hline(stroke: 1.1pt),
    table.header([*Parameter Dimension*], [*Observed Value*], [*Distribution / Share*]),
    table.hline(stroke: 0.5pt),
    [Total Baseband Frames], [4,309 Frames (2,349,376 B)], [100.0% (`FACT`)],
    [BBHeader CRC-8 Checks], [4,309 Passed / 0 Failed], [100.0% Valid (`FACT`)],
    [Stream Input Mode], [SIS: 4,308 / MIS: 1 Frame], [99.98% / 0.02% (`FACT`)],
    [Coding & Modulation], [Adaptive Coding & Mod. (ACM)], [100.0% (4,309/4,309)],
    [Roll-off Factor ($alpha$)], [$alpha = 0.35$], [100.0% (4,309/4,309)],
    [Data Field Payload], [1,958,826 Bytes], [Mean: 454.59 B/frame],
    [Data Field Length (DFL)], [216 to 10,000 Bits], [Mode: 2,992 b (85.8%)],
    table.hline(stroke: 1.1pt),
  )
) <tab_bbframe>

#figure(
  caption: [Isolation Forest Anomaly Detection Results],
  table(
    columns: (1.1fr, 0.9fr, 0.7fr, 0.8fr, 0.8fr, 1.6fr),
    stroke: none,
    table.hline(stroke: 1.1pt),
    table.header([*Format*], [*Window*], [*Total*], [*Anom.*], [*Peak*], [*Anomalous Indices*]),
    table.hline(stroke: 0.5pt),
    [MPEG-TS], [200 Pkts], [91], [5], [0.8576], [`[1, 2, 12, 88, 90]`],
    [GSE], [3 PDUs], [5], [1], [0.5018], [`[4]`],
    [BBFrame], [50 Frms], [87], [5], [0.7406], [`[0, 83, 84, 85, 86]`],
    table.hline(stroke: 1.1pt),
  )
) <tab_anom>

#figure(
  caption: [Cross-Format Stream Comparison Audit (TS vs. BBFrame)],
  table(
    columns: (1.8fr, 1.1fr, 1.2fr, 1.2fr, 1.7fr),
    stroke: none,
    table.hline(stroke: 1.1pt),
    table.header([*Metric Identifier*], [*Semantic Status*], [*Stream A (MPEG-TS)*], [*Stream B (BBFrame)*], [*Relative Delta / Status*]),
    table.hline(stroke: 0.5pt),
    [`total_payload_bytes`], [Comparable], [3,267,305 B], [1,958,826 B], [-40.05% (`SUBSTANTIAL`)],
    [`integrity_ratio`], [Comparable], [1.0000], [1.0000], [0.00% (`NEGLIGIBLE`)],
    [`total_units`], [Shielded], [18,176 pkts], [4,309 frms], [Incompatible Dimension],
    [`error_count`], [Shielded], [0 errors], [0 errors], [Heterogeneous Modes],
    [`entropy`], [Shielded], [0.1361 b], [0.0000 b], [Distinct State Spaces],
    table.hline(stroke: 1.1pt),
  )
) <tab_comp>

= VII. Verification and Limitations

System reliability is validated by an automated regression test suite executed via Python's standard `unittest`:
```powershell
python -m unittest discover -s tests -v
```
(a) *Outcome:* *304 / 304 Tests Passing (100% Pass Rate)* with 0 failures, 0 errors, and 0 skipped in 74.61s (268 backend modules and 36 frontend integration tests). Receiver resilience against malformed stream containers is validated using fault injection mutations inspired by Izumi et al. @izumi2023.
(b) *Domain Safeguards:* PRJ_111 operates strictly post-demodulator on digital streams; it does not measure analog RF parameters (SNR, MER) and indexes timeline events strictly by physical byte offsets.

= VIII. Conclusion and Future Work

PRJ_111 unifies multi-format DVB-S2 receiver output stream analysis across MPEG-TS, GSE, and BBFrames. By combining deterministic health scoring, unsupervised Isolation Forest anomaly detection, physical spatial timelines, bounded Z-score explanations, and semantic comparison shields, it establishes a dependable, offline engineering workstation for ground station telemetry and research. Future extensions include SDR front-end integration and FPGA acceleration.

#v(0.3em)
#set text(size: 8pt)
*Acknowledgment:* The authors thank Presidency University and project guide *Irfan Rajab Bhat, Assistant Professor*, for their technical guidance and computing infrastructure support.

#v(0.2em)
#bibliography("references.bib", title: [References], style: "ieee")

]
