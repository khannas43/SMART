"""
Test Script: Train ML Models for Eligibility Scoring
Use Case: AI-PLATFORM-03 - Auto Identification of Beneficiaries

This script:
1. Checks MLflow connectivity
2. Lists available schemes
3. Trains models for specified schemes
4. Verifies model registration
"""

import sys
from pathlib import Path
import argparse
import yaml
import pandas as pd
import mlflow

# Add shared utils to path
sys.path.append(str(Path(__file__).parent.parent.parent.parent / "shared" / "utils"))
from db_connector import DBConnector

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / "src"))
from train_eligibility_model import EligibilityModelTrainer


def check_mlflow():
    """Check MLflow connectivity"""
    print("="*80)
    print("Checking MLflow Connectivity")
    print("="*80)
    
    try:
        mlflow.set_tracking_uri("http://127.0.0.1:5000")
        experiments = mlflow.search_experiments()
        print(f"✅ MLflow connected successfully")
        print(f"   Found {len(experiments)} experiments")
        return True
    except Exception as e:
        print(f"❌ MLflow connection failed: {e}")
        print(f"   Make sure MLflow UI is running: mlflow ui --port 5000")
        return False


def list_available_schemes():
    """List schemes available for training"""
    print("\n" + "="*80)
    print("Available Schemes for Training")
    print("="*80)
    
    db_config_path = Path(__file__).parent.parent / "config" / "db_config.yaml"
    with open(db_config_path, 'r') as f:
        db_config = yaml.safe_load(f)['database']
    
    db = DBConnector(
        host=db_config['host'],
        port=db_config['port'],
        database=db_config['name'],
        user=db_config['user'],
        password=db_config['password']
    )
    db.connect()
    
    query = """
        SELECT scheme_code, scheme_name, category, is_auto_id_enabled
        FROM public.scheme_master
        WHERE is_auto_id_enabled = true
            AND status = 'active'
        ORDER BY scheme_code
    """
    
    df = pd.read_sql(query, db.connection)
    db.disconnect()
    
    if len(df) == 0:
        print("⚠️  No schemes found with auto-identification enabled")
        print("   Run: psql ... -f scripts/load_initial_schemes.sql")
        return []
    
    print(f"\nFound {len(df)} schemes:")
    for _, row in df.iterrows():
        print(f"  - {row['scheme_code']}: {row['scheme_name']} ({row['category']})")
    
    return df['scheme_code'].tolist()


def check_training_data(scheme_code: str, min_samples: int = 100):
    """Check if sufficient training data exists"""
    print(f"\n📊 Checking training data for {scheme_code}...")
    
    db_config_path = Path(__file__).parent.parent / "config" / "db_config.yaml"
    with open(db_config_path, 'r') as f:
        db_config = yaml.safe_load(f)
    
    # Check 360° Profile database
    profile_db_config = db_config['external_databases']['profile_360']
    db = DBConnector(
        host=profile_db_config['host'],
        port=profile_db_config['port'],
        database=profile_db_config['name'],
        user=profile_db_config['user'],
        password=profile_db_config['password']
    )
    db.connect()
    
    query = """
        SELECT COUNT(DISTINCT gr.gr_id) as total_samples,
               COUNT(DISTINCT CASE 
                   WHEN EXISTS (
                       SELECT 1 FROM application_events ae
                       INNER JOIN public.scheme_master sm ON ae.scheme_id = sm.scheme_id
                       WHERE ae.gr_id = gr.gr_id 
                       AND sm.scheme_code = %s
                       AND ae.application_status = 'APPROVED'
                   ) THEN gr.gr_id
               END) as eligible_count
        FROM golden_records gr
        WHERE gr.status = 'active'
            AND (
                EXISTS (
                    SELECT 1 FROM application_events ae
                    INNER JOIN public.scheme_master sm ON ae.scheme_id = sm.scheme_id
                    WHERE ae.gr_id = gr.gr_id AND sm.scheme_code = %s
                )
                OR
                EXISTS (
                    SELECT 1 FROM benefit_events be
                    INNER JOIN public.scheme_master sm ON be.scheme_id = sm.scheme_id
                    WHERE be.gr_id = gr.gr_id AND sm.scheme_code = %s
                )
            )
    """
    
    df = pd.read_sql(query, db.connection, params=(scheme_code, scheme_code, scheme_code))
    db.disconnect()
    
    total = df.iloc[0]['total_samples']
    eligible = df.iloc[0]['eligible_count']
    
    print(f"   Total samples: {total}")
    print(f"   Eligible: {eligible}, Not Eligible: {total - eligible}")
    
    if total < min_samples:
        print(f"   ⚠️  Insufficient data: {total} < {min_samples} (minimum)")
        return False
    
    if eligible == 0:
        print(f"   ⚠️  No eligible samples found")
        return False
    
    if eligible == total:
        print(f"   ⚠️  All samples are eligible (no negative examples)")
        return False
    
    print(f"   ✅ Sufficient training data available")
    return True


