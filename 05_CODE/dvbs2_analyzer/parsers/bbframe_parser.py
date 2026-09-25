"""
DVB-S2 Baseband Frame (BBFrame) Parser (ETSI EN 302 307-1).

Decodes 10-byte Baseband Headers (BBHeader) and extracts Data Field payloads
from raw binary streams and PCAP / PCAP-NG satellite radio captures.
"""

from collections import defaultdict
from dataclasses import dataclass, field
import io
import logging
from pathlib import Path
import struct
from typing import Any, BinaryIO, Dict, Iterator, List, Optional, Tuple, Union

from dvbs2_analyzer.parsers.base import BaseStreamParser, PacketCorruptionError

logger = logging.getLogger(__name__)

# Precomputed CRC-8 table for polynomial 0xD5 (ETSI EN 302 307-1)
CRC8_TABLE = [
    0x00, 0xD5, 0x7F, 0xAA, 0xFE, 0x2B, 0x81, 0x54, 0x29, 0xFC, 0x56, 0x83, 0xD7, 0x02, 0xA8, 0x7D,
    0x52, 0x87, 0x2D, 0xF8, 0xAC, 0x79, 0xD3, 0x06, 0x7B, 0xAE, 0x04, 0xD1, 0x85, 0x50, 0xFA, 0x2F,
    0xA4, 0x71, 0xDB, 0x0E, 0x5A, 0x8F, 0x25, 0xF0, 0x8D, 0x58, 0xF2, 0x27, 0x73, 0xA6, 0x0C, 0xD9,
    0xF6, 0x23, 0x89, 0x5C, 0x08, 0xDD, 0x77, 0xA2, 0xDF, 0x0A, 0xA0, 0x75, 0x21, 0xF4, 0x5E, 0x8B,
    0x9D, 0x48, 0xE2, 0x37, 0x63, 0xB6, 0x1C, 0xC9, 0xB4, 0x61, 0xCB, 0x1E, 0x4A, 0x9F, 0x35, 0xE0,
    0xCF, 0x1A, 0xB0, 0x65, 0x31, 0xE4, 0x4E, 0x9B, 0xE6, 0x33, 0x99, 0x4C, 0x18, 0xCD, 0x67, 0xB2,
    0x39, 0xEC, 0x46, 0x93, 0xC7, 0x12, 0xB8, 0x6D, 0x10, 0xC5, 0x6F, 0xBA, 0xEE, 0x3B, 0x91, 0x44,
    0x6B, 0xBE, 0x14, 0xC1, 0x95, 0x40, 0xEA, 0x3F, 0x42, 0x97, 0x3D, 0xE8, 0xBC, 0x69, 0xC3, 0x16,
    0xEF, 0x3A, 0x90, 0x45, 0x11, 0xC4, 0x6E, 0xBB, 0xC6, 0x13, 0xB9, 0x6C, 0x38, 0xED, 0x47, 0x92,
    0xBD, 0x68, 0xC2, 0x17, 0x43, 0x96, 0x3C, 0xE9, 0x94, 0x41, 0xEB, 0x3E, 0x6A, 0xBF, 0x15, 0xC0,
    0x4B, 0x9E, 0x34, 0xE1, 0xB5, 0x60, 0xCA, 0x1F, 0x62, 0xB7, 0x1D, 0xC8, 0x9C, 0x49, 0xE3, 0x36,
    0x19, 0xCC, 0x66, 0xB3, 0xE7, 0x32, 0x98, 0x4D, 0x30, 0xE5, 0x4F, 0x9A, 0xCE, 0x1B, 0xB1, 0x64,
    0x72, 0xA7, 0x0D, 0xD8, 0x8C, 0x59, 0xF3, 0x26, 0x5B, 0x8E, 0x24, 0xF1, 0xA5, 0x70, 0xDA, 0x0F,
    0x20, 0xF5, 0x5F, 0x8A, 0xDE, 0x0B, 0xA1, 0x74, 0x09, 0xDC, 0x76, 0xA3, 0xF7, 0x22, 0x88, 0x5D,
    0xD6, 0x03, 0xA9, 0x7C, 0x28, 0xFD, 0x57, 0x82, 0xFF, 0x2A, 0x80, 0x55, 0x01, 0xD4, 0x7E, 0xAB,
    0x84, 0x51, 0xFB, 0x2E, 0x7A, 0xAF, 0x05, 0xD0, 0xAD, 0x78, 0xD2, 0x07, 0x53, 0x86, 0x2C, 0xF9
]

