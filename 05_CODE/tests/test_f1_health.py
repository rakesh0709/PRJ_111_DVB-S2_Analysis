"""
Unit and Integration Tests for Feature F1: Stream Health Analysis (PRJ_111).

Tests:
  - Quantitative feature extraction (entropy, null ratio, TEI, CC errors, adaptation fields)
  - Rule-based health classification (HEALTHY, WARNING, CRITICAL)
  - Edge cases (empty streams, malformed packets, sync loss)
  - Deterministic evaluation and threshold configurability
  - End-to-end pipeline integration on real satellite TS captures
"""

from pathlib import Path
import unittest

from dvbs2_analyzer.analysis.health import (
    HealthAnalyzer,
    HealthClassification,
    HealthThresholds,
    StreamHealthReport,
)
from dvbs2_analyzer.config import RAW_DATA_DIR
from dvbs2_analyzer.features.extractor import FeatureExtractor, StreamFeatureSet
from dvbs2_analyzer.parsers.ts_parser import TSStreamStatistics


class TestF1FeatureExtraction(unittest.TestCase):
    """Tests feature extraction logic from TS stream statistics."""

    def setUp(self):
        self.extractor = FeatureExtractor()

    def test_feature_extraction_complete_fields(self):
        stats = TSStreamStatistics()
        stats.total_packets = 1000
        stats.valid_sync_packets = 1000
        stats.sync_byte_errors = 0
        stats.tei_error_count = 5
        stats.null_packet_count = 100
        stats.payload_packet_count = 850
        stats.adaptation_field_count = 150
        stats.adaptation_only_count = 50
        stats.adaptation_and_payload_count = 100
        stats.total_payload_bytes = 150000
        stats.malformed_packet_count = 0
        stats.pid_counts[100] = 500
        stats.pid_counts[200] = 400
        stats.pid_counts[8191] = 100
        stats.continuity_errors[100] = 2

        features = self.extractor.extract_from_ts_stats(stats)

        self.assertEqual(features.total_packets, 1000)
        self.assertEqual(features.valid_packets, 1000)
        self.assertEqual(features.invalid_packets, 0)
        self.assertAlmostEqual(features.sync_integrity, 100.0)
        self.assertEqual(features.unique_pid_count, 3)
        self.assertEqual(features.null_packet_count, 100)
        self.assertAlmostEqual(features.null_packet_ratio, 0.10)
        self.assertEqual(features.tei_error_count, 5)
        self.assertAlmostEqual(features.tei_error_rate, 0.005)
        self.assertEqual(features.continuity_error_count, 2)
        self.assertAlmostEqual(features.continuity_error_rate, 0.002)
        self.assertEqual(features.adaptation_field_count, 150)
        self.assertAlmostEqual(features.adaptation_field_ratio, 0.15)
        self.assertEqual(features.adaptation_only_count, 50)
        self.assertEqual(features.adaptation_and_payload_count, 100)
        self.assertEqual(features.payload_packet_count, 850)
        self.assertAlmostEqual(features.payload_packet_ratio, 0.85)
        self.assertEqual(features.total_payload_bytes, 150000)
        self.assertAlmostEqual(features.mean_payload_bytes_per_packet, 150.0)

    def test_null_packet_ratio_calculation(self):
        stats = TSStreamStatistics()
        stats.total_packets = 500
        stats.valid_sync_packets = 500
        stats.null_packet_count = 250
        features = self.extractor.extract_from_ts_stats(stats)
        self.assertAlmostEqual(features.null_packet_ratio, 0.50)

    def test_pid_statistics_and_entropy(self):
        # Single PID -> zero entropy
        stats_single = TSStreamStatistics()
        stats_single.total_packets = 100
        stats_single.valid_sync_packets = 100
        stats_single.pid_counts[100] = 100
        features_single = self.extractor.extract_from_ts_stats(stats_single)
        self.assertEqual(features_single.pid_entropy, 0.0)

        # 4 equally distributed PIDs -> entropy = log2(4) = 2.0
        stats_uniform = TSStreamStatistics()
        stats_uniform.total_packets = 400
        stats_uniform.valid_sync_packets = 400
        for p in [10, 20, 30, 40]:
            stats_uniform.pid_counts[p] = 100
        features_uniform = self.extractor.extract_from_ts_stats(stats_uniform)
        self.assertAlmostEqual(features_uniform.pid_entropy, 2.0, places=2)
        self.assertEqual(len(features_uniform.pid_percentages), 4)
        for pct in features_uniform.pid_percentages.values():
            self.assertAlmostEqual(pct, 25.0)

    def test_tei_counting(self):
        stats = TSStreamStatistics()
        stats.total_packets = 200
        stats.valid_sync_packets = 200
        stats.tei_error_count = 10
        features = self.extractor.extract_from_ts_stats(stats)
        self.assertEqual(features.tei_error_count, 10)
        self.assertAlmostEqual(features.tei_error_rate, 0.05)

    def test_continuity_error_metrics(self):
        stats = TSStreamStatistics()
        stats.total_packets = 1000
        stats.valid_sync_packets = 1000
        stats.continuity_errors[101] = 3
        stats.continuity_errors[102] = 2
        features = self.extractor.extract_from_ts_stats(stats)
        self.assertEqual(features.continuity_error_count, 5)
        self.assertAlmostEqual(features.continuity_error_rate, 0.005)
        self.assertEqual(features.continuity_errors_by_pid, {101: 3, 102: 2})


