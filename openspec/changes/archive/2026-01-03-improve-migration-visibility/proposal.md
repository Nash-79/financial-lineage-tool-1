# Proposal: Improve Migration Visibility

## Why

Currently, DuckDB schema migrations run automatically on startup and work reliably, but lack visibility:
- **No status endpoint**: Ops can't check which migrations have been applied
- **Limited logging**: Migration execution isn't clearly logged during startup
- **Sparse documentation**: Migration methods lack detailed context (what/why/when)
- **No health check integration**: Can't monitor schema version via standard health endpoint

This creates operational friction when:
- Debugging issues that might be schema-related
- Verifying deployments completed successfully
- Understanding what changed in each migration
- Monitoring database state via health checks

## What

Add lightweight visibility improvements to existing migration system **without changing the automatic execution model**.

**Key Changes**:
1. Add migration status to `/health` endpoint response
2. Add `get_migration_status()` method to DuckDB client
3. Enhance startup logging for migration execution
4. Add detailed docstring comments to each migration method
5. Create migration changelog document

**Total Effort**: ~2 hours (vs. 30+ hours for external migration system)

## Comparison to Rejected Proposal

This proposal is a **lightweight alternative** to the `duckdb-migration-system` proposal (now in `considered-but-rejected/`):

| Aspect | External Migration System (Rejected) | This Proposal (Lightweight) |
|--------|--------------------------------------|----------------------------|
| Execution Model | Manual via API/UI | Automatic on startup (unchanged) |
| Migration Files | Separate `.sql` files | Keep in Python (existing) |
| Complexity | 30 hours, 1000+ LOC | 2 hours, ~100 LOC |
| New Infrastructure | API endpoints, UI, runner class | None - enhance existing |
| Deployment Risk | High (manual steps) | None (no behavior change) |
| Visibility | Full audit UI | Health endpoint + logs |
| Maintenance | Ongoing | One-time enhancement |

**Philosophy**: Enhance what exists rather than rebuild from scratch.

## Proposed Changes

### Backend - DuckDB Client

#### [MODIFY] `src/storage/duckdb_client.py`

**1. Add migration status method** (lines after `_migrate_to_v4()`):
```python
def get_migration_status(self) -> Dict[str, Any]:
    """
    Get current database schema migration status.

    Returns:
        Dictionary containing:
        - current_version: Latest applied schema version
        - total_migrations: Total number of migrations applied
        - migrations: List of applied migrations with timestamps
        - is_current: Whether database is at latest version
    """
    if not self.conn:
        raise RuntimeError("DuckDB connection not initialized")

    result = self.conn.execute(
        "SELECT version, applied_at FROM schema_version ORDER BY version"
    ).fetchall()

    current_version = result[-1][0] if result else 0
    latest_version = 4  # Update when new migrations added

    return {
        "current_version": current_version,
        "latest_version": latest_version,
        "is_current": current_version == latest_version,
        "total_migrations": len(result),
        "migrations": [
            {
                "version": r[0],
                "applied_at": r[1].isoformat() if r[1] else None
            }
            for r in result
        ]
    }
```

**2. Enhance migration logging** (update `_create_schema()` method):
```python
# Before migrations start
logger.info("=" * 70)
logger.info("DATABASE SCHEMA MIGRATION CHECK")
logger.info(f"Current version: {current_version}")
logger.info(f"Target version: 4")
if current_version < 4:
    logger.info(f"Migrations to apply: {4 - current_version}")
else:
    logger.info("Schema is up-to-date")
logger.info("=" * 70)

# After each migration
logger.info(f"✓ Migration {current_version} → {current_version + 1} completed successfully")

# After all migrations
logger.info("=" * 70)
logger.info("DATABASE SCHEMA MIGRATION COMPLETE")
logger.info(f"Final version: {current_version}")
logger.info("=" * 70)
```

