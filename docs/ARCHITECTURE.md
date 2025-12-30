# Financial Data Lineage Tool - Architecture & Implementation Guide

## Executive Summary

This document provides a comprehensive implementation guide for building an AI-powered financial data lineage tool that ingests code repositories, extracts semantic information, builds knowledge graphs, and uses multi-agent orchestration to deliver accurate, traceable lineage insights.

## 1. High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              DATA EXPLORATION TOOLKIT                            │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│  ┌──────────────┐    ┌──────────────────────┐    ┌───────────────────────────┐  │
│  │   SOURCES    │───▶│  INGESTION PIPELINE  │───▶│   KNOWLEDGE LAYER        │  │
│  │              │    │                      │    │                           │  │
│  │ • GitHub     │    │ • Code Extraction    │    │ • Cosmos DB (Gremlin)     │  │
│  │ • Azure Repos│    │ • Chunking           │    │ • Azure AI Search         │  │
│  │ • DB Metadata│    │ • Embedding          │    │ • MS Fabric Graph         │  │
│  └──────────────┘    └──────────────────────┘    └───────────────────────────┘  │
│                                                              │                   │
│                                                              ▼                   │
│  ┌──────────────────────────────────────────────────────────────────────────┐   │
│  │                    AZURE AI FOUNDRY - MULTI-AGENT BACKEND                │   │
│  │  ┌─────────────────────────────────────────────────────────────────────┐ │   │
│  │  │                      SUPERVISOR AGENT (GPT-4o)                      │ │   │
│  │  │  • Orchestration • Planning • Memory • Goal Management              │ │   │
│  │  └────────────┬───────────────┬───────────────┬───────────────────────┘ │   │
│  │               │               │               │                          │   │
│  │  ┌────────────▼───┐ ┌────────▼────────┐ ┌────▼─────────────┐            │   │
│  │  │ SQL Corpus     │ │ Knowledge Graph │ │ Validation       │            │   │
│  │  │ Agent          │ │ Agent           │ │ Agent            │            │   │
│  │  │ /srchagent     │ │ /kbagent        │ │ /valagent        │            │   │
│  │  └────────────────┘ └─────────────────┘ └──────────────────┘            │   │
│  └──────────────────────────────────────────────────────────────────────────┘   │
│                                                              │                   │
│                                                              ▼                   │
│  ┌─────────────────────────────────────────────────────────────────────────┐    │
│  │                          LINEAGE OUTPUTS                                │    │
│  │  • Data Flow Lineage  • Source-to-Target  • Attribute-Level             │    │
│  │  • Operator-Level     • Transformation Logic  • Validation Insights     │    │
│  └─────────────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────────────┘
```

## 2. Component Details

### 2.1 Ingestion Pipeline

The ingestion pipeline handles code acquisition, parsing, semantic chunking, and storage.

#### 2.1.1 Code Acquisition Layer

```
GitHub/Azure Repos → Clone/Pull → File Scanner → Language Detector
```

**Supported File Types:**
- SQL files (.sql, .ddl, .dml)
- Python files (.py) - PySpark, Pandas
- Scala/Java (.scala, .java) - Spark
- JSON/YAML configs
- dbt models and manifests
- Azure Data Factory pipelines (JSON)

#### 2.1.2 Semantic Chunking Strategy

**Why semantic chunking matters for code:**
- Maintains logical boundaries (functions, classes, CTEs)
- Preserves context for accurate embedding
- Enables precise retrieval for lineage tracing

**Chunking Rules by Language:**

| Language | Chunk Boundary | Max Tokens | Overlap Strategy |
|----------|---------------|------------|------------------|
| SQL | CTE, Subquery, Statement | 1500 | Include dependent CTEs |
| Python | Function, Class, Import block | 1000 | Include imports + docstring |
| Config | Complete object/array | 500 | Parent key context |

### 2.2 Knowledge Graph Schema

#### 2.2.1 Entity Types (Nodes)

```
ENTITY TYPES:
├── DataAsset
│   ├── Table
│   ├── View
│   ├── File
│   └── Stream
├── CodeAsset
│   ├── SQLScript
│   ├── PythonScript
│   ├── Pipeline
│   └── Notebook
├── Column (Attribute)
├── Transformation
│   ├── Join
│   ├── Aggregation
│   ├── Filter
│   ├── Cast
│   └── Calculation
└── DataType
```

#### 2.2.2 Relationship Types (Edges)

```
RELATIONSHIPS:
├── DERIVES_FROM (Column → Column)
├── TRANSFORMS_TO (Source → Target)
├── CONTAINS (Table → Column)
├── EXECUTES (Script → Transformation)
├── READS_FROM (Script → Table)
├── WRITES_TO (Script → Table)
├── CASTS_TO (Column → DataType)
├── JOINS_WITH (Table → Table)
└── DEPENDS_ON (Asset → Asset)
```

### 2.3 Multi-Agent Architecture

#### 2.3.1 Agent Roles

**Supervisor Agent (Orchestrator)**
- Receives user queries
- Decomposes into sub-tasks
- Routes to appropriate specialist agents
- Aggregates and validates results
- Maintains conversation memory

**SQL Corpus Agent (/srchagent)**
- Grounded on: Azure AI Search (SQL corpus index)
- Responsibilities:
  - Parse SQL AST
  - Extract column lineage from SELECT, JOIN, WHERE
  - Identify transformations (CAST, CASE, aggregations)
  - Trace CTE dependencies

**Knowledge Graph Agent (/kbagent)**
- Grounded on: Cosmos DB Gremlin API
- Responsibilities:
  - Query existing lineage relationships
  - Traverse graph for upstream/downstream
  - Find related entities
  - Return structured lineage paths

**Validation Agent (/valagent)**
- Grounded on: Source data schemas
- Responsibilities:
  - Verify data types match across lineage
  - Check for breaking changes
  - Validate transformation logic
  - Flag inconsistencies

### 2.4 Azure AI Search Configuration

**Index Schema for Code Corpus:**

```json
{
  "name": "code-lineage-index",
  "fields": [
    {"name": "id", "type": "Edm.String", "key": true},
    {"name": "content", "type": "Edm.String", "searchable": true},
    {"name": "content_vector", "type": "Collection(Edm.Single)", "dimensions": 1536},
    {"name": "language", "type": "Edm.String", "filterable": true},
    {"name": "file_path", "type": "Edm.String"},
    {"name": "repo_name", "type": "Edm.String", "filterable": true},
    {"name": "chunk_type", "type": "Edm.String", "filterable": true},
    {"name": "entities", "type": "Collection(Edm.String)", "filterable": true},
    {"name": "tables_referenced", "type": "Collection(Edm.String)", "filterable": true},
    {"name": "columns_referenced", "type": "Collection(Edm.String)", "filterable": true}
  ],
  "vectorSearch": {
    "algorithms": [{"name": "hnsw-config", "kind": "hnsw"}],
    "profiles": [{"name": "vector-profile", "algorithm": "hnsw-config"}]
  }
}
```

## 3. Implementation Phases

### Phase 1: Ingestion Pipeline (Weeks 1-3)

1. Repository connector service
2. Code parser implementations (SQL, Python)
3. Semantic chunking engine
4. Embedding generation (text-embedding-ada-002)
5. Blob storage integration

### Phase 2: Knowledge Graph (Weeks 4-6)

1. Cosmos DB Gremlin provisioning
2. Graph schema implementation
3. Entity extraction from parsed code
4. Relationship inference engine
5. Graph population pipeline

### Phase 3: Azure AI Search (Weeks 7-8)

1. Index creation and configuration
2. Hybrid search (vector + keyword)
3. Semantic ranking configuration
4. Filter and facet setup

### Phase 4: Agent Development (Weeks 9-12)

1. Azure AI Foundry setup
2. Individual agent development
3. Tool/function definitions
4. Supervisor orchestration logic
5. FastAPI container deployment

### Phase 5: Integration & Testing (Weeks 13-14)

1. End-to-end pipeline testing
2. Lineage accuracy validation
3. Performance optimization
4. API documentation

## 4. Technology Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| Code Storage | Azure Blob Storage | Raw code and metadata |
| Vector Store | Azure AI Search | Semantic code search |
| Graph Database | Cosmos DB (Gremlin) | Lineage relationships |
| Embedding Model | text-embedding-ada-002 | Code vectorization |
| Reasoning Model | GPT-4o | Agent intelligence |
| Agent Platform | Azure AI Foundry | Multi-agent orchestration |
| Orchestration | FastAPI + Container Apps | API layer |
| API Gateway | Azure APIM | Rate limiting, auth |
| Observability | App Insights + Log Analytics | Monitoring |
| DevSecOps | GitOps + Terraform | Infrastructure |

## 5. Key Design Decisions

### 5.1 Why Multi-Agent vs Single Agent?

- **Specialization**: Each agent optimized for specific grounding source
- **Scalability**: Agents can be scaled independently
- **Accuracy**: Reduces hallucination through validation layer
- **Maintainability**: Modular updates without system-wide impact

### 5.2 Why Cosmos DB Gremlin + Azure AI Search?

- **Gremlin**: Optimized for graph traversal (lineage paths)
- **AI Search**: Optimized for semantic retrieval (finding relevant code)
- **Hybrid**: Deterministic joins (graph) + fuzzy matching (vector)

### 5.3 Why Semantic Chunking?

- Generic token-based chunking breaks code semantics
- AST-aware chunking preserves logical units
- Better embedding quality for retrieval

## 6. API Endpoints

```
POST /api/v1/lineage/query
  - Body: {"question": "What is the lineage of customer_id in fact_sales?"}
  - Returns: Structured lineage JSON + narrative

