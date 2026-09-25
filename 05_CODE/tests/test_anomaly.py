"""
Unit and Integration Tests for Feature F2: AI-Based Anomaly Detection (PRJ_111).

Tests:
  1. Model initialization and configuration
  2. Deterministic training and reproducibility (fixed random_state)
  3. Fitting baseline data and baseline distribution statistics calculation
  4. Normal sample prediction and scoring
  5. Anomaly prediction on out-of-distribution samples
  6. Normalized anomaly score generation [0.0, 1.0] and raw scores
  7. Batch prediction and AnomalyReport aggregation
  8. Empirical explanation generation and top deviation Z-score ranking
  9. Deterministic feature-order consistency across training and prediction
  10. Missing-value handling with graceful defaults
  11. Model persistence (save and load via joblib)
  12. MPEG-TS unified vector integration
  13. GSE unified vector integration
  14. DVB-S2 BBFrame unified vector integration
  15. Controlled in-memory synthetic perturbation detection (TEI bursts, sync slips, CRC errors)
  16. Insufficient training data handling (< 2 samples raises ValueError)
  17. Unfitted model prediction error handling (raises RuntimeError)
  18. MultiFormatAnomalyEngine routing and format isolation
"""

import math
from pathlib import Path
import tempfile
import unittest

from dvbs2_analyzer.analysis.anomaly import (
    AnomalyConfig,
    AnomalyDetector,
    AnomalyReport,
    AnomalyResult,
    FeatureDeviation,
    MultiFormatAnomalyEngine,
    create_perturbed_bbframe_vector,
    create_perturbed_gse_vector,
    create_perturbed_ts_vector,
)
from dvbs2_analyzer.config import StreamFormat
from dvbs2_analyzer.features.extractor import (
    CommonMetrics,
    FeatureExtractor,
    TSSpecificMetrics,
    UnifiedStreamFeatureSet,
)


def make_synthetic_ts_features(
    integrity: float = 1.0,
    null_ratio: float = 0.15,
    tei_rate: float = 0.0,
    cc_rate: float = 0.0,
    payload_bytes: int = 150000,
) -> UnifiedStreamFeatureSet:
    """Helper to synthesize unified feature sets representing TS telemetry windows."""
    c = CommonMetrics(
        total_units=1000,
        valid_units=int(1000 * integrity),
        invalid_units=int(1000 * (1.0 - integrity)),
        truncated_units=0,
        integrity_ratio=integrity,
        total_payload_bytes=payload_bytes,
        mean_payload_bytes=payload_bytes / 1000.0,
        payload_ratio=0.85,
        stream_type="MPEG_TS_MULTIPLEX",
        unit_size_bytes_min=188,
        unit_size_bytes_max=188,
        unit_size_bytes_mean=188.0,
        error_count=int(1000 * (1.0 - integrity) + 1000 * tei_rate + 1000 * cc_rate),
        error_rate=(1.0 - integrity) + tei_rate + cc_rate,
        entropy=1.25,
    )
    ts = TSSpecificMetrics(
        unique_pid_count=4,
        pid_distribution={100: 400, 200: 300, 300: 150, 8191: int(1000 * null_ratio)},
        pid_percentages={100: 40.0, 200: 300.0, 300: 15.0, 8191: null_ratio * 100.0},
        pid_entropy=1.25,
        null_packet_count=int(1000 * null_ratio),
        null_packet_ratio=null_ratio,
        tei_error_count=int(1000 * tei_rate),
        tei_error_rate=tei_rate,
        continuity_error_count=int(1000 * cc_rate),
        continuity_error_rate=cc_rate,
        continuity_errors_by_pid={},
        adaptation_field_count=50,
        adaptation_field_ratio=0.05,
        adaptation_only_count=10,
        adaptation_and_payload_count=40,
        payload_packet_count=850,
        payload_packet_ratio=0.85,
        scrambled_packet_count=None,
    )
    return UnifiedStreamFeatureSet(
        format=StreamFormat.MPEG_TS,
        common=c,
        ts_specific=ts,
        metadata={"window_size": 1000},
    )


