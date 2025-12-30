# Project Context

## Purpose
An AI-powered solution for SQL database analysis, knowledge graph creation, and data lineage visualization using Azure AI services and multi-agent orchestration. The tool organizes SQL files, extracts entities and relationships into a knowledge graph (Cosmos DB), and enables hybrid search and natural language queries about financial data lineage.

## Tech Stack
- **Language**: Python 3.10+
- **Web Framework**: FastAPI, Pydantic, Uvicorn
- **SQL Processing**: sqlglot, custom SQL Server parser, watchdog (file watching)
- **Database**: Azure Cosmos DB (Gremlin API) for Knowledge Graph, Redis for caching
- **AI/ML**: Azure OpenAI (GPT-4o), Azure AI Search (Vector Search), tiktoken, scikit-learn
- **Infrastructure**: Docker, Docker Compose
- **Dev Tools**: Black, Ruff, MyPy, Pre-commit

## Project Conventions

### Code Style
- **Python**: Follows PEP 8 guidelines.
- **Formatting**: Enforced by `black`.
- **Linting**: Enforced by `ruff`.
- **Type Checking**: Enforced by `mypy`.
- **Imports**: Sorted and organized.

### Architecture Patterns
- **Modular Structure**: Domain-driven organization in `src/` (ingestion, knowledge_graph, search, agents, api).
- **Agentic Workflow**: Multi-agent system orchestrated by a supervisor (`src/agents/supervisor.py`) for complex analysis.
- **Ingestion Pipeline**: Automated pipeline from file watching -> parsing -> graph ingestion.
- **API First**: Core functionality exposed via FastAPI endpoints.

### Testing Strategy
- **Framework**: `pytest` for unit and integration tests.
- **Async Support**: `pytest-asyncio` for testing async API endpoints and agents.
- **Coverage**: Aim for high code coverage (measured via `pytest-cov`).

### Git Workflow
- Standard feature branch workflow.
- PR reviews required for merging to main.

## Domain Context
- **Financial Data Lineage**: Tracing data flow across SQL Server databases.
- **Core Entities**: Tables, Views, Columns, Stored Procedures, Functions, Indexes, Constraints.
- **Relationships**: Foreign Keys (FK), Dependencies (Data Lineage), Usage references.
- **SQL Dialect**: Primarily Transact-SQL (T-SQL).

## Important Constraints
- **Azure Dependency**: Full functionality (Knowledge Graph, Search, AI) requires Azure services (Cosmos DB, OpenAI, AI Search).
- **Local Fallback**: SQL organization features work locally without Azure dependencies.
- **Proprietary**: Project is "Proprietary - Internal Use Only".

## External Dependencies
- **Azure OpenAI Service**: For LLM (GPT-4o) & Embeddings.
- **Azure Cosmos DB**: Gremlin API for graph storage.
- **Azure AI Search**: For vector and hybrid search.
- **GitHub API**: Used for some integration features (via `pygithub`).
