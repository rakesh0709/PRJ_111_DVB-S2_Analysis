#!/usr/bin/env python3
"""
CLI Runner and Experiment Script for Feature F2: AI-Based Anomaly Detection (PRJ_111).

Executes real-data unsupervised anomaly detection benchmarks across:
  1. MPEG-TS: 01_RAW_DATA/03_TS/DVBS2_toolkit/sample.ts
  2. GSE: 01_RAW_DATA/02_GSE/GSExtract/sample.ts
  3. DVB-S2 BBFrame: 01_RAW_DATA/01_BBFRAME_GSE/dvb-s2_bb_example.pcap

Performs:
  A. Baseline training on real satellite stream windows
  B. Normal data inference and score calibration
  C. Controlled synthetic perturbation experiments (in-memory only)
  D. Empirical feature deviation explanations
"""

import argparse
import json
from pathlib import Path
import sys

# Ensure dvbs2_analyzer package is resolvable
CURRENT_DIR = Path(__file__).resolve().parent
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))

from dvbs2_analyzer.analysis.anomaly import (
    AnomalyConfig,
    AnomalyDetector,
    MultiFormatAnomalyEngine,
    create_perturbed_bbframe_vector,
    create_perturbed_gse_vector,
    create_perturbed_ts_vector,
)
from dvbs2_analyzer.config import RAW_DATA_DIR, StreamFormat
from dvbs2_analyzer.features.extractor import FeatureExtractor
from dvbs2_analyzer.ingestion.stream_handler import StreamHandler
from dvbs2_analyzer.parsers.bbframe_parser import BBFrameStreamStatistics
from dvbs2_analyzer.parsers.gse_parser import GSEStreamStatistics
from dvbs2_analyzer.parsers.ts_parser import TSStreamStatistics


def extract_ts_windows(file_path: Path, window_size: int = 200, max_packets: int = 4000):
    """Slices an MPEG-TS capture into sequential telemetry windows."""
    handler = StreamHandler(file_path, forced_format=StreamFormat.MPEG_TS)
    parser = handler.get_parser()
    extractor = FeatureExtractor()

    windows = []
    current_stats = TSStreamStatistics()
    count = 0

    for pkt in parser.parse_file(file_path, max_packets=max_packets):
        current_stats.total_packets += 1
        if pkt.has_payload:
            current_stats.payload_packet_count += 1
        if pkt.has_adaptation_field:
            current_stats.adaptation_field_count += 1
        current_stats.total_payload_bytes += len(pkt.payload)
        current_stats.pid_counts[pkt.pid] += 1
        current_stats.valid_sync_packets += 1

        count += 1
        if count >= window_size:
            meta = {"window_index": len(windows), "window_size": count}
            feat = extractor.extract_unified(current_stats, format=StreamFormat.MPEG_TS, metadata=meta)
            windows.append(feat)
            current_stats = TSStreamStatistics()
            count = 0

    return windows


def extract_bbframe_windows(file_path: Path, window_size: int = 50, max_frames: int = 1500):
    """Slices a DVB-S2 BBFrame capture into sequential telemetry windows."""
    handler = StreamHandler(file_path, forced_format=StreamFormat.BB_FRAME)
    parser = handler.get_parser()
    extractor = FeatureExtractor()

    windows = []
    current_stats = BBFrameStreamStatistics()
    count = 0

    for frame in parser.parse_file(file_path, max_packets=max_frames):
        current_stats.total_frames += 1
        if frame.is_valid:
            current_stats.valid_frames += 1
        else:
            current_stats.invalid_crc_frames += 1
        if frame.is_truncated:
            current_stats.truncated_frames += 1
        current_stats.total_payload_bytes += frame.payload_length
        current_stats.dfl_values.append(frame.dfl)
        current_stats.upl_values.append(frame.upl)
        current_stats.stream_type_counts[frame.ts_gs] += 1
        current_stats.input_stream_mode_counts["SIS" if frame.is_sis else "MIS"] += 1
        current_stats.coding_modulation_counts["CCM" if frame.is_ccm else "ACM"] += 1
        current_stats.roll_off_counts[f"alpha={frame.ro_rolloff}"] += 1
        current_stats.sync_byte_counts[f"0x{frame.sync:02x}"] += 1
        if frame.isi is not None:
            current_stats.isi_counts[frame.isi] += 1
        if frame.mode_adaptation_type:
            current_stats.mode_adaptation_counts[frame.mode_adaptation_type] += 1

        count += 1
        if count >= window_size:
            meta = {"window_index": len(windows), "window_size": count}
            feat = extractor.extract_unified(current_stats, format=StreamFormat.BB_FRAME, metadata=meta)
            windows.append(feat)
            current_stats = BBFrameStreamStatistics()
            count = 0

    return windows


