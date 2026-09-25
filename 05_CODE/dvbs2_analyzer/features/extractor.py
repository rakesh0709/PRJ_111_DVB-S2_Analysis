"""
Feature Extraction Layer for PRJ_111.

Derives quantitative, statistical, structural, and protocol-specific stream-health metrics
from parsed output streams across all three supported input formats:
  1. MPEG Transport Stream (MPEG-TS, ISO/IEC 13818-1)
  2. Generic Stream Encapsulation (GSE, ETSI TS 102 606-1)
  3. DVB-S2 Baseband Frames (BBFrame, ETSI EN 302 307-1)

Provides both format-specific feature sets and a unified multi-format representation
(UnifiedStreamFeatureSet) suitable for downstream health analysis (F1), AI/ML anomaly
detection (F2), and pattern detection (F3).
"""

from dataclasses import dataclass, field
import math
from typing import Any, Dict, List, Optional, Union

from dvbs2_analyzer.config import StreamFormat
from dvbs2_analyzer.parsers.bbframe_parser import BBFrameStreamStatistics
from dvbs2_analyzer.parsers.gse_parser import GSEStreamStatistics
from dvbs2_analyzer.parsers.ts_parser import TSStreamStatistics


# =============================================================================
# 1. Common Cross-Format Metrics
# =============================================================================

@dataclass
class CommonMetrics:
    """
    Normalized, cross-format stream health and telemetry indicators.
    Applies uniformly to MPEG-TS packets, GSE PDUs, and DVB-S2 Baseband Frames.
    """
    total_units: int                     # Total units parsed (packets / PDUs / frames)
    valid_units: int                     # Valid units passed verification
    invalid_units: int                   # Corrupted / invalid units
    truncated_units: int                 # Truncated units
    integrity_ratio: float               # valid_units / total_units (0.0 to 1.0)

    total_payload_bytes: int             # Total extracted payload bytes
    mean_payload_bytes: float            # Average payload bytes per unit
    payload_ratio: Optional[float]       # Ratio of payload to total, or None if not applicable

    stream_type: str                     # Dominant stream classification
    unit_size_bytes_min: Optional[int]   # Min unit length in bytes
    unit_size_bytes_max: Optional[int]   # Max unit length in bytes
    unit_size_bytes_mean: Optional[float]# Mean unit length in bytes

    error_count: int                     # Total observed errors
    error_rate: float                    # error_count / total_units
    entropy: Optional[float]             # Shannon entropy in bits (PID/protocol/stream)

    def to_dict(self) -> Dict[str, Any]:
        """Converts common metrics into a structured dictionary."""
        return {
            "total_units": self.total_units,
            "valid_units": self.valid_units,
            "invalid_units": self.invalid_units,
            "truncated_units": self.truncated_units,
            "integrity_ratio": round(self.integrity_ratio, 6),
            "total_payload_bytes": self.total_payload_bytes,
            "mean_payload_bytes": round(self.mean_payload_bytes, 2),
            "payload_ratio": round(self.payload_ratio, 6) if self.payload_ratio is not None else None,
            "stream_type": self.stream_type,
            "unit_size_bytes_min": self.unit_size_bytes_min,
            "unit_size_bytes_max": self.unit_size_bytes_max,
            "unit_size_bytes_mean": round(self.unit_size_bytes_mean, 2) if self.unit_size_bytes_mean is not None else None,
            "error_count": self.error_count,
            "error_rate": round(self.error_rate, 6),
            "entropy": round(self.entropy, 4) if self.entropy is not None else None,
        }


# =============================================================================
# 2. Format-Specific Metric Models
# =============================================================================

@dataclass
class TSSpecificMetrics:
    """MPEG-2 Transport Stream (ISO/IEC 13818-1) specific telemetry."""
    unique_pid_count: int
    pid_distribution: Dict[int, int]
    pid_percentages: Dict[int, float]
    pid_entropy: float
    null_packet_count: int
    null_packet_ratio: float
    tei_error_count: int
    tei_error_rate: float
    continuity_error_count: int
    continuity_error_rate: float
    continuity_errors_by_pid: Dict[int, int]
    adaptation_field_count: int
    adaptation_field_ratio: float
    adaptation_only_count: int
    adaptation_and_payload_count: int
    payload_packet_count: int
    payload_packet_ratio: float
    scrambled_packet_count: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        """Converts TS metrics into a serializable dictionary."""
        return {
            "unique_pid_count": self.unique_pid_count,
            "pid_distribution": self.pid_distribution,
            "pid_percentages": {k: round(v, 4) for k, v in self.pid_percentages.items()},
            "pid_entropy": round(self.pid_entropy, 4),
            "null_packet_count": self.null_packet_count,
            "null_packet_ratio": round(self.null_packet_ratio, 6),
            "tei_error_count": self.tei_error_count,
            "tei_error_rate": round(self.tei_error_rate, 6),
            "continuity_error_count": self.continuity_error_count,
            "continuity_error_rate": round(self.continuity_error_rate, 6),
            "continuity_errors_by_pid": self.continuity_errors_by_pid,
            "adaptation_field_count": self.adaptation_field_count,
            "adaptation_field_ratio": round(self.adaptation_field_ratio, 6),
            "adaptation_only_count": self.adaptation_only_count,
            "adaptation_and_payload_count": self.adaptation_and_payload_count,
            "payload_packet_count": self.payload_packet_count,
            "payload_packet_ratio": round(self.payload_packet_ratio, 6),
            "scrambled_packet_count": self.scrambled_packet_count,
        }


