"""Search authors use case."""

from src.flibusta_searcher.application.ports import SearchPort
from src.flibusta_searcher.domain.entities import Author


class SearchAuthorsUseCase:
    """Orchestrates author search."""

    def __init__(self, search_port: SearchPort) -> None:
        """Initialize the search authors use case."""
        self._search = search_port

    def execute(self, query: str, limit: int = 20) -> list[Author]:
        """Search for authors by query."""
        return self._search.search_authors(query, limit)
