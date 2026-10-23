from report_content.builder_utils import (
    add_chapter_title, add_section_heading, add_subsection_heading,
    add_body_p, add_bullet_p, add_callout, add_custom_table
)

def build_ch2(doc):
    add_chapter_title(doc, "CHAPTER 2", "LITERATURE SURVEY")
    
    add_section_heading(doc, "2.1", "Evolution of Satellite Transmission Standards")
    add_body_p(
        doc,
        "The technological trajectory of satellite communications over the past three decades is characterized by continuous efforts to approach "
        "the theoretical channel capacity formulated by Claude Shannon in 1948 [1]. The first generation Digital Video Broadcasting by Satellite standard "
        "(DVB-S, ETSI EN 300 421), ratified in 1994, relied on convolutional inner coding concatenated with Reed-Solomon (204, 188) outer block coding "
        "and Quadrature Phase Shift Keying (QPSK) modulation. DVB-S was exclusively optimized for fixed-rate television broadcasting encapsulated within "
        "188-byte MPEG-2 Transport Stream (MPEG-TS) packets [2]."
    )
    add_body_p(
        doc,
        "In 2005, the DVB consortium published the Second Generation standard (DVB-S2, ETSI EN 302 307-1), authored comprehensively by Morello and "
        "Mignone [3]. DVB-S2 revolutionized satellite communications by replacing convolutional and Reed-Solomon coding with modern Low-Density "
        "Parity-Check (LDPC) codes concatenated with an outer BCH code. This coding scheme achieved a coding gain of 2.5 to 3.0 dB over DVB-S, operating "
        "within 0.7 dB to 1 dB of the Shannon limit across diverse signal-to-noise ratios. Furthermore, DVB-S2 introduced Adaptive Coding and Modulation "
        "(ACM), enabling ground receivers to continuously report channel state conditions back to satellite uplinks, allowing instantaneous transmission "
        "adjustments across 28 distinct MODCOD (Modulation and Coding) states spanning QPSK, 8PSK, 16APSK, and 32APSK."
    )
    add_body_p(
        doc,
        "To support IP-centric data traffic without the heavy encapsulation overhead of MPEG-TS (which incurs 10% to 15% protocol bloat when packing IP packets "
        "into 188-byte containers via Multi-Protocol Encapsulation), ETSI standardized Generic Stream Encapsulation (GSE, ETSI TS 102 606-1) [4]. As analyzed "
        "by Fairhurst and Collina [5], GSE provides a flexible, variable-length Protocol Data Unit (PDU) structure that dynamically encapsulates IPv4, IPv6, "
        "and Ethernet packets with protocol overhead below 2% to 3%. The subsequent DVB-S2X extension (ETSI EN 302 307-2) [6] further expanded granularity "
        "with finer channel bonding, super-framing, and modulation schemes up to 256APSK, intensifying the container diversity observed at receiving ground stations."
    )
    
    add_section_heading(doc, "2.2", "ETSI TR 101 290 Priority-1 Measurement Principles")
    add_body_p(
        doc,
        "To establish uniform quality assessment for digital broadcast transmission, the European Telecommunications Standards Institute formulated "
        "the landmark technical report ETSI TR 101 290: 'Measurement guidelines for DVB systems' [7]. ETSI TR 101 290 establishes a tripartite hierarchy "
        "of diagnostic measurement parameters categorized into Priority-1, Priority-2, and Priority-3 indicators:"
    )
    add_bullet_p(
        doc,
        "Priority-1 Indicators (Basic Decodability)",
        "Crucial parameters required for basic receiver synchronization and decoding. These include TS Sync Loss (loss of the periodic 0x47 framing marker), "
        "Sync Byte Errors (individual corrupted sync markers), PAT (Program Association Table) errors, Continuity Counter (CC) errors (missing, disordered, "
        "or duplicate packets), and PMT (Program Map Table) errors."
    )
    add_bullet_p(
        doc,
        "Priority-2 Indicators (Continuous Quality)",
        "Parameters necessary for uninterrupted continuous transmission, including Transport Error Indicators (TEI), CRC errors in signaling tables, "
        "Program Clock Reference (PCR) jitter and repetition violations, and Elementary Stream (ES) buffer management errors."
    )
    add_bullet_p(
        doc,
        "Priority-3 Indicators (Application Level)",
        "Application-specific parameters such as Network Information Table (NIT) presence, Service Description Table (SDT) errors, and conditional "
        "access entitlement management."
    )
    add_body_p(
        doc,
        "In satellite receiver stream auditing, Priority-1 indicators form the essential bedrock of stream health assessment. If synchronization byte "
        "acquisition is lost or continuity counter sequences exhibit unrecoverable discontinuities, post-processing video decoders and IP reassembly "
        "pipelines fail catastrophically. Consequently, the stream health formulation in PRJ_111 adapts these Priority-1 principles directly to quantify "
        "digital stream integrity."
    )
    
    add_section_heading(doc, "2.3", "General-Purpose Network Protocol Analyzers (Wireshark / tcpdump)")
    add_body_p(
        doc,
        "Wireshark (formerly Ethereal) and its command-line counterpart tcpdump represent the global de-facto standard for network protocol inspection "
        "across enterprise and telecommunications networks. As documented by Orebaugh et al. [8], Wireshark excels at packet-level dissection across "
        "hundreds of application and transport layer protocols (TCP/IP, UDP, HTTP, DNS, RTP). When applied to satellite streams, Wireshark includes basic "
        "dissectors for MPEG-TS (packetizing 188-byte records from network capture files) and limited dissectors for GSE and DVB-S2 BBFrames."
    )
    add_body_p(
        doc,
        "However, Wireshark exhibits severe architectural limitations when deployed as a dedicated satellite stream diagnostic workstation:"
    )
    add_bullet_p(
        doc,
        "Lack of Native Streaming Bitstream Support",
        "Wireshark is fundamentally designed for packet-switched network captures (PCAP/PCAPNG formats) where each packet possesses explicit capture "
        "timestamps and network link-layer encapsulation. When presented with continuous raw binary satellite bitstreams (.ts, .bin), Wireshark requires "
        "artificial wrapper encapsulations or struggles with continuous stream synchronization."
    )
    add_bullet_p(
        doc,
        "Absence of Multiplex Entropy and Dynamic Health Accounting",
        "Wireshark provides packet lists and protocol trees but lacks native mathematical routines to calculate Shannon multiplex entropy, sliding-window "
        "container distribution metrics, or ETSI TR 101 290 Priority-1 composite health scores."
    )
    add_bullet_p(
        doc,
        "No Machine Learning Anomaly Detection",
        "Wireshark relies entirely on static display filters and predefined protocol syntax rules. It possesses zero capability for unsupervised "
        "statistical learning, anomaly score attribution, or automatic diagnostic report generation."
    )
    
    add_section_heading(doc, "2.4", "Dedicated Broadcast Transport Stream Analyzers")
    add_body_p(
        doc,
        "In commercial broadcast engineering, specialized hardware and software transport stream analyzers are widely utilized. Prominent commercial "
        "solutions include DekTec StreamXpert [9], Rohde & Schwarz R&S BTC Broadcast Test Center [10], and open-source specialized tools such as DVBInspector [11]. "
        "DekTec StreamXpert provides comprehensive ETSI TR 101 290 real-time compliance monitoring, bit rate tracking, and PSI/SI table parsing when coupled "
        "with proprietary DekTec PCI Express or USB receiver hardware."
    )
    add_body_p(
        doc,
        "Similarly, DVBInspector is a valuable open-source Java application that performs offline structural parsing of MPEG-TS files, decoding PSI/SI "
        "descriptors, DSM-CC carousels, and subtitle streams. However, these dedicated broadcast analyzers share several fundamental drawbacks: (1) They "
        "are almost universally restricted to MPEG-TS, failing completely when presented with IP-over-satellite Generic Stream Encapsulation (GSE) or native "
        "DVB-S2 Baseband Frames; (2) They are built upon rigid static thresholds that trigger excessive false alarms during dynamic ACM rate switching; (3) "
        "Commercial solutions enforce vendor lock-in with costs exceeding $15,000 to $40,000 per workstation; and (4) They lack explainable machine learning "
        "attributions and cross-format semantic comparison capabilities."
    )
    
    add_section_heading(doc, "2.5", "Machine Learning in Telemetry Anomaly Detection")
    add_body_p(
        doc,
        "The application of machine learning for anomaly detection in telecommunications and telemetry time-series has expanded rapidly over the past "
        "decade. In their definitive survey on anomaly detection, Chandola, Banerjee, and Kumar [12] classified anomaly detection methods into supervised, "
        "semi-supervised, and unsupervised paradigms. In satellite receiver stream monitoring, supervised methods (such as Support Vector Machines, Random "
        "Forests, or deep neural networks) are fundamentally hindered by the severe scarcity of pre-labeled, ground-truth anomalous bitstream datasets. Physical "
        "satellite failures, atmospheric attenuation events, and multiplex corruptions are rare and structurally unpredictable, rendering supervised "
        "classification prone to overfitting and poor generalization."
    )
    add_body_p(
        doc,
        "Consequently, unsupervised anomaly detection techniques are optimal for stream telemetry. Pimentel et al. [13] reviewed novelty detection methods, "
        "highlighting distance-based, density-based, and tree-based isolation mechanisms. Among these, the Isolation Forest algorithm, pioneered by Liu, Ting, "
        "and Zhou [14], has emerged as the premier algorithm for high-dimensional, unsupervised anomaly detection. Unlike traditional density-based methods "
        "(such as Local Outlier Factor or DBSCAN) which compute pairwise Euclidean distances with $O(N^2)$ computational complexity, Isolation Forest explicitly "
        "isolates anomalies by constructing ensembles of random isolation trees (iTrees). Because anomalous observations have attribute values distinct from "
        "normal clusters, they are isolated near the root of the trees, resulting in noticeably shorter average path lengths with a linear $O(N \\log N)$ "
        "time complexity and minimal memory consumption [15]."
    )
    
    add_section_heading(doc, "2.6", "Explainable AI (XAI) in Diagnostic Monitoring")
    add_body_p(
        doc,
        "While machine learning models can accurately identify anomalous intervals in complex bitstreams, operational deployment in satellite ground stations "
        "demands diagnostic interpretability. As emphasized by Guidotti et al. [16] in their survey on explainable artificial intelligence, a black-box scalar "
        "anomaly score provides insufficient actionable intelligence for a telecommunications technician. The operator requires precise knowledge of which "
        "specific physical telemetry parameters deviated from expected distributions and by how much."
    )
    add_body_p(
        doc,
        "Common model-agnostic explanation frameworks such as SHAP (Shapley Additive Explanations) [17] and LIME (Local Interpretable Model-agnostic Explanations) "
        "compute feature importance through combinatorial feature perturbation. However, these methods introduce severe computational overhead that is "
        "incompatible with high-throughput bitstream monitoring. In PRJ_111, this challenge is resolved through an optimized, bounded signed Z-score "
        "attribution engine that computes localized feature deviations relative to rolling baseline statistics in $O(D)$ time complexity per window, delivering "
        "instantaneous, mathematically bounded, and intuitive diagnostic rationales."
    )
    
    add_section_heading(doc, "2.7", "Streaming Bitstream Processing and Chunked Ingestion Paradigms")
    add_body_p(
        doc,
        "Processing continuous multi-gigabyte satellite bitstreams on commercial workstation hardware necessitates memory-efficient streaming architectures. "
        "Traditional desktop utilities employ monolithic in-memory buffers (`read_all()`), which causes rapid process exhaustion and crashes when ingesting "
        "files exceeding physical RAM capacities. Modern stream processing systems, such as Apache Beam [18] and Reactive Streams [19], demonstrate the "
        "necessity of memory-bounded chunked ingestion pipelines."
    )
    add_body_p(
        doc,
        "In satellite stream parsing, chunked ingestion introduces boundary synchronization hazards. If an arbitrary chunk boundary slices through a 188-byte "
        "MPEG-TS packet or a variable-length GSE PDU header, the parser must maintain persistent internal carry-over state to seamlessly stitch fractional "
        "frames across chunk boundaries without desynchronization. Engineering this streaming state machine ensures that PRJ_111 processes arbitrarily large "
        "satellite captures within a fixed, bounded memory footprint (64 KB buffers)."
    )
    
    add_section_heading(doc, "2.8", "Synthesis of Literature and Comparative Framework")
    add_body_p(
        doc,
        "A systematic synthesis of the existing literature reveals that while individual components—such as ETSI TR 101 290 measurement rules, GSE "
        "encapsulation definitions, and Isolation Forest algorithms—are thoroughly established in isolation, no unified, open-architecture software platform "
        "integrates them into a cohesive post-demodulation diagnostic workstation. Table 2.1 summarizes the comparative capabilities of related tools "
        "against the design targets established for PRJ_111."
    )
    
    table_2_1_headers = ["Functional Capability", "Wireshark [8]", "DekTec StreamXpert [9]", "DVBInspector [11]", "PRJ_111 (Proposed)"]
    table_2_1_data = [
        ["MPEG-TS 188B Packet Parsing", "Supported (via PCAP)", "Supported (Real-time)", "Supported (Offline)", "Supported (Streaming & File)"],
        ["GSE PDU De-encapsulation", "Partial Dissector", "Not Supported", "Not Supported", "Fully Supported (Frag tracking)"],
        ["DVB-S2 BBFrame & CRC-8", "Limited Dissector", "Not Supported", "Not Supported", "Fully Supported (Table CRC-8)"],
        ["ETSI TR 101 290 Priority-1", "Not Supported", "Fully Supported (P1-P3)", "Partial (P1 checks)", "Supported (F1 Health Score)"],
        ["Unsupervised Anomaly ML", "Not Supported", "Not Supported", "Not Supported", "Supported (Isolation Forest F2)"],
        ["Explainable XAI Attribution", "Not Supported", "Not Supported", "Not Supported", "Supported (Clamped Z-score F5)"],
        ["Physical Offset Navigation", "Packet Index Only", "Time Offset Only", "Packet Index Only", "Supported (Hex Offsets 0x... F4)"],
        ["Cross-Format Semantic Barrier", "Not Supported", "Not Supported", "Not Supported", "Supported (Audit Shield F6)"],
        ["Automated Multi-Format Reports", "Basic Summary", "Proprietary PDF", "Text/HTML Export", "Supported (JSON/MD/HTML/TXT F7)"],
        ["System Cost & Deployment", "Open-Source / Free", "Proprietary ($15k-$40k)", "Open-Source / Free", "Open-Source Software COTS"]
    ]
    add_custom_table(doc, "Table 2.1: Comparison of Related DVB Stream Analysis Utilities", table_2_1_headers, table_2_1_data, col_widths=[1.8, 1.2, 1.3, 1.2, 1.5])
