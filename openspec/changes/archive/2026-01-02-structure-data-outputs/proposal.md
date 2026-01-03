# Change: Structured Data Directory

## Why

Currently, the `data/` directory contains a flat mix of database files, test SQL files, and the `contexts/` subdirectory. This unstructured layout makes it difficult to:

- Track which files belong to which ingestion action
- Debug failed ingestions (artifacts scattered)
- Understand the history of data processing runs
- Separate raw inputs from processed outputs

A hierarchical, project-based structure improves organization, enables artifact tracking, and provides clear historical context.

## What Changes

- **data-organization:** Add hierarchical directory structure `data/{project}/{run}/{artifact_type}/` for organizing ingestion artifacts by project and run.

Backend changes:
- Create `ArtifactManager` service for path generation and run tracking
- Add `runs` table to DuckDB for tracking run metadata
- Refactor DuckDB into modular structure (migrations/, procedures/, client separation)
- Implement stored procedures/macros for metadata operations and deduplication
- Update ingestion pipeline to use new directory structure
- Update graph exporters to store snapshots in run directories
- Create migration script to archive existing root-level files
- Implement backward compatibility resolver for legacy paths

## Impact

Affected specs:
- `data-organization` (added capability)
- `database-structure` (new spec delta - modular organization)

Affected code areas:
- Storage layer (new `artifact_manager.py`)
- Ingestion pipeline (`files.py`, `github.py`, `code_parser.py`)
- Graph export functionality
- DuckDB schema (add `runs` table)

Behavioral impact:
- New ingestions create timestamped run directories
- Existing data migrated to `data/archive/`
- Backward compatibility maintained for old paths

## Success Criteria

- All new ingestions create hierarchical directory structure
- Run directories are chronologically ordered
- Artifacts separated by type (raw, embeddings, exports)
- Legacy data migrated without loss
- Backward compatibility works for existing references
- Run metadata tracked in DuckDB
- No breaking changes to existing functionality

## Out of Scope (for this change)

- Retention policies or automatic cleanup (future enhancement)
- UI for browsing run history (separate change)
- Moving `contexts/` inside projects (keep separate for now)
- Artifact versioning (future enhancement)

## Requirements
- **Clean Data Folder**: Ensure `data` folder contains only structured subdirectories (except for the database file).
- **Hierarchical Structure**: `data/{ProjectName}/{Timestamp}_{seq}/{ArtifactType}/{Files}`
- **Artifact Types**:
    - `sql_embeddings`
    - `graph_export`
    - `embeddings`
    - `raw_source`
- **Ordered**: Folders should be ordered by creation time (enforced by timestamp prefix).
- **Modular Database Structure**: Organize DuckDB code following standard database project patterns:
    - `src/storage/db/client.py` - Connection management only
    - `src/storage/db/migrations/` - Version-specific schema migrations (v1, v2, v3, etc.)
    - `src/storage/db/procedures/` - Domain-organized stored procedures/macros (runs.py, files.py, etc.)
    - Separation of concerns between database logic and application logic
- **Database Best Practices**: Use DuckDB stored procedures and functions for metadata operations to ensure:
    - Proper deduplication logic (project names, file hashes, etc.)
    - Atomicity of complex operations (run creation + file registration)
    - Centralized business logic in the database layer
    - Consistent constraint enforcement
    - Better testability and maintainability

## Proposed Layout

```text
data/
  ├── AdventureworksLT/                  # Project Name
  │   ├── 20240102_001_initial_ingest/   # Action Timestamp + Sequence + Description
  │   │   ├── sql_embeddings/
  │   │   │   └── chunks.json
  │   │   ├── graph_export/
  │   │   │   └── lineage.graphml
  │   │   └── raw_source/
  │   │       └── script.sql
  │   └── 20240102_002_update_schema/
  │       └── ...
  ├── metadata.duckdb
  └── contexts/                          # Keep existing contexts dir? (Or move inside projects)
```

## Changes
1.  **Ingestion Logic (`ingest.py`)**:
    - Update to accept `project_name` (or resolve from ID).
    - Create timestamped run folder for each ingestion request.
    - Save intermediate artifacts (chunks, parsed results) into specific subfolders.
2.  **Export Logic**:
    - Ensure graph exports go to the project's run folder.
3.  **Cleanup**:
    - Move existing flat files (`.sql`, etc.) into an `archive` or specific project folder.

## Benefits
- Clear history of actions.
- Separation of concerns (embeddings vs graph).
- Easier debugging and visualization (frontend can read folder structure).
