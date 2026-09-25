"""
PRJ_111: Feature F5 — Anomaly Explanation Engine Experiment Runner.

Executes structured, domain-safe diagnostic explanation generation across all
three real satellite receiver formats:
1. MPEG Transport Stream: 01_RAW_DATA/03_TS/DVBS2_toolkit/sample.ts
2. Generic Stream Encapsulation: 01_RAW_DATA/02_GSE/GSExtract/sample.ts
3. DVB-S2 Baseband Frames: 01_RAW_DATA/01_BBFRAME_GSE/dvb-s2_bb_example.pcap

Outputs:
- Monospace ASCII diagnostic reports with the 9-point explanatory model
- Structured JSON explanation reports saved to 05_CODE/reports/
- Regenerated interactive HTML dashboards enriched with F5 diagnostics
"""

from pathlib import Path
import sys

BASE_DIR = Path(__file__).resolve().parent.parent
CODE_DIR = BASE_DIR / "05_CODE"
if str(CODE_DIR) not in sys.path:
    sys.path.insert(0, str(CODE_DIR))

from dvbs2_analyzer.analysis.explanation import (
    AnomalyExplanationEngine,
    ExplanationConfig,
    ExplanationReport,
)
from dvbs2_analyzer.analysis.timeline import TimelineConfig, TimelineGenerator
from dvbs2_analyzer.config import StreamFormat
from dvbs2_analyzer.ingestion.stream_handler import StreamHandler

RAW_DATA_DIR = BASE_DIR / "01_RAW_DATA"
REPORTS_DIR = BASE_DIR / "06_RESULTS" / "explanations"
TIMELINES_DIR = BASE_DIR / "06_RESULTS" / "timelines"


def run_f5_experiments():
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    print("=" * 78)
    print(" PRJ_111: FEATURE F5 — ANOMALY EXPLANATION ENGINE EXPERIMENT")
    print(" Structured Domain-Safe Explanations for Detected Telemetry Anomalies")
    print("=" * 78)

    engine = AnomalyExplanationEngine(ExplanationConfig())
    generator = TimelineGenerator(TimelineConfig(
        ts_window_size=200,
        gse_window_size=3,
        bbframe_window_size=50,
        f2_contamination=0.05,
    ))

    # =========================================================================
    # 1. MPEG-TS Real Capture Explanation
    # =========================================================================
    ts_file = RAW_DATA_DIR / "03_TS" / "DVBS2_toolkit" / "sample.ts"
    print(f"\n[1/3] Generating MPEG-TS Anomaly Explanations: {ts_file.name}")
    handler_ts = StreamHandler(ts_file, forced_format=StreamFormat.MPEG_TS)
    ts_timeline = generator.generate_from_handler(handler_ts, window_size=200)

    report_ts = engine.explain_timeline(ts_timeline)
    print(report_ts.render_ascii_summary())

    ts_json_path = REPORTS_DIR / "explanations_mpeg_ts.json"
    ts_json_path.write_text(report_ts.to_json(indent=2), encoding="utf-8")
    ts_html_path = TIMELINES_DIR / "timeline_mpeg_ts.html"
    ts_timeline.render_html_dashboard(output_path=ts_html_path)
    print(f"      [OK] Saved JSON Explanations: {ts_json_path.relative_to(BASE_DIR)}")
    print(f"      [OK] Updated HTML Dashboard : {ts_html_path.relative_to(BASE_DIR)}")

    # =========================================================================
    # 2. GSE Real Capture Explanation
    # =========================================================================
    gse_file = RAW_DATA_DIR / "02_GSE" / "GSExtract" / "sample.ts"
    print(f"\n[2/3] Generating GSE Anomaly Explanations: {gse_file.name}")
    handler_gse = StreamHandler(gse_file, forced_format=StreamFormat.GSE)
    gse_timeline = generator.generate_from_handler(handler_gse, window_size=3)

    report_gse = engine.explain_timeline(gse_timeline)
    print(report_gse.render_ascii_summary())

    gse_json_path = REPORTS_DIR / "explanations_gse.json"
    gse_json_path.write_text(report_gse.to_json(indent=2), encoding="utf-8")
    gse_html_path = TIMELINES_DIR / "timeline_gse.html"
    gse_timeline.render_html_dashboard(output_path=gse_html_path)
    print(f"      [OK] Saved JSON Explanations: {gse_json_path.relative_to(BASE_DIR)}")
    print(f"      [OK] Updated HTML Dashboard : {gse_html_path.relative_to(BASE_DIR)}")

    # =========================================================================
    # 3. DVB-S2 BBFrame Real Capture Explanation
    # =========================================================================
    bb_file = RAW_DATA_DIR / "01_BBFRAME_GSE" / "dvb-s2_bb_example.pcap"
    print(f"\n[3/3] Generating DVB-S2 BBFrame Anomaly Explanations: {bb_file.name}")
    handler_bb = StreamHandler(bb_file, forced_format=StreamFormat.BB_FRAME)
    bb_timeline = generator.generate_from_handler(handler_bb, window_size=50)

    report_bb = engine.explain_timeline(bb_timeline)
    print(report_bb.render_ascii_summary())

    bb_json_path = REPORTS_DIR / "explanations_bbframe.json"
    bb_json_path.write_text(report_bb.to_json(indent=2), encoding="utf-8")
    bb_html_path = TIMELINES_DIR / "timeline_bbframe.html"
    bb_timeline.render_html_dashboard(output_path=bb_html_path)
    print(f"      [OK] Saved JSON Explanations: {bb_json_path.relative_to(BASE_DIR)}")
    print(f"      [OK] Updated HTML Dashboard : {bb_html_path.relative_to(BASE_DIR)}")

    # =========================================================================
    # Overall Summary
    # =========================================================================
    print("\n" + "=" * 78)
    print(" PRJ_111 FEATURE F5 EXPERIMENT SUMMARY")
    print("=" * 78)
    print(f"  MPEG-TS : {report_ts.anomaly_count} explanations generated across {report_ts.total_windows} windows")
    print(f"  GSE     : {report_gse.anomaly_count} explanations generated across {report_gse.total_windows} windows")
    print(f"  BBFrame : {report_bb.anomaly_count} explanations generated across {report_bb.total_windows} windows")
    print(f"  Reports directory: {REPORTS_DIR}")
    print("=" * 78)


if __name__ == "__main__":
    run_f5_experiments()
