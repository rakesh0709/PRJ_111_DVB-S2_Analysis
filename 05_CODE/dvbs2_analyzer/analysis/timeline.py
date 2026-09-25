"""
Timeline & Activity Visualization Engine for PRJ_111 (Feature F4).

Constructs a sequential, visualization-ready temporal and activity representation
of DVB-S2 receiver output streams across MPEG-TS, GSE, and BBFrame formats.

Architectural Principles:
1. Alternative Formats: MPEG-TS, GSE, and BBFrame remain alternative input streams.
   There is NO sequential BBFrame -> GSE -> TS conversion pipeline.
2. Grounded Physical Coordinates: Timeline positions are indexed strictly by physical
   stream offsets (window index, unit offset range, byte offset range).
   No fake timestamps are fabricated.
3. No Fake Throughput: Payload volume is reported as payload_bytes / payload_kb,
   strictly avoiding unsubstantiated throughput rates (e.g. KB/s).
4. Unified Multi-Feature Synthesis: Integrates F1 Health scores, F2 Anomaly scores
   and feature deviation drivers, and F3 Pattern detections and transition events.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
import json
import logging
import math
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple, Union

from dvbs2_analyzer.analysis.anomaly import (
    AnomalyConfig,
    AnomalyDetector,
    AnomalyResult,
)
from dvbs2_analyzer.analysis.explanation import (
    AnomalyExplanation,
    AnomalyExplanationEngine,
)
from dvbs2_analyzer.analysis.health import (
    HealthAnalyzer,
    HealthClassification,
    HealthThresholds,
)
from dvbs2_analyzer.analysis.patterns import (
    PatternConfig,
    PatternDetector,
    PatternFinding,
    PatternResult,
    PatternType,
    TS_WELL_KNOWN_PIDS,
)
from dvbs2_analyzer.config import StreamFormat
from dvbs2_analyzer.features.extractor import (
    CommonMetrics,
    FeatureExtractor,
    StreamFeatureSet,
    UnifiedStreamFeatureSet,
)
from dvbs2_analyzer.ingestion.stream_handler import StreamHandler
from dvbs2_analyzer.parsers.bbframe_parser import BBFrame, BBFrameStreamStatistics
from dvbs2_analyzer.parsers.gse_parser import GSEPDU, GSEStreamStatistics
from dvbs2_analyzer.parsers.ts_parser import TSPacket, TSStreamStatistics

logger = logging.getLogger(__name__)


# =============================================================================
# 1. Timeline Data Structures
# =============================================================================

@dataclass
class TimelineEvent:
    """
    A discrete event occurring within a specific window of the stream timeline.
    Represents anomaly detections, structural transitions, or health warnings.
    """
    event_id: str
    window_index: int
    unit_offset_start: int
    unit_offset_end: int
    byte_offset_start: int
    byte_offset_end: int
    event_type: str            # "F2_ANOMALY", "F3_TRANSITION", "HEALTH_WARNING", "HEALTH_CRITICAL"
    severity: str              # "INFO", "LOW", "MEDIUM", "HIGH", "CRITICAL"
    title: str
    description: str
    metrics: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Serializes timeline event to dictionary."""
        return {
            "event_id": self.event_id,
            "window_index": self.window_index,
            "unit_offset_start": self.unit_offset_start,
            "unit_offset_end": self.unit_offset_end,
            "byte_offset_start": self.byte_offset_start,
            "byte_offset_end": self.byte_offset_end,
            "event_type": self.event_type,
            "severity": self.severity,
            "title": self.title,
            "description": self.description,
            "metrics": self.metrics,
        }


