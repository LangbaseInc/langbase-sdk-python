"""
Tests for the Tools.
"""

import json

import responses

from langbase.constants import BASE_URL, TOOLS_CRAWL_ENDPOINT, TOOLS_WEB_SEARCH_ENDPOINT
from tests.constants import AUTH_AND_JSON_CONTENT_HEADER
from tests.validation_utils import validate_response_headers


class TestTools:
    """Test the Tools API."""

    @responses.activate
    def test_tools_web_search_basic(self, langbase_client, mock_responses):
        """Test tools.web_search method with basic parameters."""
        responses.add(
            responses.POST,
            f"{BASE_URL}{TOOLS_WEB_SEARCH_ENDPOINT}",
            json=mock_responses["tools_web_search"],
            status=200,
        )

        request_body = {"query": "test search", "api_key": "search_api_key"}

        result = langbase_client.tools.web_search(**request_body)

        assert result == mock_responses["tools_web_search"]
        assert len(responses.calls) == 1
        request = responses.calls[0].request
        validate_response_headers(
            request.headers,
            {
                **AUTH_AND_JSON_CONTENT_HEADER,
                "LB-WEB-SEARCH-KEY": request_body["api_key"],
            },
        )
        assert json.loads(request.body) == {"query": "test search", "service": "exa"}

    @responses.activate
    def test_tools_crawl_basic(self, langbase_client, mock_responses):
        """Test tools.crawl method with basic parameters."""
        request_body = {"url": ["https://example.com"], "api_key": "crawl_api_key"}

        responses.add(
            responses.POST,
            f"{BASE_URL}{TOOLS_CRAWL_ENDPOINT}",
            json=mock_responses["tools_crawl"],
            status=200,
        )

        result = langbase_client.tools.crawl(**request_body)

        assert result == mock_responses["tools_crawl"]
        assert len(responses.calls) == 1
        request = responses.calls[0].request
        validate_response_headers(
            request.headers,
            {**AUTH_AND_JSON_CONTENT_HEADER, "LB-CRAWL-KEY": request_body["api_key"]},
        )
        assert json.loads(request.body) == {"url": ["https://example.com"]}

    @responses.activate
    def test_tools_crawl_multiple_urls(self, langbase_client, mock_responses):
        """Test tools.crawl method with multiple URLs."""
        request_body = {
            "url": ["https://example.com", "https://test.com", "https://demo.org"],
            "api_key": "crawl_api_key",
            "max_pages": 1,
        }

        responses.add(
            responses.POST,
            f"{BASE_URL}{TOOLS_CRAWL_ENDPOINT}",
            json=mock_responses["tools_crawl"],
            status=200,
        )

        result = langbase_client.tools.crawl(**request_body)

        assert result == mock_responses["tools_crawl"]
        assert len(responses.calls) == 1
        request = responses.calls[0].request
        validate_response_headers(
            request.headers,
            {**AUTH_AND_JSON_CONTENT_HEADER, "LB-CRAWL-KEY": request_body["api_key"]},
        )
        assert json.loads(request.body) == {
            "url": request_body["url"],
            "maxPages": request_body["max_pages"],
        }
