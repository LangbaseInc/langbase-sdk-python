"""Test error handling functionality."""

import pytest

from langbase.errors import (
    APIConnectionError,
    APIError,
    AuthenticationError,
    BadRequestError,
    ConflictError,
    InternalServerError,
    NotFoundError,
    PermissionDeniedError,
    RateLimitError,
    UnprocessableEntityError,
    create_api_error,
)


class TestErrorCreation:
    """Test error creation with factory function."""

    def test_create_authentication_error(self):
        """Test 401 creates AuthenticationError."""
        error = create_api_error(
            status_code=401,
            response_text='{"error": {"message": "Invalid API key"}}',
            headers={"lb-request-id": "req_123"},
        )
        assert isinstance(error, AuthenticationError)
        assert error.status_code == 401
        assert error.request_id == "req_123"
        assert "Invalid API key" in str(error)

    def test_create_bad_request_error(self):
        """Test 400 creates BadRequestError."""
        error = create_api_error(
            status_code=400,
            response_text='{"error": {"message": "Invalid request"}}',
        )
        assert isinstance(error, BadRequestError)
        assert error.status_code == 400

    def test_create_permission_denied_error(self):
        """Test 403 creates PermissionDeniedError."""
        error = create_api_error(
            status_code=403,
            response_text='{"error": {"message": "Permission denied"}}',
        )
        assert isinstance(error, PermissionDeniedError)
        assert error.status_code == 403

    def test_create_not_found_error(self):
        """Test 404 creates NotFoundError."""
        error = create_api_error(
            status_code=404,
            response_text='{"error": {"message": "Pipe not found"}}',
        )
        assert isinstance(error, NotFoundError)
        assert error.status_code == 404

    def test_create_conflict_error(self):
        """Test 409 creates ConflictError."""
        error = create_api_error(
            status_code=409,
            response_text='{"error": {"message": "Resource conflict"}}',
        )
        assert isinstance(error, ConflictError)
        assert error.status_code == 409

    def test_create_unprocessable_entity_error(self):
        """Test 422 creates UnprocessableEntityError."""
        error = create_api_error(
            status_code=422,
            response_text='{"error": {"message": "Validation failed"}}',
        )
        assert isinstance(error, UnprocessableEntityError)
        assert error.status_code == 422

    def test_create_rate_limit_error(self):
        """Test 429 creates RateLimitError."""
        error = create_api_error(
            status_code=429,
            response_text='{"error": {"message": "Rate limit exceeded"}}',
        )
        assert isinstance(error, RateLimitError)
        assert error.status_code == 429

    def test_create_internal_server_error(self):
        """Test 5xx creates InternalServerError."""
        error = create_api_error(
            status_code=500,
            response_text='{"error": {"message": "Internal server error"}}',
        )
        assert isinstance(error, InternalServerError)
        assert error.status_code == 500

    def test_create_generic_api_error(self):
        """Test other status codes create generic APIError."""
        error = create_api_error(
            status_code=418,
            response_text='{"error": {"message": "I\'m a teapot"}}',
        )
        assert isinstance(error, APIError)
        assert not isinstance(error, AuthenticationError)
        assert error.status_code == 418


class TestExceptionHandling:
    """Test that users can catch specific exception types."""

    def test_catch_authentication_error(self):
        """Test catching AuthenticationError specifically."""
        with pytest.raises(AuthenticationError) as exc_info:
            raise create_api_error(
                status_code=401,
                response_text='{"error": {"message": "Invalid API key"}}',
            )

        assert "Invalid API key" in str(exc_info.value)

    def test_catch_not_found_error(self):
        """Test catching NotFoundError specifically."""
        with pytest.raises(NotFoundError) as exc_info:
            raise create_api_error(
                status_code=404,
                response_text='{"error": {"message": "Resource not found"}}',
            )

        assert "Resource not found" in str(exc_info.value)

    def test_catch_rate_limit_error(self):
        """Test catching RateLimitError specifically."""
        with pytest.raises(RateLimitError) as exc_info:
            raise create_api_error(
                status_code=429,
                response_text='{"error": {"message": "Rate limit exceeded"}}',
            )

        assert "Rate limit exceeded" in str(exc_info.value)

    def test_catch_connection_error(self):
        """Test catching APIConnectionError specifically."""
        with pytest.raises(APIConnectionError) as exc_info:
            raise APIConnectionError("Network timeout")

        assert "Network timeout" in str(exc_info.value)

    def test_handle_malformed_responses(self):
        """Test handling of various malformed API responses."""
        # Non-JSON response
        error = create_api_error(
            status_code=500,
            response_text="Internal Server Error",
        )
        assert isinstance(error, InternalServerError)
        assert "500" in str(error)

        # Empty response
        error = create_api_error(
            status_code=404,
            response_text="",
        )
        assert isinstance(error, NotFoundError)

        # Weird JSON structure
        error = create_api_error(
            status_code=400,
            response_text='{"weird": "format", "msg": "Something went wrong"}',
        )
        assert isinstance(error, BadRequestError)

    def test_create_connection_error(self):
        """Test connection errors."""
        error = create_api_error(status_code=None, message="Connection failed")
        assert isinstance(error, APIConnectionError)
        assert error.status_code is None
        assert "Connection failed" in str(error)

    def test_connection_error_with_cause(self):
        """Test connection error with underlying cause."""
        import requests

        # Simulate a connection error
        connection_error = requests.ConnectionError("Network unreachable")
        error = APIConnectionError("Connection failed", cause=connection_error)

        assert isinstance(error, APIConnectionError)
        assert error.status_code is None
        assert "Connection failed" in str(error)
        assert error.__cause__ == connection_error

    def test_all_errors_inherit_from_api_error(self):
        """Test that all specific errors inherit from APIError."""
        errors = [
            create_api_error(status_code=400, message="Bad request"),
            create_api_error(status_code=401, message="Unauthorized"),
            create_api_error(status_code=403, message="Forbidden"),
            create_api_error(status_code=404, message="Not found"),
            create_api_error(status_code=409, message="Conflict"),
            create_api_error(status_code=422, message="Unprocessable"),
            create_api_error(status_code=429, message="Rate limited"),
            create_api_error(status_code=500, message="Server error"),
        ]

        for error in errors:
            assert isinstance(error, APIError)
