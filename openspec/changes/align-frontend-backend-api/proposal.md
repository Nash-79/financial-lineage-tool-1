# Change: Align Frontend With Backend API & Improve Local Chat UX

## Why
- Frontend calls outdated endpoints (e.g., lineage `/api/lineage/*`) that 404 on the backend and force mock data.
- File upload uses hard-coded paths and static extension lists, ignoring backend-configured limits and GitHub ingest rules.
- Admin restart will be locked down in the backend; the Settings UI needs auth/flag awareness to avoid failing or issuing forbidden calls.
- Chat UX is non-streaming and cannot opt out of memory; local Ollama users need faster responses and clearer context handling.

## What Changes
- Align frontend endpoints with backend (`/api/v1/lineage/*`, configurable upload path, restart endpoint handling).
- Wire file upload UI to backend file-config (allowed extensions, max size) and use the configured upload endpoint; expose optional ingestion instructions text.
- Add restart auth/header support and graceful handling when restart is disabled or requires auth.
- Add chat streaming (SSE) option for deep mode and a skip-memory flag for faster first responses; expose a “local/Ollama” preset with guidance on context length.
- Clarify context-length expectations for Ollama models so users know when longer prompts may be truncated.

## Impact
- Affected specs: `api-endpoints`, `ui-experience`
- Affected code: `src/hooks/useLineageData.ts`, `src/pages/Files.tsx`, `src/hooks/useFiles.ts`, `src/pages/Settings.tsx`, `src/lib/api.ts`, `src/pages/Chat.tsx`
