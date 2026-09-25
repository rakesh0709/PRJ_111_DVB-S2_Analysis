"""
MPEG Transport Stream (MPEG-TS) Parser for PRJ_111.

Compliant with ISO/IEC 13818-1 specification.
Provides 188-byte packet parsing, sync byte validation, PID extraction,
Continuity Counter (CC) tracking, adaptation field decoding, and stream statistics.
"""

from collections import defaultdict
from dataclasses import dataclass, field
import logging
from pathlib import Path
from typing import Any, BinaryIO, Dict, Iterator, Optional, Union

from dvbs2_analyzer.config import (
    AFC_ADAPTATION_AND_PAYLOAD,
    AFC_ADAPTATION_ONLY,
    AFC_PAYLOAD_ONLY,
    TS_CONTINUITY_COUNTER_MOD,
    TS_HEADER_SIZE,
    TS_MAX_PID,
    TS_NULL_PID,
    TS_PACKET_SIZE,
    TS_SYNC_BYTE,
)
from dvbs2_analyzer.parsers.base import (
    BaseStreamParser,
    PacketCorruptionError,
    SyncLossError,
)

logger = logging.getLogger(__name__)


@dataclass
class TSPacket:
    """
    Structured representation of a single 188-byte MPEG-TS packet.
    """
    sync_byte: int
    tei: bool                        # Transport Error Indicator
    pusi: bool                       # Payload Unit Start Indicator
    transport_priority: bool         # Transport Priority flag
    pid: int                         # Packet Identifier (13-bit: 0 to 8191)
    transport_scrambling_control: int  # 2-bit scrambling control
    adaptation_field_control: int    # 2-bit AFC
    continuity_counter: int          # 4-bit CC (0 to 15)
    has_adaptation_field: bool
    has_payload: bool
    adaptation_field_length: int     # Length in bytes (0 if not present)
    is_null_packet: bool             # True if PID == 0x1FFF (8191)
    raw_bytes: bytes
    payload: bytes


@dataclass
class TSStreamStatistics:
    """
    Diagnostic metrics and packet counters for an analyzed MPEG-TS stream.
    """
    total_bytes_read: int = 0
    total_packets: int = 0
    valid_sync_packets: int = 0
    sync_byte_errors: int = 0
    tei_error_count: int = 0
    null_packet_count: int = 0
    payload_packet_count: int = 0
    adaptation_field_count: int = 0
    adaptation_only_count: int = 0
    adaptation_and_payload_count: int = 0
    total_payload_bytes: int = 0
    malformed_packet_count: int = 0
    pid_counts: Dict[int, int] = field(default_factory=lambda: defaultdict(int))
    continuity_errors: Dict[int, int] = field(default_factory=lambda: defaultdict(int))

    def to_dict(self) -> Dict[str, Union[int, float, Dict[int, int]]]:
        """Converts statistics into a serializable dictionary."""
        total = self.total_packets
        valid = self.valid_sync_packets
        sync_integrity_pct = (valid / total * 100.0) if total > 0 else 0.0
        null_ratio = (self.null_packet_count / total) if total > 0 else 0.0

        return {
            "total_bytes_read": self.total_bytes_read,
            "total_packets": total,
            "valid_sync_packets": valid,
            "sync_byte_errors": self.sync_byte_errors,
            "sync_integrity_percentage": round(sync_integrity_pct, 4),
            "tei_errors": self.tei_error_count,
            "null_packet_count": self.null_packet_count,
            "null_packet_ratio": round(null_ratio, 4),
            "payload_packet_count": self.payload_packet_count,
            "adaptation_field_count": self.adaptation_field_count,
            "adaptation_only_count": self.adaptation_only_count,
            "adaptation_and_payload_count": self.adaptation_and_payload_count,
            "total_payload_bytes": self.total_payload_bytes,
            "malformed_packet_count": self.malformed_packet_count,
            "unique_pids_count": len(self.pid_counts),
            "pid_distribution": dict(self.pid_counts),
            "continuity_error_distribution": dict(self.continuity_errors),
            "total_continuity_errors": sum(self.continuity_errors.values()),
        }


