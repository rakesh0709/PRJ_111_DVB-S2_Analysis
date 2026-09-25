"""
Unit and Integration Tests for Feature F5: Anomaly Explanation Engine (PRJ_111).

Comprehensive test suite verifying:
  1. basic explanation generation
  2. F2 anomaly integration
  3. top deviation extraction
  4. baseline vs observed values
  5. above/below direction
  6. bounded Z-score handling
  7. TS explanation
  8. GSE explanation
  9. BBFrame explanation
  10. F3 pattern integration
  11. F4 timeline integration
  12. no-anomaly handling
  13. empty/insufficient data
  14. deterministic output
  15. serialization (to_dict / to_json)
  16. unsupported inference guard
  17. truncated final-window explanation
  18. real TS dataset
  19. real GSE dataset
  20. real BBFrame dataset
  21. end-to-end F1 -> F2 -> F3 -> F4 -> F5 pipeline
"""

import json
import math
from pathlib import Path
import unittest

from dvbs2_analyzer.analysis.anomaly import (
    AnomalyConfig,
    AnomalyDetector,
    AnomalyReport,
    AnomalyResult,
    FeatureDeviation,
)
from dvbs2_analyzer.analysis.explanation import (
    AnomalyExplanation,
    AnomalyExplanationEngine,
    ExplanationConfig,
    ExplanationFinding,
    ExplanationReport,
)
from dvbs2_analyzer.analysis.health import HealthAnalyzer
from dvbs2_analyzer.analysis.patterns import (
    PatternConfig,
    PatternDetector,
    PatternFinding,
    PatternResult,
    PatternType,
)
from dvbs2_analyzer.analysis.timeline import (
    StreamTimeline,
    TimelineConfig,
    TimelineGenerator,
    TimelinePoint,
)
from dvbs2_analyzer.config import StreamFormat
from dvbs2_analyzer.features.extractor import (
    CommonMetrics,
    FeatureExtractor,
    TSSpecificMetrics,
    UnifiedStreamFeatureSet,
)
from dvbs2_analyzer.ingestion.stream_handler import StreamHandler
from dvbs2_analyzer.parsers.bbframe_parser import BBFrame, BBFrameStreamStatistics
from dvbs2_analyzer.parsers.gse_parser import GSEPDU
from dvbs2_analyzer.parsers.ts_parser import TSPacket

RAW_DATA_DIR = Path(__file__).resolve().parent.parent.parent / "01_RAW_DATA"


def make_sample_deviation(
    name: str = "pid_entropy",
    obs: float = 0.0,
    mean: float = 0.63,
    std: float = 0.27,
    z: float = 2.33,
    direction: str = "BELOW_BASELINE",
) -> FeatureDeviation:
    return FeatureDeviation(
        feature_name=name,
        observed_value=obs,
        baseline_mean=mean,
        baseline_std=std,
        z_score=z,
        direction=direction,
        interpretation=f"{name} is {direction.lower()} baseline",
    )


def make_sample_anomaly_result(
    is_anomaly: bool = True,
    score: float = 0.5232,
    severity: str = "LOW",
    deviations: list = None,
    w_idx: int = 1,
    fmt: str = "MPEG_TS",
) -> AnomalyResult:
    devs = deviations or [make_sample_deviation()]
    return AnomalyResult(
        is_anomaly=is_anomaly,
        anomaly_score=score,
        raw_score=-0.02,
        severity=severity,
        top_deviations=devs,
        summary_explanation="Elevated anomaly score driven by: " + "; ".join(d.interpretation for d in devs),
        feature_values={d.feature_name: d.observed_value for d in devs},
        window_index=w_idx,
        format=fmt,
    )


