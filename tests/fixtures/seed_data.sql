-- Seed data for contract testing
INSERT INTO projects (id, name, description, created_at, updated_at) 
VALUES ('test-project-contract', 'Contract Test Project', 'Created for Schemathesis verification', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
ON CONFLICT (id) DO NOTHING;

INSERT INTO repositories (id, project_id, name, url, branch, created_at, updated_at)
VALUES ('test-repo-contract', 'test-project-contract', 'test-repo', 'https://github.com/test/repo', 'main', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
ON CONFLICT (id) DO NOTHING;

-- Note: Adjust based on your actual schema if needed
