# Flibusta Searcher

A powerful command-line interface (CLI) tool for searching and browsing books and authors on Flibusta, a popular digital library. Built with Python, this tool provides an intuitive way to discover books, explore author catalogs, and access detailed book information directly from your terminal.

## Features

- 🔍 **Book Search**: Search for books by title or author name
- 👤 **Author Search**: Find authors and browse their complete catalogs
- 📚 **Author Books**: List all books by a specific author
- 📖 **Detailed Book Info**: View comprehensive book details including:
  - Title, authors, and tags
  - Available formats with clickable download links
  - Cover images
  - Book descriptions
  - Publication dates and language
  - File sizes
- 🎨 **Rich Terminal UI**: Beautiful tables and formatted output using Rich library
- 🔗 **Interactive Navigation**: Select authors and books from search results to drill down into details
- 📄 **Pagination Support**: Automatically fetches paginated results from the OPDS catalog

## Requirements

- Python 3.13 or higher
- [uv](https://github.com/astral-sh/uv) package manager (recommended)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd flibusta-searcher
```

2. Install dependencies using `uv`:
```bash
uv sync
```

Alternatively, you can install using pip:
```bash
pip install -e .
```

## Quick Start

### Interactive Mode

Simply run the CLI without any arguments to enter interactive mode:

```bash
uv run -m main
```


You'll be prompted to choose between searching for books or browsing an author's catalog.

### Command-Line Usage

#### Search for Books

```bash
# Search for books by title or author
uv run -m main search "Tolstoy"

# Or using the module directly
uv run -m main search "War and Peace"
```

#### Search for Authors

```bash
# Search for authors by name
uv run -m main search --authors "Dostoevsky"
```

#### List Books by Author ID

```bash
# Get all books by a specific author using their ID
uv run -m main author-books 123456
```

## Usage Examples

### Example 1: Search for Books

```bash
$ uv run -m main search "1984"
```

This will display a table of books matching "1984" with their titles, authors, and available formats.

### Example 2: Interactive Author Search

```bash
$ uv run -m main search --authors "George Orwell"
```

After seeing the results, you can:
1. Enter an author number to view all their books
2. Enter a book number to see detailed information including description, cover, and download links

### Example 3: Browse Author's Complete Catalog

```bash
$ uv run -m main author-books 12345
```

This displays all books by the author with ID 12345.

## Project Structure

The project follows Clean Architecture principles:

```
flibusta-searcher/
├── src/
│   └── flibusta_searcher/
│       ├── __init__.py
│       ├── cli.py              # CLI entry point
│       ├── container.py        # Dependency injection
│       ├── models.py          # Re-exports domain entities
│       ├── domain/             # Domain layer
│       │   ├── entities.py    # Book, Author
│       │   ├── value_objects.py
│       │   └── exceptions.py
│       ├── application/       # Application layer (use cases)
│       │   ├── ports.py       # Interfaces
│       │   ├── dto.py
│       │   └── use_cases/
│       ├── infrastructure/    # Infrastructure layer
│       │   ├── config.py      # Pydantic config
│       │   ├── opds/          # OPDS client & parser
│       │   ├── download/      # File downloader
│       │   └── pagination.py
│       └── presentation/     # Presentation layer
│           ├── formatters.py  # Rich tables
│           ├── views.py       # Interactive views
│           └── utils.py
├── .env                      # FLIBUSTA_BASE_URL, FLIBUSTA_OPDS_URL
├── pyproject.toml
└── README.md
```

## Configuration

Create a `.env` file in the project root:

```
FLIBUSTA_BASE_URL=https://flibusta.is
FLIBUSTA_OPDS_URL=https://flibusta.is/opds
```

Optional settings (with defaults):
- `FLIBUSTA_DOWNLOAD_DIR` - Download directory (default: `./downloads`)
- `FLIBUSTA_DEFAULT_TIMEOUT` - HTTP timeout in seconds (default: 30)
- `FLIBUSTA_DOWNLOAD_TIMEOUT` - Download timeout (default: 60)

## Development

### Dependencies

The project uses the following main dependencies:

- **typer**: CLI framework with type hints
- **rich**: Terminal formatting and tables
- **httpx**: HTTP client for API requests
- **feedparser**: OPDS catalog parsing
- **pydantic-settings**: Configuration with validation

### Development Tools

- **ruff**: Linting and formatting
- **ty**: Type checking

### Running Tests

```bash
# Format code
uv run ruff format .

# Lint code
uv run ruff check .
```

## How It Works

The tool interacts with Flibusta's OPDS (Open Publication Distribution System) catalog to:

1. Search for books and authors using OPDS search endpoints
2. Parse XML/Atom feeds to extract book and author information
3. Handle pagination automatically to retrieve complete result sets
4. Display results in formatted tables with clickable links

## License

This project is open source and available under the MIT License.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Acknowledgments

- Built for the [Flibusta](https://flibusta.is) digital library
- Uses the OPDS catalog standard for book discovery
