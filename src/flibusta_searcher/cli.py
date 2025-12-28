from flibusta_searcher.models import Book, Author
import typer
import click
from rich.console import Console
from rich.table import Table
from rich import print as rprint
from .client import FlibustaClient

app = typer.Typer(help="Search for books and authors on Flibusta.")
console = Console()
client = FlibustaClient()


@app.callback(invoke_without_command=True)
def callback(ctx: typer.Context):
    """Flibusta Searcher CLI."""
    if ctx.invoked_subcommand is None:
        rprint("[bold green]Welcome to Flibusta Searcher![/bold green]")

        choice = typer.prompt(
            "Choose action",
            type=click.Choice(["search", "author-books"]),
            default="search",
        )

        if choice == "search":
            query = typer.prompt("Enter search query (book title or author)")
            _search_books(query)
        else:
            author_id = typer.prompt("Enter Author ID")
            author_books(author_id)


@app.command()
def search(
    query: str = typer.Argument(..., help="Search query (book title or author name)."),
    books: bool = typer.Option(True, "--books/--no-books", help="Search for books."),
    authors: bool = typer.Option(False, "--authors/--no-authors", help="Search for authors.")
):
    """Search Flibusta for books or authors."""
    # If user didn't specify either, default to books
    if not books and not authors:
        books = True

    if authors:
        # For author search, only generic pattern applies to name
        _search_authors(query)

    if books:
        _search_books(query)


def _search_authors(query: str):
    rprint(f"[bold blue]Searching authors for:[/bold blue] {query}")
    results = client.search_authors(query)

    if not results:
        rprint("[yellow]No authors found.[/yellow]")
        return

    table = _create_authors_table(results)
    console.print(table)

    # Prompt to list books for a selected author
    try:
        choice = typer.prompt(
            "Enter Author number (or press Enter to skip)",
            default="",
            show_default=False,
        )
    except Exception:
        choice = ""
    if choice:
        idx = int(choice) - 1
        author = results[idx] if 0 <= idx < len(results) else None
        if not author:
            rprint("[red]Invalid author number.[/red]")
            return
        # Reuse author_books command logic
        rprint(f"[bold blue]Fetching books for author:[/bold blue] {author.name}")
        books = client.get_author_books(author.id)
        if not books:
            rprint("[yellow]No books found for this author.[/yellow]")
            return
        table = _create_books_table(books)
        console.print(table)

        # Prompt for detailed view of a selected book
        try:
            choice = typer.prompt(
                "Enter book number for full info (or press Enter to skip)",
                default="",
                show_default=False,
            )
        except Exception:
            choice = ""
        if choice:
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(books):
                    sel_book = books[idx]
                    # Display detailed information
                    detail_table = _create_book_details_table(sel_book)
                    console.print(detail_table)
                else:
                    rprint("[red]Invalid book number.[/red]")
            except ValueError:
                rprint("[red]Please enter a valid number.[/red]")


@app.command()
def author_books(
    author_id: str = typer.Argument(..., help="The ID of the author to fetch books for."),
):
    """List all books by a specific author ID."""
    rprint(f"[bold blue]Fetching books for author ID:[/bold blue] {author_id}")
    results = client.get_author_books(author_id)

    if not results:
        rprint("[yellow]No books found.[/yellow]")
        return

    table = _create_books_table(results)
    console.print(table)


def _search_books(query: str):
    rprint(f"[bold blue]Searching books for:[/bold blue] {query}")
    results = client.search_books(query)
    if not results:
        rprint("[yellow]No books found.[/yellow]")
        return

    table = _create_books_table(results)
    console.print(table)


def _create_authors_table(authors: list[Author]) -> Table:
    table = Table(title=f"Found Authors ({len(authors)})")
    table.add_column("Nr.", style="green")
    table.add_column("ID", style="green")
    table.add_column("Name", style="cyan", no_wrap=True)
    table.add_column("Books count", style="yellow")
    table.add_column("Link", style="magenta")

    for i, author in enumerate(authors):
        table.add_row(str(i + 1), author.id, author.name, str(author.number_of_books), author.link)
    return table


def _create_books_table(books: list[Book]) -> Table:
    table = Table(title=f"Found Books ({len(books)})")
    table.add_column("Nr.", style="green")
    table.add_column("Title", style="cyan", no_wrap=False)
    table.add_column("Author", style="green")
    table.add_column("Formats", style="yellow")
    # Combine clickable format links; omit raw URLs column
    for i, book in enumerate(books):
        format_links = ", ".join(
            f"[link={url}]{fmt}[/]" for fmt, url in book.download_links.items()
        )
        table.add_row(str(i + 1), book.title, ", ".join([a.name for a in book.authors]), format_links)

    return table


def _create_book_details_table(book: Book) -> Table:
    detail_table = Table(title="Book Details", show_header=False)
    detail_table.add_row("Title", book.title)
    detail_table.add_row("Authors", ", ".join([a.name for a in book.authors]))
    if book.tags:
        detail_table.add_row("Tags", ", ".join(book.tags))
    if book.size:
        detail_table.add_row("Size", book.size)
    if book.cover_image:
        detail_table.add_row(
            "Cover", f"[link={book.cover_image}]Cover Image[/]"
        )
    fmt_links = ", ".join(
        f"[link={url}]{fmt}[/]"
        for fmt, url in book.download_links.items()
    )
    detail_table.add_row("Formats", fmt_links)
    if language := book.language:
        detail_table.add_row("Language", language)
    if published := book.published:
        detail_table.add_row("Published", published)
    if description := book.summary:
        detail_table.add_row("Description", description)
    return detail_table
