#!/usr/bin/env python3
"""
Reproducible Analysis Script for Feature F1: Stream Health Analysis (PRJ_111).

Executes the end-to-end F1 pipeline against a selected DVB-S2 / MPEG Transport Stream:
  TS file -> StreamHandler -> TSParser -> FeatureExtractor -> HealthAnalyzer -> StreamHealthReport
"""

import argparse
import json
from pathlib import Path
import sys

# Ensure local dvbs2_analyzer package is resolvable
CURRENT_DIR = Path(__file__).resolve().parent
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))

from dvbs2_analyzer.analysis.health import HealthAnalyzer, HealthThresholds
from dvbs2_analyzer.config import RAW_DATA_DIR


def main():
    default_sample = RAW_DATA_DIR / "03_TS" / "DVBS2_toolkit" / "sample.ts"

    parser = argparse.ArgumentParser(
        description="PRJ_111: Feature F1 - DVB-S2 / MPEG-TS Stream Health Analysis Pipeline"
    )
    parser.add_argument(
        "file_path",
        nargs="?",
        default=str(default_sample),
        help=f"Path to the MPEG-TS file to analyze (default: {default_sample.name})",
    )
    parser.add_argument(
        "--max-packets",
        type=int,
        default=None,
        help="Upper bound on packets to decode (useful for fast validation on large captures)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output full structured report as formatted JSON",
    )
    parser.add_argument(
        "--details",
        action="store_true",
        help="Print detailed per-metric evaluations and PID distribution table",
    )

    args = parser.parse_args()
    target_file = Path(args.file_path)

    if not target_file.exists():
        print(f"Error: Target stream file does not exist: {target_file}", file=sys.stderr)
        sys.exit(1)

    analyzer = HealthAnalyzer()
    report = analyzer.analyze_file(target_file, max_packets=args.max_packets)

    if args.json:
        print(json.dumps(report.to_dict(), indent=2))
        return

    # Print the primary human-readable report
    print(report.format_text())

    # Optional detailed metrics view
    if args.details:
        print("\nDETAILED METRIC EVALUATIONS:")
        print("----------------------------")
        for ev in report.metric_evaluations:
            status_tag = f"[{ev.status.value}]"
            print(f"  {status_tag:<11} {ev.metric_name:<30}: {ev.formatted_value}")
            print(f"              Rule: {ev.threshold_applied}")
            print(f"              Note: {ev.interpretation}")

        print("\nPID DISTRIBUTION (Top 10):")
        print("--------------------------")
        sorted_pids = sorted(report.features.pid_distribution.items(), key=lambda x: x[1], reverse=True)
        for pid, count in sorted_pids[:10]:
            pct = report.features.pid_percentages.get(pid, 0.0)
            tag = "(NULL)" if pid == 8191 else ("(PAT)" if pid == 0 else "")
            print(f"  PID 0x{pid:04x} ({pid:>4}) {tag:<7}: {count:>8,} packets ({pct:>6.2f}%)")


if __name__ == "__main__":
    main()
