"""
Local Development API - Uses FREE alternatives to Azure services.

Replacements:
- Azure OpenAI → Ollama (local LLMs)
- Cosmos DB Gremlin → Neo4j (cloud graph database)
- Azure AI Search → Qdrant (local vector DB)
"""

import asyncio
import os
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Any, Optional
import json
import pickle
from pathlib import Path

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import httpx


# ==================== Configuration ====================

class LocalConfig:
    """Local development configuration."""

    # Ollama settings
    OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
    LLM_MODEL = os.getenv("LLM_MODEL", "llama3.1:8b")
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "nomic-embed-text")

    # Qdrant settings
    QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
    QDRANT_PORT = int(os.getenv("QDRANT_PORT", "6333"))

    # Neo4j settings
    NEO4J_URI = os.getenv("NEO4J_URI", "neo4j+s://66e1cb8c.databases.neo4j.io")
    NEO4J_USERNAME = os.getenv("NEO4J_USERNAME", "neo4j")
    NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "S6OFtX78rqAyI7Zk9tcpnDAzyN1srKiq4so53WSBWhg")
    NEO4J_DATABASE = os.getenv("NEO4J_DATABASE", "neo4j")

    # Storage
    STORAGE_PATH = os.getenv("STORAGE_PATH", "./data")


config = LocalConfig()


# ==================== Ollama Client ====================

class OllamaClient:
    """Client for local Ollama LLM."""
    
    def __init__(self, host: str = config.OLLAMA_HOST):
        self.host = host
        self.client = httpx.AsyncClient(timeout=120.0)
    
    async def generate(
        self,
        prompt: str,
        model: str = config.LLM_MODEL,
        system: str = "",
        temperature: float = 0.1
    ) -> str:
        """Generate text using Ollama."""
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        
        response = await self.client.post(
            f"{self.host}/api/chat",
            json={
                "model": model,
                "messages": messages,
                "stream": False,
                "options": {
                    "temperature": temperature
                }
            }
        )
        
        if response.status_code != 200:
            raise Exception(f"Ollama error: {response.text}")
        
        return response.json()["message"]["content"]
    
    async def embed(
        self,
        text: str,
        model: str = config.EMBEDDING_MODEL
    ) -> list[float]:
        """Generate embeddings using Ollama."""
        response = await self.client.post(
            f"{self.host}/api/embeddings",
            json={
                "model": model,
                "prompt": text
            }
        )
        
        if response.status_code != 200:
            raise Exception(f"Ollama embedding error: {response.text}")
        
        return response.json()["embedding"]
    
    async def close(self):
        await self.client.aclose()


# ==================== Qdrant Client ====================

class QdrantLocalClient:
    """Client for local Qdrant vector database."""
    
    def __init__(
        self,
        host: str = config.QDRANT_HOST,
        port: int = config.QDRANT_PORT
    ):
        self.base_url = f"http://{host}:{port}"
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def create_collection(
        self,
        name: str,
        vector_size: int = 768  # nomic-embed-text dimension
    ):
        """Create a vector collection."""
        response = await self.client.put(
            f"{self.base_url}/collections/{name}",
            json={
                "vectors": {
                    "size": vector_size,
                    "distance": "Cosine"
                }
            }
        )
        return response.json()
    
    async def upsert(
        self,
        collection: str,
        points: list[dict]
    ):
        """Upsert vectors into collection."""
        response = await self.client.put(
            f"{self.base_url}/collections/{collection}/points",
            json={"points": points}
        )
        return response.json()
    
    async def search(
        self,
        collection: str,
        vector: list[float],
        limit: int = 10,
        filter_conditions: Optional[dict] = None
    ) -> list[dict]:
        """Search for similar vectors."""
        payload = {
            "vector": vector,
            "limit": limit,
            "with_payload": True
        }
        
        if filter_conditions:
            payload["filter"] = filter_conditions
        
        response = await self.client.post(
            f"{self.base_url}/collections/{collection}/points/search",
            json=payload
        )
        
        return response.json().get("result", [])
    
    async def close(self):
        await self.client.aclose()


# Import Neo4j client
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from src.knowledge_graph.neo4j_client import Neo4jGraphClient
from src.ingestion.code_parser import CodeParser
from src.knowledge_graph.entity_extractor import GraphExtractor


# Gremlin and NetworkX implementations removed - now using Neo4j


# ==================== Local Supervisor Agent ====================

