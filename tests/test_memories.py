"""
Tests for the Memories API.
"""

import json

import responses

from langbase.constants import (
    BASE_URL,
    MEMORY_DETAIL_ENDPOINT,
    MEMORY_DOCUMENT_DETAIL_ENDPOINT,
    MEMORY_DOCUMENT_EMBEDDINGS_RETRY_ENDPOINT,
    MEMORY_DOCUMENTS_ENDPOINT,
    MEMORY_DOCUMENTS_UPLOAD_ENDPOINT,
    MEMORY_ENDPOINT,
    MEMORY_RETRIEVE_ENDPOINT,
)
from langbase.types import (
    MemoryCreateResponse,
    MemoryDeleteResponse,
    MemoryListDocResponse,
    MemoryListResponse,
    MemoryRetrieveResponse,
    MemoryRetryDocEmbedResponse,
)
from tests.constants import (
    AUTH_AND_JSON_CONTENT_HEADER,
    AUTHORIZATION_HEADER,
    JSON_CONTENT_TYPE_HEADER,
)
from tests.validation_utils import validate_response_headers


class TestMemories:
    """Test the Memories API."""

    @responses.activate
    def test_memories_list(self, langbase_client, mock_responses):
        """Test memories.list method."""
        responses.add(
            responses.GET,
            f"{BASE_URL}{MEMORY_ENDPOINT}",
            json=mock_responses["memory_list"],
            status=200,
        )

        result = langbase_client.memories.list()

        assert result == mock_responses["memory_list"]
        assert len(responses.calls) == 1
        request = responses.calls[0].request
        validate_response_headers(request.headers, AUTH_AND_JSON_CONTENT_HEADER)

    @responses.activate
    def test_memories_create(self, langbase_client, mock_responses):
        """Test memories.create method."""
        request_body = {
            "name": "new-memory",
            "description": "A test memory",
            "embedding_model": "openai:text-embedding-ada-002",
        }

        responses.add(
            responses.POST,
            f"{BASE_URL}{MEMORY_ENDPOINT}",
            json=mock_responses["memory_create"],
            status=201,
        )

        result = langbase_client.memories.create(**request_body)

        assert result == mock_responses["memory_create"]
        assert len(responses.calls) == 1
        request = responses.calls[0].request
        validate_response_headers(request.headers, AUTH_AND_JSON_CONTENT_HEADER)
        assert json.loads(request.body) == request_body

    @responses.activate
    def test_memories_delete(self, langbase_client, mock_responses):
        """Test memories.delete method."""
        memory_name = "test-memory"

        responses.add(
            responses.DELETE,
            f"{BASE_URL}{MEMORY_DETAIL_ENDPOINT.format(name=memory_name)}",
            json=mock_responses["memory_delete"],
            status=200,
        )

        result = langbase_client.memories.delete(memory_name)

        assert result == mock_responses["memory_delete"]
        assert len(responses.calls) == 1
        request = responses.calls[0].request
        validate_response_headers(request.headers, AUTH_AND_JSON_CONTENT_HEADER)

    @responses.activate
    def test_memories_retrieve(self, langbase_client, mock_responses):
        """Test memories.retrieve method."""
        request_body = {
            "query": "test query",
            "memory": [{"name": "memory1"}, {"name": "memory2"}],
            "topK": 5,
        }

        responses.add(
            responses.POST,
            f"{BASE_URL}{MEMORY_RETRIEVE_ENDPOINT}",
            json=mock_responses["memory_retrieve"],
            status=200,
        )

        result = langbase_client.memories.retrieve(
            query=request_body["query"],
            memory=request_body["memory"],
            top_k=5,
        )

        assert result == mock_responses["memory_retrieve"]
        assert len(responses.calls) == 1
        request = responses.calls[0].request
        validate_response_headers(request.headers, AUTH_AND_JSON_CONTENT_HEADER)
        assert json.loads(request.body) == request_body


