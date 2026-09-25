"""
Generic Stream Encapsulation (GSE) Parser for PRJ_111.

Compliant with ETSI TS 102 606-1 specification.
Provides parsing of GSE PDU headers, fragment reassembly tracking, label extraction,
protocol identification (EtherType, IPv4/IPv6, GSE extension headers), payload boundary
validation, and stream-level GSE diagnostics.
"""

from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum, IntEnum
import logging
from pathlib import Path
import struct
from typing import Any, BinaryIO, Dict, Iterator, List, Optional, Tuple, Union

from dvbs2_analyzer.parsers.base import (
    BaseStreamParser,
    PacketCorruptionError,
    StreamParserError,
)

logger = logging.getLogger(__name__)


# -----------------------------------------------------------------------------
# GSE Protocol Enumerations & Constants (ETSI TS 102 606-1)
# -----------------------------------------------------------------------------
class GSELabelType(IntEnum):
    """GSE Label Type Indicator (LT field, 2 bits)."""
    LABEL_6B = 0b00      # 6-byte MAC address / 48-bit label
    LABEL_3B = 0b01      # 3-byte label (24-bit)
    LABEL_NONE = 0b10    # Broadcast / No label (0 bytes)
    LABEL_REUSE = 0b11   # Label re-use (0 bytes)


class GSEFragType(str, Enum):
    """GSE Fragmentation Status (derived from S and E bits)."""
    TOTAL = "TOTAL"                  # S=1, E=1 (Unfragmented PDU)
    FIRST = "FIRST"                  # S=1, E=0 (First fragment)
    INTERMEDIATE = "INTERMEDIATE"    # S=0, E=0 (Intermediate fragment)
    LAST = "LAST"                    # S=0, E=1 (Last fragment)
    PADDING = "PADDING"              # S=0, E=0, LT=0, Len=0 (Padding packet)


# Well-known Protocol Types (EtherType / Extension Headers)
GSE_PROTO_IPV4 = 0x0800
GSE_PROTO_IPV6 = 0x86DD
GSE_PROTO_MPLS_UNICAST = 0x8847
GSE_PROTO_NPA_EXT = 0x0002           # Network Point of Attachment extension header


@dataclass
class GSEPDU:
    """
    Structured representation of a single Generic Stream Encapsulation (GSE) PDU.
    """
    start_indicator: bool            # S bit: 1 = start of PDU
    end_indicator: bool              # E bit: 1 = end of PDU
    label_type: GSELabelType         # LT bits: 0, 1, 2, 3
    gse_length: int                  # 12-bit length field (bytes after length field)
    frag_id: Optional[int]           # 8-bit Frag ID (present if fragmented)
    total_length: Optional[int]      # 16-bit Total Length (present if S=1, E=0)
    protocol_type: Optional[int]     # 16-bit EtherType / Next Header (present if S=1)
    protocol_name: str               # Human-readable protocol string (e.g. 'IPv4', 'GSE_EXT_NPA')
    label: bytes                     # 6, 3, or 0 bytes label
    crc32: Optional[int]             # 32-bit CRC (present on last fragment S=0, E=1)
    payload: bytes                   # Raw PDU payload slice
    payload_length: int
    is_padding: bool
    is_unfragmented: bool            # True if S=1 and E=1
    is_first_fragment: bool          # True if S=1 and E=0
    is_intermediate_fragment: bool   # True if S=0 and E=0 (and not padding)
    is_last_fragment: bool           # True if S=0 and E=1
    encapsulated_protocol: Optional[str] # e.g. 'IPv4' if detected in payload
    raw_bytes: bytes


