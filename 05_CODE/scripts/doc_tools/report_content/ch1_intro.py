from report_content.builder_utils import (
    add_chapter_title, add_section_heading, add_subsection_heading,
    add_body_p, add_bullet_p, add_callout, add_custom_table
)

def build_ch1(doc):
    add_chapter_title(doc, "CHAPTER 1", "INTRODUCTION")
    
    add_section_heading(doc, "1.1", "Background and Context of Satellite Digital Broadcasting")
    add_body_p(
        doc,
        "Modern telecommunications infrastructure relies extensively on satellite communications to deliver high-throughput "
        "broadband internet, direct-to-home (DTH) digital television, cellular backhaul, and tactical defense data links across vast "
        "geographical expanses. The cornerstone of contemporary satellite communications is the Second Generation Digital Video "
        "Broadcasting by Satellite standard (DVB-S2), formally codified by the European Telecommunications Standards Institute under "
        "ETSI EN 302 307. DVB-S2 achieved unprecedented spectral efficiency, operating within 0.7 dB to 1 dB of the theoretical Shannon "
        "capacity limit through the integration of advanced Forward Error Correction (FEC) codes—specifically Low-Density Parity-Check "
        "(LDPC) outer codes concatenated with Bose-Chaudhuri-Hocquenghem (BCH) inner codes—alongside flexible framing and higher-order "
        "modulations including QPSK, 8PSK, 16APSK, and 32APSK."
    )
    add_body_p(
        doc,
        "A transformative capability introduced in DVB-S2 is Adaptive Coding and Modulation (ACM) and Variable Coding and Modulation (VCM). "
        "Under ACM, physical transmission parameters—such as modulation constellation and FEC code rates—dynamically adapt on a "
        "frame-by-frame basis in response to instantaneous channel state telemetry and atmospheric fade conditions reported by receiving "
        "ground stations. While ACM optimizes link utilization across unpredictable satellite propagation channels, it creates extreme "
        "structural heterogeneity in the post-demodulated digital output streams emitted by receiving hardware. Modern ground station "
        "receivers must ingest, demultiplex, and validate bitstreams whose encapsulation formats, frame boundaries, and bit rates vary "
        "dynamically over time."
    )
    
    add_section_heading(doc, "1.2", "Digital Demodulation Output Stream Paradigm")
    add_body_p(
        doc,
        "In satellite receiver architecture, the physical receiving pipeline comprises three primary stages: the radio frequency (RF) "
        "front-end and tuner, the digital demodulator and FEC decoder, and the transport/network de-encapsulation processor. The physical "
        "demodulator locks onto the modulated carrier, synchronizes carrier frequency and phase, computes log-likelihood ratios, and executes "
        "LDPC/BCH error correction. Once error correction is completed, the demodulator emits a digital bitstream. Depending on the operational "
        "profile and architectural deployment of the ground terminal, this post-demodulation output is presented in one of three mutually "
        "exclusive stream container formats:"
    )
    add_bullet_p(
        doc,
        "MPEG-2 Transport Stream (MPEG-TS)",
        "The legacy broadcast multiplex standard (ISO/IEC 13818-1) composed of rigid 188-byte fixed-length packets, each beginning with "
        "a synchronization byte (0x47). MPEG-TS encapsulates video, audio, and data elementary streams multiplexed via 13-bit Packet Identifiers (PIDs)."
    )
    add_bullet_p(
        doc,
        "Generic Stream Encapsulation (GSE)",
        "The modern IP-over-satellite encapsulation protocol (ETSI TS 102 606) engineered to transport native IPv4/IPv6 packets and Ethernet "
        "frames with low protocol overhead. GSE utilizes variable-length Protocol Data Units (PDUs) with dynamic fragmentation (Start/End flags)."
    )
    add_bullet_p(
        doc,
        "DVB-S2 Baseband Frames (BBFrame)",
        "The fundamental transmission container directly emitted by the physical-layer demodulator, consisting of a fixed 10-byte Baseband Header "
        "(BBHeader) followed by a payload data field (DFL bits). The BBHeader encodes transmission mode adaptation flags (MATYPE), user packet "
        "length (UPL), and an 8-bit Cyclic Redundancy Check (CRC-8)."
    )
    
    add_callout(
        doc,
        "Architectural Invariant: Alternative Input Format Reality",
        "A foundational engineering rule established in PRJ_111 is that BBFrame, GSE, and MPEG-TS represent alternative, mutually exclusive "
        "manifestations of the receiver output stream. A physical satellite bitstream captured at a specific digital interface point is either "
        "an MPEG-TS multiplex, a GSE PDU sequence, or raw baseband frames. The analyzer must auto-detect and isolate container semantics natively "
        "rather than attempting invalid multi-layer nested assumptions."
    )
    
    table_1_1_headers = ["Input Format", "Standard Reference", "Framing Mechanism", "Key Telemetry Fields", "Target Service Profile"]
    table_1_1_data = [
        ["MPEG-TS", "ISO/IEC 13818-1", "Fixed 188-byte packets (0x47 sync)", "PID, Continuity Counter, TEI, PUSI, AFC", "Direct-to-Home Broadcast, Legacy IPTV"],
        ["GSE", "ETSI TS 102 606", "Variable-length PDUs (Frag flags)", "Protocol Type, Total Length, Frag S/E, Label", "Satellite Broadband, IP Backhaul, VSAT"],
        ["BBFrame", "ETSI EN 302 307", "10-byte BBHeader + DFL payload", "MATYPE, UPL, DFL, SYNC, SYNCD, CRC-8", "Physical Demodulator Output, Raw Telemetry"]
    ]
    add_custom_table(doc, "Table 1.1: Target Input Formats and Physical Layer Demarcation", table_1_1_headers, table_1_1_data, col_widths=[1.2, 1.3, 1.4, 1.5, 1.1])
    
    add_section_heading(doc, "1.3", "Problem Statement")
    add_body_p(
        doc,
        "Satellite ground station operators, telecommunications engineers, and satellite ISP administrators frequently encounter "
        "subtle stream corruption, multiplex irregularities, and container degradation in post-demodulated digital streams. However, existing "
        "diagnostic tools and operational workflows exhibit critical deficiencies:"
    )
    add_bullet_p(
        doc,
        "Format Fragmentation and Siloed Tools",
        "Legacy broadcast test equipment (e.g., dedicated hardware transport stream analyzers) is rigidly coupled to fixed 188-byte MPEG-TS "
        "and is incapable of ingesting or interpreting Generic Stream Encapsulation (GSE) or raw DVB-S2 Baseband Frames. Conversely, generic network "
        "analyzers such as Wireshark treat satellite bitstreams as opaque byte dumps without native awareness of DVB-S2 baseband header CRC-8 "
        "structures, multiplex entropy, or ETSI TR 101 290 Priority-1 integrity indicators."
    )
    add_bullet_p(
        doc,
        "Rigid Static Thresholding vs. Dynamic Streams",
        "Existing monitoring probes rely on rigid, hardcoded alarm thresholds (e.g., flag error if continuity counter gap exceeds 1). Under dynamic "
        "ACM/VCM switching and variable-rate IP traffic bursts, static thresholds trigger severe false alarm fatigue or completely fail to detect "
        "subtle, non-deterministic anomalies such as structural distribution drift, silent packet stuffing, and component starvation."
    )
    add_bullet_p(
        doc,
        "Lack of Byte-Exact Spatial Traceability",
        "When an anomaly occurs, operators must pinpoint the exact physical bitstream byte offset to inspect the corrupted frame. Existing software "
        "tools inflate artificial timestamps or abstract away the raw byte coordinates, preventing deterministic correlation with physical storage."
    )
    add_bullet_p(
        doc,
        "Opaque Anomaly Classifications",
        "Contemporary machine learning prototypes that apply outlier detection typically output opaque binary labels or raw scalar anomaly scores "
        "without explainable feature attributions, leaving ground station engineers unable to deduce the underlying root cause."
    )
    
    add_section_heading(doc, "1.4", "Project Objectives")
    add_body_p(
        doc,
        "To resolve these operational and engineering challenges, the primary objective of this project is to develop, verify, and deliver PRJ_111: "
        "a self-contained, high-performance software application engineered for comprehensive analysis, deterministic health scoring, unsupervised "
        "anomaly detection, and automated diagnostic synthesis across multi-format DVB-S2 receiver output streams. The specific technical objectives are:"
    )
    add_bullet_p(
        doc,
        "Multi-Format Container Parsing Subsystem",
        "Implement robust, zero-copy parsers capable of deterministic auto-detection and validation across MPEG-TS (188-byte fixed packets), "
        "GSE (variable-length PDUs with fragmentation), and DVB-S2 BBFrames (10-byte headers with bitwise CRC-8 verification)."
    )
    add_bullet_p(
        doc,
        "Deterministic Health Scoring (Feature F1)",
        "Implement an automated stream health assessment engine inspired by ETSI TR 101 290 Priority-1 measurement principles, computing a "
        "bounded health index [0, 100] reflecting sync acquisition stability, continuity counter integrity, and transport error indicators."
    )
    add_bullet_p(
        doc,
        "Unsupervised AI Anomaly Detection (Feature F2)",
        "Integrate an unsupervised Isolation Forest machine learning engine operating over multi-dimensional sliding feature vectors to isolate "
        "structural and statistical multiplex anomalies without requiring pre-labeled training datasets."
    )
    add_bullet_p(
        doc,
        "Structural Multiplex Pattern Detection (Feature F3)",
        "Develop analytical algorithms to compute Shannon multiplex component entropy, identify dominant PIDs, quantify GSE encapsulation "
        "efficiency, and extract modal BBFrame Data Field Lengths (DFL)."
    )
    add_bullet_p(
        doc,
        "Spatial-Offset Timeline Visualization (Feature F4)",
        "Construct an interactive physical offset timeline indexing stream events by hexadecimal byte addresses (0x...) to localize bursts and "
        "anomalous regions without relying on fabricated clock timestamps."
    )
    add_bullet_p(
        doc,
        "Explainable Diagnostic Attribution (Feature F5)",
        "Formulate a bounded signed Z-score diagnostic explanation engine (|Z| <= 20 sigma) that identifies the specific telemetry metrics "
        "contributing to flagged anomalies, providing plain-language engineering rationales."
    )
    add_bullet_p(
        doc,
        "Dual-Stream Comparison with Semantic Guard (Feature F6)",
        "Engineer a differential stream comparison engine governed by an automated semantic barrier that audits format-invariant metrics while "
        "shielding format-incompatible telemetry fields during cross-format comparisons."
    )
    add_bullet_p(
        doc,
        "Automated Multi-Format Diagnostic Reporting (Feature F7)",
        "Build an automated report generation pipeline exporting comprehensive technical assessments across JSON, Markdown, Plain Text, and "
        "standalone interactive HTML formats based on an epistemological tripartite evidence register."
    )
    
    add_section_heading(doc, "1.5", "Scope of the Work")
    add_body_p(
        doc,
        "Defining strict technical boundaries is essential for scientific integrity. The scope of PRJ_111 is delineated as follows:"
    )
    add_bullet_p(
        doc,
        "In-Scope Engineering Deliverables",
        "Analysis of digital bitstreams captured immediately downstream of the satellite demodulator; container parsing for MPEG-TS, GSE, and "
        "DVB-S2 BBFrames; Shannon entropy calculation; Isolation Forest anomaly detection; physical offset mapping; semantic comparison; multi-format "
        "report compilation; memory-bounded chunked streaming (64 KB buffers); synthetic fault injection testing; and an offline SPA operator workstation."
    )
    add_bullet_p(
        doc,
        "Explicit Out-of-Scope Boundaries",
        "PRJ_111 does NOT perform analog RF signal acquisition, tuner control, carrier frequency tracking, or physical LDPC/BCH error decoding. "
        "The software operates exclusively on post-demodulated digital bitstreams. Furthermore, the system does not infer physical-layer RF telemetry "
        "(such as Carrier-to-Noise Ratio CNR or Modulation Error Ratio MER) from digital stream data unless explicit external telemetry metadata is "
        "supplied. Formal ETSI conformance certification is not claimed; all health indicators are described as inspired by ETSI TR 101 290 principles."
    )
    
    add_section_heading(doc, "1.6", "Motivation and Industrial Significance")
    add_body_p(
        doc,
        "In commercial satellite operations, ground station terminals must achieve 99.999% availability. Unexpected outages, multiplex desynchronization, "
        "or subtle packet drops degrade Quality of Service (QoS) and violate Service Level Agreements (SLAs). Traditional hardware analyzers cost "
        "tens of thousands of dollars per unit, possess proprietary locked interfaces, and cannot be readily integrated into modern virtualized ground "
        "station architectures (Cloud-based Teleports). PRJ_111 addresses this critical need by delivering an open-architecture, cross-platform, "
        "software-defined diagnostic workstation that operates on commercial off-the-shelf (COTS) computing hardware."
    )
    add_body_p(
        doc,
        "Furthermore, as satellite networks transition toward direct 5G Non-Terrestrial Network (NTN) integration and multi-beam high-throughput "
        "satellites (HTS), multi-format encapsulation (especially GSE) is rapidly displacing legacy broadcast MPEG-TS. By providing unified, "
        "unsupervised diagnostics across MPEG-TS, GSE, and BBFrames within a single coherent software environment, PRJ_111 bridges the gap between "
        "legacy broadcast engineering and next-generation satellite IP networking."
    )
    
    add_section_heading(doc, "1.7", "Organization of the Report")
    add_body_p(
        doc,
        "The remainder of this report is organized as follows: Chapter 2 presents a comprehensive literature survey covering DVB-S2 standards, ETSI "
        "measurement principles, existing diagnostic tools, and machine learning telemetry models. Chapter 3 examines the research and engineering gaps "
        "inherent in existing systems. Chapter 4 establishes the proposed methodology, mathematical derivations, chunked streaming foundation, and fault "
        "injection architecture. Chapter 5 articulates the detailed functional and operational objectives. Chapter 6 provides an exhaustive system design "
        "and module implementation breakdown. Chapter 7 documents the project execution roadmap and Gantt chart. Chapter 8 summarizes the tangible project "
        "outcomes. Chapter 9 presents the empirical results, experimental benchmark evaluations across physical bitstreams, fault-injection tests, and the "
        "304-test verification suite. Chapter 10 concludes the report and outlines future research enhancements. Finally, Appendices A through D provide "
        "algorithmic pseudocode, genuine workstation screenshots, mandatory enclosures, and the cryptographic verification ledger."
    )
