"""
Tests for the Pipes API.
"""

import json

import pytest
import responses

from langbase import Langbase
from langbase.constants import BASE_URL, PIPES_ENDPOINT
from tests.constants import (
    AUTH_AND_JSON_CONTENT_HEADER,
    AUTHORIZATION_HEADER,
    JSON_CONTENT_TYPE_HEADER,
)
from tests.validation_utils import validate_response_headers


class TestPipes:
    """Test the Pipes API."""

    @responses.activate
    def test_pipes_list(self, langbase_client, mock_responses):
        """Test pipes.list method."""
        responses.add(
            responses.GET,
            f"{BASE_URL}{PIPES_ENDPOINT}",
            json=mock_responses["pipe_list"],
            status=200,
        )

        result = langbase_client.pipes.list()

        assert result == mock_responses["pipe_list"]
        request = responses.calls[0].request
        assert len(responses.calls) == 1
        validate_response_headers(request.headers, AUTH_AND_JSON_CONTENT_HEADER)

    @responses.activate
    def test_pipes_create(self, langbase_client, mock_responses):
        """Test pipes.create method."""
        request_body = {
            "name": "new-pipe",
            "description": "A test pipe",
            "model": "anthropic:claude-3-sonnet",
        }

        responses.add(
            responses.POST,
            f"{BASE_URL}{PIPES_ENDPOINT}",
            json=mock_responses["pipe_create"],
            status=201,
        )

        result = langbase_client.pipes.create(**request_body)
        request = responses.calls[0].request
        assert result == mock_responses["pipe_create"]
        assert len(responses.calls) == 1
        assert json.loads(request.body) == request_body
        validate_response_headers(request.headers, AUTH_AND_JSON_CONTENT_HEADER)

    @responses.activate
    def test_pipes_update(self, langbase_client, mock_responses):
        """Test pipes.update method."""
        pipe_name = "test-pipe"
        request_body = {"temperature": 0.7, "description": "Updated description"}

        responses.add(
            responses.POST,
            f"{BASE_URL}{PIPES_ENDPOINT}/{pipe_name}",
            json={**mock_responses["pipe_create"], **request_body},
            status=200,
        )

        result = langbase_client.pipes.update(name=pipe_name, **request_body)
        request = responses.calls[0].request

        assert result == {**mock_responses["pipe_create"], **request_body}
        assert len(responses.calls) == 1
        assert json.loads(request.body) == {
            "name": pipe_name,
            **request_body,
        }
        validate_response_headers(request.headers, AUTH_AND_JSON_CONTENT_HEADER)

    @responses.activate
    def test_pipes_run_basic(self, langbase_client, mock_responses):
        """Test pipes.run method with basic parameters."""
        messages = [{"role": "user", "content": "Hello"}]

        responses.add(
            responses.POST,
            f"{BASE_URL}{PIPES_ENDPOINT}/run",
            json=mock_responses["pipe_run"],
            status=200,
        )

        request_body = {
            "name": "test-pipe",
            "messages": messages,
        }

        result = langbase_client.pipes.run(**request_body)
        request = responses.calls[0].request

        assert result == mock_responses["pipe_run"]
        assert len(responses.calls) == 1

        # Validate body.
        assert json.loads(request.body) == request_body

        # Validate headers.
        validate_response_headers(request.headers, AUTH_AND_JSON_CONTENT_HEADER)

    @responses.activate
    def test_pipes_run_with_api_key(self, langbase_client, mock_responses):
        """Test pipes.run method with pipe API key."""
        messages = [{"role": "user", "content": "Hello"}]

        request_body = {"messages": messages}

        responses.add(
            responses.POST,
            f"{BASE_URL}{PIPES_ENDPOINT}/run",
            json=mock_responses["pipe_run"],
            status=200,
        )

        result = langbase_client.pipes.run(api_key="pipe-specific-key", **request_body)
        request = responses.calls[0].request

        assert result == mock_responses["pipe_run"]
        assert len(responses.calls) == 1

        assert json.loads(request.body) == {
            **request_body,
            "api_key": "pipe-specific-key",
        }
        validate_response_headers(
            request.headers,
            {
                **AUTH_AND_JSON_CONTENT_HEADER,
                "Authorization": "Bearer pipe-specific-key",
            },
        )

    @responses.activate
    def test_pipes_run_streaming(self, langbase_client, stream_chunks):
        """Test pipes.run method with streaming."""
        messages = [{"role": "user", "content": "Hello"}]

        request_body = {"name": "test-pipe", "messages": messages, "stream": True}

        # Create streaming response
        stream_content = b"".join(stream_chunks)

        responses.add(
            responses.POST,
            f"{BASE_URL}{PIPES_ENDPOINT}/run",
            body=stream_content,
            status=200,
            headers={
                "Content-Type": "text/event-stream",
            },
        )

        result = langbase_client.pipes.run(**request_body)
        request = responses.calls[0].request

        assert hasattr(result["stream"], "__iter__")
        assert len(responses.calls) == 1

        # Validate body
        assert json.loads(request.body) == request_body
        validate_response_headers(request.headers, AUTH_AND_JSON_CONTENT_HEADER)

    @responses.activate
    def test_pipes_run_with_llm_key(self, langbase_client, mock_responses):
        """Test pipes.run method with LLM key header."""
        messages = [{"role": "user", "content": "Hello"}]

        request_body = {"name": "test-pipe", "messages": messages}

        responses.add(
            responses.POST,
            f"{BASE_URL}{PIPES_ENDPOINT}/run",
            json=mock_responses["pipe_run"],
            status=200,
        )

        result = langbase_client.pipes.run(llm_key="custom-llm-key", **request_body)
        request = responses.calls[0].request

        assert result == mock_responses["pipe_run"]
        assert len(responses.calls) == 1

        # Validate body
        assert json.loads(request.body) == request_body

        validate_response_headers(
            request.headers,
            {**AUTH_AND_JSON_CONTENT_HEADER, "LB-LLM-KEY": "custom-llm-key"},
        )

    @responses.activate
    def test_pipes_run_with_all_parameters(self, langbase_client, mock_responses):
        """Test pipes.run method with all possible parameters."""
        request_body = {
            "name": "test-pipe",
            "messages": [{"role": "user", "content": "Hello"}],
            "temperature": 0.7,
            "max_tokens": 100,
            "top_p": 0.9,
            "stream": False,
            "variables": {"var1": "value1"},
            "thread_id": "existing_thread",
        }

        responses.add(
            responses.POST,
            f"{BASE_URL}{PIPES_ENDPOINT}/run",
            json=mock_responses["pipe_run"],
            status=200,
        )

        result = langbase_client.pipes.run(**request_body)
        request = responses.calls[0].request

        assert result == mock_responses["pipe_run"]
        assert len(responses.calls) == 1

        # Verify all parameters were included in request
        assert json.loads(request.body) == request_body
        validate_response_headers(request.headers, AUTH_AND_JSON_CONTENT_HEADER)

    @responses.activate
    def test_pipes_run_stream_parameter_not_included_when_false(
        self, langbase_client, mock_responses
    ):
        """Test that stream parameter is included in request when explicitly set to False."""
        request_body = {
            "name": "test-pipe",
            "messages": [{"role": "user", "content": "Hello"}],
            "stream": False,
        }

        responses.add(
            responses.POST,
            f"{BASE_URL}{PIPES_ENDPOINT}/run",
            json=mock_responses["pipe_run"],
            status=200,
        )

        result = langbase_client.pipes.run(**request_body)
        request = responses.calls[0].request

        assert result == mock_responses["pipe_run"]
        assert len(responses.calls) == 1

        # Validate body - stream should be included when explicitly set to False
        assert json.loads(request.body) == request_body
        validate_response_headers(request.headers, AUTH_AND_JSON_CONTENT_HEADER)
