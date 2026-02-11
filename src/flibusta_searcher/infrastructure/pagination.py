"""Generic pagination helpers for OPDS fetching."""

from collections.abc import Callable
from typing import TypeVar
from urllib.parse import parse_qsl, urljoin, urlparse

T = TypeVar("T")


def extract_next_link(feed: dict, base_url: str) -> str | None:
    """Extract the next page URL from an OPDS feed."""
    feed_obj = feed.get("feed")
    if not feed_obj:
        return None
    links = feed_obj.get("links")
    if not links:
        return None
    for link in links:
        if link.get("rel") == "next":
            href = link.get("href")
            if href:
                return urljoin(base_url, href)
            return None
    return None


def parse_next_url_params(next_url: str, base_url: str) -> tuple[str, dict]:
    """Parse next URL into path and params for the next request."""
    parsed = urlparse(next_url)
    url = urljoin(base_url, parsed.path)
    params = dict(parse_qsl(parsed.query))
    return url, params


def fetch_paginated[T](
    url: str,
    params: dict,
    limit: int,
    base_url: str,
    get_response: Callable[[str, dict], bytes],
    parse_fn: Callable[[bytes], tuple[list[T], str | None]],
) -> list[T]:
    """Fetch pages until limit reached or no more pages (Generic function)."""
    all_items: list[T] = []
    current_url: str | None = url
    current_params = params

    while current_url and len(all_items) < limit:
        if "pageNumber=" in (current_url or ""):
            current_params = {}

        content = get_response(current_url, current_params)
        items, next_url = parse_fn(content)
        all_items.extend(items)

        if next_url:
            current_url, current_params = parse_next_url_params(next_url, base_url)
        else:
            current_url = None

    return all_items[:limit]
