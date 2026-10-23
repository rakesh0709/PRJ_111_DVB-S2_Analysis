"""
PRJ_111: Chunk 5 Investigation Workflow, F5 Diagnostic Quality, and F6 Semantic Shield Test Suite.

Focus Areas:
1. F4 Investigation Workflow: Selecting an anomalous window or timeline region leads to
   exact matching F5 diagnostic attributions, physical stream offsets, and telemetry consistency.
2. F5 Diagnostic Separation: Rigorous separation of observed facts, statistical findings,
   and engineering interpretations, strictly bounded by capture evidence.
3. F5 Epistemic Guardrails: Rejection of unsupported physical-layer inferences (RF, rain fade,
   demodulator failure) and rejection of unvalidated supervised ground-truth claims.
4. F6 Semantic Shield: Strict barrier enforcement between cross-format streams (exactly 2 comparable
   metrics vs. 9 incommensurable shielded metrics).
5. F6 Same-Format & Temporal Half Comparisons: Validated delta calculations and zero-baseline rules.
6. Multi-Format Compatibility: Consistent workflow across MPEG-TS, GSE, and BBFrame.
"""

from pathlib import Path
import tempfile
import unittest

from dvbs2_analyzer.analysis.comparison import (
    CROSS_FORMAT_INCOMPATIBLE_METRICS,
    ComparisonConfig,
    StreamComparisonEngine,
    compute_metric_difference,
)
from dvbs2_analyzer.analysis.explanation import (
    UNSUPPORTED_INFERENCES_GUARD,
    AnomalyExplanationEngine,
    ExplanationConfig,
)
from dvbs2_analyzer.config import RAW_DATA_DIR, StreamFormat
from dvbs2_analyzer.frontend.coordinator import AnalysisCoordinator


