"""
Ingestion module for PRJ_111 DVB-S2 stream analyzer.
"""

from dvbs2_analyzer.ingestion.chunk_reader import (
    ChunkReader,
    read_chunks,
)
from dvbs2_analyzer.ingestion.stream_handler import (
    StreamHandler,
    StreamInfo,
    detect_stream_format,
)

__all__ = [
    "ChunkReader",
    "StreamFormat",
    "StreamHandler",
    "StreamInfo",
    "detect_stream_format",
    "read_chunks",
]

