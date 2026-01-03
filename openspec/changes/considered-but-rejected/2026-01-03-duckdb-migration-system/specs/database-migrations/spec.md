# Spec Delta: Database Migrations

## NEW Capability: database-migrations

### Requirement: SQL Migration Scripts

System MUST provide version-controlled SQL migration scripts for DuckDB schema evolution.

#### Scenario: Listing migration files

- **WHEN** developer lists files in `migrations/duckdb/` directory
- **THEN** system shows migration files in numerical order
- **AND** each file follows naming pattern `{version}_{description}.sql`
- **AND** version numbers are zero-padded (001, 002, 003, etc.)

#### Scenario: Reading migration script

- **WHEN** migration runner reads SQL file from `migrations/duckdb/`
- **THEN** file contains valid DuckDB SQL statements
- **AND** all DDL statements use `IF NOT EXISTS` or `IF NOT EXISTS` clauses
- **AND** script is idempotent (can run multiple times safely)

### Requirement: Migration State Tracking

System MUST track which migrations have been applied to prevent re-execution.

#### Scenario: Checking applied migrations

- **WHEN** system queries `schema_migrations` table
- **THEN** table contains list of applied migration versions
- **AND** each row includes version, filename, applied_at timestamp
- **AND** table is created automatically if not exists

#### Scenario: Recording migration execution

- **WHEN** migration completes successfully
- **THEN** system inserts row into `schema_migrations` table
- **AND** row contains migration version and current timestamp
- **AND** transaction commits only if migration succeeds

### Requirement: Migration API Endpoints

System MUST provide API endpoints for migration management.

#### Scenario: Getting migration status

- **WHEN** client sends GET to `/api/v1/admin/migrations/status`
- **THEN** response contains list of applied migrations
- **AND** response contains list of pending migrations
- **AND** response includes total count and current schema version

#### Scenario: Running pending migrations

- **WHEN** client sends POST to `/api/v1/admin/migrations/run`
- **THEN** system executes pending migrations in order
- **AND** each migration runs in separate transaction
- **AND** execution stops on first error
- **AND** response includes success/failure status for each migration

#### Scenario: Dry-run preview

- **WHEN** client sends POST to `/api/v1/admin/migrations/dry-run`
- **THEN** system returns list of SQL statements that would execute
- **AND** no actual database changes are made
- **AND** response includes migration order and file contents
