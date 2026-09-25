"""
PRJ_111: Feature F7 — Automatic Analysis Report Experiment Runner.

Executes five real-data validation experiments across real satellite receiver output captures:
  1. Experiment 1: MPEG-TS Comprehensive Automatic Analysis Report (sample.ts)
  2. Experiment 2: DVB-S2 Baseband Frame Comprehensive Automatic Analysis Report (dvb-s2_bb_example.pcap)
  3. Experiment 3: Generic Stream Encapsulation (GSE) Automatic Analysis Report (sample.ts)
  4. Experiment 4: Dual-Stream Comparative Automatic Analysis Report (MPEG-TS Halves)
  5. Experiment 5: Dual-Stream Comparative Automatic Analysis Report (Cross-Format TS vs BBFrame)

Outputs:
  - Structured JSON, Markdown, ASCII Text, and Standalone HTML reports saved in 05_CODE/reports/
"""

import copy
from pathlib import Path
import sys

BASE_DIR = Path(__file__).resolve().parent.parent
CODE_DIR = BASE_DIR / "05_CODE"
if str(CODE_DIR) not in sys.path:
    sys.path.insert(0, str(CODE_DIR))

from dvbs2_analyzer.analysis.comparison import ComparisonConfig, StreamComparisonEngine
from dvbs2_analyzer.analysis.explanation import AnomalyExplanationEngine, ExplanationConfig
from dvbs2_analyzer.analysis.report import AutomaticReportGenerator, ReportConfig
from dvbs2_analyzer.analysis.timeline import StreamTimeline, TimelineConfig, TimelineGenerator
from dvbs2_analyzer.config import StreamFormat
from dvbs2_analyzer.ingestion.stream_handler import StreamHandler

RAW_DATA_DIR = BASE_DIR / "01_RAW_DATA"
REPORTS_DIR = BASE_DIR / "06_RESULTS" / "reports"


def slice_timeline(
    original: StreamTimeline,
    start_win: int,
    end_win: int,
    sub_name: str
) -> StreamTimeline:
    """Helper to cleanly slice a timeline into a contiguous sub-stream."""
    sliced_points = copy.deepcopy(original.points[start_win:end_win])
    for new_idx, pt in enumerate(sliced_points):
        pt.window_index = new_idx

    tot_units = sum(p.unit_count for p in sliced_points)
    tot_bytes = sum(p.payload_bytes for p in sliced_points)

    mean_h = sum(p.health_score for p in sliced_points) / max(1, len(sliced_points))
    peak_a = max((p.anomaly_score for p in sliced_points), default=0.0)
    anom_cnt = sum(1 for p in sliced_points if p.is_anomaly)

    return StreamTimeline(
        stream_name=sub_name,
        format=original.format,
        total_units=tot_units,
        total_bytes=tot_bytes,
        window_size=original.window_size,
        total_windows=len(sliced_points),
        anomaly_threshold=original.anomaly_threshold,
        points=sliced_points,
        events=[e for e in original.events if start_win <= e.window_index < end_win],
        summary_stats={
            "mean_health_score": round(mean_h, 2),
            "peak_anomaly_score": round(peak_a, 4),
            "anomaly_window_count": anom_cnt,
        },
    )


