# Design: Structured Data Directory

## Context

Currently, the `data/` directory contains a mix of database files, test SQL files, and the `contexts/` subdirectory. As the system grows, this flat structure becomes difficult to manage:

- No clear history of ingestion runs
- Artifacts from different projects are mixed
- Difficult to track which files belong to which ingestion action
- No separation between raw inputs and processed outputs

### Stakeholders
- Backend developers maintaining ingestion pipeline
- Users debugging ingestion issues
- Future frontend features that browse ingestion history

## Goals / Non-Goals

### Goals
- Hierarchical organization by project → run → artifact type
- Clear chronological ordering of ingestion runs
- Separation of artifact types (raw, embeddings, exports)
- Backward compatibility with existing code
- Migration path for existing data

### Non-Goals
- Changing database file location (stays in root)
- Versioning or retention policies (future enhancement)
- Automatic cleanup of old runs (future enhancement)
- UI for browsing run history (future enhancement)

## Decisions

### Decision 1: Hierarchical Directory Structure

**What**: Three-level hierarchy: `data/{project}/{run}/{artifact_type}/`

**Why**:
- Clear project isolation
- Chronological ordering via timestamp prefixes
- Easy to find artifacts for a specific run
- Supports multiple concurrent ingestions

**Structure**:
```
data/
├── {ProjectName}/                        # Project name (sanitized)
│   ├── {YYYYMMDD_HHmmss}_{seq}_{action}/   # Timestamped run
│   │   ├── raw_source/                   # Original uploaded files
│   │   ├── sql_embeddings/               # SQL chunk embeddings
│   │   ├── embeddings/                   # Other embeddings
│   │   └── graph_export/                 # Graph snapshots
│   └── {NextRun}/
├── metadata.duckdb                       # Database file (unchanged)
├── contexts/                             # Project contexts (unchanged)
└── archive/                              # Migrated legacy files
    └── {YYYYMMDD}/                       # Archive date
```

**Alternatives considered**:
- Flat structure with prefixes: Rejected - doesn't scale, hard to navigate
- Run ID as folder name: Rejected - not human-readable, no ordering
- Date-only prefix: Rejected - doesn't handle concurrent runs

### Decision 2: ArtifactManager Service

**What**: Centralized service class for path generation and artifact tracking.

**Why**:
- Single source of truth for path logic
- Easier to update path structure in future
- Handles directory creation atomically
- Can track run metadata in DuckDB

**API Design**:
```python
class ArtifactManager:
    def create_run(self, project_id: str, action: str) -> RunContext:
        """Create new run directory, return context with paths."""

    def get_artifact_path(self, run_id: str, artifact_type: str) -> Path:
        """Get path to artifact directory, create if needed."""

    def list_runs(self, project_id: str) -> List[RunMetadata]:
        """List all runs for a project, ordered by timestamp."""

    def get_run_metadata(self, run_id: str) -> RunMetadata:
        """Get metadata for a specific run."""
```

**Alternative**: Put path logic in each module - Rejected (duplication, inconsistency)

### Decision 6: File Deduplication via Versioning

**What**: Track file versions across runs, supersede old versions while preserving history.

**Why**:
- Users may re-upload the same filename (e.g., "AdventureworksLT.sql")
- Need to know which version is "current" for processing
- Historical versions valuable for debugging/rollback
- Avoid confusion from duplicate filenames

**Implementation Strategy**:

1. **Storage**: Keep all versions in separate run directories
   ```
   data/AdventureworksLT/
   ├── 20260102_153045_001_initial/
   │   └── raw_source/AdventureworksLT.sql  # v1
   ├── 20260103_091230_001_update/
   │   └── raw_source/AdventureworksLT.sql  # v2 (supersedes v1)
   ```

2. **Tracking**: Add `files` table to DuckDB
   ```sql
   CREATE TABLE files (
       id VARCHAR PRIMARY KEY,
       project_id VARCHAR,
       run_id VARCHAR,
       filename VARCHAR,        -- Original filename
       file_path VARCHAR,       -- Full path in filesystem
       file_hash VARCHAR(64),   -- SHA256 hash (64 hex chars) for content comparison
       file_size_bytes BIGINT,  -- File size for quick checks
       is_superseded BOOLEAN,   -- True if newer version exists
       superseded_by VARCHAR,   -- run_id that superseded this
       created_at TIMESTAMP,
       processed_at TIMESTAMP   -- When LLM processing completed (NULL if skipped)
   );

   -- Indexes for fast lookups
   CREATE INDEX idx_files_project_filename ON files(project_id, filename);
   CREATE INDEX idx_files_hash ON files(file_hash);  -- Fast duplicate detection
   CREATE INDEX idx_files_project_hash ON files(project_id, filename, file_hash);  -- Combined lookup
   ```