@dataclass
class GSESpecificMetrics:
    """Generic Stream Encapsulation (ETSI TS 102 606-1) specific telemetry."""
    total_pdus: int
    valid_pdus: int
    malformed_pdus: int
    truncated_pdus: int
    padding_packets: int
    unfragmented_pdus: int
    fragmented_pdus_total: int
    first_fragments: int
    intermediate_fragments: int
    last_fragments: int
    fragmentation_ratio: float
    label_type_distribution: Dict[str, int]
    protocol_type_distribution: Dict[str, int]
    encapsulated_protocol_distribution: Dict[str, int]
    protocol_entropy: float

    def to_dict(self) -> Dict[str, Any]:
        """Converts GSE metrics into a serializable dictionary."""
        return {
            "total_pdus": self.total_pdus,
            "valid_pdus": self.valid_pdus,
            "malformed_pdus": self.malformed_pdus,
            "truncated_pdus": self.truncated_pdus,
            "padding_packets": self.padding_packets,
            "unfragmented_pdus": self.unfragmented_pdus,
            "fragmented_pdus_total": self.fragmented_pdus_total,
            "first_fragments": self.first_fragments,
            "intermediate_fragments": self.intermediate_fragments,
            "last_fragments": self.last_fragments,
            "fragmentation_ratio": round(self.fragmentation_ratio, 6),
            "label_type_distribution": self.label_type_distribution,
            "protocol_type_distribution": self.protocol_type_distribution,
            "encapsulated_protocol_distribution": self.encapsulated_protocol_distribution,
            "protocol_entropy": round(self.protocol_entropy, 4),
        }


@dataclass
class BBFrameSpecificMetrics:
    """DVB-S2 Baseband Frame (ETSI EN 302 307-1) specific telemetry."""
    total_frames: int
    valid_frames: int
    invalid_crc_frames: int
    malformed_headers: int
    truncated_frames: int
    stream_type_distribution: Dict[str, int]
    input_stream_modes: Dict[str, int]
    coding_modulation_modes: Dict[str, int]
    roll_off_distribution: Dict[str, int]
    mode_adaptation_distribution: Dict[str, int]
    isi_distribution: Dict[int, int]
    sync_byte_distribution: Dict[str, int]
    dfl_min_bits: Optional[int]
    dfl_max_bits: Optional[int]
    dfl_mean_bits: Optional[float]
    upl_mean_bits: Optional[float]
    crc_status: str

    def to_dict(self) -> Dict[str, Any]:
        """Converts BBFrame metrics into a serializable dictionary."""
        return {
            "total_frames": self.total_frames,
            "valid_frames": self.valid_frames,
            "invalid_crc_frames": self.invalid_crc_frames,
            "malformed_headers": self.malformed_headers,
            "truncated_frames": self.truncated_frames,
            "stream_type_distribution": self.stream_type_distribution,
            "input_stream_modes": self.input_stream_modes,
            "coding_modulation_modes": self.coding_modulation_modes,
            "roll_off_distribution": self.roll_off_distribution,
            "mode_adaptation_distribution": self.mode_adaptation_distribution,
            "isi_distribution": self.isi_distribution,
            "sync_byte_distribution": self.sync_byte_distribution,
            "dfl_min_bits": self.dfl_min_bits,
            "dfl_max_bits": self.dfl_max_bits,
            "dfl_mean_bits": round(self.dfl_mean_bits, 2) if self.dfl_mean_bits is not None else None,
            "upl_mean_bits": round(self.upl_mean_bits, 2) if self.upl_mean_bits is not None else None,
            "crc_status": self.crc_status,
        }


# =============================================================================
# 3. Backward-Compatible StreamFeatureSet (Preserved for Feature F1)
# =============================================================================

