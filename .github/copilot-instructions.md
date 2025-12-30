## Financial Lineage Tool — Copilot / AI Agent Instructions

These notes give an AI coding agent the minimal, targeted knowledge needed to be productive in this repo.
Be concise: reference files, conventions, and concrete examples the agent should use.

1) Big picture
- Purpose: an AI-driven data-lineage service that ingests code (SQL/Python), creates semantic chunks + embeddings, populates a lineage knowledge graph (Cosmos Gremlin), and answers NL lineage queries via a multi-agent orchestrator.
- Major components:
  - `src/ingestion/` — repo cloning, parsing, semantic chunking (`semantic_chunker.py`), embedding generation.
  - `src/knowledge_graph/` — Cosmos Gremlin client and graph helpers (`cosmos_client.py`, `neo4j_client.py`).
  - `src/search/` — hybrid code search (vector + keyword) used by SQL agent.
  - `src/agents/` — multi-agent orchestration; `supervisor.py` wires LLM -> tools -> specialist agents.
  - `src/api/` — FastAPI application (`main.py`) exposing ingestion and lineage endpoints.

2) Runtime / workflows (how developers run & debug)
- Local dev: create venv, `pip install -r requirements.txt`, copy `.env.example` -> `.env` and set Azure/DB keys (see `README.md` and `config/settings.py`).
- Start API: `uvicorn src.api.main:app --reload --port 8000` (FastAPI docs at `/docs`).
- Container: `docker-compose up` / `docker-compose.local.yml` for a local stack including Ollama / Qdrant / Gremlin (see `docker-compose*.yml`).
- Quick checks: `python test_local_api.py` hits `/health` and demonstrates local Ollama usage.

3) Project-specific conventions & patterns
- Settings: all runtime configuration is via `config/settings.py` (Pydantic Settings reading `.env`). Use the env var prefixes shown there (e.g. `AZURE_OPENAI_*`, `COSMOS_*`, `SEARCH_*`, `STORAGE_*`, `GITHUB_*`).
- Agents-as-tools: `src/agents/supervisor.py` exposes agent capabilities to the LLM via tool definitions named `query_sql_corpus`, `query_knowledge_graph`, and `validate_lineage`. When adding new agent functions follow the same `Tool(...).to_openai_tool()` pattern so the supervisor can surface them to the LLM.
- Embedding / chunking: ingestion uses semantic chunking (AST-aware) in `src/ingestion/semantic_chunker.py`. Prefer keeping CTEs together and include CTE context prefixes — this is how downstream embedding/search expects content.
- Token limits: chunkers explicitly use token budgets (e.g. SQL 1500, Python 1000). Respect these values when adding or modifying chunk logic and when choosing model prompts.

4) Integration & external dependencies (what to mock in tests)
- Azure OpenAI — used through `openai.AzureOpenAI` clients in agents (`supervisor.py`) and configured in `config/settings.py`.
- Cosmos DB (Gremlin) — graph storage (see `src/knowledge_graph/cosmos_client.py`). For unit tests, mock Gremlin client methods: `query_lineage`, `get_entity`, `find_entities_by_name`.
- Azure AI Search — hybrid semantic index used by `src/search/*`. Mock the `CodeSearchIndex` methods when testing agents.
- Qdrant / Ollama — optional local stacks (see `qdrant/` and `test_local_api.py`) used for fully-local demos; treat these as integration-only.

5) Where to look to implement features or fixes (examples)
- Add new ingestion parsing rules: `src/ingestion/semantic_chunker.py` (preserve CTEs and include context_prefix).
- Adjust agent tool schemas / behavior: `src/agents/supervisor.py` — update `Tool(...).parameters` and the matching `_call_*` methods.
- API contract changes: `src/api/main.py` — Pydantic request/response models live here; update them and the example mock implementations.
- Configuration changes: `config/settings.py` — add fields to the appropriate sub-settings (AzureOpenAISettings, CosmosDBSettings, etc.).

6) Common gotchas discovered in the codebase
- Many endpoints in `src/api/main.py` are mocked (example responses). Production wiring happens by initializing `app_state` in the lifespan startup (see commented block in `lifespan`). Be sure to initialize `app_state.openai_client`, `app_state.cosmos_client`, `app_state.search_index`, and `app_state.supervisor_agent` when moving tests to integration.
- Supervisor expects agent instances with `.search()`, `.query_lineage()`, and `.validate()` async methods. Unit tests can inject small async stubs.
- Token counting uses `tiktoken` encoding `cl100k_base` — ensure it is available in the environment for chunking and tests.

7) Quick examples for an AI agent to modify code
- To expose a new specialist tool: add a Tool() in `SupervisorAgent._build_tools()` with `name`, `description`, `parameters` schema and `function=self._call_new_agent`; implement `_call_new_agent` that forwards to provided agent instance.
- To read settings in code: call `from config.settings import get_settings(); settings = get_settings()` and access `settings.search.index_name`, `settings.agent.max_iterations`, etc.

8) Tests & verification
- Unit tests: repo has simple integration test scripts: `test_local_api.py`, `test_neo4j.py`, `test_qdrant.py`. Use these for manual/local validation.
- For CI: prefer running `uvicorn` + integration harness or mocking external services. Keep tests small and mock Azure/Cosmos/Search clients.

If anything here is unclear or you want more detail (e.g., specific call traces in `supervisor.py` or the expected shape of Cosmos Gremlin responses), tell me which area to expand and I will iterate.