class TestAnomalyExplanationEngine(unittest.TestCase):
    """Test suite for Feature F5 Anomaly Explanation Engine."""

    def setUp(self):
        self.engine = AnomalyExplanationEngine()

    # -------------------------------------------------------------------------
    # 1. Basic Explanation Generation
    # -------------------------------------------------------------------------
    def test_basic_explanation_generation(self):
        anom_res = make_sample_anomaly_result()
        expl = self.engine.explain_anomaly(anom_res)

        self.assertIsInstance(expl, AnomalyExplanation)
        self.assertEqual(expl.window_index, 1)
        self.assertTrue(expl.is_anomaly)
        self.assertEqual(expl.anomaly_severity, "LOW")
        self.assertGreaterEqual(expl.anomaly_score, 0.50)
        self.assertIn("MPEG_TS", expl.format)
        self.assertIsInstance(expl.what_happened, str)
        self.assertIsInstance(expl.safe_conclusion, str)
        self.assertIsInstance(expl.concise_summary, str)

    # -------------------------------------------------------------------------
    # 2. F2 Anomaly Integration (Score, Severity, Decision)
    # -------------------------------------------------------------------------
    def test_f2_anomaly_integration(self):
        anom_res = make_sample_anomaly_result(score=0.8576, severity="CRITICAL")
        expl = self.engine.explain_anomaly(anom_res)

        # F5 must preserve F2's authoritative decision, score, and severity
        self.assertEqual(expl.anomaly_score, 0.8576)
        self.assertEqual(expl.anomaly_severity, "CRITICAL")
        self.assertTrue(expl.is_anomaly)
        self.assertEqual(expl.anomaly_threshold, 0.50)

    # -------------------------------------------------------------------------
    # 3. Top Deviation Extraction
    # -------------------------------------------------------------------------
    def test_top_deviation_extraction(self):
        dev1 = make_sample_deviation("pid_entropy", 0.0, 0.63, 0.27, 2.33, "BELOW_BASELINE")
        dev2 = make_sample_deviation("unique_pid_count", 1.0, 3.75, 1.03, 2.67, "BELOW_BASELINE")
        dev3 = make_sample_deviation("adaptation_field_ratio", 0.15, 0.05, 0.03, 3.33, "ABOVE_BASELINE")
        anom_res = make_sample_anomaly_result(deviations=[dev1, dev2, dev3])

        expl = self.engine.explain_anomaly(anom_res)
        self.assertEqual(len(expl.primary_drivers), 3)
        self.assertEqual(expl.primary_drivers[0].feature_name, "pid_entropy")
        self.assertEqual(expl.primary_drivers[1].feature_name, "unique_pid_count")
        self.assertEqual(expl.primary_drivers[2].feature_name, "adaptation_field_ratio")

    # -------------------------------------------------------------------------
    # 4. Baseline vs Observed Values
    # -------------------------------------------------------------------------
    def test_baseline_vs_observed_values(self):
        dev = make_sample_deviation("pid_entropy", obs=0.10, mean=0.60, std=0.25, z=2.0)
        anom_res = make_sample_anomaly_result(deviations=[dev])
        expl = self.engine.explain_anomaly(anom_res)

        driver = expl.primary_drivers[0]
        self.assertEqual(driver.observed_value, 0.10)
        self.assertEqual(driver.baseline_mean, 0.60)
        self.assertEqual(driver.baseline_std, 0.25)
        self.assertIn("0.10", driver.evidence)
        self.assertIn("0.60", driver.evidence)

    # -------------------------------------------------------------------------
    # 5. Above / Below Direction
    # -------------------------------------------------------------------------
    def test_above_below_direction(self):
        dev_below = make_sample_deviation("unique_pid_count", 1.0, 4.0, 1.0, 3.0, "BELOW_BASELINE")
        dev_above = make_sample_deviation("adaptation_field_ratio", 0.20, 0.05, 0.03, 5.0, "ABOVE_BASELINE")
        anom_res = make_sample_anomaly_result(deviations=[dev_below, dev_above])

        expl = self.engine.explain_anomaly(anom_res)
        self.assertEqual(expl.primary_drivers[0].direction, "BELOW_BASELINE")
        self.assertEqual(expl.primary_drivers[1].direction, "ABOVE_BASELINE")

    # -------------------------------------------------------------------------
    # 6. Bounded Z-Score Handling
    # -------------------------------------------------------------------------
    def test_bounded_z_score_handling(self):
        # Even with high Z-score, explanation should format cleanly without crashing or NaN
        dev = make_sample_deviation("log_total_units", 0.954, 2.300, 0.145, 9.28, "BELOW_BASELINE")
        anom_res = make_sample_anomaly_result(deviations=[dev])
        expl = self.engine.explain_anomaly(anom_res)

        self.assertFalse(math.isnan(expl.primary_drivers[0].z_score))
        self.assertGreater(expl.primary_drivers[0].z_score, 0.0)
        self.assertIn("|z|=9.3 below baseline", expl.primary_drivers[0].evidence)

    # -------------------------------------------------------------------------
    # 7. MPEG-TS Specific Explanation
    # -------------------------------------------------------------------------
    def test_ts_specific_explanation(self):
        dev1 = make_sample_deviation("pid_entropy", 0.0, 0.63, 0.27, 2.33, "BELOW_BASELINE")
        anom_res = make_sample_anomaly_result(deviations=[dev1], fmt="MPEG_TS")
        expl = self.engine.explain_anomaly(anom_res, stream_format=StreamFormat.MPEG_TS)

        self.assertIn("MPEG_TS", expl.format)
        self.assertIn("MPEG-TS", expl.primary_drivers[0].native_component)
        self.assertIn("PID", expl.primary_drivers[0].description)
        self.assertIn("multiplex", expl.what_happened.lower())

    # -------------------------------------------------------------------------
    # 8. GSE Specific Explanation
    # -------------------------------------------------------------------------
    def test_gse_specific_explanation(self):
        dev = make_sample_deviation("fragmentation_ratio", 0.80, 0.20, 0.15, 4.0, "ABOVE_BASELINE")
        anom_res = make_sample_anomaly_result(deviations=[dev], fmt="GSE")
        expl = self.engine.explain_anomaly(anom_res, stream_format=StreamFormat.GSE)

        self.assertEqual(expl.format, "GSE")
        self.assertIn("GSE", expl.primary_drivers[0].native_component)
        self.assertIn("fragmentation", expl.what_happened.lower())
        self.assertIn("MTU", expl.safe_conclusion)

    # -------------------------------------------------------------------------
    # 9. BBFrame Specific Explanation
    # -------------------------------------------------------------------------
    def test_bbframe_specific_explanation(self):
        dev = make_sample_deviation("sis_ratio", 0.980, 1.000, 0.002, 9.3, "BELOW_BASELINE")
        anom_res = make_sample_anomaly_result(deviations=[dev], fmt="BB_FRAME")
        expl = self.engine.explain_anomaly(anom_res, stream_format=StreamFormat.BB_FRAME)

        self.assertEqual(expl.format, "BB_FRAME")
        self.assertIn("Baseband", expl.primary_drivers[0].native_component)
        self.assertIn("Single Input Stream", expl.primary_drivers[0].description)

    # -------------------------------------------------------------------------
    # 10. F3 Pattern Integration
    # -------------------------------------------------------------------------
    def test_f3_pattern_integration(self):
        pf = PatternFinding(
            pattern_type=PatternType.TS_DOMINANT_PID.value,
            format=StreamFormat.MPEG_TS,
            description="PID 256 accounts for 100.0% of packets",
            supporting_metrics={"dominant_pid": 256, "percentage": 100.0},
            evidence="200 packets examined",
        )
        pat_res = PatternResult(
            format=StreamFormat.MPEG_TS,
            window_index=1,
            findings=[pf],
            metrics_summary={"dominant_pid": 256},
        )
        anom_res = make_sample_anomaly_result()
        expl = self.engine.explain_anomaly(anom_res, pattern_result=pat_res)

        self.assertEqual(len(expl.supporting_patterns), 1)
        self.assertEqual(expl.supporting_patterns[0]["pattern_type"], PatternType.TS_DOMINANT_PID.value)
        self.assertIn("PID 256", expl.supporting_patterns[0]["description"])

    # -------------------------------------------------------------------------
    # 11. F4 Timeline Integration
    # -------------------------------------------------------------------------
    def test_f4_timeline_integration(self):
        # Build synthetic timeline with 2 windows (1 normal, 1 anomaly)
        p0 = TimelinePoint(
            window_index=0, unit_offset_start=0, unit_offset_end=200,
            byte_offset_start=0, byte_offset_end=37600, unit_count=200,
            valid_units=200, invalid_units=0, payload_bytes=35000, payload_kb=34.18,
            unit_density=200, health_score=100.0, health_status="HEALTHY",
            error_count=0, error_rate=0.0, is_anomaly=False, anomaly_score=0.22,
            anomaly_severity="NORMAL", anomaly_explanation="Normal telemetry",
            top_deviations=[], pattern_findings=[], format_specific_metrics={},
        )
        p1 = TimelinePoint(
            window_index=1, unit_offset_start=200, unit_offset_end=400,
            byte_offset_start=37600, byte_offset_end=75200, unit_count=200,
            valid_units=200, invalid_units=0, payload_bytes=35000, payload_kb=34.18,
            unit_density=200, health_score=100.0, health_status="HEALTHY",
            error_count=0, error_rate=0.0, is_anomaly=True, anomaly_score=0.53,
            anomaly_severity="LOW", anomaly_explanation="Elevated anomaly",
            top_deviations=[make_sample_deviation().to_dict()],
            pattern_findings=[], format_specific_metrics={},
        )
        timeline = StreamTimeline(
            stream_name="test_ts", format=StreamFormat.MPEG_TS, total_units=400,
            total_bytes=75200, window_size=200, total_windows=2, anomaly_threshold=0.50,
            points=[p0, p1], events=[], summary_stats={},
        )

        report = self.engine.explain_timeline(timeline)
        self.assertIsInstance(report, ExplanationReport)
        self.assertEqual(report.total_windows, 2)
        self.assertEqual(report.anomaly_count, 1)
        self.assertEqual(len(report.explanations), 1)
        self.assertEqual(report.explanations[0].window_index, 1)

    # -------------------------------------------------------------------------
    # 12. No-Anomaly Handling
    # -------------------------------------------------------------------------
    def test_no_anomaly_handling(self):
        anom_res = make_sample_anomaly_result(is_anomaly=False, score=0.21, severity="NORMAL")
        expl = self.engine.explain_anomaly(anom_res)

        self.assertFalse(expl.is_anomaly)
        self.assertEqual(expl.anomaly_severity, "NORMAL")
        self.assertIn("Nominal", expl.what_happened)
        self.assertIn("consistent with learned baseline", expl.safe_conclusion.lower())

    # -------------------------------------------------------------------------
    # 13. Empty / Insufficient Data Handling
    # -------------------------------------------------------------------------
    def test_empty_insufficient_data(self):
        anom_res = AnomalyResult(
            is_anomaly=False, anomaly_score=0.20, raw_score=0.20, severity="NORMAL",
            top_deviations=[], summary_explanation="Insufficient data", feature_values={},
            window_index=0, format="MPEG_TS",
        )
        expl = self.engine.explain_anomaly(anom_res)
        self.assertIsInstance(expl, AnomalyExplanation)
        self.assertEqual(len(expl.primary_drivers), 0)

    # -------------------------------------------------------------------------
    # 14. Deterministic Output
    # -------------------------------------------------------------------------
    def test_deterministic_output(self):
        anom_res = make_sample_anomaly_result()
        expl1 = self.engine.explain_anomaly(anom_res)
        expl2 = self.engine.explain_anomaly(anom_res)

        self.assertEqual(expl1.to_dict(), expl2.to_dict())
        self.assertEqual(expl1.render_ascii(), expl2.render_ascii())

    # -------------------------------------------------------------------------
    # 15. Serialization (to_dict / to_json)
    # -------------------------------------------------------------------------
    def test_serialization(self):
        anom_res = make_sample_anomaly_result()
        expl = self.engine.explain_anomaly(anom_res)

        d = expl.to_dict()
        self.assertIsInstance(d, dict)
        self.assertIn("what_happened", d)
        self.assertIn("safe_conclusion", d)
        self.assertIn("unsupported_inferences", d)
        self.assertIn("primary_drivers", d)

        # JSON serialize
        json_str = json.dumps(d)
        self.assertIn("EXP_MPEG_TS_W1", json_str)

    # -------------------------------------------------------------------------
    # 16. Unsupported Inference Guard (Domain Safety)
    # -------------------------------------------------------------------------
    def test_unsupported_inference_guard(self):
        anom_res = make_sample_anomaly_result()
        expl = self.engine.explain_anomaly(anom_res)

        # Must explicitly contain guarded inferences
        guard_text = " ".join(expl.unsupported_inferences).lower()
        self.assertIn("rf", guard_text)
        self.assertIn("demodulator", guard_text)
        self.assertIn("satellite transponder", guard_text)

        # Must NOT claim unverified failures
        narrative = (expl.what_happened + expl.safe_conclusion + expl.concise_summary).lower()
        self.assertNotIn("rain fade detected", narrative)
        self.assertNotIn("demodulator failure", narrative)
        self.assertNotIn("hardware failure", narrative)

    # -------------------------------------------------------------------------
    # 17. Truncated Final-Window Explanation
    # -------------------------------------------------------------------------
    def test_truncated_final_window_explanation(self):
        dev = make_sample_deviation("log_total_units", obs=2.246, mean=2.300, std=0.0058, z=9.3, direction="BELOW_BASELINE")
        anom_res = make_sample_anomaly_result(deviations=[dev], score=0.85, severity="CRITICAL", w_idx=90)
        expl = self.engine.explain_anomaly(anom_res)

        self.assertIn("reduced unit count", expl.what_happened.lower())
        self.assertIn("termination", expl.safe_conclusion.lower())
        self.assertIn("recording", expl.safe_conclusion.lower())
        self.assertIn("Stream Slicing", expl.native_component)

    # -------------------------------------------------------------------------
    # 18. Real MPEG-TS Dataset Explanation
    # -------------------------------------------------------------------------
    def test_real_ts_dataset_explanations(self):
        ts_file = RAW_DATA_DIR / "03_TS" / "DVBS2_toolkit" / "sample.ts"
        handler = StreamHandler(ts_file, forced_format=StreamFormat.MPEG_TS)
        gen = TimelineGenerator(TimelineConfig(ts_window_size=200, f2_contamination=0.05))
        timeline = gen.generate_from_handler(handler, window_size=200)

        report = self.engine.explain_timeline(timeline)
        self.assertEqual(report.total_windows, 91)
        self.assertEqual(report.anomaly_count, 5)
        self.assertEqual(len(report.explanations), 5)

        # Check Window 1 explanation (PID concentration)
        w1_expl = [e for e in report.explanations if e.window_index == 1][0]
        self.assertIn("multiplex", w1_expl.what_happened.lower())
        self.assertIn("PID", w1_expl.primary_drivers[0].description)

        # Check Window 90 explanation (truncated window)
        w90_expl = [e for e in report.explanations if e.window_index == 90][0]
        self.assertIn("termination", w90_expl.safe_conclusion.lower())

    # -------------------------------------------------------------------------
    # 19. Real GSE Dataset Explanation
    # -------------------------------------------------------------------------
    def test_real_gse_dataset_explanations(self):
        gse_file = RAW_DATA_DIR / "02_GSE" / "GSExtract" / "sample.ts"
        handler = StreamHandler(gse_file, forced_format=StreamFormat.GSE)
        gen = TimelineGenerator(TimelineConfig(gse_window_size=3, f2_contamination=0.05))
        timeline = gen.generate_from_handler(handler, window_size=3)

        report = self.engine.explain_timeline(timeline)
        self.assertEqual(report.total_windows, 5)
        self.assertEqual(report.anomaly_count, 1)

        expl = report.explanations[0]
        self.assertEqual(expl.window_index, 4)
        self.assertIn("GSE", expl.format)
        self.assertTrue(len(expl.unsupported_inferences) > 0)

    # -------------------------------------------------------------------------
    # 20. Real BBFrame Dataset Explanation
    # -------------------------------------------------------------------------
    def test_real_bbframe_dataset_explanations(self):
        bb_file = RAW_DATA_DIR / "01_BBFRAME_GSE" / "dvb-s2_bb_example.pcap"
        handler = StreamHandler(bb_file, forced_format=StreamFormat.BB_FRAME)
        gen = TimelineGenerator(TimelineConfig(bbframe_window_size=50, f2_contamination=0.05))
        timeline = gen.generate_from_handler(handler, window_size=50)

        report = self.engine.explain_timeline(timeline)
        self.assertEqual(report.total_windows, 87)
        self.assertEqual(report.anomaly_count, 5)
        self.assertEqual(len(report.explanations), 5)

        # Check Window 0 (SIS ratio)
        w0_expl = [e for e in report.explanations if e.window_index == 0][0]
        self.assertIn("sis_ratio", [d.feature_name for d in w0_expl.primary_drivers])

        # Check Window 86 (truncated window)
        w86_expl = [e for e in report.explanations if e.window_index == 86][0]
        self.assertIn("termination", w86_expl.safe_conclusion.lower())

    # -------------------------------------------------------------------------
    # 21. True End-to-End Pipeline (F1 -> F2 -> F3 -> F4 -> F5)
    # -------------------------------------------------------------------------
    def test_true_end_to_end_pipeline_f1_to_f5(self):
        """
        True End-to-End test:
        raw TS capture -> native parser -> sequential windowing -> F1 Health
        -> F2 Anomaly -> F3 Patterns -> F4 Timeline -> F5 Explanations.
        """
        ts_file = RAW_DATA_DIR / "03_TS" / "DVBS2_toolkit" / "sample.ts"
        handler = StreamHandler(ts_file, forced_format=StreamFormat.MPEG_TS)
        parser = handler.get_parser()
        packets = list(parser.parse_file(ts_file, max_packets=600))
        self.assertEqual(len(packets), 600)

        gen = TimelineGenerator(TimelineConfig(ts_window_size=200, f2_contamination=0.05))
        timeline = gen.generate_ts_timeline(packets, window_size=200)
        self.assertEqual(timeline.total_windows, 3)

        # Generate F5 explanation report
        report = self.engine.explain_timeline(timeline)
        self.assertIsInstance(report, ExplanationReport)
        self.assertEqual(report.total_windows, 3)

        # Verify each window has valid telemetry across F1, F2, F3, F4, F5
        for p in timeline.points:
            self.assertEqual(p.health_status, "HEALTHY")
            self.assertIsInstance(p.anomaly_score, float)
            self.assertIsInstance(p.pattern_findings, list)
            if p.is_anomaly:
                self.assertIsNotNone(p.explanation)
                self.assertIn("what_happened", p.explanation)
                self.assertIn("safe_conclusion", p.explanation)

        # Verify ASCII report rendering
        ascii_summary = report.render_ascii_summary()
        self.assertIn("FEATURE F5 — ANOMALY EXPLANATION REPORT", ascii_summary)


if __name__ == "__main__":
    unittest.main()
