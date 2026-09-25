"""
PRJ_111: DVB-S2 Receiver Output Stream Analysis and Processing System.

This package provides a unified platform for ingesting, parsing, preprocessing,
feature extraction, and intelligent analysis of DVB-S2 receiver output streams
across three alternative formats:
  1. Baseband (BB) Frames
  2. Generic Stream Encapsulation (GSE)
  3. MPEG Transport Streams (TS)
"""

__version__ = "0.1.0"
__project_id__ = "PRJ_111"
__all__ = [
    "config",
    "ingestion",
    "parsers",
    "preprocessing",
    "features",
    "analysis",
]