@dataclass
class GSEStreamStatistics:
    """
    Diagnostic metrics and counters for an analyzed GSE stream.
    """
    total_bytes_read: int = 0
    total_pdus: int = 0
    valid_pdus: int = 0
    malformed_pdus: int = 0
    truncated_pdus: int = 0
    padding_packets: int = 0
    unfragmented_pdus: int = 0
    first_fragments: int = 0
    intermediate_fragments: int = 0
    last_fragments: int = 0
    total_payload_bytes: int = 0
    protocol_type_counts: Dict[str, int] = field(default_factory=lambda: defaultdict(int))
    encapsulated_protocols: Dict[str, int] = field(default_factory=lambda: defaultdict(int))
    label_type_counts: Dict[str, int] = field(default_factory=lambda: defaultdict(int))

    def to_dict(self) -> Dict[str, Any]:
        """Converts statistics into a serializable dictionary."""
        total = self.total_pdus
        valid = self.valid_pdus
        mean_payload = (self.total_payload_bytes / valid) if valid > 0 else 0.0
        frag_count = self.first_fragments + self.intermediate_fragments + self.last_fragments

        return {
            "total_bytes_read": self.total_bytes_read,
            "total_pdus": total,
            "valid_pdus": valid,
            "malformed_pdus": self.malformed_pdus,
            "truncated_pdus": self.truncated_pdus,
            "padding_packets": self.padding_packets,
            "unfragmented_pdus": self.unfragmented_pdus,
            "fragmented_pdus_total": frag_count,
            "first_fragments": self.first_fragments,
            "intermediate_fragments": self.intermediate_fragments,
            "last_fragments": self.last_fragments,
            "total_payload_bytes": self.total_payload_bytes,
            "mean_payload_bytes_per_pdu": round(mean_payload, 2),
            "protocol_type_distribution": dict(self.protocol_type_counts),
            "encapsulated_protocol_distribution": dict(self.encapsulated_protocols),
            "label_type_distribution": dict(self.label_type_counts),
        }


