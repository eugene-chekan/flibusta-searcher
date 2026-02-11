"""OPDS HTTP client for Flibusta catalog."""

import logging
from typing import Any

import httpx

from flibusta_searcher.domain.entities import Author, Book
from flibusta_searcher.infrastructure.config import FlibustaConfig
from flibusta_searcher.infrastructure.opds.parser import OpdsParser
from flibusta_searcher.infrastructure.pagination import fetch_paginated

logger = logging.getLogger(__name__)


class OpdsClient:
    """HTTP client for OPDS catalog operations."""

    def __init__(self, config: FlibustaConfig, parser: OpdsParser | None = None) -> None:
        """Initialize the OPDS client."""
        self.config = config
        self.parser = parser or OpdsParser(base_url=config.base_url)

    def search_books(self, query: str, limit: int | None = None) -> list[Book]:
        """Search for books using the OPDS catalog."""
        limit = limit if limit is not None else self.config.max_pagination_limit
        url = f"{self.config.opds_url}/search"
        params = {"searchType": "books", "searchTerm": query}
        return self._fetch_paginated_books(url, params, limit)

    def search_authors(self, query: str, limit: int = 20) -> list[Author]:
        """Search for authors using the OPDS catalog."""
        url = f"{self.config.opds_url}/search"
        params = {"searchType": "authors", "searchTerm": query}
        return self._fetch_paginated_authors(url, params, limit)

    def get_author_books(self, author_id: str, limit: int | None = None) -> list[Book]:
        """Get all books by a specific author."""
        limit = limit if limit is not None else self.config.max_pagination_limit
        url = f"{self.config.opds_url}/author/{author_id}/alphabet"
        return self._fetch_paginated_books(url, {}, limit)

    def _fetch_paginated_books(self, url: str, params: dict[str, Any], limit: int) -> list[Book]:
        """Fetch books with pagination."""
        return fetch_paginated(
            url=url,
            params=params,
            limit=limit,
            base_url=self.config.base_url,
            get_response=self._get_response,
            parse_fn=lambda c: self.parser.parse_books(c),
        )

    def _fetch_paginated_authors(self, url: str, params: dict[str, Any], limit: int) -> list[Author]:
        """Fetch authors with pagination."""
        return fetch_paginated(
            url=url,
            params=params,
            limit=limit,
            base_url=self.config.base_url,
            get_response=self._get_response,
            parse_fn=lambda c: self.parser.parse_authors(c),
        )

    def _get_response(self, url: str, params: dict[str, Any]) -> bytes:
        """Make HTTP GET request and return response content."""
        with httpx.Client(
            follow_redirects=True,
            timeout=self.config.default_timeout,
        ) as client:
            response = client.get(url, params=params)
            response.raise_for_status()
            return response.content
