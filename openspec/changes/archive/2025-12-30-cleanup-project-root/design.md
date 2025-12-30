# Design: Project Root Cleanup and Documentation Consolidation

## Context
The project root is cluttered with scripts, historical logs, and a heavy `README.md` that duplicates content in `docs/`. Docker services are not clearly categorized by role.

## Decisions

### 1. Single Source of Truth for Documentation
- **Decision**: The `docs/` directory is the canonical source for all detailed documentation.
- **Reason**: `README.md` in root is too long and duplicates maintenance effort. A "Landing Page" approach for root `README.md` encourages users to explore the structured docs.
- **Implementation**:
    - Extract "Quick Start" -> `docs/GETTING_STARTED.md` (or merge into `docs/LOCAL_SETUP_GUIDE.md`).
    - Extract "Detailed Features/Arch" -> Ensure covered in `docs/ARCHITECTURE.md`.
    - Root `README.md` becomes a signpost.

### 2. Docker Service Categorization
- **Context**: The project runs multiple containers. It is unclear which are "Apps" vs "Databases" vs "Tools".
- **Categories**:
    - **InfrastructureDBs**: Persistent state stores required by the system (e.g., Qdrant, Redis, Cosmos Emulator).
    - **App Services**: The actual application logic (e.g., API, Workers).
    - **Tools**: Ad-hoc or development interfaces (e.g., Jupyter, Prometheus).
- **Implementation**: Create `docs/DOCKER_SERVICES.md` to map these services to their categories and compose files.

### 3. Script Organization
- **Decision**: All scripts must reside in `scripts/`.
- **Reason**: Consistency and root cleanliness.

## Script Usage Updates
- Old: `.\check_status.ps1` -> New: `.\scripts\check_status.ps1`
- Old: `.\start_with_gremlin.bat` -> New: `.\scripts\start_with_gremlin.bat`
