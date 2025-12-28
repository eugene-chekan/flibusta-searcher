from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class Author:
    """
    Represents an author found in the Flibusta catalog.
    """

    name: str
    id: str  # e.g., "12345"
    link: str  # Full URL or relative path
    number_of_books: int


@dataclass
class Book:
    """
    Represents a book found in the Flibusta catalog.
    """

    title: str
    authors: List[Author]
    book_id: str
    download_links: Dict[str, str] = field(
        default_factory=dict
    )  # Format (e.g., 'fb2') -> URL
    genres: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    size: Optional[str] = None
    cover_image: Optional[str] = None
    summary: Optional[str] = None
    published: Optional[str] = None
    language: Optional[str] = None
    web_link: Optional[str] = None
