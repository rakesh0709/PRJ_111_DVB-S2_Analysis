from report_content.builder_utils import (
    add_chapter_title, add_section_heading, add_subsection_heading,
    add_body_p, add_bullet_p, add_callout, add_custom_table
)

def build_ch6(doc):
    add_chapter_title(doc, "CHAPTER 6", "SYSTEM DESIGN AND IMPLEMENTATION")
    
    add_section_heading(doc, "6.1", "Architectural Overview and Layer Separation")
    add_body_p(
        doc,
        "The software architecture of PRJ_111 is designed according to strict principles of separation of concerns, defensive modularity, and "
        "reproducible telemetry accounting. The codebase is organized into five decoupled architectural layers:"
    )
    add_bullet_p(
        doc,
        "1. Ingestion & Pre-Processing Layer (`dvbs2_analyzer.io`)",
        "Responsible for physical file access, multi-tier format sniffing, boundary validation, and chunked streaming buffering."
    )
    add_bullet_p(
        doc,
        "2. Container Parsing Subsystem (`dvbs2_analyzer.parsers`)",
        "Encapsulates format-specific binary state machines for MPEG-TS, GSE, and BBFrame, extracting headers, payloads, and integrity flags."
    )
    add_bullet_p(
        doc,
        "3. Unified Feature Extraction Layer (`dvbs2_analyzer.features`)",
        "Transforms raw container streams into standardized common metrics and 8-dimensional sliding feature vectors."
    )
    add_bullet_p(
        doc,
        "4. Analytical & Intelligence Engines (`dvbs2_analyzer.analysis`)",
        "Houses the seven core diagnostic features (F1 through F7), including ETSI health scoring, Isolation Forest anomaly detection, "
        "spatial timeline indexing, Z-score attribution, semantic stream comparison, and report compilation."
    )
    add_bullet_p(
        doc,
        "5. Presentation & Workstation Server Layer (`dvbs2_analyzer.app`)",
        "Delivers an embedded HTTP REST API and serves a high-performance, dark-themed Single-Page Application (SPA) dashboard."
    )
    
    table_6_1_headers = ["Subsystem Component", "Source Code Module", "Lines of Code", "Key Classes / Functions", "Architectural Role"]
    table_6_1_data = [
        ["Stream Ingestion", "io/stream_handler.py", "248", "StreamHandler, detect_format()", "Format auto-detection and file staging"],
        ["MPEG-TS Parser", "parsers/ts_parser.py", "382", "TSParser, TSPacket, parse()", "188B packet framing, CC, TEI, PID tracking"],
        ["GSE Parser", "parsers/gse_parser.py", "314", "GSEParser, GSEPDU, parse()", "Variable PDU length, S/E fragmentation flags"],
        ["BBFrame Parser", "parsers/bbframe_parser.py", "296", "BBFrameParser, BBFrame, compute_crc8()", "10B BBHeader, MATYPE, UPL, DFL, CRC-8"],
        ["Feature Extractor", "features/extractor.py", "340", "FeatureExtractor, compute_entropy()", "Common metrics, sliding feature vector"],
        ["Stream Health (F1)", "analysis/health.py", "215", "HealthAnalyzer, compute_health_score()", "Priority-1 health score [0, 100]"],
        ["Anomaly Engine (F2)", "analysis/anomaly.py", "265", "AnomalyDetector, fit_predict()", "Isolation Forest sliding window detection"],
        ["Pattern Engine (F3)", "analysis/patterns.py", "280", "PatternDetector, extract_patterns()", "PID distribution, GSE protocol, modal DFL"],
        ["Timeline Engine (F4)", "analysis/timeline.py", "235", "TimelineGenerator, build_timeline()", "Hexadecimal physical byte-offset indexing"],
        ["Diagnostic Explainer (F5)", "analysis/explanation.py", "255", "AnomalyExplanationEngine, explain()", "Clamped signed Z-score feature attribution"],
        ["Comparison Engine (F6)", "analysis/comparison.py", "310", "StreamComparisonEngine, compare()", "Dual-stream audit with Semantic Barrier"],
        ["Report Generator (F7)", "analysis/report.py", "420", "AutomaticReportGenerator, render()", "Tripartite reports: JSON, MD, TXT, HTML"],
        ["Streaming Engine", "io/streaming.py", "225", "StreamingChunkReader, stream_chunks()", "64 KB bounded buffer chunked processing"],
        ["Fault Injector", "fault_injection/injector.py", "290", "FaultInjector, inject_fault()", "Controlled synthetic perturbation utility"],
        ["REST API & Server", "app/server.py", "365", "AnalysisServer, REST API handlers", "Secure multipart upload and static serving"]
    ]
    add_custom_table(doc, "Table 6.1: Subsystem Components, Implementation Files, and Design Roles", table_6_1_headers, table_6_1_data, col_widths=[1.3, 1.6, 0.7, 1.8, 1.6])
    
    add_section_heading(doc, "6.2", "Low-Level Container Parsing Subsystem")
    
    add_subsection_heading(doc, "6.2.1", "MPEG-2 Transport Stream (MPEG-TS) Parser")
    add_body_p(
        doc,
        "The MPEG-TS parser (`TSParser`) ingests continuous binary byte streams and establishes 188-byte packet synchronization. The parser "
        "locates the synchronization marker (`0x47`), advances in 188-byte strides, and verifies that the subsequent packet also begins with `0x47`. "
        "If a sync byte is missing or corrupted, the parser enters an active re-synchronization state machine, scanning sequentially byte-by-byte "
        "until three consecutive valid 188-byte sync points are confirmed, thereby recovering framing lock without catastrophic stream discard."
    )
    add_body_p(
        doc,
        "For every framed packet, `TSParser` unpacks the 4-byte transport header via bitwise masking: Transport Error Indicator (TEI, bit 23), "
        "Payload Unit Start Indicator (PUSI, bit 22), Transport Priority (bit 21), Packet Identifier (PID, bits 8–20, 13 bits), Transport "
        "Scrambling Control (bits 6–7), Adaptation Field Control (AFC, bits 4–5), and Continuity Counter (CC, bits 0–3, 4 bits). The parser "
        "maintains an independent 4-bit CC tracker for every active PID. If the observed CC does not equal $(CC_{\\text{previous}} + 1) \\pmod{16}$ "
        "(excluding legitimate repeated packets carrying adaptation fields or null packets on PID 0x1FFF), a continuity counter gap is flagged and tallied."
    )
    
    add_subsection_heading(doc, "6.2.2", "Generic Stream Encapsulation (GSE) Parser")
    add_body_p(
        doc,
        "The GSE parser (`GSEParser`) processes variable-length Protocol Data Units (PDUs) adhering to ETSI TS 102 606. GSE PDUs do not possess a fixed "
        "packet length. The parser reads the 2-byte GSE header: Start Flag (S, 1 bit), End Flag (E, 1 bit), Length Type (LT, 2 bits), and GSE Length "
        "(12 bits). The 12-bit length field indicates the total number of bytes in the PDU excluding the 2-byte header ($L_{\\text{PDU}} \\le 4095$ bytes)."
    )
    add_body_p(
        doc,
        "The parser implements an explicit fragmentation state machine. When $S=1$ and $E=1$, the PDU carries an unfragmented network packet; when $S=1$ "
        "and $E=0$, the PDU carries the starting fragment of a Subnetwork Dependent Convergence Protocol Network Data Unit (SNDU); when $S=0$ and $E=0$, "
        "it carries intermediate continuation fragments; and when $S=0$ and $E=1$, it terminates the fragmented packet. The parser extracts the "
        "16-bit Protocol Type (e.g., 0x0800 for IPv4, 0x86DD for IPv6) and validates total PDU length against the physical stream boundary."
    )
    
    add_subsection_heading(doc, "6.2.3", "DVB-S2 Baseband Frame (BBFrame) Parser")
    add_body_p(
        doc,
        "The BBFrame parser (`BBFrameParser`) decodes the physical transmission frames defined in ETSI EN 302 307. Each BBFrame begins with a 10-byte "
        "Baseband Header (BBHeader): MATYPE (2 bytes), User Packet Length (UPL, 2 bytes), Data Field Length (DFL, 2 bytes), SYNC byte (1 byte), "
        "SYNCD distance (2 bytes), and CRC-8 (1 byte). The parser decodes MATYPE1 to extract stream configuration (Single/Multiple Input Stream), "
        "Adaptive Coding and Modulation (ACM/VCM status), and roll-off factors (0.35, 0.25, 0.20)."
    )
    add_body_p(
        doc,
        "To guarantee high parsing throughput, the parser verifies the 8-bit CRC over the first 9 header bytes using a precomputed 256-entry table "
        "implementing the generator polynomial $G(x) = x^8 + x^7 + x^6 + x^4 + x^2 + 1$. The Data Field Length (DFL) specifies the exact number "
        "of valid user payload bits in the frame ($K_{\\text{bch}} \\ge \\text{DFL}$), allowing precise payload extraction."
    )
    
    add_section_heading(doc, "6.3", "Unified Feature Extraction Subsystem")
    add_body_p(
        doc,
        "The `FeatureExtractor` operates as the telemetry normalizer between low-level parsers and high-level analytical engines. The extractor "
        "receives a parsed container sequence and computes: (1) Aggregate stream totals (byte counts, container tallies, payload ratios); (2) "
        "Component distributions (PID histograms, protocol frequencies); (3) Dynamic Shannon component entropy; and (4) The 8-dimensional sliding "
        "feature vectors across non-overlapping spatial windows ($W = 100$ containers). By encapsulating feature extraction into an independent "
        "layer, downstream analytical modules remain completely decoupled from container binary formats."
    )
    
    add_section_heading(doc, "6.4", "Feature F1: Stream Health & Priority-1 Analysis")
    add_body_p(
        doc,
        "The `HealthAnalyzer` computes the composite stream health index $S_{\\text{health}} \\in [0.0, 100.0]$ via the deterministic penalty formula "
        "(Equation 4.2). The module tallies synchronization byte errors, continuity counter gaps, and transport error indicator flags against the "
        "total packet count. Streams scoring $\\ge 90.0$ are classified as EXCELLENT; $[75.0, 90.0)$ as GOOD; $[50.0, 75.0)$ as DEGRADED; and $< 50.0$ "
        "as CRITICAL. The health analyzer also enforces capture-boundary neutrality, ensuring that natural stream truncation at the end of a file "
        "is not penalized as a transmission fault."
    )
    
    add_section_heading(doc, "6.5", "Feature F2: Unsupervised Isolation Forest Anomaly Detection")
    add_body_p(
        doc,
        "The `AnomalyDetector` implements an unsupervised outlier detection engine based on Scikit-Learn's `IsolationForest`. The engine ingests "
        "the $N \\times 8$ feature matrix constructed across sliding windows. The model is initialized with 100 estimators, a maximum sample size "
        "of 256 instances per tree, and a contamination parameter of $c = 0.05$. Because satellite receiver bitstreams exhibit high temporal "
        "stationarity under normal operations, the Isolation Forest constructs isolation trees that quickly isolate windows exhibiting structural "
        "distortions, outputting continuous anomaly scores $s(x) \\in [0.0, 1.0]$ with an operational anomaly threshold set at $s(x) > 0.60$."
    )
    
    add_section_heading(doc, "6.6", "Feature F3: Structural Pattern Detection & Multiplex Dynamics")
    add_body_p(
        doc,
        "The `PatternDetector` tracks multiplex component evolution and container efficiency. For MPEG-TS, it identifies the top five active PIDs, "
        "calculates the percentage of bandwidth allocated to null stuffing packets (PID 0x1FFF), and detects component starvation. For GSE, it "
        "evaluates encapsulation efficiency by measuring header overhead against net IP payload. For BBFrames, it computes the modal Data Field "
        "Length (DFL) and reports the percentage of frames operating under Adaptive Coding and Modulation (ACM)."
    )
    
    add_section_heading(doc, "6.7", "Feature F4: Spatial-Offset Timeline & Burst Localization")
    add_body_p(
        doc,
        "The `TimelineGenerator` compiles spatial telemetry series that map every analyzed window and detected anomaly to exact physical hexadecimal "
        "byte offsets (0x00000000 through 0x7FFFFFFF) from the beginning of the file. By eliminating artificial OS timestamps, the timeline enables "
        "satellite engineers to correlate anomalies directly with hex-editor offsets and physical storage sectors. The generator localizes contiguous "
        "error bursts, computing burst start offsets, burst lengths, and peak anomaly scores."
    )
    
    add_section_heading(doc, "6.8", "Feature F5: Explainable Anomaly Root-Cause Diagnostic Engine")
    add_body_p(
        doc,
        "The `AnomalyExplanationEngine` executes the bounded signed Z-score attribution algorithm (Equation 4.4). For every window flagged by "
        "Feature F2 ($s(x) > 0.60$), the engine evaluates $Z_k = (x_{w,k} - \\mu_k) / (\\sigma_k + 10^{-9})$, clamped to $[-20.0\\sigma, +20.0\\sigma]$. "
        "The engine ranks dimensions by absolute deviation $|Z_k|$ and selects all features with $|Z_k| \\ge 2.5\\sigma$ as primary contributors. "
        "It then compiles plain-language diagnostic explanations (e.g., 'Anomalous window driven by a +14.2 sigma surge in continuity counter errors "
        "and a -8.6 sigma collapse in Shannon multiplex entropy')."
    )
    
    add_section_heading(doc, "6.9", "Feature F6: Dual-Stream Comparison Engine with Semantic Barrier")
    add_body_p(
        doc,
        "The `StreamComparisonEngine` enables side-by-side comparative analysis between two streams (Reference Stream A vs. Target Stream B). "
        "When comparing streams of identical formats, the engine evaluates both common metrics and format-specific parameters across normalized "
        "progress deciles. However, when comparing streams of differing formats (e.g., comparing an MPEG-TS multiplex against a DVB-S2 Baseband Frame), "
        "the engine strictly enforces an automated Semantic Barrier."
    )
    add_body_p(
        doc,
        "The Semantic Barrier audits common invariant metrics (total payload bytes, container error rate, and encapsulation efficiency) while actively "
        "suppressing and shielding format-incompatible fields (such as PIDs, CC errors, and CRC-8 validity). This prevents invalid cross-format telemetry "
        "bleed and guarantees dimensional validity. Table 6.2 outlines the semantic comparability audit rules enforced in PRJ_111."
    )
    
    table_6_2_headers = ["Telemetry Metric", "Cross-Format Comparability", "Audit Action Under Cross-Format Mode", "Scientific Rationale"]
    table_6_2_data = [
        ["Total Processed Bytes", "Comparable", "Compute absolute and percentage delta", "Physical byte volume is universally valid"],
        ["Container Error Rate", "Comparable", "Compute normalized error percentage delta", "Error proportion is dimensionally invariant"],
        ["Encapsulation Efficiency", "Comparable", "Compare payload-to-container overhead ratio", "Both formats define clear payload boundaries"],
        ["Shannon Entropy", "Conditionally Comparable", "Compare normalized entropy ($H / H_{\\max}$)", "Component definitions differ (PID vs Protocol)"],
        ["Packet Identifier (PID)", "Incompatible", "SHIELDED (Suppress comparison)", "PIDs exist exclusively in MPEG-TS framing"],
        ["Continuity Counter (CC)", "Incompatible", "SHIELDED (Suppress comparison)", "4-bit sequence counters are unique to MPEG-TS"],
        ["Transport Error (TEI)", "Incompatible", "SHIELDED (Suppress comparison)", "TEI header bit is defined only in MPEG-TS"],
        ["GSE Fragmentation Flags", "Incompatible", "SHIELDED (Suppress comparison)", "Start/End flags exist exclusively in GSE PDUs"],
        ["BBHeader CRC-8 Validity", "Incompatible", "SHIELDED (Suppress comparison)", "Physical CRC-8 exists exclusively in BBFrames"],
        ["Mode Adaptation (MATYPE)", "Incompatible", "SHIELDED (Suppress comparison)", "MATYPE descriptors exist only in BBFrames"]
    ]
    add_custom_table(doc, "Table 6.2: Semantic Cross-Format Comparability Matrix for Dual-Stream Analysis", table_6_2_headers, table_6_2_data, col_widths=[1.5, 1.4, 1.9, 1.7])
    
    add_section_heading(doc, "6.10", "Feature F7: Multi-Format Automated Diagnostic Report Synthesis")
    add_body_p(
        doc,
        "The `AutomaticReportGenerator` compiles publication-grade diagnostic inspection reports structured into an epistemological tripartite "
        "evidence register: (1) Observed Bitstream Telemetry (raw facts, container counts, error tallies); (2) Empirical Diagnostic Analysis "
        "(ETSI health scores, Isolation Forest outlier rankings, Z-score attributions); and (3) Actionable Operator Recommendations (prescriptive "
        "engineering guidance for ground station technicians). The engine renders reports across four distinct formats:"
    )
    add_bullet_p(
        doc,
        "JSON (`diagnostic_report.json`)",
        "Machine-readable schema suitable for automated ingestion by ground station telemetry aggregators and central logging daemons."
    )
    add_bullet_p(
        doc,
        "Markdown (`diagnostic_report.md`)",
        "Human-readable structured technical summary with Markdown tables, suitable for repository documentation and technical wikis."
    )
    add_bullet_p(
        doc,
        "Plain Text (`diagnostic_report.txt`)",
        "Lightweight monospace summary designed for automated transmission across low-bandwidth serial console links or SMS/pager alerts."
    )
    add_bullet_p(
        doc,
        "Standalone HTML (`diagnostic_report.html`)",
        "Self-contained, interactive HTML document containing embedded dark-themed styling, tabular matrices, and visual alert badges with zero "
        "external stylesheet or CDN script dependencies."
    )
    
    add_section_heading(doc, "6.11", "Frontend Engineering Workstation Architecture")
    add_body_p(
        doc,
        "The presentation layer of PRJ_111 is implemented as an offline Single-Page Application (SPA) workstation served by an embedded Python HTTP "
        "server (`AnalysisServer`). Built exclusively using HTML5, Vanilla CSS, and modern ES6 JavaScript, the frontend avoids heavy JavaScript frameworks "
        "(such as React or Angular) to eliminate complex build toolchains and external node_modules dependencies. The workstation features an operator-focused "
        "dark aesthetic (#0B0F19 background) optimized for 24/7 ground station control room environments."
    )
    add_body_p(
        doc,
        "The workstation provides five synchronized views: (1) Standby Ingestion Dashboard with drag-and-drop file staging; (2) Active Telemetry "
        "Dashboard featuring SVG gauge meters and component distribution charts; (3) Anomaly & Diagnostic Attribution Inspector rendering Isolation "
        "Forest outlier distributions; (4) Spatial-Offset Timeline View scrubbing across hexadecimal byte coordinates; and (5) Dual-Stream Comparison "
        "View presenting side-by-side metric deltas governed by the Semantic Barrier."
    )
    
    add_section_heading(doc, "6.12", "Streaming Engine & High-Throughput Chunked Implementation")
    add_body_p(
        doc,
        "The `StreamingChunkReader` implements memory-bounded stream ingestion using 64 KB buffers. As chunks are read sequentially from disk or network "
        "sockets, internal accumulators stitch fractional container boundaries across chunk edges. The parser processes packets in-place and yields "
        "extracted features downstream to the sliding-window aggregator, maintaining a constant memory footprint of under 25 MB regardless of whether "
        "the input file is 10 MB or 10 GB in size."
    )
    
    add_section_heading(doc, "6.13", "Controlled Fault-Injection Framework Implementation")
    add_body_p(
        doc,
        "The `FaultInjector` utility provides an empirical workbench for sensitivity testing. Given a verified clean satellite stream, the injector "
        "allows operators to introduce controlled perturbations (sync slip, CC gap, TEI assertion, or PID starvation) at exact byte offsets with "
        "calibrated fault rates ($0.1\\% \\le r \\le 5.0\\%$). The injected stream is re-analyzed by the PRJ_111 pipeline to verify that Feature F2 "
        "accurately isolates the perturbed windows and Feature F5 correctly attributes the root cause."
    )
