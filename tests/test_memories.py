"""
Tests for the Memories API.
"""

import json

import pytest
import responses


class TestMemories:
    """Test the Memories API."""

    @responses.activate
    def test_memories_list(self, langbase_client, mock_responses):
        """Test memories.list method."""
        responses.add(
            responses.GET,
            "https://api.langbase.com/v1/memory",
            json=mock_responses["memory_list"],
            status=200,
        )

        result = langbase_client.memories.list()

        assert result == mock_responses["memory_list"]
        assert len(responses.calls) == 1

    @responses.activate
    def test_memories_create(self, langbase_client, mock_responses):
        """Test memories.create method."""
        request_data = {
            "name": "new-memory",
            "description": "A test memory",
            "embedding_model": "openai:text-embedding-ada-002",
        }

        responses.add(
            responses.POST,
            "https://api.langbase.com/v1/memory",
            json=mock_responses["memory_create"],
            status=201,
        )

        result = langbase_client.memories.create(**request_data)

        assert result == mock_responses["memory_create"]

        # Verify request data
        request = responses.calls[0].request
        request_json = json.loads(request.body)
        assert request_json["name"] == "new-memory"

    @responses.activate
    def test_memories_create_minimal(self, langbase_client, mock_responses):
        """Test memories.create method with minimal parameters."""
        responses.add(
            responses.POST,
            "https://api.langbase.com/v1/memory",
            json=mock_responses["memory_create"],
            status=201,
        )

        result = langbase_client.memories.create(name="minimal-memory")

        assert result == mock_responses["memory_create"]

    @responses.activate
    def test_memories_delete(self, langbase_client, mock_responses):
        """Test memories.delete method."""
        memory_name = "test-memory"

        responses.add(
            responses.DELETE,
            f"https://api.langbase.com/v1/memory/{memory_name}",
            json=mock_responses["memory_delete"],
            status=200,
        )

        result = langbase_client.memories.delete(memory_name)

        assert result == mock_responses["memory_delete"]

    @responses.activate
    def test_memories_retrieve(self, langbase_client, mock_responses):
        """Test memories.retrieve method."""
        responses.add(
            responses.POST,
            "https://api.langbase.com/v1/memory/retrieve",
            json=mock_responses["memory_retrieve"],
            status=200,
        )

        result = langbase_client.memories.retrieve(
            query="test query",
            memory=[{"name": "memory1"}, {"name": "memory2"}],
            top_k=5,
        )

        assert result == mock_responses["memory_retrieve"]

        # Verify request data - note that top_k becomes topK in the request
        request = responses.calls[0].request
        request_json = json.loads(request.body)
        assert request_json["query"] == "test query"
        assert request_json["topK"] == 5

    @responses.activate
    def test_memories_retrieve_minimal(self, langbase_client, mock_responses):
        """Test memories.retrieve method with minimal parameters."""
        responses.add(
            responses.POST,
            "https://api.langbase.com/v1/memory/retrieve",
            json=mock_responses["memory_retrieve"],
            status=200,
        )

        result = langbase_client.memories.retrieve(
            query="test query", memory=[{"name": "memory1"}]
        )

        assert result == mock_responses["memory_retrieve"]

    @responses.activate
    def test_memories_retrieve_multiple_memories(self, langbase_client, mock_responses):
        """Test memories.retrieve method with multiple memories."""
        responses.add(
            responses.POST,
            "https://api.langbase.com/v1/memory/retrieve",
            json=mock_responses["memory_retrieve"],
            status=200,
        )

        memories = [{"name": "memory1", "top_k": 3}, {"name": "memory2", "top_k": 2}]

        result = langbase_client.memories.retrieve(
            query="complex query", memory=memories, top_k=10
        )

        assert result == mock_responses["memory_retrieve"]


class TestMemoryDocuments:
    """Test the Memory Documents API."""

    @responses.activate
    def test_documents_list(self, langbase_client, mock_responses):
        """Test documents.list method."""
        memory_name = "test-memory"

        responses.add(
            responses.GET,
            f"https://api.langbase.com/v1/memory/{memory_name}/documents",
            json=mock_responses["memory_docs_list"],
            status=200,
        )

        result = langbase_client.memories.documents.list(memory_name)

        assert result == mock_responses["memory_docs_list"]

    @responses.activate
    def test_documents_delete(self, langbase_client, mock_responses):
        """Test documents.delete method."""
        memory_name = "test-memory"
        document_name = "test-doc.txt"

        responses.add(
            responses.DELETE,
            f"https://api.langbase.com/v1/memory/{memory_name}/documents/{document_name}",
            json=mock_responses["memory_docs_delete"],
            status=200,
        )

        result = langbase_client.memories.documents.delete(memory_name, document_name)

        assert result == mock_responses["memory_docs_delete"]

    @responses.activate
    def test_documents_upload_simple(
        self, langbase_client, mock_responses, upload_file_content
    ):
        """Test documents.upload method."""
        memory_name = "test-memory"
        document_name = "test-doc.txt"

        # Mock the signed URL request
        responses.add(
            responses.POST,
            "https://api.langbase.com/v1/memory/documents",
            json=mock_responses["memory_docs_upload_signed_url"],
            status=200,
        )

        # Mock the file upload to signed URL
        responses.add(responses.PUT, "https://upload-url.com", status=200)

        result = langbase_client.memories.documents.upload(
            memory_name=memory_name,
            document_name=document_name,
            document=upload_file_content,
            content_type="text/plain",
        )

        assert result.status_code == 200
        assert len(responses.calls) == 2

    @responses.activate
    def test_documents_upload_with_metadata(
        self, langbase_client, mock_responses, upload_file_content
    ):
        """Test documents.upload method with metadata."""
        memory_name = "test-memory"
        document_name = "test-doc.txt"
        metadata = {"author": "test", "category": "documentation"}

        # Mock the signed URL request
        responses.add(
            responses.POST,
            "https://api.langbase.com/v1/memory/documents",
            json=mock_responses["memory_docs_upload_signed_url"],
            status=200,
        )

        # Mock the file upload to signed URL
        responses.add(responses.PUT, "https://upload-url.com", status=200)

        result = langbase_client.memories.documents.upload(
            memory_name=memory_name,
            document_name=document_name,
            document=upload_file_content,
            content_type="text/plain",
            meta=metadata,
        )

        assert result.status_code == 200

        # Verify metadata was included in the signed URL request
        signed_url_request = responses.calls[0].request
        request_json = json.loads(signed_url_request.body)
        assert request_json["meta"] == metadata

    @responses.activate
    def test_documents_embeddings_retry(self, langbase_client, mock_responses):
        """Test documents.embeddings.retry method."""
        memory_name = "test-memory"
        document_name = "test-doc.txt"

        responses.add(
            responses.GET,
            f"https://api.langbase.com/v1/memory/{memory_name}/documents/{document_name}/embeddings/retry",
            json=mock_responses["memory_docs_embeddings_retry"],
            status=200,
        )

        result = langbase_client.memories.documents.embeddings.retry(
            memory_name, document_name
        )

        assert result == mock_responses["memory_docs_embeddings_retry"]
