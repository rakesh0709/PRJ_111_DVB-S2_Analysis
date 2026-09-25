"""
Unit and Integration Tests for GSEParser (PRJ_111).

Compliant with ETSI TS 102 606-1:
  - Valid single GSE PDU decoding
  - Start (S) and End (E) fragmentation flags
  - Label Type (LT) decoding (6-byte, 3-byte, None, Re-use)
  - Protocol Type resolution (IPv4, IPv6, NPA extension, EtherType)
  - Payload extraction & boundary validation
  - Multiple PDUs in a contiguous stream
  - Truncated and malformed PDU error detection
  - Padding packet handling
  - Encapsulated IPv4 payload detection
  - Real dataset integration on 01_RAW_DATA/02_GSE/GSExtract/sample.ts
"""

import io
from pathlib import Path
import struct
from typing import Optional
import unittest

from dvbs2_analyzer.config import RAW_DATA_DIR, StreamFormat
from dvbs2_analyzer.ingestion.stream_handler import StreamHandler
from dvbs2_analyzer.parsers.base import PacketCorruptionError
from dvbs2_analyzer.parsers.gse_parser import (
    GSEFragType,
    GSELabelType,
    GSEPDU,
    GSEParser,
    GSEStreamStatistics,
    GSE_PROTO_IPV4,
    GSE_PROTO_IPV6,
    GSE_PROTO_NPA_EXT,
)


def make_gse_pdu(
    s: int = 1,
    e: int = 1,
    lt: int = 2,  # LABEL_NONE (0 bytes)
    frag_id: Optional[int] = None,
    total_length: Optional[int] = None,
    protocol_type: Optional[int] = GSE_PROTO_IPV4,
    label: bytes = b"",
    payload: bytes = b"TEST_PAYLOAD_DATA_12345",
    crc32: Optional[int] = None,
) -> bytes:
    """Helper to construct an ETSI TS 102 606-1 compliant GSE PDU for testing."""
    is_unfrag = (s == 1 and e == 1)
    is_first = (s == 1 and e == 0)
    is_last = (s == 0 and e == 1)

    frag_id_bytes = bytes([frag_id & 0xFF]) if (not is_unfrag and frag_id is not None) else (b"\x00" if not is_unfrag else b"")
    total_len_bytes = struct.pack(">H", total_length) if (is_first and total_length is not None) else (b"\x00\x00" if is_first else b"")
    proto_bytes = struct.pack(">H", protocol_type) if (s == 1 and protocol_type is not None) else b""

    # Adjust label according to LT
    if s == 1:
        if lt == 0:  # 6 bytes
            label_bytes = (label + b"\x00" * 6)[:6]
        elif lt == 1:  # 3 bytes
            label_bytes = (label + b"\x00" * 3)[:3]
        else:
            label_bytes = b""
    else:
        label_bytes = b""

    crc_bytes = struct.pack(">I", crc32) if (is_last and crc32 is not None) else b""

    body = frag_id_bytes + total_len_bytes + proto_bytes + label_bytes + payload + crc_bytes
    gse_length = len(body)

    b0 = ((s & 0x01) << 7) | ((e & 0x01) << 6) | ((lt & 0x03) << 4) | ((gse_length >> 8) & 0x0F)
    b1 = gse_length & 0xFF

    return bytes([b0, b1]) + body


def make_ipv4_payload(src_ip="192.168.1.1", dst_ip="192.168.1.2", payload_data=b"HELLO") -> bytes:
    """Creates a basic valid IPv4 UDP packet for payload testing."""
    version_ihl = 0x45
    dscp = 0x00
    total_len = 20 + 8 + len(payload_data)
    ident = 0x1234
    flags_frag = 0x4000
    ttl = 64
    proto = 17  # UDP
    chk = 0x0000
    src = bytes(map(int, src_ip.split(".")))
    dst = bytes(map(int, dst_ip.split(".")))

    ip_hdr = struct.pack(">BBHHHBBH4s4s", version_ihl, dscp, total_len, ident, flags_frag, ttl, proto, chk, src, dst)
    udp_hdr = struct.pack(">HHHH", 5000, 6000, 8 + len(payload_data), 0)
    return ip_hdr + udp_hdr + payload_data


