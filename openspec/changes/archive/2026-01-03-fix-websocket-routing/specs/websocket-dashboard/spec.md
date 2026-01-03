# Spec Delta: WebSocket Dashboard Routing

## MODIFIED Requirements

### Requirement: WebSocket Dashboard Connection

System MUST provide WebSocket endpoint for real-time dashboard updates at `/admin/ws/dashboard`.

#### Scenario: Establishing WebSocket connection

- **WHEN** frontend connects to ws://127.0.0.1:8000/admin/ws/dashboard
- **THEN** backend accepts WebSocket connection
- **AND** sends connection_ack message with timestamp
- **AND** connection remains open for bidirectional communication

#### Scenario: Receiving periodic stats updates

- **WHEN** WebSocket connection is established
- **THEN** backend sends stats_update message every 5 seconds
- **AND** message contains current dashboard statistics
- **AND** statistics match /api/v1/stats endpoint data
- **AND** message includes timestamp for ordering

#### Scenario: Connection error handling

- **WHEN** WebSocket connection encounters error
- **THEN** backend logs error with connection details
- **AND** closes connection gracefully
- **AND** cleans up connection tracking resources
- **AND** frontend can reconnect immediately

#### Scenario: Client disconnection

- **WHEN** frontend closes WebSocket connection
- **THEN** backend detects disconnect event
- **AND** removes connection from active connections
- **AND** logs disconnect event
- **AND** frees associated resources

