"""
PRJ_111: Feature F3 — Stream Pattern Detection Experiment Runner.

Executes pattern detection on all three real satellite stream datasets:
1. MPEG Transport Stream: 01_RAW_DATA/03_TS/DVBS2_toolkit/sample.ts
2. Generic Stream Encapsulation: 01_RAW_DATA/02_GSE/GSExtract/sample.ts
3. DVB-S2 Baseband Frames: 01_RAW_DATA/01_BBFRAME_GSE/dvb-s2_bb_example.pcap

Generates structured pattern reports, activity breakdowns, and transition findings.
"""

from pathlib import Path
import sys

# Ensure local dvbs2_analyzer package is on path
BASE_DIR = Path(__file__).resolve().parent.parent
CODE_DIR = BASE_DIR / "05_CODE"
if str(CODE_DIR) not in sys.path:
    sys.path.insert(0, str(CODE_DIR))

from dvbs2_analyzer.analysis.patterns import (
    PatternConfig,
    PatternDetector,
    PatternType,
)
from dvbs2_analyzer.config import StreamFormat
from dvbs2_analyzer.ingestion.stream_handler import StreamHandler

RAW_DATA_DIR = BASE_DIR / "01_RAW_DATA"


def run_f3_experiments():
    print("=" * 76)
    print(" PRJ_111: FEATURE F3 — STREAM PATTERN DETECTION EXPERIMENTS")
    print(" Deterministic Multiplex, Protocol, & Transmission Pattern Profiling")
    print("=" * 76)

    detector = PatternDetector(PatternConfig(
        ts_window_size=500,
        gse_window_size=4,
        bbframe_window_size=200,
    ))

    # -------------------------------------------------------------------------
    # 1. MPEG-TS Real Stream Analysis
    # -------------------------------------------------------------------------
    ts_file = RAW_DATA_DIR / "03_TS" / "DVBS2_toolkit" / "sample.ts"
    print(f"\n[1/3] Analyzing MPEG-TS Stream: {ts_file.name}")
    handler_ts = StreamHandler(ts_file, forced_format=StreamFormat.MPEG_TS)
    parser_ts = handler_ts.get_parser()
    packets = list(parser_ts.parse_file(ts_file))

    report_ts = detector.analyze_ts_stream(packets, window_size=500, stream_name=ts_file.name)
    print(f"      Total Packets Parsed : {report_ts.total_units_analyzed:,}")
    print(f"      Telemetry Windows    : {report_ts.total_windows}")
    print("      Key Pattern Findings :")
    for f in report_ts.findings:
        if f.pattern_type != PatternType.PATTERN_TRANSITION.value:
            print(f"        * [{f.pattern_type}] {f.description}")

    # -------------------------------------------------------------------------
    # 2. GSE Real Stream Analysis
    # -------------------------------------------------------------------------
    gse_file = RAW_DATA_DIR / "02_GSE" / "GSExtract" / "sample.ts"
    print(f"\n[2/3] Analyzing GSE Stream: {gse_file.name}")
    handler_gse = StreamHandler(gse_file, forced_format=StreamFormat.GSE)
    parser_gse = handler_gse.get_parser()
    pdus = list(parser_gse.parse_file(gse_file))

    report_gse = detector.analyze_gse_stream(pdus, window_size=4, stream_name=gse_file.name)
    print(f"      Total PDUs Parsed    : {report_gse.total_units_analyzed}")
    print(f"      Telemetry Windows    : {report_gse.total_windows}")
    print("      Key Pattern Findings :")
    for f in report_gse.findings:
        print(f"        * [{f.pattern_type}] {f.description}")

    # -------------------------------------------------------------------------
    # 3. DVB-S2 Baseband Frame (BBFrame) Real Stream Analysis
    # -------------------------------------------------------------------------
    bb_file = RAW_DATA_DIR / "01_BBFRAME_GSE" / "dvb-s2_bb_example.pcap"
    print(f"\n[3/3] Analyzing DVB-S2 BBFrame Stream: {bb_file.name}")
    handler_bb = StreamHandler(bb_file, forced_format=StreamFormat.BB_FRAME)
    parser_bb = handler_bb.get_parser()
    frames = list(parser_bb.parse_file(bb_file))

    report_bb = detector.analyze_bbframe_stream(frames, window_size=200, stream_name=bb_file.name)
    print(f"      Total Frames Parsed  : {report_bb.total_units_analyzed:,}")
    print(f"      Telemetry Windows    : {report_bb.total_windows}")
    print("      Key Pattern Findings :")
    for f in report_bb.findings:
        if f.pattern_type != PatternType.PATTERN_TRANSITION.value:
            print(f"        * [{f.pattern_type}] {f.description}")

    transitions = [f for f in report_bb.findings if f.pattern_type == PatternType.PATTERN_TRANSITION.value]
    if transitions:
        print(f"      Window Transitions ({len(transitions)}) :")
        for t in transitions[:3]:
            print(f"        * Window {t.window_index}: {t.description}")

    print("\n" + "=" * 76)
    print(" F3 PATTERN DETECTION EXPERIMENTS COMPLETED SUCCESSFULLY")
    print("=" * 76)


if __name__ == "__main__":
    run_f3_experiments()