def run_f7_experiments():
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    print("=" * 80)
    print(" PRJ_111: FEATURE F7 -- AUTOMATIC ANALYSIS REPORT EXPERIMENTS")
    print(" Synthesis of Authoritative F1-F6 Telemetry, Tripartite Register & Guards")
    print("=" * 80)

    report_gen = AutomaticReportGenerator(ReportConfig())
    expl_engine = AnomalyExplanationEngine(ExplanationConfig())
    comp_engine = StreamComparisonEngine(ComparisonConfig())
    tl_gen = TimelineGenerator(TimelineConfig(
        ts_window_size=200,
        gse_window_size=3,
        bbframe_window_size=50,
        f2_contamination=0.05,
    ))

    # Raw dataset paths
    ts_file = RAW_DATA_DIR / "03_TS" / "DVBS2_toolkit" / "sample.ts"
    bb_file = RAW_DATA_DIR / "01_BBFRAME_GSE" / "dvb-s2_bb_example.pcap"
    gse_file = RAW_DATA_DIR / "02_GSE" / "GSExtract" / "sample.ts"

    # =========================================================================
    # EXPERIMENT 1: MPEG-TS Comprehensive Report (Single-Stream)
    # =========================================================================
    print("\n" + "=" * 80)
    print(" EXPERIMENT 1: MPEG-TS Comprehensive Report (sample.ts)")
    print("=" * 80)
    handler_ts = StreamHandler(ts_file, forced_format=StreamFormat.MPEG_TS)
    ts_timeline = tl_gen.generate_from_handler(handler_ts, window_size=200)
    ts_expl = expl_engine.explain_timeline(ts_timeline)

    report_1 = report_gen.generate_from_timeline(
        timeline=ts_timeline,
        explanation_report=ts_expl,
        stream_path=ts_file,
        file_size_bytes=handler_ts.size_bytes,
    )
    print(report_1.render_text())
    paths_1 = report_1.save_all_formats(REPORTS_DIR, "report_mpeg_ts")
    print(f"\n[OK] Experiment 1 saved in 4 formats under {REPORTS_DIR.relative_to(BASE_DIR)}:")
    for ext, p in paths_1.items():
        print(f"     - {ext.upper()}: {p.name}")

    # =========================================================================
    # EXPERIMENT 2: DVB-S2 Baseband Frame Comprehensive Report (Single-Stream)
    # =========================================================================
    print("\n" + "=" * 80)
    print(" EXPERIMENT 2: DVB-S2 Baseband Frame Comprehensive Report (dvb-s2_bb_example.pcap)")
    print("=" * 80)
    handler_bb = StreamHandler(bb_file, forced_format=StreamFormat.BB_FRAME)
    bb_timeline = tl_gen.generate_from_handler(handler_bb, window_size=50)
    bb_expl = expl_engine.explain_timeline(bb_timeline)

    report_2 = report_gen.generate_from_timeline(
        timeline=bb_timeline,
        explanation_report=bb_expl,
        stream_path=bb_file,
        file_size_bytes=handler_bb.size_bytes,
    )
    print(report_2.render_text())
    paths_2 = report_2.save_all_formats(REPORTS_DIR, "report_bbframe")
    print(f"\n[OK] Experiment 2 saved in 4 formats under {REPORTS_DIR.relative_to(BASE_DIR)}:")
    for ext, p in paths_2.items():
        print(f"     - {ext.upper()}: {p.name}")

    # =========================================================================
    # EXPERIMENT 3: Generic Stream Encapsulation (GSE) Report (Single-Stream)
    # =========================================================================
    print("\n" + "=" * 80)
    print(" EXPERIMENT 3: Generic Stream Encapsulation (GSE) Report (sample.ts)")
    print("=" * 80)
    handler_gse = StreamHandler(gse_file, forced_format=StreamFormat.GSE)
    gse_timeline = tl_gen.generate_from_handler(handler_gse, window_size=3)
    gse_expl = expl_engine.explain_timeline(gse_timeline)

    report_3 = report_gen.generate_from_timeline(
        timeline=gse_timeline,
        explanation_report=gse_expl,
        stream_path=gse_file,
        file_size_bytes=handler_gse.size_bytes,
    )
    print(report_3.render_text())
    paths_3 = report_3.save_all_formats(REPORTS_DIR, "report_gse")
    print(f"\n[OK] Experiment 3 saved in 4 formats under {REPORTS_DIR.relative_to(BASE_DIR)}:")
    for ext, p in paths_3.items():
        print(f"     - {ext.upper()}: {p.name}")

    # =========================================================================
    # EXPERIMENT 4: Dual-Stream Comparative Report (MPEG-TS Halves)
    # =========================================================================
    print("\n" + "=" * 80)
    print(" EXPERIMENT 4: Dual-Stream Comparative Report (MPEG-TS Halves)")
    print("=" * 80)
    n_ts = len(ts_timeline.points)
    mid_ts = n_ts // 2
    ts_half_1 = slice_timeline(ts_timeline, 0, mid_ts, f"MPEG-TS First Half (W0-W{mid_ts-1})")
    ts_half_2 = slice_timeline(ts_timeline, mid_ts, n_ts, f"MPEG-TS Second Half (W{mid_ts}-W{n_ts-1})")

    comp_rep_halves = comp_engine.compare_timelines(ts_half_1, ts_half_2)
    report_4 = report_gen.generate_from_timeline(
        timeline=ts_half_1,
        explanation_report=ts_expl,
        comparison_report=comp_rep_halves,
        stream_path=ts_file,
        file_size_bytes=handler_ts.size_bytes,
    )
    print(report_4.render_text())
    paths_4 = report_4.save_all_formats(REPORTS_DIR, "report_comparison_ts_halves")
    print(f"\n[OK] Experiment 4 saved in 4 formats under {REPORTS_DIR.relative_to(BASE_DIR)}:")
    for ext, p in paths_4.items():
        print(f"     - {ext.upper()}: {p.name}")

    # =========================================================================
    # EXPERIMENT 5: Dual-Stream Comparative Report (Cross-Format TS vs BBFrame)
    # =========================================================================
    print("\n" + "=" * 80)
    print(" EXPERIMENT 5: Dual-Stream Comparative Report (Cross-Format TS vs BBFrame)")
    print("=" * 80)
    comp_rep_cross = comp_engine.compare_timelines(
        ts_timeline,
        bb_timeline,
        name_a="MPEG-TS Real Capture (sample.ts)",
        name_b="DVB-S2 BBFrame Real Capture (dvb-s2_bb_example.pcap)"
    )
    report_5 = report_gen.generate_from_timeline(
        timeline=ts_timeline,
        explanation_report=ts_expl,
        comparison_report=comp_rep_cross,
        stream_path=ts_file,
        file_size_bytes=handler_ts.size_bytes,
    )
    print(report_5.render_text())
    paths_5 = report_5.save_all_formats(REPORTS_DIR, "report_comparison_cross_format")
    print(f"\n[OK] Experiment 5 saved in 4 formats under {REPORTS_DIR.relative_to(BASE_DIR)}:")
    for ext, p in paths_5.items():
        print(f"     - {ext.upper()}: {p.name}")

    print("\n" + "=" * 80)
    print(" ALL 5 FEATURE F7 AUTOMATIC REPORT EXPERIMENTS COMPLETED SUCCESSFULLY")
    print("=" * 80)


if __name__ == "__main__":
    run_f7_experiments()
