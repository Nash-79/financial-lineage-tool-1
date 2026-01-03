# Spec Delta: API Endpoints - Upload Settings Persistence

## Category
api-endpoints

## MODIFIED Requirements

### Requirement: File upload configuration MUST persist across restarts

File upload settings (allowed extensions, file size limits) configured via the API MUST be stored in the database and survive server restarts.

#### Scenario: Admin updates allowed file extensions

**Given** the server is running with default settings  
**When** an admin calls `PUT /files/config` with `allowed_extensions: [".sql", ".py", ".json"]`  
**Then** the settings are saved to the `upload_settings` table in DuckDB  
**And** the response confirms persistence with `{"persisted": true, "last_updated": "2026-01-02T21:00:00Z"}`  
**And** subsequent server restarts load these settings from the database

#### Scenario: Settings loaded from database on startup

**Given** upload settings exist in the database  
**When** the server starts  
**Then** settings are loaded from the `upload_settings` table  
**And** these settings override environment variable defaults  
**And** `GET /files/config` returns `{"source": "database"}`

#### Scenario: First-time startup uses environment variables

**Given** no upload settings exist in the database (first run)  
**When** the server starts  
**Then** settings are loaded from environment variables  
**And** these settings are saved to the database as defaults  
**And** `GET /files/config` returns `{"source": "environment"}`

### Requirement: Upload configuration endpoint MUST indicate persistence status

The `GET /files/config` endpoint MUST clearly indicate whether settings are persisted and when they were last updated.

#### Scenario: Get current upload configuration

**Given** settings have been persisted to the database  
**When** a client calls `GET /files/config`  
**Then** the response includes:
```json
{
  "allowed_extensions": [".sql", ".py"],
  "max_file_size_mb": 50,
  "max_file_size_bytes": 52428800,
  "persisted": true,
  "last_updated": "2026-01-02T21:00:00Z",
  "source": "database"
}
```

## Rationale

Currently, `PUT /files/config` updates settings in memory only, causing them to reset on restart. This creates operational issues where admins must reconfigure settings after every deployment. Persisting to DuckDB provides:

1. **Durability**: Settings survive restarts and deployments
2. **Audit Trail**: Track when settings changed
3. **Single Source of Truth**: Database becomes authoritative for runtime config
4. **Backward Compatibility**: Environment variables still work as defaults

This aligns with user expectations that API-configured settings should persist.
