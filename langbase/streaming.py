"""
Streaming utilities for the Langbase SDK.

This module provides typed event-based streaming interfaces for better developer experience.
"""

from enum import Enum
from typing import Any, Callable, Dict, Iterator, List, Optional, Union

from typing_extensions import Literal, TypedDict, TypeVar

from .helper import ChunkStream, parse_chunk
from .types import ToolCall


class StreamEventType(str, Enum):
    """Enum for all possible stream event types."""

    CONNECT = "connect"
    CONTENT = "content"
    TOOL_CALL = "tool_call"
    COMPLETION = "completion"
    ERROR = "error"
    END = "end"
    METADATA = "metadata"


class StreamEvent(TypedDict):
    """Base stream event."""

    type: StreamEventType
    timestamp: float


class ConnectEvent(StreamEvent):
    """Event fired when stream connection is established."""

    type: Literal[StreamEventType.CONNECT]
    threadId: Optional[str]


class ContentEvent(StreamEvent):
    """Event fired when text content is received."""

    type: Literal[StreamEventType.CONTENT]
    content: str
    chunk: ChunkStream


class ToolCallEvent(StreamEvent):
    """Event fired when a tool call is received."""

    type: Literal[StreamEventType.TOOL_CALL]
    toolCall: ToolCall
    index: int


class CompletionEvent(StreamEvent):
    """Event fired when the completion is done."""

    type: Literal[StreamEventType.COMPLETION]
    reason: str
    usage: Optional[Dict[str, int]]


class ErrorEvent(StreamEvent):
    """Event fired when an error occurs."""

    type: Literal[StreamEventType.ERROR]
    error: Exception
    message: str


class EndEvent(StreamEvent):
    """Event fired when the stream ends."""

    type: Literal[StreamEventType.END]
    duration: float


class MetadataEvent(StreamEvent):
    """Event fired when metadata is received."""

    type: Literal[StreamEventType.METADATA]
    metadata: Dict[str, Any]


# Union type for all events
Event = Union[
    ConnectEvent,
    ContentEvent,
    ToolCallEvent,
    CompletionEvent,
    ErrorEvent,
    EndEvent,
    MetadataEvent,
]

# Type for event handlers
T = TypeVar("T", bound=Event)
EventHandler = Callable[[T], None]


