# Financial Lineage Tool - Documentation Index

This directory contains all documentation for the Financial Lineage Tool project.

## Quick Start

**New users start here**:
1. [Local Setup Guide](LOCAL_SETUP_GUIDE.md) - Set up development environment
2. [SQL Organizer Quickstart](SQL_ORGANIZER_QUICKSTART.md) - Start organizing SQL files
3. [Architecture Overview](ARCHITECTURE.md) - Understand the system

## Documentation by Category

### Getting Started

| Document | Description |
|----------|-------------|
| [Local Setup Guide](LOCAL_SETUP_GUIDE.md) | Complete guide to setting up the development environment |
| [Getting Started](GETTING_STARTED.md) | **NEW** Quick start guide |
| [Docker Services](DOCKER_SERVICES.md) | **NEW** Docker service documentation |
| [Docker Troubleshooting](DOCKER_TROUBLESHOOTING.md) | Docker setup and troubleshooting |

### SQL Organization

| Document | Description |
|----------|-------------|
| [SQL Organizer Quickstart](SQL_ORGANIZER_QUICKSTART.md) | Quick start guide for SQL file organization |
| [Hierarchical Organization Guide](HIERARCHICAL_ORGANIZATION_GUIDE.md) | Comprehensive guide to hierarchical SQL organization |
| [File Watcher Guide](FILE_WATCHER_GUIDE.md) | Automatic SQL file processing with file watcher |

### Database & Infrastructure

| Document | Description |
|----------|-------------|
| [Gremlin Setup](GREMLIN_SETUP.md) | Azure Cosmos DB Gremlin API setup |
| [Qdrant Setup](QDRANT_SETUP.md) | Qdrant vector database setup |
| [AdventureWorks Guide](ADVENTUREWORKS_GUIDE.md) | Working with AdventureWorks sample database |

### Data & Exports

| Document | Description |
|----------|-------------|
| [Export Guide](EXPORT_GUIDE.md) | Exporting data from knowledge graph and embeddings |

### Architecture & Status

| Document | Description |
|----------|-------------|
| [Architecture](ARCHITECTURE.md) | System architecture and component overview |
| [Implementation Status](IMPLEMENTATION_STATUS.md) | Current implementation status and roadmap |

## Documentation by Workflow

### I want to organize SQL files

1. [SQL Organizer Quickstart](SQL_ORGANIZER_QUICKSTART.md) - Basic usage
2. [Hierarchical Organization Guide](HIERARCHICAL_ORGANIZATION_GUIDE.md) - Advanced organization
3. [File Watcher Guide](FILE_WATCHER_GUIDE.md) - Automatic processing

### I want to set up the environment

1. [Local Setup Guide](LOCAL_SETUP_GUIDE.md) - Development environment
2. [Gremlin Setup](GREMLIN_SETUP.md) - Cosmos DB setup
3. [Qdrant Setup](QDRANT_SETUP.md) - Vector database setup
4. [Docker Troubleshooting](DOCKER_TROUBLESHOOTING.md) - Docker issues

### I want to understand the system

1. [Architecture](ARCHITECTURE.md) - System overview
2. [Implementation Status](IMPLEMENTATION_STATUS.md) - Current status
3. [AdventureWorks Guide](ADVENTUREWORKS_GUIDE.md) - Sample data

### I want to export data

1. [Export Guide](EXPORT_GUIDE.md) - Export embeddings and graph data

## Quick Reference

### SQL Organization Commands

```bash
# Hierarchical organization (recommended)
python examples/test_hierarchical_organizer.py

# Start file watcher (automatic processing)
python examples/start_file_watcher.py

# Basic organization (flat structure)
python examples/demo_sql_organizer.py
```

### Development Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run API locally
python src/api/main_local.py

# Run tests
pytest tests/
```

### Utility Scripts

All utility scripts are in the `scripts/` folder:

```bash
# Add AdventureWorks entities to graph
python scripts/add_adventureworks_entities.py

# Export graph data
python scripts/export_graph_json.py

# Export embeddings
python scripts/export_embeddings_json.py

# Query Neo4j
python scripts/query_neo4j.py

# Test Qdrant
python scripts/test_qdrant.py
```

## File Organization

```
docs/
  README.md                              # This file

  Getting Started:
    LOCAL_SETUP_GUIDE.md                 # Setup guide
    DOCKER_TROUBLESHOOTING.md            # Docker help

  SQL Organization:
    SQL_ORGANIZER_QUICKSTART.md          # Quick start
    HIERARCHICAL_ORGANIZATION_GUIDE.md   # Hierarchical guide
    FILE_WATCHER_GUIDE.md                # File watcher

  Database Setup:
    GREMLIN_SETUP.md                     # Cosmos DB
    QDRANT_SETUP.md                      # Qdrant
    ADVENTUREWORKS_GUIDE.md              # Sample data

  Reference:
    ARCHITECTURE.md                      # System architecture
    IMPLEMENTATION_STATUS.md             # Project status
    EXPORT_GUIDE.md                      # Data exports
```

## Contributing

When adding new documentation:

1. **Place in docs/ folder** - All documentation goes here
2. **Update this index** - Add your document to the tables above
3. **Use descriptive names** - Clear, searchable filenames
4. **Link related docs** - Cross-reference related documentation
5. **Keep README.md clean** - Root README should be brief with link to docs/

## Document Templates

### Guide Template

```markdown
# [Feature Name] - Guide

## Overview
Brief description of the feature

## Quick Start
Step-by-step getting started

## Usage
Detailed usage instructions

## Configuration
Configuration options

## Examples
Practical examples

## Troubleshooting
Common issues and solutions

## Advanced Topics
Advanced usage patterns
```

### Reference Template

```markdown
# [Component Name] - Reference

## Overview
Component description

## API Reference
API documentation

## Configuration
Configuration options

## Examples
Code examples

## Related Documentation
Links to related docs
```

## Getting Help

- **Documentation Issues**: Check the specific guide in this folder
- **Setup Issues**: See [Local Setup Guide](LOCAL_SETUP_GUIDE.md)
- **Docker Issues**: See [Docker Troubleshooting](DOCKER_TROUBLESHOOTING.md)
- **Architecture Questions**: See [Architecture](ARCHITECTURE.md)

## Documentation Standards

1. **Clarity**: Write for beginners, explain technical terms
2. **Completeness**: Include all necessary information
3. **Examples**: Provide practical, working examples
4. **Updates**: Keep documentation current with code changes
5. **Cross-references**: Link to related documentation

---

**Last Updated**: 2025-12-08
**Documentation Version**: 1.0.0
