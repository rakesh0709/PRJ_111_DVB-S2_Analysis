from report_content.builder_utils import (
    add_chapter_title, add_section_heading, add_subsection_heading,
    add_body_p, add_bullet_p, add_callout, add_custom_table
)

def build_ch3(doc):
    add_chapter_title(doc, "CHAPTER 3", "RESEARCH GAPS OF EXISTING METHODS")
    
    add_section_heading(doc, "3.1", "Rigid Static Thresholding and Lack of Dynamic Behavioral Modeling")
    add_body_p(
        doc,
        "A primary limitation of existing commercial and open-source stream monitoring probes is their exclusive reliance on static, "
        "deterministic thresholding rules (e.g., triggering an alarm if the continuity counter gap exceeds 0, or if sync loss exceeds 3 packets). "
        "While static thresholds are effective for detecting hard, catastrophic failures in classical fixed-rate broadcasting, they perform "
        "exceptionally poorly in modern DVB-S2 environments utilizing Adaptive Coding and Modulation (ACM) and variable-rate IP encapsulation."
    )
    add_body_p(
        doc,
        "Under dynamic ACM switching, transmission rates and frame burst profiles fluctuate continuously according to atmospheric conditions. "
        "Static thresholds produce severe 'alarm fatigue' by flagging harmless, momentary rate adjustments as critical errors. Conversely, static "
        "rules are entirely blind to subtle, non-deterministic anomalies such as slow drift in component multiplex distributions, silent packet "
        "stuffing inflation, and subtle degradation in encapsulation efficiency that do not breach rigid thresholds but clearly indicate impending "
        "receiver failure or buffer exhaustion."
    )
    
    add_section_heading(doc, "3.2", "Container Fragmentation and Multi-Format Inflexibility")
    add_body_p(
        doc,
        "Modern satellite receivers emit structurally divergent container formats depending on the target service. Direct-to-home broadcast streams "
        "are encapsulated in fixed 188-byte MPEG-TS packets; satellite broadband networks utilize variable-length Generic Stream Encapsulation (GSE) "
        "Protocol Data Units; and native demodulators directly output raw physical-layer Baseband Frames (BBFrames). Existing diagnostic utilities "
        "suffer from severe container siloing:"
    )
    add_bullet_p(
        doc,
        "MPEG-TS Centricity",
        "Legacy broadcast analyzers (such as DekTec StreamXpert or DVBInspector) are hardcoded to 188-byte framing. They cannot parse GSE PDUs or "
        "BBHeader descriptors, rendering them useless for satellite broadband and VSAT networks."
    )
    add_bullet_p(
        doc,
        "General-Purpose Packet Parsers",
        "General network sniffers (such as Wireshark) analyze network packets but lack domain-aware state machines to track multi-PDU GSE fragmentation "
        "(Start/End bit sequences) across continuous raw bitstreams or evaluate 10-byte BBHeader bitwise CRC-8 validity."
    )
    add_body_p(
        doc,
        "Consequently, ground station engineers are forced to maintain disparate, incompatible software tools for each container type, preventing unified "
        "operational oversight across multi-service satellite teleports."
    )
    
    add_section_heading(doc, "3.3", "Artificial Timestamp Inflation vs. Physical Offset Traceability")
    add_body_p(
        doc,
        "When diagnosing bitstream anomalies in a satellite operations center, the technician must locate the exact physical bitstream byte offset "
        "(0x...) where corruption manifested to extract the damaged frame for hex-dump inspection or forensic replay. However, prevailing network tools "
        "such as Wireshark fundamentally rely on capture timestamps (seconds since epoch) derived from the host operating system clock. When reading raw "
        "binary dump files (.ts, .bin, or un-timestamped PCAP files), these tools fabricate artificial delta times or display packet sequence numbers that "
        "have no direct correspondence to physical byte locations on disk."
    )
    add_body_p(
        doc,
        "This absence of physical spatial referencing creates severe friction during ground station investigation. A critical research and engineering "
        "gap is the absence of an analyzer that natively indexes all stream metrics, anomalies, and multiplex events against exact physical byte offsets "
        "from the beginning of the file (0x00000000 to 0x7FFFFFFF), ensuring deterministic spatial traceability."
    )
    
    add_section_heading(doc, "3.4", "Unwarranted Cross-Format Telemetry Bleed and Semantic Incoherence")
    add_body_p(
        doc,
        "In satellite network management, operators frequently compare two receiver output streams—for instance, comparing a primary satellite downlink "
        "against a secondary backup downlink, or evaluating a demodulated baseband stream against an upstream multiplex. However, existing comparison "
        "utilities perform naive line-by-line or byte-by-byte diffing, which completely fails when comparing streams of differing container formats."
    )
    add_body_p(
        doc,
        "Crucially, comparing an MPEG-TS stream with a DVB-S2 Baseband Frame stream involves fundamental dimensional mismatches. An MPEG-TS stream possesses "
        "Packet Identifiers (PIDs), Continuity Counters (CC), and Transport Error Indicators (TEI); a BBFrame stream possesses Mode Adaptation flags (MATYPE), "
        "User Packet Length (UPL), and Data Field Length (DFL). Naive comparative tools attempt to evaluate 'missing PIDs' in BBFrames or compare non-existent "
        "CRC-8 fields in MPEG-TS, generating nonsensical deltas and catastrophic cross-format telemetry bleed. A mathematically robust semantic barrier "
        "that audits common invariant metrics while shielding format-incompatible fields is absent in current tools."
    )
    
    add_section_heading(doc, "3.5", "High Acquisition Cost and Proprietary Lock-in of Dedicated Probes")
    add_body_p(
        doc,
        "Hardware-based broadcast analyzers (e.g., Rohde & Schwarz BTC, DekTec DTA series) require dedicated PCI Express capture cards and proprietary "
        "software licenses costing upwards of $20,000 to $50,000 per installation. These closed-source appliances enforce strict hardware lock-in, cannot "
        "be deployed in virtualized cloud teleports or Docker containers, and offer zero API extensibility for automated ground station scripting. An open, "
        "cross-platform, software-defined solution that runs seamlessly on standard desktop and server hardware is critically needed."
    )
    
    add_section_heading(doc, "3.6", "Diagnostic Opacity and Lack of Root-Cause Explanations")
    add_body_p(
        doc,
        "Existing academic machine learning prototypes that apply outlier detection to network traffic suffer from severe diagnostic opacity. A standard "
        "unsupervised algorithm (e.g., raw k-means clustering or basic one-class SVM) outputs a binary decision ('anomalous' vs 'normal') or a scalar outlier "
        "probability score. When an operator in a satellite operations center is alerted that 'Window 42 is anomalous with score 0.78', the operator has "
        "no insight into what caused the anomaly: Did the stream suffer a sudden burst of null packets? Did component entropy collapse? Did continuity "
        "counter errors spike? Or was there an unexpected shift in packet size distributions?"
    )
    add_body_p(
        doc,
        "Without explainable feature attribution, machine learning anomaly detection remains an academic curiosity rather than an actionable engineering "
        "tool. A lightweight, real-time diagnostic explainer that bridges unsupervised detection and human-interpretable root-cause attribution is a "
        "conspicuous gap in the current state of the art."
    )
    
    add_section_heading(doc, "3.7", "Comprehensive Comparative Matrix")
    add_body_p(
        doc,
        "Table 3.1 establishes a comprehensive, side-by-side architectural and functional comparison between Wireshark (the prevailing open-source network "
        "analyzer) and the PRJ_111 software workstation developed in this capstone project."
    )
    
    table_3_1_headers = ["Analytical Dimension", "Wireshark (General Packet Analyzer)", "PRJ_111 DVB-S2 Stream Analyzer"]
    table_3_1_data = [
        ["Primary Architecture & Scope", "General packet-switched network sniffer (OSI L2–L7)", "Specialized post-demodulator satellite stream workstation"],
        ["Input File Handling", "PCAP/PCAPNG network packet capture format", "Raw binary bitstreams (.ts, .bin, .pcap) & chunked streams"],
        ["Stream Format Support", "Generic dissectors (requires packet boundaries)", "Unified auto-detection across MPEG-TS, GSE, and BBFrame"],
        ["Container Header Validation", "Basic syntax parsing; no DVB-S2 CRC-8 table check", "Full bitwise validation, including ETSI CRC-8 polynomial lookup"],
        ["ETSI TR 101 290 Health", "No composite health score; isolated packet display", "Deterministic F1 Health Score [0, 100] via Priority-1 metrics"],
        ["Multiplex Entropy Analysis", "Not available natively (requires external scripting)", "Built-in Shannon component entropy calculation across windows"],
        ["Machine Learning Detection", "None; static display filters and manual inspection", "Unsupervised Isolation Forest anomaly engine (Feature F2)"],
        ["Diagnostic Attribution (XAI)", "None; manual inspection of individual fields", "Bounded signed Z-score diagnostic explanation (Feature F5)"],
        ["Spatial Telemetry Indexing", "Relative capture timestamps (seconds since epoch)", "Byte-exact physical hexadecimal stream offsets (0x... F4)"],
        ["Cross-Stream Comparison", "Side-by-side packet list diff; severe format bleed", "Semantic Barrier protecting invariant metrics (Feature F6)"],
        ["Automated Report Export", "Basic text/CSV summary export", "Tripartite diagnostic reports across JSON, MD, TXT, HTML (F7)"]
    ]
    add_custom_table(doc, "Table 3.1: Objective Architectural Comparison: Wireshark vs. PRJ_111", table_3_1_headers, table_3_1_data, col_widths=[1.8, 2.3, 2.4])
