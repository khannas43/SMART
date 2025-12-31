#!/usr/bin/env python3
"""
Verify that all database schemas are created correctly
Tests all portal databases and warehouse
"""

import sys
import os

# Add shared utils to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'ai-ml', 'shared', 'utils'))

from db_connector import DBConnector

# Database configurations
DATABASES = {
    'smart_citizen': {
        'description': 'Citizen Portal',
        'expected_tables': [
            'citizens', 'schemes', 'service_applications', 'documents',
            'application_status_history', 'notifications', 'payments',
            'feedback', 'audit_log'
        ]
    },
    'smart_dept': {
        'description': 'Department Portal',
        'expected_tables': [
            'departments', 'dept_users', 'designations', 'workflows',
            'application_assignments', 'processing_actions', 'approval_chains',
            'document_verifications', 'dashboard_metrics', 'dept_notifications',
            'dept_audit_log'
        ]
    },
    'smart_aiml': {
        'description': 'AIML Portal',
        'expected_tables': [
            'ml_use_cases', 'ml_models', 'mlflow_experiments', 'mlflow_runs',
            'predictions', 'batch_prediction_jobs', 'pipeline_runs',
            'model_monitoring', 'analytics_cache'
        ]
    },
    'smart_monitor': {
        'description': 'Monitor Portal',
        'expected_tables': [
            'system_components', 'health_checks', 'system_metrics',
            'performance_metrics', 'system_logs', 'log_aggregations',
            'alert_rules', 'alert_incidents', 'admin_users', 'monitor_audit_log'
        ]
    },
    'smart_warehouse': {
        'description': 'AIML Data Warehouse',
        'expected_tables': [
            'dim_date', 'dim_citizen', 'dim_scheme', 'dim_department',
            'fact_service_applications', 'fact_application_processing',
            'fact_eligibility_scoring', 'agg_daily_applications',
            'etl_batches', 'etl_data_quality'
        ]
    }
}

def verify_database(db_name, config, host="172.17.16.1", port=5432, user="sameer", password="anjali143"):
    """Verify database schema"""
    print(f"\n{'='*60}")
    print(f"Verifying: {config['description']} ({db_name})")
    print(f"{'='*60}")
    
    try:
        db = DBConnector(
            host=host,
            port=port,
            database=db_name,
            user=user,
            password=password
        )
        db.connect()
        
        # Get all tables
        tables = db.list_tables()
        print(f"\n📊 Found {len(tables)} table(s)")
        
        # Check expected tables
        missing_tables = []
        found_tables = []
        
        for expected_table in config['expected_tables']:
            if expected_table in tables:
                found_tables.append(expected_table)
                print(f"  ✅ {expected_table}")
            else:
                missing_tables.append(expected_table)
                print(f"  ❌ {expected_table} - MISSING")
        
        # Check for unexpected tables
        unexpected_tables = [t for t in tables if t not in config['expected_tables']]
        if unexpected_tables:
            print(f"\n⚠️  Unexpected tables found: {', '.join(unexpected_tables)}")
        
        # Summary
        print(f"\n📋 Summary:")
        print(f"  Expected: {len(config['expected_tables'])}")
        print(f"  Found: {len(found_tables)}")
        print(f"  Missing: {len(missing_tables)}")
        
        if missing_tables:
            print(f"\n❌ Missing tables: {', '.join(missing_tables)}")
            db.disconnect()
            return False
        else:
            print(f"\n✅ All expected tables found!")
            db.disconnect()
            return True
            
    except Exception as e:
        print(f"\n❌ Error connecting to database: {e}")
        return False

def main():
    print("="*60)
    print("SMART Platform - Database Schema Verification")
    print("="*60)
    
    host = os.getenv('DB_HOST', '172.17.16.1')
    port = int(os.getenv('DB_PORT', '5432'))
    user = os.getenv('DB_USER', 'sameer')
    password = os.getenv('DB_PASSWORD', 'anjali143')
    
    all_passed = True
    results = {}
    
    for db_name, config in DATABASES.items():
        result = verify_database(db_name, config, host, port, user, password)
        results[db_name] = result
        if not result:
            all_passed = False
    
    # Final summary
    print(f"\n{'='*60}")
    print("Verification Summary")
    print(f"{'='*60}")
    
    for db_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"  {DATABASES[db_name]['description']:20} {db_name:20} {status}")
    
    if all_passed:
        print(f"\n✅ All databases verified successfully!")
        return 0
    else:
        print(f"\n❌ Some databases failed verification")
        return 1

if __name__ == "__main__":
    sys.exit(main())

