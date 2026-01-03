# Design: User Prompt Context for Projects

## Context

The financial lineage tool ingests SQL files and extracts entities/relationships for knowledge graph construction. Currently, extraction happens without understanding project intent or domain context. Users need a way to provide guidance that:

1. Defines project purpose and scope
2. Identifies source/target entities for lineage paths
3. Links related projects for cross-repository lineage
4. Guides LLM-assisted extraction with domain knowledge

### Stakeholders
- Data engineers defining lineage projects
- Analysts exploring cross-project data flows
- LLM service for context-aware extraction

## Goals / Non-Goals

### Goals
- Store structured context at project level
- Support multiple input formats (text, markdown, file upload)
- Integrate context with LLM during entity extraction
- Display context in project management UI
- Enable cross-project linking via context references

### Non-Goals
- Real-time context updates during ingestion (batch only)
- Version control for context changes
- AI-generated context suggestions (future enhancement)
- Repository-level context overrides (keep simple at project level)

## Decisions

### Decision 1: Store context as JSON in DuckDB

**What**: Add `context` JSON column to projects table with structured schema.

**Why**:
- Supports both plain text and structured markdown
- Allows future extension without schema migration
- DuckDB has excellent JSON support for querying

**Schema**:
```json
{
  "description": "Plain text or markdown content",
  "format": "text|markdown",
  "source_entities": ["table1", "schema.table2"],
  "target_entities": ["view1", "procedure1"],
  "related_projects": ["project-id-1", "project-id-2"],
  "domain_hints": ["financial", "customer data"],
  "file_name": "CONTEXT.md (if uploaded)",
  "updated_at": "2025-01-02T12:00:00Z"
}
```

**Alternatives considered**:
- Separate context table: Over-engineering for 1:1 relationship
- Text column only: Loses structure, harder to query

### Decision 2: Context file stored on filesystem

**What**: Uploaded context files saved to `data/contexts/{project_id}/` with reference in DB.

**Why**:
- Large markdown files don't bloat DuckDB
- Easy to edit and version control
- Can be included in project exports

**Alternative**: Store file content in DB (rejected - harder to manage, no real benefit)

### Decision 3: LLM integration via prompt injection

**What**: Prepend project context to LLM prompts during entity extraction.

**Why**:
- Non-invasive integration with existing LLM service
- Context can guide entity naming, relationship detection
- Graceful fallback when context is empty

**Example prompt structure**:
```
<project_context>
This project analyzes customer financial data flows.
Starting points: raw_transactions, customer_master
Targets: dim_customer, fact_transactions
</project_context>

<task>
Extract entities and relationships from the following SQL:
{sql_content}
</task>
```

### Decision 4: Cross-project linking via context references

**What**: `related_projects` array stores project IDs that should be considered for cross-repository lineage.

**Why**:
- Simple to implement
- Enables future cross-project lineage traversal
- Links are explicit and user-controlled

## Risks / Trade-offs

| Risk | Mitigation |
|------|------------|
| Context ignored if LLM unavailable | Store as metadata regardless, display in UI |
| Large context files slow extraction | Limit to 50KB, summarize if needed |
| Stale context after project evolution | Show "last updated" timestamp, prompt for updates |
| Circular project references | Validate and reject cycles |

## Migration Plan

1. Add nullable `context` JSON column to projects table
2. Add nullable `context_file_path` column
3. Deploy backend with new endpoints
4. Deploy frontend with context UI
5. No data migration needed (new feature)

**Rollback**: Remove columns (no data loss for existing projects)

## Open Questions

1. Should context be versioned? (Recommend: No, keep simple for v1)
2. Maximum context file size? (Recommend: 50KB)
3. Auto-detect context files in repo (like CLAUDE.md)? (Recommend: Future enhancement)
