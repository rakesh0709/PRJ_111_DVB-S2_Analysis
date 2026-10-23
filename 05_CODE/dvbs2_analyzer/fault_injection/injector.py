"""
StreamFaultInjector implementation for PRJ_111 (Chunk 2).

Provides deterministic, reproducible in-memory fault injections across
MPEG-TS, GSE, and DVB-S2 Baseband streams.
Strictly leaves source datasets untouched and reports complete injection metadata.
"""

from pathlib import Path
import struct
from typing import Any, Dict, List, Optional, Tuple, Union

from dvbs2_analyzer.config import StreamFormat
from dvbs2_analyzer.fault_injection.models import (
    FaultMetadata,
    FaultType,
    InjectionTarget,
    PerturbationResult,
)
from dvbs2_analyzer.parsers.bbframe_parser import crc8_dvbs2, BBFrameParser


class StreamFaultInjector:
    """
    Deterministic fault injection engine for DVB-S2 receiver output streams.
    Operates strictly on memory copies without modifying the underlying source files.
    """

    def __init__(self, seed: int = 42):
        self.seed = int(seed)

    # -------------------------------------------------------------------------
    # Helper Utilities
    # -------------------------------------------------------------------------

    @staticmethod
    def _diff_bytes(original: bytes, mutated: bytes) -> int:
        """Counts the number of differing bytes between original and mutated buffers."""
        min_len = min(len(original), len(mutated))
        diff = sum(1 for i in range(min_len) if original[i] != mutated[i])
        diff += abs(len(original) - len(mutated))
        return diff

    @staticmethod
    def _locate_pcapng_bbframe_offsets(data: bytes) -> List[int]:
        """
        Parses PCAP-NG structures and extracts exact byte offsets of every
        DVB-S2 BBHeader within the raw byte stream.
        """
        pos = 0
        frame_offsets: List[int] = []
        data_len = len(data)

        while pos < data_len:
            if pos + 8 > data_len:
                break
            b_type, b_len = struct.unpack("<II", data[pos : pos + 8])
            if b_len < 12:
                break
            body = data[pos + 8 : pos + b_len - 4]
            if b_type == 6 and len(body) >= 20:  # Enhanced Packet Block (EPB)
                cap_len = struct.unpack("<I", body[12:16])[0]
                pkt_data = body[20 : 20 + cap_len]
                # Check for Ethernet + IPv4 + UDP encapsulation
                if len(pkt_data) >= 34 and pkt_data[12:14] == b"\x08\x00" and pkt_data[23] == 17:
                    ihl = (pkt_data[14] & 0x0F) * 4
                    udp_payload_offset = pos + 8 + 20 + 14 + ihl + 8
                    payload = data[udp_payload_offset : pos + 8 + 20 + cap_len]
                    if len(payload) >= 10:
                        ma_offset = 0
                        if len(payload) >= 14 and payload[0] == 0xB8:
                            if crc8_dvbs2(payload[4:13]) == payload[13]:
                                ma_offset = 4
                            elif crc8_dvbs2(payload[2:11]) == payload[11]:
                                ma_offset = 2
                            elif len(payload) >= 13 and crc8_dvbs2(payload[3:12]) == payload[12]:
                                ma_offset = 3
                            else:
                                pos += b_len
                                continue
                        else:
                            if crc8_dvbs2(payload[:9]) != payload[9]:
                                pos += b_len
                                continue
                        frame_offsets.append(udp_payload_offset + ma_offset)
            pos += b_len

        return frame_offsets

    # -------------------------------------------------------------------------
    # Null / Control Perturbation
    # -------------------------------------------------------------------------

    def inject_control_null(
        self,
        source_data: bytes,
        source_name: str = "stream",
        format_name: str = "GENERIC",
        window_size: int = 200,
    ) -> PerturbationResult:
        """
        Creates an exact, unmodified copy of the stream.
        Used as a negative control to verify that zero-fault runs maintain baseline parity.
        """
        meta = FaultMetadata(
            fault_id="CTRL_NULL_001",
            format=format_name,
            fault_type=FaultType.NULL_CONTROL,
            source_dataset=source_name,
            seed=self.seed,
            injection_unit_index=0,
            affected_unit_count=0,
            injection_byte_offset=0,
            affected_byte_range=(0, 0),
            target_window_index=0,
            affected_windows=[],
            parameters={"is_control": True},
            bytes_modified_count=0,
        )
        return PerturbationResult(
            metadata=meta,
            mutated_bytes=bytes(source_data),
            original_size=len(source_data),
            mutated_size=len(source_data),
            differing_bytes_count=0,
        )

    # -------------------------------------------------------------------------
    # MPEG-TS Fault Injections
    # -------------------------------------------------------------------------

    def inject_ts_tei(
        self,
        source_data: bytes,
        target: InjectionTarget,
        source_name: str = "sample.ts",
    ) -> PerturbationResult:
        """
        Sets the Transport Error Indicator (TEI, bit 7 of byte 1) on target packets.
        Expected: F1 detects increased TEI errors and degrades health. F2 observes
        altered tei_error_rate / error_rate features in the target window.
        """
        mut = bytearray(source_data)
        total_packets = len(mut) // 188
        unit_start = max(0, min(target.unit_start_index, total_packets - 1))
        unit_count = max(1, min(target.unit_count, total_packets - unit_start))

        byte_start = unit_start * 188
        byte_end = (unit_start + unit_count) * 188
        modified = 0

        for p_idx in range(unit_start, unit_start + unit_count):
            off = p_idx * 188
            if off + 1 < len(mut):
                if not (mut[off + 1] & 0x80):
                    mut[off + 1] |= 0x80
                    modified += 1

        meta = FaultMetadata(
            fault_id=f"TS_TEI_{unit_start}_{unit_count}",
            format="MPEG_TS",
            fault_type=FaultType.TS_TEI,
            source_dataset=source_name,
            seed=self.seed,
            injection_unit_index=unit_start,
            affected_unit_count=unit_count,
            injection_byte_offset=byte_start,
            affected_byte_range=(byte_start, byte_end),
            target_window_index=target.target_window_index,
            affected_windows=target.affected_window_indices,
            parameters={"packet_count": unit_count},
            bytes_modified_count=modified,
        )

        return PerturbationResult(
            metadata=meta,
            mutated_bytes=bytes(mut),
            original_size=len(source_data),
            mutated_size=len(mut),
            differing_bytes_count=self._diff_bytes(source_data, mut),
        )

    def inject_ts_cc_discontinuity(
        self,
        source_data: bytes,
        target: InjectionTarget,
        cc_skip: int = 5,
        source_name: str = "sample.ts",
    ) -> PerturbationResult:
        """
        Modifies the Continuity Counter (CC, bits 0..3 of byte 3) of target packets
        to induce a sequence discontinuity.
        Expected: F1 detects CC discontinuities. F2 receives the altered stream.
        """
        mut = bytearray(source_data)
        total_packets = len(mut) // 188
        unit_start = max(0, min(target.unit_start_index, total_packets - 1))
        unit_count = max(1, min(target.unit_count, total_packets - unit_start))

        byte_start = unit_start * 188
        byte_end = (unit_start + unit_count) * 188
        modified = 0

        for p_idx in range(unit_start, unit_start + unit_count):
            off = p_idx * 188
            if off + 3 < len(mut):
                curr_cc = mut[off + 3] & 0x0F
                new_cc = (curr_cc + cc_skip) & 0x0F
                mut[off + 3] = (mut[off + 3] & 0xF0) | new_cc
                modified += 1

        meta = FaultMetadata(
            fault_id=f"TS_CC_{unit_start}_{unit_count}",
            format="MPEG_TS",
            fault_type=FaultType.TS_CC_DISCONTINUITY,
            source_dataset=source_name,
            seed=self.seed,
            injection_unit_index=unit_start,
            affected_unit_count=unit_count,
            injection_byte_offset=byte_start,
            affected_byte_range=(byte_start, byte_end),
            target_window_index=target.target_window_index,
            affected_windows=target.affected_window_indices,
            parameters={"cc_skip": cc_skip, "packet_count": unit_count},
            bytes_modified_count=modified,
        )

        return PerturbationResult(
            metadata=meta,
            mutated_bytes=bytes(mut),
            original_size=len(source_data),
            mutated_size=len(mut),
            differing_bytes_count=self._diff_bytes(source_data, mut),
        )

    def inject_ts_pid_perturbation(
        self,
        source_data: bytes,
        target: InjectionTarget,
        new_pid: int = 500,
        source_name: str = "sample.ts",
    ) -> PerturbationResult:
        """
        Modifies the 13-bit PID of a subset of target packets to introduce a
        new multiplex component.
        Expected: F3 dominant PID / multiplex entropy shifts; F2 receives altered
        pid_entropy and unique_pid_count feature values.
        """
        mut = bytearray(source_data)
        total_packets = len(mut) // 188
        unit_start = max(0, min(target.unit_start_index, total_packets - 1))
        unit_count = max(1, min(target.unit_count, total_packets - unit_start))

        byte_start = unit_start * 188
        byte_end = (unit_start + unit_count) * 188
        pid_hi = (new_pid >> 8) & 0x1F
        pid_lo = new_pid & 0xFF
        modified = 0

        for p_idx in range(unit_start, unit_start + unit_count):
            off = p_idx * 188
            if off + 2 < len(mut):
                mut[off + 1] = (mut[off + 1] & 0xE0) | pid_hi
                mut[off + 2] = pid_lo
                modified += 2

        meta = FaultMetadata(
            fault_id=f"TS_PID_{unit_start}_{unit_count}_{new_pid}",
            format="MPEG_TS",
            fault_type=FaultType.TS_PID_PERTURBATION,
            source_dataset=source_name,
            seed=self.seed,
            injection_unit_index=unit_start,
            affected_unit_count=unit_count,
            injection_byte_offset=byte_start,
            affected_byte_range=(byte_start, byte_end),
            target_window_index=target.target_window_index,
            affected_windows=target.affected_window_indices,
            parameters={"new_pid": new_pid, "packet_count": unit_count},
            bytes_modified_count=modified,
        )

        return PerturbationResult(
            metadata=meta,
            mutated_bytes=bytes(mut),
            original_size=len(source_data),
            mutated_size=len(mut),
            differing_bytes_count=self._diff_bytes(source_data, mut),
        )

    # -------------------------------------------------------------------------
    # GSE Fault Injections
    # -------------------------------------------------------------------------

    def inject_gse_fragmentation_perturbation(
        self,
        source_data: bytes,
        target: InjectionTarget,
        source_name: str = "sample.ts",
    ) -> PerturbationResult:
        """
        Perturbs the S (Start) and E (End) fragmentation flags of the target PDU
        inside the BBFrame data field of GSExtract/sample.ts.
        Turns unfragmented PDU (S=1, E=1) into an intermediate fragment (S=0, E=0).
        Expected: F3/F2 fragmentation_ratio changes from nominal distribution.
        """
        mut = bytearray(source_data)
        # PDU 0 starts at offset 225 in GSExtract/sample.ts (inside first BBFrame)
        # Target PDU 0 is at offset 225
        pdu_offset = 225
        byte_start = pdu_offset
        byte_end = pdu_offset + 2

        # Clear bits 7 and 6 of byte 0 (S=0, E=0)
        orig_byte = mut[pdu_offset]
        mut[pdu_offset] = (orig_byte & 0x3F)

        meta = FaultMetadata(
            fault_id="GSE_FRAG_001",
            format="GSE",
            fault_type=FaultType.GSE_S_E_PERTURBATION,
            source_dataset=source_name,
            seed=self.seed,
            injection_unit_index=target.unit_start_index,
            affected_unit_count=1,
            injection_byte_offset=byte_start,
            affected_byte_range=(byte_start, byte_end),
            target_window_index=target.target_window_index,
            affected_windows=target.affected_window_indices,
            parameters={"pdu_offset": pdu_offset, "original_flags": hex(orig_byte), "new_flags": hex(mut[pdu_offset])},
            bytes_modified_count=1,
        )

        return PerturbationResult(
            metadata=meta,
            mutated_bytes=bytes(mut),
            original_size=len(source_data),
            mutated_size=len(mut),
            differing_bytes_count=self._diff_bytes(source_data, mut),
        )

    def inject_gse_truncation(
        self,
        source_data: bytes,
        truncate_bytes: int = 500,
        source_name: str = "sample.ts",
    ) -> PerturbationResult:
        """
        Truncates the end of the GSE capture, removing trailer bytes.
        Expected: Number of parsed PDUs decreases; capture termination boundary shifts.
        """
        mut = source_data[: max(0, len(source_data) - truncate_bytes)]
        byte_start = len(mut)
        byte_end = len(source_data)

        meta = FaultMetadata(
            fault_id=f"GSE_TRUNC_{truncate_bytes}",
            format="GSE",
            fault_type=FaultType.GSE_PDU_TRUNCATION,
            source_dataset=source_name,
            seed=self.seed,
            injection_unit_index=13, # Final PDU affected
            affected_unit_count=1,
            injection_byte_offset=byte_start,
            affected_byte_range=(byte_start, byte_end),
            target_window_index=4,   # Final window in GSE (w=3, total=5)
            affected_windows=[4],
            parameters={"truncated_bytes": truncate_bytes},
            bytes_modified_count=truncate_bytes,
        )

        return PerturbationResult(
            metadata=meta,
            mutated_bytes=mut,
            original_size=len(source_data),
            mutated_size=len(mut),
            differing_bytes_count=truncate_bytes,
        )

    # -------------------------------------------------------------------------
    # DVB-S2 BBFrame Fault Injections
    # -------------------------------------------------------------------------

    def inject_bbframe_crc_corruption(
        self,
        source_data: bytes,
        target: InjectionTarget,
        source_name: str = "dvb-s2_bb_example.pcap",
    ) -> PerturbationResult:
        """
        Invalidates the BBHeader CRC-8 checksum of target BBFrames in PCAP-NG.
        In PCAP-NG satellite captures, corrupting CRC-8 causes the frame scanner
        to reject the packet or flag invalid_crc_frames in raw mode.
        """
        mut = bytearray(source_data)
        offsets = self._locate_pcapng_bbframe_offsets(source_data)
        if not offsets:
            raise ValueError("No DVB-S2 BBFrames found in PCAP-NG source buffer.")

        f_start = max(0, min(target.unit_start_index, len(offsets) - 1))
        f_count = max(1, min(target.unit_count, len(offsets) - f_start))

        modified = 0
        first_off = offsets[f_start]
        last_off = offsets[f_start + f_count - 1] + 10

        for f_idx in range(f_start, f_start + f_count):
            off = offsets[f_idx]
            crc_pos = off + 9
            mut[crc_pos] ^= 0xFF  # Invert CRC-8 byte
            modified += 1

        meta = FaultMetadata(
            fault_id=f"BB_CRC_{f_start}_{f_count}",
            format="BB_FRAME",
            fault_type=FaultType.BB_CRC_CORRUPTION,
            source_dataset=source_name,
            seed=self.seed,
            injection_unit_index=f_start,
            affected_unit_count=f_count,
            injection_byte_offset=first_off,
            affected_byte_range=(first_off, last_off),
            target_window_index=target.target_window_index,
            affected_windows=target.affected_window_indices,
            parameters={"frames_affected": f_count},
            bytes_modified_count=modified,
        )

        return PerturbationResult(
            metadata=meta,
            mutated_bytes=bytes(mut),
            original_size=len(source_data),
            mutated_size=len(mut),
            differing_bytes_count=self._diff_bytes(source_data, mut),
        )

    def inject_bbframe_mode_shift(
        self,
        source_data: bytes,
        target: InjectionTarget,
        new_mode: str = "MIS", # "MIS" or "ACM"
        source_name: str = "dvb-s2_bb_example.pcap",
    ) -> PerturbationResult:
        """
        Toggles MATYPE-1 mode adaptation flags (e.g. SIS -> MIS or CCM -> ACM)
        on target frames while correctly recalculating the CRC-8 checksum.
        Expected: F2 receives altered sis_ratio or ccm_ratio in the target window.
        """
        mut = bytearray(source_data)
        offsets = self._locate_pcapng_bbframe_offsets(source_data)
        if not offsets:
            raise ValueError("No DVB-S2 BBFrames found in PCAP-NG source buffer.")

        f_start = max(0, min(target.unit_start_index, len(offsets) - 1))
        f_count = max(1, min(target.unit_count, len(offsets) - f_start))

        modified = 0
        first_off = offsets[f_start]
        last_off = offsets[f_start + f_count - 1] + 10

        for f_idx in range(f_start, f_start + f_count):
            off = offsets[f_idx]
            if new_mode == "MIS":
                # Clear bit 5 (SIS -> MIS)
                mut[off] = (mut[off] & 0xDF)
            elif new_mode == "ACM":
                # Clear bit 4 (CCM -> ACM)
                mut[off] = (mut[off] & 0xEF)
            # Recompute valid CRC-8 over header bytes 0..8
            mut[off + 9] = crc8_dvbs2(mut[off : off + 9])
            modified += 2

        meta = FaultMetadata(
            fault_id=f"BB_MODE_{new_mode}_{f_start}_{f_count}",
            format="BB_FRAME",
            fault_type=FaultType.BB_MATYPE_MODE_SHIFT,
            source_dataset=source_name,
            seed=self.seed,
            injection_unit_index=f_start,
            affected_unit_count=f_count,
            injection_byte_offset=first_off,
            affected_byte_range=(first_off, last_off),
            target_window_index=target.target_window_index,
            affected_windows=target.affected_window_indices,
            parameters={"new_mode": new_mode, "frames_affected": f_count},
            bytes_modified_count=modified,
        )

        return PerturbationResult(
            metadata=meta,
            mutated_bytes=bytes(mut),
            original_size=len(source_data),
            mutated_size=len(mut),
            differing_bytes_count=self._diff_bytes(source_data, mut),
        )
