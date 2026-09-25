"""
Global Configuration and Constants for PRJ_111 DVB-S2 Stream Analyzer.

Defines project directory paths, protocol-specific framing constants,
supported stream formats, and unified logging setup.
"""

from enum import Enum
import logging
from pathlib import Path
from typing import Optional


# -----------------------------------------------------------------------------
# Directory Layout
# -----------------------------------------------------------------------------
PACKAGE_DIR = Path(__file__).resolve().parent
CODE_DIR = PACKAGE_DIR.parent
PROJECT_ROOT = CODE_DIR.parent

RAW_DATA_DIR = PROJECT_ROOT / "01_RAW_DATA"
PROCESSED_DATA_DIR = PROJECT_ROOT / "02_PROCESSED_DATA"
FEATURE_DATA_DIR = PROJECT_ROOT / "03_FEATURE_DATA"
MODELS_DIR = PROJECT_ROOT / "04_AI_MODELS"
RESULTS_DIR = PROJECT_ROOT / "06_RESULTS"
DOCUMENTATION_DIR = PROJECT_ROOT / "07_DOCUMENTATION"


# -----------------------------------------------------------------------------
# Supported Stream Formats (Alternative Ingestion Types)
# -----------------------------------------------------------------------------
class StreamFormat(str, Enum):
    """
    Alternative stream formats accepted by the DVB-S2 receiver output analyzer.
    These are treated as distinct input alternatives, not a sequential chain.
    """
    BB_FRAME = "BB_FRAME"    # DVB-S2 Baseband Frames (ETSI EN 302 307)
    GSE = "GSE"              # Generic Stream Encapsulation (ETSI TS 102 606)
    MPEG_TS = "MPEG_TS"      # MPEG Transport Stream (ISO/IEC 13818-1)
    UNKNOWN = "UNKNOWN"


# -----------------------------------------------------------------------------
# MPEG Transport Stream (TS) Protocol Constants (ISO/IEC 13818-1)
# -----------------------------------------------------------------------------
TS_PACKET_SIZE: int = 188
TS_SYNC_BYTE: int = 0x47
TS_NULL_PID: int = 0x1FFF        # 8191 decimal
TS_MAX_PID: int = 0x1FFF         # 13-bit unsigned int
TS_HEADER_SIZE: int = 4
TS_CONTINUITY_COUNTER_MOD: int = 16

# Adaptation Field Control flags
AFC_RESERVED: int = 0b00
AFC_PAYLOAD_ONLY: int = 0b01
AFC_ADAPTATION_ONLY: int = 0b10
AFC_ADAPTATION_AND_PAYLOAD: int = 0b11


# -----------------------------------------------------------------------------
# DVB-S2 Baseband (BB) Frame Protocol Constants (ETSI EN 302 307)
# -----------------------------------------------------------------------------
BB_HEADER_SIZE_BYTES: int = 10
BB_CRC8_POLYNOMIAL: int = 0xD5


# -----------------------------------------------------------------------------
# Generic Stream Encapsulation (GSE) Constants (ETSI TS 102 606)
# -----------------------------------------------------------------------------
GSE_MIN_HEADER_SIZE: int = 2


# -----------------------------------------------------------------------------
# Logging Setup
# -----------------------------------------------------------------------------
def configure_logging(
    level: int = logging.INFO,
    log_format: Optional[str] = None
) -> None:
    """
    Configures centralized console logging for the analyzer application.
    """
    if log_format is None:
        log_format = "[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s"

    logging.basicConfig(
        level=level,
        format=log_format,
        datefmt="%Y-%m-%d %H:%M:%S"
    )
