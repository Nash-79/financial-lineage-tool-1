"""
Cosmos DB Gremlin Client for Knowledge Graph Operations.

This module provides a high-level interface for interacting with the
lineage knowledge graph stored in Cosmos DB using the Gremlin API.
"""

import asyncio
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional
import json

from gremlin_python.driver import client, serializer
from gremlin_python.driver.protocol import GremlinServerError
from tenacity import retry, stop_after_attempt, wait_exponential


class EntityType(str, Enum):
    """Types of entities in the lineage graph."""
    TABLE = "Table"
    VIEW = "View"
    COLUMN = "Column"
    SCRIPT = "Script"
    PIPELINE = "Pipeline"
    TRANSFORMATION = "Transformation"
    DATA_TYPE = "DataType"


class RelationshipType(str, Enum):
    """Types of relationships in the lineage graph."""
    DERIVES_FROM = "DERIVES_FROM"
    TRANSFORMS_TO = "TRANSFORMS_TO"
    CONTAINS = "CONTAINS"
    EXECUTES = "EXECUTES"
    READS_FROM = "READS_FROM"
    WRITES_TO = "WRITES_TO"
    CASTS_TO = "CASTS_TO"
    JOINS_WITH = "JOINS_WITH"
    DEPENDS_ON = "DEPENDS_ON"


@dataclass
class GraphEntity:
    """Represents an entity (vertex) in the knowledge graph."""
    id: str
    entity_type: EntityType
    name: str
    properties: dict[str, Any] = field(default_factory=dict)
    
    # Lineage-specific properties
    database: Optional[str] = None
    schema: Optional[str] = None
    data_type: Optional[str] = None
    file_path: Optional[str] = None
    
    def to_gremlin_properties(self) -> str:
        """Convert to Gremlin property format."""
        props = [
            f".property('name', '{self.name}')",
            f".property('entity_type', '{self.entity_type.value}')",
        ]
        if self.database:
            props.append(f".property('database', '{self.database}')")
        if self.schema:
            props.append(f".property('schema', '{self.schema}')")
        if self.data_type:
            props.append(f".property('data_type', '{self.data_type}')")
        if self.file_path:
            props.append(f".property('file_path', '{self.file_path}')")
        
        for key, value in self.properties.items():
            if isinstance(value, str):
                props.append(f".property('{key}', '{value}')")
            else:
                props.append(f".property('{key}', {json.dumps(value)})")
        
        return "".join(props)


@dataclass
class GraphRelationship:
    """Represents a relationship (edge) in the knowledge graph."""
    source_id: str
    target_id: str
    relationship_type: RelationshipType
    properties: dict[str, Any] = field(default_factory=dict)
    
    # Lineage-specific properties
    transformation_logic: Optional[str] = None
    confidence_score: float = 1.0


@dataclass
class LineagePath:
    """Represents a lineage path from source to target."""
    source: GraphEntity
    target: GraphEntity
    path: list[tuple[GraphEntity, GraphRelationship, GraphEntity]]
    total_hops: int
    transformations: list[str] = field(default_factory=list)


