"""
Unit and Integration Test Suite for Feature F3: Stream Pattern Detection.

Covers:
1. TS dominant PID detection
2. TS PID distribution breakdown
3. TS Shannon entropy / pattern calculation
4. TS PAT/PMT detection and lockstep tracking
5. TS PCR clock activity detection
6. GSE protocol distribution
7. GSE PDU size distribution and clustering
8. GSE fragmentation patterns
9. GSE label/extension header patterns
10. BBFrame DFL distribution and modal frame size
11. BBFrame SIS/MIS behavior
12. BBFrame CCM/ACM modulation pattern
13. BBFrame roll-off factor stability
14. BBFrame mode adaptation classification
15. Empty / insufficient input handling
16. Deterministic pattern results across repeated runs
17. Window transition detection across sequential windows
18. Real MPEG-TS dataset integration
19. Real GSE dataset integration
20. Real BBFrame dataset integration
21. StreamHandler universal gateway integration
"""

from pathlib import Path
import unittest

from dvbs2_analyzer.analysis.patterns import (
    PatternConfig,
    PatternDetector,
    PatternFinding,
    PatternReport,
    PatternResult,
    PatternType,
)
from dvbs2_analyzer.config import StreamFormat
from dvbs2_analyzer.ingestion.stream_handler import StreamHandler
from dvbs2_analyzer.parsers.bbframe_parser import BBFrame, BBFrameParser
from dvbs2_analyzer.parsers.gse_parser import GSEPDU, GSELabelType, GSEParser
from dvbs2_analyzer.parsers.ts_parser import TSPacket, TSParser

BASE_DIR = Path(__file__).resolve().parent.parent.parent
RAW_DATA_DIR = BASE_DIR / "01_RAW_DATA"


# =============================================================================
# Synthetic Data Generators for Controlled Pattern Testing
# =============================================================================

def make_ts_packet(
    pid: int,
    has_af: bool = False,
    pcr: bool = False,
    pusi: bool = False,
    payload: bytes = b""
) -> TSPacket:
    raw = bytearray([0x47, 0x00, 0x00, 0x10] + [0xFF] * 184)
    raw[1] = (raw[1] & 0xE0) | ((pid >> 8) & 0x1F)
    if pusi:
        raw[1] |= 0x40
    raw[2] = pid & 0xFF
    if has_af:
        raw[3] = 0x30 # AFC: adaptation field + payload
        raw[4] = 7    # AFL
        raw[5] = 0x10 if pcr else 0x00 # AF flags: bit 4 is PCR
    return TSPacket(
        sync_byte=0x47,
        tei=False,
        pusi=pusi,
        transport_priority=False,
        pid=pid,
        transport_scrambling_control=0,
        adaptation_field_control=0x30 if has_af else 0x10,
        continuity_counter=0,
        has_adaptation_field=has_af,
        has_payload=True,
        adaptation_field_length=7 if has_af else 0,
        is_null_packet=(pid == 8191),
        raw_bytes=bytes(raw),
        payload=payload or bytes(raw[12:] if has_af else raw[4:]),
    )


def make_gse_pdu(
    protocol_name: str = "IPv4",
    is_unfrag: bool = True,
    is_first: bool = False,
    is_mid: bool = False,
    is_last: bool = False,
    payload_len: int = 500,
    label: bytes = b"\x00\x80\x69\x09\x94\x82"
) -> GSEPDU:
    return GSEPDU(
        start_indicator=is_unfrag or is_first,
        end_indicator=is_unfrag or is_last,
        label_type=GSELabelType.LABEL_6B if label else GSELabelType.LABEL_NONE,
        gse_length=payload_len + 2,
        frag_id=1 if not is_unfrag else None,
        total_length=payload_len if is_first else None,
        protocol_type=0x0800 if protocol_name == "IPv4" else 0x0002,
        protocol_name=protocol_name,
        label=label,
        crc32=0x12345678 if is_last else None,
        payload=b"G" * payload_len,
        payload_length=payload_len,
        is_padding=False,
        is_unfragmented=is_unfrag,
        is_first_fragment=is_first,
        is_intermediate_fragment=is_mid,
        is_last_fragment=is_last,
        encapsulated_protocol="IPv4" if protocol_name == "IPv4" else None,
        raw_bytes=b"GSE" + b"G" * payload_len,
    )


