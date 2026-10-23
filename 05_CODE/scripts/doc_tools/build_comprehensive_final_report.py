"""
build_comprehensive_final_report.py
Constructs the complete, authoritative, comprehensive University Final Project Report
for PRJ_111 in strict compliance with Presidency University guidelines (PART-A, PART-B, PART-C_CONTENT).

Features:
- Exact university chapter sequence (Chapters 1-10 + References + Appendices A-D)
- Times New Roman throughout: Chapter titles 18pt bold centered, Section titles 16pt bold left,
  Subsection titles 14pt bold left, Body 12pt justified, 1.5 line spacing.
- Section 1: Title page (no page number)
- Section 2: Preliminary front matter (Roman numerals starting at vi)
- Section 3: Chapters & Appendices (Arabic numerals starting at 1)
- Embedded real high-resolution screenshots & diagrams
- Synchronized with verified 304 automated tests
- Comprehensive mathematical formulations & 18 detailed empirical tables
- Word COM automation to configure headers/footers and export to PDF.
"""

import os
import sys
import shutil
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

# Ensure scripts/doc_tools is in sys.path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

from report_content.front_matter import build_front_matter
from report_content.ch1_intro import build_ch1
from report_content.ch2_literature import build_ch2
from report_content.ch3_gaps import build_ch3
from report_content.ch4_methodology import build_ch4
from report_content.ch5_objectives import build_ch5
from report_content.ch6_implementation import build_ch6
from report_content.ch7_timeline import build_ch7
from report_content.ch8_outcomes import build_ch8
from report_content.ch9_results import build_ch9
from report_content.ch10_conclusion import build_ch10
from report_content.references_data import build_references
from report_content.appendices import build_appendices

def build_report():
    print("Initializing Document...", flush=True)
    doc = docx.Document()
    
    # Configure default Normal style
    style = doc.styles['Normal']
    font = style.font
    font.name = 'Times New Roman'
    font.size = Pt(12)
    font.color.rgb = RGBColor(0, 0, 0)
    
    # Set default section margins
    for sec in doc.sections:
        sec.top_margin = Inches(1.0)
        sec.bottom_margin = Inches(1.0)
        sec.left_margin = Inches(1.25) # Standard university left binding margin
        sec.right_margin = Inches(1.0)
        
    print("Building Front Matter (Title Page, Certificates, Abstract, TOC, Lists)...", flush=True)
    build_front_matter(doc)
    
    print("Adding Section Break for Main Chapters...", flush=True)
    sec_main = doc.add_section() # Section 3 for Main Report Body
    sec_main.top_margin = Inches(1.0)
    sec_main.bottom_margin = Inches(1.0)
    sec_main.left_margin = Inches(1.25)
    sec_main.right_margin = Inches(1.0)
    
    print("Building Chapter 1: Introduction...", flush=True)
    build_ch1(doc)
    
    print("Building Chapter 2: Literature Survey...", flush=True)
    build_ch2(doc)
    
    print("Building Chapter 3: Research Gaps of Existing Methods...", flush=True)
    build_ch3(doc)
    
    print("Building Chapter 4: Proposed Methodology...", flush=True)
    build_ch4(doc)
    
    print("Building Chapter 5: Objectives and Specifications...", flush=True)
    build_ch5(doc)
    
    print("Building Chapter 6: System Design and Implementation...", flush=True)
    build_ch6(doc)
    
    print("Building Chapter 7: Timeline for Execution of Project (Gantt Chart)...", flush=True)
    build_ch7(doc)
    
    print("Building Chapter 8: Outcomes...", flush=True)
    build_ch8(doc)
    
    print("Building Chapter 9: Results and Discussions...", flush=True)
    build_ch9(doc)
    
    print("Building Chapter 10: Conclusion and Future Work...", flush=True)
    build_ch10(doc)
    
    print("Building References...", flush=True)
    build_references(doc)
    
    print("Building Appendices A, B, C, D...", flush=True)
    build_appendices(doc)
    
    out_docx = os.path.abspath("07_DOCUMENTATION/PRJ_111_Final_Project_Report.docx")
    out_docx_alt = os.path.abspath("07_DOCUMENTATION/PRJ_111_Final_Documentation.docx")
    out_pdf = os.path.abspath("07_DOCUMENTATION/PRJ_111_Final_Project_Report.pdf")
    out_pdf_alt = os.path.abspath("07_DOCUMENTATION/PRJ_111_Final_Documentation.pdf")
    
    print(f"Saving DOCX to {out_docx}...", flush=True)
    doc.save(out_docx)
    shutil.copyfile(out_docx, out_docx_alt)
    print(f"Copied duplicate to {out_docx_alt}...", flush=True)
    
    # Word COM Automation for formatting and PDF conversion
    print("Invoking Word COM for page numbering and PDF generation...", flush=True)
    import win32com.client
    word = win32com.client.DispatchEx("Word.Application")
    word.Visible = False
    word.DisplayAlerts = 0
    
    wdoc = word.Documents.Open(out_docx)
    try:
        print(f"Configuring {wdoc.Sections.Count} sections in Word...", flush=True)
        
        # Section 1: Title Page (No header/footer)
        sec1 = wdoc.Sections(1)
        sec1.Footers(1).LinkToPrevious = False
        
        # Section 2: Prelims (Roman lowercase starting at vi)
        if wdoc.Sections.Count >= 2:
            sec2 = wdoc.Sections(2)
            sec2.Footers(1).LinkToPrevious = False
            sec2.Footers(1).PageNumbers.NumberStyle = 2 # wdPageNumberStyleLowercaseRoman = 2
            sec2.Footers(1).PageNumbers.RestartNumberingAtSection = True
            sec2.Footers(1).PageNumbers.StartingNumber = 6
            sec2.Footers(1).PageNumbers.Add(1, True) # wdAlignPageNumberCenter = 1
            
        # Section 3: Main Chapters & Appendices (Arabic starting at 1)
        if wdoc.Sections.Count >= 3:
            sec3 = wdoc.Sections(3)
            sec3.Footers(1).LinkToPrevious = False
            sec3.Footers(1).PageNumbers.NumberStyle = 0 # wdPageNumberStyleArabic = 0
            sec3.Footers(1).PageNumbers.RestartNumberingAtSection = True
            sec3.Footers(1).PageNumbers.StartingNumber = 1
            sec3.Footers(1).PageNumbers.Add(1, True)
            
        # Update document fields & save
        wdoc.Fields.Update()
        wdoc.Save()
        
        # Statistics
        pages = wdoc.ComputeStatistics(2) # wdStatisticPages = 2
        words = wdoc.ComputeStatistics(0) # wdStatisticWords = 0
        paras = wdoc.ComputeStatistics(4) # wdStatisticParagraphs = 4
        print(f"\n=======================================================", flush=True)
        print(f"DOCUMENT COMPILED SUCCESSFULLY!", flush=True)
        print(f"Total Pages:      {pages}", flush=True)
        print(f"Total Words:      {words}", flush=True)
        print(f"Total Paragraphs: {paras}", flush=True)
        print(f"=======================================================\n", flush=True)
        
        # Export PDF
        print(f"Exporting PDF to {out_pdf}...", flush=True)
        wdoc.ExportAsFixedFormat(out_pdf, 17) # wdExportFormatPDF = 17
        shutil.copyfile(out_pdf, out_pdf_alt)
        print(f"Copied duplicate PDF to {out_pdf_alt}...", flush=True)
        
    finally:
        wdoc.Close(False)
        word.Quit()
        
    print("Build complete!", flush=True)

if __name__ == "__main__":
    build_report()
