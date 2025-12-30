# ingestion-pipeline Specification Deltas

## MODIFIED Requirements

### Requirement: Failed Entity Logging
The system SHALL log failed ingestion attempts to database-specific metadata folders organized by database name.

**Reason**: Support new hierarchical folder structure

#### Scenario: Failed entity logging with hierarchical paths
- **WHEN** an entity or relationship fails to write after all retry attempts
- **THEN** the system MUST log the failed item to `data/{database-name}/metadata/failed_ingestion.jsonl` with timestamp, error message, and full entity/relationship data
- **AND** the system MUST create the metadata folder if it doesn't exist

### Requirement: Output Path Configuration
The system SHALL support configurable output paths with database-specific organization.

**Added as breaking change for hierarchical folder support**

#### Scenario: Database-specific output configuration
- **WHEN** the ingestion pipeline is initialized with a database name
- **THEN** all output files SHALL be organized under `data/{database-name}/` folder
- **AND** category subfolders SHALL be created automatically (raw, separated, embeddings, graph, metadata)

#### Scenario: Default database fallback
- **WHEN** no database name is provided or detected
- **THEN** the system SHALL use "default" as the database name
- **AND** SHALL log a warning about using default database name

#### Scenario: Database name from CLI parameter
- **WHEN** the `--database` parameter is provided
- **THEN** the system SHALL use the provided database name (normalized to kebab-case)
- **AND** SHALL override any automatic database name detection

### Requirement: Cache Management Operations
The system SHALL provide operations to manage the parse cache, including inspection, clearing, and health checks. Cache remains global across all databases.

**Reason**: Clarify that parse cache is global (content-based, not database-specific)

#### Scenario: Cache statistics retrieval
- **WHEN** a user queries cache statistics
- **THEN** the system MUST return total entries, cache size (MB), oldest entry timestamp, and hit rate
- **AND** cache SHALL be stored in global `data/.cache/` folder (not database-specific)

#### Scenario: Manual cache clearing
- **WHEN** a user executes the `--clear-cache` command
- **THEN** the system MUST delete all cached parse results from global cache and confirm deletion count

#### Scenario: Cache health check on startup
- **WHEN** the ingestion system starts
- **THEN** the system MUST verify cache integrity by validating 10 random cache entries from global cache (check hash matches re-parsed content)

## ADDED Requirements

### Requirement: Separated SQL Output Organization
The system SHALL organize separated SQL objects into database-specific folder hierarchies.

#### Scenario: Separated SQL files by object type
- **WHEN** SQL objects are separated by type (tables, views, procedures, etc.)
- **THEN** files SHALL be organized in `data/{database-name}/separated/{object-type}/` folders
- **AND** object types SHALL include: tables, views, stored_procedures, functions, triggers, schemas, indexes

#### Scenario: Organization manifest output
- **WHEN** SQL separation is complete
- **THEN** the organization manifest SHALL be stored at `data/{database-name}/separated/organization_manifest.json`
- **AND** SHALL include metadata about all separated objects

### Requirement: Embedding Output Organization
The system SHALL output all embedding files to database-specific embedding folders.

#### Scenario: SQL embeddings output
- **WHEN** SQL embeddings are generated
- **THEN** the output file SHALL be `data/{database-name}/embeddings/sql_embeddings.json`

#### Scenario: Entity embeddings output
- **WHEN** entity embeddings are generated
- **THEN** the output file SHALL be `data/{database-name}/embeddings/entity_embeddings.json`

#### Scenario: Sample embeddings output
- **WHEN** sample embeddings are generated
- **THEN** the output file SHALL be `data/{database-name}/embeddings/sample_embeddings.json`

### Requirement: Graph Export Organization
The system SHALL output all graph export files to database-specific graph folders.

#### Scenario: Graph export output
- **WHEN** graph data is exported
- **THEN** the output file SHALL be `data/{database-name}/graph/graph_export.json`

#### Scenario: Graph visualization output
- **WHEN** graph visualization data is generated
- **THEN** the output file SHALL be `data/{database-name}/graph/graph_viz.json`

#### Scenario: Cypher queries output
- **WHEN** Cypher queries are exported
- **THEN** the output file SHALL be `data/{database-name}/graph/cypher_queries.json`

### Requirement: Raw SQL Storage
The system SHALL store original SQL files in database-specific raw folders.

#### Scenario: Raw SQL file storage
- **WHEN** original SQL files are stored
- **THEN** files SHALL be placed in `data/{database-name}/raw/` folder
- **AND** original filenames SHALL be preserved
