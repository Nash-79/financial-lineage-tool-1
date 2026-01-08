## 1. Data Model Updates
- [x] 1.1 Update `Neo4jGraphClient` to support edge properties: `confidence`, `source`, `status`, `evidence`.
- [x] 1.2 Create migration script or manual step to index new edge properties.
- [x] 1.3 Update `GraphExtractor` to populate default properties (`source="parser"`, `confidence=1.0`, `status="approved"`).

## 2. Deterministic Parsing Enhancements
- [x] 2.1 Update `CodeParser.parse_sql` (backed by sqlglot dialects) to extract procedure calls (`EXEC`, `sp_executesql`, function calls) across supported dialects.
- [x] 2.2 Update `CodeParser.parse_python` to extract heuristic SQL table references and relevant call/dependency information between CodeUnits.
- [x] 2.3 Update `GraphExtractor` to create `READS_FROM` / `WRITES_TO` edges for these new findings.
- [x] 2.4 Extend SQL parsing + `GraphExtractor` to support triggers, synonyms, and materialized views via sqlglot dialects (e.g., T-SQL, Postgres, MySQL), including `Trigger`, `Synonym`, and `MaterializedView` nodes and appropriate `ATTACHED_TO` / `ALIAS_OF` / `DERIVES` edges.

## 3. LLM Augmentation Service
- [x] 3.1 Create `src/services/lineage_inference.py` service shell.
- [x] 3.2 Implement `retrieve_context` to fetch subgraph + code chunks for a given scope.
- [x] 3.3 Implement `propose_edges` using Ollama JSON mode with strict schema.
- [x] 3.4 Implement `ingest_proposals` to write candidate edges to Neo4j.

## 4. Lineage Review API
- [x] 4.1 Create `POST /api/v1/lineage/review` endpoint.
- [x] 4.2 Support actions: `approve`, `reject`.
- [x] 4.3 Update `GET /api/v1/lineage/edges` to support filtering by status and confidence.

## 5. SQL Dialect Registry and API
- [x] 5.1 Add `sql_dialects` table in DuckDB (or equivalent metadata store) with fields such as `id`, `display_name`, `sqlglot_read_key`, `enabled`, `is_default`.
- [x] 5.2 Implement helpers in `CodeParser` / ingestion layer to resolve `sql_dialect` to a sqlglot dialect and pass it to `parse_sql`.
- [x] 5.3 Add `GET /api/v1/config/sql-dialects` endpoint to expose enabled dialects for the frontend.
- [x] 5.4 Update SQL ingestion endpoints to require `sql_dialect` and validate it against the registry (with an optional `"auto"` mode if supported).

## 6. Frontend Integration (stub/verification)
- [x] 6.1 Verify API endpoints work with curl/Postman.
- [ ] 6.2 (Optional) Updates to frontend are out of scope for backend change, but API must be ready.
