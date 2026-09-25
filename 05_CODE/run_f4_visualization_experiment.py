"""
PRJ_111: Feature F4 — Timeline & Activity Visualization Experiment Runner.

Executes sequential windowing, temporal activity tracking, and multi-feature
synthesis (F1 Health, F2 Anomaly Detection, F3 Pattern Findings) across all
three alternative satellite receiver formats:
1. MPEG Transport Stream: 01_RAW_DATA/03_TS/DVBS2_toolkit/sample.ts
2. Generic Stream Encapsulation: 01_RAW_DATA/02_GSE/GSExtract/sample.ts
3. DVB-S2 Baseband Frames: 01_RAW_DATA/01_BBFRAME_GSE/dvb-s2_bb_example.pcap

Outputs:
- Console ASCII telemetry summaries and event logs
- Interactive HTML dashboards saved to 05_CODE/reports/
- Structured JSON timelines saved to 05_CODE/reports/
"""

from pathlib import Path
import sys

# Ensure local dvbs2_analyzer package is on path
BASE_DIR = Path(__file__).resolve().parent.parent
CODE_DIR = BASE_DIR / "05_CODE"
if str(CODE_DIR) not in sys.path:
    sys.path.insert(0, str(CODE_DIR))

from dvbs2_analyzer.analysis.timeline import TimelineConfig, TimelineGenerator
from dvbs2_analyzer.config import StreamFormat
from dvbs2_analyzer.ingestion.stream_handler import StreamHandler

RAW_DATA_DIR = BASE_DIR / "01_RAW_DATA"
REPORTS_DIR = BASE_DIR / "06_RESULTS" / "timelines"


def run_f4_visualization_experiments():
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    print("=" * 78)
    print(" PRJ_111: FEATURE F4 — TIMELINE & ACTIVITY VISUALIZATION EXPERIMENT")
    print(" Multi-Format Temporal Analysis & Interactive Dashboard Generation")
    print("=" * 78)

    generator = TimelineGenerator(TimelineConfig(
        ts_window_size=200,
        gse_window_size=3,
        bbframe_window_size=50,
        f2_contamination=0.05,
    ))

    # =========================================================================
    # 1. MPEG-TS Stream Timeline & Dashboard
    # =========================================================================
    ts_file = RAW_DATA_DIR / "03_TS" / "DVBS2_toolkit" / "sample.ts"
    print(f"\n[1/3] Generating MPEG-TS Timeline: {ts_file.name}")
    handler_ts = StreamHandler(ts_file, forced_format=StreamFormat.MPEG_TS)
    ts_timeline = generator.generate_from_handler(handler_ts, window_size=200)

    print(ts_timeline.render_ascii_summary())

    ts_html_path = REPORTS_DIR / "timeline_mpeg_ts.html"
    ts_json_path = REPORTS_DIR / "timeline_mpeg_ts.json"
    ts_timeline.render_html_dashboard(output_path=ts_html_path)
    ts_json_path.write_text(ts_timeline.to_json(indent=2), encoding="utf-8")
    print(f"      [OK] Saved HTML Dashboard : {ts_html_path.relative_to(BASE_DIR)}")
    print(f"      [OK] Saved JSON Telemetry : {ts_json_path.relative_to(BASE_DIR)}")

    # =========================================================================
    # 2. GSE Stream Timeline & Dashboard
    # =========================================================================
    gse_file = RAW_DATA_DIR / "02_GSE" / "GSExtract" / "sample.ts"
    print(f"\n[2/3] Generating GSE Timeline: {gse_file.name}")
    handler_gse = StreamHandler(gse_file, forced_format=StreamFormat.GSE)
    gse_timeline = generator.generate_from_handler(handler_gse, window_size=3)

    print(gse_timeline.render_ascii_summary())

    gse_html_path = REPORTS_DIR / "timeline_gse.html"
    gse_json_path = REPORTS_DIR / "timeline_gse.json"
    gse_timeline.render_html_dashboard(output_path=gse_html_path)
    gse_json_path.write_text(gse_timeline.to_json(indent=2), encoding="utf-8")
    print(f"      [OK] Saved HTML Dashboard : {gse_html_path.relative_to(BASE_DIR)}")
    print(f"      [OK] Saved JSON Telemetry : {gse_json_path.relative_to(BASE_DIR)}")

    # =========================================================================
    # 3. DVB-S2 Baseband Frame (BBFrame) Timeline & Dashboard
    # =========================================================================
    bb_file = RAW_DATA_DIR / "01_BBFRAME_GSE" / "dvb-s2_bb_example.pcap"
    print(f"\n[3/3] Generating DVB-S2 BBFrame Timeline: {bb_file.name}")
    handler_bb = StreamHandler(bb_file, forced_format=StreamFormat.BB_FRAME)
    bb_timeline = generator.generate_from_handler(handler_bb, window_size=50)

    print(bb_timeline.render_ascii_summary())

    bb_html_path = REPORTS_DIR / "timeline_bbframe.html"
    bb_json_path = REPORTS_DIR / "timeline_bbframe.json"
    bb_timeline.render_html_dashboard(output_path=bb_html_path)
    bb_json_path.write_text(bb_timeline.to_json(indent=2), encoding="utf-8")
    print(f"      [OK] Saved HTML Dashboard : {bb_html_path.relative_to(BASE_DIR)}")
    print(f"      [OK] Saved JSON Telemetry : {bb_json_path.relative_to(BASE_DIR)}")

    # =========================================================================
    # Summary of Generation
    # =========================================================================
    print("\n" + "=" * 78)
    print(" PRJ_111 FEATURE F4 EXPERIMENT SUMMARY")
    print("=" * 78)
    print(f"  MPEG-TS : {ts_timeline.total_windows} windows, {len(ts_timeline.events)} events, {ts_html_path.stat().st_size:,} bytes HTML")
    print(f"  GSE     : {gse_timeline.total_windows} windows, {len(gse_timeline.events)} events, {gse_html_path.stat().st_size:,} bytes HTML")
    print(f"  BBFrame : {bb_timeline.total_windows} windows, {len(bb_timeline.events)} events, {bb_html_path.stat().st_size:,} bytes HTML")
    print(f"  Reports directory: {REPORTS_DIR}")
    print("=" * 78)


if __name__ == "__main__":
    run_f4_visualization_experiments()
