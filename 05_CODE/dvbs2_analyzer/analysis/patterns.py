"""
Stream Pattern Detection Layer for PRJ_111 (Feature F3).

Analyzes structured stream telemetry from MPEG-TS, GSE, and DVB-S2 Baseband
Frames to identify recurring transmission patterns, multiplex composition,
protocol distributions, encapsulation behaviors, and structural transitions.

Architectural Rule:
MPEG-TS, GSE, and BBFrame are ALTERNATIVE input formats, not a sequential pipeline.
Feature F3 operates natively on the structured objects of each format.
"""

from collections import Counter, defaultdict
from dataclasses import dataclass, field
from enum import Enum
import logging
import math
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Set, Tuple, Union

from dvbs2_analyzer.config import StreamFormat
from dvbs2_analyzer.ingestion.stream_handler import StreamHandler
from dvbs2_analyzer.parsers.bbframe_parser import BBFrame
from dvbs2_analyzer.parsers.gse_parser import GSEPDU
from dvbs2_analyzer.parsers.ts_parser import TSPacket

logger = logging.getLogger(__name__)


# =============================================================================
# 1. Pattern Type Definitions & Data Structures
# =============================================================================

class PatternType(str, Enum):
    """Enumeration of recognized stream pattern classifications."""
    # MPEG-TS Pattern Types
    TS_DOMINANT_PID = "TS_DOMINANT_PID"
    TS_PID_DISTRIBUTION = "TS_PID_DISTRIBUTION"
    TS_PAT_PMT_STRUCTURE = "TS_PAT_PMT_STRUCTURE"
    TS_PCR_ACTIVITY = "TS_PCR_ACTIVITY"
    TS_MULTIPLEX_COMPOSITION = "TS_MULTIPLEX_COMPOSITION"

    # GSE Pattern Types
    GSE_PROTOCOL_DISTRIBUTION = "GSE_PROTOCOL_DISTRIBUTION"
    GSE_PDU_SIZE_DISTRIBUTION = "GSE_PDU_SIZE_DISTRIBUTION"
    GSE_FRAGMENTATION_BEHAVIOR = "GSE_FRAGMENTATION_BEHAVIOR"
    GSE_LABEL_EXTENSION_USAGE = "GSE_LABEL_EXTENSION_USAGE"
    GSE_TRAFFIC_BURST = "GSE_TRAFFIC_BURST"

    # DVB-S2 BBFrame Pattern Types
    BB_DFL_DISTRIBUTION = "BB_DFL_DISTRIBUTION"
    BB_SIS_MIS_BEHAVIOR = "BB_SIS_MIS_BEHAVIOR"
    BB_CCM_ACM_BEHAVIOR = "BB_CCM_ACM_BEHAVIOR"
    BB_ROLLOFF_STABILITY = "BB_ROLLOFF_STABILITY"
    BB_MODE_ADAPTATION = "BB_MODE_ADAPTATION"
    BB_STRUCTURAL_SUMMARY = "BB_STRUCTURAL_SUMMARY"

    # Cross-Window Transition
    PATTERN_TRANSITION = "PATTERN_TRANSITION"


# Well-known MPEG-TS PID Role Assignments (ISO/IEC 13818-1 / ETSI EN 300 468)
TS_WELL_KNOWN_PIDS: Dict[int, str] = {
    0x0000: "PAT (Program Association Table)",
    0x0001: "CAT (Conditional Access Table)",
    0x0002: "TSDT (Transport Stream Description Table)",
    0x0010: "NIT (Network Information Table)",
    0x0011: "SDT/BAT (Service Description Table)",
    0x0012: "EIT (Event Information Table)",
    0x0014: "TDT/TOT (Time & Date Table)",
    0x1FFF: "Null Packet (Padding)",
}


@dataclass
class PatternFinding:
    """
    A specific observed pattern discovered during stream analysis.

    Distinguishes observed physical facts from interpretations without
    conflating pattern detection with anomaly classification.
    """
    pattern_type: str
    format: StreamFormat
    description: str
    supporting_metrics: Dict[str, Any]
    evidence: str
    confidence: float = 1.0
    severity: Optional[str] = None
    window_index: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        """Converts finding to serializable dictionary."""
        return {
            "pattern_type": self.pattern_type,
            "format": self.format.value if hasattr(self.format, "value") else str(self.format),
            "description": self.description,
            "supporting_metrics": self.supporting_metrics,
            "evidence": self.evidence,
            "confidence": round(self.confidence, 4),
            "severity": self.severity,
            "window_index": self.window_index,
        }


@dataclass
class PatternResult:
    """
    Structured pattern detection result for a stream or individual window.
    """
    format: StreamFormat
    findings: List[PatternFinding] = field(default_factory=list)
    metrics_summary: Dict[str, Any] = field(default_factory=dict)
    window_index: Optional[int] = None
    window_size: Optional[int] = None
    has_transitions: bool = False

    def get_findings_by_type(self, pattern_type: str) -> List[PatternFinding]:
        """Returns all findings matching a specific pattern classification."""
        return [f for f in self.findings if f.pattern_type == pattern_type]

    def summary(self) -> str:
        """Returns a human-readable text summary of all findings."""
        fmt_str = self.format.value if hasattr(self.format, "value") else str(self.format)
        win_str = f"Window {self.window_index}" if self.window_index is not None else "Entire Stream"
        lines = [f"=== Pattern Detection [{fmt_str}] ({win_str}) ==="]
        if not self.findings:
            lines.append("  No specific patterns detected (insufficient or empty data).")
        for f in self.findings:
            prefix = f"[{f.pattern_type}]"
            lines.append(f"  * {prefix} {f.description}")
            if f.evidence:
                lines.append(f"    Evidence: {f.evidence}")
        return "\n".join(lines)

    def to_dict(self) -> Dict[str, Any]:
        """Converts result to serializable dictionary."""
        return {
            "format": self.format.value if hasattr(self.format, "value") else str(self.format),
            "window_index": self.window_index,
            "window_size": self.window_size,
            "has_transitions": self.has_transitions,
            "findings": [f.to_dict() for f in self.findings],
            "metrics_summary": self.metrics_summary,
        }