class LocalSupervisorAgent:
    """
    Supervisor agent using local Ollama for reasoning.
    """
    
    SYSTEM_PROMPT = """You are a Financial Data Lineage Agent. Your role is to answer questions 
about data lineage by analyzing the provided context from code searches and graph queries.

When answering lineage questions:
1. Identify the target entity (table, column)
2. Trace the data flow from sources to target
3. Note any transformations applied
4. Be specific about column mappings and data types

Format your response clearly with:
- Summary: Brief answer
- Lineage Path: Source → Transformation → Target
- Transformations: Details of any data changes
- Confidence: How certain you are

If you don't have enough information, say so clearly."""

    def __init__(
        self,
        ollama: OllamaClient,
        qdrant: QdrantLocalClient,
        graph: Neo4jGraphClient
    ):
        self.ollama = ollama
        self.qdrant = qdrant
        self.graph = graph
    
    async def query(self, question: str) -> dict:
        """Process a lineage query."""
        
        # Step 1: Search for relevant code in vector DB
        try:
            query_embedding = await self.ollama.embed(question)
            code_results = await self.qdrant.search(
                collection="code_chunks",
                vector=query_embedding,
                limit=5
            )
        except Exception as e:
            code_results = []
            print(f"Vector search failed: {e}")
        
        # Step 2: Search graph for entities mentioned in question
        graph_results = []
        # Extract potential entity names (simple approach)
        words = question.replace("_", " ").split()
        for word in words:
            if len(word) > 3:  # Skip short words
                matches = self.graph.find_by_name(word)
                graph_results.extend(matches[:3])
        
        # Get lineage for found entities
        lineage_info = []
        for entity in graph_results[:2]:
            entity_id = entity.get('id')
            if entity_id:
                upstream = self.graph.get_upstream(entity_id, max_depth=5)
                downstream = self.graph.get_downstream(entity_id, max_depth=5)
                lineage_info.append({
                    "entity": entity,
                    "upstream": upstream[:5],
                    "downstream": downstream[:5]
                })
        
        # Step 3: Build context for LLM
        context = ""
        
        if code_results:
            context += "## Relevant Code:\n\n"
            for result in code_results:
                payload = result.get("payload", {})
                context += f"File: {payload.get('file_path', 'unknown')}\n"
                context += f"```sql\n{payload.get('content', '')[:1000]}\n```\n\n"
        
        if lineage_info:
            context += "## Knowledge Graph Results:\n\n"
            for info in lineage_info:
                entity = info["entity"]
                context += f"Entity: {entity.get('name')} ({entity.get('entity_type')})\n"
                if info["upstream"]:
                    context += f"Upstream sources: {len(info['upstream'])} found\n"
                if info["downstream"]:
                    context += f"Downstream targets: {len(info['downstream'])} found\n"
                context += "\n"
        
        if not context:
            context = "No relevant code or graph data found. Please ingest some data first."
        
        # Step 4: Generate response with Ollama
        prompt = f"""Question: {question}

{context}

Based on the information above, answer the question about data lineage.
If there's no relevant data, explain what information would be needed."""

        try:
            response = await self.ollama.generate(
                prompt=prompt,
                system=self.SYSTEM_PROMPT,
                temperature=0.1
            )
        except Exception as e:
            response = f"Error generating response: {e}"
        
        return {
            "question": question,
            "answer": response,
            "sources": [r.get("payload", {}).get("file_path") for r in code_results if r.get("payload")],
            "graph_entities": [e.get("name") for e in graph_results],
            "confidence": 0.8 if (code_results or graph_results) else 0.3
        }


# ==================== Request/Response Models ====================

class LineageQueryRequest(BaseModel):
    question: str = Field(..., description="Natural language question")


class LineageResponse(BaseModel):
    question: str
    answer: str
    sources: list[str] = []
    graph_entities: list[str] = []
    confidence: float


class IngestRequest(BaseModel):
    file_path: str = Field(..., description="Path to file or directory")
    file_type: str = Field(default="sql", description="File type (sql, python)")


class SqlIngestRequest(BaseModel):
    sql_content: str = Field(..., description="Raw SQL content to be parsed and ingested.")
    dialect: str = Field(default="tsql", description="The SQL dialect (e.g., tsql, spark, bigquery).")
    source_file: str = Field(default="manual_ingest", description="The original file name or source of the SQL.")


class EntityRequest(BaseModel):
    entity_id: str
    entity_type: str
    name: str
    properties: dict = {}


