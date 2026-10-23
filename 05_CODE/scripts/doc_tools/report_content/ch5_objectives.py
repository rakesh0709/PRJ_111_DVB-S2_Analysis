from report_content.builder_utils import (
    add_chapter_title, add_section_heading, add_subsection_heading,
    add_body_p, add_bullet_p, add_callout, add_custom_table
)

def build_ch5(doc):
    add_chapter_title(doc, "CHAPTER 5", "OBJECTIVES AND SPECIFICATIONS")
    
    add_section_heading(doc, "5.1", "Primary Functional Objectives (F1 through F7)")
    add_body_p(
        doc,
        "The overarching technical aim of PRJ_111 is to deliver an integrated, seven-feature analytical pipeline (F1 through F7) that transforms "
        "raw post-demodulator digital bitstreams into actionable engineering intelligence. Each feature fulfills a distinct operational requirement "
        "in satellite ground station telemetry monitoring:"
    )
    add_bullet_p(
        doc,
        "Feature F1: Stream Health & Priority-1 Integrity Analysis",
        "Continuously evaluate stream health on a normalized scale [0.0, 100.0] derived from ETSI TR 101 290 Priority-1 measurement principles. "
        "The engine must track synchronization byte stability, detect continuity counter discontinuities per PID, record transport error indicators, "
        "and classify stream integrity into EXCELLENT, GOOD, DEGRADED, or CRITICAL tiers."
    )
    add_bullet_p(
        doc,
        "Feature F2: Unsupervised Machine Learning Anomaly Detection",
        "Deploy an unsupervised Isolation Forest model operating across sliding spatial feature windows ($W = 100$ containers) to detect statistical "
        "and structural multiplex anomalies without pre-labeled training corpora. The detector must output normalized anomaly scores ($s(x) \\in [0, 1]$) "
        "calibrated against a 5% contamination baseline."
    )
    add_bullet_p(
        doc,
        "Feature F3: Structural Pattern Detection & Multiplex Dynamics",
        "Analyze the structural distribution of stream containers across time. For MPEG-TS, compute PID shares, identify dominant video/audio components, "
        "and quantify null packet stuffing; for GSE, extract protocol type distributions (IPv4, IPv6) and fragmentation ratios; for BBFrames, extract "
        "Mode Adaptation (MATYPE) flags, ACM configurations, and modal Data Field Lengths (DFL)."
    )
    add_bullet_p(
        doc,
        "Feature F4: Spatial-Offset Timeline & Burst Localization",
        "Index stream events, frame boundaries, and detected anomalies against exact physical hexadecimal byte offsets from the start of the bitstream "
        "(0x00000000). The timeline must localize error bursts and render interactive spatial distributions without fabricating artificial clock timestamps."
    )
    add_bullet_p(
        doc,
        "Feature F5: Explainable Diagnostic Root-Cause Attribution",
        "Implement a bounded signed Z-score diagnostic explanation engine ($|Z| \\le 20.0\\sigma$) that identifies the top feature dimensions contributing "
        "to flagged anomalies. The engine must generate plain-language engineering explanations linking mathematical outliers to physical failure modes."
    )
    add_bullet_p(
        doc,
        "Feature F6: Dual-Stream Comparison Engine with Semantic Barrier",
        "Provide side-by-side comparative analysis between two streams (e.g., primary vs backup downlinks). Enforce an automated Semantic Barrier "
        "that audits format-invariant metrics while shielding format-incompatible fields during cross-format comparisons, preventing spurious diffs."
    )
    add_bullet_p(
        doc,
        "Feature F7: Automated Multi-Format Diagnostic Report Synthesis",
        "Synthesize comprehensive, publication-quality technical inspection reports structured according to an epistemological tripartite evidence "
        "register (Observed Telemetry, Empirical Analysis, Actionable Operator Recommendations). Export reports across JSON, Markdown, Plain Text, "
        "and standalone interactive HTML formats."
    )
    
    table_5_1_headers = ["Feature ID", "Feature Name", "Core Implementation Module", "Verification State", "Primary Operational Metric"]
    table_5_1_data = [
        ["F1", "Stream Health Analysis", "dvbs2_analyzer.analysis.health", "Verified (12 Tests)", "Health Score [0, 100], P1 Fault Tally"],
        ["F2", "Isolation Forest Anomaly Detection", "dvbs2_analyzer.analysis.anomaly", "Verified (16 Tests)", "Anomaly Score s(x) in [0, 1], c=0.05"],
        ["F3", "Structural Pattern Detection", "dvbs2_analyzer.analysis.patterns", "Verified (20 Tests)", "Shannon Entropy (bits), PID Shares"],
        ["F4", "Spatial-Offset Timeline View", "dvbs2_analyzer.analysis.timeline", "Verified (18 Tests)", "Physical Byte Offsets (0x...), Burst Width"],
        ["F5", "Explainable Diagnostic Attribution", "dvbs2_analyzer.analysis.explanation", "Verified (21 Tests)", "Clamped Z-score (|Z| <= 20 sigma), Top Drivers"],
        ["F6", "Stream Comparison & Semantic Shield", "dvbs2_analyzer.analysis.comparison", "Verified (10 Tests)", "Common Invariant Delta, Semantic Protection"],
        ["F7", "Automated Multi-Format Reporting", "dvbs2_analyzer.analysis.report", "Verified (25 Tests)", "JSON, Markdown, TXT, Standalone HTML"]
    ]
    add_custom_table(doc, "Table 5.1: Mapping of Functional Features F1 through F7 to Verified Architectural State", table_5_1_headers, table_5_1_data, col_widths=[0.9, 1.9, 1.8, 1.1, 1.8])
    
    add_section_heading(doc, "5.2", "Non-Functional and Operational Requirements")
    add_body_p(
        doc,
        "To satisfy the demanding operational environments of commercial teleports and military satellite earth stations, PRJ_111 must fulfill strict "
        "non-functional software engineering requirements:"
    )
    add_bullet_p(
        doc,
        "Memory-Bounded Execution",
        "The system must execute within a strictly bounded memory footprint, utilizing streaming generator pipelines and 64 KB chunk buffers to process "
        "multi-gigabyte bitstreams without exhausting physical RAM."
    )
    add_bullet_p(
        doc,
        "Zero Cloud Dependencies & Air-Gapped Security",
        "The software application must run completely offline without external internet connectivity, external database servers, or cloud API calls. "
        "All analytical models (Isolation Forest), CSS stylesheets, and JavaScript charting engines must reside locally within the application bundle."
    )
    add_bullet_p(
        doc,
        "Low-Latency Execution",
        "Container parsing and feature extraction must achieve processing throughput exceeding 10 MB/s on standard quad-core workstation processors, "
        "ensuring that 100 MB satellite capture files are fully analyzed and indexed in under 10 seconds."
    )
    add_bullet_p(
        doc,
        "Cross-Platform Portability",
        "The core backend must be authored in standardized Python 3 (compatible with Linux, macOS, and Microsoft Windows), accompanied by a zero-dependency "
        "HTML5 / Vanilla CSS / ES6 JavaScript frontend accessible via any modern Chromium, Firefox, or Safari browser."
    )
    
    add_section_heading(doc, "5.3", "Mathematical and Diagnostic Verification Targets")
    add_body_p(
        doc,
        "The software architecture establishes strict mathematical invariants that must be proven and verified across all operational modes:"
    )
    add_bullet_p(
        doc,
        "Entropy Determinism",
        "Shannon multiplex entropy calculations must be strictly reproducible, deterministic, and bounded within $[0, \\log_2 M]$ bits."
    )
    add_bullet_p(
        doc,
        "Z-Score Bounding Guard",
        "All diagnostic feature attribution scores must be clamped to $[-20.0\\sigma, +20.0\\sigma]$ to protect frontend charting pipelines from "
        "floating-point overflow and visual distortion."
    )
    add_bullet_p(
        doc,
        "CRC-8 Table Lookup Integrity",
        "Every DVB-S2 Baseband Header CRC-8 calculation must match bitwise with the hardware shift-register definition of ETSI EN 302 307-1, achieving "
        "a 100% verification rate on valid frames."
    )
    
    add_section_heading(doc, "5.4", "Automated Test Suite Coverage Targets")
    add_body_p(
        doc,
        "To guarantee long-term regression stability and academic reproducibility, PRJ_111 establishes an automated regression test suite target "
        "exceeding 300 tests across 18 specialized test modules. The test suite must cover unit parsing mechanics, boundary edge conditions, "
        "mathematical models, REST API controllers, fault-injection utilities, chunked streaming equivalence, and frontend security validation, "
        "executing with a 100% pass rate under native Python `unittest`."
    )
