"""
Artifact management for ingestion runs and file versioning.

Manages hierarchical directory structure for ingestion artifacts:
- data/{project}/{timestamp}_{seq}_{action}/{artifact_type}/

Tracks run metadata and file versions in DuckDB with SHA256 content hashing.
"""

import hashlib
import logging
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from .duckdb_client import get_duckdb_client

logger = logging.getLogger(__name__)


class RunContext:
    """Context for an ingestion run with paths to artifact directories."""

    def __init__(
        self,
        run_id: str,
        project_id: str,
        project_name: str,
        timestamp: str,
        sequence: int,
        action: str,
        base_path: Path
    ):
        self.run_id = run_id
        self.project_id = project_id
        self.project_name = project_name
        self.timestamp = timestamp
        self.sequence = sequence
        self.action = action
        self.base_path = base_path

    @property
    def run_dir(self) -> Path:
        """Get the run directory path."""
        sanitized_name = self._sanitize_project_name(self.project_name)
        run_dirname = f"{self.timestamp}_{self.sequence:03d}_{self.action}"
        return self.base_path / sanitized_name / run_dirname

    def get_artifact_dir(self, artifact_type: str) -> Path:
        """
        Get path to artifact directory for this run.

        Args:
            artifact_type: Type of artifact ('raw_source', 'sql_embeddings', 'embeddings', 'graph_export')

        Returns:
            Path to artifact directory
        """
        return self.run_dir / artifact_type

    @staticmethod
    def _sanitize_project_name(name: str) -> str:
        """Sanitize project name for filesystem use."""
        # Replace non-alphanumeric chars with underscores (including spaces)
        sanitized = "".join(c if c.isalnum() or c in ('-', '_') else '_' for c in name)
        # Collapse multiple underscores
        while '__' in sanitized:
            sanitized = sanitized.replace('__', '_')
        return sanitized.strip('_')

    def to_dict(self) -> dict:
        """Convert to dictionary representation."""
        return {
            "run_id": self.run_id,
            "project_id": self.project_id,
            "project_name": self.project_name,
            "timestamp": self.timestamp,
            "sequence": self.sequence,
            "action": self.action,
            "run_dir": str(self.run_dir),
        }


class RunMetadata:
    """Metadata for an ingestion run."""

    def __init__(
        self,
        run_id: str,
        project_id: str,
        timestamp: str,
        sequence: int,
        action: str,
        status: str,
        created_at: str,
        completed_at: Optional[str] = None,
        error_message: Optional[str] = None
    ):
        self.run_id = run_id
        self.project_id = project_id
        self.timestamp = timestamp
        self.sequence = sequence
        self.action = action
        self.status = status
        self.created_at = created_at
        self.completed_at = completed_at
        self.error_message = error_message

    def to_dict(self) -> dict:
        """Convert to dictionary representation."""
        return {
            "run_id": self.run_id,
            "project_id": self.project_id,
            "timestamp": self.timestamp,
            "sequence": self.sequence,
            "action": self.action,
            "status": self.status,
            "created_at": self.created_at,
            "completed_at": self.completed_at,
            "error_message": self.error_message,
        }


class FileMetadata:
    """Metadata for a file in a run."""

    def __init__(
        self,
        file_id: str,
        project_id: str,
        run_id: str,
        filename: str,
        file_path: str,
        file_hash: str,
        file_size_bytes: int,
        is_superseded: bool,
        superseded_by: Optional[str],
        created_at: str,
        processed_at: Optional[str] = None
    ):
        self.file_id = file_id
        self.project_id = project_id
        self.run_id = run_id
        self.filename = filename
        self.file_path = file_path
        self.file_hash = file_hash
        self.file_size_bytes = file_size_bytes
        self.is_superseded = is_superseded
        self.superseded_by = superseded_by
        self.created_at = created_at
        self.processed_at = processed_at

    def to_dict(self) -> dict:
        """Convert to dictionary representation."""
        return {
            "file_id": self.file_id,
            "project_id": self.project_id,
            "run_id": self.run_id,
            "filename": self.filename,
            "file_path": self.file_path,
            "file_hash": self.file_hash,
            "file_size_bytes": self.file_size_bytes,
            "is_superseded": self.is_superseded,
            "superseded_by": self.superseded_by,
            "created_at": self.created_at,
            "processed_at": self.processed_at,
        }


