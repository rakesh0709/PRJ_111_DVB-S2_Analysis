"""
Foundation and Architecture Smoke Tests for PRJ_111.

Verifies package initialization, path configurations, stream format detection,
and baseline data structures across the modular layers.
"""

from pathlib import Path
import unittest

from dvbs2_analyzer import __project_id__, __version__
from dvbs2_analyzer.config import (
    DOCUMENTATION_DIR,
    FEATURE_DATA_DIR,
    MODELS_DIR,
    PROCESSED_DATA_DIR,
    PROJECT_ROOT,
    RAW_DATA_DIR,
    RESULTS_DIR,
    StreamFormat,
)
from dvbs2_analyzer.ingestion.stream_handler import (
    StreamHandler,
    detect_stream_format,
)
from dvbs2_analyzer.parsers.ts_parser import TSParser, TSStreamStatistics
from dvbs2_analyzer.preprocessing.sanitizer import (
    PreprocessingOptions,
    StreamSanitizer,
)
from dvbs2_analyzer.features.extractor import FeatureExtractor
from dvbs2_analyzer.analysis.health import HealthAnalyzer


class TestFoundation(unittest.TestCase):
    """Verifies foundational project scaffolding and directory paths."""

    def test_package_metadata(self):
        self.assertEqual(__project_id__, "PRJ_111")
        self.assertEqual(__version__, "0.1.0")

    def test_directory_paths_exist(self):
        self.assertTrue(PROJECT_ROOT.exists())
        self.assertTrue(RAW_DATA_DIR.exists())
        self.assertTrue(PROCESSED_DATA_DIR.exists())
        self.assertTrue(FEATURE_DATA_DIR.exists())
        self.assertTrue(MODELS_DIR.exists())
        self.assertTrue(RESULTS_DIR.exists())
        self.assertTrue(DOCUMENTATION_DIR.exists())

    def test_stream_format_detection_on_real_datasets(self):
        # 1. Baseband Frame PCAP
        bb_path = RAW_DATA_DIR / "01_BBFRAME_GSE" / "dvb-s2_bb_example.pcap"
        self.assertTrue(bb_path.exists(), f"Missing dataset: {bb_path}")
        self.assertEqual(detect_stream_format(bb_path), StreamFormat.BB_FRAME)

        # 2. MPEG-TS stream (DVBS2_toolkit)
        ts_path = RAW_DATA_DIR / "03_TS" / "DVBS2_toolkit" / "sample.ts"
        self.assertTrue(ts_path.exists(), f"Missing dataset: {ts_path}")
        self.assertEqual(detect_stream_format(ts_path), StreamFormat.MPEG_TS)

        # 3. GSE sample stream
        gse_path = RAW_DATA_DIR / "02_GSE" / "GSExtract" / "sample.ts"
        self.assertTrue(gse_path.exists(), f"Missing dataset: {gse_path}")
        self.assertEqual(detect_stream_format(gse_path), StreamFormat.GSE)

    def test_stream_handler_metadata(self):
        ts_path = RAW_DATA_DIR / "03_TS" / "DVBS2_toolkit" / "sample.ts"
        handler = StreamHandler(ts_path)
        info = handler.get_stream_info()

        self.assertEqual(info.detected_format, StreamFormat.MPEG_TS)
        self.assertTrue(info.is_valid)
        self.assertGreater(info.file_size_bytes, 0)
        self.assertIsInstance(handler.get_parser(), TSParser)

    def test_sanitizer_and_feature_pipeline(self):
        stats = TSStreamStatistics()
        stats.total_packets = 100
        stats.valid_sync_packets = 100
        stats.null_packet_count = 10
        stats.pid_counts[100] = 50
        stats.pid_counts[200] = 40
        stats.pid_counts[8191] = 10

        extractor = FeatureExtractor()
        features = extractor.extract_from_ts_stats(stats)
        self.assertEqual(features.total_packets, 100)
        self.assertAlmostEqual(features.null_packet_ratio, 0.1)
        self.assertGreater(features.pid_entropy, 0.0)

        health = HealthAnalyzer.evaluate_ts_health(stats)
        self.assertEqual(health.status, "EXCELLENT")
        self.assertEqual(health.overall_score, 100.0)


if __name__ == "__main__":
    unittest.main()
