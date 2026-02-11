"""OPDS feed parsing logic."""

import re
from html import unescape
from urllib.parse import urljoin

from feedparser import parse

from src.flibusta_searcher.domain.entities import Author, Book
from src.flibusta_searcher.domain.exceptions import ParseError
from src.flibusta_searcher.infrastructure.pagination import extract_next_link


def _strip_html(text: str) -> str:
    """Strip HTML tags and decode entities for plain-text display."""
    if not text:
        return ""
    # Replace <br>, <br/>, <br /> and block closing tags with newlines
    text = re.sub(r"<br\s*/?>", "\n", text, flags=re.IGNORECASE)
    text = re.sub(r"</(p|div|li|tr)[^>]*>", "\n", text, flags=re.IGNORECASE)
    # Remove all remaining HTML tags
    text = re.sub(r"<[^>]+>", " ", text)
    # Collapse multiple spaces to one
    text = re.sub(r"[ \t]+", " ", text)
    # Collapse multiple newlines to one
    text = re.sub(r"\n+", "\n", text)
    return unescape(text).strip()


class OpdsParser:
    """Parses OPDS XML feed content into domain entities."""

    def __init__(self, base_url: str) -> None:
        """Initialize the OPDS parser."""
        self.base_url = base_url

    def parse_books(self, xml_content: bytes) -> tuple[list[Book], str | None]:
        """Parse OPDS feed into list of books and optional next page URL."""
        try:
            feed = parse(xml_content)
        except (ValueError, KeyError, AttributeError, TypeError, OSError) as e:
            msg = f"Failed to parse OPDS feed: {e}"
            raise ParseError(msg) from e

        next_url = extract_next_link(feed, self.base_url)
        books: list[Book] = []

        for entry in feed.get("entries") or []:
            try:
                book = self._parse_book_entry(entry)
                if book:
                    books.append(book)
            except (ValueError, KeyError) as e:
                msg = f"Failed to parse book entry: {e}"
                raise ParseError(msg) from e

        return books, next_url

    def _parse_book_entry(self, entry: dict) -> Book | None:
        """Parse a single OPDS entry into a Book."""
        authors_entry = entry.get("authors") or []
        authors: list[Author] = []
        for author in authors_entry:
            author_name = author.get("name") or "Unknown"
            author_link = author.get("href") or ""
            author_id = author_link.split("/")[-1] if author_link else "0"
            authors.append(
                Author(name=author_name, id=author_id, link=author_link, number_of_books=0),
            )

        title = entry.get("title") or "Unknown Title"
        entry_id = entry.get("id", "")

        links = entry.get("links") or []
        download_links: dict[str, str] = {}
        cover_image: str | None = None

        for link in links:
            rel = link.get("rel", "")
            href = link.get("href") or ""
            type_ = link.get("type", "")

            if type_.startswith("application/") and rel != "related":
                fmt = href.split("/")[-1].replace("download", "pdf")
                if fmt:
                    download_links[fmt] = urljoin(self.base_url, href)

            if type_ == "image/jpeg" and not cover_image and href:
                cover_image = urljoin(self.base_url, href)

        web_link = urljoin(self.base_url, entry.get("link") or "")

        tags = [
            t.get("label") or t.get("term") or ""
            for t in entry.get("tags") or []
            if t.get("label") or t.get("term")
        ]

        summary_raw = entry.get("summary")
        summary = _strip_html(summary_raw) if summary_raw else None

        return Book(
            title=title,
            authors=authors,
            book_id=entry_id,
            download_links=download_links,
            tags=tags,
            cover_image=cover_image,
            summary=summary,
            language=entry.get("dcterms_language"),
            published=entry.get("published"),
            web_link=web_link,
        )

    def parse_authors(self, xml_content: bytes) -> tuple[list[Author], str | None]:
        """Parse OPDS feed into list of authors and optional next page URL."""
        try:
            feed = parse(xml_content)
        except (ValueError, KeyError, AttributeError, TypeError, OSError) as e:
            msg = f"Failed to parse OPDS feed: {e}"
            raise ParseError(msg) from e

        next_url = extract_next_link(feed, self.base_url)
        authors: list[Author] = []

        for entry in feed.get("entries") or []:
            try:
                author = self._parse_author_entry(entry)
                if author:
                    authors.append(author)
            except (ValueError, KeyError) as e:
                msg = f"Failed to parse author entry: {e}"
                raise ParseError(msg) from e

        return authors, next_url

    def _parse_author_entry(self, entry: dict) -> Author | None:
        """Parse a single OPDS entry into an Author."""
        summary = entry.get("summary")
        if not summary:
            return None

        number_str = summary.split()[0] if summary.strip() else "0"
        try:
            number_of_books = int(number_str)
        except ValueError:
            number_of_books = 0

        links = entry.get("links") or []
        alternate_link = next(
            (link for link in links if link.get("rel") == "alternate"),
            None,
        )
        if not alternate_link:
            return None

        name = entry.get("title") or "Unknown"
        href = alternate_link.get("href") or ""
        author_id = href.split("/")[-1] if href else "0"

        return Author(
            name=name,
            id=author_id,
            link=urljoin(self.base_url, href),
            number_of_books=number_of_books,
        )
