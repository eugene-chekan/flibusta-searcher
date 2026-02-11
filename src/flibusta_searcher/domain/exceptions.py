"""Domain exceptions."""


class FlibustaError(Exception):
    """Base exception for Flibusta domain errors."""


class BookNotFoundError(FlibustaError):
    """Raised when a book is not found."""


class AuthorNotFoundError(FlibustaError):
    """Raised when an author is not found."""


class DownloadError(FlibustaError):
    """Raised when a download fails."""


class ParseError(FlibustaError):
    """Raised when parsing OPDS/XML content fails."""
