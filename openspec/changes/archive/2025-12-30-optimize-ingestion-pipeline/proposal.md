# Change: Optimize Data Ingestion Pipeline Performance

## Why

The current data ingestion pipeline processes SQL files sequentially with no batching, caching, or parallelization. This leads to:
- Slow processing of large SQL files (100+ MB)
- High CPU usage from watchdog monitoring and repeated file operations
- Inefficient Neo4j writes (one-by-one entity/relationship creation with high transaction overhead)
- Redundant SQL parsing for unchanged files

This optimization improves throughput 5-10x for batch ingestion and reduces resource consumption for real-time file watching.

## What Changes

- **SQL Parsing Performance**: Add parse result caching with file hash-based invalidation to avoid re-parsing unchanged files
- **File Watching Efficiency**: Implement batch processing with configurable debounce window, add file change event coalescing to reduce duplicate processing
- **Graph Insertion Throughput**: Add batch write operations for Neo4j (batch entity/edge creation using Cypher UNWIND), implement transaction batching and retry strategies with exponential backoff
- **Pipeline Orchestration**: Parallelize independent parsing operations using asyncio/multiprocessing, add work queue with priority levels for critical vs. batch ingestion, improve error handling and partial failure recovery

## Impact

- Affected specs: None yet defined (new capability)
- Affected code:
  - `src/ingestion/enhanced_sql_parser.py` - add caching layer
  - `src/ingestion/file_watcher.py` - add batch processing and event coalescing
  - `src/knowledge_graph/neo4j_client.py` - add batch operations
  - `src/knowledge_graph/entity_extractor.py` - refactor for async batch ingestion
- Breaking changes: None (backward-compatible enhancements)
- Performance impact: Expected 5-10x throughput improvement for batch operations, 60-80% reduction in CPU usage for file watching
- Scope: Neo4j only (Cosmos DB support deferred to future iteration)
