# Tasks: Generic Corpus Ingestion

- [x] Core: CodeParser Enhancements @generic-ingestion
    - [x] Add `parse_python` method to `CodeParser` using `ast` @generic-ingestion
    - [x] Add `parse_json` method to `CodeParser` @generic-ingestion

- [x] Core: GraphExtractor Enhancements @generic-ingestion
    - [x] Implement `ingest_python` logic (Classes, Functions) @generic-ingestion
    - [x] Implement `ingest_json` logic @generic-ingestion
    - [x] Create `ingest_file` dispatcher method @generic-ingestion

- [x] Script: Generic Ingestion Script @generic-ingestion
    - [x] Create `scripts/ingest_corpus.py` to walk directories and call extractor @generic-ingestion
    - [x] Test with SQL files (AdventureWorks) @generic-ingestion

- [x] Cleanup @generic-ingestion
    - [x] Remove `scripts/add_adventureworks_entities.py` @generic-ingestion
    - [x] Update `docs/GETTING_STARTED.md` to reference new script @generic-ingestion
