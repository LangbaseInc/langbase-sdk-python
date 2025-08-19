"""
Error handling for the Langbase SDK.

This module provides error classes for handling API responses.
"""

import json
from typing import Any, Dict, Optional


class APIError(Exception):
    """Base API error that holds response information and formats error output."""

    def __init__(
        self,
        status_code: Optional[int] = None,
        error: Optional[Dict[str, Any]] = None,
        message: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
    ):
        """
        Initialize an API error.

        Args:
            status_code: HTTP status code from the API response
            error: Parsed error object from API response
            message: Custom error message (if not using API response)
            headers: HTTP response headers
        """
        if (
            isinstance(status_code, str)
            and error is None
            and headers is None
            and message is None
        ):
            message = status_code
            status_code = None

        self.status_code = status_code
        self.error = error
        self.headers = headers or {}
        self.request_id = self.headers.get("lb-request-id")

        # Extract additional fields from error object
        if isinstance(error, dict):
            self.code = error.get("code")
            self.param = error.get("param")
            self.type = error.get("type")
        else:
            self.code = None
            self.param = None
            self.type = None

        error_message = self._make_message(status_code, error, message)
        super().__init__(error_message)

    def _make_message(
        self,
        status_code: Optional[int],
        error: Optional[Dict[str, Any]],
        message: Optional[str],
    ) -> str:
        """Create error message from available information."""
        if error:
            if isinstance(error, dict) and "message" in error:
                msg = error["message"]
                if isinstance(msg, str):
                    msg = msg
                else:
                    msg = json.dumps(msg)
            else:
                msg = json.dumps(error)
        else:
            msg = message

        if status_code and msg:
            return f"{status_code} {msg}"
        elif status_code:
            return f"{status_code} status code (no body)"
        elif msg:
            return msg
        else:
            return "API request failed"

    def __str__(self) -> str:
        """String representation of the error in JSON format."""
        error_data = {
            "status": self.status_code,
            "headers": {},
            "request_id": self.request_id,
            "error": self.error or {"message": str(super().__str__())},
            "code": self.code or "API_ERROR",
        }

        return json.dumps(error_data, indent=2)


class APIConnectionError(APIError):
    """Raised when there's a connection problem (not an API error response)."""

    def __init__(
        self, message: str = "Connection error.", cause: Optional[Exception] = None
    ):
        """
        Initialize a connection error.

        Args:
            message: Error message
            cause: The underlying exception that caused this error
        """
        super().__init__(message=message)
        if cause:
            self.__cause__ = cause


class BadRequestError(APIError):
    """Raised when the API returns a 400 Bad Request error."""

    pass


class AuthenticationError(APIError):
    """Raised when the API returns a 401 Unauthorized error."""

    pass


class PermissionDeniedError(APIError):
    """Raised when the API returns a 403 Forbidden error."""

    pass


class NotFoundError(APIError):
    """Raised when the API returns a 404 Not Found error."""

    pass


class ConflictError(APIError):
    """Raised when the API returns a 409 Conflict error."""

    pass


class UnprocessableEntityError(APIError):
    """Raised when the API returns a 422 Unprocessable Entity error."""

    pass


class RateLimitError(APIError):
    """Raised when the API returns a 429 Too Many Requests error."""

    pass


class InternalServerError(APIError):
    """Raised when the API returns a 5xx Internal Server Error."""

    pass


def create_api_error(
    status_code: Optional[int] = None,
    response_text: Optional[str] = None,
    headers: Optional[Dict[str, str]] = None,
    message: Optional[str] = None,
) -> APIError:
    """
    Create the appropriate API error based on status code.

    Args:
        status_code: HTTP status code from the API response
        response_text: Raw response text from the API
        headers: HTTP response headers
        message: Custom error message

    Returns:
        Appropriate APIError subclass based on status code
    """
    if not status_code:
        return APIConnectionError(message or "Connection error.")

    # Parse error from response text
    error = None
    if response_text:
        try:
            response_data = json.loads(response_text)
            if isinstance(response_data, dict) and "error" in response_data:
                error = response_data["error"]
        except json.JSONDecodeError:
            pass

    # Map status codes to specific error classes
    error_classes = {
        400: BadRequestError,
        401: AuthenticationError,
        403: PermissionDeniedError,
        404: NotFoundError,
        409: ConflictError,
        422: UnprocessableEntityError,
        429: RateLimitError,
    }

    if status_code in error_classes:
        return error_classes[status_code](status_code, error, message, headers)
    elif status_code >= 500:
        return InternalServerError(status_code, error, message, headers)
    else:
        return APIError(status_code, error, message, headers)
