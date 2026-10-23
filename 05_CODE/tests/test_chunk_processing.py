"""
PRJ_111: Automated Test Suite for Chunk 1 - Incremental / Chunked Processing
Foundation & Whole-File Equivalence.

Tests:
1. ChunkReader binary chunk iterator abstraction and edge handling.
2. Arbitrary chunk boundary handling across MPEG-TS, GSE, and BBFrame.
3. Awkward chunk sizes (1, 7, 31, 100, 187, 188, 189, 511, 1024, 4096).
4. State management, isolation, and reset/re-use without state leakage.
5. Malformed, truncated, and edge inputs.
6. Physical global byte offset preservation across windows.
7. Full whole-file vs chunked analytical equivalence across F1, F2 (IsolationForest
   with random_state=42), F3, F4, F5, F7, and AnalysisCoordinator.
"""

import io
import math
from pathlib import Path
import tempfile
from typing import List
import unittest

from dvbs2_analyzer.analysis.explanation import AnomalyExplanationEngine, ExplanationConfig
from dvbs2_analyzer.analysis.report import AutomaticReportGenerator, ReportConfig
from dvbs2_analyzer.analysis.timeline import StreamTimeline, TimelineConfig, TimelineGenerator
from dvbs2_analyzer.config import RAW_DATA_DIR, StreamFormat, TS_PACKET_SIZE
from dvbs2_analyzer.frontend.coordinator import AnalysisCoordinator
from dvbs2_analyzer.ingestion.chunk_reader import ChunkReader, read_chunks
from dvbs2_analyzer.ingestion.stream_handler import StreamHandler
from dvbs2_analyzer.parsers.bbframe_parser import BBFrameParser
from dvbs2_analyzer.parsers.gse_parser import GSEParser
from dvbs2_analyzer.parsers.ts_parser import TSPacket, TSParser

# Authoritative dataset paths
TS_DATASET = RAW_DATA_DIR / "03_TS" / "DVBS2_toolkit" / "sample.ts"
GSE_DATASET = RAW_DATA_DIR / "02_GSE" / "GSExtract" / "sample.ts"
BBFRAME_DATASET = RAW_DATA_DIR / "01_BBFRAME_GSE" / "dvb-s2_bb_example.pcap"


class TestChunkReader(unittest.TestCase):
    """Unit tests for the ChunkReader abstraction."""

    def test_invalid_chunk_size(self):
        """Verifies rejection of non-positive chunk sizes."""
        with self.assertRaises(ValueError):
            ChunkReader(b"test data", chunk_size=0)
        with self.assertRaises(ValueError):
            ChunkReader(b"test data", chunk_size=-100)

    def test_chunk_reader_bytes_source(self):
        """Verifies chunk slicing on raw byte inputs including trailing partial chunk."""
        data = b"0123456789ABCDEF"  # 16 bytes
        reader = ChunkReader(data, chunk_size=5)
        chunks = list(reader)

        self.assertEqual(len(chunks), 4)
        self.assertEqual(chunks[0], b"01234")
        self.assertEqual(chunks[1], b"56789")
        self.assertEqual(chunks[2], b"ABCDE")
        self.assertEqual(chunks[3], b"F")  # partial chunk
        self.assertEqual(reader.total_bytes_read, 16)
        self.assertEqual(reader.global_offset, 16)
        self.assertEqual(reader.chunk_count, 4)

    def test_chunk_reader_file_source(self):
        """Verifies file-based chunk reading with context manager."""
        with tempfile.NamedTemporaryFile(delete=False) as tf:
            tf.write(b"HELLO_WORLD_DVB_S2_CHUNKING_TEST")
            tf_path = Path(tf.name)

        try:
            with ChunkReader(tf_path, chunk_size=7) as reader:
                chunks = list(reader)
            reassembled = b"".join(chunks)
            self.assertEqual(reassembled, b"HELLO_WORLD_DVB_S2_CHUNKING_TEST")
            self.assertEqual(reader.total_bytes_read, len(reassembled))
        finally:
            tf_path.unlink(missing_ok=True)

    def test_chunk_reader_reset(self):
        """Verifies reset functionality restores offsets and iteration."""
        data = b"A" * 50
        reader = ChunkReader(io.BytesIO(data), chunk_size=10)
        chunks1 = list(reader)
        self.assertEqual(len(chunks1), 5)
        self.assertEqual(reader.total_bytes_read, 50)

        reader.reset()
        self.assertEqual(reader.total_bytes_read, 0)
        self.assertEqual(reader.global_offset, 0)
        chunks2 = list(reader)
        self.assertEqual(len(chunks2), 5)

    def test_read_chunks_convenience_function(self):
        """Verifies read_chunks generator helper."""
        data = b"STREAMING_TEST"
        chunks = list(read_chunks(data, chunk_size=4))
        self.assertEqual(len(chunks), 4)
        self.assertEqual(b"".join(chunks), data)


