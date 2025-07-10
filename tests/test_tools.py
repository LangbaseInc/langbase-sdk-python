"""
Tests for the Tools API.
"""

import json

import responses


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
        request_json = json.loads(request.body)
        assert request_json["query"] == "test search"
        assert request_json["service"] == "exa"  # default service

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
        request_json = json.loads(request.body)
        assert request_json["service"] == "google"

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
        request_json = json.loads(request.body)
        assert request_json["query"] == "comprehensive search"
        assert request_json["service"] == "bing"
        assert request_json["totalResults"] == 10
        assert request_json["domains"] == ["example.com", "test.org"]

        # Verify API key header
        assert request.headers["LB-WEB-SEARCH-KEY"] == "search-api-key"

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
        assert request.headers["LB-WEB-SEARCH-KEY"] == "custom-search-key"

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
        request_json = json.loads(request.body)
        assert request_json["url"] == ["https://example.com"]

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
        request_json = json.loads(request.body)
        assert request_json["url"] == urls

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
        request_json = json.loads(request.body)
        assert request_json["maxPages"] == 5

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
        assert request.headers["LB-CRAWL-KEY"] == "crawl-api-key"

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
        request_json = json.loads(request.body)
        assert request_json["url"] == ["https://example.com", "https://test.com"]
        assert request_json["maxPages"] == 10
        assert request.headers["LB-CRAWL-KEY"] == "comprehensive-crawl-key"

    @responses.activate
    def test_tools_headers_authentication(self, langbase_client, mock_responses):
        """Test that tools methods include correct authentication headers."""
        responses.add(
            responses.POST,
            "https://api.langbase.com/v1/tools/web-search",
            json=mock_responses["tools_web_search"],
            status=200,
        )

        langbase_client.tools.web_search(query="auth test")

        request = responses.calls[0].request
        assert request.headers["Authorization"] == "Bearer test-api-key"
        assert request.headers["Content-Type"] == "application/json"

    @responses.activate
    def test_tools_request_format(self, langbase_client, mock_responses):
        """Test that tools requests are properly formatted."""
        responses.add(
            responses.POST,
            "https://api.langbase.com/v1/tools/crawl",
            json=mock_responses["tools_crawl"],
            status=200,
        )

        langbase_client.tools.crawl(url=["https://example.com"], max_pages=3)

        request = responses.calls[0].request
        assert request.url == "https://api.langbase.com/v1/tools/crawl"

        # Verify JSON body format
        request_json = json.loads(request.body)
        assert isinstance(request_json["url"], list)
        assert isinstance(request_json["maxPages"], int)
