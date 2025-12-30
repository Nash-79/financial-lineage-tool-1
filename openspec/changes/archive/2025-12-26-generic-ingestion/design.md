# Design: Generic Corpus Ingestion

## Context
Currently, `add_adventureworks_entities.py` contains hardcoded dictionaries of table definitions. This is unmaintainable. We need to parse the source files directly.

## Architecture

### 1. The Dispatcher (`ingest_corpus.py`)
A CLI script that acts as the entry point.
- **Responsibility**: File discovery and orchestration.
- **Logic**:
  ```python
  for root, dirs, files in os.walk(target_dir):
      for file in files:
          if file.endswith(('.sql', '.py', '.json')):
               extractor.ingest_file(os.path.join(root, file))
  ```

### 2. The Parser (`CodeParser`)
Stateless component that converts raw text into structured metadata (AST-like dicts).
- **SQL**: Existing `sqlglot` implementation.
- **Python**: Use `ast` module.
    - Entities: Classes, Functions.
    - Relationships: Imports, Calls (future).
- **JSON**: Use `json` module.
    - Entities: Keys.
    - Relationships: Nesting.

### 3. The Extractor (`GraphExtractor`)
Stateful component that interacts with Neo4j.
- **Extensions**:
    - `ingest_file(path)`: Facade method.
    - `ingest_python_structure(metadata)`: Creates nodes for Python classes/funcs.
    - `ingest_json_structure(metadata)`: Creates nodes for JSON objects.

## Data Model Extensions
To support generic code, we will add/reuse these Node Labels:
- `File` {name, path, language}
- `Class` {name} (for Python)
- `Function` {name} (Shared key for SQL Funcs and Py Funcs)
- `Module` {name} (for Python imports)

## Trade-offs
- **Precision vs Generality**: SQL parsing with `sqlglot` is robust for lineage. Python parsing with `ast` creates a static structure graph, but dynamic runtime lineage is hard. We accept static structure for now.
- **Performance**: Parsing thousands of files may be slow. `GraphExtractor` should batch Neo4j writes in the future (out of scope for now).
