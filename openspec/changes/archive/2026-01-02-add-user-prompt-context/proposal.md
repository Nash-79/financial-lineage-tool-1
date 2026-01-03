# Change: Add User Prompt Context for Projects

## Why

Today, ingestion (file upload or GitHub ingest) operates mostly on SQL text and repository structure. The system has limited awareness of the business intent behind a project (what it is for, the expected sources/sinks, and domain vocabulary). As a result:

- Lineage extraction can be noisy or miss the "important" paths.
- Knowledge graph nodes are harder to interpret without context and naming conventions.
- Cross-project relationships are difficult to express explicitly.

This change introduces **project-level user prompt context**: structured metadata authored by a user and persisted with the project, then injected into LLM-assisted extraction prompts to improve relevance and accuracy.

## What Changes

- **project-context:** Add persisted project context (JSON + optional uploaded markdown) and APIs to manage it; prepend context to LLM extraction prompts when present.

Backend changes:
- Add `context` storage to projects (DuckDB JSON) and optional filesystem storage for uploaded context files.
- Add endpoints:
  - `GET /api/v1/projects/{project_id}/context`
  - `PUT /api/v1/projects/{project_id}/context`
  - `POST /api/v1/projects/{project_id}/context/upload` (markdown upload)
- Update ingestion prompt building to include a deterministic `<project_context>` block when context exists.

Frontend changes:
- Project Settings UI to view/edit context (JSON form + markdown editor).
- Upload UI for markdown context file with validation and error handling.
- Display "last updated" and file name (if uploaded).

## Impact

Affected specs:
- `project-context` (added capability)

Affected code areas:
- Metadata storage layer (DuckDB schema + project store)
- API router layer (project context endpoints)
- Ingestion / prompt builder (prepend context block)
- Frontend project settings components (context editor + upload)

Behavioral impact:
- Ingestion results should become more targeted when context is provided.
- Existing projects without context continue to ingest exactly as before (no breaking change).

## Success Criteria

- Context is persisted per project and retrievable via API.
- Uploading a markdown file updates stored context deterministically.
- When context exists, ingestion prompts include the context block; when absent, prompts remain unchanged.
- Basic validation is enforced (required fields, type checks, max file size, project existence).
- UI supports editing and upload workflows with clear errors.

## Out of Scope (for this change)

- Prompt template management (CRUD/versioning), re-processing orchestration, graph version migrations, or prompt override dashboards.
  These should be proposed as a separate OpenSpec change if needed.
