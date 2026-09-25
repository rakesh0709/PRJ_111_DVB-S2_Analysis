"""
Analysis Engine - Stream Health Evaluation (Feature F1) for PRJ_111.

Evaluates transmission integrity indicators, sync stability, packet loss,
and Continuity Counter errors using transparent, configurable rule thresholds
grounded in selected Priority-1 broadcast integrity indicators.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
import logging
from pathlib import Path
import time
from typing import Any, Dict, List, Optional, Union

from dvbs2_analyzer.features.extractor import FeatureExtractor, StreamFeatureSet
from dvbs2_analyzer.parsers.ts_parser import TSParser, TSStreamStatistics

logger = logging.getLogger(__name__)


class HealthClassification(str, Enum):
    """Overall stream health status."""
    HEALTHY = "HEALTHY"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"
    NO_DATA = "NO_DATA"


@dataclass
class HealthThresholds:
    """
    Configurable quality and integrity thresholds for DVB-S2 stream health evaluation.
    Grounded in ETSI TR 101 290 Priority 1 and operational satellite standards.
    """
    # ETSI TR 101 290 P1.1 - TS Sync Loss (Sync byte 0x47 periodicity)
    min_sync_integrity_warning: float = 99.99     # < 99.99% indicates intermittent sync slips
    min_sync_integrity_critical: float = 95.00    # < 95.00% indicates catastrophic desync

    # ETSI TR 101 290 P1.3 - Transport Error Indicator (Demodulator FEC uncorrectable bit errors)
    max_tei_rate_warning: float = 0.0             # Any TEI flag indicates link degradation
    max_tei_rate_critical: float = 0.01           # > 1.0% uncorrectable packets causes A/V breakdown

    # ETSI TR 101 290 P1.4 - Continuity Counter Discontinuities (Dropped or reordered packets per PID)
    max_cc_rate_warning: float = 0.0001           # > 0.01% packet loss triggers warning
    max_cc_rate_critical: float = 0.005           # > 0.5% packet loss causes noticeable stream stutter

    # Transponder Bandwidth Utilization (Null Packets PID 0x1FFF)
    max_null_ratio_warning: float = 0.95          # > 95% indicates transponder carries mostly idle padding
    max_null_ratio_critical: float = 0.999        # > 99.9% indicates almost no active user payload

    # Header Integrity (Malformed packets detected)
    max_malformed_warning: int = 1
    max_malformed_critical: int = 10


@dataclass
class MetricEvaluation:
    """Evaluation result for an individual stream health metric."""
    metric_name: str
    raw_value: Union[int, float]
    formatted_value: str
    unit: str
    status: HealthClassification
    threshold_applied: str
    interpretation: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "metric_name": self.metric_name,
            "raw_value": self.raw_value,
            "formatted_value": self.formatted_value,
            "unit": self.unit,
            "status": self.status.value,
            "threshold_applied": self.threshold_applied,
            "interpretation": self.interpretation,
        }


@dataclass
class StreamHealthReport:
    """Structured result object for Feature F1: Stream Health Analysis."""
    input_file: str
    detected_format: str
    file_size_bytes: int
    analysis_timestamp: str
    packets_analyzed: int
    elapsed_seconds: float
    health_status: HealthClassification
    overall_score: float                          # 0.0 to 100.0 score
    packet_statistics: Dict[str, Any]
    features: StreamFeatureSet
    metric_evaluations: List[MetricEvaluation]
    issues: List[str]
    metadata: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        """Converts report into a clean serializable dictionary."""
        return {
            "input_file": self.input_file,
            "detected_format": self.detected_format,
            "file_size_bytes": self.file_size_bytes,
            "analysis_timestamp": self.analysis_timestamp,
            "packets_analyzed": self.packets_analyzed,
            "elapsed_seconds": round(self.elapsed_seconds, 4),
            "health_status": self.health_status.value,
            "overall_score": round(self.overall_score, 2),
            "packet_statistics": self.packet_statistics,
            "features": self.features.to_dict(),
            "metric_evaluations": [m.to_dict() for m in self.metric_evaluations],
            "issues": self.issues,
            "metadata": self.metadata,
        }

    def format_text(self) -> str:
        """Formats the result into a human-readable stream health report."""
        lines = [
            "STREAM HEALTH ANALYSIS",
            "======================",
            f"Input:             {self.input_file}",
            f"Format:            {self.detected_format}",
            f"Total packets:     {self.features.total_packets:,}",
            f"Unique PIDs:       {self.features.unique_pid_count}",
            f"Null packets:      {self.features.null_packet_count:,}",
            f"Null ratio:        {self.features.null_packet_ratio:.4%}",
            f"TEI errors:        {self.features.tei_error_count:,} ({self.features.tei_error_rate:.4%})",
            f"Continuity errors: {self.features.continuity_error_count:,} ({self.features.continuity_error_rate:.4%})",
            f"Sync integrity:    {self.features.sync_integrity:.4f}%",
            f"Health status:     {self.health_status.value} (Score: {self.overall_score:.1f}/100)",
        ]

        if self.issues:
            lines.append("Issues:")
            for issue in self.issues:
                lines.append(f"  - {issue}")
        else:
            lines.append("Issues:            None (All metrics within healthy operating thresholds)")

        lines.append("======================")
        return "\n".join(lines)


# Backward-compatible dataclass for foundation test
@dataclass
class HealthScore:
    """Legacy compatibility structure for basic foundation tests."""
    overall_score: float
    status: str
    sync_integrity_pct: float
    cc_error_count: int
    tei_error_count: int
    detected_issues: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Union[float, str, int, List[str]]]:
        return {
            "overall_score": self.overall_score,
            "status": self.status,
            "sync_integrity_percentage": self.sync_integrity_pct,
            "continuity_error_count": self.cc_error_count,
            "tei_error_count": self.tei_error_count,
            "detected_issues": self.detected_issues,
        }


class HealthAnalyzer:
    """
    Performs deterministic, rule-based stream health analysis against configured thresholds.
    """

    def __init__(self, thresholds: Optional[HealthThresholds] = None):
        self.thresholds = thresholds or HealthThresholds()

    def evaluate_features(
        self,
        features: StreamFeatureSet,
        input_file: str = "stream",
        detected_format: str = "MPEG_TS",
        file_size_bytes: int = 0,
        elapsed_seconds: float = 0.0,
        packet_statistics: Optional[Dict[str, Any]] = None,
    ) -> StreamHealthReport:
        """
        Evaluates extracted stream features and generates a structured StreamHealthReport.
        """
        if packet_statistics is None:
            packet_statistics = {}

        # Handle empty stream
        if features.total_packets == 0:
            return StreamHealthReport(
                input_file=input_file,
                detected_format=detected_format,
                file_size_bytes=file_size_bytes,
                analysis_timestamp=datetime.now(timezone.utc).isoformat(),
                packets_analyzed=0,
                elapsed_seconds=elapsed_seconds,
                health_status=HealthClassification.NO_DATA,
                overall_score=0.0,
                packet_statistics=packet_statistics,
                features=features,
                metric_evaluations=[],
                issues=["Zero packets parsed; stream is empty or invalid."],
                metadata={"analyzer_version": "PRJ_111-v0.1.0"},
            )

        evaluations: List[MetricEvaluation] = []
        issues: List[str] = []
        score = 100.0

        # ---------------------------------------------------------------------
        # 1. Sync Integrity (ETSI TR 101 290 P1.1)
        # ---------------------------------------------------------------------
        sync_val = features.sync_integrity
        if sync_val < self.thresholds.min_sync_integrity_critical:
            sync_status = HealthClassification.CRITICAL
            score -= 40.0
            issues.append(
                f"Sync integrity is {sync_val:.2f}% (< {self.thresholds.min_sync_integrity_critical}% critical threshold): "
                f"Severe framing desynchronization detected."
            )
            sync_interp = "Severe frame alignment loss; receiver lock failure."
        elif sync_val < self.thresholds.min_sync_integrity_warning:
            sync_status = HealthClassification.WARNING
            score -= 20.0
            issues.append(
                f"Sync integrity is {sync_val:.2f}% (< {self.thresholds.min_sync_integrity_warning}% warning threshold): "
                f"Intermittent sync slips observed."
            )
            sync_interp = "Minor sync slip; possible byte misalignment or transmission disruption."
        else:
            sync_status = HealthClassification.HEALTHY
            sync_interp = "Consistent 188-byte framing with 0x47 sync byte alignment."

        evaluations.append(MetricEvaluation(
            metric_name="Sync Integrity",
            raw_value=sync_val,
            formatted_value=f"{sync_val:.4f}%",
            unit="%",
            status=sync_status,
            threshold_applied=f"Warning: <{self.thresholds.min_sync_integrity_warning}%, Critical: <{self.thresholds.min_sync_integrity_critical}%",
            interpretation=sync_interp,
        ))

        # ---------------------------------------------------------------------
        # 2. Transport Error Indicator (TEI) (ETSI TR 101 290 P1.3)
        # ---------------------------------------------------------------------
        tei_rate = features.tei_error_rate
        if tei_rate > self.thresholds.max_tei_rate_critical:
            tei_status = HealthClassification.CRITICAL
            score -= 30.0
            issues.append(
                f"TEI rate is {tei_rate:.4%} ({features.tei_error_count:,} packets): "
                f"Corrupted packet flags exceed critical threshold ({self.thresholds.max_tei_rate_critical:.2%})."
            )
            tei_interp = "Elevated TEI flags; corrupted packets detected in digital receiver output stream."
        elif tei_rate > self.thresholds.max_tei_rate_warning:
            tei_status = HealthClassification.WARNING
            score -= 15.0
            issues.append(
                f"Detected {features.tei_error_count:,} packets with TEI flag set ({tei_rate:.4%}): "
                f"Corrupted bytes detected over the link."
            )
            tei_interp = "Occasional packet corruption flags observed in stream."
        else:
            tei_status = HealthClassification.HEALTHY
            tei_interp = "Zero transport error indicator flags observed in parsed packets."

        evaluations.append(MetricEvaluation(
            metric_name="Transport Error Indicator (TEI)",
            raw_value=features.tei_error_count,
            formatted_value=f"{features.tei_error_count:,} ({tei_rate:.4%})",
            unit="packets",
            status=tei_status,
            threshold_applied=f"Warning: >{self.thresholds.max_tei_rate_warning:.4%}, Critical: >{self.thresholds.max_tei_rate_critical:.4%}",
            interpretation=tei_interp,
        ))

        # ---------------------------------------------------------------------
        # 3. Continuity Counter Errors (Selected Priority-1 Indicator)
        # ---------------------------------------------------------------------
        cc_rate = features.continuity_error_rate
        if cc_rate > self.thresholds.max_cc_rate_critical:
            cc_status = HealthClassification.CRITICAL
            score -= 30.0
            issues.append(
                f"Continuity counter error rate is {cc_rate:.4%} ({features.continuity_error_count:,} errors): "
                f"Exceeds critical packet loss threshold ({self.thresholds.max_cc_rate_critical:.2%})."
            )
            cc_interp = "Critical packet sequence discontinuities detected across stream."
        elif cc_rate > self.thresholds.max_cc_rate_warning:
            cc_status = HealthClassification.WARNING
            score -= 15.0
            issues.append(
                f"Continuity counter error rate is {cc_rate:.4%} ({features.continuity_error_count:,} errors): "
                f"Minor packet sequence discontinuities observed."
            )
            cc_interp = "Minor packet sequence discontinuities detected across one or more PIDs."
        else:
            cc_status = HealthClassification.HEALTHY
            cc_interp = "Continuity counters strictly monotonic per PID with no lost packets."

        evaluations.append(MetricEvaluation(
            metric_name="Continuity Counter Errors",
            raw_value=features.continuity_error_count,
            formatted_value=f"{features.continuity_error_count:,} ({cc_rate:.4%})",
            unit="errors",
            status=cc_status,
            threshold_applied=f"Warning: >{self.thresholds.max_cc_rate_warning:.4%}, Critical: >{self.thresholds.max_cc_rate_critical:.4%}",
            interpretation=cc_interp,
        ))

        # ---------------------------------------------------------------------
        # 4. Null Packet Utilization (Transponder load)
        # ---------------------------------------------------------------------
        null_ratio = features.null_packet_ratio
        if null_ratio > self.thresholds.max_null_ratio_critical:
            null_status = HealthClassification.WARNING
            score -= 10.0
            issues.append(
                f"Null packet ratio is {null_ratio:.2%}: "
                f"Stream is almost entirely null padding (idle transponder beacon)."
            )
            null_interp = "Transponder is operating near-zero payload throughput."
        elif null_ratio > self.thresholds.max_null_ratio_warning:
            null_status = HealthClassification.WARNING
            score -= 5.0
            issues.append(
                f"Null packet ratio is {null_ratio:.2%}: "
                f"High proportion of padding packets (> {self.thresholds.max_null_ratio_warning:.0%})."
            )
            null_interp = "Transponder has high spare capacity."
        else:
            null_status = HealthClassification.HEALTHY
            null_interp = f"Nominal payload multiplexing with {null_ratio:.2%} null stuffing."

        evaluations.append(MetricEvaluation(
            metric_name="Null Packet Ratio",
            raw_value=null_ratio,
            formatted_value=f"{null_ratio:.4%}",
            unit="ratio",
            status=null_status,
            threshold_applied=f"Warning: >{self.thresholds.max_null_ratio_warning:.2%}, Critical: >{self.thresholds.max_null_ratio_critical:.2%}",
            interpretation=null_interp,
        ))

        # ---------------------------------------------------------------------
        # 5. Malformed Packets Check
        # ---------------------------------------------------------------------
        malformed_count = features.invalid_packets
        if malformed_count >= self.thresholds.max_malformed_critical:
            mal_status = HealthClassification.CRITICAL
            score -= 25.0
            issues.append(
                f"Encountered {malformed_count} malformed/unparseable packets: Stream corruption detected."
            )
            mal_interp = "Frequent structural packet corruption."
        elif malformed_count >= self.thresholds.max_malformed_warning:
            mal_status = HealthClassification.WARNING
            score -= 10.0
            issues.append(f"Encountered {malformed_count} malformed packet(s).")
            mal_interp = "Isolated packet length or header corruption."
        else:
            mal_status = HealthClassification.HEALTHY
            mal_interp = "All packets conform to standard 188-byte framing."

        evaluations.append(MetricEvaluation(
            metric_name="Malformed Packet Count",
            raw_value=malformed_count,
            formatted_value=str(malformed_count),
            unit="packets",
            status=mal_status,
            threshold_applied=f"Warning: >={self.thresholds.max_malformed_warning}, Critical: >={self.thresholds.max_malformed_critical}",
            interpretation=mal_interp,
        ))

        # Overall Status Classification
        final_score = max(0.0, min(100.0, round(score, 2)))

        if any(e.status == HealthClassification.CRITICAL for e in evaluations) or final_score < 60.0:
            overall_status = HealthClassification.CRITICAL
        elif any(e.status == HealthClassification.WARNING for e in evaluations) or final_score < 90.0:
            overall_status = HealthClassification.WARNING
        else:
            overall_status = HealthClassification.HEALTHY

        return StreamHealthReport(
            input_file=input_file,
            detected_format=detected_format,
            file_size_bytes=file_size_bytes,
            analysis_timestamp=datetime.now(timezone.utc).isoformat(),
            packets_analyzed=features.total_packets,
            elapsed_seconds=elapsed_seconds,
            health_status=overall_status,
            overall_score=final_score,
            packet_statistics=packet_statistics,
            features=features,
            metric_evaluations=evaluations,
            issues=issues,
            metadata={
                "analyzer_version": "PRJ_111-v0.1.0",
                "rules_specification": "ETSI TR 101 290 Priority 1",
            },
        )

    def analyze_file(
        self,
        file_path: Union[str, Path],
        max_packets: Optional[int] = None,
    ) -> StreamHealthReport:
        """
        Executes the full F1 Stream Health pipeline for a target TS file:
        TS file -> StreamHandler -> TSParser -> FeatureExtractor -> HealthAnalyzer -> StreamHealthReport.
        """
        from dvbs2_analyzer.ingestion.stream_handler import StreamHandler

        path = Path(file_path).resolve()
        handler = StreamHandler(path)
        stream_info = handler.get_stream_info()

        parser = TSParser(strict_mode=False)
        extractor = FeatureExtractor()

        t0 = time.perf_counter()
        # Stream packets through parser
        for _ in parser.parse_file(path, max_packets=max_packets):
            pass
        elapsed = time.perf_counter() - t0

        features = extractor.extract_from_ts_stats(parser.stats)

        return self.evaluate_features(
            features=features,
            input_file=path.name,
            detected_format=stream_info.detected_format.value,
            file_size_bytes=stream_info.file_size_bytes,
            elapsed_seconds=elapsed,
            packet_statistics=parser.get_statistics(),
        )

    @staticmethod
    def evaluate_ts_health(stats: TSStreamStatistics) -> HealthScore:
        """
        Legacy evaluation method preserved for backward-compatibility with test_foundation.py.
        """
        total = stats.total_packets
        if total == 0:
            return HealthScore(
                overall_score=0.0,
                status="NO_DATA",
                sync_integrity_pct=0.0,
                cc_error_count=0,
                tei_error_count=0,
                detected_issues=["Empty stream or zero packets parsed."],
            )

        sync_integrity = (stats.valid_sync_packets / total) * 100.0
        cc_errors = sum(stats.continuity_errors.values())
        tei_errors = stats.tei_error_count

        issues: List[str] = []
        score = 100.0

        if stats.sync_byte_errors > 0:
            penalty = min(stats.sync_byte_errors * 10.0, 50.0)
            score -= penalty
            issues.append(f"Detected {stats.sync_byte_errors} sync byte framing errors (-{penalty} pts)")

        if tei_errors > 0:
            penalty = min(tei_errors * 5.0, 30.0)
            score -= penalty
            issues.append(f"Detected {tei_errors} Transport Error Indicator (TEI) flags (-{penalty} pts)")

        if cc_errors > 0:
            penalty = min(cc_errors * 2.0, 30.0)
            score -= penalty
            issues.append(f"Detected {cc_errors} Continuity Counter sequence breaks (-{penalty} pts)")

        score = max(0.0, round(score, 2))

        if score >= 95.0:
            status = "EXCELLENT"
        elif score >= 80.0:
            status = "GOOD"
        elif score >= 50.0:
            status = "DEGRADED"
        else:
            status = "CRITICAL"

        return HealthScore(
            overall_score=score,
            status=status,
            sync_integrity_pct=round(sync_integrity, 4),
            cc_error_count=cc_errors,
            tei_error_count=tei_errors,
            detected_issues=issues,
        )
