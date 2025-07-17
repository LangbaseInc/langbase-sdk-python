"""
Tools API client for the Langbase SDK.
"""

from typing import List, Optional

from langbase.constants import TOOLS_CRAWL_ENDPOINT, TOOLS_WEB_SEARCH_ENDPOINT
from langbase.request import Request


class Tools:
    def __init__(self, parent):
        self.parent = parent
        self.request: Request = parent.request

    def crawl(
        self,
        url: List[str],
        max_pages: Optional[int] = None,
        api_key: Optional[str] = None,
    ):
        """
        Crawl web pages.

        Args:
            url: List of URLs to crawl
            max_pages: Maximum number of pages to crawl
            api_key: API key for crawling service

        Returns:
            List of crawled content
        """
        options = {"url": url}

        if max_pages is not None:
            options["maxPages"] = max_pages

        headers = {}
        if api_key:
            headers["LB-CRAWL-KEY"] = api_key

        return self.request.post(TOOLS_CRAWL_ENDPOINT, options, headers)

    def web_search(
        self,
        query: str,
        service: str = "exa",
        total_results: Optional[int] = None,
        domains: Optional[List[str]] = None,
        api_key: Optional[str] = None,
    ):
        """
        Search the web.

        Args:
            query: Search query
            service: Search service to use
            total_results: Number of results to return
            domains: List of domains to restrict search to
            api_key: API key for search service

        Returns:
            List of search results
        """
        options = {"query": query, "service": service}

        if total_results is not None:
            options["totalResults"] = total_results

        if domains is not None:
            options["domains"] = domains

        headers = {}
        if api_key:
            headers["LB-WEB-SEARCH-KEY"] = api_key

        return self.request.post(TOOLS_WEB_SEARCH_ENDPOINT, options, headers)
