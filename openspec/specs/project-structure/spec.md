# project-structure Specification

## Purpose
TBD - created by archiving change cleanup-project-root. Update Purpose after archive.
## Requirements
### Requirement: Centralized Documentation
All detailed project documentation SHALL be located in the `docs/` directory, with the root `README.md` serving only as a high-level landing page.

#### Scenario: User seeks documentation
- **WHEN** a user looks for "Quick Start" or "Architecture" details
- **THEN** they must be directed to `docs/` or find the files within `docs/`

### Requirement: Clean Root Directory
The project root directory SHALL containing only essential configuration files (e.g., `requirements.txt`, `.env`), entry points (e.g., `README.md`), and the `.git` directory. Utility scripts and historical artifacts SHALL be moved to `scripts/` or `docs/` respectively.

#### Scenario: Utility Script Location
- **WHEN** a utility script like `check_status.ps1` is added
- **THEN** it must be placed in `scripts/`, not the root

