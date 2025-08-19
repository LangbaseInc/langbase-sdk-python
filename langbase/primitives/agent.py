"""
Agent API client for the Langbase SDK.
"""

from typing import Any, Dict, List, Literal, Optional, Union, overload

from langbase.constants import AGENT_RUN_ENDPOINT
from langbase.request import Request
from langbase.types import McpServerSchema, Message, ToolChoice, Tools
from langbase.utils import clean_null_values


class Agent:
    def __init__(self, parent):
        self.parent = parent
        self.request: Request = parent.request

    @overload
    def run(
        self,
        input: Union[str, List[Message]],
        model: str,
        api_key: str,
        instructions: Optional[str] = None,
        top_p: Optional[float] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        presence_penalty: Optional[float] = None,
        frequency_penalty: Optional[float] = None,
        stop: Optional[List[str]] = None,
        tools: Optional[List[Tools]] = None,
        tool_choice: Optional[Union[Literal["auto", "required"], ToolChoice]] = None,
        parallel_tool_calls: Optional[bool] = None,
        reasoning_effort: Optional[str] = None,
        max_completion_tokens: Optional[int] = None,
        response_format: Optional[Dict[str, Any]] = None,
        custom_model_params: Optional[Dict[str, Any]] = None,
        mcp_servers: List[McpServerSchema] = None,
        *,
        stream: bool = True,
    ) -> Any:
        """Stream overload - returns streaming response when stream=True"""
        ...

    @overload
    def run(
        self,
        input: Union[str, List[Message]],
        model: str,
        api_key: str,
        instructions: Optional[str] = None,
        top_p: Optional[float] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        presence_penalty: Optional[float] = None,
        frequency_penalty: Optional[float] = None,
        stop: Optional[List[str]] = None,
        tools: Optional[List[Tools]] = None,
        tool_choice: Optional[Union[Literal["auto", "required"], ToolChoice]] = None,
        parallel_tool_calls: Optional[bool] = None,
        reasoning_effort: Optional[str] = None,
        max_completion_tokens: Optional[int] = None,
        response_format: Optional[Dict[str, Any]] = None,
        custom_model_params: Optional[Dict[str, Any]] = None,
        mcp_servers: List[McpServerSchema] = None,
        stream: bool = False,
    ) -> Dict[str, Any]:
        """Non-stream overload - returns dict response when stream=False"""
        ...

    def run(
        self,
        input: Union[str, List[Message]],
        model: str,
        api_key: str,
        instructions: Optional[str] = None,
        top_p: Optional[float] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        presence_penalty: Optional[float] = None,
        frequency_penalty: Optional[float] = None,
        stop: Optional[List[str]] = None,
        tools: Optional[List[Tools]] = None,
        tool_choice: Optional[Union[Literal["auto", "required"], ToolChoice]] = None,
        parallel_tool_calls: Optional[bool] = None,
        reasoning_effort: Optional[str] = None,
        max_completion_tokens: Optional[int] = None,
        response_format: Optional[Dict[str, Any]] = None,
        custom_model_params: Optional[Dict[str, Any]] = None,
        mcp_servers: List[McpServerSchema] = None,
        stream: bool = False,
    ) -> Union[Dict[str, Any], Any]:
        """
        Run an agent with the specified parameters.

        Args:
            input: Either a string prompt or a list of messages
            model: The model to use for the agent
            api_key: API key for the LLM service
            instructions: Optional instructions for the agent
            top_p: Optional top-p sampling parameter
            max_tokens: Optional maximum tokens to generate
            temperature: Optional temperature parameter
            presence_penalty: Optional presence penalty parameter
            frequency_penalty: Optional frequency penalty parameter
            stop: Optional list of stop sequences
            tools: Optional list of tools for the agent
            tool_choice: Optional tool choice configuration ('auto', 'required', or tool spec)
            parallel_tool_calls: Optional flag for parallel tool execution
            reasoning_effort: Optional reasoning effort level
            max_completion_tokens: Optional maximum completion tokens
            response_format: Optional response format configuration
            custom_model_params: Optional custom model parameters
            mcp_servers: Optional list of MCP (Model Context Protocol) servers
            stream: Whether to stream the response (default: False)

        Returns:
            Either a dictionary with the agent's response or a streaming response
        """
        options = {
            "input": input,
            "model": model,
            "apiKey": api_key,
            "instructions": instructions,
            "top_p": top_p,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "presence_penalty": presence_penalty,
            "frequency_penalty": frequency_penalty,
            "stop": stop,
            "tools": tools,
            "tool_choice": tool_choice,
            "parallel_tool_calls": parallel_tool_calls,
            "reasoning_effort": reasoning_effort,
            "max_completion_tokens": max_completion_tokens,
            "response_format": response_format,
            "customModelParams": custom_model_params,
            "mcp_servers": mcp_servers,
        }

        # Only include stream if it's True
        if stream:
            options["stream"] = True

        # Clean null values from options
        options = clean_null_values(options)

        headers = {}
        if api_key:
            headers["LB-LLM-KEY"] = api_key

        return self.request.post(
            AGENT_RUN_ENDPOINT, options, headers=headers, stream=stream
        )
