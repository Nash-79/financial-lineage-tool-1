# Implementation Tasks

## 1. Endpoint Alignment
- [ ] 1.1 Update lineage fetch/search/node calls to `/api/v1/lineage/*` (configurable via Settings endpoints).
- [ ] 1.2 Use configured upload endpoint from Settings for file uploads.
- [ ] 1.3 Add restart auth/header support; handle 401/403/404/disabled states gracefully.

## 2. File Upload UX
- [ ] 2.1 Fetch allowed extensions/max size from `/api/v1/files/config` and enforce them in the uploader accept list and client-side validation.
- [ ] 2.2 Add optional “ingestion instructions” text/markdown to accompany uploads (persist via existing upload or a new metadata field if available).

## 3. Chat Performance & Context
- [ ] 3.1 Add SSE streaming option for deep chat (`/api/chat/deep/stream`) with UI toggle.
- [ ] 3.2 Add skip-memory flag toggle for faster first responses; pass through to backend.
- [ ] 3.3 Surface “local/Ollama mode” guidance: context-length expectations and model hints when users choose streaming/skip-memory.

## 4. Validation
- [ ] 4.1 Run `openspec validate align-frontend-backend-api --strict`.
