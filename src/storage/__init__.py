"""
Storage module for metadata management.

Provides DuckDB-based storage for projects, repositories, links,
artifact management, and Parquet archiving utilities.
"""

from .artifact_manager import (
    ArtifactManager,
    FileMetadata,
    RunContext,
    RunMetadata,
)
from .duckdb_client import DuckDBClient, get_duckdb_client
from .metadata_store import ProjectStore, RepositoryStore, LinkStore

__all__ = [
    "DuckDBClient",
    "get_duckdb_client",
    "ProjectStore",
    "RepositoryStore",
    "LinkStore",
    "ArtifactManager",
    "RunContext",
    "RunMetadata",
    "FileMetadata",
]
