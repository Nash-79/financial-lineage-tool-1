# project-context Specification

## Purpose
TBD - created by archiving change add-user-prompt-context. Update Purpose after archive.
## Requirements
### Requirement: Persist project context

The system SHALL support storing structured context information for each project.

#### Scenario: Create or update context in storage
- **GIVEN** a project exists
- **WHEN** valid context JSON is provided for that project
- **THEN** the system SHALL store the context in the projects metadata store as JSON
- **AND** the stored context SHALL include (at minimum):
  - `description` (string)
  - `format` (`text` | `markdown`)
  - `source_entities` (array of strings)
  - `target_entities` (array of strings)
  - `related_projects` (array of project IDs)
  - `domain_hints` (array of strings)
  - `file_name` (string, optional; set when uploaded)
  - `updated_at` (timestamp)

#### Scenario: Validate related project references
- **GIVEN** a project exists
- **WHEN** context is submitted with `related_projects` containing the project's own ID
- **THEN** the system SHALL reject the request with an error (HTTP 400)

(Notes: multi-hop cycle detection across projects is not required for this change.)

### Requirement: Provide project context APIs

The system SHALL provide APIs to read and write project context.

#### Scenario: Retrieve project context
- **GIVEN** a project exists with stored context
- **WHEN** a GET request is made to `/api/v1/projects/{project_id}/context`
- **THEN** the system SHALL return HTTP 200 with the stored context JSON

#### Scenario: Retrieve context for a project without context
- **GIVEN** a project exists without stored context
- **WHEN** a GET request is made to `/api/v1/projects/{project_id}/context`
- **THEN** the system SHALL return HTTP 200 with an empty/default context object OR HTTP 404 (implementation choice)
- **AND** the behavior SHALL be documented and consistent across environments

#### Scenario: Update project context via API
- **GIVEN** a project exists
- **WHEN** a PUT request is made to `/api/v1/projects/{project_id}/context` with valid context JSON
- **THEN** the system SHALL persist the updated context
- **AND** return HTTP 200 with the updated context including `updated_at`

#### Scenario: Update context for a non-existent project
- **GIVEN** a project ID that does not exist
- **WHEN** a request is made to any `/api/v1/projects/{project_id}/context*` endpoint
- **THEN** the system SHALL return HTTP 404

### Requirement: Support markdown upload with deterministic parsing

The system SHALL support uploading a markdown file as project context.

Parsing convention:
- If the markdown contains YAML frontmatter, the system SHALL use it to populate structured fields (`format`, `source_entities`, `target_entities`, `related_projects`, `domain_hints`).
- The markdown body (excluding frontmatter) SHALL populate `description`.
- If no frontmatter exists, the entire markdown body SHALL populate `description` and `format` SHALL be set to `markdown`.

#### Scenario: Upload markdown context file
- **GIVEN** a project exists
- **WHEN** a markdown file is uploaded to `/api/v1/projects/{project_id}/context/upload`
- **THEN** the system SHALL store the file (or its contents) and update the project context JSON
- **AND** the stored context SHALL include `file_name` and `updated_at`

#### Scenario: Reject invalid uploads
- **GIVEN** a project exists
- **WHEN** a non-markdown file type is uploaded
- **THEN** the system SHALL return HTTP 400

#### Scenario: Reject oversized uploads
- **GIVEN** a project exists
- **WHEN** the uploaded file exceeds 50KB
- **THEN** the system SHALL return HTTP 413

### Requirement: Inject project context into LLM extraction prompts

When project context exists, the ingestion pipeline SHALL prepend a deterministic context block to LLM prompts used for extraction.

#### Scenario: Ingestion prompt includes context
- **GIVEN** a project exists with stored context
- **WHEN** an ingestion run triggers LLM-assisted extraction
- **THEN** the system SHALL include a `<project_context>` block ahead of SQL/assets in the prompt
- **AND** the block SHALL contain the context fields in a stable order

#### Scenario: Ingestion prompt without context
- **GIVEN** a project exists without stored context
- **WHEN** an ingestion run triggers LLM-assisted extraction
- **THEN** the system SHALL NOT add a `<project_context>` block
- **AND** extraction behavior SHALL remain backward compatible

