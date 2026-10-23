"""
build_ieee_docx_4pages.py
Generates the PRJ_111 IEEE-style TWO-COLUMN Microsoft Word (.docx) document
calibrated to hit EXACTLY 4 pages in Microsoft Word.
"""

import os
import sys
import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls, qn
import win32com.client

def set_section_cols(sec, num=2, space=360):
    sectPr = sec._sectPr
    for c in sectPr.xpath('./w:cols'):
        sectPr.remove(c)
    sectPr.append(parse_xml(f'<w:cols {nsdecls("w")} w:num="{num}" w:space="{space}"/>'))

def set_cell_background(cell, fill_hex):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=40, bottom=40, left=60, right=60):
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

def add_omml_equation(doc, math_inner_xml, eq_num):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.first_line_indent = Inches(0)
    
    pPr = p._p.get_or_add_pPr()
    tabs_xml = f'<w:tabs {nsdecls("w")}><w:tab w:val="center" w:pos="2400"/><w:tab w:val="right" w:pos="4800"/></w:tabs>'
    pPr.append(parse_xml(tabs_xml))
    
    p.add_run("\t")
    omml_inline = f'<m:oMath {nsdecls("m")}>{math_inner_xml}</m:oMath>'
    p._p.append(parse_xml(omml_inline))
    p.add_run("\t")
    
    r_num = p.add_run(f"({eq_num})")
    r_num.font.name = "Times New Roman"
    r_num.font.size = Pt(9)