class RelationshipRequest(BaseModel):
    source_id: str
    target_id: str
    relationship_type: str
    properties: dict = {}


class HealthResponse(BaseModel):
    status: str
    services: dict
    timestamp: str


# ==================== Application State ====================

class AppState:
    ollama: Optional[OllamaClient] = None
    qdrant: Optional[QdrantLocalClient] = None
    graph: Optional[Neo4jGraphClient] = None
    agent: Optional[LocalSupervisorAgent] = None
    parser: Optional[CodeParser] = None
    extractor: Optional[GraphExtractor] = None


state = AppState()


# ==================== Lifespan ====================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize and cleanup resources."""
    print("[*] Starting Local Lineage Tool with Neo4j...")

    # Create data directory
    Path(config.STORAGE_PATH).mkdir(parents=True, exist_ok=True)

    # Initialize clients
    state.ollama = OllamaClient()
    state.qdrant = QdrantLocalClient()

    # Connect to Neo4j
    print(f"[*] Connecting to Neo4j at {config.NEO4J_URI}...")
    try:
        state.graph = Neo4jGraphClient(
            uri=config.NEO4J_URI,
            username=config.NEO4J_USERNAME,
            password=config.NEO4J_PASSWORD,
            database=config.NEO4J_DATABASE
        )
        print("[+] Connected to Neo4j")

        # Create indexes for performance
        state.graph.create_indexes()

    except Exception as e:
        print(f"[!] Failed to connect to Neo4j: {e}")
        print("[!] Please check your Neo4j credentials in .env file")
        raise

    # Initialize Parser and Extractor
    state.parser = CodeParser()
    state.extractor = GraphExtractor(neo4j_client=state.graph, code_parser=state.parser)
    print("[+] Initialized Code Parser and Graph Extractor")

    # Create agent
    state.agent = LocalSupervisorAgent(
        ollama=state.ollama,
        qdrant=state.qdrant,
        graph=state.graph
    )

    # Create Qdrant collection if needed
    try:
        await state.qdrant.create_collection("code_chunks", vector_size=768)
        print("[+] Created Qdrant collection")
    except Exception as e:
        print(f"[i] Collection may already exist: {e}")

    print("[+] All services initialized")
    print(f"[i] Graph stats: {state.graph.get_stats()}")

    yield

    # Cleanup
    print("[*] Shutting down...")
    await state.ollama.close()
    await state.qdrant.close()
    if hasattr(state.graph, 'close'):
        state.graph.close()


# ==================== FastAPI App ====================