3. **DuckDB Macros for Business Logic**:

   To centralize business logic and improve maintainability, create DuckDB macros (stored functions):

   ```sql
   -- Get next sequence number for concurrent runs
   CREATE OR REPLACE MACRO get_next_sequence(proj_id, ts) AS (
       SELECT COALESCE(MAX(sequence), 0) + 1
       FROM runs
       WHERE project_id = proj_id AND timestamp = ts
   );

   -- Find duplicate file by content hash
   CREATE OR REPLACE MACRO find_duplicate_file(proj_id, fname, fhash) AS (
       SELECT id, run_id, file_path
       FROM files
       WHERE project_id = proj_id
         AND filename = fname
         AND file_hash = fhash
         AND is_superseded = false
       LIMIT 1
   );

   -- Find previous version of a file (for superseding)
   CREATE OR REPLACE MACRO find_previous_file_version(proj_id, fname) AS (
       SELECT id, run_id, file_hash
       FROM files
       WHERE project_id = proj_id
         AND filename = fname
         AND is_superseded = false
       LIMIT 1
   );
   ```

   **Benefits of DuckDB Macros**:
   - Centralized business logic in database layer
   - Better performance (database-side computation)
   - Enforces consistency across all callers
   - Easier to test and maintain
   - Can be called from any SQL query

4. **Content Hashing & Deduplication Logic**:
   ```python
   import hashlib

   def compute_file_hash(file_path: Path) -> str:
       """Compute SHA256 hash of file content."""
       sha256 = hashlib.sha256()
       with open(file_path, 'rb') as f:
           for chunk in iter(lambda: f.read(8192), b''):
               sha256.update(chunk)
       return sha256.hexdigest()

   def register_file(project_id: str, run_id: str, filename: str, file_path: Path):
       # Compute content hash
       file_hash = compute_file_hash(file_path)

       # Check for identical content using DuckDB macro
       identical = db.fetchone(
           "SELECT * FROM find_duplicate_file(?, ?, ?)",
           (project_id, filename, file_hash)
       )

       if identical:
           # Content is identical - skip processing, just reference existing
           logger.info(f"File {filename} has identical content (hash: {file_hash[:8]}...), skipping duplicate processing")
           return {
               'status': 'duplicate',
               'message': 'File content unchanged from previous version',
               'existing_run_id': identical['run_id'],
               'file_hash': file_hash,
               'skip_processing': True
           }

       # Mark previous versions as superseded using DuckDB macro
       previous = db.fetchone(
           "SELECT * FROM find_previous_file_version(?, ?)",
           (project_id, filename)
       )

       if previous:
           db.execute(
               "UPDATE files SET is_superseded = true, superseded_by = ? WHERE id = ?",
               (run_id, previous['id'])
           )
           logger.info(f"Superseded {filename} (old hash: {previous['file_hash'][:8]}..., new hash: {file_hash[:8]}...)")

       # Register new version
       file_id = str(uuid.uuid4())
       db.execute(
           """INSERT INTO files (id, project_id, run_id, filename, file_path, file_hash, file_size_bytes, is_superseded, created_at)
              VALUES (?, ?, ?, ?, ?, ?, ?, false, current_timestamp)""",
           (file_id, project_id, run_id, filename, str(file_path), file_hash, file_path.stat().st_size)
       )

       return {
           'status': 'new_version',
           'message': 'New file version registered',
           'file_id': file_id,
           'file_hash': file_hash,
           'superseded_previous': previous is not None,
           'skip_processing': False
       }
   ```

5. **Query Latest Version**:
   ```python
   def get_latest_file(project_id: str, filename: str) -> Optional[Path]:
       result = db.fetchone(
           """SELECT file_path FROM files
              WHERE project_id = ? AND filename = ? AND is_superseded = false
              ORDER BY created_at DESC LIMIT 1""",
           (project_id, filename)
       )
       return Path(result['file_path']) if result else None
   ```

**Benefits**:
- **True Content Deduplication**: SHA256 hash detects identical files even with re-uploads
- **Performance Optimization**: Skip expensive LLM processing if content unchanged
- **Clear Version Tracking**: Different content = new version, same content = reference existing
- **Integrity Verification**: Hash can detect file corruption
- **Smart Superseding**: Only supersede when content actually changes
- **Full History**: All versions preserved with hashes for comparison

**Content Deduplication Examples**:

