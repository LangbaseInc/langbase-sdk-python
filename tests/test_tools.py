"""
Tests for the Tools API.
"""

import json

import responses

from langbase.types import ToolCrawlResponse, ToolWebSearchResponse
from tests.validation_utils import validate_response_body, validate_response_headers


class TestTools:
    """Test the Tools API."""

    @responses.activate
    def test_tools_web_search_basic(self, langbase_client, mock_responses):
        """Test tools.web_search method with basic parameters."""
        responses.add(
            responses.POST,
            "https://api.langbase.com/v1/tools/web-search",
            json=mock_responses["tools_web_search"],
            status=200,
        )

        result = langbase_client.tools.web_search(query="test search")

        assert result == mock_responses["tools_web_search"]
        assert len(responses.calls) == 1

        # Verify request data
        request = responses.calls[0].request
        assert request.method == "POST"
        expected_headers = {
            "Authorization": "Bearer test-api-key",
            "Content-Type": "application/json",
        }
        validate_response_headers(request.headers, expected_headers)
        request_json = json.loads(request.body)
        assert request_json["query"] == "test search"
        assert request_json["service"] == "exa"  # default service
        for item in result:
            validate_response_body(item, ToolWebSearchResponse)

    @responses.activate
    def test_tools_web_search_with_service(self, langbase_client, mock_responses):
        """Test tools.web_search method with custom service."""
        responses.add(
            responses.POST,
            "https://api.langbase.com/v1/tools/web-search",
            json=mock_responses["tools_web_search"],
            status=200,
        )

        result = langbase_client.tools.web_search(query="test search", service="google")

        assert result == mock_responses["tools_web_search"]

        # Verify service parameter
        request = responses.calls[0].request
        expected_headers = {
            "Authorization": "Bearer test-api-key",
            "Content-Type": "application/json",
        }
        validate_response_headers(request.headers, expected_headers)
        request_json = json.loads(request.body)
        assert request_json["service"] == "google"
        for item in result:
            validate_response_body(item, ToolWebSearchResponse)

    @responses.activate
    def test_tools_web_search_with_all_parameters(
        self, langbase_client, mock_responses
    ):
        """Test tools.web_search method with all parameters."""
        responses.add(
            responses.POST,
            "https://api.langbase.com/v1/tools/web-search",
            json=mock_responses["tools_web_search"],
            status=200,
        )

        result = langbase_client.tools.web_search(
            query="comprehensive search",
            service="bing",
            total_results=10,
            domains=["example.com", "test.org"],
            api_key="search-api-key",
        )

        assert result == mock_responses["tools_web_search"]

        # Verify all parameters
        request = responses.calls[0].request
        expected_headers = {
            "Authorization": "Bearer test-api-key",
            "Content-Type": "application/json",
        }
        validate_response_headers(request.headers, expected_headers)
        request_json = json.loads(request.body)
        assert request_json["query"] == "comprehensive search"
        assert request_json["service"] == "bing"
        assert request_json["totalResults"] == 10
        assert request_json["domains"] == ["example.com", "test.org"]

        # Verify API key header
        assert request.headers["LB-WEB-SEARCH-KEY"] == "search-api-key"
        for item in result:
            validate_response_body(item, ToolWebSearchResponse)

    @responses.activate
    def test_tools_web_search_with_api_key(self, langbase_client, mock_responses):
        """Test tools.web_search method with API key header."""
        responses.add(
            responses.POST,
            "https://api.langbase.com/v1/tools/web-search",
            json=mock_responses["tools_web_search"],
            status=200,
        )

        result = langbase_client.tools.web_search(
            query="test search", api_key="custom-search-key"
        )

        assert result == mock_responses["tools_web_search"]

        # Verify API key header
        request = responses.calls[0].request
        expected_headers = {
            "Authorization": "Bearer test-api-key",
            "Content-Type": "application/json",
        }
        validate_response_headers(request.headers, expected_headers)
        assert request.headers["LB-WEB-SEARCH-KEY"] == "custom-search-key"
        for item in result:
            validate_response_body(item, ToolWebSearchResponse)

    @responses.activate
    def test_tools_crawl_basic(self, langbase_client, mock_responses):
        """Test tools.crawl method with basic parameters."""
        responses.add(
            responses.POST,
            "https://api.langbase.com/v1/tools/crawl",
            json=mock_responses["tools_crawl"],
            status=200,
        )

        result = langbase_client.tools.crawl(url=["https://example.com"])

        assert result == mock_responses["tools_crawl"]
        assert len(responses.calls) == 1

        # Verify request data
        request = responses.calls[0].request
        assert request.method == "POST"
        expected_headers = {
            "Authorization": "Bearer test-api-key",
            "Content-Type": "application/json",
        }
        validate_response_headers(request.headers, expected_headers)
        request_json = json.loads(request.body)
        assert request_json["url"] == ["https://example.com"]
        for item in result:
            validate_response_body(item, ToolCrawlResponse)

    @responses.activate
    def test_tools_crawl_multiple_urls(self, langbase_client, mock_responses):
        """Test tools.crawl method with multiple URLs."""
        urls = ["https://example.com", "https://test.com", "https://demo.org"]

        responses.add(
            responses.POST,
            "https://api.langbase.com/v1/tools/crawl",
            json=mock_responses["tools_crawl"],
            status=200,
        )

        result = langbase_client.tools.crawl(url=urls)

        assert result == mock_responses["tools_crawl"]

        # Verify URLs
        request = responses.calls[0].request
        expected_headers = {
            "Authorization": "Bearer test-api-key",
            "Content-Type": "application/json",
        }
        validate_response_headers(request.headers, expected_headers)
        request_json = json.loads(request.body)
        assert request_json["url"] == urls
        for item in result:
            validate_response_body(item, ToolCrawlResponse)

    @responses.activate
    def test_tools_crawl_with_max_pages(self, langbase_client, mock_responses):
        """Test tools.crawl method with max_pages parameter."""
        responses.add(
            responses.POST,
            "https://api.langbase.com/v1/tools/crawl",
            json=mock_responses["tools_crawl"],
            status=200,
        )

        result = langbase_client.tools.crawl(url=["https://example.com"], max_pages=5)

        assert result == mock_responses["tools_crawl"]

        # Verify max_pages parameter
        request = responses.calls[0].request
        expected_headers = {
            "Authorization": "Bearer test-api-key",
            "Content-Type": "application/json",
        }
        validate_response_headers(request.headers, expected_headers)
        request_json = json.loads(request.body)
        assert request_json["maxPages"] == 5
        for item in result:
            validate_response_body(item, ToolCrawlResponse)

    @responses.activate
    def test_tools_crawl_with_api_key(self, langbase_client, mock_responses):
        """Test tools.crawl method with API key header."""
        responses.add(
            responses.POST,
            "https://api.langbase.com/v1/tools/crawl",
            json=mock_responses["tools_crawl"],
            status=200,
        )

        result = langbase_client.tools.crawl(
            url=["https://example.com"], api_key="crawl-api-key"
        )

        assert result == mock_responses["tools_crawl"]

        # Verify API key header
        request = responses.calls[0].request
        expected_headers = {
            "Authorization": "Bearer test-api-key",
            "Content-Type": "application/json",
        }
        validate_response_headers(request.headers, expected_headers)
        assert request.headers["LB-CRAWL-KEY"] == "crawl-api-key"
        for item in result:
            validate_response_body(item, ToolCrawlResponse)

    @responses.activate
    def test_tools_crawl_with_all_parameters(self, langbase_client, mock_responses):
        """Test tools.crawl method with all parameters."""
        responses.add(
            responses.POST,
            "https://api.langbase.com/v1/tools/crawl",
            json=mock_responses["tools_crawl"],
            status=200,
        )

        result = langbase_client.tools.crawl(
            url=["https://example.com", "https://test.com"],
            max_pages=10,
            api_key="comprehensive-crawl-key",
        )

        assert result == mock_responses["tools_crawl"]

        # Verify all parameters
        request = responses.calls[0].request
        expected_headers = {
            "Authorization": "Bearer test-api-key",
            "Content-Type": "application/json",
        }
        validate_response_headers(request.headers, expected_headers)
        request_json = json.loads(request.body)
        assert request_json["url"] == ["https://example.com", "https://test.com"]
        assert request_json["maxPages"] == 10
        assert request.headers["LB-CRAWL-KEY"] == "comprehensive-crawl-key"
        for item in result:
            validate_response_body(item, ToolCrawlResponse)
