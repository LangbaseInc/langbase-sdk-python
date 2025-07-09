"""
Shared test configuration and fixtures for Langbase SDK tests.
"""

import json

import pytest
import responses


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
    """Common mock response patterns."""
    return {
        # Pipes responses
        "pipe_list": [
            {"name": "test-pipe", "description": "Test pipe", "status": "deployed"},
            {"name": "another-pipe", "description": "Another pipe", "status": "draft"},
        ],
        "pipe_create": {
            "name": "new-pipe",
            "api_key": "pipe-api-key",
            "description": "A test pipe",
            "status": "draft",
        },
        "pipe_run": {
            "completion": "Hello, world!",
            "usage": {"prompt_tokens": 5, "completion_tokens": 3, "total_tokens": 8},
        },
        "pipe_run_stream": {
            "completion": "Hello, world!",
            "usage": {"prompt_tokens": 5, "completion_tokens": 3, "total_tokens": 8},
        },
        # Memory responses
        "memory_list": [
            {"name": "test-memory", "description": "Test memory", "documents": 5},
            {"name": "another-memory", "description": "Another memory", "documents": 2},
        ],
        "memory_create": {
            "name": "new-memory",
            "description": "A test memory",
            "embedding_model": "openai:text-embedding-ada-002",
        },
        "memory_delete": {"success": True},
        "memory_retrieve": [
            {"text": "Test content", "similarity": 0.95, "metadata": {}},
            {"text": "Another content", "similarity": 0.85, "metadata": {}},
        ],
        # Memory documents responses
        "memory_docs_list": [
            {"name": "doc1.txt", "size": 1024, "status": "processed"},
            {"name": "doc2.pdf", "size": 2048, "status": "processing"},
        ],
        "memory_docs_delete": {"success": True},
        "memory_docs_upload_signed_url": {"signedUrl": "https://upload-url.com"},
        "memory_docs_embeddings_retry": {"success": True},
        # Tools responses
        "tools_web_search": [
            {
                "url": "https://example.com",
                "title": "Example",
                "content": "Example content",
            },
            {"url": "https://test.com", "title": "Test", "content": "Test content"},
        ],
        "tools_crawl": [
            {"url": "https://example.com", "content": "Page content", "metadata": {}}
        ],
        # Threads responses
        "threads_create": {"id": "thread_123", "object": "thread", "metadata": {}},
        "threads_update": {
            "id": "thread_123",
            "object": "thread",
            "metadata": {"updated": True},
        },
        "threads_get": {"id": "thread_123", "object": "thread", "metadata": {}},
        "threads_delete": {"deleted": True, "id": "thread_123"},
        "threads_append": [
            {"id": "msg_1", "role": "user", "content": "Hello"},
            {"id": "msg_2", "role": "assistant", "content": "Hi there!"},
        ],
        "threads_messages_list": [
            {
                "id": "msg_1",
                "role": "user",
                "content": "Hello",
                "created_at": 1234567890,
            }
        ],
        # Utilities responses
        "embed": [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]],
        "chunker": ["First chunk", "Second chunk", "Third chunk"],
        "parser": {"content": "Parsed document content", "metadata": {}},
        "agent_run": {
            "choices": [{"message": {"content": "Agent response"}}],
            "usage": {"total_tokens": 100},
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
    """Sample streaming response chunks."""
    return [
        b'data: {"chunk": "Hello"}\n\n',
        b'data: {"chunk": " world"}\n\n',
        b'data: {"chunk": "!"}\n\n',
        b"data: [DONE]\n\n",
    ]


@pytest.fixture
def upload_file_content():
    """Sample file content for upload tests."""
    return b"This is test document content for upload testing."


def create_stream_response(chunks):
    """Helper function to create streaming response."""

    def stream_generator():
        for chunk in chunks:
            yield chunk

    return stream_generator()
