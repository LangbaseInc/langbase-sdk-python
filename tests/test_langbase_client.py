"""
Tests for Langbase client initialization and configuration.
"""

from langbase import Langbase


class TestLangbaseClient:
    """Test Langbase client initialization and configuration."""

    def test_initialization_with_api_key(self):
        """Test initialization with API key parameter."""
        client = Langbase(api_key="test-api-key")
        assert client.api_key == "test-api-key"
        assert client.base_url == "https://api.langbase.com"
        assert hasattr(client, "pipes")
        assert hasattr(client, "memories")
        assert hasattr(client, "tools")
        assert hasattr(client, "threads")

    def test_request_instance_creation(self, langbase_client):
        """Test that request instance is properly created."""
        assert hasattr(langbase_client, "request")
        assert langbase_client.request.api_key == "test-api-key"
        assert langbase_client.request.base_url == "https://api.langbase.com"

    def test_nested_class_initialization(self, langbase_client):
        """Test that nested classes are properly initialized."""
        # Test pipes
        assert hasattr(langbase_client.pipes, "list")
        assert hasattr(langbase_client.pipes, "create")
        assert hasattr(langbase_client.pipes, "update")
        assert hasattr(langbase_client.pipes, "run")

        # Test memories
        assert hasattr(langbase_client.memories, "create")
        assert hasattr(langbase_client.memories, "list")
        assert hasattr(langbase_client.memories, "delete")
        assert hasattr(langbase_client.memories, "retrieve")
        assert hasattr(langbase_client.memories, "documents")

        # Test memory documents
        assert hasattr(langbase_client.memories.documents, "list")
        assert hasattr(langbase_client.memories.documents, "delete")
        assert hasattr(langbase_client.memories.documents, "upload")
        assert hasattr(langbase_client.memories.documents, "embeddings")

        # Test tools
        assert hasattr(langbase_client.tools, "crawl")
        assert hasattr(langbase_client.tools, "web_search")

        # Test threads
        assert hasattr(langbase_client.threads, "create")
        assert hasattr(langbase_client.threads, "update")
        assert hasattr(langbase_client.threads, "get")
        assert hasattr(langbase_client.threads, "delete")
        assert hasattr(langbase_client.threads, "append")
        assert hasattr(langbase_client.threads, "messages")

    def test_utility_methods_available(self, langbase_client):
        """Test that utility methods are available on the client."""
        assert hasattr(langbase_client, "embed")
        assert hasattr(langbase_client, "chunker")
        assert hasattr(langbase_client, "parser")
        assert hasattr(langbase_client, "agent")
        assert hasattr(langbase_client.agent, "run")
