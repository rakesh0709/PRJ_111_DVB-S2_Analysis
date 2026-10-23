"""
Chunk Reader and Stream Slicing Abstraction for PRJ_111.

Provides a reusable binary chunk iterator / reader for incremental stream
processing without requiring full-file in-memory accumulation. Tracks global
byte offsets and handles arbitrary chunk boundaries.
"""

import mmap
from io import BytesIO
from pathlib import Path
from typing import BinaryIO, Iterable, Iterator, Optional, Union


class ChunkReader:
    """
    Reusable binary chunk iterator / reader for incremental stream processing.

    Reads binary data in deterministic, configurable chunk sizes without
    loading the full file into memory. Tracks global byte offsets. Supports
    optional memory-mapped I/O (use_mmap=True) for large binary captures.

    Attributes:
        chunk_size: Target size in bytes for each chunk.
        total_bytes_read: Total number of bytes yielded across all chunks.
        global_offset: Current global byte position in the stream.
        chunk_count: Total number of chunks yielded so far.
        use_mmap: Whether memory-mapped reading is requested for file sources.
    """

    def __init__(
        self,
        source: Union[str, Path, BinaryIO, bytes, Iterable[bytes]],
        chunk_size: int = 65536,
        use_mmap: bool = False,
    ):
        """
        Initializes the ChunkReader.

        Args:
            source: File path, open binary stream, raw bytes, or iterable of byte chunks.
            chunk_size: Number of bytes per chunk (must be > 0).
            use_mmap: Whether to use memory-mapped I/O when reading from a file path.

        Raises:
            ValueError: If chunk_size <= 0.
        """
        if chunk_size <= 0:
            raise ValueError(f"chunk_size must be a positive integer, got: {chunk_size}")

        self.chunk_size = chunk_size
        self.use_mmap = use_mmap
        self._source = source
        self._bytes_read = 0
        self._chunk_count = 0
        self._file_handle: Optional[BinaryIO] = None
        self._mmap_handle: Optional[mmap.mmap] = None
        self._own_handle = False
        self._is_closed = False

    @property
    def total_bytes_read(self) -> int:
        """Returns total bytes yielded so far."""
        return self._bytes_read

    @property
    def global_offset(self) -> int:
        """Returns the current global byte offset into the stream."""
        return self._bytes_read

    @property
    def chunk_count(self) -> int:
        """Returns total number of chunks yielded so far."""
        return self._chunk_count

    def reset(self) -> None:
        """
        Resets reader position and counters to start of stream if seekable.
        """
        self._bytes_read = 0
        self._chunk_count = 0
        if hasattr(self._source, "seek") and callable(self._source.seek):
            try:
                self._source.seek(0)
            except (OSError, ValueError):
                pass
        elif self._file_handle is not None and hasattr(self._file_handle, "seek"):
            try:
                self._file_handle.seek(0)
            except (OSError, ValueError):
                pass
        elif isinstance(self._source, (str, Path)):
            self.close()

    def close(self) -> None:
        """Closes any file or mmap handles opened by this ChunkReader."""
        if self._mmap_handle is not None:
            try:
                self._mmap_handle.close()
            except Exception:
                pass
            self._mmap_handle = None

        if self._own_handle and self._file_handle is not None:
            try:
                self._file_handle.close()
            except Exception:
                pass
            self._file_handle = None
            self._own_handle = False
        self._is_closed = True

    def __enter__(self) -> "ChunkReader":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()

    def __iter__(self) -> Iterator[bytes]:
        """
        Yields binary chunks sequentially.
        """
        # Case 1: Raw bytes, bytearray, or memoryview (zero-copy chunking)
        if isinstance(self._source, (bytes, bytearray, memoryview)):
            mv = memoryview(self._source)
            for i in range(0, len(mv), self.chunk_size):
                chunk = bytes(mv[i : i + self.chunk_size])
                self._bytes_read += len(chunk)
                self._chunk_count += 1
                yield chunk
            return

        # Case 2: File path (str or Path)
        if isinstance(self._source, (str, Path)):
            path = Path(self._source).resolve()
            if not path.exists():
                raise FileNotFoundError(f"Input stream file not found: {path}")

            file_size = path.stat().st_size
            if file_size == 0:
                return

            if self.use_mmap:
                try:
                    with open(path, "rb") as f:
                        with mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as mm:
                            self._mmap_handle = mm
                            for i in range(0, file_size, self.chunk_size):
                                chunk = bytes(mm[i : i + self.chunk_size])
                                self._bytes_read += len(chunk)
                                self._chunk_count += 1
                                yield chunk
                            self._mmap_handle = None
                    return
                except (OSError, ValueError):
                    # Graceful fallback to buffered streaming if mmap is unbacked/fails
                    pass

            with open(path, "rb") as f:
                self._file_handle = f
                self._own_handle = False # managed by with block
                while True:
                    chunk = f.read(self.chunk_size)
                    if not chunk:
                        break
                    self._bytes_read += len(chunk)
                    self._chunk_count += 1
                    yield chunk
                self._file_handle = None
            return

        # Case 3: Open file-like binary stream
        if hasattr(self._source, "read") and callable(self._source.read):
            while True:
                chunk = self._source.read(self.chunk_size)
                if not chunk:
                    break
                self._bytes_read += len(chunk)
                self._chunk_count += 1
                yield chunk
            return

        # Case 4: Iterable of byte chunks
        if isinstance(self._source, Iterable):
            for raw_chunk in self._source:
                if not raw_chunk:
                    continue
                # If incoming chunk exceeds chunk_size, slice it
                if len(raw_chunk) > self.chunk_size:
                    for i in range(0, len(raw_chunk), self.chunk_size):
                        sub_chunk = raw_chunk[i : i + self.chunk_size]
                        self._bytes_read += len(sub_chunk)
                        self._chunk_count += 1
                        yield sub_chunk
                else:
                    self._bytes_read += len(raw_chunk)
                    self._chunk_count += 1
                    yield raw_chunk
            return

        raise TypeError(f"Unsupported source type for ChunkReader: {type(self._source)}")


def read_chunks(
    source: Union[str, Path, BinaryIO, bytes, Iterable[bytes]],
    chunk_size: int = 65536,
    use_mmap: bool = False,
) -> Iterator[bytes]:
    """
    Convenience generator function to iterate binary chunks from a source.

    Args:
        source: File path, open binary stream, raw bytes, or chunk iterable.
        chunk_size: Target size in bytes per chunk (default: 64 KB).
        use_mmap: Whether to use memory-mapped I/O for file paths.

    Yields:
        Binary chunks.
    """
    with ChunkReader(source, chunk_size=chunk_size, use_mmap=use_mmap) as reader:
        yield from reader
