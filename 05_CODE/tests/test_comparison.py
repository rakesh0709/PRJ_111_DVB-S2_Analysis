"""
Unit and Integration Tests for Feature F6: Stream Comparison Engine.
Tests all 27 planned cases covering semantic audit, zero-baseline mathematics,
significance hierarchy, same-format and cross-format comparisons, window alignment,
and domain-safety guards.
"""

from pathlib import Path
import unittest

from dvbs2_analyzer.analysis.comparison import (
    ALIGNMENT_DISCLAIMER,
    CROSS_FORMAT_ANOMALY_CAVEAT,
    CROSS_FORMAT_COMPARABLE_METRICS,
    CROSS_FORMAT_INCOMPATIBLE_METRICS,
    UNSUPPORTED_INFERENCES_GUARD,
    AnomalyComparison,
    CommonComparison,
    ComparisonConfig,
    ComparisonSummary,
    FormatComparison,
    MetricDifference,
    PatternComparison,
    StreamComparisonEngine,
    StreamComparisonReport,
    WindowAlignmentComparison,
    compute_metric_difference,
)
from dvbs2_analyzer.analysis.timeline import StreamTimeline, TimelinePoint
from dvbs2_analyzer.config import StreamFormat
from dvbs2_analyzer.features.extractor import (
    BBFrameSpecificMetrics,
    CommonMetrics,
    GSESpecificMetrics,
    TSSpecificMetrics,
    UnifiedStreamFeatureSet,
)


def create_mock_timeline(
    name: str = "Test Stream",
    fmt: StreamFormat = StreamFormat.MPEG_TS,
    num_windows: int = 10,
    window_size: int = 200,
    health_score: float = 100.0,
    anomaly_score: float = 0.15,
    is_anomaly: bool = False,
    anomaly_severity: str = "NORMAL",
    payload_kb: float = 35.0,
    dominant_pid: int = 0x0020,
    modal_dfl: int = 4000,
) -> StreamTimeline:
    """Helper to construct synthetic StreamTimeline objects for tests."""
    points = []
    for i in range(num_windows):
        fmt_metrics = {}
        if fmt == StreamFormat.MPEG_TS:
            fmt_metrics = {
                "pid_entropy": 2.5,
                "null_packet_ratio": 0.05,
                "tei_error_rate": 0.0,
                "continuity_error_rate": 0.0,
                "dominant_pid": dominant_pid,
                "dominant_pid_summary": f"PID 0x{dominant_pid:04X}",
            }
        elif fmt == StreamFormat.BB_FRAME:
            fmt_metrics = {
                "modal_dfl": modal_dfl,
                "crc_errors": 0,
            }
        elif fmt == StreamFormat.GSE:
            fmt_metrics = {
                "fragmentation_ratio": 0.10,
                "dominant_protocol": "IPv4",
            }

        pt = TimelinePoint(
            window_index=i,
            unit_offset_start=i * window_size,
            unit_offset_end=(i + 1) * window_size,
            byte_offset_start=i * window_size * 188,
            byte_offset_end=(i + 1) * window_size * 188,
            unit_count=window_size,
            valid_units=window_size,
            invalid_units=0,
            payload_bytes=int(payload_kb * 1024),
            payload_kb=payload_kb,
            unit_density=window_size,
            health_score=health_score,
            health_status="HEALTHY" if health_score >= 80 else "CRITICAL",
            error_count=0,
            error_rate=0.0,
            is_anomaly=is_anomaly,
            anomaly_score=anomaly_score,
            anomaly_severity=anomaly_severity,
            anomaly_explanation="Nominal operation",
            top_deviations=[],
            pattern_findings=[],
            has_transition=False,
            transition_description=None,
            format_specific_metrics=fmt_metrics,
            events=[],
        )
        points.append(pt)

    return StreamTimeline(
        stream_name=name,
        format=fmt,
        total_units=num_windows * window_size,
        total_bytes=num_windows * window_size * 188,
        window_size=window_size,
        total_windows=num_windows,
        anomaly_threshold=0.50,
        points=points,
        events=[],
        summary_stats={
            "mean_health_score": health_score,
            "peak_anomaly_score": anomaly_score,
            "anomaly_window_count": num_windows if is_anomaly else 0,
        },
    )


