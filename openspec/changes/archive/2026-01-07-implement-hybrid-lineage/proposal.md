# Change: Implement Hybrid Lineage System (Deterministic + LLM)

## Why
The current lineage system is purely deterministic, relying on SQL parsers and static analysis. While accurate for direct dependencies, it misses complex relationships like:
- Dynamic SQL execution in stored procedures
- Python code reading/writing SQL tables without explicit ORM models
- Cross-repository dependencies
- Logic buried in dynamic configuration files

To capture the "full picture" of lineage, we need to augment the deterministic graph with LLM-inferred edges. However, LLMs can halluncinate, so these edges must be treated differently—they need confidence scores, provenance tracking, and a human-in-the-loop review system.

## What Changes
- **Data Model Extensions:**
  - Add `CodeUnit` node types (Function, Procedure, Trigger, etc.).
  - Add additional `DataAsset` subtypes such as `MaterializedView` and `Synonym`.
  - Add `confidence` (0.0-1.0), `source` (parser/ollama_llm/human), and `status` (pending_review/approved/rejected) properties to edges.
  - Standardize edge types: `READS_FROM`, `WRITES_TO`, `CALLS`, `DERIVES`, `DEPENDS_ON`, `ATTACHED_TO`, `ALIAS_OF`.

- **Deterministic Lineage Improvements:**
  - Enhance `CodeParser` (backed by sqlglot dialects) to extract function/procedure bodies and calls.
  - Extend SQL ingestion to understand additional objects such as triggers, synonyms, and materialized views, mapping them into the unified graph model.
  - Add Python parser extensions to suggest table references and build a cross-repository `CodeUnit`-level call/dependency graph.

- **LLM Augmentation Service:**
  - New service to scan code + graph context and propose "missing" edges via Ollama.
  - Structured output parsing to create valid graph edges with evidence and confidence.

- **Human-in-the-Loop Workflow:**
  - New "Lineage Review" APIs to approve/reject inferred edges.
  - Edges default to `pending_review` (LLM) or `approved` (Deterministic), with review actions able to set `status` to `approved` or `rejected`.

- **SQL Dialect Configuration:**
  - Introduce a backend registry of supported sqlglot dialects (e.g., DuckDB, T-SQL, Fabric, Postgres, MySQL, Spark).
  - Require a `sql_dialect` to be supplied for SQL ingestion (with optional `auto` mode), and expose an API to list enabled dialects for the frontend.

## Impact
- **Affected Specs:** `data-lineage`, `llm-service`, `api-endpoints`
- **Affected Code:**
  - `src/ingestion/code_parser.py`: Enhanced parsing
  - `src/knowledge_graph/entity_extractor.py`: New node/edge types
  - `src/services/lineage_inference.py`: **[NEW]** LLM inference service
  - `src/api/routers/lineage.py`: Review endpoints and filtered querying
- **Migration:**
  - Existing Neo4j data remains valid; new properties will be added to edges on next ingestion.
  - No data loss; purely additive metadata.