class ArtifactManager:
    """
    Centralized service for managing ingestion run artifacts and file versioning.

    Responsibilities:
    - Create timestamped run directories
    - Generate artifact paths
    - Track run metadata in DuckDB
    - Handle file versioning with content hashing
    - Detect duplicate content and skip reprocessing
    """

    def __init__(self, base_path: str = "data"):
        """
        Initialize ArtifactManager.

        Args:
            base_path: Base directory for data storage (default: "data")
        """
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)

    async def create_run(
        self,
        project_id: str,
        project_name: str,
        action: str
    ) -> RunContext:
        """
        Create a new ingestion run directory and track in database.

        Generates timestamped directory with sequence number for concurrent runs.
        Format: data/{project}/{YYYYMMDD_HHmmss}_{seq}_{action}/

        Args:
            project_id: Project ID
            project_name: Project name (used for directory name)
            action: Action description (e.g., 'initial_ingest', 'github_sync')

        Returns:
            RunContext with paths to artifact directories
        """
        client = get_duckdb_client()
        run_id = str(uuid.uuid4())

        # Generate timestamp
        now = datetime.utcnow()
        timestamp = now.strftime("%Y%m%d_%H%M%S")

        # Get next sequence number for this timestamp
        sequence = await self._get_next_sequence(project_id, timestamp)

        # Create run context
        context = RunContext(
            run_id=run_id,
            project_id=project_id,
            project_name=project_name,
            timestamp=timestamp,
            sequence=sequence,
            action=action,
            base_path=self.base_path
        )

        # Create run directory
        context.run_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Created run directory: {context.run_dir}")

        # Track run in database
        await client.execute_write(
            """
            INSERT INTO runs (id, project_id, timestamp, sequence, action, status, created_at)
            VALUES (?, ?, ?, ?, ?, 'in_progress', current_timestamp)
            """,
            (run_id, project_id, timestamp, sequence, action)
        )

        logger.info(f"Created run {run_id} for project {project_id}")
        return context

    async def _get_next_sequence(self, project_id: str, timestamp: str) -> int:
        """
        Get next sequence number for runs with the same timestamp.

        Uses DuckDB macro for centralized sequence logic.

        Args:
            project_id: Project ID
            timestamp: Timestamp string (YYYYMMDD_HHmmss)

        Returns:
            Next sequence number (starting from 1)
        """
        client = get_duckdb_client()

        # Use DuckDB macro for sequence generation
        result = client.fetchone(
            "SELECT get_next_sequence(?, ?)",
            (project_id, timestamp)
        )

        return result[0] if result else 1

    def get_artifact_path(self, run_id: str, artifact_type: str) -> Optional[Path]:
        """
        Get path to artifact directory for a run, creating it if needed.

        Args:
            run_id: Run ID
            artifact_type: Artifact type ('raw_source', 'sql_embeddings', 'embeddings', 'graph_export')

        Returns:
            Path to artifact directory, or None if run not found
        """
        client = get_duckdb_client()

        # Get run metadata
        result = client.fetchone(
            """
            SELECT r.project_id, r.timestamp, r.sequence, r.action, p.name
            FROM runs r
            JOIN projects p ON r.project_id = p.id
            WHERE r.id = ?
            """,
            (run_id,)
        )

        if not result:
            logger.warning(f"Run not found: {run_id}")
            return None

        project_id, timestamp, sequence, action, project_name = result

        # Recreate run context
        context = RunContext(
            run_id=run_id,
            project_id=project_id,
            project_name=project_name,
            timestamp=timestamp,
            sequence=sequence,
            action=action,
            base_path=self.base_path
        )

        # Get artifact directory
        artifact_dir = context.get_artifact_dir(artifact_type)
        artifact_dir.mkdir(parents=True, exist_ok=True)

        return artifact_dir

    def list_runs(self, project_id: str, limit: int = 100) -> List[RunMetadata]:
        """
        List all runs for a project, ordered chronologically.

        Args:
            project_id: Project ID
            limit: Maximum number of runs to return

        Returns:
            List of RunMetadata objects
        """
        client = get_duckdb_client()

        results = client.fetchall(
            """
            SELECT id, project_id, timestamp, sequence, action, status,
                   created_at, completed_at, error_message
            FROM runs
            WHERE project_id = ?
            ORDER BY timestamp DESC, sequence DESC
            LIMIT ?
            """,
            (project_id, limit)
        )

        return [
            RunMetadata(
                run_id=row[0],
                project_id=row[1],
                timestamp=row[2],
                sequence=row[3],
                action=row[4],
                status=row[5],
                created_at=row[6].isoformat() if row[6] else None,
                completed_at=row[7].isoformat() if row[7] else None,
                error_message=row[8]
            )
            for row in results
        ]

    def get_run_metadata(self, run_id: str) -> Optional[RunMetadata]:
        """
        Get metadata for a specific run.

        Args:
            run_id: Run ID

        Returns:
            RunMetadata object or None if not found
        """
        client = get_duckdb_client()

        result = client.fetchone(
            """
            SELECT id, project_id, timestamp, sequence, action, status,
                   created_at, completed_at, error_message
            FROM runs
            WHERE id = ?
            """,
            (run_id,)
        )

        if not result:
            return None

        return RunMetadata(
            run_id=result[0],
            project_id=result[1],
            timestamp=result[2],
            sequence=result[3],
            action=result[4],
            status=result[5],
            created_at=result[6].isoformat() if result[6] else None,
            completed_at=result[7].isoformat() if result[7] else None,
            error_message=result[8]
        )

    async def complete_run(
        self,
        run_id: str,
        status: str = "completed",
        error_message: Optional[str] = None
    ) -> bool:
        """
        Mark a run as completed or failed.

        Args:
            run_id: Run ID
            status: Final status ('completed' or 'failed')
            error_message: Error message if status is 'failed'

        Returns:
            True if updated, False if run not found
        """
        client = get_duckdb_client()

        # Check run exists
        if not self.get_run_metadata(run_id):
            return False

        await client.execute_write(
            """
            UPDATE runs
            SET status = ?, completed_at = current_timestamp, error_message = ?
            WHERE id = ?
            """,
            (status, error_message, run_id)
        )

        logger.info(f"Run {run_id} marked as {status}")
        return True

    async def register_file(
        self,
        project_id: str,
        run_id: str,
        filename: str,
        file_path: Path
    ) -> Dict[str, any]:
        """
        Register a file in the files table with content hashing and deduplication.

        Uses DuckDB macros for duplicate detection and versioning logic.

        Args:
            project_id: Project ID
            run_id: Run ID
            filename: Original filename
            file_path: Full filesystem path to the file

        Returns:
            Dict with registration status:
            - status: 'duplicate' (skip processing), 'new_version', or 'new_file'
            - file_id: UUID of the file record
            - file_hash: SHA256 hash
            - message: Human-readable message
        """
        client = get_duckdb_client()

        # Compute content hash
        file_hash = self._compute_file_hash(file_path)
        file_size = file_path.stat().st_size

        # Check for identical content using DuckDB macro
        identical = client.fetchone(
            "SELECT * FROM find_duplicate_file(?, ?, ?)",
            (project_id, filename, file_hash)
        )

        if identical:
            logger.info(f"File {filename} has identical content (hash: {file_hash[:8]}...), skipping duplicate processing")
            return {
                'status': 'duplicate',
                'message': 'File content unchanged from previous version',
                'existing_run_id': identical[1],
                'existing_file_path': identical[2],
                'file_hash': file_hash,
                'skip_processing': True
            }

        # Check for previous versions using DuckDB macro
        previous = client.fetchone(
            "SELECT * FROM find_previous_file_version(?, ?)",
            (project_id, filename)
        )

        if previous:
            # Mark previous version as superseded
            await client.execute_write(
                """
                UPDATE files
                SET is_superseded = true, superseded_by = ?
                WHERE id = ?
                """,
                (run_id, previous[0])
            )
            logger.info(f"Superseded {filename} (old hash: {previous[2][:8]}..., new hash: {file_hash[:8]}...)")
            status = 'new_version'
        else:
            status = 'new_file'

        # Register new file version
        file_id = str(uuid.uuid4())
        await client.execute_write(
            """
            INSERT INTO files (id, project_id, run_id, filename, file_path, file_hash,
                               file_size_bytes, is_superseded, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, false, current_timestamp)
            """,
            (file_id, project_id, run_id, filename, str(file_path), file_hash, file_size)
        )

        logger.info(f"Registered {status} file: {filename} (hash: {file_hash[:8]}...)")
        return {
            'status': status,
            'message': f'New file version registered' if status == 'new_version' else 'New file registered',
            'file_id': file_id,
            'file_hash': file_hash,
            'file_size_bytes': file_size,
            'superseded_previous': previous is not None,
            'skip_processing': False
        }

    async def mark_file_processed(self, file_id: str) -> bool:
        """
        Mark a file as processed (LLM extraction completed).

        Args:
            file_id: File ID

        Returns:
            True if updated, False if file not found
        """
        client = get_duckdb_client()

        await client.execute_write(
            """
            UPDATE files
            SET processed_at = current_timestamp
            WHERE id = ?
            """,
            (file_id,)
        )

        logger.info(f"Marked file {file_id} as processed")
        return True

    def get_latest_file(self, project_id: str, filename: str) -> Optional[FileMetadata]:
        """
        Get the latest version of a file for a project.

        Args:
            project_id: Project ID
            filename: Filename to look up

        Returns:
            FileMetadata for the latest version, or None if not found
        """
        client = get_duckdb_client()

        result = client.fetchone(
            """
            SELECT id, project_id, run_id, filename, file_path, file_hash,
                   file_size_bytes, is_superseded, superseded_by, created_at, processed_at
            FROM files
            WHERE project_id = ? AND filename = ? AND is_superseded = false
            ORDER BY created_at DESC
            LIMIT 1
            """,
            (project_id, filename)
        )

        if not result:
            return None

        return FileMetadata(
            file_id=result[0],
            project_id=result[1],
            run_id=result[2],
            filename=result[3],
            file_path=result[4],
            file_hash=result[5],
            file_size_bytes=result[6],
            is_superseded=result[7],
            superseded_by=result[8],
            created_at=result[9].isoformat() if result[9] else None,
            processed_at=result[10].isoformat() if result[10] else None
        )

    def get_file_history(self, project_id: str, filename: str) -> List[FileMetadata]:
        """
        Get version history for a file.

        Args:
            project_id: Project ID
            filename: Filename to look up

        Returns:
            List of FileMetadata objects, ordered newest to oldest
        """
        client = get_duckdb_client()

        results = client.fetchall(
            """
            SELECT id, project_id, run_id, filename, file_path, file_hash,
                   file_size_bytes, is_superseded, superseded_by, created_at, processed_at
            FROM files
            WHERE project_id = ? AND filename = ?
            ORDER BY created_at DESC
            """,
            (project_id, filename)
        )

        return [
            FileMetadata(
                file_id=row[0],
                project_id=row[1],
                run_id=row[2],
                filename=row[3],
                file_path=row[4],
                file_hash=row[5],
                file_size_bytes=row[6],
                is_superseded=row[7],
                superseded_by=row[8],
                created_at=row[9].isoformat() if row[9] else None,
                processed_at=row[10].isoformat() if row[10] else None
            )
            for row in results
        ]

    @staticmethod
    def _compute_file_hash(file_path: Path) -> str:
        """
        Compute SHA256 hash of file content.

        Args:
            file_path: Path to file

        Returns:
            SHA256 hash as hex string (64 characters)
        """
        sha256 = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                sha256.update(chunk)
        return sha256.hexdigest()
