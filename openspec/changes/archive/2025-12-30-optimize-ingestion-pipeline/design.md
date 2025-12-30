# Design: Optimize Data Ingestion Pipeline

## Context

The financial lineage tool currently processes SQL files through a multi-stage pipeline:
1. File watching (watchdog) detects new/modified files
2. Enhanced SQL parser extracts objects using regex-based comment parsing
3. Knowledge graph entities/relationships are created one-by-one in Neo4j

Key bottlenecks identified:
- **Parsing**: No caching, every file re-parsed on modification
- **Neo4j Writes**: Individual writes cause high transaction overhead and latency
- **File watching**: Each file event processed immediately, causing duplicate work
- **Orchestration**: Sequential processing, no parallelization

Target users: Data engineers ingesting 100s-1000s of SQL files into the knowledge graph.

## Goals / Non-Goals

**Goals:**
- 5-10x throughput improvement for batch ingestion of 100+ files
- 60-80% CPU reduction for file watching operations
- Handle Neo4j transaction overhead gracefully with batch writes and retry strategies
- Maintain backward compatibility (no breaking API changes)
- Support both real-time (file watching) and batch ingestion modes

**Non-Goals:**
- Distributed processing across multiple machines (out of scope)
- Change SQL parsing algorithm or grammar (optimization only)
- Modify knowledge graph schema or query patterns
- Add support for additional graph databases (Cosmos DB support deferred to future)

## Decisions

### Decision 1: File-Hash Based Parse Caching

**Choice:** Use SHA-256 file content hash as cache key with SQLite-based cache storage.

**Rationale:**
- Deterministic: Same content always produces same hash
- Collision-resistant: SHA-256 provides sufficient uniqueness
- Lightweight: SQLite provides ACID guarantees without external dependencies

