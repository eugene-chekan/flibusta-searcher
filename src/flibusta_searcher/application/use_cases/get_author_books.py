"""Get author books use case."""

from src.flibusta_searcher.application.ports import SearchPort
from src.flibusta_searcher.domain.entities import Book


class GetAuthorBooksUseCase:
    """Orchestrates fetching books by author ID."""

    def __init__(self, search_port: SearchPort) -> None:
        """Initialize the get author books use case."""
        self._search = search_port

    def execute(self, author_id: str, limit: int | None = None) -> list[Book]:
        """Get all books by author ID."""
        return self._search.get_author_books(author_id, limit)
