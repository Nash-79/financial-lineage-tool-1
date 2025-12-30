# Implementation Tasks: Optimize Data Ingestion Pipeline

## 1. Parse Result Caching
- [x] 1.1 Create `src/ingestion/parse_cache.py` with `ParseCache` class
- [x] 1.2 Implement SQLite-based cache storage with schema `(file_hash TEXT PRIMARY KEY, parsed_result BLOB, created_at TIMESTAMP, schema_version INTEGER)`
- [x] 1.3 Add SHA-256 file hashing utility in `ParseCache._compute_file_hash(file_path)`
- [x] 1.4 Implement `ParseCache.get(file_hash)` and `ParseCache.set(file_hash, parsed_result)` methods
- [x] 1.5 Add LRU eviction policy (10,000 entry limit) and TTL-based cleanup (30 days)
- [x] 1.6 Integrate `ParseCache` into `EnhancedSQLParser` as optional parameter (default: None)
- [x] 1.7 Add cache health check on startup: `ParseCache.verify_integrity(sample_size=10)`
- [x] 1.8 Implement cache statistics: `ParseCache.get_stats()` returning hit/miss counts, size, entry count
- [x] 1.9 Add CLI commands: `--clear-cache`, `--cache-stats` to file watcher script
- [x] 1.10 Add environment variable `ENABLE_PARSE_CACHE` (default: true) and `PARSE_CACHE_PATH` (default: `data/.cache/parse_cache.db`)
- [x] 1.11 Write unit tests for cache hit/miss scenarios, eviction, and integrity checks

## 2. Batch File Processing
- [x] 2.1 Create `src/ingestion/batch_processor.py` with `BatchProcessor` class
- [x] 2.2 Implement event queue with timestamp tracking: `asyncio.Queue` + file path deduplication set
- [x] 2.3 Add configurable debounce timer (default: 5 seconds) via `DEBOUNCE_WINDOW_SECONDS` env var
- [x] 2.4 Implement batch flush on timer expiration using `asyncio.create_task()` with timeout
- [x] 2.5 Add batch size threshold flush (default: 50 files) via `BATCH_SIZE_THRESHOLD` env var
- [x] 2.6 Implement manual flush trigger: `BatchProcessor.flush_now()`
- [x] 2.7 Refactor `SQLFileHandler` in `file_watcher.py` to use `BatchProcessor`
- [x] 2.8 Add event coalescing: track unique file paths in set, discard duplicates within window
- [x] 2.9 Add CLI flags: `--disable-batching`, `--realtime` (sets debounce to 0)
- [x] 2.10 Add environment variable `ENABLE_BATCHING` (default: true)
- [x] 2.11 Write unit tests for batching, coalescing, flush triggers, and real-time mode

## 3. Neo4j Batch Write Operations
- [x] 3.1 Add `batch_create_entities(entities: List[dict])` method to `Neo4jGraphClient`
- [x] 3.2 Implement Cypher `UNWIND` pattern for batched node creation (max 100 per transaction)
- [x] 3.3 Add `batch_create_relationships(relationships: List[dict])` method to `Neo4jGraphClient`
- [x] 3.4 Implement Cypher `UNWIND` pattern for batched relationship creation (max 100 per transaction)
- [x] 3.5 Add batch size splitting logic: split lists > 100 into multiple batches
- [x] 3.6 Implement exponential backoff retry for transient Neo4j errors (connection timeout, deadlock) with backoff (1s, 2s, 4s, 8s, 16s max)
- [x] 3.7 Add transaction management using Neo4j driver's `write_transaction()` for ACID guarantees
- [x] 3.8 Add partial failure recovery: split failed batch into smaller sizes (100 → 50 → 10 → 1) and retry
- [x] 3.9 Create `data/failed_ingestion.jsonl` logging for entities/relationships that fail after all retries
- [x] 3.10 Update `GraphExtractor.ingest_sql_lineage()` to collect entities/relationships instead of immediate writes
- [x] 3.11 Add `GraphExtractor.flush_batch()` method to write accumulated entities and relationships to Neo4j
- [x] 3.12 Write unit tests for Neo4j batch operations, retry logic, and transaction management (use mocked Neo4j driver)
- [x] 3.13 Write integration tests for Neo4j batch operations with real Neo4j instance

## 4. Parallel Ingestion Processing
- [x] 4.1 Create `src/ingestion/worker_pool.py` with `WorkerPool` class using asyncio
- [x] 4.2 Implement priority queue: `asyncio.PriorityQueue` with priority levels (1=critical, 2=normal, 3=batch)
- [x] 4.3 Add worker pool with configurable size via `INGEST_WORKERS` env var (default: `min(4, cpu_count())`)
- [x] 4.4 Integrate `ProcessPoolExecutor` for CPU-bound SQL parsing tasks (parallel_file_watcher now uses worker_pool.executor for CPU-bound parsing)
- [x] 4.5 Refactor `SQLFileWatcher` to use `asyncio` event loop and submit tasks to `WorkerPool` (see `async_file_watcher.py` and `parallel_file_watcher.py`)
- [x] 4.6 Update `HierarchicalOrganizer.organize_file()` to work with async via `loop.run_in_executor()` (implemented in parallel_file_watcher.py)
- [ ] 4.7 Implement async Neo4j operations: `Neo4jGraphClient._execute_async()` using async Neo4j driver
- [x] 4.8 Add back-pressure handling: pause file watching if queue > 200 files or memory usage > 80%
- [x] 4.9 Add graceful shutdown: wait for pending tasks to complete on SIGTERM/SIGINT
- [x] 4.10 Write unit tests for worker pool, task prioritization, and back-pressure
- [x] 4.11 Write integration tests for end-to-end parallel processing (Note: Full file watcher tests have async cleanup issues on Windows; component integration validated via unit tests)

