# Spec Delta: Data Organization - Upload Settings Table

## Category
data-organization

## ADDED Requirements

### Requirement: Upload settings MUST be stored in DuckDB metadata

File upload configuration (allowed extensions, file size limits) MUST be persisted in a dedicated DuckDB table to survive server restarts.

#### Scenario: Upload settings table schema

**Given** the database has been migrated to v4  
**When** querying the database schema  
**Then** an `upload_settings` table exists with columns:
- `id` (VARCHAR PRIMARY KEY)
- `allowed_extensions` (VARCHAR, JSON array as string)
- `max_file_size_mb` (INTEGER)
- `updated_at` (TIMESTAMP)
- `updated_by` (VARCHAR, nullable)

#### Scenario: Single-row constraint for upload settings

**Given** the `upload_settings` table exists  
**When** attempting to insert multiple rows  
**Then** only one row is maintained (latest settings)  
**And** previous settings are replaced, not appended

#### Scenario: Default settings initialization

**Given** the database is freshly initialized  
**When** the application starts for the first time  
**Then** a default row is inserted into `upload_settings` with:
- `allowed_extensions`: Value from `ALLOWED_FILE_EXTENSIONS` env var
- `max_file_size_mb`: Value from `UPLOAD_MAX_FILE_SIZE_MB` env var
- `updated_at`: Current timestamp
- `updated_by`: "system"

## Rationale

Storing upload settings in DuckDB provides:

1. **Persistence**: Settings survive container restarts and redeployments
2. **Consistency**: All metadata in one place (DuckDB)
3. **Simplicity**: No need for separate configuration database
4. **Audit Trail**: Timestamps track when settings changed

The single-row design ensures there's always one authoritative configuration, avoiding ambiguity about which settings are active.
