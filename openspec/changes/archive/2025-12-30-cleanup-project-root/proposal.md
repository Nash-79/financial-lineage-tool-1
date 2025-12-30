# Proposal: Clean up project root directory

## Goal
Reduce clutter in the project root directory, centralize documentation into the `docs/` folder, and clearly categorize Docker application runs.

## User Review Required
- Confirm if `CLEANUP_SUMMARY.md` needs to be archived or if deletion is acceptable.
- Confirm if `check_status.ps1` and `start_with_gremlin.bat` can be safely moved to `scripts/`.
- Review the new Documentation Structure plan.

## Proposed Changes
### Documentation Consolidation
#### [MODIFY] [README.md](file:///c:/repos/financial-lineage-tool-1/README.md)
- **Goal**: Minimize root README to a landing page.
- **Action**: Move detailed "features", "Quick Start", "Project Structure" sections to `docs/GETTING_STARTED.md` or `docs/ARCHITECTURE.md`.
- **Result**: Root README contains only:
    - High-level Project Description.
    - Link to `docs/README.md` (Index).
    - Very brief "Quick Start" (1-2 commands or link to guide).
    - License/Status.

#### [NEW] [docs/DOCKER_SERVICES.md](file:///c:/repos/financial-lineage-tool-1/docs/DOCKER_SERVICES.md)
- **Goal**: Categorize and document Docker services.
- **Content**:
    - **InfrastructureDBs**: cosmos-gremlin, qdrant, redis (Backing services).
    - **App Services**: api, ingestion-worker, supervisor-agent (Core business logic).
    - **Tools**: file-watcher, jupyter (Dev/Ops tools).
    - Differentiate between `docker-compose.yml` (Azure-integrated) and `docker-compose.local.yml` (Local execution).

#### [MODIFY] [AGENTS.md](file:///c:/repos/financial-lineage-tool-1/AGENTS.md)
- **Action**: If content is identical to `openspec/AGENTS.md`, replace with a pointer or remove if `openspec` is the primary source. (Decision: Keep as pointer).

### Root Directory Cleanup
#### [DELETE] [CLEANUP_SUMMARY.md](file:///c:/repos/financial-lineage-tool-1/CLEANUP_SUMMARY.md)
- Historical clutter.

#### [DELETE] [nul](file:///c:/repos/financial-lineage-tool-1/nul)
- Erroneous file.

#### [MOVE] [check_status.ps1](file:///c:/repos/financial-lineage-tool-1/check_status.ps1) -> `scripts/check_status.ps1`
- Move utility script.

#### [MOVE] [start_with_gremlin.bat](file:///c:/repos/financial-lineage-tool-1/start_with_gremlin.bat) -> `scripts/start_with_gremlin.bat`
- Move utility script.

## Verification Plan
### Manual Verification
- Check links in `README.md` (root) work.
- Verify `docs/` structure is clean and navigable.
- Run moved scripts from new location.
