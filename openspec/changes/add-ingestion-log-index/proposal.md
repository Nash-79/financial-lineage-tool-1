# Change: Add Ingestion Log Index and Pipeline Stage Telemetry

## Why
Users need a centralized log page that lists ingestion runs and exposes pipeline stage details (parsing, chunking, embedding, indexing, LLM calls). Today the system only stores per-session JSONL logs without a list endpoint or rich stage events, which makes troubleshooting difficult.

## What Changes
- Persist a lightweight ingestion log index per run with metadata (source, filenames, status, timestamps) for fast listing.
- Add GET /api/v1/ingestion/logs to list ingestion sessions with filters (project, source, status) and ordering by most recent.
- Emit structured stage events for parsing, chunking, embedding, indexing, and LLM calls into the ingestion log.

## Impact
- Affected specs: logging, api-endpoints
- Affected code: src/services/ingestion_tracker.py, src/api/routers/ingestion_logs.py, ingestion pipeline modules