def make_bbframe(
    dfl: int = 2992,
    is_sis: bool = True,
    is_ccm: bool = False,
    ro: float = 0.35,
    ma_type: str = "L.3 (4B)",
    ts_gs: str = "GENERIC_CONTINUOUS"
) -> BBFrame:
    return BBFrame(
        matype1=0x00,
        matype2=0x00,
        ts_gs=ts_gs,
        is_sis=is_sis,
        is_ccm=is_ccm,
        issyi=False,
        npd=False,
        ro_rolloff=ro,
        isi=None if is_sis else 1,
        upl=0,
        dfl=dfl,
        dfl_bytes=dfl // 8,
        sync=0x00,
        syncd=0,
        crc8=0x00,
        crc8_calculated=0x00,
        is_valid=True,
        header_bytes=b"\x00" * 10,
        payload=b"B" * (dfl // 8),
        payload_length=dfl // 8,
        is_truncated=False,
        mode_adaptation_type=ma_type,
    )


# =============================================================================
# Test Suite
# =============================================================================

class TestPatternDetection(unittest.TestCase):
    """Comprehensive test cases for Feature F3 Stream Pattern Detection."""

    def setUp(self):
        self.detector = PatternDetector(PatternConfig(
            ts_window_size=20,
            gse_window_size=5,
            bbframe_window_size=10,
            dominant_pid_threshold=0.50,
        ))

    # -------------------------------------------------------------------------
    # 1. TS Dominant PID Detection
    # -------------------------------------------------------------------------
    def test_ts_dominant_pid_detection(self):
        # 80 packets of PID 256 (dominant video), 15 packets PID 257, 5 packets PID 0
        packets = [make_ts_packet(256) for _ in range(80)]
        packets += [make_ts_packet(257) for _ in range(15)]
        packets += [make_ts_packet(0) for _ in range(5)]

        res = self.detector.analyze_ts_window(packets)
        dom_findings = res.get_findings_by_type(PatternType.TS_DOMINANT_PID.value)

        self.assertEqual(len(dom_findings), 1)
        self.assertEqual(dom_findings[0].supporting_metrics["dominant_pid"], 256)
        self.assertEqual(dom_findings[0].supporting_metrics["percentage"], 80.0)
        self.assertIn("PID 256", dom_findings[0].description)
        self.assertIn("dominant stream", dom_findings[0].description)

    # -------------------------------------------------------------------------
    # 2. TS PID Distribution Breakdown
    # -------------------------------------------------------------------------
    def test_ts_pid_distribution(self):
        packets = [make_ts_packet(256) for _ in range(50)] + [make_ts_packet(257) for _ in range(50)]
        res = self.detector.analyze_ts_window(packets)
        findings = res.get_findings_by_type(PatternType.TS_PID_DISTRIBUTION.value)

        self.assertEqual(len(findings), 1)
        dist = findings[0].supporting_metrics["pid_distribution"]
        self.assertIn("256", dist)
        self.assertIn("257", dist)
        self.assertEqual(dist["256"]["percentage"], 50.0)
        self.assertEqual(dist["257"]["percentage"], 50.0)

    # -------------------------------------------------------------------------
    # 3. TS Shannon Entropy Calculation
    # -------------------------------------------------------------------------
    def test_ts_entropy_calculation(self):
        # 100 packets of a single PID -> Entropy should be 0.0 bits
        single_pid_packets = [make_ts_packet(100) for _ in range(100)]
        res_single = self.detector.analyze_ts_window(single_pid_packets)
        f_single = res_single.get_findings_by_type(PatternType.TS_MULTIPLEX_COMPOSITION.value)[0]
        self.assertAlmostEqual(f_single.supporting_metrics["shannon_entropy_bits"], 0.0, places=3)
        self.assertIn("single-program dominated", f_single.description)

        # Equal split of 2 PIDs -> Entropy should be 1.0 bit
        two_pid_packets = [make_ts_packet(100) for _ in range(50)] + [make_ts_packet(200) for _ in range(50)]
        res_two = self.detector.analyze_ts_window(two_pid_packets)
        f_two = res_two.get_findings_by_type(PatternType.TS_MULTIPLEX_COMPOSITION.value)[0]
        self.assertAlmostEqual(f_two.supporting_metrics["shannon_entropy_bits"], 1.0, places=3)

    # -------------------------------------------------------------------------
    # 4. TS PAT / PMT Recurrence & Lockstep
    # -------------------------------------------------------------------------
    def test_ts_pat_pmt_recurrence_and_lockstep(self):
        packets = []
        # Construct pattern: Video packet, PAT (PID 0), PMT (PID 4096), Video packets...
        for i in range(5):
            packets.append(make_ts_packet(256))
            packets.append(make_ts_packet(0))    # PAT
            packets.append(make_ts_packet(4096)) # PMT
            for _ in range(10):
                packets.append(make_ts_packet(256))

        res = self.detector.analyze_ts_window(packets)
        f_pat = res.get_findings_by_type(PatternType.TS_PAT_PMT_STRUCTURE.value)

        self.assertEqual(len(f_pat), 1)
        metrics = f_pat[0].supporting_metrics
        self.assertEqual(metrics["pat_count"], 5)
        self.assertEqual(metrics["pmt_count"], 5)
        self.assertTrue(metrics["is_lockstep"])
        self.assertIn("lockstep", f_pat[0].description)
        self.assertIn("average recurrence", f_pat[0].description)

    # -------------------------------------------------------------------------
    # 5. TS PCR Clock Activity Detection
    # -------------------------------------------------------------------------
    def test_ts_pcr_activity_detection(self):
        packets = [make_ts_packet(256, has_af=True, pcr=(i % 10 == 0)) for i in range(50)]
        res = self.detector.analyze_ts_window(packets)
        f_pcr = res.get_findings_by_type(PatternType.TS_PCR_ACTIVITY.value)

        self.assertEqual(len(f_pcr), 1)
        self.assertEqual(f_pcr[0].supporting_metrics["pcr_count"], 5)
        self.assertIn(256, f_pcr[0].supporting_metrics["pcr_pids"])
        self.assertIn("mean recurrence", f_pcr[0].description)

    # -------------------------------------------------------------------------
    # 6. GSE Protocol Distribution
    # -------------------------------------------------------------------------
    def test_gse_protocol_distribution(self):
        pdus = [make_gse_pdu("IPv4") for _ in range(8)] + [make_gse_pdu("IPv6") for _ in range(2)]
        res = self.detector.analyze_gse_window(pdus)
        findings = res.get_findings_by_type(PatternType.GSE_PROTOCOL_DISTRIBUTION.value)

        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0].supporting_metrics["dominant_protocol"], "IPv4")
        self.assertEqual(findings[0].supporting_metrics["dominant_percentage"], 80.0)
        self.assertIn("dominated by IPv4", findings[0].description)

    # -------------------------------------------------------------------------
    # 7. GSE Size Distribution and Clusters
    # -------------------------------------------------------------------------
    def test_gse_size_distribution(self):
        # 5 small PDUs (50B) and 5 MTU PDUs (1400B)
        pdus = [make_gse_pdu(payload_len=50) for _ in range(5)] + [make_gse_pdu(payload_len=1400) for _ in range(5)]
        res = self.detector.analyze_gse_window(pdus)
        findings = res.get_findings_by_type(PatternType.GSE_PDU_SIZE_DISTRIBUTION.value)

        self.assertEqual(len(findings), 1)
        metrics = findings[0].supporting_metrics
        self.assertEqual(metrics["min_bytes"], 50)
        self.assertEqual(metrics["max_bytes"], 1400)
        self.assertEqual(metrics["mean_bytes"], 725.0)
        self.assertIn("size_clusters", metrics)

    # -------------------------------------------------------------------------
    # 8. GSE Fragmentation Pattern
    # -------------------------------------------------------------------------
    def test_gse_fragmentation_pattern(self):
        # 6 unfragmented, 2 first, 2 last -> 4/10 = 40% fragmentation
        pdus = [make_gse_pdu(is_unfrag=True) for _ in range(6)]
        pdus += [make_gse_pdu(is_unfrag=False, is_first=True) for _ in range(2)]
        pdus += [make_gse_pdu(is_unfrag=False, is_last=True) for _ in range(2)]

        res = self.detector.analyze_gse_window(pdus)
        findings = res.get_findings_by_type(PatternType.GSE_FRAGMENTATION_BEHAVIOR.value)

        self.assertEqual(len(findings), 1)
        self.assertAlmostEqual(findings[0].supporting_metrics["fragmentation_ratio"], 0.40, places=2)
        self.assertIn("40.0% of observed PDUs belong to fragmented transmissions", findings[0].description)

    # -------------------------------------------------------------------------
    # 9. GSE Label and Extension Header Usage
    # -------------------------------------------------------------------------
    def test_gse_label_extension_pattern(self):
        pdus = [
            make_gse_pdu("GSE_EXT_NPA", label=b"\x00\x80\x69\x09\x94\x82")
            for _ in range(10)
        ]
        res = self.detector.analyze_gse_window(pdus)
        findings = res.get_findings_by_type(PatternType.GSE_LABEL_EXTENSION_USAGE.value)

        self.assertEqual(len(findings), 1)
        self.assertIn("LABEL_6B", findings[0].description)
        self.assertIn("GSE_EXT_NPA", findings[0].supporting_metrics["extension_headers"])

    # -------------------------------------------------------------------------
    # 10. BBFrame DFL Distribution and Mode
    # -------------------------------------------------------------------------
    def test_bbframe_dfl_distribution(self):
        # 8 frames with DFL=2992, 2 frames with DFL=8304
        frames = [make_bbframe(dfl=2992) for _ in range(8)] + [make_bbframe(dfl=8304) for _ in range(2)]
        res = self.detector.analyze_bbframe_window(frames)
        findings = res.get_findings_by_type(PatternType.BB_DFL_DISTRIBUTION.value)

        self.assertEqual(len(findings), 1)
        metrics = findings[0].supporting_metrics
        self.assertEqual(metrics["modal_dfl_bits"], 2992)
        self.assertEqual(metrics["modal_percentage"], 80.0)
        self.assertEqual(metrics["min_dfl_bits"], 2992)
        self.assertEqual(metrics["max_dfl_bits"], 8304)

    # -------------------------------------------------------------------------
    # 11. BBFrame SIS vs MIS Pattern
    # -------------------------------------------------------------------------
    def test_bbframe_sis_mis_pattern(self):
        # 100% SIS
        sis_frames = [make_bbframe(is_sis=True) for _ in range(10)]
        res_sis = self.detector.analyze_bbframe_window(sis_frames)
        f_sis = res_sis.get_findings_by_type(PatternType.BB_SIS_MIS_BEHAVIOR.value)[0]
        self.assertIn("SIS (Single Input Stream)", f_sis.description)
        self.assertEqual(f_sis.supporting_metrics["sis_ratio"], 1.0)

        # 100% MIS
        mis_frames = [make_bbframe(is_sis=False) for _ in range(10)]
        res_mis = self.detector.analyze_bbframe_window(mis_frames)
        f_mis = res_mis.get_findings_by_type(PatternType.BB_SIS_MIS_BEHAVIOR.value)[0]
        self.assertIn("MIS (Multiple Input Stream)", f_mis.description)
        self.assertEqual(f_mis.supporting_metrics["mis_ratio"], 1.0)

    # -------------------------------------------------------------------------
    # 12. BBFrame CCM vs ACM Pattern
    # -------------------------------------------------------------------------
    def test_bbframe_ccm_acm_pattern(self):
        # 100% ACM
        acm_frames = [make_bbframe(is_ccm=False) for _ in range(10)]
        res_acm = self.detector.analyze_bbframe_window(acm_frames)
        f_acm = res_acm.get_findings_by_type(PatternType.BB_CCM_ACM_BEHAVIOR.value)[0]
        self.assertIn("100% Adaptive Coding & Modulation (ACM)", f_acm.description)
        self.assertEqual(f_acm.supporting_metrics["acm_ratio"], 1.0)

    # -------------------------------------------------------------------------
    # 13. BBFrame Roll-Off Factor Stability
    # -------------------------------------------------------------------------
    def test_bbframe_rolloff_stability(self):
        # Constant alpha=0.35
        frames = [make_bbframe(ro=0.35) for _ in range(15)]
        res = self.detector.analyze_bbframe_window(frames)
        findings = res.get_findings_by_type(PatternType.BB_ROLLOFF_STABILITY.value)

        self.assertEqual(len(findings), 1)
        self.assertTrue(findings[0].supporting_metrics["is_stable"])
        self.assertEqual(findings[0].supporting_metrics["dominant_alpha"], 0.35)
        self.assertIn("strictly stable at alpha=0.35", findings[0].description)

    # -------------------------------------------------------------------------
    # 14. BBFrame Mode Adaptation
    # -------------------------------------------------------------------------
    def test_bbframe_mode_adaptation(self):
        frames = [make_bbframe(ma_type="L.3 (4B)") for _ in range(10)]
        res = self.detector.analyze_bbframe_window(frames)
        findings = res.get_findings_by_type(PatternType.BB_MODE_ADAPTATION.value)

        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0].supporting_metrics["dominant_type"], "L.3 (4B)")
        self.assertIn("dominated by L.3 (4B)", findings[0].description)

    # -------------------------------------------------------------------------
    # 15. Empty / Insufficient Input Handling
    # -------------------------------------------------------------------------
    def test_empty_and_insufficient_input(self):
        # Empty sequences must return empty result with zero counts and not crash
        res_ts = self.detector.analyze_ts_window([])
        self.assertEqual(len(res_ts.findings), 0)
        self.assertEqual(res_ts.window_size, 0)

        res_gse = self.detector.analyze_gse_window([])
        self.assertEqual(len(res_gse.findings), 0)

        res_bb = self.detector.analyze_bbframe_window([])
        self.assertEqual(len(res_bb.findings), 0)

        # Full stream report on empty inputs
        rep_ts = self.detector.analyze_ts_stream([])
        self.assertEqual(rep_ts.total_units_analyzed, 0)
        self.assertEqual(rep_ts.total_windows, 0)

    # -------------------------------------------------------------------------
    # 16. Deterministic Pattern Results
    # -------------------------------------------------------------------------
    def test_deterministic_pattern_results(self):
        packets = [make_ts_packet(256) for _ in range(40)] + [make_ts_packet(0) for _ in range(10)]
        rep1 = self.detector.analyze_ts_stream(packets, window_size=25)
        rep2 = self.detector.analyze_ts_stream(packets, window_size=25)

        self.assertEqual(len(rep1.findings), len(rep2.findings))
        for f1, f2 in zip(rep1.findings, rep2.findings):
            self.assertEqual(f1.pattern_type, f2.pattern_type)
            self.assertEqual(f1.description, f2.description)
            self.assertEqual(f1.supporting_metrics, f2.supporting_metrics)

    # -------------------------------------------------------------------------
    # 17. Window Transition Detection
    # -------------------------------------------------------------------------
    def test_window_transition_detection(self):
        # Window 0: dominant PID 256
        # Window 1: dominant PID 500
        packets = [make_ts_packet(256) for _ in range(20)] + [make_ts_packet(500) for _ in range(20)]
        rep = self.detector.analyze_ts_stream(packets, window_size=20)

        transitions = [f for f in rep.findings if f.pattern_type == PatternType.PATTERN_TRANSITION.value]
        self.assertEqual(len(transitions), 1)
        self.assertIn("switched from 256 to 500", transitions[0].description)
        self.assertEqual(transitions[0].window_index, 1)

    # -------------------------------------------------------------------------
    # 18. Real MPEG-TS Dataset Integration
    # -------------------------------------------------------------------------
    def test_real_ts_dataset_integration(self):
        ts_file = RAW_DATA_DIR / "03_TS" / "DVBS2_toolkit" / "sample.ts"
        self.assertTrue(ts_file.exists(), f"Sample TS file missing: {ts_file}")

        handler = StreamHandler(ts_file, forced_format=StreamFormat.MPEG_TS)
        parser = handler.get_parser()
        packets = list(parser.parse_file(ts_file, max_packets=500))
        self.assertGreaterEqual(len(packets), 500)

        rep = self.detector.analyze_ts_stream(packets, window_size=100)
        self.assertGreater(len(rep.findings), 0)

        # PID 256 must be detected as dominant
        dom_findings = [f for f in rep.findings if f.pattern_type == PatternType.TS_DOMINANT_PID.value]
        self.assertEqual(len(dom_findings), 1)
        self.assertEqual(dom_findings[0].supporting_metrics["dominant_pid"], 256)
        self.assertGreater(dom_findings[0].supporting_metrics["percentage"], 90.0)

        # PAT / PMT structure must be detected
        pat_findings = [f for f in rep.findings if f.pattern_type == PatternType.TS_PAT_PMT_STRUCTURE.value]
        self.assertEqual(len(pat_findings), 1)
        self.assertGreater(pat_findings[0].supporting_metrics["pat_count"], 0)

    # -------------------------------------------------------------------------
    # 19. Real GSE Dataset Integration
    # -------------------------------------------------------------------------
    def test_real_gse_dataset_integration(self):
        gse_file = RAW_DATA_DIR / "02_GSE" / "GSExtract" / "sample.ts"
        self.assertTrue(gse_file.exists(), f"Sample GSE file missing: {gse_file}")

        handler = StreamHandler(gse_file, forced_format=StreamFormat.GSE)
        parser = handler.get_parser()
        pdus = list(parser.parse_file(gse_file))
        self.assertEqual(len(pdus), 14) # 14 complete valid PDUs

        rep = self.detector.analyze_gse_stream(pdus, window_size=5)
        self.assertGreater(len(rep.findings), 0)

        # Protocol distribution should detect GSE_EXT_NPA
        proto_findings = [f for f in rep.findings if f.pattern_type == PatternType.GSE_PROTOCOL_DISTRIBUTION.value]
        self.assertEqual(len(proto_findings), 1)
        self.assertEqual(proto_findings[0].supporting_metrics["dominant_protocol"], "GSE_EXT_NPA")

        # Fragmentation should detect ~57% fragmentation
        frag_findings = [f for f in rep.findings if f.pattern_type == PatternType.GSE_FRAGMENTATION_BEHAVIOR.value]
        self.assertEqual(len(frag_findings), 1)
        self.assertGreater(frag_findings[0].supporting_metrics["fragmentation_ratio"], 0.50)

    # -------------------------------------------------------------------------
    # 20. Real BBFrame Dataset Integration
    # -------------------------------------------------------------------------
    def test_real_bbframe_dataset_integration(self):
        bb_file = RAW_DATA_DIR / "01_BBFRAME_GSE" / "dvb-s2_bb_example.pcap"
        self.assertTrue(bb_file.exists(), f"Sample BBFrame file missing: {bb_file}")

        handler = StreamHandler(bb_file, forced_format=StreamFormat.BB_FRAME)
        parser = handler.get_parser()
        frames = list(parser.parse_file(bb_file, max_packets=200))
        self.assertEqual(len(frames), 200)

        rep = self.detector.analyze_bbframe_stream(frames, window_size=50)
        self.assertGreater(len(rep.findings), 0)

        # DFL distribution should detect dominant mode in first 200 frames (8304 bits, 96.5%)
        dfl_findings = [f for f in rep.findings if f.pattern_type == PatternType.BB_DFL_DISTRIBUTION.value]
        self.assertEqual(len(dfl_findings), 1)
        self.assertEqual(dfl_findings[0].supporting_metrics["modal_dfl_bits"], 8304)

        # 100% ACM detection
        acm_findings = [f for f in rep.findings if f.pattern_type == PatternType.BB_CCM_ACM_BEHAVIOR.value]
        self.assertEqual(len(acm_findings), 1)
        self.assertEqual(acm_findings[0].supporting_metrics["acm_ratio"], 1.0)

        # Roll-off alpha=0.35 stable
        ro_findings = [f for f in rep.findings if f.pattern_type == PatternType.BB_ROLLOFF_STABILITY.value]
        self.assertEqual(len(ro_findings), 1)
        self.assertTrue(ro_findings[0].supporting_metrics["is_stable"])
        self.assertEqual(ro_findings[0].supporting_metrics["dominant_alpha"], 0.35)

        # Also test with 600 frames where DFL transitions to 2992 bits
        frames_600 = list(parser.parse_file(bb_file, max_packets=600))
        rep_600 = self.detector.analyze_bbframe_stream(frames_600, window_size=100)
        transitions = [f for f in rep_600.findings if f.pattern_type == PatternType.PATTERN_TRANSITION.value]
        self.assertTrue(any("DFL" in t.description for t in transitions))

    # -------------------------------------------------------------------------
    # 21. StreamHandler Universal Gateway
    # -------------------------------------------------------------------------
    def test_stream_handler_universal_gateway(self):
        ts_file = RAW_DATA_DIR / "03_TS" / "DVBS2_toolkit" / "sample.ts"
        handler = StreamHandler(ts_file, forced_format=StreamFormat.MPEG_TS)
        rep = self.detector.detect_from_handler(handler, max_units=100)

        self.assertEqual(rep.format, StreamFormat.MPEG_TS)
        self.assertEqual(rep.total_units_analyzed, 100)
        summary_text = rep.summary()
        self.assertIn("PRJ_111: STREAM PATTERN DETECTION REPORT", summary_text)
        self.assertIn("MPEG_TS", summary_text)


if __name__ == "__main__":
    unittest.main()
