# Design: Scripts Alignment

## Context
Currently, `scripts/` contains significant implementation logic. This makes unit testing hard (cannot import script easily) and confuses the "application code" boundary.

## Decisions

### 1. `src` is for Logic, `scripts` is for Execution
- **Pattern**: `scripts/foo.py` should look like:
  ```python
  from src.some_module import run_foo
  if __name__ == "__main__":
      run_foo()
  ```
- **Benefit**: The logic `run_foo` can be imported by API endpoints, other tools, or tests.

### 2. New Modules
- `src.utils.exporters`: Handles data export formats (JSON, D3, etc).
- `src.utils.diagnostics`: Handles interactive checks and status reporting.

### 3. Verification Scripts
- Operational checks (like checking if Qdrant is up) remain in `scripts/` but are named `verify_*.py` to clearly distinguish them from the test suite.

## Impact
- **Refactor**: existing scripts will become much smaller.
- **Imports**: Scripts must rely on the package structure functioning (running from root).
