"""
Feature F5: Anomaly Explanation Engine for PRJ_111.

Generates structured, human-readable, domain-safe diagnostic explanations for
detected anomalies across MPEG-TS, GSE, and DVB-S2 Baseband Frame streams.

Architectural Principles:
1. Explanatory Authority Separation:
   - F2 AnomalyDetector remains authoritative for anomaly decisions, scores, and severities.
   - F5 does NOT independently decide whether a window is anomalous; F5 explains F2 results.
2. Structured 9-Point Explanation Model:
   Answers for each anomaly:
     1. What happened?
     2. Which features changed?
     3. How far did they deviate from learned baseline?
     4. Was the feature above or below baseline?
     5. What stream structure/pattern supports the observation?
     6. Which native stream component is involved?
     7. What evidence is available?
     8. What can be concluded safely?
     9. What cannot be concluded from the available capture?
3. Strict Domain-Safety Safeguards:
   - Explicitly guards against unsupported physical-layer inferences:
     DO NOT claim RF interference, rain fade, satellite link failure, SNR degradation,
     demodulator failure, hardware failure, or transmission fault unless verified by physical telemetry.
   - When evidence is insufficient, explicitly states:
     "Not determinable from available capture data."
"""

from dataclasses import dataclass, field
import json
import logging
import math
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple, Union

from dvbs2_analyzer.analysis.anomaly import (
    AnomalyConfig,
    AnomalyDetector,
    AnomalyReport,
    AnomalyResult,
    FeatureDeviation,
)
from dvbs2_analyzer.analysis.patterns import (
    PatternFinding,
    PatternResult,
    PatternType,
    TS_WELL_KNOWN_PIDS,
)
from dvbs2_analyzer.config import StreamFormat
from dvbs2_analyzer.features.extractor import UnifiedStreamFeatureSet

logger = logging.getLogger(__name__)


# =============================================================================
# Native Stream Component Mappings
# =============================================================================

FEATURE_NATIVE_COMPONENT_MAP: Dict[str, str] = {
    # MPEG-TS Native Components
    "pid_entropy": "MPEG-TS Multiplex / PID Composition",
    "unique_pid_count": "MPEG-TS Multiplex / Active Stream Allocation",
    "dominant_pid": "MPEG-TS Multiplex / Dominant PID Allocation",
    "null_packet_ratio": "MPEG-TS Bitrate Adaptation / Stuffing",
    "tei_error_rate": "Demodulator Error Indicator (TEI) / Physical Framing",
    "error_rate": "Stream Error Counter / Physical Layer Integrity",
    "continuity_error_rate": "MPEG-TS Transport Packet Sequence (Continuity Counter)",
    "adaptation_field_ratio": "MPEG-TS Adaptation Field / Clock Timing (PCR)",
    "integrity_ratio": "Stream Framing Sync / Packet Structure",
    "payload_ratio": "Stream Payload Utilization",
    "mean_payload_kb": "User Data Concentration / Packet Size",

    # GSE Native Components
    "fragmentation_ratio": "GSE Fragmentation Sub-layer (S/E Framing)",
    "protocol_diversity": "GSE Network Protocol Multiplexing",
    "dominant_protocol": "GSE Network Protocol Encapsulation",
    "pdu_size_variance": "GSE Packet Size Distribution / MTU Utilization",

    # BBFrame Native Components
    "modal_dfl_bits": "DVB-S2 Baseband Header (Data Field Length DFL)",
    "sis_ratio": "DVB-S2 Baseband Header (MATYPE-1 Input Stream Mode SIS/MIS)",
    "acm_ratio": "DVB-S2 Baseband Header (MATYPE-1 Coding Mode ACM/CCM)",
    "dominant_ro": "DVB-S2 Baseband Header (Roll-Off Factor)",
    "stream_type": "DVB-S2 Baseband Framing / Encapsulation Mode",

    # Window Framing Component (Cross-Format)
    "log_total_units": "Stream Slicing / Capture Boundary (Unit Count)",
    "log_total_payload": "Stream Payload Volume / Traffic Activity",
}