class TypedStreamProcessor:
    """
    Enhanced stream processor with typed events for better developer experience.

    This provides an event-driven interface similar to TypeScript/JavaScript patterns,
    making it easier to handle different aspects of streaming responses.
    """

    def __init__(
        self, stream: Iterator[Union[bytes, str]], thread_id: Optional[str] = None
    ):
        """
        Initialize the typed stream processor.

        Args:
            stream: The raw stream iterator
            thread_id: Optional thread ID from the response
        """
        self.stream = stream
        self.thread_id = thread_id
        self._handlers: Dict[StreamEventType, List[EventHandler]] = {}
        self._start_time = None
        self._tool_calls_accumulator: Dict[int, ToolCall] = {}

    def on(
        self, event: StreamEventType, handler: EventHandler
    ) -> "TypedStreamProcessor":
        """
        Register an event handler.

        Args:
            event: The event type to listen for
            handler: The handler function to call when the event occurs

        Returns:
            Self for method chaining
        """
        if event not in self._handlers:
            self._handlers[event] = []
        self._handlers[event].append(handler)
        return self

    def off(
        self, event: StreamEventType, handler: EventHandler
    ) -> "TypedStreamProcessor":
        """
        Remove an event handler.

        Args:
            event: The event type
            handler: The handler function to remove

        Returns:
            Self for method chaining
        """
        if event in self._handlers and handler in self._handlers[event]:
            self._handlers[event].remove(handler)
        return self

    def _emit(self, event: Event) -> None:
        """Emit an event to all registered handlers."""
        event_type = event["type"]
        if event_type in self._handlers:
            for handler in self._handlers[event_type]:
                try:
                    handler(event)
                except Exception as e:
                    # If error handler exists, use it, otherwise re-raise
                    if StreamEventType.ERROR in self._handlers:
                        self._emit(
                            ErrorEvent(
                                type=StreamEventType.ERROR,
                                timestamp=self._get_timestamp(),
                                error=e,
                                message=f"Error in {event_type} handler: {str(e)}",
                            )
                        )
                    else:
                        raise

    def _get_timestamp(self) -> float:
        """Get current timestamp in seconds."""
        import time

        return time.time()

    def process(self) -> None:
        """
        Process the stream and emit events.

        This method consumes the stream and emits appropriate events.
        Call this after registering all event handlers.
        """
        self._start_time = self._get_timestamp()

        # Emit connect event
        self._emit(
            ConnectEvent(
                type=StreamEventType.CONNECT,
                timestamp=self._start_time,
                threadId=self.thread_id,
            )
        )

        try:
            for chunk_data in self.stream:
                if chunk_data:
                    chunk = parse_chunk(chunk_data)
                    if chunk and chunk.choices:
                        choice = chunk.choices[0]

                        # Handle content
                        if choice.delta.content:
                            self._emit(
                                ContentEvent(
                                    type=StreamEventType.CONTENT,
                                    timestamp=self._get_timestamp(),
                                    content=choice.delta.content,
                                    chunk=chunk,
                                )
                            )

                        # Handle tool calls
                        if choice.delta.tool_calls:
                            self._process_tool_calls(choice.delta.tool_calls)

                        # Handle completion
                        if choice.finish_reason:
                            usage = (
                                chunk.get("usage") if isinstance(chunk, dict) else None
                            )
                            self._emit(
                                CompletionEvent(
                                    type=StreamEventType.COMPLETION,
                                    timestamp=self._get_timestamp(),
                                    reason=choice.finish_reason,
                                    usage=usage,
                                )
                            )

            # Emit any accumulated tool calls
            for index, tool_call in sorted(self._tool_calls_accumulator.items()):
                self._emit(
                    ToolCallEvent(
                        type=StreamEventType.TOOL_CALL,
                        timestamp=self._get_timestamp(),
                        toolCall=tool_call,
                        index=index,
                    )
                )

        except Exception as e:
            self._emit(
                ErrorEvent(
                    type=StreamEventType.ERROR,
                    timestamp=self._get_timestamp(),
                    error=e,
                    message=str(e),
                )
            )
            raise
        finally:
            # Always emit end event
            duration = (
                self._get_timestamp() - self._start_time if self._start_time else 0
            )
            self._emit(
                EndEvent(
                    type=StreamEventType.END,
                    timestamp=self._get_timestamp(),
                    duration=duration,
                )
            )

    def _process_tool_calls(self, delta_tool_calls: List[Dict[str, Any]]) -> None:
        """Process incremental tool call updates."""
        for delta_tool_call in delta_tool_calls:
            index = delta_tool_call.get("index", 0)

            # Initialize if not exists
            if index not in self._tool_calls_accumulator:
                self._tool_calls_accumulator[index] = {
                    "id": "",
                    "type": "function",
                    "function": {"name": "", "arguments": ""},
                }

            # Update with new data
            if "id" in delta_tool_call:
                self._tool_calls_accumulator[index]["id"] = delta_tool_call["id"]

            if "type" in delta_tool_call:
                self._tool_calls_accumulator[index]["type"] = delta_tool_call["type"]

            if "function" in delta_tool_call:
                func_data = delta_tool_call["function"]
                if "name" in func_data:
                    self._tool_calls_accumulator[index]["function"]["name"] = func_data[
                        "name"
                    ]
                if "arguments" in func_data:
                    self._tool_calls_accumulator[index]["function"][
                        "arguments"
                    ] += func_data["arguments"]

    def collect_text(self) -> str:
        """
        Collect all text content from the stream.

        Returns:
            Complete text content
        """
        text_parts = []

        def content_handler(event: ContentEvent) -> None:
            text_parts.append(event["content"])

        self.on(StreamEventType.CONTENT, content_handler)
        self.process()

        return "".join(text_parts)

    def collect_tool_calls(self) -> List[ToolCall]:
        """
        Collect all tool calls from the stream.

        Returns:
            List of tool calls
        """
        tool_calls = []

        def tool_handler(event: ToolCallEvent) -> None:
            tool_calls.append(event["toolCall"])

        self.on(StreamEventType.TOOL_CALL, tool_handler)
        self.process()

        return tool_calls

