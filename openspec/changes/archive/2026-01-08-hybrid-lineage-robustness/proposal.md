# Change: Hybrid Lineage Robustness Improvements

## Why
The hybrid lineage system is functional, but several robustness and performance improvements were identified during implementation:

1. **Dialect "auto" handling**: `SQLClassifier` and `SQLChunker` pass `dialect="auto"` directly to sqlglot, which doesn't support it. Exception fallbacks work but are not ideal.
2. **Context query performance**: `LineageInferenceService.retrieve_context` does a full graph scan (`MATCH (n)`) without label/project filters.
3. **Sync Neo4j calls**: Async endpoints call sync Neo4j methods, potentially blocking the event loop.
4. **Legacy edge metadata**: Edges created before hybrid lineage lack `source`, `status`, `confidence` properties.
5. **Qdrant integration**: Code chunk retrieval is currently disabled (requires embedding generation).

## What Changes
- **Dialect Resolution**: Use `resolve_dialect_for_parsing` in `SQLClassifier` and `SQLChunker`.
- **Context Query**: Add label/project filters and indexes to `retrieve_context`.
- **Async Pattern**: Consider `run_in_executor` for sync Neo4j calls.
- **Backfill Migration**: Add default metadata to existing relationships.
- **Qdrant Search**: Implement embedding generation for code chunk context.

## Impact
- **Performance**: Faster inference queries, non-blocking async.
- **Robustness**: Consistent dialect handling across components.
- **UX**: Legacy edges visible in filtered views.