class TestF1HealthClassification(unittest.TestCase):
    """Tests rule-based health classification against ETSI TR 101 290 thresholds."""

    def setUp(self):
        self.analyzer = HealthAnalyzer()

    def _create_features(
        self,
        total=1000,
        valid=1000,
        invalid=0,
        sync_integrity=100.0,
        null_count=50,
        tei_count=0,
        cc_count=0,
    ) -> StreamFeatureSet:
        null_ratio = null_count / total if total > 0 else 0.0
        tei_rate = tei_count / total if total > 0 else 0.0
        cc_rate = cc_count / total if total > 0 else 0.0

        return StreamFeatureSet(
            total_packets=total,
            valid_packets=valid,
            invalid_packets=invalid,
            sync_integrity=sync_integrity,
            unique_pid_count=3,
            pid_distribution={100: total - null_count, 8191: null_count},
            pid_percentages={100: ((total - null_count) / total) * 100.0, 8191: null_ratio * 100.0},
            pid_entropy=0.5,
            null_packet_count=null_count,
            null_packet_ratio=null_ratio,
            tei_error_count=tei_count,
            tei_error_rate=tei_rate,
            continuity_error_count=cc_count,
            continuity_error_rate=cc_rate,
            continuity_errors_by_pid={100: cc_count} if cc_count > 0 else {},
            adaptation_field_count=10,
            adaptation_field_ratio=0.01,
            adaptation_only_count=5,
            adaptation_and_payload_count=5,
            payload_packet_count=total - 5,
            payload_packet_ratio=(total - 5) / total,
            total_payload_bytes=184 * (total - 5),
            mean_payload_bytes_per_packet=180.0,
        )

    def test_health_classification_healthy(self):
        feats = self._create_features()
        report = self.analyzer.evaluate_features(feats)
        self.assertEqual(report.health_status, HealthClassification.HEALTHY)
        self.assertEqual(report.overall_score, 100.0)
        self.assertEqual(len(report.issues), 0)

    def test_health_classification_warning_on_cc(self):
        # 1 CC error in 1000 packets -> rate 0.001 (0.1%), exceeds warning 0.01% but below critical 0.5%
        feats = self._create_features(cc_count=1)
        report = self.analyzer.evaluate_features(feats)
        self.assertEqual(report.health_status, HealthClassification.WARNING)
        self.assertLess(report.overall_score, 100.0)
        self.assertTrue(any("Continuity counter error" in issue for issue in report.issues))

    def test_health_classification_warning_on_high_null(self):
        # 96% null packets -> exceeds warning threshold 95%
        feats = self._create_features(null_count=960)
        report = self.analyzer.evaluate_features(feats)
        self.assertEqual(report.health_status, HealthClassification.WARNING)
        self.assertTrue(any("Null packet ratio" in issue for issue in report.issues))

    def test_health_classification_critical_on_sync_loss(self):
        # Sync integrity drops to 92% (< 95% critical)
        feats = self._create_features(sync_integrity=92.0, invalid=80)
        report = self.analyzer.evaluate_features(feats)
        self.assertEqual(report.health_status, HealthClassification.CRITICAL)
        self.assertTrue(any("Sync integrity" in issue for issue in report.issues))

    def test_health_classification_critical_on_high_tei(self):
        # TEI count = 20 (2% > critical 1%)
        feats = self._create_features(tei_count=20)
        report = self.analyzer.evaluate_features(feats)
        self.assertEqual(report.health_status, HealthClassification.CRITICAL)
        self.assertTrue(any("TEI rate" in issue for issue in report.issues))

    def test_health_classification_critical_on_high_cc(self):
        # CC count = 10 (1% > critical 0.5%)
        feats = self._create_features(cc_count=10)
        report = self.analyzer.evaluate_features(feats)
        self.assertEqual(report.health_status, HealthClassification.CRITICAL)
        self.assertTrue(any("Continuity counter error" in issue for issue in report.issues))

    def test_health_classification_empty_input(self):
        feats = FeatureExtractor().extract_from_ts_stats(TSStreamStatistics())
        report = self.analyzer.evaluate_features(feats)
        self.assertEqual(report.health_status, HealthClassification.NO_DATA)
        self.assertEqual(report.overall_score, 0.0)
        self.assertEqual(report.packets_analyzed, 0)

    def test_health_classification_malformed_input(self):
        feats = self._create_features(invalid=15)
        report = self.analyzer.evaluate_features(feats)
        self.assertEqual(report.health_status, HealthClassification.CRITICAL)
        self.assertTrue(any("malformed" in issue.lower() for issue in report.issues))

    def test_deterministic_health_results(self):
        feats = self._create_features(cc_count=1, null_count=100)
        report1 = self.analyzer.evaluate_features(feats)
        report2 = self.analyzer.evaluate_features(feats)

        self.assertEqual(report1.health_status, report2.health_status)
        self.assertEqual(report1.overall_score, report2.overall_score)
        self.assertEqual(len(report1.issues), len(report2.issues))

    def test_configurable_thresholds(self):
        # Stricter thresholds: any null ratio > 5% triggers warning
        stricter = HealthThresholds(max_null_ratio_warning=0.05)
        strict_analyzer = HealthAnalyzer(thresholds=stricter)

        # 10% null packets
        feats = self._create_features(null_count=100)

        # Default analyzer should classify as HEALTHY (10% < 95%)
        self.assertEqual(self.analyzer.evaluate_features(feats).health_status, HealthClassification.HEALTHY)

        # Stricter analyzer should classify as WARNING (10% > 5%)
        self.assertEqual(strict_analyzer.evaluate_features(feats).health_status, HealthClassification.WARNING)