@dataclass
class StreamFeatureSet:
    """
    Quantitative MPEG-TS stream-health features extracted from an ingested stream.
    Retained for complete backward compatibility with Feature F1 (Stream Health Analysis).
    """
    # Packet counts & integrity
    total_packets: int
    valid_packets: int
    invalid_packets: int
    sync_integrity: float               # Percentage 0.0 to 100.0

    # PID multiplex metrics
    unique_pid_count: int
    pid_distribution: Dict[int, int]
    pid_percentages: Dict[int, float]
    pid_entropy: float                  # Shannon entropy in bits

    # Null packet metrics (transponder bandwidth utilization)
    null_packet_count: int
    null_packet_ratio: float

    # Error indicators (ETSI TR 101 290 Priority 1 checks)
    tei_error_count: int
    tei_error_rate: float
    continuity_error_count: int
    continuity_error_rate: float
    continuity_errors_by_pid: Dict[int, int]

    # Adaptation field metrics
    adaptation_field_count: int
    adaptation_field_ratio: float
    adaptation_only_count: int
    adaptation_and_payload_count: int

    # Payload statistics
    payload_packet_count: int
    payload_packet_ratio: float
    total_payload_bytes: int
    mean_payload_bytes_per_packet: float

    def to_dict(self) -> Dict[str, Any]:
        """Converts feature set into a structured dictionary."""
        return {
            "total_packets": self.total_packets,
            "valid_packets": self.valid_packets,
            "invalid_packets": self.invalid_packets,
            "sync_integrity": round(self.sync_integrity, 4),
            "unique_pid_count": self.unique_pid_count,
            "pid_distribution": self.pid_distribution,
            "pid_percentages": {k: round(v, 4) for k, v in self.pid_percentages.items()},
            "pid_entropy": round(self.pid_entropy, 4),
            "null_packet_count": self.null_packet_count,
            "null_packet_ratio": round(self.null_packet_ratio, 6),
            "tei_error_count": self.tei_error_count,
            "tei_error_rate": round(self.tei_error_rate, 6),
            "continuity_error_count": self.continuity_error_count,
            "continuity_error_rate": round(self.continuity_error_rate, 6),
            "continuity_errors_by_pid": self.continuity_errors_by_pid,
            "adaptation_field_count": self.adaptation_field_count,
            "adaptation_field_ratio": round(self.adaptation_field_ratio, 6),
            "adaptation_only_count": self.adaptation_only_count,
            "adaptation_and_payload_count": self.adaptation_and_payload_count,
            "payload_packet_count": self.payload_packet_count,
            "payload_packet_ratio": round(self.payload_packet_ratio, 6),
            "total_payload_bytes": self.total_payload_bytes,
            "mean_payload_bytes_per_packet": round(self.mean_payload_bytes_per_packet, 2),
        }


# =============================================================================
# 4. Unified Multi-Format Feature Representation
# =============================================================================

