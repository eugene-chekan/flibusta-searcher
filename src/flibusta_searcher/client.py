import httpx
from feedparser import parse
from typing import List, Optional
from urllib.parse import urljoin, urlparse, parse_qsl
from .models import Book, Author


class FlibustaClient:
    BASE_URL = "https://flibusta.is"
    OPDS_URL = "https://flibusta.is/opds"

    def __init__(self, base_url: Optional[str] = None):
        self.base_url = base_url or self.BASE_URL
        self.client = httpx.Client(follow_redirects=True, timeout=30.0)

    def search_books(self, query: str, limit: int = 100) -> List[Book]:
        """Search for books using the OPDS catalog."""
        url = f"{self.OPDS_URL}/search"
        params = {"searchType": "books", "searchTerm": query}
        return self._fetch_paginated_books(url, params, limit)

    def search_authors(self, query: str, limit: int = 20) -> List[Author]:
        """Search for authors using the OPDS catalog."""
        url = f"{self.OPDS_URL}/search"
        params = {"searchType": "authors", "searchTerm": query}
        return self._fetch_paginated_authors(url, params, limit)

    def get_author_books(self, author_id: str, limit: int = 100) -> List[Book]:
        """Get all books by a specific author."""
        url = f"{self.OPDS_URL}/author/{author_id}/alphabet"
        return self._fetch_paginated_books(url, {}, limit)

    def _fetch_paginated_books(self, url: Optional[str], params: dict, limit: int) -> List[Book]:
        all_books = []

        while url and len(all_books) < limit:
            try:
                if "pageNumber=" in url:
                    params = {}

                response = self.client.get(url, params=params)
                response.raise_for_status()
                books, next_url = self._parse_books(response.content)
                all_books.extend(books)

                if next_url:
                    parsed = urlparse(next_url)
                    url = urljoin(self.base_url, parsed.path)
                    params = dict(parse_qsl(parsed.query))
                else:
                    url = None

            except httpx.HTTPError as e:
                print(f"Error fetching books: {e}")
                break

        return all_books

    def _fetch_paginated_authors(self, url: Optional[str], params: dict, limit: int) -> List[Author]:
        all_authors = []

        while url and len(all_authors) < limit:
            try:
                if "pageNumber=" in url:
                    params = {}

                response = self.client.get(url, params=params)
                response.raise_for_status()
                authors, next_url = self._parse_authors(response.content)
                all_authors.extend(authors)

                if next_url:
                    parsed = urlparse(next_url)
                    url = urljoin(self.base_url, parsed.path)
                    params = dict(parse_qsl(parsed.query))
                else:
                    url = None

            except httpx.HTTPError as e:
                print(f"Error fetching authors: {e}")
                break

        return all_authors

    def _parse_books(self, xml_content: bytes) -> tuple[List[Book], Optional[str]]:
        feed = parse(xml_content)
        books = []

        # Check for next page link
        next_url = None
        if feed.get("feed"):
            for link in feed.get("feed").get("links"):
                if link.get("rel") == "next":
                    next_url = urljoin(self.base_url, link.get("href"))
                    break

        for entry in feed.entries:
            # Check if it's a book entry or navigation entry
            # OPDS search results might contain navigation links (like 'next page' or 'search authors')
            # Book entries usually have an 'author' tag and acquisition links.

            authors_entry = entry.get("authors")
            authors = []
            for author in authors_entry:
                author_name = author.get("name")
                author_link = author.get("href")
                author_id = author_link.split("/")[-1]
                authors.append(Author(name=author_name, id=author_id, link=author_link, number_of_books=0))

            title = entry.get("title", "Unknown Title")

            # ID extraction
            entry_id = entry.get("id", "")
            # entry_id looks like 'tag:book:MD5HASH' or similar.

            # Download links
            links = {}
            cover_image = None

            for link in entry.get("links"):
                rel = link.get("rel")
                href = link.get("href")
                type_ = link.get("type", "")

                if type_.startswith("application/") and not rel == "related":
                    if fmt := href.split("/")[-1].replace("download", "pdf"):
                        links[fmt] = urljoin(self.base_url, href)

                if type_ == "image/jpeg" and not cover_image:
                    cover_image = urljoin(self.base_url, href)

            web_link = urljoin(self.base_url, entry.get("link"))

            # Tags
            tags = [
                t.get("label") or t.get("term") or ""
                for t in entry.get("tags")
                if t.get("label")
            ]
            # Description (content or summary)
            summary = entry.get("summary")
            # Language and published date (if available in OPDS)
            language = entry.get("dcterms_language")
            published = entry.get("published")

            books.append(
                Book(
                    title=title,
                    authors=authors,
                    book_id=entry_id,
                    download_links=links,
                    tags=tags,
                    cover_image=cover_image,
                    summary=summary,
                    language=language,
                    published=published,
                    web_link=web_link,
                )
            )

        return books, next_url

    def _parse_authors(self, xml_content: bytes) -> tuple[List[Author], Optional[str]]:
        feed = parse(xml_content)
        authors = []

        # Check for next page link
        next_url = None
        if feed.get("feed"):
            for link in feed.get("feed").get("links"):
                if link.get("rel") == "next":
                    next_url = urljoin(self.base_url, link.get("href"))
                    break

        for entry in feed.get("entries"):
            number_of_books = entry.get("summary").split()[0]
            if link := next((link for link in entry.get("links") if link.get("rel") == "alternate"), None):
                name = entry.get("title")
                href = link.get("href")
                author_id = href.split("/")[-1]

                authors.append(
                    Author(name=name, id=author_id, link=urljoin(self.base_url, href), number_of_books=int(number_of_books))
                )

        return authors, next_url
