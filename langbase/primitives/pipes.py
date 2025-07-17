"""
Pipes API client for the Langbase SDK.
"""

from typing import Any, Dict, List, Optional, Union

from langbase.constants import PIPE_DETAIL_ENDPOINT, PIPE_RUN_ENDPOINT, PIPES_ENDPOINT
from langbase.request import Request
from langbase.types import (
    PipeCreateResponse,
    PipeListResponse,
    PipeUpdateResponse,
    RunResponse,
    RunResponseStream,
)
from langbase.utils import clean_null_values


class Pipes:
    def __init__(self, parent):
        self.parent = parent
        self.request: Request = parent.request

    def list(self) -> List[PipeListResponse]:
        """
        List all pipes.

        Returns:
            List of pipe objects
        """
        return self.request.get(PIPES_ENDPOINT)

    def create(
        self, name: str, description: Optional[str] = None, **kwargs
    ) -> PipeCreateResponse:
        """
        Create a new pipe.

        Args:
            name: Name of the pipe
            description: Description of the pipe
            **kwargs: Additional parameters for the pipe

        Returns:
            Created pipe object
        """
        options = {"name": name, "description": description, **kwargs}
        return self.request.post(PIPES_ENDPOINT, clean_null_values(options))

    def update(self, name: str, **kwargs) -> PipeUpdateResponse:
        """
        Update an existing pipe.

        Args:
            name: Name of the pipe to update
            **kwargs: Parameters to update

        Returns:
            Updated pipe object
        """
        options = {"name": name, **kwargs}
        return self.request.post(
            PIPE_DETAIL_ENDPOINT.format(name=name), clean_null_values(options)
        )

    def run(
        self,
        name: Optional[str] = None,
        api_key: Optional[str] = None,
        messages: Optional[List[Dict[str, Any]]] = None,
        variables: Optional[List[Dict[str, str]]] = None,
        thread_id: Optional[str] = None,
        raw_response: Optional[bool] = None,
        run_tools: Optional[bool] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        tool_choice: Optional[Union[str, Dict[str, Any]]] = None,
        parallel_tool_calls: Optional[bool] = None,
        llm_key: Optional[str] = None,
        json: Optional[bool] = None,
        memory: Optional[List[Dict[str, str]]] = None,
        response_format: Optional[Dict[str, Any]] = None,
        top_p: Optional[float] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        presence_penalty: Optional[float] = None,
        frequency_penalty: Optional[float] = None,
        stop: Optional[List[str]] = None,
        store: Optional[bool] = None,
        moderate: Optional[bool] = None,
        stream: Optional[bool] = None,
        **kwargs,
    ) -> Union[RunResponse, RunResponseStream]:
        """
        Run a pipe.

        Args:
            name: Name of the pipe to run
            api_key: API key for the pipe
            messages: List of messages for the conversation
            variables: List of variables for template substitution
            thread_id: Thread ID for conversation continuity
            raw_response: Whether to include raw response headers
            run_tools: Whether to enable tool execution
            tools: List of tools available to the pipe
            tool_choice: Tool choice strategy ('auto', 'required', or tool spec)
            parallel_tool_calls: Whether to enable parallel tool calls
            llm_key: LLM API key for the request
            json: Whether to enable JSON mode
            memory: List of runtime memory configurations
            response_format: Response format configuration
            top_p: Top-p sampling parameter
            max_tokens: Maximum tokens to generate
            temperature: Temperature for randomness
            presence_penalty: Presence penalty parameter
            frequency_penalty: Frequency penalty parameter
            stop: List of stop sequences
            store: Whether to store the conversation
            moderate: Whether to enable content moderation
            stream: Whether to stream the response
            **kwargs: Additional parameters for the run

        Returns:
            Run response or stream
        """
        if not name and not api_key:
            msg = "Either pipe name or API key is required"
            raise ValueError(msg)

        options = {
            "name": name,
            "api_key": api_key,
            "messages": messages or [],
            "variables": variables,
            "thread_id": thread_id,
            "raw_response": raw_response,
            "run_tools": run_tools,
            "tools": tools,
            "tool_choice": tool_choice,
            "parallel_tool_calls": parallel_tool_calls,
            "json": json,
            "memory": memory,
            "response_format": response_format,
            "top_p": top_p,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "presence_penalty": presence_penalty,
            "frequency_penalty": frequency_penalty,
            "stop": stop,
            "store": store,
            "moderate": moderate,
            **kwargs,
        }

        # Only set stream in options if it's explicitly provided
        if stream is not None:
            options["stream"] = stream

        # Create a new request instance if API key is provided
        request = self.request
        if api_key:
            request = Request({"api_key": api_key, "base_url": self.parent.base_url})

        headers = {}
        if llm_key:
            headers["LB-LLM-KEY"] = llm_key

        # Pass the stream parameter to post method (which might be None)
        return request.post(
            PIPE_RUN_ENDPOINT,
            clean_null_values(options),
            headers,
            stream=stream if stream is not None else False,
        )