class GSEParser(BaseStreamParser):
    """
    Parser for Generic Stream Encapsulation (GSE) streams under ETSI TS 102 606-1.
    Supports both direct GSE byte streams and GSE streams encapsulated within
    DVB-S2 Baseband (BB) Frames.
    """

    def __init__(
        self,
        strict_mode: bool = False,
        length_includes_header: Optional[bool] = None
    ):
        """
        Initializes the GSE Parser.

        Args:
            strict_mode: If True, raises exceptions immediately on malformed PDUs;
                         if False, records malformed count and continues.
            length_includes_header: If True, gse_length encodes the total PDU size (including 2-byte header);
                                    if False, follows standard ETSI TS 102 606-1 (length after header);
                                    if None, auto-detected from the stream or PDU buffer.
        """
        self.strict_mode = strict_mode
        self.length_includes_header = length_includes_header
        self.stats = GSEStreamStatistics()

    def reset_statistics(self) -> None:
        """Resets all internal PDU counters and stats."""
        self.stats = GSEStreamStatistics()

    @staticmethod
    def _resolve_protocol_name(proto_type: Optional[int]) -> str:
        """Translates numerical EtherType or Next Header into standard name."""
        if proto_type is None:
            return "NONE"
        if proto_type == GSE_PROTO_IPV4:
            return "IPv4"
        if proto_type == GSE_PROTO_IPV6:
            return "IPv6"
        if proto_type == GSE_PROTO_MPLS_UNICAST:
            return "MPLS_UNICAST"
        if proto_type == GSE_PROTO_NPA_EXT:
            return "GSE_EXT_NPA"
        if proto_type <= 0x0600:
            return f"GSE_EXT_0x{proto_type:04x}"
        return f"0x{proto_type:04x}"

    @staticmethod
    def _detect_encapsulated_protocol(payload: bytes) -> Optional[str]:
        """
        Scans initial payload bytes for encapsulated network protocol headers
        (e.g., IPv4 or IPv6 packets within standard payload or following extension headers).
        """
        if len(payload) < 20:
            return None

        # Check direct or slightly offset IPv4 header (Version=4, IHL>=5)
        for offset in range(min(12, len(payload) - 20)):
            b0, b1 = payload[offset], payload[offset + 1]
            if (b0 & 0xF0) == 0x40 and (b0 & 0x0F) >= 5:
                tot_len = (payload[offset + 2] << 8) | payload[offset + 3]
                if 20 <= tot_len <= len(payload) - offset + 65535:
                    return "IPv4"

        # Check IPv6 header (Version=6, Next Header valid)
        for offset in range(min(12, len(payload) - 40)):
            b0 = payload[offset]
            if (b0 & 0xF0) == 0x60:
                payload_len = (payload[offset + 4] << 8) | payload[offset + 5]
                next_hdr = payload[offset + 6]
                if next_hdr in (6, 17, 58, 0, 43, 44, 50, 51) and payload_len <= len(payload):
                    return "IPv6"

        return None

    def parse_pdu(
        self,
        raw_buffer: bytes,
        offset: int = 0,
        length_includes_header: Optional[bool] = None,
    ) -> Tuple[GSEPDU, int]:
        """
        Parses exactly one GSE PDU from `raw_buffer` beginning at `offset`.

        Args:
            raw_buffer: Byte sequence containing one or more GSE packets.
            offset: Byte index where the GSE PDU begins.
            length_includes_header: Override header length calculation mode.

        Returns:
            Tuple of (GSEPDU dataclass, bytes_consumed).

        Raises:
            PacketCorruptionError: If length or header violates ETSI TS 102 606-1.
        """
        avail = len(raw_buffer) - offset
        if avail < 2:
            raise PacketCorruptionError(f"Insufficient bytes for GSE header: {avail} bytes available, min 2 required")

        b0, b1 = raw_buffer[offset], raw_buffer[offset + 1]
        start_ind = bool(b0 & 0x80)
        end_ind = bool(b0 & 0x40)
        lt_val = (b0 & 0x30) >> 4
        label_type = GSELabelType(lt_val)
        gse_length = ((b0 & 0x0F) << 8) | b1

        # Check for GSE Padding Packet (ETSI TS 102 606-1 Section 4.2.6)
        if not start_ind and not end_ind and lt_val == 0 and (b0 & 0x0F) == 0:
            padding_pdu = GSEPDU(
                start_indicator=False,
                end_indicator=False,
                label_type=label_type,
                gse_length=0,
                frag_id=None,
                total_length=None,
                protocol_type=None,
                protocol_name="PADDING",
                label=b"",
                crc32=None,
                payload=b"",
                payload_length=0,
                is_padding=True,
                is_unfragmented=False,
                is_first_fragment=False,
                is_intermediate_fragment=False,
                is_last_fragment=False,
                encapsulated_protocol=None,
                raw_bytes=raw_buffer[offset : offset + 2],
            )
            return padding_pdu, 2

        # Determine whether gse_length encodes total PDU size or bytes following the 2-byte header
        if length_includes_header is not None:
            inc_hdr = length_includes_header
        elif self.length_includes_header is not None:
            inc_hdr = self.length_includes_header
        else:
            if avail == gse_length:
                inc_hdr = True
            elif avail == 2 + gse_length:
                inc_hdr = False
            else:
                inc_hdr = False

        total_pdu_size = gse_length if inc_hdr else (2 + gse_length)
        if total_pdu_size < 2:
            raise PacketCorruptionError(f"Invalid GSE Length: {gse_length} (total PDU size {total_pdu_size} is too small)")

        if avail < total_pdu_size:
            raise PacketCorruptionError(
                f"Truncated GSE PDU: requires {total_pdu_size} bytes, but only {avail} bytes available"
            )

        pdu_slice = raw_buffer[offset : offset + total_pdu_size]
        curr = offset + 2
        pdu_end = offset + total_pdu_size

        is_unfrag = (start_ind and end_ind)
        is_first = (start_ind and not end_ind)
        is_intermediate = (not start_ind and not end_ind)
        is_last = (not start_ind and end_ind)

        # 1. Frag ID (present in all fragmented PDUs)
        frag_id: Optional[int] = None
        if not is_unfrag:
            if curr >= pdu_end:
                raise PacketCorruptionError("Missing Frag ID in fragmented GSE PDU")
            frag_id = raw_buffer[curr]
            curr += 1

        # 2. Total Length (present only in first fragment S=1, E=0)
        total_length: Optional[int] = None
        if is_first:
            if curr + 2 > pdu_end:
                raise PacketCorruptionError("Missing Total Length in first fragment GSE PDU")
            total_length = struct.unpack(">H", raw_buffer[curr : curr + 2])[0]
            curr += 2

        # 3. Protocol Type (present in start packets: S=1)
        protocol_type: Optional[int] = None
        if start_ind:
            if curr + 2 > pdu_end:
                raise PacketCorruptionError("Missing Protocol Type in GSE PDU header")
            protocol_type = struct.unpack(">H", raw_buffer[curr : curr + 2])[0]
            curr += 2

        # 4. Label (present in start packets if LT <= 1)
        label = b""
        if start_ind:
            if label_type == GSELabelType.LABEL_6B:
                label_size = 6
            elif label_type == GSELabelType.LABEL_3B:
                label_size = 3
            else:
                label_size = 0

            if label_size > 0:
                if curr + label_size > pdu_end:
                    raise PacketCorruptionError(f"Truncated Label field: expected {label_size} bytes")
                label = raw_buffer[curr : curr + label_size]
                curr += label_size

        # 5. CRC-32 (present on last fragment S=0, E=1)
        crc32: Optional[int] = None
        payload_end = pdu_end
        if is_last:
            if payload_end - curr >= 4:
                crc32 = struct.unpack(">I", raw_buffer[payload_end - 4 : payload_end])[0]
                payload_end -= 4

        payload = raw_buffer[curr : payload_end]
        encapsulated = self._detect_encapsulated_protocol(payload)
        proto_name = self._resolve_protocol_name(protocol_type)

        pdu = GSEPDU(
            start_indicator=start_ind,
            end_indicator=end_ind,
            label_type=label_type,
            gse_length=gse_length,
            frag_id=frag_id,
            total_length=total_length,
            protocol_type=protocol_type,
            protocol_name=proto_name,
            label=label,
            crc32=crc32,
            payload=payload,
            payload_length=len(payload),
            is_padding=False,
            is_unfragmented=is_unfrag,
            is_first_fragment=is_first,
            is_intermediate_fragment=is_intermediate,
            is_last_fragment=is_last,
            encapsulated_protocol=encapsulated,
            raw_bytes=pdu_slice,
        )
        return pdu, total_pdu_size

    def _update_statistics(self, pdu: GSEPDU) -> None:
        """Updates internal stream statistics with the parsed PDU."""
        self.stats.total_pdus += 1

        if pdu.is_padding:
            self.stats.padding_packets += 1
            return

        self.stats.valid_pdus += 1
        self.stats.total_payload_bytes += pdu.payload_length

        if pdu.is_unfragmented:
            self.stats.unfragmented_pdus += 1
        elif pdu.is_first_fragment:
            self.stats.first_fragments += 1
        elif pdu.is_intermediate_fragment:
            self.stats.intermediate_fragments += 1
        elif pdu.is_last_fragment:
            self.stats.last_fragments += 1

        if pdu.protocol_type is not None:
            self.stats.protocol_type_counts[pdu.protocol_name] += 1

        if pdu.encapsulated_protocol:
            self.stats.encapsulated_protocols[pdu.encapsulated_protocol] += 1

        self.stats.label_type_counts[pdu.label_type.name] += 1

    @staticmethod
    def _crc8_dvbs2(data_bytes: bytes) -> int:
        """Computes ETSI EN 302 307 CRC-8 over header bytes (poly 0xD5)."""
        crc = 0
        poly = 0xD5
        for b in data_bytes:
            crc ^= b
            for _ in range(8):
                if crc & 0x80:
                    crc = ((crc << 1) ^ poly) & 0xFF
                else:
                    crc = (crc << 1) & 0xFF
        return crc

    @classmethod
    def _is_valid_bbheader(cls, hdr: bytes) -> bool:
        """Validates DVB-S2 Baseband Header framing and CRC-8 integrity."""
        if len(hdr) < 10:
            return False
        if (hdr[0] & 0xC0) != 0x40:  # Generic Stream (GS) mode
            return False
        return cls._crc8_dvbs2(hdr[:9]) == hdr[9]

    @staticmethod
    def _detect_bbframe_gse_mode(data_field: bytes) -> bool:
        """
        Checks whether GSE packets in BBFrame encode length inclusive of the 2-byte header.
        Returns True if inclusive mode, False otherwise.
        """
        idx = 0
        while idx < len(data_field):
            b0 = data_field[idx]
            if b0 == 0:
                break
            if idx + 2 > len(data_field):
                return False
            g_len = ((b0 & 0x0F) << 8) | data_field[idx + 1]
            if g_len == 0 or idx + g_len > len(data_field):
                return False
            idx += g_len
        return idx == len(data_field) or (idx < len(data_field) and data_field[idx] == 0)

    def parse_stream(
        self,
        stream_io: BinaryIO,
        max_pdus: Optional[int] = None
    ) -> Iterator[GSEPDU]:
        """
        Parses a stream of GSE PDUs from a binary reader.
        Handles both pure GSE PDU sequences and GSE embedded within DVB-S2 Baseband frames.

        Args:
            stream_io: Binary stream to read from.
            max_pdus: Optional maximum number of PDUs to yield.

        Yields:
            Decoded GSEPDU objects.
        """
        data = stream_io.read()
        self.stats.total_bytes_read = len(data)
        if not data:
            return

        pdus_yielded = 0

        # Check if the stream is wrapped in DVB-S2 Baseband (BB) Frames:
        has_bbframe_wrapper = False
        if len(data) > 10:
            for offset in range(min(512, len(data) - 10)):
                if self._is_valid_bbheader(data[offset : offset + 10]):
                    has_bbframe_wrapper = True
                    break

        if has_bbframe_wrapper:
            # Auto-detect header length mode from first complete BBFrame if not explicitly set
            inc_hdr_mode = self.length_includes_header
            if inc_hdr_mode is None:
                chk_off = 0
                while chk_off + 10 <= len(data):
                    hdr = data[chk_off : chk_off + 10]
                    if self._is_valid_bbheader(hdr):
                        upl, dfl, sync, syncd, crc8 = struct.unpack(">HHBHB", hdr[2:10])
                        dfl_bytes = dfl // 8
                        b_data = data[chk_off + 10 : chk_off + 10 + dfl_bytes]
                        df = b_data[:-4] if len(b_data) >= 4 else b_data
                        inc_hdr_mode = self._detect_bbframe_gse_mode(df)
                        break
                    chk_off += 1
                if inc_hdr_mode is None:
                    inc_hdr_mode = False

            # Demultiplex GSE PDUs from each verified BBFrame data field
            offset = 0
            while offset + 10 <= len(data):
                if max_pdus is not None and pdus_yielded >= max_pdus:
                    break

                hdr = data[offset : offset + 10]
                if self._is_valid_bbheader(hdr):
                    upl, dfl, sync, syncd, crc8 = struct.unpack(">HHBHB", hdr[2:10])
                    dfl_bytes = dfl // 8
                    bb_data = data[offset + 10 : min(len(data), offset + 10 + dfl_bytes)]
                    data_field = bb_data[:-4] if len(bb_data) >= 4 else bb_data

                    # Parse GSE packets within this BBFrame data field
                    p_offset = 0
                    while p_offset < len(data_field):
                        if max_pdus is not None and pdus_yielded >= max_pdus:
                            break

                        avail_field = len(data_field) - p_offset
                        if avail_field < 2:
                            if offset + 10 + dfl_bytes >= len(data):
                                self.stats.truncated_pdus += 1
                                break
                            else:
                                self.stats.malformed_pdus += 1
                                if self.strict_mode:
                                    raise PacketCorruptionError(f"Trailing {avail_field} bytes in BBFrame")
                                break

                        b0 = data_field[p_offset]
                        # Check padding packet: S=0, E=0, LT=00, and low nibble 0
                        if (b0 & 0xF0) == 0x00 and (b0 & 0x0F) == 0:
                            padding_pdu = GSEPDU(
                                start_indicator=False,
                                end_indicator=False,
                                label_type=GSELabelType.LABEL_6B,
                                gse_length=0,
                                frag_id=None,
                                total_length=None,
                                protocol_type=None,
                                protocol_name="PADDING",
                                label=b"",
                                crc32=None,
                                payload=b"",
                                payload_length=0,
                                is_padding=True,
                                is_unfragmented=False,
                                is_first_fragment=False,
                                is_intermediate_fragment=False,
                                is_last_fragment=False,
                                encapsulated_protocol=None,
                                raw_bytes=data_field[p_offset : len(data_field)],
                            )
                            self._update_statistics(padding_pdu)
                            # Padding spans to end of BBFrame data field
                            break

                        try:
                            pdu, consumed = self.parse_pdu(
                                data_field,
                                p_offset,
                                length_includes_header=inc_hdr_mode
                            )
                        except PacketCorruptionError as err:
                            if offset + 10 + dfl_bytes >= len(data):
                                self.stats.truncated_pdus += 1
                                logger.info("Stream EOF reached with partial PDU: %s", err)
                                break

                            self.stats.malformed_pdus += 1
                            if self.strict_mode:
                                raise
                            logger.warning("GSE parse error: %s", err)
                            break

                        if consumed == 0:
                            break

                        self._update_statistics(pdu)
                        pdus_yielded += 1
                        yield pdu
                        p_offset += consumed

                    offset = offset + 10 + dfl_bytes
                else:
                    offset += 1
        else:
            # Direct raw GSE PDU stream
            offset = 0
            while offset + 2 <= len(data):
                if max_pdus is not None and pdus_yielded >= max_pdus:
                    break

                try:
                    pdu, consumed = self.parse_pdu(data, offset)
                except PacketCorruptionError as err:
                    self.stats.malformed_pdus += 1
                    if self.strict_mode:
                        raise
                    logger.warning("GSE parse error at offset %d: %s", offset, err)
                    offset += 1
                    continue

                if consumed == 0:
                    break

                self._update_statistics(pdu)
                pdus_yielded += 1
                yield pdu
                offset += consumed

    def parse_file(
        self,
        file_path: Union[str, Path],
        max_packets: Optional[int] = None
    ) -> Iterator[GSEPDU]:
        """
        Parses a GSE stream file from disk.

        Args:
            file_path: Path to the GSE file.
            max_packets: Optional limit on the number of PDUs to decode.

        Yields:
            GSEPDU instances.
        """
        path = Path(file_path).resolve()
        if not path.exists():
            raise FileNotFoundError(f"GSE file not found: {path}")

        logger.info("Starting GSE parsing for %s", path.name)
        with open(path, "rb") as f:
            yield from self.parse_stream(f, max_pdus=max_packets)
        logger.info("Finished GSE parsing for %s (%d PDUs decoded)", path.name, self.stats.total_pdus)

    def get_statistics(self) -> Dict[str, Any]:
        """Returns accumulated stream diagnostic metrics."""
        return self.stats.to_dict()
