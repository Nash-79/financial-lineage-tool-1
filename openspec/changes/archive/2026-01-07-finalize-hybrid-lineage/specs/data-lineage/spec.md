# Spec: Data Lineage

## MODIFIED Requirements

### Triggers must be linked to their target tables
#### Scenario: Parse Trigger with Table
Given a SQL file with `CREATE TRIGGER trg_audit ON schema.users AFTER INSERT...`
When the file is parsed and ingested
Then a `Trigger` node named `trg_audit` is created
And an `ATTACHED_TO` edge exists from `trg_audit` to the `DataAsset` `schema.users`

### Synonyms must be linked to their target objects
#### Scenario: Parse Synonym
Given a SQL file with `CREATE SYNONYM dbo.customers FOR remote.sales.customers`
When the file is parsed and ingested
Then a `Synonym` node named `dbo.customers` is created
And an `ALIAS_OF` edge exists from `dbo.customers` to the `DataAsset` `remote.sales.customers`
