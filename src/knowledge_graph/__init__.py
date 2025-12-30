# Knowledge Graph module for Cosmos DB Gremlin operations
from .cosmos_client import (
    CosmosGremlinClient,
    GraphEntity,
    GraphRelationship,
    EntityType,
    RelationshipType,
    create_table_entity,
    create_column_entity,
    create_derives_from_relationship
)
