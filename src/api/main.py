"""
FastAPI Application for Financial Data Lineage Tool.

Provides REST API endpoints for:
- Querying data lineage
- Ingesting code repositories
- Graph traversal operations
"""

import asyncio
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Any, Optional
import uuid

from fastapi import FastAPI, HTTPException, BackgroundTasks, Query, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from openai import AzureOpenAI

from src.utils import metrics

# Import our modules (these would be properly imported in production)
# from ..agents.supervisor import SupervisorAgent, SQLCorpusAgent, KnowledgeGraphAgent, ValidationAgent
# from ..knowledge_graph.cosmos_client import CosmosGremlinClient
# from ..search.hybrid_search import CodeSearchIndex
# from ...config.settings import get_settings


# ==================== Pydantic Models ====================

class LineageQueryRequest(BaseModel):
    """Request model for lineage queries."""
    question: str = Field(..., description="Natural language question about data lineage")
    include_sql_context: bool = Field(default=True, description="Include relevant SQL code")
    include_validation: bool = Field(default=True, description="Include validation checks")
    max_depth: int = Field(default=10, ge=1, le=50, description="Maximum lineage depth")


class ColumnLineageRequest(BaseModel):
    """Request model for column-level lineage."""
    table_name: str = Field(..., description="Table name (can include schema)")
    column_name: str = Field(..., description="Column name")
    direction: str = Field(default="both", pattern="^(upstream|downstream|both)$")
    include_transformations: bool = Field(default=True)


class TableLineageRequest(BaseModel):
    """Request model for table-level lineage."""
    table_name: str = Field(..., description="Table name")
    include_columns: bool = Field(default=True)
    direction: str = Field(default="both", pattern="^(upstream|downstream|both)$")


class RepositoryIngestRequest(BaseModel):
    """Request model for repository ingestion."""
    repo_url: str = Field(..., description="Git repository URL")
    branch: str = Field(default="main", description="Branch to ingest")
    file_patterns: list[str] = Field(
        default=["*.sql", "*.py", "*.json"],
        description="File patterns to include"
    )
    exclude_patterns: list[str] = Field(
        default=["**/test/**", "**/tests/**"],
        description="Patterns to exclude"
    )


class GraphTraversalRequest(BaseModel):
    """Request model for graph traversal."""
    start_node: str = Field(..., description="Starting node identifier")
    direction: str = Field(default="outbound", pattern="^(inbound|outbound|both)$")
    edge_types: list[str] = Field(default=[], description="Filter by edge types")
    max_depth: int = Field(default=5, ge=1, le=20)


class TransformationInfo(BaseModel):
    """Transformation information in lineage."""
    source_column: str
    target_column: str
    transformation_type: str
    transformation_logic: Optional[str] = None


class LineagePath(BaseModel):
    """A single lineage path."""
    nodes: list[dict]
    edges: list[dict]
    total_hops: int
    transformations: list[TransformationInfo] = []


class ValidationIssue(BaseModel):
    """A validation issue found in lineage."""
    issue_type: str
    severity: str
    message: str
    affected_entities: list[str] = []


class LineageResponse(BaseModel):
    """Response model for lineage queries."""
    query: str
    lineage_paths: list[LineagePath] = []
    transformations: list[TransformationInfo] = []
    validation_issues: list[ValidationIssue] = []
    narrative: str = ""
    confidence_score: float = Field(ge=0.0, le=1.0)
    sources_consulted: list[str] = []
    execution_time_ms: float


class IngestJobResponse(BaseModel):
    """Response model for ingestion job."""
    job_id: str
    status: str
    repo_url: str
    branch: str
    created_at: datetime
    message: str


class IngestJobStatus(BaseModel):
    """Status of an ingestion job."""
    job_id: str
    status: str
    progress_percent: float = 0.0
    files_processed: int = 0
    chunks_created: int = 0
    entities_extracted: int = 0
    errors: list[str] = []
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


class GraphNode(BaseModel):
    """A node in the graph."""
    id: str
    name: str
    entity_type: str
    properties: dict = {}


class GraphEdge(BaseModel):
    """An edge in the graph."""
    source_id: str
    target_id: str
    relationship_type: str
    properties: dict = {}


class GraphTraversalResponse(BaseModel):
    """Response model for graph traversal."""
    start_node: GraphNode
    nodes: list[GraphNode]
    edges: list[GraphEdge]
    paths: list[list[str]]


# ==================== Application State ====================

class AppState:
    """Application state container."""
    
    def __init__(self):
        self.supervisor_agent = None
        self.cosmos_client = None
        self.search_index = None
        self.openai_client = None
        self.ingestion_jobs: dict[str, IngestJobStatus] = {}


app_state = AppState()


# ==================== Lifecycle ====================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    print("Initializing Financial Lineage Tool...")
    
    # In production, initialize clients here:
    # settings = get_settings()
    # app_state.openai_client = AzureOpenAI(...)
    # app_state.cosmos_client = CosmosGremlinClient(...)
    # app_state.search_index = CodeSearchIndex(...)
    # app_state.supervisor_agent = SupervisorAgent(...)
    
    print("Initialization complete.")
    
    yield
    
    # Shutdown
    print("Shutting down...")
    if app_state.cosmos_client:
        app_state.cosmos_client.close()


