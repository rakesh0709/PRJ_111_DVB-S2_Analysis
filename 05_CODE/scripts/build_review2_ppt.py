import os
from pathlib import Path
import pptx
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

PROJECT_ROOT = Path(__file__).resolve().parents[2]
TEMPLATE_PATH = str(PROJECT_ROOT / 'Review-2 TEMPLATE_MINI PROJECT CSE7102.pptx')
OUTPUT_PATH = str(PROJECT_ROOT / 'PRJ_111_Review_2_Final.pptx')

# Colors
NAVY = RGBColor(0, 32, 96)
DARK_BLUE = RGBColor(15, 34, 64)
ACCENT_BLUE = RGBColor(0, 102, 204)
GOLD = RGBColor(218, 165, 32)
DARK_GRAY = RGBColor(40, 40, 40)
LIGHT_BG = RGBColor(245, 247, 250)
CARD_BG = RGBColor(235, 240, 248)
WHITE = RGBColor(255, 255, 255)
GREEN = RGBColor(0, 128, 0)
RED = RGBColor(180, 0, 0)

FONT_TITLE = 'Arial'
FONT_BODY = 'Arial'

def create_presentation():
    if not os.path.exists(TEMPLATE_PATH):
        raise FileNotFoundError(f"Template not found at {TEMPLATE_PATH}")

    prs = Presentation(TEMPLATE_PATH)
    print(f"Loaded template with {len(prs.slides)} initial slides.")

    # Master dimensions
    sw = prs.slide_width
    sh = prs.slide_height

    # Clear extra existing slides except Slide 1, 2, 3 as reference or reuse layout_idx=1
    # We will modify Slide 1 and Slide 2, and replace/add slides using layout 1.
    
    # ----------------------------------------------------
    # SLIDE 1: TITLE SLIDE (Modify existing Slide 1)
    # ----------------------------------------------------
    s1 = prs.slides[0]
    for shape in s1.shapes:
        if shape.has_text_frame:
            text = shape.text.strip()
            if "REVIEW-1" in text or "CSE7102" in text:
                tf = shape.text_frame
                tf.clear()
                p0 = tf.paragraphs[0]
                p0.text = "Mini Project (CSE7102)"
                p0.font.size = Pt(24)
                p0.font.bold = True
                p0.font.color.rgb = NAVY
                p0.alignment = PP_ALIGN.CENTER

                p1 = tf.add_paragraph()
                p1.text = "REVIEW-2 PRESENTATION"
                p1.font.size = Pt(20)
                p1.font.bold = True
                p1.font.color.rgb = GOLD
                p1.alignment = PP_ALIGN.CENTER

                p2 = tf.add_paragraph()
                p2.text = "Date: 26-09-2026"
                p2.font.size = Pt(16)
                p2.font.color.rgb = DARK_GRAY
                p2.alignment = PP_ALIGN.CENTER

    # ----------------------------------------------------
    # SLIDE 2: PROJECT TITLE & TEAM DETAILS (Modify existing Slide 2)
    # ----------------------------------------------------
    s2 = prs.slides[1]
    for shape in s2.shapes:
        if shape.has_text_frame:
            text = shape.text.strip()
            if "PROJECT TITLE" in text:
                tf = shape.text_frame
                tf.clear()
                p = tf.paragraphs[0]
                p.text = "Development of a Software Application for Analysis and Processing of DVB-S2 Receiver Output Stream"
                p.font.size = Pt(18)
                p.font.bold = True
                p.font.color.rgb = NAVY
            elif "Project ID:" in text:
                tf = shape.text_frame
                tf.clear()
                p = tf.paragraphs[0]
                p.text = "Project ID: PRJ_111  |  Course: CSE7102 - Mini Project  |  Review-2 (26-09-2026)"
                p.font.size = Pt(13)
                p.font.bold = True
                p.font.color.rgb = DARK_BLUE
            elif "Under the Supervision of" in text or "Dr./Mr." in text:
                tf = shape.text_frame
                tf.clear()
                p0 = tf.paragraphs[0]
                p0.text = "Under the Supervision of:"
                p0.font.size = Pt(12)
                p0.font.bold = True
                p0.font.color.rgb = NAVY

                p1 = tf.add_paragraph()
                p1.text = "Irfan Rajab Bhat"
                p1.font.size = Pt(14)
                p1.font.bold = True
                p1.font.color.rgb = DARK_BLUE

                p2 = tf.add_paragraph()
                p2.text = "Assistant Professor\nDepartment of Computer Science and Engineering\nPresidency University, Bengaluru"
                p2.font.size = Pt(11)
                p2.font.color.rgb = DARK_GRAY
            elif "CSS7102" in text or "Program(s):" in text:
                if "Program(s):" in text:
                    tf = shape.text_frame
                    tf.clear()
                    p0 = tf.paragraphs[0]
                    p0.text = "Program: B.Tech Computer Science and Engineering"
                    p0.font.size = Pt(11)
                    p0.font.color.rgb = DARK_GRAY

                    p1 = tf.add_paragraph()
                    p1.text = "HoD: Dr. T.V. Rajinikanth / Head of Department"
                    p1.font.size = Pt(11)
                    p1.font.color.rgb = DARK_GRAY

                    p2 = tf.add_paragraph()
                    p2.text = "Program Project Coordinator: Dr. Irfan Rajab Bhat"
                    p2.font.size = Pt(11)
                    p2.font.color.rgb = DARK_GRAY

                    p3 = tf.add_paragraph()
                    p3.text = "School Project Coordinator: Mr. Muthuraju V"
                    p3.font.size = Pt(11)
                    p3.font.color.rgb = DARK_GRAY
            elif "Panel No:" in text:
                tf = shape.text_frame
                tf.clear()
                p = tf.paragraphs[0]
                p.text = "Panel No: Panel 11 / PRJ_111"
                p.font.size = Pt(12)
                p.font.bold = True
                p.font.color.rgb = NAVY

        elif shape.has_table:
            table = shape.table
            if len(table.columns) == 3 and len(table.rows) == 4:
                # This is Table 1 (Team Members)
                table.rows[0].cells[0].text = "No."
                table.rows[0].cells[1].text = "Team Member Name"
                table.rows[0].cells[2].text = "University Roll No."
                for cell in table.rows[0].cells:
                    for p in cell.text_frame.paragraphs:
                        p.font.size = Pt(11)
                        p.font.bold = True
                        p.font.color.rgb = NAVY
                
                team_data = [
                    ["1", "Sk Samad", "20231COM0031"],
                    ["2", "Y Vengala Rao", "20231COM0001"],
                    ["3", "C Rakeshwar", "20231COM0008"]
                ]
                for r_i, row in enumerate(team_data):
                    t_row = table.rows[r_i + 1]
                    t_row.cells[0].text = row[0]
                    t_row.cells[1].text = row[1]
                    t_row.cells[2].text = row[2]
                    for cell in t_row.cells:
                        for p in cell.text_frame.paragraphs:
                            p.font.size = Pt(11)
                            p.font.name = FONT_BODY
                            p.font.color.rgb = DARK_GRAY
            elif len(table.columns) == 2 and len(table.rows) == 6:
                # Info table
                info_data = [
                    ["Program Name:", "B.Tech Computer Science & Engineering"],
                    ["Course & Code:", "CSE7102 - Mini Project"],
                    ["Review Milestone:", "Review-2 (26-09-2026)"],
                    ["HoD Name:", "Head of Department, CSE"],
                    ["Program Coordinator:", "Dr. Irfan Rajab Bhat"],
                    ["School Coordinator:", "Mr. Muthuraju V"]
                ]
                for r_i, row in enumerate(info_data):
                    t_row = table.rows[r_i]
                    t_row.cells[0].text = row[0]
                    t_row.cells[1].text = row[1]
                    for c_i, cell in enumerate(t_row.cells):
                        for p in cell.text_frame.paragraphs:
                            p.font.size = Pt(10)
                            p.font.name = FONT_BODY
                            p.font.bold = (c_i == 0)
                            p.font.color.rgb = NAVY if c_i == 0 else DARK_GRAY

    # Helper function to remove extra initial slides (slides 2 to 12) so we build a clean deck
    # In python-pptx, deleting slides can be done via rId or element removal.
    # Alternatively, we can update slides 3..12 in place and add new slides as needed!

    print("Populating slides 3 through 31...")
    
    # List of all slides to build
    slides_data = get_all_slides_data()

    # Reuse slide_layout[1] for content slides
    layout_obj = prs.slide_layouts[1]

    # We have 13 slides in template. Slide 0 is Title, Slide 1 is Team.
    # Let's update slides 2..12 in place and add remaining slides up to 31!

    for idx, sdata in enumerate(slides_data):
        slide_num = idx + 3 # 1-based index (Slide 3 onwards)
        if idx + 2 < len(prs.slides):
            slide = prs.slides[idx + 2]
            # Clear existing shapes on template slide except background graphics
            # Placeholders on slide
            for shp in list(slide.shapes):
                if shp.has_text_frame:
                    shp.text_frame.clear()
        else:
            slide = prs.slides.add_slide(layout_obj)

        build_single_slide(slide, sdata, prs.slide_width, prs.slide_height)

    # Save final presentation
    prs.save(OUTPUT_PATH)
    print(f"Successfully saved completed presentation to {OUTPUT_PATH}")
    print(f"Total Slides in final deck: {len(prs.slides)}")