**3. Add detailed migration docstrings** (update each `_migrate_to_vX()` method):
```python
def _migrate_to_v2(self) -> None:
    """
    Migrate schema from v1 to v2: Add project context support.

    WHAT: Add context storage columns to projects table
    WHY: Enable storing structured context and uploaded context files
    WHEN: 2026-01-02 (add-user-prompt-context OpenSpec change)

    SCHEMA CHANGES:
    - ALTER TABLE projects ADD COLUMN context JSON
      Purpose: Store structured context data (JSON format)
    - ALTER TABLE projects ADD COLUMN context_file_path VARCHAR
      Purpose: Path to uploaded context file

    DATA MIGRATION: None (new columns, no existing data)
    ROLLBACK: Not needed (additive change only)
    RISK LEVEL: Low (adds columns with no constraints)
    AFFECTED FEATURES: Project context API endpoints
    """
    # ... existing migration code ...

def _migrate_to_v3(self) -> None:
    """
    Migrate schema from v2 to v3: Add artifact management system.

    WHAT: Create runs and files tables for hierarchical data organization
    WHY: Track ingestion runs and file versions with content hashing
    WHEN: 2026-01-02 (structure-data-outputs OpenSpec change)

    SCHEMA CHANGES:
    - CREATE TABLE runs
      Purpose: Track ingestion runs with timestamp/sequence/status
    - CREATE TABLE files
      Purpose: Track file versions with SHA256 hashing
    - CREATE INDEX idx_runs_project_timestamp
    - CREATE INDEX idx_files_project_filename
    - CREATE INDEX idx_files_hash
    - CREATE INDEX idx_files_project_hash
    - CREATE INDEX idx_files_run
    - CREATE MACRO get_next_sequence(proj_id, ts)
      Purpose: Get next sequence number for concurrent runs
    - CREATE MACRO find_duplicate_file(proj_id, fname, fhash)
      Purpose: Find duplicate files by content hash
    - CREATE MACRO find_previous_file_version(proj_id, fname)
      Purpose: Find previous version of a file for superseding

    DATA MIGRATION: None (new tables)
    ROLLBACK: Not needed (additive change only)
    RISK LEVEL: Medium (complex schema with indexes and macros)
    AFFECTED FEATURES: File upload, artifact management, deduplication
    """
    # ... existing migration code ...

def _migrate_to_v4(self) -> None:
    """
    Migrate schema from v3 to v4: Add persistent upload settings.

    WHAT: Create upload_settings table for configuration persistence
    WHY: Upload settings should survive server restarts
    WHEN: 2026-01-03 (persist-upload-settings OpenSpec change)

    SCHEMA CHANGES:
    - CREATE TABLE upload_settings
      - id: PRIMARY KEY (single row: 'default')
      - allowed_extensions: VARCHAR (JSON array stored as string)
      - max_file_size_mb: INTEGER (file size limit)
      - updated_at: TIMESTAMP (last modification time)
      - updated_by: VARCHAR (who made the change: api|system)

    DATA MIGRATION: None (new table, populated on first use)
    ROLLBACK: Not needed (additive change only)
    RISK LEVEL: Low (simple single-row table)
    AFFECTED FEATURES: File upload configuration API
    """
    # ... existing migration code ...
```

---

### Backend - Health Endpoint

#### [MODIFY] `src/api/routers/admin.py` (or wherever `/health` is defined)

Add database migration status to health check response:
```python
@router.get("/health")
async def health_check():
    """Health check endpoint with database migration status."""
    from src.storage.duckdb_client import get_duckdb_client

    # ... existing health checks ...

    # Add database migration status
    try:
        db = get_duckdb_client()
        migration_status = db.get_migration_status()
        database_status = {
            "schema_version": migration_status["current_version"],
            "is_current": migration_status["is_current"],
            "total_migrations": migration_status["total_migrations"],
            "last_migration": migration_status["migrations"][-1]["applied_at"] if migration_status["migrations"] else None
        }
    except Exception as e:
        logger.error(f"Failed to get migration status: {e}")
        database_status = {"error": str(e)}

    return {
        "status": overall_status,
        "services": {
            # ... existing services ...
        },
        "database": database_status,
        "timestamp": datetime.utcnow().isoformat()
    }
```

---

### Documentation

#### [NEW] `docs/migrations/CHANGELOG.md`

