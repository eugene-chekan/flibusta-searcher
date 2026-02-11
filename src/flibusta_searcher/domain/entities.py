"""Domain entities."""

from dataclasses import dataclass, field


@dataclass
class Author:
    """Represents an author found in the Flibusta catalog."""

    name: str
    id: str
    link: str
    number_of_books: int

    def __post_init__(self) -> None:
        """Validate author data."""
        if self.number_of_books < 0:
            msg = "number_of_books must be non-negative"
            raise ValueError(msg)


@dataclass
class Book:
    """Represents a book found in the Flibusta catalog."""

    title: str
    authors: list[Author]
    book_id: str
    download_links: dict[str, str] = field(default_factory=dict)
    tags: list[str] = field(default_factory=list)
    size: str | None = None
    cover_image: str | None = None
    summary: str | None = None
    published: str | None = None
    language: str | None = None
    web_link: str | None = None

    def __post_init__(self) -> None:
        """Validate book data."""
        if not isinstance(self.authors, list):
            msg = "authors must be a list"
            raise TypeError(msg)

    def get_primary_author(self) -> Author | None:
        """Return the first/primary author, or None if no authors."""
        return self.authors[0] if self.authors else None

    def get_author_names(self) -> list[str]:
        """Return list of author names."""
        return [a.name for a in self.authors]