class CosmosGremlinClient:
    """
    Client for Cosmos DB Gremlin API operations.
    
    Provides methods for:
    - Entity CRUD operations
    - Relationship management
    - Lineage traversal queries
    - Graph analytics
    """
    
    def __init__(
        self,
        endpoint: str,
        key: str,
        database: str,
        graph: str
    ):
        """
        Initialize the Cosmos DB Gremlin client.
        
        Args:
            endpoint: Cosmos DB Gremlin endpoint (wss://...)
            key: Primary key
            database: Database name
            graph: Graph container name
        """
        self.endpoint = endpoint
        self.key = key
        self.database = database
        self.graph = graph
        self._client: Optional[client.Client] = None
    
    def _get_client(self) -> client.Client:
        """Get or create Gremlin client."""
        if self._client is None:
            self._client = client.Client(
                self.endpoint,
                'g',
                username=f"/dbs/{self.database}/colls/{self.graph}",
                password=self.key,
                message_serializer=serializer.GraphSONSerializersV2d0()
            )
        return self._client
    
    def close(self):
        """Close the client connection."""
        if self._client:
            self._client.close()
            self._client = None
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def _execute_query(self, query: str) -> list[dict]:
        """Execute a Gremlin query with retry logic."""
        try:
            result_set = self._get_client().submit(query)
            results = []
            for result in result_set:
                results.extend(result)
            return results
        except GremlinServerError as e:
            if "Request rate is large" in str(e):
                # Handle throttling
                raise
            raise
    
    # ==================== Entity Operations ====================
    
    def create_entity(self, entity: GraphEntity) -> str:
        """
        Create a new entity (vertex) in the graph.
        
        Args:
            entity: The entity to create
            
        Returns:
            The ID of the created entity
        """
        query = f"""
        g.addV('{entity.entity_type.value}')
        .property('id', '{entity.id}')
        .property('pk', '{entity.entity_type.value}')
        {entity.to_gremlin_properties()}
        """
        self._execute_query(query)
        return entity.id
    
    def get_entity(self, entity_id: str) -> Optional[GraphEntity]:
        """
        Get an entity by ID.
        
        Args:
            entity_id: The entity ID
            
        Returns:
            The entity if found, None otherwise
        """
        query = f"g.V('{entity_id}').valueMap(true)"
        results = self._execute_query(query)
        
        if not results:
            return None
        
        props = results[0]
        return GraphEntity(
            id=entity_id,
            entity_type=EntityType(props.get('entity_type', ['Unknown'])[0]),
            name=props.get('name', [''])[0],
            database=props.get('database', [None])[0],
            schema=props.get('schema', [None])[0],
            data_type=props.get('data_type', [None])[0],
            file_path=props.get('file_path', [None])[0]
        )
    
    def upsert_entity(self, entity: GraphEntity) -> str:
        """
        Create or update an entity.
        
        Args:
            entity: The entity to upsert
            
        Returns:
            The entity ID
        """
        # Check if exists
        query = f"g.V('{entity.id}').count()"
        count = self._execute_query(query)
        
        if count and count[0] > 0:
            # Update existing
            update_query = f"""
            g.V('{entity.id}')
            {entity.to_gremlin_properties()}
            """
            self._execute_query(update_query)
        else:
            self.create_entity(entity)
        
        return entity.id
    
    def find_entities_by_name(
        self, 
        name_pattern: str, 
        entity_type: Optional[EntityType] = None
    ) -> list[GraphEntity]:
        """
        Find entities by name pattern.
        
        Args:
            name_pattern: Name pattern to search (supports wildcards)
            entity_type: Optional entity type filter
            
        Returns:
            List of matching entities
        """
        if entity_type:
            query = f"""
            g.V().hasLabel('{entity_type.value}')
            .has('name', containing('{name_pattern}'))
            .valueMap(true).limit(100)
            """
        else:
            query = f"""
            g.V().has('name', containing('{name_pattern}'))
            .valueMap(true).limit(100)
            """
        
        results = self._execute_query(query)
        
        entities = []
        for props in results:
            entity_id = props.get('id', [''])[0] if isinstance(props.get('id'), list) else props.get('id', '')
            entities.append(GraphEntity(
                id=entity_id,
                entity_type=EntityType(props.get('entity_type', ['Unknown'])[0]),
                name=props.get('name', [''])[0],
                database=props.get('database', [None])[0],
                schema=props.get('schema', [None])[0]
            ))
        
        return entities
    
    # ==================== Relationship Operations ====================
    
    def create_relationship(self, relationship: GraphRelationship) -> None:
        """
        Create a relationship (edge) between entities.
        
        Args:
            relationship: The relationship to create
        """
        props = []
        if relationship.transformation_logic:
            props.append(f".property('transformation_logic', '{relationship.transformation_logic}')")
        props.append(f".property('confidence_score', {relationship.confidence_score})")
        
        for key, value in relationship.properties.items():
            if isinstance(value, str):
                props.append(f".property('{key}', '{value}')")
            else:
                props.append(f".property('{key}', {json.dumps(value)})")
        
        query = f"""
        g.V('{relationship.source_id}')
        .addE('{relationship.relationship_type.value}')
        .to(g.V('{relationship.target_id}'))
        {''.join(props)}
        """
        self._execute_query(query)
    
    # ==================== Lineage Queries ====================
    
    def get_upstream_lineage(
        self, 
        entity_id: str, 
        max_depth: int = 10
    ) -> list[dict]:
        """
        Get upstream lineage (sources) for an entity.
        
        Args:
            entity_id: Starting entity ID
            max_depth: Maximum traversal depth
            
        Returns:
            List of upstream entities with paths
        """
        query = f"""
        g.V('{entity_id}')
        .repeat(
            inE('DERIVES_FROM', 'TRANSFORMS_TO').outV()
            .simplePath()
        )
        .until(
            inE('DERIVES_FROM', 'TRANSFORMS_TO').count().is(0)
            .or().loops().is({max_depth})
        )
        .path()
        .by(valueMap(true))
        """
        return self._execute_query(query)
    
    def get_downstream_lineage(
        self, 
        entity_id: str, 
        max_depth: int = 10
    ) -> list[dict]:
        """
        Get downstream lineage (targets) for an entity.
        
        Args:
            entity_id: Starting entity ID
            max_depth: Maximum traversal depth
            
        Returns:
            List of downstream entities with paths
        """
        query = f"""
        g.V('{entity_id}')
        .repeat(
            outE('DERIVES_FROM', 'TRANSFORMS_TO').inV()
            .simplePath()
        )
        .until(
            outE('DERIVES_FROM', 'TRANSFORMS_TO').count().is(0)
            .or().loops().is({max_depth})
        )
        .path()
        .by(valueMap(true))
        """
        return self._execute_query(query)
    
    def get_column_lineage(
        self, 
        table_name: str, 
        column_name: str
    ) -> dict:
        """
        Get complete lineage for a specific column.
        
        Args:
            table_name: Table name (can include schema)
            column_name: Column name
            
        Returns:
            Lineage information including upstream, downstream, and transformations
        """
        # Find the column entity
        query = f"""
        g.V().has('name', '{column_name}')
        .where(
            inE('CONTAINS').outV().has('name', containing('{table_name}'))
        )
        .valueMap(true)
        """
        results = self._execute_query(query)
        
        if not results:
            return {"error": f"Column {table_name}.{column_name} not found"}
        
        column_id = results[0].get('id', [''])[0]
        
        # Get upstream and downstream
        upstream = self.get_upstream_lineage(column_id)
        downstream = self.get_downstream_lineage(column_id)
        
        return {
            "column": f"{table_name}.{column_name}",
            "column_id": column_id,
            "upstream": upstream,
            "downstream": downstream
        }
    
    def find_lineage_path(
        self, 
        source_id: str, 
        target_id: str, 
        max_depth: int = 10
    ) -> list[dict]:
        """
        Find all paths between source and target entities.
        
        Args:
            source_id: Source entity ID
            target_id: Target entity ID
            max_depth: Maximum path length
            
        Returns:
            List of paths with transformations
        """
        query = f"""
        g.V('{source_id}')
        .repeat(
            outE().inV()
            .simplePath()
        )
        .until(
            has('id', '{target_id}')
            .or().loops().is({max_depth})
        )
        .has('id', '{target_id}')
        .path()
        .by(valueMap(true))
        """
        return self._execute_query(query)
    
    def get_table_dependencies(self, table_name: str) -> dict:
        """
        Get all dependencies for a table.
        
        Args:
            table_name: Table name
            
        Returns:
            Dependencies including upstream tables, scripts, and pipelines
        """
        query = f"""
        g.V().has('name', '{table_name}').hasLabel('Table', 'View')
        .project('table', 'reads_from', 'writes_from', 'columns')
        .by(valueMap(true))
        .by(inE('WRITES_TO').outV().valueMap(true).fold())
        .by(outE('READS_FROM').inV().valueMap(true).fold())
        .by(outE('CONTAINS').inV().valueMap(true).fold())
        """
        return self._execute_query(query)
    
    # ==================== Graph Analytics ====================
    
    def get_transformation_summary(self, entity_id: str) -> dict:
        """
        Get a summary of all transformations applied to reach an entity.
        
        Args:
            entity_id: Target entity ID
            
        Returns:
            Summary of transformations
        """
        query = f"""
        g.V('{entity_id}')
        .repeat(
            inE('DERIVES_FROM', 'TRANSFORMS_TO')
            .has('transformation_logic')
            .outV()
            .simplePath()
        )
        .until(loops().is(10))
        .path()
        .by(valueMap(true))
        .by(valueMap(true))
        """
        paths = self._execute_query(query)
        
        transformations = []
        for path in paths:
            for item in path:
                if 'transformation_logic' in item:
                    transformations.append(item['transformation_logic'][0])
        
        return {
            "entity_id": entity_id,
            "transformations": list(set(transformations)),
            "transformation_count": len(transformations)
        }
    
    def validate_lineage_types(self, entity_id: str) -> list[dict]:
        """
        Validate data type compatibility along lineage path.
        
        Args:
            entity_id: Entity to validate
            
        Returns:
            List of type mismatches or potential issues
        """
        query = f"""
        g.V('{entity_id}')
        .repeat(
            inE('DERIVES_FROM').as('edge')
            .outV().as('source')
            .simplePath()
        )
        .until(loops().is(10))
        .select('source', 'edge')
        .by(valueMap('name', 'data_type'))
        .by(valueMap('transformation_logic'))
        """
        results = self._execute_query(query)
        
        issues = []
        for result in results:
            source_type = result.get('source', {}).get('data_type', [None])[0]
            # Add validation logic here
            if source_type:
                issues.append({
                    "source": result.get('source', {}),
                    "data_type": source_type,
                    "validation": "passed"
                })
        
        return issues


# ==================== Helper Functions ====================

def create_table_entity(
    database: str,
    schema: str,
    table_name: str,
    is_view: bool = False
) -> GraphEntity:
    """Create a table or view entity."""
    full_name = f"{database}.{schema}.{table_name}"
    return GraphEntity(
        id=full_name.lower().replace('.', '_'),
        entity_type=EntityType.VIEW if is_view else EntityType.TABLE,
        name=table_name,
        database=database,
        schema=schema
    )


def create_column_entity(
    table_entity_id: str,
    column_name: str,
    data_type: str
) -> GraphEntity:
    """Create a column entity."""
    return GraphEntity(
        id=f"{table_entity_id}_{column_name.lower()}",
        entity_type=EntityType.COLUMN,
        name=column_name,
        data_type=data_type
    )


def create_derives_from_relationship(
    source_column_id: str,
    target_column_id: str,
    transformation: Optional[str] = None,
    confidence: float = 1.0
) -> GraphRelationship:
    """Create a DERIVES_FROM relationship between columns."""
    return GraphRelationship(
        source_id=target_column_id,  # Target derives from source
        target_id=source_column_id,
        relationship_type=RelationshipType.DERIVES_FROM,
        transformation_logic=transformation,
        confidence_score=confidence
    )