class TestAnomalyDetection(unittest.TestCase):
    """Unit test suite for Feature F2 Anomaly Detection."""

    def setUp(self):
        self.config = AnomalyConfig(
            model_type="isolation_forest",
            contamination=0.05,
            n_estimators=50,
            random_state=42,
            format=StreamFormat.MPEG_TS,
        )
        self.detector = AnomalyDetector(self.config)

        # Generate a small population of normal baseline samples
        self.baseline_samples = [
            make_synthetic_ts_features(
                integrity=1.0,
                null_ratio=0.15 + (i * 0.005),
                tei_rate=0.0,
                cc_rate=0.0,
                payload_bytes=150000 + (i * 500)
            )
            for i in range(25)
        ]

    # -------------------------------------------------------------------------
    # 1. Model Initialization
    # -------------------------------------------------------------------------
    def test_model_initialization(self):
        self.assertFalse(self.detector.is_fitted)
        self.assertEqual(self.detector.contamination, 0.05)
        self.assertEqual(self.detector.random_state, 42)
        self.assertEqual(self.detector.model_type, "isolation_forest")

    # -------------------------------------------------------------------------
    # 2. Deterministic Training
    # -------------------------------------------------------------------------
    def test_deterministic_training(self):
        d1 = AnomalyDetector(AnomalyConfig(random_state=123, format=StreamFormat.MPEG_TS))
        d1.fit(self.baseline_samples)
        res1 = d1.predict_sample(self.baseline_samples[0])

        d2 = AnomalyDetector(AnomalyConfig(random_state=123, format=StreamFormat.MPEG_TS))
        d2.fit(self.baseline_samples)
        res2 = d2.predict_sample(self.baseline_samples[0])

        self.assertEqual(res1.is_anomaly, res2.is_anomaly)
        self.assertAlmostEqual(res1.anomaly_score, res2.anomaly_score, places=5)
        self.assertAlmostEqual(res1.raw_score, res2.raw_score, places=5)

    # -------------------------------------------------------------------------
    # 3. Fitting Baseline Data & Distributions
    # -------------------------------------------------------------------------
    def test_fitting_baseline_data(self):
        self.detector.fit(self.baseline_samples)
        self.assertTrue(self.detector.is_fitted)
        self.assertEqual(self.detector.training_sample_count, 25)
        self.assertIn("null_packet_ratio", self.detector.baseline_means)
        self.assertGreater(self.detector.baseline_means["null_packet_ratio"], 0.10)
        self.assertGreaterEqual(self.detector.baseline_stds["null_packet_ratio"], 0.0)

    # -------------------------------------------------------------------------
    # 4. Normal Prediction
    # -------------------------------------------------------------------------
    def test_normal_prediction(self):
        self.detector.fit(self.baseline_samples)
        normal_sample = self.baseline_samples[10]
        res = self.detector.predict_sample(normal_sample)

        self.assertFalse(res.is_anomaly)
        self.assertEqual(res.severity, "NORMAL")
        self.assertLess(res.anomaly_score, 0.50)

    # -------------------------------------------------------------------------
    # 5 & 6. Anomaly Prediction and Score Normalization
    # -------------------------------------------------------------------------
    def test_anomaly_prediction_and_scoring(self):
        self.detector.fit(self.baseline_samples)
        # Extreme anomaly: TEI error rate = 25%, integrity down to 70%
        anomalous_sample = make_synthetic_ts_features(
            integrity=0.70,
            tei_rate=0.25,
            cc_rate=0.10,
            null_ratio=0.80
        )
        res = self.detector.predict_sample(anomalous_sample)

        self.assertTrue(res.is_anomaly)
        self.assertIn(res.severity, ("MEDIUM", "HIGH", "CRITICAL"))
        self.assertGreater(res.anomaly_score, 0.50)
        self.assertIsInstance(res.raw_score, float)

    # -------------------------------------------------------------------------
    # 7. Batch Prediction
    # -------------------------------------------------------------------------
    def test_batch_prediction(self):
        self.detector.fit(self.baseline_samples)
        batch = [
            self.baseline_samples[8],
            self.baseline_samples[12],
            make_synthetic_ts_features(tei_rate=0.30), # anomaly
        ]
        report = self.detector.predict_batch(batch, dataset_name="Test Batch")

        self.assertEqual(report.total_samples, 3)
        self.assertEqual(report.anomaly_count, 1)
        self.assertEqual(report.normal_count, 2)
        self.assertAlmostEqual(report.anomaly_ratio, 1.0 / 3.0, places=2)
        summary_str = report.summary()
        self.assertIn("Test Batch", summary_str)
        self.assertIn("FLAG-TRIGGERED ANOMALIES", summary_str)

    # -------------------------------------------------------------------------
    # 8. Explanation Generation & Z-Scores
    # -------------------------------------------------------------------------
    def test_explanation_generation(self):
        self.detector.fit(self.baseline_samples)
        # Anomaly with high TEI errors
        bad_sample = make_synthetic_ts_features(tei_rate=0.20)
        res = self.detector.predict_sample(bad_sample)

        self.assertGreater(len(res.top_deviations), 0)
        # Verify Z-scores are ranked descending
        for i in range(len(res.top_deviations) - 1):
            self.assertGreaterEqual(
                res.top_deviations[i].z_score,
                res.top_deviations[i + 1].z_score
            )
        # TEI should be among top deviating features
        top_names = [d.feature_name for d in res.top_deviations[:3]]
        self.assertTrue(any("tei" in n or "error" in n for n in top_names))
        self.assertIn("Elevated anomaly score driven by", res.summary_explanation)

    # -------------------------------------------------------------------------
    # 9. Deterministic Feature Order
    # -------------------------------------------------------------------------
    def test_feature_order_consistency(self):
        self.detector.fit(self.baseline_samples)
        order1 = list(self.detector.feature_names)

        # Pass a dict with permuted key order
        permuted_dict = {k: 0.1 for k in reversed(order1)}
        res = self.detector.predict_sample(permuted_dict)
        self.assertIsInstance(res.anomaly_score, float)
        self.assertEqual(self.detector.feature_names, order1)

    # -------------------------------------------------------------------------
    # 10. Missing-Value Handling
    # -------------------------------------------------------------------------
    def test_missing_value_handling(self):
        self.detector.fit(self.baseline_samples)
        # Dictionary missing half the features
        sparse_dict = {"integrity_ratio": 1.0, "null_packet_ratio": 0.15}
        res = self.detector.predict_sample(sparse_dict)
        self.assertIsInstance(res.is_anomaly, bool)

    # -------------------------------------------------------------------------
    # 11. Model Persistence (Save & Load)
    # -------------------------------------------------------------------------
    def test_model_save_and_load(self):
        self.detector.fit(self.baseline_samples)
        test_sample = self.baseline_samples[5]
        expected_res = self.detector.predict_sample(test_sample)

        with tempfile.TemporaryDirectory() as tmpdir:
            model_path = Path(tmpdir) / "anomaly_model.joblib"
            self.detector.save(model_path)
            self.assertTrue(model_path.exists())

            loaded_detector = AnomalyDetector.load(model_path)
            self.assertTrue(loaded_detector.is_fitted)
            self.assertEqual(loaded_detector.feature_names, self.detector.feature_names)

            loaded_res = loaded_detector.predict_sample(test_sample)
            self.assertEqual(expected_res.is_anomaly, loaded_res.is_anomaly)
            self.assertAlmostEqual(expected_res.anomaly_score, loaded_res.anomaly_score, places=5)

    # -------------------------------------------------------------------------
    # 12, 13, 14. Multi-Format Support (TS, GSE, BBFrame)
    # -------------------------------------------------------------------------
    def test_gse_vector_integration(self):
        gse_detector = AnomalyDetector(AnomalyConfig(format=StreamFormat.GSE, random_state=42))
        # Build synthetic GSE samples
        samples = []
        for i in range(15):
            c = CommonMetrics(
                total_units=50, valid_units=50, invalid_units=0, truncated_units=0,
                integrity_ratio=1.0, total_payload_bytes=25000, mean_payload_bytes=500.0,
                payload_ratio=0.90, stream_type="GSE_IPV4", unit_size_bytes_min=100,
                unit_size_bytes_max=1500, unit_size_bytes_mean=500.0, error_count=0,
                error_rate=0.0, entropy=0.0
            )
            feat = UnifiedStreamFeatureSet(format=StreamFormat.GSE, common=c)
            samples.append(feat)

        gse_detector.fit(samples)
        self.assertTrue(gse_detector.is_fitted)
        res = gse_detector.predict_sample(samples[0])
        self.assertFalse(res.is_anomaly)

    def test_bbframe_vector_integration(self):
        bb_detector = AnomalyDetector(AnomalyConfig(format=StreamFormat.BB_FRAME, random_state=42))
        samples = []
        for i in range(15):
            c = CommonMetrics(
                total_units=100, valid_units=100, invalid_units=0, truncated_units=0,
                integrity_ratio=1.0, total_payload_bytes=80000, mean_payload_bytes=800.0,
                payload_ratio=0.80, stream_type="BBFRAME_GENERIC_CONTINUOUS", unit_size_bytes_min=100,
                unit_size_bytes_max=1200, unit_size_bytes_mean=800.0, error_count=0,
                error_rate=0.0, entropy=0.0
            )
            feat = UnifiedStreamFeatureSet(format=StreamFormat.BB_FRAME, common=c)
            samples.append(feat)

        bb_detector.fit(samples)
        self.assertTrue(bb_detector.is_fitted)
        res = bb_detector.predict_sample(samples[0])
        self.assertFalse(res.is_anomaly)

    # -------------------------------------------------------------------------
    # 15. Controlled In-Memory Perturbation Detection
    # -------------------------------------------------------------------------
    def test_controlled_perturbation_detection(self):
        self.detector.fit(self.baseline_samples)
        baseline_vec = self.baseline_samples[0].to_format_vector(StreamFormat.MPEG_TS)

        # 1. TEI burst perturbation
        tei_perturbed = create_perturbed_ts_vector(baseline_vec, tei_burst=True)
        res_tei = self.detector.predict_sample(tei_perturbed)
        self.assertTrue(res_tei.is_anomaly)
        top_dev_names = [d.feature_name for d in res_tei.top_deviations[:3]]
        self.assertIn("tei_error_rate", top_dev_names)

        # 2. Sync loss perturbation
        sync_perturbed = create_perturbed_ts_vector(baseline_vec, sync_loss=True)
        res_sync = self.detector.predict_sample(sync_perturbed)
        self.assertTrue(res_sync.is_anomaly)
        dev_names = [d.feature_name for d in res_sync.top_deviations[:2]]
        self.assertTrue("integrity_ratio" in dev_names or "error_rate" in dev_names)

    # -------------------------------------------------------------------------
    # 16 & 17. Error Handling (Insufficient data & unfitted model)
    # -------------------------------------------------------------------------
    def test_insufficient_training_data(self):
        with self.assertRaises(ValueError):
            self.detector.fit([self.baseline_samples[0]]) # Only 1 sample

    def test_unfitted_model_error(self):
        unfitted = AnomalyDetector()
        with self.assertRaises(RuntimeError):
            unfitted.predict_sample({"null_packet_ratio": 0.15})

    # -------------------------------------------------------------------------
    # 18. MultiFormatAnomalyEngine Routing
    # -------------------------------------------------------------------------
    def test_multi_format_engine(self):
        engine = MultiFormatAnomalyEngine(random_state=42)
        engine.fit_format(StreamFormat.MPEG_TS, self.baseline_samples)
        self.assertTrue(engine.ts_detector.is_fitted)
        self.assertFalse(engine.gse_detector.is_fitted)

        # Route sample through engine
        res = engine.predict(self.baseline_samples[10])
        self.assertEqual(res.format, "MPEG_TS")
        self.assertFalse(res.is_anomaly)

    # -------------------------------------------------------------------------
    # 19. Invariant Baseline Explanation Bounding (No Absurd Z-Scores)
    # -------------------------------------------------------------------------
    def test_invariant_baseline_explanation_bounded(self):
        """Verifies that features with zero baseline std yield bounded, human-readable explanations."""
        self.detector.fit(self.baseline_samples)
        # tei_error_rate is constant 0.0 in baseline_samples (std == 0.0)
        perturbed = make_synthetic_ts_features(tei_rate=0.15)
        res = self.detector.predict_sample(perturbed)

        self.assertTrue(res.is_anomaly)
        for dev in res.top_deviations:
            # Must not have absurd division-by-epsilon numbers
            self.assertLessEqual(dev.z_score, 20.0)
            self.assertGreaterEqual(dev.z_score, 0.0)

        self.assertIn("tei", res.summary_explanation.lower())
        self.assertNotIn("150000", res.summary_explanation)
        self.assertIn("shift from baseline", res.summary_explanation)

    # -------------------------------------------------------------------------
    # 20. Anomaly Threshold Configurability & Score Calibration
    # -------------------------------------------------------------------------
    def test_anomaly_threshold_configurability_and_calibration(self):
        """Verifies that predict_sample directly respects custom configured anomaly thresholds."""
        # Fit baseline detector
        d_default = AnomalyDetector(AnomalyConfig(
            format=StreamFormat.MPEG_TS,
            anomaly_threshold=0.50,
            contamination=0.05,
            random_state=42,
        ))
        d_default.fit(self.baseline_samples)

        # Baseline sample should have score < 0.50
        res_norm = d_default.predict_sample(self.baseline_samples[10])
        self.assertFalse(res_norm.is_anomaly)
        self.assertLess(res_norm.anomaly_score, 0.50)

        # High threshold detector (0.80)
        d_high = AnomalyDetector(AnomalyConfig(
            format=StreamFormat.MPEG_TS,
            anomaly_threshold=0.80,
            contamination=0.05,
            random_state=42,
        ))
        d_high.fit(self.baseline_samples)
        self.assertEqual(d_high.anomaly_threshold, 0.80)

        # Mildly perturbed sample (e.g. slight change that produces score ~0.52 without severe >3 sigma)
        mild_sample = make_synthetic_ts_features(
            null_ratio=0.10,
            payload_bytes=150000
        )
        res_high = d_high.predict_sample(mild_sample)
        # If score is below 0.80 and no severe deviations, should not be flagged as anomaly
        if res_high.anomaly_score < 0.80 and not any(d.z_score >= 3.0 for d in res_high.top_deviations):
            self.assertFalse(res_high.is_anomaly)


if __name__ == "__main__":
    unittest.main()
