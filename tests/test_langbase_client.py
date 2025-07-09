"""
Tests for Langbase client initialization and configuration.
"""

import os
from unittest.mock import patch

import pytest

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

    def test_initialization_with_custom_base_url(self):
        """Test initialization with custom base URL."""
        custom_url = "https://custom-api.langbase.com"
        client = Langbase(api_key="test-api-key", base_url=custom_url)
        assert client.api_key == "test-api-key"
        assert client.base_url == custom_url

    @patch.dict(os.environ, {"LANGBASE_API_KEY": "env-api-key"}, clear=True)
    def test_initialization_with_env_var(self):
        """Test initialization with environment variable."""
        client = Langbase()
        assert client.api_key == "env-api-key"
        assert client.base_url == "https://api.langbase.com"

    @patch.dict(os.environ, {"LANGBASE_API_KEY": "env-key"}, clear=True)
    def test_api_key_parameter_overrides_env(self):
        """Test that API key parameter overrides environment variable."""
        client = Langbase(api_key="param-key")
        assert client.api_key == "param-key"

    def test_initialization_no_api_key(self):
        """Test initialization with no API key raises error."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="API key must be provided"):
                Langbase()

    def test_initialization_empty_api_key(self):
        """Test initialization with empty API key raises error."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="API key must be provided"):
                Langbase(api_key="")

    @patch.dict(os.environ, {"LANGBASE_API_KEY": ""}, clear=True)
    def test_initialization_empty_env_api_key(self):
        """Test initialization with empty environment API key raises error."""
        with pytest.raises(ValueError, match="API key must be provided"):
            Langbase()

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
        assert hasattr(langbase_client, "agent_run")
