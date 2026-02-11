"""Application ports (interfaces) for dependency inversion."""

from pathlib import Path
from typing import Protocol

from src.flibusta_searcher.application.dto import DownloadResult
from src.flibusta_searcher.domain.entities import Author, Book


class SearchPort(Protocol):
    """Port for catalog search operations."""

    def search_books(self, query: str, limit: int | None = None) -> list[Book]: ...  # noqa: D102
    def search_authors(self, query: str, limit: int = 20) -> list[Author]: ...  # noqa: D102
    def get_author_books(self, author_id: str, limit: int | None = None) -> list[Book]: ...  # noqa: D102


class DownloadPort(Protocol):
    """Port for file download operations."""

    def download_book(  # noqa: D102
        self,
        book: Book,
        format_num: int,
        download_dir: Path | None = None,
        *,
        overwrite: bool = False,
    ) -> DownloadResult: ...
