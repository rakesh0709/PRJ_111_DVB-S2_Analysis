"""
Reproducible Performance Benchmarking Suite for PRJ_111 (Chunk 3).

Measures:
1. I/O reading throughput across chunk sizes (standard buffered vs. mmap).
2. Protocol parser throughput across MPEG-TS, GSE, and BBFrame.
3. End-to-end analytical pipeline time, throughput, and peak memory (tracemalloc).
4. Synthetic scaling outside 01_RAW_DATA with explicit synthetic labeling.
"""

from dataclasses import dataclass, field
import hashlib
from pathlib import Path
import tempfile
import time
import tracemalloc
from typing import Any, Dict, List, Optional, Tuple, Union

from dvbs2_analyzer.config import RAW_DATA_DIR, StreamFormat
from dvbs2_analyzer.ingestion.chunk_reader import ChunkReader
from dvbs2_analyzer.ingestion.stream_handler import StreamHandler
from dvbs2_analyzer.frontend.coordinator import AnalysisCoordinator
from dvbs2_analyzer.streaming.engine import HighThroughputStreamingEngine, StreamingEngineConfig

RAW_TS_PATH = RAW_DATA_DIR / "03_TS" / "DVBS2_toolkit" / "sample.ts"
RAW_GSE_PATH = RAW_DATA_DIR / "02_GSE" / "GSExtract" / "sample.ts"
RAW_BB_PATH = RAW_DATA_DIR / "01_BBFRAME_GSE" / "dvb-s2_bb_example.pcap"


@dataclass
class BenchmarkMetric:
    """Single benchmark measurement result."""
    name: str
    workload: str
    bytes_processed: int
    elapsed_seconds: float
    throughput_mibs: float
    peak_memory_mib: float
    runs: int
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class BenchmarkResult:
    """Aggregated benchmark suite output."""
    timestamp: float
    metrics: List[BenchmarkMetric]
    system_info: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "metrics": [
                {
                    "name": m.name,
                    "workload": m.workload,
                    "bytes_processed": m.bytes_processed,
                    "elapsed_seconds": round(m.elapsed_seconds, 4),
                    "throughput_mibs": round(m.throughput_mibs, 2),
                    "peak_memory_mib": round(m.peak_memory_mib, 2),
                    "runs": m.runs,
                    "details": m.details,
                }
                for m in self.metrics
            ],
            "system_info": self.system_info,
        }

    def format_markdown(self) -> str:
        lines = [
            "| Benchmark Name | Workload | Bytes | Elapsed (s) | Throughput (MiB/s) | Peak RAM (MiB) |",
            "| :--- | :--- | :--- | :--- | :--- | :--- |",
        ]
        for m in self.metrics:
            lines.append(
                f"| {m.name} | {m.workload} | {m.bytes_processed:,} | {m.elapsed_seconds:.4f} | {m.throughput_mibs:.2f} | {m.peak_memory_mib:.2f} |"
            )
        return "\n".join(lines)


