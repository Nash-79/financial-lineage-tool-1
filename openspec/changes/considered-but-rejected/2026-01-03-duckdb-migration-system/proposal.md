# DuckDB Migration System

## Why

Currently, DuckDB schema migrations are embedded in Python code (`src/storage/duckdb_client.py`), making them:
- **Hard to review**: SQL is scattered across Python methods
- **Not version-controlled separately**: Migrations are part of application code
- **Not reusable**: Can't run migrations independently or from other tools
- **Not transparent**: Deployment teams can't easily see what schema changes will be applied
- **Not frontend-accessible**: No way for admins to trigger migrations via UI

This creates operational friction during deployments and makes database schema evolution opaque.

## What

Extract DuckDB migrations from Python code into standalone, version-controlled SQL migration scripts with an API endpoint for execution.

**Key Changes:**
1. Create `migrations/duckdb/` directory with incremental SQL scripts
2. Implement migration runner that executes scripts in order
3. Add `POST /api/v1/admin/migrations/run` endpoint for frontend-triggered migrations
4. Make migrations re-runnable (idempotent) using `IF NOT EXISTS` and `IF NOT EXISTS` checks
5. Track migration state in `schema_migrations` table

## User Review Required

> [!IMPORTANT]
> **Breaking Change**: Migration logic moves from `duckdb_client.py` to SQL files
> - Existing deployments will need to run migrations via new API endpoint
> - Migration state tracking table will be created on first run

> [!WARNING]
> **Deployment Impact**: Requires coordination between backend deployment and migration execution
> - Migrations must be run after backend deployment
> - Frontend should check migration status before allowing operations

## Proposed Changes

### Backend - Migration Scripts

#### [NEW] `migrations/duckdb/001_initial_schema.sql`
Creates initial schema (v1): projects, repositories, links tables

#### [NEW] `migrations/duckdb/002_add_project_context.sql`
Adds context columns to projects table (v2 migration)

#### [NEW] `migrations/duckdb/003_add_runs_and_files.sql`
Creates runs and files tables with indexes and macros (v3 migration)

#### [NEW] `migrations/duckdb/004_add_upload_settings.sql`
Creates upload_settings table (v4 migration)

---

### Backend - Migration Runner

#### [NEW] `src/storage/migrations.py`
Migration runner that:
- Reads SQL files from `migrations/duckdb/` directory
- Tracks applied migrations in `schema_migrations` table
- Executes migrations in numerical order
- Supports dry-run mode
- Returns detailed migration status

---

### Backend - API Endpoint

#### [MODIFY] `src/api/routers/admin.py`
Add migration endpoints:
- `POST /api/v1/admin/migrations/run` - Execute pending migrations
- `GET /api/v1/admin/migrations/status` - Check migration state
- `POST /api/v1/admin/migrations/dry-run` - Preview pending migrations

---

### Backend - DuckDB Client

#### [MODIFY] `src/storage/duckdb_client.py`
- Remove migration methods (`_migrate_to_v2`, `_migrate_to_v3`, `_migrate_to_v4`)
- Keep `_create_initial_schema` for backward compatibility
- Update `_create_schema` to use migration runner

---

### Frontend - Migration UI

#### [NEW] `src/pages/Migrations.tsx`
Admin page for:
- Viewing migration status
- Running pending migrations
- Viewing migration history
- Dry-run preview

---

## Verification Plan

### Automated Tests
```bash
# Test migration runner
pytest tests/test_migrations.py

# Test API endpoints
pytest tests/test_admin_migrations.py

# Test idempotency (run migrations twice)
pytest tests/test_migration_idempotency.py
```

### Manual Verification
1. Fresh database: Run all migrations from scratch
2. Existing database: Run migrations on database with existing schema
3. Frontend: Trigger migrations via admin UI
4. Dry-run: Preview migrations without applying
5. Re-run: Verify migrations are idempotent