def extract_gse_windows(file_path: Path, window_size: int = 3):
    """Slices a GSE capture into sequential telemetry windows."""
    handler = StreamHandler(file_path, forced_format=StreamFormat.GSE)
    parser = handler.get_parser()
    extractor = FeatureExtractor()

    windows = []
    current_stats = GSEStreamStatistics()
    count = 0

    for pdu in parser.parse_file(file_path):
        current_stats.total_pdus += 1
        current_stats.valid_pdus += 1
        if pdu.is_padding:
            current_stats.padding_packets += 1
        elif pdu.is_unfragmented:
            current_stats.unfragmented_pdus += 1
        elif pdu.is_first_fragment:
            current_stats.first_fragments += 1
        elif pdu.is_intermediate_fragment:
            current_stats.intermediate_fragments += 1
        elif pdu.is_last_fragment:
            current_stats.last_fragments += 1

        current_stats.total_payload_bytes += pdu.payload_length
        current_stats.protocol_type_counts[pdu.protocol_name] += 1
        if pdu.encapsulated_protocol:
            current_stats.encapsulated_protocols[pdu.encapsulated_protocol] += 1
        label_str = f"LABEL_{len(pdu.label)}B" if pdu.label else "LABEL_NONE"
        current_stats.label_type_counts[label_str] += 1

        count += 1
        if count >= window_size:
            meta = {"window_index": len(windows), "window_size": count}
            feat = extractor.extract_unified(current_stats, format=StreamFormat.GSE, metadata=meta)
            windows.append(feat)
            current_stats = GSEStreamStatistics()
            count = 0

    # Add remainder
    if count > 0:
        meta = {"window_index": len(windows), "window_size": count}
        feat = extractor.extract_unified(current_stats, format=StreamFormat.GSE, metadata=meta)
        windows.append(feat)

    return windows


