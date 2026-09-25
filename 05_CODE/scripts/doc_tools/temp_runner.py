"""
build_ieee_docx.py
Generates the authoritative PRJ_111 IEEE-style TWO-COLUMN Microsoft Word (.docx) document.
Layout:
- Page setup: US Letter, 0.75 in margins.
- Title & Authors: 1-column section spanning full page width.
  Authors: ONLY Sk Samad, Y Vengala Rao, C Rakeshwar (Presidency University).
- Abstract & Index Terms + Sections I-III: 2-column continuous section.
- Fig. 1 (Architecture Pipeline): 1-column continuous section.
- Sections III-A through V-G + Single-column Figs (2-6) + Tables I + Equations (1)-(9): 2-column continuous section.
- Table II (MPEG-TS Health, 8 cols): 1-column continuous section.
- Sections VI through VII-D + Tables III, IV, V: 2-column continuous section.
- Table VI (Comparison Audit, 5 cols): 1-column continuous section.
- Sections VII-E through X + Acknowledgment + References [1]-[20]: 2-column continuous section.
"""

import os
import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls, qn

def set_section_cols(sec, num=2, space=360):
    sectPr = sec._sectPr
    for c in sectPr.xpath('./w:cols'):
        sectPr.remove(c)
    sectPr.append(parse_xml(f'<w:cols {nsdecls("w")} w:num="{num}" w:space="{space}"/>'))

def set_cell_background(cell, fill_hex):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=60, bottom=60, left=80, right=80):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = parse_xml(f'<w:tcMar {nsdecls("w")}><w:top w:w="{top}" w:type="dxa"/><w:bottom w:w="{bottom}" w:type="dxa"/><w:left w:w="{left}" w:type="dxa"/><w:right w:w="{right}" w:type="dxa"/></w:tcMar>')
    tcPr.append(tcMar)

def set_ieee_table_borders(table, border_color="000000"):
    tblPr = table._tbl.tblPr
    borders = parse_xml(
        f'<w:tblBorders {nsdecls("w")}>'
        f'<w:top w:val="single" w:sz="8" w:space="0" w:color="{border_color}"/>'
        f'<w:bottom w:val="single" w:sz="8" w:space="0" w:color="{border_color}"/>'
        f'<w:insideH w:val="single" w:sz="4" w:space="0" w:color="CCCCCC"/>'
        f'<w:insideV w:val="none"/>'
        f'<w:left w:val="none"/>'
        f'<w:right w:val="none"/>'
        f'</w:tblBorders>'
    )
    tblPr.append(borders)

def add_omml_equation(doc, math_inner_xml, eq_num, col_width_in=3.3):
    tbl = doc.add_table(rows=1, cols=2)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl.autofit = False
    w_math = col_width_in - 0.45
    w_num = 0.45
    tbl.columns[0].width = Inches(w_math)
    tbl.columns[1].width = Inches(w_num)
    
    tblPr = tbl._tbl.tblPr
    tblBorders = parse_xml(f'<w:tblBorders {nsdecls("w")}><w:top w:val="none"/><w:bottom w:val="none"/><w:insideH w:val="none"/><w:insideV w:val="none"/><w:left w:val="none"/><w:right w:val="none"/></w:tblBorders>')
    tblPr.append(tblBorders)
    
    cell_eq = tbl.cell(0, 0)
    set_cell_margins(cell_eq, 30, 30, 0, 0)
    p_eq = cell_eq.paragraphs[0]
    p_eq.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_eq.paragraph_format.space_before = Pt(2)
    p_eq.paragraph_format.space_after = Pt(2)
    
    omml_xml = f'<m:oMathPara {nsdecls("m")}><m:oMath>{math_inner_xml}</m:oMath></m:oMathPara>'
    p_eq._p.append(parse_xml(omml_xml))
    
    cell_num = tbl.cell(0, 1)
    set_cell_margins(cell_num, 30, 30, 0, 0)
    p_num = cell_num.paragraphs[0]
    p_num.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    p_num.paragraph_format.space_before = Pt(2)
    p_num.paragraph_format.space_after = Pt(2)
    r = p_num.add_run(f"({eq_num})")
    r.font.name = "Times New Roman"
    r.font.size = Pt(9.5)