class TestMemoryDocuments:
    """Test the Memory Documents API."""

    @responses.activate
    def test_documents_list(self, langbase_client, mock_responses):
        """Test documents.list method."""
        memory_name = "test-memory"

        responses.add(
            responses.GET,
            f"{BASE_URL}{MEMORY_DOCUMENTS_ENDPOINT.format(memory_name=memory_name)}",
            json=mock_responses["memory_docs_list"],
            status=200,
        )

        result = langbase_client.memories.documents.list(memory_name)

        assert result == mock_responses["memory_docs_list"]
        assert len(responses.calls) == 1
        request = responses.calls[0].request
        validate_response_headers(request.headers, AUTH_AND_JSON_CONTENT_HEADER)

    @responses.activate
    def test_documents_delete(self, langbase_client, mock_responses):
        """Test documents.delete method."""
        memory_name = "test-memory"
        document_name = "test-doc.txt"

        responses.add(
            responses.DELETE,
            f"{BASE_URL}{MEMORY_DOCUMENT_DETAIL_ENDPOINT.format(memory_name=memory_name, document_name=document_name)}",
            json=mock_responses["memory_docs_delete"],
            status=200,
        )

        result = langbase_client.memories.documents.delete(memory_name, document_name)

        assert result == mock_responses["memory_docs_delete"]
        assert len(responses.calls) == 1
        request = responses.calls[0].request
        validate_response_headers(request.headers, AUTH_AND_JSON_CONTENT_HEADER)

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
            f"{BASE_URL}{MEMORY_DOCUMENTS_UPLOAD_ENDPOINT}",
            json=mock_responses["memory_docs_upload_signed_url"],
            status=200,
        )

        # Mock the file upload to signed URL
        responses.add(
            responses.PUT,
            "https://storage.langbase.com/upload?signature=xyz",
            status=200,
        )

        result = langbase_client.memories.documents.upload(
            memory_name=memory_name,
            document_name=document_name,
            document=upload_file_content,
            content_type="text/plain",
        )

        assert len(responses.calls) == 2
        request = responses.calls[0].request
        validate_response_headers(request.headers, AUTH_AND_JSON_CONTENT_HEADER)
        assert responses.calls[1].request.body == upload_file_content
        validate_response_headers(
            responses.calls[1].request.headers,
            {**AUTHORIZATION_HEADER, "Content-Type": "text/plain"},
        )

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
            f"{BASE_URL}{MEMORY_DOCUMENTS_UPLOAD_ENDPOINT}",
            json=mock_responses["memory_docs_upload_signed_url"],
            status=200,
        )

        # Mock the file upload to signed URL
        responses.add(
            responses.PUT,
            "https://storage.langbase.com/upload?signature=xyz",
            status=200,
        )

        result = langbase_client.memories.documents.upload(
            memory_name=memory_name,
            document_name=document_name,
            document=upload_file_content,
            content_type="text/plain",
            meta=metadata,
        )

        signed_url_request = responses.calls[0].request
        validate_response_headers(
            signed_url_request.headers, AUTH_AND_JSON_CONTENT_HEADER
        )
        request_json = json.loads(signed_url_request.body)
        assert request_json["meta"] == metadata

    @responses.activate
    def test_documents_embeddings_retry(self, langbase_client, mock_responses):
        """Test documents.embeddings.retry method."""
        memory_name = "test-memory"
        document_name = "test-doc.txt"

        responses.add(
            responses.GET,
            f"{BASE_URL}{MEMORY_DOCUMENT_EMBEDDINGS_RETRY_ENDPOINT.format(memory_name=memory_name, document_name=document_name)}",
            json=mock_responses["memory_docs_embeddings_retry"],
            status=200,
        )

        result = langbase_client.memories.documents.embeddings.retry(
            memory_name, document_name
        )

        assert result == mock_responses["memory_docs_embeddings_retry"]
        assert len(responses.calls) == 1
        request = responses.calls[0].request
        validate_response_headers(request.headers, AUTH_AND_JSON_CONTENT_HEADER)
