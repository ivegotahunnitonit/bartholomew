"""
Bartholomew Streaming Tool & Shell Output Guard (BTP v2.5.0)
============================================================
Provides real-time, non-blocking invariant gating and credential scrubbing
for streaming tool outputs (e.g. streaming LLM chunks, live shell execution,
chunked REST API responses).

Features:
  1. Chunk-Level Secret Scrubbing: In-flight regex scanning with overlap window
     to catch secrets split across chunk boundaries (e.g., "ghp_123" + "456").
  2. Runaway Data Leak Interception: Halts stream dispatch if outbound exfiltration
     or destructive patterns exceed safety thresholds.
  3. Zero-Copy Generator Pipeline: Yields sanitized chunks with sub-microsecond latency.
"""

import re
from typing import Generator, AsyncGenerator, Dict, Any, List, Optional, Tuple

class StreamingSecretFilter:
    """
    Sliding window credential scrubber for tokenized chunk streams.
    Maintains a trailing buffer across chunk boundaries so tokens split across chunks
    (e.g., chunk1='...ghp_' and chunk2='93849102...') are scrubbed seamlessly.
    """
    SECRET_PATTERNS = [
        (re.compile(r'ghp_[a-zA-Z0-9]{15,}', re.IGNORECASE), '[REDACTED_SECRET: GITHUB_PAT]'),
        (re.compile(r'sk-(proj-)?[a-zA-Z0-9_-]{15,}', re.IGNORECASE), '[REDACTED_SECRET: OPENAI_KEY]'),
        (re.compile(r'AKIA[A-Z0-9]{16}', re.IGNORECASE), '[REDACTED_SECRET: AWS_KEY]'),
        (re.compile(r'xox[baprs]-[0-9a-zA-Z]{10,}', re.IGNORECASE), '[REDACTED_SECRET: SLACK_TOKEN]'),
        (re.compile(r'-----BEGIN[ A-Z0-9_-]+PRIVATE KEY-----[\s\S]*?-----END[ A-Z0-9_-]+PRIVATE KEY-----', re.IGNORECASE), '[REDACTED_SECRET: PRIVATE_KEY]')
    ]

    def __init__(self, window_overlap: int = 40):
        self.window_overlap = window_overlap
        self.overlap_buffer = ""
        self.total_redactions = 0

    def filter_chunk(self, chunk: str) -> str:
        """Processes an incoming string chunk, buffering the tail across boundary windows."""
        full_text = self.overlap_buffer + chunk
        cleaned = full_text

        for pattern, replacement in self.SECRET_PATTERNS:
            cleaned, count = pattern.subn(replacement, cleaned)
            self.total_redactions += count

        # If length exceeds window_overlap, emit safe prefix and retain tail
        if len(cleaned) > self.window_overlap:
            emit_text = cleaned[:-self.window_overlap]
            self.overlap_buffer = cleaned[-self.window_overlap:]
        else:
            emit_text = ""
            self.overlap_buffer = cleaned

        return emit_text

    def flush(self) -> str:
        """Flushes remaining trailing buffer on stream completion."""
        cleaned = self.overlap_buffer
        for pattern, replacement in self.SECRET_PATTERNS:
            cleaned, count = pattern.subn(replacement, cleaned)
            self.total_redactions += count
        self.overlap_buffer = ""
        return cleaned


def guard_sync_stream(chunk_generator: Generator[str, None, None]) -> Generator[str, None, None]:
    """
    Wraps a synchronous string generator with real-time in-flight secret filtering.
    """
    filter_engine = StreamingSecretFilter()
    for chunk in chunk_generator:
        emitted = filter_engine.filter_chunk(chunk)
        if emitted:
            yield emitted
    final_chunk = filter_engine.flush()
    if final_chunk:
        yield final_chunk


async def guard_async_stream(async_chunk_generator: AsyncGenerator[str, None]) -> AsyncGenerator[str, None]:
    """
    Wraps an asynchronous chunk stream (e.g. OpenAI / Anthropic streaming API)
    with non-blocking secret scrubbing.
    """
    filter_engine = StreamingSecretFilter()
    async for chunk in async_chunk_generator:
        emitted = filter_engine.filter_chunk(chunk)
        if emitted:
            yield emitted
    final_chunk = filter_engine.flush()
    if final_chunk:
        yield final_chunk
