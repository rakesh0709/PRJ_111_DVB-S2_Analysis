"""
PRJ_111: Chunk 4 Robustness and Regression Test Suite.

Focus Areas:
1. Empty and truncated input files across all three formats.
2. Corrupted MPEG-TS sync bytes and re-synchronization edge cases.
3. Malformed and truncated GSE PDUs.
4. Invalid, corrupt, and truncated BBFrame / PCAP inputs.
5. Random binary inputs and unsupported format handling.
6. Incorrect file extensions and format sniffing edge cases.
7. Repeated analysis, state isolation, and switching between formats.
8. API and Coordinator error handling for malformed/corrupted inputs.
9. Preservation of existing analytical results on valid reference datasets.
"""

import io
from pathlib import Path
import tempfile
import unittest

from dvbs2_analyzer.config import (
    RAW_DATA_DIR,
    StreamFormat,
    TS_PACKET_SIZE,
    TS_SYNC_BYTE,
)
from dvbs2_analyzer.frontend.coordinator import AnalysisCoordinator
from dvbs2_analyzer.ingestion.stream_handler import (
    StreamHandler,
    detect_stream_format,
)
from dvbs2_analyzer.parsers.base import (
    PacketCorruptionError,
    StreamParserError,
    SyncLossError,
)
from dvbs2_analyzer.parsers.bbframe_parser import BBFrameParser, crc8_dvbs2
from dvbs2_analyzer.parsers.gse_parser import GSEParser
from dvbs2_analyzer.parsers.ts_parser import TSParser