class TestGSEParser(unittest.TestCase):
    """Unit test suite for GSEParser according to ETSI TS 102 606-1."""

    def setUp(self):
        self.parser = GSEParser(strict_mode=True)

    def test_valid_unfragmented_pdu_no_label(self):
        raw = make_gse_pdu(s=1, e=1, lt=2, protocol_type=GSE_PROTO_IPV4, payload=b"MY_TEST_PAYLOAD")
        pdu, consumed = self.parser.parse_pdu(raw)

        self.assertEqual(consumed, len(raw))
        self.assertTrue(pdu.start_indicator)
        self.assertTrue(pdu.end_indicator)
        self.assertTrue(pdu.is_unfragmented)
        self.assertFalse(pdu.is_first_fragment)
        self.assertFalse(pdu.is_last_fragment)
        self.assertFalse(pdu.is_padding)
        self.assertEqual(pdu.label_type, GSELabelType.LABEL_NONE)
        self.assertEqual(pdu.protocol_type, GSE_PROTO_IPV4)
        self.assertEqual(pdu.protocol_name, "IPv4")
        self.assertEqual(pdu.label, b"")
        self.assertEqual(pdu.payload, b"MY_TEST_PAYLOAD")
        self.assertEqual(pdu.payload_length, len(b"MY_TEST_PAYLOAD"))

    def test_start_and_end_fragmentation_flags(self):
        # 1. First fragment: S=1, E=0
        raw_first = make_gse_pdu(s=1, e=0, frag_id=42, total_length=1500, protocol_type=GSE_PROTO_IPV6, payload=b"CHUNK_1")
        pdu_first, _ = self.parser.parse_pdu(raw_first)
        self.assertTrue(pdu_first.is_first_fragment)
        self.assertFalse(pdu_first.is_unfragmented)
        self.assertEqual(pdu_first.frag_id, 42)
        self.assertEqual(pdu_first.total_length, 1500)
        self.assertEqual(pdu_first.protocol_name, "IPv6")

        # 2. Intermediate fragment: S=0, E=0
        raw_mid = make_gse_pdu(s=0, e=0, frag_id=42, protocol_type=None, payload=b"CHUNK_2")
        pdu_mid, _ = self.parser.parse_pdu(raw_mid)
        self.assertTrue(pdu_mid.is_intermediate_fragment)
        self.assertEqual(pdu_mid.frag_id, 42)
        self.assertIsNone(pdu_mid.protocol_type)

        # 3. Last fragment: S=0, E=1 with CRC-32
        raw_last = make_gse_pdu(s=0, e=1, frag_id=42, protocol_type=None, payload=b"CHUNK_3", crc32=0xAABBCCDD)
        pdu_last, _ = self.parser.parse_pdu(raw_last)
        self.assertTrue(pdu_last.is_last_fragment)
        self.assertEqual(pdu_last.frag_id, 42)
        self.assertEqual(pdu_last.crc32, 0xAABBCCDD)
        self.assertEqual(pdu_last.payload, b"CHUNK_3")

    def test_label_types(self):
        # LT=0: 6-byte MAC label
        raw_6b = make_gse_pdu(lt=0, label=b"\x00\x11\x22\x33\x44\x55")
        pdu_6b, _ = self.parser.parse_pdu(raw_6b)
        self.assertEqual(pdu_6b.label_type, GSELabelType.LABEL_6B)
        self.assertEqual(pdu_6b.label, b"\x00\x11\x22\x33\x44\x55")

        # LT=1: 3-byte label
        raw_3b = make_gse_pdu(lt=1, label=b"\xAA\xBB\xCC")
        pdu_3b, _ = self.parser.parse_pdu(raw_3b)
        self.assertEqual(pdu_3b.label_type, GSELabelType.LABEL_3B)
        self.assertEqual(pdu_3b.label, b"\xAA\xBB\xCC")

        # LT=3: Label re-use (0 bytes)
        raw_reuse = make_gse_pdu(lt=3)
        pdu_reuse, _ = self.parser.parse_pdu(raw_reuse)
        self.assertEqual(pdu_reuse.label_type, GSELabelType.LABEL_REUSE)
        self.assertEqual(pdu_reuse.label, b"")

    def test_protocol_type_resolution(self):
        self.assertEqual(self.parser._resolve_protocol_name(GSE_PROTO_IPV4), "IPv4")
        self.assertEqual(self.parser._resolve_protocol_name(GSE_PROTO_IPV6), "IPv6")
        self.assertEqual(self.parser._resolve_protocol_name(GSE_PROTO_NPA_EXT), "GSE_EXT_NPA")
        self.assertEqual(self.parser._resolve_protocol_name(0x0001), "GSE_EXT_0x0001")
        self.assertEqual(self.parser._resolve_protocol_name(0x8847), "MPLS_UNICAST")
        self.assertEqual(self.parser._resolve_protocol_name(0x1234), "0x1234")

    def test_ipv4_payload_identification(self):
        ip_data = make_ipv4_payload(payload_data=b"PACKET_CONTENT")
        raw = make_gse_pdu(protocol_type=GSE_PROTO_IPV4, payload=ip_data)
        pdu, _ = self.parser.parse_pdu(raw)
        self.assertEqual(pdu.encapsulated_protocol, "IPv4")

    def test_padding_packet(self):
        padding_bytes = bytes([0x00, 0x00])
        pdu, consumed = self.parser.parse_pdu(padding_bytes)
        self.assertTrue(pdu.is_padding)
        self.assertEqual(pdu.payload_length, 0)
        self.assertEqual(consumed, 2)

    def test_multiple_pdus_in_stream(self):
        p1 = make_gse_pdu(s=1, e=1, payload=b"FIRST")
        p2 = make_gse_pdu(s=1, e=0, frag_id=1, total_length=50, payload=b"SECOND_PART1")
        p3 = make_gse_pdu(s=0, e=1, frag_id=1, payload=b"SECOND_PART2", crc32=0x12345678)

        stream = io.BytesIO(p1 + p2 + p3)
        pdus = list(self.parser.parse_stream(stream))

        self.assertEqual(len(pdus), 3)
        self.assertEqual(pdus[0].payload, b"FIRST")
        self.assertEqual(pdus[1].payload, b"SECOND_PART1")
        self.assertEqual(pdus[2].payload, b"SECOND_PART2")

        stats = self.parser.get_statistics()
        self.assertEqual(stats["valid_pdus"], 3)
        self.assertEqual(stats["unfragmented_pdus"], 1)
        self.assertEqual(stats["first_fragments"], 1)
        self.assertEqual(stats["last_fragments"], 1)

    def test_truncated_pdu_error(self):
        # Declare gse_length = 30, but provide only 10 bytes
        raw = bytes([0xC0, 0x1E]) + (b"\x00" * 8)
        with self.assertRaises(PacketCorruptionError):
            self.parser.parse_pdu(raw)

    def test_insufficient_bytes_error(self):
        raw = b"\xC0"
        with self.assertRaises(PacketCorruptionError):
            self.parser.parse_pdu(raw)

    def test_stream_handler_gse_instantiation(self):
        gse_file = RAW_DATA_DIR / "02_GSE" / "GSExtract" / "sample.ts"
        self.assertTrue(gse_file.exists())

        handler = StreamHandler(gse_file, forced_format=StreamFormat.GSE)
        info = handler.get_stream_info()

        self.assertEqual(info.detected_format, StreamFormat.GSE)
        self.assertTrue(info.is_valid)

        parser = handler.get_parser()
        self.assertIsInstance(parser, GSEParser)

    def test_real_gsextract_sample_dataset(self):
        gse_file = RAW_DATA_DIR / "02_GSE" / "GSExtract" / "sample.ts"
        self.assertTrue(gse_file.exists())

        parser = GSEParser(strict_mode=False)
        pdus = list(parser.parse_file(gse_file))

        self.assertGreater(len(pdus), 0)
        stats = parser.get_statistics()

        self.assertEqual(stats["total_pdus"], len(pdus))
        self.assertEqual(stats["valid_pdus"], 14)
        self.assertEqual(stats["malformed_pdus"], 0)
        self.assertEqual(stats["truncated_pdus"], 1)
        self.assertEqual(stats["unfragmented_pdus"], 6)
        self.assertEqual(stats["first_fragments"], 5)
        self.assertEqual(stats["last_fragments"], 3)
        self.assertEqual(stats["total_payload_bytes"], 8764)

        # Confirm protocol decoding
        self.assertEqual(stats["protocol_type_distribution"].get("GSE_EXT_NPA"), 11)
        # Confirm IPv4 payload recovery
        self.assertEqual(stats["encapsulated_protocol_distribution"].get("IPv4"), 9)


if __name__ == "__main__":
    unittest.main()
