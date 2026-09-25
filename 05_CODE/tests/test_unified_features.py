"""
Unit and Integration Tests for Unified Multi-Format Feature Extraction Layer (PRJ_111).

Tests:
  - MPEG-TS statistics -> UnifiedStreamFeatureSet
  - GSE statistics -> UnifiedStreamFeatureSet
  - DVB-S2 BBFrame statistics -> UnifiedStreamFeatureSet
  - Format-specific metrics preservation and non-applicable fields explicitly None
  - Shannon entropy computation across distributions
  - Telemetry vector generation (to_vector) and flattened dict export (to_flat_dict)
  - Universal dispatcher auto-detection (extract_unified)
  - StreamHandler direct end-to-end extraction (extract_from_handler)
  - Real dataset verification across TS, GSE, and BBFrame
"""

import math
from pathlib import Path
import unittest

from dvbs2_analyzer.config import RAW_DATA_DIR, StreamFormat
from dvbs2_analyzer.features.extractor import (
    BBFrameSpecificMetrics,
    CommonMetrics,
    FeatureExtractor,
    GSESpecificMetrics,
    StreamFeatureSet,
    TSSpecificMetrics,
    UnifiedStreamFeatureSet,
)
from dvbs2_analyzer.ingestion.stream_handler import StreamHandler
from dvbs2_analyzer.parsers.bbframe_parser import BBFrameParser, BBFrameStreamStatistics
from dvbs2_analyzer.parsers.gse_parser import GSEParser, GSEStreamStatistics
from dvbs2_analyzer.parsers.ts_parser import TSParser, TSStreamStatistics