def set_shape_title(slide, title_text):
    # Find title placeholder or create title box
    title_shape = None
    for shape in slide.shapes:
        if shape.is_placeholder and shape.placeholder_format.idx == 0:
            title_shape = shape
            break
        elif "Google Shape" in shape.name and shape.top < Inches(1.0):
            title_shape = shape
            break

    if title_shape and title_shape.has_text_frame:
        tf = title_shape.text_frame
        tf.clear()
        p = tf.paragraphs[0]
        p.text = title_text
        p.font.size = Pt(22)
        p.font.bold = True
        p.font.name = FONT_TITLE
        p.font.color.rgb = NAVY
    else:
        # Add a custom title box at standard position
        txBox = slide.shapes.add_textbox(Inches(0.89), Inches(0.3), Inches(11.5), Inches(0.6))
        tf = txBox.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = title_text
        p.font.size = Pt(22)
        p.font.bold = True
        p.font.name = FONT_TITLE
        p.font.color.rgb = NAVY

def build_single_slide(slide, data, sw, sh):
    title = data.get("title", "")
    set_shape_title(slide, title)

    stype = data.get("type", "bullets")

    left_margin = Inches(0.89)
    top_margin = Inches(1.15)
    content_width = Inches(11.55)
    content_height = Inches(5.1)

    if stype == "bullets":
        bullets = data.get("bullets", [])
        txBox = slide.shapes.add_textbox(left_margin, top_margin, content_width, content_height)
        tf = txBox.text_frame
        tf.word_wrap = True
        for b_idx, bullet in enumerate(bullets):
            p = tf.paragraphs[0] if b_idx == 0 else tf.add_paragraph()
            if isinstance(bullet, tuple):
                header, text = bullet
                p.text = f"{header}: "
                p.font.bold = True
                p.font.size = Pt(14)
                p.font.color.rgb = DARK_BLUE
                p.font.name = FONT_BODY
                run = p.add_run()
                run.text = text
                run.font.bold = False
                run.font.size = Pt(14)
                run.font.color.rgb = DARK_GRAY
                run.font.name = FONT_BODY
            else:
                p.text = bullet
                p.font.size = Pt(14)
                p.font.color.rgb = DARK_GRAY
                p.font.name = FONT_BODY

            p.space_after = Pt(8)
            p.level = 0

    elif stype == "two_column":
        col1_title = data.get("col1_title", "")
        col1_bullets = data.get("col1_bullets", [])
        col2_title = data.get("col2_title", "")
        col2_bullets = data.get("col2_bullets", [])

        col_w = Inches(5.6)

        # Col 1 Box
        box1 = slide.shapes.add_textbox(left_margin, top_margin, col_w, content_height)
        tf1 = box1.text_frame
        tf1.word_wrap = True
        if col1_title:
            p0 = tf1.paragraphs[0]
            p0.text = col1_title
            p0.font.size = Pt(16)
            p0.font.bold = True
            p0.font.color.rgb = NAVY
            p0.space_after = Pt(8)

        for b_idx, b in enumerate(col1_bullets):
            p = tf1.add_paragraph() if (col1_title or b_idx > 0) else tf1.paragraphs[0]
            format_bullet(p, b)

        # Col 2 Box
        box2 = slide.shapes.add_textbox(left_margin + col_w + Inches(0.35), top_margin, col_w, content_height)
        tf2 = box2.text_frame
        tf2.word_wrap = True
        if col2_title:
            p0 = tf2.paragraphs[0]
            p0.text = col2_title
            p0.font.size = Pt(16)
            p0.font.bold = True
            p0.font.color.rgb = NAVY
            p0.space_after = Pt(8)

        for b_idx, b in enumerate(col2_bullets):
            p = tf2.add_paragraph() if (col2_title or b_idx > 0) else tf2.paragraphs[0]
            format_bullet(p, b)

    elif stype == "image_and_text":
        img_path = data.get("image_path", "")
        bullets = data.get("bullets", [])
        caption = data.get("caption", "")

        col1_w = Inches(5.8)
        col2_w = Inches(5.4)

        # Bullets on Left
        box = slide.shapes.add_textbox(left_margin, top_margin, col1_w, content_height)
        tf = box.text_frame
        tf.word_wrap = True
        for b_idx, bullet in enumerate(bullets):
            p = tf.paragraphs[0] if b_idx == 0 else tf.add_paragraph()
            format_bullet(p, bullet)

        # Image on Right
        if os.path.exists(img_path):
            img_left = left_margin + col1_w + Inches(0.35)
            img_top = top_margin + Inches(0.2)
            img_width = col2_w
            img_height = Inches(4.0)
            pic = slide.shapes.add_picture(img_path, img_left, img_top, width=img_width)

            # Caption below image
            if caption:
                cap_box = slide.shapes.add_textbox(img_left, img_top + pic.height + Inches(0.05), col2_w, Inches(0.5))
                cap_tf = cap_box.text_frame
                cap_tf.word_wrap = True
                cap_p = cap_tf.paragraphs[0]
                cap_p.text = caption
                cap_p.font.size = Pt(11)
                cap_p.font.italic = True
                cap_p.font.color.rgb = DARK_GRAY
                cap_p.alignment = PP_ALIGN.CENTER

    elif stype == "table":
        headers = data.get("headers", [])
        rows = data.get("rows", [])
        notes = data.get("notes", [])

        num_rows = len(rows) + 1
        num_cols = len(headers)

        table_top = top_margin
        table_height = Inches(0.4 * num_rows)
        table_shape = slide.shapes.add_table(num_rows, num_cols, left_margin, table_top, content_width, table_height)
        table = table_shape.table

        # Format Headers
        for c_idx, h in enumerate(headers):
            cell = table.cell(0, c_idx)
            cell.text = h
            cell.fill.solid()
            cell.fill.fore_color.rgb = NAVY
            p = cell.text_frame.paragraphs[0]
            p.font.bold = True
            p.font.size = Pt(11)
            p.font.color.rgb = WHITE
            p.font.name = FONT_TITLE
            p.alignment = PP_ALIGN.CENTER

        # Format Data Rows
        for r_idx, row in enumerate(rows):
            for c_idx, val in enumerate(row):
                cell = table.cell(r_idx + 1, c_idx)
                cell.text = str(val)
                p = cell.text_frame.paragraphs[0]
                p.font.size = Pt(10)
                p.font.color.rgb = DARK_GRAY
                p.font.name = FONT_BODY
                if c_idx == 0:
                    p.font.bold = True

        # Notes below table
        if notes:
            n_top = table_top + table_height + Inches(0.2)
            n_box = slide.shapes.add_textbox(left_margin, n_top, content_width, Inches(1.5))
            n_tf = n_box.text_frame
            n_tf.word_wrap = True
            for n_idx, note in enumerate(notes):
                p = n_tf.paragraphs[0] if n_idx == 0 else n_tf.add_paragraph()
                format_bullet(p, note)

