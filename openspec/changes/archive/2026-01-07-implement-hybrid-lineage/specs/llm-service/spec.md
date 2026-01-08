## ADDED Requirements
### Requirement: LLM-Driven Lineage Inference
The system SHALL use LLMs to propose lineage edges based on code analysis.

#### Scenario: Inferring hidden dependencies
- **WHEN** the inference service runs on a code repository
- **THEN** it uses the LLM to analyze code chunks for data flow
- **AND** produces structured edge proposals with confidence scores
- **AND** each proposal includes at least `source_id_hint`, `target_id_hint`, `type`, `confidence`, `evidence`, and a short `rationale`
- **AND** uses the graph structure to validate entity existence before proposing edges
- **AND** when proposals are ingested, they are stored with `source="ollama_llm"` and initial `status="pending_review"`

### Requirement: Inference Context Retrieval
The system SHALL provide relevant graph and code context to the LLM for inference.

#### Scenario: Context assembly
- **WHEN** preparing an inference prompt
- **THEN** the system retrieves near-neighbor nodes from the graph
- **AND** retrieves relevant code chunks from the vector store
- **AND** fits them within the model's context window