class TestChunk4Robustness(unittest.TestCase):
    """Automated tests for Chunk 4 robustness, edge cases, and regression."""

    @classmethod
    def setUpClass(cls):
        cls.raw_ts = RAW_DATA_DIR / "03_TS" / "DVBS2_toolkit" / "sample.ts"
        cls.raw_gse = RAW_DATA_DIR / "02_GSE" / "GSExtract" / "sample.ts"
        cls.raw_bb = RAW_DATA_DIR / "01_BBFRAME_GSE" / "dvb-s2_bb_example.pcap"
        cls.coordinator = AnalysisCoordinator()

    # -------------------------------------------------------------------------
    # 1. Empty and Truncated Inputs
    # -------------------------------------------------------------------------

    def test_empty_file_handling(self):
        """Confirms that an empty 0-byte file is handled safely across all layers."""
        with tempfile.NamedTemporaryFile(suffix=".ts", delete=False) as tf:
            empty_path = Path(tf.name)

        try:
            # 1. Format sniffing
            detected = detect_stream_format(empty_path)
            self.assertEqual(detected, StreamFormat.UNKNOWN)

            # 2. StreamHandler
            handler = StreamHandler(empty_path)
            info = handler.get_stream_info()
            self.assertEqual(info.file_size_bytes, 0)
            self.assertFalse(info.is_valid)

            # 3. TSParser directly on empty bytes
            p_ts = TSParser()
            pkts_ts = list(p_ts.parse_chunk(b"", is_last=True))
            self.assertEqual(len(pkts_ts), 0)
            self.assertEqual(p_ts.stats.total_packets, 0)

            # 4. GSEParser directly on empty bytes
            p_gse = GSEParser()
            pdus_gse = list(p_gse.parse_chunk(b"", is_last=True))
            self.assertEqual(len(pdus_gse), 0)

            # 5. BBFrameParser directly on empty bytes
            p_bb = BBFrameParser()
            frames_bb = list(p_bb.parse_chunk(b"", is_last=True))
            self.assertEqual(len(frames_bb), 0)

            # 6. Coordinator analysis fails gracefully without crash
            with self.assertRaises(ValueError):
                self.coordinator.analyze_stream(empty_path)
        finally:
            empty_path.unlink(missing_ok=True)

    def test_truncated_header_inputs(self):
        """Tests truncated inputs shorter than minimum framing headers (1 to 9 bytes)."""
        for n_bytes in [1, 3, 4, 9]:
            data = b"\x47\x01\x02\x10\x00\x00\x00\x00\x00"[:n_bytes]
            # TS Parser: minimum is 188 bytes
            p_ts = TSParser()
            pkts = list(p_ts.parse_chunk(data, is_last=True))
            self.assertEqual(len(pkts), 0)
            self.assertEqual(p_ts.stats.total_packets, 0)

            # BBFrame Parser: minimum header is 10 bytes
            p_bb = BBFrameParser()
            frames = list(p_bb.parse_chunk(data, is_last=True))
            self.assertEqual(len(frames), 0)

            # GSE Parser: minimum header is 2 bytes
            p_gse = GSEParser()
            pdus = list(p_gse.parse_chunk(data, is_last=True))
            self.assertEqual(len(pdus), 0)

    # -------------------------------------------------------------------------
    # 2. Corrupted MPEG-TS Sync Bytes and Re-synchronization
    # -------------------------------------------------------------------------

    def test_ts_corrupted_sync_resync_and_strict_mode(self):
        """Verifies TSParser error recovery when sync byte 0x47 is corrupted or lost."""
        valid_pkt = b"\x47\x01\x00\x10" + b"\x00" * 184
        corrupted_sync_pkt = b"\x00\x01\x00\x10" + b"\x00" * 184  # Bad sync byte 0x00

        stream_bytes = valid_pkt + corrupted_sync_pkt + valid_pkt

        # Non-strict mode: skips corrupt sync, finds next 0x47, records error
        p_normal = TSParser(strict_mode=False)
        pkts = list(p_normal.parse_chunk(stream_bytes, is_last=True))
        self.assertEqual(len(pkts), 2)
        self.assertGreater(p_normal.stats.sync_byte_errors, 0)

        # Strict mode: must raise SyncLossError on corrupt sync
        p_strict = TSParser(strict_mode=True)
        with self.assertRaises(SyncLossError):
            list(p_strict.parse_chunk(stream_bytes, is_last=True))

    def test_ts_consecutive_sync_loss_garbage(self):
        """Tests that pure garbage binary with occasional random 0x47 does not crash TSParser."""
        garbage = b"\xAA" * 500 + b"\x47\xFF\xFF" + b"\xBB" * 497
        p = TSParser(strict_mode=False)
        pkts = list(p.parse_chunk(garbage, is_last=True))
        self.assertEqual(len(pkts), 0)
        self.assertGreater(p.stats.sync_byte_errors, 0)

    # -------------------------------------------------------------------------
    # 3. Malformed and Truncated GSE PDUs
    # -------------------------------------------------------------------------

    def test_gse_malformed_length_field(self):
        """Verifies GSEParser handling of PDUs claiming impossible length fields."""
        malformed_pdu_hdr = b"\x8F\xFF\x08\x00" + b"\x11" * 10  # Only 14 bytes provided
        p_gse = GSEParser(strict_mode=False)
        pdus = list(p_gse.parse_chunk(malformed_pdu_hdr, is_last=True))
        self.assertEqual(len(pdus), 0)

    def test_gse_padding_handling(self):
        """Verifies GSEParser handles GSE Padding packets according to ETSI TS 102 606-1."""
        zero_padding = b"\x00" * 20
        p_gse = GSEParser(strict_mode=False)
        pdus = list(p_gse.parse_chunk(zero_padding, is_last=True))
        for p in pdus:
            self.assertTrue(p.is_padding)

    # -------------------------------------------------------------------------
    # 4. Invalid or Truncated BBFrame / PCAP Input
    # -------------------------------------------------------------------------

    def test_bbframe_truncated_pcapng_header(self):
        """Tests PCAP-NG input with truncated Section Header Block or partial packet block."""
        pcapng_truncated = b"\x0a\x0d\x0d\x0a\x1c\x00\x00\x00\x4d\x3c\x2b\x1a"
        p_bb = BBFrameParser(strict_mode=False)
        frames = list(p_bb.parse_chunk(pcapng_truncated, is_last=True))
        self.assertEqual(len(frames), 0)

    def test_bbframe_corrupted_crc8_in_raw_stream(self):
        """Tests raw BBFrame input where CRC-8 fails validation in parse_frame."""
        # 10 bytes with all zeros: crc8 of b"\x00"*9 is 0x00.
        # Intentionally corrupt byte 9 to 0xFF so CRC mismatch occurs
        raw_bad_crc = b"\x00" * 9 + b"\xFF" + b"\x00" * 50
        p_bb_strict = BBFrameParser(strict_mode=True)
        with self.assertRaises(PacketCorruptionError):
            p_bb_strict.parse_frame(raw_bad_crc)

    # -------------------------------------------------------------------------
    # 5. Random Binary Inputs and Unsupported Formats
    # -------------------------------------------------------------------------

    def test_random_binary_input_detection(self):
        """Confirms that arbitrary random binary data is detected as UNKNOWN."""
        random_bytes = bytes((i * 37 + 13) % 256 for i in range(2048))
        with tempfile.NamedTemporaryFile(suffix=".bin", delete=False) as tf:
            tf.write(random_bytes)
            random_path = Path(tf.name)

        try:
            fmt = detect_stream_format(random_path)
            self.assertEqual(fmt, StreamFormat.UNKNOWN)

            handler = StreamHandler(random_path)
            self.assertEqual(handler.format, StreamFormat.UNKNOWN)
            with self.assertRaises(ValueError):
                handler.get_parser()
        finally:
            random_path.unlink(missing_ok=True)

    # -------------------------------------------------------------------------
    # 6. Incorrect File Extensions & Content-Based Sniffing
    # -------------------------------------------------------------------------

    def test_misnamed_extension_format_sniffing(self):
        """
        Verifies content-based format detection when file extensions are misleading:
        - MPEG-TS file renamed with .pcap extension
        """
        with open(self.raw_ts, "rb") as f:
            ts_head = f.read(TS_PACKET_SIZE * 8)

        with tempfile.NamedTemporaryFile(suffix=".pcap", delete=False) as tf:
            tf.write(ts_head)
            misnamed_ts = Path(tf.name)

        try:
            detected = detect_stream_format(misnamed_ts)
            self.assertEqual(detected, StreamFormat.MPEG_TS)
        finally:
            misnamed_ts.unlink(missing_ok=True)

    # -------------------------------------------------------------------------
    # 7. Repeated Analysis & Parser State Isolation (Zero State Leakage)
    # -------------------------------------------------------------------------

    def test_repeated_analysis_and_format_switching(self):
        """
        Executes sequential analysis across different formats on the same AnalysisCoordinator
        instance to ensure complete state isolation and zero cross-stream contamination.
        """
        # Run 1: MPEG-TS
        res_ts1 = self.coordinator.analyze_stream(self.raw_ts, forced_format="MPEG_TS", window_size=200)
        self.assertTrue(res_ts1["success"])
        self.assertEqual(res_ts1["stream_info"]["total_units"], 18176)

        # Run 2: GSE
        res_gse = self.coordinator.analyze_stream(self.raw_gse, forced_format="GSE", window_size=3)
        self.assertTrue(res_gse["success"])
        self.assertEqual(res_gse["stream_info"]["total_units"], 14)

        # Run 3: BBFrame
        res_bb = self.coordinator.analyze_stream(self.raw_bb, forced_format="BB_FRAME", window_size=50)
        self.assertTrue(res_bb["success"])
        self.assertEqual(res_bb["stream_info"]["total_units"], 4309)

        # Run 4: MPEG-TS again (must match Run 1 exactly)
        res_ts2 = self.coordinator.analyze_stream(self.raw_ts, forced_format="MPEG_TS", window_size=200)
        self.assertTrue(res_ts2["success"])
        self.assertEqual(res_ts2["stream_info"]["total_units"], 18176)
        self.assertEqual(
            res_ts1["f1_health"]["overall_health_score"],
            res_ts2["f1_health"]["overall_health_score"],
        )
        self.assertEqual(
            res_ts1["f2_anomalies"]["anomaly_window_count"],
            res_ts2["f2_anomalies"]["anomaly_window_count"],
        )
        self.assertEqual(
            res_ts1["f3_patterns"]["dominant_component"],
            res_ts2["f3_patterns"]["dominant_component"],
        )

    # -------------------------------------------------------------------------
    # 8. Analytical Equivalence Invariance Check
    # -------------------------------------------------------------------------

    def test_analytical_parity_reference_datasets(self):
        """Confirms that baseline analytical outputs on reference datasets remain bit-for-bit invariant."""
        # MPEG-TS
        res_ts = self.coordinator.analyze_stream(self.raw_ts, forced_format="MPEG_TS", window_size=200)
        self.assertEqual(res_ts["f1_health"]["overall_health_score"], 100.0)
        self.assertEqual(res_ts["f2_anomalies"]["anomaly_window_count"], 5)
        self.assertIn("PID 256", res_ts["f3_patterns"]["dominant_component"])

        # BBFrame
        res_bb = self.coordinator.analyze_stream(self.raw_bb, forced_format="BB_FRAME", window_size=50)
        self.assertEqual(res_bb["f1_health"]["overall_health_score"], 100.0)
        self.assertEqual(res_bb["f2_anomalies"]["anomaly_window_count"], 5)

        # GSE
        res_gse = self.coordinator.analyze_stream(self.raw_gse, forced_format="GSE", window_size=3)
        self.assertEqual(res_gse["f1_health"]["overall_health_score"], 100.0)
        self.assertEqual(res_gse["f2_anomalies"]["anomaly_window_count"], 1)


if __name__ == "__main__":
    unittest.main()
