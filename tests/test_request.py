"""
Tests for the Request class.
"""
import unittest
from unittest.mock import patch, MagicMock

import requests

from langbase.errors import (
    APIError, APIConnectionError, BadRequestError,
    NotFoundError, AuthenticationError
)
from langbase.request import Request


class TestRequest(unittest.TestCase):
    """Test the Request class."""

    def setUp(self):
        """Set up test fixtures."""
        self.config = {
            "api_key": "test-api-key",
            "base_url": "https://api.langbase.com"
        }
        self.request = Request(self.config)

    def test_initialization(self):
        """Test initialization."""
        self.assertEqual(self.request.api_key, "test-api-key")
        self.assertEqual(self.request.base_url, "https://api.langbase.com")

    def test_build_url(self):
        """Test build_url method."""
        url = self.request.build_url("/test")
        self.assertEqual(url, "https://api.langbase.com/test")

    def test_build_headers(self):
        """Test build_headers method."""
        headers = self.request.build_headers()
        self.assertEqual(headers["Content-Type"], "application/json")
        self.assertEqual(headers["Authorization"], "Bearer test-api-key")

        # Test with additional headers
        headers = self.request.build_headers({"X-Custom": "Value"})
        self.assertEqual(headers["Content-Type"], "application/json")
        self.assertEqual(headers["Authorization"], "Bearer test-api-key")
        self.assertEqual(headers["X-Custom"], "Value")

    @patch("requests.request")
    def test_make_request(self, mock_request):
        """Test make_request method."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_request.return_value = mock_response

        response = self.request.make_request(
            "https://api.langbase.com/test",
            "GET",
            {"Authorization": "Bearer test-api-key"}
        )

        mock_request.assert_called_once_with(
            method="GET",
            url="https://api.langbase.com/test",
            headers={"Authorization": "Bearer test-api-key"},
            json=None,
            stream=False
        )
        self.assertEqual(response, mock_response)

    @patch("requests.request")
    def test_make_request_connection_error(self, mock_request):
        """Test make_request method with connection error."""
        mock_request.side_effect = requests.RequestException("Connection error")

        with self.assertRaises(APIConnectionError):
            self.request.make_request(
                "https://api.langbase.com/test",
                "GET",
                {"Authorization": "Bearer test-api-key"}
            )

    def test_handle_error_response(self):
        """Test handle_error_response method."""
        # Test with JSON response
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.reason = "Not Found"
        mock_response.headers = {}
        mock_response.json.return_value = {"error": "Resource not found"}

        with self.assertRaises(NotFoundError):
            self.request.handle_error_response(mock_response)

        # Test with text response
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.reason = "Bad Request"
        mock_response.headers = {}
        mock_response.json.side_effect = requests.exceptions.JSONDecodeError("msg", "doc", 0)
        mock_response.text = "Bad request error"

        with self.assertRaises(BadRequestError):
            self.request.handle_error_response(mock_response)

    def test_handle_stream_response(self):
        """Test handle_stream_response method."""
        mock_response = MagicMock()
        mock_response.iter_lines.return_value = [b"line1", b"line2"]
        mock_response.headers = {"lb-thread-id": "thread_123"}

        result = self.request.handle_stream_response(mock_response)

        self.assertEqual(result["thread_id"], "thread_123")
        self.assertEqual(list(result["stream"]), [b"line1", b"line2"])

    def test_handle_run_response_stream(self):
        """Test handle_run_response_stream method."""
        mock_response = MagicMock()
        mock_response.iter_lines.return_value = [b"chunk1", b"chunk2"]
        mock_response.headers = {
            "lb-thread-id": "thread_123",
            "content-type": "text/event-stream"
        }

        # Test without raw_response
        result = self.request.handle_run_response_stream(mock_response)
        self.assertEqual(result["thread_id"], "thread_123")
        self.assertEqual(list(result["stream"]), [b"chunk1", b"chunk2"])
        self.assertNotIn("rawResponse", result)

        # Test with raw_response
        result = self.request.handle_run_response_stream(mock_response, raw_response=True)
        self.assertEqual(result["thread_id"], "thread_123")
        self.assertEqual(list(result["stream"]), [b"chunk1", b"chunk2"])
        self.assertIn("rawResponse", result)
        self.assertEqual(
            result["rawResponse"]["headers"],
            {"lb-thread-id": "thread_123", "content-type": "text/event-stream"}
        )

    def test_handle_run_response(self):
        """Test handle_run_response method."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"completion": "Hello, world!"}
        mock_response.headers = {"lb-thread-id": "thread_123"}

        # Test with thread_id, without raw_response
        result = self.request.handle_run_response(mock_response, "thread_123")
        self.assertEqual(result["completion"], "Hello, world!")
        self.assertEqual(result["threadId"], "thread_123")
        self.assertNotIn("rawResponse", result)

        # Test with thread_id and raw_response
        result = self.request.handle_run_response(mock_response, "thread_123", True)
        self.assertEqual(result["completion"], "Hello, world!")
        self.assertEqual(result["threadId"], "thread_123")
        self.assertIn("rawResponse", result)
        self.assertEqual(
            result["rawResponse"]["headers"],
            {"lb-thread-id": "thread_123"}
        )

        # Test with raw field in response
        mock_response.json.return_value = {
            "completion": "Hello, world!",
            "raw": {"id": "123", "model": "test-model"}
        }
        result = self.request.handle_run_response(mock_response, "thread_123")
        self.assertEqual(result["completion"], "Hello, world!")
        self.assertEqual(result["id"], "123")
        self.assertEqual(result["model"], "test-model")
        self.assertEqual(result["threadId"], "thread_123")

    @patch.object(Request, "make_request")
    @patch.object(Request, "build_url")
    @patch.object(Request, "build_headers")
    def test_send(self, mock_build_headers, mock_build_url, mock_make_request):
        """Test send method."""
        mock_build_url.return_value = "https://api.langbase.com/test"
        mock_build_headers.return_value = {"Authorization": "Bearer test-api-key"}

        mock_response = MagicMock()
        mock_response.ok = True
        mock_response.json.return_value = {"result": "success"}
        mock_response.headers = {}
        mock_make_request.return_value = mock_response

        # Test normal endpoint
        result = self.request.send("/test", "GET")
        mock_build_url.assert_called_with("/test")
        mock_build_headers.assert_called_with(None)
        mock_make_request.assert_called_with(
            "https://api.langbase.com/test",
            "GET",
            {"Authorization": "Bearer test-api-key"},
            None,
            False,
            None
        )
        self.assertEqual(result, {"result": "success"})

        # Test generation endpoint
        mock_response.headers = {"lb-thread-id": "thread_123"}
        mock_build_url.return_value = "https://api.langbase.com/v1/pipes/run"
        result = self.request.send("/v1/pipes/run", "POST", body={"messages": []})
        self.assertEqual(result["threadId"], "thread_123")

    @patch.object(Request, "send")
    def test_post(self, mock_send):
        """Test post method."""
        mock_send.return_value = {"result": "success"}
        result = self.request.post("/test", {"key": "value"}, {"X-Custom": "Value"})
        mock_send.assert_called_with("/test", "POST", {"X-Custom": "Value"}, {"key": "value"}, False, None)
        self.assertEqual(result, {"result": "success"})

    @patch.object(Request, "send")
    def test_get(self, mock_send):
        """Test get method."""
        mock_send.return_value = {"result": "success"}
        result = self.request.get("/test", {"X-Custom": "Value"})
        mock_send.assert_called_with("/test", "GET", {"X-Custom": "Value"})
        self.assertEqual(result, {"result": "success"})

    @patch.object(Request, "send")
    def test_put(self, mock_send):
        """Test put method."""
        mock_send.return_value = {"result": "success"}
        result = self.request.put("/test", {"key": "value"}, {"X-Custom": "Value"})
        mock_send.assert_called_with("/test", "PUT", {"X-Custom": "Value"}, {"key": "value"}, files=None)
        self.assertEqual(result, {"result": "success"})

    @patch.object(Request, "send")
    def test_delete(self, mock_send):
        """Test delete method."""
        mock_send.return_value = {"result": "success"}
        result = self.request.delete("/test", {"X-Custom": "Value"})
        mock_send.assert_called_with("/test", "DELETE", {"X-Custom": "Value"})
        self.assertEqual(result, {"result": "success"})


if __name__ == "__main__":
    unittest.main()
