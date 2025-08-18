"""
Production-ready error handling for the Langbase SDK.

This module provides simple error classes that match the TypeScript SDK structure.
"""

import json
from typing import Any, Dict, Optional


class APIError(Exception):
    """Base API error that holds response information and formats output like TypeScript SDK."""

    def __init__(
        self,
        status_code: Optional[int] = None,
        response_text: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
        message: Optional[str] = None,
    ):
        """
        Initialize an API error.

        Args:
            status_code: HTTP status code from the API response
            response_text: Raw response text from the API
            headers: HTTP response headers
            message: Custom error message (if not using API response)
        """
        # Handle legacy usage: APIError("message") -> APIError(message="message")
        if (
            isinstance(status_code, str)
            and response_text is None
            and headers is None
            and message is None
        ):
            message = status_code
            status_code = None

        self.status_code = status_code
        self.response_text = response_text
        self.headers = headers or {}
        self.request_id = self.headers.get("lb-request-id")

        # Use API response message if available, otherwise use custom message
        error_message = self._extract_error_message() or message or "API request failed"
        super().__init__(error_message)

    def _extract_error_message(self) -> Optional[str]:
        """Extract error message from API response for Exception.__str__()."""
        if not self.response_text:
            return None

        try:
            response_data = json.loads(self.response_text)
            if isinstance(response_data, dict) and "error" in response_data:
                error_obj = response_data["error"]
                if isinstance(error_obj, dict) and "message" in error_obj:
                    return error_obj["message"]
            return None
        except json.JSONDecodeError:
            return None

    def __str__(self) -> str:
        """String representation of the error matching TypeScript SDK format."""
        # Parse API response once
        api_error = self._parse_api_error()

        # Build error data structure matching TypeScript SDK
        error_data = {
            "status": self.status_code,
            "headers": {},
            "request_id": self.request_id,
            "error": api_error,
            "code": api_error.get("code", "API_ERROR")
            if isinstance(api_error, dict)
            else "API_ERROR",
        }

        return json.dumps(error_data, indent=2)

    def _parse_api_error(self) -> Dict[str, Any]:
        """Parse and extract error information from API response."""
        if not self.response_text:
            return self._create_fallback_error("API request failed")

        try:
            response_json = json.loads(self.response_text)
            if isinstance(response_json, dict) and "error" in response_json:
                return response_json["error"]
            else:
                # Response doesn't have expected error structure
                message = self._extract_simple_message() or "API request failed"
                return self._create_fallback_error(message)
        except json.JSONDecodeError:
            # Invalid JSON response
            message = (
                self.response_text
                if len(self.response_text) < 200
                else "API request failed"
            )
            return self._create_fallback_error(message)

    def _extract_simple_message(self) -> Optional[str]:
        """Extract a simple message from non-standard API responses."""
        try:
            response_data = json.loads(self.response_text)
            if isinstance(response_data, dict):
                # Try common message fields
                for field in ["message", "detail", "description"]:
                    if field in response_data and isinstance(response_data[field], str):
                        return response_data[field]
            return None
        except json.JSONDecodeError:
            return None

    def _create_fallback_error(self, message: str) -> Dict[str, Any]:
        """Create a fallback error structure when API response is malformed."""
        return {
            "code": "API_ERROR",
            "status": self.status_code or 500,
            "message": message,
        }


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
