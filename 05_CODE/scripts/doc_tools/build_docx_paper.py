"""
Builds PRJ_111_Research_Paper_Final.docx with professional IEEE academic formatting.
Includes:
- Title and Author block (Sk Samad, Y Vengala Rao, C Rakeshwar - Presidency University; NO project guide in author block)
- Abstract (214 words, single paragraph) & Alphabetical Index Terms
- Section I: Introduction
- Section II: Related Work (A, B, C) with citations [1]-[20]
- Section III: System Architecture & Workstation Design + Fig. 1 (Architecture Pipeline) + Fig. 2 (Dashboard)
- Section IV: Multi-Format Stream Processing (A, B, C) + Table I (Format Characteristics)
- Section V: Feature Engineering & Analytical Pipeline (A-G) + Eq. (1)-(5) + Fig. 3 (Timeline) + Fig. 4 (Anomaly) + Eq. (6)-(9) + Fig. 5 (Comparison) + Fig. 6 (Report)
- Section VI: Experimental Setup and Datasets
- Section VII: Results and Discussion (A-E) + Table II (MPEG-TS) + Table III (GSE) + Table IV (BBFrame) + Table V (Isolation Forest) + Table VI (Comparison Audit)
- Section VIII: Software Verification and Testing (240/240 tests)
- Section IX: Limitations and Domain Safety
- Section X: Conclusion and Future Work
- Acknowledgment (Presidency University, Irfan Rajab Bhat)
- References [1]-[20] in strict citation order
"""

import os
import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import parse_xml, OxmlElement
from docx.oxml.ns import nsdecls, qn

def set_cell_background(cell, fill_hex):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = parse_xml(f'<w:tcMar {nsdecls("w")}><w:top w:w="{top}" w:type="dxa"/><w:bottom w:w="{bottom}" w:type="dxa"/><w:left w:w="{left}" w:type="dxa"/><w:right w:w="{right}" w:type="dxa"/></w:tcMar>')
    tcPr.append(tcMar)

def set_table_borders(table, color="CCCCCC", sz="4", val="single"):
    tblPr = table._tbl.tblPr
    borders = parse_xml(
        f'<w:tblBorders {nsdecls("w")}>'
        f'<w:top w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'<w:bottom w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'<w:insideH w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'<w:insideV w:val="none"/>'
        f'<w:left w:val="none"/>'
        f'<w:right w:val="none"/>'
        f'</w:tblBorders>'
    )
    tblPr.append(borders)

