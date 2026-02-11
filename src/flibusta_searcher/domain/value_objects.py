"""Domain value objects."""

import re
from dataclasses import dataclass
from typing import NewType

AuthorId = NewType("AuthorId", str)
BookId = NewType("BookId", str)

# Default max filename length; callers can override (e.g. from config)
DEFAULT_MAX_FILENAME_LENGTH = 200


def sanitize_filename(filename: str, max_length: int = DEFAULT_MAX_FILENAME_LENGTH) -> str:
    """Remove invalid characters from filename."""
    filename = re.sub(r'[<>:"/\\|?*]', "_", filename)
    filename = filename.strip(" .")
    if len(filename) > max_length:
        filename = filename[:max_length]
    return filename


@dataclass(frozen=True)
class DownloadFormat:
    """Represents a downloadable book format (e.g., fb2, epub)."""

    format: str
    url: str
