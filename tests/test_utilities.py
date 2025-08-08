"""
Tests for utility methods.
"""

import json

import responses

from langbase.constants import (
    AGENT_RUN_ENDPOINT,
    BASE_URL,
    CHUNKER_ENDPOINT,
    EMBED_ENDPOINT,
    PARSER_ENDPOINT,
)
from langbase.types import (
    AgentRunResponse,
    ChunkResponse,
    EmbedResponse,
    ParseResponse,
    RunResponseStream,
)
from tests.constants import (
    AUTH_AND_JSON_CONTENT_HEADER,
    AUTHORIZATION_HEADER,
    JSON_CONTENT_TYPE_HEADER,
)
from tests.validation_utils import validate_response_headers


class TestUtilities:
    """Test utility methods."""

    @responses.activate
    def test_embed_with_model(self, langbase_client, mock_responses):
        """Test embed method with specific model."""
        request_body = {
            "chunks": ["First chunk", "Second chunk"],
            "embeddingModel": "openai:text-embedding-ada-002",
        }

        responses.add(
            responses.POST,
            f"{BASE_URL}{EMBED_ENDPOINT}",
            json=mock_responses["embed"],
            status=200,
        )

        result = langbase_client.embed(
            request_body["chunks"], embedding_model="openai:text-embedding-ada-002"
        )

        assert result == mock_responses["embed"]
        assert len(responses.calls) == 1
        request = responses.calls[0].request
        validate_response_headers(request.headers, AUTH_AND_JSON_CONTENT_HEADER)
        assert json.loads(request.body) == request_body

    @responses.activate
    def test_chunker_with_parameters(self, langbase_client, mock_responses):
        """Test chunker method with custom parameters."""
        request_body = {
            "content": "Long document content for chunking test.",
            "chunkMaxLength": 500,
            "chunkOverlap": 50,
        }

        responses.add(
            responses.POST,
            f"{BASE_URL}{CHUNKER_ENDPOINT}",
            json=mock_responses["chunker"],
            status=200,
        )

        result = langbase_client.chunker(
            content=request_body["content"],
            chunk_max_length=request_body["chunkMaxLength"],
            chunk_overlap=request_body["chunkOverlap"],
        )

        assert result == mock_responses["chunker"]
        assert len(responses.calls) == 1
        request = responses.calls[0].request
        validate_response_headers(request.headers, AUTH_AND_JSON_CONTENT_HEADER)
        assert json.loads(request.body) == request_body

    @responses.activate
    def test_parser_with_different_content_types(
        self, langbase_client, mock_responses, upload_file_content
    ):
        """Test parser method with different content types."""
        test_cases = [
            ("document.pdf", "application/pdf"),
            (
                "document.docx",
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            ),
            ("document.txt", "text/plain"),
        ]

        for i, (document_name, content_type) in enumerate(test_cases):
            responses.add(
                responses.POST,
                f"{BASE_URL}{PARSER_ENDPOINT}",
                json=mock_responses["parser"],
                status=200,
            )

            result = langbase_client.parser(
                document=upload_file_content,
                document_name=document_name,
                content_type=content_type,
            )

            assert result == {
                "document_name": mock_responses["parser"]["documentName"],
                "content": mock_responses["parser"]["content"],
            }
            # The number of calls increases with each iteration
            assert len(responses.calls) == i + 1
            request = responses.calls[i].request
            validate_response_headers(request.headers, AUTHORIZATION_HEADER)

    @responses.activate
    def test_agent_run_basic(self, langbase_client, mock_responses):
        """Test agent.run method with basic parameters."""
        request_body = {
            "input": "Hello, agent!",
            "model": "anthropic:claude-3-sonnet",
            "apiKey": "test-llm-key",
        }

        responses.add(
            responses.POST,
            f"{BASE_URL}{AGENT_RUN_ENDPOINT}",
            json=mock_responses["agent.run"],
            status=200,
        )

        result = langbase_client.agent.run(
            input=request_body["input"],
            model=request_body["model"],
            api_key=request_body["apiKey"],
        )

        assert result == mock_responses["agent.run"]
        assert len(responses.calls) == 1
        request = responses.calls[0].request
        validate_response_headers(request.headers, AUTH_AND_JSON_CONTENT_HEADER)
        assert json.loads(request.body) == request_body

    @responses.activate
    def test_agent_run_with_messages(self, langbase_client, mock_responses):
        """Test agent.run method with message format input."""
        request_body = {
            "input": [
                {"role": "user", "content": "Hello"},
                {"role": "assistant", "content": "Hi there!"},
            ],
            "model": "openai:gpt-4",
            "apiKey": "openai-key",
        }

        responses.add(
            responses.POST,
            f"{BASE_URL}{AGENT_RUN_ENDPOINT}",
            json=mock_responses["agent.run"],
            status=200,
        )

        result = langbase_client.agent.run(
            input=request_body["input"],
            model=request_body["model"],
            api_key=request_body["apiKey"],
        )

        assert result == mock_responses["agent.run"]
        assert len(responses.calls) == 1
        request = responses.calls[0].request
        validate_response_headers(request.headers, AUTH_AND_JSON_CONTENT_HEADER)
        assert json.loads(request.body) == request_body

    @responses.activate
    def test_agent_run_with_all_parameters(self, langbase_client, mock_responses):
        """Test agent.run method with all parameters."""
        request_body = {
            "input": "Complex query",
            "model": "anthropic:claude-3-sonnet",
            "apiKey": "test-key",
            "instructions": "Be helpful and concise",
            "temperature": 0.7,
            "max_tokens": 150,
            "top_p": 0.9,
            "tools": [{"type": "function", "function": {"name": "test"}}],
        }

        responses.add(
            responses.POST,
            f"{BASE_URL}{AGENT_RUN_ENDPOINT}",
            json=mock_responses["agent.run"],
            status=200,
        )

        result = langbase_client.agent.run(
            input=request_body["input"],
            model=request_body["model"],
            api_key=request_body["apiKey"],
            instructions=request_body["instructions"],
            temperature=request_body["temperature"],
            max_tokens=request_body["max_tokens"],
            top_p=request_body["top_p"],
            tools=request_body["tools"],
            stream=False,
        )

        assert result == mock_responses["agent.run"]
        assert len(responses.calls) == 1
        request = responses.calls[0].request
        validate_response_headers(request.headers, AUTH_AND_JSON_CONTENT_HEADER)
        assert json.loads(request.body) == request_body

    @responses.activate
    def test_agent_run_streaming(self, langbase_client, stream_chunks):
        """Test agent.run method with streaming."""
        request_body = {
            "input": "Streaming query",
            "model": "openai:gpt-4",
            "apiKey": "stream-key",
            "stream": True,
        }
        stream_content = b"".join(stream_chunks)

        responses.add(
            responses.POST,
            f"{BASE_URL}{AGENT_RUN_ENDPOINT}",
            body=stream_content,
            status=200,
            headers={"Content-Type": "text/event-stream"},
        )

        result = langbase_client.agent.run(
            input=request_body["input"],
            model=request_body["model"],
            api_key=request_body["apiKey"],
            stream=True,
        )

        assert "stream" in result
        assert hasattr(result["stream"], "__iter__")
        assert len(responses.calls) == 1
        request = responses.calls[0].request
        validate_response_headers(request.headers, AUTH_AND_JSON_CONTENT_HEADER)
        assert json.loads(request.body) == request_body

    @responses.activate
    def test_agent_run_structured_output(self, langbase_client, mock_responses):
        """Test agent.run method with structured output."""
        math_reasoning_schema = {
            "type": "object",
            "properties": {
                "steps": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "explanation": {"type": "string"},
                            "output": {"type": "string"},
                        },
                        "required": ["explanation", "output"],
                    },
                },
                "final_answer": {"type": "string"},
            },
            "required": ["steps", "final_answer"],
        }

        request_body = {
            "input": [{"role": "user", "content": "How can I solve 8x + 22 = -23?"}],
            "model": "openai:gpt-4.1",
            "apiKey": "test-openai-key",
            "instructions": "You are a helpful math tutor. Guide the user through the solution step by step.",
            "response_format": {
                "type": "json_schema",
                "json_schema": {
                    "name": "math_reasoning",
                    "schema": math_reasoning_schema,
                },
            },
        }

        responses.add(
            responses.POST,
            f"{BASE_URL}{AGENT_RUN_ENDPOINT}",
            json=mock_responses["agent.run.structured"],
            status=200,
        )

        result = langbase_client.agent.run(
            input=request_body["input"],
            model=request_body["model"],
            api_key=request_body["apiKey"],
            instructions=request_body["instructions"],
            response_format=request_body["response_format"],
        )

        assert result == mock_responses["agent.run.structured"]
        assert len(responses.calls) == 1
        request = responses.calls[0].request
        validate_response_headers(request.headers, AUTH_AND_JSON_CONTENT_HEADER)
        assert json.loads(request.body) == request_body

        # Verify structured output format
        assert "output" in result
        output_data = json.loads(result["output"])
        assert "steps" in output_data
        assert "final_answer" in output_data
        assert isinstance(output_data["steps"], list)
        assert len(output_data["steps"]) > 0

    @responses.activate
    def test_agent_run_tool_call(self, langbase_client, mock_responses):
        """Test agent.run method with tool calls."""
        send_email_tool_schema = {
            "type": "function",
            "function": {
                "name": "send_email",
                "description": "Send an email using Resend API",
                "parameters": {
                    "type": "object",
                    "required": ["from", "to", "subject", "html", "text"],
                    "properties": {
                        "from": {"type": "string"},
                        "to": {"type": "string"},
                        "subject": {"type": "string"},
                        "html": {"type": "string"},
                        "text": {"type": "string"},
                    },
                    "additionalProperties": False,
                },
            },
        }

        request_body = {
            "input": [{"role": "user", "content": "Send a welcome email to Sam."}],
            "model": "openai:gpt-4.1-mini",
            "apiKey": "test-openai-key",
            "instructions": "You are an email agent. You are given a task to send an email to a recipient. You have the ability to send an email using the send_email tool.",
            "tools": [send_email_tool_schema],
        }

        responses.add(
            responses.POST,
            f"{BASE_URL}{AGENT_RUN_ENDPOINT}",
            json=mock_responses["agent.run.tool"],
            status=200,
        )

        result = langbase_client.agent.run(
            input=request_body["input"],
            model=request_body["model"],
            api_key=request_body["apiKey"],
            instructions=request_body["instructions"],
            tools=request_body["tools"],
            stream=False,
        )

        assert result == mock_responses["agent.run.tool"]
        assert len(responses.calls) == 1
        request = responses.calls[0].request
        validate_response_headers(request.headers, AUTH_AND_JSON_CONTENT_HEADER)
        assert json.loads(request.body) == request_body

        # Verify tool call structure
        assert "choices" in result
        choices = result["choices"]
        assert len(choices) > 0
        message = choices[0]["message"]
        assert "tool_calls" in message
        tool_calls = message["tool_calls"]
        assert len(tool_calls) > 0

        tool_call = tool_calls[0]
        assert tool_call["type"] == "function"
        assert "function" in tool_call
        function = tool_call["function"]
        assert function["name"] == "send_email"
        assert "arguments" in function

    @responses.activate
    def test_agent_run_tool_call_final_response(self, langbase_client, mock_responses):
        """Test agent.run method with tool call final response."""
        # Simulate messages after tool execution
        input_messages = [
            {"role": "user", "content": "Send a welcome email to Sam."},
            {
                "role": "assistant",
                "content": None,
                "tool_calls": [
                    {
                        "id": "call_123456789",
                        "type": "function",
                        "function": {
                            "name": "send_email",
                            "arguments": '{"from": "onboarding@resend.dev", "to": "sam@example.com", "subject": "Welcome to Langbase!", "html": "Hello Sam! Welcome to Langbase.", "text": "Hello Sam! Welcome to Langbase."}',
                        },
                    }
                ],
            },
            {
                "role": "tool",
                "tool_call_id": "call_123456789",
                "name": "send_email",
                "content": "✅ Email sent successfully to sam@example.com!",
            },
        ]

        request_body = {
            "input": input_messages,
            "model": "openai:gpt-4.1-mini",
            "apiKey": "test-openai-key",
            "instructions": "You are an email sending assistant. Confirm the email has been sent successfully.",
        }

        responses.add(
            responses.POST,
            f"{BASE_URL}{AGENT_RUN_ENDPOINT}",
            json=mock_responses["agent.run.tool.final"],
            status=200,
        )

        result = langbase_client.agent.run(
            input=request_body["input"],
            model=request_body["model"],
            api_key=request_body["apiKey"],
            instructions=request_body["instructions"],
            stream=False,
        )

        assert result == mock_responses["agent.run.tool.final"]
        assert len(responses.calls) == 1
        request = responses.calls[0].request
        validate_response_headers(request.headers, AUTH_AND_JSON_CONTENT_HEADER)
        assert json.loads(request.body) == request_body

        # Verify final response structure
        assert "output" in result
        assert result["output"] == "✅ Email sent successfully to sam@example.com!"
        assert "choices" in result
        choices = result["choices"]
        assert len(choices) > 0
        message = choices[0]["message"]
        assert message["role"] == "assistant"
        assert message["content"] == "✅ Email sent successfully to sam@example.com!"
