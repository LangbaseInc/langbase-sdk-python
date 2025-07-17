"""
Tests for utility methods.
"""

import json

import responses

from langbase.types import (
    AgentRunResponse,
    ChunkResponse,
    EmbedResponse,
    ParseResponse,
    RunResponseStream,
)
from tests.validation_utils import validate_response_body, validate_response_headers


class TestUtilities:
    """Test utility methods."""

    @responses.activate
    def test_embed_basic(self, langbase_client, mock_responses):
        """Test embed method with basic parameters."""
        chunks = ["Hello world", "Another chunk"]

        responses.add(
            responses.POST,
            "https://api.langbase.com/v1/embed",
            json=mock_responses["embed"],
            status=200,
        )

        result = langbase_client.embed(chunks)

        assert result == mock_responses["embed"]
        assert len(result) == 2
        assert len(result[0]) == 3  # Vector dimension

        # Verify request data
        request = responses.calls[0].request
        assert request.method == "POST"
        expected_headers = {
            "Authorization": "Bearer test-api-key",
            "Content-Type": "application/json",
        }
        validate_response_headers(request.headers, expected_headers)
        request_json = json.loads(request.body)
        assert request_json["chunks"] == chunks
        validate_response_body(result, EmbedResponse)

    @responses.activate
    def test_embed_with_model(self, langbase_client, mock_responses):
        """Test embed method with specific model."""
        chunks = ["Text to embed"]
        model = "openai:text-embedding-ada-002"

        responses.add(
            responses.POST,
            "https://api.langbase.com/v1/embed",
            json=mock_responses["embed"],
            status=200,
        )

        result = langbase_client.embed(chunks, embedding_model=model)

        assert result == mock_responses["embed"]

        # Verify model parameter
        request = responses.calls[0].request
        expected_headers = {
            "Authorization": "Bearer test-api-key",
            "Content-Type": "application/json",
        }
        validate_response_headers(request.headers, expected_headers)
        request_json = json.loads(request.body)
        assert request_json["embeddingModel"] == model
        validate_response_body(result, EmbedResponse)

    @responses.activate
    def test_chunker_basic(self, langbase_client, mock_responses):
        """Test chunker method with basic parameters."""
        content = (
            "This is a long document that needs to be chunked into smaller pieces."
        )

        responses.add(
            responses.POST,
            "https://api.langbase.com/v1/chunker",
            json=mock_responses["chunker"],
            status=200,
        )

        result = langbase_client.chunker(content)

        assert result == mock_responses["chunker"]
        assert len(result) == 3
        assert isinstance(result[0], str)

        # Verify request data
        request = responses.calls[0].request
        assert request.method == "POST"
        expected_headers = {
            "Authorization": "Bearer test-api-key",
            "Content-Type": "application/json",
        }
        validate_response_headers(request.headers, expected_headers)
        request_json = json.loads(request.body)
        assert request_json["content"] == content
        validate_response_body(result, ChunkResponse)

    @responses.activate
    def test_chunker_with_parameters(self, langbase_client, mock_responses):
        """Test chunker method with custom parameters."""
        content = "Long document content for chunking test."

        responses.add(
            responses.POST,
            "https://api.langbase.com/v1/chunker",
            json=mock_responses["chunker"],
            status=200,
        )

        result = langbase_client.chunker(
            content=content, chunk_max_length=500, chunk_overlap=50
        )

        assert result == mock_responses["chunker"]

        # Verify parameters
        request = responses.calls[0].request
        expected_headers = {
            "Authorization": "Bearer test-api-key",
            "Content-Type": "application/json",
        }
        validate_response_headers(request.headers, expected_headers)
        request_json = json.loads(request.body)
        assert request_json["content"] == content
        assert request_json["chunkMaxLength"] == 500
        assert request_json["chunkOverlap"] == 50
        validate_response_body(result, ChunkResponse)

    @responses.activate
    def test_parser_basic(self, langbase_client, mock_responses, upload_file_content):
        """Test parser method with basic parameters."""
        document_name = "test.pdf"
        content_type = "application/pdf"

        responses.add(
            responses.POST,
            "https://api.langbase.com/v1/parser",
            json=mock_responses["parser"],
            status=200,
        )

        result = langbase_client.parser(
            document=upload_file_content,
            document_name=document_name,
            content_type=content_type,
        )

        assert result == mock_responses["parser"]
        assert "content" in result
        assert "document_name" in result
        request = responses.calls[0].request
        assert request.method == "POST"
        expected_headers = {
            "Authorization": "Bearer test-api-key",
        }
        validate_response_headers(request.headers, expected_headers)
        validate_response_body(result, ParseResponse)

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

        for document_name, content_type in test_cases:
            responses.add(
                responses.POST,
                "https://api.langbase.com/v1/parser",
                json=mock_responses["parser"],
                status=200,
            )

            result = langbase_client.parser(
                document=upload_file_content,
                document_name=document_name,
                content_type=content_type,
            )

            assert result == mock_responses["parser"]

            # Verify headers for each test case
            request = responses.calls[-1].request
            expected_headers = {
                "Authorization": "Bearer test-api-key",
            }
            validate_response_headers(request.headers, expected_headers)
            validate_response_body(result, ParseResponse)

    @responses.activate
    def test_agent_run_basic(self, langbase_client, mock_responses):
        """Test agent.run method with basic parameters."""
        responses.add(
            responses.POST,
            "https://api.langbase.com/v1/agent/run",
            json=mock_responses["agent.run"],
            status=200,
        )

        result = langbase_client.agent.run(
            input="Hello, agent!",
            model="anthropic:claude-3-sonnet",
            api_key="test-llm-key",
        )

        assert result == mock_responses["agent.run"]

        # Verify request data
        request = responses.calls[0].request
        assert request.method == "POST"
        expected_headers = {
            "Authorization": "Bearer test-api-key",
            "Content-Type": "application/json",
        }
        validate_response_headers(request.headers, expected_headers)
        request_json = json.loads(request.body)
        assert request_json["input"] == "Hello, agent!"
        assert request_json["model"] == "anthropic:claude-3-sonnet"
        assert request_json["apiKey"] == "test-llm-key"
        validate_response_body(result, AgentRunResponse)

    @responses.activate
    def test_agent_run_with_messages(self, langbase_client, mock_responses):
        """Test agent.run method with message format input."""
        messages = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there!"},
        ]

        responses.add(
            responses.POST,
            "https://api.langbase.com/v1/agent/run",
            json=mock_responses["agent.run"],
            status=200,
        )

        result = langbase_client.agent.run(
            input=messages, model="openai:gpt-4", api_key="openai-key"
        )

        assert result == mock_responses["agent.run"]

        # Verify messages format
        request = responses.calls[0].request
        expected_headers = {
            "Authorization": "Bearer test-api-key",
            "Content-Type": "application/json",
        }
        validate_response_headers(request.headers, expected_headers)
        request_json = json.loads(request.body)
        assert request_json["input"] == messages
        validate_response_body(result, AgentRunResponse)

    @responses.activate
    def test_agent_run_with_all_parameters(self, langbase_client, mock_responses):
        """Test agent.run method with all parameters."""
        responses.add(
            responses.POST,
            "https://api.langbase.com/v1/agent/run",
            json=mock_responses["agent.run"],
            status=200,
        )

        result = langbase_client.agent.run(
            input="Complex query",
            model="anthropic:claude-3-sonnet",
            api_key="test-key",
            instructions="Be helpful and concise",
            temperature=0.7,
            max_tokens=150,
            top_p=0.9,
            tools=[{"type": "function", "function": {"name": "test"}}],
            stream=False,
        )

        assert result == mock_responses["agent.run"]

        # Verify all parameters
        request = responses.calls[0].request
        expected_headers = {
            "Authorization": "Bearer test-api-key",
            "Content-Type": "application/json",
        }
        validate_response_headers(request.headers, expected_headers)
        request_json = json.loads(request.body)
        assert request_json["input"] == "Complex query"
        assert request_json["instructions"] == "Be helpful and concise"
        assert request_json["temperature"] == 0.7
        assert request_json["max_tokens"] == 150
        assert request_json["top_p"] == 0.9
        assert request_json["tools"][0]["type"] == "function"
        # stream is not included when False
        assert "stream" not in request_json
        validate_response_body(result, AgentRunResponse)

    @responses.activate
    def test_agent_run_streaming(self, langbase_client, stream_chunks):
        """Test agent.run method with streaming."""
        stream_content = b"".join(stream_chunks)

        responses.add(
            responses.POST,
            "https://api.langbase.com/v1/agent/run",
            body=stream_content,
            status=200,
            headers={"content-type": "text/event-stream"},
        )

        result = langbase_client.agent.run(
            input="Streaming query",
            model="openai:gpt-4",
            api_key="stream-key",
            stream=True,
        )

        # For streaming, the result is a dict with stream property
        assert "stream" in result
        assert hasattr(result["stream"], "__iter__")

        # Verify stream parameter and headers
        request = responses.calls[0].request
        request_json = json.loads(request.body)
        assert request_json["stream"] is True
        expected_headers = {
            "Authorization": "Bearer test-api-key",
            "Content-Type": "application/json",
        }
        validate_response_headers(request.headers, expected_headers)
        validate_response_body(result, RunResponseStream)

    @responses.activate
    def test_utilities_authentication_headers(self, langbase_client, mock_responses):
        """Test that utility methods include correct authentication headers."""
        responses.add(
            responses.POST,
            "https://api.langbase.com/v1/embed",
            json=mock_responses["embed"],
            status=200,
        )

        langbase_client.embed(["test"])

        request = responses.calls[0].request
        expected_headers = {
            "Authorization": "Bearer test-api-key",
            "Content-Type": "application/json",
        }
        validate_response_headers(request.headers, expected_headers)

    @responses.activate
    def test_request_format_validation(self, langbase_client, mock_responses):
        """Test that utility requests are properly formatted."""
        responses.add(
            responses.POST,
            "https://api.langbase.com/v1/chunker",
            json=mock_responses["chunker"],
            status=200,
        )

        result = langbase_client.chunker(content="Test content", chunk_max_length=100)

        request = responses.calls[0].request
        assert request.url == "https://api.langbase.com/v1/chunker"

        # Verify headers
        expected_headers = {
            "Authorization": "Bearer test-api-key",
            "Content-Type": "application/json",
        }
        validate_response_headers(request.headers, expected_headers)

        # Verify JSON body format
        request_json = json.loads(request.body)
        assert isinstance(request_json["content"], str)
        assert isinstance(request_json["chunkMaxLength"], int)
        validate_response_body(result, ChunkResponse)