# ==================== FastAPI App ====================

app = FastAPI(
    title="Financial Data Lineage API",
    description="""
    AI-powered data lineage tool for financial systems.
    
    Features:
    - Natural language lineage queries
    - Column and table level lineage
    - Multi-agent orchestration
    - Knowledge graph traversal
    - Lineage validation
    """,
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==================== Health Check ====================

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "components": {
            "api": "up",
            "cosmos_db": "up" if app_state.cosmos_client else "not_initialized",
            "search": "up" if app_state.search_index else "not_initialized",
            "agents": "up" if app_state.supervisor_agent else "not_initialized"
        }
    }


@app.get("/metrics")
async def prometheus_metrics():
    """
    Expose Prometheus metrics endpoint.

    Returns metrics in Prometheus text exposition format for scraping.
    Includes:
    - Parse cache hit/miss rates
    - Batch processing metrics
    - Worker pool statistics
    - File processing counters
    """
    return Response(
        content=metrics.get_registry().export_prometheus(),
        media_type="text/plain; version=0.0.4"
    )


# ==================== Lineage Endpoints ====================

@app.post("/api/v1/lineage/query", response_model=LineageResponse)
async def query_lineage(request: LineageQueryRequest):
    """
    Query data lineage using natural language.
    
    The query is processed by a multi-agent system that:
    1. Searches relevant SQL code
    2. Queries the knowledge graph
    3. Validates the lineage path
    """
    start_time = datetime.utcnow()
    
    # Mock response for demonstration
    # In production, this would call: app_state.supervisor_agent.process_query(request.question)
    
    response = LineageResponse(
        query=request.question,
        lineage_paths=[
            LineagePath(
                nodes=[
                    {"id": "source_table", "name": "raw.customers", "type": "Table"},
                    {"id": "transform", "name": "customer_transform.sql", "type": "Script"},
                    {"id": "target_table", "name": "gold.dim_customer", "type": "Table"}
                ],
                edges=[
                    {"source": "source_table", "target": "transform", "type": "READS_FROM"},
                    {"source": "transform", "target": "target_table", "type": "WRITES_TO"}
                ],
                total_hops=2,
                transformations=[
                    TransformationInfo(
                        source_column="first_name",
                        target_column="full_name",
                        transformation_type="CONCAT",
                        transformation_logic="CONCAT(first_name, ' ', last_name)"
                    )
                ]
            )
        ],
        transformations=[
            TransformationInfo(
                source_column="first_name",
                target_column="full_name",
                transformation_type="CONCAT",
                transformation_logic="CONCAT(first_name, ' ', last_name)"
            )
        ],
        validation_issues=[],
        narrative="The column 'full_name' in gold.dim_customer is derived from concatenating 'first_name' and 'last_name' from raw.customers.",
        confidence_score=0.95,
        sources_consulted=["etl/customer_transform.sql", "knowledge_graph"],
        execution_time_ms=(datetime.utcnow() - start_time).total_seconds() * 1000
    )
    
    return response


@app.post("/api/v1/lineage/column", response_model=LineageResponse)
async def get_column_lineage(request: ColumnLineageRequest):
    """
    Get lineage for a specific column.
    
    Returns upstream sources, downstream targets, and all transformations.
    """
    start_time = datetime.utcnow()
    
    # Mock response - would call cosmos_client.get_column_lineage()
    return LineageResponse(
        query=f"Lineage for {request.table_name}.{request.column_name}",
        lineage_paths=[],
        transformations=[],
        validation_issues=[],
        narrative=f"Column lineage for {request.table_name}.{request.column_name}",
        confidence_score=0.9,
        sources_consulted=["knowledge_graph"],
        execution_time_ms=(datetime.utcnow() - start_time).total_seconds() * 1000
    )


@app.get("/api/v1/lineage/column/{column_name}")
async def get_column_lineage_by_name(
    column_name: str,
    table: Optional[str] = Query(None, description="Filter by table name"),
    direction: str = Query("both", pattern="^(upstream|downstream|both)$")
):
    """Get lineage for a column by name."""
    return {
        "column": column_name,
        "table_filter": table,
        "direction": direction,
        "upstream": [],
        "downstream": [],
        "message": "Query the knowledge graph for this column's lineage"
    }


@app.get("/api/v1/lineage/table/{table_name}")
async def get_table_lineage(
    table_name: str,
    include_columns: bool = Query(True),
    direction: str = Query("both", pattern="^(upstream|downstream|both)$")
):
    """Get lineage for all columns in a table."""
    return {
        "table": table_name,
        "include_columns": include_columns,
        "direction": direction,
        "columns": [],
        "dependencies": [],
        "dependents": []
    }


# ==================== Ingestion Endpoints ====================

