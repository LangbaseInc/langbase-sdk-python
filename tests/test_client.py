"""
Tests for the Langbase client.
"""
import os
import unittest
from unittest.mock import patch, MagicMock

from langbase import Langbase, APIError, NotFoundError


class TestLangbase(unittest.TestCase):
    """Test the Langbase client."""

    def setUp(self):
        """Set up test fixtures."""
        # Create a mock API key for testing
        self.api_key = "test-api-key"
        self.lb = Langbase(api_key=self.api_key)

    def test_initialization_with_api_key(self):
        """Test initialization with API key parameter."""
        self.assertEqual(self.lb.api_key, self.api_key)
        self.assertEqual(self.lb.base_url, "https://api.langbase.com")
        self.assertEqual(self.lb.timeout, 30)

    @patch.dict(os.environ, {"LANGBASE_API_KEY": "env-api-key"}, clear=True)
    def test_initialization_with_env_var(self):
        """Test initialization with environment variable."""
        lb = Langbase()
        self.assertEqual(lb.api_key, "env-api-key")

    def test_initialization_with_no_api_key(self):
        """Test initialization with no API key."""
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(ValueError):
                Langbase()

    @patch("langbase.request.Request.get")
    def test_pipes_list(self, mock_get):
        """Test pipes.list method."""
        mock_get.return_value = [{"name": "test-pipe"}]
        result = self.lb.pipes.list()
        mock_get.assert_called_once_with("/v1/pipes")
        self.assertEqual(result, [{"name": "test-pipe"}])

    @patch("langbase.request.Request.post")
    def test_pipes_create(self, mock_post):
        """Test pipes.create method."""
        mock_post.return_value = {"name": "new-pipe", "api_key": "pipe-api-key"}
        result = self.lb.pipes.create(
            name="new-pipe",
            description="A test pipe",
            model="anthropic:claude-3-sonnet"
        )
        mock_post.assert_called_once()
        self.assertEqual(result, {"name": "new-pipe", "api_key": "pipe-api-key"})

    @patch("langbase.request.Request.post")
    def test_pipes_update(self, mock_post):
        """Test pipes.update method."""
        mock_post.return_value = {"name": "updated-pipe"}
        result = self.lb.pipes.update(
            name="test-pipe",
            temperature=0.7
        )
        mock_post.assert_called_once()
        self.assertEqual(result, {"name": "updated-pipe"})

    @patch("langbase.request.Request.post")
    def test_pipes_run(self, mock_post):
        """Test pipes.run method."""
        mock_post.return_value = {"completion": "Hello, world!"}
        result = self.lb.pipes.run(
            name="test-pipe",
            messages=[{"role": "user", "content": "Hi"}]
        )
        mock_post.assert_called_once()
        self.assertEqual(result, {"completion": "Hello, world!"})

    @patch("langbase.request.Request.post")
    def test_pipes_run_with_no_name_or_api_key(self, mock_post):
        """Test pipes.run method with no name or API key."""
        with self.assertRaises(ValueError):
            self.lb.pipes.run(messages=[{"role": "user", "content": "Hi"}])

    @patch("langbase.request.Request.post")
    def test_memories_create(self, mock_post):
        """Test memories.create method."""
        mock_post.return_value = {"name": "test-memory"}
        result = self.lb.memories.create(
            name="test-memory",
            description="A test memory"
        )
        mock_post.assert_called_once()
        self.assertEqual(result, {"name": "test-memory"})

    @patch("langbase.request.Request.get")
    def test_memories_list(self, mock_get):
        """Test memories.list method."""
        mock_get.return_value = [{"name": "test-memory"}]
        result = self.lb.memories.list()
        mock_get.assert_called_once_with("/v1/memory")
        self.assertEqual(result, [{"name": "test-memory"}])

    @patch("langbase.request.Request.delete")
    def test_memories_delete(self, mock_delete):
        """Test memories.delete method."""
        mock_delete.return_value = {"success": True}
        result = self.lb.memories.delete(name="test-memory")
        mock_delete.assert_called_once_with("/v1/memory/test-memory")
        self.assertEqual(result, {"success": True})

    @patch("langbase.request.Request.post")
    def test_memories_retrieve(self, mock_post):
        """Test memories.retrieve method."""
        mock_post.return_value = [{"text": "Test text", "similarity": 0.9}]
        result = self.lb.memories.retrieve(
            query="test query",
            memory=[{"name": "test-memory"}]
        )
        mock_post.assert_called_once()
        self.assertEqual(result, [{"text": "Test text", "similarity": 0.9}])

    @patch("langbase.request.Request.get")
    def test_memories_documents_list(self, mock_get):
        """Test memories.documents.list method."""
        mock_get.return_value = [{"name": "test-doc"}]
        result = self.lb.memories.documents.list(memory_name="test-memory")
        mock_get.assert_called_once_with("/v1/memory/test-memory/documents")
        self.assertEqual(result, [{"name": "test-doc"}])

    @patch("langbase.request.Request.delete")
    def test_memories_documents_delete(self, mock_delete):
        """Test memories.documents.delete method."""
        mock_delete.return_value = {"success": True}
        result = self.lb.memories.documents.delete(
            memory_name="test-memory",
            document_name="test-doc"
        )
        mock_delete.assert_called_once_with("/v1/memory/test-memory/documents/test-doc")
        self.assertEqual(result, {"success": True})

    @patch("langbase.request.Request.post")
    @patch("requests.put")
    def test_memories_documents_upload(self, mock_put, mock_post):
        """Test memories.documents.upload method."""
        mock_post.return_value = {"signedUrl": "https://upload-url.com"}
        mock_put.return_value = MagicMock(ok=True)

        document = b"test document content"
        result = self.lb.memories.documents.upload(
            memory_name="test-memory",
            document_name="test-doc.txt",
            document=document,
            content_type="text/plain"
        )

        mock_post.assert_called_once()
        mock_put.assert_called_once()
        self.assertTrue(result.ok)

    @patch("langbase.request.Request.get")
    def test_memories_documents_embeddings_retry(self, mock_get):
        """Test memories.documents.embeddings.retry method."""
        mock_get.return_value = {"success": True}
        result = self.lb.memories.documents.embeddings.retry(
            memory_name="test-memory",
            document_name="test-doc"
        )
        mock_get.assert_called_once_with(
            "/v1/memory/test-memory/documents/test-doc/embeddings/retry"
        )
        self.assertEqual(result, {"success": True})

    @patch("langbase.request.Request.post")
    def test_tools_web_search(self, mock_post):
        """Test tools.web_search method."""
        mock_post.return_value = [{"url": "https://example.com", "content": "Example content"}]
        result = self.lb.tools.web_search(
            query="test query",
            service="exa"
        )
        mock_post.assert_called_once()
        self.assertEqual(result, [{"url": "https://example.com", "content": "Example content"}])

    @patch("langbase.request.Request.post")
    def test_tools_crawl(self, mock_post):
        """Test tools.crawl method."""
        mock_post.return_value = [{"url": "https://example.com", "content": "Example content"}]
        result = self.lb.tools.crawl(
            url=["https://example.com"]
        )
        mock_post.assert_called_once()
        self.assertEqual(result, [{"url": "https://example.com", "content": "Example content"}])

    @patch("langbase.request.Request.post")
    def test_threads_create(self, mock_post):
        """Test threads.create method."""
        mock_post.return_value = {"id": "thread_123", "object": "thread"}
        result = self.lb.threads.create(
            metadata={"user_id": "123"}
        )
        mock_post.assert_called_once()
        self.assertEqual(result, {"id": "thread_123", "object": "thread"})

    @patch("langbase.request.Request.post")
    def test_threads_update(self, mock_post):
        """Test threads.update method."""
        mock_post.return_value = {"id": "thread_123", "object": "thread"}
        result = self.lb.threads.update(
            thread_id="thread_123",
            metadata={"status": "complete"}
        )
        mock_post.assert_called_once()
        self.assertEqual(result, {"id": "thread_123", "object": "thread"})

    @patch("langbase.request.Request.get")
    def test_threads_get(self, mock_get):
        """Test threads.get method."""
        mock_get.return_value = {"id": "thread_123", "object": "thread"}
        result = self.lb.threads.get(thread_id="thread_123")
        mock_get.assert_called_once_with("/v1/threads/thread_123")
        self.assertEqual(result, {"id": "thread_123", "object": "thread"})

    @patch("langbase.request.Request.delete")
    def test_threads_delete(self, mock_delete):
        """Test threads.delete method."""
        mock_delete.return_value = {"success": True}
        result = self.lb.threads.delete(thread_id="thread_123")
        mock_delete.assert_called_once_with("/v1/threads/thread_123")
        self.assertEqual(result, {"success": True})

    @patch("langbase.request.Request.post")
    def test_threads_append(self, mock_post):
        """Test threads.append method."""
        mock_post.return_value = [{"id": "msg_123", "content": "Hello"}]
        result = self.lb.threads.append(
            thread_id="thread_123",
            messages=[{"role": "user", "content": "Hello"}]
        )
        mock_post.assert_called_once()
        self.assertEqual(result, [{"id": "msg_123", "content": "Hello"}])

    @patch("langbase.request.Request.get")
    def test_threads_messages_list(self, mock_get):
        """Test threads.messages.list method."""
        mock_get.return_value = [{"id": "msg_123", "content": "Hello"}]
        result = self.lb.threads.messages.list(thread_id="thread_123")
        mock_get.assert_called_once_with("/v1/threads/thread_123/messages")
        self.assertEqual(result, [{"id": "msg_123", "content": "Hello"}])

    @patch("langbase.request.Request.post")
    def test_llm_run(self, mock_post):
        """Test llm.run method."""
        mock_post.return_value = {"completion": "Hello, world!"}
        result = self.lb.llm.run(
            messages=[{"role": "user", "content": "Hi"}],
            model="anthropic:claude-3-sonnet",
            llm_key="llm-api-key"
        )
        mock_post.assert_called_once()
        self.assertEqual(result, {"completion": "Hello, world!"})

    @patch("langbase.request.Request.post")
    def test_embed(self, mock_post):
        """Test embed method."""
        mock_post.return_value = [[0.1, 0.2, 0.3]]
        result = self.lb.embed(
            chunks=["Test text"]
        )
        mock_post.assert_called_once()
        self.assertEqual(result, [[0.1, 0.2, 0.3]])

    @patch("requests.post")
    def test_chunk(self, mock_post):
        """Test chunk method."""
        mock_response = MagicMock()
        mock_response.ok = True
        mock_response.json.return_value = ["Chunk 1", "Chunk 2"]
        mock_post.return_value = mock_response

        result = self.lb.chunk(
            document=b"Test document",
            document_name="test.txt",
            content_type="text/plain"
        )

        mock_post.assert_called_once()
        self.assertEqual(result, ["Chunk 1", "Chunk 2"])

    @patch("requests.post")
    def test_parse(self, mock_post):
        """Test parse method."""
        mock_response = MagicMock()
        mock_response.ok = True
        mock_response.json.return_value = {
            "documentName": "test.txt",
            "content": "Test content"
        }
        mock_post.return_value = mock_response

        result = self.lb.parse(
            document=b"Test document",
            document_name="test.txt",
            content_type="text/plain"
        )

        mock_post.assert_called_once()
        self.assertEqual(result, {"documentName": "test.txt", "content": "Test content"})

    @patch("langbase.request.Request.get")
    def test_error_handling(self, mock_get):
        """Test error handling."""
        # Simulate a 404 error
        mock_error = APIError(404, {"message": "Not found"}, "Not found", {})
        mock_get.side_effect = NotFoundError(404, {"message": "Not found"}, "Not found", {})

        with self.assertRaises(NotFoundError):
            self.lb.pipes.list()


if __name__ == "__main__":
    unittest.main()
