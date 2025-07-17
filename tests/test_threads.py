"""
Tests for the Threads API.
"""

import json

import pytest
import responses

from langbase.errors import NotFoundError
from langbase.types import ThreadMessagesBaseResponse, ThreadsBaseResponse
from tests.validation_utils import validate_response_body, validate_response_headers


class TestThreads:
    """Test the Threads API."""

    @responses.activate
    def test_threads_create_basic(self, langbase_client, mock_responses):
        """Test threads.create method with basic parameters."""
        responses.add(
            responses.POST,
            "https://api.langbase.com/v1/threads",
            json=mock_responses["threads_create"],
            status=200,
        )

        result = langbase_client.threads.create({})

        assert result == mock_responses["threads_create"]
        assert result["id"] == "thread_123"
        assert len(responses.calls) == 1
        request = responses.calls[0].request
        assert request.method == "POST"
        expected_headers = {
            "Authorization": "Bearer test-api-key",
            "Content-Type": "application/json",
        }
        validate_response_headers(request.headers, expected_headers)
        validate_response_body(result, ThreadsBaseResponse)

    @responses.activate
    def test_threads_create_with_metadata(self, langbase_client, mock_responses):
        """Test threads.create method with metadata."""
        metadata = {"user_id": "123", "session": "abc"}

        responses.add(
            responses.POST,
            "https://api.langbase.com/v1/threads",
            json=mock_responses["threads_create"],
            status=200,
        )

        result = langbase_client.threads.create(metadata=metadata)

        assert result == mock_responses["threads_create"]

        # Verify metadata was included
        request = responses.calls[0].request
        expected_headers = {
            "Authorization": "Bearer test-api-key",
            "Content-Type": "application/json",
        }
        validate_response_headers(request.headers, expected_headers)
        request_json = json.loads(request.body)
        assert request_json["metadata"] == metadata
        validate_response_body(result, ThreadsBaseResponse)

    @responses.activate
    def test_threads_create_with_thread_id(self, langbase_client, mock_responses):
        """Test threads.create method with specific thread ID."""
        thread_id = "custom_thread_456"

        responses.add(
            responses.POST,
            "https://api.langbase.com/v1/threads",
            json=mock_responses["threads_create"],
            status=200,
        )

        result = langbase_client.threads.create(thread_id=thread_id)

        assert result == mock_responses["threads_create"]

        # Verify thread_id was included
        request = responses.calls[0].request
        request_json = json.loads(request.body)
        assert request_json["threadId"] == thread_id
        expected_headers = {
            "Authorization": "Bearer test-api-key",
            "Content-Type": "application/json",
        }
        validate_response_headers(request.headers, expected_headers)
        validate_response_body(result, ThreadsBaseResponse)

    @responses.activate
    def test_threads_create_with_messages(self, langbase_client, mock_responses):
        """Test threads.create method with initial messages."""
        messages = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there!"},
        ]

        responses.add(
            responses.POST,
            "https://api.langbase.com/v1/threads",
            json=mock_responses["threads_create"],
            status=200,
        )

        result = langbase_client.threads.create(messages=messages)

        assert result == mock_responses["threads_create"]

        # Verify messages were included
        request = responses.calls[0].request
        request_json = json.loads(request.body)
        assert request_json["messages"] == messages

        expected_headers = {
            "Authorization": "Bearer test-api-key",
            "Content-Type": "application/json",
        }
        validate_response_headers(request.headers, expected_headers)
        validate_response_body(result, ThreadsBaseResponse)

    @responses.activate
    def test_threads_update(self, langbase_client, mock_responses):
        """Test threads.update method."""
        thread_id = "thread_123"
        metadata = {"status": "active", "updated": "true"}

        responses.add(
            responses.POST,
            f"https://api.langbase.com/v1/threads/{thread_id}",
            json=mock_responses["threads_update"],
            status=200,
        )

        result = langbase_client.threads.update(thread_id, metadata)

        assert result == mock_responses["threads_update"]

        # Verify request data
        request = responses.calls[0].request
        assert request.method == "POST"
        expected_headers = {
            "Authorization": "Bearer test-api-key",
            "Content-Type": "application/json",
        }
        validate_response_headers(request.headers, expected_headers)
        request_json = json.loads(request.body)
        assert request_json["threadId"] == thread_id
        assert request_json["metadata"] == metadata
        validate_response_body(result, ThreadsBaseResponse)

    @responses.activate
    def test_threads_get(self, langbase_client, mock_responses):
        """Test threads.get method."""
        thread_id = "thread_123"

        responses.add(
            responses.GET,
            f"https://api.langbase.com/v1/threads/{thread_id}",
            json=mock_responses["threads_get"],
            status=200,
        )

        result = langbase_client.threads.get(thread_id)

        assert result == mock_responses["threads_get"]
        assert result["id"] == "thread_123"
        request = responses.calls[0].request
        assert request.method == "GET"
        expected_headers = {
            "Authorization": "Bearer test-api-key",
            "Content-Type": "application/json",
        }
        validate_response_headers(request.headers, expected_headers)
        validate_response_body(result, ThreadsBaseResponse)

    @responses.activate
    def test_threads_delete(self, langbase_client, mock_responses):
        """Test threads.delete method."""
        thread_id = "thread_123"

        responses.add(
            responses.DELETE,
            f"https://api.langbase.com/v1/threads/{thread_id}",
            json=mock_responses["threads_delete"],
            status=200,
        )

        result = langbase_client.threads.delete(thread_id)

        assert result == mock_responses["threads_delete"]
        assert result["deleted"] is True
        assert result["id"] == "thread_123"
        request = responses.calls[0].request
        assert request.method == "DELETE"
        expected_headers = {
            "Authorization": "Bearer test-api-key",
            "Content-Type": "application/json",
        }
        validate_response_headers(request.headers, expected_headers)

    @responses.activate
    def test_threads_append(self, langbase_client, mock_responses):
        """Test threads.append method."""
        thread_id = "thread_123"
        messages = [{"role": "user", "content": "New message"}]

        responses.add(
            responses.POST,
            f"https://api.langbase.com/v1/threads/{thread_id}/messages",
            json=mock_responses["threads_append"],
            status=200,
        )

        result = langbase_client.threads.append(thread_id, messages)

        assert result == mock_responses["threads_append"]

        # Verify messages were sent directly as body
        request = responses.calls[0].request
        assert request.method == "POST"
        expected_headers = {
            "Authorization": "Bearer test-api-key",
            "Content-Type": "application/json",
        }
        validate_response_headers(request.headers, expected_headers)
        request_json = json.loads(request.body)
        assert request_json == messages
        for item in result:
            validate_response_body(item, ThreadMessagesBaseResponse)

    @responses.activate
    def test_threads_messages_list(self, langbase_client, mock_responses):
        """Test threads.messages.list method."""
        thread_id = "thread_123"

        responses.add(
            responses.GET,
            f"https://api.langbase.com/v1/threads/{thread_id}/messages",
            json=mock_responses["threads_messages_list"],
            status=200,
        )

        result = langbase_client.threads.messages.list(thread_id)

        assert result == mock_responses["threads_messages_list"]
        request = responses.calls[0].request
        assert request.method == "GET"
        expected_headers = {
            "Authorization": "Bearer test-api-key",
            "Content-Type": "application/json",
        }
        validate_response_headers(request.headers, expected_headers)
        for item in result:
            validate_response_body(item, ThreadMessagesBaseResponse)

    @responses.activate
    def test_threads_list_messages_direct_call(self, langbase_client, mock_responses):
        """Test threads.list method for messages."""
        thread_id = "thread_123"

        responses.add(
            responses.GET,
            f"https://api.langbase.com/v1/threads/{thread_id}/messages",
            json=mock_responses["threads_messages_list"],
            status=200,
        )

        result = langbase_client.threads.list(thread_id)

        assert result == mock_responses["threads_messages_list"]
        request = responses.calls[0].request
        assert request.method == "GET"
        expected_headers = {
            "Authorization": "Bearer test-api-key",
            "Content-Type": "application/json",
        }
        validate_response_headers(request.headers, expected_headers)
        for item in result:
            validate_response_body(item, ThreadMessagesBaseResponse)