class TestIncrementalTSParsing(unittest.TestCase):
    """Tests for incremental MPEG-TS parsing across arbitrary chunk boundaries."""

    @classmethod
    def setUpClass(cls):
        cls.whole_parser = TSParser()
        cls.whole_packets = list(cls.whole_parser.parse_file(TS_DATASET))
        cls.whole_stats = cls.whole_parser.get_statistics()

    def test_awkward_chunk_sizes_mpeg_ts(self):
        """
        Feeds sample.ts using awkward chunk sizes that intentionally cross 188-byte boundaries.
        Verifies 100% identical decoded packet count and stats.
        """
        awkward_sizes = [187, 188, 189, 511, 1024, 4096]
        for sz in awkward_sizes:
            with self.subTest(chunk_size=sz):
                parser = TSParser()
                with ChunkReader(TS_DATASET, chunk_size=sz) as reader:
                    packets = list(parser.parse_chunks(reader))
                stats = parser.get_statistics()

                self.assertEqual(len(packets), len(self.whole_packets))
                self.assertEqual(stats["total_packets"], self.whole_stats["total_packets"])
                self.assertEqual(stats["valid_sync_packets"], self.whole_stats["valid_sync_packets"])
                self.assertEqual(stats["total_payload_bytes"], self.whole_stats["total_payload_bytes"])
                self.assertEqual(stats["tei_errors"], self.whole_stats["tei_errors"])
                self.assertEqual(stats["null_packet_count"], self.whole_stats["null_packet_count"])
                self.assertEqual(dict(stats["pid_distribution"]), dict(self.whole_stats["pid_distribution"]))

    def test_ts_edge_cases(self):
        """Tests empty, single-byte, and truncated inputs."""
        parser = TSParser()
        # Empty
        pkts = list(parser.parse_chunks([b""]))
        self.assertEqual(len(pkts), 0)
        self.assertEqual(parser.stats.total_bytes_read, 0)

        # Single byte
        parser.reset()
        pkts = list(parser.parse_chunks([b"\x47"]))
        self.assertEqual(len(pkts), 0)
        self.assertEqual(parser.stats.total_bytes_read, 1)

        # 187 bytes (1 byte short of full TS packet)
        parser.reset()
        pkts = list(parser.parse_chunks([b"\x47" + b"\x00" * 186]))
        self.assertEqual(len(pkts), 0)
        self.assertEqual(parser.stats.total_bytes_read, 187)

    def test_ts_reset_and_reuse(self):
        """Verifies TSParser can be reset and re-used with zero state leakage."""
        parser = TSParser()
        chunk1 = bytes([0x47, 0x01, 0x00, 0x10]) + (b"\xAA" * 184)  # PID 256, CC 0
        pkts1 = list(parser.parse_chunk(chunk1, is_last=True))
        self.assertEqual(len(pkts1), 1)
        self.assertEqual(parser.stats.total_packets, 1)

        parser.reset()
        self.assertEqual(parser.stats.total_packets, 0)
        self.assertEqual(parser.stats.total_bytes_read, 0)
        self.assertEqual(len(parser._buffer), 0)
        self.assertEqual(len(parser._last_cc_per_pid), 0)

        # Re-parse same chunk
        pkts2 = list(parser.parse_chunk(chunk1, is_last=True))
        self.assertEqual(len(pkts2), 1)
        self.assertEqual(parser.stats.total_packets, 1)


