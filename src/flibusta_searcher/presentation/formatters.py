"""Rich table formatters for CLI output."""

from rich.table import Table

from flibusta_searcher.domain.entities import Author, Book


def create_authors_table(authors: list[Author]) -> Table:
    """Create a Rich table for authors list."""
    table = Table(title=f"Found Authors ({len(authors)})")
    table.add_column("Nr.", style="green")
    table.add_column("ID", style="green")
    table.add_column("Name", style="cyan", no_wrap=True)
    table.add_column("Books count", style="yellow")
    table.add_column("Link", style="magenta")

    for i, author in enumerate(authors):
        table.add_row(str(i + 1), author.id, author.name, str(author.number_of_books), author.link)
    return table


def create_books_table(
    books: list[Book],
    page: int = 1,
    total_pages: int = 1,
    page_offset: int = 0,
    total_count: int = 0,
) -> Table:
    """Create a Rich table for books list."""
    total = total_count if total_count > 0 else len(books)
    title = f"Found Books ({total})"
    if total_pages > 1:
        title += f" - Page {page}/{total_pages}"
    table = Table(title=title)
    table.add_column("Nr.", style="green")
    table.add_column("Title", style="cyan", no_wrap=False)
    table.add_column("Author", style="green")
    table.add_column("Formats", style="yellow")

    for i, book in enumerate(books):
        book_number = page_offset + i + 1
        format_links = ", ".join(f"[link={url}]{fmt}[/]" for fmt, url in book.download_links.items())
        # TODO: collapse authors list to 2-3 with "+ n more" when multiple authors
        table.add_row(str(book_number), book.title, ", ".join(book.get_author_names()), format_links)
    return table


def create_book_details_table(book: Book) -> Table:
    """Create a Rich table for book details."""
    detail_table = Table(title="Book Details", show_header=False)
    detail_table.add_row("Title", book.title)
    detail_table.add_row("Authors", ", ".join(book.get_author_names()))
    if book.tags:
        detail_table.add_row("Tags", ", ".join(book.tags))
    if book.size:
        detail_table.add_row("Size", book.size)
    if book.cover_image:
        detail_table.add_row("Cover", f"[link={book.cover_image}]Cover Image[/]")
    if book.download_links:
        formats_list = list(book.download_links.items())
        fmt_display = ", ".join(
            f"[green]{i+1}[/green]. {fmt}" for i, (fmt, _url) in enumerate(formats_list)
        )
        detail_table.add_row("Formats", fmt_display)
    if language := book.language:
        detail_table.add_row("Language", language)
    if published := book.published:
        detail_table.add_row("Published", published)
    if description := book.summary:
        detail_table.add_row("Description", description)
    return detail_table
