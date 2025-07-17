import json
from typing import Any, Dict, Iterator, List, Literal, Optional, Union

from .types import ToolCall

# Type aliases to match TypeScript version
MessageRole = Literal["function", "assistant", "system", "user", "tool"]

# Interface aliases for consistency with TypeScript
ToolCallResult = ToolCall


class Delta(dict):
    """Represents a delta object in a streaming chunk."""

    @property
    def role(self) -> Optional[MessageRole]:
        """Get the role from the delta."""
        return self.get("role")

    @property
    def content(self) -> Optional[str]:
        """Get the content from the delta."""
        return self.get("content")

    @property
    def tool_calls(self) -> Optional[List[ToolCall]]:
        """Get the tool calls from the delta."""
        return self.get("tool_calls")


class ChoiceStream(dict):
    """Represents a choice object in a streaming chunk."""

    @property
    def index(self) -> int:
        """Get the choice index."""
        return self.get("index", 0)

    @property
    def delta(self) -> Delta:
        """Get the delta object."""
        return Delta(self.get("delta", {}))

    @property
    def logprobs(self) -> Optional[bool]:
        """Get the logprobs value."""
        return self.get("logprobs")

    @property
    def finish_reason(self) -> Optional[str]:
        """Get the finish reason."""
        return self.get("finish_reason")


class ChunkStream(dict):
    """Represents a streaming chunk from the API."""

    @property
    def id(self) -> str:
        """Get the chunk ID."""
        return self.get("id", "")

    @property
    def object(self) -> str:
        """Get the object type."""
        return self.get("object", "")

    @property
    def created(self) -> int:
        """Get the creation timestamp."""
        return self.get("created", 0)

    @property
    def model(self) -> str:
        """Get the model name."""
        return self.get("model", "")

    @property
    def choices(self) -> List[ChoiceStream]:
        """Get the list of choices."""
        return [ChoiceStream(choice) for choice in self.get("choices", [])]


def get_text_part(chunk: Union[ChunkStream, Dict[str, Any]]) -> str:
    """
    Retrieves the text part from a given ChunkStream.

    Args:
        chunk: The ChunkStream object or dictionary.

    Returns:
        The text content of the first choice's delta, or an empty string if it doesn't exist.
    """
    if isinstance(chunk, dict) and not isinstance(chunk, ChunkStream):
        chunk = ChunkStream(chunk)

    return chunk.choices[0].delta.content or "" if chunk.choices else ""


def parse_chunk(chunk_data: Union[bytes, str]) -> Optional[ChunkStream]:
    """
    Parse a raw chunk from the stream into a ChunkStream object.

    Args:
        chunk_data: Raw chunk data from the stream (bytes or string)

    Returns:
        Parsed ChunkStream object or None if parsing fails
    """
    try:
        # Handle both bytes and string input
        if isinstance(chunk_data, bytes):
            chunk_str = chunk_data.decode("utf-8")
        else:
            chunk_str = chunk_data

        # Skip empty chunks
        if not chunk_str.strip():
            return None

        # Handle SSE format - remove "data: " prefix if present
        if chunk_str.startswith("data: "):
            json_str = chunk_str[6:]  # Remove "data: " prefix
        else:
            json_str = chunk_str

        # Skip if it's just whitespace after removing prefix
        if not json_str.strip():
            return None

        # Try to parse as JSON
        chunk_dict = json.loads(json_str)
        return ChunkStream(chunk_dict)

    except (json.JSONDecodeError, UnicodeDecodeError):
        return None


def stream_text(stream: Iterator[Union[bytes, str]]) -> Iterator[str]:
    """
    Generator that yields text content from a stream of chunks.

    Supports various stream sources including response.iter_lines(),
    SSE streams, and raw byte iterators.

    Args:
        stream: Iterator of raw chunk bytes (e.g., from response.iter_lines())

    Yields:
        Text content from each chunk

    Example:
        >>> for text in stream_text(response.iter_lines()):
        ...     print(text, end="", flush=True)
    """
    for chunk_data in stream:
        if chunk_data:
            chunk = parse_chunk(chunk_data)
            if chunk:
                text = get_text_part(chunk)
                if text:
                    yield text