class TestUnifiedFeatureExtraction(unittest.TestCase):
    """Unit tests for multi-format feature extraction logic."""

    def setUp(self):
        self.extractor = FeatureExtractor()

    # -------------------------------------------------------------------------
    # 1. MPEG-TS Extraction
    # -------------------------------------------------------------------------
    def test_ts_to_unified_features(self):
        stats = TSStreamStatistics()
        stats.total_packets = 1000
        stats.valid_sync_packets = 998
        stats.sync_byte_errors = 2
        stats.tei_error_count = 1
        stats.null_packet_count = 150
        stats.payload_packet_count = 800
        stats.total_payload_bytes = 147200
        stats.pid_counts[100] = 500
        stats.pid_counts[200] = 350
        stats.pid_counts[8191] = 150
        stats.continuity_errors[100] = 3

        features = self.extractor.extract_unified_from_ts(stats, metadata={"source": "test_ts"})

        # Identity & Metadata
        self.assertEqual(features.format, StreamFormat.MPEG_TS)
        self.assertEqual(features.metadata.get("source"), "test_ts")

        # Common Metrics
        c = features.common
        self.assertEqual(c.total_units, 1000)
        self.assertEqual(c.valid_units, 998)
        self.assertEqual(c.invalid_units, 2)
        self.assertEqual(c.truncated_units, 0)
        self.assertAlmostEqual(c.integrity_ratio, 0.998, places=3)
        self.assertEqual(c.total_payload_bytes, 147200)
        self.assertAlmostEqual(c.mean_payload_bytes, 147.2, places=1)
        self.assertAlmostEqual(c.payload_ratio, 0.80, places=2)
        self.assertEqual(c.stream_type, "MPEG_TS_MULTIPLEX")
        self.assertEqual(c.unit_size_bytes_mean, 188.0)
        self.assertEqual(c.error_count, 6) # 2 sync + 1 tei + 3 cc
        self.assertGreater(c.entropy, 0.0)

        # Format-Specific: TS populated, GSE/BBFrame None
        self.assertIsNotNone(features.ts_specific)
        self.assertIsNone(features.gse_specific)
        self.assertIsNone(features.bbframe_specific)

        ts = features.ts_specific
        self.assertEqual(ts.unique_pid_count, 3)
        self.assertEqual(ts.null_packet_count, 150)
        self.assertAlmostEqual(ts.null_packet_ratio, 0.15, places=2)
        self.assertEqual(ts.tei_error_count, 1)
        self.assertEqual(ts.continuity_error_count, 3)

    # -------------------------------------------------------------------------
    # 2. GSE Extraction
    # -------------------------------------------------------------------------
    def test_gse_to_unified_features(self):
        stats = GSEStreamStatistics()
        stats.total_bytes_read = 50000
        stats.total_pdus = 100
        stats.valid_pdus = 95
        stats.malformed_pdus = 3
        stats.truncated_pdus = 2
        stats.padding_packets = 5
        stats.unfragmented_pdus = 80
        stats.first_fragments = 10
        stats.intermediate_fragments = 5
        stats.last_fragments = 5
        stats.total_payload_bytes = 38000
        stats.protocol_type_counts["IPv4 (0x0800)"] = 75
        stats.protocol_type_counts["IPv6 (0x86DD)"] = 25
        stats.encapsulated_protocols["IPv4"] = 75

        features = self.extractor.extract_unified_from_gse(stats)

        self.assertEqual(features.format, StreamFormat.GSE)

        # Common Metrics
        c = features.common
        self.assertEqual(c.total_units, 100)
        self.assertEqual(c.valid_units, 95)
        self.assertEqual(c.invalid_units, 3)
        self.assertEqual(c.truncated_units, 2)
        self.assertAlmostEqual(c.integrity_ratio, 0.95, places=2)
        self.assertEqual(c.total_payload_bytes, 38000)
        self.assertAlmostEqual(c.mean_payload_bytes, 38000 / 95, places=1)
        self.assertAlmostEqual(c.payload_ratio, 38000 / 50000, places=3)
        self.assertTrue(c.stream_type.startswith("GSE_"))
        self.assertEqual(c.error_count, 5) # 3 malformed + 2 truncated

        # Format-Specific: GSE populated, TS/BBFrame None
        self.assertIsNone(features.ts_specific)
        self.assertIsNotNone(features.gse_specific)
        self.assertIsNone(features.bbframe_specific)

        gse = features.gse_specific
        self.assertEqual(gse.total_pdus, 100)
        self.assertEqual(gse.unfragmented_pdus, 80)
        self.assertEqual(gse.fragmented_pdus_total, 20)
        self.assertAlmostEqual(gse.fragmentation_ratio, 0.20, places=2)
        self.assertGreater(gse.protocol_entropy, 0.0)

    # -------------------------------------------------------------------------
    # 3. DVB-S2 BBFrame Extraction
    # -------------------------------------------------------------------------
    def test_bbframe_to_unified_features(self):
        stats = BBFrameStreamStatistics()
        stats.total_bytes_read = 100000
        stats.total_frames = 50
        stats.valid_frames = 48
        stats.invalid_crc_frames = 1
        stats.malformed_headers = 1
        stats.truncated_frames = 2
        stats.total_payload_bytes = 90000
        stats.dfl_values = [14400, 14400, 14400] # 1800 bytes each
        stats.upl_values = [1504, 1504, 1504]
        stats.stream_type_counts["GENERIC_CONTINUOUS"] = 50
        stats.input_stream_mode_counts["SIS"] = 49
        stats.input_stream_mode_counts["MIS"] = 1
        stats.coding_modulation_counts["ACM"] = 50
        stats.roll_off_counts["alpha=0.35"] = 50
        stats.mode_adaptation_counts["L.3 (4B)"] = 50

        features = self.extractor.extract_unified_from_bbframe(stats)

        self.assertEqual(features.format, StreamFormat.BB_FRAME)

        # Common Metrics
        c = features.common
        self.assertEqual(c.total_units, 50)
        self.assertEqual(c.valid_units, 48)
        self.assertEqual(c.invalid_units, 2) # 1 CRC + 1 malformed
        self.assertEqual(c.truncated_units, 2)
        self.assertAlmostEqual(c.integrity_ratio, 48 / 50, places=3)
        self.assertEqual(c.total_payload_bytes, 90000)
        self.assertAlmostEqual(c.mean_payload_bytes, 90000 / 48, places=1)
        self.assertEqual(c.stream_type, "BBFRAME_GENERIC_CONTINUOUS")
        self.assertEqual(c.unit_size_bytes_mean, 1800.0)
        self.assertEqual(c.error_count, 4) # 1 crc + 1 malformed + 2 truncated

        # Format-Specific: BBFrame populated, TS/GSE None
        self.assertIsNone(features.ts_specific)
        self.assertIsNone(features.gse_specific)
        self.assertIsNotNone(features.bbframe_specific)

        bb = features.bbframe_specific
        self.assertEqual(bb.total_frames, 50)
        self.assertEqual(bb.invalid_crc_frames, 1)
        self.assertEqual(bb.crc_status, "CRC_ERRORS_DETECTED")
        self.assertEqual(bb.input_stream_modes["SIS"], 49)
        self.assertEqual(bb.coding_modulation_modes["ACM"], 50)

    # -------------------------------------------------------------------------
    # 4. Explicit Non-Applicable Fields (No Fabrication)
    # -------------------------------------------------------------------------
    def test_missing_not_applicable_metrics_explicit(self):
        # TS feature set should not fabricate GSE fragmentation or BBFrame MATYPE
        ts_stats = TSStreamStatistics()
        ts_stats.total_packets = 10
        ts_stats.valid_sync_packets = 10
        ts_feat = self.extractor.extract_unified_from_ts(ts_stats)

        self.assertIsNone(ts_feat.gse_specific)
        self.assertIsNone(ts_feat.bbframe_specific)
        ts_dict = ts_feat.to_dict()
        self.assertIsNone(ts_dict["gse_specific"])
        self.assertIsNone(ts_dict["bbframe_specific"])

        # GSE feature set should not fabricate TS PIDs or CC errors
        gse_stats = GSEStreamStatistics()
        gse_stats.total_pdus = 10
        gse_stats.valid_pdus = 10
        gse_feat = self.extractor.extract_unified_from_gse(gse_stats)

        self.assertIsNone(gse_feat.ts_specific)
        self.assertIsNone(gse_feat.bbframe_specific)

        # BBFrame feature set should not fabricate TS or GSE specific features
        bb_stats = BBFrameStreamStatistics()
        bb_stats.total_frames = 10
        bb_stats.valid_frames = 10
        bb_feat = self.extractor.extract_unified_from_bbframe(bb_stats)

        self.assertIsNone(bb_feat.ts_specific)
        self.assertIsNone(bb_feat.gse_specific)

    # -------------------------------------------------------------------------
    # 5. Shannon Entropy
    # -------------------------------------------------------------------------
    def test_entropy_calculation(self):
        # Uniform distribution with 4 equal classes -> log2(4) = 2.0 bits
        uniform = {"A": 25, "B": 25, "C": 25, "D": 25}
        self.assertAlmostEqual(FeatureExtractor.calculate_entropy(uniform), 2.0, places=3)

        # Single class -> 0.0 bits
        single = {"A": 100}
        self.assertEqual(FeatureExtractor.calculate_entropy(single), 0.0)

        # Empty -> 0.0 bits
        self.assertEqual(FeatureExtractor.calculate_entropy({}), 0.0)

    # -------------------------------------------------------------------------
    # 6. Serialization and ML Feature Vector (to_vector & to_flat_dict)
    # -------------------------------------------------------------------------
    def test_deterministic_feature_vectors(self):
        ts_stats = TSStreamStatistics()
        ts_stats.total_packets = 1000
        ts_stats.valid_sync_packets = 1000
        ts_stats.payload_packet_count = 900
        ts_stats.total_payload_bytes = 160000
        ts_stats.pid_counts[100] = 900
        ts_stats.pid_counts[8191] = 100

        feat = self.extractor.extract_unified_from_ts(ts_stats)
        vec = feat.to_vector()

        self.assertEqual(vec["is_ts"], 1.0)
        self.assertEqual(vec["is_gse"], 0.0)
        self.assertEqual(vec["is_bbframe"], 0.0)
        self.assertEqual(vec["integrity_ratio"], 1.0)
        self.assertEqual(vec["error_rate"], 0.0)
        self.assertAlmostEqual(vec["log_total_units"], 3.0, places=2)
        self.assertIn("ts_null_packet_ratio", vec)
        self.assertEqual(vec["gse_fragmentation_ratio"], 0.0)
        self.assertEqual(vec["bb_sis_ratio"], 0.0)

        flat = feat.to_flat_dict()
        self.assertEqual(flat["format"], "MPEG_TS")
        self.assertIn("common_total_units", flat)
        self.assertIn("ts_unique_pid_count", flat)

    # -------------------------------------------------------------------------
    # 7. Universal Dispatcher Auto-Detection
    # -------------------------------------------------------------------------
    def test_dispatcher_auto_detection(self):
        ts_stats = TSStreamStatistics()
        gse_stats = GSEStreamStatistics()
        bb_stats = BBFrameStreamStatistics()

        f_ts = self.extractor.extract_unified(ts_stats)
        self.assertEqual(f_ts.format, StreamFormat.MPEG_TS)

        f_gse = self.extractor.extract_unified(gse_stats)
        self.assertEqual(f_gse.format, StreamFormat.GSE)

        f_bb = self.extractor.extract_unified(bb_stats)
        self.assertEqual(f_bb.format, StreamFormat.BB_FRAME)

        with self.assertRaises(ValueError):
            self.extractor.extract_unified("invalid_object")