def build_paper_4pages():
    doc = Document()
    
    # ----------------------------------------------------
    # SECTION 1: Full-Width Title & Authors (1 Column)
    # ----------------------------------------------------
    sec1 = doc.sections[0]
    sec1.page_width = Inches(8.5)
    sec1.page_height = Inches(11.0)
    sec1.top_margin = Inches(0.65)
    sec1.bottom_margin = Inches(0.65)
    sec1.left_margin = Inches(0.65)
    sec1.right_margin = Inches(0.65)
    set_section_cols(sec1, num=1)

    normal_style = doc.styles['Normal']
    normal_font = normal_style.font
    normal_font.name = 'Times New Roman'
    normal_font.size = Pt(9.5)
    normal_font.color.rgb = RGBColor(0x00, 0x00, 0x00)
    normal_style.paragraph_format.line_spacing = 1.02
    normal_style.paragraph_format.space_after = Pt(2.5)
    normal_style.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY

    # Title
    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title.paragraph_format.space_before = Pt(0)
    p_title.paragraph_format.space_after = Pt(8)
    r_title = p_title.add_run("Development of a Multi-Format DVB-S2 Receiver Output\nStream Analyzer with Anomaly Detection and Diagnostic Reporting")
    r_title.font.name = 'Times New Roman'
    r_title.font.size = Pt(15.5)
    r_title.font.bold = True

    # Author Table
    author_tbl = doc.add_table(rows=1, cols=3)
    author_tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    author_tbl.autofit = False
    tblPr = author_tbl._tbl.tblPr
    tblBorders = parse_xml(f'<w:tblBorders {nsdecls("w")}><w:top w:val="none"/><w:bottom w:val="none"/><w:insideH w:val="none"/><w:insideV w:val="none"/><w:left w:val="none"/><w:right w:val="none"/></w:tblBorders>')
    tblPr.append(tblBorders)

    col_w = Inches(2.4)
    for c in author_tbl.columns:
        c.width = col_w

    authors_data = [
        ("Y Vengala Rao", "Roll No: 20231COM0001", "Dept. of Computer Science & Eng.\nPresidency University, India"),
        ("Sk Samad", "Roll No: 20231COM0031", "Dept. of Computer Science & Eng.\nPresidency University, India"),
        ("C Rakeshwar", "Roll No: 20231COM0008", "Dept. of Computer Science & Eng.\nPresidency University, India")
    ]

    for i, (name, roll, affil) in enumerate(authors_data):
        cell = author_tbl.cell(0, i)
        cell.width = col_w
        set_cell_margins(cell, 0, 0, 30, 30)
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_after = Pt(1)
        
        rn = p.add_run(name + "\n")
        rn.font.name = 'Times New Roman'
        rn.font.size = Pt(10)
        rn.font.bold = True
        
        rr = p.add_run(roll + "\n")
        rr.font.name = 'Times New Roman'
        rr.font.size = Pt(8.5)
        
        ra = p.add_run(affil)
        ra.font.name = 'Times New Roman'
        ra.font.size = Pt(8)
        ra.font.italic = True

    p_div = doc.add_paragraph()
    p_div.paragraph_format.space_before = Pt(4)
    p_div.paragraph_format.space_after = Pt(0)

    def add_sec_h1(title):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(7)
        p.paragraph_format.space_after = Pt(2)
        p.paragraph_format.first_line_indent = Inches(0)
        r = p.add_run(title.upper())
        r.font.name = 'Times New Roman'
        r.font.size = Pt(9.5)
        r.font.bold = True
        return p

    def add_sec_h2(title):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p.paragraph_format.space_before = Pt(5)
        p.paragraph_format.space_after = Pt(2)
        p.paragraph_format.first_line_indent = Inches(0)
        r = p.add_run(title)
        r.font.name = 'Times New Roman'
        r.font.size = Pt(9.5)
        r.font.bold = True
        r.font.italic = True
        return p

    def add_body_p(text, indent=True):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p.paragraph_format.space_after = Pt(2.5)
        if indent:
            p.paragraph_format.first_line_indent = Inches(0.16)
        else:
            p.paragraph_format.first_line_indent = Inches(0)
        r = p.add_run(text)
        r.font.name = 'Times New Roman'
        r.font.size = Pt(9.5)
        return p

    def add_fig_caption(num, title):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(2)
        p.paragraph_format.space_after = Pt(5)
        p.paragraph_format.first_line_indent = Inches(0)
        r_lbl = p.add_run(f"Fig. {num}. ")
        r_lbl.font.name = 'Times New Roman'
        r_lbl.font.size = Pt(8)
        r_lbl.font.bold = True
        r_txt = p.add_run(title)
        r_txt.font.name = 'Times New Roman'
        r_txt.font.size = Pt(8)
        return p

    def add_tbl_caption(num_str, title):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(6)
        p.paragraph_format.space_after = Pt(2)
        p.paragraph_format.first_line_indent = Inches(0)
        r1 = p.add_run(f"TABLE {num_str}\n")
        r1.font.name = 'Times New Roman'
        r1.font.size = Pt(8)
        r1.font.bold = True
        r2 = p.add_run(title.upper())
        r2.font.name = 'Times New Roman'
        r2.font.size = Pt(8)
        r2.font.bold = True
        return p

    # ----------------------------------------------------
    # SECTION 2: Two Columns
    # ----------------------------------------------------
    sec2 = doc.add_section(WD_SECTION.CONTINUOUS)
    set_section_cols(sec2, num=2, space=360)

    # Abstract
    p_abs = doc.add_paragraph()
    p_abs.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p_abs.paragraph_format.space_after = Pt(3)
    p_abs.paragraph_format.first_line_indent = Inches(0)
    
    r_ah = p_abs.add_run("Abstract—")
    r_ah.font.name = 'Times New Roman'
    r_ah.font.size = Pt(8.5)
    r_ah.font.bold = True
    r_ah.font.italic = True
    
    abs_text = (
        "Digital Video Broadcasting via Satellite (DVB-S2) establishes the prevailing physical and link framing architecture "
        "for satellite broadband, high-definition television contribution, and mobile backhaul links. Satellite receiver demodulators "
        "extract baseband data from radio-frequency downlinks and deliver post-demodulation digital streams spanning several incompatible "
        "encapsulation standards: MPEG-2 Transport Streams (MPEG-TS), Generic Stream Encapsulation (GSE), and DVB-S2 Baseband Frames (BBFrame). "
        "Diagnostic inspection across these heterogeneous formats creates substantial operational friction: each framing layer employs distinct "
        "boundary markers, synchronization mechanisms, and failure profiles that legacy single-protocol inspection tools fail to harmonize. "
        "This work introduces PRJ_111, an integrated, self-contained software suite engineered to perform multi-format DVB-S2 receiver stream "
        "evaluation, unsupervised anomaly discovery, and systematic diagnostic generation. The system incorporates an integrated seven-stage "
        "analytical pipeline providing deterministic stream health accounting rooted in ETSI TR 101 290 Priority-1 criteria, unsupervised "
        "anomaly isolation utilizing format-segregated Isolation Forest ensembles, Shannon entropy and multiplex distribution profiling, "
        "byte-referenced physical activity mapping, clamped Z-score diagnostic attribution, semantically shielded cross-format stream "
        "differentials, and automated diagnostic synthesis structured around an empirical tripartite epistemology. Empirical validation on "
        "broadcast satellite captures demonstrates deterministic stream accounting (100.0% clean; 99.67% corrupted with exact transport error "
        "tracking), unsupervised localization of multiplex burst transients and file truncation boundaries, and strict semantic separation. "
        "The system is verified by an automated regression suite of 304 tests (268 backend modules and 36 frontend integration tests) attaining "
        "a 100% verification pass rate with zero failures, zero errors, and zero omissions."
    )
    r_at = p_abs.add_run(abs_text)
    r_at.font.name = 'Times New Roman'
    r_at.font.size = Pt(8.5)

    p_idx = doc.add_paragraph()
    p_idx.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p_idx.paragraph_format.space_after = Pt(6)
    p_idx.paragraph_format.first_line_indent = Inches(0)
    
    r_ih = p_idx.add_run("Index Terms—")
    r_ih.font.name = 'Times New Roman'
    r_ih.font.size = Pt(8.5)
    r_ih.font.bold = True
    r_ih.font.italic = True
    
    r_it = p_idx.add_run("Anomaly detection, Baseband frame, Digital video broadcasting, DVB-S2, Feature extraction, Generic stream encapsulation, Isolation Forest, MPEG transport stream, Receiver output analysis, Stream analysis.")
    r_it.font.name = 'Times New Roman'
    r_it.font.size = Pt(8.5)
    r_it.font.italic = True

    add_sec_h1("I. Introduction")
    add_body_p(
        "Satellite links running DVB-S2 [1] handle massive volumes of broadcast video, broadband Internet traffic, and corporate data every day. "
        "When a satellite dish locks onto a downlink carrier, the receiver's front-end downconverts the signal to an intermediate frequency. "
        "Demodulator circuitry then performs carrier recovery, matched filtering, and dual-stage forward error correction (FEC) using inner LDPC "
        "and outer BCH codes [2]. Once error correction is complete, the receiver delivers a raw digital stream to host processing software or demultiplexers."
    )
    add_body_p(
        "In real-world ground stations and teleports, however, this post-demodulator output does not come in a single neat format. Depending on how "
        "the transponder was provisioned, operators receive one of three distinct framing layers:\n"
        "• MPEG-2 Transport Stream (MPEG-TS): The long-standing broadcast standard [3], packaging data into rigid 188-byte packets synchronized by "
        "0x47 sync octets, with 13-bit Program Identifiers (PIDs) and 4-bit continuity counters.\n"
        "• Generic Stream Encapsulation (GSE): The modern IP encapsulation protocol [4], which wraps variable-length network datagrams (IPv4, IPv6) "
        "with 2-bit fragmentation headers and CRC-32 checksums, avoiding MPEG-TS overhead.\n"
        "• DVB-S2 Baseband Frames (BBFrame): The direct physical-link container [1], containing an 80-bit baseband header, Mode Adaptation flags "
        "(MATYPE), a Data Field Length (DFL) indicator, and an 8-bit CRC."
    )
    add_body_p(
        "Troubleshooting these streams during station commissioning or downlink outages is often a painful process [5]. General-purpose packet sniffers "
        "like Wireshark expect Ethernet frames and stumble on raw, unencapsulated transport streams [6]. On the other hand, commercial broadcast monitors "
        "parse MPEG-TS well, but ignore GSE packets and baseband frames altogether [5]."
    )
    add_body_p(
        "Furthermore, field engineers face three recurring traps when analyzing captured streams:\n"
        "1) Brittle Parsers and Misidentified Files: Raw captures arrive as unlabeled binary files (.ts, .bin, .pcap). Simple file-extension checks "
        "frequently guess wrong, and fragile parsers crash whenever they hit a corrupted packet or lost sync byte.\n"
        "2) Comparing Apples to Oranges: Naively comparing packet counts between 188-byte MPEG-TS packets and 7-kilobyte Baseband Frames leads to "
        "meaningless conclusions, confusing operators during multi-feed audits.\n"
        "3) Speculative Root Causes and Fake Timestamps: Many commercial tools invent smooth Megabit-per-second rate charts or guess at physical-layer "
        "issues (like blaming rain fade for packet drops) without access to actual receiver clock signals or signal-to-noise ratios."
    )
    add_body_p(
        "To fix these problems, we created PRJ_111, a lightweight, standalone software workstation for analyzing DVB-S2 receiver output streams. "
        "PRJ_111 features a seven-stage analytical pipeline (F1–F7) that automatically detects stream formats from raw binary headers, parses units "
        "deterministically, calculates stream health (F1), discovers structural anomalies with an unsupervised Isolation Forest (F2), analyzes "
        "multiplex entropy (F3), renders byte-indexed activity timelines (F4), explains anomaly drivers with clamped Z-scores (F5), protects cross-stream "
        "comparisons with a strict semantic shield (F6), and exports comprehensive diagnostic reports (F7)."
    )

    add_sec_h1("II. Related Work")
    add_body_p(
        "The DVB-S2 standard (ETSI EN 302 307-1) governs physical framing, forward error correction, and modulation, specifying Adaptive Coding and Modulation "
        "(ACM) alongside native baseband containers [1]. Morello and Mignone [2] evaluated the physical-layer mechanisms of DVB-S2, demonstrating how variable "
        "user datagrams are packed into baseband structures safeguarded by concatenated inner LDPC and outer BCH codes. Casini et al. [7] explored higher-order "
        "modulation schemes spanning QPSK through 32-APSK, examining the 80-bit Baseband Header (BBHeader), square-root raised cosine roll-off values "
        "(α ∈ {0.20, 0.25, 0.35}), and Data Field Length (DFL) bit allocation. Sklar [8] formulated the theoretical bedrock for digital modulation, channel "
        "coding capacity, and baseband framing boundaries in digital communication channels."
    )
    add_body_p(
        "For network-layer packet distribution, Fairhurst and Collini-Nocker [9] formulated Generic Stream Encapsulation (ETSI TS 102 606-1) [4] as a low-overhead "
        "successor to Multi-Protocol Encapsulation (MPE over MPEG-TS) and Unidirectional Lightweight Encapsulation (ULE, RFC 4326) [10]. GSE standardizes "
        "variable-length protocol data units carrying native IP datagrams with per-fragment CRC-32 protection, eliminating the transport stream encapsulation "
        "overhead. Meanwhile, digital television transport continues to rely upon the MPEG-2 Transport Stream (ISO/IEC 13818-1) [3]. Measurement guidelines "
        "for broadcast verification are codified in ETSI TR 101 290 [11], specifying Priority-1 operational parameters: synchronization loss, Transport Error "
        "Indicator (TEI) flags, and Continuity Counter (CC) sequence violations. Associated service metadata is governed by ETSI EN 300 468 [12]."
    )
    add_body_p(
        "Luisi et al. [5] evaluated satellite broadcast monitoring tools, observing that while specialized hardware instruments accurately flag ETSI TR 101 290 "
        "Priority-1 defects, they generally lack native parsing capabilities for emerging IP encapsulation schemes (GSE and BBFrames) output by contemporary "
        "broadband receivers. Minoli [6] surveyed network packet inspection software, highlighting that general-purpose sniffers treat raw stream dumps as opaque "
        "binary blobs unless enveloped in standard network capture headers (e.g., PCAP)."
    )
    add_body_p(
        "Surveys by Chandola et al. [13] and Pimentel et al. [14] trace the evolution of telemetry anomaly detection. Traditional statistical monitoring depends "
        "on rigid, static thresholds, which struggle in statistically multiplexed channels where instantaneous bitrates fluctuate dynamically. Conversely, "
        "supervised classification demands extensive ground-truth anomaly annotations [13]. In live satellite telemetry, labeled anomaly corpora are practically "
        "nonexistent. To analyze unannotated streaming telemetry, Liu et al. [15] introduced the Isolation Forest algorithm, constructing ensembles of random "
        "isolation trees (iTrees). Abnormal instances require fewer random partitions to isolate, yielding significantly shorter average tree paths [15]. "
        "Baggio et al. [17] proved that Isolation Forest achieves linear computational efficiency (O(n log n)) and robust outlier sensitivity compared to "
        "density or distance-based algorithms. PRJ_111 adapts Isolation Forest to DVB-S2 stream telemetry, conducting format-isolated spatial-window anomaly "
        "detection equipped with calibrated logistic decision boundaries."
    )

    # ----------------------------------------------------
    # SECTION 3: Architecture Diagram (Full Width across 1 Column)
    # ----------------------------------------------------
    sec3 = doc.add_section(WD_SECTION.CONTINUOUS)
    set_section_cols(sec3, num=1)

    fig1_path = "07_DOCUMENTATION/RESEARCH_PAPER/assets/architecture_diagram.png"
    if os.path.exists(fig1_path):
        p_img1 = doc.add_paragraph()
        p_img1.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img1.paragraph_format.space_before = Pt(4)
        p_img1.paragraph_format.space_after = Pt(2)
        doc.add_picture(fig1_path, width=Inches(6.2))
        add_fig_caption(1, "End-to-End Architectural Pipeline of PRJ_111 (Stages 1 through 6).")

    # ----------------------------------------------------
    # SECTION 4: Two Columns (Methodology, Decoders, Results, Conclusion)
    # ----------------------------------------------------
    sec4 = doc.add_section(WD_SECTION.CONTINUOUS)
    set_section_cols(sec4, num=2, space=360)

    add_sec_h1("III. System Architecture and Workstation")
    add_body_p(
        "PRJ_111 is implemented in Python 3.12 as a local engineering workstation with zero external cloud dependencies:\n"
        "• Backend Core & Ingestion Engine: Pure Python modular architecture (parsers/, features/, analysis/, streaming/). Supports multi-mode stream processing: "
        "Standard in-memory sequential parsing, 64 KB block-buffered Chunked streaming for large continuous captures, and High-Throughput zero-copy memory-mapped (mmap) processing.\n"
        "• Machine Learning Layer: Scikit-learn (IsolationForest) coupled with NumPy and SciPy for numerical vector operations and bounded Z-score feature attribution.\n"
        "• Controlled Fault-Injection Benchmark: Multi-format synthetic mutation framework (TEI corruption, CC discontinuities, PDU truncation, BBFrame CRC-8 corruption) "
        "enabling empirical before-vs-after anomaly sensitivity scoring.\n"
        "• HTTP Gateway & Workstation: Multi-threaded native Python HTTP server (ThreadingHTTPServer) exposing a RESTful JSON API (/api/status, /api/analyze, /api/compare, "
        "/api/upload, /api/export, /api/fault-inject) and Single-Page Application (SPA) dashboard."
    )

    add_sec_h1("IV. Multi-Format Stream Processing")
    add_body_p(
        "The parsing layer operates directly on raw binary stream captures, providing modular decoders tailored to each standard:\n"
        "• MPEG-2 Transport Stream (MPEG-TS): The MPEG-TS parser processes continuous 188-byte containers specified in ISO/IEC 13818-1 [3]. Validates 0x47 sync cadence, "
        "flags Transport Error Indicator (TEI) bits, extracts 13-bit Program Identifiers (PIDs), and tracks 4-bit cyclic Continuity Counters (CC) per PID.\n"
        "• Generic Stream Encapsulation (GSE): Decodes variable-size protocol data units adhering to ETSI TS 102 606-1 [4]. Parses 2-bit start/end fragmentation flags, "
        "12-bit length field (≤ 4,095 bytes payload), 16-bit EtherType (0x0800 IPv4), label addressing, and CRC-32 syndrome validation.\n"
        "• DVB-S2 Baseband Frames (BBFrame): Decodes native baseband frames specified in ETSI EN 302 307-1 [1]. Validates 80-bit headers via CRC-8 "
        "(G(x) = x^8 + x^7 + x^6 + x^4 + x^2 + 1), extracts MATYPE-1/2 (SIS/MIS, ACM/CCM, roll-off α), and measures Data Field Length (DFL ∈ [216, 10000] bits)."
    )

    # Table I
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
        set_cell_margins(cell, 30, 30, 30, 30)
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
            set_cell_margins(cell, 25, 25, 30, 30)
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER if c_idx != 0 else WD_ALIGN_PARAGRAPH.LEFT
            r = p.add_run(val)
            r.font.name = 'Times New Roman'
            r.font.size = Pt(7.5)

    add_sec_h1("V. Feature Engineering and Analytical Pipeline")
    add_body_p(
        "Telemetry is bifurcated into physical invariants (CommonMetrics) and native format-specific metrics (TSMetrics, GSEMetrics, BBFrameMetrics):\n"
        "• Feature F1 (Stream Health Analysis): Implements transparent threshold-driven deductive scoring from a 100.0% baseline based on ETSI TR 101 290 P1 criteria:\n"
        "H(W_i) = max(0.0, 100.0 + ∑ ΔH). Categorized into HEALTHY (H ≥ 99.0%), WARNING (80.0% ≤ H < 99.0%), and CRITICAL (H < 80.0%).\n"
        "• Feature F2 (AI Anomaly Detection): Instantiates an ensemble of T = 100 isolation trees (n_estimators=100, contamination=0.05). Maps raw decision scores "
        "d(x) through a centered logistic sigmoid: s(x) = 1 / (1 + e^(8.0·d(x))). Flagged anomalous if s(x) ≥ 0.5000. Real broadcast data is evaluated via "
        "synthetic perturbation rather than ungrounded ROC-AUC metrics.\n"
        "• Feature F3 (Pattern and Entropy Analysis): Evaluates individual PID shares and Shannon multiplex entropy: H_PID = - ∑ p_k log_2 p_k.\n"
        "• Feature F4 (Spatial Activity Timeline): Charts rolling health, anomaly scores, and payload density indexed strictly by physical byte offsets [B_start, B_end] "
        "and container indices, eliminating fabricated clock time axes.\n"
        "• Feature F5 (Diagnostic Anomaly Explanation): Attributes flagged anomalies to specific metric drivers using bounded Z-scores: "
        "z_bounded = clamp((x_(i,j) - μ_j) / max(σ_j, ε_j), -20.0, +20.0).\n"
        "• Feature F6 (Semantic Comparison Engine): Protects cross-format comparisons via an automated semantic barrier. Audits 2 comparable physical invariants "
        "(total_payload_bytes, integrity_ratio) while shielding 9 format-incompatible framing metrics.\n"
        "• Feature F7 (Automatic Reporting): Synthesizes diagnostics into JSON, Markdown, HTML, and CSV organized under a tripartite epistemology "
        "(OBSERVED_FACT, STATISTICAL_FINDING, ENGINEERING_INTERPRETATION)."
    )

    add_sec_h1("VI. Experimental Results and Discussion")
    add_body_p("The system was evaluated against four authoritative satellite captures in 01_RAW_DATA/ (Tables II and III).")

    # Table II (MPEG-TS)
    add_tbl_caption("II", "MPEG-TS Health and Priority-1 Integrity Results")
    tbl2 = doc.add_table(rows=3, cols=7)
    tbl2.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl2.autofit = False
    set_ieee_table_borders(tbl2)
    col2_widths = [Inches(0.9), Inches(0.45), Inches(0.45), Inches(0.45), Inches(0.45), Inches(0.7), Inches(0.55)]
    tbl2_headers = ["Stream", "Pkts", "Sync", "TEI", "CC", "Net Payload", "Health"]
    tbl2_data = [
        ["sample.ts", "18,176", "100%", "0 (0%)", "0 (0%)", "3,267,305 B", "100.0%"],
        ["corrupted", "18,168", "100%", "4 (0.02%)", "0 (0%)", "3,265,277 B", "99.67%"]
    ]
    for c_idx, w in enumerate(col2_widths):
        tbl2.columns[c_idx].width = w
    for c_idx, h_text in enumerate(tbl2_headers):
        cell = tbl2.cell(0, c_idx)
        cell.width = col2_widths[c_idx]
        set_cell_background(cell, "F0F4F8")
        set_cell_margins(cell, 30, 30, 30, 30)
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(h_text)
        r.font.name = 'Times New Roman'
        r.font.size = Pt(7.5)
        r.font.bold = True
    for r_idx, row_data in enumerate(tbl2_data):
        for c_idx, val in enumerate(row_data):
            cell = tbl2.cell(r_idx + 1, c_idx)
            cell.width = col2_widths[c_idx]
            set_cell_margins(cell, 25, 25, 30, 30)
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER if c_idx != 0 else WD_ALIGN_PARAGRAPH.LEFT
            r = p.add_run(val)
            r.font.name = 'Times New Roman'
            r.font.size = Pt(7.5)

    add_body_p(
        "• MPEG-TS Health Verification: Clean sample.ts achieved 100.0% sync integrity and 100.0% health across 18,176 packets (3,267,305 B payload). "
        "The corrupted stream dropped 8 unaligned packets, yielding 18,168 packets with 4 TEI errors in Window 0, achieving 99.67% average health (HEALTHY).\n"
        "• GSE Protocol Results: Evaluated 14 PDUs (9,324 B, 8,764 B payload), comprising 6 unfragmented (42.9%) and 8 fragmented PDUs (57.1%). Passed 100% CRC-32 checksums with 100.0% health.\n"
        "• BBFrame Transmission: Evaluated 4,309 frames (2,349,376 B, 1,958,826 B payload). Verified 100.0% CRC-8 checks, 100% ACM, and modal DFL of 2,992 bits (85.82% share).\n"
        "• Isolation Forest Findings: Consistently flagged container volume truncation at stream termination boundaries (Window 90 in TS, Window 4 in GSE, Window 86 in BBFrame) and localized multiplex burst concentrations.\n"
        "• Cross-Format Comparison Audit: Comparing TS against BBFrame revealed a -40.05% payload delta (3,267,305 B vs 1,958,826 B, SUBSTANTIAL) and identical 1.0000 integrity ratio (NEGLIGIBLE), with 9 framing fields shielded."
    )

    # Table III (Isolation Forest)
    add_tbl_caption("III", "Isolation Forest Anomaly Results across Formats")
    tbl3 = doc.add_table(rows=4, cols=5)
    tbl3.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl3.autofit = False
    set_ieee_table_borders(tbl3)
    col3_widths = [Inches(0.65), Inches(0.55), Inches(0.4), Inches(0.4), Inches(1.3)]
    tbl3_headers = ["Format", "Window", "Total", "Anom.", "Peak & Indices"]
    tbl3_data = [
        ["MPEG-TS", "200 Pkts", "91", "5", "0.8576 [Win 1, 2, 12, 88, 90]"],
        ["GSE", "3 PDUs", "5", "1", "0.5018 [Win 4]"],
        ["BBFrame", "50 Frms", "87", "5", "0.7406 [Win 0, 83, 84, 85, 86]"]
    ]
    for c_idx, w in enumerate(col3_widths):
        tbl3.columns[c_idx].width = w
    for c_idx, h_text in enumerate(tbl3_headers):
        cell = tbl3.cell(0, c_idx)
        cell.width = col3_widths[c_idx]
        set_cell_background(cell, "F0F4F8")
        set_cell_margins(cell, 30, 30, 30, 30)
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(h_text)
        r.font.name = 'Times New Roman'
        r.font.size = Pt(7.5)
        r.font.bold = True
    for r_idx, row_data in enumerate(tbl3_data):
        for c_idx, val in enumerate(row_data):
            cell = tbl3.cell(r_idx + 1, c_idx)
            cell.width = col3_widths[c_idx]
            set_cell_margins(cell, 25, 25, 30, 30)
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER if c_idx in [1, 2, 3] else WD_ALIGN_PARAGRAPH.LEFT
            r = p.add_run(val)
            r.font.name = 'Times New Roman'
            r.font.size = Pt(7.5)

    add_sec_h1("VII. Verification and Limitations")
    add_body_p(
        "System reliability is validated by an automated regression test suite executed via Python's standard unittest:\n"
        "python -m unittest discover -s tests -v\n"
        "• Outcome: 304 / 304 Tests Passing (100% Pass Rate) with 0 failures, 0 errors, and 0 skipped in 74.61s (268 backend modules and 36 frontend integration tests).\n"
        "• Domain Safeguards: PRJ_111 operates strictly post-demodulator on digital streams; it does not measure analog RF parameters (SNR, MER) and indexes timeline events strictly by physical byte offsets."
    )

    add_sec_h1("VIII. Conclusion")
    add_body_p(
        "PRJ_111 unifies multi-format DVB-S2 receiver output stream analysis across MPEG-TS, GSE, and BBFrames. By combining deterministic health scoring, "
        "unsupervised Isolation Forest anomaly detection, physical spatial timelines, bounded Z-score explanations, and semantic comparison shields, "
        "it establishes a dependable, offline engineering workstation for ground station telemetry and research. Future extensions include SDR "
        "front-end integration and FPGA acceleration."
    )

    add_sec_h1("Acknowledgment")
    add_body_p(
        "The authors thank Presidency University and project guide Irfan Rajab Bhat, Assistant Professor, for technical guidance and computing infrastructure support."
    )

    add_sec_h1("References")
    references_data = [
        "[1] “Digital Video Broadcasting (DVB); Second Generation Framing Structure, Channel Coding and Modulation Systems for Broadcasting, Interactive Services, News Gathering and Other Broadband Satellite Applications; Part 1: DVB-S2,” ETSI EN 302 307-1 V1.4.1, 2014.",
        "[2] A. Morello and V. Mignone, “DVB-S2: The Second Generation Standard for Satellite Broadband Services,” Proc. IEEE, vol. 94, no. 1, pp. 210–227, 2006.",
        "[3] “Information Technology — Generic Coding of Moving Pictures and Associated Audio Information — Part 1: Systems (MPEG-2 Transport Stream),” ISO/IEC 13818-1:2022, 2022.",
        "[4] “Digital Video Broadcasting (DVB); Generic Stream Encapsulation (GSE); Part 1: Protocol,” ETSI TS 102 606-1 V1.2.1, 2014.",
        "[5] P. L. Luisi et al., “Empirical Evaluation of Digital Video Broadcasting Systems and Transport Stream Analysis,” IEEE Trans. Broadcast., vol. 66, no. 2, pp. 431–444, 2020.",
        "[6] D. Minoli, Innovations in Satellite Communications and the Global Information Infrastructure. Hoboken, NJ: Wiley, 2015.",
        "[7] E. Casini et al., “DVB-S2 Modern Modulation and Coding Techniques for Satellite Broadcast,” IEEE Commun. Mag., vol. 42, no. 11, pp. 146–156, 2004.",
        "[8] B. Sklar, Digital Communications: Fundamentals and Applications, 2nd ed. Upper Saddle River, NJ: Prentice Hall, 2001.",
        "[9] G. Fairhurst and B. Collini-Nocker, “Generic Stream Encapsulation (GSE) for DVB-S2: Design and Evaluation,” Int. J. Satell. Commun. Netw., vol. 28, no. 5–6, pp. 287–305, 2010.",
        "[10] G. Fairhurst and B. Collini-Nocker, “Unidirectional Lightweight Encapsulation (ULE),” RFC 4326, 2005.",
        "[11] “Measurement Guidelines for DVB Systems,” ETSI TR 101 290 V1.4.1, 2020.",
        "[12] “Specification for Service Information (SI) in DVB Systems,” ETSI EN 300 468 V1.17.1, 2021.",
        "[13] V. Chandola et al., “Anomaly Detection: A Survey,” ACM Comput. Surv., vol. 41, no. 3, pp. 1–58, 2009.",
        "[14] M. A. F. Pimentel et al., “A Review of Novelty Detection,” Signal Process., vol. 99, pp. 215–249, 2014.",
        "[15] F. T. Liu, K. M. Ting, and Z.-H. Zhou, “Isolation Forest,” in Proc. IEEE ICDM, 2008, pp. 413–422.",
        "[16] F. T. Liu, K. M. Ting, and Z.-H. Zhou, “Isolation-Based Anomaly Detection,” ACM TKDD, vol. 6, no. 1, pp. 1–39, 2012.",
        "[17] R. S. Baggio et al., “Network Traffic Anomaly Detection Using Unsupervised Learning Models,” IEEE Access, vol. 9, pp. 15982–15998, 2021.",
        "[18] D. Arthur and S. Vassilvitskii, “k-means++: The Advantages of Careful Seeding,” in Proc. ACM-SIAM SODA, 2007, pp. 1027–1035.",
        "[19] M. Ester et al., “A Density-Based Algorithm for Discovering Clusters in Large Spatial Databases with Noise,” in Proc. KDD, 1996, pp. 226–231.",
        "[20] C. E. Shannon, “A Mathematical Theory of Communication,” Bell Syst. Tech. J., vol. 27, no. 3, pp. 379–423, 1948."
    ]

    for ref in references_data:
        p_ref = doc.add_paragraph()
        p_ref.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p_ref.paragraph_format.left_indent = Inches(0.18)
        p_ref.paragraph_format.first_line_indent = Inches(-0.18)
        p_ref.paragraph_format.space_after = Pt(2)
        r = p_ref.add_run(ref)
        r.font.name = 'Times New Roman'
        r.font.size = Pt(7.8)

    output_path = "07_DOCUMENTATION/RESEARCH_PAPER/PRJ_111_Research_Paper_4Pages.docx"
    doc.save(output_path)
    print(f"Successfully generated: {output_path} (Size: {os.path.getsize(output_path)} bytes)")

if __name__ == "__main__":
    build_paper_4pages()
