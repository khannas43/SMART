"""
Configuration Validation Script
Validates database connections and configuration files
"""

import sys
import os
from pathlib import Path
import yaml

# Add shared utils to path
sys.path.append(str(Path(__file__).parent.parent.parent.parent / "shared" / "utils"))
from db_connector import DBConnector


def check_config():
    """Check configuration files and database connections"""
    print("=" * 80)
    print("Configuration Validation")
    print("=" * 80)
    
    config_path = os.path.join(os.path.dirname(__file__), '../config/db_config.yaml')
    
    # Load config
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        print(f"✅ Configuration file loaded: {config_path}")
    except Exception as e:
        print(f"❌ Error loading config: {e}")
        return False
    
    # Check database connections
    db_config = config['database']
    print(f"\n📋 Checking primary database connection...")
    try:
        db = DBConnector(
            host=db_config['host'],
            port=db_config['port'],
            database=db_config['name'],
            user=db_config['user'],
            password=db_config['password']
        )
        db.connect()
        print(f"✅ Connected to PostgreSQL: {db_config['host']}:{db_config['port']}/{db_config['name']}")
        
        # Check schema exists
        cursor = db.connection.cursor()
        cursor.execute(f"SELECT schema_name FROM information_schema.schemata WHERE schema_name = '{db_config['schema']}'")
        if cursor.fetchone():
            print(f"✅ Schema '{db_config['schema']}' exists")
        else:
            print(f"⚠️  Schema '{db_config['schema']}' does not exist - run database/intimation_schema.sql")
        cursor.close()
        db.disconnect()
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False
    
    # Check external databases
    print(f"\n📋 Checking external database connections...")
    for db_name, db_cfg in config.get('external_databases', {}).items():
        try:
            ext_db = DBConnector(
                host=db_cfg['host'],
                port=db_cfg['port'],
                database=db_cfg['name'],
                user=db_cfg['user'],
                password=db_cfg['password']
            )
            ext_db.connect()
            print(f"✅ Connected to {db_name}: {db_cfg['host']}:{db_cfg['port']}/{db_cfg['name']}")
            ext_db.disconnect()
        except Exception as e:
            print(f"⚠️  Could not connect to {db_name}: {e}")
    
    # Check use case config
    use_case_config_path = os.path.join(os.path.dirname(__file__), '../config/use_case_config.yaml')
    try:
        with open(use_case_config_path, 'r') as f:
            use_case_config = yaml.safe_load(f)
        print(f"\n✅ Use case config loaded: {use_case_config_path}")
        
        # Validate required sections
        required_sections = ['campaign', 'messaging', 'fatigue', 'retry', 'consent']
        for section in required_sections:
            if section in use_case_config:
                print(f"  ✅ Section '{section}' found")
            else:
                print(f"  ⚠️  Section '{section}' missing")
    except Exception as e:
        print(f"⚠️  Error loading use case config: {e}")
    
    print("\n" + "=" * 80)
    print("✅ Configuration check complete!")
    print("=" * 80)
    return True


if __name__ == '__main__':
    check_config()

