# Proposal: Fix WebSocket Dashboard Routing

## Why

Frontend diagnostic logs show WebSocket connections failing with error code 1006 (Abnormal Closure). The root cause is a routing mismatch between frontend expectations and backend implementation:

**Frontend expects**: `ws://127.0.0.1:8000/ws/dashboard`  
**Backend provides**: `/api/v1/ws/dashboard`

This prevents the dashboard from receiving real-time updates, breaking a core user experience feature.

## Problem Statement

Frontend diagnostic logs reveal that the WebSocket connection to the dashboard is failing with error code 1006 (Abnormal Closure). Analysis shows a routing mismatch:

- **Frontend expects**: `ws://127.0.0.1:8000/ws/dashboard`
- **Backend provides**: `/api/v1/ws/dashboard` (due to router prefix)

The WebSocket endpoint is defined on the `router` with prefix `/api/v1` (line 22 of `admin.py`), but the frontend is configured to connect without this prefix.

## Root Cause

In `src/api/routers/admin.py`:
```python
router = APIRouter(prefix="/api/v1", tags=["admin"])  # Line 22
# ...
@router.websocket("/ws/dashboard")  # Line 377 - Results in /api/v1/ws/dashboard
```

The WebSocket decorator applies to `router` which has the `/api/v1` prefix, making the full path `/api/v1/ws/dashboard`. However, the frontend configuration (and the websocket-dashboard spec) expects the endpoint at `/ws/dashboard`.

## Proposed Solution

**Option 1: Move WebSocket to admin_router (Recommended)**

Move the WebSocket endpoint from `router` to `admin_router` which has prefix `/admin`:

```python
admin_router = APIRouter(prefix="/admin", tags=["admin"])  # Line 23

@admin_router.websocket("/ws/dashboard")  # Results in /admin/ws/dashboard
```

**Option 2: Update to correct prefix-less router**

There's already an `admin_router` with `/admin` prefix. We need a router without prefix for dashboard WebSocket to match the spec requirement of `/ws/dashboard`.

**Recommended: Option 1 with spec update + Config Endpoint**

Since `/admin/ws/dashboard` is more semantically correct (it's an admin feature), we should:
1. Move WebSocket to `admin_router` 
2. Create a backend config endpoint that returns the WebSocket URL
3. Update the `websocket-dashboard` spec to use `/admin/ws/dashboard`
4. Frontend can dynamically retrieve WebSocket URL from config endpoint

## Impact Analysis

### Breaking Changes
- Frontend must update WebSocket connection URL
- Any existing clients connecting to WebSocket will need to update their configuration

### Benefits
- Fixes frontend connection issue
- Aligns routing with semantic grouping (admin endpoints under `/admin`)
- Consistent with REST API organization

## Implementation Plan

1. **Backend Routing**: Move `@router.websocket` to `@admin_router.websocket`
2. **Backend Config Endpoint**: Add `GET /api/v1/config/websocket` that returns WebSocket URL
3. **Spec Updates**: 
   - Modify `websocket-dashboard/spec.md` to reflect `/admin/ws/dashboard`
   - Add `api-endpoints/spec.md` delta for new config endpoint
4. **Testing**: Verify WebSocket connection with frontend diagnostic tools
5. **Documentation**: Update API docs if needed

## Verification

Use frontend diagnostic tools to confirm:
```
GET http://127.0.0.1:8000/admin/ws/dashboard (WebSocket upgrade)
Expected: Connection successful (code 101 Switching Protocols)
```

## Related Changes

- None required (this is a routing fix only)

## User Review Required

> [!IMPORTANT]
> **Decision Required**: Should the WebSocket endpoint be at:
> - `/admin/ws/dashboard` (recommended - groups with admin features)
> - `/ws/dashboard` (matches current spec but requires new router)
>
> This decision affects frontend configuration.
