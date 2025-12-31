"""
Check Configuration and Database Connectivity
Validates database connections and configuration files
"""

import sys
from pathlib import Path
import yaml

# Add shared utils to path
sys.path.append(str(Path(__file__).parent.parent.parent.parent / "shared" / "utils"))
from db_connector import DBConnector


def check_config():
    """Check configuration files and database connectivity"""
    print("=" * 80)
    print("Configuration and Database Connectivity Check")
    print("=" * 80)
    
    # Get base directory
    base_dir = Path(__file__).parent.parent
    config_dir = base_dir / "config"
    
    # Check db_config.yaml
    print("\n1. Checking database configuration...")
    db_config_path = config_dir / "db_config.yaml"
    if not db_config_path.exists():
        print(f"   ❌ db_config.yaml not found: {db_config_path}")
        return False
    
    with open(db_config_path, 'r') as f:
        db_config = yaml.safe_load(f)
    
    print(f"   ✅ db_config.yaml found")
    print(f"      Primary DB: {db_config['database']['name']}@{db_config['database']['host']}:{db_config['database']['port']}")
    print(f"      Schema: {db_config['database']['schema']}")
    
    # Test primary database connection
    print("\n2. Testing primary database connection...")
    try:
        db = DBConnector(
            host=db_config['database']['host'],
            port=db_config['database']['port'],
            database=db_config['database']['name'],
            user=db_config['database']['user'],
            password=db_config['database']['password']
        )
        db.connect()
        print(f"   ✅ Connected to PostgreSQL: {db_config['database']['host']}:{db_config['database']['port']}/{db_config['database']['name']}")
        
        # Check if schema exists
        cursor = db.connection.cursor()
        cursor.execute("""
            SELECT EXISTS(
                SELECT 1 FROM information_schema.schemata 
                WHERE schema_name = %s
            )
        """, (db_config['database']['schema'],))
        schema_exists = cursor.fetchone()[0]
        
        if schema_exists:
            print(f"   ✅ Schema '{db_config['database']['schema']}' exists")
            
            # Count tables
            cursor.execute("""
                SELECT COUNT(*) 
                FROM information_schema.tables 
                WHERE table_schema = %s
            """, (db_config['database']['schema'],))
            table_count = cursor.fetchone()[0]
            print(f"   ✅ Found {table_count} tables in schema")
        else:
            print(f"   ⚠️  Schema '{db_config['database']['schema']}' does not exist")
            print(f"      Run: ./scripts/setup_database.sh")
        
        cursor.close()
        db.disconnect()
    except Exception as e:
        print(f"   ❌ Connection failed: {e}")
        return False
    
    # Test external database connections
    print("\n3. Testing external database connections...")
    if 'external_databases' in db_config:
        for db_name, db_params in db_config['external_databases'].items():
            try:
                ext_db = DBConnector(
                    host=db_params['host'],
                    port=db_params['port'],
                    database=db_params['name'],
                    user=db_params['user'],
                    password=db_params['password']
                )
                ext_db.connect()
                print(f"   ✅ {db_name}: {db_params['host']}:{db_params['port']}/{db_params['name']}")
                ext_db.disconnect()
            except Exception as e:
                print(f"   ⚠️  {db_name}: Connection failed - {e}")
    
    # Check use_case_config.yaml
    print("\n4. Checking use case configuration...")
    use_case_config_path = config_dir / "use_case_config.yaml"
    if use_case_config_path.exists():
        with open(use_case_config_path, 'r') as f:
            use_case_config = yaml.safe_load(f)
        print(f"   ✅ use_case_config.yaml found")
        if 'schemes' in use_case_config:
            print(f"      Configured schemes: {len(use_case_config['schemes'])}")
    else:
        print(f"   ⚠️  use_case_config.yaml not found (optional)")
    
    print("\n" + "=" * 80)
    print("✅ Configuration check complete!")
    print("=" * 80)
    return True


if __name__ == "__main__":
    success = check_config()
    sys.exit(0 if success else 1)

