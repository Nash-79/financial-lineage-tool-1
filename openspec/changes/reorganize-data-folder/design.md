# Design: Data Folder Reorganization

## Context

The financial lineage tool processes SQL files through multiple stages (parsing, separation, embedding, graph generation) and produces various output artifacts. Currently, files are scattered across the data folder with no clear organizational principle, making it difficult to:

- Understand which files belong to which database/project
- Track the processing pipeline flow
- Clean up old or test data
- Manage multiple databases simultaneously
- Onboard new developers

**Stakeholders**:
- Developers maintaining the ingestion pipeline
- Users running the tool on multiple databases
- DevOps managing data storage and backups

**Constraints**:
- Must maintain backward compatibility during migration
- Cannot lose any existing data during reorganization
- Must work with existing ingestion pipeline optimizations (caching, batching, parallel processing)

## Goals / Non-Goals

**Goals**:
- Clear, self-documenting folder hierarchy organized by database name
- Consistent folder structure across all databases
- Automated migration with safety checks and rollback
- Updated ingestion pipeline to use new structure
- Comprehensive documentation

**Non-Goals**:
- Changing data formats or file contents (only moving files)
- Adding new data processing capabilities
- Modifying database schema or Neo4j structure
- Implementing data retention policies (separate concern)

## Decisions

### Decision 1: Hierarchical Structure by Database Name

**Chosen Approach**: `data/{database-name}/{category}/`

```
data/
├── README.md
├── .cache/                          # Global cache (unchanged)
├── adventureworks-lt/               # Database-specific folder
│   ├── raw/                         # Original SQL files
│   │   └── AdventureWorksLT-All.sql
│   ├── separated/                   # Separated SQL objects
│   │   ├── tables/
│   │   ├── views/
│   │   ├── stored_procedures/
│   │   ├── functions/
│   │   └── organization_manifest.json
│   ├── embeddings/                  # All embedding outputs
│   │   ├── sql_embeddings.json
│   │   ├── entity_embeddings.json
│   │   └── sample_embeddings.json
│   ├── graph/                       # Graph exports
│   │   ├── graph_export.json
│   │   ├── graph_viz.json
│   │   └── cypher_queries.json
│   └── metadata/                    # Processing metadata
│       ├── failed_ingestion.jsonl
│       └── processing_stats.json
└── sample-financial-schema/         # Another database
    ├── raw/
    ├── separated/
    ├── embeddings/
    ├── graph/
    └── metadata/
```

**Rationale**:
- Database name as primary organization unit (most common use case)
- Category subfolders clearly show processing stages
- Easy to add new databases without restructuring
- Natural fit for multi-database scenarios
- Self-documenting structure

**Alternatives Considered**:

1. **By File Type** (`data/embeddings/`, `data/graphs/`, etc.)
   - ❌ Rejected: Mixes multiple databases, harder to manage
   - ❌ Difficult to delete all data for a specific database

2. **Flat with Prefixes** (`data/adventureworks_sql_embeddings.json`)
   - ❌ Rejected: Doesn't scale, still cluttered, harder to navigate

3. **By Processing Stage** (`data/01-raw/`, `data/02-parsed/`)
   - ❌ Rejected: Awkward for concurrent multi-database processing
   - ❌ Stage numbers arbitrary and may change

### Decision 2: Database Name Normalization

**Rule**: Convert database names to kebab-case for folder names

```python
# Examples:
"AdventureWorksLT-All" → "adventureworks-lt-all"
"sample_financial_schema" → "sample-financial-schema"
"MyDatabase.sql" → "my-database"
```

**Rationale**:
- Cross-platform compatibility (Windows, Linux, macOS)
- URL-safe for potential web interfaces
- Consistent with OpenSpec naming conventions
- Avoids case-sensitivity issues

### Decision 3: Migration Strategy

**Approach**: Automated script with three-phase execution

