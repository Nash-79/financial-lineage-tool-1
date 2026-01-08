# Spec: LLM Service

## ADDED Requirements

### API Trigger for Lineage Inference
#### Scenario: Trigger inference for a file
Given the backend is running with Ollama configured
When a POST request is made to `/api/v1/lineage/infer` with `scope="src/models/user.py"`
Then the service retrieves context and calls Ollama
And returns a list of proposed edges (status `pending_review`)
And these edges are persisted in Neo4j
