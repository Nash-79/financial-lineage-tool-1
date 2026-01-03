# User Guide: Project Context

The Project Context feature allows you to provide domain knowledge, business logic descriptions, and specific entity hints to the Financial Lineage Tool. This context helps the AI understand your code better during ingestion and lineage extraction, leading to more accurate results.

## Why use Project Context?

Standard SQL parsing is effective for explicit dependencies (e.g., `INSERT INTO table SELECT * FROM source`), but complex business logic or domain-specific transformations can be ambiguous.

By explicitly defining:
- **Source Entities**: Where your data comes from (e.g., `raw_sales`, `kafka_events`).
- **Target Entities**: What you are producing (e.g., `monthly_report`, `dim_customer`).
- **Domain Hints**: Industry terms (e.g., `GDPR`, `FASB`, `Risk Weighted Assets`).

You guide the AI to correctly interpret ambiguous code patterns.

## How to Configure Context

### 1. Via the Web Interface

You can edit project context directly in the metadata management UI.

1. Navigate to the **Connectors** page.
2. Select a single project from the project dropdown.
3. Click the **Context** button in the toolbar.
4. Fill in the fields:
    - **Description**: A plain text or Markdown overview of the project's purpose.
    - **Source Entities**: Comma-separated list of key input tables.
    - **Target Entities**: Comma-separated list of key output tables.
    - **Domain Hints**: Keywords relevant to your business domain.
5. Click **Save Context**.

### 2. Via API

You can programmatically update context using the REST API:

```bash
PUT /api/v1/projects/{project_id}/context
Content-Type: application/json

{
  "description": "Risk calculation engine for EU markets...",
  "format": "text",
  "source_entities": ["trade_repository", "market_data"],
  "target_entities": ["risk_report_daily"],
  "domain_hints": ["basel_iii", "var", "cva"]
}
```

## How it Works

When you ingest files (SQL or Code) assigned to a project with context:

1. The system fetches the active context for that project.
2. It constructs a specialized XML prompt block (`<project_context>`) containing your descriptions and hints.
3. This block is injected into the LLM prompt used for entity extraction.
4. The LLM uses this information to disambiguate table names, infer relationships, and categorize transformations more accurately.

## Best Practices

- **Keep it focused**: List only the most critical 5-10 source/target entities.
- **Explain abbreviations**: Use the Description field to expand on project-specific acronyms.
- **Update regularly**: If your project scope changes, update the context to reflect new inputs/outputs.
