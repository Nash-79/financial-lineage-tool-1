"""
Files router for file upload and management.

Provides endpoints for uploading files with project scoping.
"""

import logging
import json
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from pydantic import BaseModel

from src.storage import ArtifactManager
from src.storage.metadata_store import ProjectStore, RepositoryStore
from src.storage.upload_settings import UploadSettingsStore
from src.services.ingestion_tracker import get_tracker, FileStatus
from src.config.sql_dialects import validate_dialect
from ..config import config

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/files", tags=["files"])

# Store instances
project_store = ProjectStore()
repository_store = RepositoryStore()
artifact_manager = ArtifactManager(base_path="data")

# Maximum file size (50MB by default)
MAX_FILE_SIZE = config.UPLOAD_MAX_FILE_SIZE_MB * 1024 * 1024


class UploadConfigUpdate(BaseModel):
    """Request model for updating upload configuration."""
    allowed_extensions: Optional[List[str]] = None
    max_file_size_mb: Optional[int] = None


def get_allowed_extensions() -> set:
    """Get allowed file extensions from config."""
    return set(ext.strip() for ext in config.ALLOWED_FILE_EXTENSIONS)


def get_app_state() -> Any:
    """Get application state from FastAPI app."""
    from ..main_local import state
    return state


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename to prevent path traversal attacks.

    Args:
        filename: Original filename

    Returns:
        Sanitized filename
    """
    # Remove path components
    filename = os.path.basename(filename)

    # Replace suspicious characters
    filename = re.sub(r'[^\w\-_\.]', '_', filename)

    # Remove leading dots (hidden files)
    filename = filename.lstrip('.')

    # Ensure we have a valid filename
    if not filename:
        filename = "unnamed_file"

    return filename


def validate_file_extension(filename: str) -> bool:
    """Check if file extension is allowed."""
    ext = Path(filename).suffix.lower()
    return ext in get_allowed_extensions()


@router.post("/upload")
async def upload_files(
    files: List[UploadFile] = File(..., description="Files to upload"),
    project_id: str = Form(..., description="Project ID (required)"),
    repository_id: Optional[str] = Form(None, description="Repository ID (optional, creates new if omitted)"),
    repository_name: Optional[str] = Form(None, description="Repository name (required if repository_id omitted)"),
    instructions: Optional[str] = Form(None, description="Optional instructions for lineage extraction"),
    dialect: Optional[str] = Form("auto", description="SQL dialect for parsing"),
) -> Dict[str, Any]:
    """
    Upload files for ingestion with project scoping.

    Files are validated, sanitized, and saved to hierarchical run directory.
    Then they are processed for lineage extraction and tagged with
    project_id and repository_id.

    Args:
        files: List of files to upload
        project_id: Parent project ID (required)
        repository_id: Existing repository ID (optional)
        repository_name: Name for new repository (required if repository_id not provided)

    Returns:
        Dictionary with upload results for each file including run_id
    """
    # Validate project exists
    project = project_store.get(project_id)
    if not project:
        raise HTTPException(status_code=404, detail=f"Project not found: {project_id}")

    dialect_value = (dialect or "auto").strip()
    if not validate_dialect(dialect_value):
        raise HTTPException(status_code=400, detail=f"Unsupported SQL dialect: {dialect_value}")

    # Get or create repository
    if repository_id:
        repo = repository_store.get(repository_id)
        if not repo:
            raise HTTPException(status_code=404, detail=f"Repository not found: {repository_id}")
        if repo["project_id"] != project_id:
            raise HTTPException(
                status_code=400,
                detail=f"Repository {repository_id} does not belong to project {project_id}"
            )
    else:
        # Create new repository
        if not repository_name:
            raise HTTPException(
                status_code=400,
                detail="repository_name is required when repository_id is not provided"
            )
        repo = await repository_store.create(
            project_id=project_id,
            name=repository_name,
            source="upload",
            source_ref=f"upload/{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
        )
        repository_id = repo["id"]
        logger.info(f"Created repository {repository_id} for upload")

    # Create ingestion run for this upload batch
    action_name = repository_name or repo["name"] or "file_upload"
    run_context = await artifact_manager.create_run(
        project_id=project_id,
        project_name=project["name"],
        action=f"upload_{action_name}"
    )

    tracker = get_tracker()
    file_paths = [upload_file.filename for upload_file in files]
    session = await tracker.start_session(
        source="upload",
        project_id=project_id,
        repository_id=repository_id,
        file_paths=file_paths,
    )

    # Save instructions if provided
    if instructions:
        instructions_file = run_context.run_dir / "instructions.md"
        with open(instructions_file, "w", encoding="utf-8") as f:
            f.write(f"# Upload Instructions\n\n{instructions}\n")
        logger.info(f"Saved upload instructions to {instructions_file}")

    # Get raw_source directory for this run
    raw_source_dir = run_context.get_artifact_dir("raw_source")
    raw_source_dir.mkdir(parents=True, exist_ok=True)


    # Process each file
    results = []
    total_nodes_created = 0
    files_processed = 0
    files_failed = 0
    files_skipped_duplicate = 0

    for upload_file in files:
        file_result = {
            "filename": upload_file.filename,
            "status": "pending",
            "error": None,
            "nodes_created": 0,
            "saved_path": None,
        }

        try:
            # Validate file extension
            if not validate_file_extension(upload_file.filename):
                file_result["status"] = "error"
                file_result["error"] = f"Unsupported file type. Allowed: {', '.join(get_allowed_extensions())}"
                files_failed += 1
                await tracker.file_error(
                    session.ingestion_id,
                    upload_file.filename,
                    file_result["error"],
                )
                results.append(file_result)
                continue

            # Read file content
            content = await upload_file.read()

            # Validate file size
            if len(content) > MAX_FILE_SIZE:
                file_result["status"] = "error"
                file_result["error"] = f"File too large. Maximum size: {config.UPLOAD_MAX_FILE_SIZE_MB}MB"
                files_failed += 1
                await tracker.file_error(
                    session.ingestion_id,
                    upload_file.filename,
                    file_result["error"],
                )
                results.append(file_result)
                continue

            # Sanitize filename - keep original name for versioning
            safe_filename = sanitize_filename(upload_file.filename)
            file_path = raw_source_dir / safe_filename

            # Save file to run directory
            with open(file_path, "wb") as f:
                f.write(content)

            file_result["saved_path"] = str(file_path)
            logger.info(f"Saved uploaded file: {file_path}")

            # Register file with content hashing and deduplication
            registration = await artifact_manager.register_file(
                project_id=project_id,
                run_id=run_context.run_id,
                filename=safe_filename,
                file_path=file_path
            )

            file_result["file_hash"] = registration["file_hash"]
            file_result["file_status"] = registration["status"]

            # Check if this is a duplicate (same content)
            if registration["skip_processing"]:
                logger.info(f"Skipping processing for duplicate file: {safe_filename}")
                file_result["status"] = "skipped_duplicate"
                file_result["message"] = registration["message"]
                files_skipped_duplicate += 1
                await tracker.file_skipped(
                    session.ingestion_id,
                    upload_file.filename,
                    reason="duplicate",
                )
                results.append(file_result)
                continue

            # Process file for lineage extraction
            state = get_app_state()
            nodes_created = 0

            if state.parser and state.extractor:
                try:
                    # Parse file
                    ext = Path(upload_file.filename).suffix.lower()
                    await tracker.update_file_status(
                        session.ingestion_id,
                        upload_file.filename,
                        FileStatus.PARSING,
                    )
                    if ext in {".sql", ".ddl"}:
                        await tracker.update_file_status(
                            session.ingestion_id,
                            upload_file.filename,
                            FileStatus.EXTRACTING,
                        )
                        content_str = content.decode("utf-8")
                        nodes_created = state.extractor.ingest_sql_lineage(
                            sql_content=content_str,
                            dialect=dialect_value,
                            source_file=str(file_path),
                            project_id=project_id,
                            repository_id=repository_id,
                            source="upload",
                        ) or 0
                        state.extractor.flush_batch()
                    else:
                        await tracker.update_file_status(
                            session.ingestion_id,
                            upload_file.filename,
                            FileStatus.COMPLETE,
                        )

                except Exception as e:
                    logger.warning(f"Failed to extract lineage from {upload_file.filename}: {e}")
                    file_result["status"] = "error"
                    file_result["error"] = str(e)
                    files_failed += 1
                    await tracker.file_error(
                        session.ingestion_id,
                        upload_file.filename,
                        str(e),
                    )
                    results.append(file_result)
                    continue

            # Mark file as processed in artifact manager
            if registration.get("file_id"):
                await artifact_manager.mark_file_processed(registration["file_id"])

            file_result["status"] = "processed"
            file_result["nodes_created"] = nodes_created
            total_nodes_created += nodes_created
            files_processed += 1
            await tracker.file_complete(
                session.ingestion_id,
                upload_file.filename,
                nodes_created,
            )

        except Exception as e:
            logger.error(f"Failed to process file {upload_file.filename}: {e}")
            file_result["status"] = "error"
            file_result["error"] = str(e)
            files_failed += 1
            await tracker.file_error(
                session.ingestion_id,
                upload_file.filename,
                str(e),
            )

        results.append(file_result)

    # Update repository counts
    try:
        await repository_store.update_counts(
            repo_id=repository_id,
            file_count=(repo.get("file_count", 0) or 0) + files_processed,
            node_count=(repo.get("node_count", 0) or 0) + total_nodes_created,
        )
    except Exception as e:
        logger.warning(f"Failed to update repository counts: {e}")

    # Mark run as completed
    run_status = "completed" if files_failed == 0 else "completed_with_errors"
    await artifact_manager.complete_run(
        run_id=run_context.run_id,
        status=run_status,
        error_message=f"{files_failed} files failed" if files_failed > 0 else None
    )
    await tracker.complete_session(session.ingestion_id)

    return {
        "project_id": project_id,
        "repository_id": repository_id,
        "ingestion_id": session.ingestion_id,
        "run_id": run_context.run_id,
        "run_dir": str(run_context.run_dir),
        "files_processed": files_processed,
        "files_failed": files_failed,
        "files_skipped_duplicate": files_skipped_duplicate,
        "total_nodes_created": total_nodes_created,
        "results": results,
    }


@router.get("/config")
async def get_upload_config() -> Dict[str, Any]:
    """
    Get file upload configuration.

    Returns current settings for allowed file extensions and size limits.
    Frontend can use this to display/validate before upload.
    """
    # Try to load settings from database
    settings_store = UploadSettingsStore()
    db_settings = settings_store.get_settings()
    
    if db_settings:
        # Settings loaded from database
        extensions = json.loads(db_settings["allowed_extensions"])
        return {
            "allowed_extensions": extensions,
            "max_file_size_mb": db_settings["max_file_size_mb"],
            "max_file_size_bytes": db_settings["max_file_size_mb"] * 1024 * 1024,
            "upload_directory": config.UPLOAD_BASE_DIR,
            "persisted": True,
            "last_updated": db_settings["updated_at"],
            "source": "database",
        }
    else:
        # Fallback to config (environment variables)
        return {
            "allowed_extensions": list(get_allowed_extensions()),
            "max_file_size_mb": config.UPLOAD_MAX_FILE_SIZE_MB,
            "max_file_size_bytes": MAX_FILE_SIZE,
            "upload_directory": config.UPLOAD_BASE_DIR,
            "persisted": False,
            "last_updated": None,
            "source": "environment",
        }


@router.put("/config")
async def update_upload_config(
    config_update: UploadConfigUpdate,
) -> Dict[str, Any]:
    """
    Update file upload configuration.

    Settings are persisted to database and survive server restarts.

    Args:
        config_update: Upload configuration updates (allowed_extensions, max_file_size_mb)

    Returns:
        Updated configuration with persistence confirmation
    """
    global MAX_FILE_SIZE

    # Get current settings
    current_extensions = list(get_allowed_extensions())
    current_size = config.UPLOAD_MAX_FILE_SIZE_MB

    # Validate and update extensions
    if config_update.allowed_extensions is not None:
        allowed_extensions = config_update.allowed_extensions
        validated = []
        for ext in allowed_extensions:
            ext = ext.strip().lower()
            if not ext.startswith("."):
                ext = "." + ext
            validated.append(ext)
        current_extensions = validated
        config.ALLOWED_FILE_EXTENSIONS = validated
        logger.info(f"Updated allowed extensions: {validated}")

    # Validate and update file size
    if config_update.max_file_size_mb is not None:
        max_file_size_mb = config_update.max_file_size_mb
        if max_file_size_mb < 1 or max_file_size_mb > 500:
            raise HTTPException(
                status_code=400,
                detail="max_file_size_mb must be between 1 and 500"
            )
        current_size = max_file_size_mb
        config.UPLOAD_MAX_FILE_SIZE_MB = max_file_size_mb
        MAX_FILE_SIZE = max_file_size_mb * 1024 * 1024
        logger.info(f"Updated max file size: {max_file_size_mb}MB")

    # Persist to database
    settings_store = UploadSettingsStore()
    success = await settings_store.save_settings(
        allowed_extensions=current_extensions,
        max_file_size_mb=current_size,
        updated_by="api"
    )

    if not success:
        logger.error("Failed to persist upload settings to database")
        raise HTTPException(
            status_code=500,
            detail="Failed to persist settings to database"
        )

    return await get_upload_config()
