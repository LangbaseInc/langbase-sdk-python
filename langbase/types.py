"""
Type definitions for the Langbase SDK.

This module defines the various data structures and type hints used
throughout the SDK to provide better code assistance and documentation.
"""
from typing import Dict, List, Optional, Union, Any, TypedDict, Literal, Protocol, runtime_checkable
from typing_extensions import NotRequired


# Base types and constants
GENERATION_ENDPOINTS = [
    '/v1/pipes/run',
    '/beta/chat',
    '/beta/generate',
    '/v1/agent/run',
]

# Role types
Role = Literal["user", "assistant", "system", "tool"]

# Embedding models
EmbeddingModel = Literal[
    "openai:text-embedding-3-large",
    "cohere:embed-multilingual-v3.0",
    "cohere:embed-multilingual-light-v3.0",
    "google:text-embedding-004"
]

# Content types for documents
ContentType = Literal[
    "application/pdf",
    "text/plain",
    "text/markdown",
    "text/csv",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "application/vnd.ms-excel"
]


# Function and tool types
class Function(TypedDict):
    """Function definition for tool calls."""
    name: str
    arguments: str


class ToolCall(TypedDict):
    """Tool call definition."""
    id: str
    type: Literal["function"]
    function: Function


class ToolFunction(TypedDict):
    """Function definition for tools."""
    name: str
    description: NotRequired[str]
    parameters: NotRequired[Dict[str, Any]]


class Tools(TypedDict):
    """Tool definition."""
    type: Literal["function"]
    function: ToolFunction


class ToolChoice(TypedDict):
    """Tool choice definition."""
    type: Literal["function"]
    function: Dict[str, str]


# Message types
class MessageContentItem(TypedDict, total=False):
    """Content item for a message with multiple content parts."""
    type: str
    text: Optional[str]
    image_url: Optional[Dict[str, str]]
    cache_control: Optional[Dict[str, str]]


class Message(TypedDict, total=False):
    """Basic message structure."""
    role: Role
    content: Optional[Union[str, List[MessageContentItem]]]
    name: Optional[str]
    tool_call_id: Optional[str]
    tool_calls: Optional[List[ToolCall]]


class ThreadMessage(Message, total=False):
    """Message structure with thread-specific fields."""
    attachments: Optional[List[Any]]
    metadata: Optional[Dict[str, str]]


# Variable definition
class Variable(TypedDict):
    """Variable definition for pipe templates."""
    name: str
    value: str


# Response types
class Usage(TypedDict):
    """Token usage information."""
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


class ChoiceGenerate(TypedDict):
    """Generation choice structure."""
    index: int
    message: Message
    logprobs: Optional[bool]
    finish_reason: str


class ResponseFormat(TypedDict, total=False):
    """Response format configuration."""
    type: Literal["text", "json_object", "json_schema"]
    json_schema: Optional[Dict[str, Any]]


# Option types
class RunOptionsBase(TypedDict, total=False):
    """Base options for running a pipe."""
    messages: List[Message]
    variables: List[Variable]
    thread_id: str
    raw_response: bool
    run_tools: bool
    tools: List[Tools]
    name: str
    api_key: str
    llm_key: str
    json: bool


class RunOptions(RunOptionsBase, total=False):
    """Options for running a pipe without streaming."""
    stream: Literal[False]


class RunOptionsStream(RunOptionsBase):
    """Options for running a pipe with streaming."""
    stream: Literal[True]


class LlmOptionsBase(TypedDict):
    """Base options for running an LLM."""
    messages: List[Message]
    model: str
    llm_key: str
    top_p: NotRequired[float]
    max_tokens: NotRequired[int]
    temperature: NotRequired[float]
    presence_penalty: NotRequired[float]
    frequency_penalty: NotRequired[float]
    stop: NotRequired[List[str]]
    tools: NotRequired[List[Tools]]
    tool_choice: NotRequired[Union[Literal['auto', 'required'], ToolChoice]]
    parallel_tool_calls: NotRequired[bool]
    reasoning_effort: NotRequired[Optional[str]]
    max_completion_tokens: NotRequired[int]
    response_format: NotRequired[ResponseFormat]
    custom_model_params: NotRequired[Dict[str, Any]]


