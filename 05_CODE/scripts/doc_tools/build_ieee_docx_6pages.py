import re
"""
build_ieee_docx_6pages.py
Generates the PRJ_111 IEEE-style TWO-COLUMN Microsoft Word (.docx) document
calibrated for IEEE conference submission.
Constraints:
- No bullet points (uses numbered or alphabetical lists).
- No UI screenshots (retains the system architecture diagram Fig. 1).
- Updated references [1], [2], [3] (Liao & Chen, Izumi et al., Cao et al.) with all 20 citations aligned.
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
    tcMar = parse_xml(
        f'<w:tcMar {nsdecls("w")}>'
        f'  <w:top w:w="{top}" w:type="dxa"/>'
        f'  <w:bottom w:w="{bottom}" w:type="dxa"/>'
        f'  <w:left w:w="{left}" w:type="dxa"/>'
        f'  <w:right w:w="{right}" w:type="dxa"/>'
        f'</w:tcMar>'
    )
    tcPr.append(tcMar)

def set_ieee_table_borders(table):
    tblPr = table._tbl.tblPr
    for b in tblPr.xpath('./w:tblBorders'):
        tblPr.remove(b)
    borders_xml = parse_xml(
        f'<w:tblBorders {nsdecls("w")}>'
        f'  <w:top w:val="single" w:sz="8" w:space="0" w:color="000000"/>'
        f'  <w:bottom w:val="single" w:sz="8" w:space="0" w:color="000000"/>'
        f'  <w:insideH w:val="single" w:sz="4" w:space="0" w:color="D3D3D3"/>'
        f'  <w:insideV w:val="none"/>'
        f'  <w:left w:val="none"/>'
        f'  <w:right w:val="none"/>'
        f'</w:tblBorders>'
    )
    tblPr.append(borders_xml)

def add_formatted_runs(paragraph, text, base_font_size=Pt(10.0)):
    tokens = re.split(r'(G\(x\) = x\^8 \+ x\^7 \+ x\^6 \+ x\^4 \+ x\^2 \+ 1|s\(x\) = 1 / \(1 \+ e\^\(8\.0·d\(x\)\)\)|H\(W_i\) = max\(0\.0, 100\.0 \+ ∑ ΔH\)|H = \(1/N\) ∑ H\(W_i\)|H_PID = - ∑ p_k log_2 p_k|z_bounded = clamp\(\(x_\(i,j\) - μ_j\) / max\(σ_j, ε_j\), -20\.0, \+20\.0\)|s\(x\) ≥ 0\.5000|d\(x\) ∈ R|x_i ∈ R\^m|2\^12|O\(n log n\)|roll-off α)', text)
    for token in tokens:
        if not token:
            continue
        if token == "G(x) = x^8 + x^7 + x^6 + x^4 + x^2 + 1":
            rG = paragraph.add_run("G")
            rG.font.italic = True
            rG.font.name = "Times New Roman"
            rG.font.size = base_font_size
            r_lp = paragraph.add_run("(")
            r_lp.font.name = "Times New Roman"
            r_lp.font.size = base_font_size
            rx1 = paragraph.add_run("x")
            rx1.font.italic = True
            rx1.font.name = "Times New Roman"
            rx1.font.size = base_font_size
            r_eq = paragraph.add_run(") = ")
            r_eq.font.name = "Times New Roman"
            r_eq.font.size = base_font_size
            for pwr in [8, 7, 6, 4, 2]:
                rx = paragraph.add_run("x")
                rx.font.italic = True
                rx.font.name = "Times New Roman"
                rx.font.size = base_font_size
                rsup = paragraph.add_run(str(pwr))
                rsup.font.superscript = True
                rsup.font.name = "Times New Roman"
                rsup.font.size = base_font_size
                rplus = paragraph.add_run(" + ")
                rplus.font.name = "Times New Roman"
                rplus.font.size = base_font_size
            r1 = paragraph.add_run("1")
            r1.font.name = "Times New Roman"
            r1.font.size = base_font_size
        elif token == "s(x) = 1 / (1 + e^(8.0·d(x)))":
            rs = paragraph.add_run("s")
            rs.font.italic = True
            rs.font.name = "Times New Roman"
            rs.font.size = base_font_size
            r_lp = paragraph.add_run("(")
            r_lp.font.name = "Times New Roman"
            r_lp.font.size = base_font_size
            rx = paragraph.add_run("x")
            rx.font.italic = True
            rx.font.name = "Times New Roman"
            rx.font.size = base_font_size
            r_rest = paragraph.add_run(") = 1 / (1 + ")
            r_rest.font.name = "Times New Roman"
            r_rest.font.size = base_font_size
            r_euler = paragraph.add_run("e")
            r_euler.font.italic = True
            r_euler.font.name = "Times New Roman"
            r_euler.font.size = base_font_size
            rsup = paragraph.add_run("8.0·d(x)")
            rsup.font.superscript = True
            rsup.font.name = "Times New Roman"
            rsup.font.size = base_font_size
            r_cp = paragraph.add_run(")")
            r_cp.font.name = "Times New Roman"
            r_cp.font.size = base_font_size
        elif token == "H(W_i) = max(0.0, 100.0 + ∑ ΔH)":
            rH = paragraph.add_run("H")
            rH.font.italic = True
            rH.font.name = "Times New Roman"
            rH.font.size = base_font_size
            r_lp = paragraph.add_run("(")
            r_lp.font.name = "Times New Roman"
            r_lp.font.size = base_font_size
            rW = paragraph.add_run("W")
            rW.font.italic = True
            rW.font.name = "Times New Roman"
            rW.font.size = base_font_size
            ri = paragraph.add_run("i")
            ri.font.subscript = True
            ri.font.name = "Times New Roman"
            ri.font.size = base_font_size
            r_rest = paragraph.add_run(") = max(0.0, 100.0 + ∑ ΔH)")
            r_rest.font.name = "Times New Roman"
            r_rest.font.size = base_font_size
        elif token == "H = (1/N) ∑ H(W_i)":
            rH = paragraph.add_run("H")
            rH.font.italic = True
            rH.font.name = "Times New Roman"
            rH.font.size = base_font_size
            r_mid = paragraph.add_run(" = (1/")
            r_mid.font.name = "Times New Roman"
            r_mid.font.size = base_font_size
            rN = paragraph.add_run("N")
            rN.font.italic = True
            rN.font.name = "Times New Roman"
            rN.font.size = base_font_size
            r_sum = paragraph.add_run(") ∑ ")
            r_sum.font.name = "Times New Roman"
            r_sum.font.size = base_font_size
            rH2 = paragraph.add_run("H")
            rH2.font.italic = True
            rH2.font.name = "Times New Roman"
            rH2.font.size = base_font_size
            r_lp = paragraph.add_run("(")
            r_lp.font.name = "Times New Roman"
            r_lp.font.size = base_font_size
            rW = paragraph.add_run("W")
            rW.font.italic = True
            rW.font.name = "Times New Roman"
            rW.font.size = base_font_size
            ri = paragraph.add_run("i")
            ri.font.subscript = True
            ri.font.name = "Times New Roman"
            ri.font.size = base_font_size
            r_cp = paragraph.add_run(")")
            r_cp.font.name = "Times New Roman"
            r_cp.font.size = base_font_size
        elif token == "H_PID = - ∑ p_k log_2 p_k":
            rH = paragraph.add_run("H")
            rH.font.italic = True
            rH.font.name = "Times New Roman"
            rH.font.size = base_font_size
            rpid = paragraph.add_run("PID")
            rpid.font.subscript = True
            rpid.font.name = "Times New Roman"
            rpid.font.size = base_font_size
            r_eq = paragraph.add_run(" = - ∑ ")
            r_eq.font.name = "Times New Roman"
            r_eq.font.size = base_font_size
            rp1 = paragraph.add_run("p")
            rp1.font.italic = True
            rp1.font.name = "Times New Roman"
            rp1.font.size = base_font_size
            rk1 = paragraph.add_run("k")
            rk1.font.subscript = True
            rk1.font.name = "Times New Roman"
            rk1.font.size = base_font_size
            r_log = paragraph.add_run(" log")
            r_log.font.name = "Times New Roman"
            r_log.font.size = base_font_size
            r2 = paragraph.add_run("2")
            r2.font.subscript = True
            r2.font.name = "Times New Roman"
            r2.font.size = base_font_size
            r_sp = paragraph.add_run(" ")
            r_sp.font.name = "Times New Roman"
            r_sp.font.size = base_font_size
            rp2 = paragraph.add_run("p")
            rp2.font.italic = True
            rp2.font.name = "Times New Roman"
            rp2.font.size = base_font_size
            rk2 = paragraph.add_run("k")
            rk2.font.subscript = True
            rk2.font.name = "Times New Roman"
            rk2.font.size = base_font_size
        elif token == "z_bounded = clamp((x_(i,j) - μ_j) / max(σ_j, ε_j), -20.0, +20.0)":
            rz = paragraph.add_run("z")
            rz.font.italic = True
            rz.font.name = "Times New Roman"
            rz.font.size = base_font_size
            rb = paragraph.add_run("bounded")
            rb.font.subscript = True
            rb.font.name = "Times New Roman"
            rb.font.size = base_font_size
            r_cl = paragraph.add_run(" = clamp((")
            r_cl.font.name = "Times New Roman"
            r_cl.font.size = base_font_size
            rx = paragraph.add_run("x")
            rx.font.italic = True
            rx.font.name = "Times New Roman"
            rx.font.size = base_font_size
            rij = paragraph.add_run("i,j")
            rij.font.subscript = True
            rij.font.name = "Times New Roman"
            rij.font.size = base_font_size
            r_mu = paragraph.add_run(" - μ")
            r_mu.font.name = "Times New Roman"
            r_mu.font.size = base_font_size
            rj1 = paragraph.add_run("j")
            rj1.font.subscript = True
            rj1.font.name = "Times New Roman"
            rj1.font.size = base_font_size
            r_mx = paragraph.add_run(") / max(σ")
            r_mx.font.name = "Times New Roman"
            r_mx.font.size = base_font_size
            rj2 = paragraph.add_run("j")
            rj2.font.subscript = True
            rj2.font.name = "Times New Roman"
            rj2.font.size = base_font_size
            r_ep = paragraph.add_run(", ε")
            r_ep.font.name = "Times New Roman"
            r_ep.font.size = base_font_size
            rj3 = paragraph.add_run("j")
            rj3.font.subscript = True
            rj3.font.name = "Times New Roman"
            rj3.font.size = base_font_size
            r_end = paragraph.add_run("), -20.0, +20.0)")
            r_end.font.name = "Times New Roman"
            r_end.font.size = base_font_size
        elif token == "s(x) ≥ 0.5000":
            r1 = paragraph.add_run("s")
            r1.font.italic = True
            r1.font.name = "Times New Roman"
            r1.font.size = base_font_size
            r2 = paragraph.add_run("(x) ≥ 0.5000")
            r2.font.name = "Times New Roman"
            r2.font.size = base_font_size
        elif token == "2^12":
            r1 = paragraph.add_run("2")
            r1.font.name = "Times New Roman"
            r1.font.size = base_font_size
            r2 = paragraph.add_run("12")
            r2.font.superscript = True
            r2.font.name = "Times New Roman"
            r2.font.size = base_font_size
        elif token == "O(n log n)":
            r1 = paragraph.add_run("O(")
            r1.font.name = "Times New Roman"
            r1.font.size = base_font_size
            r2 = paragraph.add_run("n")
            r2.font.italic = True
            r2.font.name = "Times New Roman"
            r2.font.size = base_font_size
            r3 = paragraph.add_run(" log ")
            r3.font.name = "Times New Roman"
            r3.font.size = base_font_size
            r4 = paragraph.add_run("n")
            r4.font.italic = True
            r4.font.name = "Times New Roman"
            r4.font.size = base_font_size
            r5 = paragraph.add_run(")")
            r5.font.name = "Times New Roman"
            r5.font.size = base_font_size
        elif token == "roll-off α":
            r1 = paragraph.add_run("roll-off ")
            r1.font.name = "Times New Roman"
            r1.font.size = base_font_size
            r2 = paragraph.add_run("α")
            r2.font.italic = True
            r2.font.name = "Times New Roman"
            r2.font.size = base_font_size
        else:
            r = paragraph.add_run(token)
            r.font.name = "Times New Roman"
            r.font.size = base_font_size

def build_paper_6pages():
    doc = Document()

    # ----------------------------------------------------
    # SECTION 1: Page Setup (US Letter, 0.65 in margins)
    # ----------------------------------------------------
    sec1 = doc.sections[0]
    sec1.page_width = Inches(8.5)
    sec1.page_height = Inches(11.0)
    sec1.top_margin = Inches(0.65)
    sec1.bottom_margin = Inches(0.65)
    sec1.left_margin = Inches(0.65)
    sec1.right_margin = Inches(0.65)

    # Helper styling closures
    def add_sec_h1(title):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(8)
        p.paragraph_format.space_after = Pt(3)
        p.paragraph_format.keep_with_next = True
        r = p.add_run(title.upper())
        r.font.name = 'Times New Roman'
        r.font.size = Pt(10.0)
        r.font.bold = True
        return p

    def add_sec_h2(title):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p.paragraph_format.space_before = Pt(6)
        p.paragraph_format.space_after = Pt(2)
        p.paragraph_format.keep_with_next = True
        r = p.add_run(title)
        r.font.name = 'Times New Roman'
        r.font.size = Pt(10.0)
        r.font.bold = True
        r.font.italic = True
        return p


    def add_body_p(text):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p.paragraph_format.first_line_indent = Inches(0.18)
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(2.0)
        p.paragraph_format.line_spacing = 1.0
        add_formatted_runs(p, text, base_font_size=Pt(10.0))
        return p

    def add_fig_caption(num, title):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p.paragraph_format.space_before = Pt(2)
        p.paragraph_format.space_after = Pt(5)
        r_lbl = p.add_run(f"Fig. {num}. ")
        r_lbl.font.name = 'Times New Roman'
        r_lbl.font.size = Pt(8.0)
        r_lbl.font.bold = True
        r_txt = p.add_run(title)
        r_txt.font.name = 'Times New Roman'
        r_txt.font.size = Pt(8.0)
        return p

    def add_tbl_caption(num_roman, title):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(6)
        p.paragraph_format.space_after = Pt(2)
        p.paragraph_format.keep_with_next = True
        r_lbl = p.add_run(f"TABLE {num_roman}\n")
        r_lbl.font.name = 'Times New Roman'
        r_lbl.font.size = Pt(8.0)
        r_lbl.font.bold = True
        r_txt = p.add_run(title.upper())
        r_txt.font.name = 'Times New Roman'
        r_txt.font.size = Pt(8.0)
        r_txt.font.bold = True
        return p

    # Title & Metadata (1 Column)
    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title.paragraph_format.space_before = Pt(0)
    p_title.paragraph_format.space_after = Pt(6)
    r_title = p_title.add_run("Development of a Multi-Format DVB-S2 Receiver Output Stream Analyzer with Anomaly Detection and Diagnostic Reporting")
    r_title.font.name = 'Times New Roman'
    r_title.font.size = Pt(24.0)
    r_title.font.bold = True

    # Authors Table (3 Authors side by side)
    tbl_auth = doc.add_table(rows=1, cols=3)
    tbl_auth.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl_auth.autofit = False
    auth_widths = [Inches(2.4), Inches(2.4), Inches(2.4)]
    for idx, w in enumerate(auth_widths):
        tbl_auth.columns[idx].width = w

    authors = [
        ("Y Vengala Rao", "Roll No: 20231COM0001\nDept. of Computer Science & Eng.\nPresidency University, India"),
        ("Sk Samad", "Roll No: 20231COM0031\nDept. of Computer Science & Eng.\nPresidency University, India"),
        ("C Rakeshwar", "Roll No: 20231COM0008\nDept. of Computer Science & Eng.\nPresidency University, India")
    ]

    for c_idx, (name, affil) in enumerate(authors):
        cell = tbl_auth.cell(0, c_idx)
        cell.width = auth_widths[c_idx]
        set_cell_margins(cell, 10, 10, 10, 10)
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_after = Pt(2)
        r_name = p.add_run(name + "\n")
        r_name.font.name = 'Times New Roman'
        r_name.font.size = Pt(10)
        r_name.font.bold = True
        r_aff = p.add_run(affil)
        r_aff.font.name = 'Times New Roman'
        r_aff.font.size = Pt(9.0)
        r_aff.font.italic = True

    # ----------------------------------------------------
    # SECTION 2: Two Columns Layout (Abstract + Index Terms + Body)
    # ----------------------------------------------------
    sec2 = doc.add_section(WD_SECTION.CONTINUOUS)
    set_section_cols(sec2, num=2, space=360)

    # Abstract
    p_abs = doc.add_paragraph()
    p_abs.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p_abs.paragraph_format.first_line_indent = Inches(0.18)
    p_abs.paragraph_format.space_before = Pt(8)
    p_abs.paragraph_format.space_after = Pt(3)
    r_abshdr = p_abs.add_run("Abstract—")
    r_abshdr.font.name = 'Times New Roman'
    r_abshdr.font.size = Pt(9)
    r_abshdr.font.bold = True
    r_abstxt = p_abs.add_run(
        "Digital Video Broadcasting via Satellite (DVB-S2) establishes the dominant physical and link framing architecture for contemporary broadband "
        "satellite communications. Post-demodulator digital receiver bitstreams exhibit structural heterogeneity, spanning MPEG-2 Transport Streams "
        "(MPEG-TS), Generic Stream Encapsulation (GSE), and native DVB-S2 Baseband Frames (BBFrames). Field diagnostic workflows are frequently hampered "
        "by brittle protocol sniffers, uncalibrated cross-layer assertions, and the absence of ground-truth anomaly annotations. This paper presents "
        "PRJ_111, an integrated software suite for multi-format DVB-S2 receiver output stream analysis, unsupervised anomaly detection, and diagnostic "
        "reporting. PRJ_111 ingests raw digital bitstreams, executes deterministic framing parsers, extracts unified physical invariants, and deploys "
        "an unsupervised Isolation Forest calibrated with a logistic decision boundary (s ≥ 0.5000). The pipeline features seven integrated engines: "
        "deterministic stream health scoring (F1), unsupervised anomaly detection (F2), multiplex pattern and entropy analysis (F3), spatial timeline "
        "activity rendering (F4), bounded Z-score diagnostic explanation (F5), semantically guarded stream comparison (F6), and automated diagnostic "
        "reporting (F7). Empirical verification across authentic off-air satellite captures demonstrates 100.0% framing compliance on valid captures, "
        "deterministic detection of sync-byte loss and continuity errors on corrupted streams, format-isolated anomaly boundary identification, and "
        "100.0% pass rate across 304 automated regression unit and integration tests."
    )
    r_abstxt.font.name = 'Times New Roman'
    r_abstxt.font.size = Pt(9)

    # Index Terms
    p_idx = doc.add_paragraph()
    p_idx.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p_idx.paragraph_format.first_line_indent = Inches(0.18)
    p_idx.paragraph_format.space_before = Pt(0)
    p_idx.paragraph_format.space_after = Pt(6)
    r_idxhdr = p_idx.add_run("Index Terms—")
    r_idxhdr.font.name = 'Times New Roman'
    r_idxhdr.font.size = Pt(9)
    r_idxhdr.font.bold = True
    r_it = p_idx.add_run("Anomaly detection, Baseband frame, Digital video broadcasting, DVB-S2, Feature extraction, Generic stream encapsulation, Isolation Forest, MPEG transport stream, Receiver output analysis, Stream analysis.")
    r_it.font.name = 'Times New Roman'
    r_it.font.size = Pt(9)
    r_it.font.italic = True

    add_sec_h1("I. Introduction")
    add_body_p(
        "In contemporary broadband satellite communications, physical-layer signaling and frame boundary synchronization under impaired channel conditions require robust joint detection methods as established by Liao et al. [1]. "
        "Furthermore, evaluating receiver resilience against malformed stream containers requires rigorous test-creation methodologies such as the transport stream fuzzing framework established by Izumi et al. [2]. "
        "Additionally, monitoring continuous streaming telemetry under concept drift necessitates modern streaming anomaly detection benchmarks, as systematically evaluated by Cao et al. [3]. "
        "Satellite links operating under the DVB-S2 standard [4] handle massive volumes of broadcast video, broadband Internet traffic, and corporate trunking. "
        "Following carrier recovery, matched filtering, and dual-stage forward error correction (FEC) using inner LDPC and outer BCH codes [8], the demodulator delivers a raw digital stream to host processing hardware."
    )
    add_body_p(
        "In operational ground stations, this post-demodulator digital output is delivered in one of three distinct framing layers:\n"
        "(1) MPEG-2 Transport Stream (MPEG-TS): The broadcast container standard [5], packaging multiplexed data into fixed 188-byte packets synchronized "
        "by 0x47 sync octets, with 13-bit Program Identifiers (PIDs) and 4-bit cyclic continuity counters.\n"
        "(2) Generic Stream Encapsulation (GSE): The second-generation IP encapsulation protocol [6], wrapping variable-length network datagrams (IPv4, IPv6) "
        "with 2-bit fragmentation headers and CRC-32 checksums, eliminating transport stream padding overhead.\n"
        "(3) DVB-S2 Baseband Frames (BBFrame): The native physical-link container [4], containing an 80-bit baseband header, Mode Adaptation flags "
        "(MATYPE), a Data Field Length (DFL) indicator, and an 8-bit CRC."
    )
    add_body_p(
        "Troubleshooting these streams during station commissioning or downlink outages is frequently challenging [9]. General-purpose packet sniffers "
        "like Wireshark assume Ethernet encapsulation and stumble on raw, unencapsulated transport streams [10]. Commercial broadcast monitors "
        "parse MPEG-TS effectively, but lack native parsing for GSE packets and baseband frames [9]. Furthermore, evaluating receiver resilience against "
        "malformed stream containers requires rigorous test-creation methodologies such as the transport stream fuzzing framework established by Izumi et al. [2]."
    )
    add_body_p(
        "Ground station telemetry diagnostics face three recurring structural difficulties:\n"
        "(1) Brittle Parsers and Misidentified Files: Raw captures arrive as unlabeled binary files (.ts, .bin, .pcap). File-extension checks "
        "frequently fail, and fragile decoders crash upon encountering corrupted sync octets or dropped packets.\n"
        "(2) Cross-Format Semantic Conflation: Directly contrasting packet counts between 188-byte MPEG-TS packets and multi-kilobyte Baseband Frames "
        "produces invalid diagnostic deductions during multi-feed audits.\n"
        "(3) Speculative Physical Inferences: Monitoring tools frequently synthesize fictitious clock axes or infer physical-layer link conditions "
        "(such as attributing bit errors to atmospheric attenuation) without access to demodulator baseband IQ constellations or signal-to-noise ratios."
    )
    add_body_p(
        "To resolve these challenges, this project develops PRJ_111, an offline software engineering workstation for multi-format DVB-S2 receiver output stream "
        "analysis. PRJ_111 incorporates a seven-feature analytical pipeline (F1–F7) that autonomously detects stream formats from binary headers, parses units "
        "deterministically, evaluates stream health (F1), discovers structural anomalies with an unsupervised Isolation Forest (F2), analyzes multiplex entropy (F3), "
        "renders byte-indexed activity timelines (F4), explains anomaly drivers with clamped Z-scores (F5), enforces cross-format comparison semantic shields (F6), "
        "and exports comprehensive diagnostic reports (F7)."
    )

    add_sec_h1("II. Related Work")
    add_body_p(
        "The DVB-S2 standard (ETSI EN 302 307-1) governs satellite framing and channel coding, introducing Adaptive Coding and Modulation (ACM) alongside native "
        "baseband containers [4]. Morello et al. [8] evaluated the physical-layer mechanisms of DVB-S2, demonstrating how user data packets are packed into "
        "baseband structures safeguarded by concatenated inner LDPC and outer BCH codes. Casini et al. [11] explored modulation schemes spanning QPSK through "
        "32-APSK, establishing operational constraints for roll-off factors and Data Field Length (DFL) bit allocation. For physical-layer signaling and frame boundary "
        "synchronization under low-SNR reception, Liao et al. [1] developed an efficient joint detection method for DVB-S2 signaling codes."
    )
    add_body_p(
        "For network-layer packet distribution, Fairhurst et al. [12] formulated Generic Stream Encapsulation (ETSI TS 102 606-1) [6] as a low-overhead successor "
        "to Multi-Protocol Encapsulation (MPE over MPEG-TS) and Unidirectional Lightweight Encapsulation (ULE, RFC 4326) [13]. GSE standardizes variable-length protocol data units "
        "carrying native IP datagrams with per-fragment CRC-32 protection, eliminating transport stream padding overhead. Digital television broadcast transmission continues "
        "to rely upon the MPEG-2 Transport Stream standard (ISO/IEC 13818-1) [5]. Measurement guidelines for broadcast verification are codified in ETSI TR 101 290 [7], specifying "
        "Priority-1 operational parameters: synchronization loss, Transport Error Indicator (TEI) flags, and Continuity Counter (CC) sequence violations."
    )
    add_body_p(
        "Luisi et al. [9] evaluated satellite broadcast monitoring tools, observing that while specialized hardware instruments accurately flag ETSI TR 101 290 Priority-1 defects, "
        "they generally lack native parsing capabilities for emerging IP encapsulation schemes (GSE and BBFrames) output by contemporary broadband receivers. Minoli [10] surveyed "
        "network packet inspection software, highlighting that general-purpose sniffers treat raw stream dumps as opaque binary blobs unless enveloped in standard network capture "
        "headers. To systematically expose vulnerability and boundary errors in digital TV receivers, Izumi et al. [2] pioneered a fuzzing-based test-creation methodology that mutates "
        "transport stream headers and payloads. PRJ_111 adapts these concepts to incorporate a deterministic fault injection module for empirical parser validation."
    )
    add_body_p(
        "Surveys by Chandola et al. [14] and Pimentel et al. [15] trace the evolution of telemetry anomaly detection. Traditional statistical monitoring depends on rigid "
        "thresholds, which struggle in statistically multiplexed channels where instantaneous bitrates fluctuate dynamically. Supervised classification demands extensive "
        "ground-truth anomaly annotations [14]. In live satellite telemetry, labeled anomaly corpora are practically nonexistent. To analyze unannotated streaming telemetry, "
        "Liu et al. [16], [17] introduced the Isolation Forest algorithm, constructing ensembles of random isolation trees (iTrees). Abnormal instances require fewer random partitions "
        "to isolate, yielding significantly shorter average tree paths [16]. Baggio et al. [18] proved that Isolation Forest achieves linear computational efficiency (O(n log n)) "
        "and robust outlier sensitivity compared to distance or density-based clustering models such as k-means++ [19] and DBSCAN [20]. Furthermore, Cao et al. [3] established "
        "a systematic benchmark for streaming anomaly detection under continuous concept drift, validating that windowed tree ensembles effectively capture evolving temporal "
        "anomalies without requiring external ground truth. PRJ_111 grounds its streaming anomaly detection on these windowed principles."
    )

    add_sec_h1("III. System Architecture and Workstation Design")
    add_body_p(
        "We designed PRJ_111 around a clean six-stage pipeline, illustrated in Fig. 1. The software takes raw binary captures from satellite receiver outputs, decodes the container syntax, extracts physical invariants, executes analytical engines (F1–F3), renders activity timelines (F4), explains anomalies with bounded Z-scores (F5), performs semantically guarded comparisons (F6), and generates structured diagnostic reports (F7).\n"
        "PRJ_111 is implemented in Python 3.12 as a local engineering workstation with zero external cloud or proprietary licensing dependencies:\n"
        "(a) Backend Core and Ingestion Engine: Pure Python modular architecture (dvbs2_analyzer/ingestion/, parsers/, features/, analysis/, streaming/). Supports multi-mode stream "
        "processing: Standard in-memory sequential parsing, 64 KB block-buffered Chunked streaming for large continuous captures, and High-Throughput zero-copy memory-mapped (mmap) processing.\n"
        "(b) Machine Learning and Attribution Layer: Scikit-learn (IsolationForest) coupled with NumPy and SciPy for numerical vector operations, windowed temporal scoring, and bounded Z-score feature attribution.\n"
        "(c) Controlled Fault-Injection Benchmark: Multi-format synthetic mutation framework inspired by Izumi et al. [2] (TEI corruption, CC discontinuities, PDU truncation, BBFrame CRC-8 corruption) "
        "enabling empirical before-vs-after anomaly sensitivity scoring.\n"
        "(d) HTTP Gateway and Workstation: Multi-threaded native Python HTTP server (ThreadingHTTPServer) exposing a RESTful JSON API (/api/status, /api/analyze, /api/compare, "
        "/api/upload, /api/export, /api/fault-inject) and Single-Page Application (SPA) dashboard.\n"
        "(e) Printable Laboratory Certification: Standalone laboratory diagnostic test sheet export with evaluator sign-off blocks."
    )

    add_sec_h1("IV. Multi-Format Stream Processing")
    add_body_p(
        "The parsing layer operates directly on raw binary stream captures, providing modular decoders tailored to each standard. Format selection is governed by a content-aware format sniffer:\n"
        "(1) MPEG-2 Transport Stream (MPEG-TS): The MPEG-TS parser processes continuous 188-byte containers specified in ISO/IEC 13818-1 [5]. Validates 0x47 sync cadence, "
        "flags Transport Error Indicator (TEI) bits, extracts 13-bit Program Identifiers (PIDs), and tracks 4-bit cyclic Continuity Counters (CC) per PID.\n"
        "(2) Generic Stream Encapsulation (GSE): Decodes variable-size protocol data units adhering to ETSI TS 102 606-1 [6]. Parses 2-bit start/end fragmentation flags, "
        "12-bit length field (≤ 4,095 bytes payload), 16-bit EtherType (0x0800 IPv4), label addressing, and CRC-32 syndrome validation.\n"
        "(3) DVB-S2 Baseband Frames (BBFrame): Decodes native baseband frames specified in ETSI EN 302 307-1 [4] and evaluated by Liao et al. [1]. Validates 80-bit headers via CRC-8 "
        "(G(x) = x^8 + x^7 + x^6 + x^4 + x^2 + 1), extracts MATYPE-1/2 (SIS/MIS, ACM/CCM, roll-off α), and measures Data Field Length (DFL ∈ [216, 10000] bits)."
    )

    # ----------------------------------------------------
    # SECTION 3: Full-Width Architecture Diagram (Fig. 1)
    # ----------------------------------------------------
    sec3 = doc.add_section(WD_SECTION.CONTINUOUS)
    set_section_cols(sec3, num=1)

    fig1_path = "07_DOCUMENTATION/RESEARCH_PAPER/assets/architecture_diagram.png"
    if os.path.exists(fig1_path):
        p_img1 = doc.add_paragraph()
        p_img1.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img1.paragraph_format.space_before = Pt(2)
        p_img1.paragraph_format.space_after = Pt(2)
        r_img1 = p_img1.add_run()
        r_img1.add_picture(fig1_path, width=Inches(6.0))
        add_fig_caption(1, "End-to-End Architectural Pipeline of the PRJ_111 DVB-S2 Receiver Output Stream Analyzer (Stages 1 through 6).")

    # ----------------------------------------------------
    # SECTION 4: Two Columns Body Continued
    # ----------------------------------------------------
    sec4 = doc.add_section(WD_SECTION.CONTINUOUS)
    set_section_cols(sec4, num=2, space=360)

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
        r.font.size = Pt(8.0)
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
            r.font.size = Pt(8.0)

    add_sec_h1("V. Feature Engineering and Analytical Pipeline")
    add_body_p(
        "Telemetry is bifurcated into physical invariants (CommonMetrics) and native format-specific metrics (TSMetrics, GSEMetrics, BBFrameMetrics):\n"
        "(1) Feature F1 (Stream Health Analysis): Implements transparent threshold-driven deductive scoring from a 100.0% baseline based on ETSI TR 101 290 P1 criteria [7]: "
        "H(W_i) = max(0.0, 100.0 + ∑ ΔH). Overall health H is the arithmetic mean across all N spatial windows: H = (1/N) ∑ H(W_i). Categorized into HEALTHY (H ≥ 99.0%), "
        "WARNING (80.0% ≤ H < 99.0%), and CRITICAL (H < 80.0%).\n"
        "(2) Feature F2 (AI Anomaly Detection): Instantiates an ensemble of T = 100 isolation trees (n_estimators=100, contamination=0.05) [16], [17]. Following streaming "
        "evaluation benchmarks from Cao et al. [3], decision scores are evaluated over window-partitioned streams and mapped through a centered logistic sigmoid: "
        "s(x) = 1 / (1 + e^(8.0·d(x))). Flagged anomalous if s(x) ≥ 0.5000.\n"
        "(3) Feature F3 (Pattern and Entropy Analysis): Evaluates individual PID shares and Shannon multiplex entropy: H_PID = - ∑ p_k log_2 p_k.\n"
        "(4) Feature F4 (Spatial Activity Timeline): Charts rolling health, anomaly scores, and payload density indexed strictly by physical byte offsets [B_start, B_end] "
        "and container indices, eliminating fabricated clock time axes.\n"
        "(5) Feature F5 (Diagnostic Anomaly Explanation): Attributes flagged anomalies to specific metric drivers using bounded Z-scores: "
        "z_bounded = clamp((x_(i,j) - μ_j) / max(σ_j, ε_j), -20.0, +20.0).\n"
        "(6) Feature F6 (Semantic Comparison Engine): Protects cross-format comparisons via an automated semantic barrier. Audits 2 comparable physical invariants "
        "(total_payload_bytes, integrity_ratio) while shielding 9 format-incompatible framing metrics.\n"
        "(7) Feature F7 (Automatic Reporting): Synthesizes diagnostics into JSON, Markdown, HTML, and CSV organized under a tripartite epistemology "
        "(OBSERVED_FACT, STATISTICAL_FINDING, ENGINEERING_INTERPRETATION)."
    )

    add_sec_h1("VI. Experimental Results and Discussion")
    add_body_p("The system was evaluated against four authoritative satellite captures in 01_RAW_DATA/ (Tables II through V).")

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
        r.font.size = Pt(8.0)
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
            r.font.size = Pt(8.0)

    add_body_p(
        "(1) MPEG-TS Health Verification: Clean sample.ts achieved 100.0% sync integrity and 100.0% health across 18,176 packets (3,267,305 B payload). "
        "The corrupted stream dropped 8 unaligned packets, yielding 18,168 packets with 4 TEI errors in Window 0, achieving 99.67% average health (HEALTHY).\n"
        "(2) GSE Protocol Results: Evaluated 14 PDUs (9,324 B, 8,764 B payload), comprising 6 unfragmented (42.9%) and 8 fragmented PDUs (57.1%). Passed 100% CRC-32 checksums with 100.0% health.\n"
        "(3) BBFrame Transmission: Evaluated 4,309 frames (2,349,376 B, 1,958,826 B payload). Verified 100.0% CRC-8 checks, 100% ACM, and modal DFL of 2,992 bits (85.82% share).\n"
        "(4) Isolation Forest Findings: Consistently flagged container volume truncation at stream termination boundaries (Window 90 in TS, Window 4 in GSE, Window 86 in BBFrame) and localized multiplex burst concentrations.\n"
        "(5) Cross-Format Comparison Audit: Comparing TS against BBFrame revealed a -40.05% payload delta (3,267,305 B vs 1,958,826 B, SUBSTANTIAL) and identical 1.0000 integrity ratio (NEGLIGIBLE), with 9 framing fields shielded."
    )

    # Table III (GSE)
    add_tbl_caption("III", "GSE Encapsulation & Protocol Results")
    tbl3 = doc.add_table(rows=8, cols=3)
    tbl3.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl3.autofit = False
    set_ieee_table_borders(tbl3)
    col3_widths = [Inches(1.3), Inches(1.4), Inches(0.6)]
    tbl3_headers = ["Parameter", "Observed Value", "Cat."]
    tbl3_data = [
        ["Total PDUs", "14 PDUs (9,324 Bytes)", "FACT"],
        ["Framing Compliance", "100.0% (14/14 Valid)", "FACT"],
        ["Extracted Payload", "8,764 Bytes", "FACT"],
        ["Mean PDU Length", "626.0 B (45–1,444 B)", "STAT"],
        ["Fragmentation", "6 Unfrag. (42.9%), 8 Frag.", "FACT"],
        ["Protocols", "GSE_EXT_NPA: 11, IPv4: 9", "FACT"],
        ["CRC-32 Checksum", "100.0% Pass (0 Failures)", "FACT"]
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
        r.font.size = Pt(8.0)
        r.font.bold = True
    for r_idx, row_data in enumerate(tbl3_data):
        for c_idx, val in enumerate(row_data):
            cell = tbl3.cell(r_idx + 1, c_idx)
            cell.width = col3_widths[c_idx]
            set_cell_margins(cell, 25, 25, 30, 30)
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER if c_idx == 2 else WD_ALIGN_PARAGRAPH.LEFT
            r = p.add_run(val)
            r.font.name = 'Times New Roman'
            r.font.size = Pt(8.0)

    # Table IV (BBFrame)
    add_tbl_caption("IV", "DVB-S2 Baseband Frame Analysis")
    tbl4 = doc.add_table(rows=6, cols=3)
    tbl4.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl4.autofit = False
    set_ieee_table_borders(tbl4)
    col4_widths = [Inches(1.2), Inches(1.5), Inches(0.6)]
    tbl4_headers = ["Parameter", "Observed Value", "Cat."]
    tbl4_data = [
        ["Total BBFrames", "4,309 Frames (2.35 MB)", "FACT"],
        ["CRC-8 Checksum", "4,309 Passed / 0 Failed", "FACT"],
        ["Input Mode", "SIS: 4,308 / MIS: 1", "FACT"],
        ["Modulation", "Adaptive Coding (ACM 100%)", "FACT"],
        ["DFL Bit Range", "216 to 10,000 Bits (Mode: 2,992 b)", "FACT"]
    ]
    for c_idx, w in enumerate(col4_widths):
        tbl4.columns[c_idx].width = w
    for c_idx, h_text in enumerate(tbl4_headers):
        cell = tbl4.cell(0, c_idx)
        cell.width = col4_widths[c_idx]
        set_cell_background(cell, "F0F4F8")
        set_cell_margins(cell, 30, 30, 30, 30)
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(h_text)
        r.font.name = 'Times New Roman'
        r.font.size = Pt(8.0)
        r.font.bold = True
    for r_idx, row_data in enumerate(tbl4_data):
        for c_idx, val in enumerate(row_data):
            cell = tbl4.cell(r_idx + 1, c_idx)
            cell.width = col4_widths[c_idx]
            set_cell_margins(cell, 25, 25, 30, 30)
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER if c_idx == 2 else WD_ALIGN_PARAGRAPH.LEFT
            r = p.add_run(val)
            r.font.name = 'Times New Roman'
            r.font.size = Pt(8.0)

    # Table V (Anomaly)
    add_tbl_caption("V", "Isolation Forest Anomaly Results across Formats")
    tbl5 = doc.add_table(rows=4, cols=5)
    tbl5.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl5.autofit = False
    set_ieee_table_borders(tbl5)
    col5_widths = [Inches(0.65), Inches(0.55), Inches(0.4), Inches(0.4), Inches(1.3)]
    tbl5_headers = ["Format", "Window", "Total", "Anom.", "Peak & Indices"]
    tbl5_data = [
        ["MPEG-TS", "200 Pkts", "91", "5", "0.8576 [Win 1, 2, 12, 88, 90]"],
        ["GSE", "3 PDUs", "5", "1", "0.5018 [Win 4]"],
        ["BBFrame", "50 Frms", "87", "5", "0.7406 [Win 0, 83, 84, 85, 86]"]
    ]
    for c_idx, w in enumerate(col5_widths):
        tbl5.columns[c_idx].width = w
    for c_idx, h_text in enumerate(tbl5_headers):
        cell = tbl5.cell(0, c_idx)
        cell.width = col5_widths[c_idx]
        set_cell_background(cell, "F0F4F8")
        set_cell_margins(cell, 30, 30, 30, 30)
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(h_text)
        r.font.name = 'Times New Roman'
        r.font.size = Pt(8.0)
        r.font.bold = True
    for r_idx, row_data in enumerate(tbl5_data):
        for c_idx, val in enumerate(row_data):
            cell = tbl5.cell(r_idx + 1, c_idx)
            cell.width = col5_widths[c_idx]
            set_cell_margins(cell, 25, 25, 30, 30)
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER if c_idx in [1, 2, 3] else WD_ALIGN_PARAGRAPH.LEFT
            r = p.add_run(val)
            r.font.name = 'Times New Roman'
            r.font.size = Pt(8.0)

    add_sec_h1("VII. Verification and Limitations")
    add_body_p(
        "System reliability is validated by an automated regression test suite executed via Python's standard unittest:\n"
        "python -m unittest discover -s tests -v\n"
        "(a) Test Suite Outcome: 304 / 304 Tests Passing (100% Pass Rate) with 0 failures, 0 errors, and 0 skipped in 74.61s (268 backend modules and 36 frontend integration tests). "
        "Receiver resilience against malformed stream containers is validated using fault injection mutations inspired by Izumi et al. [2].\n"
        "(b) Domain Safeguards: PRJ_111 operates strictly post-demodulator on digital streams; it does not measure analog RF parameters (SNR, MER) and indexes timeline events strictly by physical byte offsets."
    )

    add_sec_h1("VIII. Conclusion and Future Work")
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
    references_entries = [
        (1, "X.-Q. Liao et al.", "An Efficient Joint Frame and Physical Layer Signaling Code Detection Method for DVB-S2", "IEEE Access", "vol. 12, pp. 41819–41825, 2024", "10.1109/ACCESS.2024.3378292"),
        (2, "F. Izumi et al.", "A fuzzing-based test-creation approach for evaluating digital TV receivers via transport streams", "Softw. Test. Verif. Reliab.", "vol. 33, no. 4, p. e1833, 2023", "10.1002/stvr.1833"),
        (3, "Y. Cao et al.", "Revisiting streaming anomaly detection: benchmark and evaluation", "Artif. Intell. Rev.", "vol. 58, no. 1, art. no. 8, 2025", "10.1007/s10462-024-10995-w"),
        (4, "ETSI", "Digital Video Broadcasting (DVB); Second Generation Framing Structure, Channel Coding and Modulation Systems for Broadcasting, Interactive Services, News Gathering and Other Broadband Satellite Applications; Part 1: DVB-S2", "ETSI Standard", "EN 302 307-1 V1.4.1, 2014", None),
        (5, "ISO/IEC", "Information Technology — Generic Coding of Moving Pictures and Associated Audio Information — Part 1: Systems (MPEG-2 Transport Stream)", "ISO/IEC Standard", "13818-1:2022, 2022", None),
        (6, "ETSI", "Digital Video Broadcasting (DVB); Generic Stream Encapsulation (GSE); Part 1: Protocol", "ETSI Standard", "TS 102 606-1 V1.2.1, 2014", None),
        (7, "ETSI", "Measurement Guidelines for DVB Systems", "ETSI Technical Report", "TR 101 290 V1.4.1, 2020", None),
        (8, "A. Morello et al.", "DVB-S2: The Second Generation Standard for Satellite Broadband Services", "Proc. IEEE", "vol. 94, no. 1, pp. 210–227, 2006", "10.1109/JPROC.2005.861013"),
        (9, "P. L. Luisi et al.", "Empirical Evaluation of Digital Video Broadcasting Systems and Transport Stream Analysis", "IEEE Trans. Broadcast.", "vol. 66, no. 2, pp. 431–444, 2020", "10.1109/TBC.2019.2954067"),
        (10, "D. Minoli", "Innovations in Satellite Communications and the Global Information Infrastructure", "John Wiley & Sons", "Hoboken, NJ, 2015", "10.1002/9781118984086"),
        (11, "E. Casini et al.", "DVB-S2 Modern Modulation and Coding Techniques for Satellite Broadcast and Broadband Transmissions", "IEEE Commun. Mag.", "vol. 42, no. 11, pp. 146–156, 2004", "10.1109/MCOM.2004.1362547"),
        (12, "G. Fairhurst et al.", "Generic Stream Encapsulation (GSE) for DVB-S2: Design and Evaluation", "Int. J. Satell. Commun. Netw.", "vol. 28, no. 5–6, pp. 287–305, 2010", "10.1002/sat.946"),
        (13, "G. Fairhurst et al.", "Unidirectional Lightweight Encapsulation (ULE) for Transmission of IP Datagrams over an MPEG-2 Transport Stream", "IETF RFC 4326", "Dec. 2005", None),
        (14, "V. Chandola et al.", "Anomaly Detection: A Survey", "ACM Comput. Surv.", "vol. 41, no. 3, pp. 1–58, 2009", "10.1145/1541880.1541882"),
        (15, "M. A. F. Pimentel et al.", "A Review of Novelty Detection", "Signal Process.", "vol. 99, pp. 215–249, 2014", "10.1016/j.sigpro.2013.12.026"),
        (16, "F. T. Liu et al.", "Isolation Forest", "in Proc. IEEE ICDM", "pp. 413–422, 2008", "10.1109/ICDM.2008.17"),
        (17, "F. T. Liu et al.", "Isolation-Based Anomaly Detection", "ACM TKDD", "vol. 6, no. 1, pp. 1–39, 2012", "10.1145/2133360.2133363"),
        (18, "R. S. Baggio et al.", "Network Traffic Anomaly Detection Using Unsupervised Learning Models: A Comparative Study", "IEEE Access", "vol. 9, pp. 15982–15998, 2021", "10.1109/ACCESS.2021.3052800"),
        (19, "D. Arthur et al.", "k-means++: The Advantages of Careful Seeding", "in Proc. ACM-SIAM SODA", "pp. 1027–1035, 2007", None),
        (20, "M. Ester et al.", "A Density-Based Algorithm for Discovering Clusters in Large Spatial Databases with Noise", "in Proc. KDD", "pp. 226–231, 1996", None)
    ]

    for num, auth, title, venue, details, doi in references_entries:
        p_ref = doc.add_paragraph()
        p_ref.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p_ref.paragraph_format.left_indent = Inches(0.18)
        p_ref.paragraph_format.first_line_indent = Inches(-0.18)
        p_ref.paragraph_format.space_after = Pt(2)
        p_ref.paragraph_format.line_spacing = 1.0

        r_num = p_ref.add_run(f"[{num}] ")
        r_num.font.name = 'Times New Roman'
        r_num.font.size = Pt(8.0)

        r_auth = p_ref.add_run(f"{auth}, ")
        r_auth.font.name = 'Times New Roman'
        r_auth.font.size = Pt(8.0)

        r_title = p_ref.add_run(f"“{title},” ")
        r_title.font.name = 'Times New Roman'
        r_title.font.size = Pt(8.0)

        r_venue = p_ref.add_run(f"{venue}, ")
        r_venue.font.name = 'Times New Roman'
        r_venue.font.size = Pt(8.0)
        r_venue.font.italic = True

        if doi:
            det_text = f"{details}, doi: {doi}."
        else:
            det_text = f"{details}."
        r_det = p_ref.add_run(det_text)
        r_det.font.name = 'Times New Roman'
        r_det.font.size = Pt(8.0)

        output_path = "07_DOCUMENTATION/RESEARCH_PAPER/PRJ_111_Research_Paper_6Pages.docx"
    doc.save(output_path)
    print(f"Successfully generated: {output_path} (Size: {os.path.getsize(output_path)} bytes)")

if __name__ == "__main__":
    build_paper_6pages()
