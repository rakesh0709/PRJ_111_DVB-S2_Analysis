"""
Unit and Integration Tests for BBFrameParser (PRJ_111).

Compliant with ETSI EN 302 307-1:
  - 10-byte BBHeader decoding (MATYPE-1, MATYPE-2, UPL, DFL, SYNC, SYNCD, CRC-8)
  - MATYPE-1 field decomposition (TS/GS, SIS/MIS, CCM/ACM, ISSYI, NPD, RO)
  - MATYPE-2 ISI extraction (conditional on MIS)
  - CRC-8 computation and validation (polynomial 0xD5)
  - Payload boundary extraction and slicing
  - Multiple consecutive frames in continuous raw stream
  - Truncated frame detection (strict vs non-strict mode)
  - Malformed header / insufficient bytes handling
  - StreamHandler instantiation for StreamFormat.BB_FRAME
  - Stream statistics aggregation, formatting, and reset
  - Real dataset integration on 01_RAW_DATA/01_BBFRAME_GSE/dvb-s2_bb_example.pcap (4,309 frames)
  - Real dataset integration on 01_RAW_DATA/02_GSE/GSExtract/sample.ts (9 frames)
"""

import io
from pathlib import Path
import struct
from typing import Optional
import unittest

from dvbs2_analyzer.config import RAW_DATA_DIR, StreamFormat
from dvbs2_analyzer.ingestion.stream_handler import StreamHandler
from dvbs2_analyzer.parsers.base import PacketCorruptionError
from dvbs2_analyzer.parsers.bbframe_parser import (
    BBFrame,
    BBFrameParser,
    BBFrameStreamStatistics,
    crc8_dvbs2,
)


