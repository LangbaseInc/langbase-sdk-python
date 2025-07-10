"""
Shared test config and fixtures for Langbase SDK tests.
"""

import time

import pytest


@pytest.fixture
def base_url():
    """Base URL for the Langbase API."""
    return "https://api.langbase.com"


@pytest.fixture
def api_key():
    """Test API key."""
    return "test-api-key"


@pytest.fixture
def langbase_client(api_key, base_url):
    """Langbase client instance for testing."""
    from langbase import Langbase

    return Langbase(api_key=api_key, base_url=base_url)


@pytest.fixture
def mock_responses():
    """Common mock response patterns matching the actual types from types.py."""
    timestamp = int(time.time())

    return {
        # Pipes responses (RunResponse type)
        "pipe_list": [
            {
                "name": "test-pipe",
                "description": "Test pipe",
                "status": "public",
                "owner_login": "test-user",
                "url": "https://langbase.com/test-user/test-pipe",
                "api_key": "pipe-key-1",
            },
            {
                "name": "another-pipe",
                "description": "Another pipe",
                "status": "private",
                "owner_login": "test-user",
                "url": "https://langbase.com/test-user/another-pipe",
                "api_key": "pipe-key-2",
            },
        ],
        "pipe_create": {
            "name": "new-pipe",
            "api_key": "pipe-api-key",
            "description": "A test pipe",
            "status": "public",
            "owner_login": "test-user",
            "url": "https://langbase.com/test-user/new-pipe",
        },
        "pipe_run": {
            "completion": "Hello, world!",
            "thread_id": "thread_test123",
            "id": "chatcmpl-123",
            "object": "chat.completion",
            "created": timestamp,
            "model": "gpt-4",
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": "Hello, world!",
                    },
                    "logprobs": None,
                    "finish_reason": "stop",
                }
            ],
            "usage": {
                "prompt_tokens": 5,
                "completion_tokens": 3,
                "total_tokens": 8,
            },
            "system_fingerprint": "fp_1234567890",
        },
        "pipe_run_stream": {
            "stream": "mock-stream-object",
            "thread_id": "thread_test123",
            "raw_response": {"headers": {"x-request-id": "req_123"}},
        },
        # Memory responses (MemoryCreateResponse, MemoryListResponse types)
        "memory_list": [
            {
                "name": "test-memory",
                "description": "Test memory",
                "owner_login": "test-user",
                "url": "https://langbase.com/test-user/test-memory",
                "embedding_model": "openai:text-embedding-3-large",
            },
            {
                "name": "another-memory",
                "description": "Another memory",
                "owner_login": "test-user",
                "url": "https://langbase.com/test-user/another-memory",
                "embedding_model": "cohere:embed-multilingual-v3.0",
            },
        ],
        "memory_create": {
            "name": "new-memory",
            "description": "A test memory",
            "owner_login": "test-user",
            "url": "https://langbase.com/test-user/new-memory",
            "embedding_model": "openai:text-embedding-3-large",
        },
        "memory_delete": {"success": True},
        "memory_retrieve": [
            {
                "text": "Test content",
                "similarity": 0.95,
                "meta": {"source": "test.pdf", "page": "1"},
            },
            {
                "text": "Another content",
                "similarity": 0.85,
                "meta": {"source": "test.pdf", "page": "2"},
            },
        ],
        # Memory documents responses (MemoryListDocResponse type)
        "memory_docs_list": [
            {
                "name": "doc1.txt",
                "status": "completed",
                "status_message": None,
                "metadata": {
                    "size": 1024,
                    "type": "text/plain",
                },
                "enabled": True,
                "chunk_size": 1000,
                "chunk_overlap": 200,
                "owner_login": "test-user",
            },
            {
                "name": "doc2.pdf",
                "status": "in_progress",
                "status_message": "Processing PDF",
                "metadata": {
                    "size": 2048,
                    "type": "application/pdf",
                },
                "enabled": True,
                "chunk_size": 1000,
                "chunk_overlap": 200,
                "owner_login": "test-user",
            },
        ],
        "memory_docs_delete": {"success": True},
        "memory_docs_upload_signed_url": {
            "signedUrl": "https://storage.langbase.com/upload?signature=xyz",
            "publicUrl": "https://storage.langbase.com/memories/test-memory/doc.pdf",
        },
        "memory_docs_embeddings_retry": {"success": True},
        # Tools responses (ToolWebSearchResponse, ToolCrawlResponse types)
        "tools_web_search": [
            {
                "url": "https://example.com",
                "content": "Example content from search result",
            },
            {
                "url": "https://test.com",
                "content": "Test content from search result",
            },
        ],
        "tools_crawl": [
            {
                "url": "https://example.com",
                "content": "Crawled page content from example.com",
            }
        ],
        # Threads responses (ThreadsBaseResponse type)
        "threads_create": {
            "id": "thread_123",
            "object": "thread",
            "created_at": timestamp,
            "metadata": {},
        },
        "threads_update": {
            "id": "thread_123",
            "object": "thread",
            "created_at": timestamp,
            "metadata": {"updated": "true"},
        },
        "threads_get": {
            "id": "thread_123",
            "object": "thread",
            "created_at": timestamp,
            "metadata": {},
        },
        "threads_delete": {"deleted": True, "id": "thread_123"},
        # Thread messages responses (ThreadMessagesBaseResponse type)
        "threads_append": [
            {
                "id": "msg_1",
                "created_at": timestamp,
                "thread_id": "thread_123",
                "role": "user",
                "content": "Hello",
                "name": None,
                "tool_call_id": None,
                "tool_calls": None,
                "attachments": None,
                "metadata": None,
            },
            {
                "id": "msg_2",
                "created_at": timestamp + 1,
                "thread_id": "thread_123",
                "role": "assistant",
                "content": "Hi there!",
                "name": None,
                "tool_call_id": None,
                "tool_calls": None,
                "attachments": None,
                "metadata": None,
            },
        ],
        "threads_messages_list": [
            {
                "id": "msg_1",
                "created_at": timestamp,
                "thread_id": "thread_123",
                "role": "user",
                "content": "Hello",
                "name": None,
                "tool_call_id": None,
                "tool_calls": None,
                "attachments": None,
                "metadata": None,
            }
        ],
        # Utilities responses (EmbedResponse, ChunkResponse, ParseResponse types)
        "embed": [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]],
        "chunker": ["First chunk", "Second chunk", "Third chunk"],
        "parser": {
            "document_name": "test.pdf",
            "content": "Parsed document content from test.pdf",
        },
        # Agent run response (similar to pipe run)
        "agent_run": {
            "completion": "Agent response to the query",
            "thread_id": "thread_agent123",
            "id": "chatcmpl-agent123",
            "object": "chat.completion",
            "created": timestamp,
            "model": "gpt-4",
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": "Agent response to the query",
                    },
                    "logprobs": None,
                    "finish_reason": "stop",
                }
            ],
            "usage": {
                "prompt_tokens": 50,
                "completion_tokens": 50,
                "total_tokens": 100,
            },
            "system_fingerprint": "fp_agent1234567890",
        },
        # Error responses
        "error_400": {"error": "Bad request", "message": "Invalid parameters"},
        "error_401": {"error": "Unauthorized", "message": "Invalid API key"},
        "error_404": {"error": "Not found", "message": "Resource not found"},
        "error_500": {
            "error": "Internal server error",
            "message": "Something went wrong",
        },
    }


