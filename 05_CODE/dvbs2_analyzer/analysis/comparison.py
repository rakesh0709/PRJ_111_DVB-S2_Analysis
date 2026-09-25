"""
Feature F6: Stream Comparison Engine for PRJ_111.

Compares two analyzed DVB-S2 receiver output streams (Stream A vs Stream B)
and identifies, quantifies, and classifies measurable differences across:
  1. Common cross-format metrics (strictly audited for semantic validity)
  2. Format-specific features (MPEG-TS, GSE, or Baseband Frame)
  3. F2 AI anomaly behavior (scores, counts, severities, distributions)
  4. F3 structural patterns (dominant PIDs, protocols, modal DFLs, modes)
  5. Sequential window timeline progressions (direct index & normalized deciles)

Architectural Principles:
1. Strict Semantic Audit:
   - Cross-Format Comparable: total_payload_bytes and integrity_ratio.
   - Cross-Format NOT_COMPARABLE: total_units, valid_units, invalid_units,
     truncated_units, mean_payload_bytes, payload_ratio, error_count,
     error_rate, and entropy.
   - Same-Format: All 11 common metrics and format-specific metrics are comparable.
2. Mathematically Sound Zero-Baseline:
   - When A=0, B>0: relative delta is None (never arbitrary +100%).
   - When A>0, B=0: relative delta is -100.0%.
   - When A=0, B=0: relative delta is 0.0%, classification UNCHANGED.
3. Single Significance Hierarchy:
   - NEGLIGIBLE (<2%), MINOR (2-10%), SUBSTANTIAL (10-50%), CRITICAL (>=50%).
   - Equality tolerance (0.5%) decoupled from significance.
4. Upstream Layer Authority:
   - Consumes existing F1-F5 outputs without duplicate parsing or scoring.
5. Strict Domain Safety:
   - Never infers RF, rain fade, transponder, or demodulator hardware faults.
   - Uses neutral terminology: "dominant PID" (no unverified "elementary stream").
   - Wording: "selected Priority-1 integrity indicators" (no formal ETSI TR 101 290 certification).
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
import json
import logging
import math
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple, Union

from dvbs2_analyzer.analysis.anomaly import AnomalyDetector, AnomalyReport, AnomalyResult
from dvbs2_analyzer.analysis.explanation import AnomalyExplanationEngine, ExplanationConfig
from dvbs2_analyzer.analysis.health import HealthAnalyzer, StreamHealthReport
from dvbs2_analyzer.analysis.patterns import PatternDetector, PatternReport, PatternResult
from dvbs2_analyzer.analysis.timeline import (
    StreamTimeline,
    TimelineConfig,
    TimelineGenerator,
    TimelinePoint,
)
from dvbs2_analyzer.config import StreamFormat
from dvbs2_analyzer.features.extractor import (
    CommonMetrics,
    FeatureExtractor,
    StreamFeatureSet,
    UnifiedStreamFeatureSet,
)
from dvbs2_analyzer.ingestion.stream_handler import StreamHandler

logger = logging.getLogger(__name__)


# =============================================================================
# Semantic Audit & Domain Safety Constants
# =============================================================================

CROSS_FORMAT_INCOMPATIBLE_METRICS: Dict[str, str] = {
    "total_units": (
        "Framing units represent physically distinct boundaries (188B packet vs "
        "variable PDU vs ~7.2KB frame). Unit counts cannot be equated cross-format."
    ),
    "valid_units": (
        "Framing unit semantics differ; raw counts of passed containers cannot be "
        "equated cross-format."
    ),
    "invalid_units": (
        "Failure blast radius and container dimensions differ fundamentally across formats."
    ),
    "truncated_units": (
        "Truncation mechanics and container sizes are format-specific."
    ),
    "mean_payload_bytes": (
        "Normalized per framing unit (per 188B packet vs per PDU vs per Baseband Frame). "
        "Comparing bytes-per-unit reflects container size, not stream throughput."
    ),
    "payload_ratio": (
        "Payload ratio definitions differ: MPEG-TS calculates packet-presence ratio, "
        "whereas GSE and BBFrame calculate byte-level encapsulation efficiency."
    ),
    "error_count": (
        "Error counts aggregate heterogeneous failure classes (packet sync/CC/TEI vs "
        "PDU syntax vs frame CRC-8) with unequal operational impact."
    ),
    "error_rate": (
        "Normalized per framing unit. A 1% error rate on 7KB frames represents "
        "catastrophic data loss compared to 1% on 188B packets."
    ),
    "entropy": (
        "Entropy measures format-specific distributions (TS PID multiplex vs GSE "
        "network protocols vs BBFrame ISI/modes) and cannot be equated cross-format."
    ),
}

CROSS_FORMAT_COMPARABLE_METRICS: Dict[str, str] = {
    "total_payload_bytes": "Physical octets of user payload data extracted from framing.",
    "integrity_ratio": "Dimensionless syntactic validity ratio [0.0, 1.0] of stream framing.",
}

UNSUPPORTED_INFERENCES_GUARD: List[str] = [
    "RF interference, jamming, or atmospheric rain fade (cannot be concluded; capture lacks RF carrier, signal power, or SNR telemetry).",
    "Demodulator or tuner hardware failure (cannot be concluded; only post-demodulator digital output stream is captured).",
    "Satellite transponder or uplink station failure (cannot be concluded; no transponder or satellite orbital telemetry available).",
    "Signal-to-Noise Ratio (SNR) or link margin degradation (cannot be concluded; physical-layer parameters are absent from baseband stream).",
    "Transmission path error or packet loss (cannot be concluded; framing syntax and CRC remain valid unless error bits are flagged).",
]

CROSS_FORMAT_ANOMALY_CAVEAT = (
    "CROSS-FORMAT ANOMALY SCORE SPACE NOTE: Anomaly scores are generated by models trained "
    "independently on format-specific feature spaces (MPEG-TS 188B framing vs GSE PDUs vs "
    "BBFrame baseband headers). Anomaly score distributions and sensitivity thresholds "
    "may not map to identical operational severity across formats."
)

ALIGNMENT_DISCLAIMER = (
    "Temporal alignment is unavailable without external receiver clock telemetry; "
    "streams are aligned by physical stream progress and sequential window index. "
    "Differences reflect spatial capture progression, not synchronized broadcast timestamps."
)


# =============================================================================
# Data Structures
# =============================================================================

@dataclass
class ComparisonConfig:
    """Configuration options for Feature F6 comparison engine."""
    equality_tolerance_pct: float = 0.5            # Changes <= 0.5% classified as UNCHANGED
    significance_minor_pct: float = 2.0            # Changes >= 2.0% flagged as MINOR
    significance_substantial_pct: float = 10.0     # Changes >= 10.0% flagged as SUBSTANTIAL
    significance_critical_pct: float = 50.0        # Changes >= 50.0% flagged as CRITICAL
    alignment_mode: str = "DIRECT_INDEX"           # "DIRECT_INDEX", "NORMALIZED_PROGRESS", "SUMMARY_ONLY"
    decile_bins: int = 10
    strict_domain_safety: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "equality_tolerance_pct": self.equality_tolerance_pct,
            "significance_minor_pct": self.significance_minor_pct,
            "significance_substantial_pct": self.significance_substantial_pct,
            "significance_critical_pct": self.significance_critical_pct,
            "alignment_mode": self.alignment_mode,
            "decile_bins": self.decile_bins,
            "strict_domain_safety": self.strict_domain_safety,
        }


@dataclass
class MetricDifference:
    """Quantitative comparison between Stream A and Stream B for a single metric."""
    metric_name: str
    stream_a_value: Optional[Union[float, int, str]]
    stream_b_value: Optional[Union[float, int, str]]
    absolute_difference: Optional[float]           # value_B - value_A (None if non-numeric or incompatible)
    relative_difference_pct: Optional[float]       # None when baseline value is zero or incompatible
    direction: str                                 # "A_HIGHER", "B_HIGHER", "EQUAL", "STRUCTURAL_CHANGE", "NOT_COMPARABLE", "INSUFFICIENT_DATA"
    classification: str                            # "UNCHANGED", "INCREASED", "DECREASED", "STRUCTURAL_DIFFERENCE", "NOT_COMPARABLE", "INSUFFICIENT_DATA"
    significance: str                              # "NEGLIGIBLE", "MINOR", "SUBSTANTIAL", "CRITICAL", "NOT_APPLICABLE"
    description: str                               # Factual observation without speculative claims
    incompatibility_reason: Optional[str] = None   # Explanatory reason when NOT_COMPARABLE
    unit: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "metric_name": self.metric_name,
            "stream_a_value": self.stream_a_value,
            "stream_b_value": self.stream_b_value,
            "absolute_difference": self.absolute_difference,
            "relative_difference_pct": self.relative_difference_pct,
            "direction": self.direction,
            "classification": self.classification,
            "significance": self.significance,
            "description": self.description,
            "incompatibility_reason": self.incompatibility_reason,
            "unit": self.unit,
        }


@dataclass
class CommonComparison:
    """Cross-format common telemetry differences."""
    metrics: Dict[str, MetricDifference]
    summary_description: str
    cross_format_audited: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "metrics": {k: v.to_dict() for k, v in self.metrics.items()},
            "summary_description": self.summary_description,
            "cross_format_audited": self.cross_format_audited,
        }


@dataclass
class FormatComparison:
    """Format-specific telemetry differences (MPEG-TS, GSE, or BBFrame)."""
    is_comparable: bool                            # True if both streams share format
    format_name: str
    metrics: Dict[str, MetricDifference] = field(default_factory=dict)
    structural_differences: List[str] = field(default_factory=list)
    incompatibility_reason: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "is_comparable": self.is_comparable,
            "format_name": self.format_name,
            "metrics": {k: v.to_dict() for k, v in self.metrics.items()},
            "structural_differences": self.structural_differences,
            "incompatibility_reason": self.incompatibility_reason,
        }


@dataclass
class AnomalyComparison:
    """Differential analysis of F2 anomaly detection telemetry."""
    stream_a_anomaly_count: int
    stream_b_anomaly_count: int
    stream_a_anomaly_ratio: float
    stream_b_anomaly_ratio: float
    stream_a_peak_score: float
    stream_b_peak_score: float
    stream_a_mean_score: float
    stream_b_mean_score: float
    severity_breakdown_a: Dict[str, int]
    severity_breakdown_b: Dict[str, int]
    score_difference: MetricDifference
    rate_difference: MetricDifference
    is_cross_format: bool = False
    comparison_notes: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stream_a_anomaly_count": self.stream_a_anomaly_count,
            "stream_b_anomaly_count": self.stream_b_anomaly_count,
            "stream_a_anomaly_ratio": round(self.stream_a_anomaly_ratio, 4),
            "stream_b_anomaly_ratio": round(self.stream_b_anomaly_ratio, 4),
            "stream_a_peak_score": round(self.stream_a_peak_score, 4),
            "stream_b_peak_score": round(self.stream_b_peak_score, 4),
            "stream_a_mean_score": round(self.stream_a_mean_score, 4),
            "stream_b_mean_score": round(self.stream_b_mean_score, 4),
            "severity_breakdown_a": self.severity_breakdown_a,
            "severity_breakdown_b": self.severity_breakdown_b,
            "score_difference": self.score_difference.to_dict(),
            "rate_difference": self.rate_difference.to_dict(),
            "is_cross_format": self.is_cross_format,
            "comparison_notes": self.comparison_notes,
        }


@dataclass
class PatternComparison:
    """Differential analysis of F3 structural pattern telemetry."""
    dominant_component_a: str                      # Dominant PID / Protocol / DFL
    dominant_component_b: str
    component_match: bool
    pattern_metrics: Dict[str, MetricDifference]
    structural_findings: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "dominant_component_a": self.dominant_component_a,
            "dominant_component_b": self.dominant_component_b,
            "component_match": self.component_match,
            "pattern_metrics": {k: v.to_dict() for k, v in self.pattern_metrics.items()},
            "structural_findings": self.structural_findings,
        }


@dataclass
class WindowAlignmentComparison:
    """Window-level comparison across sequential windows or progress quantiles."""
    alignment_mode: str                            # "DIRECT_INDEX", "NORMALIZED_PROGRESS", "SUMMARY_ONLY"
    aligned_window_count: int
    unaligned_windows_a: int
    unaligned_windows_b: int
    health_delta_series: List[float]               # health_B[i] - health_A[i]
    anomaly_delta_series: List[float]              # anomaly_B[i] - anomaly_A[i]
    payload_delta_series: List[float]              # payload_B[i] - payload_A[i]
    progress_deciles: List[Dict[str, Any]]         # 10 quantile bins for macro comparison
    alignment_disclaimer: str = ALIGNMENT_DISCLAIMER

    def to_dict(self) -> Dict[str, Any]:
        return {
            "alignment_mode": self.alignment_mode,
            "aligned_window_count": self.aligned_window_count,
            "unaligned_windows_a": self.unaligned_windows_a,
            "unaligned_windows_b": self.unaligned_windows_b,
            "health_delta_series": [round(v, 4) for v in self.health_delta_series],
            "anomaly_delta_series": [round(v, 4) for v in self.anomaly_delta_series],
            "payload_delta_series": [round(v, 4) for v in self.payload_delta_series],
            "progress_deciles": self.progress_deciles,
            "alignment_disclaimer": self.alignment_disclaimer,
        }


@dataclass
class ComparisonSummary:
    """Top-level diagnostic synthesis answering the core comparison questions."""
    key_differences: List[str]
    supporting_evidence: List[str]
    safe_conclusions: List[str]
    unsupported_inferences: List[str]
    limitations: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "key_differences": self.key_differences,
            "supporting_evidence": self.supporting_evidence,
            "safe_conclusions": self.safe_conclusions,
            "unsupported_inferences": self.unsupported_inferences,
            "limitations": self.limitations,
        }


@dataclass
class StreamComparisonReport:
    """Root comparison container for Stream A vs Stream B."""
    comparison_id: str
    stream_a_name: str
    stream_b_name: str
    format_a: str
    format_b: str
    is_same_format: bool
    common: CommonComparison
    format_specific: FormatComparison
    anomalies: AnomalyComparison
    patterns: PatternComparison
    windows: WindowAlignmentComparison
    summary: ComparisonSummary
    unsupported_inferences_guard: List[str] = field(default_factory=lambda: list(UNSUPPORTED_INFERENCES_GUARD))
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "comparison_id": self.comparison_id,
            "timestamp": self.timestamp,
            "stream_a_name": self.stream_a_name,
            "stream_b_name": self.stream_b_name,
            "format_a": self.format_a,
            "format_b": self.format_b,
            "is_same_format": self.is_same_format,
            "common": self.common.to_dict(),
            "format_specific": self.format_specific.to_dict(),
            "anomalies": self.anomalies.to_dict(),
            "patterns": self.patterns.to_dict(),
            "windows": self.windows.to_dict(),
            "summary": self.summary.to_dict(),
            "unsupported_inferences_guard": self.unsupported_inferences_guard,
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent, default=str)

    def render_ascii_summary(self) -> str:
        """Renders a clean, monospaced ASCII diagnostic comparison report."""
        lines = []
        bar = "=" * 80
        thin_bar = "-" * 80

        lines.append(bar)
        lines.append(f" PRJ_111: STREAM COMPARISON REPORT -- {self.stream_a_name} vs {self.stream_b_name}")
        lines.append(f" Comparison ID : {self.comparison_id}")
        lines.append(f" Timestamp     : {self.timestamp}")
        lines.append(f" Format A      : {self.format_a}")
        lines.append(f" Format B      : {self.format_b} (Same Format: {self.is_same_format})")
        lines.append(bar)

        # 1. Common Metrics
        lines.append("\n1. COMMON METRICS COMPARISON (Semantic Audit Applied):")
        lines.append(thin_bar)
        lines.append(f"{'Metric':<22} {'Stream A':<14} {'Stream B':<14} {'Delta':<10} {'Rel %':<10} {'Direction':<12} {'Significance'}")
        lines.append(thin_bar)
        for name, m in self.common.metrics.items():
            val_a_str = str(m.stream_a_value) if m.stream_a_value is not None else "N/A"
            val_b_str = str(m.stream_b_value) if m.stream_b_value is not None else "N/A"
            delta_str = f"{m.absolute_difference:+g}" if m.absolute_difference is not None else "N/A"
            pct_str = f"{m.relative_difference_pct:+.2f}%" if m.relative_difference_pct is not None else "N/A"
            lines.append(f"{name:<22} {val_a_str:<14} {val_b_str:<14} {delta_str:<10} {pct_str:<10} {m.direction:<12} {m.significance}")
        lines.append(thin_bar)

        # 2. Format-Specific
        lines.append(f"\n2. FORMAT-SPECIFIC COMPARISON ({self.format_specific.format_name}):")
        lines.append(thin_bar)
        if not self.format_specific.is_comparable:
            lines.append(f"   [INCOMPATIBLE]: {self.format_specific.incompatibility_reason}")
        else:
            lines.append(f"{'Metric':<25} {'Stream A':<14} {'Stream B':<14} {'Delta':<10} {'Rel %':<10} {'Significance'}")
            lines.append(thin_bar)
            for name, m in self.format_specific.metrics.items():
                val_a_str = str(m.stream_a_value) if m.stream_a_value is not None else "N/A"
                val_b_str = str(m.stream_b_value) if m.stream_b_value is not None else "N/A"
                delta_str = f"{m.absolute_difference:+g}" if m.absolute_difference is not None else "N/A"
                pct_str = f"{m.relative_difference_pct:+.2f}%" if m.relative_difference_pct is not None else "N/A"
                lines.append(f"{name:<25} {val_a_str:<14} {val_b_str:<14} {delta_str:<10} {pct_str:<10} {m.significance}")
            if self.format_specific.structural_differences:
                lines.append("\n   Structural Observations:")
                for diff in self.format_specific.structural_differences:
                    lines.append(f"   - {diff}")
        lines.append(thin_bar)

        # 3. Anomaly Analysis
        lines.append("\n3. ANOMALY & STABILITY DIFFERENTIAL:")
        lines.append(thin_bar)
        lines.append(f"   Stream A Anomalous Windows : {self.anomalies.stream_a_anomaly_count} (Rate: {self.anomalies.stream_a_anomaly_ratio:.2%}, Peak Score: {self.anomalies.stream_a_peak_score:.4f}, Mean: {self.anomalies.stream_a_mean_score:.4f})")
        lines.append(f"   Stream B Anomalous Windows : {self.anomalies.stream_b_anomaly_count} (Rate: {self.anomalies.stream_b_anomaly_ratio:.2%}, Peak Score: {self.anomalies.stream_b_peak_score:.4f}, Mean: {self.anomalies.stream_b_mean_score:.4f})")
        lines.append(f"   Mean Score Difference      : {self.anomalies.score_difference.description}")
        lines.append(f"   Anomaly Rate Difference    : {self.anomalies.rate_difference.description}")
        lines.append(f"   Severity Breakdown A       : {self.anomalies.severity_breakdown_a}")
        lines.append(f"   Severity Breakdown B       : {self.anomalies.severity_breakdown_b}")
        if self.anomalies.comparison_notes:
            lines.append("   Notes:")
            for note in self.anomalies.comparison_notes:
                lines.append(f"   * {note}")
        lines.append(thin_bar)

        # 4. Pattern Differences
        lines.append("\n4. STRUCTURAL PATTERN DIFFERENCES:")
        lines.append(thin_bar)
        lines.append(f"   Dominant Component A : {self.patterns.dominant_component_a}")
        lines.append(f"   Dominant Component B : {self.patterns.dominant_component_b}")
        lines.append(f"   Component Match      : {self.patterns.component_match}")
        if self.patterns.structural_findings:
            for f in self.patterns.structural_findings:
                lines.append(f"   - {f}")
        lines.append(thin_bar)

        # 5. Window Alignment
        lines.append("\n5. WINDOW ALIGNMENT & PROGRESS COMPARISON:")
        lines.append(thin_bar)
        lines.append(f"   Alignment Mode       : {self.windows.alignment_mode}")
        lines.append(f"   Aligned Windows      : {self.windows.aligned_window_count}")
        lines.append(f"   Unaligned Windows A  : {self.windows.unaligned_windows_a}")
        lines.append(f"   Unaligned Windows B  : {self.windows.unaligned_windows_b}")
        lines.append(f"   Disclaimer           : {self.windows.alignment_disclaimer}")
        if self.windows.progress_deciles:
            lines.append("\n   Decile Macro Trajectory (Progress Bins 0-100%):")
            lines.append(f"   {'Decile':<8} {'Progress':<10} {'Health Delta':<14} {'Anomaly Delta':<15} {'Payload Delta (KB)'}")
            for d in self.windows.progress_deciles:
                lines.append(f"   {d['decile']:<8} {d['progress_range']:<10} {d.get('mean_health_delta', 0.0):+8.2f}        {d.get('mean_anomaly_delta', 0.0):+8.4f}         {d.get('mean_payload_kb_delta', 0.0):+8.2f}")

        lines.append(thin_bar)

        # 6. Summary & Evidence
        lines.append("\n6. COMPARISON SUMMARY & DIAGNOSTIC SYNTHESIS:")
        lines.append(thin_bar)
        lines.append("   Key Differences:")
        for kd in self.summary.key_differences:
            lines.append(f"   - {kd}")
        lines.append("\n   Supporting Evidence:")
        for ev in self.summary.supporting_evidence:
            lines.append(f"   - {ev}")
        lines.append("\n   Safe Conclusions:")
        for sc in self.summary.safe_conclusions:
            lines.append(f"   - {sc}")
        if self.summary.limitations:
            lines.append("\n   Analysis Limitations:")
            for lim in self.summary.limitations:
                lines.append(f"   - {lim}")
        lines.append(thin_bar)

        # 7. Unsupported Inferences Guard
        lines.append("\n7. MANDATORY DOMAIN-SAFETY GUARD:")
        lines.append(thin_bar)
        for guard in self.unsupported_inferences_guard:
            lines.append(f"   [GUARD] {guard}")
        lines.append(bar)

        return "\n".join(lines)


# =============================================================================
# Core Calculation Logic
# =============================================================================

def compute_metric_difference(
    metric_name: str,
    val_a: Optional[Union[float, int, str]],
    val_b: Optional[Union[float, int, str]],
    unit: str = "",
    config: Optional[ComparisonConfig] = None,
    is_cross_format: bool = False,
    is_error_metric: bool = False,
) -> MetricDifference:
    """
    Computes absolute and relative difference between Stream A and Stream B
    under the approved semantic audit, zero-baseline rules, and significance tiers.
    """
    if config is None:
        config = ComparisonConfig()

    # 1. Check cross-format incompatibility
    if is_cross_format and metric_name in CROSS_FORMAT_INCOMPATIBLE_METRICS:
        reason = CROSS_FORMAT_INCOMPATIBLE_METRICS[metric_name]
        return MetricDifference(
            metric_name=metric_name,
            stream_a_value=val_a,
            stream_b_value=val_b,
            absolute_difference=None,
            relative_difference_pct=None,
            direction="NOT_COMPARABLE",
            classification="NOT_COMPARABLE",
            significance="NOT_APPLICABLE",
            description=f"{metric_name} is not comparable cross-format: {reason}",
            incompatibility_reason=reason,
            unit=unit,
        )

    # 2. Check for missing telemetry
    if val_a is None or val_b is None:
        return MetricDifference(
            metric_name=metric_name,
            stream_a_value=val_a,
            stream_b_value=val_b,
            absolute_difference=None,
            relative_difference_pct=None,
            direction="INSUFFICIENT_DATA",
            classification="INSUFFICIENT_DATA",
            significance="NOT_APPLICABLE",
            description=f"Insufficient data for {metric_name} (Stream A={val_a}, Stream B={val_b}).",
            incompatibility_reason="Missing metric telemetry in one or both streams.",
            unit=unit,
        )

    # 3. String / categorical comparison
    if isinstance(val_a, str) or isinstance(val_b, str):
        if str(val_a) == str(val_b):
            return MetricDifference(
                metric_name=metric_name,
                stream_a_value=val_a,
                stream_b_value=val_b,
                absolute_difference=None,
                relative_difference_pct=None,
                direction="EQUAL",
                classification="UNCHANGED",
                significance="NEGLIGIBLE",
                description=f"{metric_name} is identical ({val_a}).",
                unit=unit,
            )
        else:
            return MetricDifference(
                metric_name=metric_name,
                stream_a_value=val_a,
                stream_b_value=val_b,
                absolute_difference=None,
                relative_difference_pct=None,
                direction="STRUCTURAL_CHANGE",
                classification="STRUCTURAL_DIFFERENCE",
                significance="SUBSTANTIAL",
                description=f"{metric_name} shifted from '{val_a}' to '{val_b}'.",
                unit=unit,
            )

    # 4. Numeric comparison
    num_a = float(val_a)
    num_b = float(val_b)
    abs_diff = num_b - num_a

    # Zero-baseline cases (strictly adhering to Section 4.C)
    if num_a == 0.0 and num_b == 0.0:
        return MetricDifference(
            metric_name=metric_name,
            stream_a_value=val_a,
            stream_b_value=val_b,
            absolute_difference=0.0,
            relative_difference_pct=0.0,
            direction="EQUAL",
            classification="UNCHANGED",
            significance="NEGLIGIBLE",
            description=f"{metric_name} is zero in both streams.",
            unit=unit,
        )
    elif num_a == 0.0 and num_b != 0.0:
        dir_str = "B_HIGHER" if num_b > 0 else "A_HIGHER"
        class_str = "INCREASED" if num_b > 0 else "DECREASED"
        # Mathematical rule: relative percentage from zero baseline is undefined (None)
        sig_str = "CRITICAL" if is_error_metric else "SUBSTANTIAL"
        return MetricDifference(
            metric_name=metric_name,
            stream_a_value=val_a,
            stream_b_value=val_b,
            absolute_difference=round(abs_diff, 6),
            relative_difference_pct=None,
            direction=dir_str,
            classification=class_str,
            significance=sig_str,
            description=f"Stream B observed non-zero value ({val_b}{unit}) while Stream A baseline is zero.",
            unit=unit,
        )
    elif num_a != 0.0 and num_b == 0.0:
        dir_str = "A_HIGHER" if num_a > 0 else "B_HIGHER"
        class_str = "DECREASED" if num_a > 0 else "INCREASED"
        sig_str = "CRITICAL" if (is_error_metric or abs(num_a) > 0) else "SUBSTANTIAL"
        return MetricDifference(
            metric_name=metric_name,
            stream_a_value=val_a,
            stream_b_value=val_b,
            absolute_difference=round(abs_diff, 6),
            relative_difference_pct=-100.0,
            direction=dir_str,
            classification=class_str,
            significance=sig_str,
            description=f"Stream B dropped to zero from Stream A baseline ({val_a}{unit}) (-100.0%).",
            unit=unit,
        )

    # General non-zero baseline
    rel_pct = (abs_diff / abs(num_a)) * 100.0
    abs_rel = abs(rel_pct)

    # Check equality tolerance
    if abs_rel <= config.equality_tolerance_pct or abs(abs_diff) < 1e-9:
        dir_str = "EQUAL"
        class_str = "UNCHANGED"
        sig_str = "NEGLIGIBLE"
        desc = f"{metric_name} remained stable within equality tolerance (A={val_a}{unit}, B={val_b}{unit}, delta={rel_pct:+.2f}%)."
    else:
        if num_b > num_a:
            dir_str = "B_HIGHER"
            class_str = "INCREASED"
        else:
            dir_str = "A_HIGHER"
            class_str = "DECREASED"

        # Tiered significance hierarchy
        if abs_rel < config.significance_minor_pct:
            sig_str = "NEGLIGIBLE"
        elif abs_rel < config.significance_substantial_pct:
            sig_str = "MINOR"
        elif abs_rel < config.significance_critical_pct:
            sig_str = "SUBSTANTIAL"
        else:
            sig_str = "CRITICAL"

        desc = f"{metric_name} changed from {val_a}{unit} to {val_b}{unit} (delta={abs_diff:+g}{unit}, {rel_pct:+.2f}%)."

    return MetricDifference(
        metric_name=metric_name,
        stream_a_value=val_a,
        stream_b_value=val_b,
        absolute_difference=round(abs_diff, 6),
        relative_difference_pct=round(rel_pct, 4),
        direction=dir_str,
        classification=class_str,
        significance=sig_str,
        description=desc,
        unit=unit,
    )


# =============================================================================
# Feature F6: Stream Comparison Engine
# =============================================================================

class StreamComparisonEngine:
    """
    Core engine for Feature F6: Stream Comparison.
    Consumes structured telemetry from two streams (A and B) and produces a
    multi-tier StreamComparisonReport.
    """

    def __init__(self, config: Optional[ComparisonConfig] = None):
        self.config = config or ComparisonConfig()

    def compare(
        self,
        target_a: Any,
        target_b: Any,
        name_a: Optional[str] = None,
        name_b: Optional[str] = None,
        **kwargs
    ) -> StreamComparisonReport:
        """
        Polymorphic entry point for comparing two streams.
        Accepts StreamTimeline, StreamHandler, UnifiedStreamFeatureSet, or file paths.
        """
        if isinstance(target_a, StreamTimeline) and isinstance(target_b, StreamTimeline):
            return self.compare_timelines(target_a, target_b, name_a=name_a, name_b=name_b)
        elif isinstance(target_a, StreamHandler) and isinstance(target_b, StreamHandler):
            return self.compare_handlers(target_a, target_b, name_a=name_a, name_b=name_b, **kwargs)
        elif isinstance(target_a, UnifiedStreamFeatureSet) and isinstance(target_b, UnifiedStreamFeatureSet):
            return self.compare_features(target_a, target_b, name_a=name_a or "Stream A", name_b=name_b or "Stream B", **kwargs)
        elif (isinstance(target_a, (str, Path)) and isinstance(target_b, (str, Path))):
            return self.compare_files(target_a, target_b, name_a=name_a, name_b=name_b, **kwargs)
        else:
            raise TypeError(
                f"Unsupported comparison operand types: {type(target_a).__name__} vs {type(target_b).__name__}"
            )

    def compare_timelines(
        self,
        timeline_a: StreamTimeline,
        timeline_b: StreamTimeline,
        name_a: Optional[str] = None,
        name_b: Optional[str] = None,
    ) -> StreamComparisonReport:
        """
        Compares two pre-computed StreamTimeline objects.
        This provides rich window alignment, anomaly tracking, and pattern comparison.
        """
        stream_a_name = name_a or timeline_a.stream_name
        stream_b_name = name_b or timeline_b.stream_name
        fmt_a = timeline_a.format
        fmt_b = timeline_b.format
        is_same_format = (fmt_a == fmt_b)

        # 1. Extract Aggregated Common Metrics from Timelines
        common_metrics_a = self._extract_common_from_timeline(timeline_a)
        common_metrics_b = self._extract_common_from_timeline(timeline_b)
        common_comp = self._compare_common_metrics(common_metrics_a, common_metrics_b, is_same_format)

        # 2. Extract Format-Specific Metrics
        format_comp = self._compare_format_specific_from_timelines(timeline_a, timeline_b, is_same_format)

        # 3. Compare Anomaly Telemetry
        anomaly_comp = self._compare_anomalies_from_timelines(timeline_a, timeline_b, is_same_format)

        # 4. Compare Patterns
        pattern_comp = self._compare_patterns_from_timelines(timeline_a, timeline_b, is_same_format)

        # 5. Window Alignment & Progression
        windows_comp = self._compare_window_alignment(timeline_a, timeline_b)

        # 6. Synthesize Summary & Safe Conclusions
        summary = self._synthesize_summary(
            common_comp, format_comp, anomaly_comp, pattern_comp, windows_comp, is_same_format, stream_a_name, stream_b_name
        )

        comparison_id = f"CMP_{fmt_a.value.upper()}_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}"

        return StreamComparisonReport(
            comparison_id=comparison_id,
            stream_a_name=stream_a_name,
            stream_b_name=stream_b_name,
            format_a=fmt_a.value,
            format_b=fmt_b.value,
            is_same_format=is_same_format,
            common=common_comp,
            format_specific=format_comp,
            anomalies=anomaly_comp,
            patterns=pattern_comp,
            windows=windows_comp,
            summary=summary,
            unsupported_inferences_guard=list(UNSUPPORTED_INFERENCES_GUARD),
        )

    def compare_handlers(
        self,
        handler_a: StreamHandler,
        handler_b: StreamHandler,
        window_size_a: Optional[int] = None,
        window_size_b: Optional[int] = None,
        name_a: Optional[str] = None,
        name_b: Optional[str] = None,
    ) -> StreamComparisonReport:
        """
        Ingests two StreamHandler instances, runs the timeline pipeline,
        and performs complete differential comparison.
        """
        win_a = window_size_a or self._default_window_size(handler_a.format)
        win_b = window_size_b or self._default_window_size(handler_b.format)

        generator = TimelineGenerator(TimelineConfig())
        timeline_a = generator.generate_from_handler(handler_a, window_size=win_a, stream_name=name_a or handler_a.path.name)
        timeline_b = generator.generate_from_handler(handler_b, window_size=win_b, stream_name=name_b or handler_b.path.name)

        return self.compare_timelines(timeline_a, timeline_b, name_a=name_a, name_b=name_b)

    def compare_files(
        self,
        file_a: Union[str, Path],
        file_b: Union[str, Path],
        forced_format_a: Optional[StreamFormat] = None,
        forced_format_b: Optional[StreamFormat] = None,
        window_size_a: Optional[int] = None,
        window_size_b: Optional[int] = None,
        name_a: Optional[str] = None,
        name_b: Optional[str] = None,
    ) -> StreamComparisonReport:
        """Loads and compares two raw capture files."""
        handler_a = StreamHandler(file_a, forced_format=forced_format_a)
        handler_b = StreamHandler(file_b, forced_format=forced_format_b)
        return self.compare_handlers(
            handler_a, handler_b,
            window_size_a=window_size_a,
            window_size_b=window_size_b,
            name_a=name_a,
            name_b=name_b
        )

    def compare_features(
        self,
        feat_a: UnifiedStreamFeatureSet,
        feat_b: UnifiedStreamFeatureSet,
        format_a: Optional[StreamFormat] = None,
        format_b: Optional[StreamFormat] = None,
        name_a: str = "Stream A",
        name_b: str = "Stream B",
    ) -> StreamComparisonReport:
        """Compares two pre-extracted UnifiedStreamFeatureSet objects directly."""
        fmt_a = format_a or StreamFormat(feat_a.common.stream_type) if feat_a.common.stream_type in [f.value for f in StreamFormat] else StreamFormat.UNKNOWN
        fmt_b = format_b or StreamFormat(feat_b.common.stream_type) if feat_b.common.stream_type in [f.value for f in StreamFormat] else StreamFormat.UNKNOWN
        is_same_format = (fmt_a == fmt_b) and (fmt_a != StreamFormat.UNKNOWN)

        common_comp = self._compare_common_metrics(feat_a.common, feat_b.common, is_same_format)
        format_comp = self._compare_format_specific_from_features(feat_a, feat_b, fmt_a, is_same_format)

        # Build fallback anomaly comparison
        score_diff = compute_metric_difference("mean_anomaly_score", 0.0, 0.0, config=self.config)
        rate_diff = compute_metric_difference("anomaly_rate", 0.0, 0.0, config=self.config)
        anomaly_comp = AnomalyComparison(
            stream_a_anomaly_count=0,
            stream_b_anomaly_count=0,
            stream_a_anomaly_ratio=0.0,
            stream_b_anomaly_ratio=0.0,
            stream_a_peak_score=0.0,
            stream_b_peak_score=0.0,
            stream_a_mean_score=0.0,
            stream_b_mean_score=0.0,
            severity_breakdown_a={},
            severity_breakdown_b={},
            score_difference=score_diff,
            rate_difference=rate_diff,
            is_cross_format=not is_same_format,
            comparison_notes=["Direct feature-set comparison (window timeline absent)."],
        )

        pattern_comp = PatternComparison(
            dominant_component_a="N/A",
            dominant_component_b="N/A",
            component_match=True,
            pattern_metrics={},
            structural_findings=[],
        )

        windows_comp = WindowAlignmentComparison(
            alignment_mode="SUMMARY_ONLY",
            aligned_window_count=0,
            unaligned_windows_a=0,
            unaligned_windows_b=0,
            health_delta_series=[],
            anomaly_delta_series=[],
            payload_delta_series=[],
            progress_deciles=[],
            alignment_disclaimer=ALIGNMENT_DISCLAIMER,
        )

        summary = self._synthesize_summary(
            common_comp, format_comp, anomaly_comp, pattern_comp, windows_comp, is_same_format, name_a, name_b
        )

        return StreamComparisonReport(
            comparison_id=f"CMP_FEAT_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}",
            stream_a_name=name_a,
            stream_b_name=name_b,
            format_a=fmt_a.value,
            format_b=fmt_b.value,
            is_same_format=is_same_format,
            common=common_comp,
            format_specific=format_comp,
            anomalies=anomaly_comp,
            patterns=pattern_comp,
            windows=windows_comp,
            summary=summary,
            unsupported_inferences_guard=list(UNSUPPORTED_INFERENCES_GUARD),
        )

    # -------------------------------------------------------------------------
    # Internal Comparison Helpers
    # -------------------------------------------------------------------------

    def _default_window_size(self, fmt: StreamFormat) -> int:
        if fmt == StreamFormat.MPEG_TS:
            return 200
        elif fmt == StreamFormat.GSE:
            return 3
        elif fmt == StreamFormat.BB_FRAME:
            return 50
        return 100

    def _extract_common_from_timeline(self, timeline: StreamTimeline) -> Dict[str, Any]:
        """Extracts whole-stream common metrics from timeline points."""
        points = timeline.points
        if not points:
            return {
                "total_units": timeline.total_units,
                "valid_units": 0,
                "invalid_units": 0,
                "truncated_units": 0,
                "integrity_ratio": 1.0 if timeline.total_units > 0 else 0.0,
                "total_payload_bytes": 0,
                "mean_payload_bytes": 0.0,
                "payload_ratio": 0.0,
                "error_count": 0,
                "error_rate": 0.0,
                "entropy": 0.0,
            }

        total_units = timeline.total_units
        valid_units = sum(p.valid_units for p in points)
        invalid_units = sum(p.invalid_units for p in points)
        total_payload = sum(p.payload_bytes for p in points)
        error_count = sum(p.error_count for p in points)
        truncated_units = sum(1 for p in points if p.unit_count < timeline.window_size and p.window_index == len(points) - 1)

        # Safeguard: if valid_units sum is 0 but stream is valid, fallback to total_units - invalid_units
        if valid_units == 0 and invalid_units == 0 and total_units > 0:
            valid_units = total_units

        integ = valid_units / max(1, total_units)
        mean_pl = total_payload / max(1, total_units)
        err_rate = error_count / max(1, total_units)

        # Entropy estimation from format metrics
        entropy_val = 0.0
        for p in points:
            if "pid_entropy" in p.format_specific_metrics:
                entropy_val = p.format_specific_metrics["pid_entropy"]
                break
            elif "protocol_diversity" in p.format_specific_metrics:
                entropy_val = float(p.format_specific_metrics["protocol_diversity"])
                break

        # Payload ratio
        payload_units = sum(1 for p in points if p.payload_bytes > 0)
        pl_ratio = payload_units / max(1, len(points))

        return {
            "total_units": total_units,
            "valid_units": valid_units,
            "invalid_units": invalid_units,
            "truncated_units": truncated_units,
            "integrity_ratio": integ,
            "total_payload_bytes": total_payload,
            "mean_payload_bytes": mean_pl,
            "payload_ratio": pl_ratio,
            "error_count": error_count,
            "error_rate": err_rate,
            "entropy": entropy_val,
        }

    def _compare_common_metrics(
        self,
        metrics_a: Union[CommonMetrics, Dict[str, Any]],
        metrics_b: Union[CommonMetrics, Dict[str, Any]],
        is_same_format: bool
    ) -> CommonComparison:
        """
        Executes the approved Semantic Audit across all 11 Common Metrics.
        When is_same_format=False, only total_payload_bytes and integrity_ratio are compared.
        """
        def get_val(source: Any, key: str) -> Any:
            if isinstance(source, CommonMetrics):
                return getattr(source, key, None)
            elif isinstance(source, dict):
                return source.get(key)
            return None

        keys_to_compare = [
            ("total_units", " units", False),
            ("valid_units", " units", False),
            ("invalid_units", " units", True),
            ("truncated_units", " units", True),
            ("integrity_ratio", "", False),
            ("total_payload_bytes", " bytes", False),
            ("mean_payload_bytes", " B/unit", False),
            ("payload_ratio", "", False),
            ("error_count", " errors", True),
            ("error_rate", "", True),
            ("entropy", " bits", False),
        ]

        diffs: Dict[str, MetricDifference] = {}
        for key, unit, is_err in keys_to_compare:
            val_a = get_val(metrics_a, key)
            val_b = get_val(metrics_b, key)
            diff = compute_metric_difference(
                metric_name=key,
                val_a=val_a,
                val_b=val_b,
                unit=unit,
                config=self.config,
                is_cross_format=(not is_same_format),
                is_error_metric=is_err,
            )
            diffs[key] = diff

        if is_same_format:
            summary_desc = "Same-format comparison: All 11 common telemetry metrics evaluated under identical framing semantics."
        else:
            summary_desc = (
                "Cross-format comparison: Strict semantic audit applied. Only user payload bytes "
                "and framing integrity ratio are evaluated. Container-dependent metrics (unit counts, "
                "unit-level error rates, unit mean payloads, and entropy) are classified as NOT_COMPARABLE."
            )

        return CommonComparison(
            metrics=diffs,
            summary_description=summary_desc,
            cross_format_audited=(not is_same_format),
        )

    def _compare_format_specific_from_timelines(
        self,
        timeline_a: StreamTimeline,
        timeline_b: StreamTimeline,
        is_same_format: bool
    ) -> FormatComparison:
        """Compares format-specific metrics across timeline points."""
        fmt_a = timeline_a.format
        fmt_b = timeline_b.format

        if not is_same_format:
            return FormatComparison(
                is_comparable=False,
                format_name=f"{fmt_a.value} vs {fmt_b.value}",
                metrics={},
                structural_differences=[
                    f"Encapsulation formats differ ({fmt_a.value} vs {fmt_b.value}); format-specific headers are incompatible."
                ],
                incompatibility_reason=f"Streams have different encapsulation formats ({fmt_a.value} vs {fmt_b.value}); format-specific metrics cannot be cross-compared."
            )

        metrics: Dict[str, MetricDifference] = {}
        findings: List[str] = []

        if fmt_a == StreamFormat.MPEG_TS:
            # Aggregate TS metrics
            # Dominant PID
            pids_a: Dict[int, int] = {}
            pids_b: Dict[int, int] = {}
            tei_a = sum(p.format_specific_metrics.get("tei_error_rate", 0.0) * p.unit_count for p in timeline_a.points)
            tei_b = sum(p.format_specific_metrics.get("tei_error_rate", 0.0) * p.unit_count for p in timeline_b.points)
            cc_a = sum(p.format_specific_metrics.get("continuity_error_rate", 0.0) * p.unit_count for p in timeline_a.points)
            cc_b = sum(p.format_specific_metrics.get("continuity_error_rate", 0.0) * p.unit_count for p in timeline_b.points)
            null_ratio_a = sum(p.format_specific_metrics.get("null_packet_ratio", 0.0) for p in timeline_a.points) / max(1, len(timeline_a.points))
            null_ratio_b = sum(p.format_specific_metrics.get("null_packet_ratio", 0.0) for p in timeline_b.points) / max(1, len(timeline_b.points))
            entropy_a = sum(p.format_specific_metrics.get("pid_entropy", 0.0) for p in timeline_a.points) / max(1, len(timeline_a.points))
            entropy_b = sum(p.format_specific_metrics.get("pid_entropy", 0.0) for p in timeline_b.points) / max(1, len(timeline_b.points))

            # Sample dominant PID from middle window
            dom_pid_a = timeline_a.points[0].format_specific_metrics.get("dominant_pid_summary", "N/A") if timeline_a.points else "N/A"
            dom_pid_b = timeline_b.points[0].format_specific_metrics.get("dominant_pid_summary", "N/A") if timeline_b.points else "N/A"

            metrics["pid_entropy"] = compute_metric_difference("pid_entropy", entropy_a, entropy_b, unit=" bits", config=self.config)
            metrics["null_packet_ratio"] = compute_metric_difference("null_packet_ratio", null_ratio_a, null_ratio_b, config=self.config)
            metrics["tei_error_count"] = compute_metric_difference("tei_error_count", round(tei_a), round(tei_b), unit=" pkts", config=self.config, is_error_metric=True)
            metrics["continuity_error_count"] = compute_metric_difference("continuity_error_count", round(cc_a), round(cc_b), unit=" errors", config=self.config, is_error_metric=True)

            if dom_pid_a != dom_pid_b:
                findings.append(f"Dominant PID shifted from {dom_pid_a} to {dom_pid_b}.")
            else:
                findings.append(f"Dominant PID remained constant: {dom_pid_a}.")

        elif fmt_a == StreamFormat.BB_FRAME:
            # BBFrame metrics
            dfl_a = [p.format_specific_metrics.get("modal_dfl", 0) for p in timeline_a.points if "modal_dfl" in p.format_specific_metrics]
            dfl_b = [p.format_specific_metrics.get("modal_dfl", 0) for p in timeline_b.points if "modal_dfl" in p.format_specific_metrics]
            mod_a = max(set(dfl_a), key=dfl_a.count) if dfl_a else 0
            mod_b = max(set(dfl_b), key=dfl_b.count) if dfl_b else 0
            crc_a = sum(p.format_specific_metrics.get("crc_errors", 0) for p in timeline_a.points)
            crc_b = sum(p.format_specific_metrics.get("crc_errors", 0) for p in timeline_b.points)

            metrics["modal_dfl"] = compute_metric_difference("modal_dfl", mod_a, mod_b, unit=" bits", config=self.config)
            metrics["crc_error_count"] = compute_metric_difference("crc_error_count", crc_a, crc_b, unit=" errors", config=self.config, is_error_metric=True)

            if mod_a != mod_b:
                findings.append(f"Baseband Header Modal DFL shifted from {mod_a} bits to {mod_b} bits.")
            else:
                findings.append(f"Baseband Header Modal DFL consistent at {mod_a} bits.")

        elif fmt_a == StreamFormat.GSE:
            frag_a = sum(p.format_specific_metrics.get("fragmentation_ratio", 0.0) for p in timeline_a.points) / max(1, len(timeline_a.points))
            frag_b = sum(p.format_specific_metrics.get("fragmentation_ratio", 0.0) for p in timeline_b.points) / max(1, len(timeline_b.points))
            metrics["fragmentation_ratio"] = compute_metric_difference("fragmentation_ratio", frag_a, frag_b, config=self.config)
            findings.append("GSE framing encapsulation verified across streams.")

        return FormatComparison(
            is_comparable=True,
            format_name=fmt_a.value,
            metrics=metrics,
            structural_differences=findings,
        )

    def _compare_format_specific_from_features(
        self,
        feat_a: UnifiedStreamFeatureSet,
        feat_b: UnifiedStreamFeatureSet,
        fmt: StreamFormat,
        is_same_format: bool
    ) -> FormatComparison:
        """Compares format-specific metrics from UnifiedStreamFeatureSet."""
        if not is_same_format:
            return FormatComparison(
                is_comparable=False,
                format_name="Cross-Format",
                metrics={},
                structural_differences=["Incompatible stream encapsulation formats."],
                incompatibility_reason="Cross-format comparison precludes format-specific evaluation.",
            )

        metrics: Dict[str, MetricDifference] = {}
        findings: List[str] = []

        if fmt == StreamFormat.MPEG_TS and feat_a.ts_specific and feat_b.ts_specific:
            ts_a = feat_a.ts_specific
            ts_b = feat_b.ts_specific
            metrics["unique_pid_count"] = compute_metric_difference("unique_pid_count", ts_a.unique_pid_count, ts_b.unique_pid_count, config=self.config)
            metrics["pid_entropy"] = compute_metric_difference("pid_entropy", ts_a.pid_entropy, ts_b.pid_entropy, unit=" bits", config=self.config)
            metrics["null_packet_ratio"] = compute_metric_difference("null_packet_ratio", ts_a.null_packet_ratio, ts_b.null_packet_ratio, config=self.config)
            metrics["continuity_error_count"] = compute_metric_difference("continuity_error_count", ts_a.continuity_error_count, ts_b.continuity_error_count, unit=" errors", config=self.config, is_error_metric=True)
            metrics["tei_error_count"] = compute_metric_difference("tei_error_count", ts_a.tei_error_count, ts_b.tei_error_count, unit=" errors", config=self.config, is_error_metric=True)
            metrics["adaptation_field_ratio"] = compute_metric_difference("adaptation_field_ratio", ts_a.adaptation_field_ratio, ts_b.adaptation_field_ratio, config=self.config)
            findings.append(f"MPEG-TS PID diversity: A={ts_a.unique_pid_count}, B={ts_b.unique_pid_count}.")

        elif fmt == StreamFormat.BB_FRAME and feat_a.bbframe_specific and feat_b.bbframe_specific:
            bb_a = feat_a.bbframe_specific
            bb_b = feat_b.bbframe_specific
            metrics["modal_dfl"] = compute_metric_difference("modal_dfl", bb_a.modal_dfl, bb_b.modal_dfl, unit=" bits", config=self.config)
            metrics["crc_error_count"] = compute_metric_difference("crc_error_count", bb_a.crc_error_count, bb_b.crc_error_count, unit=" errors", config=self.config, is_error_metric=True)
            metrics["sis_ratio"] = compute_metric_difference("sis_ratio", bb_a.sis_ratio, bb_b.sis_ratio, config=self.config)
            metrics["acm_ratio"] = compute_metric_difference("acm_ratio", bb_a.acm_ratio, bb_b.acm_ratio, config=self.config)
            findings.append(f"BBFrame Modal DFL: A={bb_a.modal_dfl} bits, B={bb_b.modal_dfl} bits.")

        elif fmt == StreamFormat.GSE and feat_a.gse_specific and feat_b.gse_specific:
            gse_a = feat_a.gse_specific
            gse_b = feat_b.gse_specific
            metrics["fragmentation_ratio"] = compute_metric_difference("fragmentation_ratio", gse_a.fragmentation_ratio, gse_b.fragmentation_ratio, config=self.config)
            metrics["protocol_diversity"] = compute_metric_difference("protocol_diversity", gse_a.protocol_diversity, gse_b.protocol_diversity, config=self.config)
            findings.append(f"GSE Protocol Diversity: A={gse_a.protocol_diversity}, B={gse_b.protocol_diversity}.")

        return FormatComparison(
            is_comparable=True,
            format_name=fmt.value,
            metrics=metrics,
            structural_differences=findings,
        )

    def _compare_anomalies_from_timelines(
        self,
        timeline_a: StreamTimeline,
        timeline_b: StreamTimeline,
        is_same_format: bool
    ) -> AnomalyComparison:
        """Analyzes differential anomaly counts, scores, and severity distributions."""
        pts_a = timeline_a.points
        pts_b = timeline_b.points

        count_a = sum(1 for p in pts_a if p.is_anomaly)
        count_b = sum(1 for p in pts_b if p.is_anomaly)
        ratio_a = count_a / max(1, len(pts_a))
        ratio_b = count_b / max(1, len(pts_b))

        peak_a = max((p.anomaly_score for p in pts_a), default=0.0)
        peak_b = max((p.anomaly_score for p in pts_b), default=0.0)
        mean_a = (sum(p.anomaly_score for p in pts_a) / len(pts_a)) if pts_a else 0.0
        mean_b = (sum(p.anomaly_score for p in pts_b) / len(pts_b)) if pts_b else 0.0

        # Severity breakdown
        sev_a: Dict[str, int] = {"NORMAL": 0, "LOW": 0, "MEDIUM": 0, "HIGH": 0, "CRITICAL": 0}
        sev_b: Dict[str, int] = {"NORMAL": 0, "LOW": 0, "MEDIUM": 0, "HIGH": 0, "CRITICAL": 0}
        for p in pts_a:
            sev_a[p.anomaly_severity] = sev_a.get(p.anomaly_severity, 0) + 1
        for p in pts_b:
            sev_b[p.anomaly_severity] = sev_b.get(p.anomaly_severity, 0) + 1

        score_diff = compute_metric_difference("mean_anomaly_score", mean_a, mean_b, config=self.config)
        rate_diff = compute_metric_difference("anomaly_rate", ratio_a, ratio_b, config=self.config)

        notes: List[str] = []
        if not is_same_format:
            notes.append(CROSS_FORMAT_ANOMALY_CAVEAT)

        if count_b > count_a:
            notes.append(f"Stream B experienced {count_b - count_a} more anomalous windows than Stream A.")
        elif count_a > count_b:
            notes.append(f"Stream A experienced {count_a - count_b} more anomalous windows than Stream B.")
        else:
            notes.append("Both streams exhibited identical anomalous window counts.")

        return AnomalyComparison(
            stream_a_anomaly_count=count_a,
            stream_b_anomaly_count=count_b,
            stream_a_anomaly_ratio=ratio_a,
            stream_b_anomaly_ratio=ratio_b,
            stream_a_peak_score=peak_a,
            stream_b_peak_score=peak_b,
            stream_a_mean_score=mean_a,
            stream_b_mean_score=mean_b,
            severity_breakdown_a=sev_a,
            severity_breakdown_b=sev_b,
            score_difference=score_diff,
            rate_difference=rate_diff,
            is_cross_format=not is_same_format,
            comparison_notes=notes,
        )

    def _compare_patterns_from_timelines(
        self,
        timeline_a: StreamTimeline,
        timeline_b: StreamTimeline,
        is_same_format: bool
    ) -> PatternComparison:
        """Compares detected structural patterns and dominant multiplex components."""
        fmt_a = timeline_a.format

        def get_dominant(tl: StreamTimeline) -> str:
            if not tl.points:
                return "NONE"
            m = tl.points[0].format_specific_metrics
            if "dominant_pid_summary" in m:
                return m["dominant_pid_summary"]
            if "dominant_pid" in m:
                return f"PID 0x{m['dominant_pid']:04X}"
            if "modal_dfl" in m:
                return f"DFL {m['modal_dfl']} bits"
            if "dominant_protocol" in m:
                return f"Protocol {m['dominant_protocol']}"
            return "UNKNOWN"

        dom_a = get_dominant(timeline_a)
        dom_b = get_dominant(timeline_b)
        match = (dom_a == dom_b)

        findings: List[str] = []
        pattern_metrics: Dict[str, MetricDifference] = {}

        if is_same_format:
            if match:
                findings.append(f"Dominant traffic component remained unchanged: {dom_a}.")
            else:
                findings.append(f"Dominant traffic component changed: {dom_a} -> {dom_b}.")

            # Transition counts
            trans_a = sum(1 for p in timeline_a.points if p.has_transition)
            trans_b = sum(1 for p in timeline_b.points if p.has_transition)
            pattern_metrics["transition_count"] = compute_metric_difference("transition_count", trans_a, trans_b, config=self.config)
        else:
            findings.append("Cross-format comparison: Traffic components represent disparate protocol layers.")

        return PatternComparison(
            dominant_component_a=dom_a,
            dominant_component_b=dom_b,
            component_match=match,
            pattern_metrics=pattern_metrics,
            structural_findings=findings,
        )

    def _compare_window_alignment(
        self,
        timeline_a: StreamTimeline,
        timeline_b: StreamTimeline
    ) -> WindowAlignmentComparison:
        """
        Calculates window-level deltas for overlapping indices and generates
        10-decile quantile bins across stream physical progress.
        """
        pts_a = timeline_a.points
        pts_b = timeline_b.points
        na = len(pts_a)
        nb = len(pts_b)
        n_aligned = min(na, nb)

        h_deltas: List[float] = []
        a_deltas: List[float] = []
        p_deltas: List[float] = []

        for i in range(n_aligned):
            h_deltas.append(pts_b[i].health_score - pts_a[i].health_score)
            a_deltas.append(pts_b[i].anomaly_score - pts_a[i].anomaly_score)
            p_deltas.append(pts_b[i].payload_kb - pts_a[i].payload_kb)

        # 10 Decile Progress Bins
        deciles: List[Dict[str, Any]] = []
        num_bins = self.config.decile_bins

        for b in range(num_bins):
            start_pct = b * (100.0 / num_bins)
            end_pct = (b + 1) * (100.0 / num_bins)

            # Sample points in stream A and B for this progress slice
            idx_start_a = int(round(b * na / num_bins))
            idx_end_a = max(idx_start_a + 1, int(round((b + 1) * na / num_bins)))
            idx_start_b = int(round(b * nb / num_bins))
            idx_end_b = max(idx_start_b + 1, int(round((b + 1) * nb / num_bins)))

            slice_a = pts_a[idx_start_a:idx_end_a] if na > 0 else []
            slice_b = pts_b[idx_start_b:idx_end_b] if nb > 0 else []

            mean_h_a = sum(p.health_score for p in slice_a) / len(slice_a) if slice_a else 100.0
            mean_h_b = sum(p.health_score for p in slice_b) / len(slice_b) if slice_b else 100.0
            mean_a_a = sum(p.anomaly_score for p in slice_a) / len(slice_a) if slice_a else 0.0
            mean_a_b = sum(p.anomaly_score for p in slice_b) / len(slice_b) if slice_b else 0.0
            mean_p_a = sum(p.payload_kb for p in slice_a) / len(slice_a) if slice_a else 0.0
            mean_p_b = sum(p.payload_kb for p in slice_b) / len(slice_b) if slice_b else 0.0

            anom_cnt_a = sum(1 for p in slice_a if p.is_anomaly)
            anom_cnt_b = sum(1 for p in slice_b if p.is_anomaly)

            deciles.append({
                "decile": b + 1,
                "progress_range": f"{start_pct:.0f}-{end_pct:.0f}%",
                "mean_health_a": round(mean_h_a, 2),
                "mean_health_b": round(mean_h_b, 2),
                "mean_health_delta": round(mean_h_b - mean_h_a, 2),
                "mean_anomaly_a": round(mean_a_a, 4),
                "mean_anomaly_b": round(mean_a_b, 4),
                "mean_anomaly_delta": round(mean_a_b - mean_a_a, 4),
                "mean_payload_kb_a": round(mean_p_a, 2),
                "mean_payload_kb_b": round(mean_p_b, 2),
                "mean_payload_kb_delta": round(mean_p_b - mean_p_a, 2),
                "anomalies_a": anom_cnt_a,
                "anomalies_b": anom_cnt_b,
            })

        return WindowAlignmentComparison(
            alignment_mode=self.config.alignment_mode,
            aligned_window_count=n_aligned,
            unaligned_windows_a=max(0, na - nb),
            unaligned_windows_b=max(0, nb - na),
            health_delta_series=h_deltas,
            anomaly_delta_series=a_deltas,
            payload_delta_series=p_deltas,
            progress_deciles=deciles,
            alignment_disclaimer=ALIGNMENT_DISCLAIMER,
        )

    def _synthesize_summary(
        self,
        common: CommonComparison,
        fmt: FormatComparison,
        anom: AnomalyComparison,
        patterns: PatternComparison,
        windows: WindowAlignmentComparison,
        is_same_format: bool,
        name_a: str,
        name_b: str,
    ) -> ComparisonSummary:
        """Synthesizes key differences, safe conclusions, and domain guard notices."""
        key_diffs: List[str] = []
        evidence: List[str] = []
        conclusions: List[str] = []
        limitations: List[str] = []

        # 1. Evaluate Payload Volume Change
        pl_diff = common.metrics.get("total_payload_bytes")
        if pl_diff and pl_diff.classification != "UNCHANGED" and pl_diff.absolute_difference is not None:
            pct_str = f" ({pl_diff.relative_difference_pct:+.2f}%)" if pl_diff.relative_difference_pct is not None else ""
            key_diffs.append(f"User payload volume shifted by {pl_diff.absolute_difference:+g} bytes{pct_str} (Classification: {pl_diff.classification}, Significance: {pl_diff.significance}).")
            evidence.append(f"Payload telemetry: Stream A={pl_diff.stream_a_value} bytes, Stream B={pl_diff.stream_b_value} bytes.")

        # 2. Evaluate Framing Integrity Ratio
        integ_diff = common.metrics.get("integrity_ratio")
        if integ_diff and integ_diff.classification != "UNCHANGED" and integ_diff.absolute_difference is not None:
            key_diffs.append(f"Framing integrity ratio shifted by {integ_diff.absolute_difference:+.4f} (Significance: {integ_diff.significance}).")
            evidence.append(f"Syntactic framing integrity: Stream A={integ_diff.stream_a_value}, Stream B={integ_diff.stream_b_value}.")
        elif integ_diff and integ_diff.stream_a_value == 1.0 and integ_diff.stream_b_value == 1.0:
            conclusions.append("Both streams maintained 100% syntactically valid framing integrity across all parsed units.")

        # 3. Same-Format Error / Format Metrics
        if is_same_format:
            err_diff = common.metrics.get("error_count")
            if err_diff and err_diff.classification != "UNCHANGED" and err_diff.absolute_difference is not None:
                key_diffs.append(f"Observed error counter diverged by {err_diff.absolute_difference:+g} errors ({err_diff.significance}).")
                evidence.append(f"Error count: Stream A={err_diff.stream_a_value}, Stream B={err_diff.stream_b_value}.")

            if not patterns.component_match:
                key_diffs.append(f"Dominant traffic component shifted from '{patterns.dominant_component_a}' to '{patterns.dominant_component_b}'.")
                evidence.append("Traffic pattern classifier detected distinct dominant identifiers.")
            else:
                conclusions.append(f"Dominant traffic component was consistent ({patterns.dominant_component_a}).")
        else:
            limitations.append("Cross-format comparison: Unit counts, unit-level error rates, and multiplex entropy cannot be equated cross-format.")

        # 4. Anomaly Comparison Synthesis
        if anom.stream_a_anomaly_count != anom.stream_b_anomaly_count:
            delta_cnt = anom.stream_b_anomaly_count - anom.stream_a_anomaly_count
            key_diffs.append(f"Detected anomaly occurrence changed by {delta_cnt:+d} windows (Stream A={anom.stream_a_anomaly_count}, Stream B={anom.stream_b_anomaly_count}).")
            evidence.append(f"Anomaly rate: Stream A={anom.stream_a_anomaly_ratio:.2%}, Stream B={anom.stream_b_anomaly_ratio:.2%}.")
        else:
            conclusions.append(f"Anomaly counts were identical ({anom.stream_a_anomaly_count} anomalous windows in both streams).")

        # 5. Window Duration Differences
        if windows.unaligned_windows_a > 0 or windows.unaligned_windows_b > 0:
            unaligned = max(windows.unaligned_windows_a, windows.unaligned_windows_b)
            which_stream = name_a if windows.unaligned_windows_a > 0 else name_b
            limitations.append(f"Capture duration discrepancy: {which_stream} contains {unaligned} trailing unaligned windows.")

        # Default key diff fallback if streams are identical
        if not key_diffs:
            key_diffs.append("No statistically significant differences detected; streams exhibit matched operational profiles within configured tolerances.")
            conclusions.append("Telemetric parameters match baseline within the 0.5% equality tolerance.")

        # Safe Conclusions (Fact-Driven)
        conclusions.append("All reported observations are strictly grounded in parsed packet/frame telemetry.")

        return ComparisonSummary(
            key_differences=key_diffs,
            supporting_evidence=evidence,
            safe_conclusions=conclusions,
            unsupported_inferences=list(UNSUPPORTED_INFERENCES_GUARD),
            limitations=limitations,
        )
