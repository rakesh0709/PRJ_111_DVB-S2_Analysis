from report_content.builder_utils import (
    add_chapter_title, add_section_heading, add_subsection_heading,
    add_body_p, add_bullet_p, add_callout, add_custom_table, add_custom_figure
)

def build_ch4(doc):
    add_chapter_title(doc, "CHAPTER 4", "PROPOSED METHODOLOGY")
    
    add_section_heading(doc, "4.1", "Foundational Architecture Principle: Container Abstraction")
    add_body_p(
        doc,
        "The proposed methodology of PRJ_111 is grounded in a rigorous container abstraction model that directly reflects the physical "
        "reality of satellite digital receiver hardware. In satellite signal reception, the demodulator operates as a physical boundary: "
        "prior to demodulation, the signal exists as modulated electromagnetic waveform energy (IF/RF); following demodulation, the signal exists "
        "as a discrete digital bitstream. Depending on the receiver's configured operational mode, this digital stream is presented as either:"
    )
    add_bullet_p(
        doc,
        "Native Physical-Layer Baseband Frames (BBFrame)",
        "Directly emitted by the demodulator/FEC decoder, carrying raw DVB-S2 mode adaptation parameters and user data fields (DFL)."
    )
    add_bullet_p(
        doc,
        "Generic Stream Encapsulation (GSE)",
        "Emitted by an internal de-encapsulation stage that extracts IP packets from baseband frames and presents them as a GSE PDU stream."
    )
    add_bullet_p(
        doc,
        "MPEG-2 Transport Stream (MPEG-TS)",
        "Emitted when the satellite transponder carries broadcast video multiplexes organized into fixed 188-byte transport packets."
    )
    add_body_p(
        doc,
        "A foundational architectural invariant enforced in PRJ_111 is that BBFrame, GSE, and MPEG-TS represent alternative, parallel input "
        "formats. The analyzer auto-detects the stream container at ingestion and instantiates a format-dedicated parsing pipeline. Container-specific "
        "mechanics are isolated within dedicated parsers, while an abstracted feature extraction layer maps all streams into a unified analytical "
        "representation. Figure 4.1 depicts the end-to-end multi-format system architecture of PRJ_111."
    )
    
    # Figure 4.1: Architecture Diagram
    add_custom_figure(
        doc,
        "07_DOCUMENTATION/Architecture_Diagram.png",
        "Figure 4.1: End-to-End Multi-Format System Architecture of PRJ_111"
    )
    
    add_section_heading(doc, "4.2", "Unified Multi-Format Feature Extraction Pipeline")
    add_body_p(
        doc,
        "To enable format-agnostic anomaly detection without discarding container-specific domain intelligence, PRJ_111 introduces a "
        "bifurcated telemetry schema. As streams are ingested, the `FeatureExtractor` partitions telemetry into two distinct classes:"
    )
    add_bullet_p(
        doc,
        "Common Metrics (`CommonMetrics`)",
        "Universally defined across all digital stream formats: Total bytes processed, valid container count, corrupted container count, "
        "container error rate, total payload bytes, container encapsulation efficiency (%), physical stream duration, and Shannon multiplex entropy (bits)."
    )
    add_bullet_p(
        doc,
        "Format-Specific Metrics (`FormatSpecificMetrics`)",
        "Dedicated container telemetry preserved strictly within native boundaries: PID distribution, continuity counter errors, and TEI flags for MPEG-TS; "
        "protocol type distribution, PDU fragmentation ratio, and label presence for GSE; MATYPE mode flags, ACM status, UPL, DFL distributions, and "
        "CRC-8 verification status for BBFrames."
    )
    add_body_p(
        doc,
        "For downstream machine learning anomaly detection (Feature F2), the extractor constructs an 8-dimensional sliding feature vector $X_w$ "
        "over non-overlapping spatial windows of fixed container length ($W = 100$ containers). Table 4.1 enumerates the eight dimensions of the "
        "rolling feature space."
    )
    
    table_4_1_headers = ["Dimension", "Feature Name", "Mathematical Representation", "Domain Significance"]
    table_4_1_data = [
        ["$x_1$", "Container Error Ratio", "$N_{\\text{err}} / N_{\\text{total}}$", "Fraction of corrupted containers in window"],
        ["$x_2$", "Mean Payload Length", "$\\frac{1}{W} \\sum L_{\\text{payload}}$", "Average user payload per container (bytes)"],
        ["$x_3$", "Payload Variance", "$\\sigma^2(L_{\\text{payload}})$", "Burstiness and packet length variability"],
        ["$x_4$", "Shannon Entropy", "$H(X) = -\\sum P(x_i) \\log_2 P(x_i)$", "Diversity and balance of multiplex components"],
        ["$x_5$", "Dominant Component Share", "$\\max_i P(x_i)$", "Concentration of stream in single PID or Protocol"],
        ["$x_6$", "Fragmentation / Sub-framing", "$N_{\\text{frag}} / N_{\\text{total}}$", "GSE fragmentation ratio or TS adaptation share"],
        ["$x_7$", "Integrity Fault Density", "$N_{\\text{faults}} / W$", "Local density of ETSI Priority-1 violations"],
        ["$x_8$", "Header Invariant Drift", "$|\\bar{L}_{\\text{hdr}} - L_{\\text{expected}}|$", "Structural divergence from standard header sizes"]
    ]
    add_custom_table(doc, "Table 4.1: Unified Feature Vector Dimensions for Rolling Anomaly Detection", table_4_1_headers, table_4_1_data, col_widths=[0.9, 1.8, 1.8, 2.0])
    
    add_section_heading(doc, "4.3", "Mathematical Formulations and Analytical Models")
    
    add_subsection_heading(doc, "4.3.1", "Shannon Multiplex Component Entropy Formulation")
    add_body_p(
        doc,
        "To rigorously quantify multiplex diversity and detect component starvation (e.g., sudden drop in active video PIDs or illegal component "
        "monopolization), PRJ_111 evaluates the Shannon component entropy $H(X)$ over each spatial window. Let $M$ denote the number of unique "
        "active multiplex components (PIDs in MPEG-TS, Protocol Types in GSE, or MODCOD/DFL classes in BBFrame), and let $P(x_i)$ represent the empirical "
        "probability (fractional share) of the $i$-th component such that $\\sum_{i=1}^M P(x_i) = 1.0$. The Shannon entropy in bits is defined as:"
    )
    add_callout(
        doc,
        "Equation 4.1: Shannon Multiplex Component Entropy",
        "H(X) = - \\sum_{i=1}^{M} P(x_i) \\cdot \\log_2 P(x_i) \\quad [\\text{bits}]\n\n"
        "where by mathematical convention, if P(x_i) = 0, then P(x_i) \\cdot \\log_2 P(x_i) = 0. "
        "For a single-component stream (e.g., 100% null packets), H(X) = 0.0 bits. For a perfectly uniform multiplex of M components, "
        "H(X) achieves its theoretical maximum of \\log_2 M bits."
    )
    
    add_subsection_heading(doc, "4.3.2", "Deterministic Health Scoring Formulation (Priority-1 Principles)")
    add_body_p(
        doc,
        "Stream health assessment (Feature F1) is governed by a deterministic, bounded penalty scoring model anchored in ETSI TR 101 290 Priority-1 "
        "measurement principles. Rather than relying on arbitrary heuristic rules, the health score $S_{\\text{health}}$ is evaluated on a strict "
        "scale of $[0.0, 100.0]$ across the analyzed stream:"
    )
    add_callout(
        doc,
        "Equation 4.2: Deterministic Stream Health Metric",
        "S_{\\text{health}} = \\max\\left( 0.0, 100.0 - \\left[ 50.0 \\cdot \\frac{N_{\\text{sync\\_err}}}{N_{\\text{pkts}}} + 30.0 \\cdot \\frac{N_{\\text{cc\\_err}}}{N_{\\text{pkts}}} + 20.0 \\cdot \\frac{N_{\\text{tei}}}{N_{\\text{pkts}}} + \\sum_{j} w_j \\cdot f_j \\right] \\right)\n\n"
        "where N_{\\text{sync\\_err}} is the count of synchronization byte errors, N_{\\text{cc\\_err}} is the count of continuity counter discontinuities, "
        "N_{\\text{tei}} is the count of transport error indicator flags, and w_j represents penalty weights for additional format-specific integrity faults."
    )
    add_body_p(
        doc,
        "Streams with $S_{\\text{health}} \\ge 90.0$ are classified as EXCELLENT; streams with $75.0 \\le S_{\\text{health}} < 90.0$ are GOOD; "
        "streams with $50.0 \\le S_{\\text{health}} < 75.0$ are DEGRADED; and streams with $S_{\\text{health}} < 50.0$ are CRITICAL. Table 4.2 lists "
        "the verified fault identifiers, trigger conditions, and severity penalty weights."
    )
    
    table_4_2_headers = ["Fault ID", "ETSI Principle", "Trigger Condition", "Severity Weight ($w_j$)", "Integrity Impact"]
    table_4_2_data = [
        ["F_SYNC_ERR", "TR 101 290 1.1", "Header sync byte != 0x47 in MPEG-TS", "50.0", "Loss of packet framing; catastrophic decoder failure"],
        ["F_CC_GAP", "TR 101 290 1.4", "Discontinuous non-repeated continuity counter", "30.0", "Packet drop or disorder; elementary stream corruption"],
        ["F_TEI_SET", "TR 101 290 2.1", "Transport Error Indicator bit asserted (1)", "20.0", "Demodulator flagged uncorrected bit errors"],
        ["F_GSE_LEN", "TS 102 606 4.2", "PDU total length exceeds buffer boundary", "35.0", "PDU framing truncation; IP buffer corruption"],
        ["F_GSE_FRAG", "TS 102 606 5.1", "Illegal S/E fragmentation state transition", "25.0", "SNDU reassembly failure; dropped network frame"],
        ["F_CRC8_FAIL", "EN 302 307 5.1", "Computed CRC-8 != BBHeader byte 9", "40.0", "Corrupted baseband header; frame payload discarded"]
    ]
    add_custom_table(doc, "Table 4.2: Priority-1 Integrity Fault Identifiers, Trigger Conditions, and Penalty Weights", table_4_2_headers, table_4_2_data, col_widths=[1.1, 1.2, 1.9, 1.0, 1.3])
    
    add_subsection_heading(doc, "4.3.3", "Unsupervised Isolation Forest Anomaly Detection Model")
    add_body_p(
        doc,
        "To identify statistical and structural outliers without requiring pre-labeled training data, Feature F2 integrates an Isolation Forest "
        "ensemble of $T = 100$ isolation trees (iTrees). Given a dataset of $n$ sliding feature vectors $X = \\{X_1, X_2, \\dots, X_n\\} \\subset \\mathbb{R}^d$, "
        "an iTree is constructed by recursively partitioning a subsample $X' \\subset X$ ($|X'| = \\min(n, 256)$) by randomly selecting an attribute $q$ "
        "and a split value $p$ uniformly distributed between the minimum and maximum values of $q$ in the current node. Partitioning terminates when "
        "either the tree reaches a maximum depth limit $h_{\\max} = \\lceil \\log_2 |X'| \\rceil$, the node contains a single instance, or all instances "
        "have identical values."
    )
    add_body_p(
        doc,
        "The path length $h(x)$ of an instance $x$ is the number of edges traversed from the root node to the terminating leaf node. The anomaly score "
        "$s(x, n)$ for an instance $x$ across an ensemble of $T$ iTrees is defined as:"
    )
    add_callout(
        doc,
        "Equation 4.3: Isolation Forest Anomaly Scoring Formulation",
        "s(x, n) = 2^{ - \\frac{E(h(x))}{c(n)} }\n\n"
        "where E(h(x)) is the expectation of path lengths across the ensemble of T trees, and c(n) is the average path length of "
        "unsuccessful searches in a Binary Search Tree (BST) over n instances:\n\n"
        "c(n) = 2 \\cdot \\left[ \\ln(n - 1) + \\gamma \\right] - \\frac{2(n - 1)}{n}\n\n"
        "where \\gamma \\approx 0.5772156649 \\text{ is Euler's constant}.\n\n"
        "• If E(h(x)) \\to 0, then s(x, n) \\to 1.0 \\implies \\text{Strongly anomalous (isolated very near the root)}.\n"
        "• If E(h(x)) \\to c(n), then s(x, n) \\to 0.5 \\implies \\text{Normal structural behavior}.\n"
        "• If E(h(x)) \\to n - 1, then s(x, n) \\to 0.0 \\implies \\text{Highly central cluster instance}."
    )
    add_body_p(
        doc,
        "In PRJ_111, the contamination parameter is calibrated to $c = 0.05$ (5% expected outlier budget). The raw score $s(x, n)$ is mapped "
        "into a standardized anomaly index. Windows with $s(x, n) > 0.60$ trigger active diagnostic inspection."
    )
    
    add_subsection_heading(doc, "4.3.4", "Bounded Signed Z-Score Diagnostic Attribution Model")
    add_body_p(
        doc,
        "To provide actionable, human-interpretable explanations for flagged anomalous windows (Feature F5), PRJ_111 computes signed standardized "
        "deviations (Z-scores) for each feature dimension $k \\in \\{1, 2, \\dots, 8\\}$ within the anomalous window $w$, evaluated relative to the "
        "baseline mean $\\mu_k$ and standard deviation $\\sigma_k$ of the entire stream:"
    )
    add_callout(
        doc,
        "Equation 4.4: Bounded Signed Z-Score Feature Attribution",
        "Z_k = \\frac{x_{w,k} - \\mu_k}{\\sigma_k + \\epsilon}, \\quad \\text{clamped to } Z_k \\in [-20.0, +20.0]\n\n"
        "where \\epsilon = 10^{-9} \\text{ prevents division-by-zero on zero-variance dimensions}.\n\n"
        "Mathematical Bounding Rationale: In near-deterministic bitstreams, background feature variance \\sigma_k can be vanishingly small "
        "(e.g., \\sigma_k = 10^{-7}). A single localized fault can produce an unconstrained numerical Z-score exceeding 100,000\\sigma, causing "
        "floating-point overflow in UI chart renderers. Clamping to [-20.0, +20.0] preserves strict directional attribution while preventing numerical distortion."
    )
    add_body_p(
        doc,
        "A feature dimension is flagged as a primary diagnostic contributor if $|Z_k| \\ge 2.5\\sigma$. The sign of $Z_k$ dictates the operational "
        "attribution: $Z_k \\ge +2.5$ indicates an abnormal positive surge (e.g., sudden burst of continuity counter errors), whereas $Z_k \\le -2.5$ "
        "indicates an abnormal collapse (e.g., collapse of Shannon component entropy)."
    )
    
    add_subsection_heading(doc, "4.3.5", "DVB-S2 Baseband Header CRC-8 Generator Polynomial")
    add_body_p(
        doc,
        "In the DVB-S2 physical layer standard (ETSI EN 302 307-1, Section 5.1.5), the 10-byte Baseband Header is protected by an 8-bit Cyclic "
        "Redundancy Check (CRC-8) calculated over the first 9 bytes (MATYPE, UPL, DFL, SYNC, SYNCD). The standard defines the generator polynomial $G(x)$ as:"
    )
    add_callout(
        doc,
        "Equation 4.5: DVB-S2 Baseband Header CRC-8 Polynomial",
        "G(x) = x^8 + x^7 + x^6 + x^4 + x^2 + 1 \\quad (\\text{Hexadecimal: } 0xD5)\n\n"
        "Initial shift register state: 0x00. The CRC-8 is computed bitwise and inverted or directly matched with byte 9 of the BBHeader. "
        "PRJ_111 implements an optimized 256-entry table-driven lookup algorithm that verifies BBHeader integrity in constant time O(1) per frame."
    )
    
    add_section_heading(doc, "4.4", "Chunked Streaming Processing Engine (64 KB Bounded Buffer)")
    add_body_p(
        doc,
        "A major engineering advancement developed in Phase III (Review-3) of this capstone project is the memory-bounded Chunked Streaming "
        "Processing Engine. Satellite receiver dump files frequently span tens of gigabytes. Loading entire streams into memory (`read_all()`) exhausts "
        "system RAM and causes abrupt workstation termination. PRJ_111 re-architects the ingestion pipeline around a bounded 64 KB streaming buffer "
        "governed by Python generators."
    )
    add_body_p(
        doc,
        "To ensure analytical correctness, the chunked parser implements persistent boundary carry-over state. When a 64 KB chunk ends on an incomplete "
        "188-byte MPEG-TS packet or a partial GSE header, the residual bytes are carried over into an internal accumulator and prepended to the subsequent "
        "chunk. Formally, let $R(S)$ denote the complete analysis result computed by monolithic whole-file parsing, and let $R_{\\text{chunk}}(S, C)$ "
        "denote the result computed by chunked streaming with chunk size $C = 65,536$ bytes. PRJ_111 asserts and mathematically verifies the "
        "Whole-File Equivalence Invariant across all supported formats:"
    )
    add_callout(
        doc,
        "Architectural Invariant: Whole-File Analytical Equivalence",
        "R(S) \\equiv R_{\\text{chunk}}(S, C) \\quad \\forall S \\in \\{\\text{MPEG-TS}, \\text{GSE}, \\text{BBFrame}\\}, \\quad \\forall C \\ge 188 \\text{ bytes}\n\n"
        "Every extracted metric—total container count, byte offsets, error tallies, Shannon entropy, Isolation Forest anomaly scores, "
        "and diagnostic explanations—is bit-for-bit identical regardless of chunk buffer sizing."
    )
    
    add_section_heading(doc, "4.5", "Controlled Fault-Injection Validation Methodology")
    add_body_p(
        doc,
        "A fundamental scientific challenge in validating unsupervised anomaly detection algorithms on satellite bitstreams is the scarcity of "
        "ground-truth anomalies in clean commercial captures. To rigorously evaluate detection sensitivity without relying on speculative assumptions, "
        "PRJ_111 incorporates a defensive synthetic fault-injection benchmark utility (`dvbs2_analyzer.fault_injection`)."
    )
    add_body_p(
        doc,
        "The fault injection framework accepts a pristine satellite stream and injects controlled, mathematically precise perturbations at specific "
        "physical byte offsets with configurable escalation ratios ($0.1\\% \\le r \\le 5.0\\%$). Four distinct fault classes are supported:"
    )
    add_bullet_p(
        doc,
        "1. Sync Byte Corruption (Sync Slip)",
        "Overwrites periodic 0x47 synchronization markers with pseudo-random bytes, simulating receiver phase slips and framing loss."
    )
    add_bullet_p(
        doc,
        "2. Continuity Counter Discontinuities (CC Gap)",
        "Increments or resets 4-bit CC values out of sequence, simulating packet drops in multiplexer FIFOs."
    )
    add_bullet_p(
        doc,
        "3. Transport Error Indicator Assertion (TEI Burst)",
        "Sets the TEI bit in the transport header, simulating physical demodulator LDPC decoder exhaustion under atmospheric rain fade."
    )
    add_bullet_p(
        doc,
        "4. Component Starvation / Multiplex Hijacking",
        "Replaces active video PIDs with repetitive null packets (PID 0x1FFF), simulating upstream encoder freeze and entropy collapse."
    )
    add_body_p(
        doc,
        "By systematically evaluating the Isolation Forest anomaly score response curve and F5 diagnostic explanations across these controlled "
        "faults, PRJ_111 establishes verifiable empirical proof of detection efficacy."
    )
