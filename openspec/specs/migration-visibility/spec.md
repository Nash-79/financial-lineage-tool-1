# migration-visibility Specification

## Purpose
TBD - created by archiving change improve-migration-visibility. Update Purpose after archive.
## Requirements
### Requirement: Migration Status Reporting

System MUST provide programmatic access to database schema migration status.

#### Scenario: Getting migration status

- **WHEN** code calls `db_client.get_migration_status()`
- **THEN** method returns dictionary with migration information
- **AND** dictionary contains `current_version` (integer)
- **AND** dictionary contains `latest_version` (integer)
- **AND** dictionary contains `is_current` (boolean)
- **AND** dictionary contains `total_migrations` (integer)
- **AND** dictionary contains `migrations` (list of dicts)
- **AND** each migration dict contains `version` and `applied_at` timestamp

#### Scenario: Migration status in health check

- **WHEN** client requests GET `/health`
- **THEN** response includes `database` section
- **AND** database section contains `schema_version` (current version)
- **AND** database section contains `is_current` (boolean)
- **AND** database section contains `total_migrations` (count)
- **AND** database section contains `last_migration` (timestamp or null)

### Requirement: Migration Execution Logging

System MUST log migration execution progress during database initialization.

#### Scenario: Starting migration check

- **WHEN** database initializes and checks for pending migrations
- **THEN** system logs banner header "DATABASE SCHEMA MIGRATION CHECK"
- **AND** logs current schema version
- **AND** logs target schema version
- **AND** logs number of pending migrations (if any)
- **AND** logs "Schema is up-to-date" if no migrations needed

#### Scenario: Applying migrations

- **WHEN** system applies database migration
- **THEN** system logs migration version transition (e.g., "2 → 3")
- **AND** logs "completed successfully" for successful migration
- **AND** logs completion banner after all migrations

#### Scenario: Migration already current

- **WHEN** database schema is already at latest version
- **THEN** system logs "Schema is up-to-date"
- **AND** does not log individual migration steps
- **AND** logs completion banner

### Requirement: Migration Documentation

System MUST provide clear documentation of what each migration does.

#### Scenario: Reading migration method docstring

- **WHEN** developer reads migration method docstring
- **THEN** docstring contains "WHAT" section (what changes are made)
- **AND** docstring contains "WHY" section (why the change was needed)
- **AND** docstring contains "WHEN" section (date and OpenSpec change reference)
- **AND** docstring contains "SCHEMA CHANGES" section (detailed SQL changes)
- **AND** docstring contains "DATA MIGRATION" section (if data is transformed)
- **AND** docstring contains "ROLLBACK" section (rollback strategy or N/A)
- **AND** docstring contains "RISK LEVEL" section (Low/Medium/High)
- **AND** docstring contains "AFFECTED FEATURES" section (what features depend on this)

#### Scenario: Reading migration changelog

- **WHEN** developer reads `docs/migrations/CHANGELOG.md`
- **THEN** document lists all migrations in reverse chronological order
- **AND** each entry contains version number and date
- **AND** each entry contains OpenSpec change reference
- **AND** each entry contains summary of changes
- **AND** each entry contains affected features list
- **AND** each entry contains risk assessment

### Requirement: No Behavioral Changes

System MUST NOT change migration execution behavior.

#### Scenario: Automatic migration execution preserved

- **WHEN** application starts with pending migrations
- **THEN** migrations execute automatically (unchanged behavior)
- **AND** no manual intervention required
- **AND** no API calls needed to trigger migrations
- **AND** migrations run in same order as before

#### Scenario: Migration idempotency preserved

- **WHEN** migration runs multiple times
- **THEN** migration uses `CREATE TABLE IF NOT EXISTS` (unchanged)
- **AND** migration uses `ALTER TABLE ADD COLUMN IF NOT EXISTS` (unchanged)
- **AND** migration is safe to re-run (unchanged)

### Requirement: Error Handling

System MUST handle errors gracefully when reporting migration status.

#### Scenario: Database not initialized

- **WHEN** code calls `get_migration_status()` before database initialization
- **THEN** method raises `RuntimeError` with message "DuckDB connection not initialized"

#### Scenario: Health endpoint with database error

- **WHEN** health endpoint cannot get migration status (database unavailable)
- **THEN** response includes `database` section with `error` field
- **AND** error field contains error message string
- **AND** overall health status reflects degraded state
- **AND** HTTP status is still 200 OK (degraded, not failed)

---

