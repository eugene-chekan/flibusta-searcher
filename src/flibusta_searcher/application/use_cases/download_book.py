"""Download book use case."""

from pathlib import Path

from src.flibusta_searcher.application.dto import DownloadResult
from src.flibusta_searcher.application.ports import DownloadPort
from src.flibusta_searcher.domain.entities import Book


class DownloadBookUseCase:
    """Orchestrates book download with validation."""

    def __init__(self, download_port: DownloadPort) -> None:
        """Initialize the download book use case."""
        self._download = download_port

    def execute(
        self,
        book: Book,
        format_num: int,
        download_dir: Path | None = None,
        *,
        overwrite: bool = False,
    ) -> DownloadResult:
        """Download a book in the specified format (1-based index)."""
        return self._download.download_book(
            book=book,
            format_num=format_num,
            download_dir=download_dir,
            overwrite=overwrite,
        )
