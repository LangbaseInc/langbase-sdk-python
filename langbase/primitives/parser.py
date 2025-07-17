"""
Parser API client for the Langbase SDK.
"""

from io import BytesIO
from typing import BinaryIO, Union

import requests

from langbase.constants import PARSER_ENDPOINT
from langbase.request import Request
from langbase.types import ContentType, ParseResponse
from langbase.utils import convert_document_to_request_files


class Parser:
    """
    Client for document parsing operations.

    This class provides methods for parsing documents to extract their content.
    """

    def __init__(self, parent):
        """
        Initialize the Parser client.

        Args:
            parent: The parent Langbase instance
        """
        self.parent = parent
        self.request: Request = parent.request

    def parser(
        self,
        document: Union[bytes, BytesIO, str, BinaryIO],
        document_name: str,
        content_type: ContentType,
    ) -> ParseResponse:
        """
        Parse a document to extract its content.

        Args:
            document: Document content (bytes, file-like object, or path)
            document_name: Name for the document
            content_type: MIME type of the document

        Returns:
            Dictionary with document name and extracted content
        """
        files = convert_document_to_request_files(document, document_name, content_type)

        response = requests.post(
            f"{self.parent.base_url}{PARSER_ENDPOINT}",
            headers={"Authorization": f"Bearer {self.parent.api_key}"},
            files=files,
        )

        if not response.ok:
            self.request.handle_error_response(response)

        return response.json()
