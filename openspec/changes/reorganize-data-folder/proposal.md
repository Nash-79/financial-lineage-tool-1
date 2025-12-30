# Change: Reorganize Data Folder with Hierarchical Structure

## Why

The current data folder structure is disorganized with mixed file types at the root level and inconsistent naming conventions. Files like `AdventureWorksLT-All.sql`, `entity_embeddings.json`, `graph_export.json`, and `sql_embeddings.json` are scattered at the root, making it difficult to understand the data pipeline flow and locate specific outputs. The `separated_sql` folder contains a mix of database-specific folders (e.g., `AdventureWorksLT-All`) and generic object type folders (e.g., `tables`, `views`), creating confusion about the organizational hierarchy.

A clear, hierarchical folder structure organized by database/project name with consistent subfolder patterns will improve maintainability, make the ingestion pipeline more transparent, and enable easier navigation for both developers and users.

## What Changes

- Implement hierarchical data organization: `data/{database-name}/{object-type}/`
- Create consistent folder structure for each database/project:
  - `data/{database-name}/raw/` - Original SQL files
  - `data/{database-name}/separated/` - Separated SQL objects by type (tables, views, procedures, etc.)
  - `data/{database-name}/embeddings/` - All embedding outputs (sql_embeddings.json, entity_embeddings.json)
  - `data/{database-name}/graph/` - Graph exports (graph_export.json, graph_viz.json, cypher_queries.json)
  - `data/{database-name}/metadata/` - Manifests and processing logs
- Move root-level files to appropriate database folders
- Create automated migration script to reorganize existing data
- Update all ingestion scripts to use new folder structure
- Add `.gitkeep` files to preserve empty folder structure in version control
- Create README.md in data folder explaining the structure
- **BREAKING**: Changes default output paths in ingestion pipeline

## Impact

- **Affected specs**:
  - `ingestion-pipeline` (modified - output paths change)
  - `data-organization` (added - new capability)
  - `utility-scripts` (modified - add migration script)

- **Affected code**:
  - `src/ingestion/parallel_file_watcher.py` - Update output path logic
  - `src/ingestion/batch_processor.py` - Update file output locations
  - `src/parsing/enhanced_sql_parser.py` - Update separated SQL output paths
  - `src/embeddings/sql_embedder.py` - Update embedding output paths
  - `src/knowledge_graph/neo4j_client.py` - Update graph export paths
  - All scripts reading from data folder

- **Migration required**: Yes - automated migration script will reorganize existing data

- **User impact**: Users will need to update any hardcoded paths; migration script will handle automatic reorganization

## Success Criteria

- All data files organized under database-specific folders
- Clear folder hierarchy: `data/{db-name}/{category}/`
- Migration script successfully moves existing files without data loss
- All ingestion scripts work with new folder structure
- Documentation clearly explains folder organization
- No files remain at data root (except .gitkeep and README.md)

## Timeline

- Phase 1: Create folder structure and README (1 hour)
- Phase 2: Build migration script with dry-run mode (3-4 hours)
- Phase 3: Update ingestion scripts to use new paths (4-6 hours)
- Phase 4: Test migration and validate all outputs (2-3 hours)
- Phase 5: Documentation and deployment guide (1-2 hours)

**Total estimated effort**: 11-16 hours
