#!/usr/bin/env python3
"""
CLI Runner for DVB-S2 Baseband Frame (BBFrame) Stream Analysis (PRJ_111).

Demonstrates and executes the BBFrame parser pipeline compliant with ETSI EN 302 307-1
on real PCAP captures (sl_561 Mode Adaptation) and raw continuous binary BBFrame streams.
"""

import argparse
import json
from pathlib import Path
import sys

# Ensure local dvbs2_analyzer package is resolvable
CURRENT_DIR = Path(__file__).resolve().parent
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))

from dvbs2_analyzer.config import RAW_DATA_DIR
from dvbs2_analyzer.ingestion import StreamFormat, StreamHandler
from dvbs2_analyzer.parsers.bbframe_parser import BBFrameParser


def main():
    default_sample = RAW_DATA_DIR / "01_BBFRAME_GSE" / "dvb-s2_bb_example.pcap"

    parser = argparse.ArgumentParser(
        description="PRJ_111: DVB-S2 Baseband Frame (BBFrame) Analysis Tool (ETSI EN 302 307-1)"
    )
    parser.add_argument(
        "file_path",
        nargs="?",
        default=str(default_sample),
        help=f"Path to the BBFrame stream or PCAP file to analyze (default: {default_sample.name})",
    )
    parser.add_argument(
        "--max-frames",
        type=int,
        default=None,
        help="Maximum number of BBFrames to decode",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Enable strict mode (raise exception immediately on CRC error or truncation)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output diagnostics in JSON format",
    )
    parser.add_argument(
        "--details",
        action="store_true",
        help="Print detailed frame-by-frame inventory table (first 25 frames if > 25)",
    )

    args = parser.parse_args()
    target_file = Path(args.file_path).resolve()

    if not target_file.exists():
        print(f"Error: Target file not found: {target_file}", file=sys.stderr)
        sys.exit(1)

    # Ingest using StreamHandler
    handler = StreamHandler(target_file, forced_format=StreamFormat.BB_FRAME)
    stream_info = handler.get_stream_info()

    bb_parser = BBFrameParser(strict_mode=args.strict)
    frames = list(bb_parser.parse_file(target_file, max_packets=args.max_frames))
    stats = bb_parser.get_statistics()

    if args.json:
        output = {
            "stream_metadata": stream_info.to_dict(),
            "bbframe_statistics": stats,
            "frames_count": len(frames),
        }
        print(json.dumps(output, indent=2))
        return

    # Formatted human-readable report
    sep = "=" * 72
    subsep = "-" * 72
    print(sep)
    print(" PRJ_111: DVB-S2 BASEBAND FRAME (BBFRAME) ANALYSIS REPORT")
    print(f" ETSI EN 302 307-1 Protocol Diagnostics | File: {target_file.name}")
    print(sep)
    print(f" File Size               : {stream_info.file_size_bytes:,} bytes")
    print(f" Stream Ingestion Format : {stream_info.detected_format.value}")
    print(f" Total Bytes Analyzed    : {stats['total_bytes_read']:,} bytes")
    print(subsep)
    print(" BBFRAME DECODING SUMMARY:")
    print(f"   Total BBFrames Decoded: {stats['total_frames']:,}")
    print(f"   Valid CRC-8 Frames    : {stats['valid_frames']:,}")
    print(f"   Invalid CRC-8 Frames  : {stats['invalid_crc_frames']:,}")
    print(f"   Malformed Headers     : {stats['malformed_headers']:,}")
    print(f"   Truncated Frames      : {stats['truncated_frames']:,}")
    print(subsep)
    print(" STREAM MODE & MODULATION BREAKDOWN:")
    print("   Stream Types (TS/GS):")
    for stype, cnt in stats["stream_types"].items():
        print(f"     - {stype:<22}: {cnt:>6} frames")
    print("   Input Stream Modes:")
    for mode, cnt in stats["input_stream_modes"].items():
        print(f"     - {mode:<22}: {cnt:>6} frames")
    print("   Coding & Modulation:")
    for cm, cnt in stats["coding_modulation_modes"].items():
        print(f"     - {cm:<22}: {cnt:>6} frames")
    print("   Roll-Off Factors (alpha):")
    for ro, cnt in stats["roll_off_distribution"].items():
        print(f"     - {ro:<22}: {cnt:>6} frames")
    if stats["mode_adaptation_distribution"]:
        print("   Mode Adaptation (sl_561):")
        for ma, cnt in stats["mode_adaptation_distribution"].items():
            print(f"     - {ma:<22}: {cnt:>6} frames")
    print(subsep)
    print(" PAYLOAD & DATA FIELD (DFL) METRICS:")
    print(f"   Total Payload Data    : {stats['total_payload_bytes']:,} bytes")
    print(f"   Mean Payload / Frame  : {stats['mean_payload_bytes_per_frame']:.1f} bytes")
    print(f"   DFL Range             : {stats['dfl_bits_min']} .. {stats['dfl_bits_max']} bits ({stats['dfl_bits_min']//8} .. {stats['dfl_bits_max']//8} bytes)")
    print(f"   DFL Mean              : {stats['dfl_bits_mean']} bits ({stats['dfl_bytes_mean']:.1f} bytes)")
    print("   User Packet Sync Bytes:")
    for sync, cnt in stats["sync_byte_distribution"].items():
        print(f"     - {sync:<22}: {cnt:>6} frames")
    print(sep)

    if args.details:
        sample_count = min(len(frames), 25)
        print(f"\nDECODED FRAME INVENTORY (Showing first {sample_count} of {len(frames)} frames):")
        print(f" {'Idx':>5} | {'Stream':<18} | {'Mode':<4} | {'Mod':<4} | {'alpha':<5} | {'DFL (bytes)':>11} | {'SYNC':>6} | {'CRC-8':>5} | {'Valid':<5} | {'Mode Adapt':<9}")
        print("-" * 88)
        for i in range(sample_count):
            f = frames[i]
            mode_str = "SIS" if f.is_sis else f"M:{f.isi}"
            mod_str = "CCM" if f.is_ccm else "ACM"
            crc_str = f"0x{f.crc8:02X}"
            sync_str = f"0x{f.sync:02X}"
            valid_str = "YES" if f.is_valid else "NO"
            ma_str = f.mode_adaptation_type or "Direct"
            print(f" {i+1:>5} | {f.ts_gs:<18} | {mode_str:<4} | {mod_str:<4} | {f.ro_rolloff:<5} | {f.dfl_bytes:>11} | {sync_str:>6} | {crc_str:>5} | {valid_str:<5} | {ma_str:<9}")
        print("=" * 88)


if __name__ == "__main__":
    main()