**Phase 1: Dry Run (Default)**
```bash
python scripts/migrate_data_structure.py --dry-run
# Output:
# [DRY RUN] Would move: data/AdventureWorksLT-All.sql → data/adventureworks-lt-all/raw/
# [DRY RUN] Would move: data/sql_embeddings.json → data/adventureworks-lt-all/embeddings/
# ...
# Summary: 15 files would be moved, 0 conflicts, 0 errors
```

**Phase 2: Execute with Backup**
```bash
python scripts/migrate_data_structure.py --execute --backup
# Creates: data_backup_20251230_153045.tar.gz
# Moves all files
# Validates all moves successful
```

**Phase 3: Validation**
```bash
python scripts/migrate_data_structure.py --validate
# Checks all expected files exist in new locations
# Reports any missing or orphaned files
```

**Rollback Capability**:
```bash
python scripts/migrate_data_structure.py --rollback data_backup_20251230_153045.tar.gz
```

**Rationale**:
- Dry run prevents accidental data loss
- Automatic backup provides safety net
- Validation ensures migration completed successfully
- Rollback capability for quick recovery

### Decision 4: Database Name Detection

**Strategy**: Extract database name from multiple sources with fallback

**Priority Order**:
1. Explicit `--database` CLI parameter
2. Filename pattern matching (`{DatabaseName}-*.sql`, `{DatabaseName}.sql`)
3. Directory name (if processing a folder)
4. Default to `"default"` as database name

**Implementation**:
```python
def detect_database_name(file_path: str, explicit_name: str = None) -> str:
    if explicit_name:
        return normalize_database_name(explicit_name)

    # Try extracting from filename
    filename = Path(file_path).stem
    if '-' in filename:
        db_name = filename.split('-')[0]
        return normalize_database_name(db_name)

    # Default fallback
    return "default"

def normalize_database_name(name: str) -> str:
    # Convert to kebab-case
    return re.sub(r'[^a-z0-9]+', '-', name.lower()).strip('-')
```

**Rationale**:
- Explicit parameter gives users full control
- Automatic detection works for common cases
- Fallback prevents failures
- Normalization ensures consistency

### Decision 5: Path Construction Helper

**Create centralized path utility module**:

```python
# src/utils/data_paths.py

from pathlib import Path
from typing import Literal

DataCategory = Literal["raw", "separated", "embeddings", "graph", "metadata"]

class DataPathManager:
    def __init__(self, data_root: Path, database_name: str):
        self.data_root = Path(data_root)
        self.database_name = normalize_database_name(database_name)
        self.database_dir = self.data_root / self.database_name

    def get_category_path(self, category: DataCategory) -> Path:
        """Get path for a specific category (creates if not exists)."""
        path = self.database_dir / category
        path.mkdir(parents=True, exist_ok=True)
        return path

    def get_file_path(self, category: DataCategory, filename: str) -> Path:
        """Get full path for a specific file."""
        return self.get_category_path(category) / filename

    # Specific helpers
    def raw_path(self, filename: str) -> Path:
        return self.get_file_path("raw", filename)

    def separated_path(self, object_type: str) -> Path:
        """Get path for separated SQL objects."""
        sep_dir = self.get_category_path("separated") / object_type
        sep_dir.mkdir(parents=True, exist_ok=True)
        return sep_dir

    def embeddings_path(self, filename: str) -> Path:
        return self.get_file_path("embeddings", filename)

    def graph_path(self, filename: str) -> Path:
        return self.get_file_path("graph", filename)

    def metadata_path(self, filename: str) -> Path:
        return self.get_file_path("metadata", filename)
```

**Usage Example**:
```python
# In ingestion pipeline
paths = DataPathManager(data_root="./data", database_name="AdventureWorksLT")

# Write embeddings
embedding_file = paths.embeddings_path("sql_embeddings.json")
with open(embedding_file, 'w') as f:
    json.dump(embeddings, f)

# Write separated SQL
table_dir = paths.separated_path("tables")
with open(table_dir / "Customer.sql", 'w') as f:
    f.write(table_ddl)
```

**Rationale**:
- Centralized path logic prevents inconsistencies
- Automatic folder creation reduces boilerplate
- Type hints improve code safety
- Easy to test and mock

