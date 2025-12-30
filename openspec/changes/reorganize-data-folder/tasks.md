# Tasks: Reorganize Data Folder

## 1. Folder Structure Setup
- [ ] 1.1 Create standard folder hierarchy template
- [ ] 1.2 Define folder naming conventions (kebab-case for database names)
- [ ] 1.3 Create .gitkeep files for empty folders
- [ ] 1.4 Write data folder README.md with structure explanation
- [ ] 1.5 Document folder purpose and file types for each subfolder

## 2. Migration Script Development
- [ ] 2.1 Create `scripts/migrate_data_structure.py` with dry-run mode
- [ ] 2.2 Implement detection of current data files and their types
- [ ] 2.3 Implement database name extraction from filenames
- [ ] 2.4 Add file classification logic (raw, separated, embeddings, graph, metadata)
- [ ] 2.5 Implement safe file moving with conflict detection
- [ ] 2.6 Add rollback capability in case of errors
- [ ] 2.7 Create detailed migration report (files moved, conflicts, errors)
- [ ] 2.8 Add validation step to verify all files moved correctly
- [ ] 2.9 Add command-line arguments (--dry-run, --database, --skip-backup)

## 3. Update Ingestion Pipeline
- [ ] 3.1 Update `parallel_file_watcher.py` - modify output_dir structure
- [ ] 3.2 Update `batch_processor.py` - use hierarchical paths
- [ ] 3.3 Update `enhanced_sql_parser.py` - output separated SQL to correct folders
- [ ] 3.4 Add database name detection/parameter to ingestion entry points
- [ ] 3.5 Update default path configurations in config files

## 4. Update Embedding Components
- [ ] 4.1 Update `sql_embedder.py` - output to `{db}/embeddings/sql_embeddings.json`
- [ ] 4.2 Update entity embedding output paths
- [ ] 4.3 Update sample embedding output paths
- [ ] 4.4 Add automatic folder creation before writing embeddings

## 5. Update Graph Components
- [ ] 5.1 Update `neo4j_client.py` - export graphs to `{db}/graph/` folder
- [ ] 5.2 Update Cypher query export paths
- [ ] 5.3 Update graph visualization export paths
- [ ] 5.4 Add automatic folder creation before graph exports

## 6. Update Utility Scripts
- [ ] 6.1 Update `separate_sql_file.py` - use new folder structure
- [ ] 6.2 Update any scripts that read from data folder
- [ ] 6.3 Update test fixtures to use new structure
- [ ] 6.4 Add helper functions for path construction

## 7. Configuration Updates
- [ ] 7.1 Add `DATA_ROOT` configuration option
- [ ] 7.2 Add database name configuration/detection
- [ ] 7.3 Update default paths in all config files
- [ ] 7.4 Add path validation on startup

## 8. Testing
- [ ] 8.1 Test migration script in dry-run mode
- [ ] 8.2 Test migration script on test data
- [ ] 8.3 Test full ingestion pipeline with new structure
- [ ] 8.4 Test embedding generation with new paths
- [ ] 8.5 Test graph export with new paths
- [ ] 8.6 Verify all existing tests pass
- [ ] 8.7 Add integration tests for folder structure

## 9. Documentation
- [ ] 9.1 Write data folder README.md
- [ ] 9.2 Update main README.md with folder structure section
- [ ] 9.3 Create migration guide for users
- [ ] 9.4 Document folder naming conventions
- [ ] 9.5 Add examples of correct folder structure
- [ ] 9.6 Update deployment guide with migration steps

## 10. Deployment
- [ ] 10.1 Backup existing data folder
- [ ] 10.2 Run migration script on production data
- [ ] 10.3 Validate migration completed successfully
- [ ] 10.4 Update environment variables/configs
- [ ] 10.5 Verify all services work with new structure
- [ ] 10.6 Archive old backup after validation period
