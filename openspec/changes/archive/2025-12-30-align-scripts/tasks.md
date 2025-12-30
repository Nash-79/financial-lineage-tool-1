# Tasks: Align Scripts Folder

- [x] Create Core Modules @align-scripts
    - [x] Create `src/utils/exporters.py` @align-scripts
    - [x] Create `src/utils/diagnostics.py` @align-scripts

- [x] Refactor Exports @align-scripts
    - [x] Move `export_graph_json.py` logic to `src/utils/exporters.py` @align-scripts
    - [x] Update `scripts/export_graph_json.py` to be a wrapper @align-scripts
    - [x] Move `export_embeddings_json.py` logic to `src/utils/exporters.py` @align-scripts
    - [x] Update `scripts/export_embeddings_json.py` to be a wrapper @align-scripts

- [x] Refactor Diagnostics @align-scripts
    - [x] Move `query_neo4j.py` logic to `src/utils/diagnostics.py` @align-scripts
    - [x] Update `scripts/query_neo4j.py` to be a wrapper @align-scripts
    - [x] Rename `scripts/test_qdrant.py` to `scripts/verify_qdrant.py` @align-scripts
    - [x] Move `verify_qdrant.py` logic to `src/utils/diagnostics.py` <!-- id: 624 -->
    - [x] Update `scripts/verify_qdrant.py` to be a wrapper <!-- id: 625 -->

- [x] Refactor Ingestion @align-scripts
    - [x] Create `src/ingestion/corpus.py` (move `ingest_corpus` logic) <!-- id: 650 -->
    - [x] Update `scripts/ingest_corpus.py` to be a wrapper <!-- id: 651 -->

- [x] Verification @align-scripts
    - [x] Verify functionality of all refactored scripts @align-scripts