## Risks / Trade-offs

### Risk 1: Breaking Existing Scripts

**Mitigation**:
- Maintain backward compatibility during transition period
- Provide clear migration guide
- Add deprecation warnings for old path usage
- Include migration script in deployment process

### Risk 2: Data Loss During Migration

**Mitigation**:
- Mandatory dry-run mode (default)
- Automatic backup before migration
- Validation step after migration
- Rollback capability
- File checksums to verify integrity

### Risk 3: Performance Impact

**Potential Impact**: Additional folder nesting could impact file I/O

**Mitigation**:
- Modern filesystems handle nested folders efficiently
- Keep nesting depth reasonable (3 levels max)
- Benchmark before/after migration
- Current bottleneck is parsing/embedding, not file I/O

**Trade-off**: Slight increase in path length vs. significant improvement in organization

### Risk 4: Configuration Complexity

**Issue**: Need to pass database name through entire pipeline

**Mitigation**:
- Add database_name to configuration objects
- Use DataPathManager for consistent path construction
- Default to "default" if not specified
- Document configuration clearly

## Migration Plan

### Pre-Migration (Day 0)

1. **Backup current data folder**:
   ```bash
   tar -czf data_backup_$(date +%Y%m%d).tar.gz data/
   ```

2. **Run dry-run migration**:
   ```bash
   python scripts/migrate_data_structure.py --dry-run > migration_plan.txt
   ```

3. **Review migration plan**:
   - Check all files will be moved correctly
   - Verify no conflicts
   - Confirm database name detection

### Migration (Day 1)

1. **Stop all ingestion services**:
   ```bash
   systemctl stop financial-lineage-ingestion
   ```

2. **Execute migration with backup**:
   ```bash
   python scripts/migrate_data_structure.py --execute --backup
   ```

3. **Validate migration**:
   ```bash
   python scripts/migrate_data_structure.py --validate
   ```

4. **Update configuration**:
   - Update environment variables
   - Update config files with new paths

5. **Deploy updated code**:
   ```bash
   git pull origin main
   pip install -r requirements.txt
   ```

6. **Restart services**:
   ```bash
   systemctl start financial-lineage-ingestion
   ```

### Post-Migration (Day 2-7)

1. **Monitor for issues**:
   - Check logs for path errors
   - Verify all outputs created in correct locations
   - Monitor metrics for performance changes

2. **Validate outputs**:
   - Check embeddings generated correctly
   - Verify graph exports in correct locations
   - Confirm separated SQL files organized properly

3. **Archive old backup** (after 7 days):
   ```bash
   mv data_backup_*.tar.gz ./backups/archive/
   ```

### Rollback Procedure

If critical issues detected:

```bash
# Stop services
systemctl stop financial-lineage-ingestion

# Rollback to backup
python scripts/migrate_data_structure.py --rollback data_backup_20251230.tar.gz

# Restore old code version
git checkout [previous-version]
pip install -r requirements.txt

# Restart services
systemctl start financial-lineage-ingestion
```

**Rollback Time**: < 10 minutes

## Open Questions

1. **Q**: Should we support multiple databases in a single ingestion run?
   **A**: Yes, via multiple invocations or --database parameter per database

2. **Q**: How to handle temporary/working files?
   **A**: Use `{database}/metadata/temp/` subfolder, clean up after processing

3. **Q**: Should cache remain global or be per-database?
   **A**: Keep global `.cache/` - parse cache is content-based (SHA-256), not database-specific

4. **Q**: What about failed ingestion logs?
   **A**: Move to `{database}/metadata/failed_ingestion.jsonl` per database

5. **Q**: Handle legacy data during transition?
   **A**: Migration script auto-detects and moves; document manual steps if needed

## Success Metrics

- ✅ Zero data loss during migration
- ✅ All ingestion tests pass with new structure
- ✅ Migration completes in < 5 minutes for typical dataset
- ✅ All documentation updated and clear
- ✅ No hardcoded paths remaining in codebase
- ✅ New database ingestion automatically creates correct structure