class LlmOptions(LlmOptionsBase, total=False):
    """Options for running an LLM without streaming."""
    stream: Literal[False]


class LlmOptionsStream(LlmOptionsBase):
    """Options for running an LLM with streaming."""
    stream: Literal[True]


# Response types
class RawResponseHeaders(TypedDict):
    """Raw response headers."""
    headers: Dict[str, str]


class RunResponse(TypedDict, total=False):
    """Response from running a pipe."""
    completion: str
    thread_id: str
    id: str
    object: str
    created: int
    model: str
    choices: List[ChoiceGenerate]
    usage: Usage
    system_fingerprint: Optional[str]
    raw_response: Optional[RawResponseHeaders]
    messages: List[Message]
    llm_key: str
    name: str


class RunResponseStream(TypedDict, total=False):
    """Stream response from running a pipe."""
    stream: Any  # This would be an iterator in Python
    thread_id: Optional[str]
    raw_response: Optional[RawResponseHeaders]


# Memory types
class MemoryCreateOptions(TypedDict, total=False):
    """Options for creating a memory."""
    name: str
    description: str
    embedding_model: EmbeddingModel


class MemoryDeleteOptions(TypedDict):
    """Options for deleting a memory."""
    name: str


class MemoryFilter(List):
    """Filter for memory retrieval."""
    pass


class MemoryConfig(TypedDict):
    """Memory configuration for retrieval."""
    name: str
    filters: NotRequired[MemoryFilter]


class MemoryRetrieveOptions(TypedDict, total=False):
    """Options for retrieving from memory."""
    query: str
    memory: List[MemoryConfig]
    top_k: int


class MemoryListDocOptions(TypedDict):
    """Options for listing documents in a memory."""
    memory_name: str


class MemoryDeleteDocOptions(TypedDict):
    """Options for deleting a document from memory."""
    memory_name: str
    document_name: str


class MemoryRetryDocEmbedOptions(TypedDict):
    """Options for retrying embedding generation for a document."""
    memory_name: str
    document_name: str


class MemoryUploadDocOptions(TypedDict, total=False):
    """Options for uploading a document to memory."""
    memory_name: str
    document_name: str
    meta: Dict[str, str]
    document: Any  # This would be bytes, file-like object, etc.
    content_type: ContentType


# Response types for memory
class MemoryBaseResponse(TypedDict):
    """Base response for memory operations."""
    name: str
    description: str
    owner_login: str
    url: str


class MemoryCreateResponse(MemoryBaseResponse):
    """Response from creating a memory."""
    embedding_model: EmbeddingModel


class MemoryListResponse(MemoryBaseResponse):
    """Response from listing memories."""
    embedding_model: EmbeddingModel


class BaseDeleteResponse(TypedDict):
    """Base response for delete operations."""
    success: bool


class MemoryDeleteResponse(BaseDeleteResponse):
    """Response from deleting a memory."""
    pass


class MemoryDeleteDocResponse(BaseDeleteResponse):
    """Response from deleting a document from memory."""
    pass


class MemoryRetryDocEmbedResponse(BaseDeleteResponse):
    """Response from retrying document embedding."""
    pass


class MemoryRetrieveResponse(TypedDict):
    """Response from retrieving from memory."""
    text: str
    similarity: float
    meta: Dict[str, str]


class MemoryDocMetadata(TypedDict):
    """Metadata for a document in memory."""
    size: int
    type: ContentType


class MemoryListDocResponse(TypedDict):
    """Response from listing documents in memory."""
    name: str
    status: Literal['queued', 'in_progress', 'completed', 'failed']
    status_message: Optional[str]
    metadata: MemoryDocMetadata
    enabled: bool
    chunk_size: int
    chunk_overlap: int
    owner_login: str


