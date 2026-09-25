"""
Feature F7: Automatic Analysis Report for PRJ_111.

Generates comprehensive, multi-format, structured diagnostic reports for analyzed
DVB-S2 receiver output streams (MPEG-TS, GSE, and DVB-S2 Baseband Frames).

Architectural Principles:
1. Authoritative Layer Consumption:
   - Consumes existing outputs from F1 (Health), F2 (Anomaly Detection), F3 (Patterns),
     F4 (Timeline), F5 (Explanations), and F6 (Comparison Engine).
   - Zero duplicate parsing, scoring, or model training.
2. Epistemological Tripartite Register:
   - OBSERVED_FACT: Direct syntactic/binary observations from parsers.
   - STATISTICAL_FINDING: Quantitative model and aggregate metrics across windows.
   - ENGINEERING_INTERPRETATION: Grounded operational synthesis summarizing supported
     relationships directly established by F1-F6 evidence.
3. Epistemic Safety Rules:
   - Prohibits unsupported causal assertions: no "cold baseline stabilization",
     no "capture start caused the anomaly", no "traffic burst", and no inferring
     "video stream" or "audio stream" roles from PIDs without verified PSI/SI tables.
   - Edge/truncated windows are neutrally described as occurring at the capture boundary
     without speculating why the capture began or ended.
   - Where evidence only supports that an event occurred, classifies it as OBSERVED_FACT
     or STATISTICAL_FINDING.
4. Strict Domain-Safety Guard:
   - Enforces UNSUPPORTED_INFERENCES_GUARD: never infers RF interference, rain fade,
     transponder faults, SNR, MER, BER, AGC, or demodulator hardware failure.
   - Wording: "dominant PID" (no unverified "elementary stream"); "selected Priority-1
     integrity indicators" (no formal ETSI TR 101 290 certification claims).
5. Multi-Format Rendering:
   - Structured JSON, GitHub Flavored Markdown, cp1252-safe monospaced text, and
     standalone offline HTML5.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple, Union

from dvbs2_analyzer.analysis.anomaly import AnomalyConfig, AnomalyDetector, AnomalyReport, AnomalyResult
from dvbs2_analyzer.analysis.comparison import (
    ALIGNMENT_DISCLAIMER,
    CROSS_FORMAT_ANOMALY_CAVEAT,
    CROSS_FORMAT_COMPARABLE_METRICS,
    CROSS_FORMAT_INCOMPATIBLE_METRICS,
    UNSUPPORTED_INFERENCES_GUARD,
    ComparisonConfig,
    StreamComparisonEngine,
    StreamComparisonReport,
)
from dvbs2_analyzer.analysis.explanation import (
    AnomalyExplanation,
    AnomalyExplanationEngine,
    ExplanationConfig,
    ExplanationReport,
)
from dvbs2_analyzer.analysis.health import HealthAnalyzer, StreamHealthReport
from dvbs2_analyzer.analysis.patterns import PatternConfig, PatternDetector, PatternReport, PatternResult
from dvbs2_analyzer.analysis.timeline import (
    StreamTimeline,
    TimelineConfig,
    TimelineEvent,
    TimelineGenerator,
    TimelinePoint,
)
from dvbs2_analyzer.config import StreamFormat
from dvbs2_analyzer.features.extractor import CommonMetrics, FeatureExtractor, UnifiedStreamFeatureSet
from dvbs2_analyzer.ingestion.stream_handler import StreamHandler

logger = logging.getLogger(__name__)


# =============================================================================
# Epistemic Taxonomy & Guard Constants
# =============================================================================

CATEGORY_OBSERVED_FACT = "OBSERVED_FACT"
CATEGORY_STATISTICAL_FINDING = "STATISTICAL_FINDING"
CATEGORY_ENGINEERING_INTERPRETATION = "ENGINEERING_INTERPRETATION"

SUBSYSTEM_FRAMING = "FRAMING"
SUBSYSTEM_HEALTH = "HEALTH"
SUBSYSTEM_ANOMALY = "ANOMALY"
SUBSYSTEM_PATTERN = "PATTERN"
SUBSYSTEM_TIMELINE = "TIMELINE"
SUBSYSTEM_COMPARISON = "COMPARISON"

MANDATORY_DOMAIN_SAFETY_NOTICE = (
    "Physical-layer parameters (e.g., RF carrier strength, SNR, MER, BER, AGC, "
    "rain fade, atmospheric attenuation, transponder health, and demodulator hardware state) "
    "cannot be determined from digital receiver output stream data alone without external "
    "physical-layer/demodulator telemetry."
)


# =============================================================================
# Structured Report Sections & Data Models
# =============================================================================

@dataclass
class ReportFinding:
    """Individual categorized finding within the tripartite register."""
    category: str              # OBSERVED_FACT, STATISTICAL_FINDING, ENGINEERING_INTERPRETATION
    subsystem: str             # FRAMING, HEALTH, ANOMALY, PATTERN, TIMELINE, COMPARISON
    title: str
    statement: str
    evidence: str
    source_layer: str          # PARSER, F1, F2, F3, F4, F5, F6
    metrics: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "category": self.category,
            "subsystem": self.subsystem,
            "title": self.title,
            "statement": self.statement,
            "evidence": self.evidence,
            "source_layer": self.source_layer,
            "metrics": self.metrics,
        }


@dataclass
class StreamSummarySection:
    """Metadata, file characteristics, and framing identification."""
    stream_name: str
    file_path: str
    file_size_bytes: int
    detected_format: str
    format_description: str
    total_units: int
    valid_units: int
    invalid_units: int
    truncated_units: int
    total_payload_bytes: int
    integrity_ratio: float
    error_count: int

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stream_name": self.stream_name,
            "file_path": self.file_path,
            "file_size_bytes": self.file_size_bytes,
            "detected_format": self.detected_format,
            "format_description": self.format_description,
            "total_units": self.total_units,
            "valid_units": self.valid_units,
            "invalid_units": self.invalid_units,
            "truncated_units": self.truncated_units,
            "total_payload_bytes": self.total_payload_bytes,
            "integrity_ratio": round(self.integrity_ratio, 6),
            "error_count": self.error_count,
        }


@dataclass
class HealthFindingsSection:
    """Feature F1 Stream Health synthesis."""
    health_score: float
    health_status: str
    selected_priority1_checks: Dict[str, Any]
    detected_issues: List[str]
    recommendations: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "health_score": round(self.health_score, 2),
            "health_status": self.health_status,
            "selected_priority1_checks": self.selected_priority1_checks,
            "detected_issues": self.detected_issues,
            "recommendations": self.recommendations,
        }


@dataclass
class AnomalyFindingsSection:
    """Feature F2 Anomaly Detection synthesis."""
    total_windows: int
    anomalous_windows: int
    anomaly_rate_pct: float
    peak_anomaly_score: float
    mean_anomaly_score: float
    decision_threshold: float
    severity_breakdown: Dict[str, int]
    anomaly_window_indices: List[int]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_windows": self.total_windows,
            "anomalous_windows": self.anomalous_windows,
            "anomaly_rate_pct": round(self.anomaly_rate_pct, 2),
            "peak_anomaly_score": round(self.peak_anomaly_score, 4),
            "mean_anomaly_score": round(self.mean_anomaly_score, 4),
            "decision_threshold": self.decision_threshold,
            "severity_breakdown": self.severity_breakdown,
            "anomaly_window_indices": self.anomaly_window_indices,
        }


@dataclass
class PatternFindingsSection:
    """Feature F3 Structural Patterns synthesis."""
    dominant_component: str
    dominant_component_pct: float
    multiplex_entropy: Optional[float]
    active_component_count: int
    transition_count: int
    structural_findings: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "dominant_component": self.dominant_component,
            "dominant_component_pct": round(self.dominant_component_pct, 2),
            "multiplex_entropy": round(self.multiplex_entropy, 4) if self.multiplex_entropy is not None else None,
            "active_component_count": self.active_component_count,
            "transition_count": self.transition_count,
            "structural_findings": self.structural_findings,
        }


@dataclass
class TimelineFindingsSection:
    """Feature F4 Activity & Timeline progression synthesis."""
    window_size: int
    total_windows: int
    payload_volume_kb_mean: float
    payload_volume_kb_peak: float
    total_events: int
    event_counts_by_type: Dict[str, int]
    activity_summary: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "window_size": self.window_size,
            "total_windows": self.total_windows,
            "payload_volume_kb_mean": round(self.payload_volume_kb_mean, 2),
            "payload_volume_kb_peak": round(self.payload_volume_kb_peak, 2),
            "total_events": self.total_events,
            "event_counts_by_type": self.event_counts_by_type,
            "activity_summary": self.activity_summary,
        }


@dataclass
class ExplanationFindingsSection:
    """Feature F5 Diagnostic Explanations synthesis."""
    explained_anomalies_count: int
    subsystem_distribution: Dict[str, int]
    key_explanations: List[Dict[str, Any]]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "explained_anomalies_count": self.explained_anomalies_count,
            "subsystem_distribution": self.subsystem_distribution,
            "key_explanations": self.key_explanations,
        }


@dataclass
class ComparisonFindingsSection:
    """Feature F6 Stream Comparison synthesis (present in dual-stream mode)."""
    stream_b_name: str
    stream_b_format: str
    is_same_format: bool
    common_metrics_differential: Dict[str, Any]
    format_specific_differential: Dict[str, Any]
    anomaly_differential: Dict[str, Any]
    pattern_differential: Dict[str, Any]
    key_differences: List[str]
    safe_comparative_conclusions: List[str]
    alignment_disclaimer: str = ALIGNMENT_DISCLAIMER

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stream_b_name": self.stream_b_name,
            "stream_b_format": self.stream_b_format,
            "is_same_format": self.is_same_format,
            "common_metrics_differential": self.common_metrics_differential,
            "format_specific_differential": self.format_specific_differential,
            "anomaly_differential": self.anomaly_differential,
            "pattern_differential": self.pattern_differential,
            "key_differences": self.key_differences,
            "safe_comparative_conclusions": self.safe_comparative_conclusions,
            "alignment_disclaimer": self.alignment_disclaimer,
        }

    @property
    def safe_conclusions(self) -> List[str]:
        return self.safe_comparative_conclusions


@dataclass
class ReportConfig:
    """Configuration options for Feature F7 Automatic Report Generator."""
    title: str = "PRJ_111 Automatic Analysis Report"
    include_raw_telemetry: bool = True
    include_explanations: bool = True
    include_comparison: bool = True
    max_detailed_anomalies: int = 10
    strict_domain_safety: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "title": self.title,
            "include_raw_telemetry": self.include_raw_telemetry,
            "include_explanations": self.include_explanations,
            "include_comparison": self.include_comparison,
            "max_detailed_anomalies": self.max_detailed_anomalies,
            "strict_domain_safety": self.strict_domain_safety,
        }


# =============================================================================
# Root Container: AutomaticAnalysisReport
# =============================================================================

@dataclass
class AutomaticAnalysisReport:
    """Root container for the complete automatic analysis report."""
    report_id: str
    timestamp: str
    mode: str                                  # "SINGLE_STREAM" or "DUAL_STREAM"
    executive_summary: str
    stream_info: StreamSummarySection
    tripartite_findings: List[ReportFinding]
    health: HealthFindingsSection
    anomalies: AnomalyFindingsSection
    patterns: PatternFindingsSection
    timeline: TimelineFindingsSection
    explanations: Optional[ExplanationFindingsSection]
    comparison: Optional[ComparisonFindingsSection]
    limitations_and_uncertainty: List[str]
    unsupported_inferences_guard: List[str] = field(default_factory=lambda: list(UNSUPPORTED_INFERENCES_GUARD))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "report_id": self.report_id,
            "timestamp": self.timestamp,
            "mode": self.mode,
            "executive_summary": self.executive_summary,
            "stream_info": self.stream_info.to_dict(),
            "tripartite_findings": [f.to_dict() for f in self.tripartite_findings],
            "health": self.health.to_dict(),
            "anomalies": self.anomalies.to_dict(),
            "patterns": self.patterns.to_dict(),
            "timeline": self.timeline.to_dict(),
            "explanations": self.explanations.to_dict() if self.explanations else None,
            "comparison": self.comparison.to_dict() if self.comparison else None,
            "limitations_and_uncertainty": self.limitations_and_uncertainty,
            "unsupported_inferences_guard": self.unsupported_inferences_guard,
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent, default=str)

    # -------------------------------------------------------------------------
    # Text / ASCII Rendering (cp1252-safe)
    # -------------------------------------------------------------------------
    def render_text(self) -> str:
        """Renders clean, monospaced ASCII text document safe for Windows cp1252."""
        lines = []
        bar = "=" * 80
        thin_bar = "-" * 80

        lines.append(bar)
        lines.append(f" PRJ_111: AUTOMATIC ANALYSIS REPORT -- {self.stream_info.stream_name}")
        lines.append(f" Report ID  : {self.report_id}")
        lines.append(f" Generated  : {self.timestamp}")
        lines.append(f" Mode       : {self.mode}")
        lines.append(f" Format     : {self.stream_info.detected_format} ({self.stream_info.format_description})")
        lines.append(bar)

        # Executive Summary
        lines.append("\nEXECUTIVE SUMMARY:")
        lines.append(thin_bar)
        lines.append(self.executive_summary)
        lines.append(thin_bar)

        # Stream & Parsing Telemetry
        lines.append("\n1. STREAM & FRAMING TELEMETRY:")
        lines.append(thin_bar)
        lines.append(f"   File Size             : {self.stream_info.file_size_bytes} bytes")
        lines.append(f"   Total Framing Units   : {self.stream_info.total_units}")
        lines.append(f"   Valid Units           : {self.stream_info.valid_units} (Syntactic Integrity: {self.stream_info.integrity_ratio:.4f})")
        lines.append(f"   Invalid Units         : {self.stream_info.invalid_units}")
        lines.append(f"   Truncated Units       : {self.stream_info.truncated_units}")
        lines.append(f"   User Payload Volume   : {self.stream_info.total_payload_bytes} bytes")
        lines.append(f"   Framing Error Count   : {self.stream_info.error_count}")
        lines.append(thin_bar)

        # F1 Health
        lines.append("\n2. STREAM HEALTH ANALYSIS (Selected Priority-1 Indicators):")
        lines.append(thin_bar)
        lines.append(f"   Health Score          : {self.health.health_score:.2f} / 100.00 ({self.health.health_status})")
        lines.append(f"   Integrity Checks      : {self.health.selected_priority1_checks}")
        if self.health.detected_issues:
            lines.append("   Detected Health Issues:")
            for iss in self.health.detected_issues:
                lines.append(f"   - {iss}")
        if self.health.recommendations:
            lines.append("   Recommendations:")
            for rec in self.health.recommendations:
                lines.append(f"   - {rec}")
        lines.append(thin_bar)

        # F2 Anomaly Detection
        lines.append("\n3. AI-BASED ANOMALY DETECTION (Calibrated Isolation Forest):")
        lines.append(thin_bar)
        lines.append(f"   Total Windows         : {self.anomalies.total_windows}")
        lines.append(f"   Anomalous Windows     : {self.anomalies.anomalous_windows} ({self.anomalies.anomaly_rate_pct:.2f}%)")
        lines.append(f"   Decision Threshold    : {self.anomalies.decision_threshold:.4f}")
        lines.append(f"   Peak Anomaly Score    : {self.anomalies.peak_anomaly_score:.4f}")
        lines.append(f"   Mean Anomaly Score    : {self.anomalies.mean_anomaly_score:.4f}")
        lines.append(f"   Severity Breakdown    : {self.anomalies.severity_breakdown}")
        if self.anomalies.anomaly_window_indices:
            lines.append(f"   Anomalous Indices     : {self.anomalies.anomaly_window_indices}")
        lines.append(thin_bar)

        # F3 Pattern Detection
        lines.append("\n4. STREAM PATTERNS & MULTIPLEX STRUCTURE:")
        lines.append(thin_bar)
        lines.append(f"   Dominant Component    : {self.patterns.dominant_component} ({self.patterns.dominant_component_pct:.1f}%)")
        entropy_str = f"{self.patterns.multiplex_entropy:.4f} bits" if self.patterns.multiplex_entropy is not None else "N/A"
        lines.append(f"   Multiplex Diversity   : {self.patterns.active_component_count} components, Entropy: {entropy_str}")
        lines.append(f"   Pattern Transitions   : {self.patterns.transition_count} detected")
        if self.patterns.structural_findings:
            for f in self.patterns.structural_findings:
                lines.append(f"   - {f}")
        lines.append(thin_bar)

        # F4 Activity & Timeline
        lines.append("\n5. ACTIVITY & WINDOW TIMELINE PROGRESSION:")
        lines.append(thin_bar)
        lines.append(f"   Window Size           : {self.timeline.window_size} units/window")
        lines.append(f"   Payload Density Mean  : {self.timeline.payload_volume_kb_mean:.2f} KB/window (Peak: {self.timeline.payload_volume_kb_peak:.2f} KB)")
        lines.append(f"   Timeline Event Total  : {self.timeline.total_events} events")
        lines.append(f"   Event Breakdown       : {self.timeline.event_counts_by_type}")
        lines.append(f"   Activity Summary      : {self.timeline.activity_summary}")
        lines.append(thin_bar)

        # F5 Explanations (if present)
        if self.explanations:
            lines.append("\n6. ANOMALY EXPLANATIONS (Structured Subsystem Attribution):")
            lines.append(thin_bar)
            lines.append(f"   Explained Anomalies   : {self.explanations.explained_anomalies_count}")
            lines.append(f"   Subsystem Distribution: {self.explanations.subsystem_distribution}")
            for expl in self.explanations.key_explanations[:5]:
                lines.append(f"   * Window {expl.get('window_index')}: {expl.get('summary')}")
            lines.append(thin_bar)

        # F6 Comparison (if present)
        if self.comparison:
            lines.append("\n7. DIFFERENTIAL STREAM COMPARISON (Stream A vs Stream B):")
            lines.append(thin_bar)
            lines.append(f"   Stream B Name         : {self.comparison.stream_b_name} ({self.comparison.stream_b_format})")
            lines.append(f"   Format Equivalence    : Same Format = {self.comparison.is_same_format}")
            lines.append(f"   Alignment Disclaimer  : {self.comparison.alignment_disclaimer}")
            lines.append("   Key Differences:")
            for kd in self.comparison.key_differences:
                lines.append(f"   - {kd}")
            lines.append("   Safe Conclusions:")
            for sc in self.comparison.safe_conclusions:
                lines.append(f"   - {sc}")
            lines.append(thin_bar)

        # Tripartite Evidence Register
        lines.append("\n8. TRIPARTITE EVIDENCE REGISTER:")
        lines.append(thin_bar)
        facts = [f for f in self.tripartite_findings if f.category == CATEGORY_OBSERVED_FACT]
        stats = [f for f in self.tripartite_findings if f.category == CATEGORY_STATISTICAL_FINDING]
        interps = [f for f in self.tripartite_findings if f.category == CATEGORY_ENGINEERING_INTERPRETATION]

        lines.append("   [A] OBSERVED FACTS (Deterministic Syntactic Telemetry):")
        for f in facts:
            lines.append(f"   * [{f.subsystem}] {f.title}: {f.statement}")
            lines.append(f"     Evidence: {f.evidence}")

        lines.append("\n   [B] STATISTICAL FINDINGS (Model & Aggregate Measurements):")
        for f in stats:
            lines.append(f"   * [{f.subsystem}] {f.title}: {f.statement}")
            lines.append(f"     Evidence: {f.evidence}")

        lines.append("\n   [C] ENGINEERING INTERPRETATIONS (Supported Grounded Context):")
        for f in interps:
            lines.append(f"   * [{f.subsystem}] {f.title}: {f.statement}")
            lines.append(f"     Evidence: {f.evidence}")
        lines.append(thin_bar)

        # Limitations & Uncertainty
        lines.append("\n9. LIMITATIONS AND UNCERTAINTY:")
        lines.append(thin_bar)
        for lim in self.limitations_and_uncertainty:
            lines.append(f"   - {lim}")
        lines.append(thin_bar)

        # Domain-Safety Guard Notice
        lines.append("\n10. MANDATORY DOMAIN-SAFETY GUARD:")
        lines.append(thin_bar)
        lines.append(f"   NOTICE: {MANDATORY_DOMAIN_SAFETY_NOTICE}\n")
        for g in self.unsupported_inferences_guard:
            lines.append(f"   [GUARD] {g}")
        lines.append(bar)

        return "\n".join(lines)

    # -------------------------------------------------------------------------
    # Markdown Rendering
    # -------------------------------------------------------------------------
    def render_markdown(self) -> str:
        """Renders a clean, comprehensive GitHub Flavored Markdown document."""
        md = []
        md.append(f"# PRJ_111 Automatic Analysis Report: {self.stream_info.stream_name}\n")
        md.append(f"**Report ID:** `{self.report_id}` | **Generated:** `{self.timestamp}` | **Mode:** `{self.mode}`\n")
        md.append("---\n")

        # Executive Summary
        md.append("## Executive Summary\n")
        md.append(f"{self.executive_summary}\n")

        # Stream Telemetry Table
        md.append("## 1. Stream & Framing Metadata\n")
        md.append("| Property | Value |")
        md.append("|---|---|")
        md.append(f"| **File Name** | `{self.stream_info.stream_name}` |")
        md.append(f"| **File Path** | `{self.stream_info.file_path}` |")
        md.append(f"| **File Size** | {self.stream_info.file_size_bytes:,} bytes |")
        md.append(f"| **Detected Format** | `{self.stream_info.detected_format}` ({self.stream_info.format_description}) |")
        md.append(f"| **Total Framing Units** | {self.stream_info.total_units:,} |")
        md.append(f"| **Valid Framing Units** | {self.stream_info.valid_units:,} |")
        md.append(f"| **Invalid Framing Units** | {self.stream_info.invalid_units:,} |")
        md.append(f"| **Truncated Units** | {self.stream_info.truncated_units:,} |")
        md.append(f"| **Total User Payload** | {self.stream_info.total_payload_bytes:,} bytes |")
        md.append(f"| **Framing Integrity Ratio** | `{self.stream_info.integrity_ratio:.4f}` |")
        md.append(f"| **Total Framing Errors** | {self.stream_info.error_count} |\n")

        # Health Section
        md.append("## 2. Stream Health Analysis (F1)\n")
        status_badge = f"[{self.health.health_status}]"
        md.append(f"**Overall Health Status:** {status_badge} ({self.health.health_score:.2f} / 100.00)\n")
        md.append("### Selected Priority-1 Integrity Indicators:")
        for k, v in self.health.selected_priority1_checks.items():
            md.append(f"- **{k}**: `{v}`")
        if self.health.detected_issues:
            md.append("\n### Detected Health Observations:")
            for iss in self.health.detected_issues:
                md.append(f"- {iss}")
        if self.health.recommendations:
            md.append("\n### Operational Recommendations:")
            for rec in self.health.recommendations:
                md.append(f"- {rec}")
        md.append("")

        # Anomaly Section
        md.append("## 3. AI Anomaly Detection (F2)\n")
        md.append(f"- **Model**: Calibrated Isolation Forest (Contamination: 0.05, Decision Threshold: `{self.anomalies.decision_threshold:.4f}`)")
        md.append(f"- **Window Statistics**: {self.anomalies.anomalous_windows} / {self.anomalies.total_windows} windows flagged as anomalous ({self.anomalies.anomaly_rate_pct:.2f}%)")
        md.append(f"- **Score Extremes**: Peak Score = `{self.anomalies.peak_anomaly_score:.4f}`, Mean Score = `{self.anomalies.mean_anomaly_score:.4f}`")
        md.append(f"- **Severity Tier Breakdown**: `{self.anomalies.severity_breakdown}`")
        if self.anomalies.anomaly_window_indices:
            md.append(f"- **Flagged Window Indices**: `{self.anomalies.anomaly_window_indices}`\n")

        # Patterns Section
        md.append("## 4. Structural Patterns & Dynamics (F3)\n")
        entropy_val = f"`{self.patterns.multiplex_entropy:.4f}` bits" if self.patterns.multiplex_entropy is not None else "*Not Applicable*"
        md.append(f"- **Dominant Component**: `{self.patterns.dominant_component}` ({self.patterns.dominant_component_pct:.1f}% share)")
        md.append(f"- **Multiplex Diversity**: {self.patterns.active_component_count} active components (Shannon Entropy: {entropy_val})")
        md.append(f"- **Pattern Transitions**: {self.patterns.transition_count} structural transitions detected")
        if self.patterns.structural_findings:
            md.append("\n### Structural Findings:")
            for f in self.patterns.structural_findings:
                md.append(f"- {f}")
        md.append("")

        # Timeline Section
        md.append("## 5. Activity & Timeline Progression (F4)\n")
        md.append(f"- **Window Size**: {self.timeline.window_size} units per window")
        md.append(f"- **Mean Payload Density**: {self.timeline.payload_volume_kb_mean:.2f} KB/window (Peak: {self.timeline.payload_volume_kb_peak:.2f} KB)")
        md.append(f"- **Total Timeline Events**: {self.timeline.total_events} events logged (`{self.timeline.event_counts_by_type}`)")
        md.append(f"- **Progression Summary**: {self.timeline.activity_summary}\n")

        # Explanations Section (if present)
        if self.explanations:
            md.append("## 6. Diagnostic Anomaly Explanations (F5)\n")
            md.append(f"- **Explained Anomalous Windows**: {self.explanations.explained_anomalies_count}")
            md.append(f"- **Diagnostic Subsystem Distribution**: `{self.explanations.subsystem_distribution}`")
            if self.explanations.key_explanations:
                md.append("\n### Key Anomaly Explanations:")
                for expl in self.explanations.key_explanations[:5]:
                    md.append(f"- **Window {expl.get('window_index')}**: {expl.get('summary')}")
            md.append("")

        # Comparison Section (if present)
        if self.comparison:
            md.append("## 7. Differential Stream Comparison (F6)\n")
            md.append(f"**Compared Against:** `{self.comparison.stream_b_name}` (`{self.comparison.stream_b_format}`) | Same Format: `{self.comparison.is_same_format}`\n")
            md.append("> [!NOTE]")
            md.append(f"> {self.comparison.alignment_disclaimer}\n")
            md.append("### Key Telemetric Differences:")
            for kd in self.comparison.key_differences:
                md.append(f"- {kd}")
            md.append("\n### Safe Comparative Conclusions:")
            for sc in self.comparison.safe_conclusions:
                md.append(f"- {sc}")
            md.append("")

        # Tripartite Register
        md.append("## 8. Epistemological Tripartite Register\n")
        facts = [f for f in self.tripartite_findings if f.category == CATEGORY_OBSERVED_FACT]
        stats = [f for f in self.tripartite_findings if f.category == CATEGORY_STATISTICAL_FINDING]
        interps = [f for f in self.tripartite_findings if f.category == CATEGORY_ENGINEERING_INTERPRETATION]

        md.append("### A. Observed Facts (Deterministic Syntactic Telemetry)\n")
        md.append("| Subsystem | Title | Observation Statement | Grounding Evidence |")
        md.append("|---|---|---|---|")
        for f in facts:
            md.append(f"| `{f.subsystem}` | **{f.title}** | {f.statement} | `{f.evidence}` |")

        md.append("\n### B. Statistical Findings (Model & Aggregate Measurements)\n")
        md.append("| Subsystem | Title | Statistical Finding | Measurement Evidence |")
        md.append("|---|---|---|---|")
        for f in stats:
            md.append(f"| `{f.subsystem}` | **{f.title}** | {f.statement} | `{f.evidence}` |")

        md.append("\n### C. Engineering Interpretations (Grounded Contextual Synthesis)\n")
        md.append("| Subsystem | Title | Contextual Interpretation | Supporting Telemetry |")
        md.append("|---|---|---|---|")
        for f in interps:
            md.append(f"| `{f.subsystem}` | **{f.title}** | {f.statement} | `{f.evidence}` |")
        md.append("")

        # Limitations & Uncertainty
        md.append("## 9. Limitations & Uncertainty\n")
        for lim in self.limitations_and_uncertainty:
            md.append(f"- {lim}")
        md.append("")

        # Domain-Safety Guard Notice
        md.append("## 10. Mandatory Domain-Safety Guard Notice\n")
        md.append(f"> [!IMPORTANT]\n> **Notice:** {MANDATORY_DOMAIN_SAFETY_NOTICE}\n")
        for g in self.unsupported_inferences_guard:
            md.append(f"- {g}")
        md.append("\n---\n*Report generated by PRJ_111 DVB-S2 Analysis Application (Automated Verification Pipeline).*")

        return "\n".join(md)

    # -------------------------------------------------------------------------
    # HTML5 Standalone Rendering
    # -------------------------------------------------------------------------
    def render_html(self) -> str:
        """Renders self-contained, offline HTML5 report with PRJ_111 dark theme."""
        status_color = "#34d399" if self.health.health_status == "HEALTHY" else ("#fbbf24" if self.health.health_status == "WARNING" else "#f87171")
        facts = [f for f in self.tripartite_findings if f.category == CATEGORY_OBSERVED_FACT]
        stats = [f for f in self.tripartite_findings if f.category == CATEGORY_STATISTICAL_FINDING]
        interps = [f for f in self.tripartite_findings if f.category == CATEGORY_ENGINEERING_INTERPRETATION]

        def make_rows(finding_list):
            out = []
            for f in finding_list:
                out.append(f"<tr><td><code>{f.subsystem}</code></td><td><strong>{f.title}</strong></td><td>{f.statement}</td><td><code>{f.evidence}</code></td></tr>")
            return "\n".join(out)

        comparison_card = ""
        if self.comparison:
            kd_items = "".join(f"<li>{kd}</li>" for kd in self.comparison.key_differences)
            sc_items = "".join(f"<li>{sc}</li>" for sc in self.comparison.safe_comparative_conclusions)
            comparison_card = f"""
    <div class="card">
      <h2>Differential Stream Comparison (F6)</h2>
      <p><strong>Stream B:</strong> <code>{self.comparison.stream_b_name}</code> (<code>{self.comparison.stream_b_format}</code>) | Same Format: <code>{self.comparison.is_same_format}</code></p>
      <div class="disclaimer-box">
        <strong>Cross-Stream Alignment Disclaimer:</strong>
        <p>{self.comparison.alignment_disclaimer}</p>
      </div>
      <h3 style="margin-top: 16px;">Key Telemetric Differences</h3>
      <ul>{kd_items}</ul>
      <h3 style="margin-top: 16px;">Safe Comparative Conclusions</h3>
      <ul>{sc_items}</ul>
    </div>"""

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>PRJ_111: {self.stream_info.stream_name} -- Analysis Report</title>
  <style>
    :root {{
      --bg-main: #0f172a;
      --bg-card: #1e293b;
      --border: #334155;
      --text: #f8fafc;
      --text-dim: #94a3b8;
      --accent: #38bdf8;
      --green: #34d399;
      --amber: #fbbf24;
      --red: #f87171;
    }}
    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      background: var(--bg-main);
      color: var(--text);
      line-height: 1.6;
      margin: 0;
      padding: 24px;
    }}
    .container {{ max-width: 1100px; margin: 0 auto; }}
    .header {{ border-bottom: 2px solid var(--border); padding-bottom: 16px; margin-bottom: 24px; }}
    .badge {{ display: inline-block; padding: 4px 10px; border-radius: 4px; font-weight: bold; font-size: 13px; }}
    .card {{ background: var(--bg-card); border: 1px solid var(--border); border-radius: 8px; padding: 20px; margin-bottom: 24px; }}
    h1, h2, h3 {{ color: var(--accent); }}
    table {{ width: 100%; border-collapse: collapse; margin-top: 12px; }}
    th, td {{ border: 1px solid var(--border); padding: 10px; text-align: left; font-size: 14px; }}
    th {{ background: #0b1120; color: var(--accent); }}
    code {{ background: #0b1120; padding: 2px 6px; border-radius: 4px; font-size: 13px; color: #38bdf8; }}
    .guard-box {{ background: rgba(248, 113, 113, 0.1); border-left: 4px solid var(--red); padding: 14px; margin-top: 16px; }}
    .disclaimer-box {{ background: rgba(56, 189, 248, 0.1); border-left: 4px solid var(--accent); padding: 14px; margin-top: 16px; }}
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <h1>PRJ_111 Automatic Analysis Report</h1>
      <p>Stream: <code>{self.stream_info.stream_name}</code> | Report ID: <code>{self.report_id}</code> | Generated: <code>{self.timestamp}</code></p>
      <span class="badge" style="background: {status_color}; color: #000;">Health: {self.health.health_status} ({self.health.health_score:.1f}/100)</span>
      <span class="badge" style="background: var(--border); color: var(--text);">Format: {self.stream_info.detected_format}</span>
      <span class="badge" style="background: var(--border); color: var(--text);">Mode: {self.mode}</span>
    </div>

    <div class="card">
      <h2>Executive Summary</h2>
      <p>{self.executive_summary}</p>
    </div>

    <div class="card">
      <h2>Stream & Framing Metadata</h2>
      <table>
        <tr><th>Property</th><th>Value</th><th>Property</th><th>Value</th></tr>
        <tr><td>File Path</td><td><code>{self.stream_info.file_path}</code></td><td>File Size</td><td>{self.stream_info.file_size_bytes:,} bytes</td></tr>
        <tr><td>Total Units</td><td>{self.stream_info.total_units:,}</td><td>Framing Integrity</td><td>{self.stream_info.integrity_ratio:.4f}</td></tr>
        <tr><td>Valid Units</td><td>{self.stream_info.valid_units:,}</td><td>Invalid Units</td><td>{self.stream_info.invalid_units:,}</td></tr>
        <tr><td>User Payload</td><td>{self.stream_info.total_payload_bytes:,} bytes</td><td>Total Errors</td><td>{self.stream_info.error_count}</td></tr>
      </table>
    </div>
{comparison_card}
    <div class="card">
      <h2>Epistemological Tripartite Register</h2>
      <h3>1. Observed Facts (Deterministic Syntactic Telemetry)</h3>
      <table>
        <tr><th>Subsystem</th><th>Title</th><th>Statement</th><th>Evidence</th></tr>
        {make_rows(facts)}
      </table>

      <h3 style="margin-top: 24px;">2. Statistical Findings (Model & Aggregate Measurements)</h3>
      <table>
        <tr><th>Subsystem</th><th>Title</th><th>Finding</th><th>Evidence</th></tr>
        {make_rows(stats)}
      </table>

      <h3 style="margin-top: 24px;">3. Engineering Interpretations (Grounded Contextual Synthesis)</h3>
      <table>
        <tr><th>Subsystem</th><th>Title</th><th>Interpretation</th><th>Evidence</th></tr>
        {make_rows(interps)}
      </table>
    </div>

    <div class="card">
      <h2>Limitations and Uncertainty</h2>
      <ul>
        {"".join(f"<li>{lim}</li>" for lim in self.limitations_and_uncertainty)}
      </ul>
      <div class="guard-box">
        <strong>MANDATORY DOMAIN-SAFETY NOTICE:</strong>
        <p>{MANDATORY_DOMAIN_SAFETY_NOTICE}</p>
      </div>
    </div>
  </div>
</body>
</html>"""
        return html

    def save_all_formats(self, output_dir: Union[str, Path], base_name: str) -> Dict[str, Path]:
        """Saves JSON, Markdown, Text, and HTML reports to disk."""
        out_dir = Path(output_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        paths = {
            "json": out_dir / f"{base_name}.json",
            "md": out_dir / f"{base_name}.md",
            "txt": out_dir / f"{base_name}.txt",
            "html": out_dir / f"{base_name}.html",
        }
        paths["json"].write_text(self.to_json(indent=2), encoding="utf-8")
        paths["md"].write_text(self.render_markdown(), encoding="utf-8")
        paths["txt"].write_text(self.render_text(), encoding="utf-8")
        paths["html"].write_text(self.render_html(), encoding="utf-8")
        return paths


# =============================================================================
# Generator Engine: AutomaticReportGenerator
# =============================================================================

class AutomaticReportGenerator:
    """
    Core synthesis engine for Feature F7: Automatic Analysis Report.
    Consumes authoritative outputs from upstream layers and populates
    the complete AutomaticAnalysisReport.
    """

    def __init__(self, config: Optional[ReportConfig] = None):
        self.config = config or ReportConfig()

    def generate_from_timeline(
        self,
        timeline: StreamTimeline,
        explanation_report: Optional[ExplanationReport] = None,
        comparison_report: Optional[StreamComparisonReport] = None,
        stream_path: Optional[Union[str, Path]] = None,
        file_size_bytes: Optional[int] = None,
    ) -> AutomaticAnalysisReport:
        """
        Generates an AutomaticAnalysisReport from a pre-computed StreamTimeline,
        optional ExplanationReport, and optional StreamComparisonReport.
        """
        fmt = timeline.format
        stream_name = timeline.stream_name
        num_windows = timeline.total_windows
        points = timeline.points

        # 1. Stream Summary Section
        total_units = timeline.total_units
        valid_units = sum(p.valid_units for p in points) if points else total_units
        invalid_units = sum(p.invalid_units for p in points) if points else 0
        truncated_units = sum(1 for p in points if p.unit_count < timeline.window_size and p.window_index == len(points) - 1)
        total_payload = sum(p.payload_bytes for p in points) if points else 0
        error_count = sum(p.error_count for p in points) if points else 0
        integ_ratio = (valid_units / max(1, total_units)) if total_units > 0 else 1.0

        if valid_units == 0 and invalid_units == 0 and total_units > 0:
            valid_units = total_units

        fmt_desc = {
            StreamFormat.MPEG_TS: "MPEG-2 Transport Stream (188B Packets)",
            StreamFormat.GSE: "Generic Stream Encapsulation (Variable PDUs)",
            StreamFormat.BB_FRAME: "DVB-S2 Baseband Frame (Continuous Transmission)",
        }.get(fmt, "Unknown Format")

        stream_info = StreamSummarySection(
            stream_name=stream_name,
            file_path=str(stream_path or stream_name),
            file_size_bytes=file_size_bytes or timeline.total_bytes,
            detected_format=fmt.value,
            format_description=fmt_desc,
            total_units=total_units,
            valid_units=valid_units,
            invalid_units=invalid_units,
            truncated_units=truncated_units,
            total_payload_bytes=total_payload,
            integrity_ratio=integ_ratio,
            error_count=error_count,
        )

        # 2. Health Section
        mean_health = (sum(p.health_score for p in points) / len(points)) if points else 100.0
        health_status = "HEALTHY" if mean_health >= 90.0 else ("WARNING" if mean_health >= 70.0 else "CRITICAL")
        p1_checks = {
            "framing_sync_integrity": f"{integ_ratio * 100:.2f}%",
            "error_packet_count": error_count,
            "stream_continuity": "NO_GAPS" if error_count == 0 else f"{error_count}_FAULTS",
        }
        health_sec = HealthFindingsSection(
            health_score=mean_health,
            health_status=health_status,
            selected_priority1_checks=p1_checks,
            detected_issues=["Non-zero framing errors observed in stream telemetry."] if error_count > 0 else [],
            recommendations=["Monitor stream continuity and framing boundary alignment."] if error_count > 0 else ["Maintain nominal receiver telemetry monitoring."],
        )

        # 3. Anomaly Section
        anom_points = [p for p in points if p.is_anomaly]
        anom_indices = [p.window_index for p in anom_points]
        anom_count = len(anom_points)
        anom_rate = (anom_count / max(1, num_windows)) * 100.0
        peak_score = max((p.anomaly_score for p in points), default=0.0)
        mean_score = (sum(p.anomaly_score for p in points) / max(1, num_windows))

        sev_dist: Dict[str, int] = {"NORMAL": 0, "LOW": 0, "MEDIUM": 0, "HIGH": 0, "CRITICAL": 0}
        for p in points:
            sev_dist[p.anomaly_severity] = sev_dist.get(p.anomaly_severity, 0) + 1

        anom_sec = AnomalyFindingsSection(
            total_windows=num_windows,
            anomalous_windows=anom_count,
            anomaly_rate_pct=anom_rate,
            peak_anomaly_score=peak_score,
            mean_anomaly_score=mean_score,
            decision_threshold=timeline.anomaly_threshold,
            severity_breakdown=sev_dist,
            anomaly_window_indices=anom_indices,
        )

        # 4. Pattern Section
        dom_comp = "N/A"
        dom_pct = 0.0
        entropy = None
        active_comps = 0
        trans_count = sum(1 for p in points if p.has_transition)
        findings_list: List[str] = []

        if points:
            m = points[0].format_specific_metrics
            if "dominant_pid_summary" in m:
                dom_comp = m["dominant_pid_summary"]
                dom_pct = m.get("dominant_pid_pct", 0.0)
                entropy = m.get("pid_entropy")
                active_comps = m.get("unique_pids", 1)
                findings_list.append(f"MPEG-TS multiplex dominated by PID {m.get('dominant_pid')} ({dom_pct:.1f}%).")
            elif "modal_dfl_bits" in m or "modal_dfl" in m:
                dfl_val = m.get("modal_dfl_bits", m.get("modal_dfl"))
                dom_comp = f"DFL {dfl_val} bits"
                dom_pct = 100.0
                active_comps = 1
                for pf in points[0].pattern_findings:
                    if pf.get("pattern_type") == "BB_DFL_DISTRIBUTION":
                        supp = pf.get("supporting_metrics", {})
                        if "modal_percentage" in supp:
                            dom_pct = float(supp["modal_percentage"])
                        if "unique_dfl_count" in supp:
                            active_comps = int(supp["unique_dfl_count"])
                findings_list.append(f"DVB-S2 Baseband Header modal DFL is {dfl_val} bits ({dom_pct:.1f}% modal share).")
            elif "dominant_protocol" in m:
                dom_comp = f"Protocol {m['dominant_protocol']}"
                dom_pct = 100.0
                active_comps = 1
                findings_list.append(f"GSE encapsulation using {m['dominant_protocol']}.")

        pat_sec = PatternFindingsSection(
            dominant_component=dom_comp,
            dominant_component_pct=dom_pct,
            multiplex_entropy=entropy,
            active_component_count=active_comps,
            transition_count=trans_count,
            structural_findings=findings_list,
        )

        # 5. Timeline Section
        pl_mean = (sum(p.payload_kb for p in points) / max(1, num_windows)) if points else 0.0
        pl_peak = max((p.payload_kb for p in points), default=0.0)
        tot_events = len(timeline.events)
        ev_counts: Dict[str, int] = {}
        for ev in timeline.events:
            ev_counts[ev.event_type] = ev_counts.get(ev.event_type, 0) + 1

        tl_sec = TimelineFindingsSection(
            window_size=timeline.window_size,
            total_windows=num_windows,
            payload_volume_kb_mean=pl_mean,
            payload_volume_kb_peak=pl_peak,
            total_events=tot_events,
            event_counts_by_type=ev_counts,
            activity_summary=f"Stream sliced into {num_windows} sequential windows with average payload density of {pl_mean:.2f} KB/window.",
        )

        # 6. Explanations Section (if provided)
        expl_sec = None
        if explanation_report:
            key_expls = []
            sub_dist: Dict[str, int] = {}
            for anom_expl in explanation_report.explanations:
                c_name = getattr(anom_expl, "native_component", getattr(anom_expl, "subsystem", "UNKNOWN"))
                sub_dist[c_name] = sub_dist.get(c_name, 0) + 1

            for anom_expl in explanation_report.explanations[:self.config.max_detailed_anomalies]:
                c_name = getattr(anom_expl, "native_component", getattr(anom_expl, "subsystem", "UNKNOWN"))
                key_expls.append({
                    "window_index": anom_expl.window_index,
                    "severity": getattr(anom_expl, "anomaly_severity", getattr(anom_expl, "severity", "NORMAL")),
                    "subsystem": c_name,
                    "summary": anom_expl.concise_summary,
                })
            expl_sec = ExplanationFindingsSection(
                explained_anomalies_count=explanation_report.anomaly_count,
                subsystem_distribution=sub_dist,
                key_explanations=key_expls,
            )

        # 7. Comparison Section (if provided)
        comp_sec = None
        if comparison_report:
            comp_sec = ComparisonFindingsSection(
                stream_b_name=comparison_report.stream_b_name,
                stream_b_format=comparison_report.format_b,
                is_same_format=comparison_report.is_same_format,
                common_metrics_differential={k: v.to_dict() for k, v in comparison_report.common.metrics.items()},
                format_specific_differential={k: v.to_dict() for k, v in comparison_report.format_specific.metrics.items()},
                anomaly_differential=comparison_report.anomalies.to_dict(),
                pattern_differential=comparison_report.patterns.to_dict(),
                key_differences=comparison_report.summary.key_differences,
                safe_comparative_conclusions=comparison_report.summary.safe_conclusions,
                alignment_disclaimer=comparison_report.windows.alignment_disclaimer,
            )

        # 8. Tripartite Register Compilation
        tripartite_findings = self._build_tripartite_register(
            stream_info, health_sec, anom_sec, pat_sec, tl_sec, expl_sec, comp_sec, points, fmt
        )

        # 9. Limitations & Uncertainty
        limitations = [
            "Analysis is based strictly on parsed digital receiver output units without external demodulator RF clock telemetry.",
            "Temporal window progression reflects spatial sequential packet/frame ordering, not broadcast wall-clock timestamps.",
            "Unsupervised anomaly detection identifies statistical outliers relative to stream baseline; does not establish physical transmission failure.",
        ]
        if truncated_units > 0:
            limitations.append(f"Stream contains {truncated_units} edge window(s) with unit count below nominal window size at the capture boundary.")
        if fmt == StreamFormat.MPEG_TS:
            limitations.append("Transport stream component analysis uses dominant PID numbers; specific program and stream-type roles remain unverified without PSI/SI tables.")

        mode_str = "DUAL_STREAM" if comparison_report is not None else "SINGLE_STREAM"

        # Executive summary generation
        exec_summary = self._generate_executive_summary(
            stream_info, health_sec, anom_sec, pat_sec, mode_str, comparison_report
        )

        report_id = f"REP_{fmt.value.upper()}_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}"

        return AutomaticAnalysisReport(
            report_id=report_id,
            timestamp=datetime.now(timezone.utc).isoformat(),
            mode=mode_str,
            executive_summary=exec_summary,
            stream_info=stream_info,
            tripartite_findings=tripartite_findings,
            health=health_sec,
            anomalies=anom_sec,
            patterns=pat_sec,
            timeline=tl_sec,
            explanations=expl_sec,
            comparison=comp_sec,
            limitations_and_uncertainty=limitations,
            unsupported_inferences_guard=list(UNSUPPORTED_INFERENCES_GUARD),
        )

    def generate_from_handler(
        self,
        handler: StreamHandler,
        stream_b_handler: Optional[StreamHandler] = None,
        window_size_a: Optional[int] = None,
        window_size_b: Optional[int] = None,
    ) -> AutomaticAnalysisReport:
        """
        Orchestrates pipeline execution on StreamHandler inputs and generates
        a single-stream or dual-stream AutomaticAnalysisReport.
        """
        win_a = window_size_a or self._default_window_size(handler.format)
        gen = TimelineGenerator(TimelineConfig())
        timeline_a = gen.generate_from_handler(handler, window_size=win_a)

        expl_engine = AnomalyExplanationEngine(ExplanationConfig())
        expl_report = expl_engine.explain_timeline(timeline_a)

        comp_report = None
        if stream_b_handler:
            win_b = window_size_b or self._default_window_size(stream_b_handler.format)
            timeline_b = gen.generate_from_handler(stream_b_handler, window_size=win_b)
            comp_engine = StreamComparisonEngine(ComparisonConfig())
            comp_report = comp_engine.compare_timelines(timeline_a, timeline_b)

        return self.generate_from_timeline(
            timeline=timeline_a,
            explanation_report=expl_report,
            comparison_report=comp_report,
            stream_path=handler.path,
            file_size_bytes=handler.size_bytes,
        )

    # -------------------------------------------------------------------------
    # Internal Helpers
    # -------------------------------------------------------------------------
    def _default_window_size(self, fmt: StreamFormat) -> int:
        if fmt == StreamFormat.MPEG_TS:
            return 200
        elif fmt == StreamFormat.GSE:
            return 3
        elif fmt == StreamFormat.BB_FRAME:
            return 50
        return 100

    def _build_tripartite_register(
        self,
        info: StreamSummarySection,
        health: HealthFindingsSection,
        anom: AnomalyFindingsSection,
        pat: PatternFindingsSection,
        tl: TimelineFindingsSection,
        expl: Optional[ExplanationFindingsSection],
        comp: Optional[ComparisonFindingsSection],
        points: List[TimelinePoint],
        fmt: StreamFormat,
    ) -> List[ReportFinding]:
        """
        Compiles the Tripartite Register adhering strictly to epistemic safety:
        - OBSERVED_FACT: Direct syntactic observations from parsed units.
        - STATISTICAL_FINDING: Quantitative aggregations and model metrics.
        - ENGINEERING_INTERPRETATION: Grounded contextual synthesis strictly supported
          by F1-F6 evidence without ungrounded causal claims.
        """
        findings: List[ReportFinding] = []

        # =====================================================================
        # 1. OBSERVED FACTS (Deterministic Telemetry)
        # =====================================================================
        findings.append(ReportFinding(
            category=CATEGORY_OBSERVED_FACT,
            subsystem=SUBSYSTEM_FRAMING,
            title="Framing Unit Count and Syntactic Validity",
            statement=f"Parsed {info.total_units} total framing units ({info.valid_units} valid, {info.invalid_units} invalid).",
            evidence=f"total_units={info.total_units}, valid_units={info.valid_units}, invalid_units={info.invalid_units}",
            source_layer="PARSER",
            metrics={"total_units": info.total_units, "valid_units": info.valid_units},
        ))

        findings.append(ReportFinding(
            category=CATEGORY_OBSERVED_FACT,
            subsystem=SUBSYSTEM_FRAMING,
            title="User Payload Volume Extraction",
            statement=f"Extracted {info.total_payload_bytes} total octets of user data payload.",
            evidence=f"total_payload_bytes={info.total_payload_bytes}",
            source_layer="PARSER",
            metrics={"total_payload_bytes": info.total_payload_bytes},
        ))

        if fmt == StreamFormat.MPEG_TS:
            findings.append(ReportFinding(
                category=CATEGORY_OBSERVED_FACT,
                subsystem=SUBSYSTEM_PATTERN,
                title="Dominant PID Identification",
                statement=f"MPEG-TS packets show concentration on dominant component {pat.dominant_component}.",
                evidence=f"dominant_component={pat.dominant_component}, share={pat.dominant_component_pct:.1f}%",
                source_layer="PARSER",
                metrics={"dominant_component": pat.dominant_component},
            ))
            findings.append(ReportFinding(
                category=CATEGORY_OBSERVED_FACT,
                subsystem=SUBSYSTEM_HEALTH,
                title="Priority-1 Continuity and TEI Indicator Check",
                statement=f"Observed {info.error_count} Priority-1 continuity or transport error indicator flags across capture.",
                evidence=f"error_count={info.error_count}",
                source_layer="F1",
                metrics={"error_count": info.error_count},
            ))
        elif fmt == StreamFormat.BB_FRAME:
            findings.append(ReportFinding(
                category=CATEGORY_OBSERVED_FACT,
                subsystem=SUBSYSTEM_PATTERN,
                title="Baseband Frame Header Identification",
                statement=f"Baseband header parsing records modal DFL of {pat.dominant_component}.",
                evidence=f"modal_dfl={pat.dominant_component}",
                source_layer="PARSER",
                metrics={"modal_dfl": pat.dominant_component},
            ))
        elif fmt == StreamFormat.GSE:
            findings.append(ReportFinding(
                category=CATEGORY_OBSERVED_FACT,
                subsystem=SUBSYSTEM_PATTERN,
                title="GSE Encapsulation Header Identification",
                statement=f"GSE protocol encapsulation observed as {pat.dominant_component}.",
                evidence=f"dominant_protocol={pat.dominant_component}",
                source_layer="PARSER",
                metrics={"dominant_protocol": pat.dominant_component},
            ))

        # =====================================================================
        # 2. STATISTICAL FINDINGS (Quantitative / Model Measurements)
        # =====================================================================
        findings.append(ReportFinding(
            category=CATEGORY_STATISTICAL_FINDING,
            subsystem=SUBSYSTEM_HEALTH,
            title="Aggregated Stream Health Score",
            statement=f"Mean stream health score computed as {health.health_score:.2f} / 100.00 ({health.health_status}).",
            evidence=f"health_score={health.health_score:.2f}, status={health.health_status}",
            source_layer="F1",
            metrics={"health_score": health.health_score},
        ))

        findings.append(ReportFinding(
            category=CATEGORY_STATISTICAL_FINDING,
            subsystem=SUBSYSTEM_ANOMALY,
            title="Isolation Forest Anomaly Scoring",
            statement=f"Calibrated Isolation Forest flagged {anom.anomalous_windows} of {anom.total_windows} windows as anomalous ({anom.anomaly_rate_pct:.2f}%).",
            evidence=f"anomalous_windows={anom.anomalous_windows}, peak_score={anom.peak_anomaly_score:.4f}, mean_score={anom.mean_anomaly_score:.4f}",
            source_layer="F2",
            metrics={"anomalous_windows": anom.anomalous_windows, "peak_anomaly_score": anom.peak_anomaly_score},
        ))

        if pat.multiplex_entropy is not None:
            findings.append(ReportFinding(
                category=CATEGORY_STATISTICAL_FINDING,
                subsystem=SUBSYSTEM_PATTERN,
                title="Multiplex Shannon Entropy Measurement",
                statement=f"Multiplex distribution Shannon entropy measured at {pat.multiplex_entropy:.4f} bits across {pat.active_component_count} active components.",
                evidence=f"shannon_entropy={pat.multiplex_entropy:.4f}, active_components={pat.active_component_count}",
                source_layer="F3",
                metrics={"entropy": pat.multiplex_entropy},
            ))

        findings.append(ReportFinding(
            category=CATEGORY_STATISTICAL_FINDING,
            subsystem=SUBSYSTEM_TIMELINE,
            title="Payload Density Distribution Across Windows",
            statement=f"Window payload density averages {tl.payload_volume_kb_mean:.2f} KB/window with peak window payload of {tl.payload_volume_kb_peak:.2f} KB.",
            evidence=f"mean_kb={tl.payload_volume_kb_mean:.2f}, peak_kb={tl.payload_volume_kb_peak:.2f}",
            source_layer="F4",
            metrics={"mean_payload_kb": tl.payload_volume_kb_mean, "peak_payload_kb": tl.payload_volume_kb_peak},
        ))

        # =====================================================================
        # 3. ENGINEERING INTERPRETATIONS (Grounded Contextual Synthesis)
        # =====================================================================
        # Epistemic Rule: Must not claim "cold start", "traffic bursts", or "video stream role"
        if fmt == StreamFormat.MPEG_TS:
            findings.append(ReportFinding(
                category=CATEGORY_ENGINEERING_INTERPRETATION,
                subsystem=SUBSYSTEM_PATTERN,
                title="Multiplex Bandwidth Allocation Concentration",
                statement=f"Transport stream capacity is predominantly allocated to dominant PID {pat.dominant_component} (accounting for {pat.dominant_component_pct:.1f}% of units).",
                evidence=f"Dominant PID share: {pat.dominant_component_pct:.1f}%, active PIDs: {pat.active_component_count}",
                source_layer="F3",
            ))
        elif fmt == StreamFormat.BB_FRAME:
            findings.append(ReportFinding(
                category=CATEGORY_ENGINEERING_INTERPRETATION,
                subsystem=SUBSYSTEM_PATTERN,
                title="Baseband Transmission Mode Homogeneity",
                statement=f"Baseband stream exhibits modal DFL of {pat.dominant_component} across analyzed sequential window groups.",
                evidence=f"Dominant modal DFL: {pat.dominant_component}",
                source_layer="F3",
            ))

        # Edge / boundary window neutral interpretation
        if info.truncated_units > 0 or (points and points[-1].unit_count < tl.window_size):
            last_idx = len(points) - 1 if points else 0
            last_cnt = points[-1].unit_count if points else 0
            findings.append(ReportFinding(
                category=CATEGORY_ENGINEERING_INTERPRETATION,
                subsystem=SUBSYSTEM_FRAMING,
                title="Capture Boundary Window Sizing",
                statement=f"Window {last_idx} unit count deviation ({last_cnt} units vs nominal {tl.window_size}) occurs at the stream capture boundary.",
                evidence=f"window_index={last_idx}, unit_count={last_cnt}, nominal_size={tl.window_size}",
                source_layer="F4",
            ))

        # Initial window anomaly observation (neutral wording)
        if 0 in anom.anomaly_window_indices and points:
            w0_units = points[0].unit_count
            findings.append(ReportFinding(
                category=CATEGORY_ENGINEERING_INTERPRETATION,
                subsystem=SUBSYSTEM_ANOMALY,
                title="Initial Window Baseline Offset",
                statement=f"Feature deviation in Window 0 coincides with the initial capture boundary (containing {w0_units} units).",
                evidence=f"window_0_score={points[0].anomaly_score:.4f}, units={w0_units}",
                source_layer="F5",
            ))

        # Dual-stream comparative interpretation (if present)
        if comp:
            findings.append(ReportFinding(
                category=CATEGORY_ENGINEERING_INTERPRETATION,
                subsystem=SUBSYSTEM_COMPARISON,
                title="Comparative Cross-Stream Differential Synthesis",
                statement="; ".join(comp.key_differences[:2]) if comp.key_differences else "Streams demonstrate equivalent operational telemetry within configured tolerances.",
                evidence=f"is_same_format={comp.is_same_format}, key_diff_count={len(comp.key_differences)}",
                source_layer="F6",
            ))

        return findings

    def _generate_executive_summary(
        self,
        info: StreamSummarySection,
        health: HealthFindingsSection,
        anom: AnomalyFindingsSection,
        pat: PatternFindingsSection,
        mode: str,
        comp: Optional[StreamComparisonReport],
    ) -> str:
        """Generates a concise, fact-grounded executive summary paragraph."""
        if mode == "DUAL_STREAM" and comp:
            comp_txt = f" Comparative analysis against {comp.stream_b_name} ({comp.format_b}) identified {len(comp.summary.key_differences)} key telemetric differences."
        else:
            comp_txt = ""

        return (
            f"The analyzed digital receiver output stream ({info.stream_name}) consists of {info.total_units:,} parsed "
            f"{info.detected_format} framing units ({info.total_payload_bytes:,} bytes of user payload). Syntactic framing "
            f"integrity is {info.integrity_ratio * 100:.2f}%, yielding an overall stream health score of "
            f"{health.health_score:.2f}/100.00 ({health.health_status}). The calibrated Isolation Forest model flagged "
            f"{anom.anomalous_windows} of {anom.total_windows} sequential windows ({anom.anomaly_rate_pct:.2f}%) as "
            f"statistically anomalous (peak anomaly score: {anom.peak_anomaly_score:.4f}). Multiplex telemetry indicates "
            f"concentration on dominant component {pat.dominant_component} ({pat.dominant_component_pct:.1f}% share).{comp_txt} "
            f"All findings are strictly grounded in parsed packet and baseband telemetry without external physical-layer inference."
        )
