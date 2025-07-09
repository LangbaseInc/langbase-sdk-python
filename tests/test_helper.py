"""
Tests for streaming helper functions.
"""

import copy
import json
import unittest
from unittest.mock import Mock

from langbase.helper import (
    ChoiceStream,
    ChunkStream,
    Delta,
    StreamProcessor,
    collect_stream_text,
    get_text_part,
    get_tools_from_run,
    get_tools_from_stream,
    handle_response_stream,
    parse_chunk,
    stream_text,
)


class TestStreamingHelpers(unittest.TestCase):
    """Test cases for streaming helper functions."""

    def setUp(self):
        """Set up test fixtures."""
        self.sample_chunk_data = {
            "id": "chatcmpl-123",
            "object": "chat.completion.chunk",
            "created": 1677825464,
            "model": "gpt-3.5-turbo",
            "choices": [
                {
                    "index": 0,
                    "delta": {"role": "assistant", "content": "Hello, world!"},
                    "logprobs": None,
                    "finish_reason": None,
                }
            ],
        }

        self.sample_chunk_bytes = (
            f"data: {json.dumps(self.sample_chunk_data)}\n\n".encode("utf-8")
        )
        self.sample_empty_chunk = b"data: \n\n"
        self.sample_invalid_chunk = b"invalid json data"

    def test_delta_properties(self):
        """Test Delta class properties."""
        delta_data = {
            "role": "assistant",
            "content": "Hello!",
            "tool_calls": [
                {"id": "call_123", "type": "function", "function": {"name": "test"}}
            ],
        }
        delta = Delta(delta_data)

        self.assertEqual(delta.role, "assistant")
        self.assertEqual(delta.content, "Hello!")
        self.assertIsNotNone(delta.tool_calls)
        self.assertEqual(len(delta.tool_calls), 1)

    def test_choice_stream_properties(self):
        """Test ChoiceStream class properties."""
        choice_data = {
            "index": 0,
            "delta": {"content": "Test content"},
            "logprobs": None,
            "finish_reason": "stop",
        }
        choice = ChoiceStream(choice_data)

        self.assertEqual(choice.index, 0)
        self.assertIsInstance(choice.delta, Delta)
        self.assertEqual(choice.delta.content, "Test content")
        self.assertIsNone(choice.logprobs)
        self.assertEqual(choice.finish_reason, "stop")

    def test_chunk_stream_properties(self):
        """Test ChunkStream class properties."""
        chunk = ChunkStream(self.sample_chunk_data)

        self.assertEqual(chunk.id, "chatcmpl-123")
        self.assertEqual(chunk.object, "chat.completion.chunk")
        self.assertEqual(chunk.created, 1677825464)
        self.assertEqual(chunk.model, "gpt-3.5-turbo")
        self.assertEqual(len(chunk.choices), 1)
        self.assertIsInstance(chunk.choices[0], ChoiceStream)

    def test_parse_chunk(self):
        """Test parse_chunk function."""
        # Test valid chunk
        chunk = parse_chunk(self.sample_chunk_bytes)
        self.assertIsNotNone(chunk)
        self.assertIsInstance(chunk, ChunkStream)
        self.assertEqual(chunk.id, "chatcmpl-123")

        # Test empty chunk
        chunk = parse_chunk(self.sample_empty_chunk)
        self.assertIsNone(chunk)

        # Test invalid chunk
        chunk = parse_chunk(self.sample_invalid_chunk)
        self.assertIsNone(chunk)

    def test_get_text_part(self):
        """Test get_text_part function."""
        # Test with ChunkStream
        chunk = ChunkStream(self.sample_chunk_data)
        text = get_text_part(chunk)
        self.assertEqual(text, "Hello, world!")

        # Test with dict
        text = get_text_part(self.sample_chunk_data)
        self.assertEqual(text, "Hello, world!")

        # Test with empty choices
        empty_chunk = {"choices": []}
        text = get_text_part(empty_chunk)
        self.assertEqual(text, "")

    def test_stream_text(self):
        """Test stream_text generator function."""
        # Create a mock stream
        stream = [
            self.sample_chunk_bytes,
            self.sample_empty_chunk,
            self.sample_chunk_bytes,
        ]

        texts = list(stream_text(stream))
        self.assertEqual(len(texts), 2)  # Two valid chunks
        self.assertEqual(texts[0], "Hello, world!")
        self.assertEqual(texts[1], "Hello, world!")

    def test_collect_stream_text(self):
        """Test collect_stream_text function."""
        # Create a mock stream with multiple text chunks
        chunk1_data = copy.deepcopy(self.sample_chunk_data)
        chunk1_data["choices"][0]["delta"]["content"] = "Hello"

        chunk2_data = copy.deepcopy(self.sample_chunk_data)
        chunk2_data["choices"][0]["delta"]["content"] = ", world!"

        chunk1_bytes = f"data: {json.dumps(chunk1_data)}\n\n".encode("utf-8")
        chunk2_bytes = f"data: {json.dumps(chunk2_data)}\n\n".encode("utf-8")

        stream = [chunk1_bytes, chunk2_bytes]
        full_text = collect_stream_text(stream)
        self.assertEqual(full_text, "Hello, world!")

    def test_get_tools_from_run(self):
        """Test get_tools_from_run function."""
        # Test response with tool calls
        response_with_tools = {
            "choices": [
                {
                    "message": {
                        "tool_calls": [
                            {
                                "id": "call_123",
                                "type": "function",
                                "function": {"name": "test_tool"},
                            }
                        ]
                    }
                }
            ]
        }

        tools = get_tools_from_run(response_with_tools)
        self.assertEqual(len(tools), 1)
        self.assertEqual(tools[0]["id"], "call_123")

        # Test response without tool calls
        response_without_tools = {"choices": [{"message": {}}]}

        tools = get_tools_from_run(response_without_tools)
        self.assertEqual(len(tools), 0)

        # Test empty response
        tools = get_tools_from_run({})
        self.assertEqual(len(tools), 0)

    def test_get_tools_from_stream(self):
        """Test get_tools_from_stream function."""
        # Create chunk with tool calls
        chunk_with_tools = {
            "id": "chatcmpl-123",
            "object": "chat.completion.chunk",
            "created": 1677825464,
            "model": "gpt-3.5-turbo",
            "choices": [
                {
                    "index": 0,
                    "delta": {
                        "tool_calls": [
                            {
                                "id": "call_123",
                                "type": "function",
                                "function": {"name": "test_tool"},
                            }
                        ]
                    },
                }
            ],
        }

        chunk_bytes = f"data: {json.dumps(chunk_with_tools)}\n\n".encode("utf-8")
        stream = [chunk_bytes]

        tools = get_tools_from_stream(stream)
        self.assertEqual(len(tools), 1)
        self.assertEqual(tools[0]["id"], "call_123")

    def test_handle_response_stream(self):
        """Test handle_response_stream function."""
        # Mock response object
        mock_response = Mock()
        mock_response.iter_lines.return_value = [self.sample_chunk_bytes]
        mock_response.headers = {"lb-thread-id": "thread_123"}

        result = handle_response_stream(mock_response, raw_response=True)

        self.assertIn("stream", result)
        self.assertEqual(result["thread_id"], "thread_123")
        self.assertIn("raw_response", result)
        self.assertIn("headers", result["raw_response"])

    def test_stream_processor(self):
        """Test StreamProcessor class."""
        # Create a mock stream
        chunk1_data = copy.deepcopy(self.sample_chunk_data)
        chunk1_data["choices"][0]["delta"]["content"] = "Hello"

        chunk2_data = copy.deepcopy(self.sample_chunk_data)
        chunk2_data["choices"][0]["delta"]["content"] = " world!"

        chunk1_bytes = f"data: {json.dumps(chunk1_data)}\n\n".encode("utf-8")
        chunk2_bytes = f"data: {json.dumps(chunk2_data)}\n\n".encode("utf-8")

        stream = [chunk1_bytes, chunk2_bytes]
        processor = StreamProcessor(stream)

        # Test text collection
        full_text = processor.collect_text()
        self.assertEqual(full_text, "Hello world!")

        # Test chunk processing
        stream = [chunk1_bytes, chunk2_bytes]  # Reset stream
        processor = StreamProcessor(stream)
        chunks = list(processor.process_chunks())
        self.assertEqual(len(chunks), 2)
        self.assertIsInstance(chunks[0], ChunkStream)


if __name__ == "__main__":
    unittest.main()
