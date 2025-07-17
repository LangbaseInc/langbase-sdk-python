"""
Tests for error handling.
"""

import pytest
import requests
import responses

from langbase.errors import (
    APIConnectionError,
    APIError,
    AuthenticationError,
    BadRequestError,
    NotFoundError,
    RateLimitError,
)


class TestErrorHandling:
    """Test error handling scenarios."""

    @responses.activate
    def test_error_with_json_response(self, langbase_client):
        """Test error handling with JSON error response."""
        responses.add(
            responses.POST,
            "https://api.langbase.com/v1/pipes",
            json={"error": "Bad request", "message": "Invalid parameters"},
            status=400,
        )

        with pytest.raises(BadRequestError) as exc_info:
            langbase_client.pipes.create(name="test")

        assert "Bad request" in str(exc_info.value)

    @responses.activate
    def test_error_with_text_response(self, langbase_client):
        """Test error handling with text error response."""
        responses.add(
            responses.GET,
            "https://api.langbase.com/v1/pipes",
            body="Internal Server Error",
            status=500,
        )

        with pytest.raises(APIError) as exc_info:
            langbase_client.pipes.list()

        assert exc_info.value.status == 500

    @responses.activate
    def test_connection_error(self, langbase_client):
        """Test connection error handling."""
        responses.add(
            responses.GET,
            "https://api.langbase.com/v1/pipes",
            body=requests.exceptions.ConnectionError("Connection failed"),
        )

        with pytest.raises(APIConnectionError):
            langbase_client.pipes.list()

    @responses.activate
    def test_timeout_error(self, langbase_client):
        """Test timeout error handling."""
        responses.add(
            responses.GET,
            "https://api.langbase.com/v1/pipes",
            body=requests.exceptions.Timeout("Request timed out"),
        )

        with pytest.raises(APIConnectionError):
            langbase_client.pipes.list()

    @responses.activate
    def test_error_contains_request_details(self, langbase_client):
        """Test that errors contain request details."""
        responses.add(
            responses.GET,
            "https://api.langbase.com/v1/pipes",
            json={"error": "Unauthorized", "message": "Invalid API key"},
            status=401,
        )

        with pytest.raises(AuthenticationError) as exc_info:
            langbase_client.pipes.list()

        error = exc_info.value
        assert error.status == 401
        # Check that error message contains the expected text
        assert "Unauthorized" in str(error)

    @responses.activate
    def test_retry_behavior_on_5xx_errors(self, langbase_client):
        """Test that 5xx errors are raised immediately (no built-in retry)."""
        responses.add(
            responses.GET,
            "https://api.langbase.com/v1/pipes",
            json={"error": "Internal server error"},
            status=503,
        )

        with pytest.raises(APIError) as exc_info:
            langbase_client.pipes.list()

        assert exc_info.value.status == 503
        # Verify only one request was made (no retry)
        assert len(responses.calls) == 1

    @responses.activate
    def test_error_message_formatting(self, langbase_client):
        """Test error message formatting."""
        responses.add(
            responses.POST,
            "https://api.langbase.com/v1/pipes/run",
            json={"error": "Rate limit exceeded", "message": "Too many requests"},
            status=429,
        )

        with pytest.raises(RateLimitError) as exc_info:
            langbase_client.pipes.run(name="test", messages=[])

        error_msg = str(exc_info.value)
        assert "429" in error_msg
        assert "Rate limit exceeded" in error_msg

    @responses.activate
    def test_different_endpoints_error_handling(self, langbase_client):
        """Test error handling across different endpoints."""
        # Test memory endpoint
        responses.add(
            responses.GET,
            "https://api.langbase.com/v1/memory",
            json={"error": "Not found"},
            status=404,
        )

        # Test tools endpoint
        responses.add(
            responses.POST,
            "https://api.langbase.com/v1/tools/web-search",
            json={"error": "Invalid query"},
            status=400,
        )

        with pytest.raises(NotFoundError):
            langbase_client.memories.list()

        with pytest.raises(BadRequestError):
            langbase_client.tools.web_search(query="test")

    @responses.activate
    def test_streaming_endpoint_error_handling(self, langbase_client):
        """Test error handling for streaming endpoints."""
        responses.add(
            responses.POST,
            "https://api.langbase.com/v1/pipes/run",
            json={"error": "Model not available"},
            status=503,
        )

        with pytest.raises(APIError) as exc_info:
            langbase_client.pipes.run(
                name="test",
                messages=[{"role": "user", "content": "Hello"}],
                stream=True,
            )

        assert exc_info.value.status == 503

    @responses.activate
    def test_file_upload_error_handling(self, langbase_client):
        """Test error handling for file upload operations."""
        responses.add(
            responses.POST,
            "https://api.langbase.com/v1/memory/documents",
            json={"error": "File too large"},
            status=413,
        )

        with pytest.raises(APIError) as exc_info:
            langbase_client.memories.documents.upload(
                "test-memory", "test.txt", "test content", "text/plain"
            )

        assert exc_info.value.status == 413
