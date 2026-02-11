"""Search books use case."""

from flibusta_searcher.application.ports import SearchPort
from flibusta_searcher.domain.entities import Book


class SearchBooksUseCase:
    """Orchestrates book search."""

    def __init__(self, search_port: SearchPort) -> None:
        """Initialize the search books use case."""
        self._search = search_port

    def execute(self, query: str, limit: int | None = None) -> list[Book]:
        """Search for books by query."""
        return self._search.search_books(query, limit)