@dataclass
class PatternReport:
    """
    Aggregated stream-level pattern analysis report spanning multiple telemetry windows.
    """
    stream_name: str
    format: StreamFormat
    total_units_analyzed: int
    total_windows: int
    findings: List[PatternFinding] = field(default_factory=list)
    window_results: List[PatternResult] = field(default_factory=list)
    summary_text: str = ""

    def summary(self) -> str:
        """Returns comprehensive formatted summary of pattern findings."""
        fmt_str = self.format.value if hasattr(self.format, "value") else str(self.format)
        lines = [
            "=" * 72,
            f" PRJ_111: STREAM PATTERN DETECTION REPORT",
            f" Stream: {self.stream_name} | Format: {fmt_str}",
            f" Units Analyzed: {self.total_units_analyzed:,} | Windows: {self.total_windows}",
            "=" * 72,
            "",
            "GLOBAL STREAM PATTERN FINDINGS:",
        ]
        if not self.findings:
            lines.append("  No global patterns detected.")
        for i, f in enumerate(self.findings, 1):
            lines.append(f" {i:2d}. [{f.pattern_type}]")
            lines.append(f"     {f.description}")
            if f.evidence:
                lines.append(f"     Evidence: {f.evidence}")

        transitions = [f for f in self.findings if f.pattern_type == PatternType.PATTERN_TRANSITION.value]
        if transitions:
            lines.append("")
            lines.append(f"WINDOW TRANSITIONS OBSERVED ({len(transitions)}):")
            for t in transitions:
                lines.append(f"  * Window {t.window_index}: {t.description}")

        lines.append("=" * 72)
        return "\n".join(lines)

    def to_dict(self) -> Dict[str, Any]:
        """Converts report to serializable dictionary."""
        return {
            "stream_name": self.stream_name,
            "format": self.format.value if hasattr(self.format, "value") else str(self.format),
            "total_units_analyzed": self.total_units_analyzed,
            "total_windows": self.total_windows,
            "findings": [f.to_dict() for f in self.findings],
            "window_results": [w.to_dict() for w in self.window_results],
        }


# =============================================================================
# 2. Configuration Dataclass
# =============================================================================

@dataclass
class PatternConfig:
    """Configuration parameters for Feature F3 Pattern Detection."""
    ts_window_size: int = 200
    gse_window_size: int = 3
    bbframe_window_size: int = 50
    dominant_pid_threshold: float = 0.50     # 50% packet share denotes dominant PID
    high_activity_pid_threshold: float = 0.10 # 10% packet share
    low_activity_pid_threshold: float = 0.01  # 1% packet share
    fragmentation_burst_threshold: float = 0.50 # 50% fragmentation denotes burst
    min_sample_size_confidence: int = 10     # Min units required for 1.0 confidence


# =============================================================================
# 3. Pattern Detector Engine
# =============================================================================

