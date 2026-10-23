"""
Unit and Integration Tests for High-Throughput Streaming Engine (Chunk 3).

Verifies:
1. ChunkReader memory-mapped I/O equivalence and zero-copy memoryview chunking.
2. Optimized parser throughput, stats parity, and continuity preservation.
3. Awkward chunk boundaries with optimized TS and BBFrame parsers.
4. Empty and truncated stream handling.
5. Parser state reset and memory isolation.
6. End-to-end analytical equivalence (F1-F7) across MPEG-TS, BBFrame, and GSE.
7. AnalysisCoordinator.analyze_stream_fast integration.
8. Synthetic scaling fixture generation and cleanup outside 01_RAW_DATA.
9. Raw dataset hash invariants before and after tests.
"""

import hashlib
from pathlib import Path
import tempfile
import unittest

from dvbs2_analyzer.config import StreamFormat
from dvbs2_analyzer.ingestion.chunk_reader import ChunkReader, read_chunks
from dvbs2_analyzer.parsers.ts_parser import TSParser
from dvbs2_analyzer.parsers.bbframe_parser import BBFrameParser
from dvbs2_analyzer.parsers.gse_parser import GSEParser
from dvbs2_analyzer.frontend.coordinator import AnalysisCoordinator
from dvbs2_analyzer.streaming.engine import (
    HighThroughputStreamingEngine,
    StreamingEngineConfig,
)
from dvbs2_analyzer.streaming.benchmark import StreamingBenchmarkSuite

RAW_TS_PATH = Path(__file__).resolve().parent.parent.parent / "01_RAW_DATA" / "03_TS" / "DVBS2_toolkit" / "sample.ts"
RAW_GSE_PATH = Path(__file__).resolve().parent.parent.parent / "01_RAW_DATA" / "02_GSE" / "GSExtract" / "sample.ts"
RAW_BB_PATH = Path(__file__).resolve().parent.parent.parent / "01_RAW_DATA" / "01_BBFRAME_GSE" / "dvb-s2_bb_example.pcap"

EXPECTED_TS_SHA256 = "8bfd066e52d7044bd71400133e64097de9b267adb28f0e745954e396a03a80ed"
EXPECTED_GSE_SHA256 = "c9178b19d79d4f42398f9fc2b01098ad0e759cd22c4edb6ca4214998c26e8e38"
EXPECTED_BB_SHA256 = "fa6aa639732fdd96b022eaf4e23cfdb30c377f62ea32fed1d158f84252906193"


def compute_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest().lower()


