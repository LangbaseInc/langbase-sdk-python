"""
Type definitions for the Langbase SDK.

This module defines the various data structures and type hints used
throughout the SDK to provide better code assistance and documentation.
"""

from typing import Any, Dict, List, Optional, Protocol, Union, runtime_checkable

from typing_extensions import Literal, TypedDict

# NotRequired removed - using Optional instead

# Base types and constants
GENERATION_ENDPOINTS = [
    "/v1/pipes/run",
    "/beta/chat",
    "/beta/generate",
    "/v1/agent/run",
]

# Role types
Role = Literal["user", "assistant", "system", "tool"]

# Embedding models
EmbeddingModel = Literal[
    "openai:text-embedding-3-large",
    "cohere:embed-multilingual-v3.0",
    "cohere:embed-multilingual-light-v3.0",
    "google:text-embedding-004",
]

# Content types for documents
ContentType = Literal[
    "application/pdf",
    "text/plain",
    "text/markdown",
    "text/csv",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "application/vnd.ms-excel",
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
    description: Optional[str]
    parameters: Optional[Dict[str, Any]]


class Tools(TypedDict):
    """Tool definition."""

    type: Literal["function"]
    function: ToolFunction


class ToolChoice(TypedDict):
    """Tool choice definition."""

    type: Literal["function"]
    function: Dict[str, str]


class Message(TypedDict, total=False):
    """Basic message structure."""

    role: Role
    content: Optional[str]
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


# Runtime memory definition
class RuntimeMemory(TypedDict):
    """Runtime memory configuration."""

    name: str


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
    tool_choice: Union[Literal["auto", "required"], ToolChoice]
    parallel_tool_calls: bool
    name: str
    api_key: str
    llm_key: str
    json: bool
    memory: List[RuntimeMemory]
    response_format: ResponseFormat
    top_p: float
    max_tokens: int
    temperature: float
    presence_penalty: float
    frequency_penalty: float
    stop: List[str]
    store: bool
    moderate: bool


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
    top_p: Optional[float]
    max_tokens: Optional[int]
    temperature: Optional[float]
    presence_penalty: Optional[float]
    frequency_penalty: Optional[float]
    stop: Optional[List[str]]
    tools: Optional[List[Tools]]
    tool_choice: Optional[Union[Literal["auto", "required"], ToolChoice]]
    parallel_tool_calls: Optional[bool]
    reasoning_effort: Optional[str]
    max_completion_tokens: Optional[int]
    response_format: Optional[ResponseFormat]
    custom_model_params: Optional[Dict[str, Any]]


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
    """Response from running a pipe without streaming."""

    completion: str
    thread_id: Optional[str]
    id: str
    object: str
    created: int
    model: str
    choices: List[ChoiceGenerate]
    usage: Usage
    system_fingerprint: Optional[str]
    raw_response: Optional[RawResponseHeaders]


class RunResponseStream(TypedDict):
    """Response from running a pipe with streaming."""

    stream: Any  # This would be an iterator in Python
    thread_id: Optional[str]
    raw_response: Optional[RawResponseHeaders]


# Note: Delta, ChoiceStream, and ChunkStream are defined in helper.py


# Memory types
FilterOperator = Literal["Eq", "NotEq", "In", "NotIn", "And", "Or"]
FilterConnective = Literal["And", "Or"]
FilterValue = Union[str, List[str]]
FilterCondition = List[Union[str, FilterOperator, FilterValue]]

# Recursive type for memory filters
MemoryFilters = Union[
    List[Union[FilterConnective, List["MemoryFilters"]]], FilterCondition
]


class MemoryCreateOptions(TypedDict):
    """Options for creating a memory."""

    name: str
    description: Optional[str]
    embedding_model: Optional[EmbeddingModel]
    top_k: Optional[int]
    chunk_size: Optional[int]
    chunk_overlap: Optional[int]


class MemoryDeleteOptions(TypedDict):
    """Options for deleting a memory."""

    name: str


class MemoryConfig(TypedDict):
    """Memory configuration for retrieval."""

    name: str
    filters: Optional[MemoryFilters]


class MemoryRetrieveOptions(TypedDict):
    """Options for retrieving from memory."""

    query: str
    memory: List[MemoryConfig]
    top_k: Optional[int]


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


class MemoryUploadDocOptions(TypedDict):
    """Options for uploading a document to memory."""

    memory_name: str
    document_name: str
    meta: Optional[Dict[str, str]]
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

    chunk_size: int
    chunk_overlap: int
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
    status: Literal["queued", "in_progress", "completed", "failed"]
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
    service: Literal["exa"]
    total_results: int
    domains: List[str]
    api_key: str


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
    embedding_model: Optional[EmbeddingModel]


EmbedResponse = List[List[float]]


# Chunk types
class ChunkOptions(TypedDict, total=False):
    """Options for chunking content."""

    content: str
    chunkOverlap: Optional[int]
    chunkMaxLength: Optional[int]


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
    object: Literal["thread"]
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


# Pipe types - simplified based on TypeScript SDK
class PipeBaseOptions(TypedDict, total=False):
    """Base options for pipe operations."""

    name: str
    description: Optional[str]
    status: Optional[Literal["public", "private"]]
    upsert: Optional[bool]
    model: Optional[str]
    stream: Optional[bool]
    json: Optional[bool]
    store: Optional[bool]
    moderate: Optional[bool]
    top_p: Optional[float]
    max_tokens: Optional[int]
    temperature: Optional[float]
    presence_penalty: Optional[float]
    frequency_penalty: Optional[float]
    stop: Optional[List[str]]
    tools: Optional[List[Tools]]
    tool_choice: Optional[Union[Literal["auto", "required"], ToolChoice]]
    parallel_tool_calls: Optional[bool]
    messages: Optional[List[Message]]
    variables: Optional[List[Variable]]
    memory: Optional[List[Dict[str, str]]]
    response_format: Optional[ResponseFormat]


class PipeCreateOptions(PipeBaseOptions):
    """Options for creating a pipe."""

    pass


class PipeUpdateOptions(PipeBaseOptions):
    """Options for updating a pipe."""

    pass


class PipeRunOptions(TypedDict, total=False):
    """Options for running a pipe."""

    name: Optional[str]
    api_key: Optional[str]
    messages: Optional[List[Message]]
    stream: Optional[bool]
    variables: Optional[Union[List[Variable], Dict[str, str]]]
    thread_id: Optional[str]
    tools: Optional[List[Tools]]
    tool_choice: Optional[Union[Literal["auto", "required"], ToolChoice]]
    parallel_tool_calls: Optional[bool]
    memory: Optional[List[Dict[str, str]]]
    response_format: Optional[ResponseFormat]
    top_p: Optional[float]
    max_tokens: Optional[int]
    temperature: Optional[float]
    presence_penalty: Optional[float]
    frequency_penalty: Optional[float]
    stop: Optional[List[str]]
    llm_key: Optional[str]
    json: Optional[bool]
    store: Optional[bool]
    moderate: Optional[bool]


class PipeBaseResponse(TypedDict):
    """Base response for pipe operations."""

    name: str
    description: str
    status: Literal["public", "private"]
    owner_login: str
    url: str
    type: str
    api_key: str


class PipeCreateResponse(PipeBaseResponse):
    """Response from creating a pipe."""

    pass


class PipeUpdateResponse(PipeBaseResponse):
    """Response from updating a pipe."""

    pass


class PipeListResponse(TypedDict):
    """Response from listing pipes - includes all pipe configuration."""

    name: str
    description: str
    status: Literal["public", "private"]
    owner_login: str
    url: str
    model: str
    stream: bool
    json: bool
    store: bool
    moderate: bool
    top_p: float
    max_tokens: int
    temperature: float
    presence_penalty: float
    frequency_penalty: float
    stop: List[str]
    tool_choice: Union[Literal["auto", "required"], ToolChoice]
    parallel_tool_calls: bool
    messages: List[Message]
    variables: List[Variable]
    tools: List[Tools]
    memory: List[Dict[str, str]]


# Pipe run response types (use existing RunResponse and RunResponseStream)


# Config types
class LangbaseOptions(TypedDict, total=False):
    """Options for initializing Langbase client."""

    api_key: str  # Required
    base_url: Literal[
        "https://api.langbase.com", "https://eu-api.langbase.com"
    ]  # Optional


# Protocol for file-like objects
@runtime_checkable
class FileProtocol(Protocol):
    """Protocol for file-like objects."""

    def read(self, size: int = -1) -> bytes:
        ...


# Agent types
class McpServerSchema(TypedDict):
    """MCP (Model Context Protocol) server configuration."""

    name: str
    type: Literal["url"]
    url: str
    authorization_token: Optional[str]
    tool_configuration: Optional[Dict[str, Any]]
    custom_headers: Optional[Dict[str, str]]


class AgentRunOptionsBase(TypedDict):
    """Base options for running an agent."""

    input: Union[str, List[Message]]  # REQUIRED
    model: str  # REQUIRED
    apiKey: str  # REQUIRED
    instructions: Optional[str]  # OPTIONAL (has ? in TypeScript)
    top_p: Optional[float]  # OPTIONAL (has ? in TypeScript)
    max_tokens: Optional[int]  # OPTIONAL (has ? in TypeScript)
    temperature: Optional[float]  # OPTIONAL (has ? in TypeScript)
    presence_penalty: Optional[float]  # OPTIONAL (has ? in TypeScript)
    frequency_penalty: Optional[float]  # OPTIONAL (has ? in TypeScript)
    stop: Optional[List[str]]  # OPTIONAL (has ? in TypeScript)
    tools: Optional[List[Tools]]  # OPTIONAL (has ? in TypeScript)
    tool_choice: Optional[
        Union[Literal["auto", "required"], ToolChoice]
    ]  # OPTIONAL (has ? in TypeScript)
    parallel_tool_calls: Optional[bool]  # OPTIONAL (has ? in TypeScript)
    mcp_servers: Optional[List[McpServerSchema]]  # OPTIONAL (has ? in TypeScript)
    reasoning_effort: Optional[str]  # OPTIONAL (has ? in TypeScript)
    max_completion_tokens: Optional[int]  # OPTIONAL (has ? in TypeScript)
    response_format: Optional[ResponseFormat]  # OPTIONAL (has ? in TypeScript)
    customModelParams: Optional[Dict[str, Any]]  # OPTIONAL (has ? in TypeScript)


class AgentRunOptionsWithoutMcp(AgentRunOptionsBase):
    """Agent run options without MCP servers."""

    stream: Optional[Literal[False]]  # OPTIONAL (has ? in TypeScript)


class AgentRunOptionsWithMcp(TypedDict):
    """Agent run options with MCP servers."""

    # Required fields from base
    input: Union[str, List[Message]]  # REQUIRED
    model: str  # REQUIRED
    apiKey: str  # REQUIRED

    # Optional fields from base
    instructions: Optional[str]  # OPTIONAL (has ? in TypeScript)
    top_p: Optional[float]  # OPTIONAL (has ? in TypeScript)
    max_tokens: Optional[int]  # OPTIONAL (has ? in TypeScript)
    temperature: Optional[float]  # OPTIONAL (has ? in TypeScript)
    presence_penalty: Optional[float]  # OPTIONAL (has ? in TypeScript)
    frequency_penalty: Optional[float]  # OPTIONAL (has ? in TypeScript)
    stop: Optional[List[str]]  # OPTIONAL (has ? in TypeScript)
    tools: Optional[List[Tools]]  # OPTIONAL (has ? in TypeScript)
    tool_choice: Optional[
        Union[Literal["auto", "required"], ToolChoice]
    ]  # OPTIONAL (has ? in TypeScript)
    parallel_tool_calls: Optional[bool]  # OPTIONAL (has ? in TypeScript)
    reasoning_effort: Optional[str]  # OPTIONAL (has ? in TypeScript)
    max_completion_tokens: Optional[int]  # OPTIONAL (has ? in TypeScript)
    response_format: Optional[ResponseFormat]  # OPTIONAL (has ? in TypeScript)
    customModelParams: Optional[Dict[str, Any]]  # OPTIONAL (has ? in TypeScript)

    # Overridden fields
    mcp_servers: List[McpServerSchema]  # REQUIRED (overrides optional from base)
    stream: Literal[False]  # REQUIRED


class AgentRunOptionsStreamT(TypedDict):
    """Agent run options for streaming (without MCP servers)."""

    input: Union[str, List[Message]]  # REQUIRED
    model: str  # REQUIRED
    apiKey: str  # REQUIRED
    stream: Literal[True]  # REQUIRED
    instructions: Optional[str]  # OPTIONAL (has ? in TypeScript)
    top_p: Optional[float]  # OPTIONAL (has ? in TypeScript)
    max_tokens: Optional[int]  # OPTIONAL (has ? in TypeScript)
    temperature: Optional[float]  # OPTIONAL (has ? in TypeScript)
    presence_penalty: Optional[float]  # OPTIONAL (has ? in TypeScript)
    frequency_penalty: Optional[float]  # OPTIONAL (has ? in TypeScript)
    stop: Optional[List[str]]  # OPTIONAL (has ? in TypeScript)
    tools: Optional[List[Tools]]  # OPTIONAL (has ? in TypeScript)
    tool_choice: Optional[
        Union[Literal["auto", "required"], ToolChoice]
    ]  # OPTIONAL (has ? in TypeScript)
    parallel_tool_calls: Optional[bool]  # OPTIONAL (has ? in TypeScript)
    reasoning_effort: Optional[str]  # OPTIONAL (has ? in TypeScript)
    max_completion_tokens: Optional[int]  # OPTIONAL (has ? in TypeScript)
    response_format: Optional[ResponseFormat]  # OPTIONAL (has ? in TypeScript)
    customModelParams: Optional[Dict[str, Any]]  # OPTIONAL (has ? in TypeScript)


# Union types for agent options
AgentRunOptions = Union[AgentRunOptionsWithoutMcp, AgentRunOptionsWithMcp]
AgentRunOptionsStream = AgentRunOptionsStreamT

# Agent response type (reuses RunResponse)
AgentRunResponse = RunResponse
