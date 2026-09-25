"""
Preprocessing and Stream Sanitization Layer for PRJ_111.

Responsible for filtering corrupted packets, stripping null padding,
aligning time-series sequences, and preparing normalized data representations
for feature extraction and storage in 02_PROCESSED_DATA.
"""

from dataclasses import dataclass
import logging
from typing import Iterator, List

from dvbs2_analyzer.parsers.ts_parser import TSPacket

logger = logging.getLogger(__name__)


@dataclass
class PreprocessingOptions:
    """Configuration flags for stream sanitization."""
    filter_null_packets: bool = True
    drop_tei_corrupted: bool = True
    max_packets_buffer: int = 100000


@dataclass
class SanitizationSummary:
    """Summary of data removed or transformed during preprocessing."""
    input_packets: int = 0
    retained_packets: int = 0
    null_packets_dropped: int = 0
    tei_packets_dropped: int = 0


class StreamSanitizer:
    """
    Cleans and filters stream packets before feature extraction.
    """

    def __init__(self, options: PreprocessingOptions = PreprocessingOptions()):
        self.options = options
        self.summary = SanitizationSummary()

    def sanitize_packets(self, packets: Iterator[TSPacket]) -> Iterator[TSPacket]:
        """
        Yields filtered packets according to configured preprocessing rules.

        Args:
            packets: Stream of raw TSPacket objects.

        Yields:
            Sanitized TSPacket objects.
        """
        for pkt in packets:
            self.summary.input_packets += 1

            if self.options.drop_tei_corrupted and pkt.tei:
                self.summary.tei_packets_dropped += 1
                continue

            if self.options.filter_null_packets and pkt.is_null_packet:
                self.summary.null_packets_dropped += 1
                continue

            self.summary.retained_packets += 1
            yield pkt

    def get_summary(self) -> SanitizationSummary:
        """Returns sanitization counts."""
        return self.summary
