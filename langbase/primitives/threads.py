"""
Threads API client for the Langbase SDK.
"""

from typing import Any, Dict, List, Optional

from langbase.constants import (
    THREAD_DETAIL_ENDPOINT,
    THREAD_MESSAGES_ENDPOINT,
    THREADS_ENDPOINT,
)
from langbase.request import Request
from langbase.types import ThreadMessagesBaseResponse, ThreadsBaseResponse
from langbase.utils import clean_null_values


class Messages:
    def __init__(self, parent):
        self.parent = parent
        self.request: Request = parent.request

    def list(self, thread_id: str) -> List[ThreadMessagesBaseResponse]:
        """
        List all messages in a thread.

        Args:
            thread_id: ID of the thread

        Returns:
            List of messages
        """
        return self.request.get(THREAD_MESSAGES_ENDPOINT.format(thread_id=thread_id))


class Threads:
    def __init__(self, parent):
        self.parent = parent
        self.request: Request = parent.request
        self.messages = Messages(self)

    def create(
        self,
        thread_id: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None,
        messages: Optional[List[Dict[str, Any]]] = None,
    ) -> ThreadsBaseResponse:
        """
        Create a new thread.

        Args:
            thread_id: Optional specific ID for the thread
            metadata: Metadata for the thread
            messages: Initial messages for the thread

        Returns:
            Created thread object
        """
        options = {}

        if thread_id:
            options["threadId"] = thread_id

        if metadata:
            options["metadata"] = metadata

        if messages:
            options["messages"] = messages

        return self.request.post(THREADS_ENDPOINT, clean_null_values(options))

    def update(self, thread_id: str, metadata: Dict[str, str]) -> ThreadsBaseResponse:
        """
        Update thread metadata.

        Args:
            thread_id: ID of the thread to update
            metadata: New metadata

        Returns:
            Updated thread object
        """
        options = {"metadata": metadata}
        return self.request.post(
            THREAD_DETAIL_ENDPOINT.format(thread_id=thread_id), options
        )

    def get(self, thread_id: str) -> ThreadsBaseResponse:
        """
        Get thread details.

        Args:
            thread_id: ID of the thread

        Returns:
            Thread object
        """
        return self.request.get(THREAD_DETAIL_ENDPOINT.format(thread_id=thread_id))

    def delete(self, thread_id: str) -> Dict[str, bool]:
        """
        Delete a thread.

        Args:
            thread_id: ID of the thread to delete

        Returns:
            Delete response
        """
        return self.request.delete(THREAD_DETAIL_ENDPOINT.format(thread_id=thread_id))

    def append(
        self, thread_id: str, messages: List[Dict[str, Any]]
    ) -> List[ThreadMessagesBaseResponse]:
        """
        Append messages to a thread.

        Args:
            thread_id: ID of the thread
            messages: Messages to append

        Returns:
            List of added messages
        """
        options = {"messages": messages}

        return self.request.post(
            THREAD_MESSAGES_ENDPOINT.format(thread_id=thread_id), options
        )
