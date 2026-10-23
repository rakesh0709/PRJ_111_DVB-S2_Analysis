"""
High-Throughput Streaming Engine Implementation for PRJ_111 (Chunk 3).

Optimizes binary stream analysis through:
1. Zero-copy / memoryview chunk iteration.
2. Optional memory-mapped I/O (use_mmap=True) for large file captures.
3. Cursor-compacted streaming parsers eliminating quadratic memory moves.
4. Window-bounded timeline generation ensuring analytical equivalence with whole-file execution.
"""

from dataclasses import dataclass, field
import logging
from pathlib import Path
import time
from typing import Any, Dict, Iterator, List, Optional, Union

from dvbs2_analyzer.config import (
    CODE_DIR,
    PROJECT_ROOT,
    RAW_DATA_DIR,
    StreamFormat,
)
from dvbs2_analyzer.ingestion.chunk_reader import ChunkReader
from dvbs2_analyzer.ingestion.stream_handler import StreamHandler, detect_stream_format, _resolve_stream_path
from dvbs2_analyzer.parsers.base import BaseStreamParser
from dvbs2_analyzer.parsers.ts_parser import TSParser
from dvbs2_analyzer.parsers.gse_parser import GSEParser
from dvbs2_analyzer.parsers.bbframe_parser import BBFrameParser
from dvbs2_analyzer.analysis.timeline import (
    TimelineGenerator,
    TimelineConfig,
    StreamTimeline,
)
from dvbs2_analyzer.analysis.explanation import (
    AnomalyExplanationEngine,
    ExplanationConfig,
    ExplanationReport,
)
from dvbs2_analyzer.analysis.report import (
    AutomaticAnalysisReport,
    AutomaticReportGenerator,
    ReportConfig,
)

logger = logging.getLogger(__name__)


@dataclass
class StreamingEngineConfig:
    """Configuration options for the High-Throughput Streaming Engine."""
    chunk_size: int = 65536
    use_mmap: bool = False
    strict_mode: bool = False
    ts_window_size: int = 200
    gse_window_size: int = 3
    bbframe_window_size: int = 50
    f2_contamination: float = 0.05
    f2_anomaly_threshold: float = 0.50


