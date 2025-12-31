-- Grant permissions on eligibility schema
-- Run this as a superuser (postgres) or schema owner

-- Grant usage on schema
GRANT USAGE ON SCHEMA eligibility TO sameer;

-- Grant create on schema
GRANT CREATE ON SCHEMA eligibility TO sameer;

-- Grant all privileges on all tables in schema (existing and future)
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA eligibility TO sameer;
ALTER DEFAULT PRIVILEGES IN SCHEMA eligibility GRANT ALL ON TABLES TO sameer;

-- Grant all privileges on all sequences in schema
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA eligibility TO sameer;
ALTER DEFAULT PRIVILEGES IN SCHEMA eligibility GRANT ALL ON SEQUENCES TO sameer;

-- Grant execute on all functions in schema
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA eligibility TO sameer;
ALTER DEFAULT PRIVILEGES IN SCHEMA eligibility GRANT EXECUTE ON FUNCTIONS TO sameer;

-- Make sameer the owner of the schema (optional, but ensures full control)
ALTER SCHEMA eligibility OWNER TO sameer;