@pytest.fixture
def stream_chunks():
    """Sample streaming response chunks for SSE (Server-Sent Events) format."""
    return [
        b'data: {"choices":[{"delta":{"content":"Hello"},"index":0}]}\n\n',
        b'data: {"choices":[{"delta":{"content":" world"},"index":0}]}\n\n',
        b'data: {"choices":[{"delta":{"content":"!"},"index":0}]}\n\n',
        b"data: [DONE]\n\n",
    ]


@pytest.fixture
def upload_file_content():
    """Sample file content for upload tests."""
    return b"This is test document content for upload testing."


@pytest.fixture
def sample_thread_messages():
    """Sample thread messages for testing."""
    return [
        {
            "role": "user",
            "content": "What is the capital of France?",
        },
        {
            "role": "assistant",
            "content": "The capital of France is Paris.",
        },
    ]


@pytest.fixture
def sample_variables():
    """Sample variables for pipe runs."""
    return [
        {"name": "topic", "value": "AI ethics"},
        {"name": "style", "value": "professional"},
    ]


@pytest.fixture
def sample_tools():
    """Sample tools definition for function calling."""
    return [
        {
            "type": "function",
            "function": {
                "name": "get_weather",
                "description": "Get the current weather in a location",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "The city and state, e.g. San Francisco, CA",
                        },
                        "unit": {
                            "type": "string",
                            "enum": ["celsius", "fahrenheit"],
                            "description": "The unit of temperature",
                        },
                    },
                    "required": ["location"],
                },
            },
        }
    ]


@pytest.fixture
def sample_tool_calls():
    """Sample tool calls in a message."""
    return [
        {
            "id": "call_1234567890",
            "type": "function",
            "function": {
                "name": "get_weather",
                "arguments": '{"location": "San Francisco, CA", "unit": "celsius"}',
            },
        }
    ]


def create_stream_response(chunks):
    """Helper function to create streaming response."""

    def stream_generator():
        for chunk in chunks:
            yield chunk

    return stream_generator()
