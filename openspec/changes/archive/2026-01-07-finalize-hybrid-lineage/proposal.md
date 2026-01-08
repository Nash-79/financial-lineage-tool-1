# Change: Finalize Hybrid Lineage Implementation

## Why
While the core hybrid lineage system is implemented, several key gaps identified in the review process remain:
1. **Triggers**: Nodes are created but lack `ATTACHED_TO` edges to their target tables.
2. **Synonyms**: Nodes are created but lack `ALIAS_OF` edges to their target objects.
3. **LLM Service**: The API endpoint to trigger lineage inference is missing.
4. **Dialect Registry**: The SQL dialect registry is currently in-memory code; strictly adhering to the original design requires migrating it to a database (DuckDB) for dynamic configuration.

## What Changes
- **Parsing & Graph Updates (Triggers/Synonyms):**
  - Update `CodeParser` to extract target tables for triggers and synonyms.
  - Update `GraphExtractor` to create `ATTACHED_TO` and `ALIAS_OF` relationships.

- **LLM Service Integration:**
  - Initialize `LineageInferenceService` in the application state.
  - Add `POST /api/v1/lineage/infer` endpoint to trigger AI-driven edge discovery.

- **Dialect Registry Migration:**
  - Create a DuckDB migration to initialize the `sql_dialects` table.
  - Implement a repository pattern to load dialects from DuckDB.
  - Update `src/config/sql_dialects.py` and the API to use this repository.

## Impact
- **Specs**: `data-lineage` (triggers/synonyms), `llm-service` (API), `config` (dialects).
- **Code**: `CodeParser`, `GraphExtractor`, `LineageInferenceService`, `main_local.py`, new migration.
- **Data**: New edge types (`ATTACHED_TO`, `ALIAS_OF`) will appear in Neo4j.
