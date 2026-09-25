"""
PRJ_111: Feature F6 — Stream Comparison Engine Experiment Runner.

Executes four fact-driven comparative experiments across real satellite receiver output data:
  1. Experiment 1: Same-Format Sub-Stream Comparison (MPEG-TS Halves)
     - Dynamic boundary partition of sample.ts into First Half vs Second Half
     - Compares multiplex stability, active PIDs, and adaptation field usage.
  2. Experiment 2: Same-Format Sub-Stream Comparison (DVB-S2 BBFrame Pre- vs Post-Transition)
     - Dynamic detection of modal DFL transition boundary in dvb-s2_bb_example.pcap
     - Compares pre-transition phase vs post-transition phase (DFL shift & payload deltas).
  3. Experiment 3: Controlled Synthetic Degradation Comparison (MPEG-TS Pristine vs Injected Errors)
     - Compares pristine sample.ts against slice with controlled TEI & CC injection (labeled SYNTHETIC)
     - Evaluates transmission integrity degradation detection without RF speculation.
  4. Experiment 4: Cross-Format Comparison (MPEG-TS vs DVB-S2 BBFrame)
     - Demonstrates strict semantic audit: evaluates total_payload_bytes and integrity_ratio;
     - Classifies container-dependent metrics (units, error rates, entropy) as NOT_COMPARABLE;
     - Enforces domain-safety guard blocking physical-layer inferences.

Outputs:
  - Structured JSON comparison reports in 05_CODE/reports/
  - Monospaced ASCII summary tables printed to console
"""

import copy
from pathlib import Path
import sys

BASE_DIR = Path(__file__).resolve().parent.parent
CODE_DIR = BASE_DIR / "05_CODE"
if str(CODE_DIR) not in sys.path:
    sys.path.insert(0, str(CODE_DIR))

from dvbs2_analyzer.analysis.comparison import (
    ComparisonConfig,
    StreamComparisonEngine,
    StreamComparisonReport,
)
from dvbs2_analyzer.analysis.timeline import (
    StreamTimeline,
    TimelineConfig,
    TimelineGenerator,
)
from dvbs2_analyzer.config import StreamFormat
from dvbs2_analyzer.ingestion.stream_handler import StreamHandler

RAW_DATA_DIR = BASE_DIR / "01_RAW_DATA"
REPORTS_DIR = BASE_DIR / "06_RESULTS" / "comparisons"


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
    tot_bytes = sum(p.payload_bytes for p in sliced_points) # or unit * size

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


