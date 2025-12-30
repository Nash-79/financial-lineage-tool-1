"""
Example: End-to-End Financial Lineage Tool Usage

This script demonstrates how to:
1. Ingest a code repository
2. Build the knowledge graph
3. Query lineage using natural language
4. Get column-level lineage
5. Validate lineage paths
"""

import asyncio
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# In production, import from installed package
# from financial_lineage_tool.ingestion import SemanticChunker
# from financial_lineage_tool.knowledge_graph import CosmosGremlinClient
# from financial_lineage_tool.search import CodeSearchIndex
# from financial_lineage_tool.agents import SupervisorAgent


# ==================== Example SQL Code for Testing ====================

EXAMPLE_SQL = """
-- Example: Customer Dimension ETL
-- This creates dim_customer from raw customer data

WITH customer_base AS (
    SELECT 
        customer_id,
        first_name,
        last_name,
        email,
        created_date,
        status
    FROM bronze.raw_customers
    WHERE status = 'active'
),

customer_orders AS (
    SELECT 
        customer_id,
        COUNT(*) as total_orders,
        SUM(order_amount) as total_spent,
        MAX(order_date) as last_order_date
    FROM bronze.raw_orders
    GROUP BY customer_id
),

customer_enriched AS (
    SELECT 
        cb.customer_id,
        CONCAT(cb.first_name, ' ', cb.last_name) as full_name,
        cb.email,
        CAST(cb.created_date AS DATE) as customer_since,
        COALESCE(co.total_orders, 0) as order_count,
        COALESCE(co.total_spent, 0.00) as lifetime_value,
        CASE 
            WHEN co.total_spent > 10000 THEN 'VIP'
            WHEN co.total_spent > 1000 THEN 'Regular'
            ELSE 'New'
        END as customer_tier,
        co.last_order_date
    FROM customer_base cb
    LEFT JOIN customer_orders co ON cb.customer_id = co.customer_id
)

INSERT INTO gold.dim_customer (
    customer_id,
    full_name,
    email,
    customer_since,
    order_count,
    lifetime_value,
    customer_tier,
    last_order_date,
    updated_at
)
SELECT 
    customer_id,
    full_name,
    email,
    customer_since,
    order_count,
    lifetime_value,
    customer_tier,
    last_order_date,
    CURRENT_TIMESTAMP as updated_at
FROM customer_enriched;
"""


# ==================== Demo Functions ====================

async def demo_semantic_chunking():
    """Demonstrate semantic chunking of SQL code."""
    print("\n" + "="*60)
    print("DEMO: Semantic Chunking")
    print("="*60)
    
    from src.ingestion.semantic_chunker import SemanticChunker, SQLChunker
    
    chunker = SQLChunker(max_tokens=1500)
    chunks = chunker.chunk(EXAMPLE_SQL, "etl/customer_transform.sql")
    
    print(f"\nFound {len(chunks)} chunks:\n")
    
    for i, chunk in enumerate(chunks):
        print(f"--- Chunk {i+1}: {chunk.chunk_type.value} ---")
        print(f"Tables: {chunk.tables_referenced}")
        print(f"Columns: {chunk.columns_referenced[:5]}..." if len(chunk.columns_referenced) > 5 else f"Columns: {chunk.columns_referenced}")
        print(f"Tokens: {chunk.token_count}")
        print(f"Content preview: {chunk.content[:200]}...\n")


async def demo_entity_extraction():
    """Demonstrate entity extraction for knowledge graph."""
    print("\n" + "="*60)
    print("DEMO: Entity Extraction")
    print("="*60)
    
    from src.knowledge_graph.cosmos_client import (
        GraphEntity, GraphRelationship, EntityType, RelationshipType,
        create_table_entity, create_column_entity
    )
    
    # Extract entities from our example
    entities = []
    relationships = []
    
    # Source tables
    raw_customers = create_table_entity("bronze", "dbo", "raw_customers")
    raw_orders = create_table_entity("bronze", "dbo", "raw_orders")
    entities.extend([raw_customers, raw_orders])
    
    # Target table
    dim_customer = create_table_entity("gold", "dbo", "dim_customer")
    entities.append(dim_customer)
    
    # Source columns
    source_columns = [
        ("raw_customers", "first_name", "VARCHAR(50)"),
        ("raw_customers", "last_name", "VARCHAR(50)"),
        ("raw_customers", "email", "VARCHAR(100)"),
        ("raw_orders", "order_amount", "DECIMAL(18,2)"),
    ]
    
    # Target columns with derivation
    target_columns = [
        ("dim_customer", "full_name", "VARCHAR(101)", "CONCAT(first_name, ' ', last_name)"),
        ("dim_customer", "lifetime_value", "DECIMAL(18,2)", "SUM(order_amount)"),
        ("dim_customer", "customer_tier", "VARCHAR(20)", "CASE expression"),
    ]
    
    print("\nExtracted Entities:")
    for e in entities:
        print(f"  - {e.entity_type.value}: {e.database}.{e.schema}.{e.name}")
    
    print("\nSource Columns:")
    for table, col, dtype in source_columns:
        print(f"  - {table}.{col} ({dtype})")
    
    print("\nTarget Columns with Transformations:")
    for table, col, dtype, transform in target_columns:
        print(f"  - {table}.{col} ({dtype})")
        print(f"    Derived via: {transform}")


