"""
Unit and Integration Test Suite for Feature F4: Timeline & Activity Visualization.

Covers:
1. MPEG-TS timeline point generation and offset calculation
2. GSE timeline point generation and byte offset accumulation
3. BBFrame timeline point generation and offset calculation
4. Time-series extraction (get_series) for health, anomaly, and payload
5. F1 health score integration across sequential windows
6. F2 anomaly score and event marker mapping
7. F3 pattern findings and transition event mapping
8. Strict physical offset tracking (packet/frame/PDU and byte ranges, no fake timestamps)
9. Structured JSON serialization (to_dict and to_json)
10. HTML dashboard generation (interactive Chart.js + SVG, event tables)
11. Terminal ASCII summary rendering
12. Empty / zero-unit input resilience
13. Real MPEG-TS dataset timeline validation
14. Real GSE dataset timeline validation
15. Real BBFrame dataset timeline validation
16. TRUE End-to-End Integration Test:
    raw stream -> native parser -> sequential windows -> F1 -> F2 -> F3 -> F4 Timeline -> serialization/dashboard
"""

from pathlib import Path
import unittest

from dvbs2_analyzer.analysis.timeline import (
    StreamTimeline,
    TimelineConfig,
    TimelineEvent,
    TimelineGenerator,
    TimelinePoint,
)
from dvbs2_analyzer.config import StreamFormat
from dvbs2_analyzer.ingestion.stream_handler import StreamHandler
from dvbs2_analyzer.parsers.bbframe_parser import BBFrame, BBFrameParser
from dvbs2_analyzer.parsers.gse_parser import GSEPDU, GSELabelType, GSEParser
from dvbs2_analyzer.parsers.ts_parser import TSPacket, TSParser

BASE_DIR = Path(__file__).resolve().parent.parent.parent
RAW_DATA_DIR = BASE_DIR / "01_RAW_DATA"


# =============================================================================
# Synthetic Stream Builders for Controlled Unit Testing
# =============================================================================

def make_ts_packet(pid: int = 256, tei: bool = False, sync: int = 0x47, payload_len: int = 184) -> TSPacket:
    raw = bytearray([sync, 0x00, 0x00, 0x10] + [0xAA] * payload_len)
    if tei:
        raw[1] |= 0x80
    raw[1] = (raw[1] & 0xE0) | ((pid >> 8) & 0x1F)
    raw[2] = pid & 0xFF
    return TSPacket(
        sync_byte=sync,
        tei=tei,
        pusi=False,
        transport_priority=False,
        pid=pid,
        transport_scrambling_control=0,
        adaptation_field_control=0x10,
        continuity_counter=0,
        has_adaptation_field=False,
        has_payload=True,
        adaptation_field_length=0,
        is_null_packet=(pid == 8191),
        raw_bytes=bytes(raw),
        payload=bytes(raw[4:]),
    )


def make_gse_pdu(protocol_name: str = "IPv4", is_frag: bool = False, payload_len: int = 500) -> GSEPDU:
    return GSEPDU(
        start_indicator=not is_frag,
        end_indicator=not is_frag,
        label_type=GSELabelType.LABEL_6B,
        gse_length=payload_len + 2,
        frag_id=1 if is_frag else None,
        total_length=payload_len if is_frag else None,
        protocol_type=0x0800,
        protocol_name=protocol_name,
        label=b"\x00\x80\x69\x09\x94\x82",
        crc32=None,
        payload=b"P" * payload_len,
        payload_length=payload_len,
        is_padding=False,
        is_unfragmented=not is_frag,
        is_first_fragment=is_frag,
        is_intermediate_fragment=False,
        is_last_fragment=False,
        encapsulated_protocol="IPv4",
        raw_bytes=b"GSE" + b"P" * payload_len,
    )


