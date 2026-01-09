## 1. Implementation
- [ ] 1.1 Add ingestion log index metadata (per run) and keep it updated on completion.
- [ ] 1.2 Add /api/v1/ingestion/logs list endpoint with filters (project_id, source, status) and recent-first sorting.
- [ ] 1.3 Emit ingestion stage events (parsing, chunking, embedding, indexing, LLM) with start/complete/failed status.
- [ ] 1.4 Add unit tests for log list endpoint and stage telemetry emission.
- [ ] 1.5 Update API docs for the new list endpoint.

## 2. Validation
- [ ] 2.1 python -m pytest tests/unit/api -q
