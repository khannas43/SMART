#!/usr/bin/env python3
"""
Configuration and Database Connectivity Check
Use Case ID: AI-PLATFORM-09
"""

import sys
import os
import yaml
from pathlib import Path

# Add parent directories to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'shared', 'utils'))

from db_connector import DBConnector


def check_config():
    """Check database and configuration"""
    print("=" * 80)
    print("Configuration and Database Connectivity Check")
    print("=" * 80)
    
    # 1. Check database configuration
    print("\n1. Checking database configuration...")
    db_config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'db_config.yaml')
    
    if not os.path.exists(db_config_path):
        print("   ❌ db_config.yaml not found")
        return
    
    with open(db_config_path, 'r') as f:
        db_config = yaml.safe_load(f)
    
    print("   ✅ db_config.yaml found")
    db_info = db_config['database']
    print(f"      Primary DB: {db_info['name']}@{db_info['host']}:{db_info['port']}")
    print(f"      Schema: {db_info['schema']}")
    
    # 2. Test primary database connection
    print("\n2. Testing primary database connection...")
    try:
        connector = DBConnector(
            host=db_info['host'],
            port=db_info['port'],
            database=db_info['name'],
            user=db_info['user'],
            password=db_info['password']
        )
        conn = connector.connect()
        print(f"   ✅ Connected to PostgreSQL: {db_info['host']}:{db_info['port']}/{db_info['name']}")
        
        # Check schema exists
        cursor = conn.cursor()
        cursor.execute("""
            SELECT schema_name 
            FROM information_schema.schemata 
            WHERE schema_name = %s
        """, (db_info['schema'],))
        
        if cursor.fetchone():
            print(f"   ✅ Schema '{db_info['schema']}' exists")
            
            # Count tables
            cursor.execute("""
                SELECT COUNT(*) 
                FROM information_schema.tables 
                WHERE table_schema = %s AND table_type = 'BASE TABLE'
            """, (db_info['schema'],))
            table_count = cursor.fetchone()[0]
            print(f"   ✅ Found {table_count} tables in schema")
        else:
            print(f"   ❌ Schema '{db_info['schema']}' does not exist")
            print("      Run: ./scripts/setup_database.sh")
        
        cursor.close()
        connector.disconnect()
    
    except Exception as e:
        print(f"   ❌ Connection failed: {str(e)}")
        return
    
    # 3. Test external database connections
    print("\n3. Testing external database connections...")
    external_dbs = db_config.get('external_databases', {})
    
    for name, ext_config in external_dbs.items():
        try:
            ext_connector = DBConnector(
                host=ext_config['host'],
                port=ext_config['port'],
                database=ext_config['name'],
                user=ext_config['user'],
                password=ext_config['password']
            )
            ext_conn = ext_connector.connect()
            print(f"   ✅ {name}: {ext_config['host']}:{ext_config['port']}/{ext_config['name']}")
            ext_connector.disconnect()
        except Exception as e:
            print(f"   ❌ {name}: Connection failed - {str(e)}")
    
    # 4. Check use case configuration
    print("\n4. Checking use case configuration...")
    use_case_config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'use_case_config.yaml')
    
    if os.path.exists(use_case_config_path):
        print("   ✅ use_case_config.yaml found")
        with open(use_case_config_path, 'r') as f:
            use_case_config = yaml.safe_load(f)
        
        inclusion_config = use_case_config.get('inclusion_detection', {})
        print(f"      Inclusion detection enabled: {inclusion_config.get('enable_detection', False)}")
        print(f"      Inclusion gap threshold: {inclusion_config.get('inclusion_gap_threshold', 0.6)}")
        
        exception_config = use_case_config.get('exception_detection', {})
        print(f"      Exception detection enabled: {exception_config.get('enable_exception_detection', False)}")
    else:
        print("   ⚠️  use_case_config.yaml not found")
    
    print("\n" + "=" * 80)
    print("✅ Configuration check complete!")
    print("=" * 80)


if __name__ == '__main__':
    check_config()