Create migration changelog document:
```markdown
# Database Schema Migration Changelog

This document tracks all DuckDB schema migrations applied to the system.

## Migration History

### Version 4 (2026-01-03)
**OpenSpec Change**: persist-upload-settings

**Changes**:
- Added `upload_settings` table for persistent file upload configuration
- Single-row table with id='default'
- Stores allowed_extensions (JSON), max_file_size_mb, updated_at, updated_by

**Affected Features**:
- `PUT /api/v1/files/config` - now persists to database
- `GET /api/v1/files/config` - loads from database
- Settings survive server restarts

**Risk**: Low (new table, no data migration)

---

### Version 3 (2026-01-02)
**OpenSpec Change**: structure-data-outputs

**Changes**:
- Added `runs` table for ingestion run tracking
- Added `files` table for file version management
- Added 5 indexes for performance
- Added 3 DuckDB macros for business logic

**Affected Features**:
- File upload with content hashing
- File deduplication
- File versioning and superseding

**Risk**: Medium (complex schema with foreign keys)

---

### Version 2 (2026-01-02)
**OpenSpec Change**: add-user-prompt-context

**Changes**:
- Added `context` column to projects table (JSON)
- Added `context_file_path` column to projects table (VARCHAR)

**Affected Features**:
- `GET /api/v1/projects/{project_id}/context`
- `PUT /api/v1/projects/{project_id}/context`
- `POST /api/v1/projects/{project_id}/context/upload`

**Risk**: Low (additive columns)

---

### Version 1 (Initial)
**OpenSpec Change**: Initial schema

**Changes**:
- Created `projects` table
- Created `repositories` table
- Created `links` table
- Created `schema_version` table

**Affected Features**: Core project management

**Risk**: N/A (initial creation)
```

---

## Verification Plan

### Manual Testing

1. **Health endpoint includes migration status**:
   ```bash
   curl http://localhost:8000/health | jq '.database'

   # Expected:
   {
     "schema_version": 4,
     "is_current": true,
     "total_migrations": 4,
     "last_migration": "2026-01-03T12:00:00"
   }
   ```

2. **Startup logs show migration progress**:
   ```bash
   docker logs lineage-api | grep -A10 "DATABASE SCHEMA MIGRATION"

   # Expected:
   ======================================================================
   DATABASE SCHEMA MIGRATION CHECK
   Current version: 4
   Target version: 4
   Schema is up-to-date
   ======================================================================
   ```

3. **Migration status method works**:
   ```python
   from src.storage.duckdb_client import get_duckdb_client
   db = get_duckdb_client()
   status = db.get_migration_status()
   print(status)

   # Expected:
   {
       "current_version": 4,
       "latest_version": 4,
       "is_current": True,
       "total_migrations": 4,
       "migrations": [...]
   }
   ```

### Automated Tests

```python
# tests/test_migration_visibility.py

def test_get_migration_status(db_client):
    """Test migration status reporting."""
    status = db_client.get_migration_status()

    assert "current_version" in status
    assert "latest_version" in status
    assert "is_current" in status
    assert "total_migrations" in status
    assert "migrations" in status
    assert isinstance(status["migrations"], list)

def test_health_endpoint_includes_database(client):
    """Test health endpoint includes database migration status."""
    response = client.get("/health")
    assert response.status_code == 200

    data = response.json()
    assert "database" in data
    assert "schema_version" in data["database"]
    assert "is_current" in data["database"]
```

---

## Impact Analysis

### Breaking Changes
**None** - This is purely additive:
- No changes to migration execution (still automatic)
- No changes to database schema
- No changes to API contracts (health endpoint extended)
- No changes to deployment process

### Benefits
- ✅ Ops can monitor schema version via `/health` endpoint
- ✅ Clear logging shows migration progress during startup
- ✅ Detailed docstrings explain what each migration does
- ✅ Migration changelog provides historical context
- ✅ Easier debugging of schema-related issues
- ✅ Better deployment verification

### Effort vs. Value
- **Effort**: 2 hours (code) + 30 min (documentation) = 2.5 hours total
- **Value**: High visibility with zero architectural changes
- **Maintenance**: None (one-time enhancement)
- **Risk**: None (no behavior changes)

---

## Success Criteria

- ✅ `/health` endpoint returns database migration status
- ✅ `get_migration_status()` method provides detailed migration info
- ✅ Startup logs clearly show migration execution progress
- ✅ All migration methods have detailed docstrings
- ✅ Migration changelog document created
- ✅ No changes to automatic migration execution
- ✅ No breaking changes to existing functionality
- ✅ Tests verify new status reporting

---

## Related Changes

- **Rejected**: `duckdb-migration-system` (considered-but-rejected/2026-01-03-duckdb-migration-system)
  - Why rejected: Too complex for current needs
  - This proposal: Lightweight alternative providing same visibility benefits
