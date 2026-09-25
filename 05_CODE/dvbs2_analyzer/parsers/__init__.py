"""
Stream Parsers Module for PRJ_111.

Contains independent decoders for the three alternative input stream formats:
  - Baseband (BB) Frames
  - Generic Stream Encapsulation (GSE)
  - MPEG Transport Stream (MPEG-TS)
"""

from dvbs2_analyzer.parsers.base import (
    BaseStreamParser,
    PacketCorruptionError,
    StreamParserError,
    SyncLossError,
)
from dvbs2_analyzer.parsers.bbframe_parser import (
    BBFrame,
    BBFrameParser,
    BBFrameStreamStatistics,
    crc8_dvbs2,
)
from dvbs2_analyzer.parsers.gse_parser import (
    GSEFragType,
    GSELabelType,
    GSEPDU,
    GSEParser,
    GSEStreamStatistics,
    GSE_PROTO_IPV4,
    GSE_PROTO_IPV6,
    GSE_PROTO_NPA_EXT,
)
from dvbs2_analyzer.parsers.ts_parser import (
    TSPacket,
    TSParser,
    TSStreamStatistics,
)

__all__ = [
    "BaseStreamParser",
    "StreamParserError",
    "PacketCorruptionError",
    "SyncLossError",
    "TSPacket",
    "TSParser",
    "TSStreamStatistics",
    "GSEParser",
    "GSEPDU",
    "GSELabelType",
    "GSEFragType",
    "GSEStreamStatistics",
    "GSE_PROTO_IPV4",
    "GSE_PROTO_IPV6",
    "GSE_PROTO_NPA_EXT",
    "BBFrame",
    "BBFrameParser",
    "BBFrameStreamStatistics",
    "crc8_dvbs2",
]
