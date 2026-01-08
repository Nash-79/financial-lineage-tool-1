# Spec: Configuration

## MODIFIED Requirements

### SQL Dialects must be stored in DuckDB
#### Scenario: Load dialects from database
Given the application starts up
When the configuration service initializes
Then it loads the list of enabled SQL dialects from the `sql_dialects` DuckDB table
And `GET /api/v1/config/sql-dialects` returns these values
