## ADDED Requirements
### Requirement: Dialect-aware ingestion inputs
The API SHALL accept a SQL dialect parameter for file upload and GitHub ingestion requests and use it during SQL parsing.

#### Scenario: Uploading SQL files
- **WHEN** a user uploads SQL files with a dialect specified
- **THEN** the ingestion pipeline parses SQL using the specified dialect

#### Scenario: GitHub ingestion
- **WHEN** a user ingests GitHub SQL files with a dialect specified
- **THEN** the ingestion pipeline parses SQL using the specified dialect

### Requirement: Lineage edge response disambiguation
The API SHALL return edge metadata without overwriting the node `source` identifier by using `edge_source` for edge origin metadata.

#### Scenario: Fetching lineage edges
- **WHEN** a client requests lineage edges
- **THEN** each edge includes `edge_source` for edge origin metadata
- **AND** the edge `source` and `target` identifiers remain node IDs
