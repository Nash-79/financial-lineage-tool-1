# Spec Delta: WebSocket Configuration Endpoint

## ADDED Requirements

### Requirement: WebSocket Configuration Endpoint

System MUST provide an endpoint that returns the WebSocket URL for frontend clients.

#### Scenario: Retrieving WebSocket configuration

- **WHEN** frontend requests WebSocket configuration
- **THEN** backend returns GET /api/v1/config/websocket endpoint
- **AND** response includes WebSocket URL as string
- **AND** response status is 200 OK

#### Scenario: Environment-specific WebSocket URL

- **WHEN** application runs in different environments (local, staging, production)
- **THEN** WebSocket URL MUST reflect the current environment
- **AND** URL MUST be configurable via environment variable
- **AND** default value for local development is ws://127.0.0.1:8000/admin/ws/dashboard

#### Scenario: Frontend discovers WebSocket URL dynamically

- **WHEN** frontend application initializes
- **THEN** frontend MUST call /api/v1/config/websocket to get WebSocket URL
- **AND** frontend uses returned URL for WebSocket connections
- **AND** frontend does not hardcode WebSocket URL
