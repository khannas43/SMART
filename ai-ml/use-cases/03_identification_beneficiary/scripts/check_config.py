#!/usr/bin/env python3
"""
Configuration Checker for Auto Identification of Beneficiaries
Validates configuration files, database connections, and setup
"""

import sys
from pathlib import Path
import yaml

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / "src"))
sys.path.append(str(Path(__file__).parent.parent.parent.parent / "shared" / "utils"))

from db_connector import DBConnector


def check_config_files():
    """Check if configuration files exist and are valid"""
    print("📋 Checking configuration files...")
    
    base_path = Path(__file__).parent.parent
    config_files = {
        'db_config.yaml': base_path / "config" / "db_config.yaml",
        'model_config.yaml': base_path / "config" / "model_config.yaml",
        'use_case_config.yaml': base_path / "config" / "use_case_config.yaml"
    }
    
    all_valid = True
    for name, path in config_files.items():
        if path.exists():
            try:
                with open(path, 'r') as f:
                    yaml.safe_load(f)
                print(f"   ✅ {name}")
            except Exception as e:
                print(f"   ❌ {name}: Invalid YAML - {e}")
                all_valid = False
        else:
            print(f"   ❌ {name}: Not found")
            all_valid = False
    
    return all_valid


def check_database_connection():
    """Check database connectivity"""
    print("\n🗄️  Checking database connection...")
    
    config_path = Path(__file__).parent.parent / "config" / "db_config.yaml"
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    db_config = config['database']
    
    try:
        db = DBConnector(
            host=db_config['host'],
            port=db_config['port'],
            database=db_config['name'],
            user=db_config['user'],
            password=db_config['password']
        )
        db.connect()
        
        # Check if schema exists
        cursor = db.connection.cursor()
        cursor.execute("""
            SELECT schema_name 
            FROM information_schema.schemata 
            WHERE schema_name = 'eligibility'
        """)
        
        if cursor.fetchone():
            print(f"✅ Connected to PostgreSQL: {db_config['host']}:{db_config['port']}/{db_config['name']}")
            print(f"   ✅ Schema 'eligibility' exists")
            
            # Check required tables
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'eligibility'
                ORDER BY table_name
            """)
            tables = [row[0] for row in cursor.fetchall()]
            
            required_tables = [
                'scheme_master', 'scheme_eligibility_rules',
                'eligibility_snapshots', 'candidate_lists',
                'ml_model_registry', 'batch_evaluation_jobs'
            ]
            
            print(f"   Checking required tables...")
            for table in required_tables:
                if table in tables:
                    cursor.execute(f"SELECT COUNT(*) FROM eligibility.{table}")
                    count = cursor.fetchone()[0]
                    print(f"      ✅ {table} ({count} rows)")
                else:
                    print(f"      ❌ {table} (not found)")
            
        else:
            print(f"❌ Schema 'eligibility' does not exist")
            print(f"   Run: psql -f database/eligibility_schema.sql")
            return False
        
        cursor.close()
        db.disconnect()
        return True
    
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False


def check_external_databases():
    """Check connections to external databases"""
    print("\n🔗 Checking external database connections...")
    
    config_path = Path(__file__).parent.parent / "config" / "db_config.yaml"
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    external_dbs = config.get('external_databases', {})
    
    for db_name, db_config in external_dbs.items():
        try:
            db = DBConnector(
                host=db_config['host'],
                port=db_config['port'],
                database=db_config['name'],
                user=db_config['user'],
                password=db_config['password']
            )
            db.connect()
            print(f"   ✅ {db_name} ({db_config['database']})")
            db.disconnect()
        except Exception as e:
            print(f"   ⚠️  {db_name}: {e}")


def check_mlflow():
    """Check MLflow connection"""
    print("\n🤖 Checking MLflow...")
    
    try:
        import mlflow
        
        config_path = Path(__file__).parent.parent / "config" / "model_config.yaml"
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        tracking_uri = config['mlflow']['tracking_uri']
        mlflow.set_tracking_uri(tracking_uri)
        
        # Try to list experiments
        try:
            experiments = mlflow.search_experiments()
            print(f"   ✅ MLflow connected: {tracking_uri}")
            print(f"   ✅ Found {len(experiments)} experiments")
        except Exception as e:
            print(f"   ⚠️  MLflow check failed: {e}")
            print(f"   ⚠️  Make sure MLflow UI is running: mlflow ui --port 5000")
    
    except ImportError:
        print(f"   ❌ MLflow not installed")
    except Exception as e:
        print(f"   ⚠️  MLflow check failed: {e}")


def check_model_files():
    """Check if ML models exist"""
    print("\n📦 Checking model files...")
    
    # This would check for trained models
    # For now, just check if model directory structure exists
    models_dir = Path(__file__).parent.parent / "models"
    if models_dir.exists():
        model_files = list(models_dir.glob("*.pkl"))
        print(f"   ✅ Models directory exists ({len(model_files)} models)")
    else:
        print(f"   ⚠️  Models directory not found (models will be created during training)")


def main():
    """Run all checks"""
    print("=" * 80)
    print("Configuration Check for Auto Identification of Beneficiaries")
    print("=" * 80)
    print()
    
    results = {
        'Config Files': check_config_files(),
        'Database': check_database_connection(),
    }
    
    check_external_databases()
    check_mlflow()
    check_model_files()
    
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    for check, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {check}: {status}")
    print("=" * 80)
    
    if all(results.values()):
        print("\n✅ All critical checks passed!")
        return 0
    else:
        print("\n❌ Some checks failed. Please review the output above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())

