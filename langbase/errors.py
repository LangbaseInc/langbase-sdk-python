"""
Error classes for the Langbase SDK.

This module defines the exception hierarchy used throughout the SDK.
All errors inherit from the base APIError class.
"""

from typing import Any, Dict, Optional

from .constants import ERROR_MAP, STATUS_CODE_TO_MESSAGE


class APIError(Exception):
    """Base class for all API errors."""

    def __init__(
        self,
        status: Optional[int] = None,
        error: Optional[Dict[str, Any]] = None,
        message: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
        endpoint: Optional[str] = None,
    ):
        """
        Initialize an API error.

        Args:
            status: HTTP status code
            error: Error response body
            message: Error message
            headers: HTTP response headers
            endpoint: API endpoint that was called
        """
        self.status = status
        self.headers = headers
        self.endpoint = endpoint
        self.request_id = headers.get("lb-request-id") if headers else None

        if isinstance(error, dict):
            self.error = error
            self.code = error.get("code")
            self.status = error.get("status", status)
        else:
            self.error = error
            self.code = None

        msg = self._make_message(status, error, message, endpoint, self.request_id)
        super().__init__(msg)

    @staticmethod
    def _make_message(
        status: Optional[int],
        error: Any,
        message: Optional[str],
        endpoint: Optional[str] = None,
        request_id: Optional[str] = None,
    ) -> str:
        """
        Create a human-readable error message.

        Args:
            status: HTTP status code
            error: Error response body
            message: Error message
            endpoint: API endpoint that was called
            request_id: Request ID from headers

        Returns:
            Formatted error message string
        """
        # Extract the main error message
        if isinstance(error, dict) and "message" in error:
            msg = error["message"]
            if not isinstance(msg, str):
                msg = str(msg)
        elif error:
            msg = str(error)
        else:
            msg = message

        # Build comprehensive error message
        parts = []

        # Status line
        if status:
            status_text = STATUS_CODE_TO_MESSAGE.get(status, "Unknown Error")
            parts.append(f"{status_text} ({status})")

        # Error message
        if msg:
            parts.append(f"\n  Message: {msg}")

        # API endpoint
        if endpoint:
            parts.append(f"\n  Endpoint: {endpoint}")

        # Request ID
        if request_id:
            parts.append(f"\n  Request ID: {request_id}")

        # Error details from response
        if isinstance(error, dict):
            if "code" in error:
                parts.append(f"\n  Error Code: {error['code']}")
            if "details" in error:
                parts.append(f"\n  Details: {error['details']}")

        # Documentation link
        if status:
            parts.append(
                f"\n  Documentation: https://langbase.com/docs/errors/{status}"
            )

        return "".join(parts) if parts else "(no error information available)"

    @staticmethod
    def generate(
        status: Optional[int],
        error_response: Any,
        message: Optional[str],
        headers: Optional[Dict[str, str]],
        endpoint: Optional[str] = None,
    ) -> "APIError":
        """
        Generate the appropriate error based on status code.

        Args:
            status: HTTP status code
            error_response: Error response body
            message: Error message
            headers: HTTP response headers
            endpoint: API endpoint that was called

        Returns:
            An instance of the appropriate APIError subclass
        """
        if not status:
            cause = error_response if isinstance(error_response, Exception) else None
            return APIConnectionError(cause=cause)

        error = (
            error_response.get("error")
            if isinstance(error_response, dict)
            else error_response
        )

        if status in ERROR_MAP:
            error_class_name = ERROR_MAP[status]
            error_class = globals()[error_class_name]
            return error_class(status, error, message, headers, endpoint)

        if status >= 500:
            return InternalServerError(status, error, message, headers, endpoint)
        return APIError(status, error, message, headers, endpoint)


class APIConnectionError(APIError):
    """Raised when there's a problem connecting to the API."""

    def __init__(
        self, message: Optional[str] = None, cause: Optional[Exception] = None
    ):
        """
        Initialize a connection error.

        Args:
            message: Error message
            cause: The underlying exception that caused this error
        """
        super().__init__(None, None, message or "Connection error.", None)
        if cause:
            self.__cause__ = cause


class APIConnectionTimeoutError(APIConnectionError):
    """Raised when a request times out."""

    def __init__(self, message: Optional[str] = None):
        """
        Initialize a timeout error.

        Args:
            message: Error message
        """
        super().__init__(message or "Request timed out.")


class BadRequestError(APIError):
    """Raised when the API returns a 400 status code."""

    pass


class AuthenticationError(APIError):
    """Raised when the API returns a 401 status code."""

    pass


class PermissionDeniedError(APIError):
    """Raised when the API returns a 403 status code."""

    pass


class NotFoundError(APIError):
    """Raised when the API returns a 404 status code."""

    pass


class ConflictError(APIError):
    """Raised when the API returns a 409 status code."""

    pass


class UnprocessableEntityError(APIError):
    """Raised when the API returns a 422 status code."""

    pass


class RateLimitError(APIError):
    """Raised when the API returns a 429 status code."""

    pass


class InternalServerError(APIError):
    """Raised when the API returns a 5xx status code."""

    pass
