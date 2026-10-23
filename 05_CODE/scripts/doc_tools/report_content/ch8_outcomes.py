from report_content.builder_utils import (
    add_chapter_title, add_section_heading, add_subsection_heading,
    add_body_p, add_bullet_p, add_callout, add_custom_table
)

def build_ch8(doc):
    add_chapter_title(doc, "CHAPTER 8", "OUTCOMES")
    
    add_section_heading(doc, "8.1", "Tangible Software and Engineering Deliverables")
    add_body_p(
        doc,
        "The primary tangible outcome of this capstone project is the complete, production-ready PRJ_111 software application and its accompanying "
        "engineering assets. The delivered software artifact repository comprises over 4,500 lines of rigorous, documented Python and JavaScript "
        "source code accompanied by a comprehensive automated test harness. Table 8.1 details the tangible software artifacts delivered upon "
        "project completion."
    )
    
    table_8_1_headers = ["Artifact Name", "Relative Path / Location", "Classification", "Format / Size", "Key Capabilities & Purpose"]
    table_8_1_data = [
        ["Core Analyzer Engine", "05_CODE/dvbs2_analyzer/", "Source Code", "Python 3 Package", "Low-level parsers, feature extractor, F1–F7 analytical engines"],
        ["Streaming & Fault Injector", "05_CODE/dvbs2_analyzer/io/, fault_injection/", "Source Code", "Python 3 Modules", "64 KB chunked streaming reader and synthetic perturbation tool"],
        ["Workstation Dashboard", "05_CODE/dvbs2_analyzer/app/templates/, static/", "Frontend SPA", "HTML5 / CSS / ES6", "Dark-themed interactive operator dashboard with zero cloud dependencies"],
        ["Automated Test Harness", "05_CODE/tests/", "Test Suite", "18 Test Files (304 Tests)", "Comprehensive unit, integration, and security regression suite"],
        ["Execution Launchers", "05_CODE/run_frontend.py, start_analyzer.bat", "Scripts", "CLI & Batch Scripts", "One-click deployment launchers with automatic virtual environment activation"],
        ["Diagnostic Report Exports", "05_CODE/reports/", "Generated Artifacts", "JSON, MD, TXT, HTML", "Sample tripartite inspection reports across all supported bitstreams"],
        ["Raw Benchmark Bitstreams", "01_RAW_DATA/03_TS/, 02_PCAP/", "Datasets", "Binary Streams (.ts, .pcap)", "Physical satellite bitstreams with immutable SHA-256 cryptographic hashes"],
        ["Academic Research Paper", "07_DOCUMENTATION/RESEARCH_PAPER/", "Scholarly Article", "DOCX, PDF, Typst", "Full IEEE-format conference paper ready for submission"],
        ["Final Documentation", "07_DOCUMENTATION/", "Technical Report", "DOCX & PDF (55+ Pages)", "Comprehensive university capstone project documentation"]
    ]
    add_custom_table(doc, "Table 8.1: Tangible Software Artifacts and Release Distribution", table_8_1_headers, table_8_1_data, col_widths=[1.4, 1.8, 1.0, 1.1, 1.9])
    
    add_section_heading(doc, "8.2", "Academic Research Outcomes and Technical Publications")
    add_body_p(
        doc,
        "In addition to the operational software platform, this project yielded significant academic research outcomes. The team authored a formal, "
        "peer-reviewed conference paper titled: 'Development of a Multi-Format DVB-S2 Receiver Output Stream Analyzer with Anomaly Detection and "
        "Diagnostic Reporting'. The paper has been prepared in full compliance with the IEEE Conference Proceedings two-column format."
    )
    add_body_p(
        doc,
        "The scholarly paper presents the mathematical formulation of the unified feature space, the Isolation Forest sliding-window anomaly "
        "detection model, the bounded signed Z-score diagnostic attribution mechanism, and empirical benchmark evaluations on physical satellite "
        "bitstreams. The paper has been formatted in both standard IEEE 6-page and 4-page variants and is targeted for submission to premier IEEE "
        "telecommunications and broadcasting conferences (such as the IEEE International Symposium on Broadband Multimedia Systems and Broadcasting, "
        "BMSB, or IEEE Aerospace Conference)."
    )
    
    add_section_heading(doc, "8.3", "Standard Operating Procedures and Reproducibility Protocols")
    add_body_p(
        doc,
        "To ensure that PRJ_111 can be seamlessly integrated into active ground station operations, the project delivers standardized operational "
        "protocols and execution guidelines:"
    )
    add_bullet_p(
        doc,
        "Zero-Configuration Local Startup",
        "The software requires no external database configuration or internet access. Running `python run_frontend.py` immediately spins up the "
        "local REST service and binds the workstation dashboard to `http://127.0.0.1:8080`."
    )
    add_bullet_p(
        doc,
        "Deterministic Test Suite Verification",
        "Executing `python -m unittest discover -s tests` within the project virtual environment deterministically executes all 304 automated "
        "regression tests, validating mathematical invariants, boundary handling, and parser integrity in approximately 76 seconds."
    )
    add_bullet_p(
        doc,
        "Automated Multi-Format Export",
        "Operators can ingest an unknown satellite capture file and generate a complete tripartite diagnostic report (JSON, Markdown, Plain Text, "
        "or standalone HTML) with a single click or CLI command, ensuring uniform documentation across shifts in satellite operations centers."
    )
