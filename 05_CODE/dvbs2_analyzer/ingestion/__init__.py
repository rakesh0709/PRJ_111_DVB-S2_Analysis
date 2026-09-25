"""
Ingestion module for PRJ_111 DVB-S2 stream analyzer.
"""

from dvbs2_analyzer.config import StreamFormat
from dvbs2_analyzer.ingestion.stream_handler import (
    StreamHandler,
    StreamInfo,
    detect_stream_format,
)

__all__ = [
    "StreamFormat",
    "StreamHandler",
    "StreamInfo",
    "detect_stream_format",
]