@app.post("/api/v1/ingest/repository", response_model=IngestJobResponse)
async def ingest_repository(
    request: RepositoryIngestRequest,
    background_tasks: BackgroundTasks
):
    """
    Ingest a code repository for lineage analysis.
    
    This starts an async job that:
    1. Clones/pulls the repository
    2. Parses code files (SQL, Python)
    3. Chunks code semantically
    4. Generates embeddings
    5. Extracts entities and relationships
    6. Populates the knowledge graph
    """
    job_id = str(uuid.uuid4())
    
    # Create job status
    job_status = IngestJobStatus(
        job_id=job_id,
        status="pending",
        started_at=datetime.utcnow()
    )
    app_state.ingestion_jobs[job_id] = job_status
    
    # Start background task
    background_tasks.add_task(
        run_ingestion_job,
        job_id=job_id,
        repo_url=request.repo_url,
        branch=request.branch,
        file_patterns=request.file_patterns,
        exclude_patterns=request.exclude_patterns
    )
    
    return IngestJobResponse(
        job_id=job_id,
        status="accepted",
        repo_url=request.repo_url,
        branch=request.branch,
        created_at=datetime.utcnow(),
        message="Ingestion job started. Use GET /api/v1/ingest/status/{job_id} to check progress."
    )


async def run_ingestion_job(
    job_id: str,
    repo_url: str,
    branch: str,
    file_patterns: list[str],
    exclude_patterns: list[str]
):
    """Background task to run repository ingestion."""
    job = app_state.ingestion_jobs.get(job_id)
    if not job:
        return
    
    try:
        job.status = "running"
        
        # Simulate ingestion steps
        # In production: clone repo, parse files, chunk, embed, extract entities
        
        for i in range(10):
            await asyncio.sleep(1)  # Simulate work
            job.progress_percent = (i + 1) * 10
            job.files_processed = (i + 1) * 5
            job.chunks_created = (i + 1) * 20
            job.entities_extracted = (i + 1) * 10
        
        job.status = "completed"
        job.completed_at = datetime.utcnow()
        
    except Exception as e:
        job.status = "failed"
        job.errors.append(str(e))
        job.completed_at = datetime.utcnow()


@app.get("/api/v1/ingest/status/{job_id}", response_model=IngestJobStatus)
async def get_ingestion_status(job_id: str):
    """Get the status of an ingestion job."""
    job = app_state.ingestion_jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@app.get("/api/v1/ingest/jobs")
async def list_ingestion_jobs(
    status: Optional[str] = Query(None, pattern="^(pending|running|completed|failed)$"),
    limit: int = Query(20, ge=1, le=100)
):
    """List ingestion jobs."""
    jobs = list(app_state.ingestion_jobs.values())
    
    if status:
        jobs = [j for j in jobs if j.status == status]
    
    return {
        "jobs": jobs[-limit:],
        "total": len(jobs)
    }


# ==================== Graph Endpoints ====================

@app.post("/api/v1/graph/traverse", response_model=GraphTraversalResponse)
async def traverse_graph(request: GraphTraversalRequest):
    """
    Traverse the lineage knowledge graph.
    
    Performs graph traversal from a starting node following specified
    edge types and direction constraints.
    """
    # Mock response - would call cosmos_client methods
    return GraphTraversalResponse(
        start_node=GraphNode(
            id=request.start_node,
            name=request.start_node,
            entity_type="Table"
        ),
        nodes=[],
        edges=[],
        paths=[]
    )


@app.get("/api/v1/graph/entity/{entity_id}")
async def get_entity(entity_id: str):
    """Get details of a specific entity in the knowledge graph."""
    # Would call cosmos_client.get_entity()
    return {
        "id": entity_id,
        "name": entity_id,
        "entity_type": "Unknown",
        "properties": {},
        "relationships": []
    }


@app.get("/api/v1/graph/search")
async def search_entities(
    query: str = Query(..., description="Search query"),
    entity_type: Optional[str] = Query(None, description="Filter by entity type"),
    limit: int = Query(20, ge=1, le=100)
):
    """Search for entities in the knowledge graph."""
    # Would call cosmos_client.find_entities_by_name()
    return {
        "query": query,
        "entity_type": entity_type,
        "results": [],
        "total": 0
    }


# ==================== Search Endpoints ====================

@app.get("/api/v1/search/code")
async def search_code(
    query: str = Query(..., description="Search query"),
    language: Optional[str] = Query(None, description="Filter by language"),
    repo: Optional[str] = Query(None, description="Filter by repository"),
    limit: int = Query(10, ge=1, le=50)
):
    """
    Search the code corpus using hybrid search.
    
    Combines semantic (vector) search with keyword matching for
    optimal results.
    """
    # Would call search_index.hybrid_search()
    return {
        "query": query,
        "filters": {
            "language": language,
            "repo": repo
        },
        "results": [],
        "total": 0
    }


@app.get("/api/v1/search/table/{table_name}")
async def search_by_table(
    table_name: str,
    include_columns: bool = Query(True),
    limit: int = Query(20, ge=1, le=100)
):
    """Find all code that references a specific table."""
    # Would call search_index.search_by_table()
    return {
        "table": table_name,
        "code_references": [],
        "total": 0
    }


# ==================== Main ====================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
