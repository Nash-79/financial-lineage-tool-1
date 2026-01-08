# Spec Delta: Ingestion

## MODIFIED Requirements

### REQ-ING-DIALECT-001: Unified Dialect Resolution
All SQL parsing components (CodeParser, SQLClassifier, SQLChunker) SHALL use `resolve_dialect_for_parsing()` from `src/config/sql_dialects.py` to convert dialect identifiers to sqlglot-compatible values before calling sqlglot.

> [!NOTE]
> Components MAY still accept `dialect="auto"` at their public API boundary for convenience. However, they MUST only pass a concrete sqlglot dialect string (e.g., `"tsql"`, `"postgres"`) to `sqlglot.parse()` or `sqlglot.parse_one()`.

#### Scenario: Auto dialect resolution
- Given a component receives `dialect="auto"`
- When it needs to parse SQL via sqlglot
- Then it SHALL call `resolve_dialect_for_parsing("auto")` to get the default dialect
- And use the resolved value for sqlglot calls