| Scenario | File Hash | Action |
|----------|-----------|--------|
| Upload `schema.sql` (v1) | `abc123...` | Process normally, store hash |
| Re-upload `schema.sql` (identical) | `abc123...` | Skip processing, return existing |
| Upload `schema.sql` (modified) | `def456...` | Process as new version, supersede v1 |
| Upload `backup.sql` (copy of schema) | `abc123...` | Different filename → process separately |

**Alternative Considered**: Symlinks to "latest" version - Rejected (breaks on Windows, harder to manage)

### Decision 3: Run Directory Naming

**What**: `{YYYYMMDD_HHmmss}_{seq}_{action}/`

**Why**:
- Timestamp ensures chronological sorting
- Sequence number handles concurrent runs (same second)
- Action description makes runs identifiable
- Format is human-readable and filesystem-safe

**Examples**:
- `20260102_153045_001_initial_ingest/`
- `20260102_153045_002_schema_update/`
- `20260103_091230_001_github_sync/`

**Alternative**: UUID-based - Rejected (not sortable, not readable)

### Decision 4: Migration Strategy

**What**: Two-phase migration
1. Move existing root files to `archive/{date}/`
2. Update ingestion to use new structure (with backward compat)

**Why**:
- Preserves existing data
- Allows gradual adoption
- Can be rolled back if needed

**Migration Steps**:
```python
def migrate_legacy_data():
    1. Create archive directory: data/archive/{today}/
    2. Move *.sql files from data/ to archive/
    3. Keep metadata.duckdb in place
    4. Keep contexts/ in place
    5. Log migration to DuckDB
```

**Rollback**: Files can be moved back from archive if needed

### Decision 5: Backward Compatibility

**What**: Path resolver that supports both old and new structures.

**Why**:
- Existing code may reference old paths
- Gradual migration reduces risk
- Tests can run against both structures

**Implementation**:
```python
def resolve_artifact_path(reference: str) -> Path:
    """Try new structure first, fall back to old locations."""
    if new_path.exists():
        return new_path
    elif legacy_path.exists():
        logger.warning(f"Using legacy path: {legacy_path}")
        return legacy_path
    else:
        raise FileNotFoundError(f"Artifact not found: {reference}")
```

## Risks / Trade-offs

| Risk | Mitigation |
|------|------------|
| Breaking existing code paths | Implement path resolver with fallback |
| Migration corrupts data | Dry-run mode, backup before migration |
| Disk space increase (deeper nesting) | Minimal impact, metadata overhead is small |
| Concurrent write conflicts | Use sequence numbers, atomic directory creation |
| Long directory names | Limit action description to 50 chars |

## Migration Plan

### Phase 1: Implement ArtifactManager
1. Create `src/storage/artifact_manager.py`
2. Implement path generation logic
3. Add unit tests for path resolution
4. Add run metadata tracking in DuckDB

### Phase 2: Update Ingestion Pipeline
1. Update `src/api/routers/files.py` to use ArtifactManager
2. Update `src/api/routers/github.py` to use ArtifactManager
3. Update `src/ingestion/code_parser.py` to save to run directories
4. Add backward compatibility resolver

### Phase 3: Migrate Existing Data
1. Create migration script
2. Run dry-run validation
3. Execute migration (move files to archive)
4. Verify no broken references

### Phase 4: Update Graph Exports
1. Update graph export logic to use run directories
2. Test export retrieval

### Phase 5: Cleanup
1. Remove backward compatibility code (after verification)
2. Update documentation
3. Archive old path constants

**Rollback**: Keep migration script reversible for first 2 weeks after deployment.

## Open Questions

1. Should we track run metadata in DuckDB? (Recommend: **Yes**, add `runs` table) ✅ Decided
2. Should we track file versions in DuckDB? (Recommend: **Yes**, add `files` table) ✅ Decided
3. How to handle content-identical files? (Recommend: Use SHA256 hash, skip re-processing if hash matches)
4. How long should runs be retained? (Recommend: No limit for v1, add retention policy later)
5. Should contexts/ move inside projects? (Recommend: No, keep separate for now)
6. Add API to browse run history and file versions? (Recommend: Yes, but separate change)

## Performance Considerations

- Directory creation is fast (microseconds)
- Deep nesting has negligible performance impact
- Path resolution adds ~1ms overhead per artifact access
- Archive query scales with number of runs (needs indexing if >1000 runs)

## Success Metrics

- Zero data loss during migration
- All new ingestions use new structure
- Backward compatibility works for 100% of existing paths
- Run directories are human-readable and sortable
