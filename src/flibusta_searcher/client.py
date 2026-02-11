"""Flibusta client - uses OPDS infrastructure."""

from .infrastructure.config import FlibustaConfig
from .infrastructure.opds.client import OpdsClient
from .infrastructure.opds.parser import OpdsParser


class FlibustaClient:
    """Client for searching Flibusta catalog. Wraps OpdsClient with config."""

    def __init__(self, base_url: str | None = None) -> None:
        """Initialize the Flibusta client."""
        self._config = FlibustaConfig()
        if base_url:
            self._config = self._config.model_copy(
                update={
                    "base_url": base_url,
                    "opds_url": f"{base_url.rstrip('/')}/opds",
                },
            )
        parser = OpdsParser(base_url=self._config.base_url)
        self._client = OpdsClient(config=self._config, parser=parser)

    def search_books(self, query: str, limit: int | None = None) -> list:
        """Search for books using the OPDS catalog."""
        return self._client.search_books(query, limit)

    def search_authors(self, query: str, limit: int = 20) -> list:
        """Search for authors using the OPDS catalog."""
        return self._client.search_authors(query, limit)

    def get_author_books(self, author_id: str, limit: int | None = None) -> list:
        """Get all books by a specific author."""
        return self._client.get_author_books(author_id, limit)
