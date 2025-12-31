-- Transfer ownership of all tables in eligibility schema to sameer
-- Run this as postgres superuser

-- Transfer schema ownership
ALTER SCHEMA eligibility OWNER TO sameer;

-- Transfer ownership of all tables
ALTER TABLE eligibility.scheme_eligibility_rules OWNER TO sameer;
ALTER TABLE eligibility.scheme_exclusion_rules OWNER TO sameer;
ALTER TABLE eligibility.eligibility_snapshots OWNER TO sameer;
ALTER TABLE eligibility.candidate_lists OWNER TO sameer;
ALTER TABLE eligibility.ml_model_registry OWNER TO sameer;
ALTER TABLE eligibility.evaluation_audit_log OWNER TO sameer;
ALTER TABLE eligibility.rule_change_history OWNER TO sameer;
ALTER TABLE eligibility.batch_evaluation_jobs OWNER TO sameer;
ALTER TABLE eligibility.consent_status OWNER TO sameer;
ALTER TABLE eligibility.data_quality_indicators OWNER TO sameer;
ALTER TABLE eligibility.rule_set_snapshots OWNER TO sameer;
ALTER TABLE eligibility.rule_change_detail OWNER TO sameer;
ALTER TABLE eligibility.dataset_versions OWNER TO sameer;

-- Transfer ownership of all sequences
DO $$
DECLARE
    r RECORD;
BEGIN
    FOR r IN 
        SELECT sequence_name 
        FROM information_schema.sequences 
        WHERE sequence_schema = 'eligibility'
    LOOP
        EXECUTE 'ALTER SEQUENCE eligibility.' || quote_ident(r.sequence_name) || ' OWNER TO sameer';
    END LOOP;
END $$;

-- Transfer ownership of all functions
DO $$
DECLARE
    r RECORD;
BEGIN
    FOR r IN 
        SELECT routine_name 
        FROM information_schema.routines 
        WHERE routine_schema = 'eligibility'
    LOOP
        EXECUTE 'ALTER FUNCTION eligibility.' || quote_ident(r.routine_name) || ' OWNER TO sameer';
    END LOOP;
END $$;

-- Grant all privileges
GRANT ALL ON SCHEMA eligibility TO sameer;
GRANT ALL ON ALL TABLES IN SCHEMA eligibility TO sameer;
GRANT ALL ON ALL SEQUENCES IN SCHEMA eligibility TO sameer;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA eligibility TO sameer;