def collect_stream_text(stream: Iterator[Union[bytes, str]]) -> str:
    """
    Collect all text content from a stream.

    Args:
        stream: Iterator of raw chunk bytes

    Returns:
        Complete text content from the stream
    """
    return "".join(stream_text(stream))


def get_tools_from_stream(stream: Iterator[Union[bytes, str]]) -> List[ToolCall]:
    """
    Extract tool calls from a streaming response.

    This function properly assembles tool calls from streaming chunks.
    In streaming responses, tool calls come in parts:
    1. First chunk: tool call metadata (id, type, function name)
    2. Subsequent chunks: incremental function arguments that need to be concatenated

    Args:
        stream: Iterator of raw chunk data (bytes or strings)

    Returns:
        List of complete tool calls assembled from the stream
    """
    # Dictionary to accumulate tool calls by index
    tool_calls_accumulator: Dict[int, ToolCall] = {}

    for chunk_data in stream:
        if chunk_data:
            chunk = parse_chunk(chunk_data)
            if chunk and chunk.choices:
                delta_tool_calls = chunk.choices[0].delta.tool_calls
                if delta_tool_calls:
                    for delta_tool_call in delta_tool_calls:
                        # Get the index of this tool call
                        index = delta_tool_call.get("index", 0)

                        # Initialize the tool call if it doesn't exist
                        if index not in tool_calls_accumulator:
                            tool_calls_accumulator[index] = {
                                "id": "",
                                "type": "function",
                                "function": {"name": "", "arguments": ""},
                            }

                        # Update with new information from this chunk
                        if "id" in delta_tool_call:
                            tool_calls_accumulator[index]["id"] = delta_tool_call["id"]

                        if "type" in delta_tool_call:
                            tool_calls_accumulator[index]["type"] = delta_tool_call[
                                "type"
                            ]

                        if "function" in delta_tool_call:
                            function_data = delta_tool_call["function"]

                            if "name" in function_data:
                                tool_calls_accumulator[index]["function"][
                                    "name"
                                ] = function_data["name"]

                            if "arguments" in function_data:
                                # Accumulate arguments by concatenating them
                                tool_calls_accumulator[index]["function"][
                                    "arguments"
                                ] += function_data["arguments"]

    # Return the assembled tool calls as a list, sorted by index
    return [tool_calls_accumulator[i] for i in sorted(tool_calls_accumulator.keys())]


def get_tools_from_run_stream(stream: Iterator[Union[bytes, str]]) -> List[ToolCall]:
    """
    Retrieves tools from a readable stream asynchronously.

    Args:
        stream: The stream to extract tools from

    Returns:
        List of tool calls extracted from the stream
    """
    return get_tools_from_stream(stream)


def get_tools_from_run(response: Dict[str, Any]) -> List[ToolCall]:
    """
    Extracts tool calls from non-stream response.

    Args:
        response: The run response object

    Returns:
        List of tool calls. Returns empty list if no tools are present.
    """
    try:
        choices = response.get("choices", [])
        if choices:
            message = choices[0].get("message", {})
            tool_calls = message.get("tool_calls")
            return tool_calls or []
    except (KeyError, IndexError, TypeError):
        pass

    return []


def handle_response_stream(
    response: Any,
    raw_response: bool = False,
) -> Dict[str, Any]:
    """
    Handles the response stream from a given response object.

    Args:
        response: The API response to handle.
        raw_response: Optional flag to include raw response headers.

    Returns:
        Dictionary containing the processed stream, thread ID, and optionally raw response headers.
    """
    # Extract stream from response (assuming response has iter_lines method)
    stream = (
        response.iter_lines()
        if hasattr(response, "iter_lines")
        else response.get("stream")
    )

    # Try to get thread_id from response headers
    thread_id = None
    if hasattr(response, "headers"):
        thread_id = response.headers.get("lb-thread-id")
    elif isinstance(response, dict):
        thread_id = response.get("thread_id")

    result = {
        "stream": stream,
        "thread_id": thread_id,
    }

    if raw_response and hasattr(response, "headers"):
        result["raw_response"] = {"headers": dict(response.headers)}

    return result