class TSParser(BaseStreamParser):
    """
    Decodes MPEG Transport Streams into structured packets and computes
    packet-level integrity metrics.
    """

    def __init__(self, strict_mode: bool = False):
        """
        Initializes the TS Parser.

        Args:
            strict_mode: If True, raises exceptions on corrupt sync bytes;
                         if False, logs warnings and attempts resynchronization.
        """
        self.strict_mode = strict_mode
        self.stats = TSStreamStatistics()
        self._last_cc_per_pid: Dict[int, int] = {}

    def reset_statistics(self) -> None:
        """Resets all internal packet counters and continuity trackers."""
        self.stats = TSStreamStatistics()
        self._last_cc_per_pid.clear()

    def parse_packet(self, packet_bytes: bytes) -> TSPacket:
        """
        Parses exactly 188 bytes of raw data into a TSPacket.

        Args:
            packet_bytes: 188-byte buffer.

        Returns:
            TSPacket dataclass with unpacked headers and payload slice.

        Raises:
            PacketCorruptionError: If length != 188 or header fields are invalid.
            SyncLossError: If first byte != 0x47.
        """
        if len(packet_bytes) != TS_PACKET_SIZE:
            raise PacketCorruptionError(
                f"Invalid TS packet length: expected {TS_PACKET_SIZE} bytes, "
                f"got {len(packet_bytes)}"
            )

        sync_byte = packet_bytes[0]
        if sync_byte != TS_SYNC_BYTE:
            raise SyncLossError(
                f"Invalid sync byte: expected 0x{TS_SYNC_BYTE:02x}, "
                f"got 0x{sync_byte:02x}"
            )

        # Header Byte 1 & 2 (16 bits)
        b1 = packet_bytes[1]
        b2 = packet_bytes[2]
        tei = bool(b1 & 0x80)
        pusi = bool(b1 & 0x40)
        transport_priority = bool(b1 & 0x20)
        pid = ((b1 & 0x1F) << 8) | b2

        if pid > TS_MAX_PID:
            raise PacketCorruptionError(f"Extracted PID {pid} exceeds maximum 13-bit value {TS_MAX_PID}")

        # Header Byte 3 (8 bits)
        b3 = packet_bytes[3]
        tsc = (b3 & 0xC0) >> 6
        afc = (b3 & 0x30) >> 4
        cc = b3 & 0x0F

        has_adaptation_field = afc in (AFC_ADAPTATION_ONLY, AFC_ADAPTATION_AND_PAYLOAD)
        has_payload = afc in (AFC_PAYLOAD_ONLY, AFC_ADAPTATION_AND_PAYLOAD)

        adaptation_field_length = 0
        payload_offset = TS_HEADER_SIZE

        if has_adaptation_field:
            adaptation_field_length = packet_bytes[4]
            # Payload starts after 1-byte AFL + the adaptation field itself
            payload_offset = TS_HEADER_SIZE + 1 + adaptation_field_length
            if payload_offset > TS_PACKET_SIZE:
                # Malformed adaptation field length
                raise PacketCorruptionError(
                    f"Adaptation field length {adaptation_field_length} "
                    f"exceeds packet boundary"
                )

        payload = packet_bytes[payload_offset:] if has_payload else b""

        return TSPacket(
            sync_byte=sync_byte,
            tei=tei,
            pusi=pusi,
            transport_priority=transport_priority,
            pid=pid,
            transport_scrambling_control=tsc,
            adaptation_field_control=afc,
            continuity_counter=cc,
            has_adaptation_field=has_adaptation_field,
            has_payload=has_payload,
            adaptation_field_length=adaptation_field_length,
            is_null_packet=(pid == TS_NULL_PID),
            raw_bytes=packet_bytes,
            payload=payload,
        )

    def _track_continuity(self, packet: TSPacket) -> None:
        """
        Validates Continuity Counter sequence for packets of the same PID.
        Only packets carrying payload are required to increment CC.
        """
        pid = packet.pid

        # Null packets (PID 0x1FFF) have undefined CC per ISO/IEC 13818-1
        if packet.is_null_packet:
            return

        # Only packets with payload increment CC
        if not packet.has_payload:
            return

        if pid in self._last_cc_per_pid:
            prev_cc = self._last_cc_per_pid[pid]
            expected_cc = (prev_cc + 1) % TS_CONTINUITY_COUNTER_MOD

            if packet.continuity_counter != expected_cc:
                # CC mismatch indicates packet loss or out-of-order delivery
                self.stats.continuity_errors[pid] += 1
                logger.debug(
                    "CC Discontinuity on PID 0x%04x: expected %d, got %d",
                    pid, expected_cc, packet.continuity_counter
                )

        self._last_cc_per_pid[pid] = packet.continuity_counter

    def parse_stream(
        self,
        stream_io: BinaryIO,
        max_packets: Optional[int] = None
    ) -> Iterator[TSPacket]:
        """
        Reads and decodes packets from a binary stream.

        Args:
            stream_io: Binary file-like stream.
            max_packets: Maximum number of packets to yield.

        Yields:
            TSPacket instances.
        """
        packets_processed = 0

        while max_packets is None or packets_processed < max_packets:
            chunk = stream_io.read(TS_PACKET_SIZE)
            if not chunk or len(chunk) < TS_PACKET_SIZE:
                # End of stream or incomplete trailing packet
                if chunk:
                    self.stats.total_bytes_read += len(chunk)
                break

            self.stats.total_bytes_read += TS_PACKET_SIZE
            self.stats.total_packets += 1

            if chunk[0] != TS_SYNC_BYTE:
                self.stats.sync_byte_errors += 1
                if self.strict_mode:
                    raise SyncLossError(
                        f"Stream lost sync at packet #{self.stats.total_packets} "
                        f"(offset {self.stats.total_bytes_read - TS_PACKET_SIZE}): "
                        f"byte=0x{chunk[0]:02x}"
                    )
                # Resynchronization attempt: look for next 0x47 in chunk
                next_sync = chunk.find(bytes([TS_SYNC_BYTE]), 1)
                if next_sync != -1:
                    stream_io.seek(-len(chunk) + next_sync, 1)
                    self.stats.total_bytes_read += (next_sync - len(chunk))
                continue

            self.stats.valid_sync_packets += 1

            try:
                packet = self.parse_packet(chunk)
            except PacketCorruptionError as err:
                self.stats.malformed_packet_count += 1
                logger.warning("Corrupted packet encountered at packet #%d: %s", self.stats.total_packets, err)
                continue

            # Update stats
            if packet.tei:
                self.stats.tei_error_count += 1
            if packet.is_null_packet:
                self.stats.null_packet_count += 1
            if packet.has_payload:
                self.stats.payload_packet_count += 1
                self.stats.total_payload_bytes += len(packet.payload)
            if packet.has_adaptation_field:
                self.stats.adaptation_field_count += 1
                if packet.has_payload:
                    self.stats.adaptation_and_payload_count += 1
                else:
                    self.stats.adaptation_only_count += 1

            self.stats.pid_counts[packet.pid] += 1
            self._track_continuity(packet)

            packets_processed += 1
            yield packet

    def parse_file(
        self,
        file_path: Union[str, Path],
        max_packets: Optional[int] = None
    ) -> Iterator[TSPacket]:
        """
        Opens and decodes a TS file from disk.

        Args:
            file_path: Path to the .ts file.
            max_packets: Optional maximum number of packets to decode.

        Yields:
            TSPacket instances.
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"TS stream file not found: {path}")

        logger.info("Starting MPEG-TS parsing for %s", path.name)
        with open(path, "rb") as f:
            yield from self.parse_stream(f, max_packets=max_packets)
        logger.info("Finished MPEG-TS parsing for %s (%d packets)", path.name, self.stats.total_packets)

    def get_statistics(self) -> Dict[str, Any]:
        """Returns computed stream diagnostic metrics."""
        return self.stats.to_dict()
