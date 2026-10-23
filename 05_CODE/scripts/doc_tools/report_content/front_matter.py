from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from report_content.builder_utils import set_cell_margins, set_cell_shading, add_custom_table

def build_front_matter(doc):
    # =========================================================================
    # SECTION 1: COVER / TITLE PAGE
    # =========================================================================
    p = doc.add_paragraph()
    p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(24)
    p.paragraph_format.space_after = Pt(12)
    p.paragraph_format.line_spacing = 1.3
    r = p.add_run("DEVELOPMENT OF A SOFTWARE APPLICATION FOR\nANALYSIS AND PROCESSING OF DVB-S2 RECEIVER\nOUTPUT STREAM")
    r.font.name = "Times New Roman"
    r.font.size = Pt(18)
    r.font.bold = True
    r.font.color.rgb = RGBColor(0, 0, 0)
    
    p = doc.add_paragraph()
    p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(18)
    p.paragraph_format.space_after = Pt(18)
    p.paragraph_format.line_spacing = 1.3
    r = p.add_run("A PROJECT REPORT\nSubmitted in Partial Fulfillment of the Requirements\nfor the Award of the Degree of\n")
    r.font.name = "Times New Roman"
    r.font.size = Pt(12)
    r.font.bold = True
    r = p.add_run("BACHELOR OF TECHNOLOGY\nIN\nCOMPUTER SCIENCE AND ENGINEERING")
    r.font.name = "Times New Roman"
    r.font.size = Pt(14)
    r.font.bold = True
    
    p = doc.add_paragraph()
    p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(18)
    p.paragraph_format.space_after = Pt(12)
    p.paragraph_format.line_spacing = 1.2
    r = p.add_run("Submitted by\n\n")
    r.font.name = "Times New Roman"
    r.font.size = Pt(12)
    r.font.bold = True
    r = p.add_run("Y VENGALA RAO (Roll No. 20231COM0001)\nSK SAMAD (Roll No. 20231COM0031)\nC RAKESHWAR (Roll No. 20231COM0008)\n")
    r.font.name = "Times New Roman"
    r.font.size = Pt(12)
    r.font.bold = True
    
    p = doc.add_paragraph()
    p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(18)
    p.paragraph_format.space_after = Pt(24)
    p.paragraph_format.line_spacing = 1.2
    r = p.add_run("Under the guidance of\n")
    r.font.name = "Times New Roman"
    r.font.size = Pt(12)
    r.font.bold = True
    r = p.add_run("Asst. Prof. IRFAN RAJAB BHAT\nAssistant Professor, Department of Computer Science & Engineering\n")
    r.font.name = "Times New Roman"
    r.font.size = Pt(12)
    r.font.bold = True
    
    p = doc.add_paragraph()
    p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(24)
    p.paragraph_format.space_after = Pt(0)
    p.paragraph_format.line_spacing = 1.3
    r = p.add_run("PRESIDENCY SCHOOL OF COMPUTER SCIENCE AND ENGINEERING\nPRESIDENCY UNIVERSITY\nBENGALURU - 560064\nNOVEMBER 2026")
    r.font.name = "Times New Roman"
    r.font.size = Pt(13)
    r.font.bold = True

    # =========================================================================
    # SECTION 2: PRELIMINARY PAGES (ROMAN NUMERALS STARTING AT vi)
    # =========================================================================
    doc.add_section() # Section break for front matter
    
    # --- BONAFIDE CERTIFICATE ---
    p = doc.add_paragraph()
    p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(12)
    p.paragraph_format.space_after = Pt(4)
    r = p.add_run("PRESIDENCY SCHOOL OF COMPUTER SCIENCE AND ENGINEERING\nPRESIDENCY UNIVERSITY, BENGALURU\n")
    r.font.name = "Times New Roman"
    r.font.size = Pt(14)
    r.font.bold = True
    
    p = doc.add_paragraph()
    p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.space_after = Pt(18)
    r = p.add_run("BONAFIDE CERTIFICATE")
    r.font.name = "Times New Roman"
    r.font.size = Pt(16)
    r.font.bold = True
    
    p = doc.add_paragraph()
    p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(12)
    p.paragraph_format.line_spacing = 1.5
    r = p.add_run(
        "Certified that this project report entitled \"Development of a Software Application for Analysis and Processing "
        "of DVB-S2 Receiver Output Stream\" is a bonafide work of Mr. Y VENGALA RAO (Roll No. 20231COM0001), Mr. SK SAMAD "
        "(Roll No. 20231COM0031), and Mr. C RAKESHWAR (Roll No. 20231COM0008), who have successfully carried out the project "
        "work under my supervision and submitted the report in partial fulfillment of the requirements for the award of the "
        "degree of BACHELOR OF TECHNOLOGY in COMPUTER SCIENCE AND ENGINEERING from Presidency University, Bengaluru during "
        "the academic year 2026-27."
    )
    r.font.name = "Times New Roman"
    r.font.size = Pt(12)
    
    p = doc.add_paragraph()
    p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.space_after = Pt(24)
    p.paragraph_format.line_spacing = 1.5
    r = p.add_run(
        "The project work described in this report represents genuine scientific investigation and technical engineering. "
        "The software architecture, empirical evaluations, mathematical formulations, and verification test suites have not "
        "been submitted elsewhere for the award of any other degree or diploma."
    )
    r.font.name = "Times New Roman"
    r.font.size = Pt(12)
    
    # Signature Table (Guide, Coordinator, HOD)
    tbl_sig = doc.add_table(rows=1, cols=3)
    tbl_sig.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl_sig.autofit = False
    for i, w in enumerate([2.2, 2.2, 2.2]):
        tbl_sig.columns[i].width = Inches(w)
    
    sig_data = [
        ("Asst. Prof. IRFAN RAJAB BHAT\nProject Guide, PSCS\nPresidency University", 0),
        ("Ms. SUMITA GUDDIN\nProgram Project Coordinator, PSCS\nPresidency University", 1),
        ("Dr. GOPAL K SHYAM\nHead of the Department, PSCS\nPresidency University", 2)
    ]
    for text, c_idx in sig_data:
        cell = tbl_sig.cell(0, c_idx)
        cell.text = ""
        set_cell_margins(cell, top=140, bottom=40, left=40, right=40)
        p = cell.paragraphs[0]
        p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.line_spacing = 1.15
        r = p.add_run("\n\n_______________________\n" + text)
        r.font.name = "Times New Roman"
        r.font.size = Pt(10)
        r.font.bold = True
        
    p_seal = doc.add_paragraph()
    p_seal.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p_seal.paragraph_format.space_before = Pt(24)
    r = p_seal.add_run("Date: 28-11-2026\nPlace: Bengaluru                                                                   Official Institutional Seal")
    r.font.name = "Times New Roman"
    r.font.size = Pt(11)
    r.font.bold = True

    # --- CERTIFICATE OF VIVA-VOCE EXAMINATION ---
    p = doc.add_paragraph()
    p.paragraph_format.page_break_before = True
    p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(12)
    p.paragraph_format.space_after = Pt(4)
    r = p.add_run("PRESIDENCY SCHOOL OF COMPUTER SCIENCE AND ENGINEERING\nPRESIDENCY UNIVERSITY, BENGALURU\n")
    r.font.name = "Times New Roman"
    r.font.size = Pt(14)
    r.font.bold = True
    
    p = doc.add_paragraph()
    p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.space_after = Pt(18)
    r = p.add_run("CERTIFICATE OF VIVA-VOCE EXAMINATION")
    r.font.name = "Times New Roman"
    r.font.size = Pt(16)
    r.font.bold = True
    
    p = doc.add_paragraph()
    p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(14)
    p.paragraph_format.line_spacing = 1.5
    r = p.add_run(
        "This is to certify that Mr. Y VENGALA RAO (Roll No. 20231COM0001), Mr. SK SAMAD (Roll No. 20231COM0031), "
        "and Mr. C RAKESHWAR (Roll No. 20231COM0008) have been subjected to the Viva-Voce Examination on 28-11-2026 "
        "at Presidency University, Bengaluru, for their project report titled \"Development of a Software Application "
        "for Analysis and Processing of DVB-S2 Receiver Output Stream\" in partial fulfillment of the requirements for "
        "the award of the degree of Bachelor of Technology in Computer Science and Engineering."
    )
    r.font.name = "Times New Roman"
    r.font.size = Pt(12)
    
    p = doc.add_paragraph()
    p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.space_after = Pt(24)
    p.paragraph_format.line_spacing = 1.5
    r = p.add_run(
        "The project performance, technical demonstrations, architectural defenses, and comprehensive documentation "
        "presented by the candidates have been evaluated and approved by the examination committee."
    )
    r.font.name = "Times New Roman"
    r.font.size = Pt(12)
    
    tbl_viva = doc.add_table(rows=1, cols=2)
    tbl_viva.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl_viva.autofit = False
    tbl_viva.columns[0].width = Inches(3.3)
    tbl_viva.columns[1].width = Inches(3.3)
    
    c1 = tbl_viva.cell(0, 0)
    set_cell_margins(c1, top=140, bottom=40, left=40, right=40)
    p = c1.paragraphs[0]
    p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.line_spacing = 1.15
    r = p.add_run("\n\n___________________________________\nInternal Examiner\nName: Asst. Prof. IRFAN RAJAB BHAT\nDesignation: Assistant Professor\nPresidency University, Bengaluru")
    r.font.name = "Times New Roman"
    r.font.size = Pt(10)
    r.font.bold = True
    
    c2 = tbl_viva.cell(0, 1)
    set_cell_margins(c2, top=140, bottom=40, left=40, right=40)
    p = c2.paragraphs[0]
    p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.line_spacing = 1.15
    r = p.add_run("\n\n___________________________________\nExternal Examiner\nName: _____________________________\nDesignation: ______________________\nUniversity/Industry: _______________")
    r.font.name = "Times New Roman"
    r.font.size = Pt(10)
    r.font.bold = True

    # --- DECLARATION ---
    p = doc.add_paragraph()
    p.paragraph_format.page_break_before = True
    p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(12)
    p.paragraph_format.space_after = Pt(4)
    r = p.add_run("PRESIDENCY UNIVERSITY\nPRESIDENCY SCHOOL OF COMPUTER SCIENCE AND ENGINEERING\n")
    r.font.name = "Times New Roman"
    r.font.size = Pt(14)
    r.font.bold = True
    
    p = doc.add_paragraph()
    p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.space_after = Pt(18)
    r = p.add_run("DECLARATION")
    r.font.name = "Times New Roman"
    r.font.size = Pt(16)
    r.font.bold = True
    
    p = doc.add_paragraph()
    p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(12)
    p.paragraph_format.line_spacing = 1.5
    r = p.add_run(
        "We, the students of final year B.Tech in COMPUTER SCIENCE AND ENGINEERING at Presidency University, Bengaluru, "
        "named Y VENGALA RAO (Roll No. 20231COM0001), SK SAMAD (Roll No. 20231COM0031), and C RAKESHWAR (Roll No. 20231COM0008), "
        "hereby declare that the project work titled \"Development of a Software Application for Analysis and Processing "
        "of DVB-S2 Receiver Output Stream\" has been independently carried out by us and submitted in partial fulfillment "
        "for the award of the degree of Bachelor of Technology in Computer Science and Engineering during the academic year 2026-27."
    )
    r.font.name = "Times New Roman"
    r.font.size = Pt(12)
    
    p = doc.add_paragraph()
    p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.space_after = Pt(24)
    p.paragraph_format.line_spacing = 1.5
    r = p.add_run(
        "We further confirm that the software implementation, empirical results, mathematical evaluations, and written prose "
        "comprising this report are our original creations. External technical literature, standards documents, and libraries "
        "have been properly referenced and cited in accordance with academic integrity guidelines. This work has not been "
        "submitted previously to any other university or institution for any academic degree, diploma, or certificate."
    )
    r.font.name = "Times New Roman"
    r.font.size = Pt(12)
    
    tbl_dec = doc.add_table(rows=1, cols=3)
    tbl_dec.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl_dec.autofit = False
    for i, w in enumerate([2.2, 2.2, 2.2]):
        tbl_dec.columns[i].width = Inches(w)
    
    dec_data = [
        ("Y VENGALA RAO\n(20231COM0001)", 0),
        ("SK SAMAD\n(20231COM0031)", 1),
        ("C RAKESHWAR\n(20231COM0008)", 2)
    ]
    for text, c_idx in dec_data:
        cell = tbl_dec.cell(0, c_idx)
        cell.text = ""
        set_cell_margins(cell, top=140, bottom=40, left=40, right=40)
        p = cell.paragraphs[0]
        p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.line_spacing = 1.15
        r = p.add_run("\n\n_______________________\n" + text)
        r.font.name = "Times New Roman"
        r.font.size = Pt(10)
        r.font.bold = True
        
    p_dec_seal = doc.add_paragraph()
    p_dec_seal.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p_dec_seal.paragraph_format.space_before = Pt(24)
    r = p_dec_seal.add_run("Date: 28-11-2026\nPlace: Bengaluru")
    r.font.name = "Times New Roman"
    r.font.size = Pt(11)

    # --- ACKNOWLEDGEMENTS ---
    p = doc.add_paragraph()
    p.paragraph_format.page_break_before = True
    p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(12)
    p.paragraph_format.space_after = Pt(18)
    r = p.add_run("ACKNOWLEDGEMENTS")
    r.font.name = "Times New Roman"
    r.font.size = Pt(16)
    r.font.bold = True
    
    p = doc.add_paragraph()
    p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(10)
    p.paragraph_format.line_spacing = 1.5
    r = p.add_run(
        "We express our deepest gratitude to the Chancellor, Vice-Chancellor, and Pro Vice-Chancellor of Presidency University, "
        "Bengaluru, for providing the state-of-the-art computational infrastructure, research laboratories, and an inspiring "
        "academic environment that enabled the successful execution of this capstone project."
    )
    r.font.name = "Times New Roman"
    r.font.size = Pt(12)
    
    p = doc.add_paragraph()
    p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(10)
    p.paragraph_format.line_spacing = 1.5
    r = p.add_run(
        "We place on record our sincere appreciation and respectful gratitude to Dr. GOPAL K SHYAM, Head of the Department of "
        "Computer Science and Engineering, for his constant encouragement, visionary leadership, and persistent focus on technical "
        "rigor and research excellence across our engineering program."
    )
    r.font.name = "Times New Roman"
    r.font.size = Pt(12)
    
    p = doc.add_paragraph()
    p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(10)
    p.paragraph_format.line_spacing = 1.5
    r = p.add_run(
        "We are profoundly indebted to our project guide, Asst. Prof. IRFAN RAJAB BHAT, Assistant Professor, Department of "
        "Computer Science and Engineering, for his exceptional guidance, intellectual mentorship, and critical technical feedback "
        "throughout the design, algorithmic formulation, and empirical testing phases of this project. His high standards for "
        "academic integrity and systems engineering shaped the depth and precision of this work."
    )
    r.font.name = "Times New Roman"
    r.font.size = Pt(12)
    
    p = doc.add_paragraph()
    p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(10)
    p.paragraph_format.line_spacing = 1.5
    r = p.add_run(
        "We also convey our sincere thanks to Ms. SUMITA GUDDIN, Program Project Coordinator, and all faculty members and technical "
        "staff of the Presidency School of Computer Science and Engineering for their continuous coordination, administrative "
        "support, and helpful reviews during our milestone presentations."
    )
    r.font.name = "Times New Roman"
    r.font.size = Pt(12)
    
    p = doc.add_paragraph()
    p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(24)
    p.paragraph_format.line_spacing = 1.5
    r = p.add_run(
        "Finally, we extend our heartfelt appreciation to our parents, family members, and fellow students for their unwavering "
        "moral support, encouragement, and understanding throughout the course of our B.Tech engineering studies."
    )
    r.font.name = "Times New Roman"
    r.font.size = Pt(12)
    
    p = doc.add_paragraph()
    p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    p.paragraph_format.space_before = Pt(12)
    r = p.add_run("Y VENGALA RAO (20231COM0001)\nSK SAMAD (20231COM0031)\nC RAKESHWAR (20231COM0008)\n")
    r.font.name = "Times New Roman"
    r.font.size = Pt(11)
    r.font.bold = True

    # --- ABSTRACT ---
    p = doc.add_paragraph()
    p.paragraph_format.page_break_before = True
    p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(12)
    p.paragraph_format.space_after = Pt(18)
    r = p.add_run("ABSTRACT")
    r.font.name = "Times New Roman"
    r.font.size = Pt(16)
    r.font.bold = True
    
    p = doc.add_paragraph()
    p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(10)
    p.paragraph_format.line_spacing = 1.5
    r = p.add_run(
        "Second Generation Digital Video Broadcasting by Satellite (DVB-S2, ETSI EN 302 307) serves as the primary "
        "telecommunications transmission standard underpinning global satellite broadband connectivity, cellular backhaul, "
        "and high-definition direct-to-home broadcasting. Post-demodulator digital output emitted by modern commercial and defense "
        "satellite receiver hardware comprises structurally diverse container encapsulation formats, notably fixed 188-byte MPEG-2 "
        "Transport Streams (MPEG-TS), variable-length Generic Stream Encapsulation (GSE) protocol data units, and native physical-layer "
        "Baseband Frames (BBFrame). Assessing stream integrity, identifying multiplex irregularities, and isolating frame corruption "
        "downstream of the demodulation stage present acute operational challenges in real-world ground station environments. Existing "
        "diagnostic workflows are severely constrained by rigid static thresholding in commercial broadcast probes, total diagnostic "
        "blind spots regarding multi-format container fragmentation, unwarranted physical-layer extrapolations, and the absence of "
        "unsupervised anomaly detection capabilities."
    )
    r.font.name = "Times New Roman"
    r.font.size = Pt(12)
    
    p = doc.add_paragraph()
    p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(10)
    p.paragraph_format.line_spacing = 1.5
    r = p.add_run(
        "This capstone project presents PRJ_111, a comprehensive, self-contained software workstation engineered for deterministic "
        "stream health accounting, unsupervised anomaly detection, and automated diagnostic synthesis across multi-format DVB-S2 receiver "
        "output streams. The software delivers an integrated seven-feature analytical pipeline (F1 through F7) incorporating: deterministic "
        "stream health scoring anchored in ETSI TR 101 290 Priority-1 measurement principles; unsupervised outlier detection via Isolation "
        "Forest ensembles operating across 8-dimensional sliding window feature spaces; byte-exact spatial timeline visualizations referencing "
        "physical bitstream offsets (0x...); comprehensive continuity counter tracking; explainable machine learning diagnoses using clamped "
        "Z-score feature attributions (|Z| <= 20 sigma); cross-format differential stream comparisons governed by an automated semantic "
        "barrier; and multi-format report synthesis across JSON, Markdown, Text, and standalone HTML formats."
    )
    r.font.name = "Times New Roman"
    r.font.size = Pt(12)
    
    p = doc.add_paragraph()
    p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(10)
    p.paragraph_format.line_spacing = 1.5
    r = p.add_run(
        "The software architecture incorporates a chunked streaming reader processing multi-gigabyte bitstreams within 64 KB memory-bounded "
        "buffers, an empirical fault-injection benchmark utility, and an offline single-page application (SPA) operator dashboard with zero "
        "external cloud dependencies. Empirical evaluation across physical satellite bitstreams confirms 100% parsing accuracy: 18,176 packets "
        "in MPEG-TS (3,267,305 bytes payload, health score 100.0), 14 PDUs in GSE (57.1% fragmentation, 8,764 bytes payload), and 4,309 frames "
        "in BBFrame (100% ACM, modal 2,992-bit DFL, 100% valid CRC-8). The complete automated regression test suite comprising 304 tests across "
        "18 modules executes with a 100% pass rate in 76.06 seconds, establishing a reproducible, verifiable, and highly scalable software "
        "workstation for satellite ground station telemetry monitoring."
    )
    r.font.name = "Times New Roman"
    r.font.size = Pt(12)
    
    p = doc.add_paragraph()
    p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.space_after = Pt(12)
    r = p.add_run("Keywords: ")
    r.font.name = "Times New Roman"
    r.font.size = Pt(11)
    r.font.bold = True
    r = p.add_run("DVB-S2, MPEG-TS, Generic Stream Encapsulation (GSE), BBFrame, Isolation Forest, ETSI TR 101 290, Stream Health Analysis, Diagnostic Reporting, Chunked Processing.")
    r.font.name = "Times New Roman"
    r.font.size = Pt(11)
    r.font.italic = True

    # --- TABLE OF CONTENTS ---
    p = doc.add_paragraph()
    p.paragraph_format.page_break_before = True
    p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(12)
    p.paragraph_format.space_after = Pt(18)
    r = p.add_run("TABLE OF CONTENTS")
    r.font.name = "Times New Roman"
    r.font.size = Pt(16)
    r.font.bold = True
    
    toc_headers = ["CHAPTER NO", "TITLE", "PAGE NO"]
    toc_data = [
        ["", "ABSTRACT", "vi"],
        ["", "LIST OF FIGURES", "ix"],
        ["", "LIST OF TABLES", "x"],
        ["", "LIST OF ABBREVIATIONS", "xi"],
        ["CHAPTER 1", "INTRODUCTION", "1"],
        ["1.1", "Background and Context of Satellite Digital Broadcasting", "1"],
        ["1.2", "Digital Demodulation Output Stream Paradigm", "2"],
        ["1.3", "Problem Statement", "3"],
        ["1.4", "Project Objectives", "4"],
        ["1.5", "Scope of the Work", "5"],
        ["1.6", "Motivation and Industrial Significance", "6"],
        ["1.7", "Organization of the Report", "7"],
        ["CHAPTER 2", "LITERATURE SURVEY", "8"],
        ["2.1", "Evolution of Satellite Transmission Standards", "8"],
        ["2.2", "ETSI TR 101 290 Priority-1 Measurement Principles", "9"],
        ["2.3", "General-Purpose Network Protocol Analyzers (Wireshark / tcpdump)", "10"],
        ["2.4", "Dedicated Broadcast Transport Stream Analyzers", "11"],
        ["2.5", "Machine Learning in Telemetry Anomaly Detection", "12"],
        ["2.6", "Explainable AI (XAI) in Diagnostic Monitoring", "13"],
        ["2.7", "Streaming Bitstream Processing and Chunked Ingestion Paradigms", "14"],
        ["2.8", "Synthesis of Literature and Comparative Framework", "15"],
        ["CHAPTER 3", "RESEARCH GAPS OF EXISTING METHODS", "16"],
        ["3.1", "Rigid Static Thresholding and Lack of Dynamic Behavioral Modeling", "16"],
        ["3.2", "Container Fragmentation and Multi-Format Inflexibility", "17"],
        ["3.3", "Artificial Timestamp Inflation vs. Physical Offset Traceability", "18"],
        ["3.4", "Unwarranted Cross-Format Telemetry Bleed and Semantic Incoherence", "19"],
        ["3.5", "High Acquisition Cost and Proprietary Lock-in of Dedicated Probes", "20"],
        ["3.6", "Diagnostic Opacity and Lack of Root-Cause Explanations", "21"],
        ["3.7", "Comprehensive Comparative Matrix", "22"],
        ["CHAPTER 4", "PROPOSED METHODOLOGY", "23"],
        ["4.1", "Foundational Architecture Principle: Container Abstraction", "23"],
        ["4.2", "Unified Multi-Format Feature Extraction Pipeline", "24"],
        ["4.3", "Mathematical Formulations and Analytical Models", "25"],
        ["4.4", "Chunked Streaming Processing Engine (64 KB Bounded Buffer)", "28"],
        ["4.5", "Controlled Fault-Injection Validation Methodology", "30"],
        ["CHAPTER 5", "OBJECTIVES AND SPECIFICATIONS", "32"],
        ["5.1", "Primary Functional Objectives (F1 through F7)", "32"],
        ["5.2", "Non-Functional and Operational Requirements", "34"],
        ["5.3", "Mathematical and Diagnostic Verification Targets", "35"],
        ["5.4", "Automated Test Suite Coverage Targets", "36"],
        ["CHAPTER 6", "SYSTEM DESIGN AND IMPLEMENTATION", "37"],
        ["6.1", "Architectural Overview and Layer Separation", "37"],
        ["6.2", "Low-Level Container Parsing Subsystem", "38"],
        ["6.3", "Unified Feature Extraction Subsystem", "41"],
        ["6.4", "Feature F1: Stream Health & Priority-1 Analysis", "42"],
        ["6.5", "Feature F2: Unsupervised Isolation Forest Anomaly Detection", "43"],
        ["6.6", "Feature F3: Structural Pattern Detection & Multiplex Dynamics", "44"],
        ["6.7", "Feature F4: Spatial-Offset Timeline & Burst Localization", "45"],
        ["6.8", "Feature F5: Explainable Anomaly Root-Cause Diagnostic Engine", "46"],
        ["6.9", "Feature F6: Dual-Stream Comparison Engine with Semantic Barrier", "47"],
        ["6.10", "Feature F7: Multi-Format Automated Diagnostic Report Synthesis", "48"],
        ["6.11", "Frontend Engineering Workstation Architecture", "49"],
        ["6.12", "Streaming Engine & High-Throughput Chunked Implementation", "51"],
        ["6.13", "Controlled Fault-Injection Framework Implementation", "52"],
        ["CHAPTER 7", "TIMELINE FOR EXECUTION OF PROJECT (GANTT CHART)", "53"],
        ["7.1", "Five-Phase Project Milestone Execution Lifecycle", "53"],
        ["7.2", "Detailed Milestone Breakdown (Reviews 0 to 3 / Final)", "54"],
        ["7.3", "Milestone Deliverables and Timeline Schedule", "55"],
        ["CHAPTER 8", "OUTCOMES", "57"],
        ["8.1", "Tangible Software and Engineering Deliverables", "57"],
        ["8.2", "Academic Research Outcomes and Technical Publications", "58"],
        ["8.3", "Standard Operating Procedures and Reproducibility Protocols", "59"],
        ["CHAPTER 9", "RESULTS AND DISCUSSIONS", "60"],
        ["9.1", "Experimental Setup and Execution Environment", "60"],
        ["9.2", "Verification of Complete Automated Test Suite (304 / 304 Passing)", "61"],
        ["9.3", "Empirical Benchmark Evaluation Across Physical Satellite Bitstreams", "63"],
        ["9.4", "Controlled Synthetic Fault Injection Sensitivity & Escalation Experiments", "66"],
        ["9.5", "Memory Footprint, Streaming Throughput & Complexity Analysis", "68"],
        ["9.6", "Comparative Evaluation: PRJ_111 vs. Wireshark vs. Commercial Hardware", "70"],
        ["9.7", "Discussion of Empirical Findings and Practical Engineering Takeaways", "71"],
        ["CHAPTER 10", "CONCLUSION AND FUTURE WORK", "72"],
        ["10.1", "Summary of Scientific and Engineering Contributions", "72"],
        ["10.2", "Technical Limitations and Operational Boundaries", "73"],
        ["10.3", "Future Research and Engineering Enhancements", "74"],
        ["", "REFERENCES", "75"],
        ["APPENDIX A", "PSEUDOCODE AND CORE ALGORITHMS", "78"],
        ["APPENDIX B", "APPLICATION SCREENSHOTS AND ENGINEERING WORKSTATION", "82"],
        ["APPENDIX C", "MANDATORY ENCLOSURES (Publication, Awards, Originality, SDGs)", "86"],
        ["APPENDIX D", "VERIFICATION & REPRODUCIBILITY LEDGER (Hashes & Test Logs)", "89"]
    ]
    add_custom_table(doc, "TABLE OF CONTENTS", toc_headers, toc_data, col_widths=[1.5, 4.3, 0.7])

    # --- LIST OF FIGURES ---
    p = doc.add_paragraph()
    p.paragraph_format.page_break_before = True
    p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(12)
    p.paragraph_format.space_after = Pt(18)
    r = p.add_run("LIST OF FIGURES")
    r.font.name = "Times New Roman"
    r.font.size = Pt(16)
    r.font.bold = True
    
    fig_headers = ["FIGURE NO", "FIGURE CAPTION", "PAGE NO"]
    fig_data = [
        ["Figure 4.1", "End-to-End Multi-Format System Architecture of PRJ_111", "24"],
        ["Figure 7.1", "Five-Phase Project Milestone Execution Roadmap (Gantt Schedule)", "56"],
        ["Figure B.1", "Standby Ingestion Dashboard Awaiting File Upload", "82"],
        ["Figure B.2", "Live Dashboard Rendering Health Gauge and PID Distribution for sample.ts", "82"],
        ["Figure B.3", "Unsupervised Isolation Forest Outlier Plot & Diagnostic Attribution View", "83"],
        ["Figure B.4", "Spatial-Offset Timeline View Scrubbing Across Physical Byte Offsets", "83"],
        ["Figure B.5", "Side-by-Side Dual-Stream Comparison View Governed by Semantic Shield", "84"],
        ["Figure B.6", "Multi-Format Diagnostic Report Preview and Direct Download Modal", "84"],
        ["Figure B.7", "Robust Input Validation Rejection Dialog for Corrupted Non-Stream File", "85"]
    ]
    add_custom_table(doc, "LIST OF FIGURES", fig_headers, fig_data, col_widths=[1.3, 4.5, 0.7])

    # --- LIST OF TABLES ---
    p = doc.add_paragraph()
    p.paragraph_format.page_break_before = True
    p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(12)
    p.paragraph_format.space_after = Pt(18)
    r = p.add_run("LIST OF TABLES")
    r.font.name = "Times New Roman"
    r.font.size = Pt(16)
    r.font.bold = True
    
    tbl_headers = ["TABLE NO", "TABLE CAPTION", "PAGE NO"]
    tbl_list_data = [
        ["Table 1.1", "Target Input Formats and Physical Layer Demarcation", "3"],
        ["Table 2.1", "Comparison of Related DVB Stream Analysis Utilities", "11"],
        ["Table 3.1", "Objective Architectural Comparison: Wireshark vs. PRJ_111", "22"],
        ["Table 4.1", "Unified Feature Vector Dimensions for Rolling Anomaly Detection", "25"],
        ["Table 4.2", "Priority-1 Integrity Fault Identifiers, Trigger Conditions, and Penalty Weights", "26"],
        ["Table 5.1", "Mapping of Functional Features F1 through F7 to Verified Architectural State", "33"],
        ["Table 6.1", "Subsystem Components, Implementation Files, and Design Roles", "38"],
        ["Table 6.2", "Semantic Cross-Format Comparability Matrix for Dual-Stream Analysis", "48"],
        ["Table 7.1", "Milestone Execution Schedule and Engineering Deliverables", "55"],
        ["Table 8.1", "Tangible Software Artifacts and Release Distribution", "58"],
        ["Table 9.1", "Experimental Computing Environment and Dependency Specifications", "61"],
        ["Table 9.2", "Complete Automated Test Suite Breakdown Across 18 Test Modules (304 Tests)", "62"],
        ["Table 9.3", "Master Empirical Experimental Results Across Physical Satellite Bitstreams", "64"],
        ["Table 9.4", "Controlled Synthetic Fault Injection Sensitivity and Detection Benchmark", "67"],
        ["Table 9.5", "Chunked Ingestion Streaming Engine Performance and Throughput Benchmark", "69"],
        ["Table 9.6", "Comprehensive Milestone Bug History and Engineering Resolutions", "70"],
        ["Table C.1", "United Nations Sustainable Development Goals (SDG) Alignment Matrix", "88"],
        ["Table D.1", "Cryptographic Checksum Ledger (SHA-256) of Raw Datasets and Core Artifacts", "90"]
    ]
    add_custom_table(doc, "LIST OF TABLES", tbl_headers, tbl_list_data, col_widths=[1.3, 4.5, 0.7])

    # --- LIST OF ABBREVIATIONS ---
    p = doc.add_paragraph()
    p.paragraph_format.page_break_before = True
    p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(12)
    p.paragraph_format.space_after = Pt(18)
    r = p.add_run("LIST OF ABBREVIATIONS")
    r.font.name = "Times New Roman"
    r.font.size = Pt(16)
    r.font.bold = True
    
    abbr_headers = ["ABBREVIATION", "EXPANSION / DEFINITION"]
    abbr_data = [
        ["ACM", "Adaptive Coding and Modulation"],
        ["AFC", "Adaptation Field Control"],
        ["API", "Application Programming Interface"],
        ["BBFrame", "Baseband Frame (Physical layer container in DVB-S2)"],
        ["BBHeader", "Baseband Header (10-byte descriptor at the start of a BBFrame)"],
        ["BER", "Bit Error Rate"],
        ["CC", "Continuity Counter (4-bit field in MPEG-TS header)"],
        ["CNR", "Carrier-to-Noise Ratio"],
        ["CRC", "Cyclic Redundancy Check"],
        ["DFL", "Data Field Length (16-bit field in BBHeader indicating user payload bits)"],
        ["DTH", "Direct-to-Home (Satellite broadcasting service)"],
        ["DVB", "Digital Video Broadcasting"],
        ["DVB-S2", "Digital Video Broadcasting - Satellite - Second Generation (ETSI EN 302 307)"],
        ["DVB-S2X", "Digital Video Broadcasting - Satellite - Second Generation Extensions"],
        ["ES6", "ECMAScript 2015 (Modern JavaScript Standard)"],
        ["ETSI", "European Telecommunications Standards Institute"],
        ["FEC", "Forward Error Correction"],
        ["GSE", "Generic Stream Encapsulation (ETSI TS 102 606)"],
        ["GUI", "Graphical User Interface"],
        ["HOD", "Head of the Department"],
        ["HTML5", "Hypertext Markup Language Revision 5"],
        ["IEEE", "Institute of Electrical and Electronics Engineers"],
        ["IP", "Internet Protocol"],
        ["IQR", "Interquartile Range"],
        ["ISO", "International Organization for Standardization"],
        ["JSON", "JavaScript Object Notation"],
        ["LT", "Length Type (2-bit protocol field in GSE PDU header)"],
        ["MATYPE", "Mode Adaptation Type (2-byte descriptor field in BBHeader)"],
        ["ML", "Machine Learning"],
        ["MODCOD", "Modulation and Coding Scheme"],
        ["MPEG-TS", "Moving Picture Experts Group - Transport Stream (ISO/IEC 13818-1)"],
        ["MVP", "Minimum Viable Product"],
        ["PCAP", "Packet Capture (Network bitstream capture file format)"],
        ["PCR", "Program Clock Reference"],
        ["PDU", "Protocol Data Unit"],
        ["PID", "Packet Identifier (13-bit header field in MPEG-TS)"],
        ["PSCS", "Presidency School of Computer Science and Engineering"],
        ["PSI/SI", "Program Specific Information / Service Information"],
        ["PUSI", "Payload Unit Start Indicator (1-bit flag in MPEG-TS header)"],
        ["QoS", "Quality of Service"],
        ["REST", "Representational State Transfer"],
        ["RF", "Radio Frequency"],
        ["SDG", "Sustainable Development Goal (United Nations)"],
        ["SNDU", "Subnetwork Dependent Convergence Protocol Network Data Unit"],
        ["SPA", "Single-Page Application"],
        ["SYNC", "Synchronization Byte (0x47 in MPEG-TS)"],
        ["TCP", "Transmission Control Protocol"],
        ["TEI", "Transport Error Indicator (1-bit flag in MPEG-TS header)"],
        ["TR", "Technical Report (ETSI standard document series)"],
        ["TS", "Transport Stream"],
        ["UPL", "User Packet Length (16-bit field in BBHeader)"],
        ["VCM", "Variable Coding and Modulation"],
        ["XAI", "Explainable Artificial Intelligence"]
    ]
    add_custom_table(doc, "LIST OF ABBREVIATIONS", abbr_headers, abbr_data, col_widths=[1.8, 4.7])