class TestF1RealDatasetIntegration(unittest.TestCase):
    """End-to-end integration tests using real satellite capture datasets."""

    def test_integration_f1_pipeline_dvbs2_toolkit(self):
        sample_path = RAW_DATA_DIR / "03_TS" / "DVBS2_toolkit" / "sample.ts"
        self.assertTrue(sample_path.exists())

        analyzer = HealthAnalyzer()
        report = analyzer.analyze_file(sample_path)

        self.assertIsInstance(report, StreamHealthReport)
        self.assertEqual(report.input_file, "sample.ts")
        self.assertEqual(report.detected_format, "MPEG_TS")
        self.assertEqual(report.packets_analyzed, 18176)
        self.assertEqual(report.features.total_packets, 18176)
        self.assertEqual(report.features.valid_packets, 18176)
        self.assertEqual(report.features.tei_error_count, 0)
        self.assertEqual(report.features.continuity_error_count, 0)
        self.assertEqual(report.health_status, HealthClassification.HEALTHY)
        self.assertEqual(report.overall_score, 100.0)

        # Verify formatted text contains required report keys
        text = report.format_text()
        self.assertIn("STREAM HEALTH ANALYSIS", text)
        self.assertIn("Total packets:", text)
        self.assertIn("Sync integrity:    100.0000%", text)

    def test_integration_f1_pipeline_blockstream(self):
        blockstream_path = RAW_DATA_DIR / "05_REAL_DVB_S2" / "GRCon22_Blockstream" / "blockstream.ts"
        self.assertTrue(blockstream_path.exists())

        analyzer = HealthAnalyzer()
        report = analyzer.analyze_file(blockstream_path)

        self.assertIsInstance(report, StreamHealthReport)
        self.assertEqual(report.input_file, "blockstream.ts")
        self.assertEqual(report.detected_format, "MPEG_TS")
        self.assertEqual(report.packets_analyzed, 22358)
        self.assertIn(32, report.features.pid_distribution)
        self.assertEqual(report.health_status, HealthClassification.HEALTHY)


if __name__ == "__main__":
    unittest.main()
