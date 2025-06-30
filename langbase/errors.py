"""
Error classes for the Langbase SDK.

This module defines the exception hierarchy used throughout the SDK.
All errors inherit from the base APIError class.
"""
from typing import Dict, Optional, Any


class APIError(Exception):
    """Base class for all API errors."""

    def __init__(
        self,
        status: Optional[int] = None,
        error: Optional[Dict[str, Any]] = None,
        message: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
    ):
        """
        Initialize an API error.

        Args:
            status: HTTP status code
            error: Error response body
            message: Error message
            headers: HTTP response headers
        """
        self.status = status
        self.headers = headers
        self.request_id = headers.get('lb-request-id') if headers else None

        if isinstance(error, dict):
            self.error = error
            self.code = error.get('code')
            self.status = error.get('status', status)
        else:
            self.error = error
            self.code = None

        msg = self._make_message(status, error, message)
        super().__init__(msg)

    @staticmethod
    def _make_message(
        status: Optional[int],
        error: Any,
        message: Optional[str]
    ) -> str:
        """
        Create a human-readable error message.

        Args:
            status: HTTP status code
            error: Error response body
            message: Error message

        Returns:
            Formatted error message string
        """
        if isinstance(error, dict) and 'message' in error:
            msg = error['message']
            if not isinstance(msg, str):
                msg = str(msg)
        elif error:
            msg = str(error) if isinstance(error, str) else str(error)
        else:
            msg = message

        if status and msg:
            return f"{status} {msg}"
        if status:
            return f"{status} status code (no body)"
        if msg:
            return msg
        return "(no status code or body)"

    @staticmethod
    def generate(
        status: Optional[int],
        error_response: Any,
        message: Optional[str],
        headers: Optional[Dict[str, str]]
    ) -> 'APIError':
        """
        Generate the appropriate error based on status code.

        Args:
            status: HTTP status code
            error_response: Error response body
            message: Error message
            headers: HTTP response headers

        Returns:
            An instance of the appropriate APIError subclass
        """
        if not status:
            cause = error_response if isinstance(error_response, Exception) else None
            return APIConnectionError(cause=cause)

        error = error_response.get('error') if isinstance(error_response, dict) else error_response

        if status == 400:
            return BadRequestError(status, error, message, headers)
        elif status == 401:
            return AuthenticationError(status, error, message, headers)
        elif status == 403:
            return PermissionDeniedError(status, error, message, headers)
        elif status == 404:
            return NotFoundError(status, error, message, headers)
        elif status == 409:
            return ConflictError(status, error, message, headers)
        elif status == 422:
            return UnprocessableEntityError(status, error, message, headers)
        elif status == 429:
            return RateLimitError(status, error, message, headers)
        elif status >= 500:
            return InternalServerError(status, error, message, headers)
        else:
            return APIError(status, error, message, headers)


class APIConnectionError(APIError):
    """Raised when there's a problem connecting to the API."""

    def __init__(self, message: Optional[str] = None, cause: Optional[Exception] = None):
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
