#!/usr/bin/env python3
"""
CLI Runner for Generic Stream Encapsulation (GSE) Stream Analysis (PRJ_111).

Demonstrates and executes the GSE parser pipeline compliant with ETSI TS 102 606-1
on real or synthetic GSE captures (including DVB-S2 Baseband Frame encapsulations).
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
from dvbs2_analyzer.parsers.gse_parser import GSEParser


def main():
    default_sample = RAW_DATA_DIR / "02_GSE" / "GSExtract" / "sample.ts"

    parser = argparse.ArgumentParser(
        description="PRJ_111: DVB-S2 Generic Stream Encapsulation (GSE) Analysis Tool"
    )
    parser.add_argument(
        "file_path",
        nargs="?",
        default=str(default_sample),
        help=f"Path to the GSE stream file to analyze (default: {default_sample.name})",
    )
    parser.add_argument(
        "--max-pdus",
        type=int,
        default=None,
        help="Maximum number of GSE PDUs to decode",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Enable strict mode (fail immediately on any corrupted PDU)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output diagnostics in JSON format",
    )
    parser.add_argument(
        "--details",
        action="store_true",
        help="Print detailed PDU table for decoded frames",
    )

    args = parser.parse_args()
    target_file = Path(args.file_path).resolve()

    if not target_file.exists():
        print(f"Error: Target file not found: {target_file}", file=sys.stderr)
        sys.exit(1)

    # Use StreamHandler with forced GSE format
    handler = StreamHandler(target_file, forced_format=StreamFormat.GSE)
    stream_info = handler.get_stream_info()

    gse_parser = GSEParser(strict_mode=args.strict)
    pdus = list(gse_parser.parse_file(target_file, max_packets=args.max_pdus))
    stats = gse_parser.get_statistics()

    if args.json:
        output = {
            "stream_metadata": stream_info.to_dict(),
            "gse_statistics": stats,
            "pdus_count": len(pdus),
        }
        print(json.dumps(output, indent=2))
        return

    # Formatted human-readable report
    sep = "=" * 70
    subsep = "-" * 70
    print(sep)
    print(" PRJ_111: DVB-S2 GENERIC STREAM ENCAPSULATION (GSE) ANALYSIS REPORT")
    print(f" ETSI TS 102 606-1 Protocol Diagnostics | File: {target_file.name}")
    print(sep)
    print(f" File Size               : {stream_info.file_size_bytes:,} bytes")
    print(f" Detected / Forced Format: {stream_info.detected_format.value}")
    print(f" Total Bytes Read        : {stats['total_bytes_read']:,} bytes")
    print(subsep)
    print(" PDU DECODING SUMMARY:")
    print(f"   Total PDUs Decoded    : {stats['total_pdus']:,}")
    print(f"   Valid PDUs            : {stats['valid_pdus']:,}")
    print(f"   Malformed PDUs        : {stats['malformed_pdus']:,}")
    print(f"   Truncated PDUs (EOF)  : {stats['truncated_pdus']:,}")
    print(f"   Padding Packets       : {stats['padding_packets']:,}")
    print(subsep)
    print(" FRAGMENTATION BREAKDOWN:")
    print(f"   Unfragmented (S=1, E=1): {stats['unfragmented_pdus']:,}")
    print(f"   Fragmented Total       : {stats['fragmented_pdus_total']:,}")
    print(f"     - First Fragments (S=1, E=0): {stats['first_fragments']:,}")
    print(f"     - Intermediate (S=0, E=0)   : {stats['intermediate_fragments']:,}")
    print(f"     - Last Fragments (S=0, E=1) : {stats['last_fragments']:,}")
    print(subsep)
    print(" PROTOCOL & PAYLOAD METRICS:")
    print(f"   Total Payload Data    : {stats['total_payload_bytes']:,} bytes")
    print(f"   Mean Payload / PDU    : {stats['mean_payload_bytes_per_pdu']:.1f} bytes")
    print("   Protocol Type Distribution:")
    for proto, cnt in stats["protocol_type_distribution"].items():
        print(f"     - {proto:<18}: {cnt:>5} PDUs")
    print("   Encapsulated Network Protocols:")
    for encap, cnt in stats["encapsulated_protocol_distribution"].items():
        print(f"     - {encap:<18}: {cnt:>5} packets")
    print("   Label Type Distribution:")
    for lbl, cnt in stats["label_type_distribution"].items():
        print(f"     - {lbl:<18}: {cnt:>5} PDUs")
    print(sep)

    if args.details:
        print("\nDECODED PDU INVENTORY:")
        print(f" {'Idx':>3} | {'Frag':<13} | {'GSE Len':>7} | {'Protocol':<12} | {'Label (Hex)':<14} | {'Encap':<6} | {'Payload':>7}")
        print("-" * 75)
        for i, p in enumerate(pdus):
            if p.is_unfragmented:
                frag_str = "Unfragmented"
            elif p.is_first_fragment:
                frag_str = f"First (id={p.frag_id})"
            elif p.is_intermediate_fragment:
                frag_str = f"Mid (id={p.frag_id})"
            elif p.is_last_fragment:
                frag_str = f"Last (id={p.frag_id})"
            else:
                frag_str = "Padding"

            proto_str = p.protocol_name if p.protocol_name else "N/A"
            label_hex = p.label.hex() if p.label else "None"
            encap_str = p.encapsulated_protocol or "None"
            print(f" {i+1:>3} | {frag_str:<13} | {p.gse_length:>7} | {proto_str:<12} | {label_hex:<14} | {encap_str:<6} | {p.payload_length:>7}B")
        print("=" * 75)


if __name__ == "__main__":
    main()