class TestStreamComparison(unittest.TestCase):
    """27 Automated Tests for Feature F6 Stream Comparison Engine."""

    def setUp(self):
        self.config = ComparisonConfig()
        self.engine = StreamComparisonEngine(self.config)

    # 1. Config Defaults
    def test_comparison_config_defaults(self):
        cfg = ComparisonConfig()
        self.assertEqual(cfg.equality_tolerance_pct, 0.5)
        self.assertEqual(cfg.significance_minor_pct, 2.0)
        self.assertEqual(cfg.significance_substantial_pct, 10.0)
        self.assertEqual(cfg.significance_critical_pct, 50.0)
        self.assertEqual(cfg.alignment_mode, "DIRECT_INDEX")
        self.assertEqual(cfg.decile_bins, 10)
        self.assertTrue(cfg.strict_domain_safety)

    # 2. Identical Stream Comparison
    def test_identical_stream_comparison(self):
        tl_a = create_mock_timeline("TS_Stream", StreamFormat.MPEG_TS, num_windows=5)
        tl_b = create_mock_timeline("TS_Stream", StreamFormat.MPEG_TS, num_windows=5)
        report = self.engine.compare(tl_a, tl_b)

        self.assertTrue(report.is_same_format)
        for m_name, diff in report.common.metrics.items():
            self.assertEqual(diff.direction, "EQUAL")
            self.assertEqual(diff.classification, "UNCHANGED")
            self.assertEqual(diff.significance, "NEGLIGIBLE")

    # 3. Signed & Relative Percent Deltas
    def test_metric_difference_signed_and_pct(self):
        # 100 -> 120 (+20%)
        d1 = compute_metric_difference("test_metric", 100.0, 120.0, config=self.config)
        self.assertEqual(d1.absolute_difference, 20.0)
        self.assertEqual(d1.relative_difference_pct, 20.0)
        self.assertEqual(d1.direction, "B_HIGHER")
        self.assertEqual(d1.classification, "INCREASED")
        self.assertEqual(d1.significance, "SUBSTANTIAL")

        # 100 -> 80 (-20%)
        d2 = compute_metric_difference("test_metric", 100.0, 80.0, config=self.config)
        self.assertEqual(d2.absolute_difference, -20.0)
        self.assertEqual(d2.relative_difference_pct, -20.0)
        self.assertEqual(d2.direction, "A_HIGHER")
        self.assertEqual(d2.classification, "DECREASED")
        self.assertEqual(d2.significance, "SUBSTANTIAL")

    # 4. Zero Baseline Handling
    def test_zero_baseline_handling(self):
        # A=0, B=0
        d_zero = compute_metric_difference("error_count", 0, 0, config=self.config)
        self.assertEqual(d_zero.direction, "EQUAL")
        self.assertEqual(d_zero.classification, "UNCHANGED")
        self.assertEqual(d_zero.relative_difference_pct, 0.0)
        self.assertEqual(d_zero.significance, "NEGLIGIBLE")

        # A=0, B>0 -> percentage is undefined (None)
        d_pos = compute_metric_difference("error_count", 0, 5, config=self.config, is_error_metric=True)
        self.assertEqual(d_pos.direction, "B_HIGHER")
        self.assertEqual(d_pos.classification, "INCREASED")
        self.assertIsNone(d_pos.relative_difference_pct)
        self.assertEqual(d_pos.significance, "CRITICAL")

        # A>0, B=0 -> dropped to zero (-100%)
        d_drop = compute_metric_difference("error_count", 10, 0, config=self.config, is_error_metric=True)
        self.assertEqual(d_drop.direction, "A_HIGHER")
        self.assertEqual(d_drop.classification, "DECREASED")
        self.assertEqual(d_drop.relative_difference_pct, -100.0)
        self.assertEqual(d_drop.significance, "CRITICAL")

    # 5. Significance Threshold Consistency
    def test_significance_threshold_consistency(self):
        # < 2%: NEGLIGIBLE (with tolerance 0.5%, delta 1.2% is NEGLIGIBLE)
        d_neg = compute_metric_difference("metric", 100.0, 101.2, config=self.config)
        self.assertEqual(d_neg.significance, "NEGLIGIBLE")

        # 2% <= delta < 10%: MINOR (delta 5.0%)
        d_min = compute_metric_difference("metric", 100.0, 105.0, config=self.config)
        self.assertEqual(d_min.significance, "MINOR")

        # 10% <= delta < 50%: SUBSTANTIAL (delta 25.0%)
        d_sub = compute_metric_difference("metric", 100.0, 125.0, config=self.config)
        self.assertEqual(d_sub.significance, "SUBSTANTIAL")

        # >= 50%: CRITICAL (delta 75.0%)
        d_crit = compute_metric_difference("metric", 100.0, 175.0, config=self.config)
        self.assertEqual(d_crit.significance, "CRITICAL")

    # 6. Difference Classification Direction
    def test_difference_classification_direction(self):
        d_inc = compute_metric_difference("units", 10, 15, config=self.config)
        self.assertEqual(d_inc.classification, "INCREASED")
        self.assertEqual(d_inc.direction, "B_HIGHER")

        d_dec = compute_metric_difference("units", 15, 10, config=self.config)
        self.assertEqual(d_dec.classification, "DECREASED")
        self.assertEqual(d_dec.direction, "A_HIGHER")

        d_unc = compute_metric_difference("units", 1000, 1002, config=self.config)
        self.assertEqual(d_unc.classification, "UNCHANGED")
        self.assertEqual(d_unc.direction, "EQUAL")

        d_str = compute_metric_difference("stream_type", "TS", "GSE", config=self.config)
        self.assertEqual(d_str.classification, "STRUCTURAL_DIFFERENCE")
        self.assertEqual(d_str.direction, "STRUCTURAL_CHANGE")

    # 7. Same-Format TS Comparison
    def test_same_format_ts_comparison(self):
        tl_a = create_mock_timeline("TS_A", StreamFormat.MPEG_TS, dominant_pid=0x0020)
        tl_b = create_mock_timeline("TS_B", StreamFormat.MPEG_TS, dominant_pid=0x0040)
        report = self.engine.compare(tl_a, tl_b)

        self.assertTrue(report.is_same_format)
        self.assertTrue(report.format_specific.is_comparable)
        self.assertEqual(report.format_specific.format_name, "MPEG_TS")
        self.assertFalse(report.patterns.component_match)

    # 8. Same-Format GSE Comparison
    def test_same_format_gse_comparison(self):
        tl_a = create_mock_timeline("GSE_A", StreamFormat.GSE)
        tl_b = create_mock_timeline("GSE_B", StreamFormat.GSE)
        report = self.engine.compare(tl_a, tl_b)

        self.assertTrue(report.is_same_format)
        self.assertTrue(report.format_specific.is_comparable)
        self.assertEqual(report.format_specific.format_name, "GSE")

    # 9. Same-Format BBFrame Comparison
    def test_same_format_bbframe_comparison(self):
        tl_a = create_mock_timeline("BB_A", StreamFormat.BB_FRAME, modal_dfl=4000)
        tl_b = create_mock_timeline("BB_B", StreamFormat.BB_FRAME, modal_dfl=5400)
        report = self.engine.compare(tl_a, tl_b)

        self.assertTrue(report.is_same_format)
        self.assertTrue(report.format_specific.is_comparable)
        self.assertIn("modal_dfl", report.format_specific.metrics)
        self.assertEqual(report.format_specific.metrics["modal_dfl"].classification, "INCREASED")

    # 10. Cross-Format Comparison Safety
    def test_cross_format_comparison_safety(self):
        tl_ts = create_mock_timeline("TS", StreamFormat.MPEG_TS)
        tl_bb = create_mock_timeline("BB", StreamFormat.BB_FRAME)
        report = self.engine.compare(tl_ts, tl_bb)

        self.assertFalse(report.is_same_format)
        self.assertFalse(report.format_specific.is_comparable)
        self.assertIsNotNone(report.format_specific.incompatibility_reason)

    # 11. Cross-Format Entropy Incomparability
    def test_cross_format_entropy_incomparability(self):
        tl_ts = create_mock_timeline("TS", StreamFormat.MPEG_TS)
        tl_bb = create_mock_timeline("BB", StreamFormat.BB_FRAME)
        report = self.engine.compare(tl_ts, tl_bb)

        entropy_diff = report.common.metrics["entropy"]
        self.assertEqual(entropy_diff.classification, "NOT_COMPARABLE")
        self.assertEqual(entropy_diff.direction, "NOT_COMPARABLE")
        self.assertEqual(entropy_diff.significance, "NOT_APPLICABLE")
        self.assertIn("Entropy measures format-specific distributions", entropy_diff.incompatibility_reason)

    # 12. Cross-Format Common Metrics Semantic Audit
    def test_cross_format_common_metrics_semantic_audit(self):
        tl_ts = create_mock_timeline("TS", StreamFormat.MPEG_TS)
        tl_bb = create_mock_timeline("BB", StreamFormat.BB_FRAME)
        report = self.engine.compare(tl_ts, tl_bb)

        for key in ["total_units", "valid_units", "invalid_units", "truncated_units",
                    "mean_payload_bytes", "payload_ratio", "error_count", "error_rate", "entropy"]:
            diff = report.common.metrics[key]
            self.assertEqual(diff.classification, "NOT_COMPARABLE", f"{key} should be NOT_COMPARABLE")
            self.assertIsNotNone(diff.incompatibility_reason, f"{key} must provide an incompatibility reason")

    # 13. Cross-Format Shared Metrics Comparability
    def test_cross_format_shared_metrics_comparability(self):
        tl_ts = create_mock_timeline("TS", StreamFormat.MPEG_TS)
        tl_bb = create_mock_timeline("BB", StreamFormat.BB_FRAME)
        report = self.engine.compare(tl_ts, tl_bb)

        pl_diff = report.common.metrics["total_payload_bytes"]
        self.assertNotEqual(pl_diff.classification, "NOT_COMPARABLE")
        self.assertIsNotNone(pl_diff.absolute_difference)

        integ_diff = report.common.metrics["integrity_ratio"]
        self.assertNotEqual(integ_diff.classification, "NOT_COMPARABLE")
        self.assertIsNotNone(integ_diff.absolute_difference)

    # 14. Cross-Format Anomaly Caveat
    def test_cross_format_anomaly_caveat(self):
        tl_ts = create_mock_timeline("TS", StreamFormat.MPEG_TS)
        tl_bb = create_mock_timeline("BB", StreamFormat.BB_FRAME)
        report = self.engine.compare(tl_ts, tl_bb)

        self.assertTrue(report.anomalies.is_cross_format)
        found_caveat = any("CROSS-FORMAT ANOMALY SCORE SPACE NOTE" in note for note in report.anomalies.comparison_notes)
        self.assertTrue(found_caveat)

    # 15. PID Terminology Safety
    def test_pid_terminology_safety(self):
        tl_a = create_mock_timeline("TS_A", StreamFormat.MPEG_TS)
        tl_b = create_mock_timeline("TS_B", StreamFormat.MPEG_TS)
        report = self.engine.compare(tl_a, tl_b)

        summary_text = " ".join(report.summary.key_differences + report.summary.safe_conclusions)
        self.assertNotIn("elementary stream", summary_text.lower())

    # 16. Standards Compliance Wording Safety
    def test_standards_compliance_wording_safety(self):
        tl_a = create_mock_timeline("TS_A", StreamFormat.MPEG_TS)
        tl_b = create_mock_timeline("TS_B", StreamFormat.MPEG_TS)
        report = self.engine.compare(tl_a, tl_b)

        ascii_rep = report.render_ascii_summary()
        self.assertNotIn("ETSI TR 101 290 compliant", ascii_rep)
        self.assertNotIn("certified", ascii_rep.lower())

    # 17. Different Stream Lengths
    def test_different_stream_lengths(self):
        tl_short = create_mock_timeline("Short", StreamFormat.MPEG_TS, num_windows=5)
        tl_long = create_mock_timeline("Long", StreamFormat.MPEG_TS, num_windows=15)
        report = self.engine.compare(tl_short, tl_long)

        self.assertEqual(report.windows.aligned_window_count, 5)
        self.assertEqual(report.windows.unaligned_windows_a, 0)
        self.assertEqual(report.windows.unaligned_windows_b, 10)
        self.assertEqual(len(report.windows.health_delta_series), 5)

    # 18. Truncated Final Window Handling
    def test_truncated_final_window_handling(self):
        tl = create_mock_timeline("TS", StreamFormat.MPEG_TS, num_windows=5, window_size=200)
        # Simulate partial final window
        tl.points[-1].unit_count = 50
        report = self.engine.compare(tl, tl)
        self.assertIsNotNone(report)

    # 19. Empty Stream Comparison
    def test_empty_stream_comparison(self):
        tl_empty_a = create_mock_timeline("EmptyA", StreamFormat.MPEG_TS, num_windows=0)
        tl_empty_b = create_mock_timeline("EmptyB", StreamFormat.MPEG_TS, num_windows=0)
        report = self.engine.compare(tl_empty_a, tl_empty_b)

        self.assertEqual(report.windows.aligned_window_count, 0)
        self.assertEqual(report.anomalies.stream_a_anomaly_count, 0)

    # 20. Missing Metrics Graceful Fallback
    def test_missing_metrics_graceful_fallback(self):
        diff = compute_metric_difference("unsupported_field", None, 100.0, config=self.config)
        self.assertEqual(diff.direction, "INSUFFICIENT_DATA")
        self.assertEqual(diff.classification, "INSUFFICIENT_DATA")
        self.assertEqual(diff.significance, "NOT_APPLICABLE")

    # 21. Anomaly Distribution Comparison
    def test_anomaly_distribution_comparison(self):
        tl_norm = create_mock_timeline("Norm", StreamFormat.MPEG_TS, num_windows=10, is_anomaly=False, anomaly_score=0.10)
        tl_anom = create_mock_timeline("Anom", StreamFormat.MPEG_TS, num_windows=10, is_anomaly=True, anomaly_score=0.85, anomaly_severity="HIGH")
        report = self.engine.compare(tl_norm, tl_anom)

        self.assertEqual(report.anomalies.stream_a_anomaly_count, 0)
        self.assertEqual(report.anomalies.stream_b_anomaly_count, 10)
        self.assertEqual(report.anomalies.stream_b_peak_score, 0.85)
        self.assertEqual(report.anomalies.rate_difference.classification, "INCREASED")

    # 22. Severity Distribution Comparison
    def test_severity_distribution_comparison(self):
        tl_norm = create_mock_timeline("Norm", StreamFormat.MPEG_TS, num_windows=10, anomaly_severity="NORMAL")
        tl_high = create_mock_timeline("High", StreamFormat.MPEG_TS, num_windows=10, is_anomaly=True, anomaly_severity="HIGH")
        report = self.engine.compare(tl_norm, tl_high)

        self.assertEqual(report.anomalies.severity_breakdown_a["NORMAL"], 10)
        self.assertEqual(report.anomalies.severity_breakdown_b["HIGH"], 10)

    # 23. Pattern Differences PID Distribution
    def test_pattern_differences_pid_distribution(self):
        tl_pid20 = create_mock_timeline("TS_20", StreamFormat.MPEG_TS, dominant_pid=0x0020)
        tl_pid40 = create_mock_timeline("TS_40", StreamFormat.MPEG_TS, dominant_pid=0x0040)
        report = self.engine.compare(tl_pid20, tl_pid40)

        self.assertFalse(report.patterns.component_match)
        self.assertIn("PID 0x0020", report.patterns.dominant_component_a)
        self.assertIn("PID 0x0040", report.patterns.dominant_component_b)

    # 24. Pattern Differences DFL Distribution
    def test_pattern_differences_dfl_distribution(self):
        tl_dfl1 = create_mock_timeline("BB_1", StreamFormat.BB_FRAME, modal_dfl=3800)
        tl_dfl2 = create_mock_timeline("BB_2", StreamFormat.BB_FRAME, modal_dfl=5200)
        report = self.engine.compare(tl_dfl1, tl_dfl2)

        self.assertIn("modal_dfl", report.format_specific.metrics)
        self.assertEqual(report.format_specific.metrics["modal_dfl"].absolute_difference, 1400)

    # 25. Window Alignment Direct Index
    def test_window_alignment_direct_index(self):
        tl_a = create_mock_timeline("A", StreamFormat.MPEG_TS, num_windows=8, health_score=100.0)
        tl_b = create_mock_timeline("B", StreamFormat.MPEG_TS, num_windows=6, health_score=80.0)
        report = self.engine.compare(tl_a, tl_b)

        self.assertEqual(report.windows.aligned_window_count, 6)
        self.assertEqual(report.windows.unaligned_windows_a, 2)
        self.assertEqual(report.windows.unaligned_windows_b, 0)
        for h_delta in report.windows.health_delta_series:
            self.assertEqual(h_delta, -20.0)

    # 26. Window Alignment Progress Deciles
    def test_window_alignment_progress_deciles(self):
        tl_a = create_mock_timeline("A", StreamFormat.MPEG_TS, num_windows=20)
        tl_b = create_mock_timeline("B", StreamFormat.MPEG_TS, num_windows=20)
        report = self.engine.compare(tl_a, tl_b)

        self.assertEqual(len(report.windows.progress_deciles), 10)
        self.assertEqual(report.windows.progress_deciles[0]["progress_range"], "0-10%")
        self.assertEqual(report.windows.progress_deciles[9]["progress_range"], "90-100%")

    # 27. Unsupported Inferences Guard Enforced
    def test_unsupported_inferences_guard_enforced(self):
        tl_a = create_mock_timeline("A", StreamFormat.MPEG_TS)
        tl_b = create_mock_timeline("B", StreamFormat.MPEG_TS)
        report = self.engine.compare(tl_a, tl_b)

        guards = report.unsupported_inferences_guard
        self.assertTrue(any("RF interference" in g for g in guards))
        self.assertTrue(any("Demodulator or tuner" in g for g in guards))
        self.assertTrue(any("Satellite transponder" in g for g in guards))
        self.assertTrue(any("Signal-to-Noise Ratio" in g for g in guards))
        self.assertTrue(any("Transmission path error" in g for g in guards))


if __name__ == "__main__":
    unittest.main()
