"""
Unit and Integration Tests for Feature F7: Automatic Analysis Report.

Tests all 24 planned cases covering schema, tripartite finding taxonomy,
epistemic safety, domain safety guards, single/dual-stream modes, multi-format
rendering, and regression stability.
"""

from pathlib import Path
import json
import unittest

from dvbs2_analyzer.analysis.comparison import (
    ComparisonConfig,
    StreamComparisonEngine,
)
from dvbs2_analyzer.analysis.explanation import (
    AnomalyExplanation,
    ExplanationConfig,
    ExplanationReport,
)
from dvbs2_analyzer.analysis.report import (
    CATEGORY_ENGINEERING_INTERPRETATION,
    CATEGORY_OBSERVED_FACT,
    CATEGORY_STATISTICAL_FINDING,
    MANDATORY_DOMAIN_SAFETY_NOTICE,
    AnomalyFindingsSection,
    AutomaticAnalysisReport,
    AutomaticReportGenerator,
    ComparisonFindingsSection,
    ExplanationFindingsSection,
    HealthFindingsSection,
    PatternFindingsSection,
    ReportConfig,
    ReportFinding,
    StreamSummarySection,
    TimelineFindingsSection,
)
from dvbs2_analyzer.analysis.timeline import StreamTimeline, TimelinePoint
from dvbs2_analyzer.config import StreamFormat


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
    protocol: str = "IPv4",
) -> StreamTimeline:
    """Helper to construct synthetic StreamTimeline objects for report tests."""
    points = []
    for i in range(num_windows):
        fmt_metrics = {}
        if fmt == StreamFormat.MPEG_TS:
            fmt_metrics = {
                "pid_entropy": 0.15,
                "null_packet_ratio": 0.02,
                "tei_error_rate": 0.0,
                "continuity_error_rate": 0.0,
                "dominant_pid": dominant_pid,
                "dominant_pid_pct": 98.5,
                "dominant_pid_summary": f"PID 0x{dominant_pid:04X}",
                "unique_pids": 2,
            }
        elif fmt == StreamFormat.BB_FRAME:
            fmt_metrics = {
                "modal_dfl": modal_dfl,
                "crc_errors": 0,
            }
        elif fmt == StreamFormat.GSE:
            fmt_metrics = {
                "fragmentation_ratio": 0.10,
                "dominant_protocol": protocol,
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


class TestAutomaticReport(unittest.TestCase):
    """24 Automated Tests for Feature F7 Automatic Analysis Report."""

    def setUp(self):
        self.generator = AutomaticReportGenerator(ReportConfig())

    # 1. Config Defaults
    def test_report_config_defaults(self):
        cfg = ReportConfig()
        self.assertEqual(cfg.title, "PRJ_111 Automatic Analysis Report")
        self.assertTrue(cfg.include_raw_telemetry)
        self.assertTrue(cfg.include_explanations)
        self.assertTrue(cfg.include_comparison)
        self.assertEqual(cfg.max_detailed_anomalies, 10)
        self.assertTrue(cfg.strict_domain_safety)

    # 2. Single Stream TS Report
    def test_single_stream_ts_report(self):
        tl = create_mock_timeline("MPEG_TS_Stream", StreamFormat.MPEG_TS, num_windows=5)
        report = self.generator.generate_from_timeline(tl)

        self.assertEqual(report.mode, "SINGLE_STREAM")
        self.assertEqual(report.stream_info.detected_format, "MPEG_TS")
        self.assertEqual(report.health.health_status, "HEALTHY")
        self.assertIn("PID", report.patterns.dominant_component)
        self.assertIsNone(report.comparison)

    # 3. Single Stream GSE Report
    def test_single_stream_gse_report(self):
        tl = create_mock_timeline("GSE_Stream", StreamFormat.GSE, num_windows=4)
        report = self.generator.generate_from_timeline(tl)

        self.assertEqual(report.stream_info.detected_format, "GSE")
        self.assertIn("Protocol IPv4", report.patterns.dominant_component)

    # 4. Single Stream BBFrame Report
    def test_single_stream_bbframe_report(self):
        tl = create_mock_timeline("BB_Stream", StreamFormat.BB_FRAME, num_windows=6, modal_dfl=4000)
        report = self.generator.generate_from_timeline(tl)

        self.assertEqual(report.stream_info.detected_format, "BB_FRAME")
        self.assertIn("DFL 4000", report.patterns.dominant_component)

    # 5. Dual Stream Same Format Report
    def test_dual_stream_same_format_report(self):
        tl_a = create_mock_timeline("TS_A", StreamFormat.MPEG_TS, num_windows=5, payload_kb=30.0)
        tl_b = create_mock_timeline("TS_B", StreamFormat.MPEG_TS, num_windows=5, payload_kb=40.0)
        comp_engine = StreamComparisonEngine(ComparisonConfig())
        comp_rep = comp_engine.compare_timelines(tl_a, tl_b)

        report = self.generator.generate_from_timeline(tl_a, comparison_report=comp_rep)

        self.assertEqual(report.mode, "DUAL_STREAM")
        self.assertIsNotNone(report.comparison)
        self.assertTrue(report.comparison.is_same_format)
        self.assertEqual(report.comparison.stream_b_name, "TS_B")

    # 6. Dual Stream Cross Format Report
    def test_dual_stream_cross_format_report(self):
        tl_ts = create_mock_timeline("TS_Stream", StreamFormat.MPEG_TS, num_windows=5)
        tl_bb = create_mock_timeline("BB_Stream", StreamFormat.BB_FRAME, num_windows=5)
        comp_engine = StreamComparisonEngine(ComparisonConfig())
        comp_rep = comp_engine.compare_timelines(tl_ts, tl_bb)

        report = self.generator.generate_from_timeline(tl_ts, comparison_report=comp_rep)

        self.assertEqual(report.mode, "DUAL_STREAM")
        self.assertIsNotNone(report.comparison)
        self.assertFalse(report.comparison.is_same_format)

    # 7. Tripartite Categorization Integrity
    def test_tripartite_categorization_integrity(self):
        tl = create_mock_timeline("TestStream", StreamFormat.MPEG_TS, num_windows=5)
        report = self.generator.generate_from_timeline(tl)

        valid_categories = {CATEGORY_OBSERVED_FACT, CATEGORY_STATISTICAL_FINDING, CATEGORY_ENGINEERING_INTERPRETATION}
        self.assertGreater(len(report.tripartite_findings), 0)
        for f in report.tripartite_findings:
            self.assertIn(f.category, valid_categories, f"Invalid finding category: {f.category}")

    # 8. Observed Facts Grounding
    def test_observed_facts_grounding(self):
        tl = create_mock_timeline("TestStream", StreamFormat.MPEG_TS, num_windows=5)
        report = self.generator.generate_from_timeline(tl)

        facts = [f for f in report.tripartite_findings if f.category == CATEGORY_OBSERVED_FACT]
        self.assertGreater(len(facts), 0)
        for fact in facts:
            self.assertTrue(len(fact.evidence) > 0, f"Fact '{fact.title}' lacks supporting evidence.")

    # 9. Statistical Findings Grounding
    def test_statistical_findings_grounding(self):
        tl = create_mock_timeline("TestStream", StreamFormat.MPEG_TS, num_windows=5)
        report = self.generator.generate_from_timeline(tl)

        stats = [f for f in report.tripartite_findings if f.category == CATEGORY_STATISTICAL_FINDING]
        self.assertGreater(len(stats), 0)
        for stat in stats:
            self.assertTrue(len(stat.evidence) > 0, f"Statistical finding '{stat.title}' lacks numerical evidence.")

    # 10. Engineering Interpretations Grounding
    def test_engineering_interpretations_grounding(self):
        tl = create_mock_timeline("TestStream", StreamFormat.MPEG_TS, num_windows=5)
        report = self.generator.generate_from_timeline(tl)

        interps = [f for f in report.tripartite_findings if f.category == CATEGORY_ENGINEERING_INTERPRETATION]
        self.assertGreater(len(interps), 0)
        for interp in interps:
            self.assertTrue(len(interp.statement) > 0)
            self.assertTrue(len(interp.evidence) > 0)

    # 11. F1 Health Findings Inclusion
    def test_f1_health_findings_inclusion(self):
        tl = create_mock_timeline("TS_Healthy", StreamFormat.MPEG_TS, health_score=98.5)
        report = self.generator.generate_from_timeline(tl)

        self.assertAlmostEqual(report.health.health_score, 98.5, places=1)
        self.assertEqual(report.health.health_status, "HEALTHY")
        self.assertIn("framing_sync_integrity", report.health.selected_priority1_checks)

    # 12. F2 Anomaly Findings Inclusion
    def test_f2_anomaly_findings_inclusion(self):
        tl = create_mock_timeline("TS_Anom", StreamFormat.MPEG_TS, is_anomaly=True, anomaly_score=0.82, anomaly_severity="HIGH")
        report = self.generator.generate_from_timeline(tl)

        self.assertEqual(report.anomalies.anomalous_windows, 10)
        self.assertAlmostEqual(report.anomalies.peak_anomaly_score, 0.82, places=2)
        self.assertEqual(report.anomalies.severity_breakdown["HIGH"], 10)

    # 13. F3 Pattern Findings Inclusion
    def test_f3_pattern_findings_inclusion(self):
        tl = create_mock_timeline("TS_PID", StreamFormat.MPEG_TS, dominant_pid=0x0100)
        report = self.generator.generate_from_timeline(tl)

        self.assertIn("0x0100", report.patterns.dominant_component)
        self.assertEqual(report.patterns.active_component_count, 2)

    # 14. F4 Timeline Findings Inclusion
    def test_f4_timeline_findings_inclusion(self):
        tl = create_mock_timeline("TS_Time", StreamFormat.MPEG_TS, num_windows=8, window_size=200, payload_kb=34.5)
        report = self.generator.generate_from_timeline(tl)

        self.assertEqual(report.timeline.window_size, 200)
        self.assertEqual(report.timeline.total_windows, 8)
        self.assertAlmostEqual(report.timeline.payload_volume_kb_mean, 34.5, places=1)

    # 15. F5 Explanations Findings Inclusion
    def test_f5_explanations_findings_inclusion(self):
        tl = create_mock_timeline("TS_Expl", StreamFormat.MPEG_TS, num_windows=5)
        expl_report = ExplanationReport(
            stream_name="TS_Expl",
            format="MPEG_TS",
            total_windows=5,
            anomaly_count=1,
            anomaly_threshold=0.50,
            explanations=[
                AnomalyExplanation(
                    explanation_id="EX_1",
                    format="MPEG_TS",
                    window_index=0,
                    unit_offset_start=0,
                    unit_offset_end=200,
                    byte_offset_start=0,
                    byte_offset_end=37600,
                    anomaly_score=0.85,
                    anomaly_severity="HIGH",
                    anomaly_threshold=0.50,
                    is_anomaly=True,
                    primary_drivers=[],
                    native_component="FRAMING",
                    concise_summary="Anomaly in Window 0 due to unit count deviation.",
                )
            ],
            summary_stats={"anomaly_windows": 1},
        )

        report = self.generator.generate_from_timeline(tl, explanation_report=expl_report)

        self.assertIsNotNone(report.explanations)
        self.assertEqual(report.explanations.explained_anomalies_count, 1)
        self.assertIn("FRAMING", report.explanations.subsystem_distribution)

    # 16. F6 Comparison Findings Inclusion
    def test_f6_comparison_findings_inclusion(self):
        tl_a = create_mock_timeline("TS_A", StreamFormat.MPEG_TS, payload_kb=20.0)
        tl_b = create_mock_timeline("TS_B", StreamFormat.MPEG_TS, payload_kb=30.0)
        comp_engine = StreamComparisonEngine()
        comp_rep = comp_engine.compare_timelines(tl_a, tl_b)

        report = self.generator.generate_from_timeline(tl_a, comparison_report=comp_rep)

        self.assertIsNotNone(report.comparison)
        self.assertIn("total_payload_bytes", report.comparison.common_metrics_differential)
        self.assertGreater(len(report.comparison.key_differences), 0)

    # 17. Domain Safety Guard Enforced
    def test_domain_safety_guard_enforced(self):
        tl = create_mock_timeline("TS_Safe", StreamFormat.MPEG_TS)
        report = self.generator.generate_from_timeline(tl)

        guards = report.unsupported_inferences_guard
        self.assertTrue(any("RF interference" in g for g in guards))
        self.assertTrue(any("Demodulator or tuner" in g for g in guards))
        self.assertTrue(any("Satellite transponder" in g for g in guards))
        self.assertTrue(any("Signal-to-Noise Ratio" in g for g in guards))

        report_txt = report.render_text()
        self.assertIn(MANDATORY_DOMAIN_SAFETY_NOTICE, report_txt)

    # 18. Terminology Safety Enforced
    def test_terminology_safety_enforced(self):
        tl = create_mock_timeline("TS_Term", StreamFormat.MPEG_TS)
        report = self.generator.generate_from_timeline(tl)

        full_text = report.render_markdown() + report.render_text()
        self.assertNotIn("elementary stream", full_text.lower())
        self.assertNotIn("etsi tr 101 290 compliant", full_text.lower())
        self.assertNotIn("certified", full_text.lower())

    # 19. Render JSON Validity
    def test_render_json_validity(self):
        tl = create_mock_timeline("TS_JSON", StreamFormat.MPEG_TS)
        report = self.generator.generate_from_timeline(tl)

        json_str = report.to_json()
        parsed = json.loads(json_str)

        self.assertEqual(parsed["report_id"], report.report_id)
        self.assertEqual(parsed["stream_info"]["stream_name"], "TS_JSON")
        self.assertIsInstance(parsed["tripartite_findings"], list)

    # 20. Render Markdown Format
    def test_render_markdown_format(self):
        tl = create_mock_timeline("TS_MD", StreamFormat.MPEG_TS)
        report = self.generator.generate_from_timeline(tl)

        md = report.render_markdown()
        self.assertIn("# PRJ_111 Automatic Analysis Report: TS_MD", md)
        self.assertIn("Epistemological Tripartite Register", md)
        self.assertIn("| Subsystem | Title | Observation Statement | Grounding Evidence |", md)

    # 21. Render Text cp1252 Safety
    def test_render_text_cp1252_safety(self):
        tl = create_mock_timeline("TS_Text", StreamFormat.MPEG_TS)
        report = self.generator.generate_from_timeline(tl)

        txt = report.render_text()
        # Must encode cleanly to Windows cp1252 without raising UnicodeEncodeError
        encoded = txt.encode("cp1252")
        self.assertGreater(len(encoded), 100)

    # 22. Render HTML Standalone Validity
    def test_render_html_standalone_validity(self):
        tl = create_mock_timeline("TS_HTML", StreamFormat.MPEG_TS)
        report = self.generator.generate_from_timeline(tl)

        html = report.render_html()
        self.assertIn("<!DOCTYPE html>", html)
        self.assertIn("PRJ_111 Automatic Analysis Report", html)
        self.assertIn("Epistemological Tripartite Register", html)
        self.assertIn("</html>", html)

    # 23. Epistemic Safety: No Unsupported Causal Assertions
    def test_epistemic_safety_no_unsupported_causal_assertions(self):
        tl = create_mock_timeline("TS_Causal", StreamFormat.MPEG_TS, is_anomaly=True)
        report = self.generator.generate_from_timeline(tl)

        for finding in report.tripartite_findings:
            combined = (finding.title + " " + finding.statement + " " + finding.evidence).lower()
            self.assertNotIn("cold baseline stabilization", combined)
            self.assertNotIn("capture start caused", combined)
            self.assertNotIn("traffic burst", combined)
            self.assertNotIn("video stream", combined)
            self.assertNotIn("audio stream", combined)

    # 24. Capture Boundary Neutral Attribution
    def test_capture_boundary_neutral_attribution(self):
        tl = create_mock_timeline("TS_Boundary", StreamFormat.MPEG_TS, num_windows=5, window_size=200)
        tl.points[-1].unit_count = 50  # Edge window truncation

        report = self.generator.generate_from_timeline(tl)

        # Check findings mentioning boundary
        boundary_findings = [f for f in report.tripartite_findings if "boundary" in f.title.lower() or "boundary" in f.statement.lower()]
        self.assertGreater(len(boundary_findings), 0)
        for bf in boundary_findings:
            combined = (bf.title + " " + bf.statement).lower()
            self.assertNotIn("recording cessation", combined)
            self.assertNotIn("operator shutdown", combined)
            self.assertNotIn("transmission drop", combined)


    # 25. BBFrame Modal DFL Pattern Extraction
    def test_bbframe_modal_dfl_pattern_synthesis(self):
        """
        Verifies that BBFrame modal DFL is accurately extracted from modal_dfl_bits
        and populated into pattern findings without falling back to N/A.
        """
        tl = create_mock_timeline("BB_DFL_Test", StreamFormat.BB_FRAME, num_windows=3)
        tl.points[0].format_specific_metrics = {"modal_dfl_bits": 8304}
        tl.points[0].pattern_findings = [
            {
                "pattern_type": "BB_DFL_DISTRIBUTION",
                "supporting_metrics": {"modal_percentage": 92.0, "unique_dfl_count": 5},
            }
        ]

        report = self.generator.generate_from_timeline(tl)
        self.assertEqual(report.patterns.dominant_component, "DFL 8304 bits")
        self.assertAlmostEqual(report.patterns.dominant_component_pct, 92.0)
        self.assertEqual(report.patterns.active_component_count, 5)
        self.assertNotIn("N/A", report.patterns.dominant_component)


if __name__ == "__main__":
    unittest.main()

