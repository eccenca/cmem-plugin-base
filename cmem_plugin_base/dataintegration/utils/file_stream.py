"""Stream utilities for handling file streams in plugins."""

import gzip
import io
from typing import IO


def _is_gzip(stream: io.BufferedReader) -> bool:
    head = stream.read(2)
    stream.seek(0)
    return head == b"\x1f\x8b"


def prepare_stream_for_processing(
    input_stream: IO[bytes],
) -> tuple[io.TextIOWrapper | IO[bytes], bool]:
    """Prepare a file stream for processing.

    This utility function simplifies the common pattern of:
    1. Detecting if the stream is gzip compressed
    2. Decompressing if needed
    3. Detecting if the content is text or binary
    4. Returning appropriate stream wrapper

    Args:
        input_stream: The input stream to process (should be in binary mode)

    Returns:
        A tuple containing:
        - The processed stream (TextIOWrapper for text, original stream for binary)
        - Boolean indicating if the content is text (True) or binary (False)

    Example:
        ```python
        with file.read_stream(context.task.project_id()) as input_file:
            stream, is_text = prepare_stream_for_processing(input_file)
            # Use the stream directly for upload or processing
            if is_text:
                # Handle as text stream
                content = stream.read()
            else:
                # Handle as binary stream
                content = stream.read()
        ```

    """
    buffered = io.BufferedReader(input_stream)  # type: ignore[type-var]

    decompressed_stream = gzip.GzipFile(fileobj=buffered) if _is_gzip(buffered) else buffered  # type: ignore[arg-type]

    sample = decompressed_stream.read(1024)
    decompressed_stream.seek(0)

    try:
        sample.decode("utf-8")
        is_text = True
        stream_for_processing = io.TextIOWrapper(decompressed_stream, encoding="utf-8")
    except UnicodeDecodeError:
        is_text = False
        stream_for_processing = decompressed_stream  # type: ignore[assignment]

    return stream_for_processing, is_text
