# Spec Delta: LLM Service

## MODIFIED Requirements

### REQ-LLM-CONTEXT-001: Scoped Context Retrieval
`LineageInferenceService.retrieve_context()` SHALL filter graph nodes by label and project scope to avoid full graph scans.

- At least `File` and `DataAsset` labels MUST be included in the query
- Additional labels (e.g., `Column`, `FunctionOrProcedure`) MAY be included
- If `project_id` is provided in the request, the query SHOULD filter by project scope

> [!NOTE]
> `LineageInferenceRequest` will be extended with an optional `project_id` field. If not provided, retrieval will be scope-only.

#### Scenario: Scoped retrieval
- Given a scope parameter is provided
- When retrieving context from Neo4j
- Then the query SHALL include label filters (at minimum `File`, `DataAsset`)
- And the query SHOULD include project_id filter if available in request

### REQ-LLM-QDRANT-001: Code Chunk Context
`LineageInferenceService.retrieve_context()` SHALL include semantic code chunk retrieval from Qdrant when embeddings are available.

- Embeddings SHALL be generated using `OllamaClient.embed()` with `config.EMBEDDING_MODEL`
- If embedding generation or Qdrant search fails, the service SHALL still return graph-only context (graceful degradation)

#### Scenario: Code context inclusion
- Given the scope matches ingested files
- When retrieving context
- Then the service SHALL generate embeddings for the scope using OllamaClient
- And search Qdrant for relevant code chunks
- And include chunks in the context response

#### Scenario: Graceful degradation
- Given Qdrant is unavailable or embedding fails
- When retrieving context
- Then the service SHALL log a warning
- And return graph-only context without failing the request