# Tool types
class ToolWebSearchOptions(TypedDict, total=False):
    """Options for web search."""
    query: str
    service: Literal['exa']
    total_results: int
    domains: List[str]
    api_key: str

class EmbedOptions(TypedDict, total=False):
    """Options for embedding generation."""
    chunks: List[str]
    embedding_model: EmbeddingModel


EmbedResponse = List[List[float]]


class ToolWebSearchResponse(TypedDict):
    """Response from web search."""
    url: str
    content: str


class ToolCrawlOptions(TypedDict, total=False):
    """Options for web crawling."""
    url: List[str]
    max_pages: int
    api_key: str


class ToolCrawlResponse(TypedDict):
    """Response from web crawling."""
    url: str
    content: str


# Embed types
class EmbedOptions(TypedDict, total=False):
    """Options for embedding generation."""
    chunks: List[str]
    embedding_model: EmbeddingModel


EmbedResponse = List[List[float]]


# Chunk types
class ChunkOptions(TypedDict, total=False):
    """Options for chunking a document."""
    document: Any  # This would be bytes, file-like object, etc.
    document_name: str
    content_type: ContentType
    chunk_max_length: str
    chunk_overlap: str
    separator: str


ChunkResponse = List[str]


# Parse types
class ParseOptions(TypedDict):
    """Options for parsing a document."""
    document: Any  # This would be bytes, file-like object, etc.
    document_name: str
    content_type: ContentType


class ParseResponse(TypedDict):
    """Response from parsing a document."""
    document_name: str
    content: str


# Thread types
class ThreadsCreate(TypedDict, total=False):
    """Options for creating a thread."""
    thread_id: str
    metadata: Dict[str, str]
    messages: List[ThreadMessage]


class ThreadsUpdate(TypedDict):
    """Options for updating a thread."""
    thread_id: str
    metadata: Dict[str, str]


class ThreadsGet(TypedDict):
    """Options for getting a thread."""
    thread_id: str


class DeleteThreadOptions(TypedDict):
    """Options for deleting a thread."""
    thread_id: str


class ThreadsBaseResponse(TypedDict):
    """Base response for thread operations."""
    id: str
    object: Literal['thread']
    created_at: int
    metadata: Dict[str, str]


class ThreadMessagesCreate(TypedDict):
    """Options for creating messages in a thread."""
    thread_id: str
    messages: List[ThreadMessage]


class ThreadMessagesList(TypedDict):
    """Options for listing messages in a thread."""
    thread_id: str


class ThreadMessagesBaseResponse(TypedDict, total=False):
    """Base response for thread message operations."""
    id: str
    created_at: int
    thread_id: str
    role: Role
    content: Optional[str]
    name: Optional[str]
    tool_call_id: Optional[str]
    tool_calls: Optional[List[ToolCall]]
    attachments: Optional[List[Any]]
    metadata: Optional[Dict[str, str]]


# Config types
class LangbaseOptions(TypedDict, total=False):
    """Options for initializing Langbase client."""
    api_key: str
    base_url: Literal['https://api.langbase.com', 'https://eu-api.langbase.com']


# Protocol for file-like objects
@runtime_checkable
class FileProtocol(Protocol):
    """Protocol for file-like objects."""
    def read(self, size: int = -1) -> bytes: ...


# Workflow types
class WorkflowContext(TypedDict):
    """Context for workflow execution containing step outputs."""
    outputs: Dict[str, Any]


class RetryConfig(TypedDict):
    """Configuration for step retry behavior."""
    limit: int
    delay: int
    backoff: Literal['exponential', 'linear', 'fixed']


class StepConfig(TypedDict, total=False):
    """Configuration for a workflow step."""
    id: str
    timeout: Optional[int]
    retries: Optional[RetryConfig]
    run: Any  # Callable[[], Awaitable[T]] - using Any for simplicity in TypedDict
