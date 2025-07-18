"""
Tests for the Threads API.
"""

import json

import pytest
import responses

from langbase.constants import (
    BASE_URL,
    THREAD_DETAIL_ENDPOINT,
    THREAD_MESSAGES_ENDPOINT,
    THREADS_ENDPOINT,
)
from langbase.errors import NotFoundError
from tests.constants import (
    AUTH_AND_JSON_CONTENT_HEADER,
    AUTHORIZATION_HEADER,
    JSON_CONTENT_TYPE_HEADER,
)
from tests.validation_utils import validate_response_headers


class TestThreads:
    """Test the Threads API."""

    @responses.activate
    def test_threads_create_basic(self, langbase_client, mock_responses):
        """Test threads.create method with basic parameters."""
        responses.add(
            responses.POST,
            f"{BASE_URL}{THREADS_ENDPOINT}",
            json=mock_responses["threads_create"],
            status=200,
        )

        result = langbase_client.threads.create({})

        assert result == mock_responses["threads_create"]
        assert len(responses.calls) == 1
        request = responses.calls[0].request
        validate_response_headers(request.headers, AUTH_AND_JSON_CONTENT_HEADER)

    @responses.activate
    def test_threads_create_with_metadata(self, langbase_client, mock_responses):
        """Test threads.create method with metadata."""
        request_body = {"metadata": {"user_id": "123", "session": "abc"}}

        responses.add(
            responses.POST,
            f"{BASE_URL}{THREADS_ENDPOINT}",
            json=mock_responses["threads_create_with_metadata"],
            status=200,
        )

        result = langbase_client.threads.create(metadata=request_body["metadata"])

        assert result == mock_responses["threads_create_with_metadata"]
        assert len(responses.calls) == 1
        request = responses.calls[0].request
        validate_response_headers(request.headers, AUTH_AND_JSON_CONTENT_HEADER)
        assert json.loads(request.body) == request_body

    @responses.activate
    def test_threads_create_with_thread_id(self, langbase_client, mock_responses):
        """Test threads.create method with specific thread ID."""
        thread_id = "custom_thread_456"

        responses.add(
            responses.POST,
            f"{BASE_URL}{THREADS_ENDPOINT}",
            json=mock_responses["threads_create_with_thread_id"],
            status=200,
        )

        result = langbase_client.threads.create(thread_id=thread_id)

        assert result == mock_responses["threads_create_with_thread_id"]

        # Verify thread_id was included
        request = responses.calls[0].request
        validate_response_headers(request.headers, AUTH_AND_JSON_CONTENT_HEADER)
        print("request.body", request.body)
        assert json.loads(request.body) == {"threadId": thread_id}

    @responses.activate
    def test_threads_create_with_messages(self, langbase_client, mock_responses):
        """Test threads.create method with initial messages."""
        request_body = {
            "messages": [
                {"role": "user", "content": "Hello"},
                {"role": "assistant", "content": "Hi there!"},
            ]
        }

        responses.add(
            responses.POST,
            f"{BASE_URL}{THREADS_ENDPOINT}",
            json=mock_responses["threads_create_with_messages"],
            status=200,
        )

        result = langbase_client.threads.create(messages=request_body["messages"])

        assert result == mock_responses["threads_create_with_messages"]
        assert len(responses.calls) == 1
        request = responses.calls[0].request
        validate_response_headers(request.headers, AUTH_AND_JSON_CONTENT_HEADER)
        assert json.loads(request.body) == request_body

    @responses.activate
    def test_threads_update(self, langbase_client, mock_responses):
        """Test threads.update method."""
        request_data = {
            "thread_id": "thread_123",
            "metadata": {"user_id": "123", "session": "abc"},
        }

        responses.add(
            responses.POST,
            f"{BASE_URL}{THREAD_DETAIL_ENDPOINT.format(thread_id=request_data['thread_id'])}",
            json=mock_responses["threads_update"],
            status=200,
        )

        result = langbase_client.threads.update(**request_data)

        assert result == mock_responses["threads_update"]
        assert len(responses.calls) == 1
        request = responses.calls[0].request
        validate_response_headers(request.headers, AUTH_AND_JSON_CONTENT_HEADER)
        assert (
            request.url
            == f"{BASE_URL}{THREAD_DETAIL_ENDPOINT.format(thread_id=request_data['thread_id'])}"
        )
        assert json.loads(request.body) == {"metadata": request_data["metadata"]}

    @responses.activate
    def test_threads_get(self, langbase_client, mock_responses):
        """Test threads.get method."""
        thread_id = "thread_123"

        responses.add(
            responses.GET,
            f"{BASE_URL}{THREAD_DETAIL_ENDPOINT.format(thread_id=thread_id)}",
            json=mock_responses["threads_get"],
            status=200,
        )

        result = langbase_client.threads.get(thread_id)

        assert result == mock_responses["threads_get"]
        assert len(responses.calls) == 1
        request = responses.calls[0].request
        validate_response_headers(request.headers, AUTH_AND_JSON_CONTENT_HEADER)
        assert (
            request.url
            == f"{BASE_URL}{THREAD_DETAIL_ENDPOINT.format(thread_id=thread_id)}"
        )

    @responses.activate
    def test_threads_delete(self, langbase_client, mock_responses):
        """Test threads.delete method."""
        thread_id = "thread_123"

        responses.add(
            responses.DELETE,
            f"{BASE_URL}{THREAD_DETAIL_ENDPOINT.format(thread_id=thread_id)}",
            json=mock_responses["threads_delete"],
            status=200,
        )

        result = langbase_client.threads.delete(thread_id)

        assert result == mock_responses["threads_delete"]
        assert len(responses.calls) == 1
        request = responses.calls[0].request
        validate_response_headers(request.headers, AUTH_AND_JSON_CONTENT_HEADER)
        assert (
            request.url
            == f"{BASE_URL}{THREAD_DETAIL_ENDPOINT.format(thread_id=thread_id)}"
        )

    @responses.activate
    def test_threads_messages_list(self, langbase_client, mock_responses):
        """Test threads.messages.list method."""
        thread_id = "thread_123"

        responses.add(
            responses.GET,
            f"{BASE_URL}{THREAD_MESSAGES_ENDPOINT.format(thread_id=thread_id)}",
            json=mock_responses["threads_messages_list"],
            status=200,
        )

        result = langbase_client.threads.messages.list(thread_id)

        assert result == mock_responses["threads_messages_list"]
        assert len(responses.calls) == 1
        request = responses.calls[0].request
        validate_response_headers(request.headers, AUTH_AND_JSON_CONTENT_HEADER)
        assert (
            request.url
            == f"{BASE_URL}{THREAD_MESSAGES_ENDPOINT.format(thread_id=thread_id)}"
        )

    @responses.activate
    def test_threads_append(self, langbase_client, mock_responses):
        """Test threads.append method."""
        thread_id = "thread_123"
        request_body = {"messages": [{"role": "user", "content": "New message"}]}

        responses.add(
            responses.POST,
            f"{BASE_URL}{THREAD_MESSAGES_ENDPOINT.format(thread_id=thread_id)}",
            json=mock_responses["threads_append"],
            status=200,
        )

        result = langbase_client.threads.append(thread_id, request_body["messages"])

        assert result == mock_responses["threads_append"]
        assert len(responses.calls) == 1
        request = responses.calls[0].request
        validate_response_headers(request.headers, AUTH_AND_JSON_CONTENT_HEADER)
        assert json.loads(request.body) == request_body["messages"]
        assert (
            request.url
            == f"{BASE_URL}{THREAD_MESSAGES_ENDPOINT.format(thread_id=thread_id)}"
        )
