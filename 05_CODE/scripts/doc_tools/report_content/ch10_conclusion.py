from report_content.builder_utils import (
    add_chapter_title, add_section_heading, add_subsection_heading,
    add_body_p, add_bullet_p, add_callout
)

def build_ch10(doc):
    add_chapter_title(doc, "CHAPTER 10", "CONCLUSION AND FUTURE WORK")
    
    add_section_heading(doc, "10.1", "Summary of Scientific and Engineering Contributions")
    add_body_p(
        doc,
        "This capstone project successfully designed, implemented, verified, and delivered PRJ_111: an advanced, self-contained software application "
        "engineered for comprehensive analysis, deterministic health scoring, unsupervised anomaly detection, and automated diagnostic synthesis "
        "across multi-format DVB-S2 receiver output streams. Grounded in a rigorous container abstraction model, PRJ_111 addresses the acute operational "
        "challenges of container fragmentation, rigid static thresholding, and diagnostic opacity that plague contemporary satellite ground stations."
    )
    add_body_p(
        doc,
        "The primary scientific and technical contributions of this project include:"
    )
    add_bullet_p(
        doc,
        "Unified Multi-Format Container Parsing",
        "Engineered zero-copy, highly robust binary parsers supporting fixed 188-byte MPEG-TS packets, variable-length Generic Stream Encapsulation (GSE) "
        "PDUs, and native DVB-S2 Baseband Frames (BBFrames) with table-driven CRC-8 verification."
    )
    add_bullet_p(
        doc,
        "ETSI TR 101 290 Priority-1 Stream Health Scoring (F1)",
        "Formulated a deterministic, mathematically bounded health score metric [0.0, 100.0] that accurately quantifies bitstream integrity based on "
        "sync acquisition stability, continuity counter tracking, and transport error indicator monitoring."
    )
    add_bullet_p(
        doc,
        "Unsupervised Machine Learning Anomaly Detection (F2)",
        "Integrated an Isolation Forest ensemble operating over an 8-dimensional sliding feature space, detecting structural and statistical multiplex "
        "anomalies without requiring pre-labeled training datasets."
    )
    add_bullet_p(
        doc,
        "Physical Spatial-Offset Timeline Indexing (F4)",
        "Eliminated fabricated clock timestamps by indexing all stream events and detected anomalies against exact physical hexadecimal byte offsets "
        "(0x...) from the start of the bitstream, enabling direct correlation with physical storage sectors."
    )
    add_bullet_p(
        doc,
        "Explainable Diagnostic Root-Cause Attribution (F5)",
        "Developed a clamped signed Z-score attribution engine ($|Z| \\le 20.0\\sigma$) that translates mathematical feature deviations into actionable, "
        "human-interpretable diagnostic narratives."
    )
    add_bullet_p(
        doc,
        "Dual-Stream Comparison Engine with Semantic Barrier (F6)",
        "Architected an automated semantic shield that audits invariant metrics while shielding format-incompatible fields, enabling safe, rigorous "
        "cross-format stream comparison without telemetry bleed."
    )
    add_bullet_p(
        doc,
        "Automated Multi-Format Diagnostic Reporting (F7)",
        "Constructed an automated reporting pipeline generating tripartite technical assessments across JSON, Markdown, Plain Text, and standalone HTML."
    )
    add_bullet_p(
        doc,
        "Memory-Bounded Chunked Streaming Scalability",
        "Implemented a 64 KB streaming buffer architecture maintaining a constant RAM footprint (< 25 MB) across multi-gigabyte bitstreams while asserting "
        "bit-for-bit whole-file analytical equivalence."
    )
    add_bullet_p(
        doc,
        "Rigorous Automated Test Verification",
        "Constructed a 304-test automated regression suite across 18 modules, achieving a 100% pass rate in 76.06 seconds."
    )
    
    add_section_heading(doc, "10.2", "Technical Limitations and Operational Boundaries")
    add_body_p(
        doc,
        "To uphold academic rigor and scientific integrity, the operational boundaries and technical limitations of PRJ_111 must be clearly stated:"
    )
    add_bullet_p(
        doc,
        "Post-Demodulator Boundary Constraint",
        "PRJ_111 operates strictly on digital bitstreams emitted downstream of the physical demodulator and FEC decoder. The software does NOT interface "
        "with analog RF tuners, carrier tracking loops, or raw I/Q samples."
    )
    add_bullet_p(
        doc,
        "RF Physical Layer Telemetry Exclusion",
        "The software does NOT estimate physical RF parameters (such as Carrier-to-Noise Ratio CNR, Modulation Error Ratio MER, or physical channel "
        "Bit Error Rate BER) from digital stream data. Such parameters require external RF telemetry sensors and cannot be inferred purely from container bits."
    )
    add_bullet_p(
        doc,
        "Informal ETSI Inspiration vs. Certified Conformance",
        "The stream health metrics in PRJ_111 are inspired by the measurement principles of ETSI TR 101 290 Priority-1 guidelines. PRJ_111 does NOT claim "
        "formal laboratory accreditation or certified compliance as an official ETSI conformance test tool."
    )
    add_bullet_p(
        doc,
        "Synthetic Fault Injection Ground Truth",
        "Because production satellite downlinks rarely exhibit uncorrected errors, machine learning sensitivity was evaluated primarily using synthetic "
        "fault injection benchmarks rather than unverified commercial operational failures."
    )
    
    add_section_heading(doc, "10.3", "Future Research and Engineering Enhancements")
    add_body_p(
        doc,
        "Several promising avenues for future research and technical extension have been identified:"
    )
    add_bullet_p(
        doc,
        "1. Live Software-Defined Radio (SDR) Ingestion",
        "Extend the ingestion layer to interface directly with Software-Defined Radio front-ends (e.g., Ettus USRP, HackRF) via GNU Radio or native C++ "
        "bindings, allowing real-time baseband capture and analysis directly from L-band downconverters."
    )
    add_bullet_p(
        doc,
        "2. Hardware Acceleration via SIMD and Cython",
        "Accelerate binary parsing state machines and sliding-window matrix operations using Cython, C extensions, or Intel AVX-512 SIMD vectorization, "
        "scaling sustained processing throughput from 15 MB/s to over 100 MB/s for 10-Gigabit satellite backhaul links."
    )
    add_bullet_p(
        doc,
        "3. Integration with 5G Non-Terrestrial Networks (NTN)",
        "Incorporate protocol dissectors for 3GPP 5G NTN framing (3GPP Release 17/18) where 5G NR radio frames are transported over satellite GSE links, "
        "providing unified diagnostic monitoring for satellite-cellular direct-to-device connectivity."
    )
    add_bullet_p(
        doc,
        "4. Temporal Deep Learning Anomaly Ensembles",
        "Augment the tabular Isolation Forest detector with recurrent temporal architectures (such as lightweight LSTM Autoencoders or Temporal "
        "Convolutional Networks) to capture long-range temporal dependencies in high-velocity telemetry streams."
    )
