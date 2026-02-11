"""CLI entry point with dependency injection."""

import httpx
import typer
from rich import print as rprint
from rich.console import Console

from .container import Container
from .domain.exceptions import ParseError
from .presentation.formatters import create_authors_table
from .presentation.views import get_user_choice, view_books_paginated

app = typer.Typer(help="Search for books and authors on Flibusta.")
console = Console()

# Container is created lazily on first use
_container: Container | None = None


def _get_container() -> Container:
    """Get or create the DI container."""
    global _container  # noqa: PLW0603
    if _container is None:
        _container = Container()
    return _container


@app.callback(invoke_without_command=True)
def callback(ctx: typer.Context) -> None:
    """Flibusta Searcher CLI."""
    if ctx.invoked_subcommand is None:
        _interactive_menu()


def _interactive_menu() -> None:
    """Interactive menu loop for keyboard-based navigation."""
    container = _get_container()

    rprint("[bold green]Welcome to Flibusta Searcher![/bold green]")
    rprint("[dim]Search for books and authors on Flibusta[/dim]\n")

    while True:
        rprint("\n[bold cyan]Menu:[/bold cyan]")
        rprint("  [green]1[/green] - Search for authors")
        rprint("  [green]2[/green] - Search for books")
        rprint("  [yellow]q[/yellow] - Quit\n")

        choice = get_user_choice("Enter your choice", "q").strip().lower()

        if choice == "q":
            rprint("\n[bold green]Goodbye![/bold green]")
            break
        if choice == "1":
            query = typer.prompt("Enter author name to search")
            if query:
                _search_authors(container, query)
        elif choice == "2":
            query = typer.prompt("Enter book title to search")
            if query:
                _search_books(container, query)
        else:
            rprint("[red]Invalid choice. Please enter 1, 2, or q.[/red]")


@app.command()
def search(
    query: str = typer.Argument(..., help="Search query (book title or author name)."),
    *,
    books: bool = typer.Option(True, "--books/--no-books", help="Search for books."),
    authors: bool = typer.Option(False, "--authors/--no-authors", help="Search for authors."),
) -> None:
    """Search Flibusta for books or authors."""
    container = _get_container()

    if not books and not authors:
        books = True

    if authors:
        _search_authors(container, query)

    if books:
        _search_books(container, query)


def _search_authors(container: Container, query: str) -> None:
    """Search authors and optionally show their books."""
    rprint(f"[bold blue]Searching authors for:[/bold blue] {query}")
    try:
        results = container.search_authors.execute(query)
    except ParseError as e:
        rprint(f"[red]Error parsing catalog: {e}[/red]")
        return
    except httpx.HTTPError as e:
        rprint(f"[red]Network error: {e}[/red]")
        return

    if not results:
        rprint("[yellow]No authors found.[/yellow]")
        return

    table = create_authors_table(results)
    console.print(table)

    choice = get_user_choice("Enter Author number (or press Enter to skip)")
    if choice:
        idx = int(choice) - 1
        author = results[idx] if 0 <= idx < len(results) else None
        if not author:
            rprint("[red]Invalid author number.[/red]")
            return
        rprint(f"[bold blue]Fetching books for author:[/bold blue] {author.name}")
        try:
            books_list = container.get_author_books.execute(author.id)
        except ParseError as e:
            rprint(f"[red]Error parsing catalog: {e}[/red]")
            return
        except httpx.HTTPError as e:
            rprint(f"[red]Network error: {e}[/red]")
            return
        if not books_list:
            rprint("[yellow]No books found for this author.[/yellow]")
            return

        view_books_paginated(
            books_list,
            page_size=container.config.default_page_size,
            download_use_case=container.download_book,
            download_dir=container.config.download_dir,
            console=console,
        )


@app.command()
def author_books(
    author_id: str = typer.Argument(..., help="The ID of the author to fetch books for."),
) -> None:
    """List all books by a specific author ID."""
    container = _get_container()

    rprint(f"[bold blue]Fetching books for author ID:[/bold blue] {author_id}")
    try:
        results = container.get_author_books.execute(author_id)
    except ParseError as e:
        rprint(f"[red]Error parsing catalog: {e}[/red]")
        return
    except httpx.HTTPError as e:
        rprint(f"[red]Network error: {e}[/red]")
        return

    if not results:
        rprint("[yellow]No books found.[/yellow]")
        return

    view_books_paginated(
        results,
        page_size=container.config.default_page_size,
        download_use_case=container.download_book,
        download_dir=container.config.download_dir,
        console=console,
    )


def _search_books(container: Container, query: str) -> None:
    """Search books and display results."""
    rprint(f"[bold blue]Searching books for:[/bold blue] {query}")
    try:
        results = container.search_books.execute(query)
    except ParseError as e:
        rprint(f"[red]Error parsing catalog: {e}[/red]")
        return
    except httpx.HTTPError as e:
        rprint(f"[red]Network error: {e}[/red]")
        return
    if not results:
        rprint("[yellow]No books found.[/yellow]")
        return

    view_books_paginated(
        results,
        page_size=container.config.default_page_size,
        download_use_case=container.download_book,
        download_dir=container.config.download_dir,
        console=console,
    )