def build_paper_docx():
    doc = Document()
    
    # Page Setup (US Letter, 0.75 in margins)
    for section in doc.sections:
        section.page_width = Inches(8.5)
        section.page_height = Inches(11.0)
        section.top_margin = Inches(0.75)
        section.bottom_margin = Inches(0.75)
        section.left_margin = Inches(0.75)
        section.right_margin = Inches(0.75)

    # Base Normal Style
    normal_style = doc.styles['Normal']
    normal_font = normal_style.font
    normal_font.name = 'Times New Roman'
    normal_font.size = Pt(10)
    normal_font.color.rgb = RGBColor(0x11, 0x11, 0x11)
    normal_style.paragraph_format.line_spacing = 1.15
    normal_style.paragraph_format.space_after = Pt(4)
    normal_style.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY

    # Title
    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title.paragraph_format.space_before = Pt(0)
    p_title.paragraph_format.space_after = Pt(14)
    run_title = p_title.add_run("Development of a Multi-Format DVB-S2 Receiver Output\nStream Analyzer with Anomaly Detection and Diagnostic Reporting")
    run_title.font.name = 'Times New Roman'
    run_title.font.size = Pt(18)
    run_title.font.bold = True
    run_title.font.color.rgb = RGBColor(0x0a, 0x19, 0x2f)

    # Author Table (3 columns) - NO project guide in author block
    author_tbl = doc.add_table(rows=1, cols=3)
    author_tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    col_widths = [Inches(2.3), Inches(2.3), Inches(2.3)]
    
    authors_data = [
        ("Sk Samad", "Roll No: 20231COM0031", "Dept. of Computer Science & Engineering\nPresidency University\nBengaluru, India"),
        ("Y Vengala Rao", "Roll No: 20231COM0001", "Dept. of Computer Science & Engineering\nPresidency University\nBengaluru, India"),
        ("C Rakeshwar", "Roll No: 20231COM0008", "Dept. of Computer Science & Engineering\nPresidency University\nBengaluru, India")
    ]
    
    for i, (name, roll, affil) in enumerate(authors_data):
        cell = author_tbl.cell(0, i)
        cell.width = col_widths[i]
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.line_spacing = 1.1
        p.paragraph_format.space_after = Pt(2)
        r_name = p.add_run(name + "\n")
        r_name.font.name = 'Times New Roman'
        r_name.font.size = Pt(11)
        r_name.font.bold = True
        
        r_roll = p.add_run(roll + "\n")
        r_roll.font.name = 'Times New Roman'
        r_roll.font.size = Pt(9.5)
        
        r_affil = p.add_run(affil)
        r_affil.font.name = 'Times New Roman'
        r_affil.font.size = Pt(9)
        r_affil.font.italic = True

    p_spacer = doc.add_paragraph()
    p_spacer.paragraph_format.space_before = Pt(8)
    p_spacer.paragraph_format.space_after = Pt(8)

    # Abstract Box
    p_abs = doc.add_paragraph()
    p_abs.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p_abs.paragraph_format.left_indent = Inches(0.25)
    p_abs.paragraph_format.right_indent = Inches(0.25)
    p_abs.paragraph_format.space_after = Pt(6)
    
    r_abs_h = p_abs.add_run("Abstract—")
    r_abs_h.font.name = 'Times New Roman'
    r_abs_h.font.size = Pt(9.5)
    r_abs_h.font.bold = True
    r_abs_h.font.italic = True
    
    abs_text = (
        "Digital Video Broadcasting via Satellite (DVB-S2) provides the physical and data-link framing "
        "structure for satellite broadband, high-definition television distribution, and cellular backhaul. "
        "Modern satellite receivers demodulate radio-frequency downlinks and emit post-demodulator digital "
        "output streams across multiple heterogeneous encapsulation formats, primarily MPEG-2 Transport "
        "Streams (MPEG-TS), Generic Stream Encapsulation (GSE), and DVB-S2 Baseband Frames (BBFrame). "
        "Analyzing receiver output streams across these formats presents an operational engineering challenge: "
        "each format possesses fundamentally distinct framing boundaries, header structures, and error-propagation "
        "characteristics that conventional single-format protocol analyzers do not natively unify. This paper "
        "presents PRJ_111, an extensible software application engineered for multi-format DVB-S2 receiver "
        "output stream analysis, anomaly detection, and diagnostic reporting. The application establishes a "
        "unified analytical pipeline providing deterministic stream health evaluation inspired by ETSI TR 101 290 "
        "Priority-1 principles, unsupervised anomaly detection via format-isolated Isolation Forest models, "
        "structural pattern and Shannon entropy analysis, byte-indexed spatial activity timelines, bounded "
        "Z-score anomaly explanations, semantically guarded cross-format stream comparisons, and automated "
        "multi-format reporting organized under a tripartite epistemological taxonomy. Experimental validation "
        "across authoritative satellite broadcast captures demonstrates deterministic health accounting (100.0% "
        "on clean streams; 99.67% on corrupted streams with exact transport error tracking), unsupervised "
        "identification of multiplex bursts and truncation boundaries, and strict semantic isolation in "
        "cross-format differentials. The complete system is verified by an automated regression suite of 240 tests "
        "(207 backend and 33 frontend tests) achieving a 100% pass rate with zero failures and zero errors."
    )
    r_abs = p_abs.add_run(abs_text)
    r_abs.font.name = 'Times New Roman'
    r_abs.font.size = Pt(9.5)

    # Index Terms
    p_idx = doc.add_paragraph()
    p_idx.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p_idx.paragraph_format.left_indent = Inches(0.25)
    p_idx.paragraph_format.right_indent = Inches(0.25)
    p_idx.paragraph_format.space_after = Pt(14)
    
    r_idx_h = p_idx.add_run("Index Terms—")
    r_idx_h.font.name = 'Times New Roman'
    r_idx_h.font.size = Pt(9.5)
    r_idx_h.font.bold = True
    r_idx_h.font.italic = True
    
    r_idx = p_idx.add_run("Anomaly detection, Baseband frame, Digital video broadcasting, DVB-S2, Feature extraction, Generic stream encapsulation, Isolation Forest, MPEG transport stream, Receiver output analysis, Stream analysis.")
    r_idx.font.name = 'Times New Roman'
    r_idx.font.size = Pt(9.5)
    r_idx.font.italic = True

    def add_sec_h1(title):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(14)
        p.paragraph_format.space_after = Pt(5)
        run = p.add_run(title.upper())
        run.font.name = 'Times New Roman'
        run.font.size = Pt(11)
        run.font.bold = True
        return p

    def add_sec_h2(title):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p.paragraph_format.space_before = Pt(10)
        p.paragraph_format.space_after = Pt(3)
        run = p.add_run(title)
        run.font.name = 'Times New Roman'
        run.font.size = Pt(10.5)
        run.font.bold = True
        run.font.italic = True
        return p

    def add_fig_caption(num, title):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(3)
        p.paragraph_format.space_after = Pt(10)
        r_lbl = p.add_run(f"Fig. {num}. ")
        r_lbl.font.name = 'Times New Roman'
        r_lbl.font.size = Pt(9)
        r_lbl.font.bold = True
        r_txt = p.add_run(title)
        r_txt.font.name = 'Times New Roman'
        r_txt.font.size = Pt(9)
        return p

    def add_tbl_caption(num_str, title):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(12)
        p.paragraph_format.space_after = Pt(3)
        r1 = p.add_run(f"TABLE {num_str}\n")
        r1.font.name = 'Times New Roman'
        r1.font.size = Pt(9)
        r1.font.bold = True
        r2 = p.add_run(title.upper())
        r2.font.name = 'Times New Roman'
        r2.font.size = Pt(9)
        r2.font.bold = True
        return p

    def add_equation(eq_text, eq_num):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        p.paragraph_format.space_before = Pt(6)
        p.paragraph_format.space_after = Pt(6)
        p.paragraph_format.left_indent = Inches(0.5)
        p.paragraph_format.right_indent = Inches(0.5)
        
        # Tabs for center math, right number
        r_math = p.add_run(f"{eq_text}       ({eq_num})")
        r_math.font.name = 'Times New Roman'
        r_math.font.size = Pt(10)
        r_math.font.italic = True
        return p

    # SECTION I
    add_sec_h1("I. Introduction")
    
    doc.add_paragraph(
        "The Second Generation Digital Video Broadcasting via Satellite standard (DVB-S2, ETSI EN 302 307-1) "
        "represents the foundational physical and framing specification for modern satellite telecommunications [1]. "
        "Operating downstream of the satellite low-noise block downconverter (LNB) and intermediate-frequency (IF) tuner, "
        "the satellite receiver demodulator performs carrier acquisition, matched filtering, forward error correction (FEC) "
        "decoding using coupled Low-Density Parity-Check (LDPC) and Bose-Chaudhuri-Hocquenghem (BCH) codes, and baseband "
        "deframing [2]. The resulting post-demodulator digital output stream forms the critical boundary between "
        "satellite physical-layer transmission and terrestrial networking appliances."
    )
    
    doc.add_paragraph(
        "In operational satellite ground stations, television distribution networks, and satellite broadband terminals, "
        "post-demodulator output is not uniform. Depending on transponder service profiles and downstream equipment, "
        "receivers emit digital data in one of three standardized digital framing representations:\n"
        "1) MPEG-2 Transport Stream (MPEG-TS): Fixed 188-byte containers featuring periodic synchronization markers (0x47), "
        "13-bit Program Identifiers (PIDs), and continuity counters, standard in linear television broadcasting [3].\n"
        "2) Generic Stream Encapsulation (GSE): Variable-length protocol data units (PDUs) featuring 2-bit start/end "
        "fragmentation flags, 16-bit EtherType protocol identifiers, and cyclic redundancy checks, standard in satellite IP broadband [4].\n"
        "3) DVB-S2 Baseband Frames (BBFrame): The native physical-layer container defined by an 80-bit Baseband Header (BBHeader), "
        "Mode Adaptation flags (MATYPE-1/2), User Packet Length (UPL), Data Field Length (DFL), and CRC-8 header protection [1]."
    )

    doc.add_paragraph(
        "Analyzing receiver output streams is essential for ground station commissioning, transponder capacity verification, "
        "stream integrity assessment, and transmission debugging. However, analyzing these heterogeneous representations "
        "using conventional tools presents operational limitations [5]. Generic packet analyzers (such as Wireshark) "
        "treat captures as Ethernet frames, requiring specialized external dissectors that lack native support for raw "
        "concatenated transport streams or raw baseband frame telemetry [6]. Conversely, dedicated broadcast hardware "
        "instruments are tailored primarily to MPEG-TS, providing limited native support for modern DVB-S2 baseband frames "
        "or GSE IP encapsulation [5]."
    )

    doc.add_paragraph(
        "Furthermore, existing analysis tools suffer from three fundamental engineering deficiencies:\n"
        "1) Framing Heterogeneity and Parser Brittleness: Digital captures arrive as unindexed raw binary bitstreams (.ts, .gse, .bin, .pcap). "
        "Naive file-extension parsers misidentify formats, while streaming parsers without robust synchronization recovery fail when encountering bit errors.\n"
        "2) Lack of Cross-Format Telemetry: Comparing packet counts, PDU counts, and baseband frame counts directly creates false equivalence, "
        "misleading ground station operators by comparing metrics with incompatible physical dimensions.\n"
        "3) Epistemic Over-Claiming in Stream Telemetry: Many commercial monitoring tools calculate synthetic clock timestamps or fictitious "
        "Megabits-per-second (Mbps) throughputs in offline files where no receiver clock telemetry exists, or assert speculative physical-layer "
        "causal inferences (e.g., attributing a continuity counter error to 'rain fade' without demodulator signal-to-noise ratio measurements)."
    )

    doc.add_paragraph(
        "To resolve these challenges, this paper presents PRJ_111, a specialized, modular software application engineered for "
        "multi-format DVB-S2 receiver output stream analysis. PRJ_111 establishes an integrated seven-feature analytical pipeline (F1–F7) "
        "that performs content-aware format sniffer ingestion, deterministic framing parsing, unified feature extraction, rule-based stream "
        "health analysis (F1), unsupervised Isolation Forest anomaly detection (F2), structural pattern and entropy analysis (F3), physical "
        "spatial activity timelines (F4), bounded Z-score diagnostic anomaly explanations (F5), semantically guarded stream comparisons (F6), "
        "and automated multi-format diagnostic report generation (F7)."
    )

    doc.add_paragraph(
        "The remainder of this paper is organized as follows: Section II reviews related literature. Section III presents the system architecture. "
        "Section IV details multi-format parsing. Section V elaborates the seven-feature analytical pipeline. Section VI outlines the experimental "
        "setup and datasets. Section VII analyzes empirical results. Section VIII details automated software verification. Section IX presents "
        "limitations and domain-safety considerations. Section X concludes the paper with directions for future work."
    )

    # SECTION II
    add_sec_h1("II. Related Work")
    doc.add_paragraph(
        "The technical foundation of PRJ_111 synthesizes international telecommunications standards, satellite protocol engineering, "
        "unsupervised machine learning, and empirical stream monitoring."
    )

    add_sec_h2("A. DVB-S2 Framing and Encapsulation Protocols")
    doc.add_paragraph(
        "The DVB-S2 standard (ETSI EN 302 307-1) defines framing, channel coding, and modulation for satellite communications, establishing "
        "Adaptive Coding and Modulation (ACM) and Native Baseband Framing [1]. Morello and Mignone [2] analyzed the physical layer mechanisms "
        "of DVB-S2, demonstrating how variable-length user packets are encapsulated into baseband frames protected by inner LDPC and outer "
        "BCH codes. Casini et al. [7] analyzed modulation constellations ranging from QPSK to 32-APSK, detailing the role of the 80-bit Baseband "
        "Header (BBHeader), Roll-Off factors (α ∈ {0.20, 0.25, 0.35}), and Data Field Length (DFL) bit allocation. Sklar [8] provided the "
        "foundational framework for digital modulation, channel coding limits, and baseband framing boundaries in digital communication channels."
    )
    doc.add_paragraph(
        "For network layer transport, Fairhurst and Collini-Nocker [9] formulated Generic Stream Encapsulation (ETSI TS 102 606-1) [4] to replace "
        "legacy Multi-Protocol Encapsulation (MPE over MPEG-TS) and Unidirectional Lightweight Encapsulation (ULE, RFC 4326) [10]. GSE defines "
        "variable-size protocol data units carrying native IP datagrams with fragment-level CRC-32 protection, eliminating transport stream "
        "packing overhead. Digital television distribution continues to rely on the MPEG-2 Transport Stream (ISO/IEC 13818-1) [3]. Operational "
        "measurement guidelines for DVB broadcast systems are standardized in ETSI TR 101 290 [11], which defines Priority-1 stream parameters: "
        "loss of synchronization, Transport Error Indicator (TEI) assertions, and Continuity Counter (CC) errors. DVB Service Information (SI) "
        "standards are specified in ETSI EN 300 468 [12]."
    )

    add_sec_h2("B. Broadcast Stream Monitoring and Protocol Inspection")
    doc.add_paragraph(
        "Luisi et al. [5] evaluated digital video broadcast stream monitoring techniques, demonstrating that while hardware TS analyzers "
        "reliably evaluate ETSI TR 101 290 Priority-1 errors, they lack native decoding for modern multi-protocol IP encapsulations (GSE and "
        "BBFrames) emitted by satellite broadband receivers. Minoli [6] surveyed network packet inspection tools, noting that packet sniffers "
        "treat raw digital bitstreams as unstructured payloads unless encapsulated in network capture wrappers (such as PCAP). PRJ_111 resolves "
        "these limitations by providing native, modular parsers for MPEG-TS, GSE, and BBFrames directly from raw receiver bitstreams."
    )

    add_sec_h2("C. Unsupervised Anomaly Detection in Telecommunications")
    doc.add_paragraph(
        "Anomaly detection in streaming telemetry has been surveyed by Chandola et al. [13] and Pimentel et al. [14]. Traditional statistical "
        "process control relies on static thresholds, which present difficulties in multiplexed channels where bitrates fluctuate dynamically "
        "with statistical multiplexing. Supervised classification approaches require extensive ground-truth labeled anomaly datasets [13]. "
        "In operational DVB-S2 receiver monitoring, labeled anomalous bitstreams are rarely available; captured receiver data reflects "
        "proprietary commercial broadcasts, encrypted carrier feeds, or transient operational anomalies."
    )
    doc.add_paragraph(
        "To address unlabeled streaming data, Liu et al. [15], [16] introduced the Isolation Forest algorithm. Isolation Forest isolates anomalies "
        "explicitly rather than profiling normal instances, constructing ensembles of random isolation trees (iTrees). Because anomalies "
        "possess distinct feature attributes, they are isolated closer to tree roots, resulting in shorter average path lengths [15]. Baggio et al. "
        "[17] evaluated unsupervised machine learning models for network traffic anomaly detection, demonstrating that Isolation Forest achieves "
        "superior computational efficiency (O(n log n) training complexity) and robust outlier detection in streaming feature spaces compared to "
        "distance-based models such as k-means++ [18] or density-based clustering such as DBSCAN [19]. Shannon [20] established the mathematical "
        "foundation of information entropy, utilized in this work to evaluate PID multiplex distribution concentration. PRJ_111 adapts Isolation "
        "Forest to DVB-S2 telemetry, executing format-isolated, spatial-window anomaly detection with calibrated logistic decision boundaries."
    )

    # SECTION III
    add_sec_h1("III. System Architecture and Workstation Design")
    doc.add_paragraph(
        "The architecture of PRJ_111 is illustrated in Fig. 1. The system is structured as a six-stage pipeline that ingests raw post-demodulator "
        "digital receiver output, processes framing syntax, extracts unified features, executes analytical engines (F1–F3), generates spatial "
        "timeline telemetry (F4), diagnoses deviations (F5), evaluates dual-stream differentials (F6), and synthesizes multi-format reports (F7) "
        "through a standalone engineering workstation interface."
    )

    # Insert Fig 1
    fig1_path = "paper_assets/architecture_diagram.png"
    if os.path.exists(fig1_path):
        p_img = doc.add_paragraph()
        p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img.paragraph_format.space_before = Pt(8)
        p_img.paragraph_format.space_after = Pt(2)
        doc.add_picture(fig1_path, width=Inches(6.5))
        add_fig_caption(1, "End-to-End Architectural Pipeline of the PRJ_111 DVB-S2 Receiver Output Stream Analyzer (Stages 1 through 6).")

    add_sec_h2("A. Ingestion and Local Workstation Architecture")
    doc.add_paragraph(
        "PRJ_111 is implemented in Python 3.12 as a local engineering workstation with zero external cloud or proprietary licensing dependencies:\n"
        "• Backend Core: Pure Python modular architecture (dvbs2_analyzer/ingestion/, parsers/, features/, analysis/).\n"
        "• Machine Learning Layer: Scikit-learn (IsolationForest) coupled with NumPy and SciPy for numerical vector operations.\n"
        "• HTTP Gateway: Multi-threaded native Python HTTP server (ThreadingHTTPServer) exposing a RESTful JSON API (/api/status, /api/analyze, /api/compare, /api/upload, /api/export).\n"
        "• Frontend Workstation: Single-Page Application (SPA) built with vanilla HTML5, CSS3, and ES6 JavaScript. Visualizations are rendered offline using vendored Chart.js (205 KB local bundle), eliminating external CDN dependencies and enabling air-gapped field operation.\n"
        "• Local Staging Security: Direct browser file uploads are staged locally under 05_CODE/uploads/ with alphanumeric token sanitization and directory traversal prevention (os.path.commonpath)."
    )

    # Insert Fig 2
    fig2_path = "paper_assets/fig_dashboard_analyzed.png"
    if os.path.exists(fig2_path):
        p_img = doc.add_paragraph()
        p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img.paragraph_format.space_before = Pt(8)
        p_img.paragraph_format.space_after = Pt(2)
        doc.add_picture(fig2_path, width=Inches(6.0))
        add_fig_caption(2, "PRJ_111 Engineering Workstation active analysis dashboard evaluating an off-air MPEG-TS capture (sample.ts).")

    # SECTION IV
    add_sec_h1("IV. Multi-Format Stream Processing")
    doc.add_paragraph(
        "The parsing layer operates directly on raw binary stream captures, providing modular decoders tailored to each standard. "
        "Format selection is governed by a content-aware format sniffer that evaluates synchronization bytes, transport error flags, "
        "GSE headers, and BBHeader CRC-8 checksums."
    )

    add_sec_h2("A. MPEG-2 Transport Stream (MPEG-TS) Processing")
    doc.add_paragraph(
        "The MPEG-TS parser processes continuous 188-byte containers specified in ISO/IEC 13818-1 [3]. Each packet header is decoded as:\n"
        "• Sync Byte: Must equal 0x47 (01000111 binary). If the parser encounters a non-0x47 byte, it increments sync_byte_errors and scans forward byte-by-byte for the next valid synchronization byte.\n"
        "• Transport Error Indicator (TEI): Bit 7 of byte 1. When asserted (TEI = 1), indicates that an uncorrected error exists within the packet container.\n"
        "• Payload Unit Start Indicator (PUSI): Bit 6 of byte 1. Indicates that the packet payload begins with a Program Association Table (PAT), Program Map Table (PMT), or Packetized Elementary Stream (PES) header.\n"
        "• Transport Priority: Bit 5 of byte 1.\n"
        "• Program Identifier (PID): 13-bit value ([0, 8191]) defining the logical elementary stream multiplex. Null packets are identified by PID = 8191 (0x1FFF).\n"
        "• Transport Scrambling Control (TSC): Bits 7–6 of byte 3.\n"
        "• Adaptation Field Control (AFC): Bits 5–4 of byte 3, indicating payload-only (01), adaptation-field-only (10), or adaptation-field followed by payload (11).\n"
        "• Continuity Counter (CC): 4-bit cyclic counter ([0, 15]) incremented per PID. Discontinuities (CC_curr ≠ (CC_prev + 1) mod 16) indicate an observed sequence gap for the corresponding PID."
    )

    add_sec_h2("B. Generic Stream Encapsulation (GSE) Processing")
    doc.add_paragraph(
        "The GSE parser decodes variable-size protocol data units adhering to ETSI TS 102 606-1 [4]:\n"
        "• Start/End Flags (S, E): 2 bits defining PDU fragmentation. S=1, E=1 indicates an unfragmented PDU; S=1, E=0 indicates the first fragment; S=0, E=0 intermediate fragments; S=0, E=1 the last fragment.\n"
        "• GSE Length Field Specification: In ETSI TS 102 606-1, the GSE Length field is a 12-bit binary field encoding integer values from 0 to 4,095 (2^12 - 1 = 4095). It explicitly indicates the length in octets of the GSE payload and optional fields following the 2-byte GSE base header. Therefore, the maximum representable encapsulated payload is 4,095 bytes, and including the 2-byte base header, the maximum theoretical total PDU length is 4,097 bytes. In our implementation and in the captured validation dataset, all PDUs satisfy this constraint, with the maximum observed PDU length being 1,444 bytes.\n"
        "• Protocol Type: 16-bit EtherType identifier (e.g., 0x0800 for IPv4, 0x86DD for IPv6) or GSE extension header type (GSE_EXT_NPA).\n"
        "• Label Type: 2 bits specifying 6-byte (LABEL_6B), 3-byte (LABEL_3B), or label-less (LABEL_NONE) addressing.\n"
        "• Fragment ID & Total Length: Present in fragmented PDUs to facilitate payload reassembly.\n"
        "• CRC-32 Verification: 32-bit CRC polynomial calculated over the PDU payload and headers for complete PDUs and last fragments."
    )

    add_sec_h2("C. DVB-S2 Baseband Frame (BBFrame) Processing")
    doc.add_paragraph(
        "The BBFrame parser decodes native satellite baseband frames specified in ETSI EN 302 307-1 [1]. Each frame contains an 80-bit (10-byte) BBHeader followed by the data field:\n"
        "• MATYPE-1 (Mode Adaptation Type 1):\n"
        "  - Stream Input (TS/GS): Bits 7–6 indicate Single Input Stream (SIS) or Multiple Input Streams (MIS).\n"
        "  - Modulation & Coding: Bit 5 indicates Constant Coding & Modulation (CCM) or Adaptive Coding & Modulation (ACM).\n"
        "  - ISSYI / NPD: Input Stream Synchronization Indicator and Null Packet Deletion flags.\n"
        "  - Roll-Off Factor (α): Bits 1–0 specify α = 0.35 (00), α = 0.25 (01), or α = 0.20 (10).\n"
        "• MATYPE-2: Input Stream Identifier (ISI) when MIS is active.\n"
        "• User Packet Length (UPL): 16-bit integer defining the length of encapsulated user packets.\n"
        "• Data Field Length (DFL): 16-bit integer defining the active payload bits in the frame ([0, K_bch]). DFL is expressed in bits, representing the usable user data field within the physical baseband frame.\n"
        "• SYNC & SYNCD: 8-bit copy of user packet synchronization marker and 16-bit distance in bits to the first user packet.\n"
        "• CRC-8 Checksum: 8-bit error detection code computed over the preceding 72 bits using polynomial G(x) = x^8 + x^7 + x^6 + x^4 + x^2 + 1. Frames failing CRC-8 validation are flagged as corrupted."
    )

    # TABLE I
    add_tbl_caption("I", "Supported Input Format Characteristics")
    tbl1 = doc.add_table(rows=4, cols=5)
    tbl1.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(tbl1)
    tbl1_headers = ["Format", "Structure", "Header", "Container Dimension", "Checksum"]
    tbl1_data = [
        ["MPEG-TS", "Fixed Packet", "4 Bytes", "Fixed 188 Bytes", "Continuity Counter (4b)"],
        ["GSE", "Variable PDU", "2–8 Bytes", "45–1,444 Bytes (Var.)", "CRC-32 (32 bits)"],
        ["BBFrame", "Fixed Frame", "10 Bytes", "216–10,000 Bits (DFL)", "CRC-8 (8 bits)"]
    ]
    for c_idx, h_text in enumerate(tbl1_headers):
        cell = tbl1.cell(0, c_idx)
        set_cell_background(cell, "F0F4F8")
        set_cell_margins(cell, 80, 80, 100, 100)
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(h_text)
        r.font.name = 'Times New Roman'
        r.font.size = Pt(9)
        r.font.bold = True
    for r_idx, row_data in enumerate(tbl1_data):
        for c_idx, val in enumerate(row_data):
            cell = tbl1.cell(r_idx + 1, c_idx)
            set_cell_margins(cell, 60, 60, 100, 100)
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER if c_idx != 0 else WD_ALIGN_PARAGRAPH.LEFT
            r = p.add_run(val)
            r.font.name = 'Times New Roman'
            r.font.size = Pt(8.5)

    # SECTION V
    add_sec_h1("V. Feature Engineering and Analytical Pipeline")
    doc.add_paragraph(
        "To analyze streams across disparate formats without creating invalid semantic conflations, PRJ_111 establishes "
        "the UnifiedStreamFeatureSet architecture. Telemetry is bifurcated into physical invariants (CommonMetrics) and native "
        "format-specific metrics (TSMetrics, GSEMetrics, BBFrameMetrics)."
    )

    add_sec_h2("A. Feature F1: Stream Health Analysis")
    doc.add_paragraph(
        "Feature F1 executes deterministic stream health analysis, evaluating selected stream integrity indicators inspired by "
        "ETSI TR 101 290 principles [11]. Rather than employing arbitrary penalty weight sums, PRJ_111 implements a transparent "
        "threshold-driven deductive scoring model encoded in analysis/health.py. Each evaluated spatial window W_i starts from an "
        "initial healthy score of 100.0%. Deductions are applied transparently based on threshold triggers:\n"
        "• Sync Integrity (ETSI TR 101 290 P1.1): Critical (< 95.00%): deducts 40.0%; Warning (< 99.99%): deducts 20.0%.\n"
        "• Transport Error Indicator (ETSI TR 101 290 P1.3): Critical (> 1.00% error rate): deducts 30.0%; Warning (> 0.00% error rate): deducts 15.0%.\n"
        "• Continuity Counter Errors (ETSI TR 101 290 P1.4): Critical (> 0.50% error rate): deducts 30.0%; Warning (> 0.01% error rate): deducts 15.0%.\n"
        "• Null Packet Ratio: Idle Transponder Beacon (> 99.90% null packets): deducts 10.0%; High Padding (> 95.00% null packets): deducts 5.0%.\n"
        "• Header Malformations: Critical (> 10 malformed headers): deducts 20.0%; Warning (> 1 malformed header): deducts 10.0%."
    )
    doc.add_paragraph("The health score of window W_i is evaluated by:")
    add_equation("H(W_i) = max(0.0, 100.0 + ∑ ΔH)", "1")
    doc.add_paragraph("The overall stream health score H is the arithmetic mean across all N evaluated spatial windows:")
    add_equation("H = (1 / N) ∑_{i=1}^N H(W_i)", "2")
    doc.add_paragraph(
        "Streams are categorized into operational states:\n"
        "• HEALTHY: H ≥ 99.0%\n"
        "• DEGRADED / WARNING: 80.0% ≤ H < 99.0%\n"
        "• CRITICAL: H < 80.0%"
    )

    add_sec_h2("B. Feature F2: AI-Based Anomaly Detection")
    doc.add_paragraph(
        "Feature F2 implements unsupervised anomaly detection across rolling spatial windows using the Isolation Forest algorithm [15] "
        "through Scikit-learn. Given a spatial window W_i containing K units (K = 200 for TS, K = 3 for GSE, K = 50 for BBFrame), an m-dimensional "
        "feature vector x_i ∈ R^m is extracted, capturing payload volume, integrity ratio, error rate, entropy, unit size variance, and format-specific telemetry."
    )
    doc.add_paragraph(
        "The anomaly detector instantiates an ensemble of T = 100 isolation trees (n_estimators=100, contamination=0.05, random_state=42). "
        "The raw decision output d(x) ∈ R is computed using Scikit-learn's decision_function, where negative values designate outliers and "
        "positive values designate inliers. To map this output to a normalized, intuitive anomaly score s(x) ∈ [0.0, 1.0], PRJ_111 applies a "
        "centered logistic sigmoid transformation:"
    )
    add_equation("s(x) = 1 / (1 + e^{8.0 · d(x)})", "3")
    doc.add_paragraph(
        "At the nominal decision boundary (d(x) = 0.0), the score evaluates to exactly s = 0.5000. Outliers (d(x) < 0) map to s > 0.5000, "
        "while regular inliers (d(x) > 0) map to s < 0.5000. Anomaly classification is determined by the decision threshold:"
    )
    add_equation("Anomaly Flag = TRUE if s(x_i) ≥ 0.5000, FALSE if s(x_i) < 0.5000", "4")
    doc.add_paragraph(
        "Domain Safety Guard on Machine Learning Metrics: Because operational satellite receiver output bitstreams are inherently unlabeled, "
        "no ground-truth anomaly annotations exist for off-air broadcast captures. Therefore, PRJ_111 avoids asserting classification accuracy, "
        "precision, recall, or F1-score on real broadcast data. Model sensitivity is validated through controlled synthetic perturbation experiments, "
        "wherein known corruptions (bit flips, synthetic sync byte drops, and container truncations) are injected into verified captures to demonstrate "
        "that the detector flags abnormal intervals with s ≥ 0.5000."
    )

    add_sec_h2("C. Feature F3: Pattern and Entropy Analysis")
    doc.add_paragraph(
        "Feature F3 identifies structural patterns and multiplex characteristics across stream progress:\n"
        "• MPEG-TS PID Distribution & Shannon Entropy: Computes individual packet counts and percentage shares per PID. The dominant PID and Shannon entropy [20] are evaluated:"
    )
    add_equation("H_{PID} = - ∑_{k=1}^P p_k log_2 p_k,   p_k = N_k / ∑_{j=1}^P N_j", "5")
    doc.add_paragraph(
        "• PAT/PMT Program Structure: Identifies Program Association Tables (PID = 0) and Program Map Tables, tracking program multiplex recurrence [12].\n"
        "• GSE Protocol Mapping: Classifies encapsulated protocol types (GSE_EXT_NPA, IPv4, IPv6) and quantifies fragmentation ratios (N_frag / N_total).\n"
        "• BBFrame Mode Transitions: Tracks shifts in modulation profiles (ACM vs. CCM), Single vs. Multiple Input Stream allocations, and DFL distribution clustering."
    )

    add_sec_h2("D. Feature F4: Spatial Activity Timeline")
    doc.add_paragraph(
        "Feature F4 provides continuous visual mapping of stream activity across spatial progress (Fig. 3).\n"
        "Absence of Fabricated Timestamps: Offline receiver bitstreams captured from demodulator test points lack calibrated broadcast wall-clock telemetry. "
        "Assigning synthetic timestamps or calculating fictitious throughput rates (e.g., '15.4 Mbps') creates false precision. PRJ_111 indexes all timeline events strictly by:\n"
        "1) Physical Byte Offset: [B_start, B_end] indicating exact octet positions in the capture file.\n"
        "2) Container Sequence Index: Unit indices [U_start, U_end] tracking sequential packet, PDU, or frame numbers.\n"
        "The timeline visualizes rolling F1 stream health ([0, 100%]), F2 anomaly scores ([0.0, 1.0]) alongside the 0.5000 threshold line, payload density (KB per window), "
        "and format-specific telemetry without fabricating clock timestamps."
    )

    # Insert Fig 3
    fig3_path = "paper_assets/fig_timeline_view.png"
    if os.path.exists(fig3_path):
        p_img = doc.add_paragraph()
        p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img.paragraph_format.space_before = Pt(8)
        p_img.paragraph_format.space_after = Pt(2)
        doc.add_picture(fig3_path, width=Inches(6.0))
        add_fig_caption(3, "Spatial activity timeline (Feature F4) charting rolling stream health, anomaly scores with decision threshold (s = 0.5000), payload density, and PID entropy indexed strictly by physical byte offsets.")

    add_sec_h2("E. Feature F5: Diagnostic Anomaly Explanation")
    doc.add_paragraph(
        "Feature F5 bridges unsupervised machine learning and domain engineering by attributing flagged anomalies to specific metric deviations (Fig. 4). "
        "For each feature j in anomalous window W_i, deviation from the stream baseline is evaluated using an operational dispersion model:"
    )
    add_equation("z_{i,j} = (x_{i,j} - μ_j) / max(σ_j, ε_j)", "6")
    doc.add_paragraph(
        "where μ_j is the stream mean for feature j, σ_j is standard deviation, and ε_j is an operational dispersion floor preventing division-by-zero on invariant channels. "
        "To eliminate unbounded numerical artifacts while maintaining mathematical interpretability, PRJ_111 bounds the Z-score:"
    )
    add_equation("z_{bounded} = clamp(z_{i,j}, -20.0, +20.0)", "7")
    doc.add_paragraph(
        "The magnitude |z_bounded| is accompanied by an explicit deviation direction: ABOVE_BASELINE (z > 0) or BELOW_BASELINE (z < 0).\n"
        "Physical-Layer Domain Safety Guard: PRJ_111 operates strictly on digital post-demodulator bitstreams. Without access to baseband constellation measurements "
        "or RF tuner AGC levels, the application avoids asserting physical-layer root causes. F5 diagnoses are constrained to digital observations (e.g., 'Elevated adaptation "
        "field frequency' or 'Recording termination boundary'), avoiding speculative claims such as 'rain fade,' 'LNB drift,' or 'transponder power drop.'"
    )

    # Insert Fig 4
    fig4_path = "paper_assets/fig_anomaly_view.png"
    if os.path.exists(fig4_path):
        p_img = doc.add_paragraph()
        p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img.paragraph_format.space_before = Pt(8)
        p_img.paragraph_format.space_after = Pt(2)
        doc.add_picture(fig4_path, width=Inches(6.0))
        add_fig_caption(4, "Flagged anomaly windows and diagnostic attribution table (Features F2 and F5) displaying unit ranges, byte offsets, anomaly scores, and Bounded Z-Score explanations with deviation directionality.")

    add_sec_h2("F. Feature F6: Semantic Stream Comparison Engine")
    doc.add_paragraph(
        "Feature F6 provides differential comparison between two analyzed streams (Stream A and Stream B) as shown in Fig. 5.\n"
        "The Cross-Format Semantic Barrier: A key architectural contribution of PRJ_111 is the Cross-Format Semantic Barrier. Metrics sharing identical nomenclature inside "
        "CommonMetrics are not assumed to be comparable across formats:\n"
        "• Comparable Metrics (2): total_payload_bytes (an octet of user data represents an invariant physical quantity) and integrity_ratio (dimensionless syntactic compliance proportion [0.0, 1.0]).\n"
        "• Non-Comparable Metrics (9): total_units, valid_units, invalid_units, truncated_units, mean_payload_bytes, payload_ratio, error_count, error_rate, and entropy are blocked cross-format with explicit engineering justifications.\n"
        "For comparable metrics, differences are quantified without mathematical singularities:"
    )
    add_equation("Δ_{abs} = B - A", "8")
    add_equation("Δ_{rel} = ( (B - A) / A ) · 100%  if A > 0;  Undefined (Critical) if A = 0, B > 0;  0.0% if A = 0, B = 0", "9")
    doc.add_paragraph(
        "Differences are classified into a four-tier significance hierarchy:\n"
        "• NEGLIGIBLE: |Δ_{rel}| < 2.0%\n"
        "• MINOR: 2.0% ≤ |Δ_{rel}| < 10.0%\n"
        "• SUBSTANTIAL: 10.0% ≤ |Δ_{rel}| < 50.0%\n"
        "• CRITICAL: |Δ_{rel}| ≥ 50.0% (or non-zero error emergence from zero baseline)\n"
        "Windows are synchronized via direct-index overlap: i ∈ [0, min(N_A, N_B) - 1]. Trailing windows in asymmetric captures are recorded under unaligned_windows as capture duration differences, not transmission loss."
    )

    # Insert Fig 5
    fig5_path = "paper_assets/fig_comparison_view.png"
    if os.path.exists(fig5_path):
        p_img = doc.add_paragraph()
        p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img.paragraph_format.space_before = Pt(8)
        p_img.paragraph_format.space_after = Pt(2)
        doc.add_picture(fig5_path, width=Inches(6.0))
        add_fig_caption(5, "Stream comparison interface (Feature F6) evaluating MPEG-TS against corrupted TS, highlighting direct-index window alignment, payload delta (-0.06%), and the dynamic semantic audit table.")

    add_sec_h2("G. Feature F7: Automatic Multi-Format Reporting")
    doc.add_paragraph(
        "Feature F7 synthesizes F1–F6 analytical results into exportable executive reports (JSON, Markdown, CP-1252-safe Plain Text, and Standalone HTML5) as illustrated in Fig. 6.\n"
        "All findings generated by F7 are categorized under a formal tripartite epistemological taxonomy:\n"
        "1) OBSERVED_FACT: Direct, deterministic physical measurements directly verifiable in stream syntax (e.g., total_units = 18176, sync_byte_errors = 0).\n"
        "2) STATISTICAL_FINDING: Quantities derived through statistical or machine learning models (e.g., health_score = 100.0, anomalous_windows = 5, peak_anomaly_score = 0.8576).\n"
        "3) ENGINEERING_INTERPRETATION: Domain-bounded diagnostic attributions constrained strictly to digital bitstream characteristics (e.g., 'Capture termination boundary accounts for partial trailing window')."
    )

    # Insert Fig 6
    fig6_path = "paper_assets/fig_report_view.png"
    if os.path.exists(fig6_path):
        p_img = doc.add_paragraph()
        p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img.paragraph_format.space_before = Pt(8)
        p_img.paragraph_format.space_after = Pt(2)
        doc.add_picture(fig6_path, width=Inches(6.0))
        add_fig_caption(6, "Multi-format diagnostic report generation view (Feature F7) showing tripartite findings categorization and one-click export controls.")

    # SECTION VI
    add_sec_h1("VI. Experimental Setup and Datasets")
    doc.add_paragraph(
        "The system was evaluated against four authoritative satellite captures stored in 01_RAW_DATA/:\n"
        "1) MPEG-TS Clean Capture (01_RAW_DATA/03_TS/DVBS2_toolkit/sample.ts): 3,417,088 bytes of off-air DVB-S2 satellite television broadcast, "
        "captured via DVBS2_toolkit, containing 18,176 fixed 188-byte packets.\n"
        "2) MPEG-TS Corrupted Capture (01_RAW_DATA/03_TS/DVBS2_toolkit/corrupted_sample.ts): 3,417,088 bytes containing 11 corrupted synchronization bytes in the initial segment.\n"
        "3) GSE Authoritative Capture (01_RAW_DATA/02_GSE/GSExtract/sample.ts): 9,324 bytes containing 14 variable-length GSE PDUs carrying encapsulated IPv4 datagrams, "
        "captured via GSExtract. (The filename sample.ts is preserved as the authoritative project container file).\n"
        "4) DVB-S2 Baseband Frame Capture (01_RAW_DATA/01_BBFRAME_GSE/dvb-s2_bb_example.pcap): 2,349,376 bytes containing 4,309 DVB-S2 Baseband Frames with ACM and SIS/MIS configuration."
    )

    # SECTION VII
    add_sec_h1("VII. Results and Discussion")
    doc.add_paragraph(
        "Empirical results across the authoritative captures are documented in Tables II through VI."
    )

    add_sec_h2("A. MPEG-TS Health and Priority-1 Verification")
    doc.add_paragraph(
        "As shown in Table II, the clean capture sample.ts achieved 100.0% sync byte integrity across all 18,176 packets, with 0 TEI errors and 0 continuity counter discontinuities. "
        "Net extracted user payload was 3,267,305 bytes, calculated by subtracting 72,704 bytes of fixed 4-byte headers and 77,079 bytes of adaptation field overhead from the 3,417,088-byte file volume. "
        "Stream health evaluated to 100.0% (HEALTHY)."
    )
    doc.add_paragraph(
        "Diagnostic Trace of Corrupted TS: TSParser encountered 11 corrupted sync bytes in the initial segment and resynchronized, dropping exactly 8 unaligned packets. "
        "The 18,168 yielded packets exhibited 100.0% sync byte integrity. Four packets suffered false sync alignment in payload data resulting in TEI = 4 in Window 0 (Window 0 health = 70.0%). "
        "Windows 1–90 exhibited 100.0% health, yielding an average stream health of 99.67%, satisfying the ≥ 99.0% threshold for HEALTHY."
    )

    # TABLE II
    add_tbl_caption("II", "MPEG-TS Health and Priority-1 Integrity Results")
    tbl2 = doc.add_table(rows=3, cols=8)
    tbl2.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(tbl2)
    tbl2_headers = ["Stream Capture", "Yielded Pkts", "Sync Int.", "TEI", "CC", "Net Payload", "Health", "Status"]
    tbl2_data = [
        ["sample.ts (Clean)", "18,176", "100.0%", "0 (0.00%)", "0 (0.00%)", "3,267,305 B", "100.0%", "HEALTHY"],
        ["corrupted_sample.ts", "18,168", "100.0%", "4 (0.02%)", "0 (0.00%)", "3,265,277 B", "99.67%", "HEALTHY"]
    ]
    for c_idx, h_text in enumerate(tbl2_headers):
        cell = tbl2.cell(0, c_idx)
        set_cell_background(cell, "F0F4F8")
        set_cell_margins(cell, 80, 80, 80, 80)
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(h_text)
        r.font.name = 'Times New Roman'
        r.font.size = Pt(8.5)
        r.font.bold = True
    for r_idx, row_data in enumerate(tbl2_data):
        for c_idx, val in enumerate(row_data):
            cell = tbl2.cell(r_idx + 1, c_idx)
            set_cell_margins(cell, 60, 60, 80, 80)
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER if c_idx != 0 else WD_ALIGN_PARAGRAPH.LEFT
            r = p.add_run(val)
            r.font.name = 'Times New Roman'
            r.font.size = Pt(8.5)

    add_sec_h2("B. GSE Encapsulation and Protocol Results")
    doc.add_paragraph(
        "Telemetry for the authoritative GSE capture (01_RAW_DATA/02_GSE/GSExtract/sample.ts) is documented in Table III. The capture contained 14 PDUs totaling 9,324 bytes, "
        "yielding 8,764 bytes of net extracted payload (626.0 bytes mean length, ranging from 45 to 1,444 bytes). Fragmentation analysis revealed 6 unfragmented PDUs (42.9%) "
        "and 8 fragmented PDUs (57.1%), consisting of 5 first fragments, 0 intermediate fragments, and 3 last fragments. Protocol analysis showed 11 PDUs encapsulated via "
        "GSE_EXT_NPA (100% of outer headers) and 9 PDUs carrying IPv4 datagrams. Addressing labels comprised 11 6-byte labels and 3 label-less PDUs. All PDUs passed CRC-32 "
        "verification with zero failures, yielding 100.0% stream health (HEALTHY)."
    )

    # TABLE III
    add_tbl_caption("III", "GSE Encapsulation & Protocol Analysis Results")
    tbl3 = doc.add_table(rows=10, cols=3)
    tbl3.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(tbl3)
    tbl3_headers = ["Metric Parameter", "Experimental Observed Value", "Category"]
    tbl3_data = [
        ["Total Ingested PDUs", "14 PDUs (9,324 Bytes file size)", "FACT"],
        ["Framing Compliance", "100.0% (14 / 14 PDUs Valid)", "FACT"],
        ["Total Payload Extracted", "8,764 Bytes", "FACT"],
        ["Mean PDU Length", "626.0 Bytes (Min: 45 B, Max: 1,444 B)", "STAT"],
        ["Fragmentation Breakdown", "6 Unfrag. (42.9%), 8 Frag. (57.1%)", "FACT"],
        ["Fragment Subtypes", "5 First, 0 Interm., 3 Last Frags.", "FACT"],
        ["Encapsulated Protocols", "GSE_EXT_NPA: 11 (100%), IPv4: 9", "FACT"],
        ["Addressing Labels", "6-Byte Label: 11, No Label: 3 PDUs", "FACT"],
        ["CRC-32 Checksums / F1 Health", "100.0% Pass (0 Failures) / 100.0% (HEALTHY)", "FACT / STAT"]
    ]
    for c_idx, h_text in enumerate(tbl3_headers):
        cell = tbl3.cell(0, c_idx)
        set_cell_background(cell, "F0F4F8")
        set_cell_margins(cell, 80, 80, 100, 100)
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(h_text)
        r.font.name = 'Times New Roman'
        r.font.size = Pt(8.5)
        r.font.bold = True
    for r_idx, row_data in enumerate(tbl3_data):
        for c_idx, val in enumerate(row_data):
            cell = tbl3.cell(r_idx + 1, c_idx)
            set_cell_margins(cell, 60, 60, 100, 100)
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER if c_idx == 2 else WD_ALIGN_PARAGRAPH.LEFT
            r = p.add_run(val)
            r.font.name = 'Times New Roman'
            r.font.size = Pt(8.5)

    add_sec_h2("C. DVB-S2 Baseband Frame Transmission Analysis")
    doc.add_paragraph(
        "Results for the baseband frame capture (dvb-s2_bb_example.pcap) are presented in Table IV. The file contained 4,309 frames totaling 2,349,376 bytes. "
        "All 4,309 frames passed 72-bit BBHeader CRC-8 verification (100.0% valid). MATYPE-1 analysis revealed that 100.0% of frames utilized Adaptive Coding & Modulation (ACM), "
        "99.98% utilized Single Input Stream (SIS, 4,308 frames), 0.02% utilized Multiple Input Stream (MIS, 1 frame), and 100.0% specified a roll-off factor of α = 0.35.\n"
        "Net user payload extracted was 1,958,826 bytes. Data Field Length (DFL), expressed in bits, ranged from 216 to 10,000 bits (mean: 3,636.72 bits). The DFL distribution "
        "exhibited strong modality: 3,698 frames (85.82% modal share) concentrated at exactly 2,992 bits, with a secondary peak at 8,304 bits (406 frames, 9.42%). "
        "Stream health evaluated to 100.0% (HEALTHY)."
    )

    # TABLE IV
    add_tbl_caption("IV", "DVB-S2 Baseband Frame Transmission Analysis")
    tbl4 = doc.add_table(rows=7, cols=4)
    tbl4.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(tbl4)
    tbl4_headers = ["Parameter Dimension", "Observed Value", "Distribution / Share", "Category"]
    tbl4_data = [
        ["Total Baseband Frames", "4,309 Frames (2,349,376 B)", "100.0% (4,309/4,309)", "FACT"],
        ["BBHeader CRC-8 Checks", "4,309 Passed / 0 Failed", "100.0% Valid Checksums", "FACT"],
        ["Stream Input Mode", "SIS: 4,308 / MIS: 1 Frame", "99.98% / 0.02%", "FACT"],
        ["Coding & Modulation", "Adaptive Coding & Mod. (ACM)", "100.0% (4,309/4,309)", "FACT"],
        ["Roll-off Factor (α)", "α = 0.35", "100.0% (4,309/4,309)", "FACT"],
        ["Data Field Payload / DFL", "1,958,826 Bytes / 216 to 10,000 Bits", "Mean: 454.59 B/frame; Mode: 2,992 b (85.8%)", "FACT / STAT"]
    ]
    for c_idx, h_text in enumerate(tbl4_headers):
        cell = tbl4.cell(0, c_idx)
        set_cell_background(cell, "F0F4F8")
        set_cell_margins(cell, 80, 80, 100, 100)
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(h_text)
        r.font.name = 'Times New Roman'
        r.font.size = Pt(8.5)
        r.font.bold = True
    for r_idx, row_data in enumerate(tbl4_data):
        for c_idx, val in enumerate(row_data):
            cell = tbl4.cell(r_idx + 1, c_idx)
            set_cell_margins(cell, 60, 60, 100, 100)
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER if c_idx in [2, 3] else WD_ALIGN_PARAGRAPH.LEFT
            r = p.add_run(val)
            r.font.name = 'Times New Roman'
            r.font.size = Pt(8.5)

    add_sec_h2("D. Unsupervised Isolation Forest Anomaly Analysis")
    doc.add_paragraph(
        "Anomaly detection results across all three formats are summarized in Table V. In all three streams, an elevated anomaly score consistently flagged the final window "
        "boundary (Window 90 in TS, Window 4 in GSE, Window 86 in BBFrame). This demonstrates the sensitivity of the Isolation Forest to container volume truncation caused by "
        "capture termination. Intermediate anomalies (e.g., TS Windows 1, 2, and 12) corresponded to localized statistical multiplexing bursts where single PIDs concentrated up to 98.5% of window bandwidth."
    )

    # TABLE V
    add_tbl_caption("V", "Isolation Forest Anomaly Detection Results")
    tbl5 = doc.add_table(rows=4, cols=5)
    tbl5.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(tbl5)
    tbl5_headers = ["Format", "Window Dimension", "Total Windows", "Anom. Windows", "Peak Anom. Score & Anomalous Indices"]
    tbl5_data = [
        ["MPEG-TS", "200 Pkts", "91", "5", "0.8576 [Windows 1, 2, 12, 88, 90]"],
        ["GSE", "3 PDUs", "5", "1", "0.5018 [Window 4]"],
        ["BBFrame", "50 Frms", "87", "5", "0.7406 [Windows 0, 83, 84, 85, 86]"]
    ]
    for c_idx, h_text in enumerate(tbl5_headers):
        cell = tbl5.cell(0, c_idx)
        set_cell_background(cell, "F0F4F8")
        set_cell_margins(cell, 80, 80, 100, 100)
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(h_text)
        r.font.name = 'Times New Roman'
        r.font.size = Pt(8.5)
        r.font.bold = True
    for r_idx, row_data in enumerate(tbl5_data):
        for c_idx, val in enumerate(row_data):
            cell = tbl5.cell(r_idx + 1, c_idx)
            set_cell_margins(cell, 60, 60, 100, 100)
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER if c_idx in [1, 2, 3] else WD_ALIGN_PARAGRAPH.LEFT
            r = p.add_run(val)
            r.font.name = 'Times New Roman'
            r.font.size = Pt(8.5)

    add_sec_h2("E. Cross-Format Stream Comparison Audit")
    doc.add_paragraph(
        "Table VI documents the differential comparison between MPEG-TS (sample.ts) and BBFrame (dvb-s2_bb_example.pcap). For comparable metrics, total_payload_bytes "
        "decreased from 3,267,305 B to 1,958,826 B (Δ_abs = -1,308,479.0 B, Δ_rel = -40.05%), classified as SUBSTANTIAL. The integrity_ratio evaluated to 1.0000 for both streams "
        "(Δ_rel = 0.00%, NEGLIGIBLE). Exactly nine non-comparable metrics were shielded by the semantic barrier with clear domain rationales."
    )

    # TABLE VI
    add_tbl_caption("VI", "Cross-Format Stream Comparison Audit (TS vs. BBFrame)")
    tbl6 = doc.add_table(rows=11, cols=5)
    tbl6.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(tbl6)
    tbl6_headers = ["Metric Identifier", "Semantic Status", "Stream A (MPEG-TS)", "Stream B (BBFrame)", "Relative Delta / Status"]
    tbl6_data = [
        ["total_payload_bytes", "Comparable", "3,267,305 Bytes", "1,958,826 Bytes", "-40.05% (SUBSTANTIAL)"],
        ["integrity_ratio", "Comparable", "1.0000", "1.0000", "0.00% (NEGLIGIBLE)"],
        ["total_units", "Shielded", "18,176 packets", "4,309 frames", "Incompatible Dimension"],
        ["valid_units", "Shielded", "18,176 packets", "4,309 frames", "Incompatible Dimension"],
        ["invalid_units", "Shielded", "0 packets", "0 frames", "Incompatible Dimension"],
        ["mean_payload_bytes", "Shielded", "179.76 B/packet", "454.59 B/frame", "Incompatible Container"],
        ["payload_ratio", "Shielded", "1.0000", "1.0000", "Divergent Formulation"],
        ["error_count", "Shielded", "0 errors", "0 errors", "Heterogeneous Failure Modes"],
        ["error_rate", "Shielded", "0.0000", "0.0000", "Heterogeneous Failure Modes"],
        ["entropy", "Shielded", "0.1361 bits", "0.0000 bits", "Distinct State Spaces"]
    ]
    for c_idx, h_text in enumerate(tbl6_headers):
        cell = tbl6.cell(0, c_idx)
        set_cell_background(cell, "F0F4F8")
        set_cell_margins(cell, 80, 80, 80, 80)
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(h_text)
        r.font.name = 'Times New Roman'
        r.font.size = Pt(8.5)
        r.font.bold = True
    for r_idx, row_data in enumerate(tbl6_data):
        for c_idx, val in enumerate(row_data):
            cell = tbl6.cell(r_idx + 1, c_idx)
            set_cell_margins(cell, 50, 50, 80, 80)
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER if c_idx in [1, 4] else WD_ALIGN_PARAGRAPH.LEFT
            r = p.add_run(val)
            r.font.name = 'Times New Roman'
            r.font.size = Pt(8.5)

    # SECTION VIII
    add_sec_h1("VIII. Software Verification and Testing")
    doc.add_paragraph(
        "System stability, regression integrity, and parsing accuracy are verified through an automated test suite executed via Python's standard unittest framework:\n"
        "python -m unittest discover -s tests -v\n"
        "Verification Outcome: 240 / 240 Tests Passing (100% Pass Rate) with 0 Failures and 0 Errors in 19.86s.\n"
        "• Backend Analytical Suite (207 Tests): Validates deterministic framing decoders (test_ts_parser.py, test_gse_parser.py, test_bbframe_parser.py), "
        "unified feature extraction (test_unified_features.py), F1 stream health (test_f1_health.py), F2 anomaly detection (test_anomaly.py), "
        "F3 pattern detection (test_patterns.py), F4 timeline generation (test_timeline.py), F5 anomaly explanations (test_explanation.py), "
        "F6 stream comparison (test_comparison.py), and F7 reporting (test_report.py).\n"
        "• Frontend Server & Integration Suite (33 Tests): Validates threaded HTTP server lifecycle, static asset delivery, MIME types, binary file upload staging, "
        "directory traversal guards, F6 state reset lifecycle, relative path multi-candidate resolution, content-aware GSE detection, corrupted TS diagnostic "
        "accounting, sequential stream replacement lifecycle, and semantically correct HTTP 400 invalid-file handling.\n"
        "Note on Epistemic Integrity: Passing 240/240 automated software tests constitutes rigorous software verification and regression integrity. "
        "It is explicitly not presented as machine learning classification accuracy."
    )

    # SECTION IX
    add_sec_h1("IX. Limitations and Domain Safety")
    doc.add_paragraph(
        "To maintain scientific integrity, Prototype limitations are documented:\n"
        "1) Unlabeled Operational Datasets: Due to the absence of public, ground-truth-labeled DVB-S2 anomaly datasets, machine learning models are evaluated via unsupervised isolation and synthetic perturbation, rather than supervised benchmark metrics (ROC-AUC).\n"
        "2) Post-Demodulator Scope: The application operates exclusively on digital receiver output bitstreams. It cannot diagnose analog RF physical-layer conditions (e.g., signal-to-noise ratio, carrier frequency offset, or transponder compression).\n"
        "3) ETSI TR 101 290 Scope: Health analysis evaluates selected Priority-1 indicators inspired by ETSI TR 101 290 principles; it does not claim formal certification across all Priority-2 and Priority-3 guidelines.\n"
        "4) Offline Spatial Windowing: Analysis is structured over discrete spatial unit windows rather than real-time continuous sliding windows.\n"
        "5) No Temporal Sequence Memory: The Isolation Forest treats each window independently; temporal sequence dependencies across successive windows are not modeled."
    )

    # SECTION X
    add_sec_h1("X. Conclusion and Future Work")
    doc.add_paragraph(
        "This paper has presented the design, implementation, and verification of PRJ_111, a specialized software application for analyzing "
        "multi-format DVB-S2 receiver output streams. By providing content-aware format detection and modular parsing across MPEG-TS, GSE, "
        "and DVB-S2 Baseband Frames, the system overcomes the structural fragmentation of single-format analyzers."
    )
    doc.add_paragraph(
        "The seven-feature analytical pipeline achieves deterministic stream health evaluation (F1), unsupervised Isolation Forest anomaly detection (F2), "
        "structural pattern and entropy analysis (F3), physical spatial activity timelines (F4), bounded Z-score diagnostic anomaly explanations (F5), "
        "semantically guarded stream comparisons (F6), and automated tripartite diagnostic reporting (F7). Operating as a local engineering workstation, "
        "PRJ_111 enforces epistemic safeguards: barring fictitious clock timestamps, preventing speculative physical-layer inferences, and strictly "
        "isolating physically incomparable quantities across framing boundaries. Validated across authoritative satellite captures with 240/240 passing "
        "automated tests, PRJ_111 establishes a robust, extensible prototype for satellite ground station monitoring, telecommunications education, "
        "and broadcast stream verification."
    )
    doc.add_paragraph(
        "Future research directions include:\n"
        "1) Deep Sequential Architectures: Investigating bidirectional LSTM and temporal transformer networks to capture long-range sequential correlations across broadcast multiplexes.\n"
        "2) Software-Defined Radio Demodulation: Integrating an upstream GNU Radio or gr-dvbs2 physical-layer front-end to capture simultaneous RF constellation metrics (EVM, MER, SNR) alongside digital framing telemetry.\n"
        "3) Hardware Acceleration: Exploring offloading of PDU and packet header parsing to FPGA or eBPF kernel bypass engines to support high-throughput transponder aggregation.\n"
        "4) Benchmark Dataset Publication: Curating and releasing an open, expert-annotated multi-format DVB-S2 anomaly dataset for the satellite communications research community."
    )

    # ACKNOWLEDGMENT
    add_sec_h1("Acknowledgment")
    doc.add_paragraph(
        "The authors express their sincere gratitude to the Department of Computer Science and Engineering, Presidency University, Bengaluru, "
        "for providing the laboratory facilities and computing infrastructure necessary to conduct this research. The authors extend special "
        "thanks to our project guide, Irfan Rajab Bhat, Assistant Professor, for his technical guidance, insightful critiques, and support "
        "throughout the development and verification of this project."
    )

    # REFERENCES
    add_sec_h1("References")
    
    references_data = [
        "[1] “Digital Video Broadcasting (DVB); Second Generation Framing Structure, Channel Coding and Modulation Systems for Broadcasting, Interactive Services, News Gathering and Other Broadband Satellite Applications; Part 1: DVB-S2,” no. ETSI EN 302 307-1 V1.4.1. Sophia Antipolis, France, 2014.",
        "[2] A. Morello and V. Mignone, “DVB-S2: The Second Generation Standard for Satellite Broadband Services,” Proceedings of the IEEE, vol. 94, no. 1, pp. 210–227, 2006.",
        "[3] “Information Technology — Generic Coding of Moving Pictures and Associated Audio Information — Part 1: Systems (MPEG-2 Transport Stream),” no. ISO/IEC 13818-1:2022. Geneva, Switzerland, 2022.",
        "[4] “Digital Video Broadcasting (DVB); Generic Stream Encapsulation (GSE); Part 1: Protocol,” no. ETSI TS 102 606-1 V1.2.1. Sophia Antipolis, France, 2014.",
        "[5] P. L. Luisi, A. B. Sampaio, and C. A. C. Marcondes, “Empirical Evaluation of Digital Video Broadcasting Systems and Transport Stream Analysis,” IEEE Transactions on Broadcasting, vol. 66, no. 2, pp. 431–444, 2020.",
        "[6] D. Minoli, Innovations in Satellite Communications and the Global Information Infrastructure. Hoboken, NJ, USA: John Wiley & Sons, 2015.",
        "[7] E. Casini, R. De Gaudenzi, and A. Ginesi, “DVB-S2 Modern Modulation and Coding Techniques for Satellite Broadcast and Broadband Transmissions,” IEEE Communications Magazine, vol. 42, no. 11, pp. 146–156, 2004.",
        "[8] B. Sklar, Digital Communications: Fundamentals and Applications, 2nd ed. Upper Saddle River, NJ, USA: Prentice Hall PTR, 2001.",
        "[9] G. Fairhurst and B. Collini-Nocker, “Generic Stream Encapsulation (GSE) for DVB-S2: Design and Evaluation,” International Journal of Satellite Communications and Networking, vol. 28, no. 5–6, pp. 287–305, 2010.",
        "[10] G. Fairhurst and B. Collini-Nocker, “Unidirectional Lightweight Encapsulation (ULE) for Transmission of IP Datagrams over an MPEG-2 Transport Stream,” RFC 4326, Dec. 2005.",
        "[11] “Digital Video Broadcasting (DVB); Measurement Guidelines for DVB Systems,” no. ETSI TR 101 290 V1.4.1. Sophia Antipolis, France, 2020.",
        "[12] “Digital Video Broadcasting (DVB); Specification for Service Information (SI) in DVB Systems,” no. ETSI EN 300 468 V1.17.1. Sophia Antipolis, France, 2021.",
        "[13] V. Chandola, A. Banerjee, and V. Kumar, “Anomaly Detection: A Survey,” ACM Computing Surveys, vol. 41, no. 3, pp. 1–58, 2009.",
        "[14] M. A. F. Pimentel, D. A. Clifton, L. Clifton, and L. Tarassenko, “A Review of Novelty Detection,” Signal Processing, vol. 99, pp. 215–249, 2014.",
        "[15] F. T. Liu, K. M. Ting, and Z.-H. Zhou, “Isolation Forest,” in Proceedings of the 8th IEEE International Conference on Data Mining (ICDM), Pisa, Italy, 2008, pp. 413–422.",
        "[16] F. T. Liu, K. M. Ting, and Z.-H. Zhou, “Isolation-Based Anomaly Detection,” ACM Transactions on Knowledge Discovery from Data, vol. 6, no. 1, pp. 1–39, 2012.",
        "[17] R. S. Baggio, P. R. L. Gondim, and F. L. L. Mendonca, “Network Traffic Anomaly Detection Using Unsupervised Learning Models: A Comparative Study,” IEEE Access, vol. 9, pp. 15982–15998, 2021.",
        "[18] D. Arthur and S. Vassilvitskii, “k-means++: The Advantages of Careful Seeding,” in Proceedings of the 18th Annual ACM-SIAM Symposium on Discrete Algorithms (SODA), New Orleans, LA, USA, 2007, pp. 1027–1035.",
        "[19] M. Ester, H.-P. Kriegel, J. Sander, and X. Xu, “A Density-Based Algorithm for Discovering Clusters in Large Spatial Databases with Noise,” in Proceedings of the 2nd International Conference on Knowledge Discovery and Data Mining (KDD), Portland, OR, USA, 1996, pp. 226–231.",
        "[20] C. E. Shannon, “A Mathematical Theory of Communication,” Bell System Technical Journal, vol. 27, no. 3, pp. 379–423, 1948."
    ]

    for ref in references_data:
        p_ref = doc.add_paragraph()
        p_ref.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p_ref.paragraph_format.left_indent = Inches(0.3)
        p_ref.paragraph_format.first_line_indent = Inches(-0.3)
        p_ref.paragraph_format.space_after = Pt(4)
        r = p_ref.add_run(ref)
        r.font.name = 'Times New Roman'
        r.font.size = Pt(8.5)

    output_path = "PRJ_111_Research_Paper_Final.docx"
    doc.save(output_path)
    print(f"Successfully generated: {output_path} (Size: {os.path.getsize(output_path)} bytes)")

if __name__ == "__main__":
    build_paper_docx()
