# Change: Persist Upload Settings

## Why

Currently, file upload configuration (allowed extensions and file size limits) can be updated via `PUT /files/config`, but these changes are **runtime-only** and reset on server restart. The endpoint explicitly states: "Changes are runtime-only and will reset on server restart."

This creates problems:
1. **Configuration Loss**: Admin changes to upload settings are lost on restart/deployment
2. **Inconsistent State**: Settings can differ between restarts, causing confusion
3. **No Audit Trail**: No record of who changed settings or when
4. **Manual Reconfiguration**: Admins must re-apply settings after every restart

Users expect configuration changes made through the UI/API to persist across restarts.

## What Changes

Add persistent storage for file upload settings in DuckDB metadata:

1. **New `upload_settings` table** in DuckDB:
   - Stores allowed extensions, file size limits
   - Tracks who changed settings and when
   - Single-row table with current active settings

2. **Update `PUT /files/config` endpoint**:
   - Save settings to database after validation
   - Return confirmation of persistence
   - Add audit fields (updated_by, updated_at)

3. **Load settings on startup**:
   - Read from database on application initialization
   - Fall back to environment variables if no DB settings exist
   - Environment variables serve as defaults for first-time setup

4. **Add `GET /files/config/history` endpoint** (optional):
   - View history of configuration changes
   - Audit trail for compliance

## Impact

**Affected specs:**
- `api-endpoints` (modified - new persistence behavior for PUT /files/config)
- `data-organization` (modified - new upload_settings table)

**Affected code:**
- `src/api/routers/files.py` - Update config endpoint to persist
- `src/storage/duckdb_client.py` - Add upload_settings table migration
- `src/api/main_local.py` - Load settings from DB on startup

**Behavioral changes:**
- Settings persist across restarts ✅
- Settings changes are audited ✅
- Environment variables become defaults (not overrides)

**Backward compatibility:**
- First startup: Load from env vars, save to DB
- Subsequent startups: Load from DB
- Env vars still work for initial defaults

## Success Criteria

- [ ] Upload settings persist across server restarts
- [ ] PUT /files/config saves to database
- [ ] Settings loaded from database on startup
- [ ] Environment variables work as defaults
- [ ] Audit trail tracks changes (who, when)
- [ ] No breaking changes to existing upload functionality