@dataclass
class StreamingPipelineResult:
    """Structured analytical telemetry returned by the streaming engine."""
    success: bool
    stream_name: str
    file_size_bytes: int
    detected_format: StreamFormat
    total_units: int
    total_payload_bytes: int
    total_windows: int
    window_size: int
    elapsed_seconds: float
    throughput_mibs: float
    timeline: StreamTimeline
    explanation_report: ExplanationReport
    report: AutomaticAnalysisReport
    summary_dict: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Serializes complete analytical telemetry to JSON-compatible dictionary."""
        return self.summary_dict


class HighThroughputStreamingEngine:
    """
    High-Throughput Streaming Engine for DVB-S2 multi-format receiver output streams.

    Processes large binary streams incrementally while preserving 100% exact
    analytical equivalence with the authoritative frozen backend algorithms.
    """

    def __init__(self, config: Optional[StreamingEngineConfig] = None):
        self.config = config or StreamingEngineConfig()
        self.tl_gen = TimelineGenerator(TimelineConfig(
            ts_window_size=self.config.ts_window_size,
            gse_window_size=self.config.gse_window_size,
            bbframe_window_size=self.config.bbframe_window_size,
            f2_contamination=self.config.f2_contamination,
            f2_anomaly_threshold=self.config.f2_anomaly_threshold,
        ))
        self.expl_engine = AnomalyExplanationEngine(ExplanationConfig())
        self.report_gen = AutomaticReportGenerator(ReportConfig())

    def get_parser(self, format_enum: StreamFormat) -> BaseStreamParser:
        """Instantiates format parser configured with strict_mode setting."""
        if format_enum == StreamFormat.MPEG_TS:
            return TSParser(strict_mode=self.config.strict_mode)
        elif format_enum == StreamFormat.GSE:
            return GSEParser(strict_mode=self.config.strict_mode)
        elif format_enum == StreamFormat.BB_FRAME:
            return BBFrameParser(strict_mode=self.config.strict_mode)
        else:
            raise ValueError(f"Unsupported stream format: {format_enum}")

    def stream_units(
        self,
        source: Union[str, Path, bytes],
        format_enum: Optional[StreamFormat] = None,
        chunk_size: Optional[int] = None,
        use_mmap: Optional[bool] = None,
    ) -> Iterator[Any]:
        """
        Yields decoded framing units incrementally directly from binary chunks.

        Args:
            source: Path to stream file or raw binary bytes.
            format_enum: Explicit format or None to autodetect.
            chunk_size: Override chunk size in bytes.
            use_mmap: Override memory-mapped I/O preference.

        Yields:
            Decoded TSPacket, GSEPDU, or BBFrame instances.
        """
        c_size = chunk_size or self.config.chunk_size
        mmap_pref = self.config.use_mmap if use_mmap is None else use_mmap

        if isinstance(source, (str, Path)):
            path = _resolve_stream_path(source)
            if not path.exists():
                raise FileNotFoundError(f"Stream file not found: {path}")
            if format_enum is None:
                format_enum = detect_stream_format(path)
            reader = ChunkReader(path, chunk_size=c_size, use_mmap=mmap_pref)
        else:
            if format_enum is None:
                raise ValueError("format_enum must be specified when source is raw bytes")
            reader = ChunkReader(source, chunk_size=c_size)

        parser = self.get_parser(format_enum)
        with reader:
            yield from parser.parse_chunks(reader)

    def analyze_stream(
        self,
        source: Union[str, Path, bytes],
        forced_format: Optional[Union[str, StreamFormat]] = None,
        window_size: Optional[int] = None,
        chunk_size: Optional[int] = None,
        use_mmap: Optional[bool] = None,
        stream_name: Optional[str] = None,
    ) -> StreamingPipelineResult:
        """
        Executes complete end-to-end analytical pipeline (F1-F5 + F7) in high-throughput mode.

        Args:
            source: Path to stream file or raw binary bytes.
            forced_format: Optional format override (str or StreamFormat).
            window_size: Optional window size in units.
            chunk_size: Optional chunk size in bytes.
            use_mmap: Optional mmap flag.
            stream_name: Optional descriptive stream identifier.

        Returns:
            StreamingPipelineResult with full analytical telemetry.
        """
        t_start = time.perf_counter()
        c_size = chunk_size or self.config.chunk_size
        mmap_pref = self.config.use_mmap if use_mmap is None else use_mmap

        if isinstance(source, (str, Path)):
            path = _resolve_stream_path(source)
            if not path.exists():
                raise FileNotFoundError(f"Stream file not found: {path}")
            name = stream_name or path.name
            size_bytes = path.stat().st_size
            if forced_format and str(forced_format) != "AUTO":
                fmt = StreamFormat(forced_format) if isinstance(forced_format, str) else forced_format
            else:
                fmt = detect_stream_format(path)
            reader_source = path
        else:
            name = stream_name or "in_memory_stream"
            size_bytes = len(source)
            if not forced_format or str(forced_format) == "AUTO":
                raise ValueError("forced_format is required when analyzing in-memory bytes")
            fmt = StreamFormat(forced_format) if isinstance(forced_format, str) else forced_format
            reader_source = source
            mmap_pref = False # mmap only applies to file paths

        # Resolve window size
        if window_size is None or window_size <= 0:
            if fmt == StreamFormat.MPEG_TS:
                win_size = self.config.ts_window_size
            elif fmt == StreamFormat.GSE:
                win_size = self.config.gse_window_size
            elif fmt == StreamFormat.BB_FRAME:
                win_size = self.config.bbframe_window_size
            else:
                win_size = 50
        else:
            win_size = int(window_size)

        # Execute timeline generation from streaming chunks
        with ChunkReader(reader_source, chunk_size=c_size, use_mmap=mmap_pref) as reader:
            timeline = self.tl_gen.generate_from_chunks(
                chunks=reader,
                format=fmt,
                window_size=win_size,
                stream_name=name,
                strict_mode=self.config.strict_mode,
            )

        # F5 Explanation
        explanation_report = self.expl_engine.explain_timeline(timeline)

        # F7 Synthesis Report
        file_path_for_report = Path(reader_source) if isinstance(reader_source, (str, Path)) else Path(name)
        report = self.report_gen.generate_from_timeline(
            timeline=timeline,
            explanation_report=explanation_report,
            comparison_report=None,
            stream_path=file_path_for_report,
            file_size_bytes=size_bytes,
        )

        elapsed = time.perf_counter() - t_start
        throughput = (size_bytes / (1024.0 * 1024.0)) / elapsed if elapsed > 0 else 0.0

        # Construct summary telemetry matching AnalysisCoordinator schema
        anom_pts = [p for p in timeline.points if p.is_anomaly]
        trans_pts = [p for p in timeline.points if p.has_transition]

        f1_summary = {
            "overall_health_score": round(timeline.summary_stats.get("avg_health_score", 100.0), 2),
            "health_status": "HEALTHY" if timeline.summary_stats.get("avg_health_score", 100.0) >= 80.0 else "WARNING",
            "total_errors": timeline.summary_stats.get("total_errors", 0),
            "total_units": timeline.total_units,
            "error_rate": round(timeline.summary_stats.get("total_errors", 0) / timeline.total_units, 6) if timeline.total_units > 0 else 0.0,
        }
        f2_summary = {
            "total_anomalies_detected": len(anom_pts),
            "anomalous_windows": [w.window_index for w in anom_pts],
            "peak_anomaly_score": round(max([w.anomaly_score for w in timeline.points], default=0.0), 4),
            "anomaly_threshold": timeline.anomaly_threshold,
            "anomaly_rate_pct": round(len(anom_pts) / max(timeline.total_windows, 1) * 100.0, 2),
        }
        f3_summary = {
            "total_transitions": len(trans_pts),
            "transition_windows": [w.window_index for w in trans_pts],
        }

        full_telemetry = {
            "success": True,
            "stream_info": {
                "file_name": name,
                "file_size_bytes": size_bytes,
                "file_size_kb": round(size_bytes / 1024.0, 2),
                "detected_format": fmt.value,
                "total_units": timeline.total_units,
                "total_payload_bytes": timeline.total_bytes,
                "total_payload_kb": round(timeline.total_bytes / 1024.0, 2),
                "window_size": win_size,
                "total_windows": timeline.total_windows,
                "elapsed_seconds": round(elapsed, 4),
                "throughput_mibs": round(throughput, 2),
            },
            "f1_health": f1_summary,
            "f2_anomalies": f2_summary,
            "f3_patterns": f3_summary,
            "f4_timeline": timeline.to_dict(),
            "f5_explanations": explanation_report.to_dict(),
            "f7_report": report.to_dict(),
            "report_renders": {
                "markdown": report.render_markdown(),
                "text": report.render_text(),
                "html": report.render_html(),
            },
        }

        return StreamingPipelineResult(
            success=True,
            stream_name=name,
            file_size_bytes=size_bytes,
            detected_format=fmt,
            total_units=timeline.total_units,
            total_payload_bytes=timeline.total_bytes,
            total_windows=timeline.total_windows,
            window_size=win_size,
            elapsed_seconds=elapsed,
            throughput_mibs=throughput,
            timeline=timeline,
            explanation_report=explanation_report,
            report=report,
            summary_dict=full_telemetry,
        )
