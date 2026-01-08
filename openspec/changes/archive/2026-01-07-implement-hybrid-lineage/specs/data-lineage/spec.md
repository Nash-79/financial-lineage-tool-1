## ADDED Requirements
### Requirement: Hybrid Lineage Data Model
The system SHALL support both deterministic and probabilistic lineage edges in the same graph, distinguished by metadata properties.

#### Scenario: Edge Metadata
- **WHEN** an edge is created between two nodes
- **THEN** it must include `source`, `confidence`, `status`, and `evidence` properties
- **AND** deterministic parsers default to `source="parser"`, `confidence=1.0`, `status="approved"`

### Requirement: Code Unit and Object Modeling
The system SHALL represent executable code units (Functions, Procedures, Triggers) and derived data objects (Synonyms, Materialized Views) as distinct nodes in the lineage graph.

#### Scenario: Stored Procedure Lineage
- **WHEN** ingestion encounters a stored procedure
- **THEN** a `Procedure` node is created
- **AND** `READS_FROM` edges are created to tables it selects from
- **AND** `WRITES_TO` edges are created to tables it updates

#### Scenario: Trigger Lineage
- **WHEN** ingestion encounters a `CREATE TRIGGER` statement in a supported dialect
- **THEN** a `Trigger` CodeUnit node is created
- **AND** an `ATTACHED_TO` edge is created from the trigger to the table it is defined on
- **AND** `READS_FROM` / `WRITES_TO` edges are created based on the trigger body

#### Scenario: Synonym Lineage
- **WHEN** ingestion encounters a `CREATE SYNONYM` statement in a supported dialect
- **THEN** a `Synonym` DataAsset node is created
- **AND** an `ALIAS_OF` edge is created to the underlying Table/View/DataAsset it references

#### Scenario: Materialized View Lineage
- **WHEN** ingestion encounters a `CREATE MATERIALIZED VIEW` statement
- **THEN** a `MaterializedView` DataAsset node is created
- **AND** `DERIVES` / `READS_FROM` edges are created from the source tables/views defined in the view query

### Requirement: SQL Dialect-Aware Parsing
The system SHALL support multiple SQL dialects using a single parser front-end backed by sqlglot.

#### Scenario: Dialect-Specific Parsing
- **WHEN** `CodeParser.parse_sql` is invoked
- **THEN** it MUST accept a `dialect` parameter matching a configured sqlglot dialect
- **AND** it MUST pass this dialect to sqlglot when parsing
- **AND** dialect-specific helpers SHALL map constructs to the abstract graph model

### Requirement: Human-in-the-Loop Review
The system SHALL support manual review of lineage edges.

#### Scenario: Reviewing inferred edges
- **WHEN** a user reviews a `pending_review` edge
- **THEN** they can mark it as `approved` or `rejected`
- **AND** `rejected` edges are excluded from standard lineage traversals

### Requirement: Cross-Repository and Pure-Python Lineage
The system SHALL support lineage across repositories and for pure-Python-only projects.

#### Scenario: Cross-Repository CodeUnit Lineage
- **WHEN** ingestion encounters Python or other code in multiple repositories
- **THEN** it SHALL create `CodeUnit` nodes with repository metadata
- **AND** it SHALL create `CALLS` / `DEPENDS_ON` edges between CodeUnits even when they cross repository boundaries

#### Scenario: Pure-Python Projects
- **WHEN** a project contains only Python code with no SQL
- **THEN** the system SHALL still build a CodeUnit-level lineage graph via `CALLS` / `DEPENDS_ON`
- **AND** discovered DataAssets SHALL be attached to these existing CodeUnits regardless of repository

## MODIFIED Requirements
### Requirement: Lineage Querying
The system SHALL allow filtering lineage queries by edge confidence and status.

#### Scenario: Filtering low confidence edges
- **WHEN** a user queries lineage
- **THEN** they can specify a minimum confidence threshold
- **AND** edges below that threshold are excluded from the result
