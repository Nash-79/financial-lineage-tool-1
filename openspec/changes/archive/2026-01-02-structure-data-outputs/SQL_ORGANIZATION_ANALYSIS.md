# SQL Organization Analysis

## Question

Should we refactor DuckDB schema code into separate folders like `tables/`, `procedures/`, `macros/`, and `functions/` to simplify maintenance?

## Current Structure

```
src/storage/
├── duckdb_client.py       # All schema, migrations, and macros inline (~400 lines)
├── artifact_manager.py    # Business logic using the macros
└── metadata_store.py      # Project/repository stores
```

**Current Approach**: All SQL migrations and macros are defined inline within `duckdb_client.py` in the `_migrate_to_v3()` method.

## Proposed Alternative Structure

```
src/storage/db/
├── __init__.py
├── client.py              # Connection management only
├── migrations/
│   ├── v1_initial_schema.sql
│   ├── v2_project_context.sql
│   └── v3_artifact_tracking.sql
└── macros/
    ├── runs_macros.sql    # get_next_sequence
    └── files_macros.sql   # find_duplicate_file, find_previous_file_version
```

## Analysis

### Option A: Separate SQL Files (Proposed)

**Pros:**
- ✅ **Better IDE Support**: Syntax highlighting, autocomplete for SQL
- ✅ **Easier Code Review**: Diffs show pure SQL changes without Python context
- ✅ **Testable SQL**: Can test SQL separately with DuckDB CLI
- ✅ **Version Control**: Clear history of schema changes
- ✅ **Reusability**: SQL files can be executed directly for manual migrations
- ✅ **Scalability**: Works better when schema grows beyond 10 migrations

**Cons:**
- ❌ **File Management Overhead**: More files to maintain
- ❌ **Loading Logic Required**: Need code to read/execute SQL files
- ❌ **Debugging Complexity**: Stack traces less clear (file I/O involved)
- ❌ **Deployment**: Must ensure SQL files packaged correctly
- ❌ **Migration Order**: Need explicit ordering mechanism (filename prefixes)

**Implementation Sketch:**
```python
# client.py
from pathlib import Path

class DuckDBClient:
    def _run_migrations(self):
        migrations_dir = Path(__file__).parent / "migrations"
        for migration_file in sorted(migrations_dir.glob("v*.sql")):
            version = int(migration_file.stem[1])  # Extract version number
            if version > current_version:
                sql = migration_file.read_text()
                self.conn.execute(sql)
```

### Option B: Keep Current Inline Structure (Current Choice)

**Pros:**
- ✅ **Simplicity**: Everything in one file, easy to navigate
- ✅ **Debuggability**: Clear stack traces, easy to step through
- ✅ **No File I/O**: Faster, no risk of missing files
- ✅ **Explicit Migration Sequence**: Clear `if current_version == X` logic
- ✅ **Atomic**: Migration code and execution logic together
- ✅ **Python Integration**: Can use f-strings, variables in SQL easily

**Cons:**
- ❌ **File Length**: Can become unwieldy (currently ~400 lines, manageable)
- ❌ **SQL Highlighting**: Less ideal in Python strings
- ❌ **Mixing Concerns**: SQL and Python logic in same file

**Current File Length**: ~400 lines total, ~220 lines of schema/migrations

### Option C: Hybrid Approach

**Structure:**
```
src/storage/
├── duckdb_client.py       # Connection + migration orchestration
├── schema/
│   ├── __init__.py
│   ├── v1_schema.py       # Python module with SQL constants
│   ├── v2_schema.py
│   └── v3_schema.py
```

**Example:**
```python
# schema/v3_schema.py
RUNS_TABLE = """
CREATE TABLE IF NOT EXISTS runs (
    id VARCHAR PRIMARY KEY,
    project_id VARCHAR NOT NULL,
    ...
)
"""

MACROS = {
    "get_next_sequence": """
        CREATE OR REPLACE MACRO get_next_sequence(proj_id, ts) AS (...)
    """,
    "find_duplicate_file": """..."""
}

# duckdb_client.py
from .schema import v3_schema

def _migrate_to_v3(self):
    self.conn.execute(v3_schema.RUNS_TABLE)
    for macro_name, macro_sql in v3_schema.MACROS.items():
        self.conn.execute(macro_sql)
```

**Pros:**
- ✅ Organized SQL as Python constants (syntax highlighting via triple quotes)
- ✅ No file I/O overhead
- ✅ Easy to import and reference
- ✅ Modular without filesystem complexity

**Cons:**
- ❌ Still mixing SQL and Python (but more organized)
- ❌ More files than current approach

## Recommendation

### **For Current Project Size: Keep Option B (Current Structure)**

**Reasoning:**
1. **Schema is not large yet**: 3 migrations, 3 macros (~220 lines SQL)
2. **No pain points**: Current structure is working well
3. **Premature optimization**: Refactoring adds complexity without immediate benefit
4. **Easy to change later**: Can refactor when needed

### **When to Switch to Option A or C:**

**Trigger Points:**
- Schema exceeds 500 lines
- More than 10 migrations
- Team requests better SQL tooling
- Need to share SQL with non-Python tools
- Difficulty finding specific schema code

**Recommended Next Step:**
If schema grows significantly, **Option C (Hybrid)** is the best middle ground:
- Keeps Python context
- Organizes SQL logically
- No file I/O overhead
- Easy migration from current structure

## Implementation Effort

| Option | Effort | Risk |
|--------|--------|------|
| **Keep Current (B)** | 0 hours | None |
| **Hybrid (C)** | 2-3 hours | Low (pure refactor) |
| **Separate Files (A)** | 4-6 hours | Medium (file loading, packaging) |

## Decision

**Status**: ✅ **Keep current structure (Option B)**

**Rationale**: No immediate benefit outweighs the simplicity of current approach. Will revisit when schema complexity increases.

**Future Path**: If refactoring becomes necessary, prefer **Option C (Hybrid)** over **Option A (Separate Files)** to maintain debuggability and avoid file I/O complexity.

---

**Updated**: 2026-01-02
**Author**: Claude (Sonnet 4.5)
