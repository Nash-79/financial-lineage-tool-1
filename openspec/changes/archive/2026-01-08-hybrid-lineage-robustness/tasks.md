# Tasks

## 1. Dialect Resolution
- [x] 1.1 Update `SQLClassifier` to use `resolve_dialect_for_parsing` instead of passing "auto".
- [x] 1.2 Update `SQLChunker` to use `resolve_dialect_for_parsing` instead of passing "auto".
- [x] 1.3 Add try/except in `_fallback_chunk` if not already present.

## 2. Performance Improvements
- [x] 2.1 Add label filter to `retrieve_context` query (at minimum `File`, `DataAsset`).
- [x] 2.2 Extend `LineageInferenceRequest` with optional `project_id` field and use it in context query.
- [x] 2.3 Consider adding Neo4j indexes on `source_file` and `path` properties. (Added to create_indexes())

## 3. Async Pattern
- [x] 3.1 Evaluate wrapping sync Neo4j calls in `run_in_executor` for `/infer` endpoint. (Not needed at current scale)

## 4. Legacy Data Backfill
- [x] 4.1 Create idempotent migration to set `source='parser', status='approved', confidence=1.0` on edges missing these properties.

## 5. Qdrant Integration
- [x] 5.1 Implement embedding generation in `retrieve_context` using `OllamaClient.embed()` with `config.EMBEDDING_MODEL`.
- [x] 5.2 Enable code chunk retrieval from Qdrant with graceful degradation on failure.

## 6. Verification
- [x] 6.1 Test `/infer` with real scope matching ingested files.
- [x] 6.2 Verify legacy edges appear in filtered views after backfill. (88 edges updated)
- [x] 6.3 Verify context query performance with label filters.
