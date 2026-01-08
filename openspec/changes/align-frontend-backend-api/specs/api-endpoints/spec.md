## MODIFIED Requirements
### Requirement: Frontend SHALL use correct backend API routes
The system SHALL configure frontend API calls to match backend routes and handle secured endpoints.

#### Scenario: Lineage endpoints use /api/v1
- **WHEN** the frontend fetches lineage nodes/search/node lineage
- **THEN** it calls `/api/v1/lineage/nodes`, `/api/v1/lineage/edges`, `/api/v1/lineage/search`, `/api/v1/lineage/node/{id}`
- **AND** endpoints are configurable via Settings
- **AND** requests return live data instead of mock fallbacks

#### Scenario: Upload endpoint is configurable
- **WHEN** the frontend uploads files
- **THEN** it uses the configured upload endpoint from Settings (default `/api/v1/files/upload`)
- **AND** respects allowed extensions and size from backend config before sending

#### Scenario: Restart endpoint respects auth/flags
- **WHEN** the frontend tests or triggers `/admin/restart`
- **THEN** it includes configured auth headers/tokens if required
- **AND** handles 401/403/404/disabled responses gracefully without retry loops
- **AND** hides or disables restart controls when backend reports it as restricted
