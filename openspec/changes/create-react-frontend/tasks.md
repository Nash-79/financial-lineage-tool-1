# Tasks: Create Modern React Frontend

## 1. Scaffold Application
- [ ] 1.1 Initialize Vite React project in `frontend/`
- [ ] 1.2 Install dependencies (TailwindCSS, Lucide, React Router, Axios/Query)
- [ ] 1.3 Configure `vite.config.ts` and `tsconfig.json`
- [ ] 1.4 Setup Tailwind theme (colors, fonts for premium look)
- [ ] 1.5 Create basic App Shell (Layout, Sidebar)

## 2. Core UI Components
- [ ] 2.1 specific UI library components (Buttons, Inputs, Cards, Modals)
- [ ] 2.2 Create `GrafanaPanel` component (iframe wrapper)
- [ ] 2.3 Create `FileExplorer` component (tree view of ingested files)

## 3. Visualization
- [ ] 3.1 Install graph visualization library (e.g., React Flow)
- [ ] 3.2 Create `LineageCanvas` component
- [ ] 3.3 Implement `NodeDetails` panel (slide-over)
- [ ] 3.4 Connect visualization to mock data first, then API

## 4. Agentic Chat Interface
- [ ] 4.1 Create `ChatWindow` component
- [ ] 4.2 Create `AgentSelector` (Deep, Semantic, Text, NL)
- [ ] 4.3 Implement message rendering (User vs AI, Markdown support)
- [ ] 4.4 Hook up to backend API endpoints

## 5. Deployment Setup
- [ ] 5.1 Create `wrangler.toml` for Cloudflare Pages
- [ ] 5.2 Add `deploy` script to package.json
- [ ] 5.3 Document deployment steps in `docs/FRONTEND.md`

## 6. Backend Adjustments (if needed)
- [ ] 6.1 Update CORS settings in FastAPI
- [ ] 6.2 expose Grafana endpoints if necessary