app = FastAPI(
    title="Financial Lineage Tool (Local with Neo4j)",
    description="Local development version using Ollama + Qdrant + Neo4j (cloud graph database)",
    version="1.0.0-local",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==================== Endpoints ====================

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Check health of all local services."""
    services = {
        "api": "up",
        "ollama": "unknown",
        "qdrant": "unknown",
        "graph": "up"  # Always up - it's in-memory!
    }
    
    # Check Ollama
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            r = await client.get(f"{config.OLLAMA_HOST}/api/tags")
            services["ollama"] = "up" if r.status_code == 200 else "down"
    except Exception:
        services["ollama"] = "down"
    
    # Check Qdrant
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            r = await client.get(f"http://{config.QDRANT_HOST}:{config.QDRANT_PORT}/health")
            services["qdrant"] = "up" if r.status_code == 200 else "down"
    except Exception:
        services["qdrant"] = "down"
    
    overall = "healthy" if services["ollama"] == "up" else "degraded"
    
    return HealthResponse(
        status=overall,
        services=services,
        timestamp=datetime.utcnow().isoformat()
    )


@app.post("/api/v1/lineage/query", response_model=LineageResponse)
async def query_lineage(request: LineageQueryRequest):
    """Query data lineage using natural language."""
    if not state.agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    result = await state.agent.query(request.question)
    
    return LineageResponse(
        question=result["question"],
        answer=result["answer"],
        sources=result.get("sources", []),
        graph_entities=result.get("graph_entities", []),
        confidence=result["confidence"]
    )


@app.post("/api/v1/ingest/sql")
async def ingest_sql(request: SqlIngestRequest):
    """
    Parses a raw SQL string and ingests its lineage into the knowledge graph.
    """
    if not state.extractor:
        raise HTTPException(status_code=503, detail="Graph Extractor not initialized")
    
    try:
        state.extractor.ingest_sql_lineage(
            sql_content=request.sql_content,
            dialect=request.dialect,
            source_file=request.source_file
        )
        return {"status": "success", "source": request.source_file}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to ingest SQL: {e}")


@app.post("/api/v1/ingest")
async def ingest_file(request: IngestRequest, background_tasks: BackgroundTasks):
    """Ingest a file for lineage analysis."""
    
    # Check file exists
    file_path = Path(request.file_path)
    if not file_path.exists():
        raise HTTPException(status_code=404, detail=f"File not found: {request.file_path}")
    
    async def do_ingest(file_path: str, file_type: str):
        """Background ingestion task."""
        # Import chunker
        import sys
        sys.path.insert(0, str(Path(__file__).parent.parent.parent))
        from src.ingestion.semantic_chunker import SemanticChunker
        
        chunker = SemanticChunker()
        
        # Read file
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Chunk it
        chunks = chunker.chunk_file(content, file_path)
        
        # Embed and store each chunk
        for i, chunk in enumerate(chunks):
            try:
                embedding = await state.ollama.embed(chunk.to_embedding_text())
                
                await state.qdrant.upsert(
                    collection="code_chunks",
                    points=[{
                        "id": hash(f"{file_path}_{i}") % (10**12),  # Qdrant needs int IDs
                        "vector": embedding,
                        "payload": {
                            "content": chunk.content,
                            "file_path": str(chunk.file_path),
                            "chunk_type": chunk.chunk_type.value,
                            "tables": chunk.tables_referenced,
                            "columns": chunk.columns_referenced
                        }
                    }]
                )
                
                # Add entities to graph
                for table in chunk.tables_referenced:
                    state.graph.add_entity(
                        entity_id=table.lower().replace(".", "_"),
                        entity_type="Table",
                        name=table,
                        source_file=str(file_path)
                    )
                
            except Exception as e:
                print(f"Error processing chunk {i}: {e}")
        
        print(f"✅ Ingested {len(chunks)} chunks from {file_path}")
    
    background_tasks.add_task(do_ingest, str(file_path), request.file_type)
    
    return {"status": "accepted", "file": str(file_path)}


# ==================== Graph Endpoints ====================

@app.get("/api/v1/graph/stats")
async def get_graph_stats():
    """Get knowledge graph statistics."""
    return state.graph.get_stats()


@app.post("/api/v1/graph/entity")
async def add_entity(request: EntityRequest):
    """Add an entity to the knowledge graph."""
    state.graph.add_entity(
        entity_id=request.entity_id,
        entity_type=request.entity_type,
        name=request.name,
        **request.properties
    )
    return {"status": "created", "entity_id": request.entity_id}


@app.post("/api/v1/graph/relationship")
async def add_relationship(request: RelationshipRequest):
    """Add a relationship to the knowledge graph."""
    state.graph.add_relationship(
        source_id=request.source_id,
        target_id=request.target_id,
        relationship_type=request.relationship_type,
        **request.properties
    )
    return {"status": "created"}


@app.get("/api/v1/graph/entity/{entity_id}")
async def get_entity(entity_id: str):
    """Get an entity by ID."""
    entity = state.graph.get_entity(entity_id)
    if not entity:
        raise HTTPException(status_code=404, detail="Entity not found")
    return entity


@app.get("/api/v1/graph/search")
async def search_entities(name: str):
    """Search entities by name."""
    return state.graph.find_by_name(name)


@app.get("/api/v1/graph/lineage/{entity_id}")
async def get_lineage(entity_id: str, direction: str = "both", max_depth: int = 5):
    """Get lineage for an entity."""
    result = {"entity_id": entity_id}
    
    if direction in ["upstream", "both"]:
        result["upstream"] = state.graph.get_upstream(entity_id, max_depth)
    
    if direction in ["downstream", "both"]:
        result["downstream"] = state.graph.get_downstream(entity_id, max_depth)
    
    return result


@app.get("/api/v1/models")
async def list_models():
    """List available Ollama models."""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            r = await client.get(f"{config.OLLAMA_HOST}/api/tags")
            return r.json()
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Ollama not available: {e}")


# ==================== Main ====================

if __name__ == "__main__":
    import uvicorn

    print("""
    ================================================================
         Financial Lineage Tool - LOCAL with Neo4j
    ================================================================
      Using services:
      * Ollama for LLM + Embeddings (local)
      * Qdrant for Vector Search (local)
      * Neo4j for Knowledge Graph (cloud)
    ================================================================
    """)

    uvicorn.run(app, host="0.0.0.0", port=8000)
