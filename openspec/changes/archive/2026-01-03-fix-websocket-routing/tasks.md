# Tasks: Fix WebSocket Dashboard Routing

## Phase 1: Analysis ✅ COMPLETED  
- [x] 1.1 Review frontend diagnostic logs
- [x] 1.2 Identify WebSocket routing mismatch
- [x] 1.3 Verify backend endpoint path
- [x] 1.4 Review websocket-dashboard spec

## Phase 2: Backend Fix ✅ COMPLETED
- [x] 2.1 Move WebSocket from `router` to `admin_router` in `src/api/routers/admin.py`
- [x] 2.2 Verify WebSocket now at `/admin/ws/dashboard`
- [x] 2.3 Test endpoint accessibility

## Phase 2.5: WebSocket Config Endpoint ✅ COMPLETED
- [x] 2.5.1 Create `GET /api/v1/config/websocket` endpoint
- [x] 2.5.2 Add `WEBSOCKET_URL` environment variable to config
- [x] 2.5.3 Set default value to `ws://127.0.0.1:8000/admin/ws/dashboard`
- [x] 2.5.4 Test endpoint returns correct URL

## Phase 3: Spec Delta ✅ COMPLETED
- [x] 3.1 Create spec delta in `specs/websocket-dashboard/spec.md`
- [x] 3.2 Update WebSocket URL requirement to `/admin/ws/dashboard`
- [x] 3.3 Validate spec with `openspec validate --strict`

## Phase 4: Verification
- [x] 4.1 Restart backend container
- [ ] 4.2 Update frontend configuration to use `/admin/ws/dashboard`
- [ ] 4.3 Run frontend diagnostic connection test
- [ ] 4.4 Confirm WebSocket connects successfully

## Phase 5: Documentation
- [ ] 5.1 Update API documentation if needed
- [ ] 5.2 Note breaking change for frontend

## Success Criteria
- ✅ WebSocket endpoint accessible
- ✅ Frontend diagnostic shows successful connection
- ✅ No code 1006 errors
- ✅ Spec validation passes
