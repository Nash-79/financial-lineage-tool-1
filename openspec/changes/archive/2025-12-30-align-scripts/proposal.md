# Proposal: Align Scripts Folder

## Goal
Align the `scripts/` directory with the `src/` architecture by moving core business logic into `src/` modules and reducing scripts to thin CLI entry points. This ensures better testability and reuse.

## User Review Required
- **Naming**: Confirm if `src/utils` is the right place for export logic, or if `src/exporters` is preferred. (Proposed: `src/utils/exporters.py` and `src/utils/diagnostics.py`).
- **Tests**: `test_qdrant.py` is a manual smoke test. Proposal is to rename it to `scripts/verify_qdrant.py` to avoid confusion with `pytest` discovery.

## Proposed Changes

### Move Logic to Source
#### [NEW] [src/utils/exporters.py](file:///c:/repos/financial-lineage-tool-1/src/utils/exporters.py)
- Move `export_graph_to_json` and `export_graph_for_visualization` logic here.
- Move `export_embeddings` logic here.

#### [NEW] [src/utils/diagnostics.py](file:///c:/repos/financial-lineage-tool-1/src/utils/diagnostics.py)
- Refactor `query_neo4j.py` logic into a reusable `GraphInspector` class.
- Move `verify_qdrant.py` logic here (as `verify_qdrant_connection`).

#### [NEW] [src/ingestion/corpus.py](file:///c:/repos/financial-lineage-tool-1/src/ingestion/corpus.py)
- Move `ingest_corpus.py` logic here (file walking and ingestion orchestration).

### Refactor Scripts
#### [MODIFY] [scripts/export_graph_json.py](file:///c:/repos/financial-lineage-tool-1/scripts/export_graph_json.py)
- Reduce to ~10 lines: Import `export_graph_to_json` from `src.utils.exporters` and call it.

#### [MODIFY] [scripts/query_neo4j.py](file:///c:/repos/financial-lineage-tool-1/scripts/query_neo4j.py)
- Reduce to CLI wrapper around `GraphInspector`.

#### [MODIFY] [scripts/ingest_corpus.py](file:///c:/repos/financial-lineage-tool-1/scripts/ingest_corpus.py)
- Reduce to wrapper around `src.ingestion.corpus`.

#### [RENAME] [scripts/test_qdrant.py](file:///c:/repos/financial-lineage-tool-1/scripts/test_qdrant.py) -> `scripts/verify_qdrant.py`
- Reduce to wrapper calling `src.utils.diagnostics.verify_qdrant_connection`.

## Verification Plan
### Automated Tests
- Create unit tests for `src/utils/exporters.py`.
- Ensure `pytest` passes.

### Manual Verification
- Run `python scripts/export_graph_json.py` and verify it still works.
- Run `python scripts/verify_qdrant.py`.
- Run `python scripts/query_neo4j.py`.

## What Changes  
- Tidy up the `scripts/` directory by moving core business logic into `src/` modules and reducing scripts to thin CLI entry points. This ensures better testability and reuse.
- Collate graph database and vector database logic into `src/` modules.
- Add corpus processing logic into `src/` modules.
- Collate embedding logic into `src/` modules. 
- Collate export logic into `src/` modules.
- Collate diagnostics logic into `src/` modules.

