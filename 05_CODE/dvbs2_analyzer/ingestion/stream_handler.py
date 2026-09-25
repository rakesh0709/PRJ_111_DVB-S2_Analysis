"""
Input and Stream Handling Layer for PRJ_111.

Implements the multi-format ingestion gateway. Accepts DVB-S2 receiver output
in any of the three alternative formats:
  1. Baseband (BB) Frames
  2. Generic Stream Encapsulation (GSE)
  3. MPEG Transport Stream (TS)

Performs format identification (sniffing), validation, and delegates to the
appropriate parser.
"""

from dataclasses import dataclass
import logging
from pathlib import Path
from typing import Optional, Union

from dvbs2_analyzer.config import (
    CODE_DIR,
    PROJECT_ROOT,
    RAW_DATA_DIR,
    StreamFormat,
    TS_PACKET_SIZE,
    TS_SYNC_BYTE,
)
from dvbs2_analyzer.parsers.base import BaseStreamParser
from dvbs2_analyzer.parsers.ts_parser import TSParser

logger = logging.getLogger(__name__)


def _resolve_stream_path(file_path: Union[str, Path]) -> Path:
    """Safely resolves file paths against CWD, project root, CODE_DIR, uploads, and raw data."""
    p = Path(file_path)
    if p.is_absolute() and p.exists():
        return p.resolve()

    if p.exists():
        return p.resolve()

    clean_str = str(file_path).replace("\\", "/").strip("/")
    if clean_str.startswith("05_CODE/"):
        cand = (CODE_DIR / clean_str[len("05_CODE/"):]).resolve()
        if cand.exists():
            return cand

    if clean_str.startswith("01_RAW_DATA/"):
        cand = (RAW_DATA_DIR / clean_str[len("01_RAW_DATA/"):]).resolve()
        if cand.exists():
            return cand

    candidates = [
        (PROJECT_ROOT / file_path).resolve(),
        (CODE_DIR / file_path).resolve(),
        (RAW_DATA_DIR / file_path).resolve(),
        (CODE_DIR / "uploads" / p.name).resolve(),
        (CODE_DIR / "test_inputs" / p.name).resolve(),
    ]
    for c in candidates:
        if c.exists():
            return c

    # Search by unique filename in RAW_DATA_DIR as fallback
    matches = list(RAW_DATA_DIR.rglob(p.name))
    if len(matches) == 1 and matches[0].is_file():
        return matches[0].resolve()

    return (PROJECT_ROOT / file_path).resolve()


@dataclass
class StreamInfo:
    """Metadata describing an ingested input stream."""
    path: Path
    detected_format: StreamFormat
    file_size_bytes: int
    is_valid: bool
    description: str

    def to_dict(self) -> dict:
        """Converts stream info to serializable dictionary."""
        return {
            "path": str(self.path),
            "detected_format": self.detected_format.value,
            "file_size_bytes": self.file_size_bytes,
            "is_valid": self.is_valid,
            "description": self.description,
        }