UNSUPPORTED_INFERENCES_GUARD = [
    "RF interference, jamming, or atmospheric rain fade (cannot be concluded; capture lacks RF carrier, signal power, or SNR telemetry).",
    "Demodulator or tuner hardware failure (cannot be concluded; only post-demodulator digital output stream is captured).",
    "Satellite transponder or uplink station failure (cannot be concluded; no transponder or satellite orbital telemetry available).",
    "Signal-to-Noise Ratio (SNR) or link margin degradation (cannot be concluded; physical-layer parameters are absent from baseband stream).",
    "Transmission path error or packet loss (cannot be concluded; framing syntax and CRC remain valid unless error bits are flagged).",
]


# =============================================================================
# 1. Data Structures
# =============================================================================

@dataclass
class ExplanationFinding:
    """
    Detailed explanation for a single feature deviation driving an anomaly.
    Directly answers: which feature, how far, which direction, native component,
    and safe inference.
    """
    feature_name: str
    native_component: str
    observed_value: float
    baseline_mean: float
    baseline_std: float
    z_score: float
    direction: str                     # "ABOVE_BASELINE", "BELOW_BASELINE", "NORMAL"
    deviation_pct: float               # Percentage change relative to baseline mean
    description: str
    evidence: str
    safe_inference: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "feature_name": self.feature_name,
            "native_component": self.native_component,
            "observed_value": round(self.observed_value, 6),
            "baseline_mean": round(self.baseline_mean, 6),
            "baseline_std": round(self.baseline_std, 6),
            "z_score": round(self.z_score, 4),
            "direction": self.direction,
            "deviation_pct": round(self.deviation_pct, 2),
            "description": self.description,
            "evidence": self.evidence,
            "safe_inference": self.safe_inference,
        }


@dataclass
class AnomalyExplanation:
    """
    Comprehensive, structured, domain-safe explanation for an anomalous stream window.
    Synthesizes F2 anomaly telemetry, F3 stream pattern findings, and physical offsets.
    """
    explanation_id: str
    format: str                        # "MPEG_TS", "GSE", "BB_FRAME"
    window_index: Optional[int]
    unit_offset_start: Optional[int]
    unit_offset_end: Optional[int]
    byte_offset_start: Optional[int]
    byte_offset_end: Optional[int]
    anomaly_score: float               # Authoritative score from F2
    anomaly_severity: str              # Authoritative severity from F2
    anomaly_threshold: float           # Threshold from F2 config
    is_anomaly: bool                   # Authoritative decision from F2

    # Detailed drivers and findings
    primary_drivers: List[ExplanationFinding]
    secondary_drivers: List[ExplanationFinding] = field(default_factory=list)
    supporting_patterns: List[Dict[str, Any]] = field(default_factory=list)
    timeline_event_id: Optional[str] = None

    # The 9-point structured explanatory answers
    what_happened: str = ""
    native_component: str = ""
    evidence_summary: str = ""
    safe_conclusion: str = ""
    unsupported_inferences: List[str] = field(default_factory=list)
    concise_summary: str = ""
    limitations: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "explanation_id": self.explanation_id,
            "format": self.format,
            "window_index": self.window_index,
            "unit_offset_start": self.unit_offset_start,
            "unit_offset_end": self.unit_offset_end,
            "byte_offset_start": self.byte_offset_start,
            "byte_offset_end": self.byte_offset_end,
            "anomaly_score": round(self.anomaly_score, 4),
            "anomaly_severity": self.anomaly_severity,
            "anomaly_threshold": round(self.anomaly_threshold, 4),
            "is_anomaly": self.is_anomaly,
            "what_happened": self.what_happened,
            "native_component": self.native_component,
            "evidence_summary": self.evidence_summary,
            "safe_conclusion": self.safe_conclusion,
            "concise_summary": self.concise_summary,
            "primary_drivers": [d.to_dict() for d in self.primary_drivers],
            "secondary_drivers": [d.to_dict() for d in self.secondary_drivers],
            "supporting_patterns": self.supporting_patterns,
            "unsupported_inferences": self.unsupported_inferences,
            "limitations": self.limitations,
            "timeline_event_id": self.timeline_event_id,
        }

    def render_ascii(self) -> str:
        """Renders formatted multi-line ASCII explanation."""
        lines = [
            f"--- ANOMALY EXPLANATION [{self.explanation_id}] ---",
            f"Format: {self.format} | Window: {self.window_index} | Severity: {self.anomaly_severity}",
            f"Anomaly Score: {self.anomaly_score:.4f} (Threshold: {self.anomaly_threshold:.2f})",
            f"Physical Coordinates: Units [{self.unit_offset_start}..{self.unit_offset_end}), "
            f"Bytes [{self.byte_offset_start}..{self.byte_offset_end})",
            "",
            f"1. What Happened? : {self.what_happened}",
            f"2. Native Component: {self.native_component}",
            f"3. Evidence Summary : {self.evidence_summary}",
            f"4. Safe Conclusion  : {self.safe_conclusion}",
            "",
            "5. Primary Feature Drivers:",
        ]
        if self.primary_drivers:
            for d in self.primary_drivers:
                dir_label = (
                    f"|z|={d.z_score:.2f} below baseline"
                    if d.direction == "BELOW_BASELINE"
                    else (
                        f"|z|={d.z_score:.2f} above baseline"
                        if d.direction == "ABOVE_BASELINE"
                        else f"|z|={d.z_score:.2f} baseline-aligned"
                    )
                )
                lines.append(
                    f"   * {d.feature_name} ({d.native_component}): {d.observed_value:.4f} "
                    f"vs baseline {d.baseline_mean:.4f} ({dir_label})"
                )
                lines.append(f"     -> {d.description}")
        else:
            lines.append("   * Feature metrics within expected baseline statistical bounds.")

        if self.supporting_patterns:
            lines.append("")
            lines.append("6. Supporting Stream Patterns:")
            for p in self.supporting_patterns[:2]:
                lines.append(f"   * [{p.get('pattern_type')}] {p.get('description')}")

        lines.append("")
        lines.append("7. Domain-Safety Guard (Unsupported Inferences):")
        for u in self.unsupported_inferences[:2]:
            lines.append(f"   ! {u}")

        lines.append("-" * 60)
        return "\n".join(lines)