class StreamingBenchmarkSuite:
    """Executes reproducible throughput and memory benchmarks."""

    def __init__(self):
        self.coord = AnalysisCoordinator()
        self.fast_engine = HighThroughputStreamingEngine()

    def run_all_benchmarks(self) -> BenchmarkResult:
        metrics: List[BenchmarkMetric] = []
        metrics.extend(self.benchmark_io(RAW_TS_PATH))
        metrics.extend(self.benchmark_parsers())
        metrics.extend(self.benchmark_pipeline())
        metrics.append(self.benchmark_synthetic_scaling(target_mb=10))
        return BenchmarkResult(timestamp=time.time(), metrics=metrics)

    def benchmark_io(
        self,
        file_path: Path,
        chunk_sizes: Optional[List[int]] = None,
        runs: int = 3,
    ) -> List[BenchmarkMetric]:
        """Compares standard buffered ChunkReader vs. memory-mapped ChunkReader."""
        sizes = chunk_sizes or [16384, 65536, 262144, 1048576]
        metrics = []
        file_bytes = file_path.stat().st_size

        for c_sz in sizes:
            # Standard I/O
            durations_std = []
            for _ in range(runs):
                t0 = time.perf_counter()
                total = 0
                with ChunkReader(file_path, chunk_size=c_sz, use_mmap=False) as r:
                    for chunk in r:
                        total += len(chunk)
                durations_std.append(time.perf_counter() - t0)
            avg_std = sum(durations_std) / runs
            tp_std = (file_bytes / (1024.0 * 1024.0)) / avg_std if avg_std > 0 else 0.0

            metrics.append(BenchmarkMetric(
                name="IO_Standard_Buffered",
                workload=f"{file_path.name} (chunk={c_sz}B)",
                bytes_processed=file_bytes,
                elapsed_seconds=avg_std,
                throughput_mibs=tp_std,
                peak_memory_mib=0.0,
                runs=runs,
                details={"chunk_size": c_sz, "mode": "STANDARD_BUFFERED"},
            ))

            # Mmap I/O
            durations_mmap = []
            for _ in range(runs):
                t0 = time.perf_counter()
                total = 0
                with ChunkReader(file_path, chunk_size=c_sz, use_mmap=True) as r:
                    for chunk in r:
                        total += len(chunk)
                durations_mmap.append(time.perf_counter() - t0)
            avg_mmap = sum(durations_mmap) / runs
            tp_mmap = (file_bytes / (1024.0 * 1024.0)) / avg_mmap if avg_mmap > 0 else 0.0

            metrics.append(BenchmarkMetric(
                name="IO_Memory_Mapped",
                workload=f"{file_path.name} (chunk={c_sz}B)",
                bytes_processed=file_bytes,
                elapsed_seconds=avg_mmap,
                throughput_mibs=tp_mmap,
                peak_memory_mib=0.0,
                runs=runs,
                details={"chunk_size": c_sz, "mode": "MEMORY_MAPPED"},
            ))

        return metrics

    def benchmark_parsers(
        self,
        chunk_size: int = 65536,
        runs: int = 3,
    ) -> List[BenchmarkMetric]:
        """Benchmarks format parsing throughput across all 3 formats."""
        metrics = []
        datasets = [
            ("MPEG_TS", RAW_TS_PATH),
            ("GSE", RAW_GSE_PATH),
            ("BB_FRAME", RAW_BB_PATH),
        ]

        for fmt_name, path in datasets:
            if not path.exists():
                continue
            handler = StreamHandler(path)
            size = path.stat().st_size

            durations = []
            unit_counts = []
            for _ in range(runs):
                parser = handler.get_parser()
                t0 = time.perf_counter()
                cnt = 0
                with ChunkReader(path, chunk_size=chunk_size) as r:
                    for _ in parser.parse_chunks(r):
                        cnt += 1
                durations.append(time.perf_counter() - t0)
                unit_counts.append(cnt)

            avg_dur = sum(durations) / runs
            tp = (size / (1024.0 * 1024.0)) / avg_dur if avg_dur > 0 else 0.0

            metrics.append(BenchmarkMetric(
                name=f"Parser_{fmt_name}",
                workload=f"{path.name} ({size}B)",
                bytes_processed=size,
                elapsed_seconds=avg_dur,
                throughput_mibs=tp,
                peak_memory_mib=0.0,
                runs=runs,
                details={"total_units": unit_counts[0], "chunk_size": chunk_size},
            ))

        return metrics

    def benchmark_pipeline(
        self,
        runs: int = 2,
    ) -> List[BenchmarkMetric]:
        """Compares baseline chunked pipeline vs high-throughput pipeline and records peak memory."""
        metrics = []
        datasets = [
            ("MPEG_TS", RAW_TS_PATH),
            ("BB_FRAME", RAW_BB_PATH),
            ("GSE", RAW_GSE_PATH),
        ]

        for fmt_name, path in datasets:
            if not path.exists():
                continue
            size = path.stat().st_size

            # Baseline Chunked Pipeline
            durations_base = []
            peak_mems_base = []
            for _ in range(runs):
                tracemalloc.start()
                t0 = time.perf_counter()
                res = self.coord.analyze_stream_chunked(path, chunk_size=65536)
                durations_base.append(time.perf_counter() - t0)
                _, peak = tracemalloc.get_traced_memory()
                tracemalloc.stop()
                peak_mems_base.append(peak / (1024.0 * 1024.0))

            avg_dur_base = sum(durations_base) / runs
            avg_peak_base = sum(peak_mems_base) / runs
            tp_base = (size / (1024.0 * 1024.0)) / avg_dur_base if avg_dur_base > 0 else 0.0

            metrics.append(BenchmarkMetric(
                name=f"Pipeline_Chunked_Baseline_{fmt_name}",
                workload=path.name,
                bytes_processed=size,
                elapsed_seconds=avg_dur_base,
                throughput_mibs=tp_base,
                peak_memory_mib=avg_peak_base,
                runs=runs,
                details={"mode": "CHUNKED_BASELINE"},
            ))

            # High-Throughput Pipeline
            durations_fast = []
            peak_mems_fast = []
            for _ in range(runs):
                tracemalloc.start()
                t0 = time.perf_counter()
                res_fast = self.coord.analyze_stream_fast(path, chunk_size=65536, use_mmap=False)
                durations_fast.append(time.perf_counter() - t0)
                _, peak = tracemalloc.get_traced_memory()
                tracemalloc.stop()
                peak_mems_fast.append(peak / (1024.0 * 1024.0))

            avg_dur_fast = sum(durations_fast) / runs
            avg_peak_fast = sum(peak_mems_fast) / runs
            tp_fast = (size / (1024.0 * 1024.0)) / avg_dur_fast if avg_dur_fast > 0 else 0.0

            metrics.append(BenchmarkMetric(
                name=f"Pipeline_High_Throughput_{fmt_name}",
                workload=path.name,
                bytes_processed=size,
                elapsed_seconds=avg_dur_fast,
                throughput_mibs=tp_fast,
                peak_memory_mib=avg_peak_fast,
                runs=runs,
                details={"mode": "HIGH_THROUGHPUT_STREAMING"},
            ))

        return metrics

    def benchmark_synthetic_scaling(
        self,
        target_mb: int = 25,
        chunk_size: int = 65536,
    ) -> BenchmarkMetric:
        """
        Generates a temporary synthetic MPEG-TS fixture outside 01_RAW_DATA
        to benchmark sustained multi-megabyte streaming throughput.
        """
        # Packets of 188 bytes with 0x47 sync byte and alternating PID 256/257
        unit_count = (target_mb * 1024 * 1024) // 188
        total_bytes = unit_count * 188

        with tempfile.NamedTemporaryFile(delete=False, suffix=".ts") as tf:
            synth_path = Path(tf.name)
            # Write synthetic MPEG-TS stream in batches
            batch_size = 1000
            for i in range(0, unit_count, batch_size):
                batch_pkts = []
                for j in range(i, min(unit_count, i + batch_size)):
                    pid = 256 if (j % 2 == 0) else 257
                    b1 = (pid >> 8) & 0x1F
                    b2 = pid & 0xFF
                    cc = j % 16
                    pkt = bytes([0x47, b1, b2, 0x10 | cc]) + b"\x00" * 184
                    batch_pkts.append(pkt)
                tf.write(b"".join(batch_pkts))

        try:
            engine = HighThroughputStreamingEngine()
            tracemalloc.start()
            t0 = time.perf_counter()
            count = 0
            for _ in engine.stream_units(synth_path, format_enum=StreamFormat.MPEG_TS, chunk_size=chunk_size):
                count += 1
            dur = time.perf_counter() - t0
            _, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()

            tp = (total_bytes / (1024.0 * 1024.0)) / dur if dur > 0 else 0.0

            return BenchmarkMetric(
                name="Synthetic_Scaling_MPEG_TS",
                workload=f"Synthetic {target_mb}MB ({unit_count} packets)",
                bytes_processed=total_bytes,
                elapsed_seconds=dur,
                throughput_mibs=tp,
                peak_memory_mib=peak / (1024.0 * 1024.0),
                runs=1,
                details={
                    "is_synthetic": True,
                    "target_mb": target_mb,
                    "parsed_packets": count,
                },
            )
        finally:
            if synth_path.exists():
                synth_path.unlink()