class TestHighThroughputStreaming(unittest.TestCase):
    """Chunk 3 High-Throughput Verification Test Suite."""

    @classmethod
    def setUpClass(cls):
        assert RAW_TS_PATH.exists(), f"Missing {RAW_TS_PATH}"
        assert RAW_GSE_PATH.exists(), f"Missing {RAW_GSE_PATH}"
        assert RAW_BB_PATH.exists(), f"Missing {RAW_BB_PATH}"
        cls.coord = AnalysisCoordinator()
        cls.engine = HighThroughputStreamingEngine()

    def tearDown(self):
        # Mandatory raw data integrity check after every test
        self.assertEqual(compute_sha256(RAW_TS_PATH), EXPECTED_TS_SHA256)
        self.assertEqual(compute_sha256(RAW_GSE_PATH), EXPECTED_GSE_SHA256)
        self.assertEqual(compute_sha256(RAW_BB_PATH), EXPECTED_BB_SHA256)

    def test_raw_data_hash_invariants(self):
        """Verifies raw dataset files in 01_RAW_DATA match authoritative baseline."""
        self.assertEqual(compute_sha256(RAW_TS_PATH), EXPECTED_TS_SHA256)
        self.assertEqual(compute_sha256(RAW_GSE_PATH), EXPECTED_GSE_SHA256)
        self.assertEqual(compute_sha256(RAW_BB_PATH), EXPECTED_BB_SHA256)

    def test_chunk_reader_mmap_equivalence(self):
        """Verifies standard buffered reading and memory-mapped reading yield identical bytes."""
        for c_sz in [4096, 65536, 131072]:
            with ChunkReader(RAW_TS_PATH, chunk_size=c_sz, use_mmap=False) as r_std:
                chunks_std = list(r_std)
                total_std = r_std.total_bytes_read

            with ChunkReader(RAW_TS_PATH, chunk_size=c_sz, use_mmap=True) as r_mmap:
                chunks_mmap = list(r_mmap)
                total_mmap = r_mmap.total_bytes_read

            self.assertEqual(total_std, total_mmap)
            self.assertEqual(len(chunks_std), len(chunks_mmap))
            self.assertEqual(b"".join(chunks_std), b"".join(chunks_mmap))

    def test_chunk_reader_memoryview_zerocopy(self):
        """Verifies zero-copy memoryview chunking on in-memory buffers."""
        raw_data = RAW_TS_PATH.read_bytes()[:10000]
        mv = memoryview(raw_data)
        reader = ChunkReader(mv, chunk_size=1024)
        chunks = list(reader)

        self.assertEqual(reader.total_bytes_read, len(raw_data))
        self.assertEqual(b"".join(chunks), raw_data)

    def test_ts_parser_optimized_batch_compaction(self):
        """Verifies optimized cursor-compacted TSParser yields identical packets and statistics."""
        parser = TSParser()
        pkts = list(parser.parse_chunks(ChunkReader(RAW_TS_PATH, chunk_size=65536)))

        self.assertEqual(len(pkts), 18176)
        stats = parser.get_statistics()
        self.assertEqual(stats["total_packets"], 18176)
        self.assertEqual(stats["valid_sync_packets"], 18176)
        self.assertEqual(stats["sync_byte_errors"], 0)
        self.assertEqual(stats["tei_errors"], 0)
        self.assertEqual(stats["total_payload_bytes"], 3267305)

    def test_bbframe_parser_optimized_batch_compaction(self):
        """Verifies optimized cursor-compacted BBFrameParser yields identical frames and statistics."""
        parser = BBFrameParser()
        frames = list(parser.parse_chunks(ChunkReader(RAW_BB_PATH, chunk_size=65536)))

        self.assertEqual(len(frames), 4309)
        stats = parser.get_statistics()
        self.assertEqual(stats["total_frames"], 4309)
        self.assertEqual(stats["valid_frames"], 4309)
        self.assertEqual(stats["invalid_crc_frames"], 0)
        self.assertEqual(stats["total_payload_bytes"], 1958826)

    def test_awkward_chunk_sizes_ts_parser(self):
        """Tests TSParser against awkward chunk boundaries bisecting 188-byte packets."""
        for c_sz in [100, 187, 188, 189, 511, 1024, 4096]:
            parser = TSParser()
            pkts = list(parser.parse_chunks(ChunkReader(RAW_TS_PATH, chunk_size=c_sz)))
            self.assertEqual(len(pkts), 18176, f"Failed at chunk_size={c_sz}")
            self.assertEqual(parser.stats.total_bytes_read, 3417088)

    def test_awkward_chunk_sizes_bbframe_parser(self):
        """Tests BBFrameParser against awkward chunk boundaries."""
        for c_sz in [100, 187, 188, 189, 511, 1024, 4096]:
            parser = BBFrameParser()
            frames = list(parser.parse_chunks(ChunkReader(RAW_BB_PATH, chunk_size=c_sz)))
            self.assertEqual(len(frames), 4309, f"Failed at chunk_size={c_sz}")
            self.assertEqual(parser.stats.total_bytes_read, 2349376)

    def test_empty_and_truncated_inputs(self):
        """Confirms empty and truncated inputs are handled cleanly without error."""
        # Empty input
        ts_parser = TSParser()
        pkts = list(ts_parser.parse_chunks([b""]))
        self.assertEqual(len(pkts), 0)

        # Truncated input (less than packet size)
        ts_parser_trunc = TSParser()
        pkts_trunc = list(ts_parser_trunc.parse_chunks([b"\x47\x00\x00\x10" + b"\x00" * 50]))
        self.assertEqual(len(pkts_trunc), 0)
        self.assertEqual(ts_parser_trunc.stats.total_bytes_read, 54)

    def test_parser_reset_and_isolation(self):
        """Verifies parser reset clears residual buffers and statistics completely."""
        parser = TSParser()
        list(parser.parse_chunks(ChunkReader(RAW_TS_PATH, chunk_size=65536)))
        self.assertGreater(parser.stats.total_packets, 0)

        parser.reset()
        self.assertEqual(parser.stats.total_packets, 0)
        self.assertEqual(len(parser._buffer), 0)
        self.assertEqual(len(parser._last_cc_per_pid), 0)

    def test_end_to_end_analytical_equivalence_ts(self):
        """
        Confirms analyze_stream_fast produces 100% equivalent analytical telemetry
        as the baseline whole-file analyze_stream for MPEG-TS.
        """
        res_baseline = self.coord.analyze_stream(RAW_TS_PATH, window_size=200)
        res_fast = self.coord.analyze_stream_fast(RAW_TS_PATH, window_size=200, chunk_size=65536)

        # F1 Health Equivalence
        self.assertEqual(res_baseline["f1_health"]["overall_health_score"], res_fast["f1_health"]["overall_health_score"])
        self.assertEqual(res_baseline["f1_health"]["total_errors"], res_fast["f1_health"]["total_errors"])

        # F2 Anomaly Equivalence
        self.assertEqual(res_baseline["f2_anomalies"]["anomalous_windows"], res_fast["f2_anomalies"]["anomalous_windows"])
        self.assertAlmostEqual(res_baseline["f2_anomalies"]["peak_anomaly_score"], res_fast["f2_anomalies"]["peak_anomaly_score"], places=4)

        # F3 Pattern Equivalence
        self.assertEqual(res_baseline["f3_patterns"], res_fast["f3_patterns"])

        # F4 Timeline Physical Offsets
        pts_base = res_baseline["f4_timeline"]["points"]
        pts_fast = res_fast["f4_timeline"]["points"]
        self.assertEqual(len(pts_base), len(pts_fast))
        for p_b, p_f in zip(pts_base, pts_fast):
            self.assertEqual(p_b["byte_offset_start"], p_f["byte_offset_start"])
            self.assertEqual(p_b["byte_offset_end"], p_f["byte_offset_end"])
            self.assertEqual(p_b["unit_offset_start"], p_f["unit_offset_start"])
            self.assertEqual(p_b["unit_offset_end"], p_f["unit_offset_end"])
            self.assertEqual(p_b["is_anomaly"], p_f["is_anomaly"])

    def test_end_to_end_analytical_equivalence_bbframe(self):
        """Confirms analyze_stream_fast produces equivalent telemetry for BBFrame."""
        res_baseline = self.coord.analyze_stream(RAW_BB_PATH, window_size=50)
        res_fast = self.coord.analyze_stream_fast(RAW_BB_PATH, window_size=50, chunk_size=65536)

        self.assertEqual(res_baseline["f1_health"]["overall_health_score"], res_fast["f1_health"]["overall_health_score"])
        self.assertEqual(res_baseline["f2_anomalies"]["anomalous_windows"], res_fast["f2_anomalies"]["anomalous_windows"])
        self.assertEqual(res_baseline["stream_info"]["total_units"], res_fast["stream_info"]["total_units"])

    def test_end_to_end_analytical_equivalence_gse(self):
        """Confirms analyze_stream_fast produces equivalent telemetry for GSE."""
        res_baseline = self.coord.analyze_stream(RAW_GSE_PATH, window_size=3)
        res_fast = self.coord.analyze_stream_fast(RAW_GSE_PATH, window_size=3, chunk_size=256)

        self.assertEqual(res_baseline["f1_health"]["overall_health_score"], res_fast["f1_health"]["overall_health_score"])
        self.assertEqual(res_baseline["f2_anomalies"]["anomalous_windows"], res_fast["f2_anomalies"]["anomalous_windows"])
        self.assertEqual(res_baseline["stream_info"]["total_units"], res_fast["stream_info"]["total_units"])

    def test_stream_units_generator(self):
        """Verifies stream_units generator yields units cleanly without building full timeline."""
        unit_count = 0
        for _ in self.engine.stream_units(RAW_TS_PATH, format_enum=StreamFormat.MPEG_TS, chunk_size=65536):
            unit_count += 1
            if unit_count >= 1000:
                break
        self.assertEqual(unit_count, 1000)

    def test_synthetic_stream_scaling_and_cleanup(self):
        """Tests temporary synthetic multi-megabyte stream generation, processing, and cleanup."""
        suite = StreamingBenchmarkSuite()
        metric = suite.benchmark_synthetic_scaling(target_mb=5, chunk_size=65536)

        self.assertEqual(metric.name, "Synthetic_Scaling_MPEG_TS")
        self.assertTrue(metric.details["is_synthetic"])
        self.assertGreater(metric.throughput_mibs, 1.0)


if __name__ == "__main__":
    unittest.main()
