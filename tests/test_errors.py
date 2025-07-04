"""
Tests for error handling classes.
"""
import unittest

from langbase.errors import (
    APIError, APIConnectionError, APIConnectionTimeoutError,
    BadRequestError, AuthenticationError, PermissionDeniedError,
    NotFoundError, ConflictError, UnprocessableEntityError,
    RateLimitError, InternalServerError
)


class TestErrors(unittest.TestCase):
    """Test error handling classes."""

    def test_api_error_init(self):
        """Test APIError initialization."""
        error = APIError(400, {"message": "Bad request"}, "Bad request", {"X-Request-ID": "123"})

        self.assertEqual(error.status, 400)
        self.assertEqual(error.error, {"message": "Bad request"})
        self.assertEqual(error.request_id, None)  # No lb-request-id in headers
        self.assertEqual(str(error), "400 Bad request")

    def test_api_error_init_with_request_id(self):
        """Test APIError initialization with request ID."""
        error = APIError(400, {"message": "Bad request"}, "Bad request", {"lb-request-id": "123"})

        self.assertEqual(error.status, 400)
        self.assertEqual(error.error, {"message": "Bad request"})
        self.assertEqual(error.request_id, "123")
        self.assertEqual(str(error), "400 Bad request")

    def test_api_error_make_message(self):
        """Test APIError._make_message."""
        # Message from error.message (string)
        msg = APIError._make_message(400, {"message": "Error message"}, None)
        self.assertEqual(msg, "400 Error message")

        # Message from error.message (dict)
        msg = APIError._make_message(400, {"message": {"detail": "Error"}}, None)
        self.assertEqual(msg, "400 {'detail': 'Error'}")

        # Message from error (string)
        msg = APIError._make_message(400, "Error message", None)
        self.assertEqual(msg, "400 Error message")

        # Message from error (dict)
        msg = APIError._make_message(400, {"error": "Something went wrong"}, None)
        self.assertEqual(msg, "400 {'error': 'Something went wrong'}")

        # Message from message parameter
        msg = APIError._make_message(400, None, "Error message")
        self.assertEqual(msg, "400 Error message")

        # Status only
        msg = APIError._make_message(400, None, None)
        self.assertEqual(msg, "400 status code (no body)")

        # Message only
        msg = APIError._make_message(None, None, "Error message")
        self.assertEqual(msg, "Error message")

        # No information
        msg = APIError._make_message(None, None, None)
        self.assertEqual(msg, "(no status code or body)")

    def test_api_error_generate(self):
        """Test APIError.generate."""
        # No status (connection error)
        error = APIError.generate(None, None, "Connection error", {})
        self.assertIsInstance(error, APIConnectionError)

        # 400 Bad Request
        error = APIError.generate(400, {"error": "Bad request"}, None, {})
        self.assertIsInstance(error, BadRequestError)

        # 401 Authentication Error
        error = APIError.generate(401, {"error": "Unauthorized"}, None, {})
        self.assertIsInstance(error, AuthenticationError)

        # 403 Permission Denied
        error = APIError.generate(403, {"error": "Forbidden"}, None, {})
        self.assertIsInstance(error, PermissionDeniedError)

        # 404 Not Found
        error = APIError.generate(404, {"error": "Not found"}, None, {})
        self.assertIsInstance(error, NotFoundError)

        # 409 Conflict
        error = APIError.generate(409, {"error": "Conflict"}, None, {})
        self.assertIsInstance(error, ConflictError)

        # 422 Unprocessable Entity
        error = APIError.generate(422, {"error": "Invalid data"}, None, {})
        self.assertIsInstance(error, UnprocessableEntityError)

        # 429 Rate Limit
        error = APIError.generate(429, {"error": "Too many requests"}, None, {})
        self.assertIsInstance(error, RateLimitError)

        # 500 Internal Server Error
        error = APIError.generate(500, {"error": "Server error"}, None, {})
        self.assertIsInstance(error, InternalServerError)

        # Other status code
        error = APIError.generate(418, {"error": "I'm a teapot"}, None, {})
        self.assertIsInstance(error, APIError)
        self.assertEqual(error.status, 418)

    def test_api_connection_error(self):
        """Test APIConnectionError."""
        error = APIConnectionError()
        self.assertEqual(str(error), "Connection error.")
        self.assertIsNone(error.status)

        error = APIConnectionError("Custom message")
        self.assertEqual(str(error), "Custom message")

        cause = ValueError("Underlying error")
        error = APIConnectionError(cause=cause)
        self.assertEqual(error.__cause__, cause)

    def test_api_connection_timeout_error(self):
        """Test APIConnectionTimeoutError."""
        error = APIConnectionTimeoutError()
        self.assertEqual(str(error), "Request timed out.")

        error = APIConnectionTimeoutError("Custom timeout message")
        self.assertEqual(str(error), "Custom timeout message")

    def test_error_subclasses(self):
        """Test error subclasses."""
        # Check that all error subclasses have the expected status code
        self.assertEqual(BadRequestError(400, None, None, None).status, 400)
        self.assertEqual(AuthenticationError(401, None, None, None).status, 401)
        self.assertEqual(PermissionDeniedError(403, None, None, None).status, 403)
        self.assertEqual(NotFoundError(404, None, None, None).status, 404)
        self.assertEqual(ConflictError(409, None, None, None).status, 409)
        self.assertEqual(UnprocessableEntityError(422, None, None, None).status, 422)
        self.assertEqual(RateLimitError(429, None, None, None).status, 429)

        # InternalServerError can have any 5xx status
        error = InternalServerError(500, None, None, None)
        self.assertEqual(error.status, 500)

        error = InternalServerError(503, None, None, None)
        self.assertEqual(error.status, 503)


if __name__ == "__main__":
    unittest.main()
