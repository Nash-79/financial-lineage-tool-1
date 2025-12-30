# Specification: Data Organization

## ADDED Requirements

### Requirement: Hierarchical Folder Structure

The system SHALL organize all data files in a hierarchical structure with database name as the primary organizational unit, followed by category-specific subfolders.

#### Scenario: Single database data organization
- **WHEN** processing SQL files for "AdventureWorksLT" database
- **THEN** the system SHALL create folder structure: `data/adventureworks-lt/{raw,separated,embeddings,graph,metadata}/`
- **AND** all output files SHALL be placed in appropriate category folders

#### Scenario: Multiple database data organization
- **WHEN** processing SQL files for multiple databases
- **THEN** each database SHALL have its own top-level folder under `data/`
- **AND** each database folder SHALL contain the same category subfolders
- **AND** files SHALL NOT be mixed between different database folders

#### Scenario: Database name normalization
- **WHEN** database name contains mixed case, spaces, or special characters (e.g., "AdventureWorks LT")
- **THEN** the system SHALL normalize to kebab-case (e.g., "adventureworks-lt")
- **AND** the normalized name SHALL be used for the folder name

### Requirement: Category Folder Organization

The system SHALL organize files into five standard category folders within each database folder.

#### Scenario: Raw SQL files
- **WHEN** storing original SQL files
- **THEN** files SHALL be placed in `{database}/raw/` folder
- **AND** original filenames SHALL be preserved

#### Scenario: Separated SQL objects
- **WHEN** SQL objects are separated by type
- **THEN** files SHALL be organized in `{database}/separated/{object-type}/` folders
- **AND** object types SHALL include: tables, views, stored_procedures, functions, triggers, schemas, indexes
- **AND** organization manifest SHALL be stored in `{database}/separated/organization_manifest.json`

#### Scenario: Embedding outputs
- **WHEN** generating embeddings (SQL, entity, or sample)
- **THEN** all embedding files SHALL be placed in `{database}/embeddings/` folder
- **AND** files SHALL be named: `sql_embeddings.json`, `entity_embeddings.json`, `sample_embeddings.json`

#### Scenario: Graph exports
- **WHEN** exporting graph data
- **THEN** all graph files SHALL be placed in `{database}/graph/` folder
- **AND** files SHALL include: `graph_export.json`, `graph_viz.json`, `cypher_queries.json`

#### Scenario: Processing metadata
- **WHEN** storing processing metadata or logs
- **THEN** files SHALL be placed in `{database}/metadata/` folder
- **AND** files SHALL include: `failed_ingestion.jsonl`, `processing_stats.json`

### Requirement: Automatic Folder Creation

The system SHALL automatically create the required folder structure when processing data for a database.

#### Scenario: First-time database processing
- **WHEN** processing files for a database that doesn't have a folder yet
- **THEN** the system SHALL create `data/{database-name}/` folder
- **AND** SHALL create all required category subfolders (raw, separated, embeddings, graph, metadata)
- **AND** SHALL create object-type subfolders under `separated/` as needed

#### Scenario: Partial folder structure exists
- **WHEN** some category folders exist but others are missing
- **THEN** the system SHALL create only the missing folders
- **AND** SHALL NOT modify existing folders or files

### Requirement: Database Name Detection

The system SHALL detect database name from multiple sources with a defined priority order.

#### Scenario: Explicit database name provided
- **WHEN** user provides `--database` CLI parameter
- **THEN** the system SHALL use the provided name (after normalization)
- **AND** SHALL NOT attempt automatic detection

#### Scenario: Automatic detection from filename
- **WHEN** no explicit database name provided AND filename matches pattern `{DatabaseName}-*.sql`
- **THEN** the system SHALL extract database name from the prefix before the first hyphen
- **AND** SHALL normalize the extracted name to kebab-case

#### Scenario: Automatic detection from directory
- **WHEN** processing files from a directory AND no explicit name provided
- **THEN** the system SHALL use the directory name as database name
- **AND** SHALL normalize the directory name to kebab-case

#### Scenario: Fallback to default
- **WHEN** no database name can be detected from any source
- **THEN** the system SHALL use "default" as the database name
- **AND** SHALL log a warning about using default name

### Requirement: Path Construction Utilities

The system SHALL provide a centralized utility for constructing file paths consistently across all components.

#### Scenario: Get category path
- **WHEN** a component needs a path to a category folder
- **THEN** the utility SHALL return `Path` object for `data/{database}/{category}/`
- **AND** SHALL create the folder if it doesn't exist

#### Scenario: Get file path
- **WHEN** a component needs a path to a specific file
- **THEN** the utility SHALL return `Path` object for `data/{database}/{category}/{filename}`
- **AND** SHALL create parent folders if they don't exist

#### Scenario: Get separated object path
- **WHEN** storing separated SQL objects
- **THEN** the utility SHALL return path `data/{database}/separated/{object_type}/`
- **AND** SHALL support object types: tables, views, stored_procedures, functions, triggers, etc.

### Requirement: Data Folder Documentation

The system SHALL include comprehensive documentation of the folder structure.

#### Scenario: README in data folder
- **WHEN** the data folder exists
- **THEN** a `data/README.md` file SHALL exist
- **AND** SHALL document the folder structure with examples
- **AND** SHALL explain the purpose of each category folder
- **AND** SHALL provide examples of expected file types in each folder

#### Scenario: Folder structure preservation
- **WHEN** repository is cloned fresh
- **THEN** the standard folder structure SHALL be preserved via `.gitkeep` files
- **AND** empty category folders SHALL include `.gitkeep` files
