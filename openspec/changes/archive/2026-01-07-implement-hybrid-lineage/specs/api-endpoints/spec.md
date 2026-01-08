## ADDED Requirements
### Requirement: Lineage Review API
The system SHALL provide versioned endpoints for human-in-the-loop review of lineage edges.

#### Scenario: Reviewing an edge
- **WHEN** user sends POST to `/api/v1/lineage/review`
- **THEN** they can approve or reject a specific edge by ID or source/target/type
- **AND** the edge status is updated in the graph
- **AND** the decision is logged with reviewer metadata

#### Scenario: Filtered Lineage Query
- **WHEN** user queries lineage edges
- **THEN** they can filter by `source` (parser, llm, user)
- **AND** they can filter by `status` (pending, approved, rejected)
- **AND** they can filter by minimum `confidence` score

### Requirement: SQL Dialect Configuration
The system SHALL provide endpoints to discover supported SQL dialects backed by the backend dialect registry.

#### Scenario: List dialects
- **WHEN** user requests available dialects via `GET /api/v1/config/sql-dialects`
- **THEN** the system returns a list of enabled dialects with fields such as `id`, `display_name`, and `is_default`
- **AND** each `id` corresponds to a configured sqlglot dialect key used by the parser
