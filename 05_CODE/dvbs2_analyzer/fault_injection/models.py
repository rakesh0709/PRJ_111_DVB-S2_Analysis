"""
Data models and metadata definitions for Controlled Fault Injection (Chunk 2).

Enforces deterministic metadata tracking, physical byte range mapping,
and target timeline window localization.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple


class FaultType(str, Enum):
    # MPEG-TS Faults
    TS_TEI = "TS_TEI"                          # Transport Error Indicator corruption
    TS_CC_DISCONTINUITY = "TS_CC_DISCONTINUITY"# Continuity counter discontinuity
    TS_PID_PERTURBATION = "TS_PID_PERTURBATION"# PID multiplex distribution shift
    TS_SYNC_CORRUPTION = "TS_SYNC_CORRUPTION"  # Sync byte corruption (0x47 invalidation)

    # GSE Faults
    GSE_PDU_TRUNCATION = "GSE_PDU_TRUNCATION"  # Truncate trailing payload bytes
    GSE_S_E_PERTURBATION = "GSE_S_E_PERTURBATION"# Perturb S/E fragmentation flags
    GSE_LENGTH_CORRUPTION = "GSE_LENGTH_CORRUPTION"# Length field mismatch

    # BBFrame Faults
    BB_CRC_CORRUPTION = "BB_CRC_CORRUPTION"    # Invalidate CRC-8 checksum
    BB_MATYPE_MODE_SHIFT = "BB_MATYPE_MODE_SHIFT"# Perturb SIS/MIS or CCM/ACM modes
    BB_DFL_SHIFT = "BB_DFL_SHIFT"              # Shift Data Field Length (DFL)

    # Control / Null perturbation
    NULL_CONTROL = "NULL_CONTROL"              # Identity copy (0 bits modified)


@dataclass
class InjectionTarget:
    """Specifies the target location and magnitude for a fault injection."""
    unit_start_index: int
    unit_count: int = 1
    window_size: int = 200
    parameters: Dict[str, Any] = field(default_factory=dict)

    @property
    def target_window_index(self) -> int:
        return self.unit_start_index // max(1, self.window_size)

    @property
    def affected_window_indices(self) -> List[int]:
        start_w = self.unit_start_index // max(1, self.window_size)
        end_w = (self.unit_start_index + max(1, self.unit_count) - 1) // max(1, self.window_size)
        return list(range(start_w, end_w + 1))


@dataclass
class FaultMetadata:
    """
    Exhaustive deterministic metadata recording the exact location and scope
    of an injected fault.
    """
    fault_id: str
    format: str
    fault_type: FaultType
    source_dataset: str
    seed: int
    injection_unit_index: int
    affected_unit_count: int
    injection_byte_offset: int
    affected_byte_range: Tuple[int, int]
    target_window_index: int
    affected_windows: List[int]
    parameters: Dict[str, Any] = field(default_factory=dict)
    bytes_modified_count: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "fault_id": self.fault_id,
            "format": self.format,
            "fault_type": self.fault_type.value,
            "source_dataset": self.source_dataset,
            "seed": self.seed,
            "injection_unit_index": self.injection_unit_index,
            "affected_unit_count": self.affected_unit_count,
            "injection_byte_offset": self.injection_byte_offset,
            "affected_byte_range": list(self.affected_byte_range),
            "target_window_index": self.target_window_index,
            "affected_windows": self.affected_windows,
            "parameters": self.parameters,
            "bytes_modified_count": self.bytes_modified_count,
        }


@dataclass
class PerturbationResult:
    """
    Container holding the mutated byte buffer, associated metadata,
    and original-to-mutated verification metrics.
    """
    metadata: FaultMetadata
    mutated_bytes: bytes
    original_size: int
    mutated_size: int
    differing_bytes_count: int

    def to_dict(self) -> Dict[str, Any]:
        return {
            "metadata": self.metadata.to_dict(),
            "original_size": self.original_size,
            "mutated_size": self.mutated_size,
            "differing_bytes_count": self.differing_bytes_count,
        }
