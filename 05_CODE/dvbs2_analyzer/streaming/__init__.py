"""
High-Throughput Streaming Engine for PRJ_111 (Chunk 3).

Provides memory-bounded streaming pipelines, zero-copy chunk iteration,
optional memory-mapped I/O, and reproducible performance benchmarking.
"""

from dvbs2_analyzer.streaming.engine import (
    HighThroughputStreamingEngine,
    StreamingEngineConfig,
    StreamingPipelineResult,
)
from dvbs2_analyzer.streaming.benchmark import (
    StreamingBenchmarkSuite,
    BenchmarkResult,
)

__all__ = [
    "HighThroughputStreamingEngine",
    "StreamingEngineConfig",
    "StreamingPipelineResult",
    "StreamingBenchmarkSuite",
    "BenchmarkResult",
]