def detect_stream_format(file_path: Union[str, Path]) -> StreamFormat:
    """
    Inspects stream binary headers to identify the format automatically.

    Args:
        file_path: Absolute or relative path to the stream file.

    Returns:
        Detected StreamFormat enum value.
    """
    path = _resolve_stream_path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Input stream does not exist: {path}")

    size = path.stat().st_size
    if size == 0:
        return StreamFormat.UNKNOWN

    with open(path, "rb") as f:
        header = f.read(min(size, 8192))

    # 1. Check for PCAP / PCAP-NG headers (encapsulating BBFrames)
    if len(header) >= 4:
        magic_4 = header[:4]
        if magic_4 == b"\x0a\x0d\x0d\x0a" or magic_4 in (b"\xa1\xb2\xc3\xd4", b"\xd4\xc3\xb2\xa1"):
            return StreamFormat.BB_FRAME

    # 2. Check for periodic MPEG-TS 188-byte framing with sync byte 0x47
    if len(header) >= TS_PACKET_SIZE:
        sync_hits = 0
        total_checks = min(len(header) // TS_PACKET_SIZE, 8)
        for i in range(total_checks):
            if header[i * TS_PACKET_SIZE] == TS_SYNC_BYTE:
                sync_hits += 1

        if total_checks > 0 and (sync_hits / total_checks) >= 0.75:
            return StreamFormat.MPEG_TS

    # Scan for periodic TS sync lock if leading packets suffered sync loss
    if len(header) >= TS_PACKET_SIZE * 5:
        max_scan = min(len(header) - TS_PACKET_SIZE * 5, 4096)
        for off in range(max_scan):
            if header[off] == TS_SYNC_BYTE:
                if all(header[off + k * TS_PACKET_SIZE] == TS_SYNC_BYTE for k in range(1, 5)):
                    return StreamFormat.MPEG_TS

    # 3. Check for GSE header characteristics (Content-based detection)
    from dvbs2_analyzer.parsers.gse_parser import GSEParser
    for offset in range(min(512, len(header) - 10)):
        if GSEParser._is_valid_bbheader(header[offset : offset + 10]):
            return StreamFormat.GSE

    if path.suffix.lower() == ".gse" or "gse" in path.name.lower() or "gse" in str(path.parent).lower():
        return StreamFormat.GSE

    # 4. Fallback for .pcap files
    if path.suffix.lower() == ".pcap":
        return StreamFormat.BB_FRAME

    return StreamFormat.UNKNOWN


class StreamHandler:
    """
    Entry point for ingesting and validating incoming DVB-S2 receiver output.
    """

    def __init__(
        self,
        file_path: Union[str, Path],
        forced_format: Optional[StreamFormat] = None
    ):
        """
        Initializes the StreamHandler for a given input file.

        Args:
            file_path: Path to the stream file.
            forced_format: Optional manual override of stream format.
        """
        self.path = _resolve_stream_path(file_path)
        if not self.path.exists():
            raise FileNotFoundError(f"Stream file not found: {self.path}")

        self.size_bytes = self.path.stat().st_size
        self.format = forced_format or detect_stream_format(self.path)
        logger.info(
            "Ingested stream %s (Format: %s, Size: %d bytes)",
            self.path.name, self.format.value, self.size_bytes
        )

    def get_stream_info(self) -> StreamInfo:
        """Returns structured metadata regarding the ingested stream."""
        descriptions = {
            StreamFormat.BB_FRAME: "DVB-S2 Baseband (BB) Frame Stream",
            StreamFormat.GSE: "Generic Stream Encapsulation (GSE) Stream",
            StreamFormat.MPEG_TS: "MPEG-2 Transport Stream (MPEG-TS)",
            StreamFormat.UNKNOWN: "Unrecognized / Unsupported Stream Format",
        }
        return StreamInfo(
            path=self.path,
            detected_format=self.format,
            file_size_bytes=self.size_bytes,
            is_valid=(self.format != StreamFormat.UNKNOWN),
            description=descriptions.get(self.format, "Unknown"),
        )

    def get_parser(self, strict_mode: bool = False) -> BaseStreamParser:
        """
        Instantiates and returns the appropriate parser for the stream format.

        Raises:
            NotImplementedError: If the format parser is still in development.
            ValueError: If the format is unknown.
        """
        if self.format == StreamFormat.MPEG_TS:
            return TSParser(strict_mode=strict_mode)
        elif self.format == StreamFormat.GSE:
            from dvbs2_analyzer.parsers.gse_parser import GSEParser
            return GSEParser(strict_mode=strict_mode)
        elif self.format == StreamFormat.BB_FRAME:
            from dvbs2_analyzer.parsers.bbframe_parser import BBFrameParser
            return BBFrameParser(strict_mode=strict_mode)
        else:
            raise ValueError(f"Cannot instantiate parser for unrecognized format: {self.format}")