def format_bullet(p, bullet):
    p.space_after = Pt(6)
    p.level = 0
    if isinstance(bullet, tuple):
        header, text = bullet
        p.text = f"{header}: "
        p.font.bold = True
        p.font.size = Pt(13)
        p.font.color.rgb = DARK_BLUE
        p.font.name = FONT_BODY
        run = p.add_run()
        run.text = text
        run.font.bold = False
        run.font.size = Pt(13)
        run.font.color.rgb = DARK_GRAY
        run.font.name = FONT_BODY
    else:
        p.text = bullet
        p.font.size = Pt(13)
        p.font.color.rgb = DARK_GRAY
        p.font.name = FONT_BODY

def get_all_slides_data():
    img_arch = str(PROJECT_ROOT / '07_DOCUMENTATION' / 'Architecture_Diagram.png')
    img_anomaly = str(PROJECT_ROOT / '07_DOCUMENTATION' / 'RESEARCH_PAPER' / 'assets' / 'fig_anomaly_view.png')
    img_timeline = str(PROJECT_ROOT / '07_DOCUMENTATION' / 'RESEARCH_PAPER' / 'assets' / 'fig_timeline_view.png')
    img_comparison = str(PROJECT_ROOT / '07_DOCUMENTATION' / 'RESEARCH_PAPER' / 'assets' / 'fig_comparison_view.png')
    img_report = str(PROJECT_ROOT / '07_DOCUMENTATION' / 'RESEARCH_PAPER' / 'assets' / 'fig_report_view.png')
    img_qr = str(PROJECT_ROOT / 'github_qr.png')

    return [
        # Slide 3
        {
            "title": "INDEX / TABLE OF CONTENTS",
            "type": "two_column",
            "col1_title": "Project Fundamentals & Architecture",
            "col1_bullets": [
                ("01. Problem Statement", "Multi-format DVB-S2 stream challenges"),
                ("02. Objectives", "3–5 measurable project goals"),
                ("03. Literature Review", "DVB-S2, GSE & anomaly detection research"),
                ("04. Research Gap", "Unifying post-demodulation stream diagnostics"),
                ("05. Proposed Methodology", "5-layer modular alternative-format architecture"),
                ("06. System Architecture", "End-to-end data pipeline flow"),
                ("07. Workflow & Data Strategy", "Multi-dataset ingestion across 5 raw folders"),
                ("08. Seven Core Features", "Overview of F1 through F7 modules")
            ],
            "col2_title": "Implementation & Verification Results",
            "col2_bullets": [
                ("09. Feature F1", "Stream Health & Priority-1 checks"),
                ("10. Feature F2", "AI Anomaly Detection via Isolation Forest"),
                ("11. Feature F3", "Pattern Detection & Shannon Entropy"),
                ("12. Feature F4", "Spatial Activity Timeline & HTML Dashboards"),
                ("13. Feature F5", "Diagnostic Anomaly Explanations (Signed Z-Score)"),
                ("14. Feature F6", "Stream Comparison Engine & Semantic Audit"),
                ("15. Feature F7", "Automatic Multi-Format Diagnostic Reporting"),
                ("16. Validation & Results", "240/240 Tests passing, Ground Truth Ledger, GitHub & Roadmap")
            ]
        },
        # Slide 4
        {
            "title": "PROBLEM STATEMENT",
            "type": "bullets",
            "bullets": [
                ("Format Heterogeneity", "DVB-S2 receiver output streams exist across multiple alternative encapsulation layers (Baseband Frames, GSE packets, and MPEG Transport Streams), requiring fragmented, proprietary command-line utilities for inspection."),
                ("Lack of Intelligent Anomaly Detection", "Conventional stream analyzers rely on basic static threshold checks, failing to detect subtle temporal anomalies, sudden jitter variations, corrupted modulation frames, or unexpected multiplex behaviors."),
                ("Absence of Unified Diagnostic Platforms", "Existing open-source tools typically focus only on one isolated format (e.g., MPEG-TS only or PCAP inspection only) without providing unified health metrics, explainable AI diagnostics, comparative stream analysis, or automated report generation."),
                ("Need for Unified Software Workflow", "An urgent operational requirement exists for an integrated software application capable of parsing all three native formats, evaluating stream integrity, detecting statistical anomalies, and delivering root-cause diagnostic explanations rather than raw packet dumps.")
            ]
        },
        # Slide 5
        {
            "title": "PROJECT OBJECTIVES",
            "type": "bullets",
            "bullets": [
                ("1. Multi-Format Receiver Stream Ingestion", "Ingest and parse native DVB-S2 receiver output streams across three alternative formats: Baseband (BB) Frames, GSE frames, and MPEG Transport Streams (TS)."),
                ("2. Stream Health & Integrity Assessment", "Compute quantitative stream integrity indicators including packet loss rate, Continuity Counter (CC) error frequency, sync byte validation, and jitter."),
                ("3. Machine Learning Anomaly Detection", "Deploy calibrated unsupervised machine learning algorithms (Isolation Forest with sigmoid score normalization) to identify irregular stream behavior and transmission degradation."),
                ("4. Structural Pattern & Entropy Mining", "Discover recurring patterns in stream transmission, PID multiplex allocations, modal Data Field Lengths (DFL), and Shannon entropy dynamics."),
                ("5. Interactive Visualization & Explainable Diagnostics", "Deliver dynamic spatial activity timelines, bounded signed Z-score feature attributions, differential stream comparisons, and automated multi-format diagnostic reports.")
            ]
        },
        # Slide 6
        {
            "title": "LITERATURE / RESEARCH UNDERSTANDING",
            "type": "bullets",
            "bullets": [
                ("DVB-S2 Standard Architecture (Morello & Mignone, 2006)", "Pioneered the second-generation satellite broadcasting architecture (ETSI EN 302 307), defining physical/link framing, MODCOD adaptation, BBHeader structure, and CRC-8 integrity."),
                ("Adaptive Coding & GSE Encapsulation (Albertazzi 2005, Cantillo 2007/2008)", "Investigated Adaptive Coding and Modulation (ACM) and Generic Stream Encapsulation (ETSI TS 102 606) for efficient IP transport over DVB-S2 continuous generic streams."),
                ("Satellite Telemetry Anomaly Detection (Arbon 2018, Pan 2020, Hundman 2018)", "Evaluated unsupervised tree-based models and LSTM networks for spacecraft telemetry, establishing that tree ensembles achieve robust anomaly detection without catastrophic deep-learning false positives."),
                ("Explainable AI & Diagnostic Attribution (Zeng 2022, Wang 2023)", "Demonstrated feature-attention mechanisms and causal attribution for interpreting telemetry deviations, reinforcing the need for interpretable Z-score feature attributions in stream diagnostics.")
            ]
        },
        # Slide 7
        {
            "title": "RESEARCH GAP ADDRESSED BY PRJ_111",
            "type": "two_column",
            "col1_title": "Limitations of Existing Tools",
            "col1_bullets": [
                ("Protocol Inspection (Wireshark/TSDuck)", "Manual packet inspection tools lack automated ML anomaly detection, timeline tracking, and executive report compilation."),
                ("Physical RF Signal Research", "Focuses strictly on raw I/Q samples and modulation recognition (QPSK/8PSK), operating below the de-encapsulated digital stream layer."),
                ("Generic Network NIDS", "Designed for IP Ethernet traffic; unsuited for native DVB-S2 link framing (BBHeaders, GSE fragmentation, MPEG-TS PIDs).")
            ],
            "col2_title": "PRJ_111 Engineering Solution",
            "col2_bullets": [
                ("Multi-Format Integration", "First unified framework accepting BBFrame, GSE, and MPEG-TS post-demodulation streams."),
                ("Automated ML Anomaly Detection", "Calibrated Isolation Forest with sigmoid normalization and rolling spatial windowing."),
                ("Semantic Cross-Format Audit", "Strictly guards metric comparability to prevent invalid cross-format conclusions."),
                ("Automated Tripartite Reporting", "Compiles executive reports in JSON, Markdown, Plain Text, and offline HTML5.")
            ]
        },
        # Slide 8
        {
            "title": "PROPOSED METHODOLOGY & ARCHITECTURE",
            "type": "bullets",
            "bullets": [
                ("Foundational Architectural Principle", "Baseband Frames (BBFrame), Generic Stream Encapsulation (GSE), and MPEG Transport Stream (TS) are treated as native alternative receiver output formats, NOT a mandatory sequential conversion pipeline (BBFrame → GSE → TS)."),
                ("1. Ingestion Layer", "Multi-tier magic-byte & heuristic format sniffer automatically dispatches incoming streams to dedicated native parsers."),
                ("2. Parsing & Preprocessing Layer", "Robust binary parsers extract 188B TS packets, variable GSE PDUs, and 10B BBHeaders with table-driven CRC-8 verification."),
                ("3. Feature Extraction Layer", "Standardized feature extractor constructs CommonMetrics and format-specific telemetry without cross-format flattening."),
                ("4. Intelligent Analysis Engine", "Houses F1 Health Engine, F2 Isolation Forest, F3 Pattern Detector, and F5 Signed Z-Score Diagnostic Explainer."),
                ("5. Application & Reporting Layer", "Houses F4 Spatial Offset Timelines, F6 Stream Comparison Engine, and F7 Executive Diagnostic Report Generator.")
            ]
        },
        # Slide 9
        {
            "title": "SYSTEM ARCHITECTURE DIAGRAM",
            "type": "image_and_text",
            "image_path": img_arch,
            "caption": "Figure 1: PRJ_111 Layered System Architecture & Data Flow Pipeline",
            "bullets": [
                ("Layer 1: Stream Ingestion", "Native receiver captures (.ts, .pcap, .bin) ingested with automatic format sniffing."),
                ("Layer 2: Format Parsers", "Dedicated parsers for MPEG-TS, GSE PDUs, and DVB-S2 BBFrames with table CRC-8."),
                ("Layer 3: Unified Features", "Extracts CommonMetrics and format-specific structural metrics."),
                ("Layer 4: AI & Diagnostics", "F1 Health scoring, F2 Isolation Forest anomaly detection, F3 Pattern/Entropy mining, F5 Z-score explainer."),
                ("Layer 5: Application Output", "F4 Timelines, F6 Semantic Comparisons, and F7 Executive Reports.")
            ]
        },
        # Slide 10
        {
            "title": "END-TO-END PROCESSING PIPELINE",
            "type": "bullets",
            "bullets": [
                ("Step 1: Stream Ingestion & Sniffing", "StreamHandler inspects binary headers to auto-detect stream type and dispatches to TSParser, GSEParser, or BBFrameParser."),
                ("Step 2: Deterministic Binary Parsing", "Parses framing headers, checks sync byte 0x47, validates CC sequence, extracts GSE PDUs, or checks BBHeader CRC-8."),
                ("Step 3: Feature Extraction & Windowing", "Calculates payload byte volumes, error counts, and aggregates stream telemetry into rolling spatial windowing blocks."),
                ("Step 4: AI Anomaly & Pattern Mining", "Executes F1 Priority-1 health scoring, F2 Isolation Forest inference, F3 Shannon entropy calculation, and F5 Z-score attribution."),
                ("Step 5: Differential Audit & Report Synthesis", "Executes F6 semantic cross-format audit and F7 multi-renderer executive report generation (JSON/MD/TXT/HTML).")
            ]
        },
        # Slide 11
        {
            "title": "DATASET STRATEGY & RECEIVER OUTPUT FORMATS",
            "type": "bullets",
            "bullets": [
                ("01_BBFRAME_GSE/ (BBFrame Dataset)", "dvb-s2_bb_example.pcap (2.35 MB, 4,309 BBFrames) — Real DVB-S2 Baseband validation capture for link-layer header analysis."),
                ("02_GSE/ (GSE Dataset)", "GSExtract/sample.ts (9,324 B, 14 PDUs) — Real GSE encapsulation validation capture for IP PDU de-encapsulation."),
                ("03_TS/ (MPEG-TS Dataset)", "DVBS2_toolkit/sample.ts (3.42 MB, 18,176 pkts) + Astra 19.2°E satellite captures — Real MPEG-TS transport stream validation data."),
                ("04_RFI_AI/ & 05_REAL_DVB_S2/ (Reference Archives)", "Blockstream over-the-air DVB-S2 capture (blockstream.ts & ip_packets.pcap) + RFI reference data archives for AI feature exploration."),
                ("Data Retention & Security Policy", "All raw binary datasets are retained locally on dev workstations and excluded from GitHub via .gitignore adhering to best practices.")
            ]
        },
        # Slide 12
        {
            "title": "SEVEN CORE TARGET FEATURES (F1–F7)",
            "type": "two_column",
            "col1_title": "Core Analytical Engines (F1–F4)",
            "col1_bullets": [
                ("F1: Stream Health Analysis", "Quantifies transmission quality via ETSI TR 101 290 Priority-1 checks and 0–100 health scoring."),
                ("F2: AI Anomaly Detection", "Unsupervised Isolation Forest (c=0.05) flagging atypical stream deviations with sigmoid normalization."),
                ("F3: Pattern Detection", "Identifies recurring PID shares, modal DFL sizing, protocol distributions, and Shannon entropy."),
                ("F4: Spatial Activity Timeline", "Visualizes stream activity, bandwidth consumption, and error events over physical byte offsets.")
            ],
            "col2_title": "Diagnostic & Reporting Engines (F5–F7)",
            "col2_bullets": [
                ("F5: Anomaly Explanation", "Delivers bounded signed Z-score attributions mapping deviations to physical subsystems."),
                ("F6: Stream Comparison Engine", "Side-by-side differential analysis enforcing a semantic audit to prevent invalid cross-format metric comparison."),
                ("F7: Automatic Analysis Report", "Generates consolidated executive diagnostic reports across JSON, Markdown, Plain Text, and offline HTML5.")
            ]
        },
        # Slide 13
        {
            "title": "F1 — STREAM HEALTH AND PRIORITY-1 CHECKS",
            "type": "bullets",
            "bullets": [
                ("Priority-1 Stream Integrity Checks", "Evaluates ETSI TR 101 290 Priority-1 indicators: MPEG-TS sync byte consistency (0x47), Continuity Counter (CC) errors, Transport Error Indicator (TEI) flags, and BBHeader CRC-8 checks."),
                ("Objective Health Scoring Equation", "S_health = 100.0 - sum(penalties), strictly bounded within [0.0, 100.0]. Classifies streams into HEALTHY [90-100], DEGRADED [60-89], or CRITICAL [0-59]."),
                ("Empirical Baseline Validation", "All real-world validation captures (sample.ts, dvb-s2_bb_example.pcap, GSExtract/sample.ts) achieved 100.00 / 100 (HEALTHY) with zero framing errors."),
                ("Controlled Fault Injection", "Synthetic error injection verified that CC sequence breaks, sync byte corruption, and CRC-8 failures cleanly trigger objective health score penalties.")
            ]
        },
        # Slide 14
        {
            "title": "F2 — AI-BASED ANOMALY DETECTION",
            "type": "image_and_text",
            "image_path": img_anomaly,
            "caption": "Figure 2: F2 Interactive Anomaly Detection Interface & Score Trajectory",
            "bullets": [
                ("Algorithm & Configuration", "Unsupervised Isolation Forest ensemble (contamination factor c=0.05, format-specific rolling windowing)."),
                ("Sigmoid Score Normalization", "Raw tree decision scores mapped to [0.0, 1.0]: S_norm = 1 / (1 + e^-k(s_raw - theta))."),
                ("MPEG-TS Anomaly Results", "91 windows (w=200 pkts): 5 anomalous windows [1, 2, 12, 88, 90], Peak Score = 0.8576 (EOF boundary)."),
                ("BBFrame Anomaly Results", "87 windows (w=50 frames): 5 anomalous windows [0, 83, 84, 85, 86], Peak Score = 0.7406 (EOF boundary)."),
                ("GSE Anomaly Results", "5 windows (w=3 PDUs): 1 anomalous window [4], Peak Score = 0.5018 (EOF boundary).")
            ]
        },
        # Slide 15
        {
            "title": "F3 — PATTERN DETECTION & SHANNON ENTROPY",
            "type": "bullets",
            "bullets": [
                ("Operational Behavior Profiling", "Tracks multiplex allocations, modal sizing, protocol shares, and structural transitions over rolling windows."),
                ("Shannon Entropy Calculation", "H(X) = -sum(P(x_i) * log2(P(x_i))) measures information uncertainty and multiplex randomness."),
                ("MPEG-TS Dominant PID & Entropy", "Dominant PID 256 (98.5% multiplex share), Shannon entropy = 0.1361 bits (highly concentrated video broadcast multiplex)."),
                ("GSE Protocol Distribution", "Dominant protocol GSE_EXT_NPA (100.0% share), Shannon entropy = 0.0000 bits (single-protocol transport stream)."),
                ("BBFrame Modal Sizing", "Modal Data Field Length (DFL) = 8304 bits (92.0% share), reflecting uniform physical frame packaging.")
            ]
        },
        # Slide 16
        {
            "title": "F4 — SPATIAL ACTIVITY TIMELINE",
            "type": "image_and_text",
            "image_path": img_timeline,
            "caption": "Figure 3: F4 Spatial Activity Timeline Dashboard",
            "bullets": [
                ("Physical Offset Indexing", "Indexes stream activity over physical byte offsets and sequential unit indices, avoiding wall-clock clock fabrication."),
                ("Time-Series Metric Extraction", "Continuously tracks rolling health score, anomaly score trajectory, and payload byte density."),
                ("Event Mapping Engine", "Automatically flags health drops, anomaly peaks, and structural transitions on the spatial axis."),
                ("Standalone Interactive Dashboard", "Compiles self-contained HTML5 dashboards with embedded CSS for responsive offline operator inspection.")
            ]
        },
        # Slide 17
        {
            "title": "F5 — DIAGNOSTIC ANOMALY EXPLANATIONS",
            "type": "bullets",
            "bullets": [
                ("Explainable AI Mechanism", "Computes bounded signed Z-scores: Z_i = (x_i - mu_i) / max(sigma_i, sigma_min), capped at [-20.0, +20.0]."),
                ("Physical Subsystem Mapping", "Maps deviated feature Z-scores directly to physical satellite stream subsystems:"),
                ("• dominant_pid", "MPEG-TS Multiplex / Dominant PID Allocation"),
                ("• null_packet_ratio", "Bandwidth Adaptation / Null Stuffing"),
                ("• crc_error_count", "Baseband Header Integrity / CRC Checksum"),
                ("• modal_dfl_bits", "Frame Sizing / Mode Adaptation"),
                ("Ranked Diagnostic Synthesis", "Ranks features by |Z| and generates evidence-grounded explanatory sentences for operators.")
            ]
        },
        # Slide 18
        {
            "title": "F6 — STREAM COMPARISON & SEMANTIC AUDIT",
            "type": "image_and_text",
            "image_path": img_comparison,
            "caption": "Figure 4: F6 Stream Comparison Interface & Differential Metrics",
            "bullets": [
                ("Semantic Cross-Format Audit", "Enforces strict metric compatibility guard: 9 metrics barred cross-format (total_units, valid_units, mean_payload, etc.)."),
                ("Cross-Format Comparable Metrics", "Only total_payload_bytes and integrity_ratio are physically comparable across distinct formats."),
                ("MPEG-TS vs BBFrame Payload", "MPEG-TS payload = 3,267,305 B, BBFrame payload = 1,958,826 B. Delta = -1,308,479 B (-40.05% SUBSTANTIAL shift)."),
                ("Integrity Ratio Comparison", "MPEG-TS integrity = 1.0000, BBFrame integrity = 1.0000 (EQUAL, perfect syntactic integrity across both captures).")
            ]
        },
        # Slide 19
        {
            "title": "F7 — AUTOMATIC MULTI-FORMAT REPORTING",
            "type": "image_and_text",
            "image_path": img_report,
            "caption": "Figure 5: F7 Executive Diagnostic Report Generator Interface",
            "bullets": [
                ("Non-Duplication Executive Synthesis", "Directly consumes outputs from F1–F6 without re-parsing streams or re-running ML models."),
                ("Tripartite Findings Taxonomy", "Categorizes every report finding into three epistemological registers: OBSERVED_FACT, STATISTICAL_FINDING, and ENGINEERING_INTERPRETATION."),
                ("Multi-Format Renderers", "Exports comprehensive diagnostic reports in structured JSON, GitHub-Flavored Markdown, CP-1252-safe Plain Text, and offline HTML5."),
                ("Domain-Safety Guard", "Immutable guard blocks speculative physical RF/hardware claims in generated report text.")
            ]
        },
        # Slide 20
        {
            "title": "SYSTEM IMPLEMENTATION PROGRESS",
            "type": "bullets",
            "bullets": [
                ("Current Project Completion Status", "Core implementation is substantially completed across F1–F7, with automated validation and demonstration outputs available. Backend features F1 through F7 are 100% implemented, audited, and frozen."),
                ("Stream Ingestion & Sniffing", "100% Completed & Audited (Multi-tier format sniffer, 14 dedicated unit tests passing)."),
                ("Multi-Format Parsers (TS / GSE / BBFrame)", "100% Completed & Audited (61 dedicated unit tests passing, table-driven CRC-8 implemented)."),
                ("Analytics & AI Engines (F1–F7)", "100% Completed & Audited (132 dedicated unit tests passing across health, anomaly, timeline, explanation, comparison, and reporting)."),
                ("Automated Test Suite", "100% Completed & Verified (240/240 tests passing across backend and frontend).")
            ]
        },
        # Slide 21
        {
            "title": "AUTHORITATIVE GROUND TRUTH RESULTS LEDGER",
            "type": "table",
            "headers": ["Metric Dimension", "MPEG-TS Stream", "BBFrame Stream", "GSE Stream", "Cross-Format Comparison"],
            "rows": [
                ["Input File Path", "sample.ts", "dvb-s2_bb_example.pcap", "GSExtract/sample.ts", "MPEG-TS vs BBFrame"],
                ["Total Units Parsed", "18,176 packets", "4,309 frames", "14 PDUs", "18,176 pkts vs 4,309 frames"],
                ["Syntactic Validity", "100.0% (18,176/18,176)", "100.0% (4,309/4,309)", "100.0% (14/14)", "100.0% vs 100.0% (EQUAL)"],
                ["Extracted Payload", "3,267,305 bytes", "1,958,826 bytes", "8,764 bytes", "Delta: -1,308,479 B (-40.05%)"],
                ["Windowing Scheme", "91 win (w=200 pkts)", "87 win (w=50 frames)", "5 win (w=3 PDUs)", "91 win vs 87 win"],
                ["F1 Health Score", "100.00 / 100 (HEALTHY)", "100.00 / 100 (HEALTHY)", "100.00 / 100 (HEALTHY)", "100.00 vs 100.00 (COMPARABLE)"],
                ["F2 Anomaly Windows", "5 [1, 2, 12, 88, 90]", "5 [0, 83, 84, 85, 86]", "1 [4]", "9 metrics NOT_COMPARABLE"],
                ["Peak Anomaly Score", "0.8576 (Window 90)", "0.7406 (Window 86)", "0.5018 (Window 4)", "Format-specific models"],
                ["Dominant Feature", "PID 256 (98.5% share)", "Modal DFL 8304b (92%)", "GSE_EXT_NPA (100%)", "Structural metrics barred"],
                ["Shannon Entropy", "0.1361 bits", "N/A (Continuous DFL)", "0.0000 bits", "NOT_COMPARABLE"]
            ],
            "notes": [
                ("Reconciled Ground Truth", "All numbers match the authoritative ground truth ledger. Peak BBFrame anomaly score 0.7406 reconciled.")
            ]
        },
        # Slide 22
        {
            "title": "GSE CAPTURE INGESTION & DECODING DETAILS",
            "type": "bullets",
            "bullets": [
                ("Authoritative GSE Capture File", "01_RAW_DATA/02_GSE/GSExtract/sample.ts (File size: 9,324 bytes)."),
                ("Observed Decoded PDUs", "14 variable-length GSE Protocol Data Units (PDUs) extracted and validated."),
                ("GSE Length Field Specification", "12-bit header length field (Valid range: 0–4095 bytes payload)."),
                ("Theoretical Maximum PDU Size", "4097 bytes including the 2-byte base header."),
                ("Observed Maximum PDU Size", "1,444 bytes observed in the sample capture stream."),
                ("Format Auto-Sniffing Handling", "File extension .ts retained natively; multi-tier format sniffer correctly identifies GSE PDU content without requiring file renaming to .gse.")
            ]
        },
        # Slide 23
        {
            "title": "TESTING AND VALIDATION FRAMEWORK",
            "type": "bullets",
            "bullets": [
                ("Total Test Suite Validation Result", "240 / 240 Passing Tests (100% Pass Rate across the entire application)."),
                ("207 Backend Unit Tests", "11 dedicated test modules executing under Python's native unittest framework in 8.710 seconds:"),
                ("• test_ts_parser (20 tests)", "188B packet parsing, sync recovery, PID filtering, CC checking, TEI detection"),
                ("• test_gse_parser (18 tests)", "Variable PDU lengths, S/E fragmentation flags, LT types, EtherType extraction"),
                ("• test_bbframe_parser (23 tests)", "10B BBHeader parsing, MATYPE flags, UPL/DFL, table-driven CRC-8 verification"),
                ("• test_stream_handler & features (24 tests)", "Multi-tier format sniffing, unified metric extraction, Shannon entropy"),
                ("• test_health, anomaly & patterns (48 tests)", "Priority-1 health penalties, Isolation Forest calibration, transition filtering"),
                ("• test_timeline, explanation, comparison, report (74 tests)", "Byte offset tracking, signed Z-scores, semantic audit, multi-format renderers"),
                ("33 Frontend Component Tests", "33 UI tests verifying interactive timeline controls, dashboard rendering, and export state.")
            ]
        },
        # Slide 24
        {
            "title": "TECHNOLOGIES & ENGINEERING STACK",
            "type": "two_column",
            "col1_title": "Backend Analytics & AI Core",
            "col1_bullets": [
                ("Programming Language", "Python 3.x (Core implementation)"),
                ("Scientific Computing", "NumPy (>=1.26), SciPy (>=1.11), Pandas (>=2.1)"),
                ("Machine Learning Engine", "scikit-learn (Isolation Forest anomaly model)"),
                ("Testing Framework", "Python unittest, pytest (>=7.4), pytest-cov")
            ],
            "col2_title": "Visualization, UI & Tooling",
            "col2_bullets": [
                ("Visualization Engines", "Matplotlib (>=3.8), Plotly, HTML5, CSS3"),
                ("Reporting Generators", "JSON, GitHub-Flavored Markdown, ASCII Text, Standalone HTML5"),
                ("IDE & Version Control", "VS Code, Git, GitHub Repository"),
                ("Operating System", "Cross-platform support (Windows / Linux)")
            ]
        },
        # Slide 25
        {
            "title": "INDIVIDUAL CONTRIBUTIONS & RESPONSIBILITIES",
            "type": "table",
            "headers": ["Team Member Name", "University Roll No.", "Project Role", "Technical Responsibilities & Completed Modules"],
            "rows": [
                ["Sk Samad", "20231COM0031", "Testing, Validation & Documentation Lead", "Automated test suite execution (207 backend / 33 frontend tests), technical documentation authoring, literature review synthesis, experimental report verification."],
                ["Y Vengala Rao", "20231COM0001", "Frontend, Visualization & Development", "Frontend UI MVP development, interactive timeline chart components, dashboard layout design, presentation slide deck authoring."],
                ["C Rakeshwar", "20231COM0008", "Core Development & Technical Lead", "Backend architecture, multi-format stream parsers (TS/GSE/BBFrame), F1–F7 analysis engines, AI/ML Isolation Forest model integration, system integration."]
            ],
            "notes": [
                ("Equal Team Contribution", "All team members actively contributed to development, verification, and documentation under guide supervision.")
            ]
        },
        # Slide 26
        {
            "title": "GITHUB REPOSITORY ACCESS",
            "type": "image_and_text",
            "image_path": img_qr,
            "caption": "Scan QR code to access public GitHub repository",
            "bullets": [
                ("Public Repository Access", "The official PRJ_111 source code, test suite, and documentation are hosted with full public access permission."),
                ("Repository URL", "https://github.com/rakesh0709/PRJ_111_DVB-S2_Analysis.git"),
                ("Repository Contents", "Complete F1–F7 implementation, 207 backend unit tests, 5 real-data experiment scripts, documentation ledgers, and standalone report renderers."),
                ("Branching & Maintenance", "Active development branch maintained under git version control with comprehensive commit history.")
            ]
        },
        # Slide 27
        {
            "title": "OPERATIONAL LIMITATIONS",
            "type": "bullets",
            "bullets": [
                ("Absence of Physical RF Telemetry", "Operating on post-demodulator digital output, the software cannot directly measure physical RF carrier parameters (SNR, MER, C/N, carrier offset, or LNB drift)."),
                ("Offline File Capture Focus", "Processes pre-recorded stream captures (.ts, .pcap, .bin); live Software-Defined Radio (SDR) hardware streaming is not currently integrated."),
                ("Scarcity of Public Labeled Ground Truth", "The absence of standardized, frame-labeled satellite fault benchmarks requires unsupervised Isolation Forest modeling rather than supervised classification."),
                ("Format-Specific Header Parsing Scope", "Relies on standardized structural headers (BBHeader, GSE PDU, TS 188B); proprietary unencapsulated payloads require format adapters.")
            ]
        },
        # Slide 28
        {
            "title": "FUTURE WORK ROADMAP",
            "type": "bullets",
            "bullets": [
                ("Full PSI/SI Table Parsing", "Implement full Program Association Table (PAT), Program Map Table (PMT), and Service Information decoders resolving elementary audio/video codecs (AVC/H.264, HEVC, AC-3)."),
                ("Physical RF Cross-Correlation", "Ingest external demodulator telemetry logs (SNR/AGC) for cross-layer correlation between physical link budget and digital stream health."),
                ("Deep Learning Model Extensions", "Integrate semi-supervised Autoencoders and LSTM networks trained on synthetic fault injection benchmarks."),
                ("Real-Time SDR Streaming Integration", "Support real-time circular buffer streaming directly from GNU Radio or USRP SDR hardware tuners.")
            ]
        },
        # Slide 29
        {
            "title": "CONCLUSION",
            "type": "bullets",
            "bullets": [
                ("Unified Multi-Format Solution", "Successfully developed a software application for analysis and processing of DVB-S2 receiver output streams across MPEG-TS, GSE, and BBFrame formats."),
                ("Comprehensive Feature Implementation", "Features F1 through F7 are 100% implemented, audited, and verified with an automated test suite achieving 240 / 240 passing tests (100% pass rate)."),
                ("Rigorous Engineering & Epistemic Guard", "Enforced a semantic cross-format audit preventing invalid metric comparisons, bounded signed Z-score diagnostic attributions, and strict domain-safety guards."),
                ("Validated Operational Readiness", "Empirically validated against real satellite broadcast captures and deployed automated multi-format report renderers for operator decision support.")
            ]
        },
        # Slide 30
        {
            "title": "REFERENCES (IEEE FORMAT)",
            "type": "bullets",
            "bullets": [
                ("[1] A. Morello and V. Mignone", "DVB-S2: The Second Generation Standard for Satellite Broad-Band Services, Proc. IEEE, vol. 94, no. 1, pp. 210–227, 2006."),
                ("[2] G. Albertazzi et al.", "On the Adaptive DVB-S2 Physical Layer: Design and Performance, IEEE Wireless Commun., vol. 12, no. 6, pp. 62–68, 2005."),
                ("[3] E. Casini et al.", "DVB-S2 Modem Algorithms Design and Performance over Typical Satellite Channels, Int. J. Satell. Commun. Netw., vol. 22, no. 3, pp. 281–318, 2004."),
                ("[4] J. Cantillo et al.", "GSE: A Flexible, Yet Efficient, Encapsulation for IP over DVB-S2 Continuous Generic Streams, Int. J. Satell. Commun. Netw., vol. 26, pp. 231–250, 2008."),
                ("[5] J. Cantillo et al.", "Design Issues for Generic Stream Encapsulation (GSE) over DVB-S2, in Proc. IWSSC, 2007, pp. 276–280."),
                ("[6] P. Th. Savvopoulos et al.", "A Software-Radio Test-bed for DVB-S2 Receiver Performance, in Proc. SPSC, 2008."),
                ("[7] K. Hundman et al.", "Detecting Spacecraft Anomalies Using LSTMs and Nonparametric Dynamic Thresholding, in Proc. ACM KDD, 2018, pp. 387–395."),
                ("[8] E. Arbon et al.", "Anomaly Detection in Satellite Communications Systems using LSTM Networks, in Proc. MilCIS, IEEE, 2018."),
                ("[9] D. Pan et al.", "Satellite Telemetry Data Anomaly Detection Using Bi-LSTM Prediction Based Model, in Proc. IEEE I2MTC, 2020."),
                ("[10] Z. Zeng et al.", "Satellite Telemetry Data Anomaly Detection Using Causal Network and Feature-Attention-Based LSTM, IEEE Trans. Instrum. Meas., vol. 71, 2022.")
            ]
        },
        # Slide 31
        {
            "title": "THANK YOU / QUESTIONS & DEFENSE",
            "type": "bullets",
            "bullets": [
                ("Project Identifier", "PRJ_111"),
                ("Project Full Title", "Development of a Software Application for Analysis and Processing of DVB-S2 Receiver Output Stream"),
                ("Academic Milestone", "CSE7102 – Mini Project (Review-2 Milestone | 26-09-2026)"),
                ("Supervising Guide", "Asst. Prof. Irfan Rajab Bhat"),
                ("Department & School", "Department of Computer Science and Engineering, Presidency School of Computer Science and Engineering, Presidency University, Bengaluru"),
                ("Open for Questions", "We welcome feedback, technical questions, and defense evaluation from the review panel.")
            ]
        }
    ]

if __name__ == '__main__':
    create_presentation()
