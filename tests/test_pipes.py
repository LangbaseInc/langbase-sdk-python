"""
Tests for the Pipes API.
"""

import json

import pytest
import responses

from langbase import Langbase


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
        assert responses.calls[0].request.url == "https://api.langbase.com/v1/pipes"

    @responses.activate
    def test_pipes_list_with_headers(self, langbase_client, mock_responses):
        """Test pipes.list method includes correct headers."""
        responses.add(
            responses.GET,
            "https://api.langbase.com/v1/pipes",
            json=mock_responses["pipe_list"],
            status=200,
        )

        langbase_client.pipes.list()

        request = responses.calls[0].request
        assert request.headers["Authorization"] == "Bearer test-api-key"
        assert request.headers["Content-Type"] == "application/json"

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

        # Verify request body
        request = responses.calls[0].request
        assert request.url == "https://api.langbase.com/v1/pipes"
        request_json = json.loads(request.body)
        assert request_json["name"] == "new-pipe"
        assert request_json["description"] == "A test pipe"

    @responses.activate
    def test_pipes_create_minimal(self, langbase_client, mock_responses):
        """Test pipes.create method with minimal parameters."""
        responses.add(
            responses.POST,
            "https://api.langbase.com/v1/pipes",
            json=mock_responses["pipe_create"],
            status=201,
        )

        result = langbase_client.pipes.create(name="minimal-pipe")

        assert result == mock_responses["pipe_create"]

        # Verify that null values are cleaned
        request = responses.calls[0].request
        request_json = json.loads(request.body)
        assert request_json["name"] == "minimal-pipe"
        # Should not contain null description
        assert (
            "description" not in request_json or request_json["description"] is not None
        )

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
        assert request.url == f"https://api.langbase.com/v1/pipes/{pipe_name}"

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
        assert request.url == "https://api.langbase.com/v1/pipes/run"

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
                "content-type": "text/event-stream",
                "lb-thread-id": "thread_stream",
            },
        )

        result = langbase_client.pipes.run(
            name="test-pipe", messages=messages, stream=True
        )

        assert result["thread_id"] == "thread_stream"
        assert hasattr(result["stream"], "__iter__")

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

    def test_pipes_run_missing_name_and_api_key(self, langbase_client):
        """Test pipes.run method raises error when both name and API key are missing."""
        messages = [{"role": "user", "content": "Hello"}]

        with pytest.raises(ValueError, match="Either pipe name or API key is required"):
            langbase_client.pipes.run(messages=messages)

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
        request_data = json.loads(request.body)
        # stream should be in the request body when explicitly set to False
        assert request_data["stream"] is False

    @responses.activate
    def test_pipes_run_stream_parameter_included_when_true(
        self, langbase_client, stream_chunks
    ):
        """Test that stream parameter is included in request when True."""
        stream_content = b"".join(stream_chunks)

        responses.add(
            responses.POST,
            "https://api.langbase.com/v1/pipes/run",
            body=stream_content,
            status=200,
            headers={
                "content-type": "text/event-stream",
                "lb-thread-id": "thread_stream",
            },
        )

        langbase_client.pipes.run(
            name="test-pipe",
            messages=[{"role": "user", "content": "Hello"}],
            stream=True,
        )

        request = responses.calls[0].request
        request_data = json.loads(request.body)
        # stream should be in the request body when True
        assert request_data["stream"] is True