def crc8_dvbs2(data_bytes: bytes) -> int:
    """Computes ETSI EN 302 307-1 CRC-8 over header bytes using poly 0xD5."""
    crc = 0
    for b in data_bytes:
        crc = CRC8_TABLE[crc ^ b]
    return crc


@dataclass
class BBFrame:
    """
    Structured representation of a single DVB-S2 Baseband Frame (ETSI EN 302 307-1).
    """
    matype1: int                        # Byte 0: TS/GS, SIS/MIS, CCM/ACM, ISSYI, NPD, RO
    matype2: int                        # Byte 1: ISI if MIS, or reserved
    ts_gs: str                          # 'GENERIC_CONTINUOUS', 'GENERIC_PACKETIZED', 'GSE_HEM', 'TRANSPORT'
    is_sis: bool                        # True = Single Input Stream, False = Multiple Input Stream
    is_ccm: bool                        # True = Constant Coding & Modulation, False = ACM/VCM
    issyi: bool                         # True = Input Stream Synchronization Indicator active
    npd: bool                           # True = Null Packet Deletion active
    ro_rolloff: float                   # Roll-off factor: 0.35, 0.25, 0.20, or 0.15
    isi: Optional[int]                  # Input Stream Identifier (0..255) if MIS, else None
    upl: int                            # User Packet Length in bits (16-bit)
    dfl: int                            # Data Field Length in bits (16-bit)
    dfl_bytes: int                      # DFL in bytes (dfl // 8)
    sync: int                           # User packet sync byte (8-bit)
    syncd: int                          # Distance in bits to first user packet (16-bit)
    crc8: int                           # Extracted CRC-8 (8-bit)
    crc8_calculated: int                # Computed CRC-8 over first 9 bytes
    is_valid: bool                      # True if crc8 == crc8_calculated
    header_bytes: bytes                 # Exact 10-byte BBHeader
    payload: bytes                      # Data field payload slice
    payload_length: int                 # len(payload) in bytes
    is_truncated: bool                  # True if payload_length < dfl_bytes
    mode_adaptation_type: Optional[str] = None # 'L.1', 'L.2', 'L.3', 'L.4', or None
    frame_index: Optional[int] = None
    raw_bytes: bytes = b""             # Full frame bytes (header + payload)


@dataclass
class BBFrameStreamStatistics:
    """
    Diagnostic metrics and counters for an analyzed BBFrame stream.
    """
    total_bytes_read: int = 0
    total_frames: int = 0
    valid_frames: int = 0
    invalid_crc_frames: int = 0
    malformed_headers: int = 0
    truncated_frames: int = 0
    total_payload_bytes: int = 0
    dfl_values: List[int] = field(default_factory=list)
    upl_values: List[int] = field(default_factory=list)
    stream_type_counts: Dict[str, int] = field(default_factory=lambda: defaultdict(int))
    input_stream_mode_counts: Dict[str, int] = field(default_factory=lambda: defaultdict(int))
    coding_modulation_counts: Dict[str, int] = field(default_factory=lambda: defaultdict(int))
    roll_off_counts: Dict[str, int] = field(default_factory=lambda: defaultdict(int))
    sync_byte_counts: Dict[str, int] = field(default_factory=lambda: defaultdict(int))
    isi_counts: Dict[int, int] = field(default_factory=lambda: defaultdict(int))
    mode_adaptation_counts: Dict[str, int] = field(default_factory=lambda: defaultdict(int))

    def to_dict(self) -> Dict[str, Any]:
        """Converts statistics into a serializable dictionary."""
        mean_dfl = (sum(self.dfl_values) / len(self.dfl_values)) if self.dfl_values else 0.0
        min_dfl = min(self.dfl_values) if self.dfl_values else 0
        max_dfl = max(self.dfl_values) if self.dfl_values else 0

        mean_payload = (self.total_payload_bytes / self.valid_frames) if self.valid_frames > 0 else 0.0

        return {
            "total_bytes_read": self.total_bytes_read,
            "total_frames": self.total_frames,
            "valid_frames": self.valid_frames,
            "invalid_crc_frames": self.invalid_crc_frames,
            "malformed_headers": self.malformed_headers,
            "truncated_frames": self.truncated_frames,
            "total_payload_bytes": self.total_payload_bytes,
            "mean_payload_bytes_per_frame": round(mean_payload, 2),
            "dfl_bits_min": min_dfl,
            "dfl_bits_max": max_dfl,
            "dfl_bits_mean": round(mean_dfl, 1),
            "dfl_bytes_mean": round(mean_dfl / 8.0, 1),
            "stream_types": dict(self.stream_type_counts),
            "input_stream_modes": dict(self.input_stream_mode_counts),
            "coding_modulation_modes": dict(self.coding_modulation_counts),
            "roll_off_distribution": dict(self.roll_off_counts),
            "sync_byte_distribution": dict(self.sync_byte_counts),
            "isi_distribution": dict(self.isi_counts),
            "mode_adaptation_distribution": dict(self.mode_adaptation_counts),
        }