**Alternatives considered:**
- File modification timestamp: Unreliable (can be manipulated, doesn't detect content changes accurately)
- In-memory LRU cache: Lost on restart, no persistence
- Redis cache: Adds external dependency, unnecessary complexity for single-machine use case

**Implementation:**
- Cache location: `data/.cache/parse_cache.db`
- Cache entry: `(file_hash TEXT PRIMARY KEY, parsed_result BLOB, created_at TIMESTAMP)`
- Cache invalidation: On file content change (hash mismatch)
- Cache eviction: LRU policy with 10,000 entry limit or 30-day TTL

### Decision 2: Batch File Processing with Configurable Debounce

**Choice:** Accumulate file change events in 5-second window, then process batch.

**Rationale:**
- Text editors generate multiple events per save (create, modify, close)
- Batching reduces redundant processing by 70-90% in typical workflows
- 5 seconds balances responsiveness vs. batch efficiency

**Alternatives considered:**
- Immediate processing: High CPU usage, duplicate work
- 1-second debounce: Still too many small batches
- 10-second+ debounce: User-perceivable delay for real-time workflows

**Implementation:**
- Queue structure: `asyncio.Queue` with timestamp tracking
- Flush triggers: (1) Timer expires (5s), (2) Queue reaches 50 files, (3) Manual flush
- Deduplication: Track file paths in set, process each unique path once per batch

### Decision 3: Neo4j Batch Write Operations

**Choice:** Implement batched write operations for Neo4j using Cypher `UNWIND` pattern with transaction batching.

**Rationale:**
- Use Cypher `UNWIND` with transaction batching to create multiple nodes/relationships per transaction
- Reduces round-trip network latency from N requests to 1 request per batch
- Amortizes transaction overhead across batch, improving throughput significantly
- Neo4j handles large batches (100+ items) efficiently in a single transaction

**Alternatives considered:**
- Neo4j APOC batching: Adds dependency, not always available in managed Neo4j services
- Parallel requests with connection pooling: Still triggers rate limiting, higher latency
- Individual writes with connection pooling: Minimal improvement, high overhead

**Implementation:**
- Batch size: 100 entities or 100 relationships per transaction (Neo4j handles larger batches efficiently)
- Query pattern (Cypher with UNWIND):
  ```cypher
  UNWIND $entities AS entity
  CREATE (n:Table {id: entity.id, name: entity.name, schema: entity.schema})
  ```
- Retry strategy: Exponential backoff (1s, 2s, 4s, 8s, 16s max) on transient errors (connection timeout, deadlock)
- Transaction management: Use Neo4j driver session with `write_transaction()` for ACID guarantees
- Partial failure recovery: Re-run failed batch with smaller batch size (100 → 50 → 10 → 1)

### Decision 4: Async Parallel Processing with Worker Pool

**Choice:** Use `asyncio` with configurable worker pool (default: 4 workers).

**Rationale:**
- SQL parsing is CPU-bound, but file I/O and graph DB calls are I/O-bound
- `asyncio` enables efficient concurrent I/O without thread overhead
- Worker pool prevents resource exhaustion (CPU/memory/network)

**Alternatives considered:**
- `multiprocessing`: Higher overhead, complex IPC, harder to debug
- Threading: GIL limits CPU-bound parsing parallelism
- Single-threaded with async only: Underutilizes CPU for parsing

**Implementation:**
- Hybrid approach: `asyncio` event loop with `ProcessPoolExecutor` for CPU-bound parsing
- Worker pool size: Configurable via env var `INGEST_WORKERS` (default: `min(4, CPU_count)`)
- Task prioritization: Priority queue (1=critical, 2=normal, 3=batch)
  - Critical: User-triggered ingestion via API
  - Normal: Real-time file watching
  - Batch: Bulk historical ingestion

## Risks / Trade-offs

**Risk 1: Cache Invalidation Bugs**
- **Impact:** Stale parse results if hash collision or cache corruption
- **Mitigation:**
  - Use SHA-256 (collision probability negligible)
  - Add cache health check on startup (verify 10 random entries)
  - Provide `--clear-cache` flag for manual invalidation

**Risk 2: Neo4j Batch Transaction Failures**
- **Impact:** Entire batch fails if one entity/relationship is malformed
- **Mitigation:**
  - Validate all entities/relationships before batching (schema validation with Pydantic)
  - Implement partial failure recovery (split batch and retry)
  - Log failed entities to `data/failed_ingestion.jsonl` for manual review
  - Use Neo4j transaction rollback and individual entity validation
  - Implement progressive batch size reduction on failures (100 → 50 → 10 → 1)

**Risk 3: Increased Memory Usage**
- **Impact:** Batch processing holds more data in memory (50 files × ~10 MB = 500 MB)
- **Mitigation:**
  - Cap batch size at 50 files or 500 MB total
  - Stream large files (>100 MB) without full load into memory
  - Monitor memory usage, add back-pressure if approaching limit

**Trade-off: Latency vs. Throughput**
- Batching increases latency for individual files (5s debounce delay)
- Acceptable for batch ingestion, less ideal for real-time use cases
- **Resolution:** Add `--realtime` flag to disable batching (0s debounce) for latency-sensitive workflows

## Migration Plan

**Phase 1: Backward-Compatible Addition (Week 1-2)**
1. Add `ParseCache` class to `src/ingestion/parse_cache.py`
2. Update `EnhancedSQLParser` with optional cache parameter (default: None, disabled)
3. Add `BatchProcessor` to `src/ingestion/batch_processor.py`
4. Add `--enable-cache` and `--enable-batching` CLI flags (opt-in)

**Phase 2: Cosmos DB Batch Operations (Week 2-3)**
1. Add `batch_create_entities()` and `batch_create_relationships()` to `CosmosGremlinClient`
2. Update `GraphExtractor.ingest_sql_lineage()` to collect entities/relationships
3. Add `flush_batch()` method to write collected data

**Phase 3: Async Worker Pool (Week 3-4)**
1. Refactor `SQLFileWatcher` to use `asyncio` event loop
2. Add `WorkerPool` class with priority queue
3. Update `HierarchicalOrganizer` to return async tasks

**Phase 4: Default Enable & Testing (Week 4-5)**
1. Change defaults: cache=enabled, batching=enabled
2. Performance benchmarking (compare before/after metrics)
3. Load testing with 1,000+ file corpus
4. Update documentation with performance tuning guide

**Rollback Strategy:**
- All optimizations behind feature flags (can disable individually)
- Cache can be cleared/disabled without data loss
- Batch mode can revert to sequential mode via config

## Open Questions

1. **Q:** Should we add metrics/telemetry for cache hit rate and batch efficiency?
   - **A:** Yes, add Prometheus-compatible metrics endpoint (`/metrics`) with:
     - `parse_cache_hit_total`, `parse_cache_miss_total`
     - `batch_size_histogram`, `batch_processing_duration_seconds`

2. **Q:** How to handle schema evolution in cache (e.g., parser output format changes)?
   - **A:** Add schema version to cache entry, invalidate all entries on version mismatch

3. **Q:** Should batch size be auto-tuned based on Cosmos DB throttling feedback?
   - **A:** Nice-to-have for future iteration. Start with fixed batch size, add adaptive batching in Phase 5 if needed.
