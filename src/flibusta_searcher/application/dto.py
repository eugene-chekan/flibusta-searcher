"""Data transfer objects for application layer."""

from dataclasses import dataclass
from pathlib import Path


@dataclass
class DownloadResult:
    """Result of a download operation."""

    success: bool
    filepath: Path | None = None
    file_size_bytes: int = 0
    error: str | None = None
