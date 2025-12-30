# Proposal: Generic Corpus Ingestion

## Goal
Replace the hardcoded `add_adventureworks_entities.py` script with a generic ingestion system that automatically processes any SQL (and eventually Python/JSON) files added to the corpus.

## User Review Required
- **Scope**: The initial implementation will focus on generic SQL ingestion to replace the AdventureWorks script. Python/JSON support will be scaffolded (interfaces added) but fully implemented as follow-up if complex.
- **Naming**: New script will be `scripts/ingest_corpus.py`.

## Proposed Changes
### New Generic Script
#### [NEW] [scripts/ingest_corpus.py](file:///c:/repos/financial-lineage-tool-1/scripts/ingest_corpus.py)
- Replaces `add_adventureworks_entities.py`.
- accepts `--dir` argument (default: `data/raw`).
- Recursively finds supported files.
- Uses `GraphExtractor` to ingest them.

### Extensible Parser
#### [MODIFY] [src/ingestion/code_parser.py](file:///c:/repos/financial-lineage-tool-1/src/ingestion/code_parser.py)
- **Add** `parse_python(content)`: Uses Python's `ast` to find classes, functions, and imports.
- **Add** `parse_json(content)`: Basic structure parsing.

### Generic Extractor
#### [MODIFY] [src/knowledge_graph/entity_extractor.py](file:///c:/repos/financial-lineage-tool-1/src/knowledge_graph/entity_extractor.py)
- **New Method**: `ingest_file(file_path)`
    - Detects extension (`.sql`, `.py`, `.json`).
    - Calls appropriate parser.
    - Maps parsed metadata to Graph entities (Nodes/Edges).
- **Refactor**: Generalize `ingest_sql_lineage` to share logic where possible (e.g. creating "File" nodes).

### Clean Up
#### [DELETE] [scripts/add_adventureworks_entities.py](file:///c:/repos/financial-lineage-tool-1/scripts/add_adventureworks_entities.py)
- Obsolete once generic ingestion works.

## Verification Plan
### Automated Tests
- Create a test file `tests/test_generic_ingestion.py`.
- Run `ingest_corpus.py` on a dummy directory with 1 SQL file and verify Neo4j (mocked or real) receives entites.

### Manual Verification
- Run `python scripts/ingest_corpus.py` on `data/raw/` (which contains AdventureWorks).
- Verify node counts in Neo4j match or exceed previous hardcoded counts.