@dataclass
class TimelinePoint:
    """
    Structured snapshot for an individual sequential window along the timeline.
    Combines F1 Health, F2 Anomaly, and F3 Pattern telemetry.
    """
    window_index: int
    unit_offset_start: int     # 0-indexed packet / PDU / frame start
    unit_offset_end: int       # Exclusive end index
    byte_offset_start: int     # Byte position start in raw stream
    byte_offset_end: int       # Byte position end in raw stream
    unit_count: int
    valid_units: int
    invalid_units: int
    payload_bytes: int
    payload_kb: float          # Payload volume in Kilobytes (NOT KB/s rate)
    unit_density: int          # Units per window

    # Feature F1: Health Analysis
    health_score: float        # 0.0 to 100.0 score
    health_status: str         # "HEALTHY", "WARNING", "CRITICAL"
    error_count: int
    error_rate: float

    # Feature F2: AI Anomaly Detection
    is_anomaly: bool
    anomaly_score: float       # Normalized [0.0, 1.0] score
    anomaly_severity: str      # "NORMAL", "LOW", "MEDIUM", "HIGH", "CRITICAL"
    anomaly_explanation: str
    top_deviations: List[Dict[str, Any]] = field(default_factory=list)

    # Feature F3: Stream Pattern Findings & Transitions
    pattern_findings: List[Dict[str, Any]] = field(default_factory=list)
    has_transition: bool = False
    transition_description: Optional[str] = None

    # Format-Specific Telemetry
    format_specific_metrics: Dict[str, Any] = field(default_factory=dict)

    # Discrete Events originating in this window
    events: List[TimelineEvent] = field(default_factory=list)

    # Feature F5: Detailed Anomaly Explanation
    explanation: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Serializes timeline point to dictionary."""
        return {
            "window_index": self.window_index,
            "unit_offset_start": self.unit_offset_start,
            "unit_offset_end": self.unit_offset_end,
            "byte_offset_start": self.byte_offset_start,
            "byte_offset_end": self.byte_offset_end,
            "unit_count": self.unit_count,
            "valid_units": self.valid_units,
            "invalid_units": self.invalid_units,
            "payload_bytes": self.payload_bytes,
            "payload_kb": round(self.payload_kb, 3),
            "unit_density": self.unit_density,
            "health_score": round(self.health_score, 2),
            "health_status": self.health_status,
            "error_count": self.error_count,
            "error_rate": round(self.error_rate, 6),
            "is_anomaly": self.is_anomaly,
            "anomaly_score": round(self.anomaly_score, 4),
            "anomaly_severity": self.anomaly_severity,
            "anomaly_explanation": self.anomaly_explanation,
            "top_deviations": self.top_deviations,
            "pattern_findings": self.pattern_findings,
            "has_transition": self.has_transition,
            "transition_description": self.transition_description,
            "format_specific_metrics": self.format_specific_metrics,
            "events": [e.to_dict() for e in self.events],
            "explanation": self.explanation,
        }


@dataclass
class TimelineSeries:
    """Extracted 1D numerical metric series for plotting / graphing."""
    name: str
    unit: str
    values: List[float]
    window_indices: List[int]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "unit": self.unit,
            "values": [round(v, 4) for v in self.values],
            "window_indices": self.window_indices,
        }


@dataclass
class StreamTimeline:
    """
    Top-level timeline container for an analyzed stream.
    Provides metric time-series extraction, structured JSON serialization,
    and rendering utilities for dashboards.
    """
    stream_name: str
    format: StreamFormat
    total_units: int
    total_bytes: int
    window_size: int
    total_windows: int
    anomaly_threshold: float   # Directly consumed from F2 configuration
    points: List[TimelinePoint] = field(default_factory=list)
    events: List[TimelineEvent] = field(default_factory=list)
    summary_stats: Dict[str, Any] = field(default_factory=dict)
    generation_timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def get_series(self, metric_name: str) -> TimelineSeries:
        """
        Extracts a 1D numerical series for a named metric across all windows.
        Supported metrics:
          - 'health_score': Stream health (0..100)
          - 'anomaly_score': Anomaly score (0..1)
          - 'payload_kb': Payload volume (KB)
          - 'error_rate': Transmission error rate (0..1)
          - 'error_count': Total error count
          - format-specific metrics (e.g. 'pid_entropy', 'fragmentation_ratio', 'modal_dfl')
        """
        values: List[float] = []
        indices: List[int] = []
        unit = ""

        if metric_name == "health_score":
            unit = "score (0-100)"
            values = [p.health_score for p in self.points]
        elif metric_name == "anomaly_score":
            unit = "score (0.0-1.0)"
            values = [p.anomaly_score for p in self.points]
        elif metric_name == "payload_kb":
            unit = "KB"
            values = [p.payload_kb for p in self.points]
        elif metric_name == "error_rate":
            unit = "ratio"
            values = [p.error_rate for p in self.points]
        elif metric_name == "error_count":
            unit = "units"
            values = [float(p.error_count) for p in self.points]
        else:
            # Check format-specific metrics
            for p in self.points:
                val = p.format_specific_metrics.get(metric_name, 0.0)
                if isinstance(val, (int, float)):
                    values.append(float(val))
                else:
                    values.append(0.0)
            unit = "value"

        indices = [p.window_index for p in self.points]
        return TimelineSeries(name=metric_name, unit=unit, values=values, window_indices=indices)

    def to_dict(self) -> Dict[str, Any]:
        """Converts timeline into a complete JSON-ready dictionary."""
        return {
            "stream_name": self.stream_name,
            "format": self.format.value if hasattr(self.format, "value") else str(self.format),
            "total_units": self.total_units,
            "total_bytes": self.total_bytes,
            "window_size": self.window_size,
            "total_windows": self.total_windows,
            "anomaly_threshold": round(self.anomaly_threshold, 4),
            "generation_timestamp": self.generation_timestamp,
            "summary_stats": self.summary_stats,
            "points": [p.to_dict() for p in self.points],
            "events": [e.to_dict() for e in self.events],
        }

    def to_json(self, indent: int = 2) -> str:
        """Serializes timeline to formatted JSON string."""
        return json.dumps(self.to_dict(), indent=indent)

    def render_ascii_summary(self) -> str:
        """
        Renders a clean text-based terminal visualization of timeline progression.
        """
        fmt_str = self.format.value if hasattr(self.format, "value") else str(self.format)
        lines = [
            "=" * 78,
            f" PRJ_111: STREAM TIMELINE & ACTIVITY SUMMARY",
            f" Stream: {self.stream_name} | Format: {fmt_str}",
            f" Total Units: {self.total_units:,} | Windows: {self.total_windows} | Window Size: {self.window_size}",
            f" F2 Anomaly Threshold: {self.anomaly_threshold:.2f} | Total Events: {len(self.events)}",
            "=" * 78,
            f"{'Win':>4} | {'Unit Range':>13} | {'Payload':>9} | {'Health':>7} | {'Status':>8} | {'Anomaly':>7} | {'Tier':>8} | {'Events'}",
            "-" * 78,
        ]

        for p in self.points:
            unit_range = f"[{p.unit_offset_start}..{p.unit_offset_end})"
            payload_str = f"{p.payload_kb:.1f} KB"
            event_badges = []
            if p.is_anomaly:
                event_badges.append(f"[ANOMALY: {p.anomaly_severity}]")
            if p.has_transition:
                event_badges.append("[TRANSITION]")
            if p.health_status in ("WARNING", "CRITICAL"):
                event_badges.append(f"[{p.health_status}]")
            badge_str = " ".join(event_badges) if event_badges else "-"

            lines.append(
                f"{p.window_index:4d} | {unit_range:>13} | {payload_str:>9} | "
                f"{p.health_score:6.1f}% | {p.health_status:>8} | "
                f"{p.anomaly_score:7.4f} | {p.anomaly_severity:>8} | {badge_str}"
            )

        if self.events:
            lines.append("-" * 78)
            lines.append(f"TIMELINE EVENT LOG ({len(self.events)} Events):")
            for e in self.events:
                lines.append(
                    f"  * [Win {e.window_index:2d}] [{e.event_type} - {e.severity}] "
                    f"{e.title}: {e.description}"
                )

        lines.append("=" * 78)
        return "\n".join(lines)

    def render_html_dashboard(self, output_path: Optional[Union[str, Path]] = None) -> str:
        """
        Renders the timeline into a modern, self-contained interactive HTML dashboard.
        """
        from dvbs2_analyzer.visualization.dashboard import generate_html_dashboard
        html = generate_html_dashboard(self)
        if output_path:
            out_file = Path(output_path).resolve()
            out_file.parent.mkdir(parents=True, exist_ok=True)
            out_file.write_text(html, encoding="utf-8")
            logger.info("Saved timeline HTML dashboard to %s", out_file)
        return html


# =============================================================================
# 2. Timeline Configuration
# =============================================================================

@dataclass
class TimelineConfig:
    """Configuration parameters for Feature F4 Timeline Generation."""
    ts_window_size: int = 200
    gse_window_size: int = 3
    bbframe_window_size: int = 50
    f2_contamination: float = 0.05
    f2_anomaly_threshold: float = 0.50
    health_thresholds: Optional[HealthThresholds] = None


# =============================================================================
# 3. Timeline Generator Engine
# =============================================================================

class TimelineGenerator:
    """
    Feature F4 Engine: Orchestrates stream windowing and synthesizes
    Feature F1 (Health), Feature F2 (Anomaly), and Feature F3 (Patterns)
    into a unified StreamTimeline.
    """

    def __init__(self, config: Optional[TimelineConfig] = None):
        self.config = config or TimelineConfig()
        self.feature_extractor = FeatureExtractor()
        self.health_analyzer = HealthAnalyzer(thresholds=self.config.health_thresholds)
        self.pattern_detector = PatternDetector()
        self.explanation_engine = AnomalyExplanationEngine()

    # -------------------------------------------------------------------------
    # MPEG-TS Timeline Generation
    # -------------------------------------------------------------------------

    def generate_ts_timeline(
        self,
        packets: Sequence[TSPacket],
        window_size: Optional[int] = None,
        stream_name: str = "MPEG-TS Stream"
    ) -> StreamTimeline:
        """
        Generates a complete sequential timeline for an MPEG-TS packet stream.
        """
        win_size = window_size or self.config.ts_window_size
        total_packets = len(packets)
        total_bytes = total_packets * 188 # ISO/IEC 13818-1 fixed 188-byte framing

        if total_packets == 0:
            return StreamTimeline(
                stream_name=stream_name,
                format=StreamFormat.MPEG_TS,
                total_units=0,
                total_bytes=0,
                window_size=win_size,
                total_windows=0,
                anomaly_threshold=0.50,
            )

        # 1. Slicing into ordered telemetry windows and feature extraction
        window_chunks: List[Sequence[TSPacket]] = []
        window_stats: List[TSStreamStatistics] = []
        window_features: List[UnifiedStreamFeatureSet] = []

        for start in range(0, total_packets, win_size):
            chunk = packets[start:start + win_size]
            window_chunks.append(chunk)

            # Build statistics for this window
            stats = TSStreamStatistics()
            stats.total_packets = len(chunk)
            stats.total_bytes_read = len(chunk) * 188
            for pkt in chunk:
                if pkt.sync_byte == 0x47:
                    stats.valid_sync_packets += 1
                else:
                    stats.sync_byte_errors += 1
                if pkt.tei:
                    stats.tei_error_count += 1
                if pkt.is_null_packet:
                    stats.null_packet_count += 1
                if pkt.has_payload:
                    stats.payload_packet_count += 1
                if pkt.has_adaptation_field:
                    stats.adaptation_field_count += 1
                stats.total_payload_bytes += len(pkt.payload)
                stats.pid_counts[pkt.pid] += 1

            window_stats.append(stats)
            meta = {
                "window_index": len(window_features),
                "window_size": len(chunk),
                "unit_offset_start": start,
                "unit_offset_end": start + len(chunk),
            }
            feat = self.feature_extractor.extract_unified(
                stats, format=StreamFormat.MPEG_TS, metadata=meta
            )
            window_features.append(feat)

        # 2. Fit Feature F2 Anomaly Detector on baseline windows
        # Consumes the detector's configured anomaly threshold
        detector = AnomalyDetector(
            AnomalyConfig(
                format=StreamFormat.MPEG_TS,
                contamination=self.config.f2_contamination,
                random_state=42,
                anomaly_threshold=self.config.f2_anomaly_threshold,
            )
        )
        if len(window_features) >= 2:
            detector.fit(window_features)
        anomaly_threshold = detector.anomaly_threshold

        # 3. Process each window with F1, F2, and F3
        points: List[TimelinePoint] = []
        events: List[TimelineEvent] = []

        for w_idx, chunk in enumerate(window_chunks):
            feat = window_features[w_idx]
            stats = window_stats[w_idx]
            start_unit = w_idx * win_size
            end_unit = start_unit + len(chunk)
            byte_start = start_unit * 188
            byte_end = end_unit * 188

            # F1: Health Evaluation
            ts_feat = self.feature_extractor.extract_from_ts_stats(stats)
            f1_report = self.health_analyzer.evaluate_features(ts_feat)
            health_score = f1_report.overall_score
            health_status = f1_report.health_status.value

            # F2: Anomaly Evaluation
            if detector.is_fitted:
                anom_res = detector.predict_sample(feat, window_index=w_idx)
            else:
                anom_res = AnomalyResult(
                    is_anomaly=False,
                    anomaly_score=0.20,
                    raw_score=0.20,
                    severity="NORMAL",
                    top_deviations=[],
                    summary_explanation="Insufficient windows to fit anomaly baseline",
                    feature_values={},
                    window_index=w_idx,
                )

            # F3: Pattern Evaluation
            pat_res = self.pattern_detector.analyze_ts_window(chunk, window_idx=w_idx)

            # Format-Specific Telemetry (without unestablished video/audio role claims)
            ts_specific = feat.ts_specific
            dom_pid = pat_res.metrics_summary.get("dominant_pid")
            dom_pct = 0.0
            if dom_pid is not None and stats.total_packets > 0:
                dom_pct = (stats.pid_counts[dom_pid] / stats.total_packets) * 100.0

            dominant_pid_str = f"PID {dom_pid} ({dom_pct:.1f}%)" if dom_pid is not None else "None"

            fmt_metrics = {
                "pid_entropy": round(ts_specific.pid_entropy if ts_specific else 0.0, 4),
                "null_packet_ratio": round(ts_specific.null_packet_ratio if ts_specific else 0.0, 4),
                "tei_error_rate": round(ts_specific.tei_error_rate if ts_specific else 0.0, 6),
                "continuity_error_rate": round(ts_specific.continuity_error_rate if ts_specific else 0.0, 6),
                "unique_pids": ts_specific.unique_pid_count if ts_specific else 0,
                "dominant_pid": dom_pid,
                "dominant_pid_pct": round(dom_pct, 2),
                "dominant_pid_summary": dominant_pid_str,
            }

            point_events: List[TimelineEvent] = []

            # Feature F5: Structured Domain-Safe Anomaly Explanation
            expl_dict = None
            expl_summary = anom_res.summary_explanation
            if anom_res.is_anomaly:
                expl = self.explanation_engine.explain_anomaly(
                    anomaly_result=anom_res,
                    pattern_result=pat_res,
                    window_offsets=(start_unit, end_unit, byte_start, byte_end),
                    timeline_event_id=f"EV_TS_ANOM_{w_idx}",
                    stream_format=StreamFormat.MPEG_TS,
                )
                expl_dict = expl.to_dict()
                expl_summary = expl.concise_summary

            # Check for F2 Anomaly Event
            if anom_res.is_anomaly:
                ev = TimelineEvent(
                    event_id=f"EV_TS_ANOM_{w_idx}",
                    window_index=w_idx,
                    unit_offset_start=start_unit,
                    unit_offset_end=end_unit,
                    byte_offset_start=byte_start,
                    byte_offset_end=byte_end,
                    event_type="F2_ANOMALY",
                    severity=anom_res.severity,
                    title=f"Anomaly Detected ({anom_res.severity})",
                    description=expl_summary,
                    metrics={"anomaly_score": anom_res.anomaly_score, "explanation": expl_dict} if expl_dict else {"anomaly_score": anom_res.anomaly_score},
                )
                point_events.append(ev)
                events.append(ev)

            # Check for F1 Critical/Warning Health Events
            if health_status in ("CRITICAL", "WARNING"):
                ev = TimelineEvent(
                    event_id=f"EV_TS_HLTH_{w_idx}",
                    window_index=w_idx,
                    unit_offset_start=start_unit,
                    unit_offset_end=end_unit,
                    byte_offset_start=byte_start,
                    byte_offset_end=byte_end,
                    event_type=f"HEALTH_{health_status}",
                    severity="CRITICAL" if health_status == "CRITICAL" else "MEDIUM",
                    title=f"Health Degradation: {health_status}",
                    description="; ".join(f1_report.issues[:2]) if f1_report.issues else "Degraded health",
                    metrics={"health_score": health_score},
                )
                point_events.append(ev)
                events.append(ev)

            pt = TimelinePoint(
                window_index=w_idx,
                unit_offset_start=start_unit,
                unit_offset_end=end_unit,
                byte_offset_start=byte_start,
                byte_offset_end=byte_end,
                unit_count=len(chunk),
                valid_units=stats.valid_sync_packets,
                invalid_units=stats.sync_byte_errors,
                payload_bytes=stats.total_payload_bytes,
                payload_kb=stats.total_payload_bytes / 1024.0,
                unit_density=len(chunk),
                health_score=health_score,
                health_status=health_status,
                error_count=stats.tei_error_count + stats.sync_byte_errors,
                error_rate=feat.common.error_rate,
                is_anomaly=anom_res.is_anomaly,
                anomaly_score=anom_res.anomaly_score,
                anomaly_severity=anom_res.severity,
                anomaly_explanation=expl_summary,
                top_deviations=[d.to_dict() for d in anom_res.top_deviations[:3]],
                pattern_findings=[f.to_dict() for f in pat_res.findings],
                has_transition=False,
                transition_description=None,
                format_specific_metrics=fmt_metrics,
                events=point_events,
                explanation=expl_dict,
            )
            points.append(pt)

        # 4. Cross-window transition tracking (e.g. dominant PID shifts or major concentration jumps)
        for i in range(1, len(points)):
            prev = points[i - 1]
            curr = points[i]
            prev_pid = prev.format_specific_metrics.get("dominant_pid")
            curr_pid = curr.format_specific_metrics.get("dominant_pid")
            prev_pct = prev.format_specific_metrics.get("dominant_pid_pct", 0.0)
            curr_pct = curr.format_specific_metrics.get("dominant_pid_pct", 0.0)

            is_transition = False
            trans_desc = ""

            if prev_pid is not None and curr_pid is not None and prev_pid != curr_pid:
                is_transition = True
                trans_desc = f"Dominant stream shifted from PID {prev_pid} ({prev_pct:.1f}%) to PID {curr_pid} ({curr_pct:.1f}%)"
            elif prev_pid is not None and curr_pid is not None and abs(curr_pct - prev_pct) >= 25.0:
                is_transition = True
                trans_desc = f"Dominant PID {curr_pid} concentration shifted significantly from {prev_pct:.1f}% to {curr_pct:.1f}%"

            if is_transition:
                curr.has_transition = True
                curr.transition_description = trans_desc
                ev = TimelineEvent(
                    event_id=f"EV_TS_TRANS_{curr.window_index}",
                    window_index=curr.window_index,
                    unit_offset_start=curr.unit_offset_start,
                    unit_offset_end=curr.unit_offset_end,
                    byte_offset_start=curr.byte_offset_start,
                    byte_offset_end=curr.byte_offset_end,
                    event_type="F3_TRANSITION",
                    severity="LOW",
                    title="Stream Pattern Transition",
                    description=trans_desc,
                )
                curr.events.append(ev)
                events.append(ev)

        summary_stats = {
            "mean_health_score": round(sum(p.health_score for p in points) / len(points), 2),
            "peak_anomaly_score": round(max(p.anomaly_score for p in points), 4),
            "anomaly_window_count": sum(1 for p in points if p.is_anomaly),
            "transition_count": sum(1 for p in points if p.has_transition),
            "total_payload_kb": round(sum(p.payload_kb for p in points), 2),
        }

        return StreamTimeline(
            stream_name=stream_name,
            format=StreamFormat.MPEG_TS,
            total_units=total_packets,
            total_bytes=total_bytes,
            window_size=win_size,
            total_windows=len(points),
            anomaly_threshold=anomaly_threshold,
            points=points,
            events=events,
            summary_stats=summary_stats,
        )

    # -------------------------------------------------------------------------
    # GSE Timeline Generation
    # -------------------------------------------------------------------------

    def generate_gse_timeline(
        self,
        pdus: Sequence[GSEPDU],
        window_size: Optional[int] = None,
        stream_name: str = "GSE Stream"
    ) -> StreamTimeline:
        """
        Generates a complete sequential timeline for a GSE stream.
        """
        win_size = window_size or self.config.gse_window_size
        total_pdus = len(pdus)
        total_bytes = sum(len(p.raw_bytes) for p in pdus)

        if total_pdus == 0:
            return StreamTimeline(
                stream_name=stream_name,
                format=StreamFormat.GSE,
                total_units=0,
                total_bytes=0,
                window_size=win_size,
                total_windows=0,
                anomaly_threshold=0.50,
            )

        window_chunks: List[Sequence[GSEPDU]] = []
        window_stats: List[GSEStreamStatistics] = []
        window_features: List[UnifiedStreamFeatureSet] = []
        byte_offsets: List[Tuple[int, int]] = []

        curr_byte = 0
        for start in range(0, total_pdus, win_size):
            chunk = pdus[start:start + win_size]
            window_chunks.append(chunk)

            chunk_bytes = sum(len(p.raw_bytes) for p in chunk)
            byte_offsets.append((curr_byte, curr_byte + chunk_bytes))
            curr_byte += chunk_bytes

            stats = GSEStreamStatistics()
            stats.total_pdus = len(chunk)
            stats.valid_pdus = len(chunk)
            stats.total_bytes_read = chunk_bytes
            for p in chunk:
                stats.total_payload_bytes += p.payload_length
                stats.protocol_type_counts[p.protocol_name] += 1
                if p.is_padding:
                    stats.padding_packets += 1
                elif p.is_unfragmented:
                    stats.unfragmented_pdus += 1
                elif p.is_first_fragment:
                    stats.first_fragments += 1
                elif p.is_intermediate_fragment:
                    stats.intermediate_fragments += 1
                elif p.is_last_fragment:
                    stats.last_fragments += 1

            window_stats.append(stats)
            meta = {
                "window_index": len(window_features),
                "window_size": len(chunk),
                "unit_offset_start": start,
                "unit_offset_end": start + len(chunk),
            }
            feat = self.feature_extractor.extract_unified(
                stats, format=StreamFormat.GSE, metadata=meta
            )
            window_features.append(feat)

        # Fit F2 Anomaly Detector on GSE windows
        detector = AnomalyDetector(
            AnomalyConfig(
                format=StreamFormat.GSE,
                contamination=self.config.f2_contamination,
                random_state=42,
                anomaly_threshold=self.config.f2_anomaly_threshold,
            )
        )
        if len(window_features) >= 2:
            detector.fit(window_features)
        anomaly_threshold = detector.anomaly_threshold

        points: List[TimelinePoint] = []
        events: List[TimelineEvent] = []

        for w_idx, chunk in enumerate(window_chunks):
            feat = window_features[w_idx]
            stats = window_stats[w_idx]
            start_unit = w_idx * win_size
            end_unit = start_unit + len(chunk)
            b_start, b_end = byte_offsets[w_idx]

            # F1 Health Calculation for GSE
            # Perfect valid PDUs = 100.0, penalty for malformed / truncations
            integrity = feat.common.integrity_ratio
            error_rate = feat.common.error_rate
            health_score = max(0.0, 100.0 * integrity - 50.0 * error_rate)
            if health_score >= 90.0:
                health_status = "HEALTHY"
            elif health_score >= 70.0:
                health_status = "WARNING"
            else:
                health_status = "CRITICAL"

            # F2 Anomaly Evaluation
            if detector.is_fitted:
                anom_res = detector.predict_sample(feat, window_index=w_idx)
            else:
                anom_res = AnomalyResult(
                    is_anomaly=False,
                    anomaly_score=0.20,
                    raw_score=0.20,
                    severity="NORMAL",
                    top_deviations=[],
                    summary_explanation="Insufficient windows to fit anomaly baseline",
                    feature_values={},
                    window_index=w_idx,
                )

            # F3 Pattern Evaluation
            pat_res = self.pattern_detector.analyze_gse_window(chunk, window_idx=w_idx)

            gse_spec = feat.gse_specific
            fmt_metrics = {
                "dominant_protocol": pat_res.metrics_summary.get("dominant_protocol", "UNKNOWN"),
                "fragmentation_ratio": round(gse_spec.fragmentation_ratio if gse_spec else 0.0, 4),
                "mean_pdu_size_bytes": round(pat_res.metrics_summary.get("mean_size_bytes", 0.0), 2),
                "padding_packets": stats.padding_packets,
            }

            point_events: List[TimelineEvent] = []

            # Feature F5: Structured Domain-Safe Anomaly Explanation
            expl_dict = None
            expl_summary = anom_res.summary_explanation
            if anom_res.is_anomaly:
                expl = self.explanation_engine.explain_anomaly(
                    anomaly_result=anom_res,
                    pattern_result=pat_res,
                    window_offsets=(start_unit, end_unit, b_start, b_end),
                    timeline_event_id=f"EV_GSE_ANOM_{w_idx}",
                    stream_format=StreamFormat.GSE,
                )
                expl_dict = expl.to_dict()
                expl_summary = expl.concise_summary

            if anom_res.is_anomaly:
                ev = TimelineEvent(
                    event_id=f"EV_GSE_ANOM_{w_idx}",
                    window_index=w_idx,
                    unit_offset_start=start_unit,
                    unit_offset_end=end_unit,
                    byte_offset_start=b_start,
                    byte_offset_end=b_end,
                    event_type="F2_ANOMALY",
                    severity=anom_res.severity,
                    title=f"GSE Anomaly ({anom_res.severity})",
                    description=expl_summary,
                    metrics={"anomaly_score": anom_res.anomaly_score, "explanation": expl_dict} if expl_dict else {"anomaly_score": anom_res.anomaly_score},
                )
                point_events.append(ev)
                events.append(ev)

            pt = TimelinePoint(
                window_index=w_idx,
                unit_offset_start=start_unit,
                unit_offset_end=end_unit,
                byte_offset_start=b_start,
                byte_offset_end=b_end,
                unit_count=len(chunk),
                valid_units=stats.valid_pdus,
                invalid_units=stats.malformed_pdus,
                payload_bytes=stats.total_payload_bytes,
                payload_kb=stats.total_payload_bytes / 1024.0,
                unit_density=len(chunk),
                health_score=health_score,
                health_status=health_status,
                error_count=stats.malformed_pdus,
                error_rate=error_rate,
                is_anomaly=anom_res.is_anomaly,
                anomaly_score=anom_res.anomaly_score,
                anomaly_severity=anom_res.severity,
                anomaly_explanation=expl_summary,
                top_deviations=[d.to_dict() for d in anom_res.top_deviations[:3]],
                pattern_findings=[f.to_dict() for f in pat_res.findings],
                has_transition=False,
                transition_description=None,
                format_specific_metrics=fmt_metrics,
                events=point_events,
                explanation=expl_dict,
            )
            points.append(pt)

        # Cross-window GSE transitions (e.g. fragmentation bursts)
        for i in range(1, len(points)):
            prev = points[i - 1]
            curr = points[i]
            prev_frag = prev.format_specific_metrics.get("fragmentation_ratio", 0.0)
            curr_frag = curr.format_specific_metrics.get("fragmentation_ratio", 0.0)
            if curr_frag - prev_frag >= 0.30:
                curr.has_transition = True
                curr.transition_description = f"Fragmentation burst: jumped from {prev_frag*100:.1f}% to {curr_frag*100:.1f}%"
                ev = TimelineEvent(
                    event_id=f"EV_GSE_TRANS_{curr.window_index}",
                    window_index=curr.window_index,
                    unit_offset_start=curr.unit_offset_start,
                    unit_offset_end=curr.unit_offset_end,
                    byte_offset_start=curr.byte_offset_start,
                    byte_offset_end=curr.byte_offset_end,
                    event_type="F3_TRANSITION",
                    severity="LOW",
                    title="Fragmentation Burst Event",
                    description=curr.transition_description,
                )
                curr.events.append(ev)
                events.append(ev)

        summary_stats = {
            "mean_health_score": round(sum(p.health_score for p in points) / len(points), 2),
            "peak_anomaly_score": round(max(p.anomaly_score for p in points), 4),
            "anomaly_window_count": sum(1 for p in points if p.is_anomaly),
            "transition_count": sum(1 for p in points if p.has_transition),
            "total_payload_kb": round(sum(p.payload_kb for p in points), 2),
        }

        return StreamTimeline(
            stream_name=stream_name,
            format=StreamFormat.GSE,
            total_units=total_pdus,
            total_bytes=total_bytes,
            window_size=win_size,
            total_windows=len(points),
            anomaly_threshold=anomaly_threshold,
            points=points,
            events=events,
            summary_stats=summary_stats,
        )

    # -------------------------------------------------------------------------
    # DVB-S2 BBFrame Timeline Generation
    # -------------------------------------------------------------------------

    def generate_bbframe_timeline(
        self,
        frames: Sequence[BBFrame],
        window_size: Optional[int] = None,
        stream_name: str = "DVB-S2 BBFrame Stream"
    ) -> StreamTimeline:
        """
        Generates a complete sequential timeline for a DVB-S2 Baseband Frame stream.
        """
        win_size = window_size or self.config.bbframe_window_size
        total_frames = len(frames)
        total_bytes = sum(len(f.raw_bytes) if f.raw_bytes else (10 + f.payload_length) for f in frames)

        if total_frames == 0:
            return StreamTimeline(
                stream_name=stream_name,
                format=StreamFormat.BB_FRAME,
                total_units=0,
                total_bytes=0,
                window_size=win_size,
                total_windows=0,
                anomaly_threshold=0.50,
            )

        window_chunks: List[Sequence[BBFrame]] = []
        window_stats: List[BBFrameStreamStatistics] = []
        window_features: List[UnifiedStreamFeatureSet] = []
        byte_offsets: List[Tuple[int, int]] = []

        curr_byte = 0
        for start in range(0, total_frames, win_size):
            chunk = frames[start:start + win_size]
            window_chunks.append(chunk)

            chunk_bytes = sum(len(f.raw_bytes) if f.raw_bytes else (10 + f.payload_length) for f in chunk)
            byte_offsets.append((curr_byte, curr_byte + chunk_bytes))
            curr_byte += chunk_bytes

            stats = BBFrameStreamStatistics()
            stats.total_frames = len(chunk)
            stats.valid_frames = sum(1 for f in chunk if f.is_valid)
            stats.invalid_crc_frames = sum(1 for f in chunk if not f.is_valid)
            stats.total_bytes_read = chunk_bytes
            for f in chunk:
                stats.total_payload_bytes += f.payload_length
                stats.dfl_values.append(f.dfl)
                stats.stream_type_counts[f.ts_gs] += 1
                stats.input_stream_mode_counts["SIS" if f.is_sis else "MIS"] += 1
                stats.coding_modulation_counts["CCM" if f.is_ccm else "ACM"] += 1
                stats.roll_off_counts[f"alpha={f.ro_rolloff}"] += 1
                if f.mode_adaptation_type:
                    stats.mode_adaptation_counts[f.mode_adaptation_type] += 1

            window_stats.append(stats)
            meta = {
                "window_index": len(window_features),
                "window_size": len(chunk),
                "unit_offset_start": start,
                "unit_offset_end": start + len(chunk),
            }
            feat = self.feature_extractor.extract_unified(
                stats, format=StreamFormat.BB_FRAME, metadata=meta
            )
            window_features.append(feat)

        # Fit F2 Anomaly Detector on BBFrame windows
        detector = AnomalyDetector(
            AnomalyConfig(
                format=StreamFormat.BB_FRAME,
                contamination=self.config.f2_contamination,
                random_state=42,
                anomaly_threshold=self.config.f2_anomaly_threshold,
            )
        )
        if len(window_features) >= 2:
            detector.fit(window_features)
        anomaly_threshold = detector.anomaly_threshold

        points: List[TimelinePoint] = []
        events: List[TimelineEvent] = []

        for w_idx, chunk in enumerate(window_chunks):
            feat = window_features[w_idx]
            stats = window_stats[w_idx]
            start_unit = w_idx * win_size
            end_unit = start_unit + len(chunk)
            b_start, b_end = byte_offsets[w_idx]

            # F1 Health Calculation for BBFrame
            crc_valid_pct = (stats.valid_frames / stats.total_frames) if stats.total_frames > 0 else 1.0
            health_score = max(0.0, 100.0 * crc_valid_pct)
            if health_score >= 99.0:
                health_status = "HEALTHY"
            elif health_score >= 80.0:
                health_status = "WARNING"
            else:
                health_status = "CRITICAL"

            # F2 Anomaly Evaluation
            if detector.is_fitted:
                anom_res = detector.predict_sample(feat, window_index=w_idx)
            else:
                anom_res = AnomalyResult(
                    is_anomaly=False,
                    anomaly_score=0.20,
                    raw_score=0.20,
                    severity="NORMAL",
                    top_deviations=[],
                    summary_explanation="Insufficient windows to fit anomaly baseline",
                    feature_values={},
                    window_index=w_idx,
                )

            # F3 Pattern Evaluation
            pat_res = self.pattern_detector.analyze_bbframe_window(chunk, window_idx=w_idx)

            fmt_metrics = {
                "modal_dfl_bits": pat_res.metrics_summary.get("modal_dfl", 0),
                "sis_ratio": pat_res.metrics_summary.get("sis_ratio", 1.0),
                "acm_ratio": pat_res.metrics_summary.get("acm_ratio", 1.0),
                "dominant_ro": pat_res.metrics_summary.get("dominant_ro", 0.35),
                "stream_type": pat_res.metrics_summary.get("stream_type", "GENERIC_CONTINUOUS"),
            }

            point_events: List[TimelineEvent] = []

            # Feature F5: Structured Domain-Safe Anomaly Explanation
            expl_dict = None
            expl_summary = anom_res.summary_explanation
            if anom_res.is_anomaly:
                expl = self.explanation_engine.explain_anomaly(
                    anomaly_result=anom_res,
                    pattern_result=pat_res,
                    window_offsets=(start_unit, end_unit, b_start, b_end),
                    timeline_event_id=f"EV_BB_ANOM_{w_idx}",
                    stream_format=StreamFormat.BB_FRAME,
                )
                expl_dict = expl.to_dict()
                expl_summary = expl.concise_summary

            if anom_res.is_anomaly:
                ev = TimelineEvent(
                    event_id=f"EV_BB_ANOM_{w_idx}",
                    window_index=w_idx,
                    unit_offset_start=start_unit,
                    unit_offset_end=end_unit,
                    byte_offset_start=b_start,
                    byte_offset_end=b_end,
                    event_type="F2_ANOMALY",
                    severity=anom_res.severity,
                    title=f"BBFrame Anomaly ({anom_res.severity})",
                    description=expl_summary,
                    metrics={"anomaly_score": anom_res.anomaly_score, "explanation": expl_dict} if expl_dict else {"anomaly_score": anom_res.anomaly_score},
                )
                point_events.append(ev)
                events.append(ev)

            pt = TimelinePoint(
                window_index=w_idx,
                unit_offset_start=start_unit,
                unit_offset_end=end_unit,
                byte_offset_start=b_start,
                byte_offset_end=b_end,
                unit_count=len(chunk),
                valid_units=stats.valid_frames,
                invalid_units=stats.invalid_crc_frames,
                payload_bytes=stats.total_payload_bytes,
                payload_kb=stats.total_payload_bytes / 1024.0,
                unit_density=len(chunk),
                health_score=health_score,
                health_status=health_status,
                error_count=stats.invalid_crc_frames,
                error_rate=feat.common.error_rate,
                is_anomaly=anom_res.is_anomaly,
                anomaly_score=anom_res.anomaly_score,
                anomaly_severity=anom_res.severity,
                anomaly_explanation=expl_summary,
                top_deviations=[d.to_dict() for d in anom_res.top_deviations[:3]],
                pattern_findings=[f.to_dict() for f in pat_res.findings],
                has_transition=False,
                transition_description=None,
                format_specific_metrics=fmt_metrics,
                events=point_events,
                explanation=expl_dict,
            )
            points.append(pt)

        # Cross-window BBFrame transitions (e.g. DFL transitions)
        for i in range(1, len(points)):
            prev = points[i - 1]
            curr = points[i]
            prev_dfl = prev.format_specific_metrics.get("modal_dfl_bits")
            curr_dfl = curr.format_specific_metrics.get("modal_dfl_bits")
            if prev_dfl and curr_dfl and prev_dfl != curr_dfl:
                curr.has_transition = True
                curr.transition_description = f"Modal DFL frame length transitioned from {prev_dfl} to {curr_dfl} bits"
                ev = TimelineEvent(
                    event_id=f"EV_BB_TRANS_{curr.window_index}",
                    window_index=curr.window_index,
                    unit_offset_start=curr.unit_offset_start,
                    unit_offset_end=curr.unit_offset_end,
                    byte_offset_start=curr.byte_offset_start,
                    byte_offset_end=curr.byte_offset_end,
                    event_type="F3_TRANSITION",
                    severity="LOW",
                    title="Frame Length (DFL) Adaptation",
                    description=curr.transition_description,
                )
                curr.events.append(ev)
                events.append(ev)

        summary_stats = {
            "mean_health_score": round(sum(p.health_score for p in points) / len(points), 2),
            "peak_anomaly_score": round(max(p.anomaly_score for p in points), 4),
            "anomaly_window_count": sum(1 for p in points if p.is_anomaly),
            "transition_count": sum(1 for p in points if p.has_transition),
            "total_payload_kb": round(sum(p.payload_kb for p in points), 2),
        }

        return StreamTimeline(
            stream_name=stream_name,
            format=StreamFormat.BB_FRAME,
            total_units=total_frames,
            total_bytes=total_bytes,
            window_size=win_size,
            total_windows=len(points),
            anomaly_threshold=anomaly_threshold,
            points=points,
            events=events,
            summary_stats=summary_stats,
        )

    # -------------------------------------------------------------------------
    # Universal Gateway from StreamHandler
    # -------------------------------------------------------------------------

    def generate_from_handler(
        self,
        handler: StreamHandler,
        window_size: Optional[int] = None,
        max_units: Optional[int] = None
    ) -> StreamTimeline:
        """
        Universal gateway: executes timeline generation directly from a StreamHandler.
        """
        parser = handler.get_parser()
        fmt = handler.format

        if fmt == StreamFormat.MPEG_TS:
            packets = list(parser.parse_file(handler.path, max_packets=max_units))
            return self.generate_ts_timeline(packets, window_size=window_size, stream_name=handler.path.name)
        elif fmt == StreamFormat.GSE:
            pdus = list(parser.parse_file(handler.path))
            if max_units:
                pdus = pdus[:max_units]
            return self.generate_gse_timeline(pdus, window_size=window_size, stream_name=handler.path.name)
        elif fmt == StreamFormat.BB_FRAME:
            frames = list(parser.parse_file(handler.path, max_packets=max_units))
            return self.generate_bbframe_timeline(frames, window_size=window_size, stream_name=handler.path.name)
        else:
            raise ValueError(f"Unsupported format for timeline generation: {fmt}")
