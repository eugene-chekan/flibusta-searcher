"""File downloader for book content."""

from pathlib import Path

import httpx

from flibusta_searcher.application.dto import DownloadResult
from flibusta_searcher.domain.entities import Book
from flibusta_searcher.domain.exceptions import DownloadError
from flibusta_searcher.domain.value_objects import sanitize_filename
from flibusta_searcher.infrastructure.config import FlibustaConfig


class FileDownloader:
    """Downloads book files from URLs."""

    def __init__(self, config: FlibustaConfig) -> None:
        """Initialize the file downloader."""
        self.config = config

    def download_book(
        self,
        book: Book,
        format_num: int,
        download_dir: Path | None = None,
        *,
        overwrite: bool = False,
    ) -> DownloadResult:
        """Download a book in the specified format (1-based index)."""
        if not book.download_links:
            return DownloadResult(success=False, error="No download links available")

        formats_list = list(book.download_links.items())
        if not (1 <= format_num <= len(formats_list)):
            return DownloadResult(
                success=False,
                error=f"Invalid format number. Choose between 1 and {len(formats_list)}",
            )

        fmt, url = formats_list[format_num - 1]

        download_dir = download_dir or self.config.download_dir
        download_dir.mkdir(parents=True, exist_ok=True)

        safe_title = sanitize_filename(book.title, self.config.max_filename_length)
        author_names = "_".join(
            sanitize_filename(a.name, self.config.max_filename_length)
            for a in book.authors[:2]
        )
        filename = f"{author_names} - {safe_title}.{fmt}" if author_names else f"{safe_title}.{fmt}"
        filepath = download_dir / filename

        if filepath.exists() and not overwrite:
            return DownloadResult(success=False, error="File exists", filepath=filepath)

        try:
            with httpx.Client(
                follow_redirects=True,
                timeout=self.config.download_timeout,
            ) as client:
                response = client.get(url)
                response.raise_for_status()

            with filepath.open("wb") as f:
                f.write(response.content)

            file_size = filepath.stat().st_size
            return DownloadResult(
                success=True,
                filepath=filepath,
                file_size_bytes=file_size,
            )
        except httpx.HTTPError as e:
            msg = f"HTTP error downloading file: {e}"
            raise DownloadError(msg) from e
        except OSError as e:
            msg = f"Error saving file: {e}"
            raise DownloadError(msg) from e
