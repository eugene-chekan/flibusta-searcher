"""Interactive views for CLI."""

from pathlib import Path
from typing import TYPE_CHECKING

import typer
from rich import print as rprint
from rich.console import Console

from flibusta_searcher.domain.entities import Book
from flibusta_searcher.domain.exceptions import DownloadError
from flibusta_searcher.presentation.formatters import create_book_details_table, create_books_table

if TYPE_CHECKING:
    from flibusta_searcher.application.use_cases.download_book import DownloadBookUseCase


def get_user_choice(prompt_text: str, default: str = "") -> str:
    """Get user input, returning default on interrupt."""
    try:
        return typer.prompt(prompt_text, default=default, show_default=False)
    except (KeyboardInterrupt, EOFError, typer.Exit, typer.Abort):
        return default


def view_books_paginated(
    all_books: list[Book],
    page_size: int,
    download_use_case: "DownloadBookUseCase",
    download_dir: Path,
    console: Console | None = None,
) -> None:
    """Interactive paginated book viewing."""
    console = console or Console()
    total_books = len(all_books)
    total_pages = (total_books + page_size - 1) // page_size
    current_page = 1

    while True:
        start_idx = (current_page - 1) * page_size
        end_idx = min(start_idx + page_size, total_books)
        page_books = all_books[start_idx:end_idx]

        table = create_books_table(
            page_books,
            page=current_page,
            total_pages=total_pages,
            page_offset=start_idx,
            total_count=total_books,
        )
        console.print(table)

        prompt_msg = "Enter book number for full info"
        if total_pages > 1:
            prompt_msg += ', "n" for next page, "p" for previous page'
        prompt_msg += ', "b" to go back to list, or press Enter to return to menu'

        while True:
            choice = get_user_choice(prompt_msg)
            if not choice:
                return

            choice_lower = choice.strip().lower()

            if choice_lower == "n" and total_pages > 1:
                if current_page < total_pages:
                    current_page += 1
                    break
                rprint("[yellow]You are already on the last page.[/yellow]")
                continue
            if choice_lower == "p" and total_pages > 1:
                if current_page > 1:
                    current_page -= 1
                    break
                rprint("[yellow]You are already on the first page.[/yellow]")
                continue
            if choice_lower == "b":
                console.print(table)
                continue

            try:
                book_num = int(choice)
                if 1 <= book_num <= total_books:
                    sel_book = all_books[book_num - 1]
                    detail_table = create_book_details_table(sel_book)
                    console.print(detail_table)
                    _prompt_book_download(sel_book, download_use_case, download_dir, console)
                else:
                    rprint(
                        f"[red]Invalid book number. Please enter a number between 1 and {total_books}.[/red]"
                    )
            except ValueError:
                rprint(
                    '[red]Please enter a valid number, "n"/"p" for navigation, '
                    '"b" to go back, or press Enter.[/red]',
                )


def _prompt_book_download(
    book: Book,
    download_use_case: "DownloadBookUseCase",
    download_dir: Path,
    console: Console,
) -> None:
    """Prompt user to download a book after viewing details."""
    if not book.download_links:
        return

    formats_list = list(book.download_links.items())
    rprint("\n[bold cyan]Available formats:[/bold cyan]")
    for i, (fmt, _url) in enumerate(formats_list, 1):
        rprint(f"  [green]{i}[/green]. {fmt.upper()}")

    choice = get_user_choice(
        "\nEnter format number to download (or press Enter to skip)",
    )
    if not choice:
        return

    try:
        format_num = int(choice)
        _do_download(book, format_num, download_use_case, download_dir, console)
    except ValueError:
        rprint("[red]Please enter a valid number.[/red]")


def _do_download(
    book: Book,
    format_num: int,
    download_use_case: "DownloadBookUseCase",
    download_dir: Path,
    console: Console,  # noqa: ARG001
) -> None:
    """Execute download with overwrite prompt."""
    fmt = list(book.download_links.keys())[format_num - 1]
    rprint(f"[blue]Downloading {fmt} format...[/blue]")
    try:
        result = download_use_case.execute(book, format_num, download_dir, overwrite=False)
    except DownloadError as e:
        rprint(f"[red]Error downloading file: {e}[/red]")
        return

    if not result.success and result.error == "File exists" and result.filepath:
        overwrite = typer.confirm(f"File already exists: {result.filepath.name}\nOverwrite?")
        if overwrite:
            try:
                result = download_use_case.execute(book, format_num, download_dir, overwrite=True)
            except DownloadError as e:
                rprint(f"[red]Error downloading file: {e}[/red]")
                return
        else:
            rprint("[yellow]Download cancelled.[/yellow]")
            return

    if result.success and result.filepath:
        size_mb = result.file_size_bytes / (1024 * 1024)
        rprint("[green]✓ Downloaded successfully![/green]")
        rprint(f"[dim]Saved to: {result.filepath}[/dim]")
        rprint(f"[dim]Size: {size_mb:.2f} MB[/dim]")
    elif result.error:
        rprint(f"[red]{result.error}[/red]")