class StreamProcessor:
    """
    A utility class for processing streaming responses with various methods.
    """

    def __init__(self, stream: Iterator[Union[bytes, str]]):
        """
        Initialize the stream processor.

        Args:
            stream: The raw stream iterator (bytes or strings)
        """
        self.stream = stream

    def text_generator(self) -> Iterator[str]:
        """
        Generator for text content from the stream.

        Yields:
            Text content from each chunk
        """
        yield from stream_text(self.stream)

    def collect_text(self) -> str:
        """
        Collect all text from the stream.

        Returns:
            Complete text content
        """
        return collect_stream_text(self.stream)

    def get_tool_calls(self) -> List[ToolCall]:
        """
        Extract tool calls from the stream.

        Returns:
            List of tool calls
        """
        return get_tools_from_stream(self.stream)

    def process_chunks(self) -> Iterator[ChunkStream]:
        """
        Generator for parsed chunks from the stream.

        Yields:
            Parsed ChunkStream objects
        """
        for chunk_data in self.stream:
            if chunk_data:
                chunk = parse_chunk(chunk_data)
                if chunk:
                    yield chunk


# Convenience function to create a stream processor
def create_stream_processor(stream: Iterator[Union[bytes, str]]) -> StreamProcessor:
    """
    Create a StreamProcessor instance.

    Args:
        stream: The raw stream iterator (bytes or strings)

    Returns:
        StreamProcessor instance
    """
    return StreamProcessor(stream)


def get_runner(
    response_or_stream: Union[Any, Iterator[Union[bytes, str]]],
) -> StreamProcessor:
    """
    Returns a runner (StreamProcessor) for the given response or stream.

    This is the Python equivalent to TypeScript's getRunner function.
    Provides a high-level interface for processing streaming responses.

    Can accept either:
    - A response dict (like from langbase.pipes.run()) with 'stream' key
    - A response object with iter_lines() method
    - A raw stream iterator

    Args:
        response_or_stream: Response dict, response object, or raw stream iterator

    Returns:
        StreamProcessor instance that can process the stream

    """
    # Handle dict response (Python langbase.pipes.run returns {'stream': ..., 'thread_id': ...})
    if isinstance(response_or_stream, dict) and "stream" in response_or_stream:
        stream = response_or_stream["stream"]
    # Handle response object with iter_lines method (raw HTTP response)
    elif hasattr(response_or_stream, "iter_lines"):
        stream = response_or_stream.iter_lines()
    # Handle already extracted stream iterator
    elif hasattr(response_or_stream, "__iter__"):
        stream = response_or_stream
    else:
        # Fallback: assume it's a stream
        stream = response_or_stream

    return StreamProcessor(stream)


def get_typed_runner(
    response_or_stream: Union[Any, Iterator[Union[bytes, str]]],
) -> "TypedStreamProcessor":
    """
    Returns a typed stream processor for the given response or stream.

    This provides an enhanced event-driven interface for processing streaming responses.

    Args:
        response_or_stream: Response dict, response object, or raw stream iterator

    Returns:
        TypedStreamProcessor instance with event-based handling
    """
    from .streaming import TypedStreamProcessor

    # Extract stream and thread_id
    thread_id = None

    # Handle dict response
    if isinstance(response_or_stream, dict) and "stream" in response_or_stream:
        stream = response_or_stream["stream"]
        thread_id = response_or_stream.get("thread_id")
    # Handle response object with iter_lines method
    elif hasattr(response_or_stream, "iter_lines"):
        stream = response_or_stream.iter_lines()
        if hasattr(response_or_stream, "headers"):
            thread_id = response_or_stream.headers.get("lb-thread-id")
    # Handle already extracted stream iterator
    elif hasattr(response_or_stream, "__iter__"):
        stream = response_or_stream
    else:
        # Fallback: assume it's a stream
        stream = response_or_stream

    return TypedStreamProcessor(stream, thread_id)


# Export all main components for easy access
__all__ = [
    "ChoiceStream",
    "ChunkStream",
    "Delta",
    "MessageRole",
    "StreamProcessor",
    "ToolCallResult",
    "collect_stream_text",
    "create_stream_processor",
    "get_runner",
    "get_text_part",
    "get_tools_from_run",
    "get_tools_from_run_stream",
    "get_tools_from_stream",
    "get_typed_runner",
    "handle_response_stream",
    "parse_chunk",
    "stream_text",
]