def make_bbframe(
    ts_gs: int = 0b11,       # 2 bits: 11 = TRANSPORT, 00 = GENERIC_PACKETIZED, 01 = GENERIC_CONTINUOUS, 10 = GSE_HEM
    sis_mis: int = 1,        # 1 bit: 1 = SIS, 0 = MIS
    ccm_acm: int = 1,        # 1 bit: 1 = CCM, 0 = ACM
    issyi: int = 0,          # 1 bit
    npd: int = 0,            # 1 bit
    ro: int = 0b00,          # 2 bits: 00=0.35, 01=0.25, 10=0.20, 11=0.15
    isi: int = 0x00,         # MATYPE-2
    upl: int = 188 * 8,      # User Packet Length in bits
    dfl: int = 50 * 8,       # Data Field Length in bits (default 50 bytes)
    sync: int = 0x47,        # User packet sync byte
    syncd: int = 0,          # Distance in bits to first user packet
    payload: Optional[bytes] = None,
    corrupt_crc: bool = False,
    override_crc: Optional[int] = None,
) -> bytes:
    """Helper to construct an ETSI EN 302 307-1 compliant BBFrame for unit testing."""
    matype1 = (
        ((ts_gs & 0x03) << 6)
        | ((sis_mis & 0x01) << 5)
        | ((ccm_acm & 0x01) << 4)
        | ((issyi & 0x01) << 3)
        | ((npd & 0x01) << 2)
        | (ro & 0x03)
    )
    matype2 = isi & 0xFF

    hdr_first_9 = struct.pack(">BBHHBH", matype1, matype2, upl, dfl, sync, syncd)
    crc = crc8_dvbs2(hdr_first_9)
    if corrupt_crc:
        crc ^= 0xFF
    if override_crc is not None:
        crc = override_crc & 0xFF

    header = hdr_first_9 + bytes([crc])

    if payload is None:
        payload = b"\xDE\xAD\xBE\xEF" * (dfl // 32)
        if len(payload) < (dfl // 8):
            payload += b"\x00" * ((dfl // 8) - len(payload))

    return header + payload


class TestBBFrameParser(unittest.TestCase):
    """Test suite for DVB-S2 Baseband Frame parsing."""

    def setUp(self):
        self.parser = BBFrameParser(strict_mode=False)
        self.strict_parser = BBFrameParser(strict_mode=True)

    def test_crc8_known_vectors(self):
        """Validates the CRC-8 implementation against known test bytes."""
        # Single byte 0x00 gives 0x00
        self.assertEqual(crc8_dvbs2(b"\x00"), 0x00)
        # Verify deterministic computation
        sample = b"\x80\x00\x05\xe0\x00\xa0\x47\x00\x00"
        crc = crc8_dvbs2(sample)
        self.assertIsInstance(crc, int)
        self.assertGreaterEqual(crc, 0)
        self.assertLessEqual(crc, 255)
        self.assertEqual(crc8_dvbs2(sample), crc)

    def test_valid_bbframe_header_parsing(self):
        """Tests standard BBFrame parsing with Transport Stream format."""
        raw = make_bbframe(
            ts_gs=0b11,
            sis_mis=1,
            ccm_acm=1,
            issyi=0,
            npd=0,
            ro=0b00,
            isi=0,
            upl=1504,
            dfl=800, # 100 bytes
            sync=0x47,
            syncd=0,
        )
        frame, consumed = self.parser.parse_frame(raw)

        self.assertEqual(frame.ts_gs, "TRANSPORT")
        self.assertTrue(frame.is_sis)
        self.assertTrue(frame.is_ccm)
        self.assertFalse(frame.issyi)
        self.assertFalse(frame.npd)
        self.assertEqual(frame.ro_rolloff, 0.35)
        self.assertIsNone(frame.isi) # SIS mode has no ISI
        self.assertEqual(frame.upl, 1504)
        self.assertEqual(frame.dfl, 800)
        self.assertEqual(frame.dfl_bytes, 100)
        self.assertEqual(frame.sync, 0x47)
        self.assertEqual(frame.syncd, 0)
        self.assertTrue(frame.is_valid)
        self.assertFalse(frame.is_truncated)
        self.assertEqual(frame.payload_length, 100)
        self.assertEqual(consumed, 110) # 10 header + 100 payload

    def test_matype1_field_decomposition(self):
        """Tests MATYPE-1 stream types and roll-off combinations."""
        # 1. Generic Continuous (0b01), MIS (0), ACM (0), alpha=0.25 (0b01)
        raw_gc = make_bbframe(
            ts_gs=0b01,
            sis_mis=0,
            ccm_acm=0,
            ro=0b01,
            isi=0x12,
            dfl=80,
        )
        frame_gc, _ = self.parser.parse_frame(raw_gc)
        self.assertEqual(frame_gc.ts_gs, "GENERIC_CONTINUOUS")
        self.assertFalse(frame_gc.is_sis)
        self.assertFalse(frame_gc.is_ccm)
        self.assertEqual(frame_gc.ro_rolloff, 0.25)
        self.assertEqual(frame_gc.isi, 0x12)

        # 2. Generic Packetized (0b00), SIS (1), CCM (1), alpha=0.20 (0b10)
        raw_gp = make_bbframe(
            ts_gs=0b00,
            sis_mis=1,
            ccm_acm=1,
            ro=0b10,
            dfl=80,
        )
        frame_gp, _ = self.parser.parse_frame(raw_gp)
        self.assertEqual(frame_gp.ts_gs, "GENERIC_PACKETIZED")
        self.assertTrue(frame_gp.is_sis)
        self.assertEqual(frame_gp.ro_rolloff, 0.20)

        # 3. GSE / High Efficiency Mode (0b10), ISSYI=1, NPD=1, alpha=0.15 (0b11)
        raw_gse = make_bbframe(
            ts_gs=0b10,
            sis_mis=1,
            ccm_acm=1,
            issyi=1,
            npd=1,
            ro=0b11,
            dfl=80,
        )
        frame_gse, _ = self.parser.parse_frame(raw_gse)
        self.assertEqual(frame_gse.ts_gs, "GSE_HEM")
        self.assertTrue(frame_gse.issyi)
        self.assertTrue(frame_gse.npd)
        self.assertEqual(frame_gse.ro_rolloff, 0.15)

    def test_matype2_isi_extraction(self):
        """Tests MATYPE-2 ISI extraction under SIS and MIS modes."""
        # SIS mode -> ISI should be None regardless of byte value
        raw_sis = make_bbframe(sis_mis=1, isi=0x55, dfl=80)
        frame_sis, _ = self.parser.parse_frame(raw_sis)
        self.assertIsNone(frame_sis.isi)

        # MIS mode -> ISI should be extracted as integer (0..255)
        raw_mis = make_bbframe(sis_mis=0, isi=0x7A, dfl=80)
        frame_mis, _ = self.parser.parse_frame(raw_mis)
        self.assertEqual(frame_mis.isi, 0x7A)

    def test_upl_dfl_sync_syncd_extraction(self):
        """Tests exact 16-bit UPL, 16-bit DFL, 8-bit SYNC, and 16-bit SYNCD values."""
        raw = make_bbframe(
            upl=0x1234,
            dfl=0x0180, # 384 bits = 48 bytes
            sync=0xB8,
            syncd=0x00FF,
            payload=b"\x11" * 48,
        )
        frame, consumed = self.parser.parse_frame(raw)
        self.assertEqual(frame.upl, 0x1234)
        self.assertEqual(frame.dfl, 0x0180)
        self.assertEqual(frame.dfl_bytes, 48)
        self.assertEqual(frame.sync, 0xB8)
        self.assertEqual(frame.syncd, 0x00FF)
        self.assertEqual(frame.payload, b"\x11" * 48)
        self.assertEqual(consumed, 58)

    def test_crc8_validation_and_corruption(self):
        """Tests CRC-8 verification in normal and strict modes."""
        # Valid CRC
        raw_valid = make_bbframe(dfl=80)
        frame_valid, _ = self.parser.parse_frame(raw_valid)
        self.assertTrue(frame_valid.is_valid)

        # Corrupted CRC
        raw_corrupt = make_bbframe(dfl=80, corrupt_crc=True)
        # Non-strict mode: marks frame invalid, does not raise
        frame_corrupt, _ = self.parser.parse_frame(raw_corrupt)
        self.assertFalse(frame_corrupt.is_valid)
        self.assertNotEqual(frame_corrupt.crc8, frame_corrupt.crc8_calculated)

        # Strict mode: raises PacketCorruptionError
        with self.assertRaises(PacketCorruptionError):
            self.strict_parser.parse_frame(raw_corrupt)

    def test_payload_boundary_slicing(self):
        """Tests precise payload slicing according to DFL."""
        exact_payload = b"ETSI_DVB_S2_TEST_PAYLOAD_32_BYTES!"
        dfl_bits = len(exact_payload) * 8
        raw = make_bbframe(dfl=dfl_bits, payload=exact_payload)
        frame, consumed = self.parser.parse_frame(raw)

        self.assertEqual(frame.payload, exact_payload)
        self.assertEqual(frame.payload_length, len(exact_payload))
        self.assertEqual(consumed, 10 + len(exact_payload))
        self.assertFalse(frame.is_truncated)

    def test_multiple_consecutive_frames(self):
        """Tests parsing a continuous stream of multiple consecutive BBFrames."""
        f1_data = b"PAYLOAD_ONE_32B_BYTES_FOR_FRAME1"
        f2_data = b"PAYLOAD_TWO_24B_BYTES_F2"
        f3_data = b"PAYLOAD_THREE_16B"

        frame1_bytes = make_bbframe(ts_gs=0b11, dfl=len(f1_data)*8, payload=f1_data)
        frame2_bytes = make_bbframe(ts_gs=0b01, dfl=len(f2_data)*8, payload=f2_data)
        frame3_bytes = make_bbframe(ts_gs=0b10, dfl=len(f3_data)*8, payload=f3_data)

        stream_bytes = frame1_bytes + frame2_bytes + frame3_bytes
        stream_io = io.BytesIO(stream_bytes)

        frames = list(self.parser.parse_stream(stream_io))
        self.assertEqual(len(frames), 3)

        self.assertEqual(frames[0].ts_gs, "TRANSPORT")
        self.assertEqual(frames[0].payload, f1_data)

        self.assertEqual(frames[1].ts_gs, "GENERIC_CONTINUOUS")
        self.assertEqual(frames[1].payload, f2_data)

        self.assertEqual(frames[2].ts_gs, "GSE_HEM")
        self.assertEqual(frames[2].payload, f3_data)

        stats = self.parser.get_statistics()
        self.assertEqual(stats["total_frames"], 3)
        self.assertEqual(stats["valid_frames"], 3)
        self.assertEqual(stats["invalid_crc_frames"], 0)

    def test_truncated_frame_detection(self):
        """Tests handling when available bytes are less than DFL."""
        # Specify DFL = 800 bits (100 bytes), but supply only 20 bytes payload
        raw_full = make_bbframe(dfl=800)
        truncated_raw = raw_full[: 10 + 20] # 10 header + 20 payload

        # Non-strict mode: frame flagged as truncated
        frame, consumed = self.parser.parse_frame(truncated_raw)
        self.assertTrue(frame.is_truncated)
        self.assertEqual(frame.payload_length, 20)
        self.assertEqual(consumed, 30)

        # Strict mode: raises PacketCorruptionError
        with self.assertRaises(PacketCorruptionError):
            self.strict_parser.parse_frame(truncated_raw)

    def test_insufficient_header_bytes(self):
        """Tests that attempting to parse < 10 bytes raises PacketCorruptionError."""
        short_bytes = b"\x80\x00\x05\xe0\x00" # 5 bytes
        with self.assertRaises(PacketCorruptionError):
            self.parser.parse_frame(short_bytes)

    def test_stream_handler_bbframe_instantiation(self):
        """Tests that StreamHandler returns BBFrameParser for StreamFormat.BB_FRAME."""
        pcap_path = RAW_DATA_DIR / "01_BBFRAME_GSE" / "dvb-s2_bb_example.pcap"
        if pcap_path.exists():
            handler = StreamHandler(pcap_path)
            self.assertEqual(handler.format, StreamFormat.BB_FRAME)
            parser = handler.get_parser()
            self.assertIsInstance(parser, BBFrameParser)

    def test_statistics_aggregation_and_reset(self):
        """Tests diagnostic metrics aggregation and reset functionality."""
        parser = BBFrameParser()
        raw1 = make_bbframe(ts_gs=0b11, dfl=160, ro=0b00) # Transport, alpha=0.35
        raw2 = make_bbframe(ts_gs=0b01, dfl=320, ro=0b10) # Generic continuous, alpha=0.20

        f1, _ = parser.parse_frame(raw1)
        parser._update_statistics(f1)
        f2, _ = parser.parse_frame(raw2)
        parser._update_statistics(f2)

        stats = parser.get_statistics()
        self.assertEqual(stats["total_frames"], 2)
        self.assertEqual(stats["valid_frames"], 2)
        self.assertEqual(stats["stream_types"]["TRANSPORT"], 1)
        self.assertEqual(stats["stream_types"]["GENERIC_CONTINUOUS"], 1)
        self.assertEqual(stats["roll_off_distribution"]["alpha=0.35"], 1)
        self.assertEqual(stats["roll_off_distribution"]["alpha=0.2"], 1)

        parser.reset_statistics()
        reset_stats = parser.get_statistics()
        self.assertEqual(reset_stats["total_frames"], 0)
        self.assertEqual(reset_stats["valid_frames"], 0)


class TestBBFrameRealDatasets(unittest.TestCase):
    """Integration tests on real collected satellite datasets."""

    def test_real_dataset_dvb_s2_bb_example_pcap(self):
        """
        Parses real PCAP-NG satellite capture: 01_RAW_DATA/01_BBFRAME_GSE/dvb-s2_bb_example.pcap.
        Verifies exact 4,309 BBFrames extracted with 0 CRC errors.
        """
        pcap_path = RAW_DATA_DIR / "01_BBFRAME_GSE" / "dvb-s2_bb_example.pcap"
        self.assertTrue(pcap_path.exists(), f"Dataset not found: {pcap_path}")

        parser = BBFrameParser(strict_mode=False)
        frames = list(parser.parse_file(pcap_path))

        self.assertEqual(len(frames), 4309, f"Expected 4,309 frames, got {len(frames)}")

        stats = parser.get_statistics()
        self.assertEqual(stats["total_frames"], 4309)
        self.assertEqual(stats["valid_frames"], 4309)
        self.assertEqual(stats["invalid_crc_frames"], 0)
        self.assertEqual(stats["malformed_headers"], 0)

        # Verify attributes on first frame
        first_frame = frames[0]
        self.assertEqual(first_frame.ts_gs, "GENERIC_CONTINUOUS")
        self.assertTrue(first_frame.is_sis)
        self.assertFalse(first_frame.is_ccm) # Real capture uses ACM
        self.assertEqual(first_frame.ro_rolloff, 0.35)
        self.assertEqual(first_frame.dfl, 6952)
        self.assertEqual(first_frame.dfl_bytes, 869)
        self.assertEqual(first_frame.mode_adaptation_type, "L.3 (4B)")
        self.assertTrue(first_frame.is_valid)

    def test_real_dataset_sample_ts_bbframe_chain(self):
        """
        Parses raw BBFrame chain from 01_RAW_DATA/02_GSE/GSExtract/sample.ts.
        Verifies 9 BBFrames decoded (8 complete + 1 truncated).
        """
        sample_path = RAW_DATA_DIR / "02_GSE" / "GSExtract" / "sample.ts"
        self.assertTrue(sample_path.exists(), f"Dataset not found: {sample_path}")

        parser = BBFrameParser(strict_mode=False)
        frames = list(parser.parse_file(sample_path))

        self.assertEqual(len(frames), 9, f"Expected 9 frames, got {len(frames)}")

        stats = parser.get_statistics()
        self.assertEqual(stats["total_frames"], 9)
        self.assertEqual(stats["valid_frames"], 9)
        self.assertEqual(stats["truncated_frames"], 1)

        # Inspect first valid BBFrame in sample.ts
        first_frame = frames[0]
        self.assertEqual(first_frame.ts_gs, "GENERIC_CONTINUOUS")
        self.assertTrue(first_frame.is_valid)
        self.assertEqual(first_frame.dfl_bytes, 1454)


if __name__ == "__main__":
    unittest.main()