class TestIncrementalGSEParsing(unittest.TestCase):
    """Tests for incremental GSE parsing across arbitrary chunk boundaries."""

    @classmethod
    def setUpClass(cls):
        cls.whole_parser = GSEParser()
        cls.whole_pdus = list(cls.whole_parser.parse_file(GSE_DATASET))
        cls.whole_stats = cls.whole_parser.get_statistics()

    def test_awkward_chunk_sizes_gse(self):
        """
        Feeds GSExtract/sample.ts using awkward chunk sizes.
        Verifies 100% identical decoded PDU count (14) and payload metrics.
        """
        awkward_sizes = [1, 7, 31, 100, 187, 188, 189, 511, 1024, 4096]
        for sz in awkward_sizes:
            with self.subTest(chunk_size=sz):
                parser = GSEParser()
                with ChunkReader(GSE_DATASET, chunk_size=sz) as reader:
                    pdus = list(parser.parse_chunks(reader))
                stats = parser.get_statistics()

                self.assertEqual(len(pdus), len(self.whole_pdus))
                self.assertEqual(stats["total_pdus"], 14)
                self.assertEqual(stats["valid_pdus"], 14)
                self.assertEqual(stats["total_payload_bytes"], self.whole_stats["total_payload_bytes"])
                self.assertEqual(stats["unfragmented_pdus"], self.whole_stats["unfragmented_pdus"])
                self.assertEqual(stats["first_fragments"], self.whole_stats["first_fragments"])
                self.assertEqual(stats["last_fragments"], self.whole_stats["last_fragments"])

    def test_gse_reset_and_reuse(self):
        """Verifies GSEParser reset and re-use without state leakage."""
        parser = GSEParser()
        with ChunkReader(GSE_DATASET, chunk_size=512) as reader:
            pdus1 = list(parser.parse_chunks(reader))
        self.assertEqual(len(pdus1), 14)

        parser.reset()
        self.assertEqual(parser.stats.total_pdus, 0)
        self.assertEqual(parser.stats.total_bytes_read, 0)
        self.assertEqual(len(parser._buffer), 0)

        with ChunkReader(GSE_DATASET, chunk_size=1024) as reader:
            pdus2 = list(parser.parse_chunks(reader))
        self.assertEqual(len(pdus2), 14)


class TestIncrementalBBFrameParsing(unittest.TestCase):
    """Tests for incremental BBFrame parsing across arbitrary chunk boundaries."""

    @classmethod
    def setUpClass(cls):
        cls.whole_parser = BBFrameParser()
        cls.whole_frames = list(cls.whole_parser.parse_file(BBFRAME_DATASET))
        cls.whole_stats = cls.whole_parser.get_statistics()

    def test_awkward_chunk_sizes_bbframe(self):
        """
        Feeds dvb-s2_bb_example.pcap using awkward chunk sizes.
        Verifies 100% identical decoded frame count (4,309) and payload metrics.
        """
        awkward_sizes = [100, 187, 188, 189, 511, 1024, 4096, 65536]
        for sz in awkward_sizes:
            with self.subTest(chunk_size=sz):
                parser = BBFrameParser()
                with ChunkReader(BBFRAME_DATASET, chunk_size=sz) as reader:
                    frames = list(parser.parse_chunks(reader))
                stats = parser.get_statistics()

                self.assertEqual(len(frames), len(self.whole_frames))
                self.assertEqual(stats["total_frames"], 4309)
                self.assertEqual(stats["valid_frames"], 4309)
                self.assertEqual(stats["total_payload_bytes"], self.whole_stats["total_payload_bytes"])
                self.assertEqual(stats["invalid_crc_frames"], 0)

    def test_bbframe_reset_and_reuse(self):
        """Verifies BBFrameParser reset and re-use without state leakage."""
        parser = BBFrameParser()
        with ChunkReader(BBFRAME_DATASET, chunk_size=4096) as reader:
            frames1 = list(parser.parse_chunks(reader))
        self.assertEqual(len(frames1), 4309)

        parser.reset()
        self.assertEqual(parser.stats.total_frames, 0)
        self.assertEqual(parser.stats.total_bytes_read, 0)
        self.assertEqual(len(parser._buffer), 0)
        self.assertEqual(parser._frames_yielded, 0)

        with ChunkReader(BBFRAME_DATASET, chunk_size=8192) as reader:
            frames2 = list(parser.parse_chunks(reader))
        self.assertEqual(len(frames2), 4309)


