"""
Tests for utility methods.
"""

import json

import responses

from langbase.constants import (
    AGENT_RUN_ENDPOINT,
    BASE_URL,
    CHUNKER_ENDPOINT,
    EMBED_ENDPOINT,
    PARSER_ENDPOINT,
)
from langbase.types import (
    AgentRunResponse,
    ChunkResponse,
    EmbedResponse,
    ParseResponse,
    RunResponseStream,
)
from tests.constants import (
    AUTH_AND_JSON_CONTENT_HEADER,
    AUTHORIZATION_HEADER,
    JSON_CONTENT_TYPE_HEADER,
)
from tests.validation_utils import validate_response_headers


class TestUtilities:
    """Test utility methods."""

    @responses.activate
    def test_embed_with_model(self, langbase_client, mock_responses):
        """Test embed method with specific model."""
        request_body = {
            "chunks": ["First chunk", "Second chunk"],
            "embeddingModel": "openai:text-embedding-ada-002",
        }

        responses.add(
            responses.POST,
            f"{BASE_URL}{EMBED_ENDPOINT}",
            json=mock_responses["embed"],
            status=200,
        )

        result = langbase_client.embed(
            request_body["chunks"], embedding_model="openai:text-embedding-ada-002"
        )

        assert result == mock_responses["embed"]
        assert len(responses.calls) == 1
        request = responses.calls[0].request
        validate_response_headers(request.headers, AUTH_AND_JSON_CONTENT_HEADER)
        assert json.loads(request.body) == request_body

    @responses.activate
    def test_chunker_with_parameters(self, langbase_client, mock_responses):
        """Test chunker method with custom parameters."""
        request_body = {
            "content": "Long document content for chunking test.",
            "chunkMaxLength": 500,
            "chunkOverlap": 50,
        }

        responses.add(
            responses.POST,
            f"{BASE_URL}{CHUNKER_ENDPOINT}",
            json=mock_responses["chunker"],
            status=200,
        )

        result = langbase_client.chunker(
            content=request_body["content"],
            chunk_max_length=request_body["chunkMaxLength"],
            chunk_overlap=request_body["chunkOverlap"],
        )

        assert result == mock_responses["chunker"]
        assert len(responses.calls) == 1
        request = responses.calls[0].request
        validate_response_headers(request.headers, AUTH_AND_JSON_CONTENT_HEADER)
        assert json.loads(request.body) == request_body

    @responses.activate
    def test_parser_with_different_content_types(
        self, langbase_client, mock_responses, upload_file_content
    ):
        """Test parser method with different content types."""
        test_cases = [
            ("document.pdf", "application/pdf"),
            (
                "document.docx",
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            ),
            ("document.txt", "text/plain"),
        ]

        for i, (document_name, content_type) in enumerate(test_cases):
            responses.add(
                responses.POST,
                f"{BASE_URL}{PARSER_ENDPOINT}",
                json=mock_responses["parser"],
                status=200,
            )

            result = langbase_client.parser(
                document=upload_file_content,
                document_name=document_name,
                content_type=content_type,
            )

            assert result == {
                "document_name": mock_responses["parser"]["documentName"],
                "content": mock_responses["parser"]["content"],
            }
            # The number of calls increases with each iteration
            assert len(responses.calls) == i + 1
            request = responses.calls[i].request
            validate_response_headers(request.headers, AUTHORIZATION_HEADER)

    @responses.activate
    def test_agent_run_basic(self, langbase_client, mock_responses):
        """Test agent.run method with basic parameters."""
        request_body = {
            "input": "Hello, agent!",
            "model": "anthropic:claude-3-sonnet",
            "apiKey": "test-llm-key",
        }

        responses.add(
            responses.POST,
            f"{BASE_URL}{AGENT_RUN_ENDPOINT}",
            json=mock_responses["agent.run"],
            status=200,
        )

        result = langbase_client.agent.run(
            input=request_body["input"],
            model=request_body["model"],
            api_key=request_body["apiKey"],
        )

        assert result == mock_responses["agent.run"]
        assert len(responses.calls) == 1
        request = responses.calls[0].request
        validate_response_headers(request.headers, AUTH_AND_JSON_CONTENT_HEADER)
        assert json.loads(request.body) == request_body

    @responses.activate
    def test_agent_run_with_messages(self, langbase_client, mock_responses):
        """Test agent.run method with message format input."""
        request_body = {
            "input": [
                {"role": "user", "content": "Hello"},
                {"role": "assistant", "content": "Hi there!"},
            ],
            "model": "openai:gpt-4",
            "apiKey": "openai-key",
        }

        responses.add(
            responses.POST,
            f"{BASE_URL}{AGENT_RUN_ENDPOINT}",
            json=mock_responses["agent.run"],
            status=200,
        )

        result = langbase_client.agent.run(
            input=request_body["input"],
            model=request_body["model"],
            api_key=request_body["apiKey"],
        )

        assert result == mock_responses["agent.run"]
        assert len(responses.calls) == 1
        request = responses.calls[0].request
        validate_response_headers(request.headers, AUTH_AND_JSON_CONTENT_HEADER)
        assert json.loads(request.body) == request_body

    @responses.activate
    def test_agent_run_with_all_parameters(self, langbase_client, mock_responses):
        """Test agent.run method with all parameters."""
        request_body = {
            "input": "Complex query",
            "model": "anthropic:claude-3-sonnet",
            "apiKey": "test-key",
            "instructions": "Be helpful and concise",
            "temperature": 0.7,
            "max_tokens": 150,
            "top_p": 0.9,
            "tools": [{"type": "function", "function": {"name": "test"}}],
        }

        responses.add(
            responses.POST,
            f"{BASE_URL}{AGENT_RUN_ENDPOINT}",
            json=mock_responses["agent.run"],
            status=200,
        )

        result = langbase_client.agent.run(
            input=request_body["input"],
            model=request_body["model"],
            api_key=request_body["apiKey"],
            instructions=request_body["instructions"],
            temperature=request_body["temperature"],
            max_tokens=request_body["max_tokens"],
            top_p=request_body["top_p"],
            tools=request_body["tools"],
            stream=False,
        )

        assert result == mock_responses["agent.run"]
        assert len(responses.calls) == 1
        request = responses.calls[0].request
        validate_response_headers(request.headers, AUTH_AND_JSON_CONTENT_HEADER)
        assert json.loads(request.body) == request_body

    @responses.activate
    def test_agent_run_streaming(self, langbase_client, stream_chunks):
        """Test agent.run method with streaming."""
        request_body = {
            "input": "Streaming query",
            "model": "openai:gpt-4",
            "apiKey": "stream-key",
            "stream": True,
        }
        stream_content = b"".join(stream_chunks)

        responses.add(
            responses.POST,
            f"{BASE_URL}{AGENT_RUN_ENDPOINT}",
            body=stream_content,
            status=200,
            headers={"Content-Type": "text/event-stream"},
        )

        result = langbase_client.agent.run(
            input=request_body["input"],
            model=request_body["model"],
            api_key=request_body["apiKey"],
            stream=True,
        )

        assert "stream" in result
        assert hasattr(result["stream"], "__iter__")
        assert len(responses.calls) == 1
        request = responses.calls[0].request
        validate_response_headers(request.headers, AUTH_AND_JSON_CONTENT_HEADER)
        assert json.loads(request.body) == request_body
