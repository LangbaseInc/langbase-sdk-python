"""
Request handling for the Langbase SDK.

This module provides the Request class which handles all HTTP communication
with the Langbase API, including error handling and response parsing.
"""

import json
from typing import Any, Dict, Iterator, Optional, Union

import requests

from .errors import APIConnectionError, APIConnectionTimeoutError, APIError
from .types import GENERATION_ENDPOINTS


class Request:
    """
    Handles HTTP requests to the Langbase API.

    This class is responsible for handling all HTTP communication with the Langbase API,
    including building requests, handling responses, and processing errors.
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize a Request handler.

        Args:
            config: Configuration dictionary containing:
                - api_key: API key for authentication
                - base_url: Base URL for the API
        """
        self.config = config
        self.api_key = config.get("api_key", "")
        self.base_url = config.get("base_url", "")

    def build_url(self, endpoint: str) -> str:
        """
        Build the complete URL for the API request.

        Args:
            endpoint: API endpoint path (should start with /)

        Returns:
            Complete URL for the request
        """
        # Ensure the endpoint starts with a slash
        if not endpoint.startswith("/"):
            endpoint = f"/{endpoint}"

        return f"{self.base_url}{endpoint}"

    def build_headers(self, headers: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        """
        Build headers for the API request.

        Args:
            headers: Additional headers to include

        Returns:
            Dictionary of headers for the request
        """
        default_headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }

        if headers:
            default_headers.update(headers)

        return default_headers

    def make_request(
        self,
        url: str,
        method: str,
        headers: Dict[str, str],
        body: Optional[Dict[str, Any]] = None,
        stream: bool = False,
        files: Optional[Dict[str, Any]] = None,
    ) -> requests.Response:
        """
        Make an HTTP request to the API.

        Args:
            url: URL to request
            method: HTTP method (GET, POST, etc.)
            headers: HTTP headers
            body: Request body (for methods like POST)
            stream: Whether to stream the response
            files: Files to upload (for multipart/form-data requests)

        Returns:
            Response object

        Raises:
            APIConnectionError: If the request fails
            APIConnectionTimeoutError: If the request times out
        """
        try:
            # If files are provided, don't send JSON body
            if files:
                response = requests.request(
                    method=method,
                    url=url,
                    headers={k: v for k, v in headers.items() if k != "Content-Type"},
                    files=files,
                    stream=stream,
                )
            else:
                response = requests.request(
                    method=method,
                    url=url,
                    headers=headers,
                    json=body if body else None,
                    stream=stream,
                )
            return response
        except requests.Timeout as e:
            raise APIConnectionTimeoutError(str(e))
        except requests.RequestException as e:
            raise APIConnectionError(cause=e)

    def handle_error_response(self, response: requests.Response) -> None:
        """
        Handle error responses from the API.

        Args:
            response: Error response from the API

        Raises:
            APIError: With appropriate subclass based on status code
        """
        try:
            error_body = response.json()
        except json.JSONDecodeError:
            error_body = response.text

        raise APIError.generate(
            response.status_code, error_body, response.reason, dict(response.headers)
        )

    def handle_stream_response(
        self, response: requests.Response
    ) -> Dict[str, Union[Iterator[bytes], Optional[str]]]:
        """
        Handle streaming responses.

        Args:
            response: Response object with streaming enabled

        Returns:
            Dictionary with stream and thread_id
        """
        return {
            "stream": response.iter_lines(),
            "thread_id": response.headers.get("lb-thread-id"),
        }

    def handle_run_response_stream(
        self, response: requests.Response, raw_response: bool = False
    ) -> Dict[str, Any]:
        """
        Handle streaming responses for run endpoints.

        Args:
            response: Response object with streaming enabled
            raw_response: Whether to include raw response headers

        Returns:
            Dictionary with stream, thread_id, and optionally raw_response
        """
        result = {
            "stream": response.iter_lines(),
            "thread_id": response.headers.get("lb-thread-id"),
        }

        if raw_response:
            result["rawResponse"] = {"headers": dict(response.headers)}

        return result

    def handle_run_response(
        self, response, thread_id, raw_response=False, endpoint=None
    ):
        """
        Handle regular responses for run endpoints.

        Args:
            response: Response object
            thread_id: Thread ID from response headers
            raw_response: Whether to include raw response headers
            endpoint: The API endpoint being called

        Returns:
            Processed response dictionary
        """
        generate_response = response.json()
        is_agent_run = endpoint == "/v1/agent/run" if endpoint else False

        build_response = (
            {
                "output" if is_agent_run else "completion": generate_response.get(
                    "output" if is_agent_run else "completion"
                ),
                **generate_response.get("raw", {}),
            }
            if generate_response.get("raw")
            else generate_response
        )

        result = {**build_response}

        if thread_id:
            result["threadId"] = thread_id

        if raw_response:
            result["rawResponse"] = {"headers": dict(response.headers)}

        return result

    def is_generation_endpoint(self, endpoint: str) -> bool:
        """
        Check if an endpoint is a generation endpoint.

        Args:
            endpoint: API endpoint path

        Returns:
            True if the endpoint is a generation endpoint, False otherwise
        """
        return any(
            endpoint.startswith(gen_endpoint) for gen_endpoint in GENERATION_ENDPOINTS
        )

    def send(
        self,
        endpoint: str,
        method: str,
        headers: Optional[Dict[str, str]] = None,
        body: Optional[Dict[str, Any]] = None,
        stream: bool = False,
        files: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """
        Send a request to the API and handle the response.

        Args:
            endpoint: API endpoint path
            method: HTTP method
            headers: Additional headers
            body: Request body
            stream: Whether to stream the response
            files: Files to upload (for multipart/form-data requests)

        Returns:
            Processed API response

        Raises:
            APIError: If the API returns an error
        """
        url = self.build_url(endpoint)
        request_headers = self.build_headers(headers)

        response = self.make_request(url, method, request_headers, body, stream, files)

        if not response.ok:
            self.handle_error_response(response)

        # Check if this is a generation endpoint
        if self.is_generation_endpoint(endpoint):
            thread_id = response.headers.get("lb-thread-id")

            if not body:
                return self.handle_run_response(
                    response,
                    thread_id=None,
                    raw_response=body.get("raw_response", False) if body else False,
                    endpoint=endpoint,
                )

            if body.get("stream") and "run" in url:
                return self.handle_run_response_stream(
                    response, raw_response=body.get("raw_response", False)
                )

            if body.get("stream"):
                return self.handle_stream_response(response)

            return self.handle_run_response(
                response,
                thread_id=thread_id,
                raw_response=body.get("raw_response", False),
                endpoint=endpoint,
            )
        # For non-generation endpoints, just return the JSON response
        try:
            return response.json()
        except json.JSONDecodeError:
            # If the response is not JSON, return the text
            return {"text": response.text}

    def post(
        self,
        endpoint: str,
        body: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        stream: bool = False,
        files: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """
        Send a POST request to the API.

        Args:
            endpoint: API endpoint path
            body: Request body
            headers: Additional headers
            stream: Whether to stream the response
            files: Files to upload (for multipart/form-data requests)

        Returns:
            Processed API response
        """
        return self.send(endpoint, "POST", headers, body, stream, files)

    def get(
        self,
        endpoint: str,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """
        Send a GET request to the API.

        Args:
            endpoint: API endpoint path
            headers: Additional headers
            params: Query parameters

        Returns:
            Processed API response
        """
        # Add query parameters to the endpoint if provided
        if params:
            query_string = "&".join([f"{k}={v}" for k, v in params.items()])
            if "?" in endpoint:
                endpoint = f"{endpoint}&{query_string}"
            else:
                endpoint = f"{endpoint}?{query_string}"

        return self.send(endpoint, "GET", headers)

    def put(
        self,
        endpoint: str,
        body: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        files: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """
        Send a PUT request to the API.

        Args:
            endpoint: API endpoint path
            body: Request body
            headers: Additional headers
            files: Files to upload (for multipart/form-data requests)

        Returns:
            Processed API response
        """
        return self.send(endpoint, "PUT", headers, body, files=files)

    def delete(self, endpoint: str, headers: Optional[Dict[str, str]] = None) -> Any:
        """
        Send a DELETE request to the API.

        Args:
            endpoint: API endpoint path
            headers: Additional headers

        Returns:
            Processed API response
        """
        return self.send(endpoint, "DELETE", headers)