def make_bbframe(dfl: int = 2992, is_valid: bool = True, ro: float = 0.35) -> BBFrame:
    payload_len = dfl // 8
    return BBFrame(
        matype1=0x00,
        matype2=0x00,
        ts_gs="GENERIC_CONTINUOUS",
        is_sis=True,
        is_ccm=False,
        issyi=False,
        npd=False,
        ro_rolloff=ro,
        isi=None,
        upl=0,
        dfl=dfl,
        dfl_bytes=payload_len,
        sync=0x00,
        syncd=0,
        crc8=0x00 if is_valid else 0xFF,
        crc8_calculated=0x00,
        is_valid=is_valid,
        header_bytes=b"\x00" * 10,
        payload=b"B" * payload_len,
        payload_length=payload_len,
        is_truncated=False,
        mode_adaptation_type="L.3 (4B)",
        raw_bytes=b"\x00" * 10 + b"B" * payload_len,
    )


# =============================================================================
# Test Suite
# =============================================================================

class TestStreamTimeline(unittest.TestCase):
    """Unit and integration tests for Feature F4 Timeline & Activity Visualization."""

    def setUp(self):
        self.generator = TimelineGenerator(TimelineConfig(
            ts_window_size=20,
            gse_window_size=5,
            bbframe_window_size=10,
            f2_contamination=0.05,
        ))

    # -------------------------------------------------------------------------
    # 1. MPEG-TS Timeline Generation & Offsets
    # -------------------------------------------------------------------------
    def test_ts_timeline_generation_and_offsets(self):
        # 50 packets total with window size 20 -> 3 windows (20, 20, 10)
        packets = [make_ts_packet(256) for _ in range(50)]
        timeline = self.generator.generate_ts_timeline(packets, window_size=20)

        self.assertEqual(timeline.total_units, 50)
        self.assertEqual(timeline.total_windows, 3)
        self.assertEqual(timeline.total_bytes, 50 * 188)

        # Window 0 offsets: 0..20 pkts, 0..3760 bytes
        w0 = timeline.points[0]
        self.assertEqual(w0.unit_offset_start, 0)
        self.assertEqual(w0.unit_offset_end, 20)
        self.assertEqual(w0.byte_offset_start, 0)
        self.assertEqual(w0.byte_offset_end, 3760)

        # Window 2 offsets: 40..50 pkts, 7520..9400 bytes
        w2 = timeline.points[2]
        self.assertEqual(w2.unit_offset_start, 40)
        self.assertEqual(w2.unit_offset_end, 50)
        self.assertEqual(w2.byte_offset_start, 7520)
        self.assertEqual(w2.byte_offset_end, 9400)

    # -------------------------------------------------------------------------
    # 2. GSE Timeline Generation & Byte Accumulation
    # -------------------------------------------------------------------------
    def test_gse_timeline_generation(self):
        # 12 PDUs of 500 payload bytes each (+3 raw header bytes = 503B per PDU)
        pdus = [make_gse_pdu(payload_len=500) for _ in range(12)]
        timeline = self.generator.generate_gse_timeline(pdus, window_size=5)

        self.assertEqual(timeline.total_units, 12)
        self.assertEqual(timeline.total_windows, 3) # 5, 5, 2
        self.assertEqual(timeline.total_bytes, 12 * 503)

        w0 = timeline.points[0]
        self.assertEqual(w0.byte_offset_start, 0)
        self.assertEqual(w0.byte_offset_end, 5 * 503)

    # -------------------------------------------------------------------------
    # 3. BBFrame Timeline Generation & Offsets
    # -------------------------------------------------------------------------
    def test_bbframe_timeline_generation(self):
        frames = [make_bbframe(dfl=2992) for _ in range(25)]
        timeline = self.generator.generate_bbframe_timeline(frames, window_size=10)

        self.assertEqual(timeline.total_units, 25)
        self.assertEqual(timeline.total_windows, 3) # 10, 10, 5
        self.assertEqual(timeline.format, StreamFormat.BB_FRAME)

    # -------------------------------------------------------------------------
    # 4. Metric Time-Series Extraction (get_series)
    # -------------------------------------------------------------------------
    def test_time_series_extraction(self):
        packets = [make_ts_packet(256) for _ in range(40)]
        timeline = self.generator.generate_ts_timeline(packets, window_size=20)

        # Health score series
        s_health = timeline.get_series("health_score")
        self.assertEqual(len(s_health.values), 2)
        self.assertEqual(s_health.window_indices, [0, 1])
        self.assertAlmostEqual(s_health.values[0], 100.0, places=1)

        # Anomaly score series
        s_anom = timeline.get_series("anomaly_score")
        self.assertEqual(len(s_anom.values), 2)
        self.assertGreaterEqual(s_anom.values[0], 0.0)

        # Payload volume series
        s_payload = timeline.get_series("payload_kb")
        self.assertEqual(len(s_payload.values), 2)
        self.assertGreater(s_payload.values[0], 0.0)

    # -------------------------------------------------------------------------
    # 5. F1 Health Integration Across Windows
    # -------------------------------------------------------------------------
    def test_f1_health_integration(self):
        # Window 0: nominal clean packets
        # Window 1: packets with TEI demodulator bit errors
        clean = [make_ts_packet(256, tei=False) for _ in range(20)]
        corrupt = [make_ts_packet(256, tei=True) for _ in range(20)]
        timeline = self.generator.generate_ts_timeline(clean + corrupt, window_size=20)

        self.assertEqual(timeline.points[0].health_status, "HEALTHY")
        self.assertEqual(timeline.points[0].health_score, 100.0)

        # Window 1 should suffer health degradation due to 100% TEI
        self.assertIn(timeline.points[1].health_status, ("CRITICAL", "WARNING"))
        self.assertLess(timeline.points[1].health_score, 80.0)

    # -------------------------------------------------------------------------
    # 6. F2 Anomaly Score & Event Mapping
    # -------------------------------------------------------------------------
    def test_f2_anomaly_integration_and_events(self):
        # Build a 5-window baseline of clean packets
        clean_windows = [make_ts_packet(256) for _ in range(80)]
        # Window with severe TEI bit errors
        bad_window = [make_ts_packet(256, tei=True) for _ in range(20)]

        timeline = self.generator.generate_ts_timeline(clean_windows + bad_window, window_size=20)

        # Anomaly threshold should be populated directly from F2
        self.assertGreater(timeline.anomaly_threshold, 0.0)
        self.assertLessEqual(timeline.anomaly_threshold, 1.0)

        # The last window (with 100% TEI) should trigger an anomaly event
        last_pt = timeline.points[-1]
        self.assertTrue(last_pt.is_anomaly)
        self.assertIn(last_pt.anomaly_severity, ("MEDIUM", "HIGH", "CRITICAL"))

        # Verify an F2_ANOMALY event is present
        anom_events = [e for e in timeline.events if e.event_type == "F2_ANOMALY"]
        self.assertGreaterEqual(len(anom_events), 1)
        self.assertEqual(anom_events[-1].window_index, 4)

    # -------------------------------------------------------------------------
    # 7. F3 Pattern Transition Event Mapping
    # -------------------------------------------------------------------------
    def test_f3_transition_event_mapping(self):
        # Window 0: PID 256
        # Window 1: PID 500 (dominant PID shift)
        w0 = [make_ts_packet(256) for _ in range(20)]
        w1 = [make_ts_packet(500) for _ in range(20)]
        timeline = self.generator.generate_ts_timeline(w0 + w1, window_size=20)

        self.assertTrue(timeline.points[1].has_transition)
        self.assertIn("shifted", timeline.points[1].transition_description.lower())

        trans_events = [e for e in timeline.events if e.event_type == "F3_TRANSITION"]
        self.assertEqual(len(trans_events), 1)
        self.assertEqual(trans_events[0].window_index, 1)

    # -------------------------------------------------------------------------
    # 8. No Fake Timestamps & Physical Offsets
    # -------------------------------------------------------------------------
    def test_no_fake_timestamps_physical_offsets(self):
        packets = [make_ts_packet(256) for _ in range(40)]
        timeline = self.generator.generate_ts_timeline(packets, window_size=20)

        for p in timeline.points:
            # Must strictly use integer physical offsets
            self.assertIsInstance(p.window_index, int)
            self.assertIsInstance(p.unit_offset_start, int)
            self.assertIsInstance(p.unit_offset_end, int)
            self.assertIsInstance(p.byte_offset_start, int)
            self.assertIsInstance(p.byte_offset_end, int)
            self.assertGreater(p.unit_offset_end, p.unit_offset_start)
            self.assertGreater(p.byte_offset_end, p.byte_offset_start)

    # -------------------------------------------------------------------------
    # 9. Structured Serialization (to_dict & to_json)
    # -------------------------------------------------------------------------
    def test_structured_serialization(self):
        packets = [make_ts_packet(256) for _ in range(40)]
        timeline = self.generator.generate_ts_timeline(packets, window_size=20)

        d = timeline.to_dict()
        self.assertIn("stream_name", d)
        self.assertIn("format", d)
        self.assertIn("anomaly_threshold", d)
        self.assertIn("points", d)
        self.assertIn("events", d)
        self.assertEqual(len(d["points"]), 2)

        # JSON round-trip
        json_str = timeline.to_json()
        self.assertIsInstance(json_str, str)
        self.assertIn("points", json_str)
        self.assertIn("payload_kb", json_str)
        # Ensure no fake throughput units are present
        self.assertNotIn("kb/s", json_str.lower())
        self.assertNotIn("mbps", json_str.lower())

    # -------------------------------------------------------------------------
    # 10. HTML Dashboard Rendering
    # -------------------------------------------------------------------------
    def test_html_dashboard_rendering(self):
        packets = [make_ts_packet(256) for _ in range(40)]
        timeline = self.generator.generate_ts_timeline(packets, window_size=20)

        html = timeline.render_html_dashboard()
        self.assertIsInstance(html, str)
        self.assertIn("<!DOCTYPE html>", html)
        self.assertIn("PRJ_111: Stream Timeline & Activity Visualization", html)
        self.assertIn("healthAnomalyChart", html)
        self.assertIn("activityChart", html)
        self.assertIn("W0", html)
        self.assertIn("W1", html)

    # -------------------------------------------------------------------------
    # 11. ASCII Summary Rendering
    # -------------------------------------------------------------------------
    def test_ascii_summary_rendering(self):
        packets = [make_ts_packet(256) for _ in range(40)]
        timeline = self.generator.generate_ts_timeline(packets, window_size=20)

        ascii_str = timeline.render_ascii_summary()
        self.assertIsInstance(ascii_str, str)
        self.assertIn("PRJ_111: STREAM TIMELINE & ACTIVITY SUMMARY", ascii_str)
        self.assertIn("[0..20)", ascii_str)
        self.assertIn("HEALTHY", ascii_str)

    # -------------------------------------------------------------------------
    # 12. Empty Input Resilience
    # -------------------------------------------------------------------------
    def test_empty_input_resilience(self):
        timeline = self.generator.generate_ts_timeline([], window_size=20)
        self.assertEqual(timeline.total_units, 0)
        self.assertEqual(timeline.total_windows, 0)
        self.assertEqual(len(timeline.points), 0)
        self.assertIsInstance(timeline.to_dict(), dict)
        self.assertIsInstance(timeline.render_ascii_summary(), str)

    # -------------------------------------------------------------------------
    # 13. Real MPEG-TS Dataset Timeline Validation
    # -------------------------------------------------------------------------
    def test_real_ts_dataset_timeline(self):
        ts_file = RAW_DATA_DIR / "03_TS" / "DVBS2_toolkit" / "sample.ts"
        self.assertTrue(ts_file.exists())

        handler = StreamHandler(ts_file, forced_format=StreamFormat.MPEG_TS)
        parser = handler.get_parser()
        packets = list(parser.parse_file(ts_file, max_packets=1000))
        self.assertEqual(len(packets), 1000)

        timeline = self.generator.generate_ts_timeline(packets, window_size=200, stream_name="sample.ts")
        self.assertEqual(timeline.total_windows, 5)
        self.assertEqual(timeline.total_units, 1000)

        # Health should be 100% across nominal sample.ts
        for p in timeline.points:
            self.assertEqual(p.health_status, "HEALTHY")
            self.assertAlmostEqual(p.health_score, 100.0, places=1)
            self.assertIn("PID 256", p.format_specific_metrics.get("dominant_pid_summary", ""))

    # -------------------------------------------------------------------------
    # 14. Real GSE Dataset Timeline Validation
    # -------------------------------------------------------------------------
    def test_real_gse_dataset_timeline(self):
        gse_file = RAW_DATA_DIR / "02_GSE" / "GSExtract" / "sample.ts"
        self.assertTrue(gse_file.exists())

        handler = StreamHandler(gse_file, forced_format=StreamFormat.GSE)
        parser = handler.get_parser()
        pdus = list(parser.parse_file(gse_file))
        self.assertEqual(len(pdus), 14)

        timeline = self.generator.generate_gse_timeline(pdus, window_size=4, stream_name="sample.ts")
        self.assertEqual(timeline.total_windows, 4)
        self.assertEqual(timeline.total_units, 14)

        # Verify fragmentation burst detected in window 3
        self.assertTrue(any(p.has_transition for p in timeline.points))
        trans_events = [e for e in timeline.events if e.event_type == "F3_TRANSITION"]
        self.assertGreaterEqual(len(trans_events), 1)

    # -------------------------------------------------------------------------
    # 15. Real BBFrame Dataset Timeline Validation
    # -------------------------------------------------------------------------
    def test_real_bbframe_dataset_timeline(self):
        bb_file = RAW_DATA_DIR / "01_BBFRAME_GSE" / "dvb-s2_bb_example.pcap"
        self.assertTrue(bb_file.exists())

        handler = StreamHandler(bb_file, forced_format=StreamFormat.BB_FRAME)
        parser = handler.get_parser()
        frames = list(parser.parse_file(bb_file, max_packets=500))
        self.assertEqual(len(frames), 500)

        timeline = self.generator.generate_bbframe_timeline(frames, window_size=100, stream_name="dvb-s2_bb_example.pcap")
        self.assertEqual(timeline.total_windows, 5)

        # Verify DFL transition detected across windows (8304 -> 2992)
        self.assertTrue(any(p.has_transition for p in timeline.points))
        dfl_trans = [e for e in timeline.events if "DFL" in e.description]
        self.assertGreaterEqual(len(dfl_trans), 1)

    # -------------------------------------------------------------------------
    # 16. TRUE END-TO-END INTEGRATION TEST (Correction 4)
    # -------------------------------------------------------------------------
    def test_true_end_to_end_pipeline(self):
        """
        True end-to-end integration test proving:
        raw stream -> StreamHandler -> native parser -> sequential windows
        -> F1 Health -> F2 Anomaly -> F3 Patterns -> F4 TimelinePoint/StreamTimeline
        -> serialization -> HTML dashboard.
        Uses real captured data without manually fabricated component outputs.
        """
        ts_file = RAW_DATA_DIR / "03_TS" / "DVBS2_toolkit" / "sample.ts"

        # Step 1: StreamHandler Ingestion
        handler = StreamHandler(ts_file, forced_format=StreamFormat.MPEG_TS)
        self.assertEqual(handler.format, StreamFormat.MPEG_TS)

        # Step 2: Full Timeline Generation from Handler
        timeline = self.generator.generate_from_handler(handler, window_size=500, max_units=1500)

        # Step 3: Verify Grounded Properties
        self.assertEqual(timeline.format, StreamFormat.MPEG_TS)
        self.assertEqual(timeline.total_units, 1500)
        self.assertEqual(timeline.total_windows, 3)
        self.assertGreater(timeline.total_bytes, 0)
        self.assertEqual(timeline.anomaly_threshold, 0.50)

        # Step 4: Verify F1, F2, and F3 live outputs per window
        for p in timeline.points:
            # F1
            self.assertIsInstance(p.health_score, float)
            self.assertIn(p.health_status, ("HEALTHY", "WARNING", "CRITICAL"))
            # F2
            self.assertIsInstance(p.is_anomaly, bool)
            self.assertIsInstance(p.anomaly_score, float)
            self.assertIn(p.anomaly_severity, ("NORMAL", "LOW", "MEDIUM", "HIGH", "CRITICAL"))
            # F3
            self.assertIsInstance(p.pattern_findings, list)
            self.assertGreater(len(p.pattern_findings), 0)
            # Physical offsets
            self.assertEqual(p.unit_density, 500)
            self.assertGreater(p.payload_kb, 0.0)

        # Step 5: Verify Serialization
        serialized = timeline.to_dict()
        self.assertEqual(len(serialized["points"]), 3)
        self.assertIn("summary_stats", serialized)

        # Step 6: Verify HTML Dashboard Generation
        dashboard_html = timeline.render_html_dashboard()
        self.assertIn("PRJ_111", dashboard_html)
        self.assertIn("sample.ts", dashboard_html)
        self.assertIn("Chart", dashboard_html)

    # -------------------------------------------------------------------------
    # 17. TS Transition Calibration: No False Transitions on Minor Variations
    # -------------------------------------------------------------------------
    def test_ts_transition_calibration_no_false_events(self):
        """
        Verifies that slight PID percentage variations do NOT trigger false F3 transitions,
        while genuine dominant PID shifts or major concentration shifts do.
        """
        # Window 0: 190 packets of PID 256 (95%), 10 packets of PID 257 (5%)
        w0 = [make_ts_packet(256) for _ in range(190)] + [make_ts_packet(257) for _ in range(10)]
        # Window 1: 196 packets of PID 256 (98%), 4 packets of PID 257 (2%) -> slight variation, same dominant PID
        w1 = [make_ts_packet(256) for _ in range(196)] + [make_ts_packet(257) for _ in range(4)]
        # Window 2: 150 packets of PID 500 (75%), 50 packets of PID 256 (25%) -> genuine dominant PID shift
        w2 = [make_ts_packet(500) for _ in range(150)] + [make_ts_packet(256) for _ in range(50)]

        timeline = self.generator.generate_ts_timeline(w0 + w1 + w2, window_size=200)

        self.assertEqual(timeline.total_windows, 3)
        # Window 1 must NOT have a transition from Window 0 (both dominant PID 256 with <25% shift)
        self.assertFalse(timeline.points[1].has_transition)

        # Window 2 MUST have a transition (dominant shifted from 256 to 500)
        self.assertTrue(timeline.points[2].has_transition)
        trans_events = [e for e in timeline.events if e.event_type == "F3_TRANSITION"]
        self.assertEqual(len(trans_events), 1)
        self.assertEqual(trans_events[0].window_index, 2)
        self.assertIn("PID 256", trans_events[0].description)
    # -------------------------------------------------------------------------
    # 18. F2 Anomaly Threshold Dynamic Configuration & Propagation
    # -------------------------------------------------------------------------
    def test_configurable_anomaly_threshold_propagation(self):
        """
        Verifies that f2_anomaly_threshold configured in TimelineConfig propagates
        dynamically to the underlying AnomalyDetector and timeline output.
        """
        w0 = [make_ts_packet(256) for _ in range(200)]
        w1 = [make_ts_packet(256) for _ in range(200)]
        packets = w0 + w1

        # Default configuration
        default_gen = TimelineGenerator(TimelineConfig())
        tl_default = default_gen.generate_ts_timeline(packets, window_size=200)
        self.assertAlmostEqual(tl_default.anomaly_threshold, 0.50, places=2)

        # Custom threshold configuration (0.65)
        custom_config = TimelineConfig(f2_anomaly_threshold=0.65)
        custom_gen = TimelineGenerator(custom_config)
        tl_custom = custom_gen.generate_ts_timeline(packets, window_size=200)
        self.assertAlmostEqual(tl_custom.anomaly_threshold, 0.65, places=2)


if __name__ == "__main__":
    unittest.main()

