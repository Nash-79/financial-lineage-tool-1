# Design: Modern React Frontend

## Context
We need a "premium" feel interface to visualize financial lineage and interact with our AI agents. The backend exists (FastAPI, Neo4j, Qdrant), but the frontend is missing. The user explicitly requested Cloudflare hosting and specific agentic capabilities.

## Architecture

### Tech Stack (Open Source / Free Tier)
- **Framework**: React 18+ with Vite (MIT).
- **Styling**: TailwindCSS (MIT).
- **UI Components**: ShadcnUI (MIT) or Radix UI (MIT). *Avoid paid UI kits.*
- **Visualization**: React Flow (MIT) or D3.js (ISC). *Ensure we stay within React Flow free tier features.*
- **State Management**: Zustand (MIT).
- **Deployment**: Cloudflare Pages (Free Tier generous limits).
- **Icons**: Lucide React (ISC).

### Component Structure
1.  **App Shell**: Sidebar navigation, header, theme toggle.
2.  **Dashboard View**:
    -   Summary cards (total nodes, files processed).
    -   Embedded Grafana iframe or API-fetched metrics.
    -   Recent files list.
3.  **Lineage View**:
    -   Canvas for graph visualization.
    -   Sidebar for node details (properties, code snippets).
4.  **Chat Interface**:
    -   Message history view.
    -   Input area with "Agent Mode" selector (Deep, Semantic, SQL, etc.).
    -   Markdown rendering for agent responses.

### API Integration
- The frontend will consume the `api` service.
- **CORS**: Backend MUST allow requests from the Cloudflare domain and `localhost`.
- **Agents**: The Chat Interface will route requests to specific backend endpoints:
    -   `/api/chat/semantic` -> `agent_semantic_search`
    -   `/api/chat/graph` -> `agent_cypher_gen`
    -   `/api/chat/deep` -> `agent_supervisor` (orchestrator)

## Goals / Non-Goals
-   **Goal**: Visual excellence ("Wow" factor), responsiveness, ease of deployment.
-   **Goal**: **Zero License Cost**. Use only Open Source (MIT/Apache/BSD) libraries and components.
-   **Non-Goal**: Re-implementing backend logic in the browser. The frontend should be a "dumb" view layer where possible.

## Risks
-   **Performance**: Visualizing huge graphs (~10k+ nodes) in the browser can be slow. *Mitigation*: Pagination, lazy loading, or WebGL-based renderers if standard DOM libraries fail.
-   **Security**: Exposing internal APIs to the public internet via Cloudflare requires auth. *Mitigation*: Assume internal tool initially, or implement Cloudflare Access / JWT auth later.

## Open Questions
-   Do we need detailed user authentication or is this an internal tool? (Assumption: Internal tool, simple auth or none for MVP).
