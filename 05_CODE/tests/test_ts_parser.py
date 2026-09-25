"""
Unit Tests for MPEG Transport Stream (TS) Parser in PRJ_111.

Validates ISO/IEC 13818-1 compliance:
  - 188-byte packet length validation
  - Sync byte (0x47) validation
  - 13-bit PID extraction & null packet detection
  - Header flag decoding (TEI, PUSI, Priority, TSC, AFC)
  - Continuity counter extraction & discontinuity tracking
  - Adaptation field boundary detection
  - Multi-packet file streaming on real satellite datasets
"""

import io
from pathlib import Path
import unittest

from dvbs2_analyzer.config import (
    RAW_DATA_DIR,
    TS_NULL_PID,
    TS_PACKET_SIZE,
    TS_SYNC_BYTE,
)
from dvbs2_analyzer.parsers.base import (
    PacketCorruptionError,
    SyncLossError,
)
from dvbs2_analyzer.parsers.ts_parser import (
    TSPacket,
    TSParser,
    TSStreamStatistics,
)


def make_ts_packet(
    sync: int = TS_SYNC_BYTE,
    tei: int = 0,
    pusi: int = 0,
    priority: int = 0,
    pid: int = 0x0100,
    tsc: int = 0,
    afc: int = 0b01,  # payload only
    cc: int = 0,
    adaptation_length: int = 0,
    payload_byte: int = 0xAA,
) -> bytes:
    """Helper to synthesize a compliant 188-byte TS packet for testing."""
    b0 = sync & 0xFF
    b1 = ((tei & 0x01) << 7) | ((pusi & 0x01) << 6) | ((priority & 0x01) << 5) | ((pid >> 8) & 0x1F)
    b2 = pid & 0xFF
    b3 = ((tsc & 0x03) << 6) | ((afc & 0x03) << 4) | (cc & 0x0F)

    header = bytes([b0, b1, b2, b3])

    if afc in (0b10, 0b11):  # Adaptation field present
        afl = bytes([adaptation_length & 0xFF])
        # Fill adaptation field with padding
        af_body = b"\x00" * adaptation_length
        remaining = TS_PACKET_SIZE - len(header) - len(afl) - len(af_body)
        payload = bytes([payload_byte]) * max(0, remaining)
        packet = header + afl + af_body + payload
    else:
        remaining = TS_PACKET_SIZE - len(header)
        payload = bytes([payload_byte]) * remaining
        packet = header + payload

    return packet[:TS_PACKET_SIZE]


