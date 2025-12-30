# Change: Create Modern React Frontend

## Why
The current tool lacks a user-friendly interface for interacting with the financial lineage graph, viewing outputs, and executing complex searches. Users currently rely on scripts and raw database queries. A dedicated, modern web application is needed to democratize access to the lineage data, enable intuitive visualization of complex transformations, and provide a conversational interface for multi-modal search agents.

## What Changes
- **New Frontend Application**: A standalone React application built with Vite and TailwindCSS.
- **Hosting**: Configured for deployment on Cloudflare Pages.
- **Core Features**:
    - **Dashboard**: View ingested files, system status, and embedded Grafana metrics.
    - **Lineage Visualization**: Interactive graph visualization (nodes, edges, transformations) using libraries like React Flow or D3.js.
    - **Agentic Chat Interface**: A premium chatbot experience supporting:
        - **Deep Search**: Recursive graph exploration.
        - **Semantic Search**: Vector-based queries using the Qdrant backend.
        - **Text Search**: Keyword matching.
        - **Natural Language to Graph**: Converting user questions into Cypher queries.
- **Architecture**: Decoupled Single Page Application (SPA) consuming the existing Python Backend API.
- **Constraints**: All selected libraries/tools must be Open Source (MIT/Apache) or have a permanent free tier (like Cloudflare Pages) to ensure zero licensing costs.

## Impact
- **New Capability**: `frontend-app` (Entirely new spec).
- **New Codebase**: `frontend/` directory requiring new build pipelines.
- **Infrastructure**: Requires Cloudflare configuration and potentially CORS updates on the backend API.
- **User Experience**: Shifts from CLI/Script-based interaction to a GUI-based workflow.

## Success Criteria
- [ ] Modern, responsive React app running locally and deployable to Cloudflare.
- [ ] Users can visualize the lineage graph and drill down into nodes.
- [ ] Users can chat with "agents" to answer questions about the data.
- [ ] Grafana metrics and output files are accessible via the UI.
