# ingestion-pipeline Specification

## Purpose
TBD - created by archiving change optimize-ingestion-pipeline. Update Purpose after archive.
## Requirements
### Requirement: Parse Result Caching
The system SHALL cache SQL parsing results using file content hash as the cache key to avoid redundant parsing of unchanged files.

#### Scenario: Cache hit for unchanged file
- **WHEN** a SQL file is processed and its content hash matches a cached entry
- **THEN** the system MUST return the cached parse result without re-parsing the file

#### Scenario: Cache miss for new or modified file
- **WHEN** a SQL file is processed and its content hash does not match any cached entry
- **THEN** the system MUST parse the file and store the result in cache with the file hash as key

#### Scenario: Cache invalidation on content change
- **WHEN** a SQL file is modified and its content hash changes
- **THEN** the system MUST invalidate the old cache entry and create a new entry with the updated hash and parse result

#### Scenario: Cache storage persistence
- **WHEN** the ingestion system restarts
- **THEN** the system MUST retain all cached parse results from previous sessions (persistent SQLite storage)

### Requirement: Batch File Processing
The system SHALL accumulate file change events in a configurable debounce window and process them as a batch to reduce redundant operations.

#### Scenario: Multiple events for same file coalesced
- **WHEN** a file triggers multiple change events within the debounce window (e.g., editor save generates create + modify + close)
- **THEN** the system MUST process the file exactly once after the debounce window expires

#### Scenario: Batch flush on timer expiration
- **WHEN** the debounce timer expires (default: 5 seconds) and there are pending file events
- **THEN** the system MUST process all accumulated unique file paths as a batch

#### Scenario: Batch flush on queue size threshold
- **WHEN** the pending file event queue reaches the configured threshold (default: 50 files)
- **THEN** the system MUST immediately process all accumulated file paths as a batch, regardless of debounce timer

#### Scenario: Manual batch flush trigger
- **WHEN** a manual flush is triggered via API or CLI command
- **THEN** the system MUST immediately process all pending file events, regardless of debounce timer or queue size

### Requirement: Neo4j Batch Write Operations
The system SHALL batch multiple entity and relationship create operations to reduce network round-trips and improve throughput for Neo4j.

#### Scenario: Batch entity creation
- **WHEN** multiple entities (≤ 100) are ready to be written to Neo4j
- **THEN** the system MUST combine them into a single Cypher query using `UNWIND` pattern and execute in one transaction

#### Scenario: Batch relationship creation
- **WHEN** multiple relationships (≤ 100) are ready to be written to Neo4j
- **THEN** the system MUST combine them into a single Cypher query using `UNWIND` pattern and execute in one transaction

#### Scenario: Batch size limit enforcement
- **WHEN** more than 100 entities or relationships need to be written to Neo4j
- **THEN** the system MUST split them into multiple batches of maximum 100 items each

#### Scenario: Transient error retry with exponential backoff
- **WHEN** a Neo4j write transaction fails with a transient error (connection timeout, deadlock)
- **THEN** the system MUST retry the transaction with exponential backoff (1s, 2s, 4s, 8s, 16s max) up to 5 attempts

#### Scenario: Partial batch failure recovery
- **WHEN** a batch write fails and cannot be retried successfully
- **THEN** the system MUST split the batch into smaller sizes (100 → 50 → 10 → 1) and retry each sub-batch

#### Scenario: Failed entity logging
- **WHEN** an entity or relationship fails to write after all retry attempts
- **THEN** the system MUST log the failed item to `data/failed_ingestion.jsonl` with timestamp, error message, and full entity/relationship data

### Requirement: Parallel Ingestion Processing
The system SHALL process independent SQL files in parallel using an async worker pool to maximize CPU and I/O utilization.

#### Scenario: Concurrent file parsing
- **WHEN** multiple SQL files are queued for ingestion
- **THEN** the system MUST parse up to N files concurrently (default: 4, configurable via `INGEST_WORKERS` env var)

#### Scenario: Async I/O for Neo4j operations
- **WHEN** file parsing completes and graph entities are ready for ingestion
- **THEN** the system MUST use async I/O to write to Neo4j without blocking other workers

#### Scenario: CPU-bound parsing offloading
- **WHEN** SQL parsing is performed (CPU-intensive regex operations)
- **THEN** the system MUST offload parsing to a ProcessPoolExecutor to avoid blocking the asyncio event loop

#### Scenario: Priority queue processing
- **WHEN** ingestion tasks are added to the work queue with different priority levels (1=critical, 2=normal, 3=batch)
- **THEN** the system MUST process higher-priority tasks before lower-priority tasks

### Requirement: Ingestion Performance Monitoring
The system SHALL expose metrics for cache performance, batch efficiency, and throughput to enable performance tuning and monitoring.

#### Scenario: Cache hit rate metrics
- **WHEN** the metrics endpoint is queried
- **THEN** the system MUST report total cache hits and misses (`parse_cache_hit_total`, `parse_cache_miss_total`)

#### Scenario: Batch processing metrics
- **WHEN** the metrics endpoint is queried
- **THEN** the system MUST report batch size histogram and processing duration (`batch_size_histogram`, `batch_processing_duration_seconds`)

#### Scenario: Ingestion throughput metrics
- **WHEN** the metrics endpoint is queried
- **THEN** the system MUST report files processed per second and total ingestion time

### Requirement: Cache Management Operations
The system SHALL provide operations to manage the parse cache, including inspection, clearing, and health checks.

#### Scenario: Cache statistics retrieval
- **WHEN** a user queries cache statistics
- **THEN** the system MUST return total entries, cache size (MB), oldest entry timestamp, and hit rate

#### Scenario: Manual cache clearing
- **WHEN** a user executes the `--clear-cache` command
- **THEN** the system MUST delete all cached parse results and confirm deletion count

#### Scenario: Cache health check on startup
- **WHEN** the ingestion system starts
- **THEN** the system MUST verify cache integrity by validating 10 random cache entries (check hash matches re-parsed content)

### Requirement: Backward Compatibility Configuration
The system SHALL support disabling all optimizations via configuration flags to ensure backward compatibility and troubleshooting.

#### Scenario: Disable parse caching
- **WHEN** the `--disable-cache` flag is set or `ENABLE_PARSE_CACHE=false` env var
- **THEN** the system MUST bypass cache and always parse files directly

#### Scenario: Disable batch processing
- **WHEN** the `--disable-batching` flag is set or `ENABLE_BATCHING=false` env var
- **THEN** the system MUST process file events immediately without debounce or batching

#### Scenario: Real-time mode (zero latency)
- **WHEN** the `--realtime` flag is set
- **THEN** the system MUST set debounce window to 0 seconds and process files immediately for latency-sensitive workflows

