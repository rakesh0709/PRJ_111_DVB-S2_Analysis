"""
Base Parser Interface and Custom Exceptions for DVB-S2 Stream Parsers.

Defines the contract all stream decoders (MPEG-TS, BBFrame, GSE) adhere to,
ensuring consistent error handling and metric extraction.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, Iterator, Union


class StreamParserError(Exception):
    """Base exception for all stream parsing errors."""
    pass


class PacketCorruptionError(StreamParserError):
    """Raised when a packet header or structure violates protocol specification."""
    pass


class SyncLossError(StreamParserError):
    """Raised when synchronization with stream boundaries is lost."""
    pass


class BaseStreamParser(ABC):
    """
    Abstract Base Class for all stream format parsers.
    Each supported format (MPEG-TS, BBFrame, GSE) implements this interface.
    """

    @abstractmethod
    def parse_file(
        self,
        file_path: Union[str, Path],
        max_packets: Union[int, None] = None
    ) -> Iterator[Any]:
        """
        Parses a stream file, yielding structured packet objects.

        Args:
            file_path: Path to the input file.
            max_packets: Optional upper bound on packets to process.

        Yields:
            Decoded packet representations.
        """
        raise NotImplementedError

    @abstractmethod
    def get_statistics(self) -> Dict[str, Any]:
        """
        Returns accumulated diagnostic metrics and counts for the parsed stream.
        """
        raise NotImplementedError
