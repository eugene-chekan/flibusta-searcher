"""Application configuration with validation."""

from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class FlibustaConfig(BaseSettings):
    """Flibusta Searcher configuration loaded from environment."""

    model_config = SettingsConfigDict(
        env_prefix="FLIBUSTA_",
        env_file=".env",
        env_file_encoding="utf-8",
    )

    base_url: str = Field(..., description="Base URL for Flibusta")
    opds_url: str = Field(..., description="OPDS catalog URL")
    download_dir: Path = Field(default=Path.cwd() / "downloads", description="Directory for downloaded books")
    default_timeout: float = Field(default=30.0, description="HTTP request timeout in seconds")
    download_timeout: float = Field(default=60.0, description="Download request timeout in seconds")
    default_page_size: int = Field(default=50, description="Default page size for pagination")
    max_pagination_limit: int = Field(default=1_000, description="Max items to fetch when fetching all")
    max_filename_length: int = Field(default=200, description="Maximum filename length")