class BBFrameParser(BaseStreamParser):
    """
    Parser for DVB-S2 Baseband Frames (ETSI EN 302 307-1).
    Supports raw continuous binary BBFrame sequences and PCAP / PCAP-NG satellite radio captures.
    """

    def __init__(self, strict_mode: bool = False):
        """
        Initializes the BBFrame Parser.

        Args:
            strict_mode: If True, raises exceptions immediately on malformed headers / CRC errors;
                         if False, logs and records corruptions in statistics.
        """
        self.strict_mode = strict_mode
        self.stats = BBFrameStreamStatistics()

    def reset_statistics(self) -> None:
        """Resets all internal frame counters and diagnostic statistics."""
        self.stats = BBFrameStreamStatistics()

    @staticmethod
    def _decode_tsgs(tsgs_bits: int) -> str:
        """Translates 2-bit TS/GS field into standard stream type description."""
        if tsgs_bits == 0b00:
            return "GENERIC_PACKETIZED"
        elif tsgs_bits == 0b01:
            return "GENERIC_CONTINUOUS"
        elif tsgs_bits == 0b10:
            return "GSE_HEM"
        elif tsgs_bits == 0b11:
            return "TRANSPORT"
        return "RESERVED"

    @staticmethod
    def _decode_rolloff(ro_bits: int) -> float:
        """Translates 2-bit Roll-off field into numeric factor alpha."""
        if ro_bits == 0b00:
            return 0.35
        elif ro_bits == 0b01:
            return 0.25
        elif ro_bits == 0b10:
            return 0.20
        else:
            return 0.15

    def parse_frame(
        self,
        raw_buffer: bytes,
        offset: int = 0,
        frame_index: Optional[int] = None,
        mode_adaptation: Optional[str] = None
    ) -> Tuple[BBFrame, int]:
        """
        Parses exactly one DVB-S2 Baseband Frame starting at `offset` in `raw_buffer`.

        Args:
            raw_buffer: Byte sequence containing the frame.
            offset: Byte offset where the 10-byte BBHeader begins.
            frame_index: Optional sequence number.
            mode_adaptation: Mode adaptation type if extracted from UDP wrapper.

        Returns:
            Tuple of (BBFrame, total_bytes_consumed).

        Raises:
            PacketCorruptionError: If header is incomplete or corrupted in strict mode.
        """
        avail = len(raw_buffer) - offset
        if avail < 10:
            raise PacketCorruptionError(
                f"Insufficient bytes for DVB-S2 BBHeader: {avail} bytes available, min 10 required"
            )

        header_bytes = raw_buffer[offset : offset + 10]
        matype1, matype2 = header_bytes[0], header_bytes[1]
        upl, dfl, sync, syncd, crc8 = struct.unpack(">HHBHB", header_bytes[2:10])

        crc8_calc = crc8_dvbs2(header_bytes[:9])
        is_crc_valid = (crc8 == crc8_calc)

        if not is_crc_valid and self.strict_mode:
            raise PacketCorruptionError(
                f"Invalid BBHeader CRC-8: expected 0x{crc8_calc:02x}, got 0x{crc8:02x}"
            )

        # Decode MATYPE-1 fields
        tsgs_bits = (matype1 & 0xC0) >> 6
        ts_gs = self._decode_tsgs(tsgs_bits)
        is_sis = bool(matype1 & 0x20)
        is_ccm = bool(matype1 & 0x10)
        issyi = bool(matype1 & 0x08)
        npd = bool(matype1 & 0x04)
        ro_rolloff = self._decode_rolloff(matype1 & 0x03)

        # MATYPE-2: ISI if MIS
        isi = matype2 if not is_sis else None

        dfl_bytes = dfl // 8
        avail_payload = len(raw_buffer) - (offset + 10)

        if avail_payload < dfl_bytes:
            is_truncated = True
            payload = raw_buffer[offset + 10 : offset + 10 + avail_payload]
            consumed = 10 + avail_payload
            if self.strict_mode:
                raise PacketCorruptionError(
                    f"Truncated BBFrame: requires {dfl_bytes} payload bytes, but only {avail_payload} available"
                )
        else:
            is_truncated = False
            payload = raw_buffer[offset + 10 : offset + 10 + dfl_bytes]
            consumed = 10 + dfl_bytes

        raw_slice = raw_buffer[offset : offset + consumed]

        frame = BBFrame(
            matype1=matype1,
            matype2=matype2,
            ts_gs=ts_gs,
            is_sis=is_sis,
            is_ccm=is_ccm,
            issyi=issyi,
            npd=npd,
            ro_rolloff=ro_rolloff,
            isi=isi,
            upl=upl,
            dfl=dfl,
            dfl_bytes=dfl_bytes,
            sync=sync,
            syncd=syncd,
            crc8=crc8,
            crc8_calculated=crc8_calc,
            is_valid=is_crc_valid,
            header_bytes=header_bytes,
            payload=payload,
            payload_length=len(payload),
            is_truncated=is_truncated,
            mode_adaptation_type=mode_adaptation,
            frame_index=frame_index,
            raw_bytes=raw_slice,
        )

        return frame, consumed

    def _update_statistics(self, frame: BBFrame) -> None:
        """Updates diagnostic counters with the parsed frame."""
        self.stats.total_frames += 1

        if frame.is_valid:
            self.stats.valid_frames += 1
        else:
            self.stats.invalid_crc_frames += 1

        if frame.is_truncated:
            self.stats.truncated_frames += 1

        self.stats.total_payload_bytes += frame.payload_length
        self.stats.dfl_values.append(frame.dfl)
        self.stats.upl_values.append(frame.upl)

        self.stats.stream_type_counts[frame.ts_gs] += 1
        self.stats.input_stream_mode_counts["SIS" if frame.is_sis else "MIS"] += 1
        self.stats.coding_modulation_counts["CCM" if frame.is_ccm else "ACM"] += 1
        self.stats.roll_off_counts[f"alpha={frame.ro_rolloff}"] += 1
        self.stats.sync_byte_counts[f"0x{frame.sync:02x}"] += 1

        if frame.isi is not None:
            self.stats.isi_counts[frame.isi] += 1

        if frame.mode_adaptation_type:
            self.stats.mode_adaptation_counts[frame.mode_adaptation_type] += 1

    def _stream_from_pcapng(
        self,
        stream_io: BinaryIO,
        max_frames: Optional[int] = None
    ) -> Iterator[BBFrame]:
        """Streams BBFrames encapsulated within PCAP-NG blocks (e.g. over UDP port 51000)."""
        frames_yielded = 0

        while True:
            if max_frames is not None and frames_yielded >= max_frames:
                break

            hdr = stream_io.read(8)
            if len(hdr) < 8:
                break

            b_type, b_len = struct.unpack("<II", hdr)
            if b_len < 12:
                break

            body = stream_io.read(b_len - 12)
            stream_io.read(4) # Block Total Length trailer

            pkt_data: Optional[bytes] = None
            if b_type == 0x00000006 and len(body) >= 20: # Enhanced Packet Block
                cap_len = struct.unpack("<I", body[12:16])[0]
                pkt_data = body[20 : 20 + cap_len]
            elif b_type == 0x00000003 and len(body) >= 4: # Simple Packet Block
                orig_len = struct.unpack("<I", body[:4])[0]
                cap_len = min(orig_len, b_len - 16)
                pkt_data = body[4 : 4 + cap_len]

            if not pkt_data or len(pkt_data) < 14:
                continue

            # Extract UDP payload from Ethernet/IP packet if present
            payload: bytes = pkt_data
            if pkt_data[12:14] == b"\x08\x00" and len(pkt_data) >= 34: # IPv4
                ip_proto = pkt_data[23]
                ihl = (pkt_data[14] & 0x0F) * 4
                if ip_proto == 17 and len(pkt_data) >= 14 + ihl + 8: # UDP
                    payload = pkt_data[14 + ihl + 8 :]
                else:
                    continue
            elif len(pkt_data) < 10:
                continue

            if len(payload) < 10:
                continue

            # Check SatLabs Mode Adaptation Header
            ma_offset = 0
            ma_type: Optional[str] = None
            if len(payload) >= 14 and payload[0] == 0xB8:
                # Type L.3 (4 bytes)
                if crc8_dvbs2(payload[4:13]) == payload[13]:
                    ma_offset = 4
                    ma_type = "L.3 (4B)"
                # Type L.2 (2 bytes)
                elif crc8_dvbs2(payload[2:11]) == payload[11]:
                    ma_offset = 2
                    ma_type = "L.2 (2B)"
                # Type L.4 (3 bytes)
                elif len(payload) >= 13 and crc8_dvbs2(payload[3:12]) == payload[12]:
                    ma_offset = 3
                    ma_type = "L.4 (3B)"
                else:
                    continue
            else:
                if crc8_dvbs2(payload[:9]) != payload[9]:
                    continue

            try:
                frame, _ = self.parse_frame(
                    payload,
                    offset=ma_offset,
                    frame_index=frames_yielded + 1,
                    mode_adaptation=ma_type
                )
            except PacketCorruptionError as err:
                self.stats.malformed_headers += 1
                if self.strict_mode:
                    raise
                logger.warning("BBFrame parse error in PCAP-NG: %s", err)
                continue

            self._update_statistics(frame)
            frames_yielded += 1
            yield frame

    def _stream_from_pcap(
        self,
        stream_io: BinaryIO,
        magic: bytes,
        max_frames: Optional[int] = None
    ) -> Iterator[BBFrame]:
        """Streams BBFrames from classic PCAP file format."""
        endian = "<" if magic == b"\xd4\xc3\xb2\xa1" else ">"
        stream_io.read(20) # Skip remaining global header bytes

        frames_yielded = 0
        while True:
            if max_frames is not None and frames_yielded >= max_frames:
                break

            pkt_hdr = stream_io.read(16)
            if len(pkt_hdr) < 16:
                break

            ts_sec, ts_usec, incl_len, orig_len = struct.unpack(endian + "IIII", pkt_hdr)
            pkt_data = stream_io.read(incl_len)
            if len(pkt_data) < 10:
                continue

            payload: bytes = pkt_data
            if len(pkt_data) >= 34 and pkt_data[12:14] == b"\x08\x00":
                ip_proto = pkt_data[23]
                ihl = (pkt_data[14] & 0x0F) * 4
                if ip_proto == 17 and len(pkt_data) >= 14 + ihl + 8:
                    payload = pkt_data[14 + ihl + 8 :]

            if len(payload) < 10:
                continue

            ma_offset = 0
            ma_type: Optional[str] = None
            if len(payload) >= 14 and payload[0] == 0xB8:
                if crc8_dvbs2(payload[4:13]) == payload[13]:
                    ma_offset = 4
                    ma_type = "L.3 (4B)"
                elif crc8_dvbs2(payload[2:11]) == payload[11]:
                    ma_offset = 2
                    ma_type = "L.2 (2B)"

            try:
                frame, _ = self.parse_frame(
                    payload,
                    offset=ma_offset,
                    frame_index=frames_yielded + 1,
                    mode_adaptation=ma_type
                )
            except PacketCorruptionError as err:
                self.stats.malformed_headers += 1
                if self.strict_mode:
                    raise
                logger.warning("BBFrame parse error in PCAP: %s", err)
                continue

            self._update_statistics(frame)
            frames_yielded += 1
            yield frame

    def _stream_from_raw(
        self,
        stream_io: BinaryIO,
        initial_data: bytes,
        max_frames: Optional[int] = None
    ) -> Iterator[BBFrame]:
        """Streams consecutive BBFrames from a raw continuous binary stream."""
        remaining_data = stream_io.read()
        data = initial_data + remaining_data
        self.stats.total_bytes_read = len(data)

        if not data:
            return

        # Find initial frame synchronization offset
        sync_offset: Optional[int] = None
        for off in range(len(data) - 10):
            hdr = data[off : off + 10]
            if (hdr[0] & 0xC0) in (0x00, 0x40, 0xC0) and crc8_dvbs2(hdr[:9]) == hdr[9]:
                dfl = (hdr[4] << 8) | hdr[5]
                next_off = off + 10 + (dfl // 8)
                if next_off + 10 <= len(data):
                    next_hdr = data[next_off : next_off + 10]
                    if (next_hdr[0] & 0xC0) in (0x00, 0x40, 0xC0) and crc8_dvbs2(next_hdr[:9]) == next_hdr[9]:
                        sync_offset = off
                        break
                elif next_off <= len(data) + 1024:
                    sync_offset = off
                    break

        if sync_offset is None:
            # Fallback: scan for first valid CRC8 header
            for off in range(len(data) - 10):
                hdr = data[off : off + 10]
                if crc8_dvbs2(hdr[:9]) == hdr[9]:
                    sync_offset = off
                    break

        if sync_offset is None:
            sync_offset = 0

        curr_offset = sync_offset
        frames_yielded = 0

        while curr_offset + 10 <= len(data):
            if max_frames is not None and frames_yielded >= max_frames:
                break

            try:
                frame, consumed = self.parse_frame(
                    data,
                    offset=curr_offset,
                    frame_index=frames_yielded + 1
                )
            except PacketCorruptionError as err:
                self.stats.malformed_headers += 1
                if self.strict_mode:
                    raise
                logger.warning("BBFrame parse error at offset %d: %s", curr_offset, err)
                # Advance 1 byte to re-synchronize
                curr_offset += 1
                continue

            self._update_statistics(frame)
            frames_yielded += 1
            yield frame

            if consumed == 0:
                break

            curr_offset += consumed

    def parse_stream(
        self,
        stream_io: BinaryIO,
        max_frames: Optional[int] = None
    ) -> Iterator[BBFrame]:
        """
        Parses a stream of DVB-S2 Baseband Frames from a binary reader.
        Handles both PCAP/PCAP-NG captures and raw continuous BBFrame sequences.

        Args:
            stream_io: Binary stream to read from.
            max_frames: Optional upper limit on frames to yield.

        Yields:
            Decoded BBFrame objects.
        """
        magic = stream_io.read(4)
        if len(magic) < 4:
            return

        if magic == b"\x0a\x0d\x0d\x0a": # PCAP-NG
            if hasattr(stream_io, "seek") and stream_io.seekable():
                stream_io.seek(0)
            yield from self._stream_from_pcapng(stream_io, max_frames=max_frames)
        elif magic in (b"\xa1\xb2\xc3\xd4", b"\xd4\xc3\xb2\xa1"): # Classic PCAP
            if hasattr(stream_io, "seek") and stream_io.seekable():
                stream_io.seek(0)
            yield from self._stream_from_pcap(stream_io, magic, max_frames=max_frames)
        else: # Raw continuous BBFrame stream
            yield from self._stream_from_raw(stream_io, magic, max_frames=max_frames)

    def parse_file(
        self,
        file_path: Union[str, Path],
        max_packets: Optional[int] = None
    ) -> Iterator[BBFrame]:
        """
        Parses a BBFrame stream file from disk.

        Args:
            file_path: Path to the BBFrame / PCAP file.
            max_packets: Optional limit on the number of frames to decode.

        Yields:
            BBFrame instances.
        """
        path = Path(file_path).resolve()
        if not path.exists():
            raise FileNotFoundError(f"BBFrame file not found: {path}")

        self.stats.total_bytes_read = path.stat().st_size
        logger.info("Starting BBFrame parsing for %s (%d bytes)", path.name, self.stats.total_bytes_read)

        with open(path, "rb") as f:
            yield from self.parse_stream(f, max_frames=max_packets)

        logger.info(
            "Finished BBFrame parsing for %s: %d frames decoded (%d valid)",
            path.name,
            self.stats.total_frames,
            self.stats.valid_frames
        )

    def get_statistics(self) -> Dict[str, Any]:
        """Returns accumulated stream diagnostic metrics."""
        return self.stats.to_dict()