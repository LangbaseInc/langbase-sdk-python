"""
Utility functions for the Langbase SDK.

This module contains helper functions for common tasks like
document handling and data conversion.
"""
import os
from typing import Union, Dict, Any, BinaryIO
from io import BytesIO
from .types import ContentType, FileProtocol


def convert_document_to_request_files(
    document: Union[bytes, BytesIO, str, BinaryIO],
    document_name: str,
    content_type: ContentType
) -> Dict[str, Union[tuple, str]]:
    """
    Convert a document to the format needed for requests library's files parameter.

    Args:
        document: The document content as bytes, file-like object, or file path
        document_name: The name of the document
        content_type: The MIME type of the document

    Returns:
        Dictionary for use with requests.post(files=...)

    Raises:
        ValueError: If the document type is not supported
        FileNotFoundError: If the document path doesn't exist
    """
    files = {}

    if isinstance(document, str) and os.path.isfile(document):
        # If it's a file path, open and read the file
        with open(document, "rb") as f:
            files['document'] = (document_name, f.read(), content_type)
    elif isinstance(document, bytes):
        # If it's raw bytes
        files['document'] = (document_name, document, content_type)
    elif isinstance(document, BytesIO) or hasattr(document, 'read'):
        # If it's a file-like object
        document_content = document.read()
        # Reset the pointer if it's a file-like object that supports seek
        if hasattr(document, 'seek'):
            document.seek(0)
        files['document'] = (document_name, document_content, content_type)
    else:
        raise ValueError(f"Unsupported document type: {type(document)}")

    files['documentName'] = (None, document_name)
    return files


def prepare_headers(api_key: str, additional_headers: Dict[str, str] = None) -> Dict[str, str]:
    """
    Prepare headers for API requests.

    Args:
        api_key: The API key for authentication
        additional_headers: Additional headers to include

    Returns:
        Dictionary of headers to use in requests
    """
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    if additional_headers:
        headers.update(additional_headers)

    return headers


def format_thread_id(thread_id: str) -> str:
    """
    Format thread ID to ensure it's in the correct format.

    Args:
        thread_id: The thread ID to format

    Returns:
        Formatted thread ID
    """
    # Remove any whitespace and special characters
    thread_id = thread_id.strip()

    # Ensure thread_id has the correct format
    if not thread_id.startswith('thread_'):
        thread_id = f"thread_{thread_id}"

    return thread_id


def clean_null_values(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Remove keys with None values from a dictionary.

    Args:
        data: Dictionary to clean

    Returns:
        Cleaned dictionary with no None values
    """
    return {k: v for k, v in data.items() if v is not None}
