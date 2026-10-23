from report_content.builder_utils import (
    add_chapter_title, add_section_heading, add_subsection_heading,
    add_body_p, add_bullet_p, add_callout, add_custom_table, add_custom_figure
)

def build_ch7(doc):
    add_chapter_title(doc, "CHAPTER 7", "TIMELINE FOR EXECUTION OF PROJECT (GANTT CHART)")
    
    add_section_heading(doc, "7.1", "Five-Phase Project Milestone Execution Lifecycle")
    add_body_p(
        doc,
        "The development and empirical validation of PRJ_111 was executed across an intensive 16-week engineering schedule organized into five "
        "interconnected development phases. Each phase was defined by strict engineering deliverables, regression milestones, and departmental reviews:"
    )
    add_bullet_p(
        doc,
        "Phase I: Architectural Inception & Requirements Engineering (Weeks 1–3)",
        "Literature review of DVB-S2 (ETSI EN 302 307) and ETSI TR 101 290; formalization of the problem statement and research gaps; acquisition "
        "of raw satellite bitstream datasets; definition of the multi-format container abstraction model; Review-0 project defense."
    )
    add_bullet_p(
        doc,
        "Phase II: Foundation Parsing & Core Analysis Subsystems (Weeks 4–7)",
        "Implementation of low-level binary parsers for MPEG-TS, GSE, and BBFrames; integration of table-driven CRC-8 lookup; development of the "
        "unified feature extractor; initial unit test suite (74 tests); Review-1 milestone defense."
    )
    add_bullet_p(
        doc,
        "Phase III: Advanced Analytics, ML & Workstation Implementation (Weeks 8–11)",
        "Implementation of F1 Health Scoring, F2 Isolation Forest anomaly detection, F3 Pattern Detection, F4 Spatial-Offset Timeline, F5 Diagnostic "
        "Explanation Engine, F6 Comparison Engine with Semantic Barrier, and F7 Multi-Format Reporting; frontend SPA workstation development; "
        "test suite expansion to 240 passing tests; Review-2 comprehensive milestone defense."
    )
    add_bullet_p(
        doc,
        "Phase IV: Streaming Optimization, Fault Injection & Robustness Hardening (Weeks 12–14)",
        "Re-engineering ingestion around 64 KB chunked streaming buffers; empirical verification of whole-file analytical equivalence; implementation "
        "of the controlled fault-injection benchmark utility; test suite expansion to 304 passing tests (~80% completion milestone)."
    )
    add_bullet_p(
        doc,
        "Phase V: Final Verification, Packaging & Academic Documentation (Weeks 15–16)",
        "End-to-end live HTTP integration testing; cryptographic checksum verification of raw datasets; drafting of academic research paper; "
        "compilation of the comprehensive final university project documentation; Review-3 / Final Viva-Voce defense."
    )
    
    add_section_heading(doc, "7.2", "Detailed Milestone Breakdown (Reviews 0 to 3 / Final)")
    add_body_p(
        doc,
        "Progress across the engineering lifecycle was tracked through formal university evaluation milestones, ensuring continuous alignment with "
        "academic and technical standards:"
    )
    add_bullet_p(
        doc,
        "Review 0 (August 2026): Topic Approval & Conceptual Design",
        "Presented foundational domain analysis, established the necessity of post-demodulator stream analysis, approved project scope and guide allocation."
    )
    add_bullet_p(
        doc,
        "Review 1 (Late August 2026): Architecture & Initial Parser Validation",
        "Demonstrated working prototypes of TSParser and BBFrameParser; verified 188-byte packet synchronization; established dataset storage strategy."
    )
    add_bullet_p(
        doc,
        "Review 2 (Late September 2026): Comprehensive Functional Workstation",
        "Demonstrated all seven core features (F1 through F7); verified unsupervised Isolation Forest anomaly detection; showcased dark-themed SPA "
        "dashboard; presented 240 automated unit and integration tests with 100% pass rate."
    )
    add_bullet_p(
        doc,
        "Review 3 / Final Defense (November 2026): Complete Project Delivery & Viva-Voce",
        "Demonstrated chunked streaming scalability (64 KB buffers); presented controlled fault injection sensitivity benchmarks; validated 304 automated "
        "tests with 100% pass rate; submitted final university documentation and IEEE-format academic research paper."
    )
    
    add_section_heading(doc, "7.3", "Milestone Deliverables and Timeline Schedule")
    add_body_p(
        doc,
        "Table 7.1 details the milestone timeline, assigned weeks, engineering components completed, and formal verification evidence. "
        "Figure 7.1 provides the high-definition project Gantt chart roadmap depicting parallel and sequential work streams across the 16-week execution."
    )
    
    table_7_1_headers = ["Milestone", "Timeline", "Target Deliverables & Engineering Modules", "Verification State", "Passing Tests"]
    table_7_1_data = [
        ["Review 0", "Weeks 1–3 (Aug 2026)", "Project synopsis, literature survey, DVB-S2 standard review, raw dataset acquisition", "Approved", "0 Tests (Design)"],
        ["Review 1", "Weeks 4–7 (Late Aug 2026)", "Low-level TS/BBFrame parsers, table CRC-8, unified feature extractor, initial CLI", "Verified", "74 Tests Passing"],
        ["Review 2", "Weeks 8–11 (Sep 2026)", "Features F1–F7, Isolation Forest, Z-score explainer, Semantic Barrier, SPA Workstation", "Verified", "240 Tests Passing"],
        ["Chunk 1–3", "Weeks 12–13 (Oct 2026)", "64 KB chunked streaming engine, whole-file equivalence, fault injection framework", "Verified", "267 Tests Passing"],
        ["Chunk 4–5", "Week 14 (Mid Oct 2026)", "Robustness hardening, malformed file guards, timeline investigation, UI demo showcase", "Verified", "301 Tests Passing"],
        ["Review 3 (Final)", "Weeks 15–16 (Nov 2026)", "Final regression audit, 304 passing tests, academic research paper, final documentation", "Verified / Final", "304 Tests Passing"]
    ]
    add_custom_table(doc, "Table 7.1: Milestone Execution Schedule and Engineering Deliverables", table_7_1_headers, table_7_1_data, col_widths=[1.2, 1.4, 2.3, 1.0, 0.9])
    
    # Figure 7.1: Gantt Chart
    add_custom_figure(
        doc,
        "07_DOCUMENTATION/report_assets/fig_gantt_chart_hd.png",
        "Figure 7.1: Five-Phase Project Milestone Execution Roadmap (Gantt Schedule)",
        width_inches=6.2
    )