## 5. Performance Monitoring Metrics
- [x] 5.1 Add `src/utils/metrics.py` with Prometheus-compatible metrics exporters
- [x] 5.2 Implement counter metrics: `parse_cache_hit_total`, `parse_cache_miss_total`
- [x] 5.3 Implement histogram metrics: `batch_size_histogram`, `batch_processing_duration_seconds`
- [x] 5.4 Implement gauge metrics: `files_processed_per_second`, `total_files_processed`, `active_workers`
- [x] 5.5 Add `/metrics` API endpoint in FastAPI app to expose Prometheus metrics
- [x] 5.6 Integrate metrics collection into `ParseCache`, `BatchProcessor`, and `WorkerPool`
- [ ] 5.7 Add optional StatsD integration via `STATSD_HOST` and `STATSD_PORT` env vars
- [x] 5.8 Create Grafana dashboard JSON template in `docs/grafana/ingestion_performance.json`
- [ ] 5.9 Write documentation for metrics interpretation and performance tuning
- [ ] 5.10 Write unit tests for metrics collection and export

## 6. Configuration Management
- [ ] 6.1 Create `src/config/ingestion_config.py` with pydantic models for all ingestion settings
- [ ] 6.2 Consolidate all environment variables into `IngestionConfig` class with validation
- [ ] 6.3 Add config validation on startup: check for invalid combinations (e.g., batch size > Cosmos limit)
- [ ] 6.4 Implement config file support: load from `config/ingestion.yaml` if present
- [ ] 6.5 Add `--show-config` CLI flag to print effective configuration (with secrets masked)
- [ ] 6.6 Add `--config-file <path>` CLI flag to override default config file location
- [ ] 6.7 Write config schema documentation in `docs/configuration/ingestion.md`
- [ ] 6.8 Write unit tests for config loading, validation, and defaults

## 7. Testing & Validation
- [x] 7.1 Create `tests/performance/test_ingestion_benchmark.py` with benchmark suite
- [x] 7.2 Generate synthetic test corpus: SQL corpus generator in benchmark suite
- [x] 7.3 Implement baseline performance test: measure throughput without optimizations
- [x] 7.4 Implement optimized performance test: measure throughput with all optimizations enabled
- [x] 7.5 Assert 5x+ throughput improvement (baseline vs. optimized)
- [ ] 7.6 Create `tests/stress/test_cosmos_throttling.py` to simulate and test throttling recovery
- [ ] 7.7 Add memory profiling test: ensure memory usage stays < 1 GB for 1,000 file batch
- [ ] 7.8 Write load test script: `scripts/load_test_ingestion.py` to ingest large SQL corpus and report metrics
- [ ] 7.9 Update CI pipeline: run performance tests on PR, fail if throughput degrades > 10%
- [ ] 7.10 Write test documentation in `docs/testing/performance_tests.md`

## 8. Documentation & Examples
- [ ] 8.1 Update main README.md with performance optimization section
- [ ] 8.2 Create `docs/performance_tuning.md` with optimization guide and benchmarks
- [ ] 8.3 Add example configurations for different use cases (real-time, batch, high-throughput)
- [ ] 8.4 Document cache management operations and troubleshooting in `docs/operations/cache_management.md`
- [ ] 8.5 Create `examples/batch_ingestion_example.py` demonstrating optimized batch ingestion
- [ ] 8.6 Add flowchart diagram for optimized ingestion pipeline in `docs/architecture/ingestion_flow.mmd` (Mermaid)
- [ ] 8.7 Update API documentation with new environment variables and CLI flags
- [ ] 8.8 Write troubleshooting guide for common issues (cache corruption, throttling, memory)

## 9. Migration & Rollout
- [ ] 9.1 Create migration script: `scripts/migrate_to_optimized_ingestion.py`
- [x] 9.2 Add feature flag system: `src/config/feature_flags.py` to enable/disable optimizations individually
- [x] 9.3 Test backward compatibility: ensure old workflows continue to work with defaults
- [x] 9.4 Create rollback procedure document: `docs/operations/ROLLBACK_PROCEDURES.md`
- [x] 9.5 Update deployment documentation with optimization activation steps: `docs/operations/DEPLOYMENT_GUIDE.md`
- [ ] 9.6 Announce changes in CHANGELOG.md with performance improvement metrics
