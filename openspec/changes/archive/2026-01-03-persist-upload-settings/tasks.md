# Implementation Tasks: Persist Upload Settings

## Phase 1: Database Schema

- [ ] 1.1 Create DuckDB migration for `upload_settings` table
  - Add `id` (primary key)
  - Add `allowed_extensions` (JSON array)
  - Add `max_file_size_mb` (integer)
  - Add `updated_at` (timestamp)
  - Add `updated_by` (varchar, optional for future auth)
  - Single-row table (enforce with CHECK or application logic)

- [ ] 1.2 Add migration to `src/storage/duckdb_client.py`
  - Create `_migrate_to_v4()` method
  - Call from `_run_migrations()`
  - Log migration completion

## Phase 2: Settings Persistence Logic

- [ ] 2.1 Create `UploadSettingsStore` class in `src/storage/upload_settings.py`
  - `get_settings()` - Load from database
  - `save_settings(extensions, max_size)` - Persist to database
  - `get_or_create_default()` - Load from DB or create from env vars

- [ ] 2.2 Update `PUT /files/config` endpoint in `src/api/routers/files.py`
  - Call `UploadSettingsStore.save_settings()` after validation
  - Return confirmation that settings were persisted
  - Add error handling for database failures

- [ ] 2.3 Load settings on startup in `src/api/main_local.py`
  - Call `UploadSettingsStore.get_or_create_default()` on app startup
  - Override `config.ALLOWED_FILE_EXTENSIONS` and `config.UPLOAD_MAX_FILE_SIZE_MB`
  - Log loaded settings

## Phase 3: API Updates

- [ ] 3.1 Update `GET /files/config` response
  - Add `persisted: true` field
  - Add `last_updated` timestamp
  - Add `source: "database"` or `source: "environment"`

- [ ] 3.2 (Optional) Add `GET /files/config/history` endpoint
  - Return history of configuration changes
  - Include timestamps and change details
  - Limit to last 50 changes

## Phase 4: Testing

- [ ] 4.1 Write unit tests for `UploadSettingsStore`
  - Test `get_settings()` with no data
  - Test `save_settings()` persistence
  - Test `get_or_create_default()` fallback to env vars

- [ ] 4.2 Write integration tests
  - Test PUT /files/config persists settings
  - Test settings survive server restart
  - Test env vars work as defaults on first run

- [ ] 4.3 Manual testing
  - Update settings via PUT /files/config
  - Restart server
  - Verify settings persisted

## Phase 5: Documentation

- [ ] 5.1 Update API documentation
  - Document new persistence behavior
  - Document that env vars are defaults
  - Add migration notes

- [ ] 5.2 Update deployment docs
  - Explain settings precedence (DB > env vars)
  - Document how to reset to defaults

## Success Criteria

- [ ] Settings persist across server restarts
- [ ] PUT /files/config saves to database
- [ ] Settings loaded from database on startup
- [ ] Environment variables work as defaults
- [ ] Tests verify persistence behavior
- [ ] No breaking changes to upload functionality
