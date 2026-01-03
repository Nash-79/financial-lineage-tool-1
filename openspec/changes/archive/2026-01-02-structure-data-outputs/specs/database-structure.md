# Spec Delta: Database Module Organization

## Category
database-structure

## Changes

### Add: Modular Database Code Organization

**Before:**
```
src/storage/
└── duckdb_client.py  (500+ lines, migrations + client + procedures)
```

**After:**
```
src/storage/db/
├── __init__.py
├── client.py                    # Connection management only
├── migrations/
│   ├── __init__.py
│   ├── v1_initial_schema.py    # Projects, repos, links tables
│   ├── v2_project_context.py   # Context columns
│   └── v3_artifact_tracking.py # Runs, files tables + procedures
└── procedures/
    ├── __init__.py
    ├── runs.py                  # Run management macros
    └── files.py                 # File deduplication macros
```

**Behavior:**
- Each migration is self-contained in its own module
- Stored procedures organized by domain (runs, files)
- Client only handles connection lifecycle
- Easier to test individual migrations
- Clear separation of schema versions

**Constraints:**
- Migration files must be numbered/ordered (v1, v2, v3, ...)
- Each migration must be idempotent (CREATE IF NOT EXISTS)
- Procedures must be documented with docstrings
- Client must dynamically load and execute migrations in order

## Rationale

Current `duckdb_client.py` mixes concerns:
- Connection management
- Schema migrations (3 versions)
- Migration logic
- Query helpers

This makes it:
- Hard to review individual migrations
- Difficult to add new procedures without touching migration code
- Unclear which version introduced what changes
- Hard to test migrations in isolation

Separating into modules follows standard database project structure and improves maintainability.