class TestTSParser(unittest.TestCase):
    """Unit test suite for TSParser."""

    def setUp(self):
        self.parser = TSParser(strict_mode=True)

    # -------------------------------------------------------------------------
    # 1. Packet Length & Sync Byte Validation
    # -------------------------------------------------------------------------
    def test_valid_packet_parsing(self):
        raw = make_ts_packet(pid=256, cc=5)
        pkt = self.parser.parse_packet(raw)
        self.assertEqual(pkt.sync_byte, TS_SYNC_BYTE)
        self.assertEqual(pkt.pid, 256)
        self.assertEqual(pkt.continuity_counter, 5)
        self.assertFalse(pkt.tei)
        self.assertFalse(pkt.is_null_packet)
        self.assertTrue(pkt.has_payload)

    def test_invalid_packet_length_short(self):
        short_packet = b"\x47" * 187
        with self.assertRaises(PacketCorruptionError):
            self.parser.parse_packet(short_packet)

    def test_invalid_packet_length_long(self):
        long_packet = b"\x47" * 189
        with self.assertRaises(PacketCorruptionError):
            self.parser.parse_packet(long_packet)

    def test_invalid_sync_byte(self):
        corrupt_sync = b"\x00" + (b"\x00" * 187)
        with self.assertRaises(SyncLossError):
            self.parser.parse_packet(corrupt_sync)

    # -------------------------------------------------------------------------
    # 2. PID Extraction & Null Packets
    # -------------------------------------------------------------------------
    def test_pid_extraction_pat(self):
        raw = make_ts_packet(pid=0x0000)
        pkt = self.parser.parse_packet(raw)
        self.assertEqual(pkt.pid, 0)
        self.assertFalse(pkt.is_null_packet)

    def test_pid_extraction_null_packet(self):
        raw = make_ts_packet(pid=TS_NULL_PID)
        pkt = self.parser.parse_packet(raw)
        self.assertEqual(pkt.pid, 8191)
        self.assertTrue(pkt.is_null_packet)

    def test_pid_extraction_arbitrary(self):
        for test_pid in [1, 32, 100, 500, 2048, 8190]:
            raw = make_ts_packet(pid=test_pid)
            pkt = self.parser.parse_packet(raw)
            self.assertEqual(pkt.pid, test_pid)
            self.assertFalse(pkt.is_null_packet)

    # -------------------------------------------------------------------------
    # 3. Header Flags Extraction
    # -------------------------------------------------------------------------
    def test_tei_flag(self):
        pkt_clean = self.parser.parse_packet(make_ts_packet(tei=0))
        self.assertFalse(pkt_clean.tei)

        pkt_tei = self.parser.parse_packet(make_ts_packet(tei=1))
        self.assertTrue(pkt_tei.tei)

    def test_pusi_flag(self):
        pkt_no_pusi = self.parser.parse_packet(make_ts_packet(pusi=0))
        self.assertFalse(pkt_no_pusi.pusi)

        pkt_pusi = self.parser.parse_packet(make_ts_packet(pusi=1))
        self.assertTrue(pkt_pusi.pusi)

    def test_transport_priority_flag(self):
        pkt_normal = self.parser.parse_packet(make_ts_packet(priority=0))
        self.assertFalse(pkt_normal.transport_priority)

        pkt_prio = self.parser.parse_packet(make_ts_packet(priority=1))
        self.assertTrue(pkt_prio.transport_priority)

    def test_scrambling_control_values(self):
        for tsc in [0, 1, 2, 3]:
            pkt = self.parser.parse_packet(make_ts_packet(tsc=tsc))
            self.assertEqual(pkt.transport_scrambling_control, tsc)

    def test_continuity_counter_values(self):
        for cc in range(16):
            pkt = self.parser.parse_packet(make_ts_packet(cc=cc))
            self.assertEqual(pkt.continuity_counter, cc)

    # -------------------------------------------------------------------------
    # 4. Adaptation Field Detection
    # -------------------------------------------------------------------------
    def test_afc_payload_only(self):
        raw = make_ts_packet(afc=0b01)
        pkt = self.parser.parse_packet(raw)
        self.assertFalse(pkt.has_adaptation_field)
        self.assertTrue(pkt.has_payload)
        self.assertEqual(pkt.adaptation_field_length, 0)
        self.assertEqual(len(pkt.payload), 184)

    def test_afc_adaptation_only(self):
        raw = make_ts_packet(afc=0b10, adaptation_length=183)
        pkt = self.parser.parse_packet(raw)
        self.assertTrue(pkt.has_adaptation_field)
        self.assertFalse(pkt.has_payload)
        self.assertEqual(pkt.adaptation_field_length, 183)
        self.assertEqual(len(pkt.payload), 0)

    def test_afc_adaptation_and_payload(self):
        raw = make_ts_packet(afc=0b11, adaptation_length=10)
        pkt = self.parser.parse_packet(raw)
        self.assertTrue(pkt.has_adaptation_field)
        self.assertTrue(pkt.has_payload)
        self.assertEqual(pkt.adaptation_field_length, 10)
        # Payload size: 188 - 4 (header) - 1 (AFL) - 10 (AF) = 173 bytes
        self.assertEqual(len(pkt.payload), 173)

    def test_malformed_adaptation_field_length(self):
        # Header (4B) + AFL=184 -> exceeds 188 bytes total
        raw = make_ts_packet(afc=0b11, adaptation_length=184)
        with self.assertRaises(PacketCorruptionError):
            self.parser.parse_packet(raw)

    # -------------------------------------------------------------------------
    # 5. Continuity Counter & Stream Statistics
    # -------------------------------------------------------------------------
    def test_stream_continuity_tracking(self):
        # Stream of 5 consecutive packets on PID 100 with CC 0, 1, 2, 3, 4
        stream_bytes = b"".join(make_ts_packet(pid=100, cc=i) for i in range(5))
        packets = list(self.parser.parse_stream(io.BytesIO(stream_bytes)))

        self.assertEqual(len(packets), 5)
        stats = self.parser.get_statistics()
        self.assertEqual(stats["total_packets"], 5)
        self.assertEqual(stats["valid_sync_packets"], 5)
        self.assertEqual(stats["total_continuity_errors"], 0)

    def test_continuity_error_detection(self):
        # Packets with a gap: CC=0 then CC=3 (expected 1)
        stream_bytes = make_ts_packet(pid=200, cc=0) + make_ts_packet(pid=200, cc=3)
        packets = list(self.parser.parse_stream(io.BytesIO(stream_bytes)))

        self.assertEqual(len(packets), 2)
        stats = self.parser.get_statistics()
        self.assertEqual(stats["total_continuity_errors"], 1)
        self.assertEqual(stats["continuity_error_distribution"][200], 1)

    # -------------------------------------------------------------------------
    # 6. Real Dataset Verification (No Modification to Raw Data)
    # -------------------------------------------------------------------------
    def test_parse_real_satellite_toolkit_sample(self):
        sample_path = RAW_DATA_DIR / "03_TS" / "DVBS2_toolkit" / "sample.ts"
        self.assertTrue(sample_path.exists())

        parser = TSParser()
        packets = list(parser.parse_file(sample_path, max_packets=200))

        self.assertEqual(len(packets), 200)
        stats = parser.get_statistics()
        self.assertEqual(stats["total_packets"], 200)
        self.assertEqual(stats["valid_sync_packets"], 200)
        self.assertEqual(stats["sync_byte_errors"], 0)
        self.assertEqual(stats["sync_integrity_percentage"], 100.0)
        self.assertGreater(stats["unique_pids_count"], 0)

    def test_parse_real_blockstream_broadcast_sample(self):
        blockstream_path = RAW_DATA_DIR / "05_REAL_DVB_S2" / "GRCon22_Blockstream" / "blockstream.ts"
        self.assertTrue(blockstream_path.exists())

        parser = TSParser()
        packets = list(parser.parse_file(blockstream_path, max_packets=200))

        self.assertEqual(len(packets), 200)
        stats = parser.get_statistics()
        self.assertEqual(stats["total_packets"], 200)
        self.assertEqual(stats["valid_sync_packets"], 200)
        # Verify PID 32 (0x0020) exists as expected for Blockstream satellite broadcast
        self.assertIn(32, stats["pid_distribution"])


if __name__ == "__main__":
    unittest.main()