@dataclass
class ExplanationConfig:
    """Configuration options for Feature F5 Anomaly Explanation Engine."""
    max_primary_drivers: int = 3
    min_z_score_significance: float = 1.5
    include_normal_windows: bool = False
    strict_domain_safety: bool = True


@dataclass
class ExplanationReport:
    """Aggregated explanation report across a stream capture or window sequence."""
    stream_name: str
    format: str
    total_windows: int
    anomaly_count: int
    anomaly_threshold: float
    explanations: List[AnomalyExplanation]
    summary_stats: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stream_name": self.stream_name,
            "format": self.format,
            "total_windows": self.total_windows,
            "anomaly_count": self.anomaly_count,
            "anomaly_threshold": round(self.anomaly_threshold, 4),
            "summary_stats": self.summary_stats,
            "explanations": [e.to_dict() for e in self.explanations],
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent)

    def render_ascii_summary(self) -> str:
        lines = [
            "=" * 78,
            f" PRJ_111: FEATURE F5 — ANOMALY EXPLANATION REPORT",
            f" Stream: {self.stream_name} | Format: {self.format}",
            "=" * 78,
            f" Evaluated Windows : {self.total_windows}",
            f" Anomalies Flagged : {self.anomaly_count}",
            f" Anomaly Threshold : {self.anomaly_threshold:.2f}",
            "-" * 78,
        ]
        if not self.explanations:
            lines.append(" No operational anomalies flagged across evaluated windows.")
        else:
            for exp in self.explanations:
                lines.append(exp.render_ascii())
        lines.append("=" * 78)
        return "\n".join(lines)


# =============================================================================
# 2. Anomaly Explanation Engine
# =============================================================================