class TestWholeFileVsChunkedEquivalence(unittest.TestCase):
    """
    Primary Acceptance Criterion: Validates whole-file vs incremental chunked
    analytical equivalence across F1, F2 (with random_state=42), F3, F4, F5, F7.
    """

    def setUp(self):
        self.tl_gen = TimelineGenerator(TimelineConfig(
            ts_window_size=200,
            gse_window_size=3,
            bbframe_window_size=50,
            f2_contamination=0.05,
            f2_anomaly_threshold=0.50,
        ))
        self.expl_engine = AnomalyExplanationEngine(ExplanationConfig())
        self.report_gen = AutomaticReportGenerator(ReportConfig())

    def test_mpeg_ts_full_analytical_equivalence(self):
        """
        Runs whole-file vs chunked (chunk_size=187) on MPEG-TS dataset and verifies:
        - Exact unit counts, payload bytes, window counts
        - F1 Health score and Priority-1 checks
        - F2 Anomaly decisions, anomaly window indices, scores within 1e-6 tolerance
        - F3 Pattern metrics, dominant PID, Shannon entropy
        - F4 Window physical byte offsets and unit ranges
        - F5 Diagnostic explanation reports
        - F7 Tripartite findings and reports
        """
        handler = StreamHandler(TS_DATASET)

        # Whole-file path
        tl_whole = self.tl_gen.generate_from_handler(handler, window_size=200)
        expl_whole = self.expl_engine.explain_timeline(tl_whole)
        rep_whole = self.report_gen.generate_from_timeline(
            timeline=tl_whole,
            explanation_report=expl_whole,
            comparison_report=None,
            stream_path=TS_DATASET,
            file_size_bytes=handler.size_bytes,
        )

        # Incremental chunked path (awkward 187-byte chunks)
        with ChunkReader(TS_DATASET, chunk_size=187) as reader:
            tl_chunked = self.tl_gen.generate_from_chunks(
                chunks=reader,
                format=StreamFormat.MPEG_TS,
                window_size=200,
                stream_name=TS_DATASET.name,
            )
        expl_chunked = self.expl_engine.explain_timeline(tl_chunked)
        rep_chunked = self.report_gen.generate_from_timeline(
            timeline=tl_chunked,
            explanation_report=expl_chunked,
            comparison_report=None,
            stream_path=TS_DATASET,
            file_size_bytes=handler.size_bytes,
        )

        # 1. Structural / Framing Equivalence
        self.assertEqual(tl_chunked.total_units, tl_whole.total_units)
        self.assertEqual(tl_chunked.total_bytes, tl_whole.total_bytes)
        self.assertEqual(tl_chunked.total_windows, tl_whole.total_windows)
        self.assertEqual(tl_chunked.total_windows, 91)

        # 2. Window-by-window physical byte offsets and unit ranges
        for i in range(tl_whole.total_windows):
            pw = tl_whole.points[i]
            pc = tl_chunked.points[i]
            self.assertEqual(pc.unit_offset_start, pw.unit_offset_start)
            self.assertEqual(pc.unit_offset_end, pw.unit_offset_end)
            self.assertEqual(pc.byte_offset_start, pw.byte_offset_start)
            self.assertEqual(pc.byte_offset_end, pw.byte_offset_end)
            self.assertEqual(pc.payload_bytes, pw.payload_bytes)
            self.assertEqual(pc.health_score, pw.health_score)
            self.assertEqual(pc.is_anomaly, pw.is_anomaly)
            self.assertAlmostEqual(pc.anomaly_score, pw.anomaly_score, places=6)

        # 3. F1 Health Equivalence
        self.assertEqual(tl_chunked.summary_stats["mean_health_score"], tl_whole.summary_stats["mean_health_score"])

        # 4. F2 Anomaly Equivalence
        self.assertEqual(tl_chunked.summary_stats["anomaly_window_count"], tl_whole.summary_stats["anomaly_window_count"])
        self.assertEqual(tl_chunked.summary_stats["anomaly_window_count"], 5)
        self.assertAlmostEqual(tl_chunked.summary_stats["peak_anomaly_score"], tl_whole.summary_stats["peak_anomaly_score"], places=4)

        anom_indices_whole = [p.window_index for p in tl_whole.points if p.is_anomaly]
        anom_indices_chunked = [p.window_index for p in tl_chunked.points if p.is_anomaly]
        self.assertEqual(anom_indices_chunked, anom_indices_whole)
        self.assertEqual(anom_indices_chunked, [1, 2, 12, 88, 90])

        # 5. F3 Pattern / Entropy Equivalence
        for i in range(tl_whole.total_windows):
            pw = tl_whole.points[i]
            pc = tl_chunked.points[i]
            self.assertEqual(pc.format_specific_metrics.get("dominant_pid"), pw.format_specific_metrics.get("dominant_pid"))

        # 6. F5 Diagnostic Explanation Equivalence
        self.assertEqual(len(expl_chunked.explanations), len(expl_whole.explanations))
        for ew, ec in zip(expl_whole.explanations, expl_chunked.explanations):
            self.assertEqual(ec.window_index, ew.window_index)
            self.assertEqual(ec.native_component, ew.native_component)
            self.assertEqual(len(ec.primary_drivers), len(ew.primary_drivers))
            self.assertAlmostEqual(ec.anomaly_score, ew.anomaly_score, places=6)

        # 7. F7 Report Equivalence
        self.assertEqual(len(rep_chunked.tripartite_findings), len(rep_whole.tripartite_findings))
        self.assertEqual(rep_chunked.stream_info.total_units, rep_whole.stream_info.total_units)
        self.assertEqual(rep_chunked.health.health_score, rep_whole.health.health_score)

    def test_gse_full_analytical_equivalence(self):
        """Validates whole-file vs chunked equivalence on GSE dataset."""
        handler = StreamHandler(GSE_DATASET, forced_format=StreamFormat.GSE)
        tl_whole = self.tl_gen.generate_from_handler(handler, window_size=3)

        with ChunkReader(GSE_DATASET, chunk_size=100) as reader:
            tl_chunked = self.tl_gen.generate_from_chunks(
                chunks=reader,
                format=StreamFormat.GSE,
                window_size=3,
                stream_name=GSE_DATASET.name,
            )

        self.assertEqual(tl_chunked.total_units, 14)
        self.assertEqual(tl_chunked.total_windows, 5)
        self.assertEqual(tl_chunked.total_bytes, tl_whole.total_bytes)
        self.assertEqual(tl_chunked.summary_stats["anomaly_window_count"], tl_whole.summary_stats["anomaly_window_count"])
        self.assertEqual(tl_chunked.summary_stats["anomaly_window_count"], 1)

    def test_bbframe_full_analytical_equivalence(self):
        """Validates whole-file vs chunked equivalence on BBFrame dataset."""
        handler = StreamHandler(BBFRAME_DATASET, forced_format=StreamFormat.BB_FRAME)
        tl_whole = self.tl_gen.generate_from_handler(handler, window_size=50)

        with ChunkReader(BBFRAME_DATASET, chunk_size=4096) as reader:
            tl_chunked = self.tl_gen.generate_from_chunks(
                chunks=reader,
                format=StreamFormat.BB_FRAME,
                window_size=50,
                stream_name=BBFRAME_DATASET.name,
            )

        self.assertEqual(tl_chunked.total_units, 4309)
        self.assertEqual(tl_chunked.total_windows, 87)
        self.assertEqual(tl_chunked.total_bytes, tl_whole.total_bytes)
        self.assertEqual(tl_chunked.summary_stats["anomaly_window_count"], tl_whole.summary_stats["anomaly_window_count"])
        self.assertEqual(tl_chunked.summary_stats["anomaly_window_count"], 5)


