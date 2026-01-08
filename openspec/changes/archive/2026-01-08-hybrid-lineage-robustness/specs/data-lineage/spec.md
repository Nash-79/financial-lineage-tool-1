# Spec Delta: Data Lineage

## MODIFIED Requirements

### REQ-LIN-METADATA-002: Legacy Edge Backfill
Existing relationships created before hybrid lineage MUST have default metadata applied via migration:
- `source`: "parser"
- `status`: "approved"
- `confidence`: 1.0

> [!IMPORTANT]
> The migration MUST be idempotent:
> - Only set defaults when properties are missing (use `COALESCE` or `IS NULL` checks)
> - Do NOT overwrite existing `source`, `status`, `confidence` on edges that already have them
> - MUST be safe to run multiple times without side effects

#### Scenario: Backfill migration
- Given edges exist without hybrid metadata properties
- When the backfill migration runs
- Then those edges SHALL have default values set
- And they SHALL appear in filtered edge views

#### Scenario: Idempotent re-run
- Given the backfill migration has already run
- When it is run again
- Then edges with existing metadata SHALL remain unchanged
- And edges still missing metadata SHALL receive defaults