class TestChunk5Investigation(unittest.TestCase):
    """Automated tests for Chunk 5 investigation workflow, F5 explanations, and F6 comparison."""

    @classmethod
    def setUpClass(cls):
        cls.raw_ts = RAW_DATA_DIR / "03_TS" / "DVBS2_toolkit" / "sample.ts"
        cls.raw_gse = RAW_DATA_DIR / "02_GSE" / "GSExtract" / "sample.ts"
        cls.raw_bb = RAW_DATA_DIR / "01_BBFRAME_GSE" / "dvb-s2_bb_example.pcap"
        cls.coordinator = AnalysisCoordinator()
        cls.comp_engine = StreamComparisonEngine()

    # -------------------------------------------------------------------------
    # 1. F4 -> F5 Investigation Workflow Consistency
    # -------------------------------------------------------------------------

    def test_anomaly_investigation_workflow_linking(self):
        """
        Verifies that every flagged anomaly in F2/F4 maps directly to a valid F5 explanation
        record with identical window index, matching physical offsets, and consistent scores.
        """
        res = self.coordinator.analyze_stream(self.raw_ts, forced_format="MPEG_TS", window_size=200)
        self.assertTrue(res["success"])

        anom_windows = res["f2_anomalies"]["anomalous_windows"]
        self.assertGreater(len(anom_windows), 0)

        f5_expls = res["f5_explanations"]["explanations"]
        expl_map = {e["window_index"]: e for e in f5_expls}

        # Verify cross-feature linking
        for aw in anom_windows:
            w_idx = aw["window_index"]
            self.assertIn(w_idx, expl_map, f"Window {w_idx} flagged in F2 must have F5 explanation")
            expl = expl_map[w_idx]

            # Physical offsets must match exactly
            self.assertEqual(expl["unit_offset_start"], aw["unit_range"][0])
            self.assertEqual(expl["unit_offset_end"], aw["unit_range"][1])
            self.assertEqual(expl["byte_offset_start"], aw["byte_range"][0])
            self.assertEqual(expl["byte_offset_end"], aw["byte_range"][1])

            # Anomaly score and severity must be consistent
            self.assertAlmostEqual(expl["anomaly_score"], aw["score"], places=3)
            self.assertEqual(expl["anomaly_severity"], aw["severity"])

    def test_physical_offsets_no_fabricated_timestamps(self):
        """
        Confirms that timeline points and explanations use physical stream offsets
        (byte offsets and packet counts) rather than fabricated timestamps.
        """
        res = self.coordinator.analyze_stream(self.raw_ts, forced_format="MPEG_TS", window_size=200)
        tl_points = res["f4_timeline"]["points"]

        for pt in tl_points:
            self.assertIn("byte_offset_start", pt)
            self.assertIn("byte_offset_end", pt)
            self.assertIn("unit_offset_start", pt)
            self.assertIn("unit_offset_end", pt)
            self.assertGreaterEqual(pt["byte_offset_end"], pt["byte_offset_start"])
            self.assertGreaterEqual(pt["unit_offset_end"], pt["unit_offset_start"])
            # Must NOT contain fabricated wall-clock or synthetic absolute timestamps
            self.assertNotIn("synthetic_timestamp", pt)
            self.assertNotIn("fabricated_time", pt)

    # -------------------------------------------------------------------------
    # 2. F5 Diagnostic Separation (Facts vs Statistics vs Interpretations)
    # -------------------------------------------------------------------------

    def test_f5_facts_vs_statistics_vs_interpretation_separation(self):
        """
        Verifies that F5 explanations maintain strict separation between:
        - Observed facts (observed_value, baseline_mean, byte offsets)
        - Statistical findings (z_score, direction, deviation_pct)
        - Engineering interpretations (safe_inference, safe_conclusion)
        """
        res = self.coordinator.analyze_stream(self.raw_ts, forced_format="MPEG_TS", window_size=200)
        f5 = res["f5_explanations"]

        for expl in f5["explanations"]:
            # Observed facts
            self.assertIsInstance(expl["what_happened"], str)
            self.assertIsInstance(expl["native_component"], str)
            self.assertIsInstance(expl["byte_offset_start"], int)

            # Statistical findings
            self.assertIsInstance(expl["anomaly_score"], float)
            for d in expl.get("primary_drivers", []):
                self.assertIn(d["direction"], ["ABOVE_BASELINE", "BELOW_BASELINE", "NORMAL"])
                self.assertIsInstance(d["z_score"], float)
                # Bounded Z-score constraint (|Z| <= 20.0 sigma)
                self.assertLessEqual(abs(d["z_score"]), 20.0)

            # Engineering interpretations
            self.assertIsInstance(expl["safe_conclusion"], str)
            self.assertGreater(len(expl["safe_conclusion"]), 0)

    def test_f5_unsupported_inferences_guard_enforced(self):
        """
        Verifies that F5 explanations include explicit domain-safety guards against
        unsupported physical-layer or hardware speculation.
        """
        self.assertGreaterEqual(len(UNSUPPORTED_INFERENCES_GUARD), 5)
        combined_text = " ".join(UNSUPPORTED_INFERENCES_GUARD).lower()
        self.assertIn("rf interference", combined_text)
        self.assertIn("demodulator", combined_text)
        self.assertIn("satellite transponder", combined_text)
        self.assertIn("signal-to-noise ratio", combined_text)
        self.assertIn("transmission path error", combined_text)

    # -------------------------------------------------------------------------
    # 3. F6 Semantic Comparability Barrier
    # -------------------------------------------------------------------------

    def test_f6_semantic_comparability_barrier_enforced(self):
        """
        Verifies that cross-format comparisons (TS vs BBFrame) strictly enforce:
        - Exactly 2 comparable metrics: total_payload_bytes, integrity_ratio.
        - Exactly 9 shielded incommensurable metrics with domain rationales.
        """
        report = self.comp_engine.compare_files(self.raw_ts, self.raw_bb)
        self.assertFalse(report.is_same_format)

        comparable_names = [k for k, m in report.common.metrics.items() if m.direction != "NOT_COMPARABLE"]
        self.assertEqual(sorted(comparable_names), ["integrity_ratio", "total_payload_bytes"])

        incompatible_names = [k for k, m in report.common.metrics.items() if m.direction == "NOT_COMPARABLE"]
        expected_shielded = sorted([
            "total_units", "valid_units", "invalid_units", "truncated_units",
            "mean_payload_bytes", "payload_ratio", "error_count", "error_rate", "entropy"
        ])
        self.assertEqual(sorted(incompatible_names), expected_shielded)

        # Confirm all shielded metrics have non-empty domain rationales
        for k in incompatible_names:
            m = report.common.metrics[k]
            self.assertIn(k, CROSS_FORMAT_INCOMPATIBLE_METRICS)
            self.assertIsNotNone(m.incompatibility_reason)
            self.assertGreater(len(m.incompatibility_reason), 10)

    def test_f6_same_format_mathematical_zero_baseline(self):
        """
        Verifies mathematically sound zero-baseline comparison rules:
        - When baseline is 0 and target is 0: delta = 0.0%, UNCHANGED
        - When baseline is 0 and target > 0: delta = None (not arbitrary +100%)
        - When baseline > 0 and target is 0: delta = -100.0%
        """
        diff_0_0 = compute_metric_difference("test_metric", 0.0, 0.0, "units")
        self.assertEqual(diff_0_0.relative_difference_pct, 0.0)
        self.assertEqual(diff_0_0.classification, "UNCHANGED")

        diff_0_pos = compute_metric_difference("test_metric", 0.0, 50.0, "units")
        self.assertIsNone(diff_0_pos.relative_difference_pct)  # Mathematically undefined, never +100%
        self.assertEqual(diff_0_pos.classification, "INCREASED")

        diff_pos_0 = compute_metric_difference("test_metric", 100.0, 0.0, "units")
        self.assertEqual(diff_pos_0.relative_difference_pct, -100.0)
        self.assertEqual(diff_pos_0.classification, "DECREASED")

    def test_f6_temporal_half_comparison(self):
        """
        Verifies that splitting a stream into first-half vs second-half executes cleanly
        under same-format comparison rules and produces valid comparison output.
        """
        res = self.coordinator.compare_streams(
            file_path_a=self.raw_ts,
            file_path_b=self.raw_ts,
            is_half_comparison=True,
        )
        self.assertTrue(res["success"])
        self.assertTrue(res["comparison"]["is_same_format"])
        self.assertIn("First Half", res["comparison"]["stream_a_name"])
        self.assertIn("Second Half", res["comparison"]["stream_b_name"])

    # -------------------------------------------------------------------------
    # 4. Multi-Format Investigation Consistency
    # -------------------------------------------------------------------------

    def test_investigation_workflow_across_all_formats(self):
        """
        Verifies that the complete F1-F5 analysis pipeline and F6 comparison engine
        operate stably and consistently across all three supported formats.
        """
        for path, fmt, win in [
            (self.raw_ts, "MPEG_TS", 200),
            (self.raw_gse, "GSE", 3),
            (self.raw_bb, "BB_FRAME", 50),
        ]:
            res = self.coordinator.analyze_stream(path, forced_format=fmt, window_size=win)
            self.assertTrue(res["success"])
            self.assertEqual(res["f1_health"]["overall_health_score"], 100.0)
            self.assertIn("points", res["f4_timeline"])
            self.assertIn("explanations", res["f5_explanations"])
            self.assertGreater(len(res["f4_timeline"]["points"]), 0)


if __name__ == "__main__":
    unittest.main()