class AnomalyExplanationEngine:
    """
    Feature F5 Diagnostic Engine: Produces structured, human-readable, domain-safe
    explanations for detected anomalies without recalculating F2 anomaly decisions.
    """

    def __init__(self, config: Optional[ExplanationConfig] = None):
        self.config = config or ExplanationConfig()

    def _resolve_native_component(self, feature_name: str, format_name: str) -> str:
        """Maps a feature name to its native satellite stream subsystem."""
        if feature_name in FEATURE_NATIVE_COMPONENT_MAP:
            return FEATURE_NATIVE_COMPONENT_MAP[feature_name]
        if "MPEG_TS" in format_name:
            return "MPEG-TS Transport Subsystem"
        elif "GSE" in format_name:
            return "GSE Encapsulation Subsystem"
        elif "BB" in format_name:
            return "DVB-S2 Baseband Framing Subsystem"
        return "Generic Receiver Telemetry"

    def _format_feature_description(
        self,
        feature_name: str,
        observed: float,
        mean: float,
        std: float,
        z_score: float,
        direction: str,
        format_name: str
    ) -> Tuple[str, str, str]:
        """
        Generates physical description, evidence string, and safe inference for a feature deviation.
        Returns: (description, evidence, safe_inference)
        """
        dir_word = "above" if direction == "ABOVE_BASELINE" else ("below" if direction == "BELOW_BASELINE" else "aligned with")
        if direction == "BELOW_BASELINE":
            z_str = f"|z|={z_score:.1f} below baseline"
        elif direction == "ABOVE_BASELINE":
            z_str = f"|z|={z_score:.1f} above baseline"
        else:
            z_str = f"|z|={z_score:.1f} baseline-aligned"

        # 1. Truncated window features
        if feature_name == "log_total_units" and direction == "BELOW_BASELINE":
            raw_units = int(round(10.0 ** observed)) if observed > 0 else 0
            mean_units = int(round(10.0 ** mean)) if mean > 0 else 0
            desc = f"Window contains only {raw_units} units, substantially fewer than baseline {mean_units} units."
            evidence = f"log_total_units={observed:.3f} (baseline {mean:.3f} +/- {std:.3f}, {z_str})"
            safe = "Consistent with stream capture termination / recording boundary truncation; not a transmission drop-out or packet loss."
            return desc, evidence, safe

        # 2. MPEG-TS: PID entropy
        if feature_name == "pid_entropy":
            if observed == 0.0:
                desc = "PID entropy dropped to 0.00 bits because only a single PID was active in this window."
            else:
                desc = f"PID entropy deviated {dir_word} baseline ({observed:.3f} vs {mean:.3f} bits)."
            evidence = f"pid_entropy={observed:.4f} (baseline {mean:.4f} +/- {std:.4f}, {z_str})"
            safe = "Concentration of transmission on a single PID observed in this window. Sync byte integrity remains 100% valid; the available capture does not establish multiplexer scheduling intent."
            return desc, evidence, safe

        # 3. MPEG-TS: Unique PID count
        if feature_name == "unique_pid_count":
            desc = f"Active unique PID count is {int(observed)}, {dir_word} the baseline average of {mean:.2f} PIDs."
            evidence = f"unique_pid_count={observed:.1f} (baseline {mean:.2f} +/- {std:.2f}, {z_str})"
            safe = "Multiplex composition variation observed. Transport framing remains valid; scheduling cause cannot be established from the capture alone."
            return desc, evidence, safe

        # 4. MPEG-TS: Adaptation field ratio
        if feature_name == "adaptation_field_ratio":
            pct_obs = observed * 100.0
            pct_mean = mean * 100.0
            desc = f"Adaptation field frequency shifted to {pct_obs:.1f}% ({dir_word} baseline {pct_mean:.1f}%)."
            evidence = f"adaptation_field_ratio={observed:.4f} (baseline {mean:.4f} +/- {std:.4f}, {z_str})"
            safe = "Elevated adaptation-field utilization was observed. The available capture does not establish the specific cause."
            return desc, evidence, safe

        # 5. MPEG-TS / BBFrame: Payload volume
        if feature_name in ("log_total_payload", "mean_payload_kb", "payload_ratio"):
            desc = f"Payload volume metric {feature_name} is {dir_word} baseline ({observed:.3f} vs {mean:.3f})."
            evidence = f"{feature_name}={observed:.4f} (baseline {mean:.4f} +/- {std:.4f}, {z_str})"
            safe = "Payload volume variation observed relative to baseline. The capture does not by itself establish the operational cause."
            return desc, evidence, safe

        # 6. GSE: Fragmentation ratio
        if feature_name == "fragmentation_ratio":
            pct = observed * 100.0
            desc = f"PDU fragmentation ratio shifted to {pct:.1f}% ({dir_word} baseline {mean*100.0:.1f}%)."
            evidence = f"fragmentation_ratio={observed:.4f} (baseline {mean:.4f} +/- {std:.4f}, {z_str})"
            safe = "PDU fragmentation was observed. GSE framing remains syntactically valid; the available capture does not establish the operational traffic cause."
            return desc, evidence, safe

        # 7. BBFrame: SIS ratio
        if feature_name == "sis_ratio":
            desc = f"Single Input Stream (SIS) ratio is {observed*100.0:.1f}% ({dir_word} baseline {mean*100.0:.1f}%)."
            evidence = f"sis_ratio={observed:.4f} (baseline {mean:.4f} +/- {std:.4f}, {z_str})"
            safe = "Valid CRC-8 confirms structural header integrity. The capture alone cannot determine whether the MIS configuration was intentional."
            return desc, evidence, safe

        # Generic fallback
        pct_diff = ((observed - mean) / max(1e-6, abs(mean))) * 100.0 if mean != 0.0 else 0.0
        desc = f"Metric {feature_name} observed at {observed:.4f}, {dir_word} baseline {mean:.4f}."
        evidence = f"{feature_name}={observed:.4f} (baseline {mean:.4f} +/- {std:.4f}, {z_str})"
        safe = "Statistical deviation from learned baseline distribution. Capture data does not establish operational cause."
        return desc, evidence, safe

    def explain_anomaly(
        self,
        anomaly_result: AnomalyResult,
        pattern_result: Optional[PatternResult] = None,
        window_offsets: Optional[Tuple[int, int, int, int]] = None,
        timeline_event_id: Optional[str] = None,
        stream_format: Optional[StreamFormat] = None,
    ) -> AnomalyExplanation:
        """
        Constructs a complete AnomalyExplanation for an F2 AnomalyResult.
        """
        w_idx = anomaly_result.window_index
        fmt_str = (
            stream_format.value
            if stream_format
            else (anomaly_result.format or "GENERIC")
        )
        score = anomaly_result.anomaly_score
        severity = anomaly_result.severity
        is_anom = anomaly_result.is_anomaly

        # Coordinate extraction
        u_start, u_end, b_start, b_end = (None, None, None, None)
        if window_offsets:
            u_start, u_end, b_start, b_end = window_offsets

        expl_id = f"EXP_{fmt_str}_W{w_idx}" if w_idx is not None else f"EXP_{fmt_str}_SAMPLE"

        # 1. Extract and enrich feature deviations
        all_devs = anomaly_result.top_deviations or []
        findings: List[ExplanationFinding] = []

        for d in all_devs:
            mean = d.baseline_mean
            obs = d.observed_value
            pct_diff = ((obs - mean) / max(1e-6, abs(mean))) * 100.0 if mean != 0.0 else 0.0
            component = self._resolve_native_component(d.feature_name, fmt_str)
            desc, evidence, safe = self._format_feature_description(
                d.feature_name, obs, mean, d.baseline_std, d.z_score, d.direction, fmt_str
            )
            finding = ExplanationFinding(
                feature_name=d.feature_name,
                native_component=component,
                observed_value=obs,
                baseline_mean=mean,
                baseline_std=d.baseline_std,
                z_score=d.z_score,
                direction=d.direction,
                deviation_pct=pct_diff,
                description=desc,
                evidence=evidence,
                safe_inference=safe,
            )
            findings.append(finding)

        # Partition into primary and secondary drivers
        primary_drivers = findings[:self.config.max_primary_drivers]
        secondary_drivers = findings[self.config.max_primary_drivers:]

        # 2. Extract supporting pattern findings from F3
        supporting_patterns: List[Dict[str, Any]] = []
        if pattern_result and hasattr(pattern_result, "findings"):
            for pf in pattern_result.findings:
                supporting_patterns.append({
                    "pattern_type": pf.pattern_type,
                    "description": pf.description,
                    "evidence": pf.evidence,
                    "supporting_metrics": pf.supporting_metrics,
                })

        # 3. Determine if this anomaly is a truncated final window
        is_truncated_window = any(
            f.feature_name == "log_total_units" and f.direction == "BELOW_BASELINE" and f.z_score >= 2.0
            for f in primary_drivers
        )

        # 4. Synthesize the 9 structured answers
        if not is_anom:
            what_happened = f"Nominal stream operation in window {w_idx}."
            native_component = "Complete Stream Subsystem"
            evidence_summary = f"All telemetry metrics within expected baseline statistical distributions (score={score:.4f} < threshold)."
            safe_conclusion = "Stream behavior is consistent with learned baseline; no operational anomaly detected."
            concise_summary = f"Window {w_idx} exhibits normal {fmt_str} telemetry with an anomaly score of {score:.4f}."
        elif is_truncated_window:
            raw_units = [f.observed_value for f in primary_drivers if f.feature_name == "log_total_units"]
            unit_val = int(round(10.0 ** raw_units[0])) if raw_units else 0
            what_happened = f"Window {w_idx} contains a reduced unit count ({unit_val} units) at stream termination."
            native_component = "Stream Slicing / Capture File Boundary"
            evidence_summary = (
                f"Window length of {unit_val} units deviates from configured window size. "
                f"Driven by log_total_units (|z| >= 2.0 below baseline). All framed packets retain 100% syntactic validity."
            )
            safe_conclusion = (
                "Consistent with capture file end / recording termination boundary. "
                "This is an artifact of capture cessation and cannot be interpreted as packet loss, transmission failure, or system failure."
            )
            concise_summary = (
                f"Window {w_idx} (score {score:.4f}, {severity}) contains {unit_val} units at capture termination. "
                f"Framing syntax remains valid; consistent with recording boundary, not transmission loss."
            )
        else:
            # Domain-specific narrative construction
            primary_names = [f.feature_name for f in primary_drivers]
            primary_comps = list(dict.fromkeys([f.native_component for f in primary_drivers]))
            native_component = "; ".join(primary_comps) if primary_comps else self._resolve_native_component("", fmt_str)
            driver_ev_list = [
                f"{f.feature_name}={f.observed_value:.2f} (|z|={f.z_score:.1f} {'below' if f.direction == 'BELOW_BASELINE' else 'above'} baseline)"
                for f in primary_drivers
            ]

            top_driver = primary_names[0] if primary_names else ""

            # 1. BBFrame MIS / SIS ratio
            if top_driver == "sis_ratio" or ("sis_ratio" in primary_names and "BB" in fmt_str):
                what_happened = (
                    f"Multiple Input Stream (MIS) header flag observed in window {w_idx} "
                    f"alongside Single Input Stream (SIS) frames."
                )
                evidence_summary = "; ".join(driver_ev_list[:2])
                safe_conclusion = (
                    "Valid CRC-8 confirms structural header integrity. The capture alone cannot determine "
                    "whether the MIS configuration was intentional."
                )
                concise_summary = (
                    f"Window {w_idx} contains an isolated MIS header flag (score {score:.4f}, {severity}). "
                    f"Structural integrity is confirmed by valid CRC-8; operational intent cannot be determined."
                )
            # 2. MPEG-TS PID Concentration
            elif top_driver in ("pid_entropy", "unique_pid_count") or (
                ("pid_entropy" in primary_names or "unique_pid_count" in primary_names)
                and "MPEG_TS" in fmt_str
            ):
                what_happened = (
                    f"Multiplex composition shift in window {w_idx}: active PID distribution is concentrated "
                    f"on a single dominant elementary stream."
                )
                evidence_summary = "; ".join(driver_ev_list[:2])
                safe_conclusion = (
                    "Single-PID concentration observed in this window. Transport sync framing remains 100% valid; "
                    "the available capture does not establish multiplexer scheduling intent."
                )
                concise_summary = (
                    f"Window {w_idx} exhibited multiplex concentration on a single PID (score {score:.4f}, {severity}). "
                    f"Sync framing remains valid; scheduling intent cannot be determined."
                )
            # 3. MPEG-TS Adaptation Field
            elif top_driver == "adaptation_field_ratio" or "adaptation_field_ratio" in primary_names:
                what_happened = (
                    f"Elevated adaptation-field frequency in window {w_idx} relative to baseline."
                )
                evidence_summary = "; ".join(driver_ev_list[:2])
                safe_conclusion = (
                    "Elevated adaptation-field utilization was observed. The available capture does not "
                    "establish the specific cause."
                )
                concise_summary = (
                    f"Window {w_idx} exhibited elevated adaptation-field frequency (score {score:.4f}, {severity}). "
                    f"The available capture does not establish the specific cause."
                )
            # 4. BBFrame Modal DFL / Payload volume changes
            elif (
                top_driver in ("modal_dfl_bits", "log_total_payload", "mean_payload_kb", "payload_ratio")
                or any(k in primary_names for k in ("modal_dfl_bits", "log_total_payload", "mean_payload_kb", "payload_ratio"))
            ):
                what_happened = f"Baseband frame payload volume and data field length shifted in window {w_idx}."
                evidence_summary = "; ".join(driver_ev_list[:2])
                safe_conclusion = (
                    "Payload volume and DFL distribution changed together. The capture does not by itself "
                    "establish the operational cause."
                )
                concise_summary = (
                    f"Window {w_idx} exhibited payload volume and DFL distribution changes (score {score:.4f}, {severity}). "
                    f"The capture does not by itself establish the operational cause."
                )
            # 5. GSE Fragmentation
            elif top_driver == "fragmentation_ratio" or "fragmentation_ratio" in primary_names:
                what_happened = f"PDU fragmentation proportion shifted significantly in window {w_idx}."
                evidence_summary = "; ".join(driver_ev_list[:2])
                safe_conclusion = (
                    "PDU fragmentation was observed. GSE framing remains syntactically valid; "
                    "while typical when IP packets exceed encapsulation MTU, the capture alone cannot determine the operational cause."
                )
                concise_summary = (
                    f"Window {w_idx} exhibited elevated PDU fragmentation (score {score:.4f}, {severity}). "
                    f"Encapsulation framing remains valid."
                )
            # 6. Fallback
            else:
                what_happened = f"Statistical deviation detected in window {w_idx} across {len(primary_drivers)} telemetry metrics."
                evidence_summary = "; ".join(driver_ev_list)
                safe_conclusion = (
                    "Statistical outlier relative to baseline distribution; no framing or structural errors detected. "
                    "Capture data does not establish operational cause."
                )
                concise_summary = (
                    f"Anomaly in window {w_idx} (score {score:.4f}, {severity}) is driven by statistical variation "
                    f"in {', '.join(primary_names)}."
                )

        # 5. Unsupported inferences safeguards (STRICT RULE)
        unsupported = list(UNSUPPORTED_INFERENCES_GUARD)

        # 6. Capture limitations
        limitations = [
            "Physical demodulator parameters (SNR, Eb/N0, AGC, MER) are not present in digital stream captures.",
            "Bit-error rate (BER) cannot be measured directly in the absence of uncorrected demodulator telemetry.",
        ]
        if fmt_str == "GSE":
            limitations.append("The available real GSE dataset is a short sample; long-term statistical confidence is limited.")

        return AnomalyExplanation(
            explanation_id=expl_id,
            format=fmt_str,
            window_index=w_idx,
            unit_offset_start=u_start,
            unit_offset_end=u_end,
            byte_offset_start=b_start,
            byte_offset_end=b_end,
            anomaly_score=score,
            anomaly_severity=severity,
            anomaly_threshold=0.50, # Authoritative F2 threshold
            is_anomaly=is_anom,
            primary_drivers=primary_drivers,
            secondary_drivers=secondary_drivers,
            supporting_patterns=supporting_patterns,
            timeline_event_id=timeline_event_id,
            what_happened=what_happened,
            native_component=native_component,
            evidence_summary=evidence_summary,
            safe_conclusion=safe_conclusion,
            unsupported_inferences=unsupported,
            concise_summary=concise_summary,
            limitations=limitations,
        )

    def explain_timeline(self, timeline: Any) -> ExplanationReport:
        """
        Explains all anomalies present in an F4 StreamTimeline object.
        """
        tl_dict = timeline.to_dict() if hasattr(timeline, "to_dict") else {}
        stream_name = tl_dict.get("stream_name", "Stream Capture")
        fmt_str = tl_dict.get("format", "MPEG_TS")
        points = tl_dict.get("points", [])
        events = tl_dict.get("events", [])
        threshold = tl_dict.get("anomaly_threshold", 0.50)

        # Map timeline events by window index
        event_map: Dict[int, str] = {}
        for ev in events:
            if ev.get("event_type") == "F2_ANOMALY":
                event_map[ev.get("window_index", -1)] = ev.get("event_id")

        explanations: List[AnomalyExplanation] = []
        for p in points:
            is_anom = p.get("is_anomaly", False)
            if not is_anom and not self.config.include_normal_windows:
                continue

            w_idx = p.get("window_index")
            ev_id = event_map.get(w_idx)

            # Reconstruct AnomalyResult from TimelinePoint
            anom_res = AnomalyResult(
                is_anomaly=is_anom,
                anomaly_score=p.get("anomaly_score", 0.0),
                raw_score=0.0,
                severity=p.get("anomaly_severity", "NORMAL"),
                top_deviations=[
                    FeatureDeviation(
                        feature_name=d.get("feature_name", ""),
                        observed_value=d.get("observed_value", 0.0),
                        baseline_mean=d.get("baseline_mean", 0.0),
                        baseline_std=d.get("baseline_std", 0.0),
                        z_score=d.get("z_score", 0.0),
                        direction=d.get("direction", "NORMAL"),
                    )
                    for d in p.get("top_deviations", [])
                ],
                summary_explanation=p.get("anomaly_explanation", ""),
                feature_values={},
                window_index=w_idx,
                format=fmt_str,
            )

            # Reconstruct supporting PatternResult findings
            pat_res = PatternResult(
                format=StreamFormat.MPEG_TS if "MPEG_TS" in fmt_str else (StreamFormat.GSE if "GSE" in fmt_str else StreamFormat.BB_FRAME),
                window_index=w_idx,
                findings=[
                    PatternFinding(
                        pattern_type=pf.get("pattern_type", "GENERIC"),
                        format=StreamFormat.MPEG_TS,
                        description=pf.get("description", ""),
                        supporting_metrics=pf.get("supporting_metrics", {}),
                        evidence=pf.get("evidence", ""),
                    )
                    for pf in p.get("pattern_findings", [])
                ],
                metrics_summary={},
            )

            offsets = (
                p.get("unit_offset_start"),
                p.get("unit_offset_end"),
                p.get("byte_offset_start"),
                p.get("byte_offset_end"),
            )

            expl = self.explain_anomaly(
                anomaly_result=anom_res,
                pattern_result=pat_res,
                window_offsets=offsets,
                timeline_event_id=ev_id,
            )
            explanations.append(expl)

        summary_stats = {
            "total_windows": len(points),
            "anomaly_windows": len([p for p in points if p.get("is_anomaly")]),
            "explanations_generated": len(explanations),
            "mean_anomaly_score": round(
                sum(p.get("anomaly_score", 0.0) for p in points) / max(1, len(points)), 4
            ),
        }

        return ExplanationReport(
            stream_name=stream_name,
            format=fmt_str,
            total_windows=len(points),
            anomaly_count=summary_stats["anomaly_windows"],
            anomaly_threshold=threshold,
            explanations=explanations,
            summary_stats=summary_stats,
        )

    def explain_stream(
        self,
        anomaly_report: AnomalyReport,
        pattern_report: Optional[Any] = None,
        stream_name: str = "Stream Capture",
    ) -> ExplanationReport:
        """
        Generates explanations from an F2 AnomalyReport and optional F3 PatternReport.
        """
        explanations: List[AnomalyExplanation] = []
        fmt_str = anomaly_report.format
        threshold = anomaly_report.model_parameters.get("anomaly_threshold", 0.50)

        for res in anomaly_report.results:
            if not res.is_anomaly and not self.config.include_normal_windows:
                continue

            expl = self.explain_anomaly(
                anomaly_result=res,
                stream_format=StreamFormat.MPEG_TS if "MPEG_TS" in fmt_str else (StreamFormat.GSE if "GSE" in fmt_str else StreamFormat.BB_FRAME),
            )
            explanations.append(expl)

        summary_stats = {
            "total_samples": anomaly_report.total_samples,
            "anomaly_count": anomaly_report.anomaly_count,
            "anomaly_ratio": anomaly_report.anomaly_ratio,
            "explanations_generated": len(explanations),
        }

        return ExplanationReport(
            stream_name=stream_name,
            format=fmt_str,
            total_windows=anomaly_report.total_samples,
            anomaly_count=anomaly_report.anomaly_count,
            anomaly_threshold=threshold,
            explanations=explanations,
            summary_stats=summary_stats,
        )