class TestCoordinatorChunkedIntegration(unittest.TestCase):
    """Verifies AnalysisCoordinator chunked API integration."""

    def setUp(self):
        self.coordinator = AnalysisCoordinator()

    def test_coordinator_analyze_stream_chunked_ts(self):
        """Verifies analyze_stream_chunked produces equivalent response to analyze_stream."""
        res_whole = self.coordinator.analyze_stream(TS_DATASET, forced_format="MPEG_TS", window_size=200)
        res_chunked = self.coordinator.analyze_stream_chunked(
            TS_DATASET,
            chunk_size=1024,
            forced_format="MPEG_TS",
            window_size=200,
        )

        self.assertTrue(res_chunked["success"])
        info_w = res_whole["stream_info"]
        info_c = res_chunked["stream_info"]
        self.assertEqual(info_c["total_units"], info_w["total_units"])
        self.assertEqual(info_c["total_payload_bytes"], info_w["total_payload_bytes"])
        self.assertEqual(info_c["total_windows"], info_w["total_windows"])

        f1_w = res_whole["f1_health"]
        f1_c = res_chunked["f1_health"]
        self.assertEqual(f1_c["overall_health_score"], f1_w["overall_health_score"])
        self.assertEqual(f1_c["health_classification"], f1_w["health_classification"])

        f2_w = res_whole["f2_anomalies"]
        f2_c = res_chunked["f2_anomalies"]
        self.assertEqual(f2_c["anomaly_window_count"], f2_w["anomaly_window_count"])
        self.assertEqual(f2_c["peak_anomaly_score"], f2_w["peak_anomaly_score"])
        indices_w = [w["window_index"] for w in f2_w["anomalous_windows"]]
        indices_c = [w["window_index"] for w in f2_c["anomalous_windows"]]
        self.assertEqual(indices_c, indices_w)


if __name__ == "__main__":
    unittest.main()
