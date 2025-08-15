"""
Error classes for the Langbase SDK.

This module defines the exception hierarchy used throughout the SDK.
All errors inherit from the base APIError class.
"""

from typing import Any, Dict, Optional, Union

from .constants import ERROR_MAP, STATUS_CODE_TO_MESSAGE


class APIError(Exception):
    """Base class for all API errors."""

    def __init__(
        self,
        status: Optional[int] = None,
        error: Optional[Union[Dict[str, Any], Any]] = None,
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
        # Normalize positional-args misuse: APIError("msg")
        if isinstance(status, str) and error is None and message is None:
            message = status
            status = None

        self.status = status
        self.headers = headers
        self.endpoint = endpoint
        self.request_id = headers.get("lb-request-id") if headers else None

        # Handle error data extraction
        if isinstance(error, dict):
            self.error = error
            self.code = error.get("code")
            # Override status from error data if present
            if "status" in error:
                self.status = error.get("status")
        else:
            self.error = error
            self.code = None

        # Create and set the error message (simplified format like TypeScript)
        msg = self._make_message(self.status, error, message)
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
            endpoint: API endpoint that was called (unused, for compatibility)
            request_id: Request ID from headers (unused, for compatibility)

        Returns:
            Formatted error message string
        """
        # Decide the base message or object to display
        if isinstance(error, dict) and "message" in error:
            base_message: Any = error["message"]
        elif error is not None:
            base_message = error
        else:
            base_message = message

        # Convert dict/list to JSON string (double quotes), keep strings as-is
        try:
            import json
        except Exception:  # pragma: no cover
            json = None  # type: ignore

        if isinstance(base_message, (dict, list)) and json:
            message_str = json.dumps(base_message)
        elif base_message is not None:
            message_str = str(base_message)
        else:
            message_str = None

        # Simplified formats
        if status is None and message_str is None:
            return "(no status code or body)"
        if status is not None and message_str is None:
            return f"{status} status code (no body)"
        if status is None and message_str is not None:
            return message_str
        return f"{status} {message_str}"

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
            endpoint: API endpoint that were called

        Returns:
            An instance of the appropriate APIError subclass
        """
        if not status:
            cause = error_response if isinstance(error_response, Exception) else None
            return APIConnectionError(message=message, cause=cause)

        # Extract error from response
        if isinstance(error_response, dict) and "error" in error_response:
            error = error_response["error"]
        else:
            error = error_response

        # Use direct mapping instead of globals() for better performance and safety
        error_class_map = {
            400: BadRequestError,
            401: AuthenticationError,
            403: PermissionDeniedError,
            404: NotFoundError,
            409: ConflictError,
            422: UnprocessableEntityError,
            429: RateLimitError,
        }

        if status in error_class_map:
            error_class = error_class_map[status]
            return error_class(status, error, message, headers, endpoint)

        # Handle server errors (5xx)
        if status >= 500:
            return InternalServerError(status, error, message, headers, endpoint)

        # Default to base APIError for unhandled status codes
        return APIError(status, error, message, headers, endpoint)


class APIConnectionError(APIError):
    """Raised when there's a problem connecting to the API."""

    def __init__(
        self,
        message: Optional[str] = None,
        cause: Optional[Exception] = None,
        **kwargs,  # Accept additional kwargs but ignore them for compatibility
    ):
        """
        Initialize a connection error.

        Args:
            message: Error message
            cause: The underlying exception that caused this error
        """
        super().__init__(
            status=None,
            error=None,
            message=message or "Connection error.",
            headers=None,
        )
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
        super().__init__(message=message or "Request timed out.")


class BadRequestError(APIError):
    """Raised when the API returns a 400 status code."""

    def __init__(
        self,
        status: int,
        error: Any,
        message: Optional[str],
        headers: Optional[Dict[str, str]],
        endpoint: Optional[str] = None,
    ):
        super().__init__(status, error, message, headers, endpoint)
        # Ensure status is always 400 for this error type
        self.status = 400


class AuthenticationError(APIError):
    """Raised when the API returns a 401 status code."""

    def __init__(
        self,
        status: int,
        error: Any,
        message: Optional[str],
        headers: Optional[Dict[str, str]],
        endpoint: Optional[str] = None,
    ):
        super().__init__(status, error, message, headers, endpoint)
        self.status = 401


class PermissionDeniedError(APIError):
    """Raised when the API returns a 403 status code."""

    def __init__(
        self,
        status: int,
        error: Any,
        message: Optional[str],
        headers: Optional[Dict[str, str]],
        endpoint: Optional[str] = None,
    ):
        super().__init__(status, error, message, headers, endpoint)
        self.status = 403


class NotFoundError(APIError):
    """Raised when the API returns a 404 status code."""

    def __init__(
        self,
        status: int,
        error: Any,
        message: Optional[str],
        headers: Optional[Dict[str, str]],
        endpoint: Optional[str] = None,
    ):
        super().__init__(status, error, message, headers, endpoint)
        self.status = 404


class ConflictError(APIError):
    """Raised when the API returns a 409 status code."""

    def __init__(
        self,
        status: int,
        error: Any,
        message: Optional[str],
        headers: Optional[Dict[str, str]],
        endpoint: Optional[str] = None,
    ):
        super().__init__(status, error, message, headers, endpoint)
        self.status = 409


class UnprocessableEntityError(APIError):
    """Raised when the API returns a 422 status code."""

    def __init__(
        self,
        status: int,
        error: Any,
        message: Optional[str],
        headers: Optional[Dict[str, str]],
        endpoint: Optional[str] = None,
    ):
        super().__init__(status, error, message, headers, endpoint)
        self.status = 422


class RateLimitError(APIError):
    """Raised when the API returns a 429 status code."""

    def __init__(
        self,
        status: int,
        error: Any,
        message: Optional[str],
        headers: Optional[Dict[str, str]],
        endpoint: Optional[str] = None,
    ):
        super().__init__(status, error, message, headers, endpoint)
        self.status = 429


class InternalServerError(APIError):
    """Raised when the API returns a 5xx status code."""

    def __init__(
        self,
        status: int,
        error: Any,
        message: Optional[str],
        headers: Optional[Dict[str, str]],
        endpoint: Optional[str] = None,
    ):
        super().__init__(status, error, message, headers, endpoint)
        # Keep the original status for server errors (could be 500, 502, 503, etc.)
