# Change: Add dialect support for ingestion and disambiguate lineage edge source

## Why
The frontend needs SQL dialect selection for all ingestion paths, and the lineage edges response currently conflicts with the edge metadata `source` field, causing client graph issues.

## What Changes
- Accept and propagate SQL dialect on file upload and GitHub ingestion paths.
- Return `edge_source` in lineage edges responses to avoid clobbering node IDs.

## Impact
- Affected specs: api-endpoints
- Affected code: src/api/routers/files.py, src/api/routers/github.py, src/api/routers/lineage.py, ingestion pipeline