@dataclass
class UnifiedStreamFeatureSet:
    """
    Unified multi-format feature representation for PRJ_111.
    Normalizes common cross-format stream metrics while preserving format-specific
    telemetry without forcing a sequential conversion pipeline.
    """
    format: StreamFormat
    common: CommonMetrics
    ts_specific: Optional[TSSpecificMetrics] = None
    gse_specific: Optional[GSESpecificMetrics] = None
    bbframe_specific: Optional[BBFrameSpecificMetrics] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Converts feature set into a structured hierarchical dictionary."""
        return {
            "format": self.format.value if hasattr(self.format, "value") else str(self.format),
            "common": self.common.to_dict(),
            "ts_specific": self.ts_specific.to_dict() if self.ts_specific else None,
            "gse_specific": self.gse_specific.to_dict() if self.gse_specific else None,
            "bbframe_specific": self.bbframe_specific.to_dict() if self.bbframe_specific else None,
            "metadata": self.metadata,
        }

    def to_flat_dict(self) -> Dict[str, Any]:
        """Produces a flattened key-value dictionary for reporting or tabular views."""
        flat: Dict[str, Any] = {
            "format": self.format.value if hasattr(self.format, "value") else str(self.format),
        }
        for k, v in self.common.to_dict().items():
            flat[f"common_{k}"] = v

        if self.ts_specific:
            for k, v in self.ts_specific.to_dict().items():
                flat[f"ts_{k}"] = v
        elif self.gse_specific:
            for k, v in self.gse_specific.to_dict().items():
                flat[f"gse_{k}"] = v
        elif self.bbframe_specific:
            for k, v in self.bbframe_specific.to_dict().items():
                flat[f"bb_{k}"] = v

        return flat

    def to_vector(self) -> Dict[str, float]:
        """
        Produces a normalized numerical telemetry vector for AI/ML downstream consumption (F2/F3).
        Common metrics are mapped to consistent numeric ranges or log-scaled values.
        Missing format-specific indicators are explicitly set to 0.0 with one-hot format indicators.
        """
        c = self.common
        vec: Dict[str, float] = {
            # Format one-hot indicators
            "is_ts": 1.0 if self.format == StreamFormat.MPEG_TS else 0.0,
            "is_gse": 1.0 if self.format == StreamFormat.GSE else 0.0,
            "is_bbframe": 1.0 if self.format == StreamFormat.BB_FRAME else 0.0,

            # Common normalized telemetry
            "integrity_ratio": float(c.integrity_ratio),
            "error_rate": float(c.error_rate),
            "log_total_units": math.log10(max(1, c.total_units)),
            "log_total_payload": math.log10(max(1, c.total_payload_bytes)),
            "mean_payload_kb": (c.mean_payload_bytes / 1024.0),
            "payload_ratio": float(c.payload_ratio) if c.payload_ratio is not None else 0.0,
            "entropy": float(c.entropy) if c.entropy is not None else 0.0,
        }

        # TS-specific vector elements
        if self.ts_specific:
            vec["ts_null_packet_ratio"] = float(self.ts_specific.null_packet_ratio)
            vec["ts_tei_error_rate"] = float(self.ts_specific.tei_error_rate)
            vec["ts_continuity_error_rate"] = float(self.ts_specific.continuity_error_rate)
            vec["ts_adaptation_field_ratio"] = float(self.ts_specific.adaptation_field_ratio)
            vec["ts_unique_pid_count"] = float(self.ts_specific.unique_pid_count)
        else:
            vec["ts_null_packet_ratio"] = 0.0
            vec["ts_tei_error_rate"] = 0.0
            vec["ts_continuity_error_rate"] = 0.0
            vec["ts_adaptation_field_ratio"] = 0.0
            vec["ts_unique_pid_count"] = 0.0

        # GSE-specific vector elements
        if self.gse_specific:
            vec["gse_fragmentation_ratio"] = float(self.gse_specific.fragmentation_ratio)
            vec["gse_padding_ratio"] = (self.gse_specific.padding_packets / max(1, self.gse_specific.total_pdus))
        else:
            vec["gse_fragmentation_ratio"] = 0.0
            vec["gse_padding_ratio"] = 0.0

        # BBFrame-specific vector elements
        if self.bbframe_specific:
            total_bb = max(1, self.bbframe_specific.total_frames)
            sis_count = self.bbframe_specific.input_stream_modes.get("SIS", 0)
            ccm_count = self.bbframe_specific.coding_modulation_modes.get("CCM", 0)
            vec["bb_sis_ratio"] = float(sis_count / total_bb)
            vec["bb_ccm_ratio"] = float(ccm_count / total_bb)
            vec["bb_crc_error_rate"] = float(self.bbframe_specific.invalid_crc_frames / total_bb)
        else:
            vec["bb_sis_ratio"] = 0.0
            vec["bb_ccm_ratio"] = 0.0
            vec["bb_crc_error_rate"] = 0.0

        return vec

    def to_format_vector(self, format: Optional[StreamFormat] = None) -> Dict[str, float]:
        """
        Produces a format-tailored numerical telemetry vector containing only semantically
        valid metrics for the given or detected stream format. Avoids cross-format zero-filling.
        """
        target_format = format or self.format
        c = self.common

        # Format-Agnostic Common Vector
        if target_format == StreamFormat.UNKNOWN:
            return {
                "integrity_ratio": float(c.integrity_ratio),
                "error_rate": float(c.error_rate),
                "log_total_units": math.log10(max(1, c.total_units)),
                "log_total_payload": math.log10(max(1, c.total_payload_bytes)),
                "mean_payload_kb": (c.mean_payload_bytes / 1024.0),
                "payload_ratio": float(c.payload_ratio) if c.payload_ratio is not None else 0.0,
                "entropy": float(c.entropy) if c.entropy is not None else 0.0,
            }

        # MPEG-TS Specific Vector (12 features)
        if target_format == StreamFormat.MPEG_TS and self.ts_specific:
            ts = self.ts_specific
            return {
                "integrity_ratio": float(c.integrity_ratio),
                "error_rate": float(c.error_rate),
                "log_total_units": math.log10(max(1, c.total_units)),
                "log_total_payload": math.log10(max(1, c.total_payload_bytes)),
                "mean_payload_kb": (c.mean_payload_bytes / 1024.0),
                "payload_ratio": float(c.payload_ratio) if c.payload_ratio is not None else 0.0,
                "pid_entropy": float(ts.pid_entropy),
                "null_packet_ratio": float(ts.null_packet_ratio),
                "tei_error_rate": float(ts.tei_error_rate),
                "continuity_error_rate": float(ts.continuity_error_rate),
                "adaptation_field_ratio": float(ts.adaptation_field_ratio),
                "unique_pid_count": float(ts.unique_pid_count),
            }

        # GSE Specific Vector (9 features)
        if target_format == StreamFormat.GSE and self.gse_specific:
            gse = self.gse_specific
            return {
                "integrity_ratio": float(c.integrity_ratio),
                "error_rate": float(c.error_rate),
                "log_total_units": math.log10(max(1, c.total_units)),
                "log_total_payload": math.log10(max(1, c.total_payload_bytes)),
                "mean_payload_kb": (c.mean_payload_bytes / 1024.0),
                "payload_ratio": float(c.payload_ratio) if c.payload_ratio is not None else 0.0,
                "protocol_entropy": float(gse.protocol_entropy),
                "fragmentation_ratio": float(gse.fragmentation_ratio),
                "padding_ratio": float(gse.padding_packets / max(1, gse.total_pdus)),
            }

        # BBFrame Specific Vector (10 features)
        if target_format == StreamFormat.BB_FRAME and self.bbframe_specific:
            bb = self.bbframe_specific
            total_bb = max(1, bb.total_frames)
            sis_count = bb.input_stream_modes.get("SIS", 0)
            ccm_count = bb.coding_modulation_modes.get("CCM", 0)
            return {
                "integrity_ratio": float(c.integrity_ratio),
                "error_rate": float(c.error_rate),
                "log_total_units": math.log10(max(1, c.total_units)),
                "log_total_payload": math.log10(max(1, c.total_payload_bytes)),
                "mean_payload_kb": (c.mean_payload_bytes / 1024.0),
                "payload_ratio": float(c.payload_ratio) if c.payload_ratio is not None else 0.0,
                "entropy": float(c.entropy) if c.entropy is not None else 0.0,
                "sis_ratio": float(sis_count / total_bb),
                "ccm_ratio": float(ccm_count / total_bb),
                "crc_error_rate": float(bb.invalid_crc_frames / total_bb),
            }

        # Fallback to common vector if format-specific metrics are absent
        return {
            "integrity_ratio": float(c.integrity_ratio),
            "error_rate": float(c.error_rate),
            "log_total_units": math.log10(max(1, c.total_units)),
            "log_total_payload": math.log10(max(1, c.total_payload_bytes)),
            "mean_payload_kb": (c.mean_payload_bytes / 1024.0),
            "payload_ratio": float(c.payload_ratio) if c.payload_ratio is not None else 0.0,
            "entropy": float(c.entropy) if c.entropy is not None else 0.0,
        }


# =============================================================================
# 5. Feature Extractor Engine
# =============================================================================

class FeatureExtractor:
    """
    Computes common, structural, and protocol-specific metrics across
    MPEG-TS, GSE, and DVB-S2 BBFrame stream statistics.
    """

    @staticmethod
    def calculate_entropy(counts: Dict[Any, int]) -> float:
        """
        Calculates Shannon entropy across any discrete probability distribution:
            H = - sum(p_i * log2(p_i))
        Returns 0.0 for empty or single-category distributions.
        """
        total = sum(counts.values())
        if total <= 0:
            return 0.0

        entropy = 0.0
        for count in counts.values():
            if count > 0:
                p = count / total
                entropy -= p * math.log2(p)
        return round(entropy, 4)

    @staticmethod
    def calculate_pid_entropy(pid_counts: Dict[int, int]) -> float:
        """Backward-compatible alias for Shannon entropy across TS PID distribution."""
        return FeatureExtractor.calculate_entropy(pid_counts)

    @staticmethod
    def calculate_pid_percentages(pid_counts: Dict[int, int]) -> Dict[int, float]:
        """Calculates the percentage share of each PID in the TS stream."""
        total = sum(pid_counts.values())
        if total == 0:
            return {}
        return {pid: round((count / total) * 100.0, 4) for pid, count in pid_counts.items()}

    # -------------------------------------------------------------------------
    # Backward-Compatible Extraction (for Feature F1 Stream Health Analysis)
    # -------------------------------------------------------------------------
    def extract_from_ts_stats(self, stats: TSStreamStatistics) -> StreamFeatureSet:
        """
        Derives full quantitative stream features from accumulated TS statistics.
        Retained for 100% backward compatibility with Feature F1.
        """
        total = stats.total_packets
        valid = stats.valid_sync_packets
        invalid = stats.sync_byte_errors + stats.malformed_packet_count

        if total == 0:
            return StreamFeatureSet(
                total_packets=0,
                valid_packets=0,
                invalid_packets=0,
                sync_integrity=0.0,
                unique_pid_count=0,
                pid_distribution={},
                pid_percentages={},
                pid_entropy=0.0,
                null_packet_count=0,
                null_packet_ratio=0.0,
                tei_error_count=0,
                tei_error_rate=0.0,
                continuity_error_count=0,
                continuity_error_rate=0.0,
                continuity_errors_by_pid={},
                adaptation_field_count=0,
                adaptation_field_ratio=0.0,
                adaptation_only_count=0,
                adaptation_and_payload_count=0,
                payload_packet_count=0,
                payload_packet_ratio=0.0,
                total_payload_bytes=0,
                mean_payload_bytes_per_packet=0.0,
            )

        sync_integrity = (valid / total) * 100.0
        total_cc_errors = sum(stats.continuity_errors.values())
        null_ratio = stats.null_packet_count / total
        tei_rate = stats.tei_error_count / total
        cc_rate = total_cc_errors / total
        af_ratio = stats.adaptation_field_count / total
        payload_ratio = stats.payload_packet_count / total
        mean_payload = stats.total_payload_bytes / total

        return StreamFeatureSet(
            total_packets=total,
            valid_packets=valid,
            invalid_packets=invalid,
            sync_integrity=round(sync_integrity, 4),
            unique_pid_count=len(stats.pid_counts),
            pid_distribution=dict(stats.pid_counts),
            pid_percentages=self.calculate_pid_percentages(stats.pid_counts),
            pid_entropy=self.calculate_pid_entropy(stats.pid_counts),
            null_packet_count=stats.null_packet_count,
            null_packet_ratio=round(null_ratio, 6),
            tei_error_count=stats.tei_error_count,
            tei_error_rate=round(tei_rate, 6),
            continuity_error_count=total_cc_errors,
            continuity_error_rate=round(cc_rate, 6),
            continuity_errors_by_pid=dict(stats.continuity_errors),
            adaptation_field_count=stats.adaptation_field_count,
            adaptation_field_ratio=round(af_ratio, 6),
            adaptation_only_count=stats.adaptation_only_count,
            adaptation_and_payload_count=stats.adaptation_and_payload_count,
            payload_packet_count=stats.payload_packet_count,
            payload_packet_ratio=round(payload_ratio, 6),
            total_payload_bytes=stats.total_payload_bytes,
            mean_payload_bytes_per_packet=round(mean_payload, 2),
        )

    # -------------------------------------------------------------------------
    # Unified Multi-Format Extraction
    # -------------------------------------------------------------------------
    def extract_unified_from_ts(
        self,
        stats: TSStreamStatistics,
        metadata: Optional[Dict[str, Any]] = None
    ) -> UnifiedStreamFeatureSet:
        """Derives UnifiedStreamFeatureSet from MPEG-TS statistics."""
        total = stats.total_packets
        valid = stats.valid_sync_packets
        invalid = stats.sync_byte_errors + stats.malformed_packet_count
        total_cc = sum(stats.continuity_errors.values())
        error_count = stats.sync_byte_errors + stats.malformed_packet_count + stats.tei_error_count + total_cc

        integrity_ratio = (valid / total) if total > 0 else 0.0
        error_rate = (error_count / total) if total > 0 else 0.0
        mean_payload = (stats.total_payload_bytes / total) if total > 0 else 0.0
        payload_ratio = (stats.payload_packet_count / total) if total > 0 else 0.0
        entropy = self.calculate_entropy(stats.pid_counts)

        common = CommonMetrics(
            total_units=total,
            valid_units=valid,
            invalid_units=invalid,
            truncated_units=0,
            integrity_ratio=integrity_ratio,
            total_payload_bytes=stats.total_payload_bytes,
            mean_payload_bytes=mean_payload,
            payload_ratio=payload_ratio,
            stream_type="MPEG_TS_MULTIPLEX",
            unit_size_bytes_min=188 if total > 0 else None,
            unit_size_bytes_max=188 if total > 0 else None,
            unit_size_bytes_mean=188.0 if total > 0 else None,
            error_count=error_count,
            error_rate=error_rate,
            entropy=entropy,
        )

        ts_specific = TSSpecificMetrics(
            unique_pid_count=len(stats.pid_counts),
            pid_distribution=dict(stats.pid_counts),
            pid_percentages=self.calculate_pid_percentages(stats.pid_counts),
            pid_entropy=entropy,
            null_packet_count=stats.null_packet_count,
            null_packet_ratio=(stats.null_packet_count / total) if total > 0 else 0.0,
            tei_error_count=stats.tei_error_count,
            tei_error_rate=(stats.tei_error_count / total) if total > 0 else 0.0,
            continuity_error_count=total_cc,
            continuity_error_rate=(total_cc / total) if total > 0 else 0.0,
            continuity_errors_by_pid=dict(stats.continuity_errors),
            adaptation_field_count=stats.adaptation_field_count,
            adaptation_field_ratio=(stats.adaptation_field_count / total) if total > 0 else 0.0,
            adaptation_only_count=stats.adaptation_only_count,
            adaptation_and_payload_count=stats.adaptation_and_payload_count,
            payload_packet_count=stats.payload_packet_count,
            payload_packet_ratio=payload_ratio,
            scrambled_packet_count=getattr(stats, "scrambled_packet_count", None),
        )

        return UnifiedStreamFeatureSet(
            format=StreamFormat.MPEG_TS,
            common=common,
            ts_specific=ts_specific,
            gse_specific=None,
            bbframe_specific=None,
            metadata=metadata or {},
        )

    def extract_unified_from_gse(
        self,
        stats: GSEStreamStatistics,
        metadata: Optional[Dict[str, Any]] = None
    ) -> UnifiedStreamFeatureSet:
        """Derives UnifiedStreamFeatureSet from GSE statistics."""
        total = stats.total_pdus
        valid = stats.valid_pdus
        invalid = stats.malformed_pdus
        truncated = stats.truncated_pdus
        error_count = invalid + truncated

        integrity_ratio = (valid / total) if total > 0 else 0.0
        error_rate = (error_count / total) if total > 0 else 0.0
        mean_payload = (stats.total_payload_bytes / valid) if valid > 0 else 0.0
        payload_ratio = (stats.total_payload_bytes / stats.total_bytes_read) if stats.total_bytes_read > 0 else None

        dominant_proto = (
            max(stats.protocol_type_counts.items(), key=lambda x: x[1])[0]
            if stats.protocol_type_counts else "UNKNOWN"
        )
        stream_type = f"GSE_{dominant_proto}"

        entropy = self.calculate_entropy(stats.protocol_type_counts)

        common = CommonMetrics(
            total_units=total,
            valid_units=valid,
            invalid_units=invalid,
            truncated_units=truncated,
            integrity_ratio=integrity_ratio,
            total_payload_bytes=stats.total_payload_bytes,
            mean_payload_bytes=mean_payload,
            payload_ratio=payload_ratio,
            stream_type=stream_type,
            unit_size_bytes_min=None,
            unit_size_bytes_max=None,
            unit_size_bytes_mean=round(mean_payload, 2) if valid > 0 else None,
            error_count=error_count,
            error_rate=error_rate,
            entropy=entropy,
        )

        frag_total = stats.first_fragments + stats.intermediate_fragments + stats.last_fragments
        frag_ratio = (frag_total / total) if total > 0 else 0.0
        gse_specific = GSESpecificMetrics(
            total_pdus=total,
            valid_pdus=valid,
            malformed_pdus=invalid,
            truncated_pdus=truncated,
            padding_packets=stats.padding_packets,
            unfragmented_pdus=stats.unfragmented_pdus,
            fragmented_pdus_total=frag_total,
            first_fragments=stats.first_fragments,
            intermediate_fragments=stats.intermediate_fragments,
            last_fragments=stats.last_fragments,
            fragmentation_ratio=frag_ratio,
            label_type_distribution=dict(stats.label_type_counts),
            protocol_type_distribution=dict(stats.protocol_type_counts),
            encapsulated_protocol_distribution=dict(stats.encapsulated_protocols),
            protocol_entropy=entropy,
        )

        return UnifiedStreamFeatureSet(
            format=StreamFormat.GSE,
            common=common,
            ts_specific=None,
            gse_specific=gse_specific,
            bbframe_specific=None,
            metadata=metadata or {},
        )

    def extract_unified_from_bbframe(
        self,
        stats: BBFrameStreamStatistics,
        metadata: Optional[Dict[str, Any]] = None
    ) -> UnifiedStreamFeatureSet:
        """Derives UnifiedStreamFeatureSet from DVB-S2 Baseband Frame statistics."""
        total = stats.total_frames
        valid = stats.valid_frames
        invalid = stats.invalid_crc_frames + stats.malformed_headers
        truncated = stats.truncated_frames
        error_count = stats.invalid_crc_frames + stats.malformed_headers + truncated

        integrity_ratio = (valid / total) if total > 0 else 0.0
        error_rate = (error_count / total) if total > 0 else 0.0
        mean_payload = (stats.total_payload_bytes / valid) if valid > 0 else 0.0
        payload_ratio = (stats.total_payload_bytes / stats.total_bytes_read) if stats.total_bytes_read > 0 else None

        dominant_type = (
            max(stats.stream_type_counts.items(), key=lambda x: x[1])[0]
            if stats.stream_type_counts else "UNKNOWN"
        )
        stream_type = f"BBFRAME_{dominant_type}"

        dfl_bytes_list = [d // 8 for d in stats.dfl_values]
        min_len = min(dfl_bytes_list) if dfl_bytes_list else None
        max_len = max(dfl_bytes_list) if dfl_bytes_list else None
        mean_len = (sum(dfl_bytes_list) / len(dfl_bytes_list)) if dfl_bytes_list else None

        # Entropy of stream types or ISI distribution
        entropy = (
            self.calculate_entropy(stats.isi_counts)
            if stats.isi_counts
            else self.calculate_entropy(stats.stream_type_counts)
        )

        common = CommonMetrics(
            total_units=total,
            valid_units=valid,
            invalid_units=invalid,
            truncated_units=truncated,
            integrity_ratio=integrity_ratio,
            total_payload_bytes=stats.total_payload_bytes,
            mean_payload_bytes=mean_payload,
            payload_ratio=payload_ratio,
            stream_type=stream_type,
            unit_size_bytes_min=min_len,
            unit_size_bytes_max=max_len,
            unit_size_bytes_mean=mean_len,
            error_count=error_count,
            error_rate=error_rate,
            entropy=entropy,
        )

        dfl_min_bits = min(stats.dfl_values) if stats.dfl_values else None
        dfl_max_bits = max(stats.dfl_values) if stats.dfl_values else None
        dfl_mean_bits = (sum(stats.dfl_values) / len(stats.dfl_values)) if stats.dfl_values else None
        upl_mean_bits = (sum(stats.upl_values) / len(stats.upl_values)) if stats.upl_values else None
        crc_status = "ALL_VALID" if stats.invalid_crc_frames == 0 else "CRC_ERRORS_DETECTED"

        bbframe_specific = BBFrameSpecificMetrics(
            total_frames=total,
            valid_frames=valid,
            invalid_crc_frames=stats.invalid_crc_frames,
            malformed_headers=stats.malformed_headers,
            truncated_frames=truncated,
            stream_type_distribution=dict(stats.stream_type_counts),
            input_stream_modes=dict(stats.input_stream_mode_counts),
            coding_modulation_modes=dict(stats.coding_modulation_counts),
            roll_off_distribution=dict(stats.roll_off_counts),
            mode_adaptation_distribution=dict(stats.mode_adaptation_counts),
            isi_distribution=dict(stats.isi_counts),
            sync_byte_distribution=dict(stats.sync_byte_counts),
            dfl_min_bits=dfl_min_bits,
            dfl_max_bits=dfl_max_bits,
            dfl_mean_bits=dfl_mean_bits,
            upl_mean_bits=upl_mean_bits,
            crc_status=crc_status,
        )

        return UnifiedStreamFeatureSet(
            format=StreamFormat.BB_FRAME,
            common=common,
            ts_specific=None,
            gse_specific=None,
            bbframe_specific=bbframe_specific,
            metadata=metadata or {},
        )

    def extract_unified(
        self,
        stats: Any,
        format: Optional[StreamFormat] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> UnifiedStreamFeatureSet:
        """
        Universal extraction dispatcher. Automatically identifies statistics type
        or format enum and routes to the appropriate unified feature builder.
        """
        if isinstance(stats, TSStreamStatistics) or format == StreamFormat.MPEG_TS:
            return self.extract_unified_from_ts(stats, metadata=metadata)
        elif isinstance(stats, GSEStreamStatistics) or format == StreamFormat.GSE:
            return self.extract_unified_from_gse(stats, metadata=metadata)
        elif isinstance(stats, BBFrameStreamStatistics) or format == StreamFormat.BB_FRAME:
            return self.extract_unified_from_bbframe(stats, metadata=metadata)
        else:
            raise ValueError(f"Unsupported statistics object or format: {type(stats)} / {format}")

    def extract_from_handler(
        self,
        handler: Any,
        max_units: Optional[int] = None
    ) -> UnifiedStreamFeatureSet:
        """
        High-level pipeline method: ingests a StreamHandler, executes the appropriate
        parser, accumulates statistics, and returns the UnifiedStreamFeatureSet.
        """
        parser = handler.get_parser()
        # Drain generator to collect full statistics
        list(parser.parse_file(handler.path, max_packets=max_units))
        stats = parser.stats
        meta = handler.get_stream_info().to_dict()
        return self.extract_unified(stats, format=handler.format, metadata=meta)