def train_model_for_scheme(scheme_code: str, min_samples: int = 100):
    """Train model for a single scheme"""
    print(f"\n{'='*80}")
    print(f"Training Model for Scheme: {scheme_code}")
    print("="*80)
    
    # Check training data
    if not check_training_data(scheme_code, min_samples):
        print(f"❌ Skipping {scheme_code} - insufficient training data")
        return False
    
    try:
        trainer = EligibilityModelTrainer()
        trainer.train(scheme_code, save_model=True)
        trainer.close()
        
        print(f"\n✅ Successfully trained model for {scheme_code}")
        return True
        
    except Exception as e:
        print(f"\n❌ Error training model for {scheme_code}: {e}")
        import traceback
        traceback.print_exc()
        return False


def verify_model_registration(scheme_code: str):
    """Verify model was registered in database"""
    print(f"\n🔍 Verifying model registration for {scheme_code}...")
    
    db_config_path = Path(__file__).parent.parent / "config" / "db_config.yaml"
    with open(db_config_path, 'r') as f:
        db_config = yaml.safe_load(f)['database']
    
    db = DBConnector(
        host=db_config['host'],
        port=db_config['port'],
        database=db_config['name'],
        user=db_config['user'],
        password=db_config['password']
    )
    db.connect()
    
    query = """
        SELECT model_version, model_type, mlflow_run_id, training_samples_count,
               training_metrics, is_active, is_production, deployed_at
        FROM eligibility.ml_model_registry
        WHERE scheme_code = %s
        ORDER BY deployed_at DESC
        LIMIT 1
    """
    
    df = pd.read_sql(query, db.connection, params=(scheme_code,))
    db.disconnect()
    
    if len(df) == 0:
        print(f"   ⚠️  Model not found in registry")
        return False
    
    row = df.iloc[0]
    print(f"   ✅ Model registered:")
    print(f"      Version: {row['model_version']}")
    print(f"      Type: {row['model_type']}")
    print(f"      MLflow Run ID: {row['mlflow_run_id']}")
    print(f"      Training Samples: {row['training_samples_count']}")
    print(f"      Active: {row['is_active']}, Production: {row['is_production']}")
    
    return True


def main():
    parser = argparse.ArgumentParser(description='Train ML models for eligibility scoring')
    parser.add_argument('--scheme-code', help='Train model for specific scheme code')
    parser.add_argument('--all', action='store_true', help='Train models for all available schemes')
    parser.add_argument('--check-only', action='store_true', help='Only check data availability, do not train')
    parser.add_argument('--min-samples', type=int, default=100, help='Minimum samples required (default: 100)')
    
    args = parser.parse_args()
    
    # Check MLflow
    if not check_mlflow():
        print("\n❌ MLflow check failed. Please start MLflow UI:")
        print("   mlflow ui --port 5000")
        return
    
    # List available schemes
    available_schemes = list_available_schemes()
    
    if len(available_schemes) == 0:
        print("\n❌ No schemes available for training")
        return
    
    # Determine which schemes to train
    if args.scheme_code:
        schemes_to_train = [args.scheme_code]
    elif args.all:
        schemes_to_train = available_schemes
    else:
        print("\n⚠️  Please specify --scheme-code <CODE> or --all")
        print(f"   Available schemes: {', '.join(available_schemes)}")
        return
    
    # Train models
    if args.check_only:
        print("\n" + "="*80)
        print("Data Availability Check Only")
        print("="*80)
        
        for scheme_code in schemes_to_train:
            check_training_data(scheme_code, args.min_samples)
    
    else:
        print("\n" + "="*80)
        print("Starting Model Training")
        print("="*80)
        
        results = {}
        for scheme_code in schemes_to_train:
            success = train_model_for_scheme(scheme_code, args.min_samples)
            results[scheme_code] = success
            
            if success:
                verify_model_registration(scheme_code)
        
        # Summary
        print("\n" + "="*80)
        print("Training Summary")
        print("="*80)
        
        successful = [s for s, r in results.items() if r]
        failed = [s for s, r in results.items() if not r]
        
        print(f"✅ Successful: {len(successful)}")
        for s in successful:
            print(f"   - {s}")
        
        if failed:
            print(f"\n❌ Failed: {len(failed)}")
            for s in failed:
                print(f"   - {s}")


if __name__ == "__main__":
    main()