def run_f6_experiments():
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    print("=" * 80)
    print(" PRJ_111: FEATURE F6 — STREAM COMPARISON ENGINE EXPERIMENTS")
    print(" Multi-Format Differential Analysis, Semantic Auditing & Domain Safety")
    print("=" * 80)

    engine = StreamComparisonEngine(ComparisonConfig())
    generator = TimelineGenerator(TimelineConfig(
        ts_window_size=200,
        gse_window_size=3,
        bbframe_window_size=50,
        f2_contamination=0.05,
    ))

    # Ingest raw files
    ts_file = RAW_DATA_DIR / "03_TS" / "DVBS2_toolkit" / "sample.ts"
    bb_file = RAW_DATA_DIR / "01_BBFRAME_GSE" / "dvb-s2_bb_example.pcap"

    handler_ts = StreamHandler(ts_file, forced_format=StreamFormat.MPEG_TS)
    handler_bb = StreamHandler(bb_file, forced_format=StreamFormat.BB_FRAME)

    print("\nGenerating base timelines from raw captures...")
    ts_timeline = generator.generate_from_handler(handler_ts, window_size=200)
    bb_timeline = generator.generate_from_handler(handler_bb, window_size=50)
    print(f"  [OK] MPEG-TS Timeline generated: {len(ts_timeline.points)} windows")
    print(f"  [OK] BBFrame Timeline generated: {len(bb_timeline.points)} windows")

    # =========================================================================
    # EXPERIMENT 1: MPEG-TS Same-Format Sub-Stream Comparison (First vs Second Half)
    # =========================================================================
    print("\n" + "=" * 80)
    print(" EXPERIMENT 1: MPEG-TS Sub-Stream Comparison (First Half vs Second Half)")
    print("=" * 80)
    n_ts = len(ts_timeline.points)
    mid_ts = n_ts // 2

    ts_half_1 = slice_timeline(ts_timeline, 0, mid_ts, f"MPEG-TS First Half (W0-W{mid_ts-1})")
    ts_half_2 = slice_timeline(ts_timeline, mid_ts, n_ts, f"MPEG-TS Second Half (W{mid_ts}-W{n_ts-1})")

    report_1 = engine.compare_timelines(ts_half_1, ts_half_2)
    print(report_1.render_ascii_summary())

    rep1_path = REPORTS_DIR / "comparison_ts_substreams.json"
    rep1_path.write_text(report_1.to_json(indent=2), encoding="utf-8")
    print(f"\n[OK] Saved Experiment 1 Report: {rep1_path.relative_to(BASE_DIR)}")

    # =========================================================================
    # EXPERIMENT 2: BBFrame Same-Format Pre- vs Post-Transition Comparison
    # =========================================================================
    print("\n" + "=" * 80)
    print(" EXPERIMENT 2: BBFrame Modal DFL Transition Differential Analysis")
    print("=" * 80)

    # Dynamically locate transition boundary in BBFrame timeline
    n_bb = len(bb_timeline.points)
    trans_boundary = None
    for i in range(1, n_bb):
        curr_dfl = bb_timeline.points[i].format_specific_metrics.get("modal_dfl")
        prev_dfl = bb_timeline.points[i - 1].format_specific_metrics.get("modal_dfl")
        if curr_dfl != prev_dfl or bb_timeline.points[i].has_transition:
            trans_boundary = i
            break

    if trans_boundary is None:
        trans_boundary = n_bb // 2
    print(f"Dynamically detected BBFrame modal transition boundary at Window {trans_boundary}.")

    bb_pre = slice_timeline(bb_timeline, 0, trans_boundary, f"BBFrame Pre-Transition (W0-W{trans_boundary-1})")
    bb_post = slice_timeline(bb_timeline, trans_boundary, n_bb, f"BBFrame Post-Transition (W{trans_boundary}-W{n_bb-1})")

    report_2 = engine.compare_timelines(bb_pre, bb_post)
    print(report_2.render_ascii_summary())

    rep2_path = REPORTS_DIR / "comparison_bbframe_substreams.json"
    rep2_path.write_text(report_2.to_json(indent=2), encoding="utf-8")
    print(f"\n[OK] Saved Experiment 2 Report: {rep2_path.relative_to(BASE_DIR)}")

    # =========================================================================
    # EXPERIMENT 3: Controlled Synthetic Degradation Comparison (MPEG-TS)
    # =========================================================================
    print("\n" + "=" * 80)
    print(" EXPERIMENT 3: Controlled Synthetic Degradation Comparison (MPEG-TS)")
    print("=" * 80)

    # Synthesize degraded version of first 30 windows
    ts_pristine = slice_timeline(ts_timeline, 0, min(30, n_ts), "MPEG-TS Pristine Baseline")
    ts_degraded = slice_timeline(ts_timeline, 0, min(30, n_ts), "MPEG-TS Synthetic Degradation (TEI & CC Injected - SYNTHETIC)")

    # Inject controlled synthetic anomalies into windows 10-20
    for idx in range(10, min(20, len(ts_degraded.points))):
        pt = ts_degraded.points[idx]
        pt.health_score = 65.0
        pt.health_status = "WARNING"
        pt.error_count = 12
        pt.error_rate = 0.06
        pt.invalid_units = 12
        pt.valid_units = max(0, pt.unit_count - 12)
        pt.is_anomaly = True
        pt.anomaly_score = 0.82
        pt.anomaly_severity = "HIGH"
        pt.anomaly_explanation = "Synthetically injected TEI and continuity counter discontinuities."
        pt.format_specific_metrics["tei_error_rate"] = 0.045
        pt.format_specific_metrics["continuity_error_rate"] = 0.035

    # Update summary stats of degraded slice
    ts_degraded.summary_stats["mean_health_score"] = round(sum(p.health_score for p in ts_degraded.points) / len(ts_degraded.points), 2)
    ts_degraded.summary_stats["peak_anomaly_score"] = max(p.anomaly_score for p in ts_degraded.points)
    ts_degraded.summary_stats["anomaly_window_count"] = sum(1 for p in ts_degraded.points if p.is_anomaly)

    report_3 = engine.compare_timelines(ts_pristine, ts_degraded)
    print(report_3.render_ascii_summary())

    rep3_path = REPORTS_DIR / "comparison_ts_synthetic_degradation.json"
    rep3_path.write_text(report_3.to_json(indent=2), encoding="utf-8")
    print(f"\n[OK] Saved Experiment 3 Report: {rep3_path.relative_to(BASE_DIR)}")

    # =========================================================================
    # EXPERIMENT 4: Cross-Format Comparison (MPEG-TS vs DVB-S2 BBFrame)
    # =========================================================================
    print("\n" + "=" * 80)
    print(" EXPERIMENT 4: Cross-Format Comparison (MPEG-TS vs DVB-S2 BBFrame)")
    print("=" * 80)

    report_4 = engine.compare_timelines(
        ts_timeline,
        bb_timeline,
        name_a="MPEG-TS Real Capture (sample.ts)",
        name_b="DVB-S2 BBFrame Real Capture (dvb-s2_bb_example.pcap)"
    )
    print(report_4.render_ascii_summary())

    rep4_path = REPORTS_DIR / "comparison_cross_format_ts_bbframe.json"
    rep4_path.write_text(report_4.to_json(indent=2), encoding="utf-8")
    print(f"\n[OK] Saved Experiment 4 Report: {rep4_path.relative_to(BASE_DIR)}")

    print("\n" + "=" * 80)
    print(" ALL 4 FEATURE F6 COMPARISON EXPERIMENTS COMPLETED SUCCESSFULLY")
    print("=" * 80)


if __name__ == "__main__":
    run_f6_experiments()
