#!/usr/bin/env python3
"""
Configuration and Database Connectivity Check for Auto Approval & Straight-through Processing
Use Case ID: AI-PLATFORM-06
"""

import sys
import os
import yaml

# Add parent directories to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'shared', 'utils'))

try:
    from db_connector import DBConnector
except ImportError:
    print("❌ Error: Cannot import db_connector. Make sure shared/utils/db_connector.py exists.")
    sys.exit(1)


def check_database_config():
    """Check database configuration file exists and is valid."""
    print("1. Checking database configuration...")
    config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'db_config.yaml')
    
    if not os.path.exists(config_path):
        print(f"   ❌ db_config.yaml not found at {config_path}")
        return False
    
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    db_config = config.get('database', {})
    print(f"   ✅ db_config.yaml found")
    print(f"      Primary DB: {db_config.get('name')}@{db_config.get('host')}:{db_config.get('port')}")
    print(f"      Schema: {db_config.get('schema')}")
    return True


def test_database_connection():
    """Test primary database connection."""
    print("\n2. Testing primary database connection...")
    
    try:
        config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'db_config.yaml')
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        db_config = config['database']
        connector = DBConnector(
            host=db_config['host'],
            port=db_config['port'],
            database=db_config['name'],
            user=db_config['user'],
            password=db_config['password']
        )
        conn = connector.connect()
        
        print(f"   ✅ Connected to PostgreSQL: {db_config['host']}:{db_config['port']}/{db_config['name']}")
        
        # Check schema exists
        cursor = conn.cursor()
        cursor.execute("""
            SELECT schema_name 
            FROM information_schema.schemata 
            WHERE schema_name = %s
        """, (db_config['schema'],))
        
        if cursor.fetchone():
            print(f"   ✅ Schema '{db_config['schema']}' exists")
        else:
            print(f"   ⚠️  Schema '{db_config['schema']}' does not exist")
            print(f"      Run: ./scripts/setup_database.sh")
        
        # Check tables
        cursor.execute("""
            SELECT COUNT(*) 
            FROM information_schema.tables 
            WHERE table_schema = %s AND table_type = 'BASE TABLE'
        """, (db_config['schema'],))
        
        table_count = cursor.fetchone()[0]
        print(f"   ✅ Found {table_count} tables in schema")
        
        cursor.close()
        connector.disconnect()
        print("   Database connection closed")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Database connection failed: {e}")
        return False


def test_external_databases():
    """Test external database connections."""
    print("\n3. Testing external database connections...")
    
    try:
        config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'db_config.yaml')
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        external_dbs = config.get('external_databases', {})
        
        for db_name, db_config in external_dbs.items():
            try:
                connector = DBConnector(
                    host=db_config['host'],
                    port=db_config['port'],
                    database=db_config['name'],
                    user=db_config['user'],
                    password=db_config['password']
                )
                conn = connector.connect()
                print(f"   ✅ Connected to PostgreSQL: {db_config['host']}:{db_config['port']}/{db_config['name']}")
                print(f"      {db_name}: {db_config['host']}:{db_config['port']}/{db_config.get('schema', 'public')}")
                connector.disconnect()
                print("   Database connection closed")
            except Exception as e:
                print(f"   ❌ {db_name}: Connection failed: {e}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ External database check failed: {e}")
        return False


def check_use_case_config():
    """Check use case configuration file."""
    print("\n4. Checking use case configuration...")
    config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'use_case_config.yaml')
    
    if not os.path.exists(config_path):
        print(f"   ❌ use_case_config.yaml not found at {config_path}")
        return False
    
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    print(f"   ✅ use_case_config.yaml found")
    
    # Check key sections
    decision_config = config.get('decision', {})
    risk_config = config.get('risk_scoring', {})
    
    print(f"      Auto approval enabled: {decision_config.get('enable_auto_approval', False)}")
    print(f"      Risk model type: {risk_config.get('model_type', 'N/A')}")
    
    # Count configured schemes
    schemes = config.get('schemes', {})
    print(f"      Configured schemes: {len(schemes)}")
    
    return True


def main():
    """Main function."""
    print("=" * 80)
    print("Configuration and Database Connectivity Check")
    print("=" * 80)
    
    checks = [
        check_database_config(),
        test_database_connection(),
        test_external_databases(),
        check_use_case_config()
    ]
    
    print("\n" + "=" * 80)
    if all(checks):
        print("✅ Configuration check complete!")
    else:
        print("⚠️  Configuration check completed with warnings")
    print("=" * 80)


if __name__ == '__main__':
    main()

