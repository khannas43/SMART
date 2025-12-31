#!/usr/bin/env python3
"""
Configuration Checker for Eligibility Scoring & 360° Profiles
Validates configuration files and database connectivity
"""

import sys
from pathlib import Path
import yaml

# Add paths
sys.path.append(str(Path(__file__).parent.parent.parent.parent / "shared" / "utils"))
from db_connector import DBConnector


def check_config_files():
    """Check if all config files exist and are valid"""
    print("📋 Checking configuration files...")
    
    config_dir = Path(__file__).parent.parent / "config"
    required_files = [
        "db_config.yaml",
        "model_config.yaml",
        "use_case_config.yaml"
    ]
    
    all_valid = True
    for file in required_files:
        file_path = config_dir / file
        if file_path.exists():
            try:
                with open(file_path, 'r') as f:
                    yaml.safe_load(f)
                print(f"   ✅ {file}")
            except Exception as e:
                print(f"   ❌ {file}: Invalid YAML - {e}")
                all_valid = False
        else:
            print(f"   ❌ {file}: Not found")
            all_valid = False
    
    return all_valid


def check_database_connection():
    """Check database connectivity"""
    print("\n🗄️  Checking database connection...")
    
    config_path = Path(__file__).parent.parent / "config" / "db_config.yaml"
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        db_config = config['database']
        db = DBConnector(
            host=db_config['host'],
            port=db_config['port'],
            database=db_config['dbname'],
            user=db_config['user'],
            password=db_config['password']
        )
        
        db.connect()
        print(f"   ✅ Connected to {db_config['dbname']} at {db_config['host']}:{db_config['port']}")
        
        # Check if required tables exist
        print("\n   Checking required tables...")
        required_tables = [
            'golden_records',
            'gr_relationships',
            'scheme_master',
            'benefit_events',
            'application_events',
            'socio_economic_facts',
            'profile_360',
            'analytics_flags'
        ]
        
        all_tables_exist = True
        for table in required_tables:
            query = f"SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = '{table}')"
            result = db.execute_query(query)
            exists = result.iloc[0, 0]
            
            if exists:
                # Get row count
                count_query = f"SELECT COUNT(*) FROM {table}"
                count_result = db.execute_query(count_query)
                count = count_result.iloc[0, 0]
                print(f"      ✅ {table} ({count:,} rows)")
            else:
                print(f"      ❌ {table}: Not found")
                all_tables_exist = False
        
        db.disconnect()
        return all_tables_exist
        
    except Exception as e:
        print(f"   ❌ Connection failed: {e}")
        return False


def check_model_files():
    """Check if model files exist"""
    print("\n🤖 Checking model files...")
    
    model_dir = Path(__file__).parent.parent / "models" / "checkpoints"
    
    if not model_dir.exists():
        print(f"   ⚠️  Model directory not found: {model_dir}")
        print("   (This is OK if models haven't been trained yet)")
        return True
    
    model_files = {
        "income_band_model.pkl": "Income Band Inference Model",
        "eligibility_scoring_model.pkl": "Eligibility Scoring Model"
    }
    
    all_exist = True
    for file, name in model_files.items():
        file_path = model_dir / file
        if file_path.exists():
            size = file_path.stat().st_size / (1024 * 1024)  # MB
            print(f"   ✅ {name}: {size:.2f} MB")
        else:
            print(f"   ⚠️  {name}: Not found (training required)")
            all_exist = False
    
    return all_exist


def check_mlflow():
    """Check MLflow connectivity"""
    print("\n📊 Checking MLflow...")
    
    try:
        import mlflow
        config_path = Path(__file__).parent.parent / "config" / "model_config.yaml"
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        tracking_uri = config['mlflow']['tracking_uri']
        mlflow.set_tracking_uri(tracking_uri)
        
        # Try to list experiments
        experiments = mlflow.search_experiments()
        print(f"   ✅ Connected to MLflow at {tracking_uri}")
        print(f"   📁 Found {len(experiments)} experiments")
        
        # Check for our experiment
        experiment_name = config['mlflow']['experiment_name']
        exp = mlflow.get_experiment_by_name(experiment_name)
        if exp:
            print(f"   ✅ Experiment '{experiment_name}' exists")
        else:
            print(f"   ⚠️  Experiment '{experiment_name}' not found (will be created on first run)")
        
        return True
        
    except Exception as e:
        print(f"   ❌ MLflow check failed: {e}")
        print("   ⚠️  Make sure MLflow UI is running: mlflow ui --port 5000")
        return False


def main():
    """Run all checks"""
    print("=" * 60)
    print("Configuration Check for Eligibility Scoring & 360° Profiles")
    print("=" * 60)
    
    results = {
        "Config Files": check_config_files(),
        "Database": check_database_connection(),
        "Model Files": check_model_files(),
        "MLflow": check_mlflow()
    }
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    all_passed = True
    for check, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {check}: {status}")
        if not passed:
            all_passed = False
    
    print("=" * 60)
    
    if all_passed:
        print("✅ All checks passed!")
        return 0
    else:
        print("❌ Some checks failed. Please review the output above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())