class PatternDetector:
    """
    Feature F3 Engine: Performs deterministic stream pattern detection across
    MPEG-TS, GSE, and DVB-S2 Baseband Frames.
    """

    def __init__(self, config: Optional[PatternConfig] = None):
        self.config = config or PatternConfig()

    @staticmethod
    def _calculate_entropy(counts: Dict[Any, int], total: int) -> float:
        """Calculates Shannon entropy in bits for a discrete distribution."""
        if total <= 0:
            return 0.0
        entropy = 0.0
        for count in counts.values():
            if count > 0:
                p = count / total
                entropy -= p * math.log2(p)
        return max(entropy, 0.0)

    # -------------------------------------------------------------------------
    # MPEG-TS Pattern Analysis
    # -------------------------------------------------------------------------

    def analyze_ts_window(
        self,
        packets: Sequence[TSPacket],
        window_idx: int = 0
    ) -> PatternResult:
        """
        Analyzes a sequence of MPEG-TS packets within a single telemetry window.
        """
        if not packets:
            return PatternResult(format=StreamFormat.MPEG_TS, window_index=window_idx, window_size=0)

        total_packets = len(packets)
        pid_counts: Dict[int, int] = defaultdict(int)
        pid_payload_bytes: Dict[int, int] = defaultdict(int)
        af_packet_indices: List[int] = []
        pcr_packet_indices: List[int] = []
        pcr_pids: Set[int] = set()
        pat_packet_indices: List[int] = []
        pmt_candidate_pids: Set[int] = set()
        pmt_packet_indices: List[int] = []

        # 1. Packet-by-packet parsing & feature aggregation
        for idx, pkt in enumerate(packets):
            pid = pkt.pid
            pid_counts[pid] += 1
            pid_payload_bytes[pid] += len(pkt.payload)

            # Adaptation Field & PCR inspection
            if pkt.has_adaptation_field and pkt.adaptation_field_length > 0:
                af_packet_indices.append(idx)
                # ISO/IEC 13818-1: Byte 4 is AFL, Byte 5 is AF flags. Bit 4 (0x10) is PCR flag
                if len(pkt.raw_bytes) >= 6:
                    af_flags = pkt.raw_bytes[5]
                    if af_flags & 0x10:
                        pcr_packet_indices.append(idx)
                        pcr_pids.add(pid)

            # PAT (PID 0) inspection
            if pid == 0:
                pat_packet_indices.append(idx)
                # Parse PAT payload if PUSI is set to discover PMT PIDs directly
                if pkt.pusi and len(pkt.payload) >= 8:
                    try:
                        # Pointer field is first byte if PUSI
                        ptr = pkt.payload[0]
                        table_offset = 1 + ptr
                        if len(pkt.payload) > table_offset + 8:
                            # Table ID for PAT is 0x00
                            if pkt.payload[table_offset] == 0x00:
                                section_len = ((pkt.payload[table_offset + 1] & 0x0F) << 8) | pkt.payload[table_offset + 2]
                                # Program loop starts after 8-byte section header, ends before 4-byte CRC
                                loop_start = table_offset + 8
                                loop_end = min(table_offset + 3 + section_len - 4, len(pkt.payload))
                                for pos in range(loop_start, loop_end, 4):
                                    if pos + 4 <= len(pkt.payload):
                                        prog_num = (pkt.payload[pos] << 8) | pkt.payload[pos + 1]
                                        pmt_pid = ((pkt.payload[pos + 2] & 0x1F) << 8) | pkt.payload[pos + 3]
                                        if prog_num != 0: # Program 0 is NIT
                                            pmt_candidate_pids.add(pmt_pid)
                    except Exception:
                        pass # Resilient to malformed table fragments

            # If PID matches known PMT PID or standard PMT range (e.g. 4096 / 0x1000)
            if pid in pmt_candidate_pids or pid == 4096:
                pmt_packet_indices.append(idx)

        findings: List[PatternFinding] = []
        confidence = min(1.0, total_packets / self.config.min_sample_size_confidence)

        # 2. Pattern: PID Activity & Dominant Stream
        sorted_pids = sorted(pid_counts.items(), key=lambda item: item[1], reverse=True)
        dominant_pids = [
            (pid, count) for pid, count in sorted_pids
            if (count / total_packets) >= self.config.dominant_pid_threshold
        ]

        if dominant_pids:
            dom_pid, dom_count = dominant_pids[0]
            dom_pct = (dom_count / total_packets) * 100.0
            role = TS_WELL_KNOWN_PIDS.get(dom_pid, None)
            role_desc = f" ({role})" if role else ""
            findings.append(PatternFinding(
                pattern_type=PatternType.TS_DOMINANT_PID.value,
                format=StreamFormat.MPEG_TS,
                description=(
                    f"PID {dom_pid}{role_desc} accounts for {dom_pct:.1f}% of packets, "
                    f"indicating a dominant stream."
                ),
                supporting_metrics={
                    "dominant_pid": dom_pid,
                    "packet_count": dom_count,
                    "percentage": round(dom_pct, 2),
                    "role": role or "Elementary Stream",
                },
                evidence=f"Observed {dom_count}/{total_packets} packets on PID {dom_pid}",
                confidence=confidence,
                window_index=window_idx,
            ))

        # 3. Pattern: Full PID Distribution Breakdown
        pid_dist_metrics = {}
        for pid, count in sorted_pids:
            pct = (count / total_packets) * 100.0
            role = TS_WELL_KNOWN_PIDS.get(pid, "Elementary Stream")
            pid_dist_metrics[str(pid)] = {
                "count": count,
                "percentage": round(pct, 2),
                "role": role,
            }

        findings.append(PatternFinding(
            pattern_type=PatternType.TS_PID_DISTRIBUTION.value,
            format=StreamFormat.MPEG_TS,
            description=(
                f"Multiplex contains {len(pid_counts)} active PIDs: "
                + ", ".join([f"PID {p} ({c} pkts, {pid_dist_metrics[str(p)]['percentage']}%)" for p, c in sorted_pids[:4]])
                + ("..." if len(sorted_pids) > 4 else "")
            ),
            supporting_metrics={"pid_distribution": pid_dist_metrics},
            evidence=f"Extracted {len(pid_counts)} unique PIDs from {total_packets} packets",
            confidence=confidence,
            window_index=window_idx,
        ))

        # 4. Pattern: PAT / PMT Periodic Recurrence (in packet intervals)
        if pat_packet_indices:
            pat_count = len(pat_packet_indices)
            intervals = [
                pat_packet_indices[i] - pat_packet_indices[i - 1]
                for i in range(1, pat_count)
            ]
            mean_interval = (sum(intervals) / len(intervals)) if intervals else total_packets
            min_interval = min(intervals) if intervals else total_packets
            max_interval = max(intervals) if intervals else total_packets

            # Check lockstep behavior with PMT
            is_lockstep = False
            if pmt_packet_indices and len(pat_packet_indices) == len(pmt_packet_indices):
                is_lockstep = all(
                    pmt_packet_indices[i] == pat_packet_indices[i] + 1
                    for i in range(min(len(pat_packet_indices), len(pmt_packet_indices)))
                )

            desc = (
                f"PAT observed {pat_count} times with average recurrence of {mean_interval:.1f} packets "
                f"(min: {min_interval}, max: {max_interval})."
            )
            if is_lockstep:
                desc += " PMT packets follow PAT in exact consecutive lockstep."

            findings.append(PatternFinding(
                pattern_type=PatternType.TS_PAT_PMT_STRUCTURE.value,
                format=StreamFormat.MPEG_TS,
                description=desc,
                supporting_metrics={
                    "pat_count": pat_count,
                    "pmt_count": len(pmt_packet_indices),
                    "mean_interval_packets": round(mean_interval, 2),
                    "min_interval_packets": min_interval,
                    "max_interval_packets": max_interval,
                    "is_lockstep": is_lockstep,
                    "pmt_pids_discovered": sorted(list(pmt_candidate_pids)),
                },
                evidence=(
                    f"PAT occurrences at packet indices {pat_packet_indices[:5]}... "
                    f"(timing in ms requires receiver clock stamps; recurrence expressed in packet units)"
                ),
                confidence=confidence,
                window_index=window_idx,
            ))

        # 5. Pattern: PCR Clock Activity
        if pcr_packet_indices:
            pcr_count = len(pcr_packet_indices)
            pcr_intervals = [
                pcr_packet_indices[i] - pcr_packet_indices[i - 1]
                for i in range(1, pcr_count)
            ]
            mean_pcr_interval = (sum(pcr_intervals) / len(pcr_intervals)) if pcr_intervals else total_packets
            findings.append(PatternFinding(
                pattern_type=PatternType.TS_PCR_ACTIVITY.value,
                format=StreamFormat.MPEG_TS,
                description=(
                    f"PCR clock references observed on PID(s) {sorted(list(pcr_pids))} "
                    f"across {pcr_count} packets with mean recurrence of {mean_pcr_interval:.1f} packets."
                ),
                supporting_metrics={
                    "pcr_count": pcr_count,
                    "pcr_pids": sorted(list(pcr_pids)),
                    "mean_interval_packets": round(mean_pcr_interval, 2),
                },
                evidence=f"Adaptation field PCR flags active on packets {pcr_packet_indices[:4]}...",
                confidence=confidence,
                window_index=window_idx,
            ))

        # 6. Pattern: Multiplex Composition & Shannon Entropy
        entropy = self._calculate_entropy(pid_counts, total_packets)
        findings.append(PatternFinding(
            pattern_type=PatternType.TS_MULTIPLEX_COMPOSITION.value,
            format=StreamFormat.MPEG_TS,
            description=(
                f"Multiplex Shannon entropy H={entropy:.3f} bits across {len(pid_counts)} PIDs "
                f"({('single-program dominated' if entropy < 1.0 else 'multi-program distributed')})."
            ),
            supporting_metrics={
                "shannon_entropy_bits": round(entropy, 4),
                "unique_pids": len(pid_counts),
                "total_packets": total_packets,
            },
            evidence=f"Computed from discrete PID probability distribution over {total_packets} packets",
            confidence=confidence,
            window_index=window_idx,
        ))

        return PatternResult(
            format=StreamFormat.MPEG_TS,
            findings=findings,
            metrics_summary={
                "total_packets": total_packets,
                "unique_pids": len(pid_counts),
                "entropy": round(entropy, 4),
                "dominant_pid": dominant_pids[0][0] if dominant_pids else None,
            },
            window_index=window_idx,
            window_size=total_packets,
        )

    def analyze_ts_stream(
        self,
        packets: Sequence[TSPacket],
        window_size: Optional[int] = None,
        stream_name: str = "MPEG-TS Stream"
    ) -> PatternReport:
        """
        Performs full multi-window pattern analysis and transition tracking on MPEG-TS.
        """
        win_size = window_size or self.config.ts_window_size
        total_packets = len(packets)

        # Global analysis across all packets
        global_result = self.analyze_ts_window(packets, window_idx=0)
        global_findings = list(global_result.findings)

        # Sequential windowing
        window_results: List[PatternResult] = []
        if total_packets > 0:
            for start in range(0, total_packets, win_size):
                chunk = packets[start:start + win_size]
                w_idx = len(window_results)
                res = self.analyze_ts_window(chunk, window_idx=w_idx)
                window_results.append(res)

        # Detect cross-window transitions
        transitions = self._detect_ts_transitions(window_results)
        global_findings.extend(transitions)

        report = PatternReport(
            stream_name=stream_name,
            format=StreamFormat.MPEG_TS,
            total_units_analyzed=total_packets,
            total_windows=len(window_results),
            findings=global_findings,
            window_results=window_results,
            summary_text=global_result.summary(),
        )
        return report

    def _detect_ts_transitions(
        self,
        window_results: List[PatternResult]
    ) -> List[PatternFinding]:
        """Detects PID composition shifts across adjacent windows."""
        transitions: List[PatternFinding] = []
        if len(window_results) < 2:
            return transitions

        for i in range(1, len(window_results)):
            prev = window_results[i - 1]
            curr = window_results[i]

            prev_dom = prev.metrics_summary.get("dominant_pid")
            curr_dom = curr.metrics_summary.get("dominant_pid")

            if prev_dom is not None and curr_dom is not None and prev_dom != curr_dom:
                finding = PatternFinding(
                    pattern_type=PatternType.PATTERN_TRANSITION.value,
                    format=StreamFormat.MPEG_TS,
                    description=f"Dominant PID switched from {prev_dom} to {curr_dom} between window {prev.window_index} and {curr.window_index}.",
                    supporting_metrics={"prev_dominant": prev_dom, "curr_dominant": curr_dom},
                    evidence=f"Window {prev.window_index} dom={prev_dom}, Window {curr.window_index} dom={curr_dom}",
                    confidence=1.0,
                    window_index=curr.window_index,
                )
                curr.has_transitions = True
                transitions.append(finding)

        return transitions

    # -------------------------------------------------------------------------
    # GSE Pattern Analysis
    # -------------------------------------------------------------------------

    def analyze_gse_window(
        self,
        pdus: Sequence[GSEPDU],
        window_idx: int = 0
    ) -> PatternResult:
        """
        Analyzes a sequence of Generic Stream Encapsulation (GSE) PDUs.
        """
        if not pdus:
            return PatternResult(format=StreamFormat.GSE, window_index=window_idx, window_size=0)

        total_pdus = len(pdus)
        protocol_counts: Dict[str, int] = defaultdict(int)
        label_counts: Dict[str, int] = defaultdict(int)
        frag_counts: Dict[str, int] = {
            "unfragmented": 0,
            "first": 0,
            "intermediate": 0,
            "last": 0,
            "padding": 0,
        }
        payload_sizes: List[int] = []
        extension_headers: Set[str] = set()

        for pdu in pdus:
            payload_sizes.append(pdu.payload_length)

            # Protocol tracking
            pname = pdu.protocol_name
            protocol_counts[pname] += 1
            if "EXT" in pname or (pdu.protocol_type and pdu.protocol_type < 0x0600):
                extension_headers.add(pname)

            # Label tracking
            label_str = f"LABEL_{len(pdu.label)}B" if pdu.label else "LABEL_NONE"
            label_counts[label_str] += 1

            # Fragmentation status
            if pdu.is_padding:
                frag_counts["padding"] += 1
            elif pdu.is_unfragmented:
                frag_counts["unfragmented"] += 1
            elif pdu.is_first_fragment:
                frag_counts["first"] += 1
            elif pdu.is_intermediate_fragment:
                frag_counts["intermediate"] += 1
            elif pdu.is_last_fragment:
                frag_counts["last"] += 1

        findings: List[PatternFinding] = []
        confidence = min(1.0, total_pdus / self.config.min_sample_size_confidence)

        # 1. Pattern: Protocol Distribution
        sorted_protos = sorted(protocol_counts.items(), key=lambda item: item[1], reverse=True)
        dom_proto, dom_proto_count = sorted_protos[0]
        dom_proto_pct = (dom_proto_count / total_pdus) * 100.0

        findings.append(PatternFinding(
            pattern_type=PatternType.GSE_PROTOCOL_DISTRIBUTION.value,
            format=StreamFormat.GSE,
            description=(
                f"Protocol distribution dominated by {dom_proto} ({dom_proto_pct:.1f}% of observed PDUs)."
            ),
            supporting_metrics={
                "protocol_counts": dict(protocol_counts),
                "dominant_protocol": dom_proto,
                "dominant_percentage": round(dom_proto_pct, 2),
            },
            evidence=f"{dom_proto_count}/{total_pdus} PDUs match {dom_proto}",
            confidence=confidence,
            window_index=window_idx,
        ))

        # 2. Pattern: PDU Size Distribution & Bins
        min_size = min(payload_sizes)
        max_size = max(payload_sizes)
        mean_size = sum(payload_sizes) / total_pdus
        variance = sum((x - mean_size) ** 2 for x in payload_sizes) / total_pdus
        std_size = math.sqrt(variance)

        size_bins = {
            "small_control (<128B)": sum(1 for s in payload_sizes if s < 128),
            "medium_payload (128-576B)": sum(1 for s in payload_sizes if 128 <= s <= 576),
            "large_mtu (>576B)": sum(1 for s in payload_sizes if s > 576),
        }
        modal_bin = max(size_bins.items(), key=lambda item: item[1])[0]

        findings.append(PatternFinding(
            pattern_type=PatternType.GSE_PDU_SIZE_DISTRIBUTION.value,
            format=StreamFormat.GSE,
            description=(
                f"PDU payload size spans {min_size} to {max_size} bytes (mean: {mean_size:.1f} B, std: {std_size:.1f} B). "
                f"Modal size cluster: {modal_bin}."
            ),
            supporting_metrics={
                "min_bytes": min_size,
                "max_bytes": max_size,
                "mean_bytes": round(mean_size, 2),
                "std_bytes": round(std_size, 2),
                "size_clusters": size_bins,
            },
            evidence=f"Computed across {total_pdus} GSE PDU lengths",
            confidence=confidence,
            window_index=window_idx,
        ))

        # 3. Pattern: Fragmentation Behavior
        total_frag = frag_counts["first"] + frag_counts["intermediate"] + frag_counts["last"]
        frag_ratio = total_frag / total_pdus if total_pdus > 0 else 0.0

        findings.append(PatternFinding(
            pattern_type=PatternType.GSE_FRAGMENTATION_BEHAVIOR.value,
            format=StreamFormat.GSE,
            description=(
                f"{frag_ratio * 100.0:.1f}% of observed PDUs belong to fragmented transmissions "
                f"({frag_counts['first']} first, {frag_counts['intermediate']} mid, "
                f"{frag_counts['last']} last, {frag_counts['unfragmented']} unfragmented)."
            ),
            supporting_metrics={
                "fragmentation_ratio": round(frag_ratio, 4),
                "fragmentation_counts": frag_counts,
                "is_burst": frag_ratio >= self.config.fragmentation_burst_threshold,
            },
            evidence=f"{total_frag}/{total_pdus} fragmented PDUs observed",
            confidence=confidence,
            window_index=window_idx,
        ))

        # 4. Pattern: Label & Extension Header Usage
        dom_label = max(label_counts.items(), key=lambda item: item[1])[0]
        dom_label_pct = (label_counts[dom_label] / total_pdus) * 100.0

        findings.append(PatternFinding(
            pattern_type=PatternType.GSE_LABEL_EXTENSION_USAGE.value,
            format=StreamFormat.GSE,
            description=(
                f"Addressing uses {dom_label} on {dom_label_pct:.1f}% of PDUs. "
                f"Extension headers: {sorted(list(extension_headers)) if extension_headers else 'None'}."
            ),
            supporting_metrics={
                "label_counts": dict(label_counts),
                "dominant_label": dom_label,
                "extension_headers": sorted(list(extension_headers)),
            },
            evidence=f"Label inspection on {total_pdus} PDUs",
            confidence=confidence,
            window_index=window_idx,
        ))

        return PatternResult(
            format=StreamFormat.GSE,
            findings=findings,
            metrics_summary={
                "total_pdus": total_pdus,
                "dominant_protocol": dom_proto,
                "fragmentation_ratio": round(frag_ratio, 4),
                "mean_size_bytes": round(mean_size, 2),
            },
            window_index=window_idx,
            window_size=total_pdus,
        )

    def analyze_gse_stream(
        self,
        pdus: Sequence[GSEPDU],
        window_size: Optional[int] = None,
        stream_name: str = "GSE Stream"
    ) -> PatternReport:
        """
        Performs multi-window pattern analysis and fragmentation burst detection on GSE.
        """
        win_size = window_size or self.config.gse_window_size
        total_pdus = len(pdus)

        global_result = self.analyze_gse_window(pdus, window_idx=0)
        global_findings = list(global_result.findings)

        window_results: List[PatternResult] = []
        if total_pdus > 0:
            for start in range(0, total_pdus, win_size):
                chunk = pdus[start:start + win_size]
                w_idx = len(window_results)
                res = self.analyze_gse_window(chunk, window_idx=w_idx)
                window_results.append(res)

        # Detect cross-window transitions (e.g. fragmentation bursts)
        transitions = self._detect_gse_transitions(window_results)
        global_findings.extend(transitions)

        return PatternReport(
            stream_name=stream_name,
            format=StreamFormat.GSE,
            total_units_analyzed=total_pdus,
            total_windows=len(window_results),
            findings=global_findings,
            window_results=window_results,
            summary_text=global_result.summary(),
        )

    def _detect_gse_transitions(
        self,
        window_results: List[PatternResult]
    ) -> List[PatternFinding]:
        """Detects fragmentation bursts and protocol transitions in GSE streams."""
        transitions: List[PatternFinding] = []
        if len(window_results) < 2:
            return transitions

        for i in range(1, len(window_results)):
            prev = window_results[i - 1]
            curr = window_results[i]

            prev_frag = prev.metrics_summary.get("fragmentation_ratio", 0.0)
            curr_frag = curr.metrics_summary.get("fragmentation_ratio", 0.0)

            # Significant jump in fragmentation (> 30% increase)
            if curr_frag - prev_frag >= 0.30:
                transitions.append(PatternFinding(
                    pattern_type=PatternType.PATTERN_TRANSITION.value,
                    format=StreamFormat.GSE,
                    description=(
                        f"Fragmentation burst observed in window {curr.window_index}: "
                        f"jumped from {prev_frag * 100:.1f}% to {curr_frag * 100:.1f}%."
                    ),
                    supporting_metrics={"prev_frag_ratio": prev_frag, "curr_frag_ratio": curr_frag},
                    evidence=f"Window {prev.window_index} vs {curr.window_index}",
                    confidence=1.0,
                    window_index=curr.window_index,
                ))
                curr.has_transitions = True

        return transitions

    # -------------------------------------------------------------------------
    # DVB-S2 Baseband Frame (BBFrame) Pattern Analysis
    # -------------------------------------------------------------------------

    def analyze_bbframe_window(
        self,
        frames: Sequence[BBFrame],
        window_idx: int = 0
    ) -> PatternResult:
        """
        Analyzes a sequence of DVB-S2 Baseband Frames within a single window.
        """
        if not frames:
            return PatternResult(format=StreamFormat.BB_FRAME, window_index=window_idx, window_size=0)

        total_frames = len(frames)
        dfl_values = [f.dfl for f in frames]
        sis_count = sum(1 for f in frames if f.is_sis)
        mis_count = total_frames - sis_count
        ccm_count = sum(1 for f in frames if f.is_ccm)
        acm_count = total_frames - ccm_count

        ro_counts: Dict[float, int] = defaultdict(int)
        for f in frames:
            ro_counts[f.ro_rolloff] += 1

        stream_types: Dict[str, int] = defaultdict(int)
        for f in frames:
            stream_types[f.ts_gs] += 1

        mode_adapt_counts: Dict[str, int] = defaultdict(int)
        for f in frames:
            ma = f.mode_adaptation_type or "STANDARD"
            mode_adapt_counts[ma] += 1

        findings: List[PatternFinding] = []
        confidence = min(1.0, total_frames / self.config.min_sample_size_confidence)

        # 1. Pattern: DFL / Frame Size Distribution
        min_dfl = min(dfl_values)
        max_dfl = max(dfl_values)
        mean_dfl = sum(dfl_values) / total_frames
        variance_dfl = sum((x - mean_dfl) ** 2 for x in dfl_values) / total_frames
        std_dfl = math.sqrt(variance_dfl)

        dfl_counter = Counter(dfl_values)
        modal_dfl, modal_count = dfl_counter.most_common(1)[0]
        modal_pct = (modal_count / total_frames) * 100.0

        findings.append(PatternFinding(
            pattern_type=PatternType.BB_DFL_DISTRIBUTION.value,
            format=StreamFormat.BB_FRAME,
            description=(
                f"DFL spans {min_dfl} to {max_dfl} bits (mean: {mean_dfl:.1f} bits, std: {std_dfl:.1f}). "
                f"Modal DFL: {modal_dfl} bits ({modal_pct:.1f}% of frames)."
            ),
            supporting_metrics={
                "min_dfl_bits": min_dfl,
                "max_dfl_bits": max_dfl,
                "mean_dfl_bits": round(mean_dfl, 2),
                "std_dfl_bits": round(std_dfl, 2),
                "modal_dfl_bits": modal_dfl,
                "modal_percentage": round(modal_pct, 2),
                "unique_dfl_count": len(dfl_counter),
            },
            evidence=f"Analyzed {total_frames} DVB-S2 header DFL fields",
            confidence=confidence,
            window_index=window_idx,
        ))

        # 2. Pattern: SIS vs MIS Behavior
        sis_ratio = sis_count / total_frames
        mis_ratio = mis_count / total_frames

        findings.append(PatternFinding(
            pattern_type=PatternType.BB_SIS_MIS_BEHAVIOR.value,
            format=StreamFormat.BB_FRAME,
            description=(
                f"Stream operates in {'SIS (Single Input Stream)' if sis_ratio >= 0.99 else ('MIS (Multiple Input Stream)' if mis_ratio >= 0.99 else 'mixed SIS/MIS')} "
                f"mode ({sis_ratio * 100:.2f}% SIS, {mis_ratio * 100:.2f}% MIS)."
            ),
            supporting_metrics={
                "sis_frames": sis_count,
                "mis_frames": mis_count,
                "sis_ratio": round(sis_ratio, 4),
                "mis_ratio": round(mis_ratio, 4),
            },
            evidence=f"MATYPE-1 byte 0 bit 5 decoded over {total_frames} frames",
            confidence=confidence,
            window_index=window_idx,
        ))

        # 3. Pattern: CCM vs ACM Modulation Behavior
        ccm_ratio = ccm_count / total_frames
        acm_ratio = acm_count / total_frames

        findings.append(PatternFinding(
            pattern_type=PatternType.BB_CCM_ACM_BEHAVIOR.value,
            format=StreamFormat.BB_FRAME,
            description=(
                f"Modulation mode is {'100% Adaptive Coding & Modulation (ACM)' if acm_ratio == 1.0 else ('100% Constant Coding & Modulation (CCM)' if ccm_ratio == 1.0 else f'mixed ({ccm_ratio*100:.1f}% CCM, {acm_ratio*100:.1f}% ACM)')}."
            ),
            supporting_metrics={
                "ccm_frames": ccm_count,
                "acm_frames": acm_count,
                "ccm_ratio": round(ccm_ratio, 4),
                "acm_ratio": round(acm_ratio, 4),
            },
            evidence=f"MATYPE-1 byte 0 bit 4 decoded over {total_frames} frames",
            confidence=confidence,
            window_index=window_idx,
        ))

        # 4. Pattern: Roll-Off Factor Stability
        dom_ro = max(ro_counts.items(), key=lambda item: item[1])[0]
        is_stable = len(ro_counts) == 1

        findings.append(PatternFinding(
            pattern_type=PatternType.BB_ROLLOFF_STABILITY.value,
            format=StreamFormat.BB_FRAME,
            description=(
                f"Roll-off factor is {'strictly stable at alpha=' + str(dom_ro) if is_stable else f'varying (dominant alpha={dom_ro})'}."
            ),
            supporting_metrics={
                "roll_off_counts": {str(k): v for k, v in ro_counts.items()},
                "dominant_alpha": dom_ro,
                "is_stable": is_stable,
            },
            evidence=f"MATYPE-1 roll-off bits over {total_frames} frames",
            confidence=confidence,
            window_index=window_idx,
        ))

        # 5. Pattern: Mode Adaptation
        dom_ma = max(mode_adapt_counts.items(), key=lambda item: item[1])[0]
        dom_ma_pct = (mode_adapt_counts[dom_ma] / total_frames) * 100.0

        findings.append(PatternFinding(
            pattern_type=PatternType.BB_MODE_ADAPTATION.value,
            format=StreamFormat.BB_FRAME,
            description=(
                f"SatLabs mode adaptation is dominated by {dom_ma} ({dom_ma_pct:.1f}% of frames)."
            ),
            supporting_metrics={
                "mode_adaptation_counts": dict(mode_adapt_counts),
                "dominant_type": dom_ma,
            },
            evidence=f"SYNCD / Mode adaptation classification on {total_frames} frames",
            confidence=confidence,
            window_index=window_idx,
        ))

        # 6. Pattern: Structural Stream Summary
        dom_st = max(stream_types.items(), key=lambda item: item[1])[0]
        findings.append(PatternFinding(
            pattern_type=PatternType.BB_STRUCTURAL_SUMMARY.value,
            format=StreamFormat.BB_FRAME,
            description=(
                f"Transmission framing: {dom_st} stream."
            ),
            supporting_metrics={
                "stream_types": dict(stream_types),
                "dominant_stream_type": dom_st,
            },
            evidence=f"MATYPE-1 byte 0 bits 6-7 over {total_frames} frames",
            confidence=confidence,
            window_index=window_idx,
        ))

        return PatternResult(
            format=StreamFormat.BB_FRAME,
            findings=findings,
            metrics_summary={
                "total_frames": total_frames,
                "modal_dfl": modal_dfl,
                "sis_ratio": round(sis_ratio, 4),
                "acm_ratio": round(acm_ratio, 4),
                "dominant_ro": dom_ro,
                "stream_type": dom_st,
            },
            window_index=window_idx,
            window_size=total_frames,
        )

    def analyze_bbframe_stream(
        self,
        frames: Sequence[BBFrame],
        window_size: Optional[int] = None,
        stream_name: str = "DVB-S2 BBFrame Stream"
    ) -> PatternReport:
        """
        Performs multi-window pattern analysis and mode transition detection on BBFrames.
        """
        win_size = window_size or self.config.bbframe_window_size
        total_frames = len(frames)

        global_result = self.analyze_bbframe_window(frames, window_idx=0)
        global_findings = list(global_result.findings)

        window_results: List[PatternResult] = []
        if total_frames > 0:
            for start in range(0, total_frames, win_size):
                chunk = frames[start:start + win_size]
                w_idx = len(window_results)
                res = self.analyze_bbframe_window(chunk, window_idx=w_idx)
                window_results.append(res)

        # Detect cross-window transitions (e.g. mode changes, roll-off shifts)
        transitions = self._detect_bbframe_transitions(window_results)
        global_findings.extend(transitions)

        return PatternReport(
            stream_name=stream_name,
            format=StreamFormat.BB_FRAME,
            total_units_analyzed=total_frames,
            total_windows=len(window_results),
            findings=global_findings,
            window_results=window_results,
            summary_text=global_result.summary(),
        )

    def _detect_bbframe_transitions(
        self,
        window_results: List[PatternResult]
    ) -> List[PatternFinding]:
        """Detects transmission mode shifts across adjacent BBFrame windows."""
        transitions: List[PatternFinding] = []
        if len(window_results) < 2:
            return transitions

        for i in range(1, len(window_results)):
            prev = window_results[i - 1]
            curr = window_results[i]

            # 1. Roll-off factor transition
            prev_ro = prev.metrics_summary.get("dominant_ro")
            curr_ro = curr.metrics_summary.get("dominant_ro")
            if prev_ro is not None and curr_ro is not None and prev_ro != curr_ro:
                transitions.append(PatternFinding(
                    pattern_type=PatternType.PATTERN_TRANSITION.value,
                    format=StreamFormat.BB_FRAME,
                    description=(
                        f"Transmission roll-off factor transitioned from alpha={prev_ro} "
                        f"to alpha={curr_ro} between window {prev.window_index} and {curr.window_index}."
                    ),
                    supporting_metrics={"prev_ro": prev_ro, "curr_ro": curr_ro},
                    evidence=f"Window {prev.window_index} vs {curr.window_index}",
                    confidence=1.0,
                    window_index=curr.window_index,
                ))
                curr.has_transitions = True

            # 2. Modal DFL frame size transition
            prev_dfl = prev.metrics_summary.get("modal_dfl")
            curr_dfl = curr.metrics_summary.get("modal_dfl")
            if prev_dfl is not None and curr_dfl is not None and prev_dfl != curr_dfl:
                transitions.append(PatternFinding(
                    pattern_type=PatternType.PATTERN_TRANSITION.value,
                    format=StreamFormat.BB_FRAME,
                    description=(
                        f"Modal frame length (DFL) transitioned from {prev_dfl} bits to {curr_dfl} bits "
                        f"between window {prev.window_index} and {curr.window_index}."
                    ),
                    supporting_metrics={"prev_dfl": prev_dfl, "curr_dfl": curr_dfl},
                    evidence=f"Window {prev.window_index} vs {curr.window_index}",
                    confidence=1.0,
                    window_index=curr.window_index,
                ))
                curr.has_transitions = True

        return transitions

    # -------------------------------------------------------------------------
    # Unified Ingestion Handler Gateway
    # -------------------------------------------------------------------------

    def detect_from_handler(
        self,
        handler: StreamHandler,
        max_units: Optional[int] = None
    ) -> PatternReport:
        """
        Universal gateway: executes pattern detection directly from a StreamHandler.
        """
        parser = handler.get_parser()
        fmt = handler.format

        if fmt == StreamFormat.MPEG_TS:
            packets = list(parser.parse_file(handler.path, max_packets=max_units))
            return self.analyze_ts_stream(packets, stream_name=handler.path.name)
        elif fmt == StreamFormat.GSE:
            pdus = list(parser.parse_file(handler.path))
            if max_units:
                pdus = pdus[:max_units]
            return self.analyze_gse_stream(pdus, stream_name=handler.path.name)
        elif fmt == StreamFormat.BB_FRAME:
            frames = list(parser.parse_file(handler.path, max_packets=max_units))
            return self.analyze_bbframe_stream(frames, stream_name=handler.path.name)
        else:
            raise ValueError(f"Unsupported format for pattern detection: {fmt}")