POST /api/v1/lineage/column/{column_name}
  - Returns: Full upstream/downstream lineage

POST /api/v1/lineage/table/{table_name}
  - Returns: Table-level lineage with all columns

POST /api/v1/ingest/repository
  - Body: {"repo_url": "...", "branch": "main"}
  - Returns: Ingestion job ID

GET /api/v1/graph/traverse
  - Params: start_node, direction, depth
  - Returns: Graph traversal results
```

## 7. Lineage Output Formats

### 7.1 Data Flow Lineage
```json
{
  "source": "raw.customers",
  "target": "gold.dim_customer", 
  "transformations": ["filter", "aggregate", "rename"],
  "scripts": ["etl/customer_transform.sql"]
}
```

### 7.2 Attribute-Level Lineage
```json
{
  "target_column": "gold.dim_customer.full_name",
  "derivation": "CONCAT(first_name, ' ', last_name)",
  "source_columns": [
    "bronze.raw_customers.first_name",
    "bronze.raw_customers.last_name"
  ],
  "data_type_transformation": "VARCHAR(50) + VARCHAR(50) → VARCHAR(101)"
}
```

### 7.3 Validation Insights
```json
{
  "validation_type": "data_type_compatibility",
  "status": "warning",
  "message": "Potential precision loss: DECIMAL(18,6) → DECIMAL(10,2)",
  "affected_path": ["staging.amounts.value", "gold.transactions.amount"]
}
```