def build_paper():
    doc = Document()
    
    # ----------------------------------------------------
    # SECTION 1: Full-Width Title & Authors (1 Column)
    # ----------------------------------------------------
    sec1 = doc.sections[0]
    sec1.page_width = Inches(8.5)
    sec1.page_height = Inches(11.0)
    sec1.top_margin = Inches(0.75)
    sec1.bottom_margin = Inches(0.75)
    sec1.left_margin = Inches(0.75)
    sec1.right_margin = Inches(0.75)
    set_section_cols(sec1, num=1)

    # Base Normal Style
    normal_style = doc.styles['Normal']
    normal_font = normal_style.font
    normal_font.name = 'Times New Roman'
    normal_font.size = Pt(10)
    normal_font.color.rgb = RGBColor(0x00, 0x00, 0x00)
    normal_style.paragraph_format.line_spacing = 1.05
    normal_style.paragraph_format.space_after = Pt(3)
    normal_style.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY

    # Title
    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title.paragraph_format.space_before = Pt(0)
    p_title.paragraph_format.space_after = Pt(12)
    r_title = p_title.add_run("Development of a Multi-Format DVB-S2 Receiver Output\nStream Analyzer with Anomaly Detection and Diagnostic Reporting")
    r_title.font.name = 'Times New Roman'
    r_title.font.size = Pt(17)
    r_title.font.bold = True

    # Author Table (3 Columns across 7.0 inches)
    author_tbl = doc.add_table(rows=1, cols=3)
    author_tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    author_tbl.autofit = False
    tblPr = author_tbl._tbl.tblPr
    tblBorders = parse_xml(f'<w:tblBorders {nsdecls("w")}><w:top w:val="none"/><w:bottom w:val="none"/><w:insideH w:val="none"/><w:insideV w:val="none"/><w:left w:val="none"/><w:right w:val="none"/></w:tblBorders>')
    tblPr.append(tblBorders)

    col_w = Inches(2.33)
    for c in author_tbl.columns:
        c.width = col_w

    authors_data = [
        ("Sk Samad", "Roll No: 20231COM0031", "Dept. of Computer Science & Engineering\nPresidency University\nBengaluru, India"),
        ("Y Vengala Rao", "Roll No: 20231COM0001", "Dept. of Computer Science & Engineering\nPresidency University\nBengaluru, India"),
        ("C Rakeshwar", "Roll No: 20231COM0008", "Dept. of Computer Science & Engineering\nPresidency University\nBengaluru, India")
    ]

    for i, (name, roll, affil) in enumerate(authors_data):
        cell = author_tbl.cell(0, i)
        cell.width = col_w
        set_cell_margins(cell, 0, 0, 40, 40)
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_after = Pt(2)
        
        rn = p.add_run(name + "\n")
        rn.font.name = 'Times New Roman'
        rn.font.size = Pt(11)
        rn.font.bold = True
        
        rr = p.add_run(roll + "\n")
        rr.font.name = 'Times New Roman'
        rr.font.size = Pt(9.5)
        
        ra = p.add_run(affil)
        ra.font.name = 'Times New Roman'
        ra.font.size = Pt(9)
        ra.font.italic = True

    p_div = doc.add_paragraph()
    p_div.paragraph_format.space_before = Pt(6)
    p_div.paragraph_format.space_after = Pt(0)

    # ----------------------------------------------------
    # Helper functions for Two-Column Body Content
    # ----------------------------------------------------
    def add_sec_h1(title):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(9)
        p.paragraph_format.space_after = Pt(3)
        p.paragraph_format.first_line_indent = Inches(0)
        r = p.add_run(title.upper())
        r.font.name = 'Times New Roman'
        r.font.size = Pt(10)
        r.font.bold = True
        return p

    def add_sec_h2(title):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p.paragraph_format.space_before = Pt(7)
        p.paragraph_format.space_after = Pt(2)
        p.paragraph_format.first_line_indent = Inches(0)
        r = p.add_run(title)
        r.font.name = 'Times New Roman'
        r.font.size = Pt(10)
        r.font.bold = True
        r.font.italic = True
        return p

    def add_body_p(text, indent=True):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p.paragraph_format.space_after = Pt(3)
        if indent:
            p.paragraph_format.first_line_indent = Inches(0.18)
        else:
            p.paragraph_format.first_line_indent = Inches(0)
        r = p.add_run(text)
        r.font.name = 'Times New Roman'
        r.font.size = Pt(10)
        return p

    def add_fig_caption(num, title):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(2)
        p.paragraph_format.space_after = Pt(7)
        p.paragraph_format.first_line_indent = Inches(0)
        r_lbl = p.add_run(f"Fig. {num}. ")
        r_lbl.font.name = 'Times New Roman'
        r_lbl.font.size = Pt(8.5)
        r_lbl.font.bold = True
        r_txt = p.add_run(title)
        r_txt.font.name = 'Times New Roman'
        r_txt.font.size = Pt(8.5)
        return p

    def add_tbl_caption(num_str, title):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(8)
        p.paragraph_format.space_after = Pt(2)
        p.paragraph_format.first_line_indent = Inches(0)
        r1 = p.add_run(f"TABLE {num_str}\n")
        r1.font.name = 'Times New Roman'
        r1.font.size = Pt(8.5)
        r1.font.bold = True
        r2 = p.add_run(title.upper())
        r2.font.name = 'Times New Roman'
        r2.font.size = Pt(8.5)
        r2.font.bold = True
        return p

    # ----------------------------------------------------
    # SECTION 2: Continuous Break -> TWO COLUMNS
    # Abstract, Index Terms, Sections I, II, III
    # ----------------------------------------------------
    sec2 = doc.add_section(WD_SECTION.CONTINUOUS)
    set_section_cols(sec2, num=2, space=360)

    # Abstract
    p_abs = doc.add_paragraph()
    p_abs.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p_abs.paragraph_format.space_after = Pt(4)
    p_abs.paragraph_format.first_line_indent = Inches(0)
    
    r_ah = p_abs.add_run("Abstract—")
    r_ah.font.name = 'Times New Roman'
    r_ah.font.size = Pt(9)
    r_ah.font.bold = True
    r_ah.font.italic = True
    
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
    r_at = p_abs.add_run(abs_text)
    r_at.font.name = 'Times New Roman'
    r_at.font.size = Pt(9)

    # Index Terms
    p_idx = doc.add_paragraph()
    p_idx.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p_idx.paragraph_format.space_after = Pt(8)
    p_idx.paragraph_format.first_line_indent = Inches(0)
    
    r_ih = p_idx.add_run("Index Terms—")
    r_ih.font.name = 'Times New Roman'
    r_ih.font.size = Pt(9)
    r_ih.font.bold = True
    r_ih.font.italic = True
    
    r_it = p_idx.add_run("Anomaly detection, Baseband frame, Digital video broadcasting, DVB-S2, Feature extraction, Generic stream encapsulation, Isolation Forest, MPEG transport stream, Receiver output analysis, Stream analysis.")
    r_it.font.name = 'Times New Roman'
    r_it.font.size = Pt(9)
    r_it.font.italic = True

    # Section I
    add_sec_h1("I. Introduction")
    add_body_p(
        "The Second Generation Digital Video Broadcasting via Satellite standard (DVB-S2, ETSI EN 302 307-1) "
        "represents the foundational physical and framing specification for modern satellite telecommunications [1]. "
        "Operating downstream of the satellite low-noise block downconverter (LNB) and intermediate-frequency (IF) tuner, "
        "the satellite receiver demodulator performs carrier acquisition, matched filtering, forward error correction (FEC) "
        "decoding using coupled Low-Density Parity-Check (LDPC) and Bose-Chaudhuri-Hocquenghem (BCH) codes, and baseband "
        "deframing [2]. The resulting post-demodulator digital output stream forms the critical boundary between "
        "satellite physical-layer transmission and terrestrial networking appliances."
    )
    add_body_p(
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
    add_body_p(
        "Analyzing receiver output streams is essential for ground station commissioning, transponder capacity verification, "
        "stream integrity assessment, and transmission debugging. However, analyzing these heterogeneous representations "
        "using conventional tools presents operational limitations [5]. Generic packet analyzers (such as Wireshark) "
        "treat captures as Ethernet frames, requiring specialized external dissectors that lack native support for raw "
        "concatenated transport streams or raw baseband frame telemetry [6]. Conversely, dedicated broadcast hardware "
        "instruments are tailored primarily to MPEG-TS, providing limited native support for modern DVB-S2 baseband frames "
        "or GSE IP encapsulation [5]."
    )
    add_body_p(
        "Furthermore, existing analysis tools suffer from three fundamental engineering deficiencies: "
        "1) Framing Heterogeneity and Parser Brittleness: Digital captures arrive as unindexed raw binary bitstreams (.ts, .gse, .bin, .pcap). "
        "Naive file-extension parsers misidentify formats, while streaming parsers without robust synchronization recovery fail when encountering bit errors. "
        "2) Lack of Cross-Format Telemetry: Comparing packet counts, PDU counts, and baseband frame counts directly creates false equivalence, "
        "misleading ground station operators by comparing metrics with incompatible physical dimensions. "
        "3) Epistemic Over-Claiming in Stream Telemetry: Many commercial monitoring tools calculate synthetic clock timestamps or fictitious "
        "Megabits-per-second (Mbps) throughputs in offline files where no receiver clock telemetry exists, or assert speculative physical-layer "
        "causal inferences (e.g., attributing a continuity counter error to 'rain fade' without demodulator signal-to-noise ratio measurements)."
    )
    add_body_p(
        "To resolve these challenges, this paper presents PRJ_111, a specialized, modular software application engineered for "
        "multi-format DVB-S2 receiver output stream analysis. PRJ_111 establishes an integrated seven-feature analytical pipeline (F1–F7) "
        "that performs content-aware format sniffer ingestion, deterministic framing parsing, unified feature extraction, rule-based stream "
        "health analysis (F1), unsupervised Isolation Forest anomaly detection (F2), structural pattern and entropy analysis (F3), physical "
        "spatial activity timelines (F4), bounded Z-score diagnostic anomaly explanations (F5), semantically guarded stream comparisons (F6), "
        "and automated multi-format diagnostic report generation (F7)."
    )
    add_body_p(
        "The remainder of this paper is organized as follows: Section II reviews related literature. Section III presents the system architecture. "
        "Section IV details multi-format parsing. Section V elaborates the seven-feature analytical pipeline. Section VI outlines the experimental "
        "setup and datasets. Section VII analyzes empirical results. Section VIII details automated software verification. Section IX presents "
        "limitations and domain-safety considerations. Section X concludes the paper with directions for future work."
    )

    # Section II
    add_sec_h1("II. Related Work")
    add_body_p(
        "The technical foundation of PRJ_111 synthesizes international telecommunications standards, satellite protocol engineering, "
        "unsupervised machine learning, and empirical stream monitoring."
    )
    add_sec_h2("A. DVB-S2 Framing and Encapsulation Protocols")
    add_body_p(
        "The DVB-S2 standard (ETSI EN 302 307-1) defines framing, channel coding, and modulation for satellite communications, establishing "
        "Adaptive Coding and Modulation (ACM) and Native Baseband Framing [1]. Morello and Mignone [2] analyzed the physical layer mechanisms "
        "of DVB-S2, demonstrating how variable-length user packets are encapsulated into baseband frames protected by inner LDPC and outer "
        "BCH codes. Casini et al. [7] analyzed modulation constellations ranging from QPSK to 32-APSK, detailing the role of the 80-bit Baseband "
        "Header (BBHeader), Roll-Off factors (α ∈ {0.20, 0.25, 0.35}), and Data Field Length (DFL) bit allocation. Sklar [8] provided the "
        "foundational framework for digital modulation, channel coding limits, and baseband framing boundaries in digital communication channels."
    )
    add_body_p(
        "For network layer transport, Fairhurst and Collini-Nocker [9] formulated Generic Stream Encapsulation (ETSI TS 102 606-1) [4] to replace "
        "legacy Multi-Protocol Encapsulation (MPE over MPEG-TS) and Unidirectional Lightweight Encapsulation (ULE, RFC 4326) [10]. GSE defines "
        "variable-size protocol data units carrying native IP datagrams with fragment-level CRC-32 protection, eliminating transport stream "
        "packing overhead. Digital television distribution continues to rely on the MPEG-2 Transport Stream (ISO/IEC 13818-1) [3]. Operational "
        "measurement guidelines for DVB broadcast systems are standardized in ETSI TR 101 290 [11], which defines Priority-1 stream parameters: "
        "loss of synchronization, Transport Error Indicator (TEI) assertions, and Continuity Counter (CC) errors. DVB Service Information (SI) "
        "standards are specified in ETSI EN 300 468 [12]."
    )
    add_sec_h2("B. Broadcast Stream Monitoring and Protocol Inspection")
    add_body_p(
        "Luisi et al. [5] evaluated digital video broadcast stream monitoring techniques, demonstrating that while hardware TS analyzers "
        "reliably evaluate ETSI TR 101 290 Priority-1 errors, they lack native decoding for modern multi-protocol IP encapsulations (GSE and "
        "BBFrames) emitted by satellite broadband receivers. Minoli [6] surveyed network packet inspection tools, noting that packet sniffers "
        "treat raw digital bitstreams as unstructured payloads unless encapsulated in network capture wrappers (such as PCAP). PRJ_111 resolves "
        "these limitations by providing native, modular parsers for MPEG-TS, GSE, and BBFrames directly from raw receiver bitstreams."
    )
    add_sec_h2("C. Unsupervised Anomaly Detection in Telecommunications")
    add_body_p(
        "Anomaly detection in streaming telemetry has been surveyed by Chandola et al. [13] and Pimentel et al. [14]. Traditional statistical "
        "process control relies on static thresholds, which present difficulties in multiplexed channels where bitrates fluctuate dynamically "
        "with statistical multiplexing. Supervised classification approaches require extensive ground-truth labeled anomaly datasets [13]. "
        "In operational DVB-S2 receiver monitoring, labeled anomalous bitstreams are rarely available; captured receiver data reflects "
        "proprietary commercial broadcasts, encrypted carrier feeds, or transient operational anomalies."
    )
    add_body_p(
        "To address unlabeled streaming data, Liu et al. [15], [16] introduced the Isolation Forest algorithm. Isolation Forest isolates anomalies "
        "explicitly rather than profiling normal instances, constructing ensembles of random isolation trees (iTrees). Because anomalies "
        "possess distinct feature attributes, they are isolated closer to tree roots, resulting in shorter average path lengths [15]. Baggio et al. "
        "[17] evaluated unsupervised machine learning models for network traffic anomaly detection, demonstrating that Isolation Forest achieves "
        "superior computational efficiency (O(n log n) training complexity) and robust outlier detection in streaming feature spaces compared to "
        "distance-based models such as k-means++ [18] or density-based clustering such as DBSCAN [19]. Shannon [20] established the mathematical "
        "foundation of information entropy, utilized in this work to evaluate PID multiplex distribution concentration. PRJ_111 adapts Isolation "
        "Forest to DVB-S2 telemetry, executing format-isolated, spatial-window anomaly detection with calibrated logistic decision boundaries."
    )

    # Section III
    add_sec_h1("III. System Architecture and Workstation Design")
    add_body_p(
        "The architecture of PRJ_111 is illustrated in Fig. 1. The system is structured as a six-stage pipeline that ingests raw post-demodulator "
        "digital receiver output, processes framing syntax, extracts unified features, executes analytical engines (F1–F3), generates spatial "
        "timeline telemetry (F4), diagnoses deviations (F5), evaluates dual-stream differentials (F6), and synthesizes multi-format reports (F7) "
        "through a standalone engineering workstation interface."
    )

    # ----------------------------------------------------
    # SECTION 3: Continuous Break -> 1 COLUMN (Full-Width Fig. 1)
    # ----------------------------------------------------
    sec3 = doc.add_section(WD_SECTION.CONTINUOUS)
    set_section_cols(sec3, num=1)

    fig1_path = "paper_assets/architecture_diagram.png"
    if os.path.exists(fig1_path):
        p_img1 = doc.add_paragraph()
        p_img1.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img1.paragraph_format.space_before = Pt(6)
        p_img1.paragraph_format.space_after = Pt(2)
        doc.add_picture(fig1_path, width=Inches(6.6))
        add_fig_caption(1, "End-to-End Architectural Pipeline of the PRJ_111 DVB-S2 Receiver Output Stream Analyzer (Stages 1 through 6).")

    # ----------------------------------------------------
    # SECTION 4: Continuous Break -> TWO COLUMNS
    # Section III-A, Fig 2, Section IV, Table I, Section V (Eq 1-9, Figs 3-6)
    # ----------------------------------------------------
    sec4 = doc.add_section(WD_SECTION.CONTINUOUS)
    set_section_cols(sec4, num=2, space=360)

    add_sec_h2("A. Ingestion and Local Workstation Architecture")
    add_body_p(
        "PRJ_111 is implemented in Python 3.12 as a local engineering workstation with zero external cloud or proprietary licensing dependencies:\n"
        "• Backend Core: Pure Python modular architecture (dvbs2_analyzer/ingestion/, parsers/, features/, analysis/).\n"
        "• Machine Learning Layer: Scikit-learn (IsolationForest) coupled with NumPy and SciPy for numerical vector operations.\n"
        "• HTTP Gateway: Multi-threaded native Python HTTP server (ThreadingHTTPServer) exposing a RESTful JSON API (/api/status, /api/analyze, /api/compare, /api/upload, /api/export).\n"
        "• Frontend Workstation: Single-Page Application (SPA) built with vanilla HTML5, CSS3, and ES6 JavaScript. Visualizations are rendered offline using vendored Chart.js (205 KB local bundle), eliminating external CDN dependencies and enabling air-gapped field operation.\n"
        "• Local Staging Security: Direct browser file uploads are staged locally under 05_CODE/uploads/ with alphanumeric token sanitization and directory traversal prevention (os.path.commonpath)."
    )

    # Fig. 2 (Single column)
    fig2_path = "paper_assets/fig_dashboard_analyzed.png"
    if os.path.exists(fig2_path):
        p_img2 = doc.add_paragraph()
        p_img2.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img2.paragraph_format.space_before = Pt(6)
        p_img2.paragraph_format.space_after = Pt(2)
        doc.add_picture(fig2_path, width=Inches(3.3))
        add_fig_caption(2, "PRJ_111 Engineering Workstation active analysis dashboard evaluating an off-air MPEG-TS capture (sample.ts).")

    # Section IV
    add_sec_h1("IV. Multi-Format Stream Processing")
    add_body_p(
        "The parsing layer operates directly on raw binary stream captures, providing modular decoders tailored to each standard. "
        "Format selection is governed by a content-aware format sniffer that evaluates synchronization bytes, transport error flags, "
        "GSE headers, and BBHeader CRC-8 checksums."
    )
    add_sec_h2("A. MPEG-2 Transport Stream (MPEG-TS) Processing")
    add_body_p(
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
    add_body_p(
        "The GSE parser decodes variable-size protocol data units adhering to ETSI TS 102 606-1 [4]:\n"
        "• Start/End Flags (S, E): 2 bits defining PDU fragmentation. S=1, E=1 indicates an unfragmented PDU; S=1, E=0 indicates the first fragment; S=0, E=0 intermediate fragments; S=0, E=1 the last fragment.\n"
        "• GSE Length Field Specification: In ETSI TS 102 606-1, the GSE Length field is a 12-bit binary field encoding integer values from 0 to 4,095 (2^12 - 1 = 4095). It explicitly indicates the length in octets of the GSE payload and optional fields following the 2-byte GSE base header. Therefore, the maximum representable encapsulated payload is 4,095 bytes, and including the 2-byte base header, the maximum theoretical total PDU length is 4,097 bytes. In our implementation and in the captured validation dataset, all PDUs satisfy this constraint, with the maximum observed PDU length being 1,444 bytes.\n"
        "• Protocol Type: 16-bit EtherType identifier (e.g., 0x0800 for IPv4, 0x86DD for IPv6) or GSE extension header type (GSE_EXT_NPA).\n"
        "• Label Type: 2 bits specifying 6-byte (LABEL_6B), 3-byte (LABEL_3B), or label-less (LABEL_NONE) addressing.\n"
        "• Fragment ID & Total Length: Present in fragmented PDUs to facilitate payload reassembly.\n"
        "• CRC-32 Verification: 32-bit CRC polynomial calculated over the PDU payload and headers for complete PDUs and last fragments."
    )
    add_sec_h2("C. DVB-S2 Baseband Frame (BBFrame) Processing")
    add_body_p(
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

    # Table I (Single Column, width 3.3 in)
    add_tbl_caption("I", "Supported Input Format Characteristics")
    tbl1 = doc.add_table(rows=4, cols=5)
    tbl1.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl1.autofit = False
    set_ieee_table_borders(tbl1)
    col1_widths = [Inches(0.65), Inches(0.65), Inches(0.50), Inches(0.75), Inches(0.75)]
    tbl1_headers = ["Format", "Structure", "Header", "Container Dim.", "Checksum"]
    tbl1_data = [
        ["MPEG-TS", "Fixed Pkt", "4 Bytes", "188 Bytes", "Cont. Ctr (4b)"],
        ["GSE", "Var. PDU", "2–8 Bytes", "45–1,444 B", "CRC-32 (32b)"],
        ["BBFrame", "Fixed Frm", "10 Bytes", "216–10k b", "CRC-8 (8b)"]
    ]
    for c_idx, w in enumerate(col1_widths):
        tbl1.columns[c_idx].width = w
    for c_idx, h_text in enumerate(tbl1_headers):
        cell = tbl1.cell(0, c_idx)
        cell.width = col1_widths[c_idx]
        set_cell_background(cell, "F0F4F8")
        set_cell_margins(cell, 40, 40, 40, 40)
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(h_text)
        r.font.name = 'Times New Roman'
        r.font.size = Pt(7.5)
        r.font.bold = True
    for r_idx, row_data in enumerate(tbl1_data):
        for c_idx, val in enumerate(row_data):
            cell = tbl1.cell(r_idx + 1, c_idx)
            cell.width = col1_widths[c_idx]
            set_cell_margins(cell, 30, 30, 40, 40)
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER if c_idx != 0 else WD_ALIGN_PARAGRAPH.LEFT
            r = p.add_run(val)
            r.font.name = 'Times New Roman'
            r.font.size = Pt(7.5)

    # Section V
    add_sec_h1("V. Feature Engineering and Analytical Pipeline")
    add_body_p(
        "To analyze streams across disparate formats without creating invalid semantic conflations, PRJ_111 establishes "
        "the UnifiedStreamFeatureSet architecture. Telemetry is bifurcated into physical invariants (CommonMetrics) and native "
        "format-specific metrics (TSMetrics, GSEMetrics, BBFrameMetrics)."
    )
    add_sec_h2("A. Feature F1: Stream Health Analysis")
    add_body_p(
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
    add_body_p("The health score of window W_i is evaluated by:")
    
    # Eq (1)
    eq1_xml = (
        '<m:r><m:t>H(</m:t></m:r>'
        '<m:sSub><m:sSubPr/><m:e><m:r><m:t>W</m:t></m:r></m:e><m:sub><m:r><m:t>i</m:t></m:r></m:sub></m:sSub>'
        '<m:r><m:t>) = max(0.0, 100.0 + ∑ ΔH)</m:t></m:r>'
    )
    add_omml_equation(doc, eq1_xml, 1)

    add_body_p("The overall stream health score H is the arithmetic mean across all N evaluated spatial windows:")
    
    # Eq (2)
    eq2_xml = (
        '<m:r><m:t>H = </m:t></m:r>'
        '<m:f><m:fPr/><m:num><m:r><m:t>1</m:t></m:r></m:num><m:den><m:r><m:t>N</m:t></m:r></m:den></m:f>'
        '<m:sSubSup><m:sSubSupPr/><m:e><m:r><m:t>∑</m:t></m:r></m:e><m:sub><m:r><m:t>i=1</m:t></m:r></m:sub><m:sup><m:r><m:t>N</m:t></m:r></m:sup></m:sSubSup>'
        '<m:r><m:t> H(</m:t></m:r>'
        '<m:sSub><m:sSubPr/><m:e><m:r><m:t>W</m:t></m:r></m:e><m:sub><m:r><m:t>i</m:t></m:r></m:sub></m:sSub>'
        '<m:r><m:t>)</m:t></m:r>'
    )
    add_omml_equation(doc, eq2_xml, 2)

    add_body_p(
        "Streams are categorized into operational states:\n"
        "• HEALTHY: H ≥ 99.0%\n"
        "• DEGRADED / WARNING: 80.0% ≤ H < 99.0%\n"
        "• CRITICAL: H < 80.0%"
    )

    add_sec_h2("B. Feature F2: AI-Based Anomaly Detection")
    add_body_p(
        "Feature F2 implements unsupervised anomaly detection across rolling spatial windows using the Isolation Forest algorithm [15] "
        "through Scikit-learn. Given a spatial window W_i containing K units (K = 200 for TS, K = 3 for GSE, K = 50 for BBFrame), an m-dimensional "
        "feature vector x_i ∈ R^m is extracted, capturing payload volume, integrity ratio, error rate, entropy, unit size variance, and format-specific telemetry."
    )
    add_body_p(
        "The anomaly detector instantiates an ensemble of T = 100 isolation trees (n_estimators=100, contamination=0.05, random_state=42). "
        "The raw decision output d(x) ∈ R is computed using Scikit-learn's decision_function, where negative values designate outliers and "
        "positive values designate inliers. To map this output to a normalized anomaly score s(x) ∈ [0.0, 1.0], PRJ_111 applies a centered logistic sigmoid transformation:"
    )

    # Eq (3)
    eq3_xml = (
        '<m:r><m:t>s(x) = </m:t></m:r>'
        '<m:f><m:fPr/>'
        '<m:num><m:r><m:t>1</m:t></m:r></m:num>'
        '<m:den>'
        '<m:r><m:t>1 + </m:t></m:r>'
        '<m:sSup><m:sSupPr/><m:e><m:r><m:t>e</m:t></m:r></m:e><m:sup><m:r><m:t>8.0 · d(x)</m:t></m:r></m:sup></m:sSup>'
        '</m:den>'
        '</m:f>'
    )
    add_omml_equation(doc, eq3_xml, 3)

    add_body_p(
        "At the nominal decision boundary (d(x) = 0.0), the score evaluates to exactly s = 0.5000. Outliers (d(x) < 0) map to s > 0.5000, "
        "while regular inliers (d(x) > 0) map to s < 0.5000. Anomaly classification is determined by the decision threshold:"
    )

    # Eq (4)
    eq4_xml = (
        '<m:r><m:t>Anomaly Flag = </m:t></m:r>'
        '<m:d>'
        '<m:dPr><m:begChr m:val="{"/><m:endChr m:val=""/><m:sepChr m:val=""/><m:grow/></m:dPr>'
        '<m:e>'
        '<m:eqArr><m:eqArrPr/>'
        '<m:e><m:r><m:t>TRUE   if s(</m:t></m:r><m:sSub><m:sSubPr/><m:e><m:r><m:t>x</m:t></m:r></m:e><m:sub><m:r><m:t>i</m:t></m:r></m:sub></m:sSub><m:r><m:t>) ≥ 0.5000</m:t></m:r></m:e>'
        '<m:e><m:r><m:t>FALSE  if s(</m:t></m:r><m:sSub><m:sSubPr/><m:e><m:r><m:t>x</m:t></m:r></m:e><m:sub><m:r><m:t>i</m:t></m:r></m:sub></m:sSub><m:r><m:t>) &lt; 0.5000</m:t></m:r></m:e>'
        '</m:eqArr>'
        '</m:e>'
        '</m:d>'
    )
    add_omml_equation(doc, eq4_xml, 4)

    add_body_p(
        "Domain Safety Guard on Machine Learning Metrics: Because operational satellite receiver output bitstreams are inherently unlabeled, "
        "no ground-truth anomaly annotations exist for off-air broadcast captures. Therefore, PRJ_111 avoids asserting classification accuracy, "
        "precision, recall, or F1-score on real broadcast data. Model sensitivity is validated through controlled synthetic perturbation experiments, "
        "wherein known corruptions (bit flips, synthetic sync byte drops, and container truncations) are injected into verified captures to demonstrate "
        "that the detector flags abnormal intervals with s ≥ 0.5000."
    )

    add_sec_h2("C. Feature F3: Pattern and Entropy Analysis")
    add_body_p(
        "Feature F3 identifies structural patterns and multiplex characteristics across stream progress:\n"
        "• MPEG-TS PID Distribution & Shannon Entropy: Computes individual packet counts and percentage shares per PID. The dominant PID and Shannon entropy [20] are evaluated:"
    )

    # Eq (5)
    eq5_xml = (
        '<m:sSub><m:sSubPr/><m:e><m:r><m:t>H</m:t></m:r></m:e><m:sub><m:r><m:t>PID</m:t></m:r></m:sub></m:sSub>'
        '<m:r><m:t> = - </m:t></m:r>'
        '<m:sSubSup><m:sSubSupPr/><m:e><m:r><m:t>∑</m:t></m:r></m:e><m:sub><m:r><m:t>k=1</m:t></m:r></m:sub><m:sup><m:r><m:t>P</m:t></m:r></m:sup></m:sSubSup>'
        '<m:sSub><m:sSubPr/><m:e><m:r><m:t>p</m:t></m:r></m:e><m:sub><m:r><m:t>k</m:t></m:r></m:sub></m:sSub>'
        '<m:r><m:t> </m:t></m:r>'
        '<m:sSub><m:sSubPr/><m:e><m:r><m:t>log</m:t></m:r></m:e><m:sub><m:r><m:t>2</m:t></m:r></m:sub></m:sSub>'
        '<m:r><m:t> </m:t></m:r>'
        '<m:sSub><m:sSubPr/><m:e><m:r><m:t>p</m:t></m:r></m:e><m:sub><m:r><m:t>k</m:t></m:r></m:sub></m:sSub>'
        '<m:r><m:t>,   </m:t></m:r>'
        '<m:sSub><m:sSubPr/><m:e><m:r><m:t>p</m:t></m:r></m:e><m:sub><m:r><m:t>k</m:t></m:r></m:sub></m:sSub>'
        '<m:r><m:t> = </m:t></m:r>'
        '<m:f><m:fPr/>'
        '<m:num><m:sSub><m:sSubPr/><m:e><m:r><m:t>N</m:t></m:r></m:e><m:sub><m:r><m:t>k</m:t></m:r></m:sub></m:sSub></m:num>'
        '<m:den><m:sSubSup><m:sSubSupPr/><m:e><m:r><m:t>∑</m:t></m:r></m:e><m:sub><m:r><m:t>j=1</m:t></m:r></m:sub><m:sup><m:r><m:t>P</m:t></m:r></m:sup></m:sSubSup><m:sSub><m:sSubPr/><m:e><m:r><m:t>N</m:t></m:r></m:e><m:sub><m:r><m:t>j</m:t></m:r></m:sub></m:sSub></m:den>'
        '</m:f>'
    )
    add_omml_equation(doc, eq5_xml, 5)

    add_body_p(
        "• PAT/PMT Program Structure: Identifies Program Association Tables (PID = 0) and Program Map Tables, tracking program multiplex recurrence [12].\n"
        "• GSE Protocol Mapping: Classifies encapsulated protocol types (GSE_EXT_NPA, IPv4, IPv6) and quantifies fragmentation ratios (N_frag / N_total).\n"
        "• BBFrame Mode Transitions: Tracks shifts in modulation profiles (ACM vs. CCM), Single vs. Multiple Input Stream allocations, and DFL distribution clustering."
    )

    add_sec_h2("D. Feature F4: Spatial Activity Timeline")
    add_body_p(
        "Feature F4 provides continuous visual mapping of stream activity across spatial progress (Fig. 3).\n"
        "Absence of Fabricated Timestamps: Offline receiver bitstreams captured from demodulator test points lack calibrated broadcast wall-clock telemetry. "
        "Assigning synthetic timestamps or calculating fictitious throughput rates (e.g., '15.4 Mbps') creates false precision. PRJ_111 indexes all timeline events strictly by:\n"
        "1) Physical Byte Offset: [B_start, B_end] indicating exact octet positions in the capture file.\n"
        "2) Container Sequence Index: Unit indices [U_start, U_end] tracking sequential packet, PDU, or frame numbers.\n"
        "The timeline visualizes rolling F1 stream health ([0, 100%]), F2 anomaly scores ([0.0, 1.0]) alongside the 0.5000 threshold line, payload density (KB per window), "
        "and format-specific telemetry without fabricating clock timestamps."
    )

    # Fig. 3 (Single column)
    fig3_path = "paper_assets/fig_timeline_view.png"
    if os.path.exists(fig3_path):
        p_img3 = doc.add_paragraph()
        p_img3.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img3.paragraph_format.space_before = Pt(6)
        p_img3.paragraph_format.space_after = Pt(2)
        doc.add_picture(fig3_path, width=Inches(3.3))
        add_fig_caption(3, "Spatial activity timeline (Feature F4) charting rolling stream health, anomaly scores with decision threshold (s = 0.5000), payload density, and PID entropy indexed strictly by physical byte offsets.")

    add_sec_h2("E. Feature F5: Diagnostic Anomaly Explanation")
    add_body_p(
        "Feature F5 bridges unsupervised machine learning and domain engineering by attributing flagged anomalies to specific metric deviations (Fig. 4). "
        "For each feature j in anomalous window W_i, deviation from the stream baseline is evaluated using an operational dispersion model:"
    )

    # Eq (6)
    eq6_xml = (
        '<m:sSub><m:sSubPr/><m:e><m:r><m:t>z</m:t></m:r></m:e><m:sub><m:r><m:t>i,j</m:t></m:r></m:sub></m:sSub>'
        '<m:r><m:t> = </m:t></m:r>'
        '<m:f><m:fPr/>'
        '<m:num>'
        '<m:sSub><m:sSubPr/><m:e><m:r><m:t>x</m:t></m:r></m:e><m:sub><m:r><m:t>i,j</m:t></m:r></m:sub></m:sSub>'
        '<m:r><m:t> - </m:t></m:r>'
        '<m:sSub><m:sSubPr/><m:e><m:r><m:t>μ</m:t></m:r></m:e><m:sub><m:r><m:t>j</m:t></m:r></m:sub></m:sSub>'
        '</m:num>'
        '<m:den>'
        '<m:r><m:t>max(</m:t></m:r>'
        '<m:sSub><m:sSubPr/><m:e><m:r><m:t>σ</m:t></m:r></m:e><m:sub><m:r><m:t>j</m:t></m:r></m:sub></m:sSub>'
        '<m:r><m:t>, </m:t></m:r>'
        '<m:sSub><m:sSubPr/><m:e><m:r><m:t>ε</m:t></m:r></m:e><m:sub><m:r><m:t>j</m:t></m:r></m:sub></m:sSub>'
        '<m:r><m:t>)</m:t></m:r>'
        '</m:den>'
        '</m:f>'
    )
    add_omml_equation(doc, eq6_xml, 6)

    add_body_p(
        "where μ_j is the stream mean for feature j, σ_j is standard deviation, and ε_j is an operational dispersion floor preventing division-by-zero on invariant channels. "
        "To eliminate unbounded numerical artifacts while maintaining mathematical interpretability, PRJ_111 bounds the Z-score:"
    )

    # Eq (7)
    eq7_xml = (
        '<m:sSub><m:sSubPr/><m:e><m:r><m:t>z</m:t></m:r></m:e><m:sub><m:r><m:t>bounded</m:t></m:r></m:sub></m:sSub>'
        '<m:r><m:t> = clamp(</m:t></m:r>'
        '<m:sSub><m:sSubPr/><m:e><m:r><m:t>z</m:t></m:r></m:e><m:sub><m:r><m:t>i,j</m:t></m:r></m:sub></m:sSub>'
        '<m:r><m:t>, -20.0, +20.0)</m:t></m:r>'
    )
    add_omml_equation(doc, eq7_xml, 7)

    add_body_p(
        "The magnitude |z_bounded| is accompanied by an explicit deviation direction: ABOVE_BASELINE (z > 0) or BELOW_BASELINE (z < 0).\n"
        "Physical-Layer Domain Safety Guard: PRJ_111 operates strictly on digital post-demodulator bitstreams. Without access to baseband constellation measurements "
        "or RF tuner AGC levels, the application avoids asserting physical-layer root causes. F5 diagnoses are constrained to digital observations (e.g., 'Elevated adaptation "
        "field frequency' or 'Recording termination boundary'), avoiding speculative claims such as 'rain fade,' 'LNB drift,' or 'transponder power drop.'"
    )

    # Fig. 4 (Single column)
    fig4_path = "paper_assets/fig_anomaly_view.png"
    if os.path.exists(fig4_path):
        p_img4 = doc.add_paragraph()
        p_img4.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img4.paragraph_format.space_before = Pt(6)
        p_img4.paragraph_format.space_after = Pt(2)
        doc.add_picture(fig4_path, width=Inches(3.3))
        add_fig_caption(4, "Flagged anomaly windows and diagnostic attribution table (Features F2 and F5) displaying unit ranges, byte offsets, anomaly scores, and Bounded Z-Score explanations with deviation directionality.")

    add_sec_h2("F. Feature F6: Semantic Stream Comparison Engine")
    add_body_p(
        "Feature F6 provides differential comparison between two analyzed streams (Stream A and Stream B) as shown in Fig. 5.\n"
        "The Cross-Format Semantic Barrier: A key architectural contribution of PRJ_111 is the Cross-Format Semantic Barrier. Metrics sharing identical nomenclature inside "
        "CommonMetrics are not assumed to be comparable across formats:\n"
        "• Comparable Metrics (2): total_payload_bytes (an octet of user data represents an invariant physical quantity) and integrity_ratio (dimensionless syntactic compliance proportion [0.0, 1.0]).\n"
        "• Non-Comparable Metrics (9): total_units, valid_units, invalid_units, truncated_units, mean_payload_bytes, payload_ratio, error_count, error_rate, and entropy are blocked cross-format with explicit engineering justifications.\n"
        "For comparable metrics, differences are quantified without mathematical singularities:"
    )

    # Eq (8)
    eq8_xml = (
        '<m:sSub><m:sSubPr/><m:e><m:r><m:t>Δ</m:t></m:r></m:e><m:sub><m:r><m:t>abs</m:t></m:r></m:sub></m:sSub>'
        '<m:r><m:t> = B - A</m:t></m:r>'
    )
    add_omml_equation(doc, eq8_xml, 8)

    # Eq (9)
    eq9_xml = (
        '<m:sSub><m:sSubPr/><m:e><m:r><m:t>Δ</m:t></m:r></m:e><m:sub><m:r><m:t>rel</m:t></m:r></m:sub></m:sSub>'
        '<m:r><m:t> = </m:t></m:r>'
        '<m:d>'
        '<m:dPr><m:begChr m:val="{"/><m:endChr m:val=""/><m:sepChr m:val=""/><m:grow/></m:dPr>'
        '<m:e>'
        '<m:eqArr><m:eqArrPr/>'
        '<m:e>'
        '<m:f><m:fPr/><m:num><m:r><m:t>B - A</m:t></m:r></m:num><m:den><m:r><m:t>A</m:t></m:r></m:den></m:f>'
        '<m:r><m:t> × 100%   if A &gt; 0</m:t></m:r>'
        '</m:e>'
        '<m:e><m:r><m:t>Undefined (Critical)   if A = 0 and B &gt; 0</m:t></m:r></m:e>'
        '<m:e><m:r><m:t>0.0%   if A = 0 and B = 0</m:t></m:r></m:e>'
        '</m:eqArr>'
        '</m:e>'
        '</m:d>'
    )
    add_omml_equation(doc, eq9_xml, 9)

    add_body_p(
        "Differences are classified into a four-tier significance hierarchy:\n"
        "• NEGLIGIBLE: |Δ_{rel}| < 2.0%\n"
        "• MINOR: 2.0% ≤ |Δ_{rel}| < 10.0%\n"
        "• SUBSTANTIAL: 10.0% ≤ |Δ_{rel}| < 50.0%\n"
        "• CRITICAL: |Δ_{rel}| ≥ 50.0% (or non-zero error emergence from zero baseline)\n"
        "Windows are synchronized via direct-index overlap: i ∈ [0, min(N_A, N_B) - 1]. Trailing windows in asymmetric captures are recorded under unaligned_windows as capture duration differences, not transmission loss."
    )

    # Fig. 5 (Single column)
    fig5_path = "paper_assets/fig_comparison_view.png"
    if os.path.exists(fig5_path):
        p_img5 = doc.add_paragraph()
        p_img5.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img5.paragraph_format.space_before = Pt(6)
        p_img5.paragraph_format.space_after = Pt(2)
        doc.add_picture(fig5_path, width=Inches(3.3))
        add_fig_caption(5, "Stream comparison interface (Feature F6) evaluating MPEG-TS against corrupted TS, highlighting direct-index window alignment, payload delta (-0.06%), and the dynamic semantic audit table.")

    add_sec_h2("G. Feature F7: Automatic Multi-Format Reporting")
    add_body_p(
        "Feature F7 synthesizes F1–F6 analytical results into exportable executive reports (JSON, Markdown, CP-1252-safe Plain Text, and Standalone HTML5) as illustrated in Fig. 6.\n"
        "All findings generated by F7 are categorized under a formal tripartite epistemological taxonomy:\n"
        "1) OBSERVED_FACT: Direct, deterministic physical measurements directly verifiable in stream syntax (e.g., total_units = 18176, sync_byte_errors = 0).\n"
        "2) STATISTICAL_FINDING: Quantities derived through statistical or machine learning models (e.g., health_score = 100.0, anomalous_windows = 5, peak_anomaly_score = 0.8576).\n"
        "3) ENGINEERING_INTERPRETATION: Domain-bounded diagnostic attributions constrained strictly to digital bitstream characteristics (e.g., 'Capture termination boundary accounts for partial trailing window')."
    )

    # Fig. 6 (Single column)
    fig6_path = "paper_assets/fig_report_view.png"
    if os.path.exists(fig6_path):
        p_img6 = doc.add_paragraph()
        p_img6.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img6.paragraph_format.space_before = Pt(6)
        p_img6.paragraph_format.space_after = Pt(2)
        doc.add_picture(fig6_path, width=Inches(3.3))
        add_fig_caption(6, "Multi-format diagnostic report generation view (Feature F7) showing tripartite findings categorization and one-click export controls.")

    # ----------------------------------------------------
    # SECTION 5: Continuous Break -> 1 COLUMN (Full-Width Table II)
    # ----------------------------------------------------
    sec5 = doc.add_section(WD_SECTION.CONTINUOUS)
    set_section_cols(sec5, num=1)

    add_tbl_caption("II", "MPEG-TS Health and Priority-1 Integrity Results")
    tbl2 = doc.add_table(rows=3, cols=8)
    tbl2.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl2.autofit = False
    set_ieee_table_borders(tbl2)
    col2_widths = [Inches(1.4), Inches(0.7), Inches(0.65), Inches(0.8), Inches(0.7), Inches(1.0), Inches(0.7), Inches(0.85)]
    tbl2_headers = ["Stream Capture", "Yielded Pkts", "Sync Int.", "TEI", "CC", "Net Payload", "Health", "Status"]
    tbl2_data = [
        ["sample.ts (Clean)", "18,176", "100.0%", "0 (0.00%)", "0 (0.00%)", "3,267,305 B", "100.0%", "HEALTHY"],
        ["corrupted_sample.ts", "18,168", "100.0%", "4 (0.02%)", "0 (0.00%)", "3,265,277 B", "99.67%", "HEALTHY"]
    ]
    for c_idx, w in enumerate(col2_widths):
        tbl2.columns[c_idx].width = w
    for c_idx, h_text in enumerate(tbl2_headers):
        cell = tbl2.cell(0, c_idx)
        cell.width = col2_widths[c_idx]
        set_cell_background(cell, "F0F4F8")
        set_cell_margins(cell, 50, 50, 50, 50)
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(h_text)
        r.font.name = 'Times New Roman'
        r.font.size = Pt(8.5)
        r.font.bold = True
    for r_idx, row_data in enumerate(tbl2_data):
        for c_idx, val in enumerate(row_data):
            cell = tbl2.cell(r_idx + 1, c_idx)
            cell.width = col2_widths[c_idx]
            set_cell_margins(cell, 40, 40, 50, 50)
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER if c_idx != 0 else WD_ALIGN_PARAGRAPH.LEFT
            r = p.add_run(val)
            r.font.name = 'Times New Roman'
            r.font.size = Pt(8.5)

    # ----------------------------------------------------
    # SECTION 6: Continuous Break -> TWO COLUMNS
    # Sections VI, VII, Tables III, IV, V
    # ----------------------------------------------------
    sec6 = doc.add_section(WD_SECTION.CONTINUOUS)
    set_section_cols(sec6, num=2, space=360)

    # Section VI
    add_sec_h1("VI. Experimental Setup and Datasets")
    add_body_p(

    doc.save('test_step5_sec6_7_tbl2.docx')
build_paper()