def run_experiments():
    print("=" * 75)
    print(" PRJ_111: FEATURE F2 — AI-BASED ANOMALY DETECTION EXPERIMENTS")
    print(" Unsupervised Baseline: Isolation Forest | Review-2 Milestone")
    print("=" * 75)

    # -------------------------------------------------------------------------
    # Experiment 1: MPEG-TS
    # -------------------------------------------------------------------------
    ts_file = RAW_DATA_DIR / "03_TS" / "DVBS2_toolkit" / "sample.ts"
    print(f"\n[1/3] Benchmarking MPEG-TS Stream: {ts_file.name}")
    ts_windows = extract_ts_windows(ts_file, window_size=200, max_packets=4000)
    print(f"      Generated {len(ts_windows)} telemetry windows (200 packets/window).")

    # Split 70% train / 30% test
    split_idx = int(len(ts_windows) * 0.70)
    ts_train = ts_windows[:split_idx]
    ts_test = ts_windows[split_idx:]

    ts_detector = AnomalyDetector(AnomalyConfig(format=StreamFormat.MPEG_TS, contamination=0.05, random_state=42))
    ts_detector.fit(ts_train)
    ts_report = ts_detector.predict_batch(ts_test, dataset_name="MPEG-TS Held-Out Windows")

    print(f"      Training Samples: {len(ts_train)} | Test Samples: {len(ts_test)}")
    print(f"      Feature Dimensions: {len(ts_detector.feature_names)}")
    print(f"      Features: {', '.join(ts_detector.feature_names)}")
    print(f"      Test Results: {ts_report.normal_count} Normal, {ts_report.anomaly_count} Anomalous ({ts_report.anomaly_ratio*100:.1f}%)")
    print(f"      Score Range : [{ts_report.min_score:.4f} .. {ts_report.max_score:.4f}] (Mean: {ts_report.mean_score:.4f})")

    # In-memory perturbation test
    baseline_vec = ts_test[0].to_format_vector(StreamFormat.MPEG_TS)
    perturbed_ts = create_perturbed_ts_vector(baseline_vec, tei_burst=True, continuity_gap=True)
    res_perturbed_ts = ts_detector.predict_sample(perturbed_ts)
    print("      --- Controlled Perturbation Test (In-Memory TEI + CC Error Injection) ---")
    print(f"      Decision: {'ANOMALY' if res_perturbed_ts.is_anomaly else 'NORMAL'} | Severity: {res_perturbed_ts.severity} | Score: {res_perturbed_ts.anomaly_score:.4f}")
    print(f"      Explanation: {res_perturbed_ts.summary_explanation}")
    for d in res_perturbed_ts.top_deviations[:2]:
        print(f"        * {d.feature_name}: {d.observed_value:.4f} (baseline: {d.baseline_mean:.4f} +/- {d.baseline_std:.4f}, z={d.z_score:.1f})")

    # -------------------------------------------------------------------------
    # Experiment 2: GSE
    # -------------------------------------------------------------------------
    gse_file = RAW_DATA_DIR / "02_GSE" / "GSExtract" / "sample.ts"
    print(f"\n[2/3] Benchmarking GSE Stream: {gse_file.name}")
    gse_windows = extract_gse_windows(gse_file, window_size=3)
    print(f"      Generated {len(gse_windows)} telemetry windows (3 PDUs/window).")

    gse_detector = AnomalyDetector(AnomalyConfig(format=StreamFormat.GSE, contamination=0.10, random_state=42))
    gse_detector.fit(gse_windows)
    gse_report = gse_detector.predict_batch(gse_windows, dataset_name="GSE Real Windows")

    print(f"      Training Samples: {len(gse_windows)} | Feature Dimensions: {len(gse_detector.feature_names)}")
    print(f"      Results: {gse_report.normal_count} Normal, {gse_report.anomaly_count} Anomalous ({gse_report.anomaly_ratio*100:.1f}%)")

    # Controlled perturbation
    baseline_gse = gse_windows[0].to_format_vector(StreamFormat.GSE)
    perturbed_gse = create_perturbed_gse_vector(baseline_gse, extreme_fragmentation=True, truncation_anomaly=True)
    res_perturbed_gse = gse_detector.predict_sample(perturbed_gse)
    print("      --- Controlled Perturbation Test (In-Memory Fragmentation + Truncation) ---")
    print(f"      Decision: {'ANOMALY' if res_perturbed_gse.is_anomaly else 'NORMAL'} | Severity: {res_perturbed_gse.severity} | Score: {res_perturbed_gse.anomaly_score:.4f}")
    print(f"      Explanation: {res_perturbed_gse.summary_explanation}")
    for d in res_perturbed_gse.top_deviations[:2]:
        print(f"        * {d.feature_name}: {d.observed_value:.4f} (baseline: {d.baseline_mean:.4f}, z={d.z_score:.1f})")

    # -------------------------------------------------------------------------
    # Experiment 3: DVB-S2 Baseband Frame (BBFrame)
    # -------------------------------------------------------------------------
    bb_file = RAW_DATA_DIR / "01_BBFRAME_GSE" / "dvb-s2_bb_example.pcap"
    print(f"\n[3/3] Benchmarking DVB-S2 BBFrame Stream: {bb_file.name}")
    bb_windows = extract_bbframe_windows(bb_file, window_size=50, max_frames=1500)
    print(f"      Generated {len(bb_windows)} telemetry windows (50 frames/window).")

    bb_split = int(len(bb_windows) * 0.70)
    bb_train = bb_windows[:bb_split]
    bb_test = bb_windows[bb_split:]

    bb_detector = AnomalyDetector(AnomalyConfig(format=StreamFormat.BB_FRAME, contamination=0.05, random_state=42))
    bb_detector.fit(bb_train)
    bb_report = bb_detector.predict_batch(bb_test, dataset_name="BBFrame Held-Out Windows")

    print(f"      Training Samples: {len(bb_train)} | Test Samples: {len(bb_test)}")
    print(f"      Feature Dimensions: {len(bb_detector.feature_names)}")
    print(f"      Test Results: {bb_report.normal_count} Normal, {bb_report.anomaly_count} Anomalous ({bb_report.anomaly_ratio*100:.1f}%)")

    # Controlled perturbation
    baseline_bb = bb_test[0].to_format_vector(StreamFormat.BB_FRAME)
    perturbed_bb = create_perturbed_bbframe_vector(baseline_bb, crc_corruption=True, payload_shrink=True)
    res_perturbed_bb = bb_detector.predict_sample(perturbed_bb)
    print("      --- Controlled Perturbation Test (In-Memory CRC Corruption + Payload Collapse) ---")
    print(f"      Decision: {'ANOMALY' if res_perturbed_bb.is_anomaly else 'NORMAL'} | Severity: {res_perturbed_bb.severity} | Score: {res_perturbed_bb.anomaly_score:.4f}")
    print(f"      Explanation: {res_perturbed_bb.summary_explanation}")
    for d in res_perturbed_bb.top_deviations[:2]:
        print(f"        * {d.feature_name}: {d.observed_value:.4f} (baseline: {d.baseline_mean:.4f}, z={d.z_score:.1f})")

    print("\n" + "=" * 75)
    print(" F2 ANOMALY DETECTION EXPERIMENTS COMPLETED SUCCESSFULLY")
    print("=" * 75)


if __name__ == "__main__":
    run_experiments()
