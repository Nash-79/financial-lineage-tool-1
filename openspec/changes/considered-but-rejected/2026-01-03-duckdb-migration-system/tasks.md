# DuckDB Migration System - Tasks

## Phase 1: Migration Script Creation
- [ ] 1.1 Create `migrations/duckdb/` directory structure
- [ ] 1.2 Extract v1 schema to `001_initial_schema.sql`
- [ ] 1.3 Extract v2 migration to `002_add_project_context.sql`
- [ ] 1.4 Extract v3 migration to `003_add_runs_and_files.sql`
- [ ] 1.5 Extract v4 migration to `004_add_upload_settings.sql`
- [ ] 1.6 Add `schema_migrations` table creation to `001_initial_schema.sql`
- [ ] 1.7 Ensure all scripts use `IF NOT EXISTS` for idempotency

## Phase 2: Migration Runner Implementation
- [ ] 2.1 Create `src/storage/migrations.py` with `MigrationRunner` class
- [ ] 2.2 Implement `get_applied_migrations()` method
- [ ] 2.3 Implement `get_pending_migrations()` method
- [ ] 2.4 Implement `run_migrations()` method with transaction support
- [ ] 2.5 Implement `dry_run()` method for preview
- [ ] 2.6 Add migration validation (SQL syntax check)
- [ ] 2.7 Add detailed logging for each migration step

## Phase 3: API Endpoints
- [ ] 3.1 Add `POST /api/v1/admin/migrations/run` endpoint
- [ ] 3.2 Add `GET /api/v1/admin/migrations/status` endpoint
- [ ] 3.3 Add `POST /api/v1/admin/migrations/dry-run` endpoint
- [ ] 3.4 Add request/response models for migration endpoints
- [ ] 3.5 Add authentication/authorization for migration endpoints
- [ ] 3.6 Add rate limiting to prevent concurrent migrations

## Phase 4: DuckDB Client Updates
- [ ] 4.1 Remove `_migrate_to_v2()` method
- [ ] 4.2 Remove `_migrate_to_v3()` method
- [ ] 4.3 Remove `_migrate_to_v4()` method
- [ ] 4.4 Update `_create_schema()` to use `MigrationRunner`
- [ ] 4.5 Add backward compatibility check
- [ ] 4.6 Update initialization logic

## Phase 5: Frontend Migration UI
- [ ] 5.1 Create `src/pages/Migrations.tsx` component
- [ ] 5.2 Add migration status display
- [ ] 5.3 Add "Run Migrations" button with confirmation
- [ ] 5.4 Add dry-run preview functionality
- [ ] 5.5 Add migration history table
- [ ] 5.6 Add real-time progress updates (WebSocket)
- [ ] 5.7 Add navigation link in admin menu

## Phase 6: Testing
- [ ] 6.1 Write unit tests for `MigrationRunner`
- [ ] 6.2 Write integration tests for migration endpoints
- [ ] 6.3 Test fresh database migration (all migrations)
- [ ] 6.4 Test existing database migration (partial migrations)
- [ ] 6.5 Test idempotency (run migrations twice)
- [ ] 6.6 Test dry-run functionality
- [ ] 6.7 Test error handling and rollback

## Phase 7: Documentation
- [ ] 7.1 Update deployment documentation
- [ ] 7.2 Create migration authoring guide
- [ ] 7.3 Document API endpoints in OpenAPI spec
- [ ] 7.4 Add migration troubleshooting guide
- [ ] 7.5 Update README with migration instructions

## Success Criteria
- ✅ All 4 migrations extracted to SQL files
- ✅ Migrations are idempotent (can run multiple times)
- ✅ Migration state tracked in database
- ✅ API endpoints functional and tested
- ✅ Frontend UI allows triggering migrations
- ✅ Fresh database can be migrated from scratch
- ✅ Existing database can be migrated incrementally
- ✅ All tests passing

## Behavior Changes
- **Migration Execution**: Moves from automatic (on startup) to manual (via API/UI)
- **Migration Visibility**: SQL scripts are now visible in version control
- **Deployment Process**: Requires explicit migration step after deployment
- **Rollback**: Migrations can be reviewed before execution via dry-run