async def demo_lineage_query():
    """Demonstrate natural language lineage query."""
    print("\n" + "="*60)
    print("DEMO: Natural Language Lineage Query")
    print("="*60)
    
    # Simulated query and response
    query = "What is the complete lineage of customer_tier in dim_customer?"
    
    print(f"\nQuery: {query}")
    print("\n--- Agent Processing ---")
    print("1. Supervisor Agent receives query")
    print("2. Routes to Knowledge Graph Agent for entity lookup")
    print("3. Routes to SQL Corpus Agent for transformation logic")
    print("4. Routes to Validation Agent for type checking")
    print("5. Synthesizes results")
    
    print("\n--- Response ---")
    response = """
## Summary
The `customer_tier` column in `gold.dim_customer` is derived from the `total_spent` 
aggregation of `bronze.raw_orders.order_amount`, using a CASE expression.

## Lineage Path
```
bronze.raw_orders.order_amount
    ↓ [SUM aggregation]
customer_orders CTE (total_spent)
    ↓ [CASE expression]
gold.dim_customer.customer_tier
```

## Transformation Logic
```sql
CASE 
    WHEN total_spent > 10000 THEN 'VIP'
    WHEN total_spent > 1000 THEN 'Regular'
    ELSE 'New'
END as customer_tier
```

## Data Type Changes
- Source: DECIMAL(18,2) (order_amount)
- Intermediate: DECIMAL(18,2) (total_spent after SUM)
- Target: VARCHAR(20) (customer_tier after CASE)

## Validation
✓ Transformation logic is valid
✓ Data type conversion is explicit via CASE
⚠ Note: Null handling via COALESCE ensures no NULL values

## Sources
- etl/customer_transform.sql (lines 25-30)
- Knowledge graph: 3 entities, 2 relationships traversed

## Confidence: High (0.95)
All transformations are explicitly defined in code.
"""
    print(response)


async def demo_api_usage():
    """Demonstrate API usage patterns."""
    print("\n" + "="*60)
    print("DEMO: API Usage Examples")
    print("="*60)
    
    print("""
# Query lineage via natural language
curl -X POST http://localhost:8000/api/v1/lineage/query \\
  -H "Content-Type: application/json" \\
  -d '{
    "question": "What is the lineage of customer_tier in dim_customer?",
    "include_sql_context": true,
    "include_validation": true
  }'

# Get column lineage directly
curl -X POST http://localhost:8000/api/v1/lineage/column \\
  -H "Content-Type: application/json" \\
  -d '{
    "table_name": "gold.dim_customer",
    "column_name": "lifetime_value",
    "direction": "upstream"
  }'

# Ingest a repository
curl -X POST http://localhost:8000/api/v1/ingest/repository \\
  -H "Content-Type: application/json" \\
  -d '{
    "repo_url": "https://github.com/org/data-pipelines",
    "branch": "main",
    "file_patterns": ["*.sql", "*.py"]
  }'

# Check ingestion status
curl http://localhost:8000/api/v1/ingest/status/{job_id}

# Traverse the knowledge graph
curl -X POST http://localhost:8000/api/v1/graph/traverse \\
  -H "Content-Type: application/json" \\
  -d '{
    "start_node": "gold_dbo_dim_customer",
    "direction": "inbound",
    "max_depth": 5
  }'

# Search the code corpus
curl "http://localhost:8000/api/v1/search/code?query=customer%20tier&language=sql"
""")


async def demo_graph_queries():
    """Demonstrate Gremlin graph queries."""
    print("\n" + "="*60)
    print("DEMO: Knowledge Graph Queries (Gremlin)")
    print("="*60)
    
    print("""
# Find all upstream sources for a column
g.V('gold_dbo_dim_customer_lifetime_value')
  .repeat(
    inE('DERIVES_FROM').outV()
    .simplePath()
  )
  .until(inE('DERIVES_FROM').count().is(0))
  .path()
  .by(valueMap(true))

# Find all tables that depend on raw_customers
g.V().has('name', 'raw_customers')
  .repeat(
    outE('TRANSFORMS_TO').inV()
    .simplePath()
  )
  .until(loops().is(5))
  .dedup()
  .valueMap('name', 'entity_type')

# Get transformation chain for a column
g.V('gold_dbo_dim_customer_customer_tier')
  .repeat(
    inE('DERIVES_FROM')
    .as('edge')
    .outV()
    .as('source')
  )
  .until(loops().is(10))
  .select('edge', 'source')
  .by(valueMap('transformation_logic'))
  .by(valueMap('name', 'data_type'))

# Find columns with type changes
g.V().hasLabel('Column')
  .where(
    inE('DERIVES_FROM').outV()
    .has('data_type', neq(__.select('data_type')))
  )
  .valueMap('name', 'data_type')
""")


async def main():
    """Run all demos."""
    print("\n" + "="*60)
    print("FINANCIAL DATA LINEAGE TOOL - DEMO")
    print("="*60)
    
    await demo_semantic_chunking()
    await demo_entity_extraction()
    await demo_lineage_query()
    await demo_api_usage()
    await demo_graph_queries()
    
    print("\n" + "="*60)
    print("DEMO COMPLETE")
    print("="*60)
    print("""
Next Steps:
1. Set up Azure resources using Terraform: cd infrastructure/terraform && terraform apply
2. Configure .env with your credentials
3. Run the API: uvicorn src.api.main:app --reload
4. Ingest your code repositories
5. Query lineage!

For more information, see:
- ARCHITECTURE.md - System architecture and design
- README.md - Quick start guide
- config/prompts/ - Agent prompt templates
""")


if __name__ == "__main__":
    asyncio.run(main())