class TestUnifiedFeaturesRealDatasets(unittest.TestCase):
    """Integration tests validating feature extraction against real satellite captures."""

    def setUp(self):
        self.extractor = FeatureExtractor()

    def test_real_dataset_ts_unified(self):
        """Extracts unified features from 01_RAW_DATA/03_TS/DVBS2_toolkit/sample.ts."""
        sample_path = RAW_DATA_DIR / "03_TS" / "DVBS2_toolkit" / "sample.ts"
        self.assertTrue(sample_path.exists())

        handler = StreamHandler(sample_path, forced_format=StreamFormat.MPEG_TS)
        features = self.extractor.extract_from_handler(handler, max_units=1000)

        self.assertEqual(features.format, StreamFormat.MPEG_TS)
        self.assertEqual(features.common.total_units, 1000)
        self.assertEqual(features.common.valid_units, 1000)
        self.assertEqual(features.common.invalid_units, 0)
        self.assertEqual(features.common.integrity_ratio, 1.0)
        self.assertEqual(features.common.stream_type, "MPEG_TS_MULTIPLEX")
        self.assertEqual(features.common.unit_size_bytes_mean, 188.0)
        self.assertIsNotNone(features.ts_specific)
        self.assertGreater(features.ts_specific.unique_pid_count, 0)
        self.assertGreater(features.common.entropy, 0.0)

    def test_real_dataset_gse_unified(self):
        """Extracts unified features from 01_RAW_DATA/02_GSE/GSExtract/sample.ts."""
        sample_path = RAW_DATA_DIR / "02_GSE" / "GSExtract" / "sample.ts"
        self.assertTrue(sample_path.exists())

        handler = StreamHandler(sample_path, forced_format=StreamFormat.GSE)
        features = self.extractor.extract_from_handler(handler)

        self.assertEqual(features.format, StreamFormat.GSE)
        self.assertEqual(features.common.total_units, 14)
        self.assertEqual(features.common.valid_units, 14)
        self.assertEqual(features.common.invalid_units, 0)
        self.assertEqual(features.common.integrity_ratio, 1.0)
        self.assertIsNotNone(features.gse_specific)
        self.assertEqual(features.gse_specific.total_pdus, 14)
        self.assertEqual(features.gse_specific.unfragmented_pdus, 6)
        self.assertEqual(features.gse_specific.fragmented_pdus_total, 8)
        self.assertEqual(features.common.total_payload_bytes, 8764)

    def test_real_dataset_bbframe_unified(self):
        """Extracts unified features from 01_RAW_DATA/01_BBFRAME_GSE/dvb-s2_bb_example.pcap."""
        sample_path = RAW_DATA_DIR / "01_BBFRAME_GSE" / "dvb-s2_bb_example.pcap"
        self.assertTrue(sample_path.exists())

        handler = StreamHandler(sample_path, forced_format=StreamFormat.BB_FRAME)
        features = self.extractor.extract_from_handler(handler, max_units=500)

        self.assertEqual(features.format, StreamFormat.BB_FRAME)
        self.assertEqual(features.common.total_units, 500)
        self.assertEqual(features.common.valid_units, 500)
        self.assertEqual(features.common.invalid_units, 0)
        self.assertEqual(features.common.integrity_ratio, 1.0)
        self.assertEqual(features.common.stream_type, "BBFRAME_GENERIC_CONTINUOUS")
        self.assertIsNotNone(features.bbframe_specific)
        self.assertEqual(features.bbframe_specific.coding_modulation_modes["ACM"], 500)
        self.assertEqual(features.bbframe_specific.crc_status, "ALL_VALID")


if __name__ == "__main__":
    unittest.main()
