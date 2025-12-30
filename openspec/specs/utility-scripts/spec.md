# utility-scripts Specification

## Purpose
TBD - created by archiving change align-scripts. Update Purpose after archive.
## Requirements
### Requirement: Centralized Script Logic
Core business logic for utility scripts (exports, diagnostics, verification) SHALL be implemented in `src/` modules, ensuring scripts in the `scripts/` directory remain thin CLI wrappers.

#### Scenario: Export Graph Logic
- **WHEN** `scripts/export_graph_json.py` is executed
- **THEN** it must import and run logic from `src.utils.exporters`

#### Scenario: Verification Script Naming
- **WHEN** operational verification scripts are added to `scripts/`
- **THEN** they must use the `verify_` prefix (e.g., `verify_qdrant.py`) to avoid confusion with unit tests

