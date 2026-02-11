"""Dependency injection container."""

from .application.use_cases.download_book import DownloadBookUseCase
from .application.use_cases.get_author_books import GetAuthorBooksUseCase
from .application.use_cases.search_authors import SearchAuthorsUseCase
from .application.use_cases.search_books import SearchBooksUseCase
from .infrastructure.config import FlibustaConfig
from .infrastructure.download.downloader import FileDownloader
from .infrastructure.opds.client import OpdsClient
from .infrastructure.opds.parser import OpdsParser


class Container:
    """DI container holding all application dependencies."""

    def __init__(self) -> None:
        """Initialize the container."""
        self._config = FlibustaConfig()
        self._parser = OpdsParser(base_url=self._config.base_url)
        self._opds_client = OpdsClient(config=self._config, parser=self._parser)
        self._downloader = FileDownloader(config=self._config)

        self._search_books = SearchBooksUseCase(search_port=self._opds_client)
        self._search_authors = SearchAuthorsUseCase(search_port=self._opds_client)
        self._get_author_books = GetAuthorBooksUseCase(search_port=self._opds_client)
        self._download_book = DownloadBookUseCase(download_port=self._downloader)

    @property
    def config(self) -> FlibustaConfig:
        """Get the configuration."""
        return self._config

    @property
    def search_books(self) -> SearchBooksUseCase:
        """Get the search books use case."""
        return self._search_books

    @property
    def search_authors(self) -> SearchAuthorsUseCase:
        """Get the search authors use case."""
        return self._search_authors

    @property
    def get_author_books(self) -> GetAuthorBooksUseCase:
        """Get the get author books use case."""
        return self._get_author_books

    @property
    def download_book(self) -> DownloadBookUseCase:
        """Get the download book use case."""
        return self._download_book
