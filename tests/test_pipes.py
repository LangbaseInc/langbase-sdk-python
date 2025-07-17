"""
Tests for the Pipes API.
"""

import json

import pytest
import responses

from langbase import Langbase
from langbase.types import (
    PipeCreateResponse,
    PipeListResponse,
    PipeUpdateResponse,
    RunResponse,
    RunResponseStream,
)
from tests.validation_utils import validate_response_body, validate_response_headers


class TestPipes:
    """Test the Pipes API."""

    @responses.activate
    def test_pipes_list(self, langbase_client, mock_responses):
        """Test pipes.list method."""
        responses.add(
            responses.GET,
            "https://api.langbase.com/v1/pipes",
            json=mock_responses["pipe_list"],
            status=200,
        )

        result = langbase_client.pipes.list()

        assert result == mock_responses["pipe_list"]
        assert len(responses.calls) == 1
        request = responses.calls[0].request
        assert request.method == "GET"
        assert request.url == "https://api.langbase.com/v1/pipes"
        expected_headers = {
            "Authorization": "Bearer test-api-key",
            "Content-Type": "application/json",
        }
        validate_response_headers(request.headers, expected_headers)
        for item in result:
            validate_response_body(item, PipeListResponse)

    @responses.activate
    def test_pipes_create(self, langbase_client, mock_responses):
        """Test pipes.create method."""
        request_data = {
            "name": "new-pipe",
            "description": "A test pipe",
            "model": "anthropic:claude-3-sonnet",
        }

        responses.add(
            responses.POST,
            "https://api.langbase.com/v1/pipes",
            json=mock_responses["pipe_create"],
            status=201,
        )

        result = langbase_client.pipes.create(**request_data)

        assert result == mock_responses["pipe_create"]
        assert len(responses.calls) == 1

        # Verify request body and headers
        request = responses.calls[0].request
        assert request.method == "POST"
        assert request.url == "https://api.langbase.com/v1/pipes"
        expected_headers = {
            "Authorization": "Bearer test-api-key",
            "Content-Type": "application/json",
        }
        validate_response_headers(request.headers, expected_headers)
        request_json = json.loads(request.body)
        assert request_json["name"] == "new-pipe"
        assert request_json["description"] == "A test pipe"
        validate_response_body(result, PipeCreateResponse)

    @responses.activate
    def test_pipes_update(self, langbase_client, mock_responses):
        """Test pipes.update method."""
        pipe_name = "test-pipe"
        update_data = {"temperature": 0.7, "description": "Updated description"}

        responses.add(
            responses.POST,
            f"https://api.langbase.com/v1/pipes/{pipe_name}",
            json={**mock_responses["pipe_create"], **update_data},
            status=200,
        )

        result = langbase_client.pipes.update(name=pipe_name, **update_data)

        assert "temperature" in str(result)
        assert len(responses.calls) == 1

        request = responses.calls[0].request
        assert request.method == "POST"
        assert request.url == f"https://api.langbase.com/v1/pipes/{pipe_name}"
        expected_headers = {
            "Authorization": "Bearer test-api-key",
            "Content-Type": "application/json",
        }
        validate_response_headers(request.headers, expected_headers)
        validate_response_body(result, PipeUpdateResponse)

    @responses.activate
    def test_pipes_run_basic(self, langbase_client, mock_responses):
        """Test pipes.run method with basic parameters."""
        messages = [{"role": "user", "content": "Hello"}]

        responses.add(
            responses.POST,
            "https://api.langbase.com/v1/pipes/run",
            json=mock_responses["pipe_run"],
            status=200,
            headers={"lb-thread-id": "thread_123"},
        )

        result = langbase_client.pipes.run(name="test-pipe", messages=messages)

        assert result["completion"] == "Hello, world!"
        assert result["threadId"] == "thread_123"
        assert "usage" in result

        request = responses.calls[0].request
        assert request.method == "POST"
        assert request.url == "https://api.langbase.com/v1/pipes/run"

        expected_headers = {
            "Authorization": "Bearer test-api-key",
            "Content-Type": "application/json",
        }
        validate_response_headers(request.headers, expected_headers)
        validate_response_body(result, RunResponse)

    @responses.activate
    def test_pipes_run_with_api_key(self, mock_responses):
        """Test pipes.run method with pipe API key."""
        # Create client with different API key
        client = Langbase(api_key="client-api-key")
        messages = [{"role": "user", "content": "Hello"}]

        responses.add(
            responses.POST,
            "https://api.langbase.com/v1/pipes/run",
            json=mock_responses["pipe_run"],
            status=200,
            headers={"lb-thread-id": "thread_456"},
        )

        result = client.pipes.run(api_key="pipe-specific-key", messages=messages)

        assert result["threadId"] == "thread_456"

        # Verify the request used the pipe-specific API key
        request = responses.calls[0].request
        assert request.headers["Authorization"] == "Bearer pipe-specific-key"
        expected_headers = {
            "Authorization": "Bearer pipe-specific-key",
            "Content-Type": "application/json",
        }
        validate_response_headers(request.headers, expected_headers)
        validate_response_body(result, RunResponse)

    @responses.activate
    def test_pipes_run_streaming(self, langbase_client, stream_chunks):
        """Test pipes.run method with streaming."""
        messages = [{"role": "user", "content": "Hello"}]

        # Create streaming response
        stream_content = b"".join(stream_chunks)

        responses.add(
            responses.POST,
            "https://api.langbase.com/v1/pipes/run",
            body=stream_content,
            status=200,
            headers={
                "Content-Type": "text/event-stream",
                "lb-thread-id": "thread_123",
            },
        )

        result = langbase_client.pipes.run(
            name="test-pipe", messages=messages, stream=True
        )

        assert result["thread_id"] == "thread_123"
        assert hasattr(result["stream"], "__iter__")
        request = responses.calls[0].request
        expected_headers = {
            "Authorization": "Bearer test-api-key",
            "Content-Type": "application/json",
        }
        validate_response_headers(request.headers, expected_headers)
        validate_response_body(result, RunResponseStream)

    @responses.activate
    def test_pipes_run_with_llm_key(self, langbase_client, mock_responses):
        """Test pipes.run method with LLM key header."""
        messages = [{"role": "user", "content": "Hello"}]

        responses.add(
            responses.POST,
            "https://api.langbase.com/v1/pipes/run",
            json=mock_responses["pipe_run"],
            status=200,
            headers={"lb-thread-id": "thread_123"},
        )

        result = langbase_client.pipes.run(
            name="test-pipe", messages=messages, llm_key="custom-llm-key"
        )

        assert result["threadId"] == "thread_123"
        request = responses.calls[0].request
        assert request.headers["LB-LLM-KEY"] == "custom-llm-key"
        expected_headers = {
            "Authorization": "Bearer test-api-key",
            "Content-Type": "application/json",
        }
        validate_response_headers(request.headers, expected_headers)
        validate_response_body(result, RunResponse)

    @responses.activate
    def test_pipes_run_with_all_parameters(self, langbase_client, mock_responses):
        """Test pipes.run method with all possible parameters."""
        responses.add(
            responses.POST,
            "https://api.langbase.com/v1/pipes/run",
            json=mock_responses["pipe_run"],
            status=200,
            headers={"lb-thread-id": "thread_123"},
        )

        result = langbase_client.pipes.run(
            name="test-pipe",
            messages=[{"role": "user", "content": "Hello"}],
            temperature=0.7,
            max_tokens=100,
            top_p=0.9,
            stream=False,
            variables={"var1": "value1"},
            thread_id="existing_thread",
        )

        assert result["threadId"] == "thread_123"

        # Verify all parameters were included in request
        request = responses.calls[0].request
        request_data = json.loads(request.body)
        assert request_data["temperature"] == 0.7
        assert request_data["max_tokens"] == 100
        assert request_data["top_p"] == 0.9
        assert request_data["variables"]["var1"] == "value1"
        assert request_data["thread_id"] == "existing_thread"
        expected_headers = {
            "Authorization": "Bearer test-api-key",
            "Content-Type": "application/json",
        }
        validate_response_headers(request.headers, expected_headers)
        validate_response_body(result, RunResponse)

    @responses.activate
    def test_pipes_run_stream_parameter_not_included_when_false(
        self, langbase_client, mock_responses
    ):
        """Test that stream parameter is included in request when explicitly set to False."""
        responses.add(
            responses.POST,
            "https://api.langbase.com/v1/pipes/run",
            json=mock_responses["pipe_run"],
            status=200,
            headers={"lb-thread-id": "thread_123"},
        )

        # When stream=False, it should be included in the request because it's explicitly set
        langbase_client.pipes.run(
            name="test-pipe",
            messages=[{"role": "user", "content": "Hello"}],
            stream=False,
        )

        request = responses.calls[0].request
        expected_headers = {
            "Authorization": "Bearer test-api-key",
            "Content-Type": "application/json",
        }
        validate_response_headers(request.headers, expected_headers)
        request_data = json.loads(request.body)
        # stream should be in the request body when explicitly set to False
        assert request_data["stream"] is False
