# Tasks: Improve Migration Visibility

## Phase 1: DuckDB Client Enhancements

- [ ] 1.1 Add `get_migration_status()` method to `DuckDBClient` class
  - Return current_version, latest_version, is_current
  - Return list of applied migrations with timestamps
  - Add error handling for uninitialized connection

- [ ] 1.2 Enhance migration logging in `_create_schema()` method
  - Add header banner before migration check
  - Log current version and target version
  - Log number of pending migrations
  - Log each migration completion
  - Add footer banner after all migrations

- [ ] 1.3 Add detailed docstrings to migration methods
  - Update `_migrate_to_v2()` docstring (WHAT/WHY/WHEN/CHANGES/RISK)
  - Update `_migrate_to_v3()` docstring
  - Update `_migrate_to_v4()` docstring
  - Include OpenSpec change reference in each

- [ ] 1.4 Update `_create_initial_schema()` docstring
  - Document v1 schema (projects, repositories, links)
  - Add WHAT/WHY/WHEN/CHANGES format

## Phase 2: Health Endpoint Integration

- [ ] 2.1 Locate health check endpoint (likely in `src/api/routers/admin.py`)
  - Find existing `/health` endpoint
  - Review current response structure

- [ ] 2.2 Add database migration status to health response
  - Import `get_duckdb_client` in health endpoint
  - Call `get_migration_status()` method
  - Add `database` section to health response
  - Include: schema_version, is_current, total_migrations, last_migration
  - Add error handling for database unavailability

- [ ] 2.3 Test health endpoint response
  - Verify database section included
  - Verify schema version reported correctly
  - Verify last_migration timestamp included

## Phase 3: Documentation

- [ ] 3.1 Create migration changelog document
  - Create `docs/migrations/` directory
  - Create `CHANGELOG.md` with all 4 migrations
  - Document version 1 (initial schema)
  - Document version 2 (project context)
  - Document version 3 (runs and files)
  - Document version 4 (upload settings)
  - Include OpenSpec change references

- [ ] 3.2 Update migration method comments
  - Add inline comments explaining complex SQL
  - Reference CHANGELOG.md in docstrings

- [ ] 3.3 Update deployment documentation (if exists)
  - Document new `/health` database section
  - Document how to check migration status
  - Add troubleshooting guide for migration issues

## Phase 4: Testing

- [ ] 4.1 Write unit tests for `get_migration_status()`
  - Test with fresh database (version 0)
  - Test with partial migrations (version 2)
  - Test with current database (version 4)
  - Test error handling (uninitialized connection)

- [ ] 4.2 Write integration tests for health endpoint
  - Test `/health` includes database section
  - Test database section structure
  - Test schema_version accuracy
  - Test is_current flag

- [ ] 4.3 Manual testing
  - Start fresh database, verify logs show migrations
  - Check `/health` endpoint for database status
  - Verify startup logs are clear and informative

## Phase 5: Code Review & Cleanup

- [ ] 5.1 Review all docstring additions
  - Ensure consistent format across all migrations
  - Verify OpenSpec change references are accurate
  - Check grammar and clarity

- [ ] 5.2 Review logging additions
  - Ensure logging is informative but not verbose
  - Verify log levels are appropriate (INFO for migrations)
  - Check banner formatting looks good in console

- [ ] 5.3 Update README if needed
  - Document migration visibility features
  - Add example health endpoint response

## Success Criteria

- ✅ `get_migration_status()` method returns complete migration info
- ✅ Health endpoint includes database migration status
- ✅ Startup logs clearly show migration progress with banners
- ✅ All migration methods have detailed WHAT/WHY/WHEN/CHANGES docstrings
- ✅ Migration changelog document created and complete
- ✅ Tests pass for status method and health endpoint
- ✅ No changes to automatic migration execution behavior
- ✅ No breaking changes to existing functionality

## Non-Goals

- ❌ Do NOT add API endpoints for migration control
- ❌ Do NOT add frontend migration UI
- ❌ Do NOT change automatic migration execution
- ❌ Do NOT extract migrations to separate SQL files
- ❌ Do NOT add migration runner class
- ❌ Keep existing automatic execution model unchanged

## Estimated Effort

- Phase 1: 1 hour (DuckDB client enhancements)
- Phase 2: 30 minutes (health endpoint integration)
- Phase 3: 30 minutes (documentation)
- Phase 4: 30 minutes (testing)
- Phase 5: 30 minutes (review)

**Total: 3 hours** (including buffer for testing and review)

## Implementation Order

1. **Start with Phase 1.1** - Add `get_migration_status()` method
2. **Then Phase 2** - Integrate with health endpoint (proves value immediately)
3. **Then Phase 1.3** - Add docstrings (improves code documentation)
4. **Then Phase 1.2** - Enhance logging (better startup visibility)
5. **Then Phase 3** - Create changelog (historical documentation)
6. **Finally Phase 4** - Add tests (ensure quality)

This order delivers value incrementally - health endpoint first, then documentation.
