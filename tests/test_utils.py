"""
Tests for utility functions.
"""
import os
import unittest
from io import BytesIO
from unittest.mock import patch, mock_open

from langbase.utils import (
    convert_document_to_request_files,
    prepare_headers,
    format_thread_id,
    clean_null_values
)


class TestUtils(unittest.TestCase):
    """Test utility functions."""

    def test_convert_document_to_request_files_bytes(self):
        """Test convert_document_to_request_files with bytes."""
        document = b"Test document content"
        result = convert_document_to_request_files(
            document, "test.txt", "text/plain"
        )

        self.assertIn("document", result)
        self.assertIn("documentName", result)
        self.assertEqual(result["document"][0], "test.txt")
        self.assertEqual(result["document"][1], b"Test document content")
        self.assertEqual(result["document"][2], "text/plain")
        self.assertEqual(result["documentName"], (None, "test.txt"))

    def test_convert_document_to_request_files_bytesio(self):
        """Test convert_document_to_request_files with BytesIO."""
        document = BytesIO(b"Test document content")
        result = convert_document_to_request_files(
            document, "test.txt", "text/plain"
        )

        self.assertIn("document", result)
        self.assertIn("documentName", result)
        self.assertEqual(result["document"][0], "test.txt")
        self.assertEqual(result["document"][1], b"Test document content")
        self.assertEqual(result["document"][2], "text/plain")
        self.assertEqual(result["documentName"], (None, "test.txt"))

        # Check that the file pointer was reset
        self.assertEqual(document.tell(), 0)

    @patch("builtins.open", new_callable=mock_open, read_data=b"Test document content")
    @patch("os.path.isfile", return_value=True)
    def test_convert_document_to_request_files_filepath(self, mock_isfile, mock_file_open):
        """Test convert_document_to_request_files with file path."""
        result = convert_document_to_request_files(
            "test.txt", "test.txt", "text/plain"
        )

        mock_isfile.assert_called_once_with("test.txt")
        mock_file_open.assert_called_once_with("test.txt", "rb")

        self.assertIn("document", result)
        self.assertIn("documentName", result)
        self.assertEqual(result["document"][0], "test.txt")
        self.assertEqual(result["document"][1], b"Test document content")
        self.assertEqual(result["document"][2], "text/plain")
        self.assertEqual(result["documentName"], (None, "test.txt"))

    def test_convert_document_to_request_files_invalid_type(self):
        """Test convert_document_to_request_files with invalid type."""
        with self.assertRaises(ValueError):
            convert_document_to_request_files(
                123, "test.txt", "text/plain"
            )

    def test_prepare_headers(self):
        """Test prepare_headers."""
        # Basic test
        headers = prepare_headers("test-api-key")
        self.assertEqual(headers["Content-Type"], "application/json")
        self.assertEqual(headers["Authorization"], "Bearer test-api-key")

        # With additional headers
        headers = prepare_headers("test-api-key", {"X-Custom": "Value"})
        self.assertEqual(headers["Content-Type"], "application/json")
        self.assertEqual(headers["Authorization"], "Bearer test-api-key")
        self.assertEqual(headers["X-Custom"], "Value")

    def test_format_thread_id(self):
        """Test format_thread_id."""
        # Already formatted
        self.assertEqual(format_thread_id("thread_123"), "thread_123")

        # Not formatted
        self.assertEqual(format_thread_id("123"), "thread_123")

        # With whitespace
        self.assertEqual(format_thread_id(" 123 "), "thread_123")

    def test_clean_null_values(self):
        """Test clean_null_values."""
        data = {
            "name": "test",
            "description": None,
            "value": 123,
            "options": None
        }

        result = clean_null_values(data)

        self.assertIn("name", result)
        self.assertIn("value", result)
        self.assertNotIn("description", result)
        self.assertNotIn("options", result)
        self.assertEqual(result["name"], "test")
        self.assertEqual(result["value"], 123)


if __name__ == "__main__":
    unittest.main()
